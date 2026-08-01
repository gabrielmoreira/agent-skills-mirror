#!/usr/bin/env python3
"""Summarize the agent-instruction surface for a project.

Inventories AGENTS.md / CLAUDE.md / Codex / Copilot / Gemini instruction files,
parses Codex config.toml for project trust + plugin/feature state (with sensitive
values redacted), and flags drift between Claude and Codex surfaces.

Run as: python3 check_agent_context.py [ROOT] [summary|deep]
"""

from __future__ import annotations

import argparse
import fnmatch
import hashlib
import json
import os
import re
import shlex
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Optional

SENSITIVE_RE = re.compile(r"(api[_-]?key|token|secret|password|credential)", re.IGNORECASE)
PROJECT_RE = re.compile(r'^\[projects\."(.+)"\]\s*$')
TABLE_RE = re.compile(r'^\[([A-Za-z0-9_.@"\-/]+)\]\s*$')
OPERATIONAL_RULE_RE = re.compile(
    r"(Git Safety|Public Issue Replies|Investigation Honesty|Verification|Response Style|Commit|Security)",
    re.IGNORECASE,
)


def rel(path: Path, root: Path) -> str:
    try:
        return path.resolve().relative_to(root).as_posix()
    except ValueError:
        return path.as_posix()


def read(path: Path, limit: Optional[int] = None) -> str:
    try:
        data = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return ""
    return data[:limit] if limit else data


def yes(path: Path) -> str:
    return "yes" if path.exists() else "no"


def print_list(
    title: str,
    items: list[str],
    empty: str = "(none)",
    limit: Optional[int] = None,
) -> None:
    print(f"{title}:")
    shown = items if limit is None else items[:limit]
    if not shown:
        print(f"  {empty}")
        return
    for item in shown:
        print(f"  {item}")
    if limit is not None and len(items) > limit:
        print(f"  ... {len(items) - limit} more")


def load_json(path: Path) -> tuple[Optional[object], Optional[str]]:
    if not path.is_file():
        return None, None
    try:
        return json.loads(read(path)), None
    except json.JSONDecodeError as exc:
        return None, f"{path.name}: invalid JSON at line {exc.lineno}"


def redact_sensitive_entries(value: object, prefix: str = "") -> list[str]:
    entries: list[str] = []
    if isinstance(value, dict):
        for key, child in value.items():
            child_prefix = f"{prefix}.{key}" if prefix else str(key)
            if SENSITIVE_RE.search(str(key)):
                entries.append(f"{child_prefix}=[REDACTED]")
                continue
            entries.extend(redact_sensitive_entries(child, child_prefix))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            entries.extend(redact_sensitive_entries(child, f"{prefix}[{index}]"))
    return entries


def string_list(value: object) -> list[str]:
    if isinstance(value, list):
        return [str(item) if not SENSITIVE_RE.search(str(item)) else "[REDACTED]" for item in value]
    if isinstance(value, dict):
        return sorted(str(key) for key in value)
    if isinstance(value, str):
        return ["[REDACTED]" if SENSITIVE_RE.search(value) else value]
    return []


def skill_root_count(path: Path, include_root_md: bool) -> int:
    if not path.is_dir():
        return 0
    count = len(list(path.rglob("SKILL.md")))
    if include_root_md:
        count += len([p for p in path.glob("*.md") if p.name != "SKILL.md"])
    return count


def same_physical_file(left: Path, right: Path) -> bool:
    try:
        return left.samefile(right)
    except OSError:
        return False


def unique_physical_files(paths: list[Path]) -> list[Path]:
    unique: list[Path] = []
    seen: set[tuple[int, int]] = set()
    for path in paths:
        try:
            stat = path.stat()
        except OSError:
            continue
        identity = (stat.st_dev, stat.st_ino)
        if identity in seen:
            continue
        seen.add(identity)
        unique.append(path)
    return unique


