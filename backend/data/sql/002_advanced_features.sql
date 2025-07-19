-- =============================================================================
-- |||       GENESIS - V2 ADVANCED FEATURES MIGRATION SCRIPT (FIXED)       ||| --
-- =============================================================================
--
--  VERSION: 2.0 FIXED
--  FECHA: 2025-07-18
--
--  DESCRIPCIÓN:
--  Este script de migración añade las tablas necesarias para las
--  funcionalidades avanzadas de la FASE 2 de GENESIS, incluyendo colaboración
--  multi-agente, memoria a largo plazo y analíticas de rendimiento.
--
--  INSTRUCCIONES:
--  Este script debe ejecutarse DESPUÉS de que la base de datos haya sido
--  configurada con 'MASTER_SETUP.sql'. Es seguro ejecutarlo múltiples veces.
--
-- =============================================================================


-- =============================================================================
-- PARTE 1: SISTEMA DE GESTIÓN DE MIGRACIONES
-- =============================================================================

CREATE TABLE IF NOT EXISTS public.migration_log (
    id SERIAL PRIMARY KEY,
    migration_name VARCHAR(255) NOT NULL UNIQUE,
    executed_at TIMESTAMPTZ DEFAULT NOW(),
    status VARCHAR(20) DEFAULT 'completed',
    checksum VARCHAR(64)
);


-- =============================================================================
-- PARTE 2: SISTEMA DE TAREAS Y COLABORACIÓN MULTI-AGENTE
-- =============================================================================

-- Crear tipos con manejo de errores
DO $$ BEGIN
    CREATE TYPE task_status AS ENUM ('pending', 'in_progress', 'completed', 'failed', 'archived');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

DO $$ BEGIN
    CREATE TYPE task_priority AS ENUM ('low', 'medium', 'high', 'critical');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

CREATE TABLE IF NOT EXISTS public.tasks (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    title TEXT NOT NULL,
    description TEXT,
    status task_status DEFAULT 'pending',
    priority task_priority DEFAULT 'medium',
    created_by_user_id UUID REFERENCES public.users(id) ON DELETE SET NULL,
    created_by_agent_id VARCHAR(100) REFERENCES public.agents(agent_id) ON DELETE SET NULL,
    assigned_to_agent_id VARCHAR(100) REFERENCES public.agents(agent_id) ON DELETE SET NULL,
    parent_task_id UUID REFERENCES public.tasks(id) ON DELETE CASCADE,
    related_session_id UUID REFERENCES public.chat_sessions(id) ON DELETE SET NULL,
    due_date TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,
    metadata JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Crear trigger solo si no existe
DO $$ BEGIN
    CREATE TRIGGER update_tasks_updated_at BEFORE UPDATE ON public.tasks FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

CREATE TABLE IF NOT EXISTS public.agent_partnerships (
    id SERIAL PRIMARY KEY,
    agent_one_id VARCHAR(100) NOT NULL REFERENCES public.agents(agent_id) ON DELETE CASCADE,
    agent_two_id VARCHAR(100) NOT NULL REFERENCES public.agents(agent_id) ON DELETE CASCADE,
    relationship_type VARCHAR(100) NOT NULL, -- e.g., 'consultant', 'supervisor', 'peer'
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (agent_one_id, agent_two_id)
);

CREATE TABLE IF NOT EXISTS public.collaboration_requests (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    requesting_agent_id VARCHAR(100) NOT NULL REFERENCES public.agents(agent_id) ON DELETE CASCADE,
    target_agent_id VARCHAR(100) NOT NULL REFERENCES public.agents(agent_id) ON DELETE CASCADE,
    task_id UUID REFERENCES public.tasks(id) ON DELETE CASCADE,
    request_details TEXT,
    status VARCHAR(20) DEFAULT 'pending' CHECK (status IN ('pending', 'accepted', 'rejected')),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);


-- =============================================================================
-- PARTE 3: MEMORIA A LARGO PLAZO Y PERSONALIDAD
-- =============================================================================

CREATE TABLE IF NOT EXISTS public.conversation_memory (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    session_id UUID NOT NULL REFERENCES public.chat_sessions(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES public.users(id) ON DELETE CASCADE,
    key_insight TEXT NOT NULL,
    relevance_score FLOAT CHECK (relevance_score >= 0 AND relevance_score <= 1),
    embedding VECTOR(1536), -- Assuming OpenAI embeddings, adjust size if needed
    source_message_id UUID REFERENCES public.chat_messages(id) ON DELETE SET NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS public.personality_profiles (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES public.users(id) ON DELETE CASCADE UNIQUE,
    learned_traits JSONB DEFAULT '{}'::jsonb, -- e.g., {'openness': 0.8, 'conscientiousness': 0.6}
    communication_summary TEXT,
    last_updated_from_session_id UUID REFERENCES public.chat_sessions(id),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Crear trigger solo si no existe
DO $$ BEGIN
    CREATE TRIGGER update_personality_profiles_updated_at BEFORE UPDATE ON public.personality_profiles FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;


-- =============================================================================
-- PARTE 4: GESTIÓN DE SESIONES Y ANALÍTICAS
-- =============================================================================

CREATE TABLE IF NOT EXISTS public.user_sessions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES public.users(id) ON DELETE CASCADE,
    device_info TEXT,
    ip_address INET,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    expires_at TIMESTAMPTZ NOT NULL
);

CREATE TABLE IF NOT EXISTS public.query_performance_metrics (
    id BIGSERIAL PRIMARY KEY,
    agent_id VARCHAR(100) REFERENCES public.agents(agent_id),
    session_id UUID REFERENCES public.chat_sessions(id),
    query_text TEXT,
    response_time_ms INT,
    was_successful BOOLEAN,
    error_details TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS public.insight_fusion_results (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES public.users(id) ON DELETE CASCADE,
    fused_insight TEXT NOT NULL,
    contributing_agents VARCHAR(100)[],
    source_data JSONB, -- References to data points used for the insight
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS public.async_task_queue (
    id BIGSERIAL PRIMARY KEY,
    task_type VARCHAR(100) NOT NULL,
    payload JSONB NOT NULL,
    status VARCHAR(20) DEFAULT 'queued' CHECK (status IN ('queued', 'processing', 'completed', 'failed')),
    priority INT DEFAULT 0,
    retry_count INT DEFAULT 0,
    error_log TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    process_after TIMESTAMPTZ DEFAULT NOW()
);


-- =============================================================================
-- PARTE 5: REGISTRO DE MIGRACIÓN
-- =============================================================================

INSERT INTO public.migration_log (migration_name, checksum) 
VALUES ('V2_ADVANCED_FEATURES', NULL)
ON CONFLICT (migration_name) DO NOTHING;


-- FIN DEL SCRIPT DE MIGRACIÓN V2
SELECT '¡ÉXITO! La migración V2 para funcionalidades avanzadas ha sido aplicada correctamente.' AS result;