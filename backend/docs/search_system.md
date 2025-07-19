# 🔍 Sistema de Búsqueda - NGX Agents

## Descripción General

El sistema de búsqueda de NGX Agents implementa una solución dual que combina búsqueda semántica (Vector Search) con búsqueda de texto completo (PostgreSQL). Esto permite a los usuarios y agentes encontrar información relevante tanto por significado como por coincidencia exacta de términos.

## Arquitectura del Sistema

```
┌─────────────────────────────────────────────────────────────┐
│                    Cliente/Usuario                           │
├─────────────────────────────────────────────────────────────┤
│                   API de Búsqueda                            │
│                  /search/* endpoints                         │
├─────────────────────────────────────────────────────────────┤
│                   SearchManager                              │
│  ┌──────────────┬──────────────┬─────────────────────────┐ │
│  │   Búsqueda   │   Búsqueda   │      Sugerencias        │ │
│  │   Semántica  │  Texto Full  │    y Autocompletado     │ │
│  └──────┬───────┴───────┬──────┴──────────┬──────────────┘ │
├─────────┼───────────────┼──────────────────┼────────────────┤
│         ▼               ▼                  ▼                 │
│  ┌─────────────┐ ┌─────────────┐ ┌────────────────┐        │
│  │   Vector     │ │ PostgreSQL  │ │    Fuzzy       │        │
│  │   Search     │ │ Full-Text   │ │   Matching     │        │
│  │ (Embeddings) │ │   Search    │ │  (Trigrams)    │        │
│  └─────────────┘ └─────────────┘ └────────────────┘        │
│                         │                                     │
│                         ▼                                     │
│              ┌─────────────────────┐                        │
│              │  Supabase Database  │                        │
│              │  - Conversations    │                        │
│              │  - Training Plans   │                        │
│              │  - Nutrition Logs   │                        │
│              │  - Progress Metrics │                        │
│              │  - User Notes       │                        │
│              └─────────────────────┘                        │
└─────────────────────────────────────────────────────────────┘
```

## Tipos de Búsqueda

### 1. Búsqueda Semántica (Vector Search)
Encuentra contenido con significado similar usando embeddings.

**Casos de uso:**
- "Ejercicios para ganar fuerza" → Encuentra planes con sentadillas, peso muerto, etc.
- "Comidas altas en proteína" → Encuentra registros con pollo, huevos, etc.
- "Dolor muscular post-entreno" → Encuentra conversaciones sobre recuperación

### 2. Búsqueda de Texto Completo (PostgreSQL)
Encuentra coincidencias exactas o parciales de términos.

**Casos de uso:**
- Buscar una conversación específica por palabras exactas
- Encontrar planes que mencionen "press de banca"
- Localizar notas con términos técnicos específicos

### 3. Búsqueda Híbrida
Combina ambos métodos para máxima precisión.

## Componentes del Sistema

### SearchManager (`core/search_manager.py`)

Gestor principal que coordina todos los tipos de búsqueda.

**Características:**
- Búsqueda unificada en múltiples tipos de contenido
- Sanitización automática de queries
- Paginación eficiente
- Estadísticas de uso
- Caché de resultados frecuentes

### Tipos de Contenido Indexados

#### 1. Conversaciones (`conversations`)
```python
{
    "table": "conversations",
    "search_columns": ["user_message", "agent_response"],
    "return_columns": ["id", "user_message", "agent_response", "agent_name", "created_at"]
}
```

#### 2. Planes de Entrenamiento (`training_plans`)
```python
{
    "table": "training_plans",
    "search_columns": ["name", "description", "exercises"],
    "return_columns": ["id", "name", "description", "difficulty", "duration_weeks"]
}
```

#### 3. Registros de Nutrición (`nutrition_logs`)
```python
{
    "table": "nutrition_logs",
    "search_columns": ["meal_name", "foods", "notes"],
    "return_columns": ["id", "meal_name", "calories", "protein", "carbs", "fats"]
}
```

#### 4. Métricas de Progreso (`progress_metrics`)
```python
{
    "table": "progress_metrics",
    "search_columns": ["metric_name", "notes"],
    "return_columns": ["id", "metric_name", "value", "unit", "category"]
}
```

#### 5. Notas del Usuario (`user_notes`)
```python
{
    "table": "user_notes",
    "search_columns": ["title", "content", "tags"],
    "return_columns": ["id", "title", "content", "category", "tags"]
}
```

## API REST

### Endpoints Disponibles

#### 1. Búsqueda Principal
```http
POST /search/
Content-Type: application/json
Authorization: Bearer {token}

{
    "query": "proteína post entreno",
    "search_type": "all",  // o específico: conversations, training_plans, etc.
    "limit": 20,
    "offset": 0,
    "filters": {
        "category": "nutrition"
    }
}
```

