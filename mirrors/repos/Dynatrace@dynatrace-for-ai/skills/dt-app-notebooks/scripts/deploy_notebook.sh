#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<EOF
Usage: $0 [--dry-run] <notebook.json>

Options:
  --dry-run   Validate and preview apply without persisting changes
  -h, --help  Show this help message
EOF
}

DRY_RUN=false
INPUT=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --dry-run)
      DRY_RUN=true
      shift
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    -*)
      echo "Error: Unknown option: $1" >&2
      usage >&2
      exit 1
      ;;
    *)
      if [[ -n "$INPUT" ]]; then
        echo "Error: Multiple input files provided" >&2
        usage >&2
        exit 1
      fi
      INPUT="$1"
      shift
      ;;
  esac
done

[[ -z "$INPUT" ]] && { usage >&2; exit 1; }

# ── Input guards ─────────────────────────────────────────────────
[[ -f "$INPUT" ]] || { echo "Error: File not found: $INPUT" >&2; exit 1; }
jq empty "$INPUT" 2>/dev/null || { echo "Error: File is not valid JSON: $INPUT" >&2; exit 1; }

# ── Validate ─────────────────────────────────────────────────────
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
EXECUTOR="$SCRIPT_DIR/notebook-validator.js"

VALIDATION_OUTPUT=$(cat "$INPUT" | jq '{notebook: .}' \
  | dtctl exec function -f "$EXECUTOR" --data - --plain \
  | jq -r .result) || {
  echo "Validation failed. Deployment aborted." >&2
  exit 1
}

echo "$VALIDATION_OUTPUT" >&2
echo "$VALIDATION_OUTPUT" | grep -q "VALIDATION SUCCEEDED" || {
  echo "Validation failed. Deployment aborted." >&2
  exit 1
}

# ── Deploy ───────────────────────────────────────────────────────
APPLY_ARGS=(-f "$INPUT" -o yaml --plain)
if [[ "$DRY_RUN" == "true" ]]; then
  APPLY_ARGS+=(--dry-run)
fi

APPLY_OUTPUT=$(dtctl apply "${APPLY_ARGS[@]}" 2>&1) || {
  echo "$APPLY_OUTPUT" >&2
  exit 1
}

echo "$APPLY_OUTPUT"

if [[ "$DRY_RUN" == "false" ]]; then
  rm -- "$INPUT"
  echo "Notebook deployed successfully. The local file has been deleted. To make further changes, download the deployed notebook first: dtctl get notebook <id> -o json --plain > notebook.json"
fi
