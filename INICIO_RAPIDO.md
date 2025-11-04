# 🚀 Início Rápido - Fortaleza Segura

## ✅ Pré-requisitos Instalados

- ✅ Python 3.14
- ✅ Ambiente virtual (venv) criado
- ✅ 37 dependências instaladas
- ✅ Sistema de processamento testado e funcionando

---

## 🎯 Para Começar AGORA

### 1️⃣ Ativar Ambiente Virtual

**Windows:**
```cmd
cd fortaleza-segura
ativar_venv.bat
```

**Linux/Mac:**
```bash
cd fortaleza-segura
source ativar_venv.sh
```

### 2️⃣ Processar Dados SSPDS

```bash
python scripts/run_processing.py
```

**Isso vai:**
- Processar arquivos Excel do SSPDS
- Filtrar dados de Fortaleza
- Gerar estatísticas completas
- Criar relatórios JSON em `relatorios_sspds/`

### 3️⃣ Ver Resultados

```bash
# Ver estatísticas geradas
cat relatorios_sspds/estatisticas_*.json

# Ver insights
cat relatorios_sspds/insights_*.json
```

---

## 📊 Comandos Principais

### Baixar Novos Dados

```bash
python scripts/carregar_estatisticas_sspds.py
```

### Processar Dados (versão sem banco)

```bash
python scripts/processar_estatisticas_sem_bd.py
```

### Processar Dados (versão completa - requer .env)

```bash
python scripts/processar_estatisticas_completo.py
```

### Iniciar API FastAPI

```bash
python app/main.py
```

---

## 📁 Estrutura do Projeto

```
fortaleza-segura/
├── venv/                          # Ambiente virtual ✅
├── requirements.txt               # Dependências ✅
│
├── app/
│   ├── banco_de_dados/
│   │   ├── data_filter.py        # Filtrador ✅
│   │   ├── data_processor.py     # Processador ✅
│   │   └── data_analyzer.py      # Analisador ✅
│   └── main.py                    # API FastAPI
│
├── scripts/
│   ├── run_processing.py          # Script principal ✅
│   ├── carregar_estatisticas_sspds.py
│   └── processar_estatisticas_*.py
│
├── sspds_downloads/               # Dados baixados (24 arquivos)
├── relatorios_sspds/              # Relatórios gerados ✅
│
└── docs/
    ├── README_PROCESSAMENTO.md    # Documentação completa
    ├── VENV_SETUP.md              # Guia do ambiente
    └── INICIO_RAPIDO.md           # Este arquivo
```

---

## 🎓 Exemplos de Uso

### Exemplo 1: Processar Dados e Ver Top 5 Crimes

```bash
# 1. Ativar venv
ativar_venv.bat

# 2. Processar dados
python scripts/run_processing.py

# 3. Ver no terminal os top crimes
# O script já mostra um resumo automático
```

**Saída esperada:**
```
TOP 5 CRIMES MAIS COMUNS:
1. Roubo: 15.234 ocorrências
2. Furto: 12.456 ocorrências
...
```

### Exemplo 2: Análise por Horário

```bash
python scripts/run_processing.py
```

**Resultado em `insights_*.json`:**
```json
{
  "padroes_temporais": {
    "horario_pico": "19:00",
    "dia_mais_perigoso": "Sexta"
  }
}
```

### Exemplo 3: Identificar Zonas de Risco

```bash
python scripts/run_processing.py
```

**Resultado em `insights_*.json`:**
```json
{
  "analise_espacial": {
    "ais_mais_perigosa": "AIS 03",
    "zonas_criticas": [...]
  }
}
```

---

## 🔍 O Que Cada Script Faz

### `run_processing.py` ⭐ RECOMENDADO
- Processa dados com encoding UTF-8
- Gera estatísticas completas
- Cria insights avançados
- Exporta JSON
- **Não requer banco de dados**

### `carregar_estatisticas_sspds.py`
- Baixa arquivos do site SSPDS
- Detecta novos arquivos automaticamente
- Mantém manifesto de downloads
- Salva em `sspds_downloads/`

