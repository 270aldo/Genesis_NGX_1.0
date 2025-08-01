# CLAUDE.md - Guía de Desarrollo GENESIS

Este archivo proporciona orientación a Claude Code cuando trabaja con el código de GENESIS.

## 🚀 Estado Actual: 98% COMPLETADO - BETA VALIDATION SUITE READY

### Arquitectura del Sistema

**Backend**: FastAPI con 11 agentes especializados usando Google Vertex AI
**Frontend**: React/TypeScript con Vite y shadcn-ui
**Agentes**: 11 agentes implementados siguiendo arquitectura ADK/A2A
**Seguridad**: Rate limiting, headers HTTP, validaciones, encriptación
**IA**: Vertex AI con streaming, function calling y grounding
**API**: Endpoints paginados y documentados con OpenAPI
**MCP Gateway**: Sistema unificado conectando 5 herramientas del ecosistema NGX
**Alta Disponibilidad**: Failover automático, load balancing, monitoring completo

## Arquitectura de Agentes (ADK/A2A)

### ✅ Agentes Completamente Refactorizados (2025-07-18)

Todos los agentes siguen la arquitectura modular ADK/A2A:

| Agente | Tipo | Líneas | Reducción | Estado |
|--------|------|---------|-----------|---------|
| NEXUS (Orchestrator) | Core | ~400 | - | ✅ ADK/A2A |
| BLAZE (Elite Training) | Frontend | 361 | 87% | ✅ ADK/A2A |
| SAGE (Nutrition) | Frontend | ~400 | - | ✅ ADK/A2A |
| CODE (Genetic) | Frontend | 361 | 87% | ✅ ADK/A2A |
| WAVE (Analytics) | Frontend | 324 | 59% | ✅ ADK/A2A |
| LUNA (Female Wellness) | Frontend | 353 | 83% | ✅ ADK/A2A |
| STELLA (Progress) | Frontend | 362 | 87% | ✅ ADK/A2A |
| SPARK (Motivation) | Frontend | 357 | 88% | ✅ ADK/A2A |
| NOVA (Biohacking) | Frontend | 354 | 89% | ✅ ADK/A2A |
| GUARDIAN (Security) | Backend | 304 | 89% | ✅ ADK/A2A |
| NODE (Integration) | Backend | 302 | 89% | ✅ ADK/A2A |

### Reglas de Arquitectura ADK/A2A

**REGLA FUNDAMENTAL**: TODOS los agentes DEBEN heredar de BaseNGXAgent Y ADKAgent

```python
class AgentName(BaseNGXAgent, ADKAgent):
    """Siempre hereda de AMBAS clases base."""
```

### Estructura de Agentes

```text
agents/
└── agent_name/
    ├── agent.py         # < 400 líneas, hereda de BaseNGXAgent Y ADKAgent
    ├── config.py        # Configuración con Pydantic
    ├── prompts.py       # Prompts centralizados
    └── skills/          # Skills modulares
        ├── __init__.py
        └── skill_name.py # Una skill por archivo
```

## Comandos Esenciales

### Backend

```bash
cd backend
poetry install --with dev
make dev            # Puerto 8000

# Testing
make test           # Todos los tests
make test-unit      # Tests unitarios
make test-agents    # Tests de agentes
make test-cov       # Reporte de cobertura (objetivo: 85%+)

# Calidad de código
make lint           # Ruff y mypy
make format         # Black e isort
make check          # Todas las verificaciones
```

### Frontend

```bash
cd frontend
npm install
npm run dev         # Puerto 5173

# Testing
npm test            # Jest tests
npm run test:watch  # Modo watch
npm run test:coverage

# Build
npm run build       # Build de producción
npm run lint        # ESLint
npm run preview     # Preview del build
```

## Guías de Desarrollo

### Al Agregar Nuevas Características

1. **Backend**: Sigue el patrón A+ en `/docs/A+_AGENT_STANDARDIZATION.md`
2. **Frontend**: Usa patrones existentes de `/src/components/`
3. **Testing**: Mantén 85%+ de cobertura, usa marcadores de test apropiados
4. **Documentación**: Actualiza docs relevantes siguiendo estándares A+