def project_instruction_files(root: Path) -> list[Path]:
    files = [
        root / "AGENTS.md",
        root / "CLAUDE.md",
        root / ".github" / "copilot-instructions.md",
        root / "GEMINI.md",
    ]
    instructions_dir = root / ".github" / "instructions"
    if instructions_dir.is_dir():
        files.extend(sorted(instructions_dir.glob("*.md")))
    return unique_physical_files([path for path in files if path.is_file()])


def claude_delegates_to_agents(path: Path) -> bool:
    text = read(path, 20_000)
    if not text:
        return False
    meaningful = [
        line.strip()
        for line in text.splitlines()
        if line.strip() and not line.strip().startswith("#")
    ]
    return any("AGENTS.md" in line for line in meaningful)


def has_operational_rules(path: Path) -> bool:
    text = read(path, 40_000)
    if not text:
        return False
    return len(set(m.group(1).lower() for m in OPERATIONAL_RULE_RE.finditer(text))) >= 2


def looks_identity_only(path: Path) -> bool:
    text = read(path, 40_000)
    if not text:
        return False
    return "nian-identity:start" in text and not has_operational_rules(path)


def rule_paths(text: str) -> list[str]:
    if not text.startswith("---"):
        return []
    lines = text.splitlines()
    paths: list[str] = []
    in_paths = False
    for line in lines[1:]:
        stripped = line.strip()
        if stripped == "---":
            break
        if stripped == "paths:":
            in_paths = True
            continue
        if in_paths and stripped.startswith("-"):
            value = stripped[1:].strip().strip('"\'')
            if value:
                paths.append(value)
            continue
        if in_paths and stripped and not line.startswith((" ", "\t")):
            in_paths = False
    return paths


def summarize_rule_context(project_rules: Path) -> list[str]:
    path_counts: Counter[str] = Counter()
    path_words: Counter[str] = Counter()
    scoped_files = 0
    scoped_words = 0
    always_files = 0
    always_words = 0
    if project_rules.is_dir():
        for path in unique_physical_files(sorted(project_rules.glob("*.md"))):
            text = read(path)
            words = len(text.split())
            paths = rule_paths(text)
            if paths:
                scoped_files += 1
                scoped_words += words
                for selector in paths:
                    path_counts[selector] += 1
                    path_words[selector] += words
            else:
                always_files += 1
                always_words += words
    ranked = sorted(
        path_counts,
        key=lambda selector: (path_words[selector], path_counts[selector], selector),
        reverse=True,
    )
    lines = [
        "=== PATH-SCOPED CONTEXT ===",
        f"path_scoped_rule_files: {scoped_files}",
        f"path_scoped_rule_words: {scoped_words}",
        f"always_loaded_rule_files: {always_files}",
        f"always_loaded_rule_words: {always_words}",
        "largest_path_triggers:",
    ]
    if not ranked:
        lines.append("  (none)")
    else:
        for selector in ranked[:10]:
            lines.append(
                f"  selector={selector} files={path_counts[selector]} "
                f"combined_words={path_words[selector]}"
            )
    return lines


def skill_name(path: Path) -> str:
    for line in read(path, 8_000).splitlines()[:40]:
        match = re.match(r"^name:\s*[\"']?([^\"']+?)[\"']?\s*$", line.strip())
        if match:
            return match.group(1).strip()
    return ""


def display_path(path: Path, root: Path, home: Path) -> str:
    for base, prefix in ((root, "project:/"), (home, "~/")):
        try:
            return prefix + path.relative_to(base).as_posix()
        except ValueError:
            continue
    return path.as_posix()


