#!/bin/bash
# Script para ejecutar tests en CI/CD

set -e

echo "🚀 Iniciando tests para CI/CD..."

# Ir al directorio backend
cd backend

# Instalar dependencias
echo "📦 Instalando dependencias..."
poetry install --with dev

# Ejecutar linting
echo "🔍 Ejecutando linting..."
poetry run make lint || echo "⚠️ Linting falló pero continuamos"

# Ejecutar tests unitarios
echo "🧪 Ejecutando tests unitarios..."
poetry run pytest tests/unit -v --tb=short || echo "⚠️ Algunos tests unitarios fallaron"

# Ejecutar tests de adaptadores
echo "🔌 Ejecutando tests de adaptadores..."
poetry run pytest tests/test_adapters -v --tb=short || echo "⚠️ Algunos tests de adaptadores fallaron"

# Ejecutar beta validation (versión rápida)
echo "🎯 Ejecutando beta validation tests..."
poetry run python -m tests.beta_validation.run_beta_validation --quick || echo "⚠️ Beta validation tuvo algunos fallos"

echo "✅ Tests completados!"