### Desarrollo de Agentes

1. **Estructura Obligatoria**:
   - Hereda de BaseNGXAgent Y ADKAgent
   - Implementa métodos requeridos
   - Registra en servidor A2A
   - Archivos < 400 líneas

2. **Skills Modulares**:
   - Una skill por archivo
   - Hereda de clase base Skill
   - Implementa método execute()
   - Maneja errores apropiadamente

3. **Configuración**:
   - Usa Pydantic para validación
   - Define en config.py
   - Incluye metadata del agente

### Trabajo con IA

- **Prompts**: Centralizados en prompts.py
- **Personalidad**: Sistema PRIME vs LONGEVITY
- **Seguridad**: Template de seguridad obligatorio
- **Streaming**: Soporte nativo con Vertex AI

## Integración con ElevenLabs

### ✅ Voces Oficiales Implementadas

| Agente | Voice ID | Voz |
|--------|----------|-----|
| NEXUS | EkK5I93UQWFDigLMpZcX | James |
| BLAZE | iP95p4xoKVk53GoZ742B | Chris |
| SAGE | 5l5f8iK3YPeGga21rQIX | Adelina |
| SPARK | scOwDtmlUjD3prqpp97I | Sam |
| WAVE | SOYHLrjzK2X1ezoPC6cr | Harry |
| LUNA | kdmDKE6EkgrWrrykO9Qt | Alexandra |
| STELLA | BZgkqPqms7Kj9ulSkVzn | Eve |
| NOVA | aMSt68OGf4xUZAnLpTU8 | Juniper |
| CODE | 1SM7GgM6IMuvQlz2BwM3 | Mark |

## Consideraciones de Rendimiento

- Usa caché Redis para operaciones costosas
- Implementa streaming para respuestas largas
- Usa connection pooling para base de datos
- Monitorea con Prometheus en `/metrics`

## Seguridad

- JWT tokens manejados por `core/auth.py`
- Toda configuración sensible en variables de entorno
- Características GDPR/HIPAA en Guardian
- Nunca commits `.env` o expone API keys

## ✅ Estado de Supabase: 100% COMPLETADO

**ÚLTIMA ACTUALIZACIÓN**: 2025-07-18

### Base de Datos Supabase

- ✅ **25 Tablas Creadas** - Esquema completo implementado
- ✅ **11 Agentes Registrados** - Todos operativos con voice IDs
- ✅ **RLS Policies Activas** - Seguridad a nivel de fila funcionando
- ✅ **Service Role Configurado** - Acceso administrativo completo
- ✅ **Migraciones Ejecutadas** - Master setup + features avanzadas

### Conectividad Validada

- ✅ Supabase Client API - Funcionando
- ✅ Autenticación JWT - Integrada
- ✅ Acceso Administrativo - Configurado
- ⚠️ Conexión Directa PostgreSQL - Solo desde IPs whitelistadas

**Ver reporte completo**: `/backend/SUPABASE_COMPLETION_REPORT.md`

## ✅ Optimizaciones Completadas (2025-07-19)

### Performance & Cleanup

- **Embeddings**: `batch_generate_embeddings` implementado y testeado
- **Frontend**: Lazy loading + code splitting configurado
- **Database**: Índices de rendimiento optimizados (V3_PERFORMANCE_INDICES.sql)
- **CDN**: Sistema completo con componentes React y Service Worker
- **Project Cleanup**: 40+ archivos obsoletos eliminados/organizados

### Estructura Organizada

```text
backend/
├── .archive/              # Archivos históricos
├── docs/
│   ├── reports/          # Reportes organizados
│   └── status/           # Estados del proyecto
├── scripts/
│   └── cleanup.sh        # Script consolidado
└── sql/                  # Scripts optimizados
```

## ✅ MCP Ecosystem Integration (COMPLETADO 2025-07-20)

### Gateway Unificado

- **Puerto**: 3000
- **Protocolo**: HTTP/WebSocket con soporte SSE
- **Autenticación**: API Key unificada
- **Cache**: Redis distribuido con TTL configurable

### Adaptadores Implementados

