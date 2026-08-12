# TODO

## 2026-08-12 Optimization and Feature Plan

- [x] Audit the active runtime, renderer boundary, Git history and stale documentation; document that the room is Three.js while the active bookshelf is DOM/CSS 3D.
- [x] Consolidate the spatial client's duplicate Study/Work Knowledge resource selection without changing the API contract.
- [x] Add a 5180 core-route smoke suite for the normal entry, Study, Plan, Knowledge, Wordbook, Cards, Work, Novel and the Vite API proxy before splitting any large spatial client module.
- [x] Split bookshelf catalog, reader-page model and iframe bridge responsibilities after the regression baseline passes; retain the confirmed reference scene and `postMessage` contract.
- [x] Separate bookshelf and Knowledge Blackboard CSS from the room shell; preserve existing values and keep the 5180 visual surfaces regression-checked.
- [ ] Verify source license and actual implementation before localizing any external bookshelf resources.
- [x] Run one controlled RAGFlow TXT, Markdown and PDF acceptance set with a valid embedding provider; record `processed`, chunk evidence, reader content and Tutor source links without requeueing existing long PDFs.
- [x] Complete F1 runtime acceptance with one approved new PDF after restoring a stuck worker; leave existing long PDFs unsubmitted and record the evidence in the dated plan and installation guide.
- [x] Design the Study Session unit-of-work before changing Task/Event/Memory write behavior; preserve the execution-finish API and require failure-injection coverage before implementation.
- [x] Implement the approved Study Session unit-of-work across SQLite/PostgreSQL adapters, including partial-write rollback, retry and concurrent-finish evidence; verify PostgreSQL in an isolated temporary schema and keep legacy repair explicit.
- [x] Add an explainable, user-adjustable interval-review schedule for source-owned knowledge cards and Wordbook entries; keep repeated same-day results idempotent and preserve first-time Goal mastery accounting.
- [x] Add explicit, revocable Study Goal Knowledge grants to active Work Tech Stacks; preserve source ownership and filter Work reads to owned or granted documents only.
- [x] Design and implement multi-Goal document links with SQLite/PostgreSQL backfill, explicit goal-link APIs, isolated retrieval filtering and Work-grant compatibility; synced reading progress remains a separate pending decision.
- [x] Design optional user/document reading-progress synchronization while retaining offline browser-local bookmarks and excluding Goal progress or Wordbook review facts.
- [x] Implement the approved reading-progress migration, API conflict handling and best-effort 5180 synchronization.
- [x] Add a read-only, evidence-backed Study feedback recommendation API for due reviews, incomplete tasks and synced reading positions; do not automatically mutate a plan.

## Study Bookshelf Module

- [x] Retire the old local Vue page from the normal startup/shutdown path and make the 5180 spatial room the sole product entry.
- [x] Remove the Planning Table's visible room outline and make the existing wall blackboard the direct entrance to a Study Knowledge Board for document-owned notes and recall cards.
- [x] Add `/study/cards`: a physical blackboard review space that groups existing Knowledge annotations into cards and notes, supports answer reveal and toggling the durable “背过了” state.
- [x] Apply the Rope Gallery hanging-rope visual language to the knowledge blackboard: paired cords, pin anchors, inset card stock and gentle motion, without replacing the learner-owned card data flow.
- [x] Make room assets use root-relative URLs so direct refreshes of shareable room paths, including `/study/cards`, keep loading the original room model.
- [x] Add Focus Reader notes and knowledge cards that remain owned by their source Knowledge document, including passage selection, optional Goal association, random key-term hiding, answer reveal and a durable “背过了” state.
- [x] Add Wordbook memory cards with English front / learner meaning back, remembered and mistaken result tracking, and durable review timestamps.
- [x] Count each first-time Knowledge/Wordbook “背过了” result once in the linked Study Goal workspace progress, without treating repeated clicks as additional progress.
- [x] Remove reader page scrolling and fit each generated paper page to the physical spread before turning it.
- [x] Add page-number jumping and browser-local bookmarks to the open Knowledge reader.
- [x] Keep the reference three-book hero composition while exposing every uploaded Study Knowledge document through previous/next shelf pages after the third book.
- [x] Add Study Knowledge subject filtering, goal association during upload, and a confirmed delete action that uses the existing document API.
- [x] Present every Wordbook tag as a vocabulary book in the deployed reference shelf, with the source physical open motion and paged paper reader for its real tagged entries.
- [x] Make an opened physical cover the reading entry: clicking it opens a center two-page spread and turns pages in pairs for Knowledge and Wordbook.
- [x] Let the open reader edit/delete the active Study Knowledge document or Wordbook entry, and use a shareable URL for every room module.
- [x] Integrate the deployed reference 3D book structure, its physical book-cover/detail motion, and its visual layout into Knowledge without substituting a custom animation.
- [x] Generate deterministic reference-style cover variants from Knowledge metadata when a new document enters the collection.

