#!/usr/bin/env bash
set -euo pipefail

umask 077
DATABASE_PATH="${UNIVERSE_DATABASE_PATH:-database/universe.sqlite3}"
BACKUP_DIR="${BACKUP_DIR:-storage/backups/sqlite}"
mkdir -p "$BACKUP_DIR"
timestamp="$(date -u +%Y%m%dT%H%M%SZ)"
output="$BACKUP_DIR/universe-$timestamp.sqlite3"

if ! command -v sqlite3 >/dev/null 2>&1; then
  echo "sqlite3 CLI is required for SQLite backups" >&2
  exit 1
fi

sqlite3 "$DATABASE_PATH" ".backup '$output'"
echo "SQLite backup written to $output"