def candidate_skill_files(root: Path, home: Path) -> list[Path]:
    roots = [
        root / ".claude" / "skills",
        root / ".agents" / "skills",
        root / ".codex" / "skills",
        home / ".claude" / "skills",
        home / ".agents" / "skills",
        home / ".codex" / "skills",
    ]
    candidates: list[Path] = []
    repository_roots: set[Path] = set()
    for skill_root in roots:
        if not skill_root.is_dir():
            continue
        candidates.extend(skill_root.glob("*/SKILL.md"))
        for child in skill_root.iterdir():
            if not child.is_symlink():
                continue
            try:
                resolved = child.resolve(strict=True)
            except OSError:
                continue
            if (resolved / "skills").is_dir() or (resolved / "plugins").is_dir():
                repository_roots.add(resolved)
    for repository in repository_roots:
        candidates.extend(repository.glob("skills/*/SKILL.md"))
    unique: dict[Path, Path] = {}
    for path in candidates:
        if not path.is_file():
            continue
        try:
            canonical = path.resolve(strict=True)
        except OSError:
            continue
        unique[canonical] = path
    return sorted(unique)


def summarize_skill_duplicates(root: Path, home: Path) -> tuple[str, list[str]]:
    by_name: dict[str, list[tuple[Path, str]]] = defaultdict(list)
    for path in candidate_skill_files(root, home):
        name = skill_name(path)
        if not name:
            continue
        try:
            digest = hashlib.sha256(path.read_bytes()).hexdigest()
        except OSError:
            continue
        by_name[name].append((path, digest))
    duplicate_lines: list[str] = []
    for name, entries in sorted(by_name.items()):
        if len(entries) < 2:
            continue
        digest_counts = Counter(digest for _, digest in entries)
        exact_duplicate = any(count > 1 for count in digest_counts.values())
        kind = "exact-copy" if exact_duplicate else "name-collision"
        surfaces = ", ".join(display_path(path, root, home) for path, _ in entries[:6])
        duplicate_lines.append(f"{name}: kind={kind} surfaces={surfaces}")
    lines = [
        "=== SKILL ROUTING DUPLICATES ===",
        f"skill_files_scanned: {sum(len(entries) for entries in by_name.values())}",
        f"duplicate_skill_names: {len(duplicate_lines)}",
        "duplicate_skills:",
    ]
    lines.extend(f"  {line}" for line in (duplicate_lines or ["(none)"]))
    return ("WARN" if duplicate_lines else "PASS"), lines


def parse_codex_config(
    path: Path,
) -> tuple[dict[str, str], list[str], list[str], list[str], list[str]]:
    projects: dict[str, str] = {}
    features: list[str] = []
    plugins: list[str] = []
    marketplaces: list[str] = []
    redacted: list[str] = []
    if not path.is_file():
        return projects, features, plugins, marketplaces, redacted

    section = ""
    for raw in read(path).splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        project_match = PROJECT_RE.match(line)
        if project_match:
            section = f'projects."{project_match.group(1)}"'
            projects.setdefault(project_match.group(1), "")
            continue
        table_match = TABLE_RE.match(line)
        if table_match:
            section = table_match.group(1)
            marketplace_match = re.match(r'marketplaces\.([A-Za-z0-9_.@-]+)$', section)
            plugin_match = re.match(r'plugins\."?([^"]+)"?$', section)
            if marketplace_match:
                marketplaces.append(marketplace_match.group(1))
            if plugin_match:
                plugins.append(plugin_match.group(1))
            continue

        if SENSITIVE_RE.search(line):
            key = line.split("=", 1)[0].strip() if "=" in line else "sensitive"
            redacted.append(f"{key}=[REDACTED]")
            continue

        if "=" not in line:
            continue
        key, value = [part.strip() for part in line.split("=", 1)]
        if section == "features" and value.split("#", 1)[0].strip().strip('"').lower() == "true":
            features.append(key)
        elif section.startswith('projects."') and key == "trust_level":
            project = section[len('projects."'): -1]
            projects[project] = value.strip('"')

    return (
        projects,
        sorted(set(features)),
        sorted(set(plugins)),
        sorted(set(marketplaces)),
        sorted(set(redacted)),
    )


def permission_rules(data: object, key: str) -> list[str]:
    if not isinstance(data, dict):
        return []
    permissions = data.get("permissions")
    if not isinstance(permissions, dict):
        return []
    value = permissions.get(key)
    if not isinstance(value, list):
        return []
    return [str(item) for item in value if isinstance(item, str)]


