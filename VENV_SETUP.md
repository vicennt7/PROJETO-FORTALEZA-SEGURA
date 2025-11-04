# 🐍 Ambiente Virtual - Fortaleza Segura

## ✅ Ambiente Virtual Criado e Configurado!

O ambiente virtual Python (`venv`) foi criado com sucesso e todas as dependências foram instaladas.

---

## 📦 Dependências Instaladas

### Processamento de Dados
- **pandas** (2.3.3) - Análise de dados
- **numpy** (2.3.4) - Computação numérica
- **openpyxl** (3.1.5) - Leitura de arquivos Excel
- **PyMuPDF** (1.26.5) - Processamento de PDFs

### Web Scraping
- **requests** (2.32.5) - Requisições HTTP
- **beautifulsoup4** (4.14.2) - Parsing HTML
- **lxml** (6.0.2) - Parser XML/HTML
- **urllib3** (2.5.0) - Cliente HTTP

### Banco de Dados
- **SQLAlchemy** (2.0.44) - ORM
- **psycopg2-binary** (2.9.11) - Driver PostgreSQL
- **GeoAlchemy2** (0.18.0) - Extensões geoespaciais

### API / Web
- **fastapi** (0.121.0) - Framework web
- **uvicorn** (0.38.0) - Servidor ASGI
- **starlette** (0.49.3) - Toolkit ASGI
- **pydantic** (2.12.3) - Validação de dados

### Utilitários
- **python-dotenv** (1.2.1) - Variáveis de ambiente
- **click** (8.3.0) - CLI
- **python-dateutil** (2.9.0) - Manipulação de datas

---

## 🚀 Como Usar o Ambiente Virtual

### Windows

```cmd
# Ativar ambiente virtual
venv\Scripts\activate

# Ou use o script de ativação
ativar_venv.bat

# Desativar
deactivate
```

### Linux/Mac

```bash
# Ativar ambiente virtual
source venv/bin/activate

# Ou use o script de ativação
source ativar_venv.sh

# Desativar
deactivate
```

---

## 📋 Comandos Rápidos

### Executar Processamento de Dados

```bash
# 1. Ativar ambiente virtual
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac

# 2. Processar dados SSPDS
python scripts/run_processing.py

# 3. Baixar novos dados
python scripts/carregar_estatisticas_sspds.py

# 4. Iniciar API
python app/main.py
```

---

## 🔄 Reinstalar Dependências

Se precisar reinstalar tudo:

```bash
# Ativar ambiente virtual primeiro
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac

# Instalar do requirements.txt
pip install -r requirements.txt
```

---

## 🆕 Adicionar Nova Dependência

```bash
# 1. Ativar ambiente virtual
venv\Scripts\activate

# 2. Instalar nova biblioteca
pip install nome-da-biblioteca

# 3. Atualizar requirements.txt
pip freeze > requirements.txt
```

---

## 📊 Verificar Instalações

```bash
# Listar todas as bibliotecas instaladas
pip list

# Verificar versão de biblioteca específica
pip show pandas
pip show fastapi
```

---

## 🗑️ Recriar Ambiente Virtual

Se algo der errado:

```bash
# 1. Deletar pasta venv
rmdir /s venv  # Windows
rm -rf venv    # Linux/Mac

# 2. Criar novo ambiente
python -m venv venv

# 3. Ativar
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac

# 4. Instalar dependências
pip install -r requirements.txt
```

---

## 📁 Estrutura do Ambiente Virtual

```
fortaleza-segura/
├── venv/                      # Ambiente virtual ✅
│   ├── Scripts/              # Executáveis (Windows)
│   │   ├── activate.bat      # Ativar venv
│   │   ├── python.exe        # Python isolado
│   │   └── pip.exe           # Gerenciador de pacotes
│   ├── Lib/                  # Bibliotecas instaladas
│   └── pyvenv.cfg            # Configuração
├── requirements.txt          # Lista de dependências ✅
├── ativar_venv.bat          # Script Windows ✅
├── ativar_venv.sh           # Script Linux/Mac ✅
└── VENV_SETUP.md            # Este arquivo ✅
```

---

## ✅ Status das Instalações

### Core
- [x] Python 3.14
- [x] pip 25.3
- [x] venv criado

### Processamento
- [x] pandas
- [x] numpy
- [x] openpyxl
- [x] PyMuPDF

### Web/API
- [x] requests
- [x] beautifulsoup4
- [x] fastapi
- [x] uvicorn

### Banco de Dados
- [x] SQLAlchemy
- [x] psycopg2-binary
- [x] GeoAlchemy2

### Utilitários
- [x] python-dotenv
- [x] lxml

**Total: 37 pacotes instalados com sucesso!**

---

## 🎯 Próximos Passos

1. ✅ Ambiente virtual criado
2. ✅ Dependências instaladas
3. ✅ requirements.txt gerado
4. 🔄 Pronto para usar!

### Para começar a trabalhar:

```bash
# 1. Ative o ambiente
ativar_venv.bat  # Windows

# 2. Execute o processamento
python scripts/run_processing.py

# 3. Veja os resultados em:
# relatorios_sspds/estatisticas_*.json
# relatorios_sspds/insights_*.json
```

---

## 📝 Notas Importantes

- ⚠️ **SEMPRE ative o ambiente virtual antes de trabalhar**
- ⚠️ **NÃO commite a pasta venv/** no Git (já está no .gitignore)
- ✅ **Commite o requirements.txt** para outros desenvolvedores
- ✅ **Use pip freeze** após instalar novas bibliotecas

---

## 🐛 Problemas Comuns

### Erro: "venv\Scripts\activate não é reconhecido"
**Solução:** Use o caminho completo ou navegue até a pasta primeiro
```bash
cd fortaleza-segura
venv\Scripts\activate
```

### Erro: "ModuleNotFoundError"
**Solução:** Verifique se o ambiente está ativado
```bash
# Deve aparecer (venv) no início do prompt
(venv) C:\...\fortaleza-segura>
```

### Erro: "pip não encontrado"
**Solução:** Use python -m pip
```bash
python -m pip install nome-pacote
```

---

## 🔗 Links Úteis

- [Documentação venv](https://docs.python.org/3/library/venv.html)
- [Guia pip](https://pip.pypa.io/en/stable/)
- [requirements.txt](https://pip.pypa.io/en/stable/user_guide/#requirements-files)

---

**Ambiente configurado e pronto para uso!** 🎉
