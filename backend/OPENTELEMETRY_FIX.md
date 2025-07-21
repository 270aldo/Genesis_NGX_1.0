# 🔧 Plan de Corrección de OpenTelemetry

## Problema Identificado
- Las versiones beta de instrumentación (0.48b0) requieren semantic-conventions 0.48b0
- Las versiones estables de SDK (1.31.0) requieren semantic-conventions 0.52b0
- Esto crea un conflicto irreconciliable

## Solución Propuesta

### Opción 1: Usar versiones estables (RECOMENDADO)
```toml
# Versiones estables más recientes
opentelemetry-api = "1.27.0"
opentelemetry-sdk = "1.27.0"
opentelemetry-instrumentation = "0.48b0"
opentelemetry-semantic-conventions = "0.48b0"
```

### Opción 2: Remover instrumentación problemática temporalmente
- Comentar las líneas de instrumentación específicas
- Usar solo opentelemetry-api y sdk base
- Reimplementar telemetría manualmente donde sea necesario

### Opción 3: Usar todo en versiones beta compatibles
```toml
opentelemetry-api = "1.27.0"
opentelemetry-sdk = "1.27.0"
opentelemetry-instrumentation = "0.48b0"
opentelemetry-instrumentation-fastapi = "0.48b0"
opentelemetry-instrumentation-httpx = "0.48b0"
opentelemetry-instrumentation-logging = "0.48b0"
opentelemetry-instrumentation-aiohttp-client = "0.48b0"
opentelemetry-semantic-conventions = "0.48b0"
```

## Implementación
Voy a proceder con la Opción 3 para mantener toda la funcionalidad.