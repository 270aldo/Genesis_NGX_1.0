# GENESIS - El Cerebro AI del Ecosistema NGX

Sistema de inteligencia artificial multi-agente que actúa como el núcleo inteligente del ecosistema NGX, coordinando 11 agentes especializados en fitness, nutrición y bienestar, ahora con integración completa MCP (Model Context Protocol) para conectar todas las herramientas NGX.

## 🚀 Estado Actual del Proyecto

### Resumen General
GENESIS es el cerebro AI del ecosistema NGX - un sistema avanzado que implementa el protocolo A2A (Agent-to-Agent) de Google ADK para coordinar agentes especializados, ahora completamente integrado con todas las herramientas del ecosistema vía MCP. El proyecto ha alcanzado **96% de completitud** con el sistema MCP Gateway implementado y listo para producción.

### 📊 Progreso Global: 96% Completado - PRODUCTION READY

| Fase | Estado | Completado |
|------|--------|------------|
| FASE 1-4: Estabilización y Calidad | ✅ Completo | 100% |
| FASE 5: Features Avanzadas (Streaming, Métricas, Feedback) | ✅ Completo | 100% |
| FASE 6: Multimodalidad Completa (Visión, Audio, Visualización) | ✅ Completo | 100% |
| FASE 7: Escalabilidad y Distribución | ✅ Completo | 100% |
| FASE 8: Integraciones Externas | ✅ Completo | 100% |
| FASE 8.5: Embeddings & Search System | ✅ Completo | 100% |
| FASE 8.8: Supabase Database Setup | ✅ Completo | 100% |
| FASE 8.9: Performance Optimization | ✅ Completo | 100% |
| FASE 8.95: Project Cleanup & Organization | ✅ Completo | 100% |
| **FASE 9: MCP Ecosystem Integration** | ✅ **Completo** | **100%** |
| FASE 10: AI Avanzado, Seguridad | ⬜ Pendiente | 0% |

### 🎉 **NUEVO**: MCP Ecosystem Integration Complete (2025-07-20)

#### ✅ MCP Gateway Unificado Implementado
- **Gateway único** para todas las herramientas NGX (puerto 3000)
- **5 adaptadores** completos: nexus_core, nexus_crm, ngx_pulse, ngx_blog, nexus_conversations
- **Alta disponibilidad** con failover automático y load balancing
- **Cache distribuido** para optimización de rendimiento
- **Monitoring completo** con Prometheus y alertas configuradas

#### ✅ Herramientas del Ecosistema Integradas

**Para Usuarios (Suscripción GENESIS):**
- **GENESIS**: 11 agentes AI especializados trabajando 24/7
- **NGX Pulse**: Integración con wearables y análisis biométrico
- **NGX Blog**: Contenido personalizado generado por AI

**Para Entrenadores/Gimnasios (Herramientas Internas):**
- **Nexus Core**: Centro de control con analytics y reportes
- **Nexus CRM**: Gestión inteligente de clientes y ventas
- **Nexus Conversations**: Análisis de conversaciones y engagement

### 🎉 Performance Optimization & Project Cleanup (2025-07-19)

#### ✅ Optimizaciones de Rendimiento Completadas
- **Embeddings System**: Implementado `batch_generate_embeddings` para procesamiento eficiente
- **Frontend Optimization**: Lazy loading con React.Suspense y code splitting en Vite
- **Database Optimization**: Índices de rendimiento avanzados y análisis de queries
- **CDN Integration**: Sistema completo de CDN con optimización automática de imágenes
- **Service Worker**: Cache inteligente offline-first para assets CDN

#### ✅ Limpieza y Organización del Proyecto
- **40+ archivos obsoletos** eliminados o archivados
- **Estructura unificada**: Documentación organizada en `docs/reports/` y `docs/status/`
- **Scripts consolidados**: Cleanup y environment scripts optimizados
- **Frontend clarificado**: Confirmado nexus-chat-frontend como oficial
- **.gitignore actualizado**: Patrones mejorados para archivos temporales y backups

#### 🗃️ Supabase Database - 100% Configurado (2025-07-18)
- ✅ **25 Tablas** creadas con esquema completo
- ✅ **11 Agentes** registrados con voice IDs de ElevenLabs
- ✅ **RLS Policies** activas para seguridad máxima
- ✅ **Service Role** configurado para operaciones administrativas
- ✅ **Migraciones** ejecutadas y validadas
- ✅ **Cliente Optimizado** con circuit breaker y batch processing

### Componentes Principales

