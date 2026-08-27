# Universe OS RAGFlow Installation

Version: 0.2

Document Type: Runtime Installation Guide

Status: Local Docker Compose and provider lifecycle available; controlled TXT, Markdown and PDF acceptance recorded on 2026-08-13

Scope: Run RAGFlow as the Knowledge infrastructure for Universe OS.

> **Local deployment path (2026-08-27):** the runnable local RAGFlow Compose
> project has been moved out of this repository to
> `/Users/xiaxin/service/ragflow`. Run local `start.sh`, `stop.sh`, `.env` and
> `universe.env` commands from that directory. The `docker/ragflow` paths shown
> in older sections are historical references; they are not the active local
> deployment location.

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

## 2.1 Cloud preflight and isolated deployment

The cloud installation is a separate Compose project named `universe-ragflow`.
It owns RAGFlow, Elasticsearch, MySQL, MinIO, Valkey and their volumes; it does
not reuse Universe PostgreSQL, does not join the main Universe database, and
does not publish its API or admin port to the public Internet. The supplied
minimum checks intentionally match the official CPU deployment baseline:

- CPU >= 4 cores
- RAM >= 16 GiB
- free disk >= 50 GiB
- `vm.max_map_count >= 262144`

On the server, first run the non-mutating check:

```bash
cd /Universal
docker/ragflow/cloud-preflight.sh
```

Only after it passes, copy `docker/ragflow/cloud.env.example` to the private
`docker/ragflow/cloud.env`, replace every password, and set mode `0600`. Then
run `docker/ragflow/cloud-start.sh`. The default cloud bind address is
`127.0.0.1`; access the Web UI through an SSH tunnel rather than opening it on
the server IP. The Universe API uses `host.docker.internal:19380` only after an
RAGFlow API key is created in the RAGFlow UI and stored in the private
`docker/development/universe.env` file.

Do not lower the preflight values to force a start. A failed preflight is a
deployment record, not a partial RAGFlow installation. The host kernel setting
is outside the `/Universal` directory and requires explicit host-level
authorization.

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

For ordinary long-text sources, keep the dataset parser on the conservative
path: `Plain Text`, `RAPTOR: off`, `GraphRAG: off`, and no figure/visual
enhancement. Universe now sends this parser configuration when it creates a
new Goal- or Tech Stack-scoped RAGFlow dataset. It does not change existing
datasets or reparse their documents automatically. Use visual or graph
features only after separately validating their resource cost and output.

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
RAGFLOW_TIMEOUT_SECONDS=120
```

On Apple Silicon, the supported local RAGFlow image runs through amd64
emulation and can cold-start slowly. `RAGFLOW_TIMEOUT_SECONDS` only bounds one
Universe-to-RAGFlow request; it neither resubmits an existing document nor
changes RAGFlow's parser queue.

Start Universe backend:

```bash
cd /Users/xiaxin/Documents/Codex/Universal
set -a
. docker/ragflow/universe.env
set +a
uvicorn backend.app.main:app --host 127.0.0.1 --port 8000
```

Start the Universe spatial entry:

```bash
cd /Users/xiaxin/Documents/Codex/Universal/room-portfolio
npm run dev -- --host 127.0.0.1 --port 5180
```

Open Universe:

```text
http://127.0.0.1:5180/
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
Study Workspace → Knowledge → select file → Upload
```

Expected result:

- document shows `provider: ragflow`
- processing status moves through `parsing` / `chunking`
- provider-backed PDF, TXT and Markdown uploads enter processing; only a
  local-provider PDF remains metadata-only
- after RAGFlow chunks are available, Universe stores a local chunk preview cache
- Tutor retrieval still goes through AI Core ToolRouter and Universe RetrievalService, constrained to processed documents in the current Universe scope

## 8.1 Controlled local acceptance (2026-08-13)

The local provider was verified with three small new sources in an isolated
Study Goal dataset: TXT, Markdown and a one-page text-layer PDF. Each reached
RAGFlow `DONE` and Universe `processed` with one nonzero chunk. The PDF ran
with `Plain Text`, RAPTOR disabled and GraphRAG disabled; the executor log
recorded embedding and Elasticsearch indexing before completion.

Universe RetrievalService returned the PDF's mapped Universe document and
chunk identifiers. A Study Tutor request using the `all_study` scope returned
source links for all three acceptance files, including the PDF reader URL.
The 5180 Knowledge reader opened the processed PDF, rendered its real chunk
text on page `1 / 1`, and exposed correctly disabled previous/next controls.

This verification deliberately did not resubmit the existing long PDFs. On
Apple Silicon the supported amd64 image can take several minutes to cold-start;
if a worker is stuck with no task progress, cancel only the affected new task,
restore worker health, then resume that one approved sample after confirming
its parser configuration.

## 8.2 Adopt an existing RAGFlow document without reprocessing

Files uploaded in the RAGFlow administration UI do not automatically create a
Universe-owned Knowledge record. A controlled backend-only adoption endpoint
exists for that recovery path:

```text
POST /api/study/knowledge/documents/adopt-ragflow
```

Required metadata is the normal Knowledge `fileName`, `fileType`, `subject`
and `topic`, plus the existing `providerDatasetId` and `providerDocumentId`.
Before persisting anything, Universe verifies that exact dataset/document pair
through the provider. It then creates only the local ownership metadata and
refreshes the chunks already readable from RAGFlow. It does **not** upload a
file, submit a parse request, or reset the provider queue. Repeating the same
request refreshes the existing Universe record instead of duplicating it.

Use this recovery operation only for a document the current learner owns and
intends to manage through the Universe bookshelf. Once adopted, the ordinary
Universe delete action continues to delete its linked provider document, just
as it does for documents uploaded from Universe.

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

RAGFlow parsing and indexing can be asynchronous. Universe refreshes the provider status
and exposes returned chunk previews while processing continues. Do not repeatedly submit
or reparse a long PDF merely because its final state has not arrived: first inspect the
provider status and available chunks. Real TXT, Markdown and PDF `processed` acceptance
with a valid embedding provider remains a required separate verification.

---

# 10. References

- RAGFlow self-hosting README: https://github.com/infiniflow/ragflow
- RAGFlow Docker README: https://github.com/infiniflow/ragflow/blob/main/docker/README.md

---

# End
