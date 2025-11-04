# Sistema de Processamento de Dados SSPDS

Sistema completo para download, filtragem, processamento e análise de dados de segurança pública do SSPDS-CE.

## 📋 Componentes do Sistema

### 1. **Data Filter** (`app/banco_de_dados/data_filter.py`)
Responsável por:
- ✅ Remover duplicados (tanto internos quanto do banco de dados)
- ✅ Filtrar apenas registros de Fortaleza
- ✅ Validar dados (verificar campos obrigatórios)
- ✅ Normalizar dados (trim, lowercase)
- ✅ Gerar hashes únicos para cada registro

### 2. **Data Processor** (`app/banco_de_dados/data_processor.py`)
Extrai estatísticas detalhadas:
- 📊 Crimes por bairro
- 📊 Crimes por tipo/natureza
- 📊 Crimes por horário
- 📊 Crimes por dia da semana
- 📊 Crimes por AIS (Área Integrada de Segurança)
- 📊 Crimes por período do dia (manhã, tarde, noite, madrugada)
- 📊 Crimes por mês e ano
- 📊 Rankings (top crimes, bairros mais perigosos, horários críticos)

### 3. **Data Analyzer** (`app/banco_de_dados/data_analyzer.py`)
Gera insights avançados:
- 🔍 Análise de padrões temporais
- 🔍 Análise de padrões espaciais
- 🔍 Correlações entre crime/local/horário
- 🔍 Score de risco por bairro (0-100)
- 🔍 Alertas de segurança
- 🔍 Recomendações estratégicas

### 4. **Pipeline Completo** (`scripts/processar_estatisticas_completo.py`)
Orquestra todo o processo:
1. Download de arquivos do SSPDS
2. Filtragem e limpeza
3. Processamento de estatísticas
4. Análise avançada
5. Exportação de relatórios

## 🚀 Como Usar

### Opção 1: Executar Pipeline Completo (Recomendado)

```bash
cd fortaleza-segura
python scripts/processar_estatisticas_completo.py
```

Este script irá:
- Baixar novos arquivos do SSPDS
- Processar todos os dados
- Gerar relatórios JSON com estatísticas e insights
- Salvar tudo na pasta `relatorios_sspds/`

### Opção 2: Apenas Download (Script Original)

```bash
cd fortaleza-segura
python scripts/carregar_estatisticas_sspds.py
```

## 📊 Saídas Geradas

### 1. Estatísticas (`estatisticas_YYYYMMDD_HHMMSS.json`)

Contém:
```json
{
  "por_bairro": {
    "Centro": {
      "total_crimes": 150,
      "tipos_crime": {
        "Roubo": 80,
        "Furto": 70
      },
      "por_periodo": {
        "Noite (18h-00h)": 90,
        "Manhã (06h-12h)": 60
      }
    }
  },
  "crimes_mais_comuns": [...],
  "bairros_mais_perigosos": [...],
  "por_horario": {...},
  "por_dia_semana": {...}
}
```

### 2. Insights (`insights_YYYYMMDD_HHMMSS.json`)

Contém:
```json
{
  "padroes_temporais": {
    "horario_pico": "20:00",
    "periodo_mais_perigoso": "Noite (18h-00h)",
    "dia_mais_perigoso": "Sexta-feira"
  },
  "analise_espacial": {
    "zonas_criticas": [...],
    "ranking_risco": [
      {
        "bairro": "Centro",
        "score": 85.5,
        "nivel": "CRÍTICO",
        "total_crimes": 150
      }
    ]
  },
  "alertas": [...],
  "recomendacoes": [...]
}
```

## 📈 Estatísticas Disponíveis

### Por Localização
- ✅ Total de crimes por bairro
- ✅ Tipos de crime por bairro
- ✅ Crimes por AIS
- ✅ Score de risco por bairro (0-100)
- ✅ Ranking de bairros mais perigosos

### Por Horário
- ✅ Crimes por hora específica (00:00 - 23:00)
- ✅ Crimes por período do dia
- ✅ Horários mais perigosos (ranking)
- ✅ Padrão temporal por bairro

### Por Tipo
- ✅ Ranking de crimes mais comuns
- ✅ Distribuição por natureza do crime
- ✅ Crimes por meio empregado

### Por Tempo
- ✅ Crimes por dia da semana
- ✅ Crimes por mês
- ✅ Crimes por ano
- ✅ Tendências temporais

## 🎯 Funcionalidades de Filtragem

