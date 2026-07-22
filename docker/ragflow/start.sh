#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
RAGFLOW_DIR="$ROOT_DIR/docker/ragflow"

if [ ! -f "$RAGFLOW_DIR/.env" ]; then
  cp "$RAGFLOW_DIR/.env.example" "$RAGFLOW_DIR/.env"
  echo "Created $RAGFLOW_DIR/.env from .env.example. Review passwords before shared deployment."
fi

cd "$RAGFLOW_DIR"
if docker compose version >/dev/null 2>&1; then
  docker compose -f docker-compose.yml up -d
else
  docker-compose -f docker-compose.yml up -d
fi
