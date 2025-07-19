# 🦾 Sistema de Embeddings - NGX Agents

## Descripción General

El sistema de embeddings de NGX Agents proporciona una infraestructura completa para generar, almacenar y buscar embeddings vectoriales de alta dimensión. Utiliza el modelo más avanzado de Google (`text-embedding-large-exp-03-07`) y combina almacenamiento persistente en la nube con búsqueda vectorial escalable.

## Arquitectura

```
┌─────────────────────────────────────────────────────────────┐
│                      Aplicación NGX                          │
├─────────────────────────────────────────────────────────────┤
│                   EmbeddingsManager                          │
│  ┌──────────────┬──────────────┬─────────────────────────┐ │
│  │ Generación   │ Almacenamiento│      Búsqueda          │ │
│  │ Embeddings   │   Híbrido     │   Inteligente          │ │
│  └──────┬───────┴───────┬──────┴──────────┬──────────────┘ │
│         │               │                  │                 │
├─────────┼───────────────┼──────────────────┼────────────────┤
│         ▼               ▼                  ▼                 │
│  ┌─────────────┐ ┌─────────────┐ ┌────────────────┐        │
│  │ Vertex AI   │ │    GCS      │ │ Vector Search  │        │
│  │ Embeddings  │ │  Storage    │ │   (Vertex AI)  │        │
│  │ API Model   │ │  (Bucket)   │ │ Index+Endpoint │        │
│  └─────────────┘ └─────────────┘ └────────────────┘        │
│         │               │                  │                 │
│  ┌──────┴───────────────┴──────────────────┴──────────────┐ │
│  │              Caché en Memoria (Redis/Local)            │ │
│  └────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

## Componentes Principales

### 1. EmbeddingsManager (`core/embeddings_manager.py`)

Gestor centralizado que coordina todas las operaciones de embeddings.

**Características principales:**
- Generación de embeddings individuales y en lote
- Almacenamiento híbrido (memoria + GCS)
- Búsqueda semántica con fallback inteligente
- Gestión de caché con TTL configurable
- Estadísticas y métricas de uso

**Configuración:**
```python
embeddings_manager = EmbeddingsManager(
    cache_enabled=True,
    cache_ttl=86400,  # 24 horas
    vector_dimension=3072,  # Para text-embedding-large-exp-03-07
    similarity_threshold=0.7,
    use_gcs=True,
    gcs_prefix="embeddings/",
    use_vector_search=True
)
```

### 2. Modelo de Embeddings

**Modelo**: `text-embedding-large-exp-03-07`
- **Dimensiones**: 3072
- **Tipo**: Experimental de Google (mejor rendimiento)
- **Ventajas**: Mayor precisión en búsquedas semánticas
- **Casos de uso**: Contexto de conversaciones, búsqueda de conocimiento

### 3. Almacenamiento en GCS

**Configuración:**
- **Bucket**: `agents_ngx`
- **Región**: US (multi-región)
- **Estructura**: `embeddings/{key}.json`
- **Formato**: JSON con embedding, texto, metadata y timestamp

**Ventajas:**
- Almacenamiento ilimitado y económico
- Backup automático
- Acceso global
- Integración nativa con Google Cloud

### 4. Vector Search

**Configuración:**
- **Index ID**: `5755708075919015936`
- **Endpoint ID**: `9027115808366526464`
- **Algoritmo**: Tree-AH (optimizado para alta precisión)
- **Neighbors**: 100 (búsquedas amplias)
- **Distancia**: Coseno (ideal para embeddings normalizados)

**Características:**
- Búsqueda en millones de vectores en milisegundos
- Escalabilidad automática
- Filtros avanzados
- Actualización en lote

## API de Uso

### Generar Embeddings

```python
# Individual
embedding = await embeddings_manager.generate_embedding("Texto a convertir")

