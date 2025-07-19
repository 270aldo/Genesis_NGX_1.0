-- =============================================================================
-- |||           GENESIS - MASTER DATABASE SETUP SCRIPT          ||| --
-- =============================================================================
--
--  VERSION: 1.0
--  FECHA: 2025-07-18
--
--  DESCRIPCIÓN:
--  Este es el script maestro y definitivo para configurar la base de datos
--  del proyecto GENESIS desde cero. Combina el esquema base, las tablas
--  adicionales, los datos iniciales (seed) y las políticas de seguridad (RLS)
--  en un único archivo ejecutable.
--
--  INSTRUCCIONES:
--  1. Ve al "SQL Editor" en tu proyecto de Supabase.
--  2. Copia y pega el contenido COMPLETO de este archivo.
--  3. Haz clic en "RUN".
--
--  Este script es idempotente, lo que significa que se puede ejecutar
--  múltiples veces sin causar errores. Limpiará la base de datos
--  existente y la recreará con la estructura correcta y segura.
--
-- =============================================================================



-- =============================================================================
-- PARTE 1: CONFIGURACIÓN INICIAL Y ESQUEMA BASE
-- (Basado en CLEAN_GENESIS_SETUP.sql)
-- =============================================================================

-- 1.1. LIMPIEZA DEL ESQUEMA
-- -----------------------------------------------------------------------------
DROP SCHEMA IF EXISTS public CASCADE;
CREATE SCHEMA public;
GRANT ALL ON SCHEMA public TO postgres;
GRANT ALL ON SCHEMA public TO public;

-- 1.2. HABILITACIÓN DE EXTENSIONES
-- -----------------------------------------------------------------------------
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- 1.3. FUNCIÓN PARA ACTUALIZAR TIMESTAMPS
-- -----------------------------------------------------------------------------
CREATE OR REPLACE FUNCTION public.update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- 1.4. TABLAS CENTRALES (Users, Profiles, Preferences, Agents, Chat)
-- -----------------------------------------------------------------------------

CREATE TABLE public.users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email TEXT UNIQUE NOT NULL CHECK (email ~* '^[A-Za-z0-9._+%-]+@[A-Za-z0-9.-]+[.][A-Za-z]+$'),
    api_key TEXT UNIQUE NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    last_seen TIMESTAMPTZ,
    is_active BOOLEAN NOT NULL DEFAULT true,
    metadata JSONB DEFAULT '{}'::jsonb
);

CREATE TABLE public.user_profiles (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES public.users(id) ON DELETE CASCADE UNIQUE,
    name VARCHAR(255),
    age INTEGER CHECK (age > 0 AND age < 150),
    goals TEXT,
    experience_level VARCHAR(50) CHECK (experience_level IN ('beginner', 'intermediate', 'advanced', 'expert')),
    timezone VARCHAR(50) DEFAULT 'UTC',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE public.user_preferences (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES public.users(id) ON DELETE CASCADE UNIQUE,
    preferred_agents JSONB DEFAULT '[]'::jsonb,
    communication_style VARCHAR(50) DEFAULT 'balanced',
    notification_settings JSONB DEFAULT '{"email": true, "push": true, "sms": false}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE public.agents (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    agent_id VARCHAR(100) NOT NULL UNIQUE,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    version VARCHAR(20) DEFAULT '1.0.0',
    capabilities JSONB DEFAULT '[]'::jsonb,
    status VARCHAR(20) DEFAULT 'online' CHECK (status IN ('online', 'offline', 'maintenance')),
    voice_id VARCHAR(100),
    is_active BOOLEAN NOT NULL DEFAULT true,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE public.chat_sessions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES public.users(id) ON DELETE CASCADE,
    agent_id VARCHAR(100) REFERENCES public.agents(agent_id),
    title VARCHAR(255),
    context JSONB DEFAULT '{}'::jsonb,
    is_active BOOLEAN NOT NULL DEFAULT true,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE public.chat_messages (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    session_id UUID NOT NULL REFERENCES public.chat_sessions(id) ON DELETE CASCADE,
    role VARCHAR(20) NOT NULL CHECK (role IN ('user', 'assistant', 'system')),
    content TEXT NOT NULL,
    metadata JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);


-- =============================================================================
-- PARTE 2: TABLAS ADICIONALES DETALLADAS
-- (Basado en 007_missing_tables.sql)
-- =============================================================================

-- 2.1. TABLAS DE LOGGING (Weight, Body Composition, Performance, Nutrition)
-- -----------------------------------------------------------------------------

CREATE TABLE public.weight_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    weight DECIMAL(5,2) NOT NULL, 
    unit VARCHAR(10) DEFAULT 'kg',
    date DATE NOT NULL DEFAULT CURRENT_DATE,
    CONSTRAINT unique_weight_log_per_day UNIQUE (user_id, date)
);

CREATE TABLE public.body_composition_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    date DATE NOT NULL DEFAULT CURRENT_DATE,
    body_fat_percentage DECIMAL(4,2),
    muscle_mass_kg DECIMAL(5,2),
    CONSTRAINT unique_composition_per_day UNIQUE (user_id, date)
);

