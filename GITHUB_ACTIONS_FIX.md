# 🔧 Solución de Problemas de GitHub Actions

## 📋 Estado Actual

Basado en el análisis de los workflows fallidos:

### Problemas Identificados:
1. **test: Actualizar tests para compatibilidad con ADK** - Falla
2. **test: Major Phase 3 optimizations - ADK, Feature Flags, Performance** - Falla
3. **docs: Actualizar documentación con estado del proyecto post-configura...** - Falla
4. **feat: Preparar SDK para publicación en npm** - Falla
5. **test: Verificar GitHub Actions CI/CD** - Falla

## 🚀 Plan de Acción

### Paso 1: Verificar Tests Localmente

```bash
# Backend
cd backend
poetry install --with dev
make test

# Frontend
cd ../frontend
npm install
npm test
```

### Paso 2: Configurar Secretos en GitHub

Necesitas configurar estos secretos en tu repositorio:
1. Ve a: https://github.com/270aldo/Genesis_NGX_1.0/settings/secrets/actions
2. Agrega los siguientes secretos:

```
SUPABASE_URL
SUPABASE_KEY
VERTEX_AI_PROJECT_ID
VERTEX_AI_LOCATION
GOOGLE_APPLICATION_CREDENTIALS
REDIS_URL
JWT_SECRET_KEY
ELEVENLABS_API_KEY
```

### Paso 3: Crear archivo .env.test para CI/CD

```bash
cd backend
cat > .env.test << EOF
ENVIRONMENT=test
REDIS_URL=redis://localhost:6379
SUPABASE_URL=https://test.supabase.co
SUPABASE_KEY=test-key
VERTEX_AI_PROJECT_ID=test-project
VERTEX_AI_LOCATION=us-central1
EOF
```

### Paso 4: Actualizar workflow para usar secretos

Modificar `.github/workflows/ci.yml` para incluir las variables de entorno:

```yaml
env:
  SUPABASE_URL: ${{ secrets.SUPABASE_URL }}
  SUPABASE_KEY: ${{ secrets.SUPABASE_KEY }}
  VERTEX_AI_PROJECT_ID: ${{ secrets.VERTEX_AI_PROJECT_ID }}
  VERTEX_AI_LOCATION: ${{ secrets.VERTEX_AI_LOCATION }}
  JWT_SECRET_KEY: ${{ secrets.JWT_SECRET_KEY }}
```

### Paso 5: Corregir problemas específicos

1. **ADK Compatibility**: Verificar que todos los agentes estén usando el nuevo ADK
2. **Feature Flags**: Asegurar que el sistema de feature flags esté configurado
3. **SDK para npm**: Verificar la estructura del SDK en `sdk/` o `packages/`

## 📊 Monitoreo

Una vez aplicados los cambios:
1. Hacer push de los cambios
2. Monitorear los workflows en: https://github.com/270aldo/Genesis_NGX_1.0/actions
3. Revisar logs detallados de cada job fallido

## 🔍 Debugging Tips

Si un workflow sigue fallando:
1. Revisa los logs completos del job
2. Ejecuta el mismo comando localmente
3. Verifica que todas las dependencias estén instaladas
4. Asegúrate de que los paths sean correctos