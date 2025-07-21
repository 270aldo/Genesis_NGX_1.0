-- V7: Feature Flags System
-- Description: Create tables and policies for feature flag management
-- Author: GENESIS Team
-- Date: 2025-07-21

-- Create enum types
CREATE TYPE flag_type AS ENUM (
    'boolean',
    'percentage',
    'user_list',
    'user_segment',
    'variant',
    'schedule',
    'operational'
);

CREATE TYPE flag_status AS ENUM (
    'active',
    'disabled',
    'archived'
);

-- Create feature_flags table
CREATE TABLE IF NOT EXISTS feature_flags (
    -- Primary key
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    
    -- Flag identification
    name VARCHAR(100) NOT NULL UNIQUE,
    description TEXT NOT NULL,
    
    -- Flag configuration
    type flag_type NOT NULL DEFAULT 'boolean',
    status flag_status NOT NULL DEFAULT 'active',
    default_value JSONB DEFAULT 'false',
    
    -- Targeting
    target_percentage INTEGER CHECK (target_percentage >= 0 AND target_percentage <= 100),
    target_users TEXT[] DEFAULT ARRAY[]::TEXT[],
    target_segments TEXT[] DEFAULT ARRAY[]::TEXT[],
    
    -- Rules (for complex evaluations)
    rules JSONB DEFAULT '[]'::JSONB,
    
    -- Variants (for A/B testing)
    variants JSONB DEFAULT '{}'::JSONB,
    
    -- Schedule
    start_date TIMESTAMPTZ,
    end_date TIMESTAMPTZ,
    
    -- Metadata
    metadata JSONB DEFAULT '{}'::JSONB,
    
    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    
    -- Constraints
    CONSTRAINT valid_percentage CHECK (
        type != 'percentage' OR target_percentage IS NOT NULL
    ),
    CONSTRAINT valid_schedule CHECK (
        type != 'schedule' OR (start_date IS NOT NULL OR end_date IS NOT NULL)
    ),
    CONSTRAINT valid_date_range CHECK (
        start_date IS NULL OR end_date IS NULL OR start_date <= end_date
    )
);

-- Create indexes
CREATE INDEX idx_feature_flags_name ON feature_flags(name);
CREATE INDEX idx_feature_flags_status ON feature_flags(status);
CREATE INDEX idx_feature_flags_type ON feature_flags(type);
CREATE INDEX idx_feature_flags_schedule ON feature_flags(start_date, end_date) 
    WHERE type = 'schedule';
CREATE INDEX idx_feature_flags_updated_at ON feature_flags(updated_at DESC);

-- GIN index for JSONB searches
CREATE INDEX idx_feature_flags_metadata ON feature_flags USING GIN (metadata);
CREATE INDEX idx_feature_flags_variants ON feature_flags USING GIN (variants);

-- Create feature_flag_evaluations table for analytics
CREATE TABLE IF NOT EXISTS feature_flag_evaluations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    
    -- Flag reference
    flag_id UUID NOT NULL REFERENCES feature_flags(id) ON DELETE CASCADE,
    flag_name VARCHAR(100) NOT NULL,
    
    -- Evaluation context
    user_id UUID,
    user_segment VARCHAR(50),
    context JSONB DEFAULT '{}'::JSONB,
    
    -- Result
    evaluated_value JSONB NOT NULL,
    variant VARCHAR(100),
    
    -- Metadata
    evaluation_time_ms INTEGER,
    cache_hit BOOLEAN DEFAULT FALSE,
    
    -- Timestamp
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create indexes for evaluations
CREATE INDEX idx_flag_evaluations_flag_id ON feature_flag_evaluations(flag_id);
CREATE INDEX idx_flag_evaluations_user_id ON feature_flag_evaluations(user_id);
CREATE INDEX idx_flag_evaluations_created_at ON feature_flag_evaluations(created_at DESC);

-- Partition by month for better performance
-- Note: Requires PostgreSQL 11+
DO $$
BEGIN
    IF current_setting('server_version_num')::int >= 110000 THEN
        EXECUTE 'ALTER TABLE feature_flag_evaluations PARTITION BY RANGE (created_at)';
    END IF;
END $$;

