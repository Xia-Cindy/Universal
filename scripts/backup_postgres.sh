#!/usr/bin/env bash
set -euo pipefail

umask 077
: "${DATABASE_URL:?DATABASE_URL is required}"
BACKUP_DIR="${BACKUP_DIR:-storage/backups/postgres}"
mkdir -p "$BACKUP_DIR"
timestamp="$(date -u +%Y%m%dT%H%M%SZ)"
output="$BACKUP_DIR/universe-$timestamp.dump"

command -v pg_dump >/dev/null 2>&1 || { echo "pg_dump is required" >&2; exit 1; }
pg_dump --format=custom --no-owner --file="$output" "$DATABASE_URL"
echo "PostgreSQL backup written to $output"
