# 📊 Reporte de Auditoría de Dependencias - GENESIS
**Fecha**: 2025-07-20  
**Estado**: CRÍTICO - Requiere acción inmediata

## 🚨 Problemas Identificados

### 1. Incompatibilidad de OpenTelemetry
**Problema**: Conflicto entre versiones
- `opentelemetry-instrumentation`: 0.54b0 (beta)
- `opentelemetry-api`: ^1.33.0 (estable)
- `opentelemetry-sdk`: ^1.33.0 (estable)

**Error**: `ImportError: cannot import name '_set_status' from 'opentelemetry.instrumentation._semconv'`

**Causa**: Las versiones beta (0.54b0) de instrumentation no son compatibles con las versiones estables (1.33.0) de api/sdk.

### 2. Google Cloud Vision No Disponible
**Problema**: A pesar de estar listado en dependencias
- `google-cloud-vision`: ^3.10.1 está instalado
- Pero el código reporta: "Google Cloud Vision not available. OCR features will be disabled."

**Posibles causas**:
- Falta archivo de credenciales
- Variable de entorno GOOGLE_APPLICATION_CREDENTIALS no configurada
- Problemas de autenticación

### 3. Duplicación de Dependencias
**Problema**: Mismas dependencias en múltiples grupos
- `pydantic` aparece en 4 grupos diferentes
- `httpx` aparece en 3 grupos
- `google-generativeai` aparece en 2 grupos

### 4. Dependencias Conflictivas
**Problema**: Posibles conflictos de versiones
- `protobuf`: ^5.26.1 (puede conflictuar con otras librerías de Google)
- `google-adk`: ^0.1.0 (versión muy temprana, posiblemente inestable)

### 5. Imports Circulares Detectados
**Problema**: Al intentar importar BaseNGXAgent
```
agents.base.base_ngx_agent → core.personality → core.telemetry → opentelemetry
```

## 📋 Plan de Acción Inmediato

### Día 1: Resolver Conflictos de OpenTelemetry
1. **Opción A**: Actualizar todas las instrumentations a versión estable
   ```toml
   opentelemetry-instrumentation = "^0.49b0"  # Última versión compatible
   opentelemetry-instrumentation-fastapi = "^0.49b0"
   opentelemetry-instrumentation-httpx = "^0.49b0"
   opentelemetry-instrumentation-logging = "^0.49b0"
   opentelemetry-instrumentation-aiohttp-client = "^0.49b0"
   ```

2. **Opción B**: Downgrade api/sdk para compatibilidad
   ```toml
   opentelemetry-api = "^1.27.0"
   opentelemetry-sdk = "^1.27.0"
   ```

### Día 2: Configurar Google Cloud Vision
1. Verificar archivo de credenciales existe
2. Configurar variable de entorno correctamente
3. Crear script de validación de servicios Google Cloud
4. Documentar proceso de configuración

### Día 3: Limpiar Dependencias
1. Consolidar dependencias duplicadas
2. Mover todas las dependencias compartidas a la sección principal
3. Eliminar grupos opcionales innecesarios
4. Actualizar poetry.lock

## 🔧 Soluciones Propuestas

### 1. Fix Inmediato para OpenTelemetry
```toml
# Reemplazar todas las versiones de opentelemetry con:
opentelemetry-api = "1.27.0"
opentelemetry-sdk = "1.27.0"
opentelemetry-instrumentation = "0.48b0"
opentelemetry-instrumentation-fastapi = "0.48b0"
opentelemetry-instrumentation-httpx = "0.48b0"
opentelemetry-instrumentation-logging = "0.48b0"
opentelemetry-instrumentation-aiohttp-client = "0.48b0"
```

### 2. Script de Validación de Google Cloud
```python
# verify_google_cloud.py
import os
import sys

def verify_google_cloud_setup():
    """Verifica que Google Cloud esté configurado correctamente."""
    
    # 1. Verificar credenciales
    creds_path = os.environ.get('GOOGLE_APPLICATION_CREDENTIALS')
    if not creds_path:
        print("❌ GOOGLE_APPLICATION_CREDENTIALS no está configurada")
        return False
    
    if not os.path.exists(creds_path):
        print(f"❌ Archivo de credenciales no existe: {creds_path}")
        return False
    
    # 2. Intentar importar servicios
    try:
        from google.cloud import vision
        print("✅ Google Cloud Vision importado correctamente")
    except ImportError as e:
        print(f"❌ Error importando Google Cloud Vision: {e}")
        return False
    
    # 3. Intentar crear cliente
    try:
        client = vision.ImageAnnotatorClient()
        print("✅ Cliente de Vision creado correctamente")
    except Exception as e:
        print(f"❌ Error creando cliente: {e}")
        return False
    
    return True
```

### 3. Resolver Imports Circulares
```python
# core/telemetry.py - Usar imports lazy
def get_tracer():
    """Obtiene tracer con import lazy para evitar circular."""
    from opentelemetry import trace
    return trace.get_tracer(__name__)
```

## 📊 Resumen de Prioridades

| Prioridad | Problema | Impacto | Solución |
|-----------|----------|---------|----------|
| 🔴 CRÍTICA | OpenTelemetry incompatible | Tests no ejecutan | Actualizar versiones |
| 🔴 CRÍTICA | Google Vision no disponible | Features de visión rotas | Configurar credenciales |
| 🟡 ALTA | Imports circulares | Dificulta testing | Refactorizar imports |
| 🟡 ALTA | Dependencias duplicadas | Mantenimiento difícil | Consolidar deps |
| 🟢 MEDIA | google-adk inestable | Posibles bugs | Evaluar alternativas |

## 🚀 Próximos Pasos

1. **Inmediato**: Actualizar opentelemetry a versiones compatibles
2. **Hoy**: Configurar Google Cloud correctamente
3. **Mañana**: Limpiar dependencias y resolver circulares
4. **Día 3**: Validar todo funciona y ejecutar tests

## 📝 Comandos para Ejecutar

```bash
# 1. Actualizar dependencias
poetry update opentelemetry-api opentelemetry-sdk opentelemetry-instrumentation

# 2. Verificar Google Cloud
export GOOGLE_APPLICATION_CREDENTIALS="/path/to/credentials.json"
python verify_google_cloud.py

# 3. Limpiar cache de Poetry
poetry cache clear pypi --all

# 4. Reinstalar todo limpio
poetry install --with dev,test

# 5. Ejecutar test simple
python -m pytest tests/unit/test_settings.py -v
```

---

**Estado**: Esperando aprobación para proceder con las correcciones