### Remoção de Duplicados
O sistema identifica duplicados usando:
- Hash MD5 do conteúdo do registro + nome do arquivo
- Verificação no banco de dados
- Deduplicação dentro do mesmo arquivo

### Validação de Dados
Verifica:
- Campo município presente (obrigatório para filtrar Fortaleza)
- Data do evento informada
- Natureza do crime informada

### Normalização
- Remove espaços extras
- Padroniza capitalização
- Trata valores nulos

## 🔧 Requisitos

```bash
pip install pandas openpyxl sqlalchemy requests beautifulsoup4 PyMuPDF
```

## 📁 Estrutura de Pastas

```
fortaleza-segura/
├── app/
│   └── banco_de_dados/
│       ├── data_filter.py        # Filtrador de dados
│       ├── data_processor.py     # Processador de estatísticas
│       └── data_analyzer.py      # Analisador de insights
├── scripts/
│   ├── carregar_estatisticas_sspds.py          # Script original
│   └── processar_estatisticas_completo.py      # Pipeline completo
├── sspds_downloads/              # Arquivos baixados
├── relatorios_sspds/             # Relatórios gerados
│   ├── estatisticas_*.json
│   └── insights_*.json
└── PROCESSAMENTO_DADOS.md        # Este arquivo
```

## 📊 Exemplo de Uso Programático

```python
from app.banco_de_dados.data_filter import DataFilter
from app.banco_de_dados.data_processor import DataProcessor
from app.banco_de_dados.data_analyzer import DataAnalyzer
import pandas as pd

# 1. Filtrar dados
filtrador = DataFilter()
df_limpo = filtrador.filter_and_clean(
    df=df_original,
    source_file="arquivo.xlsx",
    municipio_col="Município"
)

# 2. Processar estatísticas
processador = DataProcessor()
processador.process_dataframe(df_limpo, mapa_colunas)
processador.export_statistics("stats.json")

# 3. Analisar insights
analisador = DataAnalyzer(processador.statistics)
analisador.run_full_analysis()
analisador.export_insights("insights.json")

# 4. Ver resumos
filtrador.print_summary()
processador.print_summary()
analisador.print_summary()
```

## 🎨 Níveis de Risco

O sistema classifica bairros em 4 níveis:

- 🟢 **BAIXO** (score 0-30): Poucos crimes, baixa diversidade
- 🟡 **MÉDIO** (score 30-50): Crimes moderados
- 🟠 **ALTO** (score 50-70): Muitos crimes ou alta diversidade
- 🔴 **CRÍTICO** (score 70-100): Zona de alta periculosidade

## 💡 Insights Gerados

O sistema gera automaticamente:
- 🚨 **Alertas**: Zonas de risco, horários perigosos, padrões críticos
- 💡 **Recomendações**: Estratégias de policiamento, alocação de recursos
- 📈 **Rankings**: Top crimes, bairros, horários
- 🔍 **Correlações**: Padrões entre crime/local/tempo

## 🔄 Fluxo de Dados

```
Download (SSPDS)
    ↓
Filtragem (duplicados, validação)
    ↓
Processamento (estatísticas)
    ↓
Análise (insights, scores)
    ↓
Exportação (JSON)
    ↓
Banco de Dados (PostgreSQL)
```

## 🎯 Casos de Uso

1. **Análise de Segurança Pública**: Identificar zonas críticas
2. **Planejamento de Policiamento**: Otimizar alocação de recursos
3. **Estudos Acadêmicos**: Pesquisas sobre criminalidade
4. **Dashboards**: Alimentar visualizações em tempo real
5. **Alertas Automáticos**: Sistema de notificações de risco

## 📝 Notas Importantes

- ✅ O sistema detecta automaticamente colunas nos arquivos SSPDS
- ✅ Processa múltiplos formatos de data/hora
- ✅ Lida com dados faltantes de forma inteligente
- ✅ Mantém histórico de downloads (manifest.json)
- ✅ Evita reprocessar arquivos já baixados
- ✅ Thread-safe para processamento paralelo

## 🐛 Solução de Problemas

**Erro: "Coluna Município não encontrada"**
→ O arquivo não possui a coluna padrão. Verifique o mapeamento de colunas.

**Nenhum dado processado**
→ Verifique se existem registros de Fortaleza no arquivo.

**Muitos duplicados removidos**
→ Normal. O sistema evita inserir dados já processados.

---

**Desenvolvido para o Projeto Fortaleza Segura** 🛡️
