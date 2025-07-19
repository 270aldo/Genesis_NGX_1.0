# 📡 API Endpoints v2 - NGX Agents

Documentación completa de todos los endpoints disponibles en NGX Agents, incluyendo los nuevos sistemas de búsqueda y embeddings.

## Base URL
```
Desarrollo: http://localhost:8000
Producción: https://api.ngxagents.com
```

## Autenticación
Todos los endpoints (excepto los marcados como públicos) requieren autenticación JWT:
```http
Authorization: Bearer {token}
```

## Índice de Endpoints

### 🔐 Autenticación (`/auth`)
- [Login](#login)
- [Register](#register)
- [Refresh Token](#refresh-token)
- [Logout](#logout)

### 🤖 Agentes (`/agents`)
- [List Agents](#list-agents)
- [Get Agent Details](#get-agent-details)
- [Run Agent](#run-agent)

### 💬 Chat (`/chat`)
- [Send Message](#send-message)
- [Stream Chat](#stream-chat)
- [Get History](#get-history)

### 🔍 Búsqueda (`/search`) **NUEVO**
- [Search](#search)
- [Quick Search](#quick-search)
- [Get Suggestions](#get-suggestions)
- [Search Types](#search-types)
- [Search Stats](#search-stats)

### 📊 Visualización (`/visualization`)
- [Generate Progress Chart](#generate-progress-chart)
- [Generate Nutrition Infographic](#generate-nutrition-infographic)
- [Generate PDF Report](#generate-pdf-report)
- [Get Exercise Videos](#get-exercise-videos)

### 🎤 Audio (`/audio`)
- [Transcribe Audio](#transcribe-audio)
- [Synthesize Speech](#synthesize-speech)
- [Analyze Voice Emotion](#analyze-voice-emotion)

### ⌚ Wearables (`/wearables`)
- [Sync Wearable Data](#sync-wearable-data)
- [Get Wearable Status](#get-wearable-status)
- [List Connected Devices](#list-connected-devices)

### 📱 Notificaciones (`/notifications`)
- [Send Push Notification](#send-push-notification)
- [Schedule Notification](#schedule-notification)
- [Get Notification History](#get-notification-history)

### 📈 Métricas (`/metrics`)
- [Get System Metrics](#get-system-metrics)
- [Get Agent Metrics](#get-agent-metrics)

### 💭 Feedback (`/feedback`)
- [Submit Feedback](#submit-feedback)
- [Get Feedback Stats](#get-feedback-stats)

---

## 🔐 Autenticación

### Login
```http
POST /auth/login
Content-Type: application/json

{
    "email": "user@example.com",
    "password": "securepassword"
}
```

**Respuesta exitosa (200):**
```json
{
    "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
    "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
    "token_type": "bearer",
    "expires_in": 3600,
    "user": {
        "id": "550e8400-e29b-41d4-a716-446655440000",
        "email": "user@example.com",
        "name": "John Doe",
        "role": "user"
    }
}
```

### Register
```http
POST /auth/register
Content-Type: application/json

{
    "email": "newuser@example.com",
    "password": "securepassword",
    "name": "Jane Doe",
    "age": 28,
    "goals": ["weight_loss", "muscle_gain"]
}
```

### Refresh Token
```http
POST /auth/refresh
Content-Type: application/json

{
    "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

### Logout
```http
POST /auth/logout
Authorization: Bearer {token}
```

---

## 🤖 Agentes

### List Agents
```http
GET /agents/
Authorization: Bearer {token}
```

**Respuesta (200):**
```json
{
    "agents": [
        {
            "id": "elite_training_strategist",
            "name": "Elite Training Strategist",
            "description": "Diseña programas de entrenamiento personalizados",
            "available": true,
            "skills": ["training_plan", "exercise_selection", "periodization"]
        },
        {
            "id": "precision_nutrition_architect",
            "name": "Precision Nutrition Architect",
            "description": "Crea planes nutricionales adaptados",
            "available": true,
            "skills": ["meal_planning", "macro_calculation", "supplementation"]
        }
    ]
}
```

### Get Agent Details
```http
GET /agents/{agent_id}
Authorization: Bearer {token}
```

### Run Agent
```http
POST /agents/run
Authorization: Bearer {token}
Content-Type: application/json

{
    "agent_id": "elite_training_strategist",
    "input": "Necesito un plan de entrenamiento para ganar fuerza",
    "context": {
        "user_level": "intermediate",
        "available_days": 4
    }
}
```

---

## 💬 Chat

### Send Message
```http
POST /chat/message
Authorization: Bearer {token}
Content-Type: application/json

{
    "message": "¿Cuál es el mejor ejercicio para pectorales?",
    "session_id": "550e8400-e29b-41d4-a716-446655440001",
    "context": {}
}
```

### Stream Chat
```http
GET /stream/chat?message=Hola&session_id=123
Authorization: Bearer {token}
Accept: text/event-stream
```

**Respuesta (Server-Sent Events):**
```
data: {"agent": "orchestrator", "content": "Hola! Soy", "type": "partial"}
data: {"agent": "orchestrator", "content": " el orquestador de NGX Agents.", "type": "partial"}
data: {"agent": "orchestrator", "content": "", "type": "complete"}
```

---

## 🔍 Búsqueda (NUEVO)

### Search
```http
POST /search/
Authorization: Bearer {token}
Content-Type: application/json

{
    "query": "ejercicios para espalda",
    "search_type": "all",
    "limit": 20,
    "offset": 0,
    "filters": {
        "category": "training"
    }
}
```

**Respuesta (200):**
```json
{
    "query": "ejercicios para espalda",
    "search_type": "all",
    "results": [
        {
            "type": "training_plans",
            "results": [
                {
                    "id": "uuid-1",
                    "name": "Plan de Espalda y Core",
                    "description": "Programa especializado en desarrollo de espalda",
                    "difficulty": "intermediate",
                    "duration_weeks": 8
                }
            ]
        },
        {
            "type": "conversations",
            "results": [
                {
                    "id": "uuid-2",
                    "user_message": "¿Cuáles son los mejores ejercicios para espalda?",
                    "agent_response": "Los mejores ejercicios incluyen dominadas, remo con barra...",
                    "agent_name": "Elite Training Strategist",
                    "created_at": "2025-05-30T10:00:00Z"
                }
            ]
        }
    ],
    "total_results": 15,
    "limit": 20,
    "offset": 0,
    "timestamp": "2025-05-31T20:00:00Z"
}
```

### Quick Search
```http
GET /search/quick?q=proteína&type=nutrition_logs&limit=10
Authorization: Bearer {token}
```

### Get Suggestions
```http
POST /search/suggestions
Authorization: Bearer {token}
Content-Type: application/json

{
    "partial_query": "prot",
    "search_type": "all",
    "limit": 5
}
```

**Respuesta (200):**
```json
{
    "partial_query": "prot",
    "suggestions": ["proteína", "proteínas", "protein", "protocolo", "protección"],
    "search_type": "all"
}
```

### Search Types
```http
GET /search/types
```

**Respuesta (200):**
```json
["all", "conversations", "training_plans", "nutrition_logs", "progress_metrics", "user_notes"]
```

### Search Stats (Admin)
```http
GET /search/stats
Authorization: Bearer {admin_token}
```

**Respuesta (200):**
```json
{
    "stats": {
        "searches_performed": 1542,
        "results_returned": 15420,
        "errors": 3,
        "search_types": {
            "all": 800,
            "conversations": 400,
            "training_plans": 200,
            "nutrition_logs": 142
        }
    },
    "search_types_available": ["all", "conversations", "training_plans", "nutrition_logs", "progress_metrics", "user_notes"],
    "initialized": true,
    "timestamp": "2025-05-31T20:00:00Z"
}
```

---

## 📊 Visualización

### Generate Progress Chart
```http
POST /visualization/progress-chart
Authorization: Bearer {token}
Content-Type: application/json

{
    "chart_type": "weight_progress",
    "time_range": "last_3_months",
    "metrics": ["weight", "body_fat"]
}
```

**Respuesta (200):**
```json
{
    "chart_url": "https://storage.googleapis.com/ngx-charts/user123/weight_progress_2025.png",
    "chart_data": {
        "labels": ["2025-03-01", "2025-04-01", "2025-05-01"],
        "datasets": [
            {
                "label": "Peso (kg)",
                "data": [75.5, 74.2, 73.1]
            }
        ]
    }
}
```

### Generate PDF Report
```http
POST /visualization/pdf-report
Authorization: Bearer {token}
Content-Type: application/json

{
    "report_type": "monthly_progress",
    "month": "2025-05",
    "include_sections": ["summary", "training", "nutrition", "metrics"]
}
```

---

## 🎤 Audio

### Transcribe Audio
```http
POST /audio/transcribe
Authorization: Bearer {token}
Content-Type: multipart/form-data

file: (audio file)
language: es-ES (optional)
```

**Respuesta (200):**
```json
{
    "transcription": "Hoy hice 3 series de sentadillas con 100 kilos",
    "language": "es-ES",
    "confidence": 0.95,
    "duration": 5.2
}
```

### Synthesize Speech
```http
POST /audio/synthesize
Authorization: Bearer {token}
Content-Type: application/json

{
    "text": "Bienvenido a tu sesión de entrenamiento",
    "voice": "es-ES-Neural2-A",
    "speed": 1.0
}
```

---

## ⌚ Wearables

### Sync Wearable Data
```http
POST /wearables/sync
Authorization: Bearer {token}
Content-Type: application/json

{
    "device_type": "whoop",
    "sync_from": "2025-05-01T00:00:00Z"
}
```

### List Connected Devices
```http
GET /wearables/devices
Authorization: Bearer {token}
```

**Respuesta (200):**
```json
{
    "devices": [
        {
            "type": "whoop",
            "name": "WHOOP 4.0",
            "connected": true,
            "last_sync": "2025-05-31T19:00:00Z"
        },
        {
            "type": "apple_watch",
            "name": "Apple Watch Series 8",
            "connected": true,
            "last_sync": "2025-05-31T20:00:00Z"
        }
    ]
}
```

---

## 📱 Notificaciones

### Send Push Notification
```http
POST /notifications/push
Authorization: Bearer {token}
Content-Type: application/json

{
    "title": "Hora de entrenar! 💪",
    "body": "Tu sesión de piernas comienza en 30 minutos",
    "data": {
        "type": "workout_reminder",
        "workout_id": "123"
    }
}
```

### Schedule Notification
```http
POST /notifications/schedule
Authorization: Bearer {token}
Content-Type: application/json

{
    "title": "Recordatorio de hidratación",
    "body": "No olvides beber agua",
    "schedule_time": "2025-06-01T10:00:00Z",
    "repeat": "daily"
}
```

---

## 📈 Métricas

### Get System Metrics
```http
GET /metrics
Authorization: Bearer {admin_token}
```

**Respuesta (Prometheus format):**
```
# HELP ngx_agents_requests_total Total requests
# TYPE ngx_agents_requests_total counter
ngx_agents_requests_total{method="GET",endpoint="/chat/message"} 1234

# HELP ngx_agents_response_time_seconds Response time
# TYPE ngx_agents_response_time_seconds histogram
ngx_agents_response_time_seconds_bucket{le="0.1"} 100
```

---

## 💭 Feedback

### Submit Feedback
```http
POST /feedback/submit
Authorization: Bearer {token}
Content-Type: application/json

{
    "type": "thumbs_up",
    "session_id": "550e8400-e29b-41d4-a716-446655440001",
    "message_id": "msg_123",
    "comment": "Excelente respuesta!",
    "rating": 5
}
```

### Get Feedback Stats
```http
GET /feedback/stats?period=last_30_days
Authorization: Bearer {admin_token}
```

**Respuesta (200):**
```json
{
    "period": "last_30_days",
    "total_feedback": 523,
    "positive": 456,
    "negative": 67,
    "average_rating": 4.3,
    "nps_score": 72,
    "sentiment_distribution": {
        "very_positive": 0.45,
        "positive": 0.35,
        "neutral": 0.15,
        "negative": 0.05
    }
}
```

---

## 🔄 Códigos de Estado HTTP

| Código | Descripción |
|--------|-------------|
| 200 | OK - Solicitud exitosa |
| 201 | Created - Recurso creado exitosamente |
| 400 | Bad Request - Parámetros inválidos |
| 401 | Unauthorized - Token inválido o expirado |
| 403 | Forbidden - Sin permisos para este recurso |
| 404 | Not Found - Recurso no encontrado |
| 422 | Unprocessable Entity - Validación falló |
| 429 | Too Many Requests - Rate limit excedido |
| 500 | Internal Server Error - Error del servidor |

## 🔒 Rate Limiting

- **Autenticados**: 1000 requests/hora
- **No autenticados**: 100 requests/hora
- **Búsquedas**: 300 requests/hora
- **Streaming**: 50 conexiones concurrentes

## 🛡️ Seguridad

### Headers Requeridos
```http
X-Request-ID: uuid-v4
User-Agent: NGX-Agents-Client/1.0
```

### CORS
```http
Access-Control-Allow-Origin: https://app.ngxagents.com
Access-Control-Allow-Methods: GET, POST, PUT, DELETE, OPTIONS
Access-Control-Allow-Headers: Content-Type, Authorization
```

---

Esta documentación refleja el estado actual de la API de NGX Agents incluyendo todos los nuevos endpoints de búsqueda. Para más detalles sobre implementación o casos de uso específicos, consultar la documentación técnica individual de cada sistema.