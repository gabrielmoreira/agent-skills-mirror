#!/bin/bash
# clawhip × OMC — Show last N lines of session output
# Usage: tail.sh <session-name> [lines]

SESSION="${1:?Usage: $0 <session-name> [lines]}"
LINES="${2:-20}"

if ! tmux has-session -t "$SESSION" 2>/dev/null; then
  echo "❌ Session not found: $SESSION"
  exit 1
fi

tmux capture-pane -t "$SESSION" -p -S "-$LINES"
