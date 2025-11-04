# scripts/carregar_estatisticas_sspds.py

import sys
import os
import requests
import pandas as pd
import fitz
import hashlib
import datetime
import json
from bs4 import BeautifulSoup
from urllib.parse import urljoin

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
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

# --- Funções de Controle com "Diário de Bordo" (Manifesto) ---

def carregar_manifesto():
    if os.path.exists(ARQUIVO_MANIFESTO):
        with open(ARQUIVO_MANIFESTO, 'r', encoding='utf-8') as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return {} # Retorna um dicionário vazio se o arquivo estiver corrompido
    return {}

def salvar_manifesto(manifesto):
    os.makedirs(PASTA_DOWNLOADS, exist_ok=True)
    with open(ARQUIVO_MANIFESTO, 'w', encoding='utf-8') as f:
        json.dump(manifesto, f, indent=4)

def calcular_hash_arquivo(caminho_arquivo):
    hash_md5 = hashlib.md5()
    with open(caminho_arquivo, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()

# --- Funções de Coleta (Encontrar e Baixar de Forma Inteligente) ---

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
                link = tag_a['href'].lower()
                if link.endswith(('.xlsx', '.xls', '.csv', '.ods', '.pdf')):
                    link_completo = urljoin(url_da_pagina, tag_a['href'])
                    links_encontrados.add(link_completo)
        except requests.exceptions.RequestException as e:
            print(f"Falha ao investigar a página: {e}")
    if links_encontrados: print(f"Total de {len(links_encontrados)} links de arquivos encontrados.")
    else: print("Nenhum link de arquivo encontrado.")
    return list(links_encontrados)

def baixar_e_validar_arquivos(lista_de_links):
    print("\n--- FASE 2: Baixando e validando arquivos (com verificação de atualização) ---")
    os.makedirs(PASTA_DOWNLOADS, exist_ok=True)
    manifesto = carregar_manifesto()
    arquivos_para_processar = []
    
    for link in lista_de_links:
        nome_base_arquivo = os.path.basename(link)
        caminho_arquivo_final = os.path.join(PASTA_DOWNLOADS, nome_base_arquivo)
        caminho_arquivo_temp = caminho_arquivo_final + ".tmp"
        
        try:
            print(f"  -> Verificando '{nome_base_arquivo}'...")
            resposta = requests.get(link, headers=HEADERS, stream=True, timeout=180)
            resposta.raise_for_status()
            
            with open(caminho_arquivo_temp, 'wb') as f:
                for chunk in resposta.iter_content(chunk_size=8192): f.write(chunk)
            
            hash_novo_arquivo = calcular_hash_arquivo(caminho_arquivo_temp)
            
            if manifesto.get(nome_base_arquivo) == hash_novo_arquivo:
                print("     -> Arquivo já existe e está atualizado. Pulando.")
                os.remove(caminho_arquivo_temp)
                continue
            else:
                print("     -> NOVO ARQUIVO ou ATUALIZAÇÃO detectada! Salvando e marcando para processamento.")
                os.rename(caminho_arquivo_temp, caminho_arquivo_final)
                manifesto[nome_base_arquivo] = hash_novo_arquivo
                arquivos_para_processar.append(caminho_arquivo_final)

        except requests.exceptions.RequestException as e:
            print(f"Falha no download de '{nome_base_arquivo}': {e}")
            if os.path.exists(caminho_arquivo_temp): os.remove(caminho_arquivo_temp)
    
    salvar_manifesto(manifesto)
    print(f"Verificação de downloads concluída. {len(arquivos_para_processar)} arquivos precisam ser processados.")
    return arquivos_para_processar

# --- Funções de Processamento (Inteligência de Dados) ---

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
            'local': encontrar_nome_coluna(df, ['Local'])
        }

        if mapa_colunas['municipio']:
            df_fortaleza = df[df[mapa_colunas['municipio']].astype(str).str.strip().str.lower() == 'fortaleza']
        else:
            print("  -> Aviso: Coluna 'Município' não encontrada. Impossível filtrar por Fortaleza. Pulando arquivo.")
            return

        for index, row in df_fortaleza.iterrows():
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
        print(f"  -> Processamento da planilha concluído. {eventos_novos} novos eventos salvos, {eventos_ignorados} duplicados ignorados.")
    except Exception as e:
        db.rollback()
        print(f"Erro ao ler ou processar a planilha: {e}")

def processar_pdf(caminho_arquivo, db):
    print(f"\n[Analisando PDF]: {os.path.basename(caminho_arquivo)}")
    print("    -> Lógica de extração de PDF a ser implementada.")
    pass

# --- Função Principal de Orquestração ---
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
    finally:
        if 'db' in locals() and db.is_active: db.close()
    print("\nProcessamento inteligente concluído.")

if __name__ == "__main__":
    links = encontrar_links_de_arquivos(URL_ALVOS)
    if links:
        arquivos_novos_ou_atualizados = baixar_e_validar_arquivos(links)
        processar_arquivos_baixados(arquivos_novos_ou_atualizados)
    print("\n--- OPERAÇÃO FINALIZADA ---")