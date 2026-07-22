# Local RAGFlow Service

This folder runs a local RAGFlow service for Universe OS through Docker Compose.

The stack contains:

- RAGFlow Web/API
- Elasticsearch for document and vector indexing
- MySQL for RAGFlow metadata
- MinIO for file storage
- Valkey/Redis for queue/cache

## Start

```bash
cd /Users/xiaxin/Documents/Codex/Universal
cp docker/ragflow/.env.example docker/ragflow/.env
docker/ragflow/start.sh
```

The scripts use `docker compose` when available and fall back to `docker-compose`.

Open:

```text
http://127.0.0.1:8088
```

The RAGFlow API is exposed at:

```text
http://127.0.0.1:9380
```

## Connect Universe

Create an API key in the RAGFlow UI, then:

```bash
cp docker/ragflow/universe.env.example docker/ragflow/universe.env
```

Edit `docker/ragflow/universe.env` and set `RAGFLOW_API_KEY`.

Start Universe backend with:

```bash
cd /Users/xiaxin/Documents/Codex/Universal
set -a
. docker/ragflow/universe.env
set +a
uvicorn backend.app.main:app --host 127.0.0.1 --port 8000
```

## Stop

```bash
cd /Users/xiaxin/Documents/Codex/Universal
docker/ragflow/stop.sh
```

## Notes

- Do not use the default passwords outside local development.
- RAGFlow images are published for x86. On Apple Silicon, Docker Desktop may run them through amd64 emulation.
- RAGFlow requires an embedding model/provider configured in its UI before document parsing and retrieval are production-ready.
- Keep Universe frontend, Tutor, AI Core and Study Planet behind Universe backend APIs; do not call RAGFlow directly from them.
