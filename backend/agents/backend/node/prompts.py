"""
Node Prompts
============

Centralized prompts for the Node agent.
"""

from typing import Dict, Any, List


class NodePrompts:
    """Manages all prompts for Node agent."""
    
    @staticmethod
    def get_base_instructions() -> str:
        """Get base instructions for Node."""
        return """Eres NODE, el especialista en integración de sistemas y operaciones. Tu función es facilitar la integración de diferentes sistemas, automatizar flujos de trabajo, gestionar conexiones con APIs externas, y optimizar la infraestructura tecnológica.

FUNCIONES PRINCIPALES:
- Integras sistemas de fitness y salud (Garmin, Fitbit, Apple Health, Strava, etc.)
- Automatizas flujos de trabajo complejos entre múltiples plataformas
- Gestionas APIs REST, GraphQL, WebSocket y otros protocolos
- Optimizas infraestructura cloud y on-premise
- Diseñas y mantienes pipelines de datos eficientes
- Coordinas microservicios y arquitecturas distribuidas

INTEGRACIÓN DE SISTEMAS:
- Conectas wearables y dispositivos de fitness con plataformas centralizadas
- Sincronizas datos entre múltiples fuentes manteniendo consistencia
- Implementas transformaciones de datos y mapeos entre formatos
- Manejas autenticación OAuth, API keys y tokens de acceso
- Resuelves conflictos de datos y duplicados inteligentemente

AUTOMATIZACIÓN Y ORQUESTACIÓN:
- Diseñas workflows automatizados usando herramientas como Zapier, n8n, Airflow
- Implementas lógica condicional y manejo de errores robusto
- Orquestas procesos batch y streaming en tiempo real
- Optimizas rendimiento y minimizas latencia en integraciones
- Monitoreas y alertas sobre fallos en pipelines

PRINCIPIOS DE OPERACIÓN:
1. Confiabilidad primero - las integraciones deben ser robustas y resilientes
2. Eficiencia en recursos - optimiza uso de CPU, memoria y ancho de banda
3. Seguridad en tránsito - encripta datos sensibles siempre
4. Escalabilidad horizontal - diseña para crecer sin límites
5. Observabilidad total - logs, métricas y trazas para debugging"""

    @staticmethod
    def get_integration_request_prompt(data: Dict[str, Any]) -> str:
        """Get prompt for system integration requests."""
        systems = data.get("systems", [])
        requirements = data.get("requirements", {})
        query = data.get("query", "")
        
        return f"""Analiza la siguiente solicitud de integración de sistemas:

Solicitud: {query}
Sistemas a integrar: {', '.join(systems) if systems else 'Por determinar'}
Requisitos: {requirements}

Proporciona una solución de integración que incluya:
1. Arquitectura de integración recomendada
2. APIs y endpoints necesarios
3. Flujo de datos entre sistemas
4. Autenticación y autorización requerida
5. Transformaciones de datos necesarias
6. Consideraciones de rendimiento y escalabilidad
7. Plan de implementación paso a paso

Enfócate en soluciones prácticas y probadas en producción."""

    @staticmethod
    def get_automation_request_prompt(data: Dict[str, Any]) -> str:
        """Get prompt for workflow automation."""
        workflow = data.get("workflow", {})
        triggers = data.get("triggers", [])
        actions = data.get("actions", [])
        
        return f"""Diseña una automatización para el siguiente workflow:

Workflow: {workflow}
Triggers: {', '.join(triggers) if triggers else 'Por definir'}
Acciones: {', '.join(actions) if actions else 'Por definir'}

Crea un diseño de automatización que incluya:
1. Diagrama de flujo del proceso
2. Condiciones y reglas de negocio
3. Manejo de errores y reintentos
4. Validaciones de datos en cada paso
5. Notificaciones y alertas
6. Métricas de éxito y KPIs
7. Herramientas recomendadas (Zapier, n8n, etc.)

Asegura que la automatización sea mantenible y debuggeable."""

    @staticmethod
    def get_api_management_prompt(data: Dict[str, Any]) -> str:
        """Get prompt for API management."""
        api_type = data.get("api_type", "REST")
        operations = data.get("operations", [])
        requirements = data.get("requirements", {})
        
        return f"""Gestiona la siguiente implementación de API:

Tipo de API: {api_type}
Operaciones: {', '.join(operations) if operations else 'CRUD estándar'}
Requisitos: {requirements}

Proporciona especificaciones que incluyan:
1. Diseño de endpoints y recursos
2. Esquemas de request/response
3. Autenticación y rate limiting
4. Versionado y compatibilidad
5. Documentación OpenAPI/Swagger
6. Tests de integración
7. Monitoreo y analytics

Sigue mejores prácticas de diseño de APIs RESTful."""

    @staticmethod
    def get_infrastructure_optimization_prompt(data: Dict[str, Any]) -> str:
        """Get prompt for infrastructure optimization."""
        current_setup = data.get("current_setup", {})
        pain_points = data.get("pain_points", [])
        goals = data.get("goals", [])
        
        return f"""Optimiza la siguiente infraestructura:

Setup actual: {current_setup}
Problemas identificados: {', '.join(pain_points) if pain_points else 'Performance general'}
Objetivos: {', '.join(goals) if goals else 'Mejorar eficiencia'}

Proporciona un plan de optimización que incluya:
1. Análisis de bottlenecks actuales
2. Arquitectura objetivo recomendada
3. Estrategias de migración sin downtime
4. Optimizaciones de costo
5. Mejoras de seguridad y compliance
6. Automatización de deployment
7. Métricas de éxito

Prioriza quick wins y mejoras incrementales."""

    @staticmethod
    def get_data_pipeline_prompt(data: Dict[str, Any]) -> str:
        """Get prompt for data pipeline design."""
        sources = data.get("sources", [])
        transformations = data.get("transformations", [])
        destinations = data.get("destinations", [])
        volume = data.get("data_volume", "medium")
        
        return f"""Diseña un pipeline de datos para:

Fuentes de datos: {', '.join(sources) if sources else 'Múltiples fuentes'}
Transformaciones: {', '.join(transformations) if transformations else 'ETL estándar'}
Destinos: {', '.join(destinations) if destinations else 'Data warehouse'}
Volumen estimado: {volume}

Crea un diseño que incluya:
1. Arquitectura del pipeline (batch vs streaming)
2. Herramientas y tecnologías recomendadas
3. Esquemas de datos y validaciones
4. Estrategias de particionamiento
5. Manejo de errores y recuperación
6. Monitoreo y alertas
7. Optimización de costos

Considera escalabilidad y mantenibilidad a largo plazo."""

    @staticmethod
    def get_service_orchestration_prompt(data: Dict[str, Any]) -> str:
        """Get prompt for microservices orchestration."""
        services = data.get("services", [])
        communication = data.get("communication_pattern", "sync")
        requirements = data.get("requirements", {})
        
        return f"""Orquesta los siguientes microservicios:

Servicios: {', '.join(services) if services else 'Múltiples servicios'}
Patrón de comunicación: {communication}
Requisitos: {requirements}

Diseña una estrategia de orquestación que incluya:
1. Topología de servicios y dependencias
2. Patrones de comunicación (sync/async)
3. Service discovery y load balancing
4. Circuit breakers y resilience
5. Distributed tracing y logging
6. Gestión de configuración
7. Deployment y rollback strategies

Usa patrones probados como saga, event sourcing cuando aplique."""

    @staticmethod
    def get_performance_monitoring_prompt(data: Dict[str, Any]) -> str:
        """Get prompt for performance monitoring setup."""
        systems = data.get("systems", [])
        metrics = data.get("key_metrics", [])
        sla = data.get("sla_requirements", {})
        
        return f"""Configura monitoreo de performance para:

Sistemas: {', '.join(systems) if systems else 'Stack completo'}
Métricas clave: {', '.join(metrics) if metrics else 'Latencia, throughput, errores'}
SLA requerido: {sla}

Implementa una solución de monitoreo que incluya:
1. Métricas de aplicación y infraestructura
2. Dashboards en tiempo real
3. Alertas inteligentes y escalamiento
4. Análisis de root cause
5. Capacity planning
6. Cost tracking
7. Reportes automatizados

Utiliza herramientas como Prometheus, Grafana, ELK stack."""