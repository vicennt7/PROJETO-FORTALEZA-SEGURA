# app/banco_de_dados/data_analyzer.py
"""
Analisador Avançado de Estatísticas
Gera análises detalhadas por localização, horário, padrões temporais, etc.
"""

import pandas as pd
import json
from typing import Dict, List, Tuple
from datetime import datetime


class DataAnalyzer:
    """Analisador que gera insights avançados dos dados"""

    def __init__(self, statistics: Dict):
        self.stats = statistics
        self.insights = {
            'padroes_temporais': {},
            'analise_espacial': {},
            'correlacoes': {},
            'alertas': [],
            'recomendacoes': []
        }

    def analyze_temporal_patterns(self):
        """
        Analisa padrões temporais (horários/dias mais perigosos)
        """
        print("\n[Analisando padrões temporais...]")

        # Identifica horário mais perigoso
        if self.stats.get('horarios_mais_perigosos'):
            horario_pico = self.stats['horarios_mais_perigosos'][0]
            self.insights['padroes_temporais']['horario_pico'] = horario_pico

            self.insights['alertas'].append({
                'tipo': 'Horário de Risco',
                'mensagem': f"Horário mais perigoso: {horario_pico['horario']} com {horario_pico['total']} ocorrências"
            })

        # Identifica período do dia mais perigoso
        if self.stats.get('por_periodo_dia'):
            periodo_mais_perigoso = max(
                self.stats['por_periodo_dia'].items(),
                key=lambda x: x[1]
            )

            self.insights['padroes_temporais']['periodo_mais_perigoso'] = {
                'periodo': periodo_mais_perigoso[0],
                'total': periodo_mais_perigoso[1]
            }

            self.insights['recomendacoes'].append({
                'area': 'Segurança Temporal',
                'recomendacao': f"Aumentar policiamento no período: {periodo_mais_perigoso[0]}"
            })

        # Identifica dia da semana mais perigoso
        if self.stats.get('por_dia_semana'):
            dia_mais_perigoso = max(
                self.stats['por_dia_semana'].items(),
                key=lambda x: x[1]
            )

            self.insights['padroes_temporais']['dia_mais_perigoso'] = {
                'dia': dia_mais_perigoso[0],
                'total': dia_mais_perigoso[1]
            }

        # Analisa tendência mensal
        if self.stats.get('por_mes'):
            meses_ordenados = ['Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho',
                              'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro']

            meses_com_dados = {
                mes: self.stats['por_mes'].get(mes, 0)
                for mes in meses_ordenados
            }

            mes_mais_perigoso = max(meses_com_dados.items(), key=lambda x: x[1])
            mes_mais_seguro = min(
                [(m, v) for m, v in meses_com_dados.items() if v > 0],
                key=lambda x: x[1],
                default=(None, 0)
            )

            self.insights['padroes_temporais']['mes_mais_perigoso'] = {
                'mes': mes_mais_perigoso[0],
                'total': mes_mais_perigoso[1]
            }

            if mes_mais_seguro[0]:
                self.insights['padroes_temporais']['mes_mais_seguro'] = {
                    'mes': mes_mais_seguro[0],
                    'total': mes_mais_seguro[1]
                }

        print("   ✓ Análise temporal concluída")

    def analyze_spatial_patterns(self):
        """
        Analisa padrões espaciais (bairros, AIS)
        """
        print("\n[Analisando padrões espaciais...]")

        # Identifica zonas de alto risco
        if self.stats.get('bairros_mais_perigosos'):
            top_5_bairros = self.stats['bairros_mais_perigosos'][:5]

            self.insights['analise_espacial']['zonas_criticas'] = top_5_bairros

            for bairro_data in top_5_bairros[:3]:
                self.insights['alertas'].append({
                    'tipo': 'Zona de Alto Risco',
                    'mensagem': f"Bairro {bairro_data['bairro']}: {bairro_data['total_crimes']} crimes registrados"
                })

                self.insights['recomendacoes'].append({
                    'area': 'Policiamento Espacial',
                    'recomendacao': f"Intensificar patrulhamento no bairro {bairro_data['bairro']}"
                })

        # Analisa distribuição por AIS
        if self.stats.get('por_ais'):
            ais_mais_perigosa = max(
                self.stats['por_ais'].items(),
                key=lambda x: x[1]
            )

            self.insights['analise_espacial']['ais_mais_perigosa'] = {
                'ais': ais_mais_perigosa[0],
                'total': ais_mais_perigosa[1]
            }

        # Identifica bairros com tipos específicos de crime
        if self.stats.get('por_bairro'):
            bairros_por_tipo_crime = {}

            for bairro, dados in self.stats['por_bairro'].items():
                if dados.get('tipos_crime'):
                    crime_principal = max(
                        dados['tipos_crime'].items(),
                        key=lambda x: x[1]
                    )

                    if crime_principal[0] not in bairros_por_tipo_crime:
                        bairros_por_tipo_crime[crime_principal[0]] = []

                    bairros_por_tipo_crime[crime_principal[0]].append({
                        'bairro': bairro,
                        'total': crime_principal[1]
                    })

            self.insights['analise_espacial']['bairros_por_tipo_crime'] = bairros_por_tipo_crime

        print("   ✓ Análise espacial concluída")

    def analyze_crime_correlations(self):
        """
        Analisa correlações entre tipos de crime, local e horário
        """
        print("\n[Analisando correlações...]")

        # Crimes mais comuns por período
        if self.stats.get('por_bairro'):
            crimes_por_periodo = {}

            for bairro, dados in self.stats['por_bairro'].items():
                if dados.get('por_periodo'):
                    for periodo, total in dados['por_periodo'].items():
                        if periodo not in crimes_por_periodo:
                            crimes_por_periodo[periodo] = 0
                        crimes_por_periodo[periodo] += total

            if crimes_por_periodo:
                self.insights['correlacoes']['crimes_por_periodo'] = crimes_por_periodo

        print("   ✓ Análise de correlações concluída")

    def generate_risk_score(self):
        """
        Gera score de risco para cada bairro
        """
        print("\n[Gerando scores de risco...]")

        if not self.stats.get('por_bairro'):
            return

        # Calcula total de crimes
        total_crimes = sum(
            dados['total_crimes']
            for dados in self.stats['por_bairro'].values()
        )

        bairros_com_score = []

        for bairro, dados in self.stats['por_bairro'].items():
            # Score baseado em:
            # 1. Porcentagem do total de crimes
            # 2. Diversidade de tipos de crime
            # 3. Crimes em horários perigosos (noite/madrugada)

            percentual_crimes = (dados['total_crimes'] / total_crimes) * 100

            diversidade = len(dados.get('tipos_crime', {}))

            crimes_noturnos = (
                dados.get('por_periodo', {}).get('Noite (18h-00h)', 0) +
                dados.get('por_periodo', {}).get('Madrugada (00h-06h)', 0)
            )

            # Score de 0 a 100
            score = min(100, (
                (percentual_crimes * 0.5) +
                (diversidade * 2) +
                (crimes_noturnos / dados['total_crimes'] * 30 if dados['total_crimes'] > 0 else 0)
            ))

            nivel_risco = 'BAIXO'
            if score > 70:
                nivel_risco = 'CRÍTICO'
            elif score > 50:
                nivel_risco = 'ALTO'
            elif score > 30:
                nivel_risco = 'MÉDIO'

            bairros_com_score.append({
                'bairro': bairro,
                'score': round(score, 2),
                'nivel': nivel_risco,
                'total_crimes': dados['total_crimes']
            })

        # Ordena por score
        bairros_com_score.sort(key=lambda x: x['score'], reverse=True)

        self.insights['analise_espacial']['ranking_risco'] = bairros_com_score

        # Gera alertas para bairros críticos
        for bairro_data in bairros_com_score:
            if bairro_data['nivel'] == 'CRÍTICO':
                self.insights['alertas'].append({
                    'tipo': 'Risco Crítico',
                    'mensagem': f"Bairro {bairro_data['bairro']} está em nível CRÍTICO (score: {bairro_data['score']})"
                })

        print("   ✓ Scores de risco calculados")

    def generate_security_recommendations(self):
        """
        Gera recomendações de segurança baseadas nas análises
        """
        print("\n[Gerando recomendações de segurança...]")

        # Recomendações baseadas em padrões temporais
        if self.insights['padroes_temporais'].get('periodo_mais_perigoso'):
            periodo = self.insights['padroes_temporais']['periodo_mais_perigoso']['periodo']
            self.insights['recomendacoes'].append({
                'area': 'Estratégia Temporal',
                'recomendacao': f"Implementar rondas frequentes durante {periodo}"
            })

        # Recomendações baseadas em crimes mais comuns
        if self.stats.get('crimes_mais_comuns'):
            top_crime = self.stats['crimes_mais_comuns'][0]
            self.insights['recomendacoes'].append({
                'area': 'Prevenção Específica',
                'recomendacao': f"Criar campanhas de prevenção contra: {top_crime['crime']}"
            })

        # Recomendações baseadas em zonas críticas
        if self.insights['analise_espacial'].get('ranking_risco'):
            bairros_criticos = [
                b for b in self.insights['analise_espacial']['ranking_risco']
                if b['nivel'] == 'CRÍTICO'
            ]

            if bairros_criticos:
                self.insights['recomendacoes'].append({
                    'area': 'Distribuição de Recursos',
                    'recomendacao': f"Alocar recursos prioritários para {len(bairros_criticos)} bairros em nível crítico"
                })

        print("   ✓ Recomendações geradas")

    def run_full_analysis(self):
        """
        Executa análise completa
        """
        print("\n" + "="*60)
        print("INICIANDO ANÁLISE AVANÇADA DE DADOS")
        print("="*60)

        self.analyze_temporal_patterns()
        self.analyze_spatial_patterns()
        self.analyze_crime_correlations()
        self.generate_risk_score()
        self.generate_security_recommendations()

        print("\n✅ Análise completa finalizada")

    def export_insights(self, output_file: str):
        """
        Exporta insights para arquivo JSON
        """
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(self.insights, f, indent=4, ensure_ascii=False)

        print(f"\n✅ Insights exportados para: {output_file}")

    def print_summary(self):
        """
        Imprime resumo dos insights
        """
        print("\n" + "="*60)
        print("RESUMO DOS INSIGHTS GERADOS")
        print("="*60)

        # Alertas
        if self.insights.get('alertas'):
            print(f"\n🚨 ALERTAS CRÍTICOS ({len(self.insights['alertas'])}):")
            for i, alerta in enumerate(self.insights['alertas'][:5], 1):
                print(f"   {i}. [{alerta['tipo']}] {alerta['mensagem']}")

        # Recomendações
        if self.insights.get('recomendacoes'):
            print(f"\n💡 RECOMENDAÇÕES ({len(self.insights['recomendacoes'])}):")
            for i, rec in enumerate(self.insights['recomendacoes'][:5], 1):
                print(f"   {i}. [{rec['area']}] {rec['recomendacao']}")

        # Top 5 bairros de maior risco
        if self.insights.get('analise_espacial', {}).get('ranking_risco'):
            print("\n⚠️ TOP 5 BAIRROS DE MAIOR RISCO:")
            for i, bairro in enumerate(self.insights['analise_espacial']['ranking_risco'][:5], 1):
                print(f"   {i}. {bairro['bairro']}: Score {bairro['score']} - Nível {bairro['nivel']}")

        print("\n" + "="*60 + "\n")
