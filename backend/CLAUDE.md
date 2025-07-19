# CLAUDE.md - Guía de Desarrollo GENESIS

Este archivo proporciona orientación a Claude Code cuando trabaja con el código de GENESIS.

## 🚀 Estado Actual: 95% COMPLETADO - OPTIMIZADO Y ORGANIZADO

### Arquitectura del Sistema

**Backend**: FastAPI con 11 agentes especializados usando Google Vertex AI  
**Frontend**: React/TypeScript con Vite y shadcn-ui  
**Agentes**: 11 agentes implementados siguiendo arquitectura ADK/A2A  
**Seguridad**: Rate limiting, headers HTTP, validaciones, encriptación  
**IA**: Vertex AI con streaming, function calling y grounding  
**API**: Endpoints paginados y documentados con OpenAPI  

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

```
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
```
backend/
├── .archive/              # Archivos históricos
├── docs/
│   ├── reports/          # Reportes organizados
│   └── status/           # Estados del proyecto
├── scripts/
│   └── cleanup.sh        # Script consolidado
└── sql/                  # Scripts optimizados
```

## Próximos Pasos

1. **MCP Integration**: Implementar Model Context Protocol
2. **Deployment**: Configurar staging environment  
3. **Monitoreo**: Prometheus + Grafana
4. **CI/CD**: Pipeline automatizado

---

**Nota**: Este es un documento vivo. Actualízalo cuando hagas cambios significativos en la arquitectura.