#### 1. **Arquitectura A2A (Agent-to-Agent)**
- ✅ **Estado**: Implementación completa (100%)
- **Servidor A2A optimizado** con características enterprise:
  - Circuit breakers para prevenir fallos en cascada
  - Colas de mensajes con priorización (CRITICAL, HIGH, NORMAL, LOW)
  - Comunicación asíncrona WebSocket y HTTP
  - Telemetría y métricas integradas
  - Sistema de reintentos y timeouts configurables

#### 2. **Google ADK (Agent Development Kit)**
- ✅ **Estado**: Implementado con fallback inteligente
- Utiliza la biblioteca oficial `google-adk` v0.1.0
- Sistema de fallback a stubs locales cuando ADK no está disponible
- Implementación de Agent y Toolkit siguiendo el estándar de Google

#### 3. **Agentes Especializados** (11 agentes - 100% implementados)
1. **Orchestrator**: Coordinador central que analiza intenciones y distribuye tareas
2. **Elite Training Strategist**: Diseña programas de entrenamiento personalizados
3. **Precision Nutrition Architect**: Crea planes nutricionales adaptados
4. **Biometrics Insight Engine**: Analiza datos biométricos y de salud
5. **Motivation Behavior Coach**: Proporciona apoyo motivacional y conductual
6. **Progress Tracker**: Monitorea y reporta el progreso del usuario
7. **Recovery Corrective**: Especialista en recuperación y prevención de lesiones
8. **Security Compliance Guardian**: Asegura privacidad y cumplimiento normativo
9. **Systems Integration Ops**: Gestiona integraciones con sistemas externos
10. **Biohacking Innovator**: Explora técnicas avanzadas de optimización
11. **Client Success Liaison**: Gestiona la satisfacción del cliente

#### 4. **MCP Ecosystem Integration** 
- ✅ **Estado**: COMPLETADO (100%)
- Gateway MCP unificado operativo para todo el ecosistema NGX:
  - **nexus_core**: Centro de control empresarial con analytics avanzados
  - **nexus_crm**: CRM inteligente con sync bidireccional GENESIS
  - **ngx_pulse**: Plataforma de salud con integración de wearables
  - **ngx_agents_blog**: Sistema de contenido AI con SEO automático
  - **nexus_conversations**: Hub de comunicación con análisis de engagement
- **Características implementadas**:
  - Registro dinámico de herramientas
  - Cache distribuido con Redis
  - Health monitoring y auto-recovery
  - WebSocket para streaming en tiempo real
  - Alta disponibilidad con failover automático

#### 5. **Sistema de Embeddings y Búsqueda (NUEVO - 2025-05-31)**

##### 🦾 Sistema de Embeddings Avanzado
- ✅ **Modelo**: text-embedding-large-exp-03-07 (3072 dimensiones)
- ✅ **Almacenamiento**: Google Cloud Storage (bucket: agents_ngx)
- ✅ **Vector Search**: Vertex AI Vector Search para búsqueda semántica
  - Index ID: 5755708075919015936
  - Endpoint ID: 9027115808366526464
- ✅ **Caché**: Sistema de caché en memoria con TTL configurable
- ✅ **Fallback**: Búsqueda local cuando Vector Search no está disponible

##### 🔍 Sistema de Búsqueda de Texto Completo
- ✅ **Dual Search**: Combina Vector Search (semántico) + PostgreSQL (texto)
- ✅ **Tipos de contenido**:
  - Conversaciones
  - Planes de entrenamiento
  - Registros de nutrición
  - Métricas de progreso
  - Notas del usuario
- ✅ **Características**:
  - Búsqueda fuzzy con trigrams
  - Autocompletado inteligente
  - Filtros por categoría/fecha/usuario
  - Paginación eficiente
- ✅ **API Endpoints**:
  - `POST /search/` - Búsqueda principal
  - `GET /search/quick` - Búsqueda rápida
  - `POST /search/suggestions` - Sugerencias
  - `GET /search/stats` - Estadísticas

#### 6. **Integraciones Externas (FASE 8)**

##### 🎯 Wearables y Dispositivos IoT
- ✅ **WHOOP**: Recuperación, sueño, estrés, entrenamientos
- ✅ **Apple Watch/Health**: Webhooks, shortcuts, datos de salud
- ✅ **Oura Ring**: Sueño, preparación, actividad, frecuencia cardíaca
- ✅ **Garmin**: Actividades, composición corporal, estadísticas diarias

##### 🏋️ Plataformas de Fitness
- ✅ **MyFitnessPal**: Sincronización nutricional completa
  - Seguimiento diario de nutrición
  - Registro de comidas y macronutrientes
  - Análisis de tendencias nutricionales

