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
