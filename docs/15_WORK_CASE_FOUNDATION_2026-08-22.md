# Work Case Foundation — Phase 0 and Phase 1

Date: 2026-08-22

## Scope

This document records the approved Work Planet direction: one `PracticeCase`
organizes the professional-practice loop `Discover → Define → Govern →
Validate → Operate → Review`. It does not create a second Knowledge, RAGFlow,
monitoring, project-management, or execution system.

## Phase 0 baseline audit

### Existing

- The active user entry is React `room-portfolio` on port 5180. The Vue Work
  pages remain compatibility/contract-test sources.
- Work already has `TechStack`, `WorkProject`, `WorkArticle`,
  `WorkLearningRecord`, `ResumeVersion`, `WorkService`, `WorkRepository`,
  `/api/work/home`, shared PostgreSQL/SQLite persistence and shared Knowledge
  authorization.
- `work_records` is the portable JSON payload store used by the existing
  SQLite and PostgreSQL Work repositories.

### Reusable

- Work repository/service/API facade layering, user ownership, timestamps,
  contract registry, migration runners and 5180 API client.
- Existing Tech Stack, Project and Resume records remain distinct supporting
  capabilities; no data is copied into a Case in Phase 1.

### Missing before this phase

- No Case aggregate, active-case policy, stage model, next-action service,
  Case API, Case UI or `case_id` relation column.

### Conflict and adaptation

- The previous Work UI treated Tech Stack, Work Knowledge, Projects and Resume
  as peer tools. The approved direction makes them Case-linked capabilities.
- `/work/knowledge` duplicated a Work-specific content entry. Its active UI
  route/navigation is retired; legacy APIs and existing data remain read-only
  compatibility surface until a separately approved migration plan exists.
- The old `/work` Sylva landing page is not the Phase 1 implementation. It is
  retained only for Study's currently local visual reuse; the Work Tree is
  deferred until Case data is proven.

## Phase 1 implementation

- `PracticeCase`: title, problem, goal, scope, non-goal, status, current
  stage, success metrics, risks and dependencies.
- Server-owned rules: one active Case per user and no forward stage skips.
- APIs: list/create/read/update Cases and the extended Work Home aggregate.
- UI: real Case overview, Case list/create and Case detail/edit at the active
  5180 Work entry.

## Verification boundary

Phase 1 proves `Create Case → activeCase → currentStage → nextAction → edit
Case`. Artifact/BA, Backlog/PM, Governance, Labs, Operations, Evidence
relations, SOP, Radar, Bookshelf links and the Three.js Work Tree remain out
of scope.