-- Create feature_flag_audit table
CREATE TABLE IF NOT EXISTS feature_flag_audit (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    
    -- Flag reference
    flag_id UUID NOT NULL,
    flag_name VARCHAR(100) NOT NULL,
    
    -- Change information
    action VARCHAR(20) NOT NULL, -- created, updated, deleted, enabled, disabled
    changed_by UUID NOT NULL,
    changed_by_email VARCHAR(255),
    
    -- Change details
    old_value JSONB,
    new_value JSONB,
    change_summary TEXT,
    
    -- Timestamp
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create indexes for audit
CREATE INDEX idx_flag_audit_flag_id ON feature_flag_audit(flag_id);
CREATE INDEX idx_flag_audit_changed_by ON feature_flag_audit(changed_by);
CREATE INDEX idx_flag_audit_created_at ON feature_flag_audit(created_at DESC);

-- Create updated_at trigger
CREATE OR REPLACE FUNCTION update_feature_flags_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER feature_flags_updated_at
    BEFORE UPDATE ON feature_flags
    FOR EACH ROW
    EXECUTE FUNCTION update_feature_flags_updated_at();

-- Create audit trigger
CREATE OR REPLACE FUNCTION audit_feature_flag_changes()
RETURNS TRIGGER AS $$
DECLARE
    changed_by_id UUID;
    changed_by_email VARCHAR(255);
    action_type VARCHAR(20);
BEGIN
    -- Get user info from context (set by application)
    changed_by_id := current_setting('app.current_user_id', true)::UUID;
    changed_by_email := current_setting('app.current_user_email', true);
    
    -- Determine action
    IF TG_OP = 'INSERT' THEN
        action_type := 'created';
    ELSIF TG_OP = 'UPDATE' THEN
        IF OLD.status != NEW.status THEN
            action_type := CASE 
                WHEN NEW.status = 'active' THEN 'enabled'
                WHEN NEW.status = 'disabled' THEN 'disabled'
                ELSE 'updated'
            END;
        ELSE
            action_type := 'updated';
        END IF;
    ELSIF TG_OP = 'DELETE' THEN
        action_type := 'deleted';
    END IF;
    
    -- Insert audit record
    INSERT INTO feature_flag_audit (
        flag_id,
        flag_name,
        action,
        changed_by,
        changed_by_email,
        old_value,
        new_value,
        change_summary
    ) VALUES (
        COALESCE(NEW.id, OLD.id),
        COALESCE(NEW.name, OLD.name),
        action_type,
        COALESCE(changed_by_id, '00000000-0000-0000-0000-000000000000'::UUID),
        changed_by_email,
        CASE WHEN TG_OP != 'INSERT' THEN to_jsonb(OLD) ELSE NULL END,
        CASE WHEN TG_OP != 'DELETE' THEN to_jsonb(NEW) ELSE NULL END,
        CASE
            WHEN TG_OP = 'INSERT' THEN 'Flag created'
            WHEN TG_OP = 'UPDATE' THEN 'Flag updated: ' || 
                array_to_string(
                    ARRAY(
                        SELECT unnest(
                            ARRAY(
                                SELECT key FROM jsonb_each(to_jsonb(NEW)) 
                                EXCEPT 
                                SELECT key FROM jsonb_each(to_jsonb(OLD))
                            )
                        )
                    ), 
                    ', '
                )
            WHEN TG_OP = 'DELETE' THEN 'Flag deleted'
        END
    );
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER audit_feature_flags
    AFTER INSERT OR UPDATE OR DELETE ON feature_flags
    FOR EACH ROW
    EXECUTE FUNCTION audit_feature_flag_changes();

-- Row Level Security
ALTER TABLE feature_flags ENABLE ROW LEVEL SECURITY;
ALTER TABLE feature_flag_evaluations ENABLE ROW LEVEL SECURITY;
ALTER TABLE feature_flag_audit ENABLE ROW LEVEL SECURITY;

-- Policies for feature_flags
-- Anyone authenticated can read active flags
CREATE POLICY "feature_flags_read_active" ON feature_flags
    FOR SELECT
    TO authenticated
    USING (status = 'active');

-- Admins can read all flags
CREATE POLICY "feature_flags_read_all_admin" ON feature_flags
    FOR SELECT
    TO authenticated
    USING (
        EXISTS (
            SELECT 1 FROM user_profiles
            WHERE user_profiles.id = auth.uid()
            AND user_profiles.role = 'admin'
        )
    );

-- Only admins can insert, update, delete
CREATE POLICY "feature_flags_write_admin" ON feature_flags
    FOR ALL
    TO authenticated
    USING (
        EXISTS (
            SELECT 1 FROM user_profiles
            WHERE user_profiles.id = auth.uid()
            AND user_profiles.role = 'admin'
        )
    );

-- Policies for feature_flag_evaluations
-- Users can only see their own evaluations
CREATE POLICY "flag_evaluations_read_own" ON feature_flag_evaluations
    FOR SELECT
    TO authenticated
    USING (user_id = auth.uid());

-- Service role can insert evaluations
CREATE POLICY "flag_evaluations_insert_service" ON feature_flag_evaluations
    FOR INSERT
    TO service_role
    WITH CHECK (true);

-- Policies for feature_flag_audit
-- Only admins can read audit logs
CREATE POLICY "flag_audit_read_admin" ON feature_flag_audit
    FOR SELECT
    TO authenticated
    USING (
        EXISTS (
            SELECT 1 FROM user_profiles
            WHERE user_profiles.id = auth.uid()
            AND user_profiles.role = 'admin'
        )
    );

-- Service role can insert audit logs
CREATE POLICY "flag_audit_insert_service" ON feature_flag_audit
    FOR INSERT
    TO service_role
    WITH CHECK (true);

-- Insert default feature flags
INSERT INTO feature_flags (name, description, type, status, default_value, metadata) VALUES
    ('maintenance_mode', 'Enable maintenance mode', 'boolean', 'disabled', 'false', '{"critical": true}'),
    ('rate_limiting_enhanced', 'Enhanced rate limiting', 'boolean', 'active', 'true', '{"category": "security"}'),
    ('ai_coaching_beta', 'AI-powered coaching features', 'percentage', 'active', 'false', '{"category": "features"}'),
    ('new_onboarding_flow', 'Improved onboarding experience', 'user_segment', 'active', 'false', '{"category": "ux"}'),
    ('workout_style', 'Workout presentation style', 'variant', 'active', '"standard"', '{"category": "ab_test"}')
ON CONFLICT (name) DO NOTHING;

-- Set variants for A/B test
UPDATE feature_flags 
SET variants = '{
    "standard": {"style": "classic", "animations": false},
    "modern": {"style": "minimal", "animations": true},
    "gamified": {"style": "game-like", "animations": true, "points": true}
}'::jsonb,
target_percentage = 100
WHERE name = 'workout_style';

