-- =============================================================================
-- |||        GENESIS - PERFORMANCE OPTIMIZATION INDICES          ||| --
-- =============================================================================
--
--  VERSION: 3.0
--  FECHA: 2025-07-19
--
--  DESCRIPCIÓN:
--  Este script añade índices adicionales para optimizar el rendimiento
--  de las queries más comunes en el sistema GENESIS.
--
--  CAMBIOS:
--  - Índices compuestos para queries complejas
--  - Índices parciales para queries con filtros específicos
--  - Índices de texto completo para búsquedas
--  - Índices para operaciones JOIN frecuentes
--
-- =============================================================================

-- =============================================================================
-- PARTE 1: ÍNDICES PARA BÚSQUEDAS Y FILTROS COMUNES
-- =============================================================================

-- Índices para usuarios activos (partial index)
CREATE INDEX IF NOT EXISTS idx_users_active 
ON public.users(is_active, created_at DESC) 
WHERE is_active = true;

-- Índices compuestos para sesiones de chat
CREATE INDEX IF NOT EXISTS idx_chat_sessions_user_active 
ON public.chat_sessions(user_id, is_active, created_at DESC) 
WHERE is_active = true;

-- Índices para mensajes recientes
CREATE INDEX IF NOT EXISTS idx_chat_messages_recent 
ON public.chat_messages(session_id, created_at DESC)
WHERE created_at > (NOW() - INTERVAL '30 days');

-- Índices para búsqueda de agentes por estado
CREATE INDEX IF NOT EXISTS idx_agents_status_active 
ON public.agents(status, is_active) 
WHERE is_active = true;

-- =============================================================================
-- PARTE 2: ÍNDICES PARA MÉTRICAS Y ANÁLISIS
-- =============================================================================

-- Índices para métricas de uso
CREATE INDEX IF NOT EXISTS idx_usage_metrics_agent_date 
ON public.usage_metrics(agent_id, metric_date DESC);

CREATE INDEX IF NOT EXISTS idx_usage_metrics_user_agent_date 
ON public.usage_metrics(user_id, agent_id, metric_date DESC);

-- Índices para logs de errores recientes
CREATE INDEX IF NOT EXISTS idx_error_logs_recent 
ON public.error_logs(created_at DESC)
WHERE created_at > (NOW() - INTERVAL '7 days');

CREATE INDEX IF NOT EXISTS idx_error_logs_agent_severity 
ON public.error_logs(agent_id, severity, created_at DESC);

-- =============================================================================
-- PARTE 3: ÍNDICES DE TEXTO COMPLETO
-- =============================================================================

-- Índice de texto completo para búsqueda en mensajes de chat
CREATE INDEX IF NOT EXISTS idx_chat_messages_content_fts 
ON public.chat_messages 
USING gin(to_tsvector('spanish', content));

-- Índice de texto completo para búsqueda en feedback
CREATE INDEX IF NOT EXISTS idx_feedback_comments_fts 
ON public.feedback 
USING gin(to_tsvector('spanish', comments));

-- Índice de texto completo para búsqueda en objetivos de usuario
CREATE INDEX IF NOT EXISTS idx_user_profiles_goals_fts 
ON public.user_profiles 
USING gin(to_tsvector('spanish', goals));

-- =============================================================================
-- PARTE 4: ÍNDICES PARA JSONB
-- =============================================================================

-- Índices GIN para búsquedas en campos JSONB
CREATE INDEX IF NOT EXISTS idx_users_metadata_gin 
ON public.users 
USING gin(metadata);

CREATE INDEX IF NOT EXISTS idx_agents_capabilities_gin 
ON public.agents 
USING gin(capabilities);

CREATE INDEX IF NOT EXISTS idx_user_preferences_preferred_agents_gin 
ON public.user_preferences 
USING gin(preferred_agents);

CREATE INDEX IF NOT EXISTS idx_training_plans_exercises_gin 
ON public.training_plans 
USING gin(exercises);

CREATE INDEX IF NOT EXISTS idx_nutrition_plans_meals_gin 
ON public.nutrition_plans 
USING gin(meals);

-- =============================================================================
-- PARTE 5: ÍNDICES PARA CONSULTAS DE RANGO
-- =============================================================================

-- Índices para consultas de rango temporal
CREATE INDEX IF NOT EXISTS idx_weight_logs_user_date_range 
ON public.weight_logs(user_id, date)
WHERE date > (NOW() - INTERVAL '90 days');

CREATE INDEX IF NOT EXISTS idx_training_sessions_user_date_range 
ON public.training_sessions(user_id, session_date)
WHERE session_date > (NOW() - INTERVAL '90 days');

CREATE INDEX IF NOT EXISTS idx_nutrition_logs_user_date_range 
ON public.nutrition_logs(user_id, log_date)
WHERE log_date > (NOW() - INTERVAL '90 days');

-- =============================================================================
-- PARTE 6: ÍNDICES PARA JOINS FRECUENTES
-- =============================================================================

-- Índices para optimizar joins entre tablas relacionadas
CREATE INDEX IF NOT EXISTS idx_user_profiles_user_id 
ON public.user_profiles(user_id);

CREATE INDEX IF NOT EXISTS idx_chat_messages_agent_id 
ON public.chat_messages(agent_id);

CREATE INDEX IF NOT EXISTS idx_training_plans_user_id_active 
ON public.training_plans(user_id, is_active)
WHERE is_active = true;

CREATE INDEX IF NOT EXISTS idx_nutrition_plans_user_id_active 
ON public.nutrition_plans(user_id, is_active)
WHERE is_active = true;

-- =============================================================================
-- PARTE 7: ÍNDICES PARA QUERIES DE AGGREGACIÓN
-- =============================================================================

-- Índices para queries de aggregación comunes
CREATE INDEX IF NOT EXISTS idx_usage_metrics_aggregation 
ON public.usage_metrics(metric_date, agent_id, metric_type);

CREATE INDEX IF NOT EXISTS idx_daily_summaries_aggregation 
ON public.daily_summaries(date, user_id, summary_type);

-- =============================================================================
-- PARTE 8: ACTUALIZAR ESTADÍSTICAS
-- =============================================================================

-- Actualizar las estadísticas de las tablas para que el query planner
-- pueda tomar mejores decisiones
ANALYZE public.users;
ANALYZE public.user_profiles;
ANALYZE public.user_preferences;
ANALYZE public.agents;
ANALYZE public.chat_sessions;
ANALYZE public.chat_messages;
ANALYZE public.training_plans;
ANALYZE public.nutrition_plans;
ANALYZE public.training_sessions;
ANALYZE public.nutrition_logs;
ANALYZE public.weight_logs;
ANALYZE public.daily_summaries;
ANALYZE public.feedback;
ANALYZE public.usage_metrics;
ANALYZE public.error_logs;

-- =============================================================================
-- NOTAS DE IMPLEMENTACIÓN
-- =============================================================================
--
-- 1. Los índices parciales (WHERE clause) reducen el tamaño del índice
--    y mejoran el rendimiento para queries específicas.
--
-- 2. Los índices GIN son ideales para búsquedas en campos JSONB.
--
-- 3. Los índices de texto completo mejoran significativamente las búsquedas
--    de texto en campos grandes.
--
-- 4. Es importante ejecutar ANALYZE periódicamente para mantener las
--    estadísticas actualizadas.
--
-- 5. Monitorear el uso de índices con:
--    SELECT * FROM pg_stat_user_indexes WHERE schemaname = 'public';
--
-- =============================================================================