# 🎛️ Guia do Dashboard Completo - Fortaleza Segura

## ✅ Dashboard com Botões de Controle Criado!

O dashboard agora possui **botões interativos** para executar os scripts de processamento diretamente da interface!

---

## 🎯 Novos Recursos

### 🎛️ Painel de Controle na Sidebar

#### 1. **📥 Baixar Novos Dados SSPDS**
- Executa o script de download
- Busca novos arquivos no site SSPDS
- Mostra progresso em tempo real
- Exibe log de execução

#### 2. **🔄 Processar e Analisar Dados**
- Processa todos os arquivos baixados
- Filtra dados de Fortaleza
- Gera estatísticas e insights
- Atualiza dashboard automaticamente

#### 3. **♻️ Recarregar Dashboard**
- Limpa cache
- Recarrega dados
- Atualiza visualizações

---

## 🚀 Como Usar

### 1. Executar o Dashboard

```bash
# Windows
cd fortaleza-segura
ativar_venv.bat
streamlit run dashboard_completo.py
```

```bash
# Linux/Mac
cd fortaleza-segura
source venv/bin/activate
streamlit run dashboard_completo.py
```

### 2. Workflow Completo

#### Primeira Vez (Sem Dados)

1. **Abra o dashboard** → `streamlit run dashboard_completo.py`
2. **Baixe os dados** → Clique em "📥 Baixar Novos Dados SSPDS"
3. **Aguarde o download** (pode demorar alguns minutos)
4. **Processe os dados** → Clique em "🔄 Processar e Analisar Dados"
5. **Veja os resultados** → Dashboard atualiza automaticamente!

#### Atualizações Diárias

1. **Abra o dashboard**
2. **Baixe novos dados** (se houver)
3. **Processe** → O sistema só processa arquivos novos
4. **Pronto!**

---

## 📊 Estrutura do Dashboard

### **Barra Lateral (Sidebar)**

```
┌─────────────────────────────┐
│  🛡️ Fortaleza Segura        │
├─────────────────────────────┤
│  🎛️ Painel de Controle      │
│                              │
│  ⚙️ Processamento            │
│  [📥 Baixar Dados]           │
│  [🔄 Processar Dados]        │
│                              │
│  🔄 Atualização              │
│  [♻️ Recarregar]            │
│                              │
│  ℹ️ Informações              │
│  ✅ Dados disponíveis        │
│  Última atualização: ...     │
│                              │
│  📁 Status dos Arquivos      │
│  Arquivos SSPDS: 24          │
│  Relatórios: 6               │
└─────────────────────────────┘
```

### **Área Principal**

```
┌─────────────────────────────────────┐
│  🛡️ Fortaleza Segura                │
│  Dashboard de Segurança Pública     │
├─────────────────────────────────────┤
│                                      │
│  📊 Visão Geral (Métricas)          │
│  [Total] [Horário] [Dia] [AIS]      │
│                                      │
│  📑 Abas                             │
│  ├─ ⏰ Análise Temporal              │
│  ├─ 🗺️ Análise Espacial             │
│  ├─ 📈 Tendências                    │
│  ├─ 🚨 Alertas                       │
│  └─ 📄 Dados Brutos                  │
│                                      │
└─────────────────────────────────────┘
```

---

## 🎨 Funcionalidades de Cada Aba

### Aba 1: ⏰ Análise Temporal

**Visualizações:**
- Gráfico de barras: Ocorrências por hora (00:00 - 23:00)
- Tabela: Top 10 horários mais perigosos
- Gráfico de barras: Ocorrências por dia da semana
- Tabela comparativa de dias

**Insights:**
- Identifica horários de pico
- Mostra dias mais perigosos
- Ajuda no planejamento de policiamento

### Aba 2: 🗺️ Análise Espacial

**Visualizações:**
- Gráfico de barras: Distribuição por AIS
- Tabela: Ranking de AIS mais perigosas
- Placeholder para mapa (em breve)

**Insights:**
- Identifica áreas críticas
- Mostra distribuição geográfica
- Ajuda na alocação de recursos

### Aba 3: 📈 Tendências

**Visualizações:**
- Gráfico de linha: Ocorrências por mês
- Gráfico de linha: Ocorrências por ano

**Insights:**
- Identifica sazonalidade
- Mostra tendências de longo prazo
- Detecta padrões temporais

### Aba 4: 🚨 Alertas

**Visualizações:**
- Cards de alertas críticos
- Cards de recomendações

**Insights:**
- Alertas automáticos de risco
- Recomendações de segurança
- Sugestões de ações

### Aba 5: 📄 Dados Brutos

**Visualizações:**
- JSON completo de estatísticas
- JSON completo de insights

**Uso:**
- Exportar dados
- Debugging
- Integração com outros sistemas

---

## 🎯 Fluxo de Execução dos Botões

### Botão: "📥 Baixar Novos Dados SSPDS"

```
1. Clique no botão
   ↓
2. Dashboard mostra "🔄 Executando Download SSPDS..."
   ↓
3. Script busca novos arquivos no site SSPDS
   ↓
4. Baixa apenas arquivos novos/atualizados
   ↓
5. Salva em sspds_downloads/
   ↓
6. Mostra "✅ Download executado com sucesso!"
   ↓
7. Exibe log em expander (opcional)
   ↓
8. Atualiza status na sidebar
```

### Botão: "🔄 Processar e Analisar Dados"

