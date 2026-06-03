#!/usr/bin/env python3
"""Scaffold portable ub-workflow artifacts."""

import argparse
from dataclasses import dataclass
from datetime import date, datetime, timezone
from pathlib import Path
import re
import shutil

SKILL_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OPS_ROOT = Path(".ub-workflows")
INITIATIVE_TEMPLATE_ROOT = SKILL_ROOT / "assets" / "initiative-template"
SPRINT_TEMPLATE_ROOT = INITIATIVE_TEMPLATE_ROOT / "sprint-template"
OPERATIONS_ROOT_TEMPLATE = SKILL_ROOT / "assets" / "operations-root"
GITKEEP = ".gitkeep"
ROOT_AGENTS = "AGENTS.md"
SOURCE_ATLAS = "SOURCE_ATLAS.md"
UB_WORKFLOW_AGENTS_START = "<!-- BEGIN UB-WORKFLOW ROOT ROUTING -->"
UB_WORKFLOW_AGENTS_END = "<!-- END UB-WORKFLOW ROOT ROUTING -->"
TEXT_SUFFIXES = {".md", ".txt", ".yaml", ".yml", ".json"}
SOURCE_SCAN_SKIP_DIRS = {
    ".agents",
    ".cache",
    ".git",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
    ".ub-workflows",
    ".venv",
    "__pycache__",
    "build",
    "dist",
    "donors",
    "node_modules",
}
SOURCE_SCAN_PRIORITY = (
    "src",
    "tests",
    "docs",
    "scripts",
    "tools",
    "app",
    "apps",
    "packages",
    "lib",
)
WAVE_RE = re.compile(r"^w(?P<num>\d{2})-")
INIT_RE = re.compile(r"^i(?P<num>\d{2})-")
SPRINT_RE = re.compile(r"^w\d{2}-i\d{2}-s(?P<num>\d{2})-")
WAVE_DISCOVERY_RE = re.compile(r"^w\d{2}-d(?P<num>\d{2})-")
INIT_DISCOVERY_RE = re.compile(r"^w\d{2}-i\d{2}-d(?P<num>\d{2})-")
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}-")
MACHINE_PLACEHOLDER_RE = re.compile(r"\bREPLACE_[A-Z0-9_]+\b")
HUMAN_PLACEHOLDER_RE = re.compile(r"Replace with\b")
CODE_FENCE_RE = re.compile(r"^\s*(```|~~~)")
OPTION_HEADING_RE = re.compile(r"^(?P<marks>#{2,3})\s+(?P<title>.+?)\s*$")
OPTION_FIELD_RE = re.compile(r"^-\s+(?P<label>[A-Za-z ]+):")
OPTION_DATE_RE = re.compile(r"^-\s+Last reviewed:\s+(?P<date>\d{4}-\d{2}-\d{2})\.")
STATUS_ACTIVE_INITIATIVE_RE = re.compile(r"^- Active initiative:\s+`(?P<path>[^`]+)`\.?\s*$")
STATUS_INITIATIVE_ROADMAP_RE = re.compile(r"^- Initiative roadmap:\s+`(?P<path>[^`]+)`\.?\s*$")
REQUIRED_OPTION_FIELDS = {
    "Assignment confidence",
    "Evidence links",
    "Last reviewed",
    "Promotion trigger",
    "Revalidation rule",
    "Suggested home",
    "Why it matters",
}
FORBIDDEN_OPTION_LANE_PREFIXES = (
    "archive",
    "archived",
    "closed",
    "completed",
    "done",
)
PRODUCT_OPTION_MARKERS = (
    "W12",
    "W13",
    "First-Party Context Compaction",
    "Memory Provider",
    "External AgentRuntime",
    "AgentHarness",
)


@dataclass(frozen=True)
class PlaceholderFinding:
    workflow_root: Path
    file_path: Path
    line_number: int
    category: str
    severity: str
    marker: str
    line_text: str


@dataclass(frozen=True)
class OptionCard:
    file_path: Path
    line_number: int
    title: str
    fields: frozenset[str]
    last_reviewed: date | None


@dataclass(frozen=True)
class OptionsFinding:
    workflow_root: Path
    file_path: Path
    line_number: int | None
    category: str
    severity: str
    message: str


