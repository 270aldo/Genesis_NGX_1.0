# 🚀 Instrucciones para Ejecutar Migraciones en Supabase

## Estado Actual
- ✅ Conexión API de Supabase funcionando correctamente
- ✅ Credenciales configuradas en `.env`
- ❌ Tablas no creadas aún (necesitan migraciones)

## Archivos de Migración
Las migraciones SQL están en `/backend/data/sql/`:
1. `001_enhanced_core_schema.sql` - Esquema principal
2. `002_conversation_memory_system.sql` - Sistema de memoria
3. `003_agent_collaboration_system.sql` - Colaboración entre agentes
4. `004_performance_optimization_system.sql` - Optimización de rendimiento

## Opción 1: SQL Editor en Dashboard (Recomendado)

1. **Acceder al Dashboard de Supabase:**
   - Ve a: https://supabase.com/dashboard/project/wqovemdzgvofjoukhufe
   - Navega a: SQL Editor

2. **Ejecutar Migraciones en Orden:**
   - Abre cada archivo SQL en orden
   - Copia el contenido completo
   - Pégalo en el SQL Editor
   - Haz clic en "Run"
   - Verifica que no haya errores

3. **Orden de Ejecución:**
   ```
   1. 001_enhanced_core_schema.sql
   2. 002_conversation_memory_system.sql
   3. 003_agent_collaboration_system.sql
   4. 004_performance_optimization_system.sql
   ```

## Opción 2: Script Automatizado

Ejecuta el siguiente script que he preparado:

```bash
cd backend
python scripts/execute_supabase_migrations.py
```

Este script:
- Lee los archivos SQL
- Los ejecuta en orden
- Registra el progreso
- Verifica la integridad

## Verificación Post-Migración

Después de ejecutar las migraciones:

```bash
# Verificar que las tablas se crearon
python test_supabase_api.py

# Verificar el backend completo
python test_db_connection.py
```

## Tablas Esperadas

Después de las migraciones deberías tener:
- `users` - Usuarios del sistema
- `user_profiles` - Perfiles extendidos
- `agents` - Registro de agentes
- `conversation_memory` - Memoria de conversaciones
- `agent_partnerships` - Colaboraciones
- `tasks` - Tareas del sistema
- Y muchas más...

## Troubleshooting

Si encuentras errores:

1. **Error de sintaxis SQL:**
   - Verifica que Supabase use PostgreSQL 15+
   - Algunos features pueden necesitar ajustes

2. **Tablas ya existen:**
   - Las migraciones incluyen `IF NOT EXISTS`
   - Es seguro re-ejecutar

3. **Permisos insuficientes:**
   - Usa las credenciales de service_role
   - No las anon keys

## Próximos Pasos

Una vez completadas las migraciones:
1. ✅ Verificar conexión del backend
2. ✅ Iniciar el servidor FastAPI
3. ✅ Probar los endpoints
4. ✅ Verificar los agentes