## Milestone 1 Foundation

- [x] Align repository structure with `AGENTS.md`.
- [x] Add backend project structure and API contract boundaries.
- [x] Add database foundation migration and seed data.
- [x] Add Planet registry with Study active and Future Planet placeholders.
- [x] Add Study Home empty-state contract.
- [x] Add Study Workspace shell files.

## Milestone 2 Learning Workflow

- [x] Add Study Goal service and API contracts.
- [x] Add Learning Plan and Daily Task service contracts.
- [x] Add Study Session start/finish recording.
- [x] Add Study Home progress aggregation.
- [x] Add Study Plan frontend workflow.
- [x] Keep Knowledge, Tutor, Review, and Analytics as placeholders.

## Milestone 3 AI Core + Tutor

- [x] Add shared AI Core service entry point.
- [x] Add LLM Gateway interface and deterministic provider.
- [x] Add Prompt Manager, Context Manager, and Agent Manager.
- [x] Add Study Tutor as an AI Core consumer.
- [x] Add Tutor API and frontend page.
- [x] Record Tutor interactions as Learning Events.
- [x] Keep RAG, embeddings, Knowledge Graph, document retrieval, and source citations out of scope.

## Milestone 3.5 AI Core Generalization

- [x] Add AgentDefinition registration model.
- [x] Refactor AgentManager to resolve registered definitions.
- [x] Refactor ContextManager to use context providers.
- [x] Move Study Tutor context assembly into a Study provider.
- [x] Refactor PromptManager to resolve prompt keys.
- [x] Keep LLM Gateway provider-only.
- [x] Add ToolRouter, Tool, and Retriever interfaces only.

## Milestone 4.1 Knowledge Foundation

- [x] Add shared Knowledge domain models for Documents, Document Chunks, and Concepts.
- [x] Add File service foundation for txt and markdown processing.
- [x] Add database migration `004_knowledge_foundation.sql`.
- [x] Add Knowledge API contracts for document registration, processing, listing, and detail.
- [x] Replace Study Knowledge placeholder with Knowledge document and chunk UI.
- [x] Keep embeddings, vector storage, retrieval, Tutor integration, and AI summary out of scope.

## Milestone 4.2 Retrieval Foundation

- [x] Add EmbeddingProvider abstraction and deterministic test provider.
- [x] Add VectorStore abstraction and in-memory test implementation.
- [x] Add chunk embedding metadata records and migration `005_retrieval_foundation.sql`.
- [x] Add RetrievalService for chunk embedding preparation and chunk-only retrieval.
- [x] Add Retrieval API contracts for embedding preparation, status listing, and chunk search.
- [x] Keep Tutor integration, RAG answer generation, real vector database deployment, and Knowledge Graph out of scope.

## Milestone 4.3 Tutor Retrieval Integration

- [x] Add AI Core ToolRouter execution flow for allowed tools.
- [x] Add RetrieverTool adapter over RetrievalService.
- [x] Connect Study Tutor retrieval through AI Core ToolRouter only.
- [x] Inject retrieved Knowledge chunks into Study Tutor context.
- [x] Record retrieval metadata in Learning Events.
- [x] Show grounding chunks in Tutor UI when available.
- [x] Keep Knowledge Graph, automatic summarization, Memory Intelligence, and new Agents out of scope.

## Milestone 5 Memory Intelligence Foundation

