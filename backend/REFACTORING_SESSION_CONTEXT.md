# 📋 Contexto de Sesión de Refactorización

## 🎯 Resumen para la Próxima Conversación

### Objetivo Principal
Refactorizar los 9 agentes principales del sistema NGX para reducir su tamaño de 1,900-3,800 líneas a ~200-300 líneas cada uno, utilizando la nueva arquitectura modular.

### Lo que ya tenemos listo:

1. **Clases Base Implementadas**:
   - `agents/base/base_data_service.py` - Para servicios de datos
   - `agents/base/base_security_service.py` - Para servicios de seguridad
   - `agents/base/base_integration_service.py` - Para integraciones
   - `agents/base/base_ngx_agent.py` - Para todos los agentes

2. **Scripts de Automatización**:
   - `scripts/refactor_services.py` - Refactoriza servicios automáticamente
   - `scripts/modularize_agent.py` - Divide agentes en módulos

3. **Ejemplo Completo**:
   - `agents/elite_training_strategist/agent_refactored.py` - BLAZE refactorizado
   - De 3,151 → 200 líneas (93% reducción)

### Agentes por Refactorizar (en orden de prioridad):

| Agente | Líneas Actuales | Prioridad | Razón |
|--------|-----------------|-----------|-------|
| orchestrator | 1,924 | CRÍTICA | Coordina todos los demás |
| precision_nutrition_architect | 3,833 | ALTA | El más grande |
| nova_biohacking_innovator | 3,322 | ALTA | Segundo más grande |
| progress_tracker | 2,881 | ALTA | Mucha duplicación |
| motivation_behavior_coach | 2,871 | MEDIA | Duplicación con wellness |
| female_wellness_coach | 2,030 | MEDIA | Skills compartidas |
| code_genetic_specialist | 1,909 | MEDIA | Más pequeño |
| wave_performance_analytics | ~1,500 | BAJA | Ya más optimizado |

### Estructura Target para Cada Agente:

```
agents/agent_name/
├── __init__.py              # Exports públicos
├── agent.py                 # Clase principal (~200 líneas)
├── config.py               # Configuración (~150 líneas)
├── prompts/                # Prompts modulares
│   ├── __init__.py
│   └── base_prompt.py
├── skills/                 # Skills individuales
│   ├── __init__.py
│   ├── skill_1.py
│   └── skill_2.py
├── services/               # Servicios refactorizados
│   ├── __init__.py
│   └── data_service.py
└── models/                 # Modelos Pydantic
    ├── __init__.py
    └── schemas.py
```

### Proceso de Refactorización:

1. **Backup**: `cp agent.py agent_original.py`
2. **Modularizar**: `python scripts/modularize_agent.py agents/[agent_name]/ --no-dry-run`
3. **Refactorizar servicios**: Heredar de clases base
4. **Actualizar agent.py**: Heredar de `BaseNGXAgent`
5. **Test**: Verificar que todo funciona
6. **Commit**: Un commit por agente

### Beneficios que Obtendremos:

- **Caching Redis**: Automático para todos
- **Circuit Breaker**: Protección incluida
- **Health Checks**: Sin código adicional
- **Métricas**: Dashboard automático
- **Rate Limiting**: Control de uso
- **Audit Logging**: GDPR/HIPAA compliance

### Para Iniciar la Próxima Sesión:

```bash
# 1. Navegar al proyecto
cd /Users/aldoolivas/Desktop/GENESIS_oficial_BETA/backend

# 2. Activar entorno
source .venv/bin/activate

# 3. Ver este contexto
cat REFACTORING_SESSION_CONTEXT.md

# 4. Empezar con orchestrator
python scripts/modularize_agent.py agents/orchestrator/ --dry-run
```

### Mensaje para Claude en la próxima sesión:

"Hola Claude, continuemos con la refactorización de los agentes NGX. Ya tenemos las clases base, scripts de automatización y un ejemplo completo con BLAZE. Ahora necesitamos refactorizar los 8 agentes restantes, empezando por el orchestrator que es el más crítico. El plan completo está en REFACTORING_MASTER_PLAN.md y el contexto en REFACTORING_SESSION_CONTEXT.md."

---

**Guardado: 2025-07-17**
**Próxima tarea: Refactorizar orchestrator agent**