1. **nexus_core**: Analytics, dashboard, reportes, AI insights
2. **nexus_crm**: Contactos, deals, actividades, sync con GENESIS
3. **ngx_pulse**: Biométricos, wearables, trends, reportes de salud
4. **ngx_blog**: Generación de contenido, SEO, analytics, scheduling
5. **nexus_conversations**: Chat management, historial, engagement, insights

### Alta Disponibilidad

- **Orchestrator**: `mcp/startup_orchestrator.py`
- **Docker HA**: `mcp/docker-compose.ha.yml`
- **HAProxy**: Load balancing con health checks
- **Prometheus**: Monitoring y alertas configuradas

### Configuración Claude Desktop

```json
{
  "mcpServers": {
    "genesis-ngx-ecosystem": {
      "command": "python",
      "args": ["-m", "mcp.main"],
      "cwd": "/path/to/genesis/backend",
      "env": {
        "MCP_PORT": "3000",
        "MCP_API_KEY": "your-key"  # pragma: allowlist secret
      }
    }
  }
}
```

## ✅ Beta Validation Suite (ACTUALIZADO 2025-08-01)

### 🔄 Última Sesión de Trabajo (1 Agosto 2025)

- **Week 1**: ✅ COMPLETADO - Beta Validation optimizada (88% pass rate)
- **Week 2**: ✅ COMPLETADO - 141 unit tests implementados para 6 módulos core
- **Week 3**: 🔄 EN PROGRESO - Staging tests con GCP real (3/11 agentes completados)

### Resultados de Tests (1 Agosto)

- **Beta Validation**: 88% ✅ (59/67 tests) - OBJETIVO ALCANZADO
- **Edge Cases**: 86.7% ✅ (13/15) - MEJORADO SIGNIFICATIVAMENTE
- **Unit Tests**: 141 tests implementados cubriendo 6 módulos core
- **Staging Tests**: Infraestructura creada + 3 agentes testeados

### Testing Progress

#### Week 1 ✅

- Optimización de Beta Validation Suite
- Edge cases mejorados de 6.7% → 86.7%
- Tiempo reducido de >2min → 0.41s

#### Week 2 ✅

- JWT Auth: 11 tests
- Persistence Client: 21 tests
- State Manager: 24 tests
- Budget Manager: 25 tests
- Telemetry: 31 tests
- Redis Pool: 29 tests

#### Week 3 🔄

- ✅ Infraestructura de staging tests
- ✅ NEXUS Orchestrator tests
- ✅ BLAZE Elite Training tests
- ✅ SAGE Nutrition tests
- ⏳ 8 agentes restantes por testear

### Suite de Testing Completa

- **69 Escenarios de Prueba** cubriendo todos los casos críticos
- **5 Categorías**: Frustración, Edge Cases, Multi-Agent, Ecosystem, Stress
- **Response Quality Validator** con 8 dimensiones de calidad
- **Automatización CI/CD** con GitHub Actions

### Ejecutar Tests

```bash
# Todos los tests
./scripts/run_beta_tests.sh

# Tests rápidos
./scripts/run_beta_tests.sh --quick

# Categoría específica
./scripts/run_beta_tests.sh --category user_frustration

# Con reporte detallado
./scripts/run_beta_tests.sh --verbose --report
```

### Criterios de Lanzamiento

- ✅ **Listo para BETA**: Pass rate ≥ 90%, sin issues críticos
- ⚠️ **Retrasar**: Pass rate < 90% o issues menores
- ❌ **Bloquear**: Fallos críticos de seguridad/privacidad

### Escenarios Críticos

1. Detección de emergencias médicas
2. Protocolos de seguridad
3. Privacidad de datos GDPR
4. Resiliencia del sistema
5. Activación del Guardian

## Próximos Pasos

1. **Ejecutar Beta Validation Suite**: Validar todos los escenarios antes del lanzamiento
2. **Integración Real del Orchestrator**: Conectar tests con el sistema real
3. **Testing en Staging**: Validar integración completa del ecosistema
4. **Security Audit**: Revisión completa pre-producción
5. **Launch Readiness**: Preparar infraestructura para BETA

---

**Nota**: Este es un documento vivo. Actualízalo cuando hagas cambios significativos en la arquitectura.
