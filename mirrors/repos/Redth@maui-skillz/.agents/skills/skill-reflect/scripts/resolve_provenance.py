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
    # -> {"repo": "owner/repo", "source": "frontmatter", "confidence": "Confirmed"}

CLI
---
    python3 resolve_provenance.py --skill <name> \\
        [--skill-md <path>] [--manifest <path> ...] \\
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

def _repo_from_manifest_data(data: dict) -> tuple[Optional[str], str]:
    """
    Scan a parsed *flat* manifest dict for a GitHub repo reference.

    Returns (owner/repo | None, confidence).

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
    # source_repo: written by installer → Confirmed
    if "source_repo" in data:
        r = _extract_repo(str(data["source_repo"]))
        if r:
            return r, "Confirmed"

    # repository: npm-style (string or {"type":"git","url":"..."})
    repo_field = data.get("repository")
    if isinstance(repo_field, dict):
        r = _extract_repo(str(repo_field.get("url", "")))
        if r:
            return r, "Likely"
    elif isinstance(repo_field, str):
        r = _extract_repo(repo_field)
        if r:
            return r, "Likely"

    # Other fallback URL fields
    for key in ("source", "homepage", "url"):
        val = data.get(key)
        if isinstance(val, str):
            r = _extract_repo(val)
            if r:
                return r, "Likely"

    return None, "None"


def _repo_from_marketplace_data(
    data: dict, skill_name: str, marketplace_repo: Optional[str]
) -> tuple[Optional[str], str, str]:
    """
    Handle a Claude Code ``.claude-plugin/marketplace.json`` shape::

        { "plugins": [ {"name": "...", "source": <str|obj>, ...}, ... ] }

    Match the plugin whose ``name`` equals *skill_name* (skills are distributed
    inside plugins; the plugin name is the closest provenance key in this file).

    Returns ``(owner/repo | None, confidence, source_label)`` where *source_label*
    may be ``"manifest"``, ``"marketplace"`` (relative source resolved to the
    marketplace repo), or ``"marketplace-relative"`` (relative source, repo not yet
    resolvable from the JSON alone — caller must derive git origin or ask).
    """
    plugins = data.get("plugins")
    if not isinstance(plugins, list):
        return None, "None", "manifest"

    entry = None
    for p in plugins:  # exact name match first
        if isinstance(p, dict) and p.get("name") == skill_name:
            entry = p
            break
    if entry is None:  # then case-insensitive
        for p in plugins:
            if isinstance(p, dict) and str(p.get("name", "")).lower() == skill_name.lower():
                entry = p
                break
    if entry is None:
        return None, "None", "manifest"

    # Explicit repository/homepage on the entry beats a bare source
    for key in ("repository", "homepage"):
        r, kind = _interpret_source(entry.get(key))
        if kind == "repo":
            return r, "Likely", "manifest"

    r, kind = _interpret_source(entry.get("source"))
    if kind == "repo":
        return r, "Likely", "manifest"
    if kind == "relative":
        if marketplace_repo:
            mr = _extract_repo(marketplace_repo)
            if mr:
                return mr, "Likely", "marketplace"
        return None, "Possible", "marketplace-relative"
    return None, "None", "manifest"


def _read_manifest(
    path: str | Path,
    skill_name: str = "",
    marketplace_repo: Optional[str] = None,
    allow_git: bool = False,
) -> tuple[Optional[str], str, str]:
    """
    Load a JSON manifest and return ``(owner/repo | None, confidence, source_label)``.

    Detects the Claude Code marketplace shape (``{"plugins":[…]}``) and routes to the
    marketplace reader; otherwise treats the file as a flat manifest.  For a relative
    marketplace ``source`` with no ``marketplace_repo`` supplied, optionally derives
    the marketplace repo from the manifest directory's git origin when *allow_git*.
    """
    try:
        data = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError, UnicodeDecodeError):
        return None, "None", "manifest"

    if not isinstance(data, dict):
        return None, "None", "manifest"

    if isinstance(data.get("plugins"), list):
        repo, conf, label = _repo_from_marketplace_data(data, skill_name, marketplace_repo)
        if repo:
            return repo, conf, label
        if label == "marketplace-relative":
            if allow_git:
                derived = _git_origin_repo(Path(path).parent)
                if derived:
                    return derived, "Likely", "marketplace"
            return None, "Possible", "marketplace-relative"
        # marketplace file present but plugin not matched → fall through to flat scan

    repo, conf = _repo_from_manifest_data(data)
    return repo, conf, "manifest"


# ---------------------------------------------------------------------------
# Registry reader
# ---------------------------------------------------------------------------

def _read_registry(path: str | Path, skill_name: str) -> Optional[str]:
    """
    Look up *skill_name* in a registry.json file.

    Value forms accepted:
      "owner/repo"                        (string)
      {"repo": "owner/repo", "ref": "…"} (object)
    Returns owner/repo string or None.
    """
    try:
        data = json.loads(Path(path).read_text(encoding="utf-8"))
        if not isinstance(data, dict):
            return None
        entry = data.get(skill_name)
        if entry is None:
            return None
        if isinstance(entry, str) and _OWNER_REPO_RE.match(entry.strip()):
            return entry.strip()
        if isinstance(entry, dict):
            repo = entry.get("repo", "")
            if isinstance(repo, str) and _OWNER_REPO_RE.match(repo.strip()):
                return repo.strip()
    except (OSError, json.JSONDecodeError, UnicodeDecodeError):
        pass
    return None


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

    Returns
    -------
    {
        "repo":       "owner/repo" | None,
        "source":     "frontmatter" | "manifest" | "marketplace" | "vendored"
                       | "registry" | "marketplace-relative" | "unknown",
        "confidence": "Confirmed" | "Likely" | "Possible" | "None",
        "note":       (optional) present for "marketplace-relative" to explain the
                       follow-up needed
    }

    Note: a ``source`` of ``"marketplace-relative"`` (Possible) does NOT clear the
    never-guess bar — the caller must resolve the marketplace repo (git origin) or
    ask the user before any send.
    """
    config = config or {}
    dest_cfg: dict = config.get("destination") or {}

    # ------------------------------------------------------------------
    # Step 1: SKILL.md frontmatter
    # ------------------------------------------------------------------
    if skill_md_path:
        fm = _read_skill_md(skill_md_path)
        repo = fm.get("source_repo", "").strip()
        if repo:
            return {"repo": repo, "source": "frontmatter", "confidence": "Confirmed"}

    # ------------------------------------------------------------------
    # Step 2: Plugin / marketplace manifest
    # ------------------------------------------------------------------
    relative_hint = False
    for mpath in (manifest_paths or []):
        repo, confidence, label = _read_manifest(
            mpath, skill_name, marketplace_repo, allow_git
        )
        if repo:
            return {"repo": repo, "source": label, "confidence": confidence}
        if label == "marketplace-relative":
            relative_hint = True

    # ------------------------------------------------------------------
    # Step 3: Vendored config
    # ------------------------------------------------------------------
    if config.get("mode") == "vendored":
        repo = dest_cfg.get("repo")
        if isinstance(repo, str) and _OWNER_REPO_RE.match(repo.strip()):
            return {"repo": repo.strip(), "source": "vendored", "confidence": "Confirmed"}

    # ------------------------------------------------------------------
    # Step 4: Registry map
    # ------------------------------------------------------------------
    reg = (
        registry_path
        or dest_cfg.get("registryMapPath")
        or str(_default_registry_path())
    )
    if reg:
        repo = _read_registry(reg, skill_name)
        if repo:
            return {"repo": repo, "source": "registry", "confidence": "Likely"}

    # ------------------------------------------------------------------
    # Step 5: Unknown (surface a marketplace-relative hint if we saw one)
    # ------------------------------------------------------------------
    if relative_hint:
        return {
            "repo": None,
            "source": "marketplace-relative",
            "confidence": "Possible",
            "note": (
                "Plugin found in a Claude Code marketplace.json with a repo-relative "
                "'source'; provenance is the marketplace repo itself. Resolve the "
                "marketplace repo (git origin) or ask the user before sending."
            ),
        }
    return {"repo": None, "source": "unknown", "confidence": "None"}


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
    )
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    _cli()
