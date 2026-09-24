#!/usr/bin/env python3
"""Read-only validation for a Hell Grind AIGC project directory."""

from __future__ import annotations

import argparse
import csv
import json
import re
from collections import Counter
from pathlib import Path
from typing import Any


REQUIRED_TEXT_FILES = [
    "00_brief/project.yaml",
    "01_story/story-bible.md",
    "05_prompts/prompt-template.md",
    "07_review/qa-checklist.md",
    "08_edit/edit-notes.md",
    "09_delivery/delivery-checklist.md",
]

V1_CSV_SCHEMAS = {
    "02_assets/assets.csv": ["asset_id", "asset_type", "name", "version", "status", "reference_path", "notes"],
    "03_scenes/scenes.csv": ["scene_id", "scene_order", "title", "location_id", "time_of_day", "story_goal", "status", "notes"],
    "04_shots/shots.csv": ["shot_id", "scene_id", "shot_order", "duration_seconds", "status", "prompt_version", "selected_generation_id", "notes"],
    "06_generations/generation-log.csv": ["generation_id", "shot_id", "prompt_version", "provider", "model", "seed", "created_at", "status", "output_path", "cost", "notes"],
    "07_review/selection-log.csv": ["selection_id", "shot_id", "generation_id", "decision", "reviewer", "reviewed_at", "notes"],
    "07_review/continuity-matrix.csv": ["shot_id", "character_ids", "asset_ids", "screen_direction", "costume_state", "injury_state", "prop_state", "environment_state", "notes"],
}

V2_CSV_SCHEMAS = {
    "02_assets/assets.csv": ["asset_id", "asset_type", "name", "version", "status", "identity_invariants", "reference_ids", "rights_status", "approved_by", "notes"],
    "02_assets/reference-scope.csv": ["reference_id", "asset_id", "source_path_or_url", "rights_status", "inherit_identity", "inherit_state", "inherit_material", "inherit_space", "inherit_composition", "inherit_camera", "inherit_lighting", "inherit_color", "exclude", "approval_status", "notes"],
    "02_assets/asset-state-matrix.csv": ["asset_version_id", "asset_id", "version", "state_name", "identity_invariants", "state_variables", "costume_or_surface", "damage_or_weathering", "carried_props", "reference_ids", "approval_status", "notes"],
    "03_scenes/scenes.csv": ["scene_id", "scene_order", "title", "location_id", "time_of_day", "story_goal", "open_state", "close_state", "status", "notes"],
    "03_scenes/spatial-map.csv": ["scene_id", "zone_id", "zone_name", "screen_relation", "depth_layer", "entry_exit", "anchor_objects", "allowed_assets", "lighting_source", "continuity_notes"],
    "04_shots/shots.csv": ["shot_id", "scene_id", "shot_order", "duration_seconds", "status", "narrative_goal", "asset_version_ids", "open_state", "close_state", "camera_start", "camera_path", "camera_end", "continuity_in", "continuity_out", "must_hold", "changes_here", "must_not_appear", "risk_focus", "prompt_id", "selected_generation_id", "notes"],
    "04_shots/beat-sheet.csv": ["shot_id", "beat_order", "start_seconds", "end_seconds", "actor_or_source", "trigger", "action", "contact_target", "reaction", "end_state", "dialogue_id", "audio_cue_id"],
    "04_shots/audio-cues.csv": ["audio_cue_id", "shot_id", "start_seconds", "end_seconds", "category", "source", "content_or_effect", "spatial_position", "mix_priority", "continuity_key", "notes"],
    "05_prompts/prompt-index.csv": ["prompt_id", "shot_id", "version", "status", "richness", "master_prompt_path", "adapter_path", "parent_version", "change_reason", "changed_variables", "prompt_sha256", "approved_by", "notes"],
    "06_generations/generation-log.csv": ["generation_id", "shot_id", "prompt_id", "batch_id", "provider", "model", "seed", "parameters_json", "created_at", "status", "output_path", "cost", "currency", "failure_codes", "notes"],
    "06_generations/iteration-log.csv": ["iteration_id", "shot_id", "prompt_id", "batch_id", "observed_failure_codes", "responsibility_layer", "changed_variables", "hypothesis", "expected_improvement", "result_generation_ids", "decision", "next_action"],
    "07_review/selection-log.csv": ["selection_id", "shot_id", "generation_id", "decision", "passed_gates", "known_defects", "continuity_impact", "rationale", "reviewer", "reviewed_at", "notes"],
    "07_review/continuity-matrix.csv": ["shot_id", "asset_version_ids", "screen_direction", "spatial_state", "costume_state", "injury_state", "prop_state", "environment_state", "action_in", "action_out", "audio_state", "open_issues", "notes"],
    "07_review/waivers.csv": ["waiver_id", "shot_id", "gate_code", "issue", "rationale", "impact", "approved_by", "approved_at", "expires_or_scope", "notes"],
}

