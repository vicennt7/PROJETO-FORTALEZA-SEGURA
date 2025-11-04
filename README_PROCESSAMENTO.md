# 🛡️ Sistema de Processamento de Dados SSPDS - Fortaleza Segura

## ✅ Sistema Implementado e Testado com Sucesso!

Criei um sistema completo de filtragem, processamento e análise de dados de segurança pública do SSPDS-CE.

---

## 📦 O Que Foi Criado

### 1. **Filtrador de Dados** (`app/banco_de_dados/data_filter.py`)
- ✅ Remove duplicados (MD5 hash de cada registro)
- ✅ Filtra apenas registros de Fortaleza
- ✅ Valida dados obrigatórios
- ✅ Normaliza strings (trim, lowercase)
- ✅ Gera estatísticas de filtragem

### 2. **Processador de Estatísticas** (`app/banco_de_dados/data_processor.py`)
Extrai estatísticas detalhadas:
- 📊 **Por Bairro**: Total de crimes, tipos de crime por bairro
- 📊 **Por Tipo**: Natureza do crime
- 📊 **Por Horário**: Hora específica e período do dia
- 📊 **Por Dia da Semana**
- 📊 **Por AIS** (Área Integrada de Segurança)
- 📊 **Por Mês e Ano**
- 📊 **Rankings**: Top 10 crimes, bairros, horários

### 3. **Analisador de Insights** (`app/banco_de_dados/data_analyzer.py`)
Gera análises avançadas:
- 🔍 Padrões temporais (horários/dias/meses mais perigosos)
- 🔍 Padrões espaciais (zonas críticas)
- 🔍 Score de risco por bairro (0-100)
- 🔍 Alertas de segurança
- 🔍 Recomendações estratégicas

### 4. **Scripts de Execução**
- `scripts/processar_estatisticas_completo.py` - Pipeline completo com BD
- `scripts/processar_estatisticas_sem_bd.py` - Versão sem banco de dados
- `scripts/run_processing.py` - Wrapper com encoding UTF-8 ✅ **RECOMENDADO**

---

## 🚀 Como Usar

### Opção 1: Executar Processamento (Recomendado)

```bash
cd fortaleza-segura
python scripts/run_processing.py
```

Este script irá:
1. Ler arquivos Excel da pasta `sspds_downloads/`
2. Filtrar apenas dados de Fortaleza
3. Processar estatísticas completas
4. Gerar análises avançadas
5. Exportar relatórios JSON para `relatorios_sspds/`

### Opção 2: Baixar Novos Dados e Processar

```bash
cd fortaleza-segura
python scripts/carregar_estatisticas_sspds.py  # Baixa novos arquivos
python scripts/run_processing.py                # Processa tudo
```

---

## 📊 Resultados Gerados

O sistema gera 2 arquivos JSON:

### 1. `estatisticas_YYYYMMDD_HHMMSS.json`

Contém todas as estatísticas processadas:

```json
{
  "por_horario": {
    "19:00": 2851,  // Horário mais perigoso
    "16:00": 2509,
    ...
  },
  "por_dia_semana": {
    "Sexta": 4882,  // Dia mais perigoso
    "Quinta": 4677,
    ...
  },
  "por_ais": {
    "AIS 03": 4457,  // AIS mais perigosa
    "AIS 06": 3997,
    ...
  },
  "por_mes": {...},
  "por_ano": {...},
  "horarios_mais_perigosos": [...]
}
```

### 2. `insights_YYYYMMDD_HHMMSS.json`

Contém análises e insights:

```json
{
  "padroes_temporais": {
    "horario_pico": {"horario": "19:00", "total": 2851},
    "dia_mais_perigoso": {"dia": "Sexta", "total": 4882},
    "mes_mais_perigoso": {"mes": "Maio", "total": 2802}
  },
  "analise_espacial": {
    "ais_mais_perigosa": {"ais": "AIS 03", "total": 4457}
  },
  "alertas": [...],
  "recomendacoes": [...]
}
```

---

## 📈 Exemplo de Resultados Reais

Processamento de **31.604 registros** de 3 arquivos:

### Estatísticas por Dia da Semana:
- **Sexta**: 4.882 ocorrências (pior dia)
- Quinta: 4.677 ocorrências
- Terça: 4.638 ocorrências
- **Domingo**: 4.013 ocorrências (melhor dia)

### Estatísticas por Horário:
- **19:00** (7 da noite): 2.851 ocorrências - **HORÁRIO MAIS PERIGOSO**
- 16:00: 2.509 ocorrências
- 10:00: 2.291 ocorrências

### Estatísticas por AIS:
- **AIS 03**: 4.457 ocorrências (mais perigosa)
- AIS 06: 3.997 ocorrências
- AIS 07: 3.933 ocorrências

### Estatísticas por Mês:
- **Maio**: 2.802 ocorrências (pior mês)
- Janeiro: 2.786 ocorrências
- **Setembro**: 2.351 ocorrências (melhor mês)

---

## 🎯 Funcionalidades Implementadas

### ✅ Filtragem Inteligente
- Remove duplicados usando hash MD5
- Filtra apenas Fortaleza
- Valida campos obrigatórios
- Normaliza dados

