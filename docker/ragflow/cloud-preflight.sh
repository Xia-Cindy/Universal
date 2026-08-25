#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"

failures=0
check_minimum() {
  local label="$1" actual="$2" required="$3"
  if [ "$actual" -lt "$required" ]; then
    echo "FAIL $label: $actual < required $required"
    failures=1
  else
    echo "OK   $label: $actual"
  fi
}

check_minimum "CPU cores" "$(nproc)" 4
memory_kib="$(awk '/MemTotal:/ { print $2 }' /proc/meminfo)"
check_minimum "RAM MiB" "$((memory_kib / 1024))" 16384
disk_kib="$(df -Pk "$ROOT_DIR" | awk 'NR==2 { print $4 }')"
check_minimum "free disk MiB" "$((disk_kib / 1024))" 51200
map_count="$(sysctl -n vm.max_map_count)"
check_minimum "vm.max_map_count" "$map_count" 262144

if [ "$failures" -ne 0 ]; then
  echo "RAGFlow start is blocked. Do not lower these checks: the official CPU deployment baseline and Elasticsearch requirement are not met."
  exit 2
fi

echo "RAGFlow cloud preflight passed. Continue only with a private cloud.env and server-only model/provider credentials."
