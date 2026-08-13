# Universe OS Operations And Recovery

## Persistence

- Universe runtime defaults to PostgreSQL and requires `DATABASE_URL`.
- SQLite is available only when a local developer explicitly sets `PERSISTENCE_BACKEND=sqlite` and `UNIVERSE_DATABASE_PATH`.
- Both paths use the repository interfaces; Planet services do not know which adapter is active.
- File content uses local object storage in development and S3-compatible storage when `OBJECT_STORAGE_BACKEND=s3`.

## Backups

SQLite:

```bash
UNIVERSE_DATABASE_PATH=database/universe.sqlite3 scripts/backup_sqlite.sh
```

PostgreSQL:

```bash
DATABASE_URL="$DATABASE_URL" scripts/backup_postgres.sh
```

The PostgreSQL backup is a custom-format dump and should run at least daily in production, with encrypted off-host retention. Test restoration regularly in an isolated database:

```bash
ALLOW_RESTORE=1 DATABASE_URL="$RESTORE_DATABASE_URL" BACKUP_FILE=storage/backups/postgres/example.dump scripts/restore_postgres.sh
```

No credential may be committed to the repository. The scripts read connection values from the environment and use restrictive file permissions.

## RAGFlow runtime configuration

RAGFlow owns the embedding provider, LLM provider and rerank model. Universe OS only stores provider references and calls the provider adapter. Optional labels can be supplied without exposing secrets:

```bash
RAGFLOW_EMBEDDING_MODEL="<model label>"
RAGFLOW_LLM_MODEL="<model label>"
RAGFLOW_RERANK_MODEL="<model label>"
```

`GET /api/knowledge/provider/health` reports API reachability and these optional Universe-side labels. It does not claim that RAGFlow has successfully processed a file; runtime acceptance still requires TXT, Markdown and PDF samples to reach `processed` with asynchronous status polling.

### Explicit runtime verification before a bookshelf upload

`POST /api/knowledge/provider/runtime-verification` is the explicit runtime acceptance
check used by the 5180 Knowledge bookshelf before it creates a new RAGFlow-backed
document. It returns only `verified` or `failed`, a `checkedAt` timestamp, a stable
`errorCode`, and a user-safe message. It does **not** accept a file payload, create a
dataset, upload a document, persist a probe record, or schedule parsing.

When RAGFlow is enabled, the backend sends one fixed, tiny query through
`/api/v1/retrieval` against one already-`processed` document owned by the current
user. RAGFlow therefore executes its query embedding and retrieval paths, while no
user-provided text is sent by the probe. A missing processed source is deliberately a
`failed` result (`RAGFLOW_RUNTIME_NO_PROCESSED_SOURCE`) rather than creating a throwaway
dataset just to test the provider.

The bookshelf blocks a new RAGFlow upload when this response is not `verified` and
shows the safe reason instead. `GET /api/knowledge/provider/health` remains a reachability
diagnostic only; it is not an upload safety check.

## Email registration

Development defaults to a console sender and keeps the last verification code in the process for tests. Production should set `EMAIL_BACKEND=smtp` and provide `SMTP_HOST`, `SMTP_PORT`, `SMTP_USERNAME`, `SMTP_PASSWORD` and `SMTP_FROM` through a secret manager.
