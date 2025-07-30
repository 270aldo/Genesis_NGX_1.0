# Guía de Configuración de Entornos - GENESIS

## Resumen de Entornos Necesarios

### 1. Entorno Python (Poetry)
- **Gestor**: Poetry 2.1.3
- **Python**: 3.12.9
- **Ubicación**: `.venv` en el directorio backend
- **Estado**: ✅ Configurado correctamente

### 2. Entorno Node.js (Frontend)
- **Gestor**: npm/pnpm
- **Node**: Requerido para el frontend React
- **Ubicación**: `frontend/node_modules`

### 3. Servicios Docker
- **Redis**: Para caché y rate limiting
- **PostgreSQL**: Base de datos local (opcional, si no usas Supabase)
- **Prometheus/Grafana**: Monitoreo (opcional)

## Comandos Esenciales

### Python/Backend

```bash
# Activar entorno Poetry
cd backend
poetry shell

# Instalar dependencias
poetry install

# Ejecutar comandos en el entorno
poetry run python script.py
poetry run pytest

# Actualizar dependencias
poetry update

# Añadir nueva dependencia
poetry add nombre-paquete

# Añadir dependencia de desarrollo
poetry add --dev nombre-paquete
```

### Docker Services

```bash
# Iniciar servicios de desarrollo
./start-dev-services.sh

# O manualmente:
docker-compose -f docker-compose.dev.yml up -d redis

# Ver logs
docker-compose -f docker-compose.dev.yml logs -f redis

# Detener servicios
docker-compose -f docker-compose.dev.yml down
```

## Verificación del Entorno

### 1. Python/Poetry
```bash
# Verificar entorno activo
poetry env info

# Verificar dependencias instaladas
poetry show

# Verificar pytest
poetry run pytest --version
```

### 2. Variables de Entorno
```bash
# Verificar que .env existe
ls -la backend/.env

# Verificar variables críticas
grep -E "JWT_SECRET|REDIS_PASSWORD|ENV=" backend/.env
```

### 3. Servicios
```bash
# Verificar Redis
docker-compose -f docker-compose.dev.yml exec redis redis-cli ping

# Verificar conectividad
redis-cli -h localhost -p 6379 -a $REDIS_PASSWORD ping
```

## Problemas Comunes y Soluciones

### 1. "pytest not found"
**Problema**: pytest no se encuentra aunque está instalado
**Solución**: 
```bash
# Siempre usar poetry run
poetry run pytest

# O activar el shell primero
poetry shell
pytest
```

### 2. "Permission denied"
**Problema**: Permisos en scripts
**Solución**:
```bash
chmod +x start-dev-services.sh
chmod +x scripts/*.py
```

### 3. "Docker not running"
**Problema**: Docker daemon no está activo
**Solución**:
- macOS: Iniciar Docker Desktop
- Linux: `sudo systemctl start docker`

### 4. "Port already in use"
**Problema**: Puerto 6379 (Redis) o 8000 (FastAPI) ocupado
**Solución**:
```bash
# Ver qué usa el puerto
lsof -i :6379
lsof -i :8000

# Matar proceso si es necesario
kill -9 [PID]
```

## Flujo de Trabajo Recomendado

### 1. Iniciar Sesión de Desarrollo
```bash
# 1. Navegar al backend
cd /Users/aldoolivas/Desktop/NGX_Ecosystem/GENESIS_oficial_BETA/backend

# 2. Activar Poetry
poetry shell

# 3. Iniciar servicios
./start-dev-services.sh

# 4. Ejecutar servidor
poetry run uvicorn app.main:app --reload
```

### 2. Ejecutar Tests
```bash
# Tests de seguridad
poetry run pytest tests/test_security_config.py -v

# Todos los tests
poetry run pytest

# Con coverage
poetry run pytest --cov=app --cov-report=html
```

### 3. Desarrollo con Aislamiento
```bash
# Siempre trabajar dentro del entorno Poetry
poetry shell

# Verificar que estás en el entorno correcto
which python  # Debe mostrar .venv/bin/python

# Instalar nuevas dependencias
poetry add nombre-paquete

# Actualizar requirements.txt (si es necesario)
poetry export -f requirements.txt --output requirements.txt
```

## Integración con IDEs

### VS Code
1. Abrir el proyecto
2. Cmd/Ctrl + Shift + P → "Python: Select Interpreter"
3. Seleccionar `.venv/bin/python`

### PyCharm
1. Settings → Project → Python Interpreter
2. Add → Existing Environment
3. Seleccionar `.venv/bin/python`

## Notas de Seguridad

1. **NUNCA** commitear archivos `.env` con credenciales reales
2. Usar `.env.example` como plantilla
3. Rotar secretos regularmente con:
   ```bash
   poetry run python scripts/rotate_secrets.py
   ```

## Próximos Pasos

1. ✅ Verificar entorno Poetry
2. ✅ Iniciar servicios Docker (Redis)
3. ⏳ Ejecutar tests de seguridad
4. ⏳ Verificar integración con Supabase
5. ⏳ Configurar monitoreo (Prometheus/Grafana)