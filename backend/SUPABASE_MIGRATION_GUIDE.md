# 🚀 Guía de Migración Supabase - GENESIS

## 📋 Pasos para Completar la Configuración

### 1. **Acceder al Dashboard de Supabase**

1. Ve a [https://supabase.com/dashboard](https://supabase.com/dashboard)
2. Selecciona tu proyecto: `wqovemdzgvofjoukhufe`
3. Ve a **SQL Editor** en el menú lateral

### 2. **Ejecutar Migración Principal (MASTER_SETUP)**

1. En el SQL Editor, crea una nueva consulta
2. Copia **TODO** el contenido del archivo: `/backend/data/sql/001_master_setup.sql`
3. Pega el contenido completo en el editor
4. Haz clic en **"RUN"**
5. Deberías ver el mensaje: `¡ÉXITO! La base de datos de GENESIS ha sido configurada correctamente.`

**⚠️ IMPORTANTE**: Este script limpia y recrea el esquema completo. Es seguro ejecutarlo.

### 3. **Ejecutar Migración de Funcionalidades Avanzadas**

1. Crea otra nueva consulta en el SQL Editor
2. Copia **TODO** el contenido del archivo: `/backend/data/sql/002_advanced_features.sql`
3. Pega el contenido completo en el editor
4. Haz clic en **"RUN"**
5. Deberías ver el mensaje: `¡ÉXITO! La migración V2 para funcionalidades avanzadas ha sido aplicada.`

### 4. **Configurar Acceso de Red (Opcional)**

Si necesitas conexión directa PostgreSQL:

1. En Supabase Dashboard, ve a **Settings** > **Database**
2. Busca la sección **Network Restrictions**
3. Agrega tu IP actual a la whitelist
4. Guarda los cambios

### 5. **Validar la Configuración**

Ejecuta el script de validación desde tu terminal:

```bash
cd backend
python scripts/validate_supabase_setup.py
```

Esto verificará:
- ✅ Todas las tablas existen
- ✅ Políticas RLS están activas
- ✅ Datos de agentes fueron insertados
- ✅ Cliente Supabase funciona correctamente

### 6. **Test de Conexión Final**

```bash
python scripts/test_supabase_connection.py
```

Ahora deberías ver:
- ✅ Supabase Client: OK
- ✅ Direct PostgreSQL: OK (si configuraste la IP)
- ✅ Todas las tablas listadas
- ✅ Sin errores de permisos

## 🎯 Resultados Esperados

Después de completar estos pasos:

### Tablas Creadas (25 total):
- **Core**: `users`, `user_profiles`, `user_preferences`, `agents`, `chat_sessions`, `chat_messages`
- **Logging**: `weight_logs`, `body_composition_logs`, `performance_logs`, `nutrition_logs`
- **Planning**: `meal_plans`, `training_plans`
- **Feedback**: `feedback`, `biomarker_records`
- **Wearables**: `user_device_connections`, `daily_summaries`
- **Advanced**: `tasks`, `agent_partnerships`, `collaboration_requests`, `conversation_memory`
- **Analytics**: `personality_profiles`, `user_sessions`, `query_performance_metrics`
- **System**: `migration_log`, `insight_fusion_results`, `async_task_queue`

### Políticas RLS Activas:
- 🔒 Usuarios solo pueden acceder a sus propios datos
- 🔒 Agentes son visibles para usuarios autenticados
- 🔒 Mensajes de chat protegidos por sesión
- 🔒 Todas las tablas con datos sensibles protegidas

### Agentes Seed Data:
- **NEXUS** - Orquestador central
- **BLAZE** - Entrenamiento élite
- **SAGE** - Nutrición de precisión
- **CODE** - Análisis genético
- **WAVE** - Analytics biométricos
- **LUNA** - Especialista femenina
- **STELLA** - Seguimiento de progreso
- **SPARK** - Coach de motivación
- **NOVA** - Experto en biohacking
- **GUARDIAN** - Seguridad y compliance
- **NODE** - Integración de sistemas

## 🔧 Solución de Problemas

### Error: "permission denied for table"
- **Causa**: RLS no está configurado correctamente
- **Solución**: Verificar que la primera migración se ejecutó completamente

### Error: "relation does not exist"
- **Causa**: Tablas no fueron creadas
- **Solución**: Re-ejecutar la migración principal

### Error: "connection refused"
- **Causa**: IP no está en whitelist
- **Solución**: Agregar IP en Settings > Database > Network Restrictions

### Script de validación falla
- **Causa**: Migraciones incompletas
- **Solución**: Re-ejecutar migraciones en orden

## ✅ Estado Final

Una vez completado, tendrás:

- 🎯 **Base de datos 100% configurada**
- 🔒 **Seguridad RLS activa**
- 🤖 **11 agentes registrados**
- 📊 **25 tablas funcionales**
- 🔗 **Conectividad completa**
- 🚀 **Listo para producción**

---

**¿Necesitas ayuda?** Ejecuta `python scripts/validate_supabase_setup.py` para diagnósticos automáticos.