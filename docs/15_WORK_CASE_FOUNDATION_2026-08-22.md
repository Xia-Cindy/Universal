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

## 2026-08-25 R2: Technology Stack as a living learning space

`/work` is the capability entrance, with exactly five visible domains:

1. PM
2. BA
3. SRE
4. Data Governance
5. Technology Stack

Technology Stack is not a résumé form or a proficiency scoreboard. Each
Technology Stack record opens one horizontal tab in a personal technical
space. The tab presents a learner-facing map with three durable layers:

- implementation principles and system position (`WorkArticle`);
- a record of a real operation or practice (`WorkLearningRecord`); and
- a learner-authored theory-extension and real-application note
  (`WorkArticle` with `articleType=extension`).

The R2 room client reuses the existing Work API and PostgreSQL-backed
`work_records` persistence; it does not create an additional Work content
store, independent Knowledge base, or another RAGFlow client. Shared Knowledge
can be displayed only through the existing explicit grant path.

The current Universe build may be recorded as truthful practice evidence—for
example React/Three.js room work, FastAPI, PostgreSQL, Docker Compose, Linux
delivery and Nginx caching. RAGFlow is represented as a planned shared
Knowledge infrastructure until its own cloud deployment and retrieval-only
verification have completed. A future `ragflow-lab` must use isolated data and
must not read or write the `universe-ragflow` production Knowledge runtime.

### R2.1: Pasted screenshot evidence

One implementation-principle, extension or practice record may carry up to
four pasted screenshots. The 5180 client downscales the clipboard image to a
maximum 1600-pixel edge and previews the compressed WebP before save. The
existing `WorkArticle` and `WorkLearningRecord` payloads persist those small
private attachments in `work_records`; there is no second file store, Knowledge
document, RAGFlow upload or cross-Planet copy.

The Work service accepts only base64 PNG/JPEG/WebP/GIF data URLs, rejects SVG
and other executable URL forms, and caps each payload image at 1.5 MB. This is
appropriate for a personal development-learning log. Larger evidence and
shared-source materials remain a future object-storage/Knowledge authorization
decision, rather than being silently added to the Work record model.

Theory-extension notes are not an implementation backlog for Universe. Each
one should first state the theorem, architecture pattern, constraint or
engineering trade-off that follows from the current principle, then describe
one concrete application: its system context, operational constraint and what
would be verified. The subsequent real attempt belongs in the separate
practice log, preserving the distinction between understanding, application
design and observed evidence.

### R2.2: AI exploration with source boundaries

The right-side Technology Stack panel is an **AI exploration** surface, not a
second Work Knowledge database. A learner may select a passage in an
implementation-principle or theory-extension note and ask one question through
the shared AI Core. The request carries the Tech Stack, the originating Work
article, the selected quote and only the documents explicitly granted to that
Tech Stack. The browser never contacts an LLM provider directly.

An answer displays one of two source states: citations to matching authorized
Knowledge chunks, or a clear statement that no personal Knowledge source was
used. It is never silently promoted into Knowledge. The learner can explicitly
open the existing add-content form as `AI exploration / unresolved point`, edit
the answer into their own words, and save source article ID, selected quote,
question and citations as a WorkArticle. Practice remains a separate
WorkLearningRecord.

The shared AI Core can use an OpenAI-compatible Chat Completions provider when
the server-only `AI_PROVIDER`, `AI_OPENAI_BASE_URL`, `AI_OPENAI_API_KEY` and
`AI_OPENAI_MODEL` environment variables are configured. Keys are not persisted
in PostgreSQL or `work_records`, returned to the browser, or committed.

### R3.2: Knowledge route naming

The canonical spatial UI route for the shared Knowledge bookshelf is now
`/knowledge`. The previous `/study/knowledge` URL remains a compatibility alias
for existing bookmarks and citations. The browser still calls the Study-scoped
backend resources under `/api/study/knowledge/...`; this separates the public
room route from the Planet-owned API namespace.

## 2026-08-26 R3: categorized technical publication

The learner clarified that a fixed pair of “implementation principles / system
position” panels is not a general model for every technology. Technology Stack
therefore becomes a personal technical publication rather than a matrix of
predefined learning fields.

The Technology Stack landing page groups existing topics at presentation time
into five broad domains: AI and Knowledge, Runtime and Cloud, Backend and Data,
Frontend and Experience, and Engineering Methods. The grouping is a stable UI
taxonomy derived from the existing stack name, category and tags. It does not
rewrite historical categories or add a duplicate category persistence model.

Within one topic, all updates appear in one reverse-chronological article
stream. The learner may write a learning note, principle note, architecture
observation, theory-to-application extension, practice retrospective, or AI
exploration. “System position” is now an optional architecture-observation
article type, not a compulsory field. Existing `WorkArticle` records remain
articles, and existing `WorkLearningRecord` records render as practice
retrospectives in the same stream; their separate storage and evidence meaning
remain intact.

This is CSDN-like in its topic navigation and article-reading experience, not
a copied community product: there are no fabricated readers, likes, rankings,
external content feeds or second content service. Images remain private Work
attachments, Shared Knowledge remains source-owned and explicitly granted, and
AI exploration retains its existing shared-AI-Core and citation boundary.

### R3.1: self-contained Knowledge bookshelf fallback

The Study Knowledge and Wordbook shelves no longer require a network fetch of
the external visual reference at runtime. A clean-room, self-contained HTML
scene is bundled in `room-portfolio/src/bookshelf/fallbackSource.js`; it draws
the real catalog as CSS/canvas 3D book covers and keeps the existing
`postMessage` contract for filters, pagination, opening a book, and the reader
bridge. The source reference remains inspiration only and is not copied or
localized. This keeps the physical-cover and two-page reader interactions
available when an external host is slow or unreachable.
