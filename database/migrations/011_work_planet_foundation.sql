-- Milestone 10.0 Work Planet Foundation
-- Adds Work-owned tables for tech stacks, projects, and dynamic resume drafts.

CREATE TABLE IF NOT EXISTS tech_stacks (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    name TEXT NOT NULL,
    category TEXT NOT NULL,
    proficiency TEXT NOT NULL,
    description TEXT NOT NULL DEFAULT '',
    tags TEXT NOT NULL DEFAULT '[]',
    status TEXT NOT NULL DEFAULT 'active',
    created_at TIMESTAMPTZ NOT NULL,
    updated_at TIMESTAMPTZ NOT NULL
);

CREATE TABLE IF NOT EXISTS work_projects (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    title TEXT NOT NULL,
    description TEXT NOT NULL DEFAULT '',
    tech_stack_ids TEXT NOT NULL DEFAULT '[]',
    evidence_refs TEXT NOT NULL DEFAULT '[]',
    status TEXT NOT NULL DEFAULT 'draft',
    created_at TIMESTAMPTZ NOT NULL,
    updated_at TIMESTAMPTZ NOT NULL
);

CREATE TABLE IF NOT EXISTS resume_versions (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    role_target TEXT NOT NULL,
    title TEXT NOT NULL,
    content TEXT NOT NULL,
    evidence_refs TEXT NOT NULL DEFAULT '[]',
    status TEXT NOT NULL DEFAULT 'draft',
    created_at TIMESTAMPTZ NOT NULL,
    updated_at TIMESTAMPTZ NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_tech_stacks_user_status
    ON tech_stacks(user_id, status);

CREATE INDEX IF NOT EXISTS idx_work_projects_user_status
    ON work_projects(user_id, status);

CREATE INDEX IF NOT EXISTS idx_resume_versions_user_role
    ON resume_versions(user_id, role_target);