CREATE TABLE public.performance_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    date DATE NOT NULL DEFAULT CURRENT_DATE,
    exercise_name VARCHAR(255) NOT NULL,
    sets INTEGER, 
    reps INTEGER[], 
    weight DECIMAL[]
);

CREATE TABLE public.nutrition_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    date DATE NOT NULL DEFAULT CURRENT_DATE,
    meal_type VARCHAR(50),
    foods JSONB NOT NULL DEFAULT '[]',
    total_calories DECIMAL(7,2)
);

-- 2.2. TABLAS DE PLANIFICACIÓN (Meal Plans, Training Plans)
-- -----------------------------------------------------------------------------

CREATE TABLE public.meal_plans (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    meals JSONB NOT NULL DEFAULT '[]'
);

-- Re-definición de training_plans para consistencia
DROP TABLE IF EXISTS public.training_plans CASCADE;
CREATE TABLE public.training_plans (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES public.users(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    plan_data JSONB NOT NULL DEFAULT '{}'::jsonb,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 2.3. TABLAS DE FEEDBACK Y BIOMÉTRICAS
-- -----------------------------------------------------------------------------

CREATE TYPE public.feedback_type AS ENUM ('thumbs_up', 'thumbs_down', 'rating', 'comment', 'issue', 'suggestion');
CREATE TYPE public.feedback_category AS ENUM ('accuracy', 'relevance', 'completeness', 'speed', 'helpfulness', 'user_experience', 'technical_issue', 'other');

CREATE TABLE public.feedback (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES public.users(id) ON DELETE CASCADE,
    session_id UUID NOT NULL REFERENCES public.chat_sessions(id) ON DELETE CASCADE,
    message_id UUID REFERENCES public.chat_messages(id) ON DELETE SET NULL,
    feedback_type public.feedback_type NOT NULL,
    rating INT CHECK (rating >= 1 AND rating <= 5),
    comment TEXT,
    categories public.feedback_category[],
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE public.biomarker_records (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    date DATE NOT NULL DEFAULT CURRENT_DATE,
    biomarker_type VARCHAR(100) NOT NULL,
    value DECIMAL(10,4) NOT NULL,
    unit VARCHAR(50) NOT NULL
);

-- 2.4. TABLAS DE WEARABLES
-- -----------------------------------------------------------------------------

CREATE TYPE public.wearable_device_type AS ENUM ('whoop', 'apple_watch', 'oura_ring', 'garmin', 'cgm');

CREATE TABLE public.user_device_connections (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES public.users(id) ON DELETE CASCADE,
    device_type public.wearable_device_type NOT NULL,
    is_active BOOLEAN NOT NULL DEFAULT true,
    last_sync TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (user_id, device_type)
);

CREATE TABLE public.daily_summaries (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES public.users(id) ON DELETE CASCADE,
    date DATE NOT NULL,
    recovery_score INT,
    sleep_score INT,
    strain_score FLOAT,
    summary_data JSONB NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (user_id, date)
);


-- =============================================================================
-- PARTE 3: TRIGGERS, ÍNDICES Y DATOS INICIALES (SEED)
-- =============================================================================

-- 3.1. TRIGGERS PARA 'updated_at'
-- -----------------------------------------------------------------------------
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON public.users FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();
CREATE TRIGGER update_user_profiles_updated_at BEFORE UPDATE ON public.user_profiles FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();
CREATE TRIGGER update_user_preferences_updated_at BEFORE UPDATE ON public.user_preferences FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();
CREATE TRIGGER update_agents_updated_at BEFORE UPDATE ON public.agents FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();
CREATE TRIGGER update_chat_sessions_updated_at BEFORE UPDATE ON public.chat_sessions FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();
CREATE TRIGGER update_training_plans_updated_at BEFORE UPDATE ON public.training_plans FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();
CREATE TRIGGER update_user_device_connections_updated_at BEFORE UPDATE ON public.user_device_connections FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();
CREATE TRIGGER update_daily_summaries_updated_at BEFORE UPDATE ON public.daily_summaries FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();

-- 3.2. ÍNDICES PARA MEJORAR RENDIMIENTO
-- -----------------------------------------------------------------------------
CREATE INDEX idx_users_api_key ON public.users(api_key);
CREATE INDEX idx_chat_sessions_user_id ON public.chat_sessions(user_id);
CREATE INDEX idx_chat_messages_session_id ON public.chat_messages(session_id);
CREATE INDEX idx_feedback_user_session ON public.feedback(user_id, session_id);
CREATE INDEX idx_daily_summaries_user_date ON public.daily_summaries(user_id, date DESC);
CREATE INDEX idx_weight_logs_user_date ON public.weight_logs(user_id, date DESC);

-- 3.3. INSERCIÓN DE AGENTES (SEED DATA)
-- -----------------------------------------------------------------------------
INSERT INTO public.agents (agent_id, name, description, voice_id, status, is_active)
VALUES
    ('nexus_central_command', 'NEXUS', 'Orquestador central y punto de entrada principal.', 'EkK5I93UQWFDigLMpZcX', 'online', true),
    ('blaze_elite_performance', 'BLAZE', 'Especialista en entrenamiento de élite y rendimiento físico.', 'iP95p4xoKVk53GoZ742B', 'online', true),
    ('sage_nutritional_wisdom', 'SAGE', 'Experto en nutrición de precisión y planes alimenticios.', '5l5f8iK3YPeGga21rQIX', 'online', true),
    ('code_genetic_optimization', 'CODE', 'Analista de datos genéticos para optimización del rendimiento.', '1SM7GgM6IMuvQlz2BwM3', 'online', true),
    ('wave_quantum_analytics', 'WAVE', 'Analista de datos biométricos y patrones de recuperación.', 'SOYHLrjzK2X1ezoPC6cr', 'online', true),
    ('luna_female_specialist', 'LUNA', 'Especialista en bienestar y salud femenina.', 'kdmDKE6EkgrWrrykO9Qt', 'online', true),
    ('stella_progress_tracker', 'STELLA', 'Monitor de progreso y seguimiento de objetivos a largo plazo.', 'BZgkqPqms7Kj9ulSkVzn', 'online', true),
    ('spark_motivation_coach', 'SPARK', 'Coach de motivación, comportamiento y establecimiento de hábitos.', 'scOwDtmlUjD3prqpp97I', 'online', true),
    ('nova_biohacking_expert', 'NOVA', 'Experto en biohacking, innovación y técnicas de vanguardia.', 'aMSt68OGf4xUZAnLpTU8', 'online', true),
    ('guardian_security', 'GUARDIAN', 'Agente de seguridad, compliance y anonimización de datos.', NULL, 'online', true),
    ('node_integration', 'NODE', 'Especialista en integración de sistemas y APIs externas.', NULL, 'online', true)
ON CONFLICT (agent_id) DO NOTHING;


-- =============================================================================
-- PARTE 4: POLÍTICAS DE SEGURIDAD (ROW-LEVEL SECURITY)
-- ¡¡¡CRÍTICO PARA PRODUCCIÓN!!!
-- =============================================================================

-- 4.1. HABILITAR RLS EN TODAS LAS TABLAS NECESARIAS
-- -----------------------------------------------------------------------------
ALTER TABLE public.user_profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.user_preferences ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.chat_sessions ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.chat_messages ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.feedback ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.user_device_connections ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.daily_summaries ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.weight_logs ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.body_composition_logs ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.performance_logs ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.nutrition_logs ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.meal_plans ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.training_plans ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.biomarker_records ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.agents ENABLE ROW LEVEL SECURITY;

-- 4.2. DEFINIR POLÍTICAS DE ACCESO
-- -----------------------------------------------------------------------------

-- Los usuarios solo pueden manejar sus propios datos.
CREATE POLICY "Users can manage their own profiles" ON public.user_profiles FOR ALL USING (auth.uid() = user_id);
CREATE POLICY "Users can manage their own preferences" ON public.user_preferences FOR ALL USING (auth.uid() = user_id);
CREATE POLICY "Users can manage their own chat sessions" ON public.chat_sessions FOR ALL USING (auth.uid() = user_id);
CREATE POLICY "Users can manage their own feedback" ON public.feedback FOR ALL USING (auth.uid() = user_id);
CREATE POLICY "Users can manage their own device connections" ON public.user_device_connections FOR ALL USING (auth.uid() = user_id);
CREATE POLICY "Users can manage their own daily summaries" ON public.daily_summaries FOR ALL USING (auth.uid() = user_id);
CREATE POLICY "Users can manage their own weight logs" ON public.weight_logs FOR ALL USING (auth.uid() = user_id);
CREATE POLICY "Users can manage their own body composition" ON public.body_composition_logs FOR ALL USING (auth.uid() = user_id);
CREATE POLICY "Users can manage their own performance logs" ON public.performance_logs FOR ALL USING (auth.uid() = user_id);
CREATE POLICY "Users can manage their own nutrition logs" ON public.nutrition_logs FOR ALL USING (auth.uid() = user_id);
CREATE POLICY "Users can manage their own meal plans" ON public.meal_plans FOR ALL USING (auth.uid() = user_id);
CREATE POLICY "Users can manage their own training plans" ON public.training_plans FOR ALL USING (auth.uid() = user_id);
CREATE POLICY "Users can manage their own biomarker records" ON public.biomarker_records FOR ALL USING (auth.uid() = user_id);

-- Políticas más complejas para mensajes de chat.
CREATE POLICY "Users can view messages in their own sessions" ON public.chat_messages FOR SELECT USING ((SELECT user_id FROM public.chat_sessions WHERE id = session_id) = auth.uid());
CREATE POLICY "Users can insert messages in their own sessions" ON public.chat_messages FOR INSERT WITH CHECK ((SELECT user_id FROM public.chat_sessions WHERE id = session_id) = auth.uid());

-- La tabla de agentes es de solo lectura para cualquier usuario autenticado.
CREATE POLICY "Authenticated users can view all agents" ON public.agents FOR SELECT TO authenticated USING (true);


-- =============================================================================
-- FIN DEL SCRIPT MAESTRO
-- =============================================================================
SELECT '¡ÉXITO! La base de datos de GENESIS ha sido configurada correctamente.' AS result;
