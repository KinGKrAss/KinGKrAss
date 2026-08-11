CREATE EXTENSION IF NOT EXISTS pgcrypto;

CREATE SCHEMA IF NOT EXISTS zoe;
SET search_path TO zoe, public;

DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'zoe_access_level') THEN
        CREATE TYPE zoe_access_level AS ENUM ('READ', 'ANALYZE', 'WRITE', 'ADMIN');
    END IF;

    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'zoe_actor_type') THEN
        CREATE TYPE zoe_actor_type AS ENUM ('USER', 'ZOE', 'AGENT', 'SYSTEM', 'CONNECTOR');
    END IF;

    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'zoe_change_operation') THEN
        CREATE TYPE zoe_change_operation AS ENUM (
            'CREATE',
            'UPDATE',
            'ARCHIVE',
            'RESTORE',
            'MERGE',
            'CONFIRM',
            'DELETE_REQUEST',
            'DELETE_APPROVED'
        );
    END IF;

    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'zoe_epistemic_status') THEN
        CREATE TYPE zoe_epistemic_status AS ENUM (
            'ORIGINAL',
            'REKONSTRUKTION',
            'INTERPRETATION',
            'AKTUELLE_DEFINITION',
            'BENUTZERBESTAETIGT'
        );
    END IF;

    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'zoe_object_status') THEN
        CREATE TYPE zoe_object_status AS ENUM ('ACTIVE', 'ARCHIVED', 'SUPERSEDED', 'DRAFT');
    END IF;

    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'zoe_connector_system') THEN
        CREATE TYPE zoe_connector_system AS ENUM ('POSTGRESQL', 'GITHUB', 'TERRABOX', 'MANUAL', 'SYSTEM');
    END IF;
END $$;

CREATE TABLE IF NOT EXISTS zoe_identity_versions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    version_label TEXT NOT NULL UNIQUE,
    is_current BOOLEAN NOT NULL DEFAULT FALSE,
    name TEXT NOT NULL,
    designation TEXT,
    system_name TEXT NOT NULL DEFAULT 'Z1',
    primary_role TEXT NOT NULL,
    functions JSONB NOT NULL DEFAULT '[]'::jsonb,
    network_name TEXT,
    status TEXT NOT NULL DEFAULT 'CORE_INTELLIGENCE',
    communication_principles JSONB NOT NULL DEFAULT '[]'::jsonb,
    values JSONB NOT NULL DEFAULT '[]'::jsonb,
    origin_summary TEXT,
    module_relationships JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_by TEXT
);

CREATE TABLE IF NOT EXISTS zoe_conversations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    external_ref TEXT,
    title TEXT NOT NULL,
    source_system zoe_connector_system NOT NULL DEFAULT 'MANUAL',
    initiated_by TEXT,
    started_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    last_activity_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb
);

CREATE TABLE IF NOT EXISTS zoe_conversation_messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    conversation_id UUID NOT NULL REFERENCES zoe_conversations(id) ON DELETE CASCADE,
    role TEXT NOT NULL,
    content TEXT NOT NULL,
    content_type TEXT NOT NULL DEFAULT 'text/plain',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb
);

CREATE TABLE IF NOT EXISTS zoe_provenance_sources (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    source_system zoe_connector_system NOT NULL,
    source_kind TEXT NOT NULL,
    source_locator TEXT NOT NULL,
    source_excerpt TEXT,
    checksum TEXT,
    recorded_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb
);

CREATE TABLE IF NOT EXISTS zoe_memory (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    memory_key TEXT NOT NULL UNIQUE,
    category TEXT NOT NULL,
    priority SMALLINT NOT NULL DEFAULT 5 CHECK (priority BETWEEN 1 AND 10),
    status zoe_object_status NOT NULL DEFAULT 'ACTIVE',
    current_version_id UUID,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_by TEXT,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_by TEXT
);

