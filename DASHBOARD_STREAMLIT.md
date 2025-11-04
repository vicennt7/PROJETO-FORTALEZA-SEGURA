# 📊 Dashboard Streamlit - Fortaleza Segura

## ✅ Dashboard Criado e Pronto para Uso!

Um dashboard web interativo foi criado usando Streamlit para visualizar os dados de segurança pública de Fortaleza.

---

## 🎯 O Que o Dashboard Mostra

### 1. **Métricas Principais** (Cards no Topo)
- Total de ocorrências
- Horário mais perigoso
- Dia mais perigoso da semana
- AIS (Área de Segurança) mais perigosa

### 2. **Análise por Horário**
- Gráfico de barras: Ocorrências por hora (00:00 - 23:00)
- Tabela: Top 10 horários mais perigosos

### 3. **Análise por Dia da Semana**
- Gráfico de barras: Crimes por dia
- Tabela comparativa

### 4. **Análise por AIS**
- Gráfico: Distribuição por área de segurança
- Ranking de AIS mais perigosas

### 5. **Tendências Temporais**
- Gráfico de linha: Ocorrências por mês
- Gráfico de linha: Ocorrências por ano

### 6. **Alertas e Recomendações**
- Alertas de segurança críticos
- Recomendações baseadas nos dados

### 7. **Dados Brutos**
- JSON completo de estatísticas
- JSON completo de insights

---

## 🚀 Como Executar o Dashboard

### Método 1: Comando Direto (Windows)

```cmd
cd fortaleza-segura
venv\Scripts\streamlit run dashboard_streamlit.py
```

### Método 2: Com Ambiente Ativado

```cmd
# 1. Ativar ambiente virtual
ativar_venv.bat

# 2. Executar dashboard
streamlit run dashboard_streamlit.py
```

### Método 3: Linux/Mac

```bash
cd fortaleza-segura
source venv/bin/activate
streamlit run dashboard_streamlit.py
```

---

## 🌐 Acessando o Dashboard

Após executar o comando, você verá:

```
You can now view your Streamlit app in your browser.

Local URL: http://localhost:8501
Network URL: http://192.168.X.X:8501
```

**O navegador abrirá automaticamente** no endereço `http://localhost:8501`

Se não abrir, copie e cole o URL no navegador.

---

## 📊 Fluxo de Trabalho Completo

### 1. Processar Dados

```bash
python scripts/run_processing.py
```

Isso gera:
- `relatorios_sspds/estatisticas_*.json`
- `relatorios_sspds/insights_*.json`

### 2. Visualizar no Dashboard

```bash
streamlit run dashboard_streamlit.py
```

O dashboard **lê automaticamente** os arquivos JSON mais recentes!

### 3. Atualizar Dados

Se você processar novos dados:

1. Clique no botão **"🔄 Recarregar Dados"** no dashboard
2. Ou aperte **"R"** no teclado (atalho do Streamlit)
3. Ou atualize a página do navegador

---

## 🎨 Recursos do Dashboard

### ✅ Interatividade
- ✅ Gráficos interativos (hover para detalhes)
- ✅ Tabelas ordenáveis
- ✅ Expandir/recolher seções
- ✅ Atualização em tempo real

### ✅ Visualizações
- ✅ Gráficos de barras
- ✅ Gráficos de linha (tendências)
- ✅ Métricas com cards
- ✅ Alertas coloridos

### ✅ Dados
- ✅ Lê JSON automaticamente
- ✅ Cache para performance
- ✅ Sem necessidade de banco de dados

---

## 📱 Compartilhar o Dashboard

### Na Rede Local

O dashboard já está acessível na sua rede local!

**Outros computadores podem acessar usando:**
```
http://SEU_IP:8501
```

Exemplo: `http://192.168.1.100:8501`

### Descobrir Seu IP

**Windows:**
```cmd
ipconfig
```
Procure por "IPv4 Address"

**Linux/Mac:**
```bash
ifconfig
```

---

## ⚙️ Personalização

O dashboard pode ser customizado editando `dashboard_streamlit.py`:

### Mudar Cores

```python
st.set_page_config(
    page_title="Seu Título",
    page_icon="🎯",  # Emoji personalizado
    layout="wide"
)
```

### Adicionar Novos Gráficos

```python
# Gráfico de pizza
st.subheader("Distribuição por Tipo")
fig = px.pie(df, values='total', names='tipo')
st.plotly_chart(fig)
```

### Adicionar Filtros

```python
# Filtro por período
periodo = st.selectbox(
    "Selecione o período:",
    ["Manhã", "Tarde", "Noite"]
)
```

---

## 🔄 Hot Reload (Atualização Automática)

O Streamlit tem **hot reload** automático:

1. Edite `dashboard_streamlit.py`
2. Salve o arquivo
3. O dashboard detecta a mudança
4. Aparece botão "Rerun" ou aperte "R"
5. Dashboard atualiza instantaneamente!

**Não precisa reiniciar o servidor!**

---

## 📊 Exemplos de Visualizações

### Métricas
```python
st.metric(
    label="Total de Crimes",
    value="31.604",
    delta="+1.234 este mês"
)
```

