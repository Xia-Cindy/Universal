#!/usr/bin/env bash
set -euo pipefail

: "${DATABASE_URL:?DATABASE_URL is required}"
: "${BACKUP_FILE:?BACKUP_FILE is required}"
if [[ "${ALLOW_RESTORE:-}" != "1" ]]; then
  echo "Set ALLOW_RESTORE=1 to confirm a destructive PostgreSQL restore" >&2
  exit 1
fi

command -v pg_restore >/dev/null 2>&1 || { echo "pg_restore is required" >&2; exit 1; }
pg_restore --clean --if-exists --no-owner --dbname="$DATABASE_URL" "$BACKUP_FILE"
echo "PostgreSQL restore completed from $BACKUP_FILE"
