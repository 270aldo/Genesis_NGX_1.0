# Guía de Implementación RAG para NGX Agents

## 📋 Resumen

Esta guía detalla la implementación de Retrieval-Augmented Generation (RAG) en NGX Agents usando:
- **Vertex AI Search** para búsqueda semántica y almacenamiento de vectores
- **text-embedding-large-exp-03-07** para embeddings de 3072 dimensiones
- **Gemini 2.0 Flash** para generación de respuestas

## 🏗️ Arquitectura RAG

```
┌─────────────────────────────────────────────────────────────┐
│                        Usuario                               │
└─────────────────────────────────────┬───────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────┐
│                    NGX Agent (con RAG)                       │
├─────────────────────────────────────────────────────────────┤
│  1. Procesar Query → 2. Generar Embeddings → 3. Búsqueda    │
│  4. Recuperar Docs → 5. Generar Respuesta → 6. Retornar     │
└─────────────────────────────────────┬───────────────────────┘
                                      │
                ┌─────────────────────┴─────────────────────┐
                ▼                                           ▼
┌───────────────────────────────┐   ┌───────────────────────────────┐
│    Vertex AI Search           │   │    Vertex AI Models           │
│  - Document Store             │   │  - Embeddings (3072D)         │
│  - Semantic Search            │   │  - Gemini 2.0 Flash           │
│  - Ranking & Filtering        │   │  - Context Generation         │
└───────────────────────────────┘   └───────────────────────────────┘
```

## 🚀 Configuración Paso a Paso

### 1. Configuración de Google Cloud

```bash
# Ejecutar el script de configuración
cd /Users/aldoolivas/Desktop/ngx-agents
chmod +x scripts/setup_gcp_rag.sh
./scripts/setup_gcp_rag.sh
```

### 2. Configurar Vertex AI Search

