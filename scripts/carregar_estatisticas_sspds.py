# scripts/carregar_estatisticas_sspds.py

import sys
import os
import re
import json
import hashlib
import tempfile
import datetime
from pathlib import Path
from urllib.parse import urljoin

import requests
import pandas as pd
import pdfplumber
from bs4 import BeautifulSoup
from requests.adapters import HTTPAdapter
from urllib3.util import Retry
from sqlalchemy import text

# Evita problema de encoding no Windows (emoji e acentos)
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

# --- Configuração do Ambiente ---
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app.banco_de_dados.db_config import SessionLocal
from app.banco_de_dados.db_saida import Evento

# --- Configurações do Robô ---
URL_ALVOS = [
    "https://www.sspds.ce.gov.br/estatisticas/",
    "https://www.sspds.ce.gov.br/indicadores-de-seguranca-publica/"
]
PASTA_DOWNLOADS = os.path.join(os.path.dirname(__file__), '..', 'sspds_downloads')
ARQUIVO_MANIFESTO = os.path.join(PASTA_DOWNLOADS, "manifest.json")
HEADERS = {
    'User-Agent': ('Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                   'AppleWebKit/537.36 (KHTML, like Gecko) '
                   'Chrome/121.0 Safari/537.36')
}
EXTS_OK = {".pdf", ".xlsx", ".csv"}  # extensões aceitas

# Mapa global: nome_arquivo -> URL de origem (preenchido no download)
FONTE_URL_MAP: dict[str, str] = {}

# --- Manifesto (diário de bordo) ---

def carregar_manifesto():
    if os.path.exists(ARQUIVO_MANIFESTO):
        with open(ARQUIVO_MANIFESTO, 'r', encoding='utf-8') as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return {}
    return {}

def salvar_manifesto(manifesto):
    os.makedirs(PASTA_DOWNLOADS, exist_ok=True)
    with open(ARQUIVO_MANIFESTO, 'w', encoding='utf-8') as f:
        json.dump(manifesto, f, indent=4, ensure_ascii=False)

