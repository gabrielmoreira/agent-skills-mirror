#!/usr/bin/env bash
# loop-ctl.sh — quick start/stop/status for openloomi-loop
# Usage: ./loop-ctl.sh {start|stop|status|restart}
# Env:   LOOP_WEB_PORT=3614  INTERVAL=600  (10 min)
set -euo pipefail

SKILL_DIR="$(cd "$(dirname "$0")" && pwd)"
DATA="$SKILL_DIR/data"
LOOP=(node "$SKILL_DIR/scripts/openloomi-loop.cjs")
LOOP_WEB_PORT="${LOOP_WEB_PORT:-3614}"
INTERVAL="${INTERVAL:-600}"
DAEMON_PID="$DATA/daemon.pid"
WEB_PID="$DATA/web.pid"

is_alive() {
  [ -f "$1" ] && kill -0 "$(cat "$1")" 2>/dev/null
}

cmd_start() {
  # Recreate data/ if it was wiped (e.g. by an external cleanup). All loop
  # state — decisions, signals, pid files, inbox — lives here.
  mkdir -p "$DATA"

  if is_alive "$DAEMON_PID"; then
    echo "✗ schedule already running (pid=$(cat "$DAEMON_PID"))"
    return 1
  fi
  if is_alive "$WEB_PID"; then
    echo "✗ web already running (pid=$(cat "$WEB_PID"))"
    return 1
  fi

  rm -f "$DAEMON_PID" "$WEB_PID"

  # schedule: writes its own daemon.pid during init
  nohup "${LOOP[@]}" schedule --interval "$INTERVAL" > "$DATA/schedule.log" 2>&1 &
  disown 2>/dev/null || true

  # web
  nohup "${LOOP[@]}" web --port "$LOOP_WEB_PORT" > "$DATA/web.log" 2>&1 &
  local web_pid=$!
  echo "$web_pid" > "$WEB_PID"
  disown 2>/dev/null || true

  # Wait briefly for both to settle
  sleep 1

  local ok=1
  if is_alive "$DAEMON_PID"; then
    echo "✓ schedule started (pid=$(cat "$DAEMON_PID"), interval=${INTERVAL}s)"
  else
    echo "✗ schedule failed (see $DATA/schedule.log)"
    ok=0
  fi
  if lsof -i ":$LOOP_WEB_PORT" -P -n >/dev/null 2>&1; then
    echo "✓ web started (pid=$web_pid, http://127.0.0.1:$LOOP_WEB_PORT/)"
  else
    echo "✗ web failed (see $DATA/web.log)"
    ok=0
  fi
  return $((1 - ok))
}

cmd_stop() {
  local stopped=0
  for pf in "$DAEMON_PID" "$WEB_PID"; do
    if [ -f "$pf" ]; then
      local p; p=$(cat "$pf")
      if kill -0 "$p" 2>/dev/null; then
        kill "$p" 2>/dev/null && echo "✓ killed $(basename "$pf") pid=$p"
        stopped=$((stopped+1))
      fi
      rm -f "$pf"
    fi
  done
  # belt-and-suspenders: catch anything that escaped the pid files
  pkill -f "openloomi-loop.cjs (schedule|web)" 2>/dev/null || true
  pkill -f "loop-web.cjs $LOOP_WEB_PORT" 2>/dev/null || true
  if [ "$stopped" -eq 0 ]; then
    echo "(nothing was running)"
  fi
  return 0
}

cmd_status() {
  echo "=== loop status ==="
  "${LOOP[@]}" status || true
  echo ""
  echo "=== web port $LOOP_WEB_PORT ==="
  lsof -i ":$LOOP_WEB_PORT" -P -n 2>/dev/null | head -3 || echo "(not listening)"
  echo ""
  echo "=== pid files ==="
  for pf in "$DAEMON_PID" "$WEB_PID"; do
    if [ -f "$pf" ]; then
      local p; p=$(cat "$pf")
      if kill -0 "$p" 2>/dev/null; then
        printf "  %-12s %-8s  (alive)\n" "$(basename "$pf")" "$p"
      else
        printf "  %-12s %-8s  (stale — process gone)\n" "$(basename "$pf")" "$p"
      fi
    else
      printf "  %-12s (not present)\n" "$(basename "$pf")"
    fi
  done
}

case "${1:-}" in
  start)   cmd_start ;;
  stop)    cmd_stop ;;
  status)  cmd_status ;;
  restart) cmd_stop; cmd_start ;;
  *)       echo "usage: $0 {start|stop|status|restart}"; exit 1 ;;
esac
