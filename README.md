# Fortaleza Segura

Plataforma de coleta, processamento e analise de dados de seguranca publica de Fortaleza-CE, com API em FastAPI, scripts de ETL e dashboards para visualizacao.

## Visao Geral

O projeto integra diferentes fontes de dados para gerar estatisticas, insights e relatorios sobre ocorrencias em Fortaleza.

Principais componentes:
- Coleta de dados SSPDS
- Filtragem e validacao de dados
- Processamento estatistico por bairro, horario e periodo
- Geracao de insights automatizados
- API REST com FastAPI
- Dashboards interativos com Streamlit

## Estrutura Principal

- `app/`: API FastAPI, modelos, rotas e logica de analise
- `scripts/`: pipeline de processamento e carga de dados
- `scrapers/`: scripts de coleta
- `data/`: arquivos de base (CSV e GeoJSON)
- `sspds_downloads/`: dados baixados para processamento
- `requirements.txt`: dependencias Python
- `INICIO_RAPIDO.md`: guia detalhado de uso
- `RESUMO_COMPLETO_PROJETO.md`: documentacao completa do projeto

## Pre-requisitos

- Python 3.10+ (recomendado usar o ambiente virtual do projeto)
- `pip`

## Instalacao

1. Clone o repositorio e entre na pasta:

```bash
git clone <url-do-repositorio>
cd trabalho-big-data
```

2. Crie e ative o ambiente virtual:

```bash
python -m venv venv
source venv/bin/activate
```

No Windows:

```bat
venv\Scripts\activate
```

3. Instale as dependencias:

```bash
pip install -r requirements.txt
```

## Como Executar

### 1) Processamento principal de dados

```bash
python scripts/run_processing.py
```

### 2) API FastAPI

```bash
uvicorn app.main:app --reload
```

Se preferir, voce tambem pode executar:

```bash
python app/main.py
```

### 3) Dashboards Streamlit

```bash
streamlit run dashboard_streamlit.py
```

Opcoes alternativas:
- `dashboard_completo.py`
- `dashboard_simples.py`

## Scripts uteis

- `python scripts/carregar_estatisticas_sspds.py`: baixa/atualiza dados SSPDS
- `python scripts/processar_estatisticas_sem_bd.py`: processamento sem banco de dados
- `python scripts/processar_estatisticas_completo.py`: pipeline com persistencia em banco

## Documentacao complementar

- `INICIO_RAPIDO.md`
- `PROCESSAMENTO_DADOS.md`
- `README_PROCESSAMENTO.md`
- `RESUMO_COMPLETO_PROJETO.md`

## Status

Projeto em desenvolvimento com pipeline de dados, API e dashboards funcionais.
