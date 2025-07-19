# Registro de Cambios (CHANGELOG)

Todos los cambios notables en el proyecto GENESIS serán documentados en este archivo.

## [1.2.0] - 2025-07-19 - Performance Optimization & Project Cleanup

### ✨ Añadido
- **Sistema de Embeddings**: Implementado método `batch_generate_embeddings` en `vertex_ai_client.py`
- **Optimización Frontend**: 
  - Lazy loading con React.Suspense para todas las páginas
  - Code splitting configurado en Vite con chunks manuales
- **Rendimiento de Base de Datos**: 
  - Script `V3_PERFORMANCE_INDICES.sql` con índices optimizados
  - Script `analyze_query_performance.py` para análisis de rendimiento
- **Sistema CDN**: 
  - Configuración completa de CDN para backend y frontend
  - Componentes React optimizados (`CDNImage`, `CDNAvatar`, etc.)
  - Service Worker para cache offline-first
  - Documentación completa en `CDN_IMPLEMENTATION_GUIDE.md`

### 🔧 Cambiado
- **Estructura del Proyecto**: Reorganizada completamente
- **Documentación**: Movida a directorios organizados (`docs/reports/`, `docs/status/`)
- **Scripts**: Consolidados en un único `cleanup.sh` con múltiples opciones
- **Configuración de Entorno**: Mantenidos solo scripts esenciales

### 🗑️ Eliminado
- **Archivos Duplicados**: 40+ archivos duplicados y obsoletos eliminados
- **Directorios Antiguos**: `backups/`, `tmp/`, `frontend/` duplicado
- **Archivos Temporales**: Screenshots, reportes JSON antiguos

### 📁 Organizado
- **Estructura de Archivo**: Creado `.archive/` con subdirectorios organizados
- **Documentación**: Organizada en `docs/reports/` y `docs/status/`

### 🔒 Seguridad
- **Actualizado .gitignore**: Patrones mejorados para archivos de backup y temporales

## [1.1.0] - 2025-07-18 - Supabase Database Complete Setup

### ✨ Añadido
- **Integración Supabase**: Configuración completa de 25 tablas
- **Registro de Agentes**: 11 agentes registrados con voice IDs
- **Políticas RLS**: Seguridad a nivel de fila implementada

## [No publicado - Legacy]

### Añadido
- Clase base `BaseAgentAdapter` para reducir duplicación de código en adaptadores
- Script unificado `setup_unified_env.sh` para configuración de entornos
- Script `scripts/clean_pyproject_files.sh` para consolidar dependencias
- Implementación completa de `_get_program_type_from_profile` en `ProgramClassificationService`
- Pruebas para verificar la inicialización condicional de telemetría
- Documentación detallada sobre las mejoras en `docs/refactorizacion_y_optimizacion.md`
- Soporte para configuración condicional de telemetría
- Pruebas completas para el cliente Vertex AI optimizado
- Soporte para OpenTelemetry en el cliente Vertex AI
- Script `scripts/verify_adapter_inheritance.py` para identificar adaptadores que necesitan migración
- Implementación del adaptador `RecoveryCorrectiveAdapter` con herencia de `BaseAgentAdapter`
- Pruebas unitarias completas para `RecoveryCorrectiveAdapter`

### Corregido
- Errores de importación en las pruebas del cliente Vertex AI
- Problemas con la caché en memoria en el cliente Vertex AI
- Problemas con el pool de conexiones en el cliente Vertex AI
- Errores de importación de StateManager en pruebas unitarias
- Problemas de inicialización de TestClient en pruebas de autenticación
- Actualización de adaptadores para utilizar la clase base BaseAgentAdapter

### Cambiado
- Refactorización del cliente Vertex AI para usar una estructura modular
- Mejora en la gestión de errores y telemetría

## [0.1.0] - 2025-05-11

### Añadido
- Versión inicial del proyecto NGX Agents
- Implementación de agentes básicos
- Integración con Vertex AI
- Sistema de caché en memoria y pool de conexiones
