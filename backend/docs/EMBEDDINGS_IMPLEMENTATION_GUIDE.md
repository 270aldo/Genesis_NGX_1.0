# 🧠 Guía de Implementación del Sistema de Embeddings

## 📋 Resumen del Sistema

El sistema de embeddings de GENESIS NGX utiliza tecnología de Google Vertex AI para convertir texto en representaciones vectoriales de alta dimensión, permitiendo búsquedas semánticas avanzadas y recuperación de contexto inteligente.

### Características Principales:
- **Modelo**: `text-embedding-large-exp-03-07` (3072 dimensiones)
- **Almacenamiento Híbrido**: Memoria + GCS + Vector Search
- **Caché Multinivel**: L1 (texto→embedding), L2 (memoria), L3 (GCS), L4 (Vector Search)
- **Búsqueda Semántica**: Similitud coseno con threshold configurable

## 🏗️ Arquitectura

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
└─────────────────────────────────────────────────────────────┘
```

## 🚀 Uso del Sistema

### 1. Generar Embeddings

```python
from core.embeddings_manager import embeddings_manager

# Individual
embedding = await embeddings_manager.generate_embedding("Texto a convertir")

# En lote (más eficiente)
embeddings = await embeddings_manager.batch_generate_embeddings([
    "Texto 1",
    "Texto 2",
    "Texto 3"
])
```

### 2. Almacenar con Metadata

```python
# Almacenar contexto de conversación
success = await embeddings_manager.store_embedding(
    key="conversation_123",
    text="¿Cuál es el mejor ejercicio para ganar músculo?",
    metadata={
        "user_id": "user_456",
        "agent": "training_strategist",
        "timestamp": "2025-07-19T20:00:00Z"
    }
)
```

### 3. Buscar por Similitud

```python
# Buscar contexto relevante
results = await embeddings_manager.find_similar(
    query="ejercicios para brazos",
    top_k=5,
    threshold=0.7
)

for result in results:
    print(f"Texto: {result['text']}")
    print(f"Similitud: {result['similarity']:.3f}")
    print(f"Metadata: {result['metadata']}")
```

## 💡 Casos de Uso en GENESIS

### 1. Contexto de Conversación
Cada intercambio usuario-agente se almacena como embedding para mantener contexto a largo plazo:

```python
# En el orchestrator
await embeddings_manager.store_embedding(
    key=f"conv_{session_id}_{timestamp}",
    text=f"{user_message} {agent_response}",
    metadata={
        "session_id": session_id,
        "user_id": user_id,
        "agent": agent_name,
        "intent": primary_intent
    }
)
```

### 2. Base de Conocimiento
Los documentos de entrenamiento y nutrición se indexan para búsqueda rápida:

```python
# Indexar documentos
for doc in training_documents:
    await embeddings_manager.store_embedding(
        key=f"kb_{doc.id}",
        text=doc.content,
        metadata={
            "category": doc.category,
            "tags": doc.tags,
            "source": "knowledge_base"
        }
    )
```

### 3. Personalización de Usuario
Las preferencias y objetivos del usuario se convierten en embeddings para encontrar patrones similares:

```python
# Almacenar perfil de usuario
user_profile = f"""
Objetivos: {user.goals}
Nivel: {user.fitness_level}
Preferencias: {user.preferences}
"""

await embeddings_manager.store_embedding(
    key=f"user_profile_{user_id}",
    text=user_profile,
    metadata={"user_id": user_id, "type": "profile"}
)
```

## ⚙️ Configuración

### Variables de Entorno

```env
# Google Cloud
GOOGLE_APPLICATION_CREDENTIALS=/path/to/credentials.json
GCP_PROJECT_ID=agentes-ngx
VERTEX_LOCATION=us-central1

# GCS
GCS_BUCKET_NAME=agents_ngx

# Vector Search (IDs del índice y endpoint)
VERTEX_AI_INDEX_ID=5755708075919015936
VERTEX_AI_INDEX_ENDPOINT_ID=9027115808366526464

# Caché
USE_REDIS_CACHE=true
REDIS_URL=redis://localhost:6379
```

### Verificación de Configuración

```bash
# Verificar que Vector Search esté configurado
python scripts/verify_vector_search.py

# Probar el sistema de embeddings
python scripts/test_embeddings_integration.py
```

## 🔍 Flujo de Búsqueda

1. **Query** → Se genera embedding del texto de búsqueda
2. **Vector Search** → Búsqueda en índice escalable (si está configurado)
3. **Fallback Local** → Búsqueda en memoria si Vector Search falla
4. **GCS Sync** → Carga embeddings desde GCS si es necesario
5. **Resultados** → Retorna items ordenados por similitud

## 📊 Monitoreo y Métricas

```python
# Obtener estadísticas del sistema
stats = await embeddings_manager.get_stats()

print(f"Embeddings en memoria: {stats['store_size']}")
print(f"Embeddings en GCS: {stats['gcs_embeddings_count']}")
print(f"Búsquedas realizadas: {stats['stats']['similarity_searches']}")
print(f"Cache hit rate: {stats['stats']['cache_hits'] / stats['stats']['embedding_requests']:.2%}")
```

## 🚨 Consideraciones Importantes

### 1. Costos
- Cada embedding generation tiene un costo en Vertex AI
- Usar caché agresivamente para reducir costos
- Batch operations son más eficientes que individuales

### 2. Rendimiento
- Los embeddings son de 3072 dimensiones (12KB por embedding)
- Limitar embeddings en memoria según recursos disponibles
- Vector Search es necesario para escalar a millones de embeddings

### 3. Seguridad
- No almacenar información sensible en embeddings
- Los embeddings pueden ser parcialmente reversibles
- Aplicar sanitización antes de generar embeddings

## 🛠️ Troubleshooting

### Problema: Vector Search no retorna resultados
**Solución**: 
1. Verificar que el índice tenga datos: `scripts/verify_vector_search.py`
2. Verificar que el endpoint esté desplegado
3. Revisar logs en GCP Console

### Problema: Alta latencia en búsquedas
**Solución**:
1. Aumentar caché en memoria
2. Ajustar threshold de similitud (más alto = menos resultados)
3. Usar Vector Search en lugar de búsqueda local

### Problema: Embeddings no se generan
**Solución**:
1. Verificar credenciales de Google Cloud
2. Verificar cuota de API en Vertex AI
3. Revisar logs: `grep "embedding" logs/app.log`

## 📚 Referencias

- [Vertex AI Embeddings](https://cloud.google.com/vertex-ai/docs/generative-ai/embeddings/get-text-embeddings)
- [Vector Search](https://cloud.google.com/vertex-ai/docs/vector-search/overview)
- [Similitud Coseno](https://en.wikipedia.org/wiki/Cosine_similarity)

---

**Última actualización**: 2025-07-19