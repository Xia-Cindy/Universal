# Universe OS RAGFlow Installation

Version: 0.1

Document Type: Runtime Installation Guide

Status: Local Docker Compose Stack Added

Scope: Run RAGFlow as the Knowledge infrastructure for Universe OS.

---

# 1. Purpose

Universe OS uses RAGFlow as Knowledge infrastructure only.

Allowed path:

```text
Universe Frontend
→ Universe Backend API
→ KnowledgeService
→ KnowledgeProvider
→ RAGFlow API
```

Forbidden path:

```text
Frontend / Tutor / AI Core / Study Planet → RAGFlow
```

Universe remains responsible for:

- user ownership
- Study Goal relation
- subject and topic metadata
- frontend API contract
- AI Core and ToolRouter boundary

RAGFlow is responsible for:

- document storage
- parsing
- chunking
- embedding
- vector indexing
- retrieval

---

# 2. Prerequisites

Official RAGFlow self-hosting guidance expects:

- CPU >= 4 cores
- RAM >= 16 GB
- Disk >= 50 GB
- Docker >= 24.0.0
- Docker Compose >= v2.26.1

On Linux, Elasticsearch requires:

```bash
sysctl vm.max_map_count
sudo sysctl -w vm.max_map_count=262144
```

On macOS, Docker Desktop manages this differently. Give Docker Desktop enough memory before starting RAGFlow.

RAGFlow Docker images are x86. On Apple Silicon, Docker Desktop can run the stack through amd64 emulation, but startup and parsing can be slow.

---

# 3. Project Files

Universe OS keeps the local RAGFlow stack in:

```text
docker/ragflow/
├── docker-compose.yml
├── .env.example
├── universe.env.example
├── init.sql
├── start.sh
├── stop.sh
└── README.md
```

The stack starts:

- `ragflow`
- `es01`
- `mysql`
- `minio`
- `redis`

`infinity` is included as an optional Docker Compose profile for future testing,
but the default supported document engine remains Elasticsearch.

Only RAGFlow Web/API/Admin ports are exposed to the host by default.

---

# 4. Start RAGFlow

From the repository root:

```bash
cd /Users/xiaxin/Documents/Codex/Universal
cp docker/ragflow/.env.example docker/ragflow/.env
docker/ragflow/start.sh
```

The scripts use `docker compose` when available and fall back to `docker-compose`.

If Docker Hub or Elastic downloads are slow in China, use local-only mirror values
in `docker/ragflow/.env`:

```bash
RAGFLOW_IMAGE=swr.cn-north-4.myhuaweicloud.com/infiniflow/ragflow:v0.26.4
MYSQL_IMAGE=docker.m.daocloud.io/library/mysql:8.0.40
REDIS_IMAGE=docker.m.daocloud.io/library/redis:7-alpine
ES_IMAGE=docker.m.daocloud.io/elasticsearch:8.11.3
```

Open RAGFlow Web:

```text
http://127.0.0.1:8088
```

RAGFlow API:

```text
http://127.0.0.1:9380
```

Admin API:

```text
http://127.0.0.1:9381
```

---

# 5. Configure RAGFlow

After the RAGFlow UI is available:

1. Create or sign in to the local admin/user account.
2. Configure an embedding model/provider in RAGFlow.
3. Create an API key from RAGFlow.
4. Keep the API key local and do not commit it.

RAGFlow v0.22+ images do not include embedding models by default, so retrieval quality depends on the model/provider configured in RAGFlow.

---

# 6. Connect Universe Backend

Create a local Universe runtime env file:

```bash
cd /Users/xiaxin/Documents/Codex/Universal
cp docker/ragflow/universe.env.example docker/ragflow/universe.env
```

Edit `docker/ragflow/universe.env`:

```bash
KNOWLEDGE_PROVIDER=ragflow
RAGFLOW_BASE_URL=http://127.0.0.1:9380
RAGFLOW_API_KEY=<your-ragflow-api-key>
RAGFLOW_DATASET_ID=
RAGFLOW_DATASET_NAME=Universe OS Knowledge
```

Start Universe backend:

```bash
cd /Users/xiaxin/Documents/Codex/Universal
set -a
. docker/ragflow/universe.env
set +a
uvicorn backend.app.main:app --host 127.0.0.1 --port 8000
```

Start Universe frontend:

```bash
cd /Users/xiaxin/Documents/Codex/Universal/frontend
npm run dev -- --host 127.0.0.1 --port 5173
```

Open Universe:

```text
http://127.0.0.1:5173
```

---

# 7. Stop RAGFlow

Stop containers while preserving volumes:

```bash
cd /Users/xiaxin/Documents/Codex/Universal
docker/ragflow/stop.sh
```

Remove containers and volumes only when you intentionally want to delete local RAGFlow data:

```bash
cd docker/ragflow
docker-compose -f docker-compose.yml down -v
```

---

# 8. Verification

Check RAGFlow API:

```bash
curl http://127.0.0.1:9380
```

Check Universe backend:

```bash
curl http://127.0.0.1:8000/api/health
```

Upload a Knowledge document in Study Planet:

```text
Study Workspace → Knowledge → select file → Upload → Process
```

Expected result:

- document shows `provider: ragflow`
- processing status moves through `parsing` / `chunking`
- after RAGFlow chunks are available, Universe stores a local chunk preview cache
- Tutor retrieval still goes through AI Core ToolRouter and Universe RetrievalService

---

# 9. Troubleshooting

## RAGFlow cannot start on Apple Silicon

Keep:

```bash
RAGFLOW_PLATFORM=linux/amd64
```

Then make sure Docker Desktop has enough memory. If emulation is too slow, use an x86 Linux host for RAGFlow.

## Elasticsearch stays unhealthy

On Linux:

```bash
sudo sysctl -w vm.max_map_count=262144
```

Then restart the stack.

## Elasticsearch image download is slow

The Elasticsearch image contains a large layer. On this machine, the default
Elastic registry stalled while downloading that layer. Use:

```bash
ES_IMAGE=docker.m.daocloud.io/elasticsearch:8.11.3
```

Then re-run:

```bash
docker/ragflow/start.sh
```

Docker will reuse successfully downloaded images and layers where possible.

## Infinity does not become healthy

RAGFlow officially supports switching `DOC_ENGINE` from `elasticsearch` to
`infinity`, but also warns that Infinity is not supported on Linux/arm64.

On this macOS Colima environment, running `infiniflow/infinity:v0.7.0` through
`linux/amd64` emulation left the container in `health: starting` and generated a
`qemu_infinity_*.core` file. Treat Infinity as unavailable on this machine unless
it is moved to a native x86 Linux host.

## Universe says RAGFLOW_API_KEY is required

The backend was started with:

```bash
KNOWLEDGE_PROVIDER=ragflow
```

but `RAGFLOW_API_KEY` was empty. Create a RAGFlow API key and set it in `docker/ragflow/universe.env`.

## Documents remain chunking

RAGFlow parsing and indexing can be asynchronous. Re-run `Process` on the same Universe document to reuse the existing RAGFlow document id and refresh chunk previews. Production background polling remains future work.

---

# 10. References

- RAGFlow self-hosting README: https://github.com/infiniflow/ragflow
- RAGFlow Docker README: https://github.com/infiniflow/ragflow/blob/main/docker/README.md

---

# End