V2_ONLY_PATHS = sorted(set(V2_CSV_SCHEMAS) - set(V1_CSV_SCHEMAS))

COMMON_ID_PATTERNS = {
    "scene_id": re.compile(r"^SC\d{3}$"),
    "shot_id": re.compile(r"^SC\d{3}-SH\d{3}$"),
    "generation_id": re.compile(r"^GEN-[A-Z0-9][A-Z0-9-]*$"),
    "selection_id": re.compile(r"^SEL-[A-Z0-9][A-Z0-9-]*$"),
}
V1_ASSET_ID_PATTERN = re.compile(r"^(CHR|CRT|PROP|LOC|VFX)-[A-Z0-9][A-Z0-9-]*$")
V2_ASSET_ID_PATTERN = re.compile(r"^AST-(CHAR|CREA|PROP|LOC|VFX)-[A-Z0-9][A-Z0-9-]*$")
V2_ASSET_VERSION_PATTERN = re.compile(r"^AST-(CHAR|CREA|PROP|LOC|VFX)-[A-Z0-9][A-Z0-9-]*@v\d{3}$")
V2_REFERENCE_ID_PATTERN = re.compile(r"^REF-[A-Z0-9][A-Z0-9-]*$")
V2_PROMPT_ID_PATTERN = re.compile(r"^SC\d{3}-SH\d{3}-P\d{3}$")
V2_AUDIO_ID_PATTERN = re.compile(r"^AUD-[A-Z0-9][A-Z0-9-]*$")
V2_ITERATION_ID_PATTERN = re.compile(r"^ITR-[A-Z0-9][A-Z0-9-]*$")
V2_WAIVER_ID_PATTERN = re.compile(r"^WVR-[A-Z0-9][A-Z0-9-]*$")


def issue(code: str, path: str, message: str, severity: str = "error") -> dict[str, str]:
    return {"code": code, "severity": severity, "path": path, "message": message}


def empty_result(root: Path, issues: list[dict[str, str]], schema_version: int | None = None) -> dict[str, Any]:
    errors = sum(entry["severity"] == "error" for entry in issues)
    warnings = sum(entry["severity"] == "warning" for entry in issues)
    return {
        "valid": errors == 0,
        "project": str(root),
        "schema_version": schema_version,
        "issues": issues,
        "error_count": errors,
        "warning_count": warnings,
        "counts": {},
        "network_requests": 0,
        "database_operations": 0,
    }


