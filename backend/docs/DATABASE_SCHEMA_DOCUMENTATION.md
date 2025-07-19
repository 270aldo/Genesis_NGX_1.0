# NGX Agents Database Schema Documentation

## Overview

This document provides comprehensive documentation for the NGX Agents database schema, including all tables, relationships, indexes, and business logic implemented in FASE 12 (Enhanced Intelligence & Optimization).

## 📋 Table of Contents

1. [Core System Tables](#core-system-tables)
2. [Conversation Memory System](#conversation-memory-system)
3. [Agent Collaboration System](#agent-collaboration-system)
4. [Performance Optimization System](#performance-optimization-system)
5. [Relationships and Foreign Keys](#relationships-and-foreign-keys)
6. [Indexes and Performance](#indexes-and-performance)
7. [Views and Computed Data](#views-and-computed-data)
8. [Triggers and Business Logic](#triggers-and-business-logic)
9. [Migration Information](#migration-information)

## Core System Tables

### 1. users
**Purpose**: Core user authentication and identification (existing table)
```sql
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email TEXT UNIQUE,
    api_key TEXT UNIQUE NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);
```

### 2. user_profiles
**Purpose**: Extended user profile information for personalized health and fitness guidance
```sql
CREATE TABLE user_profiles (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    name VARCHAR(255),
    age INTEGER CHECK (age > 0 AND age < 150),
    weight VARCHAR(50), -- Support for "70kg", "155lbs", etc.
    height VARCHAR(50), -- Support for "175cm", "5'9\"", etc.
    goals TEXT,
    experience_level VARCHAR(50) CHECK (experience_level IN ('beginner', 'intermediate', 'advanced', 'expert')),
    dietary_restrictions TEXT,
    allergies TEXT,
    limitations TEXT,
    timezone VARCHAR(50) DEFAULT 'UTC',
    locale VARCHAR(10) DEFAULT 'en-US',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);
```

### 3. user_preferences
**Purpose**: User preferences for agent interactions and communication styles
```sql
CREATE TABLE user_preferences (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    preferred_agents JSONB DEFAULT '[]',
    communication_style VARCHAR(50) DEFAULT 'balanced',
    response_length VARCHAR(20) DEFAULT 'medium',
    interaction_frequency VARCHAR(20) DEFAULT 'normal',
    privacy_level VARCHAR(20) DEFAULT 'standard',
    notification_settings JSONB DEFAULT '{"email": true, "push": true, "sms": false}',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);
```

### 4. agents
**Purpose**: Registry of all available agents in the NGX system with capabilities and status
```sql
CREATE TABLE agents (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    agent_id VARCHAR(100) NOT NULL UNIQUE,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    version VARCHAR(20) DEFAULT '1.0.0',
    capabilities JSONB DEFAULT '[]',
    skills JSONB DEFAULT '[]',
    status VARCHAR(20) DEFAULT 'online',
    agent_type VARCHAR(20) DEFAULT 'local',
    endpoint_url TEXT,
    health_check_url TEXT,
    last_seen TIMESTAMPTZ DEFAULT NOW(),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    -- Performance tracking
    total_interactions BIGINT DEFAULT 0,
    successful_interactions BIGINT DEFAULT 0,
    average_response_time DECIMAL(10,3) DEFAULT 0.0,
    -- Configuration
    max_concurrent_requests INTEGER DEFAULT 10,
    timeout_seconds INTEGER DEFAULT 30,
    retry_count INTEGER DEFAULT 3
);
```

### 5. tasks
**Purpose**: Task execution tracking with multi-agent collaboration support
```sql
CREATE TABLE tasks (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    task_id VARCHAR(100) NOT NULL UNIQUE,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    task_type VARCHAR(50) NOT NULL,
    status VARCHAR(20) DEFAULT 'pending',
    priority VARCHAR(10) DEFAULT 'normal',
    input_data JSONB NOT NULL DEFAULT '{}',
    output_data JSONB,
    error_details JSONB,
    primary_agent_id VARCHAR(100),
    collaborating_agents JSONB DEFAULT '[]',
    agent_assignments JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    started_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,
    timeout_at TIMESTAMPTZ,
    execution_time_seconds DECIMAL(10,3),
    estimated_duration_seconds DECIMAL(10,3),
    complexity_score DECIMAL(3,2),
    session_id VARCHAR(100),
    client_info JSONB DEFAULT '{}',
    tags JSONB DEFAULT '[]'
);
```

## Conversation Memory System

### 6. conversation_memory
**Purpose**: Enhanced conversation memory storage with importance scoring and context tracking
```sql
CREATE TABLE conversation_memory (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    agent_id VARCHAR(100) NOT NULL,
    session_id VARCHAR(100),
    content TEXT NOT NULL,
    context VARCHAR(50) NOT NULL,
    emotional_state VARCHAR(20),
    importance_score DECIMAL(3,2) NOT NULL DEFAULT 0.5,
    relevance_score DECIMAL(3,2) DEFAULT 0.5,
    metadata JSONB DEFAULT '{}',
    tags JSONB DEFAULT '[]',
    timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    retention_priority VARCHAR(10) DEFAULT 'normal',
    expires_at TIMESTAMPTZ,
    is_archived BOOLEAN DEFAULT false,
    parent_memory_id UUID REFERENCES conversation_memory(id) ON DELETE SET NULL,
    related_task_id UUID REFERENCES tasks(id) ON DELETE SET NULL
);
```

### 7. user_sessions
**Purpose**: Cross-device session management with sync support and context tracking
```sql
CREATE TABLE user_sessions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    session_id VARCHAR(100) NOT NULL UNIQUE,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    device_id VARCHAR(100) NOT NULL,
    device_type VARCHAR(20) NOT NULL,
    device_info JSONB DEFAULT '{}',
    status VARCHAR(20) DEFAULT 'active',
    sync_token VARCHAR(100) NOT NULL UNIQUE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    last_activity TIMESTAMPTZ DEFAULT NOW(),
    expires_at TIMESTAMPTZ,
    total_interactions INTEGER DEFAULT 0,
    total_duration_seconds INTEGER DEFAULT 0,
    current_topic VARCHAR(50),
    active_agent_id VARCHAR(100),
    conversation_flow JSONB DEFAULT '[]',
    user_goals JSONB DEFAULT '[]',
    last_emotional_state VARCHAR(20),
    session_metadata JSONB DEFAULT '{}',
    ip_address INET,
    timezone VARCHAR(50) DEFAULT 'UTC'
);
```

### 8. personality_profiles
**Purpose**: Learned personality profiles from user interactions with confidence scoring
```sql
CREATE TABLE personality_profiles (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    communication_style JSONB NOT NULL DEFAULT '{}',
    preferred_topics JSONB DEFAULT '[]',
    response_patterns JSONB DEFAULT '{}',
    motivation_triggers JSONB DEFAULT '[]',
    learning_preferences JSONB DEFAULT '{}',
    goal_orientation JSONB DEFAULT '{}',
    confidence_score DECIMAL(3,2) NOT NULL DEFAULT 0.0,
    sample_size INTEGER DEFAULT 0,
    last_updated TIMESTAMPTZ DEFAULT NOW(),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    version INTEGER DEFAULT 1,
    is_active BOOLEAN DEFAULT true
);
```

## Agent Collaboration System

### 9. agent_partnerships
**Purpose**: Strategic partnerships between complementary agents for enhanced collaboration
```sql
CREATE TABLE agent_partnerships (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    partnership_id VARCHAR(100) NOT NULL UNIQUE,
    primary_agent_id VARCHAR(100) NOT NULL,
    secondary_agent_id VARCHAR(100) NOT NULL,
    partnership_type VARCHAR(30) NOT NULL,
    name VARCHAR(255) NOT NULL,
    description TEXT NOT NULL,
    collaboration_focus JSONB NOT NULL DEFAULT '[]',
    total_collaborations INTEGER DEFAULT 0,
    successful_collaborations INTEGER DEFAULT 0,
    average_user_satisfaction DECIMAL(3,2) DEFAULT 0.0,
    effectiveness_score DECIMAL(3,2) DEFAULT 0.5,
    is_active BOOLEAN DEFAULT true,
    auto_trigger_conditions JSONB DEFAULT '{}',
    max_concurrent_collaborations INTEGER DEFAULT 5,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);
```

### 10. collaboration_requests
**Purpose**: Requests for collaboration between agents with status tracking and results
```sql
CREATE TABLE collaboration_requests (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    request_id VARCHAR(100) NOT NULL UNIQUE,
    requesting_agent_id VARCHAR(100) NOT NULL,
    target_agents JSONB NOT NULL DEFAULT '[]',
    collaboration_type VARCHAR(30) NOT NULL,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    session_id VARCHAR(100) REFERENCES user_sessions(session_id) ON DELETE SET NULL,
    task_id UUID REFERENCES tasks(id) ON DELETE SET NULL,
    context_data JSONB NOT NULL DEFAULT '{}',
    priority VARCHAR(10) NOT NULL DEFAULT 'medium',
    expected_outcome TEXT NOT NULL,
    deadline TIMESTAMPTZ,
    status VARCHAR(20) DEFAULT 'pending',
    participating_agents JSONB DEFAULT '[]',
    collaboration_result JSONB DEFAULT '{}',
    user_feedback_rating INTEGER,
    user_feedback_text TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    accepted_at TIMESTAMPTZ,
    started_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,
    request_metadata JSONB DEFAULT '{}'
);
```

### 11. insight_fusion_results
**Purpose**: Results of multi-agent insight fusion with quality metrics
```sql
CREATE TABLE insight_fusion_results (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    fusion_id VARCHAR(100) NOT NULL UNIQUE,
    collaboration_request_id UUID REFERENCES collaboration_requests(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    participating_agents JSONB NOT NULL DEFAULT '[]',
    individual_insights JSONB NOT NULL DEFAULT '{}',
    fusion_method VARCHAR(30) NOT NULL,
    consensus_level DECIMAL(3,2) NOT NULL DEFAULT 0.0,
    confidence_score DECIMAL(3,2) NOT NULL DEFAULT 0.0,
    unified_insight TEXT NOT NULL,
    key_recommendations JSONB DEFAULT '[]',
    conflicting_viewpoints JSONB DEFAULT '[]',
    additional_context JSONB DEFAULT '{}',
    insight_quality_score DECIMAL(3,2) DEFAULT 0.0,
    actionability_score DECIMAL(3,2) DEFAULT 0.0,
    processing_time_seconds DECIMAL(10,3),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    metadata JSONB DEFAULT '{}'
);
```

## Performance Optimization System

### 12. query_performance_metrics
**Purpose**: Detailed query performance tracking with optimization strategies and results
```sql
CREATE TABLE query_performance_metrics (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    query_id VARCHAR(100) NOT NULL,
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    query_type VARCHAR(30) NOT NULL,
    query_hash VARCHAR(64) NOT NULL,
    query_pattern TEXT,
    execution_time_ms INTEGER NOT NULL,
    cache_hit BOOLEAN DEFAULT false,
    result_size_bytes INTEGER DEFAULT 0,
    rows_processed INTEGER DEFAULT 0,
    optimization_strategy VARCHAR(30),
    optimization_applied BOOLEAN DEFAULT false,
    optimization_improvement_ms INTEGER DEFAULT 0,
    complexity_level VARCHAR(10) NOT NULL,
    complexity_score DECIMAL(3,2) DEFAULT 0.5,
    request_source VARCHAR(50),
    session_id VARCHAR(100),
    timestamp TIMESTAMPTZ DEFAULT NOW(),
    metadata JSONB DEFAULT '{}'
);
```

### 13. async_task_queue
**Purpose**: Priority-based async task queue with resource management and dependency tracking
```sql
CREATE TABLE async_task_queue (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    task_id VARCHAR(100) NOT NULL UNIQUE,
    task_type VARCHAR(50) NOT NULL,
    task_name VARCHAR(255) NOT NULL,
    task_payload JSONB NOT NULL DEFAULT '{}',
    priority VARCHAR(10) NOT NULL DEFAULT 'normal',
    priority_score INTEGER GENERATED ALWAYS AS (...) STORED,
    status VARCHAR(20) DEFAULT 'queued',
    worker_id VARCHAR(100),
    worker_type VARCHAR(30) DEFAULT 'general',
    queued_at TIMESTAMPTZ DEFAULT NOW(),
    started_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,
    timeout_at TIMESTAMPTZ DEFAULT (NOW() + INTERVAL '30 minutes'),
    estimated_duration_seconds INTEGER,
    actual_duration_seconds INTEGER,
    resource_usage JSONB DEFAULT '{}',
    retry_count INTEGER DEFAULT 0,
    max_retries INTEGER DEFAULT 3,
    error_details JSONB,
    result_data JSONB,
    result_size_bytes INTEGER,
    depends_on_tasks JSONB DEFAULT '[]',
    blocks_tasks JSONB DEFAULT '[]',
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    session_id VARCHAR(100),
    request_id VARCHAR(100),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    metadata JSONB DEFAULT '{}'
);
```

## Key Relationships and Foreign Keys

### Primary Relationships

1. **users → user_profiles** (1:1)
   - Each user has one extended profile

2. **users → user_preferences** (1:1)
   - Each user has one set of preferences

3. **users → conversation_memory** (1:many)
   - Users can have multiple conversation memories

4. **users → user_sessions** (1:many)
   - Users can have multiple active sessions (multi-device)

5. **users → tasks** (1:many)
   - Users can have multiple tasks

6. **collaboration_requests → insight_fusion_results** (1:many)
   - Each collaboration can generate multiple insight fusion results

7. **conversation_memory → conversation_memory** (parent-child)
   - Memories can reference related memories

### Cross-System Relationships

1. **Memory ↔ Collaboration**: Sessions and memory are shared across collaborative agent interactions
2. **Performance ↔ All Systems**: All operations are tracked for performance optimization
3. **Tasks ↔ Collaboration**: Tasks can trigger agent collaborations

## Indexes and Performance

### Critical Indexes

#### User-centric queries
```sql
CREATE INDEX idx_conversation_memory_user_context_time 
    ON conversation_memory(user_id, context, timestamp DESC);

CREATE INDEX idx_user_sessions_user_status_activity 
    ON user_sessions(user_id, status, last_activity DESC);
```

#### Performance optimization
```sql
CREATE INDEX idx_query_performance_metrics_execution_time 
    ON query_performance_metrics(execution_time_ms);

CREATE INDEX idx_async_task_queue_status_priority 
    ON async_task_queue(status, priority_score DESC);
```

#### Agent collaboration
```sql
CREATE INDEX idx_collaboration_requests_user_status_time 
    ON collaboration_requests(user_id, status, created_at DESC);
```

## Views and Computed Data

### Key Views

1. **active_user_sessions**: Shows active sessions with inactivity tracking
2. **user_memory_summary**: Aggregated memory statistics per user
3. **active_partnerships_metrics**: Partnership effectiveness metrics
4. **query_performance_summary**: Performance metrics by query type

## Triggers and Business Logic

### Automatic Updates

1. **update_updated_at_column()**: Automatically updates timestamp fields
2. **update_session_activity()**: Updates session activity on interactions
3. **update_partnership_effectiveness()**: Updates partnership metrics on completion
4. **clean_expired_cache()**: Removes expired cache entries

### Data Integrity

1. **update_personality_sample_size()**: Maintains sample size counts for personality profiles
2. **update_collaboration_compatibility()**: Updates agent compatibility based on outcomes

## Migration Information

### Migration Order

1. **001_enhanced_core_schema.sql**: Core system tables and agent registry
2. **002_conversation_memory_system.sql**: FASE 12 POINT 1 implementation
3. **003_agent_collaboration_system.sql**: FASE 12 POINT 2 implementation  
4. **004_performance_optimization_system.sql**: FASE 12 POINT 3 implementation

### Migration Tracking

The `migration_log` table tracks all executed migrations:

```sql
CREATE TABLE migration_log (
    id SERIAL PRIMARY KEY,
    migration_name VARCHAR(255) NOT NULL UNIQUE,
    migration_file VARCHAR(255) NOT NULL,
    executed_at TIMESTAMPTZ DEFAULT NOW(),
    execution_time_seconds DECIMAL(10,3),
    status VARCHAR(20) DEFAULT 'completed',
    error_message TEXT,
    checksum VARCHAR(64),
    notes TEXT
);
```

## Data Types and Constraints

### Common Patterns

1. **UUIDs**: All primary keys use UUID for global uniqueness
2. **JSONB**: Flexible schema fields use JSONB for performance
3. **Check Constraints**: Enum-like fields use CHECK constraints
4. **Timestamps**: All tables include created_at, many include updated_at
5. **Soft Deletes**: Some tables use is_active/is_archived instead of hard deletes

### Validation Rules

1. **Scores**: Most score fields use DECIMAL(3,2) with CHECK constraints (0.0-1.0)
2. **Ratings**: User ratings use INTEGER with CHECK constraints (1-5)
3. **Status Fields**: Use CHECK constraints to enforce valid states
4. **Required Fields**: Critical fields marked as NOT NULL

## Business Rules

### Conversation Memory

1. Memories have configurable retention based on importance_score
2. Sessions can be synchronized across multiple devices
3. Personality profiles are learned automatically from interactions

### Agent Collaboration

1. Partnerships have effectiveness tracking and auto-optimization
2. Collaborations can be triggered automatically based on conditions
3. Insight fusion supports multiple algorithms for combining agent responses

### Performance Optimization

1. Query patterns are automatically detected and optimized
2. Circuit breakers protect against failing external services
3. Resource usage is tracked for capacity planning

## Security Considerations

1. **Row Level Security**: Can be implemented for multi-tenant scenarios
2. **Data Encryption**: Sensitive fields can be encrypted at application level
3. **Audit Logging**: All changes are tracked with timestamps and user context
4. **Access Control**: Foreign key constraints ensure data integrity

## Maintenance and Monitoring

### Regular Maintenance

1. **Cache Cleanup**: Expired cache entries are automatically removed
2. **Session Cleanup**: Expired sessions should be archived periodically
3. **Performance Analysis**: Query patterns should be reviewed for optimization opportunities

### Monitoring Queries

```sql
-- Check system health
SELECT * FROM database_health_check();

-- Monitor query performance
SELECT * FROM query_performance_summary;

-- Check active collaborations
SELECT * FROM recent_collaboration_activity;

-- Monitor resource usage
SELECT * FROM active_performance_alerts;
```

---

*This documentation covers the complete database schema for NGX Agents FASE 12 implementation. For implementation details, refer to the individual migration files and the migration runner script.*