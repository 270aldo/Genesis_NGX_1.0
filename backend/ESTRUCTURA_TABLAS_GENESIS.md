# Estructura de Tablas para GENESIS

## Tablas Principales Necesarias

### 1. users
- id: UUID (primary key)
- email: TEXT (unique, nullable)
- api_key: TEXT (unique, not null)
- created_at: TIMESTAMPTZ
- updated_at: TIMESTAMPTZ
- last_seen: TIMESTAMPTZ
- is_active: BOOLEAN (default true)
- metadata: JSONB

### 2. user_profiles
- id: UUID (primary key)
- user_id: UUID (foreign key to users)
- name: VARCHAR(255)
- age: INTEGER (check between 1-150)
- gender: VARCHAR(20)
- weight_kg: DECIMAL(5,2)
- height_cm: DECIMAL(5,2)
- activity_level: VARCHAR(50)
- goals: TEXT[]
- medical_conditions: TEXT[]
- allergies: TEXT[]
- dietary_restrictions: TEXT[]
- experience_level: VARCHAR(50)
- timezone: VARCHAR(50)
- locale: VARCHAR(10)
- created_at: TIMESTAMPTZ
- updated_at: TIMESTAMPTZ

### 3. user_preferences
- id: UUID (primary key)
- user_id: UUID (foreign key to users)
- preferred_agents: JSONB
- communication_style: VARCHAR(50)
- response_length: VARCHAR(20)
- personality_mode: VARCHAR(20)
- notification_settings: JSONB
- privacy_settings: JSONB
- created_at: TIMESTAMPTZ
- updated_at: TIMESTAMPTZ

### 4. agents
- id: UUID (primary key)
- agent_id: VARCHAR(100) (unique)
- name: VARCHAR(255)
- description: TEXT
- version: VARCHAR(20)
- agent_type: VARCHAR(20)
- capabilities: JSONB
- skills: JSONB
- voice_id: VARCHAR(100)
- personality_traits: JSONB
- is_active: BOOLEAN
- created_at: TIMESTAMPTZ
- updated_at: TIMESTAMPTZ

### 5. chat_sessions
- id: UUID (primary key)
- user_id: UUID (foreign key to users)
- agent_id: VARCHAR(100)
- title: VARCHAR(255)
- context: JSONB
- is_active: BOOLEAN
- created_at: TIMESTAMPTZ
- updated_at: TIMESTAMPTZ

### 6. chat_messages
- id: UUID (primary key)
- session_id: UUID (foreign key to chat_sessions)
- role: VARCHAR(20) (user/assistant/system)
- content: TEXT
- metadata: JSONB
- created_at: TIMESTAMPTZ

### 7. training_plans
- id: UUID (primary key)
- user_id: UUID (foreign key to users)
- name: VARCHAR(255)
- plan_data: JSONB
- is_active: BOOLEAN
- created_at: TIMESTAMPTZ
- updated_at: TIMESTAMPTZ

## Datos de los Agentes

Los 11 agentes que necesitas insertar:

1. **NEXUS** (nexus_central_command) - Orchestrator - Voice: EkK5I93UQWFDigLMpZcX
2. **BLAZE** (blaze_elite_performance) - Elite Training - Voice: iP95p4xoKVk53GoZ742B
3. **SAGE** (sage_nutritional_wisdom) - Nutrition - Voice: 5l5f8iK3YPeGga21rQIX
4. **CODE** (code_genetic_optimization) - Genetics - Voice: 1SM7GgM6IMuvQlz2BwM3
5. **WAVE** (wave_quantum_analytics) - Analytics - Voice: SOYHLrjzK2X1ezoPC6cr
6. **LUNA** (luna_female_specialist) - Female Wellness - Voice: kdmDKE6EkgrWrrykO9Qt
7. **STELLA** (stella_progress_tracker) - Progress - Voice: BZgkqPqms7Kj9ulSkVzn
8. **SPARK** (spark_motivation_coach) - Motivation - Voice: scOwDtmlUjD3prqpp97I
9. **NOVA** (nova_biohacking_expert) - Biohacking - Voice: aMSt68OGf4xUZAnLpTU8
10. **GUARDIAN** (guardian_security) - Security - Sin voice
11. **NODE** (node_integration) - Integration - Sin voice

## Funcionalidad Requerida

1. **Triggers**: Todas las tablas con updated_at necesitan un trigger que actualice ese campo automáticamente
2. **Índices**: Crear índices en api_key, email, y foreign keys
3. **RLS**: Si usas Supabase, habilitar Row Level Security con políticas permisivas para desarrollo

## Extensiones PostgreSQL Necesarias
- uuid-ossp (para generar UUIDs)
- pg_trgm (para búsquedas de texto)
- pgcrypto (para encriptación)

## Notas Importantes
- Todas las tablas usan UUID como primary key
- Los timestamps son TIMESTAMPTZ (con timezone)
- Las relaciones tienen ON DELETE CASCADE
- Los campos JSONB tienen default '{}'::jsonb o '[]'::jsonb según el caso