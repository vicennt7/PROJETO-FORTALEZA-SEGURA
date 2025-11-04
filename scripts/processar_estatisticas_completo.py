# scripts/processar_estatisticas_completo.py
"""
Script Principal - Pipeline Completo de Processamento de Dados SSPDS
Executa: Download -> Filtragem -> Processamento -> Análise -> Exportação
"""

import sys
import os
import pandas as pd
from datetime import datetime

# Configuração do ambiente
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.banco_de_dados.db_config import SessionLocal
from app.banco_de_dados.db_saida import Evento
from app.banco_de_dados.data_filter import DataFilter
from app.banco_de_dados.data_processor import DataProcessor
from app.banco_de_dados.data_analyzer import DataAnalyzer

# Importa funções do script original
from carregar_estatisticas_sspds import (
    encontrar_links_de_arquivos,
    baixar_e_validar_arquivos,
    encontrar_nome_coluna,
    URL_ALVOS,
    PASTA_DOWNLOADS
)


def processar_planilha_completo(caminho_arquivo: str, db_session: Session):
    """
    Processa planilha com pipeline completo:
    1. Leitura
    2. Filtragem e remoção de duplicados
    3. Extração de estatísticas
    4. Salvamento no banco
    """
    print(f"\n{'='*60}")
    print(f"PROCESSANDO: {os.path.basename(caminho_arquivo)}")
    print(f"{'='*60}")

    try:
        # 1. Ler planilha
        df = pd.read_excel(caminho_arquivo, engine='openpyxl')
        print(f"✓ Planilha lida: {len(df)} registros")

        # 2. Mapear colunas
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

        if not mapa_colunas['municipio']:
            print("⚠️ Coluna 'Município' não encontrada. Pulando arquivo.")
            return None, None

        # 3. Filtrar e limpar dados
        filtrador = DataFilter(db_session)

        df_limpo = filtrador.filter_and_clean(
            df=df,
            source_file=os.path.basename(caminho_arquivo),
            municipio_col=mapa_colunas['municipio'],
            required_columns=mapa_colunas
        )

        if len(df_limpo) == 0:
            print("⚠️ Nenhum registro válido após filtragem.")
            return filtrador, None

        # 4. Processar estatísticas
        processador = DataProcessor()
        processador.process_dataframe(df_limpo, mapa_colunas)

        # 5. Salvar no banco de dados
        eventos_salvos = salvar_eventos_no_banco(
            df_limpo,
            mapa_colunas,
            os.path.basename(caminho_arquivo),
            db_session
        )

        print(f"✅ {eventos_salvos} novos eventos salvos no banco de dados")

        return filtrador, processador

    except Exception as e:
        print(f"❌ Erro ao processar planilha: {e}")
        import traceback
        traceback.print_exc()
        return None, None


