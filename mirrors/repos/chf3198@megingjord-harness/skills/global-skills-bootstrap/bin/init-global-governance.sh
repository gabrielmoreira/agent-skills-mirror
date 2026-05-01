#!/usr/bin/env bash

set -euo pipefail

if [[ $# -lt 1 ]]; then
  echo "Usage: $0 /absolute/path/to/repo" >&2
  exit 1
fi

REPO_PATH="$1"
if [[ ! -d "$REPO_PATH" ]]; then
  echo "Repository path does not exist: $REPO_PATH" >&2
  exit 1
fi

SKILL_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TEMPLATE="$SKILL_ROOT/templates/global-skills.instructions.md"

mkdir -p "$REPO_PATH/.github/instructions" "$REPO_PATH/.github/workflows" "$REPO_PATH/.github/scripts" "$REPO_PATH/.githooks"

TARGET_INSTR="$REPO_PATH/.github/instructions/global-skills.instructions.md"
if [[ ! -f "$TARGET_INSTR" ]]; then
  cp "$TEMPLATE" "$TARGET_INSTR"
  echo "Created $TARGET_INSTR"
else
  echo "Kept existing $TARGET_INSTR"
fi

CHECK_SCRIPT="$REPO_PATH/.github/scripts/check-global-governance.sh"
if [[ ! -f "$CHECK_SCRIPT" ]]; then
  cat > "$CHECK_SCRIPT" <<'EOF'
#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
required=(
  "$ROOT_DIR/.github/instructions/global-skills.instructions.md"
)

for f in "${required[@]}"; do
  if [[ ! -f "$f" ]]; then
    echo "[global-governance] missing required file: $f"
    exit 1
  fi
done

echo "[global-governance] required files present"
EOF
  chmod +x "$CHECK_SCRIPT"
  echo "Created $CHECK_SCRIPT"
else
  echo "Kept existing $CHECK_SCRIPT"
fi

WORKFLOW="$REPO_PATH/.github/workflows/global-governance-presence.yml"
if [[ ! -f "$WORKFLOW" ]]; then
  cat > "$WORKFLOW" <<'EOF'
name: Global Governance Presence

on:
  pull_request:
  push:
    branches:
      - main
      - develop

permissions:
  contents: read

jobs:
  verify-global-governance:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v4
      - name: Verify global governance artifacts
        run: bash .github/scripts/check-global-governance.sh
EOF
  echo "Created $WORKFLOW"
else
  echo "Kept existing $WORKFLOW"
fi

PRE_COMMIT="$REPO_PATH/.githooks/pre-commit"
if [[ ! -f "$PRE_COMMIT" ]]; then
  cat > "$PRE_COMMIT" <<'EOF'
#!/usr/bin/env bash
set -euo pipefail
bash .github/scripts/check-global-governance.sh
EOF
  chmod +x "$PRE_COMMIT"
  echo "Created $PRE_COMMIT"
else
  echo "Kept existing $PRE_COMMIT"
fi

PRE_PUSH="$REPO_PATH/.githooks/pre-push"
if [[ ! -f "$PRE_PUSH" ]]; then
  cat > "$PRE_PUSH" <<'EOF'
#!/usr/bin/env bash
set -euo pipefail
bash .github/scripts/check-global-governance.sh
EOF
  chmod +x "$PRE_PUSH"
  echo "Created $PRE_PUSH"
else
  echo "Kept existing $PRE_PUSH"
fi

if git -C "$REPO_PATH" rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  git -C "$REPO_PATH" config core.hooksPath .githooks
  echo "Configured core.hooksPath=.githooks"
fi

echo "Global governance bootstrap complete for: $REPO_PATH"
