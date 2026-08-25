#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
RAGFLOW_DIR="$ROOT_DIR/docker/ragflow"
ENV_FILE="$RAGFLOW_DIR/cloud.env"

if [ ! -f "$ENV_FILE" ]; then
  echo "Missing $ENV_FILE. Copy cloud.env.example, set strong private passwords, and chmod 600 it."
  exit 2
fi

if grep -q 'replace-with-a-long-random-secret' "$ENV_FILE"; then
  echo "cloud.env still contains placeholder credentials."
  exit 2
fi

"$RAGFLOW_DIR/cloud-preflight.sh"
docker compose --env-file "$ENV_FILE" -f "$RAGFLOW_DIR/docker-compose.yml" up -d
