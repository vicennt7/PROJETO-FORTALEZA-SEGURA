#!/bin/bash
# Script para ativar o ambiente virtual no Linux/Mac

echo "========================================"
echo "Ativando ambiente virtual..."
echo "========================================"

source venv/bin/activate

echo ""
echo "Ambiente virtual ativado!"
echo "Para desativar, digite: deactivate"
echo ""
echo "========================================"
echo "Comandos disponíveis:"
echo "========================================"
echo "python scripts/run_processing.py        - Processar dados SSPDS"
echo "python scripts/carregar_estatisticas_sspds.py - Baixar novos dados"
echo "python app/main.py                      - Iniciar API FastAPI"
echo "========================================"
