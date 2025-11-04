# dashboard_completo.py
"""
Dashboard Streamlit Completo - Fortaleza Segura
Com botões para executar scripts de processamento
"""

import streamlit as st
import pandas as pd
import json
import glob
import os
import subprocess
import sys
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
        # Caminho do Python no venv
        python_exe = os.path.join("venv", "Scripts", "python.exe")

        if not os.path.exists(python_exe):
            python_exe = sys.executable  # Fallback para Python do sistema

        # Container para mostrar progresso
        progress_container = st.empty()
        output_container = st.empty()

        progress_container.info(f"🔄 Executando {nome_script}...")

        # Executa o script
        process = subprocess.Popen(
            [python_exe, script_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding='utf-8',
            errors='replace'
        )

        # Captura a saída
        stdout, stderr = process.communicate(timeout=300)  # 5 minutos timeout

        if process.returncode == 0:
            progress_container.success(f"✅ {nome_script} executado com sucesso!")

            # Mostra saída em expander
            with output_container.expander("📋 Ver log de execução"):
                st.code(stdout, language="text")

            # Limpa cache para recarregar dados
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

def criar_df_horarios(dados_horarios):
    """Converte dados de horários em DataFrame para gráficos"""
    if not dados_horarios:
        return pd.DataFrame()

    df = pd.DataFrame(list(dados_horarios.items()), columns=['Horário', 'Ocorrências'])
    df = df.sort_values('Horário')
    return df

# --- SIDEBAR COM CONTROLES ---

with st.sidebar:
    st.image("https://via.placeholder.com/200x100/1e3a8a/ffffff?text=Fortaleza+Segura", use_container_width=True)

    st.header("🎛️ Painel de Controle")
    st.markdown("---")

    # Seção de Processamento
    st.subheader("⚙️ Processamento de Dados")

    # Botão 1: Baixar Dados SSPDS
    if st.button("📥 Baixar Novos Dados SSPDS", use_container_width=True):
        with st.spinner("Baixando dados do SSPDS..."):
            sucesso = executar_script(
                "scripts/carregar_estatisticas_sspds.py",
                "Download SSPDS"
            )
            if sucesso:
                st.balloons()

    # Botão 2: Processar Dados
    if st.button("🔄 Processar e Analisar Dados", use_container_width=True):
        with st.spinner("Processando dados..."):
            sucesso = executar_script(
                "scripts/run_processing.py",
                "Processamento de Dados"
            )
            if sucesso:
                st.balloons()
                st.rerun()  # Atualiza o dashboard

    st.markdown("---")

    # Seção de Atualização
    st.subheader("🔄 Atualização")

    if st.button("♻️ Recarregar Dashboard", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

    st.markdown("---")

    # Informações
    st.subheader("ℹ️ Informações")

    # Verifica se há dados
    pasta_relatorios = "relatorios_sspds"
    if os.path.exists(pasta_relatorios):
        arquivos_stats = glob.glob(os.path.join(pasta_relatorios, "estatisticas_*.json"))
        if arquivos_stats:
            arquivo_mais_recente = max(arquivos_stats, key=os.path.getmtime)
            timestamp = os.path.getmtime(arquivo_mais_recente)
            data_atualizacao = datetime.fromtimestamp(timestamp)

            st.success(f"✅ Dados disponíveis")
            st.caption(f"Última atualização:")
            st.caption(data_atualizacao.strftime("%d/%m/%Y às %H:%M"))
        else:
            st.warning("⚠️ Nenhum dado processado")
            st.caption("Clique em 'Processar Dados'")
    else:
        st.error("❌ Pasta de relatórios não encontrada")

    st.markdown("---")

    # Status dos Arquivos
    with st.expander("📁 Status dos Arquivos"):
        pasta_downloads = "sspds_downloads"
        if os.path.exists(pasta_downloads):
            arquivos = glob.glob(os.path.join(pasta_downloads, "*.xlsx"))
            st.metric("Arquivos SSPDS", len(arquivos))
        else:
            st.metric("Arquivos SSPDS", 0)

        if os.path.exists(pasta_relatorios):
            relatorios = glob.glob(os.path.join(pasta_relatorios, "*.json"))
            st.metric("Relatórios Gerados", len(relatorios))
        else:
            st.metric("Relatórios Gerados", 0)

# --- CONTEÚDO PRINCIPAL ---

# Cabeçalho
st.title("🛡️ Fortaleza Segura")
st.markdown("### Dashboard de Segurança Pública de Fortaleza")
st.markdown("---")

# Carregar dados
estatisticas = carregar_ultimas_estatisticas()
insights = carregar_ultimos_insights()

if estatisticas is None:
    st.warning("⚠️ Nenhum dado encontrado!")
    st.info("👉 Use os botões na barra lateral para:")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("""
        **1. Baixar Dados**
        - Clique em "📥 Baixar Novos Dados SSPDS"
        - Aguarde o download completar
        """)

    with col2:
        st.markdown("""
        **2. Processar Dados**
        - Clique em "🔄 Processar e Analisar Dados"
        - O dashboard será atualizado automaticamente
        """)

    st.stop()

# --- SEÇÃO DE MÉTRICAS PRINCIPAIS ---
st.header("📊 Visão Geral")

col1, col2, col3, col4 = st.columns(4)

# Total de crimes
total_crimes = sum(estatisticas.get('por_dia_semana', {}).values())

with col1:
    st.metric(
        label="Total de Ocorrências",
        value=f"{total_crimes:,}".replace(',', '.'),
        delta=None
    )

with col2:
    if insights and 'padroes_temporais' in insights:
        horario_pico = insights['padroes_temporais'].get('horario_pico', {})
        st.metric(
            label="Horário Mais Perigoso",
            value=horario_pico.get('horario', 'N/A'),
            delta=f"{horario_pico.get('total', 0)} ocorrências",
            delta_color="inverse"
        )

with col3:
    if insights and 'padroes_temporais' in insights:
        dia_perigoso = insights['padroes_temporais'].get('dia_mais_perigoso', {})
        st.metric(
            label="Dia Mais Perigoso",
            value=dia_perigoso.get('dia', 'N/A'),
            delta=f"{dia_perigoso.get('total', 0)} ocorrências",
            delta_color="inverse"
        )

with col4:
    if insights and 'analise_espacial' in insights:
        ais_perigosa = insights['analise_espacial'].get('ais_mais_perigosa', {})
        st.metric(
            label="AIS Mais Perigosa",
            value=ais_perigosa.get('ais', 'N/A'),
            delta=f"{ais_perigosa.get('total', 0)} crimes",
            delta_color="inverse"
        )

st.markdown("---")

# --- TABS PARA ORGANIZAR CONTEÚDO ---
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "⏰ Análise Temporal",
    "🗺️ Análise Espacial",
    "📈 Tendências",
    "🚨 Alertas",
    "📄 Dados Brutos"
])