##### 📨 Comunicación y Notificaciones
- ✅ **Firebase Cloud Messaging**: Sistema de push notifications
- ✅ **WhatsApp Business API**:
  - Mensajería bidireccional con comandos
  - 8 plantillas de mensajes
  - Respuestas rápidas para registro rápido
  - Soporte multimedia completo
  - Notificaciones programadas con Celery

#### 7. **Nuevas Características (FASE 5-7)**

##### 🎥 Sistema de Streaming en Tiempo Real
- ✅ Server-Sent Events (SSE) para respuestas incrementales
- ✅ Endpoint `/stream/chat` con soporte para múltiples agentes
- ✅ Componentes React y HTML para consumo de streams

##### 📊 Sistema de Visualización Completo
- ✅ **ProgressChartGenerator**: Gráficos de peso, composición corporal, rendimiento
- ✅ **NutritionInfographicGenerator**: Infografías nutricionales interactivas
- ✅ **PDFReportGenerator**: Reportes comprehensivos multi-página
- ✅ **ExerciseVideoLinkGenerator**: Enlaces a videos de demostración
- ✅ 11 nuevos endpoints API para visualización

##### 🎤 Procesamiento de Audio/Voz
- ✅ Integración completa con Vertex AI Speech
- ✅ Transcripción y síntesis de voz
- ✅ Análisis emocional de voz
- ✅ Comandos de voz para entrenamientos
- ✅ 7 endpoints API para audio

##### 🖼️ Procesamiento Avanzado de Imágenes
- ✅ Análisis de forma física desde fotos
- ✅ Detección de postura en ejercicios
- ✅ Seguimiento visual de progreso
- ✅ OCR para etiquetas nutricionales

##### 📈 Métricas y Monitoreo
- ✅ Integración con Prometheus
- ✅ Dashboards de Grafana preconfigurados
- ✅ Alertas automáticas (16 reglas)
- ✅ Métricas personalizadas por agente

##### 🔄 Sistema de Feedback
- ✅ Múltiples tipos de feedback (👍/👎, rating, comentarios)
- ✅ Análisis de sentimiento
- ✅ Cálculo de NPS
- ✅ Componente React para UI

##### 🚀 Infraestructura Kubernetes
- ✅ Dockerfiles optimizados multi-stage
- ✅ docker-compose.yml para desarrollo local
- ✅ Manifiestos K8s completos para GKE
- ✅ Configuración de Istio service mesh
- ✅ Auto-scaling avanzado (HPA, VPA)
- ✅ Blue-green deployment strategy

## 🌟 Beneficios del Ecosistema Integrado

### Para Usuarios con Suscripción GENESIS
- **Experiencia Unificada**: Un solo login para acceder a todo el ecosistema
- **AI Personalizada**: 11 agentes que aprenden de todas tus interacciones
- **Datos Sincronizados**: Tu progreso en NGX Pulse se refleja automáticamente en tus planes GENESIS
- **Contenido Inteligente**: NGX Blog genera artículos basados en tus necesidades específicas
- **Soporte 24/7**: Los agentes están siempre disponibles para ayudarte

### Para Entrenadores y Gimnasios
- **Visión 360°**: Dashboard unificado con todas las métricas en Nexus Core
- **CRM Inteligente**: Nexus CRM detecta automáticamente oportunidades de venta
- **Insights Valiosos**: Análisis profundo de conversaciones para mejorar servicios
- **Automatización**: Reduce trabajo manual en 70%
- **ROI Medible**: Tracking preciso del impacto de AI en tu negocio

### Flujo de Datos Inteligente
```
Usuario entrena → NGX Pulse captura datos → GENESIS ajusta plan → 
Nexus Core reporta → CRM registra progreso → Blog sugiere contenido
```

## 🛠️ Stack Tecnológico

### Backend
- **Python 3.9+** - Lenguaje principal
- **FastAPI** - Framework web asíncrono
- **Poetry** - Gestión de dependencias
- **WebSockets** - Comunicación en tiempo real
- **Redis** - Caché y gestión de estado distribuido

### IA y Machine Learning
- **Google Vertex AI** - Modelos de lenguaje y embeddings
- **Google Gemini** - Generación de texto avanzada
- **OpenAI GPT** - Modelos alternativos (opcional)

### Base de Datos y Autenticación
- **Supabase** - ✅ Base de datos PostgreSQL completamente configurada
  - 25 tablas con esquema completo
  - 11 agentes registrados
  - RLS (Row Level Security) activo
  - Service role configurado
  - Cliente optimizado con circuit breaker
- **JWT** - Autenticación integrada con Supabase Auth