# En lote
embeddings = await embeddings_manager.batch_generate_embeddings([
    "Texto 1",
    "Texto 2",
    "Texto 3"
])
```

### Almacenar Embeddings

```python
# Almacenar con metadata
success = await embeddings_manager.store_embedding(
    key="conversation_123",
    text="¿Cuál es el mejor ejercicio para ganar músculo?",
    metadata={
        "user_id": "user_456",
        "agent": "training_strategist",
        "timestamp": "2025-05-31T20:00:00Z"
    }
)

# Almacenamiento en lote
items = [
    {
        "key": "doc_001",
        "text": "Plan de entrenamiento de fuerza",
        "metadata": {"type": "training_plan"}
    },
    {
        "key": "doc_002",
        "text": "Guía nutricional para volumen",
        "metadata": {"type": "nutrition_guide"}
    }
]
results = await embeddings_manager.batch_store_embeddings(items)
```

### Buscar por Similitud

```python
# Búsqueda semántica
results = await embeddings_manager.find_similar(
    query="ejercicios para brazos",
    top_k=5,
    threshold=0.7
)

# Procesar resultados
for result in results:
    print(f"Key: {result['key']}")
    print(f"Texto: {result['text']}")
    print(f"Similitud: {result['similarity']:.3f}")
    print(f"Metadata: {result['metadata']}")
```

### Gestión de Embeddings

```python
# Obtener por clave
item = await embeddings_manager.get_by_key("conversation_123")

# Eliminar
deleted = await embeddings_manager.delete_by_key("conversation_123")

# Estadísticas
stats = await embeddings_manager.get_stats()
print(f"Embeddings en memoria: {stats['store_size']}")
print(f"Embeddings en GCS: {stats['gcs_embeddings_count']}")
print(f"Búsquedas realizadas: {stats['stats']['similarity_searches']}")
```

## Flujo de Búsqueda

1. **Query** → Generar embedding del texto de búsqueda
2. **Vector Search** → Buscar en índice escalable (si disponible)
3. **Fallback Local** → Buscar en memoria si Vector Search falla
4. **GCS Sync** → Cargar embeddings desde GCS si necesario
5. **Resultados** → Retornar items ordenados por similitud

## Optimizaciones Implementadas

### 1. Caché Multinivel
- **L1**: Caché de texto a embedding (evita regenerar)
- **L2**: Embeddings en memoria (acceso rápido)
- **L3**: GCS para persistencia
- **L4**: Vector Search para escala

### 2. Procesamiento Eficiente
- Generación en lote para múltiples textos
- Paralelización de operaciones I/O
- Límites de caché inteligentes
- Limpieza automática de caché antiguo

### 3. Resiliencia
- Fallback automático entre niveles
- Reintentos con backoff exponencial
- Logging detallado de errores
- Métricas de rendimiento

## Casos de Uso en NGX Agents

### 1. Contexto de Conversación
```python
# Almacenar cada intercambio
await embeddings_manager.store_embedding(
    key=f"conv_{session_id}_{timestamp}",
    text=f"{user_message} {agent_response}",
    metadata={
        "session_id": session_id,
        "user_id": user_id,
        "agent": agent_name
    }
)

# Buscar contexto relevante
context = await embeddings_manager.find_similar(
    query=current_message,
    top_k=10
)
```

### 2. Base de Conocimiento
```python
# Indexar documentos
for doc in training_documents:
    await embeddings_manager.store_embedding(
        key=f"kb_{doc.id}",
        text=doc.content,
        metadata={
            "category": doc.category,
            "tags": doc.tags
        }
    )

# Buscar información relevante
relevant_docs = await embeddings_manager.find_similar(
    query="técnicas de recuperación muscular",
    top_k=5,
    threshold=0.8
)
```

### 3. Personalización de Usuario
```python
# Almacenar preferencias
await embeddings_manager.store_embedding(
    key=f"user_pref_{user_id}",
    text=" ".join(user_preferences),
    metadata={"user_id": user_id}
)