def slugify(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", value.strip().lower()).strip("-")
    return slug or "workflow"


def wave_id_from_root(wave_root: Path) -> str:
    match = WAVE_RE.match(wave_root.name)
    if not match:
        raise ValueError(f"Wave root must be named wNN-slug: {wave_root}")
    return f"w{match.group('num')}"


def initiative_id_from_root(initiative_root: Path) -> str:
    match = INIT_RE.match(initiative_root.name)
    if not match:
        raise ValueError(f"Initiative root must be named iNN-slug: {initiative_root}")
    return f"i{match.group('num')}"


def owning_wave_root(path: Path) -> Path:
    current = path.resolve()
    for candidate in [current, *current.parents]:
        if WAVE_RE.match(candidate.name) and (candidate / "wave.md").exists():
            return candidate
    raise ValueError(f"Unable to find owning wave root for {path}")


def next_number(container: Path, pattern: re.Pattern[str]) -> int:
    max_num = 0
    if container.exists():
        for child in container.iterdir():
            match = pattern.match(child.name)
            if match:
                max_num = max(max_num, int(match.group("num")))
    return max_num + 1


def ensure_empty(target: Path) -> None:
    if target.exists() and any(target.iterdir() if target.is_dir() else [target]):
        raise ValueError(f"Refusing to overwrite non-empty target: {target}")
    target.mkdir(parents=True, exist_ok=True)


def add_gitkeep(container: Path) -> None:
    container.mkdir(parents=True, exist_ok=True)
    if not any(child.name != GITKEEP for child in container.iterdir()):
        (container / GITKEEP).touch()


def remove_gitkeep(container: Path) -> None:
    gitkeep = container / GITKEEP
    if gitkeep.exists():
        gitkeep.unlink()


def refresh_gitkeep(container: Path) -> None:
    if any(child.name != GITKEEP for child in container.iterdir()):
        remove_gitkeep(container)
    else:
        add_gitkeep(container)


def discover_workflow_root(scan_root: Path) -> Path:
    root = scan_root.resolve()
    if root.name == ".ub-workflows" and (root / "status.md").exists():
        return root
    if (root / ".ub-workflows" / "status.md").exists():
        return root / ".ub-workflows"
    for candidate in root.parents:
        if candidate.name == ".ub-workflows" and (candidate / "status.md").exists():
            return candidate
        nested = candidate / ".ub-workflows"
        if (nested / "status.md").exists():
            return nested
    raise ValueError(f"Unable to find .ub-workflows root from {scan_root}")


def path_from_workflow_root(workflow_root: Path, raw_path: str) -> Path:
    candidate = Path(raw_path)
    if candidate.is_absolute():
        return candidate
    return workflow_root / candidate


def active_initiative_root(workflow_root: Path) -> Path | None:
    status_path = workflow_root / "status.md"
    if not status_path.exists():
        return None
    for line in status_path.read_text(encoding="utf-8").splitlines():
        match = STATUS_ACTIVE_INITIATIVE_RE.match(line.strip())
        if match:
            return path_from_workflow_root(workflow_root, match.group("path"))
    return None


def active_initiative_roadmap(workflow_root: Path) -> Path | None:
    status_path = workflow_root / "status.md"
    if status_path.exists():
        for line in status_path.read_text(encoding="utf-8").splitlines():
            match = STATUS_INITIATIVE_ROADMAP_RE.match(line.strip())
            if match:
                return path_from_workflow_root(workflow_root, match.group("path"))
    initiative_root = active_initiative_root(workflow_root)
    return initiative_root / "roadmap.md" if initiative_root else None


def option_board_paths(workflow_root: Path, *, include_history: bool = False) -> list[Path]:
    paths = [workflow_root / "options.md"]
    active_root = active_initiative_root(workflow_root)
    if active_root is not None:
        paths.append(active_root / "options.md")
    if include_history:
        paths.extend(sorted((workflow_root / "waves").glob("w??-*/initiatives/i??-*/options.md")))
    seen: set[Path] = set()
    unique_paths: list[Path] = []
    for path in paths:
        resolved = path.resolve()
        if resolved in seen:
            continue
        seen.add(resolved)
        unique_paths.append(path)
    return unique_paths


def render(text: str, replacements: dict[str, str]) -> str:
    for key, value in replacements.items():
        text = text.replace(key, value)
    return text


def copy_rendered_tree(
    source: Path,
    target: Path,
    replacements: dict[str, str],
    *,
    skip_parts: set[str] | None = None,
) -> None:
    excluded = skip_parts or set()
    for item in source.rglob("*"):
        relative = item.relative_to(source)
        if any(part in excluded for part in relative.parts):
            continue
        destination = target / relative
        if item.is_dir():
            destination.mkdir(parents=True, exist_ok=True)
            continue
        destination.parent.mkdir(parents=True, exist_ok=True)
        if item.suffix in TEXT_SUFFIXES or item.name in {"AGENTS.md", "README.md"}:
            destination.write_text(
                render(item.read_text(encoding="utf-8"), replacements), encoding="utf-8"
            )
        else:
            shutil.copy2(item, destination)


def detected_source_roots(project_root: Path) -> list[Path]:
    roots = [project_root / name for name in SOURCE_SCAN_PRIORITY if (project_root / name).is_dir()]
    priority_names = {path.name for path in roots}
    for child in sorted(project_root.iterdir(), key=lambda path: path.name):
        if not child.is_dir():
            continue
        if child.name in SOURCE_SCAN_SKIP_DIRS or child.name.startswith("."):
            continue
        if child.name in priority_names:
            continue
        if (child / ROOT_AGENTS).exists() or any(child.glob("*.py")):
            roots.append(child)
    return roots


def source_route_lines(project_root: Path) -> list[str]:
    lines: list[str] = []
    for source_root in detected_source_roots(project_root):
        relative = source_root.relative_to(project_root).as_posix()
        local_agents = source_root / ROOT_AGENTS
        start = f"`{relative}/AGENTS.md`" if local_agents.exists() else f"`{relative}/`"
        lines.append(f"- `{relative}/`: start at {start}.")
    if not lines:
        lines.append("- No source roots detected yet. Add routes when source boundaries exist.")
    return lines


def build_source_atlas(project_root: Path) -> str:
    return (
        "# Source Atlas\n\n"
        "This file routes source-code work before agents read implementation files. "
        "It is seeded once by `ub-workflow` bootstrap from visible project roots "
        "and then maintained when source boundaries change.\n\n"
        "## First-Read Order\n\n"
        "For non-trivial source work:\n\n"
        "1. Root `AGENTS.md`.\n"
        "2. `.ub-workflows/status.md`.\n"
        "3. `SOURCE_ATLAS.md`.\n"
        "4. Nearest relevant folder `AGENTS.md` when one exists.\n"
        "5. Selected source files and tests.\n"
        "6. `.ub-workflows/vision.md` only when product direction matters.\n\n"
        "Do not read unrelated folder guidance unless the task crosses that boundary.\n\n"
        "## Map Use Rule\n\n"
        "Module maps are routing aids, not source truth. Use them to choose files "
        "to open first, then inspect source and tests with fast local search before "
        "changing behavior. If source ownership changes, update this atlas in the "
        "same change.\n\n"
        "## Detected Source Routes\n\n" + "\n".join(source_route_lines(project_root)) + "\n\n"
        "## Workflow Route\n\n"
        "- Workflow state, waves, discoveries, initiatives, sprints, and source "
        "packs: start at `.ub-workflows/WORKFLOW_ATLAS.md`, then "
        "`.ub-workflows/AGENTS.md`.\n\n"
        "## Local Guidance Policy\n\n"
        "Local `AGENTS.md` files should answer only what the folder owns, when work "
        "starts there, local boundaries, what to inspect before editing, likely "
        "tests, and what to avoid. Add local guidance only when a folder has a "
        "meaningful responsibility boundary, rule set, or repeated navigation cost.\n\n"
        "## Source Route Note\n\n"
        "Before editing, identify the owning folder, local guidance read, expected "
        "source files, expected tests, and boundaries intentionally avoided.\n\n"
        "## Maintenance\n\n"
        "Update this file and the nearest relevant folder `AGENTS.md` when a change "
        "adds, removes, renames, or moves a source boundary, plugin lane, public API "
        "area, runtime/protocol/host responsibility, major package, or test topology."
        "\n"
    )


def build_root_agents_section() -> str:
    return (
        f"{UB_WORKFLOW_AGENTS_START}\n"
        "## UB Workflow Routing\n\n"
        "- Before substantial work, read `.ub-workflows/status.md`.\n"
        "- For non-trivial source work, read `SOURCE_ATLAS.md` and then the nearest "
        "relevant folder `AGENTS.md`.\n"
        "- Use `.ub-workflows/vision.md` when product direction matters.\n"
        "- Use `.ub-workflows/options.md` for wave or initiative transition, "
        "future-work lookup, or option promotion.\n"
        "- Use `.ub-workflows/WORKFLOW_ATLAS.md` for workflow-artifact routing.\n"
        "- Use `.ub-workflows/SOURCE_PACK_ATLAS.md` before opening retained source "
        "packs.\n"
        "- When forecast pressure appears, present options and tradeoffs, then wait "
        "for explicit operator decision before expanding scope.\n"
        "- Keep reusable workflow mechanics in the shared `ub-workflow` skill; keep "
        "repo overlays focused on local facts, boundaries, and validation commands.\n"
        f"{UB_WORKFLOW_AGENTS_END}"
    )


def patch_root_agents(project_root: Path) -> None:
    path = project_root / ROOT_AGENTS
    section = build_root_agents_section()
    if path.exists():
        text = path.read_text(encoding="utf-8").rstrip()
        pattern = re.compile(
            re.escape(UB_WORKFLOW_AGENTS_START) + r".*?" + re.escape(UB_WORKFLOW_AGENTS_END),
            re.DOTALL,
        )
        updated = (
            pattern.sub(section, text) if pattern.search(text) else f"{text}\n\n{section}"
        )
    else:
        updated = f"# Agent Instructions\n\n{section}"
    path.write_text(f"{updated.rstrip()}\n", encoding="utf-8")


def command_bootstrap(args: argparse.Namespace) -> int:
    ops_root = Path(args.ops_root).resolve()
    project_root = ops_root.parent
    ensure_empty(ops_root)
    add_gitkeep(ops_root / "source-packs")
    add_gitkeep(ops_root / "waves")
    source_atlas = project_root / SOURCE_ATLAS
    if not source_atlas.exists():
        source_atlas.write_text(build_source_atlas(project_root), encoding="utf-8")
    patch_root_agents(project_root)
    copy_rendered_tree(OPERATIONS_ROOT_TEMPLATE, ops_root, {})
    (ops_root / "vision.md").write_text(
        "# Product Vision\n\n"
        "## Product Promise\n\nReplace with the durable product promise.\n\n"
        "## Audiences\n\n1. Replace with the first audience.\n\n"
        "## Durable Principles\n\n1. Replace with the first principle.\n\n"
        "## Capability Pillars\n\n1. Replace with the first capability pillar.\n\n"
        "## Evidence Questions\n\n1. Replace with the first evidence question.\n\n"
        "## Change Rule\n\nUpdate this vision only through reviewed discovery, closeout, transition, "
        "or an explicit product decision.\n",
        encoding="utf-8",
    )
    (ops_root / "options.md").write_text(
        "# Product Options Board\n\n"
        "This board preserves curated product-level, future-wave, and "
        "unknown-owner options before commitment. It is not a backlog ledger, "
        "completion history, or execution authorization surface.\n\n"
        "Order is document order within each horizon lane. Order means current "
        "review preference, not delivery commitment.\n\n"
        "## Board Rules\n\n"
        "- Keep cards compact; move deep context into source packs, discoveries, "
        "or owner artifacts.\n"
        "- Remove a card after it is promoted, rejected, merged, or completed and "
        "the receiving artifact records the durable trace.\n"
        "- Revalidate every card before activation; stale cards are not executable.\n"
        "- If this file becomes hard to scan quickly, prune, merge, or move context "
        "back into source packs before adding more cards.\n"
        "- During wave or initiative transition, review this board plus unresolved "
        "local initiative options before selecting the next route.\n\n"
        "## Next Wave Candidate\n\nNo active cards.\n\n"
        "## Probable Later Wave\n\nNo active cards.\n\n"
        "## Unassigned Product Option\n\nNo active cards.\n\n"
        "## Update Rules\n\n"
        "Add only options that are likely to matter after context loss and do not "
        "yet belong in a committed roadmap. Remove cards once the receiving "
        "artifact owns the trace.\n",
        encoding="utf-8",
    )
    (ops_root / "status.md").write_text(
        "# Workflow Status\n\n"
        "## Current Product Posture\n\nReplace with current posture.\n\n"
        "## Current Operating State\n\nState: initialized.\n\n"
        "## WIP State\n\nNo active discovery or delivery sprint.\n\n"
        "## Active Pointers\n\nNo active wave yet.\n\n"
        "## Blockers\n\nNone.\n\n"
        "## Wave Sequence\n\nNo waves yet.\n\n"
        "## Conditional Candidate Tracks\n\nNo candidates yet.\n\n"
        "## Retained-Context Routes\n\nUse `SOURCE_PACK_ATLAS.md` before opening source packs.\n\n"
        "## Next Allowed Action\n\nCreate or activate the first wave.\n",
        encoding="utf-8",
    )
    (ops_root / "WORKFLOW_ATLAS.md").write_text(
        "# Workflow Atlas\n\n"
        "Portable workflow rules live in the `ub-workflow` skill. This atlas routes "
        "project-local workflow artifacts to their owning files.\n\n"
        "## Owners\n\n"
        "- `vision.md`: product north star.\n"
        "- `options.md`: curated product-level, future-wave, and unknown-owner options before commitment.\n"
        "- `status.md`: current posture, active pointers, WIP, blockers, and next action.\n"
        "- `waves/wNN-*/`: wave, initiative, local options, forecast, discovery, sprint, and evidence owners.\n"
        "- `source-packs/YYYY-MM-DD-*/`: retained context only.\n",
        encoding="utf-8",
    )
    (ops_root / "SOURCE_PACK_ATLAS.md").write_text(
        "# Source Pack Atlas\n\n"
        "Source packs are dated retained context. Search first, open the owning "
        "`00-readme.md`, then open at most one named section file unless the "
        "current artifact records a broader read receipt.\n",
        encoding="utf-8",
    )
    print(ops_root.as_posix())
    return 0


def command_create_wave(args: argparse.Namespace) -> int:
    ops_root = Path(args.ops_root).resolve()
    wave_id = args.wave_id.lower()
    if not re.fullmatch(r"w\d{2}", wave_id):
        raise ValueError("wave_id must use wNN format")
    wave_root = ops_root / "waves" / f"{wave_id}-{slugify(args.slug)}"
    ensure_empty(wave_root)
    remove_gitkeep(ops_root / "waves")
    add_gitkeep(wave_root / "discoveries")
    add_gitkeep(wave_root / "initiatives")
    add_gitkeep(wave_root / "source-packs")
    (wave_root / "wave.md").write_text(
        f"# Wave {wave_id.upper()}: {args.slug.replace('-', ' ').title()}\n\n"
        "## Outcome\n\nReplace with the wave outcome.\n\n"
        "## Why Now\n\nReplace with the reason this wave matters now.\n\n"
        "## Scope Boundaries\n\n1. Replace with the first boundary.\n\n"
        "## Bet Framing\n\n"
        "- Appetite: Replace with wave appetite.\n"
        "- Success evidence: Replace with success evidence.\n"
        "- Circuit breaker: Replace with stop or reroute condition.\n"
        "- Deferral path: Replace with where not-now work lives.\n\n"
        "## Outcome Signals\n\n"
        "- Product/user signal: Replace with product, user, customer, or operator value signal.\n"
        "- Delivery/flow signal: Replace with delivery, WIP, blocked-time, or route-clarity signal.\n"
        "- Quality/stability signal: Replace with correctness, reliability, validation, or failure-handling signal.\n"
        "- Context/evidence cost signal: Replace with context, evidence, or recovery-cost signal.\n\n"
        "## Forecast And Appetite\n\n"
        "- Appetite: Replace with wave appetite.\n"
        "- Forecast range/count: Replace with candidate count, timebox, or tranche.\n"
        "- Confidence: Replace with high, medium, or low and why.\n"
        "- Throughput basis: Replace with recent completed sprint evidence or `not available`.\n"
        "- Known unknowns: Replace with the main forecast risks.\n"
        "- Scope hammers: Replace with operator-choice cut, defer, or reframe options.\n"
        "- Expansion trigger: Replace with what requires operator decision or buy-more.\n\n"
        "## Non-Goals\n\n1. Replace with the first non-goal.\n\n"
        "## Status\n\nState: draft.\n\n"
        "## Initiative Map\n\nNo initiatives yet.\n\n"
        "## Retained Inputs\n\nNone yet.\n\n"
        "## Transition And Reroute Rules\n\n1. Replace with transition or reroute rule.\n",
        encoding="utf-8",
    )
    print(wave_root.as_posix())
    return 0


def command_create_initiative(args: argparse.Namespace) -> int:
    wave_root = Path(args.wave_root).resolve()
    wave_id_from_root(wave_root)
    initiatives_root = wave_root / "initiatives"
    initiatives_root.mkdir(parents=True, exist_ok=True)
    number = (
        int(args.initiative_id[1:])
        if args.initiative_id
        else next_number(initiatives_root, INIT_RE)
    )
    initiative_id = f"i{number:02d}"
    initiative_root = initiatives_root / f"{initiative_id}-{slugify(args.slug)}"
    ensure_empty(initiative_root)
    remove_gitkeep(initiatives_root)
    replacements = {
        "REPLACE_INITIATIVE_TITLE": args.slug.replace("-", " ").title(),
        "REPLACE_APPETITE": "Replace with initiative appetite.",
        "REPLACE_SUCCESS_EVIDENCE": "Replace with success evidence.",
        "REPLACE_CIRCUIT_BREAKER": "Replace with circuit breaker.",
        "REPLACE_DEFERRAL_PATH": "Replace with deferral path.",
    }
    copy_rendered_tree(
        INITIATIVE_TEMPLATE_ROOT, initiative_root, replacements, skip_parts={"sprint-template"}
    )
    add_gitkeep(initiative_root / "discoveries")
    add_gitkeep(initiative_root / "sprints")
    print((initiative_root / "initiative.md").as_posix())
    return 0


def command_create_discovery(args: argparse.Namespace) -> int:
    owner = Path(args.owner_root).resolve()
    if (owner / "wave.md").exists():
        wave_root = owner
        wave_id = wave_id_from_root(wave_root)
        discoveries_root = wave_root / "discoveries"
        number = next_number(discoveries_root, WAVE_DISCOVERY_RE)
        filename = f"{wave_id}-d{number:02d}-{slugify(args.slug)}.md"
    elif (owner / "initiative.md").exists():
        wave_root = owning_wave_root(owner)
        wave_id = wave_id_from_root(wave_root)
        initiative_id = initiative_id_from_root(owner)
        discoveries_root = owner / "discoveries"
        number = next_number(discoveries_root, INIT_DISCOVERY_RE)
        filename = f"{wave_id}-{initiative_id}-d{number:02d}-{slugify(args.slug)}.md"
    else:
        raise ValueError("owner_root must be a wave root or initiative root")
    discoveries_root.mkdir(parents=True, exist_ok=True)
    path = discoveries_root / filename
    if path.exists():
        raise ValueError(f"Discovery already exists: {path}")
    remove_gitkeep(discoveries_root)
    path.write_text(
        f"# Discovery: {args.slug.replace('-', ' ').title()}\n\n"
        "## Question\n\nReplace with the decision question.\n\n"
        "## Context Receipt\n\nReplace with loaded artifacts and skipped surfaces.\n\n"
        "## Repo Truth\n\nReplace with current repo truth.\n\n"
        "## User Or Operator Evidence\n\n"
        "- Status: Replace with `used`, `not triggered`, or `deferred`.\n"
        "- Evidence: Replace with user/operator input, operator decision, or `n/a`.\n"
        "- Decision impact: Replace with how the evidence changes this decision, or why it does not.\n\n"
        "## Forecast Impact\n\n"
        "- Status: Replace with `fits appetite`, `cuts/defers scope`, "
        "`requires operator buy-more`, or `reroutes/stops`.\n"
        "- Evidence: Replace with forecast basis or `n/a`.\n"
        "- Decision impact: Replace with roadmap, index, or status update needed.\n\n"
        "## Options\n\n- Recommended: Replace with recommended path.\n"
        "- Rejected: Replace with rejected alternative.\n\n"
        "## Recommendation\n\nReplace with recommendation.\n\n"
        "## Validation Expectations\n\nReplace with validation expectations.\n\n"
        "## Decision Slot\n\nPending operator decision.\n",
        encoding="utf-8",
    )
    print(path.as_posix())
    return 0


def command_create_source_pack(args: argparse.Namespace) -> int:
    owner = Path(args.owner_root).resolve()
    if (owner / "wave.md").exists():
        packs_root = owner / "source-packs"
    else:
        packs_root = owner / "source-packs" if owner.name == ".ub-workflows" else owner
    pack_date = args.date or datetime.now(tz=timezone.utc).date().isoformat()
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", pack_date):
        raise ValueError("--date must use YYYY-MM-DD")
    target = packs_root / f"{pack_date}-{slugify(args.slug)}"
    ensure_empty(target)
    remove_gitkeep(packs_root)
    (target / "00-readme.md").write_text(
        "---\n"
        f"artifact_id          : source-pack-{slugify(args.slug)}-readme\n"
        "artifact_type        : source_pack_readme\n"
        "status               : retained\n"
        "context_tier         : T3\n"
        f"updated_at           : {pack_date}\n"
        "summary_budget_lines : 120\n"
        "---\n\n"
        f"# Source Pack: {args.slug.replace('-', ' ').title()}\n\n"
        "## Status\n\nStatus: retained context.\n"
        f"Date basis: {pack_date}.\n"
        "Last reviewed: replace when reviewed.\n\n"
        "## Context Routing\n\n"
        "Read triggers: Replace with triggers.\n\n"
        "Do not read for: startup, live state, or execution authorization.\n\n"
        "Default section limit: open at most one named section file after this "
        "readme unless the current artifact records a broader read receipt.\n\n"
        "Promotion rule: facts become current truth only when promoted into the owning artifact.\n",
        encoding="utf-8",
    )
    print(target.as_posix())
    return 0


def command_prepare_sprint(args: argparse.Namespace) -> int:
    initiative_root = Path(args.initiative_root).resolve()
    if not (initiative_root / "initiative.md").exists():
        raise ValueError("initiative_root must contain initiative.md")
    wave_root = owning_wave_root(initiative_root)
    wave_id = wave_id_from_root(wave_root)
    initiative_id = initiative_id_from_root(initiative_root)
    sprints_root = initiative_root / "sprints"
    sprints_root.mkdir(parents=True, exist_ok=True)
    if args.all:
        candidates = []
        for line in (initiative_root / "roadmap.md").read_text(encoding="utf-8").splitlines():
            line_text = line.strip()
            if line_text.startswith("- [ ]"):
                candidate = line_text.removeprefix("- [ ]").strip()
                if candidate.startswith("`") and candidate.endswith("`"):
                    candidate = candidate[1:-1].strip()
                candidates.append(slugify(candidate))
        if not candidates:
            candidates = [args.slug]
    else:
        candidates = [args.slug]
    created: list[Path] = []
    for candidate in candidates:
        number = next_number(sprints_root, SPRINT_RE)
        candidate_slug = slugify(candidate)
        sprint_slug = (
            candidate_slug if candidate_slug.startswith("sprint-") else f"sprint-{candidate_slug}"
        )
        sprint_root = sprints_root / f"{wave_id}-{initiative_id}-s{number:02d}-{sprint_slug}"
        ensure_empty(sprint_root)
        remove_gitkeep(sprints_root)
        sprint_id = f"{wave_id}-{initiative_id}-s{number:02d}"
        today = datetime.now(tz=timezone.utc).date().isoformat()
        replacements = {
            "REPLACE_SPRINT_ARTIFACT_ID": sprint_root.name,
            "REPLACE_DECISION_LOG_ARTIFACT_ID": f"{sprint_id}-decision-log",
            "REPLACE_CLOSEOUT_ARTIFACT_ID": f"{sprint_id}-closeout",
            "REPLACE_EVIDENCE_INDEX_ARTIFACT_ID": f"{sprint_id}-evidence-index",
            "REPLACE_UPDATED_AT": today,
            "REPLACE_SPRINT_TITLE": candidate.replace("-", " ").title(),
            "REPLACE_SPRINT_OBJECTIVE": f"Deliver {candidate.replace('-', ' ')}.",
            "REPLACE_SPRINT_SOURCE": "accepted discovery or reviewed preview pending",
            "REPLACE_APPETITE": "Replace with sprint appetite.",
            "REPLACE_SUCCESS_EVIDENCE": "Replace with success evidence.",
            "REPLACE_CIRCUIT_BREAKER": "Replace with circuit breaker.",
            "REPLACE_NON_GOALS": "Replace with non-goals.",
            "REPLACE_DEFERRAL_PATH": "Replace with deferral path.",
        }
        copy_rendered_tree(SPRINT_TEMPLATE_ROOT, sprint_root, replacements)
        created.append(sprint_root)
        if not args.all:
            break
    for path in created:
        print(path.as_posix())
    return 0


def command_archive_initiative(args: argparse.Namespace) -> int:
    initiative_root = Path(args.initiative_root).resolve()
    wave_root = owning_wave_root(initiative_root)
    archive_root = wave_root / "archive" / initiative_root.name
    if archive_root.exists():
        raise ValueError(f"Archive target already exists: {archive_root}")
    archive_root.parent.mkdir(parents=True, exist_ok=True)
    shutil.move(initiative_root.as_posix(), archive_root.as_posix())
    refresh_gitkeep(initiative_root.parent)
    print(archive_root.as_posix())
    return 0


def generated_artifact_paths(workflow_root: Path) -> list[Path]:
    candidates: list[Path] = []
    for name in (
        "wave.md",
        "initiative.md",
        "options.md",
        "roadmap.md",
        "index.md",
        "retained-note.md",
    ):
        path = workflow_root / name
        if path.exists():
            candidates.append(path)
    for pattern in (
        "discoveries/*.md",
        "sprints/*/sprint.md",
        "sprints/*/decision-log.md",
        "sprints/*/closeout.md",
        "sprints/*/evidence/index.md",
    ):
        candidates.extend(sorted(workflow_root.glob(pattern)))
    return candidates


def discover_generated_roots_for_placeholder_scan(scan_root: Path) -> list[Path]:
    root = scan_root.resolve()
    if (root / "initiative.md").exists() or (root / "wave.md").exists():
        return [root]
    if root.name == "waves":
        return sorted(path for path in root.iterdir() if path.is_dir() and WAVE_RE.match(path.name))
    if root.name == "initiatives":
        return sorted(path for path in root.iterdir() if path.is_dir() and INIT_RE.match(path.name))
    if root.name == ".ub-workflows":
        roots: list[Path] = []
        if (root / "waves").exists():
            for wave in sorted((root / "waves").glob("w??-*")):
                roots.append(wave)
                roots.extend(sorted((wave / "initiatives").glob("i??-*")))
        return [path for path in roots if path.is_dir()]
    if (root / ".ub-workflows").exists():
        return discover_generated_roots_for_placeholder_scan(root / ".ub-workflows")
    raise ValueError(f"Unsupported scan root: {scan_root}")


def collect_placeholder_findings(workflow_root: Path) -> list[PlaceholderFinding]:
    findings: list[PlaceholderFinding] = []
    for path in generated_artifact_paths(workflow_root):
        in_code_fence = False
        for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
            if CODE_FENCE_RE.match(line):
                in_code_fence = not in_code_fence
                continue
            if in_code_fence:
                continue
            findings.extend(
                PlaceholderFinding(
                    workflow_root,
                    path,
                    line_number,
                    "machine-token",
                    "required",
                    marker,
                    line.strip(),
                )
                for marker in MACHINE_PLACEHOLDER_RE.findall(line)
            )
            if HUMAN_PLACEHOLDER_RE.search(line):
                severity = (
                    "advisory" if path.name in {"closeout.md", "retained-note.md"} else "required"
                )
                findings.append(
                    PlaceholderFinding(
                        workflow_root,
                        path,
                        line_number,
                        "human-prompt",
                        severity,
                        "Replace with",
                        line.strip(),
                    )
                )
            if "PENDING_HANDOFF:" in line:
                findings.append(
                    PlaceholderFinding(
                        workflow_root,
                        path,
                        line_number,
                        "pending-handoff",
                        "advisory",
                        "PENDING_HANDOFF:",
                        line.strip(),
                    )
                )
    return findings


def format_placeholder_summary(workflow_root: Path, findings: list[PlaceholderFinding]) -> str:
    required = sum(1 for finding in findings if finding.severity == "required")
    advisory = len(findings) - required
    if not findings:
        return f"placeholder summary: no unresolved generated-artifact placeholders under {workflow_root.as_posix()}"
    lines = [
        f"placeholder summary: {required} required, {advisory} advisory finding(s) under {workflow_root.as_posix()}"
    ]
    for finding in findings:
        try:
            rel = finding.file_path.relative_to(workflow_root)
        except ValueError:
            rel = finding.file_path
        lines.append(
            f"- {finding.severity} {finding.category}: {rel.as_posix()}:{finding.line_number} -> {finding.marker}"
        )
    return "\n".join(lines)


def collect_option_cards(path: Path) -> list[OptionCard]:
    cards: list[OptionCard] = []
    lines = path.read_text(encoding="utf-8").splitlines()
    current_title: str | None = None
    current_line = 0
    current_fields: set[str] = set()
    current_reviewed: date | None = None

    def finish_card() -> None:
        nonlocal current_fields, current_line, current_reviewed, current_title
        if current_title is None:
            return
        cards.append(
            OptionCard(
                file_path=path,
                line_number=current_line,
                title=current_title,
                fields=frozenset(current_fields),
                last_reviewed=current_reviewed,
            )
        )
        current_title = None
        current_line = 0
        current_fields = set()
        current_reviewed = None

    for line_number, line in enumerate(lines, start=1):
        match = OPTION_HEADING_RE.match(line)
        if not match:
            field_match = OPTION_FIELD_RE.match(line)
            if current_title is not None and field_match:
                current_fields.add(field_match.group("label").strip())
            date_match = OPTION_DATE_RE.match(line)
            if current_title is not None and date_match:
                current_reviewed = date.fromisoformat(date_match.group("date"))
            continue
        level = len(match.group("marks"))
        if level == 2:
            finish_card()
            continue
        finish_card()
        current_title = match.group("title").strip()
        current_line = line_number
    finish_card()
    return cards


def collect_option_board_findings(
    workflow_root: Path,
    path: Path,
    *,
    today: date,
    stale_days: int,
) -> list[OptionsFinding]:
    findings: list[OptionsFinding] = []
    if not path.exists():
        findings.append(
            OptionsFinding(
                workflow_root=workflow_root,
                file_path=path,
                line_number=None,
                category="missing-options-board",
                severity="required",
                message=f"missing options board: {path.as_posix()}",
            )
        )
        return findings

    lines = path.read_text(encoding="utf-8").splitlines()
    for line_number, line in enumerate(lines, start=1):
        match = OPTION_HEADING_RE.match(line)
        if not match or len(match.group("marks")) != 2:
            continue
        normalized = match.group("title").strip().lower()
        if normalized.startswith(FORBIDDEN_OPTION_LANE_PREFIXES):
            findings.append(
                OptionsFinding(
                    workflow_root=workflow_root,
                    file_path=path,
                    line_number=line_number,
                    category="forbidden-options-lane",
                    severity="required",
                    message=f"forbidden options-board archive lane: {match.group('title')}",
                )
            )

    for card in collect_option_cards(path):
        missing_fields = sorted(REQUIRED_OPTION_FIELDS - card.fields)
        findings.extend(
            [
                OptionsFinding(
                    workflow_root=workflow_root,
                    file_path=card.file_path,
                    line_number=card.line_number,
                    category="missing-option-field",
                    severity="required",
                    message=f"option card `{card.title}` is missing `{field_name}`",
                )
                for field_name in missing_fields
            ]
        )
        if card.last_reviewed is None:
            continue
        age_days = (today - card.last_reviewed).days
        if age_days > stale_days:
            findings.append(
                OptionsFinding(
                    workflow_root=workflow_root,
                    file_path=card.file_path,
                    line_number=card.line_number,
                    category="stale-option-review",
                    severity="advisory",
                    message=(
                        f"option card `{card.title}` was last reviewed "
                        f"{age_days} day(s) ago"
                    ),
                )
            )
    return findings


def options_review_routing_present(workflow_root: Path) -> bool:
    for relative in ("AGENTS.md", "WORKFLOW_ATLAS.md", "status.md"):
        path = workflow_root / relative
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8").lower()
        if "options.md" in text and "transition" in text:
            return True
    return False


def collect_historical_backlog_findings(workflow_root: Path) -> list[OptionsFinding]:
    findings: list[OptionsFinding] = []
    for path in sorted((workflow_root / "source-packs").glob("**/*.md")):
        for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
            if "backlog" in line.lower() or "wishlist" in line.lower():
                findings.append(
                    OptionsFinding(
                        workflow_root=workflow_root,
                        file_path=path,
                        line_number=line_number,
                        category="historical-backlog-language",
                        severity="advisory",
                        message="retained source-pack wording mentions backlog or wishlist",
                    )
                )
    return findings


def collect_product_option_visibility_findings(workflow_root: Path) -> list[OptionsFinding]:
    root_options = workflow_root / "options.md"
    root_text = root_options.read_text(encoding="utf-8") if root_options.exists() else ""
    initiative_root = active_initiative_root(workflow_root)
    if initiative_root is None or not initiative_root.exists():
        return []

    findings: list[OptionsFinding] = []
    for path in (initiative_root / "roadmap.md", initiative_root / "index.md"):
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8")
        findings.extend(
            [
                OptionsFinding(
                    workflow_root=workflow_root,
                    file_path=path,
                    line_number=None,
                    category="product-option-only-local",
                    severity="advisory",
                    message=f"product-level marker `{marker}` appears locally but not in root options",
                )
                for marker in PRODUCT_OPTION_MARKERS
                if marker in text and marker not in root_text
            ]
        )
    return findings


def collect_workflow_options_findings(
    scan_root: Path,
    *,
    mode: str = "normal",
    stale_days: int = 45,
    include_history: bool = False,
    today: date | None = None,
) -> list[OptionsFinding]:
    workflow_root = discover_workflow_root(scan_root)
    current_day = today or datetime.now(tz=timezone.utc).date()
    findings: list[OptionsFinding] = []

    root_options = workflow_root / "options.md"
    if not root_options.exists():
        findings.append(
            OptionsFinding(
                workflow_root=workflow_root,
                file_path=root_options,
                line_number=None,
                category="missing-root-options",
                severity="required",
                message="missing root options board",
            )
        )

    initiative_root = active_initiative_root(workflow_root)
    if initiative_root is not None:
        initiative_options = initiative_root / "options.md"
        if not initiative_options.exists():
            findings.append(
                OptionsFinding(
                    workflow_root=workflow_root,
                    file_path=initiative_options,
                    line_number=None,
                    category="missing-initiative-options",
                    severity="required",
                    message="active initiative is missing local options board",
                )
            )

    roadmap = active_initiative_roadmap(workflow_root)
    if roadmap and roadmap.exists() and "## Later Candidate Queue" in roadmap.read_text(
        encoding="utf-8"
    ):
        findings.append(
            OptionsFinding(
                workflow_root=workflow_root,
                file_path=roadmap,
                line_number=None,
                category="later-candidate-queue",
                severity="required",
                message="active roadmap contains `## Later Candidate Queue`",
            )
        )

    for path in option_board_paths(workflow_root, include_history=include_history):
        findings.extend(
            collect_option_board_findings(
                workflow_root,
                path,
                today=current_day,
                stale_days=stale_days,
            )
        )

    if mode in {"transition", "terminal-audit"} and not options_review_routing_present(
        workflow_root
    ):
        findings.append(
            OptionsFinding(
                workflow_root=workflow_root,
                file_path=workflow_root / "AGENTS.md",
                line_number=None,
                category="missing-transition-routing",
                severity="required",
                message="transition mode requires root options review routing",
            )
        )

    if mode in {"closeout", "terminal-audit"} and initiative_root is not None:
        initiative_options = initiative_root / "options.md"
        if initiative_options.exists():
            findings.extend(
                [
                    OptionsFinding(
                        workflow_root=workflow_root,
                        file_path=card.file_path,
                        line_number=card.line_number,
                        category="unresolved-local-option",
                        severity="required",
                        message=f"local option `{card.title}` remains unresolved for {mode}",
                    )
                    for card in collect_option_cards(initiative_options)
                ]
            )

    findings.extend(collect_product_option_visibility_findings(workflow_root))
    findings.extend(collect_historical_backlog_findings(workflow_root))
    return findings


def format_options_summary(workflow_root: Path, findings: list[OptionsFinding]) -> str:
    required = sum(1 for finding in findings if finding.severity == "required")
    advisory = len(findings) - required
    if not findings:
        return (
            "options summary: no options-board findings under "
            f"{workflow_root.as_posix()}"
        )
    lines = [
        "options summary: "
        f"{required} required, {advisory} advisory finding(s) under "
        f"{workflow_root.as_posix()}"
    ]
    for finding in findings:
        try:
            rel = finding.file_path.relative_to(workflow_root)
        except ValueError:
            rel = finding.file_path
        suffix = "" if finding.line_number is None else f":{finding.line_number}"
        lines.append(
            f"- {finding.severity} {finding.category}: "
            f"{rel.as_posix()}{suffix} -> {finding.message}"
        )
    return "\n".join(lines)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    bootstrap = subparsers.add_parser("bootstrap")
    bootstrap.add_argument("--ops-root", default=str(DEFAULT_OPS_ROOT))

    wave = subparsers.add_parser("create-wave")
    wave.add_argument("wave_id")
    wave.add_argument("slug")
    wave.add_argument("--ops-root", default=str(DEFAULT_OPS_ROOT))

    initiative = subparsers.add_parser("create-initiative")
    initiative.add_argument("wave_root")
    initiative.add_argument("slug")
    initiative.add_argument("--initiative-id")

    discovery = subparsers.add_parser("create-discovery")
    discovery.add_argument("owner_root")
    discovery.add_argument("slug")

    source_pack = subparsers.add_parser("create-source-pack")
    source_pack.add_argument("owner_root")
    source_pack.add_argument("slug")
    source_pack.add_argument("--date")

    sprint = subparsers.add_parser("prepare-sprint")
    sprint.add_argument("initiative_root")
    sprint.add_argument("slug")
    sprint.add_argument("--all", action="store_true")

    archive = subparsers.add_parser("archive-initiative")
    archive.add_argument("initiative_root")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    match args.command:
        case "bootstrap":
            return command_bootstrap(args)
        case "create-wave":
            return command_create_wave(args)
        case "create-initiative":
            return command_create_initiative(args)
        case "create-discovery":
            return command_create_discovery(args)
        case "create-source-pack":
            return command_create_source_pack(args)
        case "prepare-sprint":
            return command_prepare_sprint(args)
        case "archive-initiative":
            return command_archive_initiative(args)
    raise AssertionError(args.command)


if __name__ == "__main__":
    raise SystemExit(main())
