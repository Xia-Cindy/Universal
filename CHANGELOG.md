# Changelog

## Unreleased

### Added

- Milestone 1 foundation backend structure, API contracts, Planet registry, Memory scope boundary, database foundation, and Study Workspace frontend shell.
- Milestone 2 Study learning workflow foundation: Goal, Plan, Daily Tasks, Study Sessions, Study Home progress aggregation, database migration, frontend Plan/Home workflow, and tests.
- Milestone 3 AI Core and Study Tutor foundation: shared AI Core entry point, deterministic LLM Gateway, Prompt/Context/Agent managers, Study Tutor consumer, Learning Events, Tutor API/frontend, and tests without RAG or embeddings.
- Milestone 3.5 AI Core generalization: AgentDefinition registry, context providers, prompt keys, provider-only LLM Gateway boundary, and tool interface preparation without RAG implementation.
- Milestone 4.1 Knowledge foundation: shared Knowledge service, File service foundation, document/chunk/concept models, database migration, Knowledge API/frontend, and tests without embeddings, vector storage, or Tutor integration.
- Milestone 4.2 Retrieval foundation: embedding provider abstraction, deterministic embedding provider, vector store interface, in-memory test store, chunk embedding pipeline, retrieval API, and tests without Tutor or RAG integration.
- Milestone 4.3 grounded Tutor foundation: AI Core ToolRouter invocation, RetrieverTool adapter, Knowledge context injection, grounded Tutor metadata, frontend grounding display, and tests without Knowledge Graph or new Agents.
- Milestone 5 Memory Intelligence foundation: shared Memory Manager, lifecycle/status fields, scoped retrieval, AI context preparation, Memory API, Tutor memory context payload, and tests without autonomous extraction or personality inference.
- Milestone 6 Study Intelligence foundation: Study Agent Analyst capability, Analytics service, progress metrics, structured reports, Analytics frontend, and tests without autonomous decisions, new Agents, or new Planets.
- Milestone 7 Study product learning loop: Study onboarding, manual plan productization, Study Home control center, session execution wrapper, factual Memory write points, Analytics insight integration, frontend loop screens, and tests without AI Core redesign or new Planets.
- Local browser run chain: Vite dev server now proxies `/api` to the local FastAPI backend and README documents the two-terminal startup flow.
- Study workspace experience update: Universe return navigation, configurable exam/learning/reading/growth goals, optional deadlines, real Knowledge file selection for txt/markdown/PDF metadata, and Home response aliases for progress, Knowledge overview and Analytics insight.
- Milestone 7.5 Study domain model refinement: reading goals, multiple goals with switching, multiple plans per goal, plan type separation, optional Knowledge goal links, normalized migration numbering, and compatibility tests without AI Core or RAG changes.
- Milestone 7.6 Study product workspace UX: Study Workspace aggregation API, Goal management page, current-Goal Home control center, guided Plan tree UI, Knowledge Goal filtering, and tests without AI Core, RAG, Memory, or Knowledge Graph expansion.
- Milestone 7.8.1 Study Workspace IA refactor: Current Goal header context, six-item Study navigation, Home primary-action hierarchy, single Plan Structure creation action, Knowledge upload enablement, workspace `planSummary`, and IA tests without AI Core, Retrieval, Memory, or database changes.
- Study Workspace smoke-test fixes: backend-owned `primaryAction`, completed-task action cleanup, PDF metadata status copy, Tutor empty-input validation, compact Goal switching, Goals IA grouping, human-readable Analytics language, and Review coming-later copy.
- Milestone 8.1 RAGFlow Knowledge provider adapter: provider config, RAGFlow upload/parse/chunk/retrieval client, provider metadata migration, backend Knowledge/ Retrieval routing, frontend provider status display, and mocked adapter tests while preserving local fallback.
- Local RAGFlow runtime stack: project-owned Docker Compose service under `docker/ragflow/`, local Universe env example, start/stop scripts, and installation guide.
- Milestone 7.9 Study productization slice: drilled Create Goal flow, Goal-type Knowledge Space preview, Study Plan Calendar, Daily Task priority, migration `010_study_plan_calendar_priority.sql`, and IA regression tests.
- Milestone 10.0 Work Planet foundation: active Work Planet entry, Work Workspace, Tech Stack directory/detail, project evidence records, Dynamic Resume drafts, Work APIs, migration `011_work_planet_foundation.sql`, and tests without a new AI system or Work Agent.
- Work Planet IA refinement: Work Knowledge is now a first-class workspace module, while Study Knowledge is treated as reference material through the shared Knowledge Service.
- Knowledge Space metadata refinement: documents now support Planet scope, Work Tech Stack binding and tags, while RAGFlow uses separate datasets for different Study Goals.
- Work Tech Stack content refinement: Tech Stacks now support owned articles and learning records, with directory-level content feed and resume evidence refs.
- Work Tech Stack navigation refinement: stack tabs now use actual Tech Stack names, Community tab shows CSDN public articles, and Work articles are typed as Knowledge or Note.
- Work Tech Stack directory workflow fix: Add Tech Stack now opens a modal, directory navigation uses a two-row category/stack structure, and the CSDN Community tab keeps 30 displayable discovery items when live fetch is unavailable.
- Work Community reading fix: CSDN articles can now expand inline inside Work Planet through a backend article detail endpoint, and Community loading no longer blocks switching back to `全部` or other directories.
- Work Tech Stack authoring refinement: Tech Stack detail now supports editing/archiving stacks and a focused article editor with an auto-generated left outline plus a compact title-level toolbar that inserts image, editable table and code content directly into the article body with basic text formatting and cell merge/split.