def parse_permission_rule(rule: str) -> tuple[str, str] | None:
    match = re.fullmatch(r"([A-Za-z][A-Za-z0-9_]*)\((.*)\)", rule.strip())
    if not match:
        return None
    return match.group(1), match.group(2).strip()


def normalized_rule_targets(rules: list[str], tool: str) -> list[str]:
    targets: list[str] = []
    for rule in rules:
        parsed = parse_permission_rule(rule)
        if parsed is None or parsed[0].lower() != tool.lower():
            continue
        targets.append(parsed[1].replace("\\", "/").lower())
    return targets


def expand_permission_target(target: str, home: Path) -> str:
    normalized = target.strip().replace("\\", "/")
    home_text = home.resolve().as_posix().lower()
    lowered = normalized.lower()
    for prefix in ("${home}", "$home", "~"):
        if lowered == prefix:
            return home_text
        if lowered.startswith(prefix + "/"):
            return home_text + normalized[len(prefix):].lower()
    return lowered


def target_covers_samples(target: str, home: Path, samples: tuple[str, ...]) -> bool:
    pattern = expand_permission_target(target, home)
    home_text = home.resolve().as_posix().lower()
    return all(
        fnmatch.fnmatchcase(f"{home_text}/{sample.lower()}", pattern)
        for sample in samples
    )


def target_covers_command(target: str, command: str) -> bool:
    escaped = re.escape(command.lower())
    return re.fullmatch(rf"{escaped}(?::\*|\s+\*.*)", target.strip()) is not None


def resolve_command_path(token: str, home: Path, project_root: Path) -> Path | None:
    if token.startswith("~/"):
        candidate = home / token[2:]
    elif token.startswith("$HOME/"):
        candidate = home / token[6:]
    elif token.startswith("${HOME}/"):
        candidate = home / token[8:]
    else:
        candidate = Path(token)
        if not candidate.is_absolute():
            candidate = project_root / candidate
    try:
        resolved = candidate.resolve(strict=True)
    except OSError:
        return None
    return resolved if resolved.is_file() else None


def resolve_hook_handler(command: str, home: Path, project_root: Path) -> Path | None:
    try:
        lexer = shlex.shlex(command, posix=True, punctuation_chars=True)
        lexer.whitespace_split = True
        tokens = list(lexer)
    except ValueError:
        return None
    if not tokens:
        return None

    command_index = 0
    if Path(tokens[0]).name == "env":
        command_index += 1
        while command_index < len(tokens) and (
            tokens[command_index] in {"-i", "--ignore-environment"}
            or re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*=.*", tokens[command_index])
        ):
            command_index += 1
    if command_index >= len(tokens):
        return None

    executable = tokens[command_index]
    if Path(executable).name in {"python", "python3"}:
        safe_flags = {"-B", "-E", "-I", "-O", "-OO", "-P", "-q", "-s", "-S", "-u", "-v"}
        for index, token in enumerate(tokens[command_index + 1 :], command_index + 1):
            if token == "--":
                continue
            if token.startswith("-"):
                if token not in safe_flags:
                    return None
                continue
            if index != len(tokens) - 1:
                return None
            resolved = resolve_command_path(token, home, project_root)
            return resolved if resolved is not None and resolved.suffix == ".py" else None
        return None
    return None


def hook_handler_enforces_pipe_block(path: Path) -> bool:
    canonical = Path(__file__).with_name("block-pipe-to-shell.py")
    try:
        return path.read_bytes() == canonical.read_bytes()
    except OSError:
        return False


