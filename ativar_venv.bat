@echo off
REM Script para ativar o ambiente virtual no Windows

echo ========================================
echo Ativando ambiente virtual...
echo ========================================

call venv\Scripts\activate.bat

echo.
echo Ambiente virtual ativado!
echo Para desativar, digite: deactivate
echo.
echo ========================================
echo Comandos disponiveis:
echo ========================================
echo python scripts/run_processing.py        - Processar dados SSPDS
echo python scripts/carregar_estatisticas_sspds.py - Baixar novos dados
echo python app/main.py                      - Iniciar API FastAPI
echo ========================================
