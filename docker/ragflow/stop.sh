#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
RAGFLOW_DIR="$ROOT_DIR/docker/ragflow"

cd "$RAGFLOW_DIR"
if docker compose version >/dev/null 2>&1; then
  docker compose -f docker-compose.yml down
else
  docker-compose -f docker-compose.yml down
fi
