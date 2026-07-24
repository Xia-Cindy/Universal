# Universe OS Operations And Recovery

## Persistence

- Local development defaults to SQLite at `UNIVERSE_DATABASE_PATH`.
- Production should set `PERSISTENCE_BACKEND=postgres` and `DATABASE_URL`.
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

## Email registration

Development defaults to a console sender and keeps the last verification code in the process for tests. Production should set `EMAIL_BACKEND=smtp` and provide `SMTP_HOST`, `SMTP_PORT`, `SMTP_USERNAME`, `SMTP_PASSWORD` and `SMTP_FROM` through a secret manager.
