# scripts/processar_estatisticas_sem_bd.py
"""
Script de Processamento - Versão SEM Banco de Dados
Apenas processa arquivos e gera relatórios JSON
"""

import sys
import os
import pandas as pd
from datetime import datetime
import glob

# Configuração do ambiente
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.banco_de_dados.data_processor import DataProcessor


def encontrar_nome_coluna(df, possiveis_nomes):
    """Encontra nome de coluna no DataFrame"""
    colunas_df = [str(col).lower().strip() for col in df.columns]
    for nome in possiveis_nomes:
        if nome.lower() in colunas_df:
            return df.columns[colunas_df.index(nome.lower())]
    return None


def processar_planilha_simples(caminho_arquivo: str):
    """
    Processa planilha e retorna DataFrame filtrado
    """
    print(f"\n{'='*60}")
    print(f"PROCESSANDO: {os.path.basename(caminho_arquivo)}")
    print(f"{'='*60}")

    try:
        # 1. Ler planilha
        df = pd.read_excel(caminho_arquivo, engine='openpyxl')
        print(f"[OK] Planilha lida: {len(df)} registros")

        # 2. Mapear colunas
        mapa_colunas = {
            'municipio': encontrar_nome_coluna(df, ['Município', 'Municipio']),
            'data': encontrar_nome_coluna(df, ['Data', 'Data Fato', 'Data da Ocorrência']),
            'hora': encontrar_nome_coluna(df, ['Hora Fato', 'Hora']),
            'dia_semana': encontrar_nome_coluna(df, ['Dia da Semana']),
            'natureza': encontrar_nome_coluna(df, ['Natureza', 'Natureza Crime']),
            'bairro': encontrar_nome_coluna(df, ['Bairro', 'Bairro Fato']),
            'ais': encontrar_nome_coluna(df, ['AIS']),
            'local': encontrar_nome_coluna(df, ['Local'])
        }

        if not mapa_colunas['municipio']:
            print("[AVISO] Coluna 'Municipio' nao encontrada. Pulando arquivo.")
            return None, None

        # 3. Filtrar apenas Fortaleza
        df_fortaleza = df[
            df[mapa_colunas['municipio']].astype(str).str.strip().str.lower() == 'fortaleza'
        ]

        print(f"[OK] Filtrados {len(df_fortaleza)} registros de Fortaleza")

        if len(df_fortaleza) == 0:
            print("[AVISO] Nenhum registro de Fortaleza encontrado.")
            return None, None

        return df_fortaleza, mapa_colunas

    except Exception as e:
        print(f"[ERRO] Erro ao processar planilha: {e}")
        import traceback
        traceback.print_exc()
        return None, None


def main():
    """
    Função principal - processa arquivos e gera relatórios
    """
    print("\n" + "="*60)
    print("PROCESSAMENTO DE DADOS SSPDS (Sem Banco de Dados)")
    print("="*60)
    print(f"Início: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

    # Pasta de dados
    PASTA_DOWNLOADS = os.path.join(os.path.dirname(__file__), '..', 'sspds_downloads')
    PASTA_RELATORIOS = os.path.join(os.path.dirname(__file__), '..', 'relatorios_sspds')
    os.makedirs(PASTA_RELATORIOS, exist_ok=True)

    # Buscar todos os arquivos Excel
    arquivos = glob.glob(os.path.join(PASTA_DOWNLOADS, "*.xlsx"))

    if not arquivos:
        print("[ERRO] Nenhum arquivo .xlsx encontrado em sspds_downloads/")
        return

    print(f"Encontrados {len(arquivos)} arquivos para processar\n")

    # Processador global
    processador_global = DataProcessor()
    arquivos_processados = 0
    total_registros = 0

    # Processar cada arquivo
    for arquivo in arquivos[:5]:  # Limita a 5 arquivos para teste
        df_filtrado, mapa_colunas = processar_planilha_simples(arquivo)

        if df_filtrado is not None and mapa_colunas is not None:
            # Processa estatísticas
            processador_arquivo = DataProcessor()
            processador_arquivo.process_dataframe(df_filtrado, mapa_colunas)

            # Mescla com processador global
            for key in processador_arquivo.statistics:
                if isinstance(processador_arquivo.statistics[key], dict):
                    if key not in processador_global.statistics:
                        processador_global.statistics[key] = {}

                    for sub_key, value in processador_arquivo.statistics[key].items():
                        if isinstance(value, dict):
                            if sub_key not in processador_global.statistics[key]:
                                processador_global.statistics[key][sub_key] = {}

                            for k, v in value.items():
                                if k not in processador_global.statistics[key][sub_key]:
                                    if isinstance(v, dict):
                                        processador_global.statistics[key][sub_key][k] = {}
                                    else:
                                        processador_global.statistics[key][sub_key][k] = 0

                                if isinstance(v, (int, float)):
                                    processador_global.statistics[key][sub_key][k] += v
                                elif isinstance(v, dict):
                                    for kk, vv in v.items():
                                        if kk not in processador_global.statistics[key][sub_key][k]:
                                            processador_global.statistics[key][sub_key][k][kk] = 0
                                        if isinstance(vv, (int, float)):
                                            processador_global.statistics[key][sub_key][k][kk] += vv

                        elif isinstance(value, (int, float)):
                            if sub_key not in processador_global.statistics[key]:
                                processador_global.statistics[key][sub_key] = 0
                            processador_global.statistics[key][sub_key] += value
                        elif isinstance(value, list):
                            if sub_key not in processador_global.statistics[key]:
                                processador_global.statistics[key][sub_key] = []

            arquivos_processados += 1
            total_registros += len(df_filtrado)

    # Recalcula rankings
    processador_global.calculate_rankings()

    # Análise Avançada
    print("\n\nANALISE AVANCADA")
    print("="*60)

    from app.banco_de_dados.data_analyzer import DataAnalyzer

    analisador = DataAnalyzer(processador_global.statistics)
    analisador.run_full_analysis()

    # Exportação
    print("\n\nEXPORTACAO DE RELATORIOS")
    print("="*60)

    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

    arquivo_stats = os.path.join(PASTA_RELATORIOS, f'estatisticas_{timestamp}.json')
    processador_global.export_statistics(arquivo_stats)

    arquivo_insights = os.path.join(PASTA_RELATORIOS, f'insights_{timestamp}.json')
    analisador.export_insights(arquivo_insights)

    # Resumo Final
    print("\n\n" + "="*60)
    print("RESUMO FINAL")
    print("="*60)
    print(f"Arquivos processados: {arquivos_processados}")
    print(f"Total de registros: {total_registros}")
    print(f"Relatórios salvos em: {PASTA_RELATORIOS}")

    processador_global.print_summary()
    analisador.print_summary()

    print("\nProcessamento finalizado com sucesso!")
    print(f"Termino: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60 + "\n")


if __name__ == "__main__":
    main()
