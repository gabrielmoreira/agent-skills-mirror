#!/usr/bin/env python3
"""Read task-forest exports without modifying them."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
from typing import Any


EXPORTS = {
    "graph": Path(".agent-workbench/task-forest/exports/task-forest.graph.json"),
    "todos": Path(".agent-workbench/task-forest/exports/task-forest.todos.json"),
    "timeline": Path(".agent-workbench/task-forest/exports/task-forest.timeline.json"),
}


def read_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8", errors="replace"))
    except (OSError, json.JSONDecodeError):
        return None


def short(value: Any, limit: int = 220) -> str:
    if value is None:
        return ""
    text = value if isinstance(value, str) else json.dumps(value, ensure_ascii=False, sort_keys=True)
    text = " ".join(text.split())
    return text if len(text) <= limit else text[: max(0, limit - 1)] + "…"


def collect_records(obj: Any, keys: tuple[str, ...], limit: int) -> list[dict[str, str]]:
    records: list[dict[str, str]] = []

    def visit(value: Any) -> None:
        if len(records) >= limit:
            return
        if isinstance(value, dict):
            if any(k in value for k in keys):
                record: dict[str, str] = {}
                for key in ("id", "kind", "title", "status", "priority", "summary", "requirement", "acceptance", "description"):
                    if key in value and value[key] not in (None, ""):
                        record[key] = short(value[key])
                if record:
                    records.append(record)
            for child in value.values():
                visit(child)
        elif isinstance(value, list):
            for child in value:
                visit(child)

    visit(obj)
    return records


def summarize(workspace: Path) -> dict[str, Any]:
    out: dict[str, Any] = {"workspace": str(workspace), "found": False, "files": {}, "summary": {}}
    for name, rel in EXPORTS.items():
        path = workspace / rel
        meta: dict[str, Any] = {"path": str(path), "exists": path.exists()}
        if path.exists():
            stat = path.stat()
            data = read_json(path)
            meta.update({"mtime": stat.st_mtime, "size": stat.st_size, "parse_ok": data is not None})
            out["found"] = True
            if name == "graph" and data is not None:
                out["summary"]["graph_records"] = collect_records(data, ("title", "kind", "status"), 24)
            elif name == "todos" and data is not None:
                out["summary"]["todo_records"] = collect_records(data, ("title", "status", "priority"), 24)
            elif name == "timeline" and data is not None:
                out["summary"]["timeline_records"] = collect_records(data, ("event", "title", "summary", "status"), 16)
        out["files"][name] = meta
    return out


def main() -> int:
    parser = argparse.ArgumentParser(description="Read task-forest export summaries without modifying them.")
    parser.add_argument("--workspace", default=os.getcwd())
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    result = summarize(Path(args.workspace).expanduser().resolve())
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(f"workspace={result['workspace']}")
        print(f"task_forest_found={result['found']}")
        for name, meta in result["files"].items():
            print(f"{name}: exists={meta['exists']} path={meta['path']}")
        for key, records in result["summary"].items():
            print(f"\n{key}:")
            for record in records:
                title = record.get("title") or record.get("summary") or json.dumps(record, ensure_ascii=False)
                print(f"- {record.get('id', '-')}: {record.get('kind', record.get('status', '-'))}: {title}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