def has_pretool_bash_hook(
    data: object,
    home: Path,
    project_root: Path,
) -> bool:
    if not isinstance(data, dict):
        return False
    hooks = data.get("hooks")
    if not isinstance(hooks, dict):
        return False
    pretool = hooks.get("PreToolUse")
    if not isinstance(pretool, list):
        return False
    for group in pretool:
        if not isinstance(group, dict) or group.get("matcher") != "Bash":
            continue
        handlers = group.get("hooks")
        if not isinstance(handlers, list):
            continue
        for handler in handlers:
            if not isinstance(handler, dict) or handler.get("type") != "command":
                continue
            command = handler.get("command")
            if not isinstance(command, str):
                continue
            path = resolve_hook_handler(command, home, project_root)
            if path is not None and hook_handler_enforces_pipe_block(path):
                return True
    return False


def deny_category_status(
    rules: list[str],
    hook_present: bool,
    home: Path,
) -> dict[str, bool]:
    reads = normalized_rule_targets(rules, "Read")
    bash = normalized_rule_targets(rules, "Bash")
    return {
        "ssh_directory": any(
            target_covers_samples(target, home, (".ssh/id_key", ".ssh/config"))
            for target in reads
        ),
        "aws_directory": any(
            target_covers_samples(target, home, (".aws/credentials", ".aws/config"))
            for target in reads
        ),
        "gnupg_directory": any(
            target_covers_samples(
                target,
                home,
                (".gnupg/private-keys-v1.d/key", ".gnupg/gpg.conf"),
            )
            for target in reads
        ),
        "gh_directory": any(
            target_covers_samples(
                target,
                home,
                (".config/gh/hosts.yml", ".config/gh/config.yml"),
            )
            for target in reads
        ),
        "env_files": any(
            target_covers_samples(
                target,
                home,
                ("project/.env", "project/.env.local"),
            )
            for target in reads
        ),
        "credential_files": any(
            target_covers_samples(
                target,
                home,
                ("project/credentials.json", "project/service-credentials.txt"),
            )
            for target in reads
        ),
        "secrets_directories": any(
            target_covers_samples(
                target,
                home,
                ("project/secrets/token", "project/secrets/nested/key"),
            )
            for target in reads
        ),
        "outbound_shell": all(
            any(target_covers_command(target, command) for target in bash)
            for command in ("ssh", "scp", "nc")
        ),
        "pipe_to_shell": hook_present,
        "git_reset_hard": any(
            target_covers_command(target, "git reset --hard") for target in bash
        ),
    }


def summarize_claude_permissions(
    global_path: Path,
    shared_path: Path,
    local_path: Path,
) -> tuple[str, list[str], list[str]]:
    sources = [
        ("global", global_path),
        ("shared", shared_path),
        ("local", local_path),
    ]
    loaded: dict[str, object] = {}
    errors: list[str] = []
    for label, path in sources:
        data, error = load_json(path)
        if error:
            errors.append(f"{label}: {error}")
        loaded[label] = data

    rules = {
        label: {
            key: permission_rules(loaded[label], key)
            for key in ("allow", "deny", "ask")
        }
        for label, _path in sources
    }
    combined_allow = [
        rule for label, _path in sources for rule in rules[label]["allow"]
    ]
    combined_deny = [
        rule for label, _path in sources for rule in rules[label]["deny"]
    ]
    home = global_path.parent.parent
    hook_present = any(
        has_pretool_bash_hook(
            loaded[label],
            home,
            path.parent.parent,
        )
        for label, path in sources
    )
    categories = deny_category_status(combined_deny, hook_present, home)
    missing = [name for name, present in categories.items() if not present]
    broad_read_allow = any(
        "**" in target
        for target in normalized_rule_targets(combined_allow, "Read")
    )
    credential_floor = all(categories.values())
    settings_surface_present = any(path.is_file() for _label, path in sources)
    findings: list[str] = list(errors)
    if settings_surface_present and not credential_floor:
        findings.append(
            "configured global + shared project + local project deny floor is incomplete: "
            + ", ".join(missing)
        )
    lines = [
        "=== CLAUDE PERMISSION SURFACE ===",
        f"global_settings_json: {yes(global_path)}",
        f"shared_project_settings_json: {yes(shared_path)}",
        f"local_project_settings_json: {yes(local_path)}",
    ]
    for label, _path in sources:
        lines.extend(
            f"{label}_{key}_count: {len(rules[label][key])}"
            for key in ("allow", "deny", "ask")
        )
    lines.extend([
        f"broad_read_allow_present: {'yes' if broad_read_allow else 'no'}",
        f"pretool_pipe_to_shell_hook: {'yes' if hook_present else 'no'}",
        "configured_sensitive_deny_floor_complete: "
        + (
            "not_applicable"
            if not settings_surface_present
            else ("yes" if credential_floor else "no")
        ),
    ])
    lines.extend(
        f"deny_{name}: {'yes' if present else 'no'}"
        for name, present in categories.items()
    )
    lines.append("permission_findings:")
    lines.extend(f"  {item}" for item in (findings or ["(none)"]))
    status = "WARN" if findings else "PASS"
    return status, lines, findings