-- Grant permissions
GRANT SELECT ON feature_flags TO authenticated;
GRANT SELECT ON feature_flag_evaluations TO authenticated;
GRANT SELECT ON feature_flag_audit TO authenticated;
GRANT ALL ON feature_flags TO service_role;
GRANT ALL ON feature_flag_evaluations TO service_role;
GRANT ALL ON feature_flag_audit TO service_role;

-- Create helper functions
CREATE OR REPLACE FUNCTION evaluate_feature_flag(
    p_flag_name VARCHAR(100),
    p_user_id UUID DEFAULT NULL,
    p_context JSONB DEFAULT '{}'::JSONB
) RETURNS JSONB AS $$
DECLARE
    v_flag feature_flags%ROWTYPE;
    v_result JSONB;
    v_hash_value BIGINT;
BEGIN
    -- Get flag
    SELECT * INTO v_flag 
    FROM feature_flags 
    WHERE name = p_flag_name 
    AND status = 'active';
    
    IF NOT FOUND THEN
        RETURN jsonb_build_object('enabled', false, 'reason', 'flag_not_found');
    END IF;
    
    -- Check schedule
    IF v_flag.type = 'schedule' THEN
        IF v_flag.start_date IS NOT NULL AND NOW() < v_flag.start_date THEN
            RETURN jsonb_build_object('enabled', false, 'reason', 'before_start_date');
        END IF;
        IF v_flag.end_date IS NOT NULL AND NOW() > v_flag.end_date THEN
            RETURN jsonb_build_object('enabled', false, 'reason', 'after_end_date');
        END IF;
    END IF;
    
    -- Evaluate based on type
    CASE v_flag.type
        WHEN 'boolean' THEN
            RETURN jsonb_build_object('enabled', v_flag.default_value::boolean);
            
        WHEN 'percentage' THEN
            -- Use consistent hashing
            v_hash_value := abs(hashtext(v_flag.name || ':' || COALESCE(p_user_id::text, 'anonymous')));
            IF (v_hash_value % 100) < v_flag.target_percentage THEN
                RETURN jsonb_build_object('enabled', true);
            ELSE
                RETURN jsonb_build_object('enabled', false);
            END IF;
            
        WHEN 'user_list' THEN
            IF p_user_id IS NOT NULL AND p_user_id::text = ANY(v_flag.target_users) THEN
                RETURN jsonb_build_object('enabled', true);
            ELSE
                RETURN jsonb_build_object('enabled', false);
            END IF;
            
        ELSE
            RETURN jsonb_build_object('enabled', v_flag.default_value::boolean);
    END CASE;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Comments
COMMENT ON TABLE feature_flags IS 'Feature flag configurations for gradual rollout and A/B testing';
COMMENT ON TABLE feature_flag_evaluations IS 'Log of feature flag evaluations for analytics';
COMMENT ON TABLE feature_flag_audit IS 'Audit trail for feature flag changes';
COMMENT ON FUNCTION evaluate_feature_flag IS 'Server-side feature flag evaluation function';