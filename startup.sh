#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
RUN_DIR="$ROOT_DIR/.universe-os"
LOG_DIR="$RUN_DIR/logs"
BACKEND_PID_FILE="$RUN_DIR/backend.pid"
ROOM_PID_FILE="$RUN_DIR/room.pid"

BACKEND_HOST="${BACKEND_HOST:-127.0.0.1}"
BACKEND_PORT="${BACKEND_PORT:-8000}"
ROOM_HOST="${ROOM_HOST:-127.0.0.1}"
ROOM_PORT="${ROOM_PORT:-5180}"

mkdir -p "$LOG_DIR"

is_running() {
  local pid_file="$1"
  [ -f "$pid_file" ] && kill -0 "$(cat "$pid_file")" 2>/dev/null
}

is_http_available() {
  local url="$1"
  curl --silent --fail --max-time 2 "$url" >/dev/null 2>&1
}

require_room_dependencies() {
  if [ ! -d "$ROOT_DIR/room-portfolio/node_modules" ]; then
    echo "room-portfolio/node_modules is missing. Run this first:"
    echo "  cd $ROOT_DIR/room-portfolio && npm install"
    exit 1
  fi
}

start_room() {
  if is_running "$ROOM_PID_FILE"; then
    echo "Room already running: pid $(cat "$ROOM_PID_FILE")"
    return
  fi
  if is_http_available "http://$ROOM_HOST:$ROOM_PORT/"; then
    rm -f "$ROOM_PID_FILE"
    echo "Room already running: http://$ROOM_HOST:$ROOM_PORT"
    return
  fi

  (
    cd "$ROOT_DIR/room-portfolio"
    exec npm run dev -- --host "$ROOM_HOST" --port "$ROOM_PORT"
  ) >"$LOG_DIR/room.log" 2>&1 &

  echo "$!" > "$ROOM_PID_FILE"
  sleep 1

  if is_running "$ROOM_PID_FILE"; then
    echo "Room started: http://$ROOM_HOST:$ROOM_PORT"
    echo "Room log: $LOG_DIR/room.log"
  else
    echo "Room failed to start. See: $LOG_DIR/room.log"
    exit 1
  fi
}

start_backend() {
  if is_running "$BACKEND_PID_FILE"; then
    echo "Backend already running: pid $(cat "$BACKEND_PID_FILE")"
    return
  fi
  if is_http_available "http://$BACKEND_HOST:$BACKEND_PORT/api/health"; then
    rm -f "$BACKEND_PID_FILE"
    echo "Backend already running: http://$BACKEND_HOST:$BACKEND_PORT"
    return
  fi

  (
    cd "$ROOT_DIR"
    set -a
    if [ -f "$ROOT_DIR/docker/universe.env" ]; then
      # Shared persistence settings must be available before the API imports.
      # shellcheck disable=SC1091
      . "$ROOT_DIR/docker/universe.env"
    fi
    if [ -f "$ROOT_DIR/docker/ragflow/universe.env" ]; then
      # Knowledge provider settings extend the shared runtime configuration.
      # shellcheck disable=SC1091
      . "$ROOT_DIR/docker/ragflow/universe.env"
    elif [ ! -f "$ROOT_DIR/docker/universe.env" ]; then
      export KNOWLEDGE_PROVIDER="${KNOWLEDGE_PROVIDER:-local}"
    fi
    set +a
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

require_room_dependencies
start_backend
start_room

echo
echo "Universe OS is running:"
echo "  Entry:    http://$ROOM_HOST:$ROOM_PORT"
echo "  API docs: http://$BACKEND_HOST:$BACKEND_PORT/docs"