### `processar_estatisticas_completo.py`
- Pipeline completo com banco de dados
- Salva eventos no PostgreSQL
- Requer arquivo `.env` configurado

### `processar_estatisticas_sem_bd.py`
- Versão sem banco de dados
- Apenas gera relatórios JSON
- Mais simples para testes

---

## 📈 Dados Disponíveis

### Já Baixados (24 arquivos):
- Armas de Fogo (2009-2025)
- CVLI - Crimes Violentos Letais Intencionais
- CVP - Crimes Violentos contra o Patrimônio
- Crimes Sexuais
- Furtos
- Lei Maria da Penha
- Crimes Raciais
- Homofobia/Transfobia
- Indígenas
- Entorpecentes
- Incêndios
- Salvamentos

### Total de Registros:
- **Mais de 100.000 registros** disponíveis
- **31.604 registros** já processados no teste

---

## 🎯 Resultados Que Você Obtém

### Estatísticas Geradas:

1. **Por Localização**
   - Crimes por bairro
   - Crimes por AIS
   - Ranking de zonas perigosas

2. **Por Horário**
   - Crimes por hora (00:00 - 23:00)
   - Período do dia mais perigoso
   - Ranking de horários

3. **Por Tempo**
   - Crimes por dia da semana
   - Crimes por mês
   - Crimes por ano

4. **Por Tipo**
   - Tipos de crime
   - Crimes mais comuns
   - Distribuição por natureza

### Insights Gerados:

- 🚨 **Alertas**: Zonas/horários de risco
- 💡 **Recomendações**: Estratégias de segurança
- 📊 **Padrões**: Tendências temporais
- 🎯 **Scores**: Risco por bairro (0-100)

---

## ⚡ Comandos Mais Usados

```bash
# Setup inicial (já feito)
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt

# Uso diário
ativar_venv.bat                           # Ativar ambiente
python scripts/run_processing.py          # Processar dados
python scripts/carregar_estatisticas_sspds.py  # Baixar novos
deactivate                                # Desativar ambiente

# Desenvolvimento
pip install nova-biblioteca               # Adicionar dependência
pip freeze > requirements.txt             # Salvar dependências
python -m pytest                          # Rodar testes (se houver)
```

---

## 🐛 Solução Rápida de Problemas

### Erro: ModuleNotFoundError
```bash
# Certifique-se que o venv está ativado
# Deve aparecer (venv) no prompt
ativar_venv.bat
```

### Erro: Arquivo não encontrado
```bash
# Verifique se está na pasta correta
cd fortaleza-segura
pwd  # ou cd (Windows) para ver pasta atual
```

### Erro: Encoding/Unicode
```bash
# Use o run_processing.py ao invés dos outros
python scripts/run_processing.py
```

### Erro: Sem dados processados
```bash
# Baixe os dados primeiro
python scripts/carregar_estatisticas_sspds.py
```

---

## 📚 Documentação Completa

- **README_PROCESSAMENTO.md** - Documentação completa do sistema
- **PROCESSAMENTO_DADOS.md** - Guia técnico detalhado
- **VENV_SETUP.md** - Guia do ambiente virtual

---

## ✅ Checklist Rápido

Antes de começar a trabalhar, verifique:

- [ ] Pasta `fortaleza-segura`
- [ ] Pasta `venv/` existe
- [ ] Arquivos em `sspds_downloads/`
- [ ] Ambiente virtual ativado `(venv)`
- [ ] Python funcionando: `python --version`

---

## 🎉 Você Está Pronto!

Agora você pode:
1. ✅ Processar dados do SSPDS
2. ✅ Gerar estatísticas automáticas
3. ✅ Criar insights de segurança
4. ✅ Exportar relatórios JSON
5. ✅ Integrar com dashboards

**Comece agora:**
```bash
ativar_venv.bat
python scripts/run_processing.py
```

---

**Bom trabalho!** 🚀
