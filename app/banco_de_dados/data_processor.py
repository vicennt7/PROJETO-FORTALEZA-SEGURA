# app/banco_de_dados/data_processor.py
"""
Processador de Dados - Extrai estatísticas detalhadas
Analisa dados por bairro, localização, horário, tipo de crime, etc.
"""

import pandas as pd
import json
from datetime import datetime, time
from typing import Dict, List
from collections import defaultdict


class DataProcessor:
    """Processador que extrai estatísticas detalhadas dos dados"""

    def __init__(self):
        self.statistics = {
            'por_bairro': {},
            'por_natureza': {},
            'por_horario': {},
            'por_dia_semana': {},
            'por_ais': {},
            'por_periodo_dia': {},
            'por_mes': {},
            'por_ano': {},
            'crimes_mais_comuns': [],
            'bairros_mais_perigosos': [],
            'horarios_mais_perigosos': []
        }

    def classify_time_period(self, hour_value) -> str:
        """
        Classifica horário em período do dia
        """
        if pd.isna(hour_value):
            return "Não informado"

        try:
            if isinstance(hour_value, time):
                hour = hour_value.hour
            elif isinstance(hour_value, datetime):
                hour = hour_value.hour
            elif isinstance(hour_value, str):
                # Tenta parsear string como horário
                time_obj = pd.to_datetime(hour_value).time()
                hour = time_obj.hour
            else:
                hour = int(hour_value)

            if 0 <= hour < 6:
                return "Madrugada (00h-06h)"
            elif 6 <= hour < 12:
                return "Manhã (06h-12h)"
            elif 12 <= hour < 18:
                return "Tarde (12h-18h)"
            else:
                return "Noite (18h-00h)"

        except:
            return "Não informado"

    def extract_month_year(self, date_value):
        """
        Extrai mês e ano de uma data
        """
        if pd.isna(date_value):
            return None, None

        try:
            if isinstance(date_value, str):
                date_obj = pd.to_datetime(date_value)
            else:
                date_obj = date_value

            return date_obj.month, date_obj.year
        except:
            return None, None

    def process_by_bairro(self, df: pd.DataFrame, bairro_col: str, natureza_col: str = None):
        """
        Processa estatísticas por bairro
        """
        if not bairro_col or bairro_col not in df.columns:
            return

        for bairro in df[bairro_col].dropna().unique():
            bairro_str = str(bairro).strip()
            if bairro_str == '' or bairro_str.lower() == 'nan':
                continue

            df_bairro = df[df[bairro_col] == bairro]

            if bairro_str not in self.statistics['por_bairro']:
                self.statistics['por_bairro'][bairro_str] = {
                    'total_crimes': 0,
                    'tipos_crime': {},
                    'por_periodo': {
                        'Madrugada (00h-06h)': 0,
                        'Manhã (06h-12h)': 0,
                        'Tarde (12h-18h)': 0,
                        'Noite (18h-00h)': 0
                    }
                }

            self.statistics['por_bairro'][bairro_str]['total_crimes'] += len(df_bairro)

            # Tipos de crime por bairro
            if natureza_col and natureza_col in df.columns:
                for natureza in df_bairro[natureza_col].dropna():
                    natureza_str = str(natureza).strip()
                    if natureza_str not in self.statistics['por_bairro'][bairro_str]['tipos_crime']:
                        self.statistics['por_bairro'][bairro_str]['tipos_crime'][natureza_str] = 0
                    self.statistics['por_bairro'][bairro_str]['tipos_crime'][natureza_str] += 1

    def process_by_natureza(self, df: pd.DataFrame, natureza_col: str):
        """
        Processa estatísticas por natureza/tipo de crime
        """
        if not natureza_col or natureza_col not in df.columns:
            return

        for natureza in df[natureza_col].dropna():
            natureza_str = str(natureza).strip()
            if natureza_str == '' or natureza_str.lower() == 'nan':
                continue

            if natureza_str not in self.statistics['por_natureza']:
                self.statistics['por_natureza'][natureza_str] = 0

            self.statistics['por_natureza'][natureza_str] += 1

    def process_by_horario(self, df: pd.DataFrame, hora_col: str):
        """
        Processa estatísticas por horário
        """
        if not hora_col or hora_col not in df.columns:
            return

        for hora in df[hora_col].dropna():
            periodo = self.classify_time_period(hora)

            if periodo not in self.statistics['por_periodo_dia']:
                self.statistics['por_periodo_dia'][periodo] = 0

            self.statistics['por_periodo_dia'][periodo] += 1

            # Estatística por hora específica
            try:
                if isinstance(hora, time):
                    hora_int = hora.hour
                elif isinstance(hora, datetime):
                    hora_int = hora.hour
                else:
                    hora_int = pd.to_datetime(str(hora)).hour

                hora_str = f"{hora_int:02d}:00"

                if hora_str not in self.statistics['por_horario']:
                    self.statistics['por_horario'][hora_str] = 0

                self.statistics['por_horario'][hora_str] += 1
            except:
                pass

    def process_by_dia_semana(self, df: pd.DataFrame, dia_col: str):
        """
        Processa estatísticas por dia da semana
        """
        if not dia_col or dia_col not in df.columns:
            return

        for dia in df[dia_col].dropna():
            dia_str = str(dia).strip()
            if dia_str == '' or dia_str.lower() == 'nan':
                continue

            if dia_str not in self.statistics['por_dia_semana']:
                self.statistics['por_dia_semana'][dia_str] = 0

            self.statistics['por_dia_semana'][dia_str] += 1

    def process_by_ais(self, df: pd.DataFrame, ais_col: str):
        """
        Processa estatísticas por AIS (Área Integrada de Segurança)
        """
        if not ais_col or ais_col not in df.columns:
            return

        for ais in df[ais_col].dropna():
            ais_str = str(ais).strip()
            if ais_str == '' or ais_str.lower() == 'nan':
                continue

            if ais_str not in self.statistics['por_ais']:
                self.statistics['por_ais'][ais_str] = 0

            self.statistics['por_ais'][ais_str] += 1

    def process_by_date(self, df: pd.DataFrame, data_col: str):
        """
        Processa estatísticas por mês e ano
        """
        if not data_col or data_col not in df.columns:
            return

        for data in df[data_col].dropna():
            mes, ano = self.extract_month_year(data)

            if mes and ano:
                mes_nome = [
                    'Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho',
                    'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro'
                ][mes - 1]

                # Por mês
                if mes_nome not in self.statistics['por_mes']:
                    self.statistics['por_mes'][mes_nome] = 0
                self.statistics['por_mes'][mes_nome] += 1

                # Por ano
                ano_str = str(ano)
                if ano_str not in self.statistics['por_ano']:
                    self.statistics['por_ano'][ano_str] = 0
                self.statistics['por_ano'][ano_str] += 1

    def calculate_rankings(self):
        """
        Calcula rankings (top crimes, bairros mais perigosos, etc.)
        """
        # Top 10 crimes mais comuns
        if self.statistics['por_natureza']:
            sorted_crimes = sorted(
                self.statistics['por_natureza'].items(),
                key=lambda x: x[1],
                reverse=True
            )
            self.statistics['crimes_mais_comuns'] = [
                {'crime': crime, 'total': count}
                for crime, count in sorted_crimes[:10]
            ]

        # Top 10 bairros mais perigosos
        if self.statistics['por_bairro']:
            sorted_bairros = sorted(
                self.statistics['por_bairro'].items(),
                key=lambda x: x[1]['total_crimes'],
                reverse=True
            )
            self.statistics['bairros_mais_perigosos'] = [
                {'bairro': bairro, 'total_crimes': data['total_crimes']}
                for bairro, data in sorted_bairros[:10]
            ]

        # Top 10 horários mais perigosos
        if self.statistics['por_horario']:
            sorted_horarios = sorted(
                self.statistics['por_horario'].items(),
                key=lambda x: x[1],
                reverse=True
            )
            self.statistics['horarios_mais_perigosos'] = [
                {'horario': hora, 'total': count}
                for hora, count in sorted_horarios[:10]
            ]

    def process_dataframe(
        self,
        df: pd.DataFrame,
        column_map: Dict[str, str]
    ):
        """
        Processa DataFrame completo extraindo todas as estatísticas
        """
        print(f"\n[Processando estatísticas de {len(df)} registros]")

        # Processa cada tipo de estatística
        self.process_by_bairro(df, column_map.get('bairro'), column_map.get('natureza'))
        self.process_by_natureza(df, column_map.get('natureza'))
        self.process_by_horario(df, column_map.get('hora'))
        self.process_by_dia_semana(df, column_map.get('dia_semana'))
        self.process_by_ais(df, column_map.get('ais'))
        self.process_by_date(df, column_map.get('data'))

        # Calcula rankings
        self.calculate_rankings()

        print("   ✅ Processamento de estatísticas concluído")

    def export_statistics(self, output_file: str):
        """
        Exporta estatísticas para arquivo JSON
        """
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(self.statistics, f, indent=4, ensure_ascii=False)

        print(f"\n✅ Estatísticas exportadas para: {output_file}")

    def print_summary(self):
        """
        Imprime resumo das estatísticas
        """
        print("\n" + "="*60)
        print("RESUMO DAS ESTATÍSTICAS PROCESSADAS")
        print("="*60)

        if self.statistics['crimes_mais_comuns']:
            print("\n🔴 TOP 5 CRIMES MAIS COMUNS:")
            for i, crime_data in enumerate(self.statistics['crimes_mais_comuns'][:5], 1):
                print(f"   {i}. {crime_data['crime']}: {crime_data['total']} ocorrências")

        if self.statistics['bairros_mais_perigosos']:
            print("\n📍 TOP 5 BAIRROS COM MAIS OCORRÊNCIAS:")
            for i, bairro_data in enumerate(self.statistics['bairros_mais_perigosos'][:5], 1):
                print(f"   {i}. {bairro_data['bairro']}: {bairro_data['total_crimes']} crimes")

        if self.statistics['por_periodo_dia']:
            print("\n🕐 CRIMES POR PERÍODO DO DIA:")
            for periodo, total in sorted(self.statistics['por_periodo_dia'].items(), key=lambda x: x[1], reverse=True):
                print(f"   {periodo}: {total} ocorrências")

        if self.statistics['por_dia_semana']:
            print("\n📅 CRIMES POR DIA DA SEMANA:")
            for dia, total in sorted(self.statistics['por_dia_semana'].items(), key=lambda x: x[1], reverse=True):
                print(f"   {dia}: {total} ocorrências")

        print("\n" + "="*60 + "\n")