- [x] Add shared Memory Manager repository/service boundary.
- [x] Preserve global, planet, and session memory scopes.
- [x] Add memory lifecycle states: active, archived, expired.
- [x] Add scoped memory retrieval and access timestamp updates.
- [x] Add AI context preparation for active memories.
- [x] Add Memory API contracts for create, list, update, archive, and context.
- [x] Pass prepared memory context into Study Tutor through AI Core payload.
- [x] Keep autonomous extraction, personality inference, Knowledge Graph, vector memory, new Agents, and new Planets out of scope.

## Milestone 6 Study Intelligence Foundation

- [x] Add Study Analyst as a Study Agent capability.
- [x] Add Analytics service for progress metrics and learning insights.
- [x] Add Study Analyst context provider.
- [x] Add Study Analytics API contracts for metrics and report generation.
- [x] Replace Analytics placeholder with Study Intelligence page.
- [x] Reuse Study workflow data, Memory context, Knowledge and Retrieval.
- [x] Keep autonomous decisions, personality inference, new Agents, and new Planets out of scope.

## Milestone 7 Study Product Loop

- [x] Add Study onboarding status and Goal creation flow.
- [x] Persist onboarding learning preferences through Memory Service.
- [x] Productize manual Plan workflow without AI-generated planning.
- [x] Redesign Study Home as a daily control center backed by services.
- [x] Add Study Session execution wrapper with learning event and Memory write points.
- [x] Integrate existing Study Analytics / Analyst output into Study Home AI Insight.
- [x] Add frontend Onboarding and Session screens.
- [x] Keep AI Core architecture, Agents, Planets, RAG, Knowledge Graph and autonomous planning unchanged.

## Study Workspace Product Experience

- [x] Add Universe Home return entry in Study Workspace.
- [x] Show current Planet and user location in Study Workspace.
- [x] Extend Study Goal for exam, learning, reading, and growth goals.
- [x] Allow Goal deadline to be empty for non-exam learning scenarios.
- [x] Add Goal description field.
- [x] Support multiple Goals and Goal switching.
- [x] Support multiple Plans per Goal.
- [x] Add plan type separation for long-term, monthly, and weekly plans.
- [x] Allow Knowledge documents to exist independently or link to a Goal.
- [x] Replace Knowledge manual document registration with real file selection.
- [x] Support txt and markdown upload with processing.
- [x] Support PDF metadata upload without parser/RAG expansion.
- [x] Add Study Workspace aggregation API for current Goal, Goals, Plans, Today Tasks, Knowledge summary and Analytics summary.
- [x] Add Goal management page for listing, creating and switching Goals.
- [x] Refactor Study Home to use current Goal, plan hierarchy, Today Tasks and Analytics-only recommendations.
- [x] Refactor Plan UI into a current-Goal plan tree without raw plan type selection.
- [x] Add Knowledge Goal filter while preserving independent Knowledge.
- [x] Move Current Goal display and switching into the Study Workspace header.
- [x] Keep primary Study navigation to Home, Plan, Knowledge, Tutor, Review and Analytics.
- [x] Downgrade Goals to a management entry instead of a primary navigation item.
- [x] Refine Study Home around Current Goal, Today Mission, Primary Action, Recent Progress and AI Insight.
- [x] Replace separate Plan creation actions with one `Create Plan Structure` action.
- [x] Fix Knowledge upload button enablement so valid file selections can be submitted.
- [x] Make Home and Workspace primary action backend-owned so the frontend only renders the service decision.
- [x] Replace completed-task Start Session action with a progress/review-oriented action.
- [x] Clarify PDF Knowledge uploads as metadata-only when the parser is unavailable.
- [x] Add Tutor empty-question validation.
- [x] Reduce duplicate Current Goal display in the Study header.
- [x] Group Goals page into Current Goal, Other Goals and Create Goal sections.
- [x] Convert Analytics copy from raw engineering metrics to user-facing learning language.
- [x] Rename static side guidance to Study Context so AI recommendations only come from Analytics/Analyst.
- [x] Mark Review / Wrong Questions as a later closed-loop feature instead of implying it is complete.

## Milestone 8.1 RAGFlow Knowledge Provider