1. Ve a [Google Cloud Console - Vertex AI Search](https://console.cloud.google.com/gen-app-builder)

2. Crea una nueva aplicación:
   - Tipo: **Search**
   - Nombre: `ngx-fitness-search`
   - Región: `global`

3. Crea un Data Store:
   - Nombre: `ngx-fitness-datastore`
   - Tipo: **Unstructured documents**
   - Fuente: Cloud Storage
   - Bucket: `{PROJECT_ID}-knowledge-base`

4. Configura el esquema:
   ```json
   {
     "fields": [
       {"name": "content", "type": "string", "searchable": true},
       {"name": "title", "type": "string", "searchable": true},
       {"name": "domain", "type": "string", "facetable": true},
       {"name": "category", "type": "string", "facetable": true},
       {"name": "tags", "type": "string", "repeatable": true, "facetable": true},
       {"name": "created_at", "type": "datetime"},
       {"name": "embedding", "type": "float", "repeatable": true, "dimension": 3072}
     ]
   }
   ```

### 3. Variables de Entorno

Añadir a tu archivo `.env`:

```env
# RAG Configuration
RAG_ENABLED=true
VERTEX_SEARCH_APP_ID=ngx-fitness-search
VERTEX_SEARCH_DATASTORE_ID=ngx-fitness-datastore
EMBEDDING_MODEL=text-embedding-large-exp-03-07
GENERATION_MODEL=gemini-2.0-flash-exp
VECTOR_DIMENSIONS=3072

# RAG Parameters
CHUNK_SIZE=512
CHUNK_OVERLAP=50
MAX_SEARCH_RESULTS=5
SIMILARITY_THRESHOLD=0.7
TEMPERATURE=0.3
MAX_OUTPUT_TOKENS=8192
```

### 4. Estructura de Conocimiento

Organizar documentos en Cloud Storage:

```
gs://{PROJECT_ID}-knowledge-base/
├── fitness/
│   ├── exercises/
│   ├── programs/
│   └── techniques/
├── nutrition/
│   ├── diets/
│   ├── supplements/
│   └── recipes/
├── wellness/
│   ├── recovery/
│   ├── biohacking/
│   └── mental_health/
└── user_data/
    └── {user_id}/
```

## 💻 Uso del Pipeline RAG

### Uso Básico

```python
from rag.pipeline import RAGPipeline

# Inicializar pipeline
pipeline = RAGPipeline()

# Procesar consulta
result = await pipeline.process_query(
    query="¿Cómo puedo mejorar mi fuerza en sentadillas?",
    domain="fitness",
    user_context={
        "fitness_level": "intermediate",
        "goals": ["strength", "powerlifting"]
    }
)

print(result['response'])
```

### Integración con Agentes

```python
from agents.base.rag_agent import RAGAgent

class EliteTrainingStrategistRAG(RAGAgent):
    def __init__(self):
        super().__init__(
            agent_id="elite_training_rag",
            name="Elite Training Strategist con RAG",
            description="Diseña programas de entrenamiento con knowledge base",
            capabilities=["program_design", "exercise_selection", "periodization"],
            domain="fitness",
            enable_rag=True,
            rag_config={
                "max_results": 7,
                "threshold": 0.75
            }
        )
    
    async def _process_without_rag(self, task_input: str, context: Dict[str, Any]):
        # Fallback sin RAG
        return "Procesamiento sin RAG no disponible"
```

### Búsqueda Personalizada

```python
# Búsqueda con filtros específicos
results = await pipeline.search_client.search(
    query="rutina de fuerza",
    filters={
        "domain": "fitness",
        "category": "strength",
        "tags": ["powerlifting", "intermediate"]
    },
    boost_specs=[
        {"condition": 'equipment:"barbell"', "boost": 1.5},
        {"condition": 'duration:"60min"', "boost": 1.3}
    ]
)
```

### Streaming de Respuestas

```python
# Generar respuesta en streaming
result = await pipeline.process_query(
    query="Explica una rutina completa de push/pull/legs",
    stream=True
)

# Consumir el stream
async for chunk in result['response_generator']:
    print(chunk, end='', flush=True)
```

## 📊 Indexación de Documentos

### Script de Indexación

```python
import asyncio
from rag.pipeline import RAGPipeline

async def index_fitness_document():
    pipeline = RAGPipeline()
    
    document_content = """
    Rutina de Fuerza 5x5
    
    Esta rutina se enfoca en movimientos compuestos básicos:
    - Sentadilla: 5 series de 5 repeticiones
    - Press de banca: 5x5
    - Peso muerto: 1x5
    - Press militar: 5x5
    - Remo con barra: 5x5
    
    Frecuencia: 3 días por semana (Lunes, Miércoles, Viernes)
    Progresión: Añadir 2.5kg cada sesión
    """
    
    metadata = {
        "title": "Rutina StrongLifts 5x5",
        "domain": "fitness",
        "category": "strength",
        "tags": ["beginner", "strength", "barbell", "5x5"],
        "equipment": ["barbell", "rack", "bench"],
        "duration": "45-60min",
        "frequency": "3x/week"
    }
    
    result = await pipeline.index_document(
        content=document_content,
        metadata=metadata,
        document_id="routine_5x5_001"
    )
    
    print(f"Documento indexado: {result}")
```

## 🔍 Monitoreo y Optimización

### Métricas Clave

1. **Calidad de Búsqueda**
   - Relevancia de resultados (>0.85)
   - Tiempo de búsqueda (<500ms)
   - Hit rate del caché (>60%)

2. **Calidad de Generación**
   - Coherencia con contexto
   - Precisión factual
   - Satisfacción del usuario

3. **Performance**
   - Latencia end-to-end (<2s)
   - Tokens por segundo (>50)
   - Costo por consulta

### Dashboard de Monitoreo

```python
from rag.monitoring import RAGMonitor

monitor = RAGMonitor()

# Ver estadísticas
stats = await monitor.get_stats()
print(f"Consultas totales: {stats['total_queries']}")
print(f"Latencia promedio: {stats['avg_latency_ms']}ms")
print(f"Documentos promedio por consulta: {stats['avg_docs_retrieved']}")
```

## 🛠️ Troubleshooting

### Problemas Comunes

1. **Error: "Model not found"**
   - Verificar que el modelo experimental esté disponible en tu región
   - Contactar soporte de Google Cloud para acceso

2. **Embeddings de dimensión incorrecta**
   - Asegurar que VECTOR_DIMENSIONS=3072 en todas las configuraciones
   - Limpiar caché si cambias de modelo

3. **Búsquedas sin resultados**
   - Verificar que los documentos estén indexados correctamente
   - Revisar filtros y umbrales de similitud

4. **Latencia alta**
   - Habilitar caché de embeddings
   - Reducir max_search_results
   - Usar regiones más cercanas

## 📈 Mejores Prácticas

1. **Chunking de Documentos**
   - Mantener chunks entre 400-600 tokens
   - Preservar contexto con overlap de 50 tokens
   - Incluir metadata relevante

2. **Prompt Engineering**
   - Ser específico sobre el dominio
   - Incluir contexto del usuario
   - Pedir formato estructurado cuando sea necesario

3. **Caché y Optimización**
   - Cachear embeddings frecuentes
   - Pre-computar embeddings para documentos estáticos
   - Usar batch processing para indexación masiva

4. **Personalización**
   - Mantener perfiles de usuario actualizados
   - Ajustar boosts según feedback
   - A/B testing de configuraciones

## 🔗 Recursos Adicionales

- [Vertex AI Search Documentation](https://cloud.google.com/generative-ai-app-builder/docs/introduction)
- [Embeddings Model Guide](https://cloud.google.com/vertex-ai/docs/generative-ai/embeddings/get-text-embeddings)
- [Gemini 2.0 Flash Documentation](https://cloud.google.com/vertex-ai/generative-ai/docs/model-reference/gemini)
- [NGX Agents Architecture](./README.md)