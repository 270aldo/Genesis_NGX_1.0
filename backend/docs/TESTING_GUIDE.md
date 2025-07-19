# 🧪 Guía de Testing para Agentes NGX

## 📋 Resumen

Esta guía proporciona información completa sobre cómo escribir, ejecutar y mantener tests para los agentes del sistema NGX GENESIS.

## 🏗️ Estructura de Tests

```
backend/tests/
├── agents/                      # Tests específicos de agentes
│   ├── conftest.py             # Fixtures compartidos
│   ├── test_base_agent.py      # Suite base de tests
│   ├── test_all_agents.py      # Tests para todos los agentes
│   ├── orchestrator/           # Tests del orchestrator
│   │   ├── unit/
│   │   │   └── test_orchestrator_core.py
│   │   └── test_orchestrator_a2a.py
│   ├── precision_nutrition_architect/
│   │   └── unit/
│   │       └── test_sage_core.py
│   └── ... (otros agentes)
├── unit/                       # Tests unitarios generales
├── integration/                # Tests de integración
├── mocks/                      # Mocks compartidos
└── conftest.py                # Configuración global pytest
```

## 🚀 Ejecutar Tests

### Script de Ejecución Rápida

```bash
# Ejecutar todos los tests de agentes
python run_agent_tests.py

# Tests de un agente específico
python run_agent_tests.py --agent sage

# Con cobertura
python run_agent_tests.py --coverage

# Solo tests rápidos (sin integration)
python run_agent_tests.py --fast

# Con reporte HTML
python run_agent_tests.py --coverage --html
```

### Usando Make

```bash
# Todos los tests
make test

# Solo tests de agentes
make test-agents

# Con cobertura
make test-cov

# Reporte HTML
make test-cov-html
```

### Usando pytest directamente

```bash
# Tests de un agente específico
pytest tests/agents/precision_nutrition_architect/ -v

# Tests con un marcador específico
pytest -m agents

# Tests excluyendo los lentos
pytest -m "not slow"

# Con cobertura
pytest --cov=agents --cov-report=term-missing
```

## 📝 Escribir Tests

### 1. Usar la Suite Base

Todos los agentes deben heredar de `BaseAgentTestSuite`:

```python
from tests.agents.test_base_agent import BaseAgentTestSuite

class TestMyAgent(BaseAgentTestSuite):
    agent_class = MyAgentClass
    agent_id = "my_agent_id"
    expected_capabilities = ["capability_1", "capability_2"]
```

### 2. Tests Específicos del Agente

```python
class TestSageSpecific:
    """Tests específicos para SAGE"""
    
    @pytest.fixture
    def sage(self, mock_vertex_ai_client, mock_mcp_toolkit):
        return PrecisionNutritionArchitect(mcp_toolkit=mock_mcp_toolkit)
    
    @pytest.mark.asyncio
    async def test_calculate_macros(self, sage, mock_vertex_ai_client):
        # Configurar mock
        mock_vertex_ai_client.generate_content.return_value = {
            "text": '{"calories": 2500, "protein": 150}',
            "finish_reason": "STOP"
        }
        
        # Ejecutar
        result = await sage.calculate_macros(user_context)
        
        # Verificar
        assert result["calories"] == 2500
        assert result["protein"] == 150
```

### 3. Usar Fixtures

```python
@pytest.fixture
def user_context():
    """Contexto de usuario para tests"""
    return {
        "user_id": "test_123",
        "age": 30,
        "weight": 75,
        "height": 175,
        "gender": "male",
        "fitness_level": "intermediate"
    }

@pytest.mark.asyncio
async def test_with_context(sage, user_context):
    response = await sage.process("Test", user_context)
    assert response is not None
```

### 4. Mocks y Patches

```python
from unittest.mock import patch, AsyncMock

@pytest.mark.asyncio
async def test_with_mocked_service(sage):
    with patch('agents.sage.some_service') as mock_service:
        mock_service.call_api = AsyncMock(return_value={"data": "test"})
        
        result = await sage.some_method()
        
        mock_service.call_api.assert_called_once()
```

## 🎯 Mejores Prácticas

### 1. Nombrado de Tests

```python
# ✅ Bueno: Descriptivo y específico
async def test_calculate_macros_for_muscle_gain_goal()

# ❌ Malo: Vago
async def test_macros()
```

### 2. Organización de Tests

```python
class TestSageCore:
    """Tests principales de funcionalidad"""
    pass

class TestSageValidation:
    """Tests de validación de entrada"""
    pass

class TestSageErrorHandling:
    """Tests de manejo de errores"""
    pass
```

### 3. Tests Asincrónicos

