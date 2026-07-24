# TODO

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
- [x] Add Tech Stack update and archive actions.
- [x] Refine Tech Stack article writing into a focused editor with an auto-generated left outline.
- [x] Add compact title-level article tools that insert images, editable tables and code snippets directly into the article body, plus pasted image/table handling, bold text, text color, table row/column operations and cell merge/split.
- [x] Keep AI Core, Retrieval, RAGFlow and Memory architecture unchanged.
- [x] Keep Work Agent and autonomous resume generation out of scope.

## Later Milestones

- [ ] Connect Study services to PostgreSQL adapters.
- [ ] Connect Knowledge services to PostgreSQL adapters and object/file storage.
- [ ] Run production RAGFlow runtime validation with a real API key and embedding model configured.
- [ ] Add provider status polling and retry handling.
- [ ] Add provider-backed citation formatting for Tutor answers.
- [ ] Backfill existing local documents into RAGFlow when original content is available.
- [ ] Productize Plan Builder with editable long-term, monthly and weekly plan layers.
- [ ] Implement full Goal-aware Knowledge Space UI modes: exam isolation, reading bookshelf and knowledge cards.
- [ ] Add Work Agent capability after explicit design approval.
- [ ] Add richer Dynamic Resume editor, version comparison and user confirmation flow.
- [ ] Implement autonomous Memory extraction after explicit design approval.
- [ ] Implement Wrong Questions and Review.