**Respuesta:**
```json
{
    "query": "proteína post entreno",
    "search_type": "all",
    "results": [
        {
            "type": "nutrition_logs",
            "results": [
                {
                    "id": "uuid",
                    "meal_name": "Batido post-entreno",
                    "protein": 30,
                    "calories": 250
                }
            ]
        },
        {
            "type": "conversations",
            "results": [...]
        }
    ],
    "total_results": 15,
    "limit": 20,
    "offset": 0,
    "timestamp": "2025-05-31T20:00:00Z"
}
```

#### 2. Búsqueda Rápida
```http
GET /search/quick?q=sentadilla&type=training_plans&limit=10
Authorization: Bearer {token}
```

#### 3. Sugerencias de Autocompletado
```http
POST /search/suggestions
Content-Type: application/json
Authorization: Bearer {token}

{
    "partial_query": "prot",
    "search_type": "all",
    "limit": 5
}
```

**Respuesta:**
```json
{
    "partial_query": "prot",
    "suggestions": ["proteína", "proteínas", "protein", "protocolo", "protección"],
    "search_type": "all"
}
```

#### 4. Tipos de Búsqueda Disponibles
```http
GET /search/types
```

**Respuesta:**
```json
["all", "conversations", "training_plans", "nutrition_logs", "progress_metrics", "user_notes"]
```

#### 5. Estadísticas (Admin)
```http
GET /search/stats
Authorization: Bearer {admin_token}
```

## Índices de Base de Datos

### Índices de Texto Completo
```sql
-- Conversaciones
CREATE INDEX idx_conversations_search 
ON conversations 
USING gin(to_tsvector('spanish', user_message || ' ' || agent_response));

-- Planes de entrenamiento
CREATE INDEX idx_training_plans_search 
ON training_plans 
USING gin(to_tsvector('spanish', name || ' ' || description || ' ' || exercises));

-- Registros de nutrición
CREATE INDEX idx_nutrition_logs_search 
ON nutrition_logs 
USING gin(to_tsvector('spanish', meal_name || ' ' || foods || ' ' || notes));
```

### Índices Trigram (Búsqueda Fuzzy)
```sql
CREATE EXTENSION pg_trgm;

CREATE INDEX idx_conversations_trigram 
ON conversations 
USING gin(user_message gin_trgm_ops, agent_response gin_trgm_ops);

CREATE INDEX idx_training_plans_trigram 
ON training_plans 
USING gin(name gin_trgm_ops, description gin_trgm_ops);
```

## Uso en Código

### Búsqueda Simple
```python
from core.search_manager import search_manager

# Buscar en todos los tipos
results = await search_manager.search(
    query="ejercicios para espalda",
    search_type="all",
    user_id=current_user_id,
    limit=20
)

# Buscar solo en planes de entrenamiento
training_results = await search_manager.search(
    query="hipertrofia",
    search_type="training_plans",
    user_id=current_user_id,
    limit=10
)
```

### Búsqueda con Filtros
```python
# Buscar métricas de peso en los últimos 30 días
from datetime import datetime, timedelta

results = await search_manager.search(
    query="peso",
    search_type="progress_metrics",
    user_id=current_user_id,
    filters={
        "category": "weight",
        "recorded_at__gte": (datetime.now() - timedelta(days=30)).isoformat()
    }
)
```

### Integración con Agentes
```python
# En un agente
class NutritionArchitect(BaseAgent):
    async def find_similar_meals(self, meal_description: str):
        # Buscar comidas similares en el historial
        results = await search_manager.search(
            query=meal_description,
            search_type="nutrition_logs",
            user_id=self.user_id,
            limit=5
        )
        
        # Usar embeddings para búsqueda más precisa
        embedding_results = await embeddings_manager.find_similar(
            query=meal_description,
            top_k=5
        )
        
        return self._combine_results(results, embedding_results)
```

## Optimizaciones Implementadas

### 1. Búsqueda Paralela
Cuando se busca en "all", las búsquedas en diferentes tablas se ejecutan en paralelo:
```python
tasks = []
for search_type in self.search_configs.keys():
    task = self._search_single_type(query, search_type, ...)
    tasks.append(task)

results = await asyncio.gather(*tasks)
```

### 2. Límites Inteligentes
Al buscar en todos los tipos, se limitan los resultados por tipo:
```python
limit_per_type = max(5, limit // len(self.search_configs))
```

### 3. Sanitización de Queries
Se escapan caracteres especiales para prevenir inyección:
```python
special_chars = ["'", '"', "\\", "%", "_", "[", "]", "^", "$"]
for char in special_chars:
    sanitized = sanitized.replace(char, f"\\{char}")
```

## Casos de Uso Avanzados