def salvar_eventos_no_banco(df: pd.DataFrame, mapa_colunas: dict, nome_arquivo: str, db_session: Session) -> int:
    """
    Salva eventos filtrados no banco de dados
    """
    import hashlib
    from datetime import datetime as dt

    eventos_salvos = 0

    for index, row in df.iterrows():
        # Gera hash único
        string_unica = str(row.to_dict()) + nome_arquivo
        hash_do_evento = hashlib.md5(string_unica.encode('utf-8')).hexdigest()

        # Verifica se já existe
        evento_existente = db_session.query(Evento).filter(
            Evento.hash_origem == hash_do_evento
        ).first()

        if evento_existente:
            continue

        # Processa data e hora
        data_str = str(row[mapa_colunas['data']]) if mapa_colunas['data'] and pd.notna(row[mapa_colunas['data']]) else None
        hora_str = str(row[mapa_colunas['hora']]) if mapa_colunas['hora'] and pd.notna(row[mapa_colunas['hora']]) else None

        data_evento_final = None
        if data_str:
            try:
                data_temp = pd.to_datetime(data_str.split(" ")[0])
                if hora_str:
                    hora_temp = pd.to_datetime(hora_str).time()
                    data_evento_final = dt.combine(data_temp.date(), hora_temp)
                else:
                    data_evento_final = data_temp
            except (ValueError, TypeError):
                data_evento_final = None

        # Cria novo evento
        novo_evento = Evento(
            hash_origem=hash_do_evento,
            tipo_fonte="SSPDS",
            nome_fonte=nome_arquivo,
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

        db_session.add(novo_evento)
        eventos_salvos += 1

    db_session.commit()
    return eventos_salvos


def main():
    """
    Função principal - executa pipeline completo
    """
    print("\n" + "="*60)
    print("PIPELINE COMPLETO DE PROCESSAMENTO - SSPDS")
    print("="*60)
    print(f"Início: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

    # Pasta de saída para relatórios
    PASTA_RELATORIOS = os.path.join(os.path.dirname(__file__), '..', 'relatorios_sspds')
    os.makedirs(PASTA_RELATORIOS, exist_ok=True)

    # FASE 1: Download de arquivos
    print("\n📥 FASE 1: DOWNLOAD DE ARQUIVOS")
    print("="*60)

    links = encontrar_links_de_arquivos(URL_ALVOS)

    if not links:
        print("❌ Nenhum link encontrado. Encerrando.")
        return

    arquivos_novos = baixar_e_validar_arquivos(links)

    # Se não houver arquivos novos, processar todos os existentes
    if not arquivos_novos:
        print("\n⚠️ Nenhum arquivo novo detectado.")
        print("   Processando todos os arquivos existentes...")

        import glob
        arquivos_novos = glob.glob(os.path.join(PASTA_DOWNLOADS, "*.xlsx"))

    if not arquivos_novos:
        print("❌ Nenhum arquivo para processar. Encerrando.")
        return

    # FASE 2: Processamento com filtragem e análise
    print("\n\n📊 FASE 2: PROCESSAMENTO E ANÁLISE")
    print("="*60)

    db_session = SessionLocal()

    processador_global = DataProcessor()
    filtrador_global = DataFilter(db_session)

    arquivos_processados = 0

    try:
        for arquivo in arquivos_novos:
            if not arquivo.lower().endswith('.xlsx'):
                continue

            filtrador_arquivo, processador_arquivo = processar_planilha_completo(arquivo, db_session)

            if processador_arquivo:
                # Mescla estatísticas no processador global
                for key in processador_arquivo.statistics:
                    if isinstance(processador_arquivo.statistics[key], dict):
                        if key not in processador_global.statistics:
                            processador_global.statistics[key] = {}

                        for sub_key, value in processador_arquivo.statistics[key].items():
                            if sub_key not in processador_global.statistics[key]:
                                processador_global.statistics[key][sub_key] = 0

                            if isinstance(value, (int, float)):
                                processador_global.statistics[key][sub_key] += value
                            elif isinstance(value, dict):
                                if not isinstance(processador_global.statistics[key][sub_key], dict):
                                    processador_global.statistics[key][sub_key] = {}
                                for k, v in value.items():
                                    if k not in processador_global.statistics[key][sub_key]:
                                        processador_global.statistics[key][sub_key] = 0
                                    processador_global.statistics[key][sub_key] += v if isinstance(v, (int, float)) else 0

                arquivos_processados += 1

            if filtrador_arquivo:
                # Mescla stats de filtragem
                for key in filtrador_arquivo.stats:
                    filtrador_global.stats[key] += filtrador_arquivo.stats[key]

    finally:
        db_session.close()

    # Recalcula rankings após mesclar tudo
    processador_global.calculate_rankings()

    # FASE 3: Análise Avançada
    print("\n\n🔍 FASE 3: ANÁLISE AVANÇADA")
    print("="*60)

    analisador = DataAnalyzer(processador_global.statistics)
    analisador.run_full_analysis()

    # FASE 4: Exportação de Relatórios
    print("\n\n💾 FASE 4: EXPORTAÇÃO DE RELATÓRIOS")
    print("="*60)

    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

    # Exporta estatísticas
    arquivo_stats = os.path.join(PASTA_RELATORIOS, f'estatisticas_{timestamp}.json')
    processador_global.export_statistics(arquivo_stats)

    # Exporta insights
    arquivo_insights = os.path.join(PASTA_RELATORIOS, f'insights_{timestamp}.json')
    analisador.export_insights(arquivo_insights)

    # FASE 5: Resumo Final
    print("\n\n" + "="*60)
    print("RESUMO FINAL DO PROCESSAMENTO")
    print("="*60)

    filtrador_global.print_summary()
    processador_global.print_summary()
    analisador.print_summary()

    print("\n" + "="*60)
    print("PIPELINE FINALIZADO COM SUCESSO")
    print("="*60)
    print(f"Arquivos processados: {arquivos_processados}")
    print(f"Relatórios salvos em: {PASTA_RELATORIOS}")
    print(f"Término: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60 + "\n")


if __name__ == "__main__":
    main()
