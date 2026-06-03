#!/usr/bin/env python3
"""Check workflow options boards for lifecycle drift."""

import argparse
from datetime import datetime, timezone
import importlib.util
import json
from pathlib import Path
import sys

SCRIPT_DIR = Path(__file__).resolve().parent
SCAFFOLD_SCRIPT = SCRIPT_DIR / "scaffold_workflow.py"


def load_scaffold_module():
    spec = importlib.util.spec_from_file_location("ub_workflow_scaffold", SCAFFOLD_SCRIPT)
    if spec is None or spec.loader is None:
        raise ImportError(f"Unable to load scaffold helper from {SCAFFOLD_SCRIPT.as_posix()}")
    module = importlib.util.module_from_spec(spec)
    sys.modules.setdefault(spec.name, module)
    spec.loader.exec_module(module)
    return module


SCAFFOLD_MODULE = load_scaffold_module()


def finding_payload(finding) -> dict[str, object]:
    try:
        file_name = finding.file_path.resolve().relative_to(finding.workflow_root.resolve())
    except ValueError:
        file_name = finding.file_path.resolve()
    return {
        "file"     : file_name.as_posix(),
        "line"     : finding.line_number,
        "category" : finding.category,
        "severity" : finding.severity,
        "message"  : finding.message,
    }


def build_payload(
    scan_root: Path,
    *,
    mode: str,
    stale_days: int,
    include_history: bool,
) -> dict[str, object]:
    workflow_root = SCAFFOLD_MODULE.discover_workflow_root(scan_root)
    findings = SCAFFOLD_MODULE.collect_workflow_options_findings(
        workflow_root,
        mode=mode,
        stale_days=stale_days,
        include_history=include_history,
        today=datetime.now(tz=timezone.utc).date(),
    )
    required_count = sum(1 for finding in findings if finding.severity == "required")
    advisory_count = len(findings) - required_count
    return {
        "status"        : "fail" if required_count else "pass",
        "scanRoot"      : scan_root.resolve().as_posix(),
        "workflowRoot"  : workflow_root.as_posix(),
        "mode"          : mode,
        "staleDays"     : stale_days,
        "includeHistory": include_history,
        "requiredCount" : required_count,
        "advisoryCount" : advisory_count,
        "summary"       : SCAFFOLD_MODULE.format_options_summary(workflow_root, findings),
        "findings"      : [finding_payload(finding) for finding in findings],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("scan_root", nargs="?", default=str(Path(".ub-workflows")))
    parser.add_argument("--strict", action="store_true")
    parser.add_argument(
        "--mode",
        choices=("normal", "closeout", "transition", "terminal-audit"),
        default="normal",
    )
    parser.add_argument("--stale-days", type=int, default=45)
    parser.add_argument("--include-history", action="store_true")
    parser.add_argument("--format", choices=("text", "json"), default="text")
    args = parser.parse_args()

    payload = build_payload(
        Path(args.scan_root).resolve(),
        mode=args.mode,
        stale_days=args.stale_days,
        include_history=args.include_history,
    )
    if args.format == "json":
        print(json.dumps(payload, indent=2))
    else:
        print(payload["summary"])
    return 1 if args.strict and payload["requiredCount"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
