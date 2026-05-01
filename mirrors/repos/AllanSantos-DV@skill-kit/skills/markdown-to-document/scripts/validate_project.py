"""
Validate an MSPDI XML file for common issues.

Usage:
    python validate_project.py output.xml
    python validate_project.py output.xml --json
    python validate_project.py output.xml --strict

Validates: task names, predecessors, cycles, orphans, durations, dates,
WBS consistency, resource assignments. No Java required — uses xml.etree.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import xml.etree.ElementTree as ET
from collections import defaultdict
from pathlib import Path

NS = "http://schemas.microsoft.com/project"


def _find(el: ET.Element, tag: str) -> str | None:
    """Find a child element text by tag name within the MSPDI namespace."""
    child = el.find(f"{{{NS}}}{tag}")
    if child is not None and child.text:
        return child.text.strip()
    return None


def _parse_iso_duration_hours(dur_str: str) -> float | None:
    """Parse MSPDI ISO duration like 'PT40H0M0S' into hours."""
    if not dur_str:
        return None
    m = re.match(r"PT(\d+)H(\d+)M(\d+)S", dur_str)
    if m:
        return int(m.group(1)) + int(m.group(2)) / 60 + int(m.group(3)) / 3600
    return None


def _parse_iso_datetime(dt_str: str) -> str | None:
    """Extract just the date part from '2026-04-01T08:00:00'."""
    if not dt_str:
        return None
    return dt_str[:10] if len(dt_str) >= 10 else dt_str


def _looks_placeholder(name: str) -> bool:
    """Check if a task name looks like a placeholder."""
    placeholders = {"tbd", "todo", "tba", "xxx", "placeholder", "untitled", "new task"}
    return name.strip().lower() in placeholders


def validate(xml_path: Path) -> dict:
    """Validate an MSPDI XML file and return structured results."""
    try:
        tree = ET.parse(str(xml_path))
    except ET.ParseError as e:
        return {
            "file": str(xml_path),
            "parse_error": str(e),
            "errors": [{"type": "PARSE_ERROR", "message": f"XML parse error: {e}"}],
            "warnings": [],
            "info": [],
        }

    root = tree.getroot()
    errors: list[dict] = []
    warnings: list[dict] = []
    info: list[dict] = []

    # --- Parse tasks ---
    tasks_el = root.find(f"{{{NS}}}Tasks")
    task_elements = tasks_el.findall(f"{{{NS}}}Task") if tasks_el is not None else []

    tasks: dict[str, dict] = {}  # uid -> task info
    name_count: dict[str, int] = defaultdict(int)

    for tel in task_elements:
        uid = _find(tel, "UID")
        if uid is None:
            continue

        name = _find(tel, "Name") or ""
        duration = _find(tel, "Duration")
        start = _find(tel, "Start")
        finish = _find(tel, "Finish")
        outline_level = _find(tel, "OutlineLevel")
        summary = _find(tel, "Summary")
        milestone = _find(tel, "Milestone")
        percent_complete = _find(tel, "PercentComplete")

        # Parse predecessors
        pred_links = []
        for pred_el in tel.findall(f"{{{NS}}}PredecessorLink"):
            pred_uid = _find(pred_el, "PredecessorUID")
            if pred_uid:
                pred_links.append(pred_uid)

        hours = _parse_iso_duration_hours(duration) if duration else None
        days = round(hours / 8, 2) if hours is not None else None

        is_summary = summary == "1" if summary else False
        is_milestone = milestone == "1" if milestone else False

        tasks[uid] = {
            "uid": uid,
            "name": name,
            "duration_hours": hours,
            "duration_days": days,
            "start": _parse_iso_datetime(start),
            "finish": _parse_iso_datetime(finish),
            "outline_level": int(outline_level) if outline_level else 0,
            "is_summary": is_summary,
            "is_milestone": is_milestone,
            "predecessors": pred_links,
            "raw_duration": duration,
        }
        if name:
            name_count[name] += 1

    # --- Parse resources ---
    resources_el = root.find(f"{{{NS}}}Resources")
    resource_elements = resources_el.findall(f"{{{NS}}}Resource") if resources_el is not None else []
    resource_uids: set[str] = set()
    for rel in resource_elements:
        ruid = _find(rel, "UID")
        if ruid:
            resource_uids.add(ruid)

    # --- Parse assignments ---
    assignments_el = root.find(f"{{{NS}}}Assignments")
    assignment_elements = assignments_el.findall(f"{{{NS}}}Assignment") if assignments_el is not None else []
    assignment_task_uids: set[str] = set()
    assignment_resource_uids: set[str] = set()
    for ael in assignment_elements:
        task_uid = _find(ael, "TaskUID")
        res_uid = _find(ael, "ResourceUID")
        if task_uid:
            assignment_task_uids.add(task_uid)
        if res_uid:
            assignment_resource_uids.add(res_uid)
            # Check: resource UID in assignment must exist
            if res_uid not in resource_uids and res_uid != "-65535":
                errors.append({
                    "type": "INVALID_RESOURCE_ASSIGNMENT",
                    "task_uid": task_uid,
                    "resource_uid": res_uid,
                    "message": f"Assignment references Resource UID {res_uid} which does not exist",
                })

    # --- Validation checks ---
    # Build successor map for orphan detection
    has_successor: set[str] = set()
    has_predecessor: set[str] = set()

    for uid, t in tasks.items():
        # Skip UID 0 (virtual root)
        if uid == "0":
            continue

        # 1. Tasks without name
        if not t["name"]:
            warnings.append({
                "type": "MISSING_NAME",
                "task_uid": uid,
                "message": f"Task UID {uid}: No name defined",
            })

        # 3. Invalid predecessor UIDs
        for pred_uid in t["predecessors"]:
            if pred_uid not in tasks:
                errors.append({
                    "type": "INVALID_PREDECESSOR",
                    "task_uid": uid,
                    "task_name": t["name"],
                    "predecessor_uid": pred_uid,
                    "message": f'Task UID {uid} "{t["name"]}": Predecessor UID {pred_uid} not found',
                })
            else:
                has_successor.add(pred_uid)
                has_predecessor.add(uid)

        # 6. Duration checks
        if t["duration_days"] is not None and not t["is_summary"]:
            if t["duration_days"] == 0 and not t["is_milestone"]:
                warnings.append({
                    "type": "ZERO_DURATION",
                    "task_uid": uid,
                    "task_name": t["name"],
                    "message": f'Task UID {uid} "{t["name"]}": Duration is 0 days but not marked as milestone',
                })
            if t["duration_days"] > 365:
                warnings.append({
                    "type": "UNREALISTIC_DURATION",
                    "task_uid": uid,
                    "task_name": t["name"],
                    "duration_days": t["duration_days"],
                    "message": f'Task UID {uid} "{t["name"]}": Duration {t["duration_days"]} days seems unrealistic',
                })

        # 7. Missing start dates without predecessors
        if not t["start"] and not t["predecessors"] and not t["is_summary"] and uid != "0":
            warnings.append({
                "type": "MISSING_START",
                "task_uid": uid,
                "task_name": t["name"],
                "message": f'Task UID {uid} "{t["name"]}": No start date and no predecessors',
            })

        # 10. Date inconsistency (finish < start)
        if t["start"] and t["finish"] and t["finish"] < t["start"]:
            errors.append({
                "type": "DATE_INCONSISTENCY",
                "task_uid": uid,
                "task_name": t["name"],
                "start": t["start"],
                "finish": t["finish"],
                "message": f'Task UID {uid} "{t["name"]}": Finish date ({t["finish"]}) is before start date ({t["start"]})',
            })

        # Placeholder name check
        if _looks_placeholder(t["name"]):
            warnings.append({
                "type": "PLACEHOLDER_NAME",
                "task_uid": uid,
                "task_name": t["name"],
                "message": f'Task UID {uid} "{t["name"]}": Name looks like a placeholder',
            })

    # 2. Duplicate task names
    for name, count in name_count.items():
        if count > 1 and name:
            warnings.append({
                "type": "DUPLICATE_NAME",
                "task_name": name,
                "count": count,
                "message": f'Task name "{name}" appears {count} times',
            })

    # 4. Predecessor loops (cycle detection via topological sort)
    # Build adjacency: task uid -> list of successor uids
    graph: dict[str, list[str]] = defaultdict(list)
    in_degree: dict[str, int] = defaultdict(int)
    all_nodes: set[str] = set()

    for uid, t in tasks.items():
        if uid == "0":
            continue
        all_nodes.add(uid)
        for pred_uid in t["predecessors"]:
            if pred_uid in tasks and pred_uid != "0":
                graph[pred_uid].append(uid)
                in_degree[uid] += 1
                all_nodes.add(pred_uid)

    # Kahn's algorithm
    queue = [n for n in all_nodes if in_degree[n] == 0]
    visited_count = 0
    visited_set: set[str] = set()

    while queue:
        node = queue.pop(0)
        visited_set.add(node)
        visited_count += 1
        for succ in graph.get(node, []):
            in_degree[succ] -= 1
            if in_degree[succ] == 0:
                queue.append(succ)

    if visited_count < len(all_nodes):
        # Find nodes in cycles
        cycle_nodes = all_nodes - visited_set
        # Try to trace a cycle
        cycle_desc = []
        for cn in cycle_nodes:
            t = tasks.get(cn, {})
            cycle_desc.append(f'UID {cn} "{t.get("name", "")}"')
        errors.append({
            "type": "CYCLE_DETECTED",
            "nodes": sorted(cycle_nodes),
            "message": f"Cycle detected involving: {', '.join(sorted(cycle_desc)[:5])}",
        })

    # 5. Orphan tasks
    for uid, t in tasks.items():
        if uid == "0" or t["is_summary"]:
            continue
        if uid not in has_successor and uid not in has_predecessor:
            # Only flag if it's not outline level 0/1 root
            if t["outline_level"] > 1 or len(tasks) > 2:
                info.append({
                    "type": "ORPHAN_TASK",
                    "task_uid": uid,
                    "task_name": t["name"],
                    "message": f'Task UID {uid} "{t["name"]}": Orphan (no predecessor/successor)',
                })

    # 8. WBS consistency (outline levels)
    prev_level = 0
    for uid in sorted(tasks.keys(), key=lambda x: int(x)):
        if uid == "0":
            continue
        t = tasks[uid]
        level = t["outline_level"]
        if level > prev_level + 1:
            warnings.append({
                "type": "WBS_GAP",
                "task_uid": uid,
                "task_name": t["name"],
                "expected_max": prev_level + 1,
                "actual": level,
                "message": f'Task UID {uid} "{t["name"]}": Outline level jumps from {prev_level} to {level}',
            })
        prev_level = level

    # Count totals
    task_count = len([u for u in tasks if u != "0"])
    resource_count = len([r for r in resource_uids if r != "0"])
    assignment_count = len(assignment_elements)

    return {
        "file": str(xml_path),
        "summary": {
            "tasks": task_count,
            "resources": resource_count,
            "assignments": assignment_count,
        },
        "errors": errors,
        "warnings": warnings,
        "info": info,
    }


def print_results(results: dict, as_json: bool = False) -> int:
    """Print validation results. Returns exit code."""
    if as_json:
        print(json.dumps(results, indent=2, ensure_ascii=False))
    else:
        file_name = Path(results["file"]).name
        s = results["summary"]
        print(f"Validating: {file_name}")
        print(f"  {s['tasks']} tasks, {s['resources']} resources, {s['assignments']} assignments")
        print()

        if results.get("parse_error"):
            print(f"  PARSE ERROR: {results['parse_error']}")
            print()

        if results["errors"]:
            print(f"Errors (must fix):")
            for e in results["errors"]:
                print(f"  \U0001f534 {e['message']}")
            print()

        if results["warnings"]:
            print(f"Warnings (review):")
            for w in results["warnings"]:
                print(f"  \U0001f7e1 {w['message']}")
            print()

        if results["info"]:
            print(f"Info:")
            for i in results["info"]:
                print(f"  \u2139 {i['message']}")
            print()

        total_e = len(results["errors"])
        total_w = len(results["warnings"])
        total_i = len(results["info"])
        print(f"Summary: {total_e} errors, {total_w} warnings, {total_i} info")

    return 1 if results["errors"] else 0


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Validate an MSPDI XML file for common issues."
    )
    parser.add_argument(
        "input",
        type=Path,
        help="Path to MSPDI XML file to validate."
    )
    parser.add_argument(
        "--json",
        action="store_true",
        dest="as_json",
        help="Output results as JSON."
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Treat warnings as errors (exit 1 if any warnings)."
    )
    args = parser.parse_args()

    if not args.input.is_file():
        print(f"Error: File not found: {args.input}", file=sys.stderr)
        sys.exit(1)

    results = validate(args.input)

    exit_code = print_results(results, as_json=args.as_json)

    if args.strict and results["warnings"]:
        exit_code = 1

    sys.exit(exit_code)


if __name__ == "__main__":
    main()
