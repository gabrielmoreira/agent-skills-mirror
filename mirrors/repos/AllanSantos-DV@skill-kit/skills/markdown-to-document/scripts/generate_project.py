"""
Generate an MSPDI XML file (MS Project) from JSON input.

Usage:
    python generate_project.py input.json -o output.xml
    python generate_project.py input.json -o output.xml --java-home "C:\\Program Files\\Java\\jdk-17"
    python generate_project.py inject.json -t template.xml -o output.xml --mode inject

Input format (JSON) — generate mode:
    {
      "tasks": [
        {
          "name": "Task Name",
          "start": "2026-04-01",
          "duration": "5d",
          "predecessors": [1],
          "resources": ["PM"],
          "outline_level": 1,
          "summary": true,
          "children": [...],
          "notes": "Some notes",
          "percent_complete": 50,
          "constraint_type": "SNET",
          "constraint_date": "2026-04-01",
          "priority": 500,
          "custom_fields": {"text1": "val", "number1": 42, "flag1": true}
        }
      ],
      "resources": [
        {"name": "PM", "type": "work", "group": "Mgmt", "standard_rate": 100, "max_units": 100}
      ],
      "calendar": {
        "name": "Standard",
        "working_days": ["MON", "TUE", "WED", "THU", "FRI"],
        "hours": {"start": "08:00", "end": "17:00"}
      }
    }

Input format (JSON) — inject mode:
    {
      "tasks": [
        {"task_uid": 5, "name": "Updated Name", "duration": "8d"},
        {"task_name": "Design", "notes": "Updated notes"},
        {"name": "New Task", "duration": "3d", "start": "2026-05-01"}
      ]
    }

Duration formats: "5d" (days), "8h" (hours), "2w" (weeks)
Predecessors: 1-based index (int) or {"task": id, "type": "FS"|"SS"|"FF"|"SF", "lag": "2d"}

Requires: pip install mpxj  (and Java 11+)
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import xml.etree.ElementTree as ET
from pathlib import Path


def _ensure_package(import_name: str, pip_name: str | None = None) -> bool:
    """Try to import a package; auto-install if non-interactive. Returns True if available."""
    pip_name = pip_name or import_name
    try:
        __import__(import_name)
        return True
    except (ImportError, OSError):
        pass

    if sys.stdin.isatty():
        answer = input(f'Package "{pip_name}" is not installed. Install it now? [Y/n] ').strip().lower()
        if answer in ("", "y", "yes"):
            subprocess.check_call([sys.executable, "-m", "pip", "install", pip_name])
            return True
        return False
    else:
        print(f"Auto-installing missing package: {pip_name}", file=sys.stderr)
        subprocess.check_call([sys.executable, "-m", "pip", "install", pip_name])
        __import__(import_name)  # verify
        return True


def check_java(min_version: int = 11, java_home: str | None = None) -> str | None:
    """Check if Java is available and meets the minimum version. Returns java path or None."""
    # Try runtime_resolver if available
    resolver = Path(__file__).parent / "runtime_resolver.py"
    if resolver.is_file():
        extra = []
        if java_home:
            extra = ["--extra-paths", java_home]
        try:
            result = subprocess.run(
                [sys.executable, str(resolver), "java",
                 "--min-version", str(min_version)] + extra,
                capture_output=True, text=True, timeout=30
            )
            if result.returncode == 0:
                import json as _json
                info = _json.loads(result.stdout)
                if info.get("found"):
                    return info.get("path")
        except Exception:
            pass

    # Direct check
    java_cmd = "java"
    if java_home:
        candidate = Path(java_home) / "bin" / "java"
        if candidate.is_file():
            java_cmd = str(candidate)
        candidate_exe = Path(java_home) / "bin" / "java.exe"
        if candidate_exe.is_file():
            java_cmd = str(candidate_exe)

    try:
        result = subprocess.run(
            [java_cmd, "-version"],
            capture_output=True, text=True, timeout=10
        )
        # Java outputs version to stderr
        output = result.stderr or result.stdout
        if output:
            return java_cmd
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass

    return None


def load_input(input_path: Path) -> dict:
    """Load and validate JSON input. Returns full data dict."""
    text = input_path.read_text(encoding="utf-8")
    try:
        data = json.loads(text)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in {input_path}: {e}", file=sys.stderr)
        sys.exit(1)
    if "tasks" not in data:
        print("Error: JSON must have a 'tasks' key.", file=sys.stderr)
        sys.exit(1)
    return data


def parse_duration(dur_str: str) -> tuple[float, str]:
    """Parse duration string like '5d', '8h', '2w' into (value, unit)."""
    dur_str = dur_str.strip().lower()
    if dur_str.endswith("w"):
        return float(dur_str[:-1]) * 5, "DAYS"
    elif dur_str.endswith("h"):
        return float(dur_str[:-1]), "HOURS"
    elif dur_str.endswith("d"):
        return float(dur_str[:-1]), "DAYS"
    else:
        try:
            return float(dur_str), "DAYS"
        except ValueError:
            print(f"Warning: Cannot parse duration '{dur_str}', defaulting to 1 day.", file=sys.stderr)
            return 1.0, "DAYS"


def _resolve_java_home(java_path: str) -> Path | None:
    """Resolve the actual JAVA_HOME from a java executable path.

    Handles symlinks, Oracle shims, and non-standard paths by querying
    the Java process for its java.home property as a fallback.
    """
    resolved = Path(java_path).resolve()
    # Standard JDK layout: <JAVA_HOME>/bin/java[.exe]
    if resolved.parent.name.lower() == "bin":
        return resolved.parent.parent

    # Non-standard path (e.g., Oracle shim) — ask Java itself
    try:
        result = subprocess.run(
            [java_path, "-XshowSettings:properties", "-version"],
            capture_output=True, text=True, timeout=10,
        )
        for line in (result.stderr or "").splitlines():
            if "java.home" in line and "=" in line:
                return Path(line.split("=", 1)[1].strip())
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass
    return None


def _find_jvm_dll(jdk_home: Path) -> str | None:
    """Locate the JVM shared library inside a JDK home directory."""
    if sys.platform == "win32":
        candidates = [
            jdk_home / "bin" / "server" / "jvm.dll",
            jdk_home / "bin" / "client" / "jvm.dll",
        ]
    elif sys.platform == "darwin":
        candidates = [
            jdk_home / "lib" / "server" / "libjvm.dylib",
            jdk_home / "lib" / "client" / "libjvm.dylib",
        ]
    else:
        candidates = [
            jdk_home / "lib" / "server" / "libjvm.so",
            jdk_home / "lib" / "client" / "libjvm.so",
        ]

    for c in candidates:
        if c.is_file():
            return str(c)
    return None


def _parse_lag_duration(lag_str: str) -> float:
    """Parse a lag string like '2d', '4h' into days (float)."""
    val, unit = parse_duration(lag_str)
    if unit == "HOURS":
        return val / 8.0  # 8h per day
    return val


# Map of constraint type short names to MPXJ ConstraintType enum names
CONSTRAINT_MAP = {
    "ASAP": "AS_SOON_AS_POSSIBLE",
    "ALAP": "AS_LATE_AS_POSSIBLE",
    "SNET": "START_NO_EARLIER_THAN",
    "SNLT": "START_NO_LATER_THAN",
    "FNET": "FINISH_NO_EARLIER_THAN",
    "FNLT": "FINISH_NO_LATER_THAN",
    "MSO": "MUST_START_ON",
    "MFO": "MUST_FINISH_ON",
}

# Map of predecessor type short names to MPXJ RelationType enum names
RELATION_TYPE_MAP = {
    "FS": "FINISH_START",
    "SS": "START_START",
    "FF": "FINISH_FINISH",
    "SF": "START_FINISH",
}


def _flatten_tasks(tasks_data: list[dict], parent_level: int = 0) -> list[tuple[dict, int, int | None]]:
    """Flatten a hierarchical task list into (task_data, level, parent_flat_index).

    Returns a flat list where each entry is (task_dict, outline_level, parent_index).
    parent_index is the index in the flat list of the parent task, or None for roots.
    """
    result: list[tuple[dict, int, int | None]] = []

    for td in tasks_data:
        level = td.get("outline_level", parent_level + 1) if parent_level > 0 else td.get("outline_level", 1)
        if parent_level == 0 and "outline_level" not in td and "children" not in td:
            level = 1  # flat tasks default to level 1
        current_idx = len(result)
        parent_idx = None
        # find parent: last item at level-1 that is a summary
        if parent_level > 0:
            for ri in range(len(result) - 1, -1, -1):
                if result[ri][1] == parent_level:
                    parent_idx = ri
                    break
        result.append((td, level, parent_idx))

        children = td.get("children", [])
        if children:
            for child in children:
                child_level = child.get("outline_level", level + 1)
                child_idx = len(result)
                result.append((child, child_level, current_idx))
                # Recurse for grandchildren
                grandchildren = child.get("children", [])
                if grandchildren:
                    sub = _flatten_tasks(grandchildren, parent_level=child_level)
                    for sub_td, sub_level, sub_parent in sub:
                        if sub_parent is not None:
                            result.append((sub_td, sub_level, sub_parent + child_idx))
                        else:
                            result.append((sub_td, sub_level, child_idx))

    return result


def generate(data: dict, output_path: Path, java_path: str) -> None:
    """Generate MSPDI XML using MPXJ."""
    # Resolve the actual JDK home and JVM library path
    jdk_home = _resolve_java_home(java_path)
    jvm_path = _find_jvm_dll(jdk_home) if jdk_home else None

    # Set JAVA_HOME so mpxj/jpype internals can use it
    if jdk_home:
        os.environ["JAVA_HOME"] = str(jdk_home)

    if not _ensure_package("mpxj"):
        print("Error: mpxj is required.", file=sys.stderr)
        sys.exit(1)
    if not _ensure_package("jpype", "jpype1"):
        print("Error: jpype1 is required.", file=sys.stderr)
        sys.exit(1)

    import mpxj  # noqa: F401 — adds MPXJ jars to classpath
    import jpype
    try:
        if not jpype.isJVMStarted():
            if jvm_path:
                jpype.startJVM(jvm_path)
            else:
                jpype.startJVM()
    except Exception as e:
        print(f"Error starting JVM: {e}", file=sys.stderr)
        print("Ensure JAVA_HOME is set correctly or pass --java-home.", file=sys.stderr)
        sys.exit(1)

    try:
        from org.mpxj import (
            ProjectFile, Duration, TimeUnit, Relation,
            ConstraintType, Priority, ResourceType,
        )
        from org.mpxj.mspdi import MSPDIWriter
        from java.time import LocalDateTime, LocalTime
    except Exception:
        print("Error: Failed to load MPXJ Java classes. Ensure mpxj and jpype1 are installed.", file=sys.stderr)
        sys.exit(1)

    tasks_data = data.get("tasks", [])
    resources_data = data.get("resources", [])
    calendar_data = data.get("calendar", None)

    project = ProjectFile()

    # --- Calendar setup ---
    if calendar_data:
        try:
            from org.mpxj import DayType, ProjectCalendar
            cal = project.addCalendar()
            cal.setName(calendar_data.get("name", "Standard"))
            project.setDefaultCalendar(cal)

            day_map = {
                "MON": "MONDAY", "TUE": "TUESDAY", "WED": "WEDNESDAY",
                "THU": "THURSDAY", "FRI": "FRIDAY", "SAT": "SATURDAY", "SUN": "SUNDAY",
            }
            working_days = set(calendar_data.get("working_days", ["MON", "TUE", "WED", "THU", "FRI"]))
            for short, full in day_map.items():
                try:
                    day = DayType.valueOf(full)
                    if short in working_days:
                        cal.setWorkingDay(day, True)
                    else:
                        cal.setWorkingDay(day, False)
                except Exception:
                    pass

            hours = calendar_data.get("hours", {})
            if hours.get("start") and hours.get("end"):
                try:
                    start_parts = hours["start"].split(":")
                    end_parts = hours["end"].split(":")
                    start_time = LocalTime.of(int(start_parts[0]), int(start_parts[1]))
                    end_time = LocalTime.of(int(end_parts[0]), int(end_parts[1]))
                    from org.mpxj import ProjectCalendarHours
                    for short in working_days:
                        if short in day_map:
                            try:
                                day = DayType.valueOf(day_map[short])
                                cal_hours = cal.addCalendarHours(day)
                                from org.mpxj import LocalTimeRange
                                cal_hours.add(LocalTimeRange(start_time, end_time))
                            except Exception:
                                pass
                except Exception:
                    pass
        except Exception as e:
            print(f"Warning: Could not set calendar: {e}", file=sys.stderr)

    # --- Resources ---
    resource_map: dict[str, object] = {}

    # Pre-create resources from resources_data
    for res_data in resources_data:
        res_name = res_data.get("name", "")
        if not res_name or res_name in resource_map:
            continue
        resource = project.addResource()
        resource.setName(res_name)

        # Resource type
        rtype = res_data.get("type", "work").upper()
        try:
            resource.setType(ResourceType.valueOf(rtype))
        except Exception:
            try:
                resource.setType(ResourceType.WORK)
            except Exception:
                pass

        # Group
        if res_data.get("group"):
            resource.setGroup(res_data["group"])

        # Max units
        if res_data.get("max_units") is not None:
            try:
                from java.lang import Double
                resource.setMaxUnits(Double(float(res_data["max_units"])))
            except Exception:
                pass

        # Standard rate
        if res_data.get("standard_rate") is not None:
            try:
                from org.mpxj import Rate
                rate = Rate(float(res_data["standard_rate"]), TimeUnit.HOURS)
                resource.setStandardRate(rate)
            except Exception:
                pass

        resource_map[res_name] = resource

    # --- Flatten tasks (handle hierarchy) ---
    has_hierarchy = any(t.get("children") for t in tasks_data)

    if has_hierarchy:
        flat_tasks = _flatten_tasks(tasks_data)
    else:
        flat_tasks = [(td, td.get("outline_level", 1), None) for td in tasks_data]

    # --- Create tasks ---
    created_tasks: list[object] = []
    task_parent_map: dict[int, int] = {}  # flat_idx -> parent_flat_idx

    for flat_idx, (task_data, level, parent_idx) in enumerate(flat_tasks):
        # Always create via project.addTask(), establish hierarchy via outline level
        task = project.addTask()

        if parent_idx is not None and 0 <= parent_idx < len(created_tasks):
            task_parent_map[flat_idx] = parent_idx
            # Move the task under its parent using addChildTask(Task)
            try:
                created_tasks[parent_idx].addChildTask(task)
            except Exception:
                pass

        task.setName(task_data.get("name", f"Task {flat_idx + 1}"))

        # Outline level
        try:
            task.setOutlineLevel(int(level))
        except Exception:
            pass

        # Summary flag
        if task_data.get("summary"):
            try:
                task.setSummary(True)
            except Exception:
                pass

        # Start date
        if task_data.get("start"):
            parts = task_data["start"].split("-")
            task.setStart(LocalDateTime.of(int(parts[0]), int(parts[1]), int(parts[2]), 8, 0))

        # Duration
        if task_data.get("duration"):
            dur_val, dur_unit = parse_duration(task_data["duration"])
            unit = TimeUnit.DAYS if dur_unit == "DAYS" else TimeUnit.HOURS
            task.setDuration(Duration.getInstance(dur_val, unit))

        # Notes
        if task_data.get("notes"):
            try:
                task.setNotes(task_data["notes"])
            except Exception:
                pass

        # Percent complete
        if task_data.get("percent_complete") is not None:
            try:
                from java.lang import Double
                task.setPercentageComplete(Double(float(task_data["percent_complete"])))
            except Exception:
                pass

        # Constraint
        if task_data.get("constraint_type"):
            try:
                ct_name = CONSTRAINT_MAP.get(
                    task_data["constraint_type"].upper(),
                    task_data["constraint_type"].upper()
                )
                ct = ConstraintType.valueOf(ct_name)
                task.setConstraintType(ct)
                if task_data.get("constraint_date"):
                    cd_parts = task_data["constraint_date"].split("-")
                    task.setConstraintDate(
                        LocalDateTime.of(int(cd_parts[0]), int(cd_parts[1]), int(cd_parts[2]), 8, 0)
                    )
            except Exception as e:
                print(f"Warning: Could not set constraint on '{task_data.get('name')}': {e}", file=sys.stderr)

        # Priority
        if task_data.get("priority") is not None:
            try:
                task.setPriority(Priority.getInstance(int(task_data["priority"])))
            except Exception:
                pass

        # Custom fields
        custom = task_data.get("custom_fields", {})
        for key, val in custom.items():
            key_lower = key.lower()
            try:
                if key_lower.startswith("text"):
                    idx = int(key_lower.replace("text", ""))
                    task.setText(idx, str(val))
                elif key_lower.startswith("number"):
                    idx = int(key_lower.replace("number", ""))
                    from java.lang import Double
                    task.setNumber(idx, Double(float(val)))
                elif key_lower.startswith("flag"):
                    idx = int(key_lower.replace("flag", ""))
                    task.setFlag(idx, bool(val))
            except Exception:
                pass

        created_tasks.append(task)

    # --- Predecessors ---
    for flat_idx, (task_data, level, parent_idx) in enumerate(flat_tasks):
        preds = task_data.get("predecessors", [])
        for pred in preds:
            pred_idx: int | None = None
            rel_type_name = "FINISH_START"
            lag_duration = None

            if isinstance(pred, int):
                # Backward compat: simple 1-based index, FS type
                pred_idx = pred - 1
            elif isinstance(pred, dict):
                task_ref = pred.get("task")
                if task_ref is not None:
                    pred_idx = int(task_ref) - 1
                ptype = pred.get("type", "FS").upper()
                rel_type_name = RELATION_TYPE_MAP.get(ptype, "FINISH_START")
                if pred.get("lag"):
                    lag_days = _parse_lag_duration(pred["lag"])
                    try:
                        lag_duration = Duration.getInstance(lag_days, TimeUnit.DAYS)
                    except Exception:
                        pass

            if pred_idx is not None and 0 <= pred_idx < len(created_tasks):
                try:
                    builder = Relation.Builder()
                    builder.predecessorTask(created_tasks[pred_idx])
                    builder.successorTask(created_tasks[flat_idx])
                    try:
                        from org.mpxj import RelationType
                        builder.type(RelationType.valueOf(rel_type_name))
                    except Exception:
                        pass
                    if lag_duration:
                        builder.lag(lag_duration)
                    created_tasks[flat_idx].addPredecessor(builder)
                except Exception as e:
                    print(f"Warning: Could not set predecessor on task {flat_idx + 1}: {e}", file=sys.stderr)

    # --- Auto-create resources referenced in tasks but not in resources_data ---
    for flat_idx, (task_data, level, parent_idx) in enumerate(flat_tasks):
        for res_name in task_data.get("resources", []):
            if res_name not in resource_map:
                resource = project.addResource()
                resource.setName(res_name)
                resource_map[res_name] = resource

    # --- Assign resources to tasks ---
    for flat_idx, (task_data, level, parent_idx) in enumerate(flat_tasks):
        for res_name in task_data.get("resources", []):
            if res_name in resource_map:
                try:
                    created_tasks[flat_idx].addResourceAssignment(resource_map[res_name])
                except Exception:
                    pass

    output_path.parent.mkdir(parents=True, exist_ok=True)
    writer = MSPDIWriter()
    writer.write(project, str(output_path))
    print(f"Generated: {output_path} ({len(created_tasks)} tasks, {len(resource_map)} resources, MSPDI XML format)")


# ---------------------------------------------------------------------------
# Inject mode
# ---------------------------------------------------------------------------

def inject_mpxj(data: dict, template_path: Path, output_path: Path, java_path: str) -> None:
    """Inject data into an existing project file using MPXJ (requires Java)."""
    jdk_home = _resolve_java_home(java_path)
    jvm_path = _find_jvm_dll(jdk_home) if jdk_home else None

    if jdk_home:
        os.environ["JAVA_HOME"] = str(jdk_home)

    if not _ensure_package("mpxj"):
        print("Error: mpxj is required.", file=sys.stderr)
        sys.exit(1)
    if not _ensure_package("jpype", "jpype1"):
        print("Error: jpype1 is required.", file=sys.stderr)
        sys.exit(1)

    import mpxj  # noqa: F401
    import jpype
    try:
        if not jpype.isJVMStarted():
            if jvm_path:
                jpype.startJVM(jvm_path)
            else:
                jpype.startJVM()
    except Exception as e:
        print(f"Error starting JVM: {e}", file=sys.stderr)
        sys.exit(1)

    try:
        from org.mpxj.reader import UniversalProjectReader
        from org.mpxj import Duration, TimeUnit, Priority, ConstraintType
        from org.mpxj.mspdi import MSPDIWriter
        from java.time import LocalDateTime
    except Exception:
        print("Error: Failed to load MPXJ Java classes.", file=sys.stderr)
        sys.exit(1)

    reader = UniversalProjectReader()
    project = reader.read(str(template_path))
    if project is None:
        print(f"Error: Could not read template '{template_path}'.", file=sys.stderr)
        sys.exit(1)

    # Re-enable auto-assignment after reading (reader disables it to preserve original IDs)
    config = project.getProjectConfig()
    config.setAutoTaskID(True)
    config.setAutoTaskUniqueID(True)
    config.setAutoResourceID(True)
    config.setAutoResourceUniqueID(True)

    all_tasks = list(project.getTasks() or [])
    tasks_by_uid: dict[int, object] = {}
    tasks_by_name: dict[str, object] = {}
    for t in all_tasks:
        uid = t.getUniqueID()
        if uid is not None:
            tasks_by_uid[int(uid)] = t
        name = t.getName()
        if name:
            tasks_by_name[str(name)] = t

    modified = 0
    added = 0

    for task_data in data.get("tasks", []):
        target = None
        if task_data.get("task_uid") is not None:
            target = tasks_by_uid.get(int(task_data["task_uid"]))
        elif task_data.get("task_name"):
            target = tasks_by_name.get(task_data["task_name"])

        if target is None:
            # Add as new task
            target = project.addTask()
            added += 1
        else:
            modified += 1

        # Apply fields
        if task_data.get("name"):
            target.setName(task_data["name"])
        if task_data.get("start"):
            parts = task_data["start"].split("-")
            target.setStart(LocalDateTime.of(int(parts[0]), int(parts[1]), int(parts[2]), 8, 0))
        if task_data.get("duration"):
            dur_val, dur_unit = parse_duration(task_data["duration"])
            unit = TimeUnit.DAYS if dur_unit == "DAYS" else TimeUnit.HOURS
            target.setDuration(Duration.getInstance(dur_val, unit))
        if task_data.get("notes"):
            try:
                target.setNotes(task_data["notes"])
            except Exception:
                pass
        if task_data.get("percent_complete") is not None:
            try:
                from java.lang import Double
                target.setPercentageComplete(Double(float(task_data["percent_complete"])))
            except Exception:
                pass
        if task_data.get("priority") is not None:
            try:
                target.setPriority(Priority.getInstance(int(task_data["priority"])))
            except Exception:
                pass
        if task_data.get("constraint_type"):
            try:
                ct_name = CONSTRAINT_MAP.get(
                    task_data["constraint_type"].upper(),
                    task_data["constraint_type"].upper()
                )
                target.setConstraintType(ConstraintType.valueOf(ct_name))
                if task_data.get("constraint_date"):
                    cd_parts = task_data["constraint_date"].split("-")
                    target.setConstraintDate(
                        LocalDateTime.of(int(cd_parts[0]), int(cd_parts[1]), int(cd_parts[2]), 8, 0)
                    )
            except Exception:
                pass

        # Custom fields
        custom = task_data.get("custom_fields", {})
        for key, val in custom.items():
            key_lower = key.lower()
            try:
                if key_lower.startswith("text"):
                    idx = int(key_lower.replace("text", ""))
                    target.setText(idx, str(val))
                elif key_lower.startswith("number"):
                    idx = int(key_lower.replace("number", ""))
                    from java.lang import Double
                    target.setNumber(idx, Double(float(val)))
                elif key_lower.startswith("flag"):
                    idx = int(key_lower.replace("flag", ""))
                    target.setFlag(idx, bool(val))
            except Exception:
                pass

        # Resources for new tasks
        if added > modified or task_data.get("task_uid") is None and task_data.get("task_name") is None:
            for res_name in task_data.get("resources", []):
                # Check if resource exists
                existing_res = None
                for r in (project.getResources() or []):
                    if r.getName() and str(r.getName()) == res_name:
                        existing_res = r
                        break
                if not existing_res:
                    existing_res = project.addResource()
                    existing_res.setName(res_name)
                try:
                    target.addResourceAssignment(existing_res)
                except Exception:
                    pass

    output_path.parent.mkdir(parents=True, exist_ok=True)
    try:
        writer = MSPDIWriter()
        writer.write(project, str(output_path))
        print(f"Injected: {output_path} (modified {modified}, added {added} tasks)")
    except Exception as e:
        print(f"Warning: MPXJ writer failed ({e}). Falling back to XML inject.", file=sys.stderr)
        # Fall back to xml.etree for MSPDI XML
        ext = template_path.suffix.lower()
        if ext in (".xml", ".mspdi"):
            inject_xml_fallback(data, template_path, output_path)
        else:
            print(f"Error: Cannot fall back to XML inject for '{ext}' files.", file=sys.stderr)
            sys.exit(1)


def inject_xml_fallback(data: dict, template_path: Path, output_path: Path) -> None:
    """Inject data into an MSPDI XML file using xml.etree (no Java required).

    Only works with .xml/.mspdi files, not .mpp (binary).
    """
    NS = "http://schemas.microsoft.com/project"
    ET.register_namespace("", NS)

    tree = ET.parse(str(template_path))
    root = tree.getroot()

    # Build task index
    tasks_el = root.find(f"{{{NS}}}Tasks")
    if tasks_el is None:
        print("Error: No <Tasks> element found in template XML.", file=sys.stderr)
        sys.exit(1)

    task_elements = tasks_el.findall(f"{{{NS}}}Task")
    tasks_by_uid: dict[str, ET.Element] = {}
    tasks_by_name: dict[str, ET.Element] = {}
    for tel in task_elements:
        uid_el = tel.find(f"{{{NS}}}UID")
        name_el = tel.find(f"{{{NS}}}Name")
        if uid_el is not None and uid_el.text:
            tasks_by_uid[uid_el.text] = tel
        if name_el is not None and name_el.text:
            tasks_by_name[name_el.text] = tel

    # Find max UID for new tasks
    max_uid = 0
    for tel in task_elements:
        uid_el = tel.find(f"{{{NS}}}UID")
        if uid_el is not None and uid_el.text:
            try:
                max_uid = max(max_uid, int(uid_el.text))
            except ValueError:
                pass
    # Also find max ID
    max_id = 0
    for tel in task_elements:
        id_el = tel.find(f"{{{NS}}}ID")
        if id_el is not None and id_el.text:
            try:
                max_id = max(max_id, int(id_el.text))
            except ValueError:
                pass

    def _set_element(parent: ET.Element, tag: str, value: str) -> None:
        """Set or create a child element with the given value."""
        el = parent.find(f"{{{NS}}}{tag}")
        if el is None:
            el = ET.SubElement(parent, f"{{{NS}}}{tag}")
        el.text = value

    def _duration_to_iso(dur_str: str) -> str:
        """Convert '5d' to 'PT40H0M0S' (ISO 8601 duration for MSPDI)."""
        val, unit = parse_duration(dur_str)
        if unit == "HOURS":
            hours = int(val)
        else:
            hours = int(val * 8)  # 8h per day
        return f"PT{hours}H0M0S"

    def _date_to_iso(date_str: str) -> str:
        """Convert '2026-04-01' to '2026-04-01T08:00:00'."""
        return f"{date_str}T08:00:00"

    modified = 0
    added = 0

    for task_data in data.get("tasks", []):
        target: ET.Element | None = None
        if task_data.get("task_uid") is not None:
            target = tasks_by_uid.get(str(task_data["task_uid"]))
        elif task_data.get("task_name"):
            target = tasks_by_name.get(task_data["task_name"])

        if target is not None:
            modified += 1
        else:
            # Create new task
            max_uid += 1
            max_id += 1
            target = ET.SubElement(tasks_el, f"{{{NS}}}Task")
            _set_element(target, "UID", str(max_uid))
            _set_element(target, "ID", str(max_id))
            added += 1

        # Apply fields
        if task_data.get("name"):
            _set_element(target, "Name", task_data["name"])
        if task_data.get("start"):
            _set_element(target, "Start", _date_to_iso(task_data["start"]))
        if task_data.get("duration"):
            _set_element(target, "Duration", _duration_to_iso(task_data["duration"]))
        if task_data.get("notes"):
            _set_element(target, "Notes", task_data["notes"])
        if task_data.get("percent_complete") is not None:
            _set_element(target, "PercentComplete", str(int(task_data["percent_complete"])))
        if task_data.get("priority") is not None:
            _set_element(target, "Priority", str(int(task_data["priority"])))

    output_path.parent.mkdir(parents=True, exist_ok=True)
    tree.write(str(output_path), xml_declaration=True, encoding="UTF-8")
    print(f"Injected (XML fallback): {output_path} (modified {modified}, added {added} tasks)")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate or inject into an MSPDI XML file (MS Project) from JSON input."
    )
    parser.add_argument(
        "input",
        type=Path,
        help="Path to JSON input file with task definitions."
    )
    parser.add_argument(
        "-o", "--output",
        type=Path,
        default=Path("output.xml"),
        help="Output file path (default: output.xml)."
    )
    parser.add_argument(
        "-t", "--template",
        type=Path,
        default=None,
        help="Template file for inject mode (.xml, .mspdi, .mpp)."
    )
    parser.add_argument(
        "--mode",
        choices=["generate", "inject"],
        default="generate",
        help="Mode: 'generate' (default) or 'inject' into template."
    )
    parser.add_argument(
        "--java-home",
        type=str,
        default=None,
        help="Path to Java JDK installation (e.g., 'C:\\Program Files\\Java\\jdk-17')."
    )
    args = parser.parse_args()

    if not args.input.is_file():
        print(f"Error: Input file not found: {args.input}", file=sys.stderr)
        sys.exit(1)

    if args.mode == "inject" and not args.template:
        print("Error: Inject mode requires --template (-t) argument.", file=sys.stderr)
        sys.exit(1)

    if args.template and not args.template.is_file():
        print(f"Error: Template file not found: {args.template}", file=sys.stderr)
        sys.exit(1)

    data = load_input(args.input)

    if args.mode == "inject":
        # Check Java availability for inject
        java_path = check_java(min_version=11, java_home=args.java_home)
        if java_path:
            inject_mpxj(data, args.template, args.output, java_path)
        else:
            # Fallback: xml.etree for .xml/.mspdi files
            ext = args.template.suffix.lower()
            if ext in (".xml", ".mspdi"):
                print("Warning: Java not found. Using XML fallback (limited features).", file=sys.stderr)
                inject_xml_fallback(data, args.template, args.output)
            else:
                print(f"Error: Java 11+ is required for inject mode with '{ext}' files.", file=sys.stderr)
                print("", file=sys.stderr)
                print("The XML fallback only supports .xml/.mspdi templates.", file=sys.stderr)
                print("For .mpp files, Java + MPXJ is required.", file=sys.stderr)
                print("", file=sys.stderr)
                print("Install Java:", file=sys.stderr)
                print("  Windows: choco install temurin17", file=sys.stderr)
                print("  Linux:   apt install openjdk-17-jdk", file=sys.stderr)
                print("  macOS:   brew install openjdk@17", file=sys.stderr)
                sys.exit(1)
    else:
        # Generate mode
        java_path = check_java(min_version=11, java_home=args.java_home)
        if not java_path:
            print("Error: Java 11+ is required but was not found.", file=sys.stderr)
            print("", file=sys.stderr)
            print("Install Java:", file=sys.stderr)
            print("  Windows: choco install temurin17", file=sys.stderr)
            print("  Linux:   apt install openjdk-17-jdk", file=sys.stderr)
            print("  macOS:   brew install openjdk@17", file=sys.stderr)
            print("", file=sys.stderr)
            print("Or pass --java-home to specify the JDK location.", file=sys.stderr)
            sys.exit(1)

        generate(data, args.output, java_path)


if __name__ == "__main__":
    main()
