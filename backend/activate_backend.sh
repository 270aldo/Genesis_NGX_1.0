#!/bin/bash
# Script para activar el entorno del backend GENESIS

echo "Activando entorno GENESIS backend..."

# Activar virtual environment
source /Users/aldoolivas/Desktop/GENESIS_oficial_BETA/backend/.venv/bin/activate

# Configurar PYTHONPATH
export PYTHONPATH=/Users/aldoolivas/Desktop/GENESIS_oficial_BETA/backend:$PYTHONPATH

# Cambiar al directorio del backend
cd /Users/aldoolivas/Desktop/GENESIS_oficial_BETA/backend

echo "✅ Entorno activado"
echo "Python: $(which python)"
echo "Version: $(python --version)"
echo "PYTHONPATH: $PYTHONPATH"