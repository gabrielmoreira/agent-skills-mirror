#!/usr/bin/env bash
set -euo pipefail

echo "[preflight] system memory"
free -h

echo "[preflight] process footprint (code/chrome/node playwright)"
ps -eo pid,ppid,comm,rss --sort=-rss \
  | awk 'BEGIN{print "PID PPID COMM RSS_KB"} NR>1 && ($3 ~ /code|chrome|chromium|node/){print $1, $2, $3, $4}' \
  | head -n 25

avail_kb=$(awk '/MemAvailable:/ {print $2}' /proc/meminfo)
if [[ -z "${avail_kb}" ]]; then
  echo "[preflight] unable to read MemAvailable" >&2
  exit 2
fi

avail_mb=$((avail_kb / 1024))
echo "[preflight] MemAvailable=${avail_mb}MB"

if (( avail_mb < 1500 )); then
  echo "[preflight] RISK=HIGH (available memory < 1500MB)"
  echo "[preflight] action: run local-smoke only (workers=1, no headed sessions, minimal artifacts)"
  exit 10
fi

if (( avail_mb < 2500 )); then
  echo "[preflight] RISK=MEDIUM"
  echo "[preflight] action: workers=1, chromium only, trace/video on failure only"
  exit 0
fi

echo "[preflight] RISK=LOW"
echo "[preflight] action: local-debug profile acceptable"
