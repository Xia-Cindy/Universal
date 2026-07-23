#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
RUN_DIR="$ROOT_DIR/.universe-os"
LOG_DIR="$RUN_DIR/logs"
BACKEND_PID_FILE="$RUN_DIR/backend.pid"
FRONTEND_PID_FILE="$RUN_DIR/frontend.pid"

BACKEND_HOST="${BACKEND_HOST:-127.0.0.1}"
BACKEND_PORT="${BACKEND_PORT:-8000}"
FRONTEND_HOST="${FRONTEND_HOST:-127.0.0.1}"
FRONTEND_PORT="${FRONTEND_PORT:-5173}"

mkdir -p "$LOG_DIR"

is_running() {
  local pid_file="$1"
  [ -f "$pid_file" ] && kill -0 "$(cat "$pid_file")" 2>/dev/null
}

require_frontend_dependencies() {
  if [ ! -d "$ROOT_DIR/frontend/node_modules" ]; then
    echo "frontend/node_modules is missing. Run this first:"
    echo "  cd $ROOT_DIR/frontend && npm install"
    exit 1
  fi
}

start_backend() {
  if is_running "$BACKEND_PID_FILE"; then
    echo "Backend already running: pid $(cat "$BACKEND_PID_FILE")"
    return
  fi

  (
    cd "$ROOT_DIR"
    if [ -f "$ROOT_DIR/docker/ragflow/universe.env" ]; then
      set -a
      # shellcheck disable=SC1091
      . "$ROOT_DIR/docker/ragflow/universe.env"
      set +a
    else
      export KNOWLEDGE_PROVIDER="${KNOWLEDGE_PROVIDER:-local}"
    fi
    exec python3 -m uvicorn backend.app.main:app --host "$BACKEND_HOST" --port "$BACKEND_PORT"
  ) >"$LOG_DIR/backend.log" 2>&1 &

  echo "$!" > "$BACKEND_PID_FILE"
  sleep 1

  if is_running "$BACKEND_PID_FILE"; then
    echo "Backend started: http://$BACKEND_HOST:$BACKEND_PORT"
    echo "Backend log: $LOG_DIR/backend.log"
  else
    echo "Backend failed to start. See: $LOG_DIR/backend.log"
    exit 1
  fi
}

start_frontend() {
  if is_running "$FRONTEND_PID_FILE"; then
    echo "Frontend already running: pid $(cat "$FRONTEND_PID_FILE")"
    return
  fi

  (
    cd "$ROOT_DIR/frontend"
    exec npm run dev -- --host "$FRONTEND_HOST" --port "$FRONTEND_PORT"
  ) >"$LOG_DIR/frontend.log" 2>&1 &

  echo "$!" > "$FRONTEND_PID_FILE"
  sleep 1

  if is_running "$FRONTEND_PID_FILE"; then
    echo "Frontend started: http://$FRONTEND_HOST:$FRONTEND_PORT"
    echo "Frontend log: $LOG_DIR/frontend.log"
  else
    echo "Frontend failed to start. See: $LOG_DIR/frontend.log"
    exit 1
  fi
}

require_frontend_dependencies
start_backend
start_frontend

echo
echo "Universe OS is running:"
echo "  App:      http://$FRONTEND_HOST:$FRONTEND_PORT"
echo "  API docs: http://$BACKEND_HOST:$BACKEND_PORT/docs"
