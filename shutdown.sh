#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
RUN_DIR="$ROOT_DIR/.universe-os"
BACKEND_PID_FILE="$RUN_DIR/backend.pid"
ROOM_PID_FILE="$RUN_DIR/room.pid"

stop_process() {
  local name="$1"
  local pid_file="$2"

  if [ ! -f "$pid_file" ]; then
    echo "$name is not running: missing pid file"
    return
  fi

  local pid
  pid="$(cat "$pid_file")"

  if ! kill -0 "$pid" 2>/dev/null; then
    echo "$name is not running: stale pid $pid"
    rm -f "$pid_file"
    return
  fi

  kill "$pid"

  for _ in 1 2 3 4 5 6 7 8 9 10; do
    if ! kill -0 "$pid" 2>/dev/null; then
      rm -f "$pid_file"
      echo "$name stopped"
      return
    fi
    sleep 1
  done

  echo "$name did not stop within 10 seconds. PID remains: $pid"
  echo "Inspect logs or stop it manually if needed."
}

stop_process "Room" "$ROOM_PID_FILE"
stop_process "Backend" "$BACKEND_PID_FILE"
