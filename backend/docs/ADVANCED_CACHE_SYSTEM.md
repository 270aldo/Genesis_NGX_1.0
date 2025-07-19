# 🚀 Sistema de Caché Avanzado Multi-Capa - GENESIS

## 📋 Resumen

El sistema de caché avanzado de GENESIS implementa una arquitectura multi-capa de alto rendimiento que mejora drásticamente la velocidad de respuesta y reduce la carga en los sistemas externos.

### Características Principales

- **3 Capas de Caché**: L1 (Memory), L2 (Redis), L3 (Database)
- **Múltiples Estrategias**: Standard, SWR, Tagged, Personalized
- **Auto-optimización**: Distribución inteligente entre capas
- **Métricas en Tiempo Real**: Hit ratios, latencias, eficiencia
- **Prefetching Predictivo**: Anticipa necesidades futuras

## 🏗️ Arquitectura

```
┌─────────────────────────────────────────┐
│          Solicitud del Usuario          │
└────────────────┬────────────────────────┘
                 │
┌────────────────▼────────────────────────┐
│         L1: Memory Cache                │
│  • Ultra-rápido (<1ms)                  │
│  • 50MB capacity                        │
│  • LRU/LFU eviction                     │
└────────────────┬────────────────────────┘
                 │ Miss
┌────────────────▼────────────────────────┐
│          L2: Redis Cache                │
│  • Rápido (<10ms)                       │
│  • 500MB capacity                       │
│  • Distribuido                          │
└────────────────┬────────────────────────┘
                 │ Miss
┌────────────────▼────────────────────────┐
│        L3: Database Cache               │
│  • Persistente                          │
│  • 2GB capacity                         │
│  • Long-term storage                    │
└─────────────────────────────────────────┘
```

## 🔧 Configuración

### Variables de Entorno

```bash
# Redis Configuration
REDIS_URL=redis://localhost:6379/0
REDIS_MAX_CONNECTIONS=50
REDIS_CONNECTION_TIMEOUT=20
REDIS_SOCKET_TIMEOUT=5

# Cache Sizes (MB)
L1_CACHE_SIZE_MB=50
L2_CACHE_SIZE_MB=500
L3_CACHE_SIZE_MB=2000

# Cache Strategy
CACHE_READ_STRATEGY=READ_THROUGH
CACHE_WRITE_STRATEGY=WRITE_THROUGH
CACHE_EVICTION_POLICY=ADAPTIVE
```

## 📖 Uso Básico

### 1. Importar el Sistema

```python
from core.advanced_cache_manager import (
    get_cached_value,
    set_cached_value,
    get_cache_analytics
)
from core.cache_strategies import (
    cached,
    standard_cache,
    tagged_cache,
    personalized_cache
)
```

### 2. Guardar y Obtener Valores

```python
# Guardar en caché
await set_cached_value(
    key="user:123:profile",
    value={"name": "John", "age": 30},
    ttl=3600,  # 1 hora
    priority=CachePriority.HIGH
)

# Obtener del caché
profile = await get_cached_value("user:123:profile")
```

### 3. Usar Decoradores

```python
@cached(ttl=1800, key_prefix="agent_response")
async def get_expensive_data(param: str) -> dict:
    # Esta función solo se ejecuta en cache miss
    return expensive_computation(param)
```

## 🎯 Estrategias de Caché

### 1. Standard Cache
Caché tradicional con TTL fijo.

```python
await standard_cache.set("key", "value", ttl=3600)
value = await standard_cache.get("key")
```

### 2. Stale-While-Revalidate (SWR)
Sirve contenido stale mientras actualiza en segundo plano.

```python
async def fetch_fresh_data():
    return await api.get_latest_data()

data = await swr_cache.get(
    "metrics",
    revalidate_func=fetch_fresh_data
)
```

### 3. Tagged Cache
Permite invalidar grupos de entradas por tags.

```python
# Guardar con tags
await tagged_cache.set(
    "article:1",
    article_data,
    tags=["sports", "nutrition"]
)

# Invalidar todos los artículos de nutrición
await tagged_cache.delete_by_tag("nutrition")
```

### 4. Personalized Cache
Caché específico por usuario o segmento.

```python
# Cache por usuario
await personalized_cache.set(
    "preferences",
    user_prefs,
    user_id="user_123"
)

# Cache por segmento
await personalized_cache.set(
    "recommendations",
    recs,
    segment="premium_users"
)
```

## 📊 Métricas y Analíticas

### Obtener Estadísticas Completas

```python
stats = await get_cache_analytics()

# Estadísticas globales
print(f"Hit ratio: {stats['global_statistics']['global_hit_ratio']:.2%}")
print(f"Response time: {stats['global_statistics']['average_response_time_ms']}ms")

# Por capa
for layer, data in stats['layer_statistics'].items():
    print(f"{layer}: {data['hit_ratio']:.2%} hit ratio")
```

### Optimización Automática

```python
# El sistema optimiza automáticamente la distribución
result = await advanced_cache_manager.optimize_cache_distribution()
```

## 🚀 Mejores Prácticas

