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

Milestone 5 adds the Memory Intelligence foundation:

- shared Memory Manager repository/service boundary
- global, planet, and session scoped memory retrieval
- active, archived, and expired lifecycle states
- AI context preparation for active memory
- Memory API contracts
- Study Tutor memory context payload

Milestone 5 does not implement autonomous memory extraction, personality inference, Knowledge Graph, vector memory, new Agents, or new Planets.

Milestone 6 adds the Study Intelligence foundation:

- Study Analyst as a Study Agent capability
- Analytics service for progress metrics and learning insights
- structured Study reports through AI Core
- Memory context and optional Knowledge retrieval context
- Study Analytics frontend page

Milestone 6 does not implement autonomous decisions, personality inference, new Agents, or new Planets.

Milestone 7 completes the Study Planet product learning loop:

- Study onboarding for first active Goal creation
- manual Learning Plan creation, editing, and completion flow
- Study Home daily control center from live Study data
- Study Session execution wrapper with duration recording
- factual Memory write points through Memory Service
- existing Study Analyst insights shown in Study Home

Milestone 7 does not redesign AI Core, add new Agents, add new Planets, or implement autonomous planning.

Current Study Workspace polish adds configurable Goal types for exam, knowledge learning, and growth goals; optional deadlines; a Universe Home return path; and Knowledge file selection for txt, markdown, and PDF metadata.

The source of truth lives in `AGENTS.md` and `docs/`.

## Local Browser Run

Run the backend API in one terminal:

```bash
cd /Users/xiaxin/Documents/Codex/Universal
uvicorn backend.app.main:app --host 127.0.0.1 --port 8000
```

Run the frontend workspace in another terminal:

```bash
cd /Users/xiaxin/Documents/Codex/Universal/frontend
npm install
npm run dev -- --host 127.0.0.1 --port 5173
```

Open:

```text
http://127.0.0.1:5173
```

The Vite dev server proxies `/api` requests to `http://127.0.0.1:8000`, so the browser can use Universe Portal, Study onboarding, Plan, Session, Knowledge, Tutor and Analytics from the frontend.

Backend API docs are available at:

```text
http://127.0.0.1:8000/docs
```

## Test

Run the dependency-light foundation tests:

```bash
python3 -m unittest discover -s tests
```

Frontend validation:

```bash
cd frontend
npm install
npm run build
```
