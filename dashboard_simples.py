# dashboard_simples.py
"""
Dashboard Streamlit Simples - Fortaleza Segura
Versão sem Altair para evitar problemas de compatibilidade
"""

import streamlit as st
import pandas as pd
import json
import glob
import os
import subprocess
import sys
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go

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

def executar_script(script_path, nome_script):
    """Executa um script Python e mostra o progresso"""
    try:
        python_exe = os.path.join("venv", "Scripts", "python.exe")

        if not os.path.exists(python_exe):
            python_exe = sys.executable

        progress_container = st.empty()
        output_container = st.empty()

        progress_container.info(f"🔄 Executando {nome_script}...")

        process = subprocess.Popen(
            [python_exe, script_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding='utf-8',
            errors='replace'
        )

        stdout, stderr = process.communicate(timeout=300)

        if process.returncode == 0:
            progress_container.success(f"✅ {nome_script} executado com sucesso!")

            with output_container.expander("📋 Ver log de execução"):
                st.code(stdout, language="text")

            st.cache_data.clear()
            return True
        else:
            progress_container.error(f"❌ Erro ao executar {nome_script}")
            with output_container.expander("🐛 Ver erro"):
                st.code(stderr, language="text")
            return False

    except subprocess.TimeoutExpired:
        progress_container.error(f"⏱️ Timeout: {nome_script} demorou muito (>5 min)")
        return False
    except Exception as e:
        progress_container.error(f"❌ Erro: {str(e)}")
        return False

# --- SIDEBAR COM CONTROLES ---

with st.sidebar:
    st.header("🎛️ Painel de Controle")
    st.markdown("---")

    st.subheader("⚙️ Processamento de Dados")

    if st.button("📥 Baixar Novos Dados SSPDS", use_container_width=True):
        with st.spinner("Baixando dados..."):
            sucesso = executar_script(
                "scripts/carregar_estatisticas_sspds.py",
                "Download SSPDS"
            )
            if sucesso:
                st.balloons()

    if st.button("🔄 Processar e Analisar Dados", use_container_width=True):
        with st.spinner("Processando..."):
            sucesso = executar_script(
                "scripts/run_processing.py",
                "Processamento"
            )
            if sucesso:
                st.balloons()
                st.rerun()

    st.markdown("---")

    st.subheader("🔄 Atualização")

    if st.button("♻️ Recarregar Dashboard", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

    st.markdown("---")

    st.subheader("ℹ️ Informações")

    pasta_relatorios = "relatorios_sspds"
    if os.path.exists(pasta_relatorios):
        arquivos_stats = glob.glob(os.path.join(pasta_relatorios, "estatisticas_*.json"))
        if arquivos_stats:
            arquivo_mais_recente = max(arquivos_stats, key=os.path.getmtime)
            timestamp = os.path.getmtime(arquivo_mais_recente)
            data_atualizacao = datetime.fromtimestamp(timestamp)

            st.success("✅ Dados disponíveis")
            st.caption(f"Última atualização:")
            st.caption(data_atualizacao.strftime("%d/%m/%Y às %H:%M"))
        else:
            st.warning("⚠️ Nenhum dado processado")

    with st.expander("📁 Status"):
        pasta_downloads = "sspds_downloads"
        if os.path.exists(pasta_downloads):
            arquivos = glob.glob(os.path.join(pasta_downloads, "*.xlsx"))
            st.metric("Arquivos SSPDS", len(arquivos))
        else:
            st.metric("Arquivos SSPDS", 0)

# --- CONTEÚDO PRINCIPAL ---

st.title("🛡️ Fortaleza Segura")
st.markdown("### Dashboard de Segurança Pública")
st.markdown("---")

estatisticas = carregar_ultimas_estatisticas()
insights = carregar_ultimos_insights()

if estatisticas is None:
    st.warning("⚠️ Nenhum dado encontrado!")
    st.info("👉 Use os botões na barra lateral para baixar e processar dados")
    st.stop()

# --- MÉTRICAS ---
st.header("📊 Visão Geral")

col1, col2, col3, col4 = st.columns(4)

total_crimes = sum(estatisticas.get('por_dia_semana', {}).values())

with col1:
    st.metric("Total de Ocorrências", f"{total_crimes:,}".replace(',', '.'))

with col2:
    if insights and 'padroes_temporais' in insights:
        horario_pico = insights['padroes_temporais'].get('horario_pico', {})
        st.metric("Horário Mais Perigoso", horario_pico.get('horario', 'N/A'))

with col3:
    if insights and 'padroes_temporais' in insights:
        dia_perigoso = insights['padroes_temporais'].get('dia_mais_perigoso', {})
        st.metric("Dia Mais Perigoso", dia_perigoso.get('dia', 'N/A'))

with col4:
    if insights and 'analise_espacial' in insights:
        ais_perigosa = insights['analise_espacial'].get('ais_mais_perigosa', {})
        st.metric("AIS Mais Perigosa", ais_perigosa.get('ais', 'N/A'))

st.markdown("---")

# --- TABS ---
tab1, tab2, tab3, tab4 = st.tabs([
    "⏰ Análise Temporal",
    "🗺️ Análise Espacial",
    "📈 Tendências",
    "🚨 Alertas"
])

# TAB 1: TEMPORAL
with tab1:
    st.header("⏰ Análise por Horário e Dia")

    # Horários
    dados_horarios = estatisticas.get('por_horario', {})
    if dados_horarios:
        df_horarios = pd.DataFrame(list(dados_horarios.items()),
                                   columns=['Horário', 'Ocorrências'])
        df_horarios = df_horarios.sort_values('Horário')

        fig = px.bar(df_horarios, x='Horário', y='Ocorrências',
                    title='Ocorrências por Hora do Dia')
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")

    # Dias da semana
    dados_dia_semana = estatisticas.get('por_dia_semana', {})
    if dados_dia_semana:
        ordem_dias = ['Segunda', 'Terça', 'Quarta', 'Quinta', 'Sexta', 'Sábado', 'Domingo']

        df_dias = pd.DataFrame(list(dados_dia_semana.items()),
                              columns=['Dia', 'Ocorrências'])
        df_dias['ordem'] = df_dias['Dia'].map({dia: i for i, dia in enumerate(ordem_dias)})
        df_dias = df_dias.sort_values('ordem').drop('ordem', axis=1)

        fig = px.bar(df_dias, x='Dia', y='Ocorrências',
                    title='Ocorrências por Dia da Semana')
        st.plotly_chart(fig, use_container_width=True)

# TAB 2: ESPACIAL
with tab2:
    st.header("🗺️ Análise por Localização")

    dados_ais = estatisticas.get('por_ais', {})
    if dados_ais:
        df_ais = pd.DataFrame(list(dados_ais.items()),
                             columns=['AIS', 'Ocorrências'])
        df_ais = df_ais.sort_values('Ocorrências', ascending=False)

        fig = px.bar(df_ais, x='AIS', y='Ocorrências',
                    title='Distribuição por AIS')
        st.plotly_chart(fig, use_container_width=True)

        st.table(df_ais)

# TAB 3: TENDÊNCIAS
with tab3:
    st.header("📈 Tendências Temporais")

    col1, col2 = st.columns(2)

    with col1:
        dados_mes = estatisticas.get('por_mes', {})
        if dados_mes:
            ordem_meses = ['Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho',
                          'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro']

            df_meses = pd.DataFrame(list(dados_mes.items()),
                                   columns=['Mês', 'Ocorrências'])
            df_meses['ordem'] = df_meses['Mês'].map({mes: i for i, mes in enumerate(ordem_meses)})
            df_meses = df_meses.sort_values('ordem').drop('ordem', axis=1)

            fig = px.line(df_meses, x='Mês', y='Ocorrências',
                         title='Ocorrências por Mês')
            st.plotly_chart(fig, use_container_width=True)

    with col2:
        dados_ano = estatisticas.get('por_ano', {})
        if dados_ano:
            df_anos = pd.DataFrame(list(dados_ano.items()),
                                  columns=['Ano', 'Ocorrências'])
            df_anos = df_anos.sort_values('Ano')

            fig = px.line(df_anos, x='Ano', y='Ocorrências',
                         title='Ocorrências por Ano')
            st.plotly_chart(fig, use_container_width=True)

# TAB 4: ALERTAS
with tab4:
    st.header("🚨 Alertas e Recomendações")

    if insights:
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("⚠️ Alertas")
            alertas = insights.get('alertas', [])

            if alertas:
                for i, alerta in enumerate(alertas, 1):
                    st.warning(f"**{i}. {alerta.get('tipo')}**\n\n{alerta.get('mensagem')}")
            else:
                st.success("✅ Nenhum alerta crítico")

        with col2:
            st.subheader("💡 Recomendações")
            recomendacoes = insights.get('recomendacoes', [])

            if recomendacoes:
                for i, rec in enumerate(recomendacoes, 1):
                    st.info(f"**{i}. {rec.get('area')}**\n\n{rec.get('recomendacao')}")
            else:
                st.info("ℹ️ Nenhuma recomendação")

st.markdown("---")
st.caption("🛡️ Fortaleza Segura - Sistema de Monitoramento")