CREATE TABLE IF NOT EXISTS zoe_memory_versions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    memory_id UUID NOT NULL REFERENCES zoe_memory(id) ON DELETE CASCADE,
    version_number INTEGER NOT NULL CHECK (version_number > 0),
    epistemic_status zoe_epistemic_status NOT NULL,
    title TEXT NOT NULL,
    content TEXT NOT NULL,
    source_summary TEXT,
    confidence NUMERIC(4,3) CHECK (confidence BETWEEN 0 AND 1),
    supersedes_version_id UUID REFERENCES zoe_memory_versions(id),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_by TEXT,
    UNIQUE (memory_id, version_number)
);

CREATE TABLE IF NOT EXISTS zoe_memory_version_sources (
    memory_version_id UUID NOT NULL REFERENCES zoe_memory_versions(id) ON DELETE CASCADE,
    provenance_source_id UUID NOT NULL REFERENCES zoe_provenance_sources(id) ON DELETE CASCADE,
    trust_score NUMERIC(4,3) NOT NULL DEFAULT 1.000 CHECK (trust_score BETWEEN 0 AND 1),
    is_primary BOOLEAN NOT NULL DEFAULT FALSE,
    PRIMARY KEY (memory_version_id, provenance_source_id)
);

CREATE TABLE IF NOT EXISTS zoe_memory_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    memory_id UUID NOT NULL REFERENCES zoe_memory(id) ON DELETE CASCADE,
    from_version_id UUID REFERENCES zoe_memory_versions(id),
    to_version_id UUID REFERENCES zoe_memory_versions(id),
    operation zoe_change_operation NOT NULL,
    reason TEXT,
    actor_type zoe_actor_type NOT NULL,
    actor_id TEXT,
    approval_required BOOLEAN NOT NULL DEFAULT FALSE,
    approval_state TEXT NOT NULL DEFAULT 'not_required',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb
);

CREATE TABLE IF NOT EXISTS zoe_knowledge_objects (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    object_key TEXT NOT NULL UNIQUE,
    subject_type TEXT NOT NULL,
    subject_ref TEXT,
    title TEXT NOT NULL,
    category TEXT NOT NULL,
    status zoe_object_status NOT NULL DEFAULT 'ACTIVE',
    current_version_id UUID,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_by TEXT,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_by TEXT
);

CREATE TABLE IF NOT EXISTS zoe_knowledge_object_versions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    knowledge_object_id UUID NOT NULL REFERENCES zoe_knowledge_objects(id) ON DELETE CASCADE,
    version_number INTEGER NOT NULL CHECK (version_number > 0),
    epistemic_status zoe_epistemic_status NOT NULL,
    summary TEXT NOT NULL,
    body TEXT NOT NULL,
    extracted_from TEXT,
    confidence NUMERIC(4,3) CHECK (confidence BETWEEN 0 AND 1),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_by TEXT,
    UNIQUE (knowledge_object_id, version_number)
);

CREATE TABLE IF NOT EXISTS zoe_knowledge_object_sources (
    knowledge_object_version_id UUID NOT NULL REFERENCES zoe_knowledge_object_versions(id) ON DELETE CASCADE,
    provenance_source_id UUID NOT NULL REFERENCES zoe_provenance_sources(id) ON DELETE CASCADE,
    trust_score NUMERIC(4,3) NOT NULL DEFAULT 1.000 CHECK (trust_score BETWEEN 0 AND 1),
    is_primary BOOLEAN NOT NULL DEFAULT FALSE,
    PRIMARY KEY (knowledge_object_version_id, provenance_source_id)
);

CREATE TABLE IF NOT EXISTS zoe_decisions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    decision_key TEXT NOT NULL UNIQUE,
    title TEXT NOT NULL,
    summary TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'PROPOSED',
    outcome TEXT,
    decided_at TIMESTAMPTZ,
    decided_by TEXT,
    confidence NUMERIC(4,3) CHECK (confidence BETWEEN 0 AND 1),
    supporting_context JSONB NOT NULL DEFAULT '[]'::jsonb,
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS zoe_preferences (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    scope_type TEXT NOT NULL CHECK (scope_type IN ('GLOBAL', 'USER', 'AGENT', 'MODULE')),
    scope_ref TEXT NOT NULL DEFAULT 'GLOBAL',
    preference_key TEXT NOT NULL,
    preference_value JSONB NOT NULL,
    access_level zoe_access_level NOT NULL DEFAULT 'READ',
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_by TEXT,
    UNIQUE (scope_type, scope_ref, preference_key)
);

