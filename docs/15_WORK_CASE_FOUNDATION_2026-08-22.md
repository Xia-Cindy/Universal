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

## 2026-08-23 R1 direction correction: personal capability learning space

The learner clarified that Work Planet is a personal career-learning space,
not a client-delivery workspace. Its first screen must not require a project,
Case, metrics, or professional history before it becomes useful.

`/work` therefore becomes a capability entry surface with five domains:

1. BA / Business Analysis
2. PM / Product and Project Management
3. Governance
4. Operations
5. Technology Stack

Each domain initially offers a clear learning path and the kinds of evidence
the learner may later collect. It does not display invented progress and does
not create a new Knowledge, Memory, AI Core, or content store. Future domain
materials must use Shared Knowledge; a real-work exercise may use the existing
PracticeCase aggregate only when the learner explicitly chooses to open one.

The existing Case APIs, records, stage rules and `/work/cases` routes remain
intact as an optional practice layer. A low-resource technology service lab is
also deferred until an isolated sandbox design has been approved; it must not
share the Universe OS runtime or expose a host service directly.
