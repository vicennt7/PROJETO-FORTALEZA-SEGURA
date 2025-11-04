# scripts/run_processing.py
"""
Wrapper para executar processamento com encoding UTF-8
"""

import sys
import os

# Força encoding UTF-8
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')
if sys.stderr.encoding != 'utf-8':
    sys.stderr.reconfigure(encoding='utf-8')

# Agora importa e executa o script principal
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pandas as pd
import glob
from datetime import datetime
from app.banco_de_dados.data_processor import DataProcessor
from app.banco_de_dados.data_analyzer import DataAnalyzer


def encontrar_nome_coluna(df, possiveis_nomes):
    """Encontra nome de coluna no DataFrame"""
    colunas_df = [str(col).lower().strip() for col in df.columns]
    for nome in possiveis_nomes:
        if nome.lower() in colunas_df:
            return df.columns[colunas_df.index(nome.lower())]
    return None


def processar_planilha(caminho_arquivo: str):
    """Processa planilha e retorna DataFrame filtrado"""
    print(f"\n{'='*60}")
    print(f"PROCESSANDO: {os.path.basename(caminho_arquivo)}")
    print(f"{'='*60}")

    try:
        df = pd.read_excel(caminho_arquivo, engine='openpyxl')
        print(f"[OK] Planilha lida: {len(df)} registros")

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
            print("[AVISO] Coluna 'Municipio' nao encontrada.")
            return None, None

        df_fortaleza = df[
            df[mapa_colunas['municipio']].astype(str).str.strip().str.lower() == 'fortaleza'
        ]

        print(f"[OK] Filtrados {len(df_fortaleza)} registros de Fortaleza")

        if len(df_fortaleza) == 0:
            return None, None

        return df_fortaleza, mapa_colunas

    except Exception as e:
        print(f"[ERRO] {e}")
        return None, None


def main():
    print("\n" + "="*60)
    print("PROCESSAMENTO DE DADOS SSPDS")
    print("="*60)
    print(f"Inicio: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

    PASTA_DOWNLOADS = os.path.join(os.path.dirname(__file__), '..', 'sspds_downloads')
    PASTA_RELATORIOS = os.path.join(os.path.dirname(__file__), '..', 'relatorios_sspds')
    os.makedirs(PASTA_RELATORIOS, exist_ok=True)

    arquivos = glob.glob(os.path.join(PASTA_DOWNLOADS, "*.xlsx"))

    if not arquivos:
        print("[ERRO] Nenhum arquivo encontrado")
        return

    print(f"Encontrados {len(arquivos)} arquivos\n")

    processador_global = DataProcessor()
    total_registros = 0

    # Processa primeiros 3 arquivos como teste
    for arquivo in arquivos[:3]:
        df_filtrado, mapa_colunas = processar_planilha(arquivo)

        if df_filtrado is not None:
            processador = DataProcessor()
            processador.process_dataframe(df_filtrado, mapa_colunas)
            total_registros += len(df_filtrado)

            # Mescla estatísticas
            for key in ['por_natureza', 'por_horario', 'por_dia_semana', 'por_ais', 'por_mes', 'por_ano']:
                if key in processador.statistics:
                    if key not in processador_global.statistics:
                        processador_global.statistics[key] = {}
                    for k, v in processador.statistics[key].items():
                        processador_global.statistics[key][k] = processador_global.statistics[key].get(k, 0) + v

            # Mescla bairros
            if 'por_bairro' in processador.statistics:
                for bairro, dados in processador.statistics['por_bairro'].items():
                    if bairro not in processador_global.statistics['por_bairro']:
                        processador_global.statistics['por_bairro'][bairro] = {
                            'total_crimes': 0,
                            'tipos_crime': {}
                        }
                    processador_global.statistics['por_bairro'][bairro]['total_crimes'] += dados.get('total_crimes', 0)

                    for crime, qtd in dados.get('tipos_crime', {}).items():
                        if crime not in processador_global.statistics['por_bairro'][bairro]['tipos_crime']:
                            processador_global.statistics['por_bairro'][bairro]['tipos_crime'][crime] = 0
                        processador_global.statistics['por_bairro'][bairro]['tipos_crime'][crime] += qtd

    processador_global.calculate_rankings()

    print("\n" + "="*60)
    print("ANALISE AVANCADA")
    print("="*60)

    analisador = DataAnalyzer(processador_global.statistics)
    analisador.run_full_analysis()

    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

    arquivo_stats = os.path.join(PASTA_RELATORIOS, f'estatisticas_{timestamp}.json')
    processador_global.export_statistics(arquivo_stats)

    arquivo_insights = os.path.join(PASTA_RELATORIOS, f'insights_{timestamp}.json')
    analisador.export_insights(arquivo_insights)

    print("\n" + "="*60)
    print("RESUMO FINAL")
    print("="*60)
    print(f"Total de registros processados: {total_registros}")
    print(f"Relatorios salvos em: {PASTA_RELATORIOS}\n")

    processador_global.print_summary()
    analisador.print_summary()

    print(f"\nTermino: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60)


if __name__ == "__main__":
    main()