```python
# Siempre usar @pytest.mark.asyncio
@pytest.mark.asyncio
async def test_async_method():
    result = await some_async_function()
    assert result is not None
```

### 4. Cobertura de Casos

Asegúrate de cubrir:
- ✅ Casos exitosos (happy path)
- ✅ Casos de error
- ✅ Casos límite (edge cases)
- ✅ Validación de entrada
- ✅ Manejo de timeouts
- ✅ Respuestas vacías o null

## 📊 Métricas de Calidad

### Objetivos de Cobertura

- **Mínimo**: 70%
- **Objetivo**: 85%
- **Ideal**: 90%+

### Ver Cobertura

```bash
# Reporte en terminal
pytest --cov=agents --cov-report=term-missing

# Reporte HTML
pytest --cov=agents --cov-report=html
open htmlcov/index.html
```

### Excluir de Cobertura

```python
# En .coveragerc o pyproject.toml
[tool.coverage.run]
omit = [
    "*/tests/*",
    "*/mocks/*",
    "*/__init__.py"
]
```

## 🔍 Debugging Tests

### 1. Ejecutar Test Específico

```bash
# Un test específico
pytest tests/agents/sage/test_core.py::TestSageCore::test_calculate_macros -v

# Con output completo
pytest tests/agents/sage/test_core.py -s -v
```

### 2. Usar pdb

```python
@pytest.mark.asyncio
async def test_debug():
    import pdb; pdb.set_trace()
    result = await some_function()
```

### 3. Ver Logs

```python
# En el test
import logging
logging.basicConfig(level=logging.DEBUG)

# O al ejecutar
pytest --log-cli-level=DEBUG
```

## 🏷️ Marcadores (Markers)

### Marcadores Disponibles

```python
@pytest.mark.unit          # Tests unitarios
@pytest.mark.integration   # Tests de integración
@pytest.mark.agents        # Tests específicos de agentes
@pytest.mark.slow          # Tests lentos
@pytest.mark.a2a           # Tests de protocolo A2A
```

### Ejecutar por Marcador

```bash
# Solo unit tests
pytest -m unit

# Excluir tests lentos
pytest -m "not slow"

# Combinar marcadores
pytest -m "agents and not integration"
```

## 🔧 Configuración de Tests

### pytest.ini

```ini
[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
asyncio_mode = "strict"
markers = [
    "unit: Unit tests",
    "integration: Integration tests",
    "agents: Agent-specific tests",
    "slow: Slow tests"
]
```

### Configurar Timeouts

```python
@pytest.mark.timeout(30)  # Timeout de 30 segundos
@pytest.mark.asyncio
async def test_with_timeout():
    await long_running_function()
```

## 🚨 Errores Comunes

### 1. Olvidar @pytest.mark.asyncio

```python
# ❌ Error: no marcado como async
async def test_async():
    await some_function()

# ✅ Correcto
@pytest.mark.asyncio
async def test_async():
    await some_function()
```

### 2. No Mockear Dependencias Externas

```python
# ❌ Malo: Llama a API real
async def test_api_call():
    result = await call_external_api()

# ✅ Bueno: Mock de la API
async def test_api_call(mock_api):
    mock_api.return_value = {"data": "test"}
    result = await call_external_api()
```

### 3. Tests Dependientes

```python
# ❌ Malo: Depende del orden
class TestOrder:
    data = None
    
    def test_create(self):
        self.data = create_data()
    
    def test_use(self):
        use_data(self.data)  # Falla si test_create no se ejecutó

# ✅ Bueno: Tests independientes
class TestIndependent:
    @pytest.fixture
    def data(self):
        return create_data()
    
    def test_use(self, data):
        use_data(data)
```

## 📈 Monitoreo de Tests

### CI/CD Integration

```yaml
# .github/workflows/tests.yml
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Run tests
        run: |
          make test-cov
      - name: Upload coverage
        uses: codecov/codecov-action@v1
```

### Pre-commit Hooks

```yaml
# .pre-commit-config.yaml
repos:
  - repo: local
    hooks:
      - id: pytest-check
        name: pytest-check
        entry: pytest -m unit --quiet
        language: system
        pass_filenames: false
        always_run: true
```

## 🎯 Checklist para PR

Antes de crear un PR, asegúrate de:

- [ ] Todos los tests pasan: `make test`
- [ ] Cobertura >= 85%: `make test-cov`
- [ ] No hay tests marcados como skip sin justificación
- [ ] Tests nuevos para features nuevas
- [ ] Tests actualizados para cambios
- [ ] Sin warnings de deprecación
- [ ] Documentación de tests actualizada

---

**Última actualización**: 2025-07-17  
**Mantenedor**: NGX Platform Team