#!/usr/bin/env python3
"""
resolve_provenance.py — Skill provenance resolver for skill-reflect.

Resolves the source GitHub repository for a named skill using the ordered lookup
defined in references/provenance-routing.md.  Stdlib only; no third-party deps.

Public API
----------
    from resolve_provenance import resolve_provenance

    result = resolve_provenance(
        skill_name="my-skill",
        skill_md_path="/path/to/SKILL.md",
        manifest_paths=["/path/to/extension.json"],
        registry_path="/path/to/registry.json",
        config={"mode": "standalone", "destination": {}},
    )
    # -> {
    #      "repo": "owner/repo",
    #      "source": "frontmatter",
    #      "confidence": "Confirmed",
    #      "install_scope": "project",
    #      "ref": "main",
    #      "sha": "abc1234"
    #    }

CLI
---
    python3 resolve_provenance.py --skill <name> \\
        [--skill-md <path>] [--manifest <path> ...] \\
        [--install-root <path>] [--install-scope <scope>] \\
        [--registry <path>] [--config <path>]
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from pathlib import Path
from typing import Optional

# ---------------------------------------------------------------------------
# YAML frontmatter parser (hand-rolled; handles simple key: value scalars only)
# ---------------------------------------------------------------------------

def _parse_frontmatter(text: str) -> dict:
    """
    Extract key: value pairs from the YAML frontmatter block at the top of *text*.

    Recognises the opening '---' on line 1 and reads until the closing '---'.
    Only simple scalar values are handled (string / empty).  Nested YAML,
    lists, and multi-line blocks are not needed for provenance keys.

    Returns an empty dict when no valid frontmatter is found.
    """
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return {}

    result: dict = {}
    for line in lines[1:]:
        stripped = line.strip()
        if stripped == "---":
            break  # end of frontmatter block
        if not stripped or stripped.startswith("#"):
            continue
        if ":" in stripped:
            key, _, raw_value = stripped.partition(":")
            key = key.strip()
            value = raw_value.strip()
            # Strip inline YAML comments
            value = re.sub(r"\s+#.*$", "", value)
            # Strip surrounding single or double quotes
            if len(value) >= 2 and value[0] == value[-1] and value[0] in ('"', "'"):
                value = value[1:-1]
            result[key] = value
    return result


def _read_skill_md(path: str | Path) -> dict:
    """Load a SKILL.md file and return its parsed frontmatter (or {})."""
    try:
        return _parse_frontmatter(Path(path).read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError):
        return {}


# ---------------------------------------------------------------------------
# GitHub URL → owner/repo extractor
# ---------------------------------------------------------------------------

# Matches github.com/owner/repo with optional .git suffix and trailing chars
_GH_RE = re.compile(
    r"github\.com[/:]([A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+?)(?:\.git)?(?:[/?#]|$)"
)
# Plain owner/repo shorthand (no slashes except the separator)
_OWNER_REPO_RE = re.compile(r"^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$")


def _extract_repo(value: str) -> Optional[str]:
    """
    Extract 'owner/repo' from a string that may be:
      - an owner/repo shorthand
      - a full GitHub HTTPS URL
      - an npm-style git URL  (https://github.com/owner/repo.git)
    Returns None for non-GitHub URLs.
    """
    if not value:
        return None
    v = value.strip()
    if _OWNER_REPO_RE.match(v):
        return v
    m = _GH_RE.search(v)
    return m.group(1) if m else None


_INSTALL_SCOPES = {"project", "user", "vendored", "unknown"}
_SAFE_ID_RE = re.compile(r"^[A-Za-z0-9_.@+-]{1,128}$")
_SAFE_VERSION_RE = re.compile(r"^[A-Za-z0-9_.+~-]{1,128}$")
_SAFE_REF_RE = re.compile(r"^[A-Za-z0-9_.+~/-]{1,160}$")
_SAFE_SHA_RE = re.compile(r"^[A-Fa-f0-9]{7,64}$")
_RESULT_METADATA_FIELDS = ("plugin", "marketplace", "version", "ref", "sha")


def _safe_identifier(value) -> Optional[str]:
    if isinstance(value, str):
        candidate = value.strip()
        if _SAFE_ID_RE.fullmatch(candidate):
            return candidate
    return None


def _safe_version(value) -> Optional[str]:
    if isinstance(value, str):
        candidate = value.strip()
        if _SAFE_VERSION_RE.fullmatch(candidate):
            return candidate
    return None


def _safe_ref(value) -> Optional[str]:
    if not isinstance(value, str):
        return None
    candidate = value.strip()
    if (
        not _SAFE_REF_RE.fullmatch(candidate)
        or candidate.startswith(("/", "./", "../"))
        or "/../" in f"/{candidate}/"
    ):
        return None
    return candidate


def _safe_sha(value) -> Optional[str]:
    if isinstance(value, str):
        candidate = value.strip()
        if _SAFE_SHA_RE.fullmatch(candidate):
            return candidate
    return None


def _metadata_from(data: dict, *, plugin=None, marketplace=None) -> dict:
    """Extract display-safe provenance metadata without returning filesystem paths."""
    metadata: dict = {}

    safe_plugin = _safe_identifier(plugin)
    if safe_plugin:
        metadata["plugin"] = safe_plugin

    safe_marketplace = _safe_identifier(marketplace)
    if safe_marketplace:
        metadata["marketplace"] = safe_marketplace

    version = _safe_version(data.get("version"))
    if version:
        metadata["version"] = version

    for key in ("source_ref", "ref", "git_ref"):
        ref = _safe_ref(data.get(key))
        if ref:
            metadata["ref"] = ref
            break

    for key in ("source_sha", "sha", "commit", "commit_sha"):
        sha = _safe_sha(data.get(key))
        if sha:
            metadata["sha"] = sha
            break

    source = data.get("source")
    if isinstance(source, dict):
        if "ref" not in metadata:
            metadata_ref = _safe_ref(source.get("ref"))
            if metadata_ref:
                metadata["ref"] = metadata_ref
        if "sha" not in metadata:
            for key in ("sha", "commit", "commit_sha"):
                metadata_sha = _safe_sha(source.get(key))
                if metadata_sha:
                    metadata["sha"] = metadata_sha
                    break

    return metadata


def _result(
    repo: Optional[str],
    source: str,
    confidence: str,
    install_scope: str,
    *,
    metadata: Optional[dict] = None,
    note: Optional[str] = None,
) -> dict:
    result = {
        "repo": repo,
        "source": source,
        "confidence": confidence,
        "install_scope": (
            install_scope if install_scope in _INSTALL_SCOPES else "unknown"
        ),
    }
    for key in _RESULT_METADATA_FIELDS:
        value = (metadata or {}).get(key)
        if value:
            result[key] = value
    if note:
        result["note"] = note
    return result


def _is_relative_to(path: Path, parent: Path) -> bool:
    try:
        path.relative_to(parent)
        return True
    except ValueError:
        return False


def _infer_install_scope(
    skill_md_path: Optional[str],
    install_root: Optional[str],
    config: dict,
    explicit_scope: Optional[str],
) -> str:
    if explicit_scope in _INSTALL_SCOPES:
        return explicit_scope
    if config.get("mode") == "vendored":
        return "vendored"

    candidate = skill_md_path or install_root
    if not candidate:
        return "unknown"

    try:
        path = Path(candidate).expanduser().resolve()
        cwd = Path.cwd().resolve()
        home = Path.home().resolve()
    except OSError:
        return "unknown"

    if _is_relative_to(path, cwd):
        return "project"

    user_roots = (
        home / ".copilot",
        home / ".claude",
        home / ".agents",
        home / ".config" / "opencode",
    )
    if any(_is_relative_to(path, root) for root in user_roots):
        return "user"

    return "unknown"


# ---------------------------------------------------------------------------
# Source-value interpreter (shared by flat-manifest + marketplace readers)
# ---------------------------------------------------------------------------

def _interpret_source(value) -> tuple[Optional[str], str]:
    """
    Interpret a plugin ``source`` / ``repository`` value.

    Returns ``(owner/repo | None, kind)`` where *kind* is one of:
      "repo"      -> a concrete ``owner/repo`` was extracted
      "relative"  -> a repo-relative path (e.g. ``"./plugins/x"``).  In a Claude Code
                     ``marketplace.json`` a relative ``source`` means the plugin lives
                     *inside the marketplace repo itself*, so provenance is that
                     marketplace repo — which must be resolved separately (caller
                     supplies ``marketplace_repo`` or we derive it from git origin).
      "none"      -> nothing usable
    """
    # Object forms: {"source":"github","repo":"owner/repo"} | {"type":"git","url":...}
    if isinstance(value, dict):
        for key in ("repo", "url", "source", "homepage"):
            v = value.get(key)
            if isinstance(v, str):
                r = _extract_repo(v)
                if r:
                    return r, "repo"
        return None, "none"
    if not isinstance(value, str):
        return None, "none"
    v = value.strip()
    if not v:
        return None, "none"
    # Repo-relative path -> provenance is the marketplace repo itself
    if v.startswith("./") or v.startswith("../") or v.startswith("/"):
        return None, "relative"
    # Concrete owner/repo shorthand or GitHub URL
    r = _extract_repo(v)
    if r:
        return r, "repo"
    return None, "none"


def _git_origin_repo(start: Path) -> Optional[str]:
    """
    Best-effort ``owner/repo`` from ``git -C <dir> remote.origin.url`` of the tree
    containing *start*.  Used only when explicitly allowed (``allow_git=True``) to
    resolve a Claude Code marketplace's own repo for a relative ``source``.
    """
    import subprocess  # local import; only used on the opt-in git path

    try:
        out = subprocess.run(
            ["git", "-C", str(start), "config", "--get", "remote.origin.url"],
            capture_output=True, text=True, timeout=5,
        )
        if out.returncode == 0:
            return _extract_repo(out.stdout.strip())
    except (OSError, subprocess.SubprocessError):
        pass
    return None


# ---------------------------------------------------------------------------
# Manifest readers
#   - flat manifest  : plugin.json / package.json-style single object
#   - marketplace    : Claude Code .claude-plugin/marketplace.json {"plugins":[…]}
# ---------------------------------------------------------------------------

def _repo_from_manifest_data(data: dict) -> tuple[Optional[str], str, dict]:
    """
    Scan a parsed *flat* manifest dict for a GitHub repo reference.

    Returns (owner/repo | None, confidence, safe metadata).

    Priority / confidence:
      source_repo  → "Confirmed"  (written by gh-skill-cli installer)
      repository   → "Likely"     (set by plugin author; npm shorthand or git URL)
      source       → "Likely"
      homepage     → "Likely"
      url          → "Likely"

    NOTE: Copilot CLI extensions have **no runtime-consumed manifest** — the CLI
    auto-discovers ``extension.mjs`` only.  Any ``extension.json`` present is
    metadata-only, so Copilot-CLI skill provenance normally comes from SKILL.md
    frontmatter (step 1) or the registry (step 4), not from a manifest.
    """
    metadata = _metadata_from(data, plugin=data.get("name"))

    # source_repo: written by installer → Confirmed
    if "source_repo" in data:
        r = _extract_repo(str(data["source_repo"]))
        if r:
            return r, "Confirmed", metadata

    # repository: npm-style (string or {"type":"git","url":"..."})
    repo_field = data.get("repository")
    if isinstance(repo_field, dict):
        r = _extract_repo(str(repo_field.get("url", "")))
        if r:
            return r, "Likely", metadata
    elif isinstance(repo_field, str):
        r = _extract_repo(repo_field)
        if r:
            return r, "Likely", metadata

    # Other fallback URL fields
    for key in ("source", "homepage", "url"):
        val = data.get(key)
        if isinstance(val, str):
            r = _extract_repo(val)
            if r:
                return r, "Likely", metadata

    return None, "None", metadata


def _skill_basename(value) -> Optional[str]:
    """Return the skill directory basename from a marketplace ``skills[]`` entry."""
    if not isinstance(value, str):
        return None
    normalized = value.strip().replace("\\", "/").rstrip("/")
    if not normalized:
        return None
    parts = [part for part in normalized.split("/") if part not in ("", ".")]
    if not parts:
        return None
    if parts[-1].lower() == "skill.md":
        if len(parts) < 2:
            return None
        return parts[-2]
    return parts[-1]


def _marketplace_entry(
    plugins: list, skill_name: str
) -> Optional[dict]:
    """Match a plugin by name first, then by the basename of its ``skills[]`` paths."""
    for case_sensitive in (True, False):
        for plugin in plugins:
            if not isinstance(plugin, dict):
                continue
            plugin_name = str(plugin.get("name", ""))
            if (
                plugin_name == skill_name
                if case_sensitive
                else plugin_name.lower() == skill_name.lower()
            ):
                return plugin

    for case_sensitive in (True, False):
        for plugin in plugins:
            if not isinstance(plugin, dict):
                continue
            skills = plugin.get("skills")
            if not isinstance(skills, list):
                continue
            for value in skills:
                basename = _skill_basename(value)
                if basename and (
                    basename == skill_name
                    if case_sensitive
                    else basename.lower() == skill_name.lower()
                ):
                    return plugin
    return None


def _repo_from_marketplace_data(
    data: dict, skill_name: str, marketplace_repo: Optional[str]
) -> tuple[Optional[str], str, str, dict]:
    """
    Handle a Claude Code ``.claude-plugin/marketplace.json`` shape::

        { "plugins": [ {"name": "...", "source": <str|obj>, ...}, ... ] }

    Match the plugin whose ``name`` equals *skill_name* or whose ``skills[]`` contains a
    path with a basename equal to *skill_name*.

    Returns ``(owner/repo | None, confidence, source_label, metadata)`` where *source_label*
    may be ``"manifest"``, ``"marketplace"`` (relative source resolved to the
    marketplace repo), or ``"marketplace-relative"`` (relative source, repo not yet
    resolvable from the JSON alone — caller must derive git origin or ask).
    """
    plugins = data.get("plugins")
    if not isinstance(plugins, list):
        return None, "None", "manifest", {}

    entry = _marketplace_entry(plugins, skill_name)
    if entry is None:
        return None, "None", "manifest", {}

    metadata = _metadata_from(
        entry,
        plugin=entry.get("name"),
        marketplace=data.get("name"),
    )

    # Explicit repository/homepage on the entry beats a bare source
    for key in ("repository", "homepage"):
        r, kind = _interpret_source(entry.get(key))
        if kind == "repo":
            return r, "Likely", "manifest", metadata

    r, kind = _interpret_source(entry.get("source"))
    if kind == "repo":
        return r, "Likely", "manifest", metadata
    if kind == "relative":
        if marketplace_repo:
            mr = _extract_repo(marketplace_repo)
            if mr:
                return mr, "Likely", "marketplace", metadata
        for container in (data, data.get("metadata")):
            if not isinstance(container, dict):
                continue
            for key in ("repository", "homepage"):
                mr, marketplace_kind = _interpret_source(container.get(key))
                if marketplace_kind == "repo":
                    return mr, "Likely", "marketplace", metadata
        return None, "Possible", "marketplace-relative", metadata
    return None, "None", "manifest", metadata


def _read_manifest(
    path: str | Path,
    skill_name: str = "",
    marketplace_repo: Optional[str] = None,
    allow_git: bool = False,
) -> tuple[Optional[str], str, str, dict]:
    """
    Load a JSON manifest and return
    ``(owner/repo | None, confidence, source_label, safe metadata)``.

    Detects the Claude Code marketplace shape (``{"plugins":[…]}``) and routes to the
    marketplace reader; otherwise treats the file as a flat manifest.  For a relative
    marketplace ``source`` with no ``marketplace_repo`` supplied, optionally derives
    the marketplace repo from the manifest directory's git origin when *allow_git*.
    """
    try:
        data = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError, UnicodeDecodeError):
        return None, "None", "manifest", {}

    if not isinstance(data, dict):
        return None, "None", "manifest", {}

    if isinstance(data.get("plugins"), list):
        repo, conf, label, metadata = _repo_from_marketplace_data(
            data, skill_name, marketplace_repo
        )
        if repo:
            return repo, conf, label, metadata
        if label == "marketplace-relative":
            if allow_git:
                derived = _git_origin_repo(Path(path).parent)
                if derived:
                    return derived, "Likely", "marketplace", metadata
            return None, "Possible", "marketplace-relative", metadata
        # Never attribute a marketplace's top-level repository to an unmatched skill.
        return None, conf, label, metadata

    repo, conf, metadata = _repo_from_manifest_data(data)
    return repo, conf, "manifest", metadata


# ---------------------------------------------------------------------------
# Registry reader
# ---------------------------------------------------------------------------

def _read_registry(path: str | Path, skill_name: str) -> tuple[Optional[str], dict]:
    """
    Look up *skill_name* in a registry.json file.

    Value forms accepted:
      "owner/repo"                        (string)
      {"repo": "owner/repo", "ref": "…"} (object)
    Returns ``(owner/repo | None, safe metadata)``.
    """
    try:
        data = json.loads(Path(path).read_text(encoding="utf-8"))
        if not isinstance(data, dict):
            return None, {}
        entry = data.get(skill_name)
        if entry is None:
            return None, {}
        if isinstance(entry, str) and _OWNER_REPO_RE.match(entry.strip()):
            return entry.strip(), {}
        if isinstance(entry, dict):
            repo = entry.get("repo", "")
            if isinstance(repo, str) and _OWNER_REPO_RE.match(repo.strip()):
                return repo.strip(), _metadata_from(entry)
    except (OSError, json.JSONDecodeError, UnicodeDecodeError):
        pass
    return None, {}


# ---------------------------------------------------------------------------
# Bounded local manifest discovery
# ---------------------------------------------------------------------------

_KNOWN_MANIFEST_PATHS = (
    Path(".claude-plugin/plugin.json"),
    Path("plugin.json"),
    Path(".claude-plugin/marketplace.json"),
    Path("marketplace.json"),
)
_MAX_MANIFEST_ANCESTORS = 8


def _discover_manifests(
    skill_md_path: Optional[str],
    install_root: Optional[str],
) -> list[str]:
    """
    Discover known plugin manifests on the supplied installation ancestor chain.

    The search is local-only, bounded to eight ancestors, and restricted to fixed known
    filenames. If *install_root* is supplied it must contain the skill path and becomes
    the upper boundary. Returned paths are internal inputs only and never enter results.
    """
    candidate = skill_md_path or install_root
    if not candidate:
        return []

    try:
        start_path = Path(candidate).expanduser().resolve()
        start = start_path.parent if skill_md_path else start_path
        boundary = Path(install_root).expanduser().resolve() if install_root else None
    except OSError:
        return []

    if boundary and not _is_relative_to(start, boundary):
        return []

    manifests: list[str] = []
    seen: set[Path] = set()
    current = start
    for _ in range(_MAX_MANIFEST_ANCESTORS):
        for relative_path in _KNOWN_MANIFEST_PATHS:
            manifest = current / relative_path
            try:
                resolved = manifest.resolve()
                is_file = resolved.is_file()
            except OSError:
                continue
            if (
                is_file
                and _is_relative_to(resolved, current)
                and resolved not in seen
            ):
                manifests.append(str(resolved))
                seen.add(resolved)

        if (boundary and current == boundary) or current.parent == current:
            break
        current = current.parent

    return manifests


# ---------------------------------------------------------------------------
# Default path helper
# ---------------------------------------------------------------------------

def _default_registry_path() -> Path:
    home = os.environ.get("SKILL_REFLECT_HOME", os.path.expanduser("~/.skill-reflect"))
    return Path(home) / "registry.json"


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def resolve_provenance(
    skill_name: str,
    skill_md_path: Optional[str] = None,
    manifest_paths: Optional[list[str]] = None,
    registry_path: Optional[str] = None,
    config: Optional[dict] = None,
    marketplace_repo: Optional[str] = None,
    allow_git: bool = False,
    install_root: Optional[str] = None,
    install_scope: Optional[str] = None,
) -> dict:
    """
    Resolve the source GitHub repo for *skill_name*.

    Resolution order (stops at first confident hit):
      1. source_repo in SKILL.md frontmatter          → Confirmed
      2. Plugin/marketplace manifest repo field        → Confirmed | Likely
      3. Vendored config (destination.repo)            → Confirmed
      4. Local registry map                            → Likely
      5. Unknown                                       → None

    Parameters
    ----------
    skill_name      : canonical skill name (exact match for registry/marketplace lookup)
    skill_md_path   : path to the skill's SKILL.md file
    manifest_paths  : list of paths to JSON manifests (plugin.json, marketplace.json, …)
    registry_path   : path to registry.json; falls back to $SKILL_REFLECT_HOME/registry.json
    config          : parsed skill-reflect.config.json dict
    marketplace_repo: owner/repo of the Claude Code marketplace, used to resolve a
                      plugin whose ``source`` is a repo-relative path
    allow_git       : when True, permit deriving ``marketplace_repo`` from the manifest
                      directory's git origin for a relative ``source`` (runs ``git``)
    install_root    : optional upper boundary for bounded known-manifest discovery
    install_scope   : optional trusted scope: project | user | vendored | unknown

    Returns
    -------
    {
        "repo":       "owner/repo" | None,
        "source":     "frontmatter" | "manifest" | "marketplace" | "vendored"
                       | "registry" | "marketplace-relative" | "unknown",
        "confidence": "Confirmed" | "Likely" | "Possible" | "None",
        "install_scope": "project" | "user" | "vendored" | "unknown",
        "plugin":     (optional) display-safe plugin identity,
        "marketplace": (optional) display-safe marketplace identity,
        "version":    (optional) display-safe version,
        "ref":        (optional) display-safe source ref,
        "sha":        (optional) validated hexadecimal source SHA,
        "note":       (optional) present for "marketplace-relative" to explain the
                       follow-up needed
    }

    Note: a ``source`` of ``"marketplace-relative"`` (Possible) does NOT clear the
    never-guess bar — the caller must resolve the marketplace repo (git origin) or
    ask the user before any send.
    """
    config = config or {}
    dest_cfg: dict = config.get("destination") or {}
    resolved_scope = _infer_install_scope(
        skill_md_path, install_root, config, install_scope
    )

    # ------------------------------------------------------------------
    # Step 1: SKILL.md frontmatter
    # ------------------------------------------------------------------
    if skill_md_path:
        fm = _read_skill_md(skill_md_path)
        repo = _extract_repo(fm.get("source_repo", ""))
        if repo:
            return _result(
                repo,
                "frontmatter",
                "Confirmed",
                resolved_scope,
                metadata=_metadata_from(
                    {
                        "version": fm.get("version"),
                        "source_ref": fm.get("source_ref"),
                        "source_sha": fm.get("source_sha"),
                    }
                ),
            )

    # ------------------------------------------------------------------
    # Step 2: Plugin / marketplace manifest
    # ------------------------------------------------------------------
    relative_hint = False
    relative_metadata: dict = {}
    all_manifests: list[str] = []
    seen_manifests: set[Path] = set()
    for mpath in [
        *(manifest_paths or []),
        *_discover_manifests(skill_md_path, install_root),
    ]:
        try:
            manifest_key = Path(mpath).expanduser().resolve()
        except OSError:
            continue
        if manifest_key in seen_manifests:
            continue
        seen_manifests.add(manifest_key)
        all_manifests.append(str(manifest_key))

    for mpath in all_manifests:
        repo, confidence, label, metadata = _read_manifest(
            mpath, skill_name, marketplace_repo, allow_git
        )
        if repo:
            return _result(
                repo,
                label,
                confidence,
                resolved_scope,
                metadata=metadata,
            )
        if label == "marketplace-relative":
            relative_hint = True
            relative_metadata = metadata

    # ------------------------------------------------------------------
    # Step 3: Vendored config
    # ------------------------------------------------------------------
    if config.get("mode") == "vendored":
        repo = dest_cfg.get("repo")
        if isinstance(repo, str) and _OWNER_REPO_RE.match(repo.strip()):
            return _result(
                repo.strip(),
                "vendored",
                "Confirmed",
                "vendored",
            )

    # ------------------------------------------------------------------
    # Step 4: Registry map
    # ------------------------------------------------------------------
    reg = (
        registry_path
        or dest_cfg.get("registryMapPath")
        or str(_default_registry_path())
    )
    if reg:
        repo, metadata = _read_registry(reg, skill_name)
        if repo:
            return _result(
                repo,
                "registry",
                "Likely",
                resolved_scope,
                metadata=metadata,
            )

    # ------------------------------------------------------------------
    # Step 5: Unknown (surface a marketplace-relative hint if we saw one)
    # ------------------------------------------------------------------
    if relative_hint:
        return _result(
            None,
            "marketplace-relative",
            "Possible",
            resolved_scope,
            metadata=relative_metadata,
            note=(
                "Plugin found in a Claude Code marketplace.json with a repo-relative "
                "'source'; provenance is the marketplace repo itself. Resolve the "
                "marketplace repo (git origin) or ask the user before sending."
            ),
        )
    return _result(None, "unknown", "None", resolved_scope)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def _cli() -> None:
    parser = argparse.ArgumentParser(
        prog="resolve_provenance",
        description=(
            "Resolve the source GitHub repo for a named skill.\n"
            "Prints the result as JSON to stdout."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--skill", required=True, metavar="NAME",
                        help="Skill name to resolve")
    parser.add_argument("--skill-md", metavar="PATH",
                        help="Path to the skill's SKILL.md file")
    parser.add_argument("--manifest", action="append", dest="manifests",
                        metavar="PATH",
                        help="Path to a plugin/extension manifest JSON (repeatable)")
    parser.add_argument("--registry", metavar="PATH",
                        help="Path to registry.json")
    parser.add_argument("--config", metavar="PATH",
                        help="Path to skill-reflect.config.json")
    parser.add_argument("--marketplace-repo", metavar="OWNER/REPO",
                        help="owner/repo of the Claude Code marketplace, used to "
                             "resolve a plugin whose marketplace.json 'source' is a "
                             "repo-relative path")
    parser.add_argument("--allow-git", action="store_true",
                        help="Permit deriving the marketplace repo from the manifest "
                             "directory's git origin for a relative 'source' (runs git)")
    parser.add_argument("--install-root", metavar="PATH",
                        help="Upper boundary for bounded local manifest discovery")
    parser.add_argument(
        "--install-scope",
        choices=("project", "user", "vendored", "unknown"),
        help="Trusted installation scope to report without exposing its path",
    )
    args = parser.parse_args()

    config: dict = {}
    if args.config:
        try:
            config = json.loads(Path(args.config).read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            print(f"Warning: could not load config ({exc})", file=sys.stderr)

    result = resolve_provenance(
        skill_name=args.skill,
        skill_md_path=args.skill_md,
        manifest_paths=args.manifests,
        registry_path=args.registry,
        config=config,
        marketplace_repo=args.marketplace_repo,
        allow_git=args.allow_git,
        install_root=args.install_root,
        install_scope=args.install_scope,
    )
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    _cli()
