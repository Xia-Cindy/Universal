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

Current Study Workspace polish adds configurable Goal types for exam, knowledge learning, reading, and growth goals; optional deadlines; multiple goals with switching; multiple plans per goal; a Universe Home return path; and Knowledge file selection for txt, markdown, and PDF metadata.

Milestone 7.6 refactors the Study frontend workflow around the current Goal:

- `/api/study/workspace` aggregates current Goal, all Goals, plan hierarchy, Today Tasks, Knowledge summary, and Analytics summary.
- Study Home shows the current Goal, Goal switcher, plan hierarchy, Today Tasks, learning summary, and Analytics-only AI insight.
- Goals page supports listing, creating, and switching exam, learning, reading, and growth goals.
- Plan page shows a guided current-Goal plan tree and daily tasks without exposing raw plan type fields.
- Knowledge page supports Goal filtering while still allowing independent Knowledge.

Milestone 7.8.1 stabilizes Study Workspace information architecture:

- Current Goal appears in the Study Workspace header with switching and a Goals management entry.
- Primary navigation stays focused on Home, Plan, Knowledge, Tutor, Review, and Analytics.
- Study Home focuses on the current Goal, Today Mission, Primary Action, Recent Progress, and Analytics-only AI Insight.
- Plan uses a single `Create Plan Structure` action and displays the Goal → Plan → Task hierarchy.
- Knowledge upload keeps the existing API and enables submission once a supported file, Subject, and Topic are present.

Post-7.8.1 smoke-test fixes align the product loop more closely with the PRD:

- Home and Workspace now use a backend-owned `primaryAction` as the single source for "what should I do next?"
- Completed tasks no longer offer a new Study Session action from Plan.
- PDF uploads are presented as metadata-only when PDF parsing is unavailable.
- Tutor blocks empty questions before submission.
- Goals, Analytics, Review, and the Study side panel use clearer product language for a personal learning workspace.

Milestone 8.1 connects Knowledge to RAGFlow through a backend provider adapter:

- `KNOWLEDGE_PROVIDER=local` remains the default local Knowledge path.
- `KNOWLEDGE_PROVIDER=ragflow` routes new Knowledge processing and retrieval through RAGFlow.
- Universe keeps document ownership, Goal relation, subject/topic metadata, and frontend API contracts.
- Frontend, Tutor, Study Planet, and AI Core do not call RAGFlow directly.

Milestone 7.9 starts Study productization from the latest design document:

- Create Goal now uses a drilled `/study/goals/new` flow with Goal type selection.
- Goal creation previews the Knowledge Space mode for exam, reading, learning, and growth goals.
- Study Plan adds a weekly Calendar view over Daily Tasks.
- Daily Tasks now have editable priority for Calendar planning.

Milestone 10.0 activates the Work Planet foundation:

- Universe Portal can enter Work Planet.
- Work Workspace includes Home, Tech Stack, Projects, and Dynamic Resume.
- Tech Stack detail can reference shared Knowledge through the backend Knowledge Service.
- Dynamic Resume drafts are evidence-based and do not invent experience.
- AI Core, Retrieval, RAGFlow, and Memory architecture remain unchanged.

Current Work Knowledge refinement adds a first-class Work Knowledge module. Work documents bind to Tech Stack and tags through the shared Knowledge Service. RAGFlow-backed Study Knowledge uses separate provider datasets for different Study Goals.

Work Tech Stack directories now support article writing and learning records, so each stack can collect knowledge, practice notes, project evidence and resume-ready proof in one place.

The Work Tech Stack page includes a Community tab for reading public CSDN topic articles. Community articles are discovery material only; they are not automatically imported into Work Knowledge.

The Tech Stack directory uses a two-row navigation pattern: first choose a category such as `全部` or `社区`, then choose a concrete Tech Stack inside that category. Creating a Tech Stack opens a modal form and does not move the directory layout.

CSDN Community articles can be expanded inline inside Work Planet. The backend keeps CSDN access behind Universe APIs; community content is still discovery material and is not automatically saved into Work Knowledge.

Tech Stack detail now includes stack management and a focused article editor. The writing surface behaves like a simple document editor: the left outline is generated from headings in the article body, and a compact toolbar under the title inserts images, editable tables and code snippets directly into the article body flow while supporting bold text, text color and basic table row/column operations.

The source of truth lives in `AGENTS.md` and `docs/`.

## Local Browser Run

For the normal local development loop, use the background startup script:

```bash
cd /Users/xiaxin/Documents/Codex/Universal
./startup.sh
```

Open:

```text
http://127.0.0.1:5173
```

Stop both frontend and backend:

```bash
cd /Users/xiaxin/Documents/Codex/Universal
./shutdown.sh
```

Runtime logs are written under `.universe-os/logs/`.

If `docker/ragflow/universe.env` exists, `startup.sh` loads it and starts the backend in the configured Knowledge provider mode. If it does not exist, the backend defaults to local Knowledge mode.

Manual startup is also supported.

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

## RAGFlow Knowledge Provider

Start the local RAGFlow stack from this project:

```bash
cd /Users/xiaxin/Documents/Codex/Universal
cp docker/ragflow/.env.example docker/ragflow/.env
docker/ragflow/start.sh
```

Open RAGFlow:

```text
http://127.0.0.1:8088
```

Create a RAGFlow API key, then start the backend with:

```bash
cp docker/ragflow/universe.env.example docker/ragflow/universe.env
# edit docker/ragflow/universe.env and set RAGFLOW_API_KEY
set -a
. docker/ragflow/universe.env
set +a
uvicorn backend.app.main:app --host 127.0.0.1 --port 8000
```

If `RAGFLOW_DATASET_ID` is empty, Universe asks RAGFlow to create a dataset named by `RAGFLOW_DATASET_NAME`.

Without those environment variables, Knowledge uses the local txt/markdown path and keeps PDF uploads as metadata-only.

Full installation notes live in `docs/06_RAGFLOW_INSTALLATION.md`.

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