CREATE TABLE IF NOT EXISTS zoe_tool_registry (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tool_name TEXT NOT NULL UNIQUE,
    description TEXT NOT NULL,
    integration_target zoe_connector_system NOT NULL,
    minimum_access_level zoe_access_level NOT NULL DEFAULT 'READ',
    requires_confirmation BOOLEAN NOT NULL DEFAULT FALSE,
    risk_level TEXT NOT NULL DEFAULT 'LOW',
    enabled BOOLEAN NOT NULL DEFAULT TRUE,
    input_schema JSONB NOT NULL DEFAULT '{}'::jsonb,
    output_schema JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS zoe_tool_permissions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    principal_type TEXT NOT NULL CHECK (principal_type IN ('ROLE', 'USER', 'AGENT', 'SYSTEM')),
    principal_ref TEXT NOT NULL,
    tool_id UUID NOT NULL REFERENCES zoe_tool_registry(id) ON DELETE CASCADE,
    access_level zoe_access_level NOT NULL,
    requires_confirmation BOOLEAN NOT NULL DEFAULT FALSE,
    approved_by TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (principal_type, principal_ref, tool_id, access_level)
);

CREATE TABLE IF NOT EXISTS zoe_tool_executions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tool_id UUID NOT NULL REFERENCES zoe_tool_registry(id),
    actor_type zoe_actor_type NOT NULL,
    actor_id TEXT NOT NULL,
    requested_access_level zoe_access_level NOT NULL,
    permission_granted BOOLEAN NOT NULL,
    confirmation_token TEXT,
    request_payload JSONB NOT NULL DEFAULT '{}'::jsonb,
    response_payload JSONB,
    status TEXT NOT NULL DEFAULT 'REQUESTED',
    requested_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    completed_at TIMESTAMPTZ,
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb
);

CREATE TABLE IF NOT EXISTS audit_log (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    occurred_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    actor_type zoe_actor_type NOT NULL,
    actor_id TEXT NOT NULL,
    action TEXT NOT NULL,
    access_level zoe_access_level,
    target_table TEXT,
    target_record_id TEXT,
    result TEXT NOT NULL,
    correlation_id TEXT,
    details JSONB NOT NULL DEFAULT '{}'::jsonb
);

DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1
        FROM information_schema.table_constraints
        WHERE constraint_schema = 'zoe'
          AND table_name = 'zoe_memory'
          AND constraint_name = 'zoe_memory_current_version_fk'
    ) THEN
        ALTER TABLE zoe_memory
            ADD CONSTRAINT zoe_memory_current_version_fk
            FOREIGN KEY (current_version_id) REFERENCES zoe_memory_versions(id);
    END IF;

    IF NOT EXISTS (
        SELECT 1
        FROM information_schema.table_constraints
        WHERE constraint_schema = 'zoe'
          AND table_name = 'zoe_knowledge_objects'
          AND constraint_name = 'zoe_knowledge_current_version_fk'
    ) THEN
        ALTER TABLE zoe_knowledge_objects
            ADD CONSTRAINT zoe_knowledge_current_version_fk
            FOREIGN KEY (current_version_id) REFERENCES zoe_knowledge_object_versions(id);
    END IF;
END $$;

CREATE INDEX IF NOT EXISTS idx_zoe_memory_status ON zoe_memory (status, priority DESC);
CREATE INDEX IF NOT EXISTS idx_zoe_memory_events_memory_id ON zoe_memory_events (memory_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_zoe_knowledge_subject ON zoe_knowledge_objects (subject_type, subject_ref);
CREATE INDEX IF NOT EXISTS idx_zoe_tool_permissions_principal ON zoe_tool_permissions (principal_type, principal_ref);
CREATE INDEX IF NOT EXISTS idx_audit_log_actor_time ON audit_log (actor_id, occurred_at DESC);
