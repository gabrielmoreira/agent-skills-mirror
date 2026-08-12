#!/usr/bin/env bash
# Run the shared routing benchmark through the Bash structured router.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BENCHMARK="$SCRIPT_DIR/../tests/routing-benchmark.json"
ROUTER="$SCRIPT_DIR/master-route.sh"

PYTHON=""
for candidate in python3 python; do
  if command -v "$candidate" >/dev/null 2>&1; then
    PYTHON="$candidate"
    break
  fi
done
if [[ -z "$PYTHON" ]]; then
  echo 'ERROR: Python 3 is required by the Bash routing benchmark runner.' >&2
  exit 2
fi

"$PYTHON" - "$BENCHMARK" "$ROUTER" <<'PY'
import json
import pathlib
import re
import subprocess
import sys
import tempfile

benchmark_path = pathlib.Path(sys.argv[1])
router_path = pathlib.Path(sys.argv[2])
benchmark = json.loads(benchmark_path.read_text(encoding="utf-8-sig"))
cases = benchmark["cases"]

failures = []
passed = 0
print(f"=== Bash routing benchmark | {len(cases)} cases ===")

with tempfile.TemporaryDirectory(prefix="rs-routing-bash-") as scratch:
    root = pathlib.Path(scratch)
    for index, case in enumerate(cases):
        hint = case["hint"]
        expected = case["expect"]
        out_dir = root / str(index)
        result = subprocess.run(
            ["bash", str(router_path), "--hint", hint, "--out-dir", str(out_dir)],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )

        got = "ERR"
        scope_path = out_dir / "route-scope.md"
        if result.returncode == 0 and scope_path.is_file():
            match = re.search(
                r"(?m)^- primary:[ \t]*(\S+)[ \t]*$",
                scope_path.read_text(encoding="utf-8"),
            )
            if match:
                got = match.group(1)

        if got == expected:
            passed += 1
        else:
            failures.append(
                f"hint={hint!r} expect={expected} got={got} exit={result.returncode}"
            )

print(f"TOTAL={len(cases)} PASS={passed} FAIL={len(failures)}")
if failures:
    for failure in failures:
        print(f"[FAIL] {failure}", file=sys.stderr)
    raise SystemExit(1)

print(f"OVERALL: ALL PASS ({passed})")
PY