# TAB 1: ANÁLISE TEMPORAL
with tab1:
    st.header("⏰ Análise por Horário e Dia")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Ocorrências por Hora do Dia")
        df_horarios = criar_df_horarios(estatisticas.get('por_horario', {}))

        if not df_horarios.empty:
            st.bar_chart(df_horarios.set_index('Horário'))
        else:
            st.warning("Sem dados de horário disponíveis")

    with col2:
        st.subheader("Top 10 Horários Mais Perigosos")
        horarios_perigosos = estatisticas.get('horarios_mais_perigosos', [])

        if horarios_perigosos:
            df_top_horarios = pd.DataFrame(horarios_perigosos[:10])
            st.dataframe(
                df_top_horarios,
                use_container_width=True,
                hide_index=True
            )
        else:
            st.warning("Sem dados de ranking de horários")

    st.markdown("---")

    st.subheader("📅 Ocorrências por Dia da Semana")

    dados_dia_semana = estatisticas.get('por_dia_semana', {})

    if dados_dia_semana:
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

# TAB 2: ANÁLISE ESPACIAL
with tab2:
    st.header("🗺️ Análise por Localização")

    st.subheader("Distribuição por AIS (Área Integrada de Segurança)")

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

    # Mapa placeholder
    st.subheader("🗺️ Mapa de Calor (Em breve)")
    st.info("Funcionalidade de mapa geográfico será implementada em breve")

# TAB 3: TENDÊNCIAS
with tab3:
    st.header("📈 Tendências Temporais")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Ocorrências por Mês")
        dados_mes = estatisticas.get('por_mes', {})

        if dados_mes:
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

# TAB 4: ALERTAS
with tab4:
    st.header("🚨 Alertas e Recomendações")

    if insights:
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("⚠️ Alertas de Segurança")
            alertas = insights.get('alertas', [])

            if alertas:
                for i, alerta in enumerate(alertas, 1):
                    st.warning(f"**{i}. {alerta.get('tipo', 'Alerta')}**\n\n{alerta.get('mensagem', '')}")
            else:
                st.success("✅ Nenhum alerta crítico no momento")

        with col2:
            st.subheader("💡 Recomendações")
            recomendacoes = insights.get('recomendacoes', [])

            if recomendacoes:
                for i, rec in enumerate(recomendacoes, 1):
                    st.info(f"**{i}. {rec.get('area', 'Recomendação')}**\n\n{rec.get('recomendacao', '')}")
            else:
                st.info("ℹ️ Nenhuma recomendação disponível")
    else:
        st.warning("Insights não disponíveis")

# TAB 5: DADOS BRUTOS
with tab5:
    st.header("📄 Dados Brutos (JSON)")

    col1, col2 = st.columns(2)

    with col1:
        with st.expander("📊 Ver Estatísticas Completas"):
            st.json(estatisticas)

    with col2:
        with st.expander("🔍 Ver Insights Completos"):
            if insights:
                st.json(insights)
            else:
                st.info("Nenhum insight disponível")

# --- RODAPÉ ---
st.markdown("---")
st.caption("🛡️ Fortaleza Segura - Sistema de Monitoramento de Segurança Pública")
st.caption("📊 Dados processados do SSPDS-CE | Desenvolvido com Streamlit")