```
1. Clique no botão
   ↓
2. Dashboard mostra "🔄 Executando Processamento..."
   ↓
3. Script processa arquivos Excel
   ↓
4. Filtra dados de Fortaleza
   ↓
5. Gera estatísticas
   ↓
6. Cria insights e análises
   ↓
7. Exporta JSON para relatorios_sspds/
   ↓
8. Mostra "✅ Processamento executado com sucesso!"
   ↓
9. Limpa cache
   ↓
10. Dashboard recarrega automaticamente com novos dados
    ↓
11. 🎉 Balões celebrando!
```

---

## 📊 Indicadores de Status

### Status na Sidebar

#### ✅ Dados Disponíveis
```
✅ Dados disponíveis
Última atualização:
04/11/2025 às 14:30
```

#### ⚠️ Sem Dados
```
⚠️ Nenhum dado processado
Clique em 'Processar Dados'
```

#### ❌ Erro
```
❌ Pasta de relatórios não encontrada
```

### Status dos Arquivos

```
📁 Status dos Arquivos
┌────────────────────┐
│ Arquivos SSPDS: 24 │
│ Relatórios: 6      │
└────────────────────┘
```

---

## 🎨 Recursos Visuais

### Cores e Feedback

**Sucesso (Verde):**
- ✅ "Dados disponíveis"
- ✅ "Script executado com sucesso"

**Aviso (Amarelo):**
- ⚠️ "Nenhum dado processado"
- ⚠️ "Sem dados disponíveis"

**Erro (Vermelho):**
- ❌ "Erro ao executar script"
- ❌ "Pasta não encontrada"

**Info (Azul):**
- ℹ️ "Funcionalidade em breve"
- 💡 "Recomendações"

### Animações

- 🎈 **Balões** após processamento bem-sucedido
- 🔄 **Spinner** durante execução de scripts
- ⏱️ **Progress bar** (futura implementação)

---

## 🔧 Personalização

### Mudar Timeout dos Scripts

```python
# No arquivo dashboard_completo.py, linha ~45
stdout, stderr = process.communicate(timeout=300)  # 5 minutos

# Altere para:
stdout, stderr = process.communicate(timeout=600)  # 10 minutos
```

### Adicionar Novos Botões

```python
# Na sidebar:
if st.button("🆕 Meu Novo Script", use_container_width=True):
    sucesso = executar_script(
        "scripts/meu_script.py",
        "Meu Script"
    )
```

### Mudar Layout

```python
# Trocar de wide para centered:
st.set_page_config(
    layout="centered"  # ou "wide"
)
```

---

## 🐛 Solução de Problemas

### Problema: Botão não funciona

**Causa:** Script não encontrado

**Solução:**
```bash
# Verifique se o script existe
dir scripts\run_processing.py
```

### Problema: "Timeout"

**Causa:** Script demora mais de 5 minutos

**Solução:** Aumente o timeout (veja seção Personalização)

### Problema: Erro de encoding

**Causa:** Windows com charset diferente

**Solução:** O dashboard já trata isso com `encoding='utf-8', errors='replace'`

### Problema: Dashboard não atualiza após processar

**Causa:** Cache não foi limpo

**Solução:** Clique em "♻️ Recarregar Dashboard"

---

## 📱 Acesso Remoto

### Compartilhar na Rede Local

```bash
# Execute com configuração de rede:
streamlit run dashboard_completo.py --server.address 0.0.0.0
```

**Acesse de outros PCs:**
```
http://SEU_IP:8501
```

### Descobrir Seu IP

**Windows:**
```cmd
ipconfig
```
Procure "IPv4 Address"

**Linux/Mac:**
```bash
ifconfig | grep inet
```

---

## ⚡ Atalhos de Teclado

| Tecla | Ação |
|-------|------|
| **R** | Recarregar dashboard |
| **C** | Limpar cache |
| **Ctrl+F** | Buscar na página |
| **F11** | Tela cheia |

---

## 📊 Exemplo de Uso Completo

### Cenário: Análise Semanal

```
Segunda-feira 8h00:
1. Abrir dashboard
2. Clicar "📥 Baixar Novos Dados"
3. Aguardar download (2-3 min)
4. Clicar "🔄 Processar Dados"
5. Aguardar processamento (1-2 min)
6. Analisar métricas na visão geral
7. Ir para aba "🚨 Alertas"
8. Anotar recomendações
9. Ir para aba "📈 Tendências"
10. Verificar evolução semanal
```

**Tempo total: ~10 minutos**

---

## 🎯 Próximas Melhorias

### Planejadas

1. **Agendamento Automático**
   - Processar dados todo dia às 8h
   - Enviar relatório por email

2. **Exportação de Relatórios**
   - Botão para baixar PDF
   - Botão para baixar Excel

3. **Mapa Interativo**
   - Mapa de calor de Fortaleza
   - Marcadores por bairro
   - Popup com detalhes

4. **Filtros Avançados**
   - Filtrar por período
   - Filtrar por tipo de crime
   - Filtrar por bairro

5. **Notificações**
   - Alert quando processar terminar
   - Notificação de novos dados

---

## ✅ Checklist de Uso

Antes de usar o dashboard:

- [ ] Ambiente virtual ativado
- [ ] Streamlit instalado
- [ ] Pasta `sspds_downloads/` existe
- [ ] Pasta `relatorios_sspds/` existe
- [ ] Internet conectada (para baixar dados)

---

## 🚀 Comando Rápido

```bash
# Um único comando para tudo:
cd fortaleza-segura && ativar_venv.bat && streamlit run dashboard_completo.py
```

---

## 📞 Suporte

**Problemas?**
1. Verifique a aba "📄 Dados Brutos" para ver se há dados
2. Clique em "♻️ Recarregar Dashboard"
3. Verifique os logs nos expanders após executar scripts

---

**Dashboard Completo - Fortaleza Segura** 🛡️
**Status: ✅ Funcional com Botões Interativos!**
