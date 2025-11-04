# dashboard_streamlit.py
"""
Dashboard Streamlit - Fortaleza Segura
Visualização interativa dos dados de segurança pública
"""

import streamlit as st
import pandas as pd
import json
import glob
import os
from datetime import datetime

# Configuração da página
st.set_page_config(
    page_title="Fortaleza Segura - Dashboard",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- FUNÇÕES AUXILIARES ---

@st.cache_data
def carregar_ultimas_estatisticas():
    """Carrega o arquivo de estatísticas mais recente"""
    pasta_relatorios = "relatorios_sspds"

    if not os.path.exists(pasta_relatorios):
        return None

    arquivos = glob.glob(os.path.join(pasta_relatorios, "estatisticas_*.json"))

    if not arquivos:
        return None

    # Pega o arquivo mais recente
    arquivo_mais_recente = max(arquivos, key=os.path.getmtime)

    with open(arquivo_mais_recente, 'r', encoding='utf-8') as f:
        return json.load(f)

@st.cache_data
def carregar_ultimos_insights():
    """Carrega o arquivo de insights mais recente"""
    pasta_relatorios = "relatorios_sspds"

    if not os.path.exists(pasta_relatorios):
        return None

    arquivos = glob.glob(os.path.join(pasta_relatorios, "insights_*.json"))

    if not arquivos:
        return None

    arquivo_mais_recente = max(arquivos, key=os.path.getmtime)

    with open(arquivo_mais_recente, 'r', encoding='utf-8') as f:
        return json.load(f)

def criar_df_horarios(dados_horarios):
    """Converte dados de horários em DataFrame para gráficos"""
    if not dados_horarios:
        return pd.DataFrame()

    df = pd.DataFrame(list(dados_horarios.items()), columns=['Horário', 'Ocorrências'])
    df = df.sort_values('Horário')
    return df

def criar_df_ranking(dados):
    """Converte dados de ranking em DataFrame"""
    if not dados:
        return pd.DataFrame()

    df = pd.DataFrame(dados)
    return df

# --- INTERFACE DO DASHBOARD ---

# Cabeçalho
st.title("🛡️ Fortaleza Segura - Dashboard de Segurança Pública")
st.markdown("---")

# Sidebar com informações
with st.sidebar:
    st.header("ℹ️ Informações")
    st.write("Dashboard de monitoramento de segurança pública de Fortaleza")

    if st.button("🔄 Recarregar Dados"):
        st.cache_data.clear()
        st.rerun()

    st.markdown("---")
    st.info(f"Última atualização: {datetime.now().strftime('%d/%m/%Y %H:%M')}")

# Carregar dados
estatisticas = carregar_ultimas_estatisticas()
insights = carregar_ultimos_insights()

if estatisticas is None:
    st.error("⚠️ Nenhum dado encontrado!")
    st.info("Execute primeiro: `python scripts/run_processing.py`")
    st.stop()

# --- SEÇÃO DE MÉTRICAS PRINCIPAIS ---
st.header("📊 Visão Geral")

col1, col2, col3, col4 = st.columns(4)

# Total de crimes por período
total_crimes = sum(estatisticas.get('por_dia_semana', {}).values())

with col1:
    st.metric(
        label="Total de Ocorrências",
        value=f"{total_crimes:,}",
        delta=None
    )

with col2:
    if insights and 'padroes_temporais' in insights:
        horario_pico = insights['padroes_temporais'].get('horario_pico', {})
        st.metric(
            label="Horário Mais Perigoso",
            value=horario_pico.get('horario', 'N/A'),
            delta=f"{horario_pico.get('total', 0)} ocorrências"
        )

with col3:
    if insights and 'padroes_temporais' in insights:
        dia_perigoso = insights['padroes_temporais'].get('dia_mais_perigoso', {})
        st.metric(
            label="Dia Mais Perigoso",
            value=dia_perigoso.get('dia', 'N/A'),
            delta=f"{dia_perigoso.get('total', 0)} ocorrências"
        )

with col4:
    if insights and 'analise_espacial' in insights:
        ais_perigosa = insights['analise_espacial'].get('ais_mais_perigosa', {})
        st.metric(
            label="AIS Mais Perigosa",
            value=ais_perigosa.get('ais', 'N/A'),
            delta=f"{ais_perigosa.get('total', 0)} crimes"
        )

st.markdown("---")

# --- SEÇÃO DE HORÁRIOS ---
st.header("🕐 Análise por Horário")

col1, col2 = st.columns(2)

with col1:
    st.subheader("Ocorrências por Hora")
    df_horarios = criar_df_horarios(estatisticas.get('por_horario', {}))

    if not df_horarios.empty:
        st.bar_chart(df_horarios.set_index('Horário'))
    else:
        st.warning("Sem dados de horário disponíveis")

with col2:
    st.subheader("Top 10 Horários Mais Perigosos")
    horarios_perigosos = estatisticas.get('horarios_mais_perigosos', [])

    if horarios_perigosos:
        df_top_horarios = pd.DataFrame(horarios_perigosos)
        st.dataframe(
            df_top_horarios,
            use_container_width=True,
            hide_index=True
        )
    else:
        st.warning("Sem dados de ranking de horários")

st.markdown("---")

# --- SEÇÃO DE DIA DA SEMANA ---
st.header("📅 Análise por Dia da Semana")

dados_dia_semana = estatisticas.get('por_dia_semana', {})

if dados_dia_semana:
    # Ordena os dias da semana corretamente
    ordem_dias = ['Segunda', 'Terça', 'Quarta', 'Quinta', 'Sexta', 'Sábado', 'Domingo']

    df_dias = pd.DataFrame(list(dados_dia_semana.items()), columns=['Dia', 'Ocorrências'])
    df_dias['ordem'] = df_dias['Dia'].map({dia: i for i, dia in enumerate(ordem_dias)})
    df_dias = df_dias.sort_values('ordem').drop('ordem', axis=1)

    col1, col2 = st.columns([2, 1])

    with col1:
        st.bar_chart(df_dias.set_index('Dia'))

    with col2:
        st.dataframe(df_dias, use_container_width=True, hide_index=True)
else:
    st.warning("Sem dados de dia da semana disponíveis")

st.markdown("---")

# --- SEÇÃO DE AIS (ÁREAS DE SEGURANÇA) ---
st.header("🗺️ Análise por AIS (Área Integrada de Segurança)")

dados_ais = estatisticas.get('por_ais', {})

if dados_ais:
    df_ais = pd.DataFrame(list(dados_ais.items()), columns=['AIS', 'Ocorrências'])
    df_ais = df_ais.sort_values('Ocorrências', ascending=False)

    col1, col2 = st.columns([2, 1])

    with col1:
        st.bar_chart(df_ais.set_index('AIS'))

    with col2:
        st.subheader("Ranking de AIS")
        st.dataframe(df_ais, use_container_width=True, hide_index=True)
else:
    st.warning("Sem dados de AIS disponíveis")

st.markdown("---")

# --- SEÇÃO DE TENDÊNCIAS TEMPORAIS ---
st.header("📈 Tendências Temporais")

col1, col2 = st.columns(2)

with col1:
    st.subheader("Ocorrências por Mês")
    dados_mes = estatisticas.get('por_mes', {})

    if dados_mes:
        # Ordena os meses
        ordem_meses = ['Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho',
                       'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro']

        df_meses = pd.DataFrame(list(dados_mes.items()), columns=['Mês', 'Ocorrências'])
        df_meses['ordem'] = df_meses['Mês'].map({mes: i for i, mes in enumerate(ordem_meses)})
        df_meses = df_meses.sort_values('ordem').drop('ordem', axis=1)

        st.line_chart(df_meses.set_index('Mês'))
    else:
        st.warning("Sem dados mensais disponíveis")

with col2:
    st.subheader("Ocorrências por Ano")
    dados_ano = estatisticas.get('por_ano', {})

    if dados_ano:
        df_anos = pd.DataFrame(list(dados_ano.items()), columns=['Ano', 'Ocorrências'])
        df_anos = df_anos.sort_values('Ano')

        st.line_chart(df_anos.set_index('Ano'))
    else:
        st.warning("Sem dados anuais disponíveis")

st.markdown("---")

# --- SEÇÃO DE ALERTAS E INSIGHTS ---
if insights:
    st.header("🚨 Alertas e Recomendações")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Alertas de Segurança")
        alertas = insights.get('alertas', [])

        if alertas:
            for alerta in alertas:
                st.warning(f"**{alerta.get('tipo', 'Alerta')}**: {alerta.get('mensagem', '')}")
        else:
            st.info("Nenhum alerta crítico no momento")

    with col2:
        st.subheader("Recomendações")
        recomendacoes = insights.get('recomendacoes', [])

        if recomendacoes:
            for rec in recomendacoes:
                st.info(f"**{rec.get('area', 'Recomendação')}**: {rec.get('recomendacao', '')}")
        else:
            st.info("Nenhuma recomendação disponível")

st.markdown("---")

# --- RODAPÉ ---
st.markdown("### 📊 Dados Brutos")

with st.expander("Ver Estatísticas Completas (JSON)"):
    st.json(estatisticas)

with st.expander("Ver Insights Completos (JSON)"):
    if insights:
        st.json(insights)
    else:
        st.info("Nenhum insight disponível")

# Informações do rodapé
st.markdown("---")
st.caption("Fortaleza Segura - Sistema de Monitoramento de Segurança Pública")
st.caption("Dados processados do SSPDS-CE")