- [x] Add KnowledgeProvider protocol and RAGFlow adapter.
- [x] Add provider metadata migration for Knowledge documents.
- [x] Keep Universe frontend, Tutor, Study Planet and AI Core behind Universe Backend APIs.
- [x] Route provider-backed document processing through RAGFlow upload, parse and chunk APIs.
- [x] Route provider-backed retrieval through RAGFlow retrieval API.
- [x] Preserve local Knowledge fallback when `KNOWLEDGE_PROVIDER=local`.
- [x] Display provider-backed status in Study Knowledge.
- [x] Add mocked RAGFlow provider tests.
- [x] Add project-local RAGFlow Docker Compose stack.
- [x] Add RAGFlow installation and Universe connection documentation.

## Milestone 7.9 Study Goal and Plan Productization

- [x] Move Create Goal into a drilled `/study/goals/new` flow.
- [x] Add Goal type selection before the detailed Goal form.
- [x] Show Goal-type Knowledge Space preview for exam, reading, learning and growth goals.
- [x] Route empty Study Home / Workspace primary action to the drilled Goal creation page.
- [x] Add Daily Task priority with migration `010_study_plan_calendar_priority.sql`.
- [x] Add Study Plan Calendar to visualize current Goal tasks by day.
- [x] Allow task priority editing from Plan.
- [x] Keep AI Core, RAGFlow provider, Retrieval, Memory and Work Planet untouched in this slice.

## Milestone 10.0 Work Planet Foundation

- [x] Make Work Planet active and enterable from Universe Portal.
- [x] Add Work-owned Tech Stack, Project and Resume domain models.
- [x] Add migration `011_work_planet_foundation.sql`.
- [x] Add Work Home API and frontend page.
- [x] Add Tech Stack directory and detail pages.
- [x] Add project evidence creation.
- [x] Add Dynamic Resume draft creation based on confirmed Work evidence.
- [x] Allow Work to reference shared Knowledge through Knowledge Service summaries only.
- [x] Add Work Knowledge as a first-class workspace module without duplicating the shared Knowledge Service.
- [x] Bind Work Knowledge documents to Tech Stack and tags.
- [x] Separate RAGFlow datasets by Study Goal for provider-backed Study Knowledge.
- [x] Add Tech Stack-owned article writing and learning record capture.
- [x] Add CSDN Community tab for public technology article discovery without auto-ingesting it into Knowledge.
- [x] Keep Tech Stack tabs ordered by creation time and type Work articles as Knowledge or Note.
- [x] Move Add Tech Stack into a modal form with only name and category required.
- [x] Refine Tech Stack directory into category row plus stack row, with Community isolated from stack tabs.
- [x] Keep CSDN Community display usable with 30 discovery items when live fetch is unavailable.
- [x] Add inline CSDN article reading inside Work Planet without requiring a jump to CSDN.
- [x] Keep category switching usable while Community articles are loading.
- [x] Remove duplicated Tech Stack directory card after the second-row stack selector and align selected tabs with the system teal colorway.
- [x] Remove the redundant `Open Stack` summary card because the second-row stack selector already defines the current stack context.
- [x] Animate the Universe Home starfield with alternating vertical dot-column motion and reduced-motion support.
- [x] Add Study Knowledge Write Article mode that saves goal-linked markdown articles through the existing Knowledge API.
- [x] Add Tech Stack update and archive actions.
- [x] Refine Tech Stack article writing into a focused editor with an auto-generated left outline.
- [x] Restore an explicit Work `写文章` entry and keep the Tech Stack editor closed by default.
- [x] Add compact title-level article tools that insert images, editable tables and code snippets directly into the article body, plus pasted image/table handling, bold text, text color, table row/column operations and cell merge/split.
- [x] Keep AI Core, Retrieval, RAGFlow and Memory architecture unchanged.
- [x] Keep Work Agent and autonomous resume generation out of scope.

## Later Milestones