### 1. Búsqueda Contextual en Conversaciones
```python
# Buscar conversaciones previas sobre un tema
async def get_conversation_context(topic: str, session_id: str):
    # Búsqueda semántica
    semantic_results = await embeddings_manager.find_similar(
        query=topic,
        top_k=10
    )
    
    # Búsqueda de texto
    text_results = await search_manager.search(
        query=topic,
        search_type="conversations",
        filters={"session_id": session_id}
    )
    
    return merge_and_rank_results(semantic_results, text_results)
```

### 2. Análisis de Tendencias
```python
# Buscar patrones en métricas
async def analyze_progress_trends(user_id: str, metric: str):
    results = await search_manager.search(
        query=metric,
        search_type="progress_metrics",
        user_id=user_id,
        limit=100,
        filters={"recorded_at__gte": "2025-01-01"}
    )
    
    # Procesar para tendencias
    return calculate_trends(results["results"])
```

### 3. Recomendaciones Personalizadas
```python
# Encontrar usuarios con objetivos similares
async def find_similar_users(current_user_goals: str):
    # Buscar en notas y planes
    similar_notes = await search_manager.search(
        query=current_user_goals,
        search_type="user_notes",
        limit=50
    )
    
    # Extraer user_ids únicos
    similar_users = extract_unique_users(similar_notes)
    
    # Obtener sus planes exitosos
    successful_plans = await get_successful_plans(similar_users)
    
    return successful_plans
```

## Configuración y Tuning

### Variables de Entorno
```env
# Base de datos
SUPABASE_URL=https://proyecto.supabase.co
SUPABASE_ANON_KEY=tu-clave

# Búsqueda
SEARCH_DEFAULT_LIMIT=20
SEARCH_MAX_LIMIT=100
SEARCH_LANGUAGE=spanish  # o english

# Performance
SEARCH_CACHE_TTL=300  # 5 minutos
SEARCH_PARALLEL_QUERIES=true
```

### Optimización de Índices
```sql
-- Actualizar estadísticas
ANALYZE conversations;
ANALYZE training_plans;
ANALYZE nutrition_logs;

-- Verificar uso de índices
EXPLAIN (ANALYZE, BUFFERS) 
SELECT * FROM conversations 
WHERE to_tsvector('spanish', user_message) @@ plainto_tsquery('spanish', 'proteína');
```

## Monitoreo y Métricas

### Métricas Clave
1. **Latencia de búsqueda** por tipo
2. **Queries por segundo**
3. **Hit rate de caché**
4. **Términos más buscados**
5. **Tipos de búsqueda más usados**

### Dashboard de Ejemplo
```python
stats = await search_manager.get_stats()

print(f"Total búsquedas: {stats['stats']['searches_performed']}")
print(f"Resultados promedio: {stats['stats']['results_returned'] / stats['stats']['searches_performed']}")
print(f"Tipo más buscado: {max(stats['stats']['search_types'], key=stats['stats']['search_types'].get)}")
```

## Mejores Prácticas

### 1. Queries Efectivas
- Usar términos específicos cuando sea posible
- Combinar búsqueda semántica y texto para mejor precisión
- Aplicar filtros para reducir el conjunto de resultados

### 2. Indexación Eficiente
- Actualizar índices regularmente con `REINDEX`
- Monitorear el tamaño de índices
- Usar particionamiento para tablas grandes

### 3. Performance
- Implementar paginación para resultados grandes
- Cachear búsquedas frecuentes
- Usar búsqueda asíncrona cuando sea posible

### 4. Seguridad
- Siempre filtrar por user_id
- Sanitizar todas las queries
- Implementar rate limiting

## Troubleshooting

### Problema: Búsquedas lentas
**Solución**: 
- Verificar índices con `EXPLAIN ANALYZE`
- Aumentar work_mem en PostgreSQL
- Reducir limit o implementar paginación

### Problema: Resultados irrelevantes
**Solución**:
- Ajustar configuración de idioma
- Usar búsqueda semántica además de texto
- Mejorar términos de búsqueda

### Problema: Sin resultados
**Solución**:
- Verificar que los datos estén indexados
- Probar con términos más generales
- Verificar permisos RLS en Supabase

## Roadmap Futuro

1. **Búsqueda por voz**: Integrar con sistema de audio
2. **Búsqueda visual**: Buscar por imágenes similares
3. **Facetas dinámicas**: Filtros automáticos basados en resultados
4. **Búsqueda predictiva**: Sugerir búsquedas antes de escribir
5. **Análisis de búsquedas**: Dashboard de términos y tendencias

---

Esta documentación cubre el sistema completo de búsqueda en NGX Agents. Para casos de uso específicos o problemas no cubiertos, consultar el código fuente o contactar al equipo de desarrollo.