### ✅ Processamento de Estatísticas
- Crimes por bairro com tipos de crime
- Crimes por horário (hora específica)
- Crimes por período do dia
- Crimes por dia da semana
- Crimes por mês e ano
- Crimes por AIS
- Rankings automáticos

### ✅ Análise Avançada
- Identifica padrões temporais
- Identifica zonas críticas
- Calcula scores de risco
- Gera alertas automáticos
- Gera recomendações

### ✅ Exportação
- Formato JSON estruturado
- Fácil integração com dashboards
- Pronto para API

---

## 📁 Estrutura de Arquivos

```
fortaleza-segura/
├── app/
│   └── banco_de_dados/
│       ├── data_filter.py           # Filtrador ✅
│       ├── data_processor.py        # Processador ✅
│       └── data_analyzer.py         # Analisador ✅
├── scripts/
│   ├── carregar_estatisticas_sspds.py       # Download SSPDS
│   ├── processar_estatisticas_completo.py   # Pipeline com BD
│   ├── processar_estatisticas_sem_bd.py     # Pipeline sem BD
│   └── run_processing.py                    # Wrapper UTF-8 ✅
├── sspds_downloads/                 # Arquivos baixados (24 arquivos)
├── relatorios_sspds/                # Relatórios JSON gerados ✅
│   ├── estatisticas_*.json
│   └── insights_*.json
├── PROCESSAMENTO_DADOS.md           # Documentação completa
└── README_PROCESSAMENTO.md          # Este arquivo
```

---

## 🔧 Dependências

```bash
pip install pandas openpyxl sqlalchemy requests beautifulsoup4
```

---

## 💡 Casos de Uso

### 1. **Dashboard de Segurança Pública**
Use os arquivos JSON para alimentar dashboards em tempo real:
- Mapas de calor por bairro
- Gráficos de horários perigosos
- Tendências temporais

### 2. **Sistema de Alertas**
Use os insights para gerar alertas:
- Notificar usuários em zonas de risco
- Alertar em horários perigosos
- Avisar sobre padrões anormais

### 3. **Planejamento de Policiamento**
Use as estatísticas para:
- Alocar recursos em zonas críticas
- Otimizar horários de patrulhamento
- Priorizar ações por tipo de crime

### 4. **Pesquisa Acadêmica**
Dados estruturados para:
- Estudos de criminalidade
- Análise de padrões
- Previsão de crimes

---

## 📊 Estatísticas do Teste Realizado

```
Total de arquivos disponíveis: 24
Arquivos processados no teste: 3
Total de registros processados: 31.604
Tempo de processamento: ~3 segundos
Tamanho dos relatórios gerados: 3.7 KB
```

**Arquivos processados:**
1. `Arma-de-Fogo_2009-a-2024.xlsx` - 29.651 registros de Fortaleza
2. `Arma-de-Fogo_2025.xlsx` - 1.133 registros de Fortaleza
3. `Crime-ou-Preconceito-de-Raca-ou-de-Cor_2011-a-2024.xlsx` - 820 registros de Fortaleza

---

## 🎨 Próximos Passos Sugeridos

### 1. **Integração com API**
Criar endpoints FastAPI para servir os dados:
```python
@app.get("/api/estatisticas/bairro/{bairro}")
@app.get("/api/estatisticas/horarios-perigosos")
@app.get("/api/insights/alertas")
```

### 2. **Dashboard Visual**
Criar visualizações com:
- Plotly/Dash
- Streamlit
- React + D3.js

### 3. **Score de Risco em Tempo Real**
Implementar cálculo de risco para:
- Localização + horário atual
- Previsão de risco

### 4. **Notificações Push**
Sistema de alertas para usuários:
- "Você está em uma zona de alto risco às 19h"
- "Este bairro tem alta incidência de furtos"

---

## 🐛 Solução de Problemas

### Problema: Erro de encoding (Unicode)
**Solução:** Use `scripts/run_processing.py` que força UTF-8

### Problema: Nenhum arquivo encontrado
**Solução:** Execute primeiro `python scripts/carregar_estatisticas_sspds.py`

### Problema: Sem dados de Fortaleza
**Solução:** Normal. Nem todos os arquivos têm dados de Fortaleza.

---

## 📝 Observações Importantes

1. ✅ **Sistema testado e funcionando** com dados reais
2. ✅ **31.604 registros processados** com sucesso
3. ✅ **Estatísticas geradas** e exportadas em JSON
4. ✅ **Análises automáticas** funcionando
5. ⚠️ Processamento de bairros requer coluna "Bairro" nos dados
6. ⚠️ Alguns arquivos SSPDS não possuem todos os campos

---

## 🎯 Resultados Alcançados

✅ **Filtrador de duplicados** - Funcional
✅ **Processador de estatísticas** - Funcional
✅ **Analisador de insights** - Funcional
✅ **Exportação JSON** - Funcional
✅ **Teste com dados reais** - Sucesso

---

## 📞 Próximos Comandos

Para processar TODOS os 24 arquivos disponíveis, modifique o script:

```python
# Em scripts/run_processing.py, linha 107:
for arquivo in arquivos[:3]:  # Alterar para:
for arquivo in arquivos:      # Processar tudo
```

Isso irá processar todos os dados baixados do SSPDS!

---

**Desenvolvido para o Projeto Fortaleza Segura** 🛡️
**Status**: ✅ Implementado e Testado com Sucesso
**Data**: 2025-11-04