def parse_project_yaml(path: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip() or line.lstrip().startswith("#") or ":" not in line:
            continue
        key, value = line.split(":", 1)
        values[key.strip()] = value.strip().strip('"')
    return values


def parse_schema_version(config: dict[str, str]) -> int:
    raw = config.get("schema_version", "1")
    try:
        value = int(raw)
    except ValueError:
        return 0
    return value


def read_csv(
    root: Path,
    relative: str,
    required: list[str],
    issues: list[dict[str, str]],
    *,
    severity: str = "error",
) -> list[dict[str, str]]:
    path = root / relative
    if not path.is_file():
        issues.append(issue("MISSING_FILE", relative, "required CSV file is missing", severity))
        return []
    try:
        with path.open(newline="", encoding="utf-8-sig") as handle:
            reader = csv.DictReader(handle)
            headers = reader.fieldnames or []
            for column in required:
                if column not in headers:
                    issues.append(issue("MISSING_COLUMN", relative, f"missing column: {column}", severity))
            return [{key: (value or "").strip() for key, value in row.items() if key is not None} for row in reader]
    except (OSError, csv.Error, UnicodeError) as error:
        issues.append(issue("INVALID_CSV", relative, str(error), severity))
        return []


def validate_ids(
    relative: str,
    rows: list[dict[str, str]],
    column: str,
    pattern: re.Pattern[str],
    issues: list[dict[str, str]],
) -> set[str]:
    values = [row.get(column, "") for row in rows if row.get(column, "")]
    for value, count in Counter(values).items():
        if count > 1:
            issues.append(issue("DUPLICATE_ID", relative, f"duplicate {column}: {value}"))
    for value in values:
        if not pattern.fullmatch(value):
            issues.append(issue("INVALID_ID", relative, f"invalid {column}: {value}"))
    return set(values)


def require_references(
    relative: str,
    rows: list[dict[str, str]],
    column: str,
    valid: set[str],
    issues: list[dict[str, str]],
    *,
    split: str | None = None,
) -> None:
    for index, row in enumerate(rows, start=2):
        value = row.get(column, "")
        values = [item.strip() for item in value.split(split)] if value and split else ([value] if value else [])
        for candidate in values:
            if candidate and candidate not in valid:
                issues.append(issue("MISSING_REFERENCE", relative, f"row {index} references missing {column}: {candidate}"))


def validate_statuses(
    relative: str,
    rows: list[dict[str, str]],
    column: str,
    allowed: set[str],
    issues: list[dict[str, str]],
) -> None:
    for index, row in enumerate(rows, start=2):
        value = row.get(column, "")
        if value and value not in allowed:
            issues.append(issue("INVALID_STATUS", relative, f"row {index} has invalid {column}: {value}"))


def parse_number(relative: str, row_number: int, column: str, raw: str, issues: list[dict[str, str]]) -> float | None:
    if not raw:
        return None
    try:
        return float(raw)
    except ValueError:
        issues.append(issue("INVALID_NUMBER", relative, f"row {row_number} has invalid {column}: {raw}"))
        return None


def validate_positive_numbers(
    relative: str,
    rows: list[dict[str, str]],
    column: str,
    issues: list[dict[str, str]],
    *,
    allow_zero: bool = False,
) -> None:
    for row_number, row in enumerate(rows, start=2):
        value = parse_number(relative, row_number, column, row.get(column, ""), issues)
        if value is not None and (value < 0 or (value == 0 and not allow_zero)):
            issues.append(issue("NON_POSITIVE_NUMBER", relative, f"row {row_number} requires positive {column}: {value:g}"))


def validate_unique_order(
    relative: str,
    rows: list[dict[str, str]],
    group_column: str | None,
    order_column: str,
    issues: list[dict[str, str]],
) -> None:
    seen: dict[tuple[str, str], int] = {}
    for row_number, row in enumerate(rows, start=2):
        order = row.get(order_column, "")
        if not order:
            continue
        group = row.get(group_column, "") if group_column else ""
        key = (group, order)
        if key in seen:
            label = f" within {group}" if group else ""
            issues.append(issue("DUPLICATE_ORDER", relative, f"rows {seen[key]} and {row_number} duplicate {order_column}={order}{label}"))
        else:
            seen[key] = row_number


def validate_timeline_bounds(
    relative: str,
    rows: list[dict[str, str]],
    shot_durations: dict[str, float],
    issues: list[dict[str, str]],
) -> None:
    for row_number, row in enumerate(rows, start=2):
        start = parse_number(relative, row_number, "start_seconds", row.get("start_seconds", ""), issues)
        end = parse_number(relative, row_number, "end_seconds", row.get("end_seconds", ""), issues)
        if start is None or end is None:
            continue
        if start < 0 or end <= start:
            issues.append(issue("TIMELINE_ORDER", relative, f"row {row_number} requires 0 <= start_seconds < end_seconds"))
        shot_id = row.get("shot_id", "")
        duration = shot_durations.get(shot_id)
        if duration is not None and end > duration:
            issues.append(issue("TIMELINE_OVERFLOW", relative, f"row {row_number} ends at {end:g}s beyond {shot_id} duration {duration:g}s"))


def validate_iteration_records(rows: list[dict[str, str]], issues: list[dict[str, str]]) -> None:
    relative = "06_generations/iteration-log.csv"
    required = ["changed_variables", "hypothesis", "next_action"]
    for row_number, row in enumerate(rows, start=2):
        missing = [column for column in required if not row.get(column, "")]
        if missing:
            issues.append(issue("INCOMPLETE_ITERATION", relative, f"row {row_number} is missing: {', '.join(missing)}"))


def validate_selection_consistency(
    shots: list[dict[str, str]],
    selections: list[dict[str, str]],
    issues: list[dict[str, str]],
) -> None:
    selected_by_shot: dict[str, list[str]] = {}
    for row in selections:
        if row.get("decision") == "select":
            selected_by_shot.setdefault(row.get("shot_id", ""), []).append(row.get("generation_id", ""))
    for row_number, shot in enumerate(shots, start=2):
        shot_id = shot.get("shot_id", "")
        chosen = shot.get("selected_generation_id", "")
        logged = [value for value in selected_by_shot.get(shot_id, []) if value]
        if chosen and chosen not in logged:
            issues.append(issue("SELECTION_MISMATCH", "04_shots/shots.csv", f"row {row_number} selects {chosen} but selection-log has {logged or 'no select decision'}"))
        if len(logged) > 1:
            issues.append(issue("MULTIPLE_SELECTIONS", "07_review/selection-log.csv", f"{shot_id} has multiple active select decisions: {logged}"))


def validate_state_requirements(
    shots: list[dict[str, str]],
    prompts: list[dict[str, str]],
    generations: list[dict[str, str]],
    selections: list[dict[str, str]],
    continuity: list[dict[str, str]],
    waivers: list[dict[str, str]],
    issues: list[dict[str, str]],
) -> None:
    prompt_ids = {row.get("prompt_id", "") for row in prompts if row.get("prompt_id", "")}
    generated_shots = {row.get("shot_id", "") for row in generations if row.get("shot_id", "")}
    selected_shots = {row.get("shot_id", "") for row in selections if row.get("decision") == "select"}
    waiver_shots = {row.get("shot_id", "") for row in waivers if row.get("shot_id", "") and row.get("approved_by", "")}
    continuity_by_shot = {row.get("shot_id", ""): row for row in continuity if row.get("shot_id", "")}
    prompt_required = {"prompt_ready", "generated", "reviewed", "selected", "locked", "needs_revision"}
    generation_required = {"generated", "reviewed", "selected", "locked", "needs_revision"}
    selection_required = {"selected", "locked"}
    for row_number, shot in enumerate(shots, start=2):
        shot_id = shot.get("shot_id", "")
        status = shot.get("status", "")
        prompt_id = shot.get("prompt_id", "")
        if status in prompt_required and (not prompt_id or prompt_id not in prompt_ids):
            issues.append(issue("STATE_REQUIREMENT", "04_shots/shots.csv", f"row {row_number} status {status} requires a valid prompt_id"))
        if status in generation_required and shot_id not in generated_shots:
            issues.append(issue("STATE_REQUIREMENT", "04_shots/shots.csv", f"row {row_number} status {status} requires a generation record"))
        if status in selection_required and shot_id not in selected_shots:
            issues.append(issue("STATE_REQUIREMENT", "04_shots/shots.csv", f"row {row_number} status {status} requires a select decision"))
        open_issues = continuity_by_shot.get(shot_id, {}).get("open_issues", "").lower()
        if status == "locked" and "error" in open_issues and shot_id not in waiver_shots:
            issues.append(issue("UNWAIVED_ERROR", "07_review/continuity-matrix.csv", f"{shot_id} is locked with an unwaived error: {open_issues}"))


def validate_project(root: Path, *, strict_v2: bool = False) -> dict[str, Any]:
    issues: list[dict[str, str]] = []
    if not root.is_dir():
        issues.append(issue("MISSING_PROJECT", str(root), "project directory does not exist"))
        return empty_result(root, issues)

    for relative in REQUIRED_TEXT_FILES:
        if not (root / relative).is_file():
            issues.append(issue("MISSING_FILE", relative, "required file is missing"))

    config: dict[str, str] = {}
    config_path = root / "00_brief/project.yaml"
    if config_path.is_file():
        config = parse_project_yaml(config_path)
        for key in ["schema_version", "project_id", "project_name", "created_date", "aspect_ratio", "status"]:
            if not config.get(key):
                issues.append(issue("MISSING_CONFIG", "00_brief/project.yaml", f"missing value: {key}"))
        project_id = config.get("project_id", "")
        if project_id and not re.fullmatch(r"^PRJ-[A-Z0-9][A-Z0-9-]{1,61}$", project_id):
            issues.append(issue("INVALID_ID", "00_brief/project.yaml", f"invalid project_id: {project_id}"))

    schema_version = parse_schema_version(config)
    if schema_version not in {1, 2}:
        issues.append(issue("INVALID_SCHEMA_VERSION", "00_brief/project.yaml", f"unsupported schema_version: {config.get('schema_version', '')}"))
    effective_version = 2 if strict_v2 or schema_version == 2 else 1
    schemas = V2_CSV_SCHEMAS if effective_version == 2 else V1_CSV_SCHEMAS

    if schema_version == 1 and strict_v2:
        issues.append(issue("V2_REQUIRED", "00_brief/project.yaml", "strict v2 validation requires schema_version: 2"))
    elif schema_version == 1:
        issues.append(issue("V1_COMPATIBILITY", "00_brief/project.yaml", "schema v1 is accepted in compatibility mode; migrate to v2 for strict production gates", "warning"))
        for relative in V2_ONLY_PATHS:
            if not (root / relative).is_file():
                issues.append(issue("V2_MIGRATION_FILE", relative, "v2 project file is not present", "warning"))

    tables = {relative: read_csv(root, relative, columns, issues) for relative, columns in schemas.items()}
    assets = tables["02_assets/assets.csv"]
    scenes = tables["03_scenes/scenes.csv"]
    shots = tables["04_shots/shots.csv"]
    generations = tables["06_generations/generation-log.csv"]
    selections = tables["07_review/selection-log.csv"]
    continuity = tables["07_review/continuity-matrix.csv"]

    asset_pattern = V2_ASSET_ID_PATTERN if effective_version == 2 else V1_ASSET_ID_PATTERN
    asset_ids = validate_ids("02_assets/assets.csv", assets, "asset_id", asset_pattern, issues)
    scene_ids = validate_ids("03_scenes/scenes.csv", scenes, "scene_id", COMMON_ID_PATTERNS["scene_id"], issues)
    shot_ids = validate_ids("04_shots/shots.csv", shots, "shot_id", COMMON_ID_PATTERNS["shot_id"], issues)
    generation_ids = validate_ids("06_generations/generation-log.csv", generations, "generation_id", COMMON_ID_PATTERNS["generation_id"], issues)
    validate_ids("07_review/selection-log.csv", selections, "selection_id", COMMON_ID_PATTERNS["selection_id"], issues)

    require_references("03_scenes/scenes.csv", scenes, "location_id", asset_ids, issues)
    require_references("04_shots/shots.csv", shots, "scene_id", scene_ids, issues)
    require_references("04_shots/shots.csv", shots, "selected_generation_id", generation_ids, issues)
    require_references("06_generations/generation-log.csv", generations, "shot_id", shot_ids, issues)
    require_references("07_review/selection-log.csv", selections, "shot_id", shot_ids, issues)
    require_references("07_review/selection-log.csv", selections, "generation_id", generation_ids, issues)
    require_references("07_review/continuity-matrix.csv", continuity, "shot_id", shot_ids, issues)

    if effective_version == 2:
        references = tables["02_assets/reference-scope.csv"]
        asset_states = tables["02_assets/asset-state-matrix.csv"]
        spatial = tables["03_scenes/spatial-map.csv"]
        beats = tables["04_shots/beat-sheet.csv"]
        audio_cues = tables["04_shots/audio-cues.csv"]
        prompts = tables["05_prompts/prompt-index.csv"]
        iterations = tables["06_generations/iteration-log.csv"]
        waivers = tables["07_review/waivers.csv"]

        reference_ids = validate_ids("02_assets/reference-scope.csv", references, "reference_id", V2_REFERENCE_ID_PATTERN, issues)
        asset_version_ids = validate_ids("02_assets/asset-state-matrix.csv", asset_states, "asset_version_id", V2_ASSET_VERSION_PATTERN, issues)
        prompt_ids = validate_ids("05_prompts/prompt-index.csv", prompts, "prompt_id", V2_PROMPT_ID_PATTERN, issues)
        validate_ids("04_shots/audio-cues.csv", audio_cues, "audio_cue_id", V2_AUDIO_ID_PATTERN, issues)
        validate_ids("06_generations/iteration-log.csv", iterations, "iteration_id", V2_ITERATION_ID_PATTERN, issues)
        validate_ids("07_review/waivers.csv", waivers, "waiver_id", V2_WAIVER_ID_PATTERN, issues)

        require_references("02_assets/reference-scope.csv", references, "asset_id", asset_ids, issues)
        require_references("02_assets/asset-state-matrix.csv", asset_states, "asset_id", asset_ids, issues)
        require_references("02_assets/asset-state-matrix.csv", asset_states, "reference_ids", reference_ids, issues, split=";")
        require_references("03_scenes/spatial-map.csv", spatial, "scene_id", scene_ids, issues)
        require_references("03_scenes/spatial-map.csv", spatial, "allowed_assets", asset_ids, issues, split=";")
        require_references("04_shots/shots.csv", shots, "asset_version_ids", asset_version_ids, issues, split=";")
        require_references("04_shots/shots.csv", shots, "prompt_id", prompt_ids, issues)
        require_references("04_shots/beat-sheet.csv", beats, "shot_id", shot_ids, issues)
        require_references("04_shots/audio-cues.csv", audio_cues, "shot_id", shot_ids, issues)
        require_references("05_prompts/prompt-index.csv", prompts, "shot_id", shot_ids, issues)
        require_references("06_generations/generation-log.csv", generations, "prompt_id", prompt_ids, issues)
        require_references("06_generations/iteration-log.csv", iterations, "shot_id", shot_ids, issues)
        require_references("06_generations/iteration-log.csv", iterations, "prompt_id", prompt_ids, issues)
        require_references("06_generations/iteration-log.csv", iterations, "result_generation_ids", generation_ids, issues, split=";")
        require_references("07_review/continuity-matrix.csv", continuity, "asset_version_ids", asset_version_ids, issues, split=";")
        require_references("07_review/waivers.csv", waivers, "shot_id", shot_ids, issues)

        validate_statuses("02_assets/assets.csv", assets, "status", {"proposed", "reference_ready", "approved", "deprecated"}, issues)
        validate_statuses("02_assets/reference-scope.csv", references, "approval_status", {"proposed", "approved", "rejected", "deprecated"}, issues)
        validate_statuses("02_assets/asset-state-matrix.csv", asset_states, "approval_status", {"proposed", "approved", "deprecated"}, issues)
        validate_statuses("03_scenes/scenes.csv", scenes, "status", {"planned", "ready", "locked", "needs_revision"}, issues)
        validate_statuses("04_shots/shots.csv", shots, "status", {"planned", "contract_ready", "prompt_ready", "generated", "reviewed", "selected", "locked", "needs_revision"}, issues)
        validate_statuses("05_prompts/prompt-index.csv", prompts, "status", {"draft", "checked", "approved", "superseded"}, issues)
        validate_statuses("06_generations/generation-log.csv", generations, "status", {"queued", "running", "completed", "failed", "canceled"}, issues)
        validate_statuses("07_review/selection-log.csv", selections, "decision", {"shortlist", "reject", "select", "supersede"}, issues)

        validate_positive_numbers("04_shots/shots.csv", shots, "duration_seconds", issues)
        validate_unique_order("03_scenes/scenes.csv", scenes, None, "scene_order", issues)
        validate_unique_order("04_shots/shots.csv", shots, "scene_id", "shot_order", issues)
        validate_unique_order("04_shots/beat-sheet.csv", beats, "shot_id", "beat_order", issues)

        shot_durations: dict[str, float] = {}
        for row_number, row in enumerate(shots, start=2):
            duration = parse_number("04_shots/shots.csv", row_number, "duration_seconds", row.get("duration_seconds", ""), issues)
            if duration is not None:
                shot_durations[row.get("shot_id", "")] = duration
        validate_timeline_bounds("04_shots/beat-sheet.csv", beats, shot_durations, issues)
        validate_timeline_bounds("04_shots/audio-cues.csv", audio_cues, shot_durations, issues)

        for row_number, row in enumerate(generations, start=2):
            cost = parse_number("06_generations/generation-log.csv", row_number, "cost", row.get("cost", ""), issues)
            if cost is not None and cost < 0:
                issues.append(issue("NEGATIVE_COST", "06_generations/generation-log.csv", f"row {row_number} has negative cost: {cost:g}"))

        validate_iteration_records(iterations, issues)
        validate_selection_consistency(shots, selections, issues)
        validate_state_requirements(shots, prompts, generations, selections, continuity, waivers, issues)

    count_names = {
        "02_assets/assets.csv": "assets",
        "02_assets/reference-scope.csv": "references",
        "02_assets/asset-state-matrix.csv": "asset_states",
        "03_scenes/scenes.csv": "scenes",
        "03_scenes/spatial-map.csv": "spatial_zones",
        "04_shots/shots.csv": "shots",
        "04_shots/beat-sheet.csv": "beats",
        "04_shots/audio-cues.csv": "audio_cues",
        "05_prompts/prompt-index.csv": "prompts",
        "06_generations/generation-log.csv": "generations",
        "06_generations/iteration-log.csv": "iterations",
        "07_review/selection-log.csv": "selections",
        "07_review/continuity-matrix.csv": "continuity_rows",
        "07_review/waivers.csv": "waivers",
    }
    counts = {count_names[path]: len(rows) for path, rows in tables.items()}
    severity_rank = {"error": 0, "warning": 1, "info": 2}
    issues.sort(key=lambda entry: (severity_rank[entry["severity"]], entry["path"], entry["code"], entry["message"]))
    errors = sum(entry["severity"] == "error" for entry in issues)
    warnings = sum(entry["severity"] == "warning" for entry in issues)
    return {
        "valid": errors == 0,
        "project": str(root),
        "schema_version": schema_version,
        "strict_v2": strict_v2,
        "issues": issues,
        "error_count": errors,
        "warning_count": warnings,
        "counts": counts,
        "network_requests": 0,
        "database_operations": 0,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("project", type=Path, help="Project directory to validate")
    parser.add_argument("--strict-v2", action="store_true", help="Require schema v2 files and rules")
    parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    result = validate_project(args.project.expanduser().resolve(), strict_v2=args.strict_v2)
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        status = "PASS" if result["valid"] else "FAIL"
        print(f"{status}: {result['project']} (schema v{result['schema_version']})")
        for entry in result["issues"]:
            print(f"- [{entry['severity']}:{entry['code']}] {entry['path']}: {entry['message']}")
        print(f"Counts: {json.dumps(result['counts'], ensure_ascii=False)}")
        print(f"Errors: {result['error_count']}; warnings: {result['warning_count']}")
        print("Network requests: 0; database operations: 0")
    return 0 if result["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