def calcular_hash_arquivo(caminho_arquivo):
    hash_md5 = hashlib.md5()
    with open(caminho_arquivo, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()

def _sha256(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()

# --- Coleta (encontrar links) ---

def encontrar_links_de_arquivos(urls):
    print("--- FASE 1: Buscando links de TODOS os arquivos de dados ---")
    links_encontrados = set()
    for url_da_pagina in urls:
        print(f" Investigando: {url_da_pagina}")
        try:
            resposta = requests.get(url_da_pagina, headers=HEADERS, timeout=30)
            resposta.raise_for_status()
            soup = BeautifulSoup(resposta.text, 'html.parser')
            for tag_a in soup.find_all('a', href=True):
                href_raw = tag_a['href']
                href = href_raw.lower()
                # filtra por extensão
                if not any(href.endswith(ext) for ext in EXTS_OK):
                    continue
                # opcional: ignore rótulos ainda não publicados
                if href.endswith("_2025-1.xlsx"):
                    continue
                link_completo = urljoin(url_da_pagina, href_raw)
                links_encontrados.add(link_completo)
        except requests.exceptions.RequestException as e:
            print(f"[WARN] Falha ao investigar a página: {e}")

    if links_encontrados:
        print(f"Total de {len(links_encontrados)} links de arquivos encontrados.")
    else:
        print("Nenhum link de arquivo encontrado.")
    return list(links_encontrados)

# --- HTTP robusto e download ---

def _session_http_robusta() -> requests.Session:
    retry = Retry(
        total=5,
        connect=5,
        read=5,
        backoff_factor=0.5,
        status_forcelist=(429, 500, 502, 503, 504),
        allowed_methods=frozenset(["HEAD", "GET"])
    )
    adapter = HTTPAdapter(max_retries=retry, pool_connections=10, pool_maxsize=10)

    s = requests.Session()
    s.mount("http://", adapter)
    s.mount("https://", adapter)
    s.headers.update({
        "User-Agent": HEADERS["User-Agent"],
        "Accept": "application/pdf,application/octet-stream;q=0.9,*/*;q=0.8",
        "Accept-Encoding": "identity"
    })
    return s

def baixar_e_validar_arquivos(links):
    """
    Baixa somente arquivos com extensões em EXTS_OK.
    Faz retry/backoff, salva em tmp único e dá replace atômico.
    Preenche FONTE_URL_MAP[nome_arquivo] = url_origem.
    """
    global FONTE_URL_MAP
    pasta = Path(__file__).parent.parent / "sspds_downloads"
    pasta.mkdir(parents=True, exist_ok=True)

    s = _session_http_robusta()
    baixados_ou_atualizados = []

    for url in links:
        nome = url.split("/")[-1] or "arquivo"
        nome_lower = nome.lower()
        # segurança extra: somente EXTS_OK
        if not any(nome_lower.endswith(ext) for ext in EXTS_OK):
            continue

        destino = pasta / nome
        FONTE_URL_MAP[nome] = url  # registra origem

        try:
            # tenta um HEAD rápido (ignora se falhar)
            try:
                s.head(url, timeout=(10, 15), allow_redirects=True)
            except requests.RequestException:
                pass

            with s.get(url, stream=True, timeout=(15, 180)) as r:
                try:
                    r.raise_for_status()
                except requests.HTTPError as e:
                    status = getattr(e.response, "status_code", None)
                    if status == 404:
                        print(f"[WARN] HTTP 404 em {url}")
                        continue
                    raise

                with tempfile.NamedTemporaryFile(delete=False, dir=pasta, suffix=".tmp") as tmpf:
                    tmp_path = Path(tmpf.name)
                    for chunk in r.iter_content(chunk_size=1024 * 256):
                        if chunk:
                            tmpf.write(chunk)

            # se já existe e é igual, descarta
            if destino.exists() and _sha256(tmp_path) == _sha256(destino):
                tmp_path.unlink(missing_ok=True)
                continue

            os.replace(tmp_path, destino)
            baixados_ou_atualizados.append(str(destino))

        except requests.exceptions.ConnectTimeout:
            print(f"[WARN] Timeout de conexão: {url}")
        except requests.exceptions.ReadTimeout:
            print(f"[WARN] Timeout de leitura: {url}")
        except requests.RequestException as e:
            print(f"[WARN] Falha de rede em {url}: {e}")
        except Exception as e:
            print(f"[WARN] Erro inesperado com {url}: {e}")
        finally:
            try:
                if 'tmp_path' in locals() and tmp_path.exists():
                    tmp_path.unlink(missing_ok=True)
            except Exception:
                pass

    return baixados_ou_atualizados

# --- Processamento de planilhas existentes (seus dados) ---

def encontrar_nome_coluna(df, possiveis_nomes):
    colunas_df = [str(col).lower().strip() for col in df.columns]
    for nome in possiveis_nomes:
        if nome.lower() in colunas_df:
            return df.columns[colunas_df.index(nome.lower())]
    return None

def processar_planilha(caminho_arquivo, db):
    print(f"\n[Analisando Planilha]: {os.path.basename(caminho_arquivo)}")
    eventos_novos = 0
    eventos_ignorados = 0
    try:
        df = pd.read_excel(caminho_arquivo, engine='openpyxl')

        mapa_colunas = {
            'municipio': encontrar_nome_coluna(df, ['Município', 'Municipio']),
            'data': encontrar_nome_coluna(df, ['Data', 'Data Fato', 'Data da Ocorrência']),
            'hora': encontrar_nome_coluna(df, ['Hora Fato', 'Hora']),
            'dia_semana': encontrar_nome_coluna(df, ['Dia da Semana']),
            'natureza': encontrar_nome_coluna(df, ['Natureza', 'Natureza Crime']),
            'genero': encontrar_nome_coluna(df, ['Gênero', 'Sexo da Vítima']),
            'idade': encontrar_nome_coluna(df, ['Idade da Vítima', 'Idade']),
            'raca': encontrar_nome_coluna(df, ['Raça da Vítima', 'Cor da Pele']),
            'escolaridade': encontrar_nome_coluna(df, ['Escolaridade da Vítima']),
            'meio_empregado': encontrar_nome_coluna(df, ['Meio Empregado']),
            'tipo_objeto': encontrar_nome_coluna(df, ['Tipo de Entorpecente', 'Tipo Arma']),
            'quantidade': encontrar_nome_coluna(df, ['Quantidade (Kg)', 'Quantidade']),
            'bairro': encontrar_nome_coluna(df, ['Bairro', 'Bairro Fato']),
            'ais': encontrar_nome_coluna(df, ['AIS']),
            'local': encontrar_nome_coluna(df, ['Local']),
        }

        if mapa_colunas['municipio']:
            df_fortaleza = df[df[mapa_colunas['municipio']].astype(str).str.strip().str.lower() == 'fortaleza']
        else:
            print("  -> Aviso: Coluna 'Município' não encontrada. Pulando arquivo.")
            return

        for _, row in df_fortaleza.iterrows():
            string_unica = str(row.to_dict()) + os.path.basename(caminho_arquivo)
            hash_do_evento = hashlib.md5(string_unica.encode('utf-8')).hexdigest()

            evento_existente = db.query(Evento).filter(Evento.hash_origem == hash_do_evento).first()

            if not evento_existente:
                data_str = str(row[mapa_colunas['data']]) if mapa_colunas['data'] and pd.notna(row[mapa_colunas['data']]) else None
                hora_str = str(row[mapa_colunas['hora']]) if mapa_colunas['hora'] and pd.notna(row[mapa_colunas['hora']]) else None

                data_evento_final = None
                if data_str:
                    try:
                        data_temp = pd.to_datetime(data_str.split(" ")[0])
                        if hora_str:
                            hora_temp = pd.to_datetime(hora_str).time()
                            data_evento_final = datetime.datetime.combine(data_temp.date(), hora_temp)
                        else:
                            data_evento_final = data_temp
                    except (ValueError, TypeError):
                        data_evento_final = None

                novo_evento = Evento(
                    hash_origem=hash_do_evento,
                    tipo_fonte="SSPDS",
                    nome_fonte=os.path.basename(caminho_arquivo),
                    titulo=str(row.get(mapa_colunas['natureza'], "Não informado")),
                    data_evento=data_evento_final,
                    hora_ocorrencia=data_evento_final.time() if data_evento_final else None,
                    dia_semana=row.get(mapa_colunas['dia_semana']),
                    bairro=row.get(mapa_colunas['bairro']),
                    ais=str(row.get(mapa_colunas['ais'])),
                    local_especifico=row.get(mapa_colunas['local']),
                    natureza_crime=row.get(mapa_colunas['natureza']),
                    meio_empregado=row.get(mapa_colunas['meio_empregado']),
                    genero_vitima=row.get(mapa_colunas['genero']),
                    idade_vitima=str(row.get(mapa_colunas['idade'])),
                    raca_vitima=row.get(mapa_colunas['raca']),
                    escolaridade_vitima=row.get(mapa_colunas['escolaridade']),
                    tipo_objeto=row.get(mapa_colunas['tipo_objeto']),
                    quantidade_objeto=pd.to_numeric(row.get(mapa_colunas['quantidade']), errors='coerce')
                )
                db.add(novo_evento)
                eventos_novos += 1
            else:
                eventos_ignorados += 1

        db.commit()
        print(f"  -> Planilha OK. {eventos_novos} novos, {eventos_ignorados} duplicados.")
    except Exception as e:
        db.rollback()
        print(f"Erro ao ler/processar a planilha: {e}")

# --- Persistência do texto bruto em DadoBruto ---

def salvar_dado_bruto(fonte: str, url: str, texto: str,
                      tipo_evento: str | None = None,
                      locais: list[str] | None = None,
                      datas: list[str] | None = None) -> None:
    session = SessionLocal()
    try:
        session.execute(
            text("""
                INSERT INTO "DadoBruto"
                    (fonte, url_noticia, texto_completo, tipo_evento_classificado, locais_extraidos, datas_extraidas)
                VALUES
                    (:fonte, :url, :texto, :tipo, :locais, :datas)
                ON CONFLICT (url_noticia) DO UPDATE SET
                    texto_completo = EXCLUDED.texto_completo,
                    tipo_evento_classificado = EXCLUDED.tipo_evento_classificado,
                    locais_extraidos = EXCLUDED.locais_extraidos,
                    datas_extraidas = EXCLUDED.datas_extraidas
            """),
            {
                "fonte": fonte,
                "url": url,
                "texto": texto,
                "tipo": tipo_evento,
                "locais": locais,
                "datas": datas,
            }
        )
        session.commit()
    finally:
        session.close()

# --- Extração de PDF (texto + tentativa de tabela) ---

RE_DATA = re.compile(r"\b(20\d{2}|19\d{2})\b")  # anos (ajuste se quiser MM/YYYY)
RE_LOCAL = re.compile(r"\b(Fortaleza|Ceará|Sobral|Maracanaú|Juazeiro do Norte)\b", re.I)

def processar_pdf(caminho_arquivo, db=None):
    p = Path(caminho_arquivo)
    print(f"\n[Analisando PDF]: {p.name}")

    texto_total = []
    tabelas = []

    try:
        with pdfplumber.open(p) as pdf:
            for page in pdf.pages:
                # texto
                t = page.extract_text() or ""
                if t:
                    texto_total.append(t)

                # tentativa de tabela simples
                try:
                    table = page.extract_table()
                    if table and len(table) >= 2 and len(table[0]) >= 2:
                        df = pd.DataFrame(table[1:], columns=table[0])
                        tabelas.append(df)
                except Exception:
                    pass

        texto = "\n".join(texto_total)

        # extrações simples
        datas = sorted(set(RE_DATA.findall(texto))) or None
        locais = sorted(set(m.group(0) for m in RE_LOCAL.finditer(texto))) or None

        # salva bruto em DadoBruto (fonte/url)
        url_origem = FONTE_URL_MAP.get(p.name, p.name)
        salvar_dado_bruto(
            fonte="SSPDS/CE",
            url=url_origem,
            texto=texto,
            tipo_evento=None,
            locais=locais,
            datas=datas,
        )

        # salva CSVs de tabelas (se houver)
        tabelas_csv_paths = []
        if tabelas:
            out_dir = Path(__file__).parent.parent / "sspds_extracoes"
            out_dir.mkdir(parents=True, exist_ok=True)
            for i, df in enumerate(tabelas, start=1):
                out_csv = out_dir / f"{p.stem}__tabela{i}.csv"
                try:
                    df.to_csv(out_csv, index=False)
                except Exception:
                    # fallback: cabeçalhos genéricos
                    df.columns = [f"col_{j+1}" for j in range(df.shape[1])]
                    df.to_csv(out_csv, index=False)
                tabelas_csv_paths.append(str(out_csv))

        print(f"    -> OK. texto={len(texto)} chars, datas={datas}, locais={locais}, tabelas={len(tabelas_csv_paths)}")

    except Exception as e:
        print(f"    -> Falha ao processar PDF {p.name}: {e}")

# --- Orquestração ---

def processar_arquivos_baixados(lista_de_arquivos):
    print("\n--- FASE 3: Processando APENAS arquivos novos/atualizados ---")
    if not lista_de_arquivos:
        print("Nenhum arquivo novo para processar.")
        return

    db = SessionLocal()
    try:
        for caminho_arquivo in lista_de_arquivos:
            nome_arquivo_lower = caminho_arquivo.lower()
            if nome_arquivo_lower.endswith(('.xlsx', '.xls')):
                processar_planilha(caminho_arquivo, db)
            elif nome_arquivo_lower.endswith('.pdf'):
                processar_pdf(caminho_arquivo, db)
            else:
                print(f"[Ignorado]: {os.path.basename(caminho_arquivo)}")
    finally:
        if 'db' in locals() and db.is_active:
            db.close()
    print("\nProcessamento inteligente concluído.")

if __name__ == "__main__":
    links = encontrar_links_de_arquivos(URL_ALVOS)
    if links:
        arquivos_novos_ou_atualizados = baixar_e_validar_arquivos(links)
        processar_arquivos_baixados(arquivos_novos_ou_atualizados)
    print("\n--- OPERAÇÃO FINALIZADA ---")