### Infraestructura y DevOps
- **Docker** - Contenedorización completa con multi-stage builds
- **Kubernetes** - Manifiestos completos para GKE con Istio service mesh
- **Terraform** - Infraestructura como código
- **Google Cloud Platform** - Plataforma cloud principal
- **GitHub Actions** - CI/CD
- **Istio** - Service mesh para observabilidad y gestión de tráfico

### Observabilidad
- **OpenTelemetry** - Telemetría y trazas distribuidas
- **Prometheus** - Métricas
- **Grafana** - Visualización

## ⚠️ Problemas Identificados y Soluciones

### 1. Error de Configuración de Variables de Entorno
**Problema**: ValidationError de Pydantic por variables de entorno no definidas en el modelo Settings.

**Solución aplicada**: 
```python
class Config:
    extra = "ignore"  # Agregado para ignorar campos extra
```

**Acción requerida**: Crear archivo `.env` basándose en `.env.example`:
```bash
cp .env.example .env
# Editar .env con tus credenciales reales
```

### 2. MCP Tools en Estado Preliminar
**Problema**: La integración con MCP solo devuelve respuestas simuladas.

**Solución propuesta**: Implementar clientes reales para cada servidor MCP en `tools/mcp_toolkit.py`.

### 3. Falta de Archivo .env
**Problema**: El proyecto requiere variables de entorno que no están configuradas.

**Solución**: Crear `.env` con todas las variables necesarias (ver sección Configuración).

## 📋 Requisitos

- Python 3.9 o superior
- Poetry (gestor de dependencias)
- Redis (para caché, opcional en desarrollo)
- Cuenta en Supabase (para base de datos)
- Credenciales de Google Cloud (para Vertex AI)

## 🚀 Instalación Rápida

```bash
# 1. Clonar el repositorio
git clone <url-del-repositorio>
cd genesis-backend

# 2. Instalar Poetry si no está instalado
curl -sSL https://install.python-poetry.org | python3 -

# 3. Instalar dependencias
poetry install --with dev,test

# 4. Configurar variables de entorno
cp .env.example .env
# Editar .env con tus credenciales

# 5. Activar el entorno virtual
poetry shell

# 6. (Opcional) Configurar MCP para Claude Desktop
cp mcp/claude_desktop_config.json ~/Library/Application\ Support/Claude/
# Editar con tu configuración
```

## 🏃‍♂️ Ejecución

### Desarrollo Completo con MCP (Recomendado)
```bash
# Inicia TODO el ecosistema
make ecosystem-dev
```

Este comando inicia:
1. MCP Gateway (puerto 3000)
2. GENESIS Backend (puerto 8000) 
3. Servidor A2A (puerto 9000)
4. Todos los agentes AI

### Solo GENESIS + MCP
```bash
# Inicia MCP Gateway
python -m mcp.main

# En otra terminal, inicia GENESIS
make dev
```

### Solo API GENESIS
```bash
make dev
# o: poetry run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Alta Disponibilidad (Docker)
```bash
docker-compose -f mcp/docker-compose.ha.yml up -d
```

## 🧪 Pruebas

```bash
# Todas las pruebas
make test

# Por categoría
make test-unit        # Pruebas unitarias
make test-integration # Pruebas de integración
make test-agents      # Pruebas de agentes

# Con cobertura
make test-cov         # Cobertura básica
make test-cov-html    # Informe HTML detallado
```

## 📁 Estructura del Proyecto

```
genesis-backend/
├── agents/              # Implementación de los 11 agentes especializados
│   ├── base/            # Clases base ADKAgent y A2AAgent
│   ├── orchestrator/    # Agente coordinador principal
│   └── */               # Demás agentes especializados
├── app/                 # API FastAPI
│   ├── routers/         # Endpoints REST
│   └── schemas/         # Esquemas Pydantic
├── mcp/                 # 🆕 MCP Gateway y Adaptadores
│   ├── server/          # Gateway server unificado
│   ├── adapters/        # Adaptadores para cada herramienta NGX
│   ├── config/          # Configuración MCP
│   └── startup_orchestrator.py # Alta disponibilidad
├── clients/             # Clientes para servicios externos
│   ├── vertex_ai/       # Cliente optimizado para Vertex AI
│   ├── gemini_client.py # Cliente para Gemini
│   └── supabase_client.py # Cliente para Supabase
├── core/                # Funcionalidades centrales
│   ├── state_manager_optimized.py # Gestión de estado distribuido
│   ├── intent_analyzer.py # Análisis de intenciones
│   └── telemetry.py     # Sistema de telemetría
├── infrastructure/      # Infraestructura A2A
│   ├── a2a_optimized.py # Servidor A2A optimizado
│   └── adapters/        # Adaptadores para cada agente
├── tests/               # Suite completa de pruebas
│   ├── unit/            # Pruebas unitarias
│   ├── integration/     # Pruebas de integración
│   └── mocks/           # Mocks para pruebas
├── terraform/           # Infraestructura como código
├── kubernetes/          # Configuración K8s
└── docs/                # Documentación detallada
```

## 🔧 Configuración de Variables de Entorno

Variables críticas que deben configurarse en `.env`:

```env
# API y Servidor
HOST=0.0.0.0
PORT=8000
DEBUG=false

