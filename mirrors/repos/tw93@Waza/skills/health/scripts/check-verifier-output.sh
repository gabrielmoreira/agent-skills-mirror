#!/usr/bin/env bash
set -euo pipefail

ROOT="${1:-.}"
LOG_FILE="${2:-}"

if [ -z "$LOG_FILE" ] || [ ! -f "$LOG_FILE" ]; then
  echo "Usage: $0 [repo-root] <log-file>" >&2
  exit 2
fi

if [ ! -d "$ROOT" ]; then
  echo "Repo root not found: $ROOT" >&2
  exit 2
fi

python3 - "$ROOT" "$LOG_FILE" <<'PY'
from __future__ import annotations

import re
import sys
from pathlib import Path

root = Path(sys.argv[1]).resolve()
log_file = Path(sys.argv[2]).resolve()
text = log_file.read_text(encoding="utf-8", errors="replace")

TOKEN_RE = re.compile(r"(?P<path>(?:/|\.\./)(?:[^\s:'\"(),]+/)*[^\s:'\"(),]+\.[A-Za-z0-9_+-]+)")
TMP_RE = re.compile(r"(^|/)(private/)?tmp/")


def normalize(token: str) -> Path:
    if token.startswith("/"):
        return Path(token)
    return (root / token).resolve()


paths: list[Path] = []
for match in TOKEN_RE.finditer(text):
    token = match.group("path").rstrip(".")
    if "/.git/" in token:
        continue
    path = normalize(token)
    if TMP_RE.search(path.as_posix()):
        paths.append(path)

unique_paths = []
seen = set()
for path in paths:
    value = path.as_posix()
    if value in seen:
        continue
    seen.add(value)
    unique_paths.append(path)

stale_paths = [path for path in unique_paths if not path.exists()]
existing_paths = [path for path in unique_paths if path.exists()]
lower = text.lower()

actions: list[str] = []
if stale_paths:
    if "golangci-lint" in lower or "errcheck" in lower:
        actions.append("golangci-lint cache clean")
    if re.search(r"\bgo (test|vet|build)\b", lower) or "go-build" in lower:
        actions.append("go clean -cache -testcache")
    if "npm" in lower or "node_modules" in lower:
        actions.append("npm cache verify")
    if not actions:
        actions.append("rerun the verifier after removing stale temporary worktrees")

status = "WARN" if stale_paths else "PASS"

print("=== VERIFIER OUTPUT SURFACE ===")
print(f"verifier_output_status: {status}")
print(f"log_file: {log_file}")
print("stale_paths:")
if stale_paths:
    for path in stale_paths[:20]:
        print(f"  {path}")
    if len(stale_paths) > 20:
        print(f"  ... {len(stale_paths) - 20} more")
else:
    print("  (none)")
print("existing_tmp_paths:")
if existing_paths:
    for path in existing_paths[:10]:
        print(f"  {path}")
    if len(existing_paths) > 10:
        print(f"  ... {len(existing_paths) - 10} more")
else:
    print("  (none)")
print("recommended_actions:")
if actions:
    for action in dict.fromkeys(actions):
        print(f"  {action}")
else:
    print("  (none)")
print("verifier_findings:")
if stale_paths:
    print("  stale external verifier paths detected")
else:
    print("  (none)")
PY