def project_trust(projects: dict[str, str], root: Path) -> str:
    root_text = root.as_posix()
    if root_text in projects:
        return f"exact:{projects[root_text] or 'configured'}"
    candidates = []
    for project, level in projects.items():
        try:
            project_path = Path(project).expanduser().resolve()
        except OSError:
            continue
        if project_path == root:
            return f"exact:{level or 'configured'}"
        try:
            root.relative_to(project_path)
        except ValueError:
            continue
        candidates.append(
            (len(project_path.as_posix()), level or "configured", project_path.as_posix())
        )
    if candidates:
        _, level, project = sorted(candidates, reverse=True)[0]
        return f"inherited:{level} from {project}"
    return "missing"


def summarize_pi_surface(root: Path, home: Path) -> tuple[str, list[str]]:
    global_settings = home / ".pi" / "agent" / "settings.json"
    project_settings = root / ".pi" / "settings.json"
    settings_sources = [
        ("global_settings", global_settings),
        ("project_settings", project_settings),
    ]

    configured_skills: list[str] = []
    configured_packages: list[str] = []
    redacted_entries: list[str] = []
    findings: list[str] = []
    malformed = False

    for label, path in settings_sources:
        data, error = load_json(path)
        if error:
            malformed = True
            findings.append(error)
            continue
        if not isinstance(data, dict):
            continue
        configured_skills.extend(
            f"{label}.skills: {item}" for item in string_list(data.get("skills"))
        )
        configured_packages.extend(
            f"{label}.packages: {item}" for item in string_list(data.get("packages"))
        )
        redacted_entries.extend(
            f"{label}.{item}" for item in redact_sensitive_entries(data)
        )

    package_path = root / "package.json"
    package_pi_skills: list[str] = []
    data, error = load_json(package_path)
    if error:
        findings.append(error)
    elif isinstance(data, dict):
        pi_manifest = data.get("pi")
        if isinstance(pi_manifest, dict):
            package_pi_skills = string_list(pi_manifest.get("skills"))

    pi_skill_dirs = [
        ("global_pi_skill_roots", home / ".pi" / "agent" / "skills", True),
        ("project_pi_skill_roots", root / ".pi" / "skills", True),
        ("global_agents_skill_roots", home / ".agents" / "skills", False),
        ("project_agents_skill_roots", root / ".agents" / "skills", False),
    ]
    skill_counts = [
        f"{label}: {skill_root_count(path, include_root_md)}"
        for label, path, include_root_md in pi_skill_dirs
    ]

    has_pi_surface = (
        global_settings.is_file()
        or project_settings.is_file()
        or bool(package_pi_skills)
        or any(not line.endswith(": 0") for line in skill_counts)
        or bool(configured_skills)
        or bool(configured_packages)
    )
    if not has_pi_surface:
        findings.append("no Pi settings, package manifest, or skill directories found")

    status = "WARN" if malformed else "PASS"
    lines = [
        "=== PI SURFACE ===",
        f"pi_status: {status}",
        f"global_settings_json: {yes(global_settings)}",
        f"project_settings_json: {yes(project_settings)}",
        f"package_json: {yes(package_path)}",
    ]
    lines.extend(skill_counts)
    lines.append("package_pi_skills:")
    lines.extend(f"  {item}" for item in (package_pi_skills or ["(none)"]))
    lines.append("configured_skills:")
    lines.extend(f"  {item}" for item in (configured_skills or ["(none)"]))
    lines.append("configured_packages:")
    lines.extend(f"  {item}" for item in (configured_packages or ["(none)"]))
    lines.append("redacted_pi_entries:")
    lines.extend(f"  {item}" for item in (redacted_entries or ["(none)"]))
    lines.append("pi_findings:")
    lines.extend(f"  {item}" for item in (findings or ["(none)"]))
    return status, lines


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", nargs="?", default=".", help="Repo root (default: cwd)")
    parser.add_argument(
        "mode", nargs="?", default="summary", choices=("summary", "deep"),
        help="Output detail level",
    )
    args = parser.parse_args()
    root = Path(args.root).resolve()
    mode = args.mode
    home = Path(os.environ.get("HOME", str(Path.home()))).expanduser()

    if not root.is_dir():
        print(f"Repo root not found: {root}", file=sys.stderr)
        return 2

    instruction_files = project_instruction_files(root)
    agents = root / "AGENTS.md"
    claude = root / "CLAUDE.md"
    claude_aliases_agents = (
        agents.is_file() and claude.is_file() and same_physical_file(agents, claude)
    )
    claude_delegates = claude_aliases_agents or claude_delegates_to_agents(claude)
    github_instructions_dir = root / ".github" / "instructions"
    github_instruction_count = (
        len(list(github_instructions_dir.glob("*.md"))) if github_instructions_dir.is_dir() else 0
    )

    instruction_findings: list[str] = []
    if not instruction_files:
        instruction_findings.append("no project agent instruction files")
    if agents.is_file() and claude.is_file() and not claude_delegates:
        claude_lines = len(read(claude).splitlines())
        agents_lines = len(read(agents).splitlines())
        if claude_lines > 20 and agents_lines > 20:
            instruction_findings.append(
                "AGENTS.md and CLAUDE.md both contain substantial guidance without delegation"
            )

    global_codex_agents = home / ".codex" / "AGENTS.md"
    codex_config = home / ".codex" / "config.toml"
    projects, features, plugins, marketplaces, redacted = parse_codex_config(codex_config)
    trust = project_trust(projects, root) if codex_config.is_file() else "unavailable"
    codex_findings: list[str] = []
    if not global_codex_agents.is_file() and not codex_config.is_file():
        codex_findings.append("Codex surface not found")
    elif codex_config.is_file() and trust == "missing":
        codex_findings.append("current project is not configured in Codex trust table")

    global_claude = home / ".claude" / "CLAUDE.md"
    global_claude_settings = home / ".claude" / "settings.json"
    shared_project_settings = root / ".claude" / "settings.json"
    local_project_settings = root / ".claude" / "settings.local.json"
    project_rules = root / ".claude" / "rules"
    project_skills = root / ".claude" / "skills"
    global_skills = home / ".claude" / "skills"
    claude_findings: list[str] = []
    if claude.is_file() and claude_delegates:
        if claude_aliases_agents:
            claude_findings.append("CLAUDE.md resolves to the same physical file as AGENTS.md")
        else:
            claude_findings.append("CLAUDE.md delegates to AGENTS.md")
    if not global_claude.is_file() and not claude.is_file():
        claude_findings.append("Claude instruction surface not found")

    if (
        global_claude.is_file()
        and has_operational_rules(global_claude)
        and global_codex_agents.is_file()
        and looks_identity_only(global_codex_agents)
    ):
        codex_findings.append(
            "global Codex AGENTS.md has identity/memory context but lacks operational rules present in global Claude CLAUDE.md"
        )
    codex_config_text = read(codex_config) if codex_config.is_file() else ""
    if (
        'sandbox_mode = "danger-full-access"' in codex_config_text
        and 'approval_policy = "never"' in codex_config_text
    ):
        codex_findings.append(
            "Codex runs danger-full-access with approval_policy=never; Codex has no command-level deny mechanism, so the only levers are sandbox_mode and approval_policy -- surface once as a user tradeoff, not a per-project fix"
        )

    permission_status, permission_lines, permission_findings = summarize_claude_permissions(
        global_claude_settings,
        shared_project_settings,
        local_project_settings,
    )
    duplicate_status, duplicate_lines = summarize_skill_duplicates(root, home)

    conflict_findings: list[str] = []
    if agents.is_file() and claude.is_file() and not claude_delegates:
        conflict_findings.append("AGENTS.md and CLAUDE.md both exist; verify they do not diverge")

    instruction_status = "FAIL" if not instruction_files else ("WARN" if instruction_findings else "PASS")
    codex_status = "WARN" if codex_findings else "PASS"
    claude_status = (
        "WARN"
        if (
            (claude_findings and "surface not found" in " ".join(claude_findings))
            or permission_status == "WARN"
        )
        else "PASS"
    )
    conflict_status = "WARN" if conflict_findings else "PASS"

    print("=== AGENT INSTRUCTION SURFACE ===")
    print(f"agent_instruction_status: {instruction_status}")
    print(f"mode: {mode}")
    print(f"AGENTS.md: {yes(agents)}")
    print(f"CLAUDE.md: {yes(claude)}")
    print(f"claude_aliases_agents: {'yes' if claude_aliases_agents else 'no'}")
    print(f"claude_delegates_to_agents: {'yes' if claude_delegates else 'no'}")
    print(f".github/copilot-instructions.md: {yes(root / '.github' / 'copilot-instructions.md')}")
    print(f".github/instructions/*.md: {github_instruction_count}")
    print(f"GEMINI.md: {yes(root / 'GEMINI.md')}")
    print_list("instruction_files", [rel(path, root) for path in instruction_files])
    print_list("instruction_findings", instruction_findings)

    print("=== CODEX SURFACE ===")
    print(f"codex_status: {codex_status}")
    print(f"global_agents_md: {yes(global_codex_agents)}")
    print(f"global_config_toml: {yes(codex_config)}")
    print(f"project_trust: {trust}")
    print_list("features", features, limit=20 if mode == "summary" else None)
    print_list("enabled_plugins", plugins, limit=20 if mode == "summary" else None)
    print_list("marketplaces", marketplaces, limit=20 if mode == "summary" else None)
    print_list("redacted_config_entries", redacted)
    print_list("codex_findings", codex_findings)

    print("=== CLAUDE SURFACE ===")
    print(f"claude_status: {claude_status}")
    print(f"global_claude_md: {yes(global_claude)}")
    print(f"global_settings_json: {yes(global_claude_settings)}")
    print(f"project_claude_md: {yes(claude)}")
    print(f"shared_settings_json: {yes(shared_project_settings)}")
    print(f"settings_local_json: {yes(local_project_settings)}")
    rule_count = len(list(project_rules.glob('*.md'))) if project_rules.is_dir() else 0
    local_skill_count = len(list(project_skills.glob('*/SKILL.md'))) if project_skills.is_dir() else 0
    global_skill_count = len(list(global_skills.glob('*/SKILL.md'))) if global_skills.is_dir() else 0
    print(f"project_rules: {rule_count}")
    print(f"project_skills: {local_skill_count}")
    print(f"global_skills: {global_skill_count}")
    print_list("claude_findings", claude_findings)

    for line in permission_lines:
        print(line)

    for line in summarize_rule_context(project_rules):
        print(line)

    for line in duplicate_lines:
        print(line)

    _, pi_lines = summarize_pi_surface(root, home)
    for line in pi_lines:
        print(line)

    print("=== INSTRUCTION CONFLICTS ===")
    print(f"conflict_status: {conflict_status}")
    print_list("conflict_findings", conflict_findings)
    return 0


if __name__ == "__main__":
    sys.exit(main())