### Gráfico de Barras
```python
st.bar_chart(df.set_index('categoria'))
```

### Gráfico de Linha
```python
st.line_chart(df.set_index('data'))
```

### Mapa (para implementar depois)
```python
st.map(df)  # Requer colunas 'lat' e 'lon'
```

---

## 🗺️ Adicionando Mapas Geográficos (Próximo Passo)

Para mostrar crimes em mapa de Fortaleza:

```python
# Seus dados precisam ter lat/lon
df_mapa = pd.DataFrame({
    'bairro': ['Aldeota', 'Meireles'],
    'lat': [-3.7435, -3.7279],
    'lon': [-38.5030, -38.4870],
    'crimes': [150, 200]
})

st.map(df_mapa)
```

---

## 🚀 Deploy (Hospedar Online)

### Opção 1: Streamlit Cloud (GRÁTIS)

1. Crie conta em https://share.streamlit.io
2. Conecte seu repositório GitHub
3. Selecione `dashboard_streamlit.py`
4. Deploy automático!

**Resultado:** URL público tipo `https://seu-app.streamlit.app`

### Opção 2: Docker

```dockerfile
FROM python:3.14
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["streamlit", "run", "dashboard_streamlit.py"]
```

### Opção 3: Servidor Próprio

```bash
streamlit run dashboard_streamlit.py --server.port 80 --server.address 0.0.0.0
```

---

## 📈 Vantagens do Streamlit

### ✅ Para Este Projeto

1. **Rápido**: Dashboard criado em 1 arquivo Python
2. **Sem Frontend**: Não precisa HTML/CSS/JS
3. **Interativo**: Atualização em tempo real
4. **Grátis**: Open source e gratuito
5. **Fácil Deploy**: Streamlit Cloud gratuito

### ✅ Comparado a Outras Opções

| Recurso | Streamlit | React | Dash |
|---------|-----------|-------|------|
| Curva de aprendizado | Fácil | Difícil | Médio |
| Código Python puro | ✅ | ❌ | ✅ |
| Deploy gratuito | ✅ | ❌ | ❌ |
| Hot reload | ✅ | ✅ | ✅ |
| Mapas integrados | ✅ | ❌ | ✅ |

---

## 🐛 Solução de Problemas

### Erro: "No module named 'streamlit'"
```bash
venv\Scripts\activate
pip install streamlit
```

### Erro: "Port 8501 already in use"
```bash
# Use outra porta
streamlit run dashboard_streamlit.py --server.port 8502
```

### Dashboard não atualiza dados
1. Clique em "🔄 Recarregar Dados"
2. Ou pressione **"R"** no teclado
3. Ou use `st.cache_data.clear()`

### Página em branco
Verifique se os arquivos JSON existem:
```bash
dir relatorios_sspds\*.json
```

Se não existir, execute:
```bash
python scripts/run_processing.py
```

---

## 🎯 Próximas Melhorias Possíveis

### 1. **Filtros Interativos**
```python
# Filtrar por período
periodo = st.select_slider(
    "Período:",
    options=["Manhã", "Tarde", "Noite", "Madrugada"]
)
```

### 2. **Download de Relatórios**
```python
# Botão para baixar CSV
csv = df.to_csv()
st.download_button(
    label="Baixar CSV",
    data=csv,
    file_name="relatorio.csv"
)
```

### 3. **Gráficos Plotly (mais interativos)**
```python
import plotly.express as px

fig = px.bar(df, x='bairro', y='crimes', color='tipo')
st.plotly_chart(fig)
```

### 4. **Conexão Direta com Banco**
```python
import psycopg2

@st.cache_resource
def get_connection():
    return psycopg2.connect(...)

df = pd.read_sql("SELECT * FROM eventos", get_connection())
```

### 5. **Autenticação**
```python
# Requer streamlit-authenticator
import streamlit_authenticator as stauth

authenticator = stauth.Authenticate(...)
authenticator.login('Login', 'main')
```

---

## 📚 Documentação Streamlit

- **Documentação Oficial**: https://docs.streamlit.io
- **Galeria de Apps**: https://streamlit.io/gallery
- **Cheat Sheet**: https://cheat-sheet.streamlit.app
- **Forum**: https://discuss.streamlit.io

---

## ✨ Comandos Úteis do Streamlit

```bash
# Rodar dashboard
streamlit run dashboard_streamlit.py

# Rodar em porta diferente
streamlit run dashboard_streamlit.py --server.port 8502

# Rodar sem abrir navegador
streamlit run dashboard_streamlit.py --server.headless true

# Ver configurações
streamlit config show

# Limpar cache
streamlit cache clear
```

---

## 🎉 Status: Pronto para Uso!

✅ Dashboard criado: `dashboard_streamlit.py`
✅ Streamlit instalado no venv
✅ Lê dados JSON automaticamente
✅ Visualizações interativas funcionando
✅ Pronto para executar!

**Execute agora:**
```bash
streamlit run dashboard_streamlit.py
```

---

**Dashboard Streamlit - Fortaleza Segura** 🛡️📊