# Encontrar usuarios similares
similar_users = await embeddings_manager.find_similar(
    query=current_user_profile,
    top_k=20
)
```

## Configuración y Deployment

### Variables de Entorno

```env
# Google Cloud
GOOGLE_APPLICATION_CREDENTIALS=/path/to/credentials.json
GCP_PROJECT_ID=agentes-ngx
VERTEX_LOCATION=us-central1

# GCS
GCS_BUCKET_NAME=agents_ngx
GCS_BUCKET_LOCATION=us

# Vector Search
VERTEX_AI_INDEX_ID=5755708075919015936
VERTEX_AI_INDEX_ENDPOINT_ID=9027115808366526464

# Caché
USE_REDIS_CACHE=true
REDIS_HOST=localhost
REDIS_PORT=6379
```

### Inicialización

```python
# En app/main.py o donde se inicialice
from core.embeddings_manager import embeddings_manager

# El manager se auto-inicializa cuando se usa
# Opcionalmente, pre-cargar embeddings
await embeddings_manager._load_embeddings_from_gcs(limit=1000)
```

### Scripts de Utilidad

```bash
# Probar el sistema completo
python scripts/test_embeddings_integration.py

# Migrar embeddings existentes
python scripts/migrate_embeddings_to_gcs.py

# Reindexar en Vector Search
python scripts/reindex_vector_search.py
```

## Monitoreo y Métricas

### Métricas Disponibles

1. **Rendimiento**:
   - Tiempo de generación de embeddings
   - Latencia de búsqueda
   - Hit rate del caché

2. **Uso**:
   - Total de embeddings almacenados
   - Búsquedas por minuto
   - Tamaño del caché

3. **Errores**:
   - Fallos de generación
   - Timeouts de Vector Search
   - Errores de GCS

### Dashboard Recomendado

```python
# Obtener métricas
stats = await embeddings_manager.get_stats()

# Métricas clave
print(f"Cache hit rate: {stats['stats']['cache_hits'] / stats['stats']['embedding_requests']:.2%}")
print(f"Búsquedas/hora: {stats['stats']['similarity_searches'] * 60}")
print(f"Errores: {stats['stats']['errors']}")
```

## Mejores Prácticas

### 1. Claves Únicas
- Usar UUIDs o hashes para evitar colisiones
- Incluir tipo de contenido en la clave
- Ejemplo: `conv_{uuid}`, `kb_doc_{id}`, `user_pref_{user_id}`

### 2. Metadata Rica
- Incluir toda información relevante para filtrado
- Timestamps para ordenamiento temporal
- Categorías para agrupación

### 3. Limpieza Regular
- Eliminar embeddings antiguos no usados
- Implementar TTL para contenido temporal
- Monitorear crecimiento del storage

### 4. Búsquedas Eficientes
- Usar threshold apropiado (0.7-0.8 típicamente)
- Limitar top_k según necesidad
- Pre-filtrar cuando sea posible

## Troubleshooting

### Problema: Embeddings no se generan
**Solución**: Verificar credenciales de Google Cloud y cuota de API

### Problema: Vector Search no retorna resultados
**Solución**: Verificar que el índice esté desplegado y el endpoint activo

### Problema: Alta latencia en búsquedas
**Solución**: Aumentar caché en memoria, optimizar threshold

### Problema: Costos elevados de GCS
**Solución**: Implementar lifecycle policies, comprimir embeddings

## Roadmap Futuro

1. **Compresión de Embeddings**: Reducir tamaño sin perder precisión
2. **Multi-tenancy**: Separación por organización
3. **Embeddings Multimodales**: Soporte para imágenes y audio
4. **Fine-tuning**: Modelos especializados por dominio
5. **Analytics Avanzado**: Clustering y visualización de embeddings

---

Esta documentación cubre la implementación completa del sistema de embeddings en NGX Agents. Para preguntas específicas o casos de uso adicionales, consultar el código fuente o contactar al equipo de desarrollo.