- [x] Add shared SQLite persistence behind the existing repository boundaries.
- [x] Add migration runner and persist Study, Knowledge, Memory and Work records.
- [x] Persist one `current_goal` per user and Study Planet in `user_planet_context`.
- [x] Add PostgreSQL adapter using the same repository interfaces.
- [x] Connect Knowledge services to PostgreSQL adapters and local/S3 object storage boundaries.
- [x] Add SQLite/PostgreSQL backup and guarded PostgreSQL restore scripts.
- [x] Add email verification registration with SMTP production boundary and console development sender.
- [x] Run RAGFlow runtime acceptance with fresh TXT, Markdown and PDF samples now that the embedding-provider key issue is resolved; record processed status, chunk preview and Tutor retrieval evidence.
- [x] Keep Study Goal and Work Tech Stack dataset scopes readable, isolated and reusable across provider restarts; surface the provider error code when embedding binding fails.
- [x] Add provider status polling and retry handling.
- [x] Keep Work Knowledge provider status polling separate from parse initiation so an in-flight RAGFlow document is not parsed twice.
- [x] Synchronize provider document deletion with RAGFlow.
- [x] Add stable Citation / Evidence source contract, source quote preview, Knowledge click-through and saved Tutor Learning Events.
- [x] Add Study Wordbook with manual entry, TXT/CSV batch import, scope-local duplicate handling, and editable tags/phrases/examples/notes.
- [x] Repair Wordbook save/list behavior across language and independent scope filters, with a forward-compatible PostgreSQL migration.
- [x] Make PostgreSQL the default Universe runtime persistence configuration and provide a local pgvector startup profile.
- [x] Decode native PostgreSQL JSONB payloads across shared repositories so persistent Study, Knowledge, Memory and Work reads remain portable.
- [x] Unify Universe Portal, Study Workspace, and Work Workspace around the dark planetary visual language while preserving existing API-driven product flows.
- [x] Replace the spatial room drawer with independent 3D module worlds for all Study, Work and Novel drill-down pages.
- [x] Enter 3D module worlds through mapped room furniture with a short focus transition and near-field module stage.
- [x] Redesign the spatial Wordbook as a searchable, paginated vocabulary garden with selectable plants, readable lexicon details, single-word creation and TXT/CSV import instruments.
- [x] Preserve Chinese Pinyin composition in the spatial Wordbook creation form without propagating keyboard input into the 3D controls.
- [x] Reconnect dropped PostgreSQL sessions at the shared persistence boundary and show explicit Wordbook save status without replaying uncertain writes.
- [x] Add a shared English-English Dictionary reference to Study Knowledge and automatically attach English Wordbook entries with dictionary pronunciation and usage records while preserving user-authored meanings, phrases, examples and notes.
- [x] Add Wordbook dictionary refresh actions to the Vue and spatial Wordbook interfaces, including explicit unavailable and not-found states.
- [x] Remove the central in-world web panel and express module data through interactive physical models.
- [x] Replace the Study Plan tile wall with a Blender-authored orbital calendar: six week rings, 42 date nodes, a Goal core and a rising task ribbon.
- [x] Reuse the original room wall, trim, warm wood, paper, cyan, pink and gold material language across all module worlds.
- [ ] Backfill existing local documents into RAGFlow when original content is available.
- [x] Productize Plan Builder with Goal-owned long-term, monthly, weekly and daily node creation plus task ordering.
- [ ] Implement full Goal-aware Knowledge Space UI modes: exam isolation, reading bookshelf and knowledge cards.
- [ ] Add Work Agent capability after explicit design approval.
- [ ] Add richer Dynamic Resume editor, version comparison and user confirmation flow.
- [ ] Implement autonomous Memory extraction after explicit design approval.
- [x] Implement Wrong Questions, 1/3/7/30 Review queue, idempotent completion and Analytics summary integration.
- [ ] Complete cross-provider source-position verification beyond the locally validated RAGFlow provider.
- [ ] Add production PostgreSQL unit-of-work transaction for atomic Session finish across Task, Event and Memory.

## Spatial Universe Workspace

- [x] Expand the original room GLB by modifying the existing wall and floor geometry.
- [x] Add a wall-height Knowledge bookshelf using the original desk's warm wood color system.
- [x] Add Work and novel-writing furniture hotspots without duplicating Study or Work services.
- [x] Persist novel drafts through the shared repository boundary without adding a Novel Agent.
- [x] Keep the expanded room framed on desktop and narrow mobile viewports.
- [x] Pass three browser smoke-test rounds across 13 Study/Work routes and novel draft saving.
- [x] Replace static route overlays with API-driven spatial consoles and furniture-focus camera states.
- [x] Keep active Study, Knowledge and Work furniture visible beside responsive data consoles.