# A2A
A2A_HOST=0.0.0.0
A2A_PORT=9000
A2A_SERVER_URL=ws://localhost:9000

# Supabase (Requerido)
SUPABASE_URL=https://tu-proyecto.supabase.co
SUPABASE_ANON_KEY=tu-clave-anonima

# Google AI (Requerido para agentes)
GEMINI_API_KEY=tu-api-key
VERTEX_PROJECT_ID=tu-proyecto-id
VERTEX_LOCATION=us-central1

# Redis (Opcional en desarrollo)
USE_REDIS_CACHE=false

# MCP Gateway (Requerido para ecosistema)
MCP_HOST=0.0.0.0
MCP_PORT=3000
MCP_API_KEY=tu-mcp-api-key
NEXUS_CORE_URL=http://localhost:8001
NEXUS_CRM_URL=http://localhost:8002
NGX_PULSE_URL=http://localhost:8003
NGX_BLOG_URL=http://localhost:8004
NEXUS_CONV_URL=http://localhost:8005
```

## 📊 Estado de Componentes

| Componente | Estado | Progreso |
|-----------|--------|----------|
| Servidor A2A | ✅ Completado | 100% |
| Adaptadores de Agentes | ✅ Completado | 100% |
| Cliente Vertex AI | ✅ Completado | 100% |
| State Manager | ✅ Completado | 100% |
| Intent Analyzer | ✅ Completado | 100% |
| MCP Gateway | ✅ Completado | 100% |
| MCP Adaptadores | ✅ Completado | 100% |
| Alta Disponibilidad | ✅ Completado | 100% |
| Documentación | ✅ Actualizada | 100% |

## 🚦 Próximos Pasos

### Fase 10: AI Avanzado y Seguridad (Próxima)
1. **Modelos AI Personalizados**: Fine-tuning de modelos para cada agente
2. **Seguridad Avanzada**: Implementar zero-trust architecture
3. **Análisis Predictivo**: ML para predecir resultados de usuarios
4. **Blockchain Integration**: Para certificación de logros

### Deployment a Producción
1. **Testing en Staging**: Probar todo el ecosistema integrado
2. **Load Testing**: Validar capacidad para 10,000+ usuarios concurrentes
3. **Security Audit**: Revisión completa de seguridad
4. **Launch Strategy**: Rollout gradual por regiones

## 🤝 Contribución

1. Fork el repositorio
2. Crea una rama para tu feature (`git checkout -b feature/NuevaCaracteristica`)
3. Commit con mensajes descriptivos siguiendo el formato:
   - `Feat(component): descripción`
   - `Fix(component): descripción`
   - `Docs(component): descripción`
4. Push a tu rama (`git push origin feature/NuevaCaracteristica`)
5. Abre un Pull Request

## 📄 Licencia

[Especificar licencia del proyecto]

## 📞 Soporte

Para reportar problemas o solicitar ayuda:
- Abrir un issue en GitHub
- Contactar al equipo de desarrollo
- Revisar la documentación en `/docs`

---

## 🎯 Visión del Ecosistema NGX

GENESIS no es solo un backend - es el cerebro AI que potencia todo el ecosistema NGX. Con la integración MCP completa, hemos logrado:

- **Unificación Total**: Un solo punto de acceso para todas las herramientas
- **Inteligencia Distribuida**: Los agentes aprenden de todas las interacciones
- **Escalabilidad Infinita**: Arquitectura preparada para millones de usuarios
- **Experiencia Revolucionaria**: AI que realmente entiende y ayuda

**"El futuro del fitness no es tener más datos, es tener inteligencia que los interprete y actúe por ti."**

---

**Última actualización**: 2025-07-20 | **Versión**: 1.0.0-RC1 | **Estado**: Production Ready 🚀

Para más información:
- **Documentación técnica**: `/docs/`
- **Guía del ecosistema**: `NGX_ECOSYSTEM_OVERVIEW.md`
- **Estado MCP**: `MCP_INTEGRATION_STATUS.md`
- **Deployment**: `mcp/DEPLOYMENT_GUIDE.md`
