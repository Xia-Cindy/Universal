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

## Later Milestones

- [ ] Connect Study services to PostgreSQL adapters.
- [ ] Connect Knowledge services to PostgreSQL adapters and object/file storage.
- [ ] Add production vector storage adapter.
- [ ] Implement Knowledge + RAG with citations.
- [ ] Implement autonomous Memory extraction after explicit design approval.
- [ ] Implement Wrong Questions and Review.