### 1. Elegir la Capa Correcta

- **L1 (Memory)**: Datos muy frecuentes, pequeños
- **L2 (Redis)**: Datos compartidos entre instancias
- **L3 (Database)**: Datos grandes, menos frecuentes

### 2. TTL Apropiados

```python
# Datos estáticos (capacidades de agentes)
TTL_STATIC = 7200  # 2 horas

# Datos dinámicos (métricas)
TTL_DYNAMIC = 300  # 5 minutos

# Datos personalizados (perfiles)
TTL_PERSONAL = 3600  # 1 hora
```

### 3. Prioridades

```python
# Alta prioridad - mantener en L1
CachePriority.CRITICAL  # Datos críticos del sistema
CachePriority.HIGH      # Usuarios activos

# Prioridad normal - L2
CachePriority.NORMAL    # Datos generales

# Baja prioridad - puede ir a L3
CachePriority.LOW       # Datos históricos
```

## 🔌 Integración con FastAPI

### Ejemplo de Router con Caché

```python
from fastapi import APIRouter
from core.advanced_cache_manager import get_cached_value, set_cached_value

router = APIRouter()

@router.get("/api/v1/agents/{agent_id}")
async def get_agent_info(agent_id: str):
    # Check cache first
    cache_key = f"agent:{agent_id}:info"
    cached = await get_cached_value(cache_key)
    
    if cached:
        return {"data": cached, "cached": True}
    
    # Get from database
    agent_info = await db.get_agent(agent_id)
    
    # Store in cache
    await set_cached_value(
        cache_key,
        agent_info,
        ttl=3600,
        priority=CachePriority.NORMAL
    )
    
    return {"data": agent_info, "cached": False}
```

## 🔍 Monitoreo

### Logs de Caché

```python
# Los logs incluyen:
# - Cache hits/misses
# - Tiempos de respuesta
# - Evictions
# - Errores

logger.info("Cache hit L1: user:123:profile")
logger.debug("Cache miss completo: metrics:daily")
```

### Métricas Prometheus

```python
# Métricas expuestas en /metrics
cache_hit_total{layer="l1"} 12345
cache_miss_total{layer="l2"} 678
cache_response_time_seconds{layer="l1"} 0.001
cache_size_bytes{layer="l2"} 52428800
```

## 🚨 Troubleshooting

### 1. Redis No Disponible

El sistema automáticamente degrada a modo L1-only:

```python
# Log esperado:
# ⚠️ Redis no disponible - usando solo caché en memoria
```

### 2. Cache Misses Altos

Verificar:
- TTLs muy cortos
- Claves no consistentes
- Datos no cacheables

### 3. Memoria Llena

El sistema aplica eviction automática:
- LRU para L1
- TTL-based para L2
- Size-based para L3

## 🎯 Casos de Uso Recomendados

### 1. Respuestas de Agentes

```python
@cached(ttl=1800, key_prefix="agent")
async def get_agent_response(agent_id: str, prompt: str):
    return await agent.process(prompt)
```

### 2. Perfiles de Usuario

```python
cache_key = f"user:{user_id}:full_profile"
await set_cached_value(
    cache_key,
    profile,
    ttl=3600,
    priority=CachePriority.HIGH
)
```

### 3. Métricas del Dashboard

```python
# Usar SWR para métricas
metrics = await swr_cache.get(
    "dashboard:metrics",
    revalidate_func=calculate_metrics
)
```

### 4. Configuraciones

```python
# Cachear indefinidamente configuraciones
await set_cached_value(
    "config:app_settings",
    settings,
    ttl=None,  # Sin expiración
    priority=CachePriority.CRITICAL
)
```

## 📈 Impacto en Performance

### Métricas Esperadas

- **Reducción de Latencia**: 80-95%
- **Hit Ratio Target**: >85%
- **Reducción de Carga DB**: 70%
- **Ahorro en Costos**: 60%

### Antes vs Después

```
Antes (sin caché):
- Agent response: 1200ms
- DB queries/min: 5000
- Vertex AI calls/min: 200

Después (con caché):
- Agent response: 50ms (L1 hit)
- DB queries/min: 500
- Vertex AI calls/min: 20
```

## 🔐 Consideraciones de Seguridad

1. **No cachear datos sensibles sin encriptar**
2. **Usar TTLs cortos para datos de autenticación**
3. **Limpiar caché en logout**
4. **Validar permisos en cada request**

```python
# Limpiar caché de usuario en logout
await personalized_cache.delete_user_cache(user_id)
```

## 🚀 Próximos Pasos

1. **Activar Redis en Producción**
   ```bash
   docker run -d -p 6379:6379 redis:7-alpine
   ```

2. **Configurar Monitoreo**
   - Grafana dashboards
   - Alertas de hit ratio bajo
   - Métricas de eviction

3. **Optimizar TTLs**
   - Analizar patrones de uso
   - Ajustar según métricas
   - A/B testing de estrategias

---

**Última actualización**: 2025-07-17  
**Versión**: 1.0.0  
**Mantenedor**: NGX Platform Team