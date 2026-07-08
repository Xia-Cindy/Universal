# Universe OS

Universe OS is a personal AI operating system built around Planet-based workspaces.

Milestone 1 implements the project foundation only:

- repository structure
- backend service boundaries
- database foundation migration and seed data
- Planet registry
- Universe Portal frontend shell
- Study Workspace shell
- basic API contracts

Milestone 2 adds the Study Planet learning workflow foundation:

- Goal management
- Learning Plan and Daily Tasks
- Study Session recording
- Study Home progress aggregation

Milestone 3 adds the AI Core and Tutor foundation:

- shared AI Core service entry point
- deterministic LLM Gateway for local tests
- Prompt Manager, Context Manager, and Agent Manager
- Study Tutor as an AI Core consumer
- Learning Events for Tutor interactions

Milestone 3 does not implement RAG, embeddings, Knowledge Graph, document retrieval, or source citations.

Milestone 3.5 generalizes AI Core boundaries:

- AgentDefinition registry
- context provider architecture
- prompt-key registry
- provider-only LLM Gateway input/output
- ToolRouter / Tool / Retriever interfaces only

Milestone 4.1 adds the Knowledge foundation:

- shared Knowledge service and File service foundation
- document, chunk, and concept models
- txt and markdown text processing
- database migration for documents, chunks, and concepts
- Knowledge API and Study Knowledge frontend page

Milestone 4.1 does not implement embeddings, vector storage, retrieval, RAG, AI summary, or Tutor integration.

Milestone 4.2 adds the Retrieval foundation:

- EmbeddingProvider abstraction and deterministic local provider
- VectorStore abstraction and in-memory test store
- chunk embedding metadata/status records
- chunk embedding preparation pipeline
- chunk-only retrieval service and API

Milestone 4.2 does not implement real vector database deployment, Tutor integration, RAG answer generation, or Knowledge Graph.

Milestone 4.3 connects Retrieval to Study Tutor through AI Core:

- AI Core ToolRouter execution for allowed tools
- RetrieverTool adapter over RetrievalService
- Knowledge chunk context injection for Tutor
- grounded Tutor metadata and Learning Event records
- Tutor UI grounding display

Milestone 4.3 does not implement Knowledge Graph, automatic summarization, Memory Intelligence, or new Agents.

The source of truth lives in `AGENTS.md` and `docs/`.

## Test

Run the dependency-light foundation tests:

```bash
python3 -m unittest discover -s tests
```

Frontend files are scaffolded for Vue 3 / Vite, but dependencies are not installed in this milestone.
