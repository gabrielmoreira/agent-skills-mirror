#!/usr/bin/env python3
"""Deterministic scratch-def validate / enrich / map helpers.

Optional draft-07 check against references/project-scratch-def.schema.json
when jsonschema is installed. Feature tokens come from the PUBLIC catalog
(live or project cache; shipped snapshot JSON last). Missing jsonschema is
not a hard fail: warn, ask the user to install, continue if install fails.

map/validate/preview/apply load the PUBLIC catalog into in-memory maps. A
calendar-day cache lives at ``{sfdx_root}/cache/public-config-values-YYYY-MM-DD.json``
(sibling of ``config/``) — never the skill package and never under ``config/``.
The shipped references/ snapshot is last-resort only when live fetch fails and
no prior project cache is usable.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from copy import deepcopy
from datetime import date, timedelta
from difflib import get_close_matches
from pathlib import Path
from typing import Any

# Keep bytecode out of the skill package so a later factory sync cannot
# promote local __pycache__ into unified-sors reference_artifacts.
sys.dont_write_bytecode = True

try:
    from jsonschema import Draft7Validator
except ImportError:  # pragma: no cover — preview/apply still run; agent asks to install
    Draft7Validator = None  # type: ignore[misc, assignment]

JSONSCHEMA_MISSING_WARNING = (
    "jsonschema not installed; ask the user to install it with: "
    "python3 -m pip install jsonschema (or python -m pip install jsonschema). "
    "If install fails, continue without the draft-07 schema check — "
    "preview/apply still run."
)

SCRIPT_DIR = Path(__file__).resolve().parent
SKILL_DIR = SCRIPT_DIR.parent
REF_DIR = SKILL_DIR / "references"
SCHEMA_PATH = REF_DIR / "project-scratch-def.schema.json"
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

EDITIONS = {
    "Developer",
    "Enterprise",
    "Group",
    "Partner Developer",
    "Partner Enterprise",
    "Partner Group",
    "Partner Professional",
    "Professional",
}

# Restricted My Domain tokens — whole tokens only, not substrings
# (so "Enforcement Demo" / "SalesforceDemo" are left intact).
RESTRICTED_ORGNAME = {
    "salesforce",
    "force",
    "cloudforce",
    "database",
}
_RESTRICTED_ORGNAME_RE = re.compile(
    r"(?i)(?<![A-Za-z0-9])("
    + "|".join(
        sorted((re.escape(w) for w in RESTRICTED_ORGNAME), key=len, reverse=True)
    )
    + r")(?![A-Za-z0-9])"
)


def load_cache() -> tuple[dict, dict]:
    features = json.loads((REF_DIR / "features.json").read_text(encoding="utf-8"))
    settings = json.loads((REF_DIR / "settings-map.json").read_text(encoding="utf-8"))
    return features, settings


# Project-local calendar-day cache under {sfdx_root}/cache/ (next to config/).
# Tests may set DX_SCRATCH_DEF_CATALOG_CACHE_DIR to an isolated directory.
CATALOG_CACHE_DIR_ENV = "DX_SCRATCH_DEF_CATALOG_CACHE_DIR"
CATALOG_CACHE_BASENAME = "public-config-values"
CATALOG_CACHE_FILE_RE = re.compile(
    rf"^{re.escape(CATALOG_CACHE_BASENAME)}-(\d{{4}}-\d{{2}}-\d{{2}})\.json$"
)
CATALOG_CACHE_KEEP_DAYS = 2
CATALOG_GENERATED_BY = "dx-scratch-def-configure"


def catalog_cache_dir() -> Path | None:
    """Return the project cache dir, or None when cwd is not an SF DX root.

    Default: ``{cwd}/cache`` when ``{cwd}/config`` exists. Env override is for
    tests / advanced isolation only. Does not create the directory.
    """
    override = os.environ.get(CATALOG_CACHE_DIR_ENV, "").strip()
    if override:
        return Path(override)
    if not (Path.cwd() / "config").is_dir():
        return None
    return Path.cwd() / "cache"


def _no_project_cache_warning() -> str:
    return "no project cache (cwd has no config/); catalog will not be persisted"


def _ensure_cache_dir() -> tuple[Path | None, list[str]]:
    """Create/reuse ``cache/`` for a write. Not used on the read/hit path."""
    warnings: list[str] = []
    cache_dir = catalog_cache_dir()
    if cache_dir is None:
        warnings.append(_no_project_cache_warning())
        return None, warnings
    try:
        cache_dir.mkdir(parents=True, exist_ok=True)
        return cache_dir.resolve(), []
    except OSError as e:
        warnings.append(f"could not create cache/ ({e}); catalog will not be persisted")
        return None, warnings


def _iter_dated_cache_files(cache_dir: Path) -> list[tuple[date, Path]]:
    """Dated catalog files in ``cache_dir`` (missing dir → empty, no mkdir)."""
    found: list[tuple[date, Path]] = []
    try:
        entries = list(cache_dir.iterdir())
    except OSError:
        return found
    for p in entries:
        m = CATALOG_CACHE_FILE_RE.match(p.name)
        if not m or not p.is_file():
            continue
        try:
            found.append((date.fromisoformat(m.group(1)), p))
        except ValueError:
            continue
    return found


def _today_cache_filename(day: date | None = None) -> str:
    d = day or date.today()
    return f"{CATALOG_CACHE_BASENAME}-{d.isoformat()}.json"


def _cache_day_from_notes(notes: list[str]) -> str | None:
    """Filename date in a hit note (cache/public-config-values-YYYY-MM-DD.json)."""
    blob = " ".join(notes)
    m = re.search(
        rf"{re.escape(CATALOG_CACHE_BASENAME)}-(\d{{4}}-\d{{2}}-\d{{2}})\.json",
        blob,
    )
    return m.group(1) if m else None


def _cached_catalog_usable(features_doc: dict, settings_doc: dict) -> bool:
    """Same guards as the live fetch path — bad/thin cache is a miss."""
    from scrape_config_values import live_parse_too_thin, sanity_check

    feats = features_doc.get("features")
    by_feature = settings_doc.get("byFeature")
    if not isinstance(feats, dict) or not isinstance(by_feature, dict):
        return False
    if sanity_check(feats, by_feature):
        return False
    if live_parse_too_thin(len(feats), None):
        return False
    return True


def _load_cache_file(
    path: Path,
) -> tuple[dict, dict, list[str]] | None:
    """Parse one dated cache file; None if missing/unusable (caller may warn)."""
    if not path.is_file():
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, PermissionError, json.JSONDecodeError, TypeError, ValueError):
        return None
    if not isinstance(data, dict):
        return None
    features = data.get("features")
    settings = data.get("settings")
    if not isinstance(features, dict) or not isinstance(settings, dict):
        return None
    if not _cached_catalog_usable(features, settings):
        return None
    day_label = path.name
    m = CATALOG_CACHE_FILE_RE.match(path.name)
    if m:
        day_label = m.group(1)
    note = (
        f"using project cache file cache/{path.name} "
        f"(generated catalog for {day_label}; do not hand-edit)"
    )
    return features, settings, [note]


def read_today_catalog_cache() -> tuple[dict, dict, list[str]] | tuple[None, None, list[str]]:
    """Return today's dated cache hit, or (None, None, warnings) on miss/error.

    Does not create ``cache/``. Missing today's file is a quiet miss. No
    ``config/`` (and no env override) warns. Unusable JSON warns then misses.
    """
    warnings: list[str] = []
    cache_dir = catalog_cache_dir()
    if cache_dir is None:
        return None, None, [_no_project_cache_warning()]
    path = cache_dir / _today_cache_filename()
    if not path.is_file():
        return None, None, warnings
    loaded = _load_cache_file(path)
    if loaded is None:
        warnings.append(
            f"ignored unusable cache file cache/{path.name}; refetching live catalog"
        )
        return None, None, warnings
    return loaded


def read_newest_prior_catalog_cache() -> tuple[dict, dict, list[str]] | None:
    """Newest dated cache file that is not today and still passes sanity/thin."""
    cache_dir = catalog_cache_dir()
    if cache_dir is None:
        return None
    today = date.today()
    candidates = [(d, p) for d, p in _iter_dated_cache_files(cache_dir) if d != today]
    candidates.sort(key=lambda t: t[0], reverse=True)
    for _day, path in candidates:
        loaded = _load_cache_file(path)
        if loaded is not None:
            return loaded
    return None


def _prune_old_cache_files(cache_dir: Path) -> None:
    """Best-effort delete dated files older than CATALOG_CACHE_KEEP_DAYS."""
    cutoff = date.today() - timedelta(days=CATALOG_CACHE_KEEP_DAYS)
    for file_day, p in _iter_dated_cache_files(cache_dir):
        if file_day < cutoff:
            try:
                p.unlink()
            except OSError:
                pass


def write_catalog_cache(features_doc: dict, settings_doc: dict) -> list[str]:
    """Write today's dated cache file. Returns notes/warnings (never raises).

    Missing ``config/`` is not re-warned here — ``read_today_catalog_cache``
    already reported that miss. mkdir/write failures always warn.
    """
    warnings: list[str] = []
    cache_dir, dir_warns = _ensure_cache_dir()
    if cache_dir is None:
        warnings.extend(w for w in dir_warns if "no project cache" not in w)
        return warnings
    path = cache_dir / _today_cache_filename()
    payload = {
        "generatedBy": CATALOG_GENERATED_BY,
        "fetchedAt": date.today().isoformat(),
        "features": features_doc,
        "settings": settings_doc,
    }
    try:
        path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        _prune_old_cache_files(cache_dir)
        warnings.append(
            f"wrote project cache file cache/{path.name} "
            f"(generated PUBLIC catalog; do not hand-edit; safe to delete)"
        )
    except (OSError, PermissionError, TypeError, ValueError) as e:
        warnings.append(
            f"could not write cache/{path.name} ({e}); catalog still used in memory"
        )
    return warnings


def _docs_from_live_parse(
    live_f: dict[str, dict],
    live_by: dict[str, dict],
    url: str,
    parse_warns: list,
) -> tuple[dict, dict, list[str]]:
    stamp = {
        "fetchedAt": date.today().isoformat(),
        "sourceUrl": url,
        "version": "live-memory",
        "generatedBy": CATALOG_GENERATED_BY,
    }
    notes = [str(w) for w in parse_warns if w]
    notes.append(f"live PUBLIC catalog from {url} ({len(live_f)} features)")
    return (
        {
            **stamp,
            "featureCount": len(live_f),
            "features": dict(sorted(live_f.items(), key=lambda kv: kv[0].lower())),
        },
        {
            **stamp,
            "byFeature": dict(sorted(live_by.items(), key=lambda kv: kv[0].lower())),
        },
        notes,
    )


def _fetch_live_catalog() -> tuple[dict, dict, list[str]]:
    """Fetch + parse PUBLIC catalog into in-memory maps. Never writes. Raises on failure."""
    from scrape_config_values import (
        fetch_live_feed,
        live_parse_too_thin,
        parse_markdown,
        sanity_check,
    )

    text, url = fetch_live_feed()
    live_f, live_by, parse_warns = parse_markdown(text)
    err = sanity_check(live_f, live_by)
    if err:
        raise RuntimeError(f"live parse sanity_check failed: {err}")
    # Absolute thin guard only — a thin/broken parse is a fetch failure, not a merge.
    if live_parse_too_thin(len(live_f), None):
        raise RuntimeError(f"live parse too thin ({len(live_f)} features)")
    return _docs_from_live_parse(live_f, live_by, url, parse_warns)


def load_runtime_catalog() -> tuple[dict, dict, list[str]]:
    """Live PUBLIC maps (project calendar-day cache). Snapshot last-resort.

    Never writes the skill directory or the user's config/. Never merges live
    onto the snapshot. Cache I/O warns on failure (not silent).
    On network/sanity/thin failure: newest prior project cache, else snapshot.
    """
    warnings: list[str] = []
    today_hit = read_today_catalog_cache()
    if today_hit[0] is not None:
        features, settings, notes = today_hit  # type: ignore[misc]
        return features, settings, notes
    warnings.extend(today_hit[2])

    try:
        features_doc, settings_doc, notes = _fetch_live_catalog()
    except Exception as e:  # noqa: BLE001 — fail open to prior cache / snapshot
        prior = read_newest_prior_catalog_cache()
        if prior is not None:
            features, settings, prior_notes = prior
            catalog_day = _cache_day_from_notes(prior_notes) or features.get(
                "fetchedAt"
            ) or "a previous day"
            warnings.append(
                f"live PUBLIC catalog fetch failed ({e}); "
                f"reusing prior project cache from {catalog_day} (tokens may lag)"
            )
            warnings.extend(prior_notes)
            return features, settings, warnings
        warnings.append(
            f"live PUBLIC catalog fetch failed; using shipped snapshot ({e})"
        )
        snap_f, snap_s = load_cache()
        return snap_f, snap_s, warnings

    warnings.extend(notes)
    warnings.extend(write_catalog_cache(features_doc, settings_doc))
    return features_doc, settings_doc, warnings


def load_schema() -> dict:
    if not SCHEMA_PATH.is_file():
        raise FileNotFoundError(f"Missing schema: {SCHEMA_PATH}")
    return json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))


def _schema_for_validate(schema: dict) -> dict:
    """Copy schema for draft-07; do not treat the snapshot feature enum as SoT.

    Feature names/patterns in the forcedotcom snapshot lag the PUBLIC catalog.
    Catalog mapping already dropped unknown tokens; items stay ``string``.
    """
    out = deepcopy(schema)
    for container in (out.get("definitions") or {}, out.get("properties") or {}):
        feats = container.get("features")
        if isinstance(feats, dict):
            feats["items"] = {"type": "string"}
    return out


def validate_against_schema(doc: dict, schema: dict) -> list[str]:
    """Draft-07 check when jsonschema is installed. Empty list if it is not.

    Missing jsonschema is not a hard fail — callers warn and continue.
    """
    if Draft7Validator is None:
        return []
    schema_use = _schema_for_validate(schema)
    # edition is not required when creating from shape (sourceOrg) or snapshot
    if doc.get("sourceOrg") or doc.get("snapshot"):
        req = list(schema_use.get("required") or [])
        schema_use["required"] = [r for r in req if r != "edition"]
    validator = Draft7Validator(schema_use)
    errs: list[str] = []
    for err in sorted(validator.iter_errors(doc), key=lambda e: list(e.absolute_path)):
        path = ".".join(str(p) for p in err.absolute_path) or "(root)"
        errs.append(f"JSON Schema: {path}: {err.message}")
    return errs


DEFAULT_OUT_NAME = "project-scratch-def.json"
# Optional alternate: config/<purpose>-scratch-def.json (not v1/v2, not bare names).
PURPOSE_OUT_RE = re.compile(r"^[a-z0-9][a-z0-9_-]*-scratch-def\.json$")
VERSIONED_OUT_RE = re.compile(r"^v\d+-scratch-def\.json$")


def assert_safe_output_path(dest: Path) -> list[str]:
    """Require relative config/project-scratch-def.json (default) or purpose-named.

    Default path may overwrite on confirm (INT-7.1). Purpose-named alternates
    must be new files (no clobber). The cwd must already be an SF DX project
    with an existing config/ directory — never create config/ here.
    """
    errs: list[str] = []
    dest = Path(dest)
    name = dest.name
    config_dir = Path.cwd() / "config"
    if not config_dir.is_dir():
        errs.append(
            "config/ does not exist under the current working directory. "
            "Ask the user for the Salesforce DX project root that already "
            "contains config/ (where they intend to create scratch orgs). "
            "Do not create config/."
        )
    if dest.expanduser().is_absolute():
        errs.append(
            "output must be a relative path under config/ as "
            "config/project-scratch-def.json (got an absolute path)"
        )
    else:
        resolved = (Path.cwd() / dest).resolve()
        want_parent = config_dir.resolve()
        if resolved.parent != want_parent:
            errs.append(
                "output must be under config/ as config/project-scratch-def.json "
                f"(got parent '{dest.parent.name or dest.parent}')"
            )
    is_default = name == DEFAULT_OUT_NAME
    if not is_default and (
        VERSIONED_OUT_RE.match(name) or not PURPOSE_OUT_RE.match(name)
    ):
        errs.append(
            f"output name '{name}' must be {DEFAULT_OUT_NAME} or purpose-named "
            "<purpose>-scratch-def.json (not v1/v2 or arbitrary filenames)"
        )
    check = dest if dest.expanduser().is_absolute() else Path.cwd() / dest
    try:
        exists = check.resolve().exists() if dest.expanduser().is_absolute() else dest.exists()
    except OSError:
        exists = dest.exists()
    # Default path: overwrite allowed after user confirm. Alternates: no clobber.
    if exists and not is_default:
        errs.append(
            f"refusing to overwrite existing file '{dest}' — no revert. "
            f"Use {DEFAULT_OUT_NAME} (overwrite on confirm) or a new purpose-named path."
        )
    return errs


def suggest_purpose_path(doc: dict) -> str:
    """Default INT-7.1 path: config/project-scratch-def.json.

    doc is accepted for API compatibility with callers that pass the draft.
    """
    _ = doc
    return f"config/{DEFAULT_OUT_NAME}"


def suggest_purpose_named_alternate(doc: dict) -> str:
    """Optional purpose-named alternate under config/ (not the default write path).

    Purpose segment is always lowercased so it matches PURPOSE_OUT_RE
    (shape/snapshot org-id tails often contain uppercase hex).
    """
    parts: list[str] = []
    if doc.get("snapshot"):
        parts.append(f"snapshot-{_slug(str(doc['snapshot']))}")
    elif doc.get("sourceOrg"):
        oid = str(doc["sourceOrg"])
        tail = oid[-6:] if len(oid) >= 6 else oid
        parts.append(f"shape-{_slug(tail)}")
    for feat in (doc.get("features") or [])[:3]:
        parts.append(_slug(str(feat).split(":", 1)[0]))
    if doc.get("edition") and not doc.get("snapshot") and not doc.get("sourceOrg"):
        parts.insert(0, _slug(str(doc["edition"])))
    if not parts:
        parts.append("scratch")
    purpose = "-".join(parts)[:80].strip("-")
    return f"config/{purpose}-scratch-def.json"


def _slug(s: str) -> str:
    s = re.sub(r"[^A-Za-z0-9]+", "-", s).strip("-").lower()
    return s or "x"


def suggest_org_names(base: str | None, n: int = 3) -> list[str]:
    """Suggest n alternative orgName values (no live uniqueness check)."""
    if not base:
        base = "scratch-org"
    cleaned, _ = rewrite_org_name(base)
    cleaned = cleaned or "scratch-org"
    # keep ≤40 including suffix
    stems = []
    for suffix in ("-dev", "-sbx", "-demo"):
        stem = cleaned
        if len(stem) + len(suffix) > 40:
            stem = stem[: 40 - len(suffix)].rstrip("-")
        stems.append(f"{stem}{suffix}")
    return stems[:n]


def _index_features(features_doc: dict) -> dict[str, dict]:
    """Lowercase name → feature entry."""
    out = {}
    for name, entry in features_doc.get("features", {}).items():
        out[name.lower()] = entry
    return out


def _synonym_index(features_doc: dict) -> dict[str, str]:
    """Lowercase synonym / phrase → canonical name."""
    idx: dict[str, str] = {}
    for name, entry in features_doc.get("features", {}).items():
        idx[name.lower()] = name
        for syn in entry.get("synonyms") or []:
            idx[str(syn).lower()] = name
    return idx


def closest_feature(token: str, features_doc: dict, cutoff: float = 0.85) -> str | None:
    names = list(features_doc.get("features", {}).keys())
    matches = get_close_matches(token, names, n=1, cutoff=cutoff)
    if matches:
        return matches[0]
    # also try against lowercased
    lower_map = {n.lower(): n for n in names}
    matches = get_close_matches(token.lower(), list(lower_map.keys()), n=1, cutoff=cutoff)
    return lower_map[matches[0]] if matches else None


def map_feature_token(
    raw: str, features_doc: dict
) -> tuple[str | None, list[str]]:
    """Map a raw feature string to a canonical emit token (Name or Name:N).

    Returns (canonical_or_None, warnings).
    """
    warnings: list[str] = []
    raw = (raw or "").strip()
    if not raw:
        return None, ["empty feature token dropped"]

    quantity: int | None = None
    base = raw
    if ":" in raw:
        base, _, rest = raw.partition(":")
        base = base.strip()
        rest = rest.strip()
        if rest:
            try:
                quantity = int(rest)
            except ValueError:
                warnings.append(f"non-integer quantity on '{raw}' — dropped")
                return None, warnings

    by_name = _index_features(features_doc)
    syn = _synonym_index(features_doc)

    entry = by_name.get(base.lower())
    if entry is None:
        canon = syn.get(base.lower())
        if canon:
            entry = by_name[canon.lower()]
        else:
            from scrape_config_values import longest_phrase_match

            phrase_hit = longest_phrase_match(base, features_doc)
            if phrase_hit:
                entry = by_name[phrase_hit.lower()]
            else:
                near = closest_feature(base, features_doc)
                if near:
                    warnings.append(
                        f"unknown feature '{raw}' — dropped this write (closest: {near}). "
                        "Not in the PUBLIC catalog."
                    )
                else:
                    warnings.append(
                        f"unknown feature '{raw}' — dropped this write. "
                        "Not in the PUBLIC catalog."
                    )
                return None, warnings

    name = entry["name"]
    if entry.get("quantified"):
        qmeta = entry.get("quantity") or {}
        if quantity is None:
            warnings.append(
                f"'{name}' is quantified (Name:N) but no quantity was given — dropped"
            )
            return None, warnings
        qmin = qmeta.get("min")
        qmax = qmeta.get("max")
        if qmin is not None and quantity < qmin:
            warnings.append(f"'{name}:{quantity}' below min {qmin} — dropped")
            return None, warnings
        if qmax is not None and quantity > qmax:
            warnings.append(f"'{name}:{quantity}' above max {qmax} — dropped")
            return None, warnings
        return f"{name}:{quantity}", warnings

    if quantity is not None:
        warnings.append(
            f"'{name}' is not quantified; ignoring quantity {quantity}"
        )
    return name, warnings


def rewrite_org_name(name: str | None) -> tuple[str | None, list[str]]:
    """Rewrite reserved My Domain tokens in orgName; return (value, warnings)."""
    if name is None:
        return None, []
    warnings: list[str] = []
    original = name
    s = name.strip()
    # collapse whitespace → hyphen for my-domain-ish safety when spaces present
    s = re.sub(r"\s+", "-", s)
    s = re.sub(r"-{2,}", "-", s)  # no double hyphens
    s = s.strip("-")  # no trailing/leading hyphen
    if len(s) > 40:
        s = s[:40].rstrip("-")
        warnings.append("orgName truncated to 40 chars")
    # Strip reserved tokens (hyphen/start/end), never substrings of a larger word.
    while True:
        match = _RESTRICTED_ORGNAME_RE.search(s)
        if not match:
            break
        warnings.append(
            f"orgName removed restricted word '{match.group(1).lower()}'"
        )
        s = _RESTRICTED_ORGNAME_RE.sub("", s, count=1)
        s = re.sub(r"-{2,}", "-", s).strip("-")
        s = s or "scratch-org"
    if s != original:
        warnings.append(f"orgName rewrite: '{original}' → '{s}'")
    return s, warnings


def set_by_path(root: dict, path: str, value: Any) -> None:
    path = normalize_settings_path(path)
    parts = path.split(".")
    cur = root
    for p in parts[:-1]:
        if p not in cur or not isinstance(cur[p], dict):
            cur[p] = {}
        cur = cur[p]
    cur[parts[-1]] = value


def lower_camel_settings_key(key: str) -> str:
    """Scratch-def settings categories are lower camelCase (not Metadata UpperCamel)."""
    if not key or not isinstance(key, str):
        return key
    if key[0].isupper():
        return key[0].lower() + key[1:]
    return key


def normalize_settings_path(path: str) -> str:
    if not path or "." not in path:
        return lower_camel_settings_key(path)
    cat, rest = path.split(".", 1)
    return f"{lower_camel_settings_key(cat)}.{rest}"


def normalize_settings_tree(settings: dict | None) -> tuple[dict, list[str]]:
    """Rewrite top-level settings keys to lower camelCase; warn on renames."""
    warnings: list[str] = []
    if not isinstance(settings, dict):
        return {}, warnings
    out: dict = {}
    for k, v in settings.items():
        nk = lower_camel_settings_key(k)
        if nk != k:
            warnings.append(
                f"settings key '{k}' rewritten to '{nk}' "
                "(scratch-def uses lower camelCase, not Metadata API UpperCamel)"
            )
        if nk in out and isinstance(out[nk], dict) and isinstance(v, dict):
            out[nk] = {**out[nk], **v}
        else:
            out[nk] = v
    return out, warnings


def enrich_feature_dependencies(
    kept: list[str], features_doc: dict
) -> tuple[list[str], list[str]]:
    """Auto-add cache `dependsOnFeatures` siblings (PUBLIC docs co-requirements)."""
    warnings: list[str] = []
    by_name = _index_features(features_doc)
    out = list(kept)
    # Fixpoint: newly added siblings may themselves declare dependsOnFeatures.
    changed = True
    while changed:
        changed = False
        present = {f.split(":", 1)[0].lower() for f in out}
        for feat in list(out):
            base = feat.split(":", 1)[0]
            entry = by_name.get(base.lower())
            if not entry:
                continue
            for dep in entry.get("dependsOnFeatures") or []:
                if not isinstance(dep, str) or not dep.strip():
                    continue
                if dep.split(":", 1)[0].lower() in present:
                    continue
                mapped, w = map_feature_token(dep, features_doc)
                warnings.extend(w)
                if mapped and mapped.split(":", 1)[0].lower() not in present:
                    out.append(mapped)
                    present.add(mapped.split(":", 1)[0].lower())
                    warnings.append(
                        f"added sibling feature {mapped} required by {base}"
                    )
                    changed = True
    return out, warnings


def enrich_settings(
    features: list[str], settings: dict | None, settings_map: dict
) -> tuple[dict, list[str]]:
    """Deep-merge required settings for each kept feature."""
    warnings: list[str] = []
    out, nw = normalize_settings_tree(settings if isinstance(settings, dict) else {})
    warnings.extend(nw)
    by_feature = settings_map.get("byFeature") or {}
    for feat in features:
        base = feat.split(":", 1)[0]
        entry = by_feature.get(base)
        if not entry:
            continue
        for req in entry.get("required") or []:
            path = normalize_settings_path(req["path"])
            example = req.get("example", True)
            parts = path.split(".")
            cur = out
            missing = False
            conflict = False
            for p in parts[:-1]:
                if p not in cur or not isinstance(cur.get(p), dict):
                    missing = True
                    break
                cur = cur[p]
            else:
                if parts[-1] not in cur:
                    missing = True
                elif cur[parts[-1]] != example:
                    conflict = True
            if missing:
                set_by_path(out, path, example)
                warnings.append(f"enriched required setting {path} for {base}")
            elif conflict:
                # Required cache value wins — a false/wrong leaf would disable the feature.
                set_by_path(out, path, example)
                warnings.append(
                    f"overrode conflicting setting {path} to required {example!r} for {base}"
                )
    return out, warnings


def validate_object_settings(obj: Any, errors: list[str], warnings: list[str]) -> dict | None:
    """Normalize objectSettings shape; value legality is owned by create."""
    if obj is None:
        return None
    if not isinstance(obj, dict):
        errors.append(
            f"objectSettings must be an object map (got {type(obj).__name__})"
        )
        return None
    if not obj:
        return None
    out: dict = {}
    for raw_key, raw_val in obj.items():
        key = str(raw_key)
        nk = key.lower()
        if nk != key:
            warnings.append(
                f"objectSettings key '{key}' rewritten to '{nk}' "
                "(object names are lowercase in scratch-defs)"
            )
        if not isinstance(raw_val, dict):
            errors.append(
                f"objectSettings.{nk} must be an object with sharingModel "
                "and/or defaultRecordType"
            )
            continue
        entry: dict = {}
        allowed = {"sharingModel", "defaultRecordType"}
        unknown = sorted(set(raw_val) - allowed)
        if unknown:
            warnings.append(
                f"objectSettings.{nk} ignoring unknown keys {unknown} — "
                "create validates sharingModel / defaultRecordType"
            )
        sm = raw_val.get("sharingModel")
        if sm is not None:
            if isinstance(sm, str) and sm.strip():
                entry["sharingModel"] = sm.strip()
            else:
                warnings.append(
                    f"objectSettings.{nk}.sharingModel ignored (non-string/empty); "
                    "create validates allowed values"
                )
        drt = raw_val.get("defaultRecordType")
        if drt is not None:
            if isinstance(drt, str) and drt.strip():
                entry["defaultRecordType"] = drt.strip()
            else:
                warnings.append(
                    f"objectSettings.{nk}.defaultRecordType ignored "
                    "(non-string/empty); create validates allowed values"
                )
        if entry:
            if nk in out:
                out[nk] = {**out[nk], **entry}
            else:
                out[nk] = entry
        elif not unknown:
            warnings.append(
                f"objectSettings.{nk} has no sharingModel/defaultRecordType — omitted"
            )
    return out or None


def coerce_has_sample_data(val: Any) -> tuple[Any, list[str]]:
    if isinstance(val, str) and val.lower() in ("true", "false"):
        return val.lower() == "true", [f'hasSampleData coerced from string "{val}"']
    return val, []


def _strip_org_preferences(
    out: dict, errors: list[str], warnings: list[str]
) -> None:
    if "orgPreferences" in out:
        del out["orgPreferences"]
        warnings.append(
            "dropped top-level orgPreferences; keep settings only "
            "(SignupDuplicateSettingsSpecifiedError)"
        )


def _normalize_base_and_edition(out: dict, errors: list[str], warnings: list[str]) -> None:
    has_source_org = bool(out.get("sourceOrg"))
    has_snapshot = bool(out.get("snapshot"))
    if has_source_org and has_snapshot:
        errors.append(
            "sourceOrg and snapshot are mutually exclusive — keep only one base"
        )
    if out.get("template"):
        errors.append(
            "template field refused — for org shape use sourceOrg (after listing "
            "via dx-org-shape-manage); for snapshot use snapshot (via "
            "dx-org-snapshot-manage). Pure shape/snapshot create: hand off those skills."
        )

    edition = out.get("edition")
    if has_source_org or has_snapshot:
        if edition in ("", None):
            out.pop("edition", None)
        elif edition not in EDITIONS:
            errors.append(
                f"illegal edition '{edition}' — must be one of {sorted(EDITIONS)}"
            )
        else:
            warnings.append(
                "edition is usually omitted when using sourceOrg/snapshot — "
                "kept because you set it"
            )
    else:
        if edition is None or edition == "":
            out["edition"] = "Developer"
            warnings.append("edition omitted — defaulted to Developer")
        elif edition not in EDITIONS:
            errors.append(
                f"illegal edition '{edition}' — must be one of {sorted(EDITIONS)}"
            )

    if "hasSampleData" in out:
        coerced, w = coerce_has_sample_data(out["hasSampleData"])
        out["hasSampleData"] = coerced
        warnings.extend(w)


def _map_kept_features(
    out: dict, features_doc: dict, warnings: list[str]
) -> list[str]:
    kept: list[str] = []
    seen: set[str] = set()
    for raw in out.get("features") or []:
        if not isinstance(raw, str):
            warnings.append(f"non-string feature {raw!r} — dropped")
            continue
        mapped, w = map_feature_token(raw, features_doc)
        warnings.extend(w)
        if mapped and mapped not in seen:
            kept.append(mapped)
            seen.add(mapped)
    if "features" in out or kept:
        out["features"] = kept
    return kept


def _warn_edition_and_entitlement(
    kept: list[str],
    out: dict,
    features_doc: dict,
    warnings: list[str],
) -> None:
    by_name = _index_features(features_doc)
    edition = out.get("edition")
    for feat in kept:
        base = feat.split(":", 1)[0]
        entry = by_name.get(base.lower())
        if not entry:
            continue
        notes = entry.get("editionNotes")
        if notes and edition:
            if "Not available" in notes:
                warnings.append(
                    f"{base}: {notes} — suggest upgrading edition, or drop this "
                    "feature if edition is a hard constraint"
                )
            elif (
                edition in ("Group", "Professional", "Partner Group", "Partner Professional")
                and "Enterprise" in notes
                and edition.split()[-1] not in notes
            ):
                warnings.append(
                    f"{base}: may require a higher edition than {edition} "
                    f"({notes}). Suggest upgrading edition, or drop the feature "
                    "if edition is a hard constraint"
                )
        # Do not warn on bare "license" in PUBLIC blurbs — those are product
        # licenses, not Dev Hub. Create-time entitlement stays with dx-org-manage.


def _apply_orgname_and_namespace(
    out: dict, errors: list[str], warnings: list[str]
) -> list[str]:
    """orgName token rewrite + optional My Domain name suggestions."""
    if "orgName" in out:
        rewritten, w = rewrite_org_name(out.get("orgName"))
        warnings.extend(w)
        if rewritten:
            out["orgName"] = rewritten
        else:
            del out["orgName"]

    # namespace: pass through unchanged — Dev Hub / create owns validity.

    suggestions: list[str] = []
    if out.get("orgName"):
        suggestions = suggest_org_names(out["orgName"])
        warnings.append(
            "if My Domain is taken at create time, try: "
            f"{', '.join(suggestions)}"
        )
    return suggestions


def _schema_gate(
    out: dict, errors: list[str], warnings: list[str]
) -> None:
    skip = any(
        "template field refused" in e or "shape/snapshot-only def refused" in e
        for e in errors
    )
    if skip:
        return
    if Draft7Validator is None:
        warnings.append(JSONSCHEMA_MISSING_WARNING)
        return
    try:
        errors.extend(validate_against_schema(out, load_schema()))
    except FileNotFoundError as e:
        errors.append(f"JSON Schema: {e}")
    except Exception as e:  # noqa: BLE001 — do not block write on validator crash
        warnings.append(f"JSON Schema: validator failed to load/run ({e}); skipped")


def _is_hard_fail(errors: list[str]) -> bool:
    """Any error refuses apply. Warnings are the write-with-notes channel."""
    return bool(errors)


def validate_and_enrich(doc: dict, features_doc: dict, settings_map: dict) -> dict:
    """Validate, enrich, and return the CLI result envelope."""
    errors: list[str] = []
    warnings: list[str] = []
    if not isinstance(doc, dict):
        kind = type(doc).__name__
        errors.append(f"scratch-def draft must be a JSON object (got {kind})")
        return {
            "ok": False,
            "document": {},
            "errors": errors,
            "warnings": [],
            "suggestedPath": f"config/{DEFAULT_OUT_NAME}",
            "confirmCard": {"errors": errors, "warnings": [], "features": []},
        }
    out = deepcopy(doc)
    if not _has_generate_intent(out):
        errors.append(
            "underspecified def refused — provide edition and/or features, "
            "or sourceOrg/snapshot with features to layer"
        )

    _strip_org_preferences(out, errors, warnings)
    _normalize_base_and_edition(out, errors, warnings)
    kept = _map_kept_features(out, features_doc, warnings)
    kept, dep_w = enrich_feature_dependencies(kept, features_doc)
    warnings.extend(dep_w)
    if "features" in out or kept:
        out["features"] = kept

    if (
        (out.get("sourceOrg") or out.get("snapshot"))
        and not kept
        and not out.get("settings")
    ):
        errors.append(
            "shape/snapshot-only def refused — hand off to dx-org-shape-manage / "
            "dx-org-snapshot-manage with context. To layer features on a shape/snapshot, "
            "resolve sourceOrg/snapshot then add features[] and re-run."
        )

    _warn_edition_and_entitlement(kept, out, features_doc, warnings)

    raw_settings = out.get("settings")
    if raw_settings is not None and not isinstance(raw_settings, dict):
        errors.append(
            f"settings must be a JSON object (got {type(raw_settings).__name__})"
        )
        del out["settings"]
        raw_settings = None

    settings, w = enrich_settings(kept, raw_settings, settings_map)
    warnings.extend(w)
    if settings:
        out["settings"] = settings
    elif "settings" in out and not out["settings"]:
        del out["settings"]

    if "objectSettings" in out:
        cleaned = validate_object_settings(out.get("objectSettings"), errors, warnings)
        if cleaned is None:
            del out["objectSettings"]
        else:
            out["objectSettings"] = cleaned

    org_name_suggestions = _apply_orgname_and_namespace(out, errors, warnings)
    _schema_gate(out, errors, warnings)
    suggested_path = suggest_purpose_path(out)
    settings_for_card = out.get("settings") if isinstance(out.get("settings"), dict) else {}

    return {
        "ok": not _is_hard_fail(errors),
        "document": out,
        "errors": errors,
        "warnings": warnings,
        "suggestedPath": suggested_path,
        "confirmCard": {
            "edition": out.get("edition"),
            "features": out.get("features") or [],
            "settingsPaths": sorted(p for p, _ in _flatten(settings_for_card)),
            "orgName": out.get("orgName"),
            "orgNameSuggestions": org_name_suggestions,
            "sourceOrg": out.get("sourceOrg"),
            "snapshot": out.get("snapshot"),
            "suggestedPath": suggested_path,
            "warnings": warnings,
            "errors": errors,
        },
    }


def _flatten(obj: dict, prefix: str = "") -> list[tuple[str, Any]]:
    if not isinstance(obj, dict):
        return []
    out: list[tuple[str, Any]] = []
    for k, v in obj.items():
        path = f"{prefix}.{k}" if prefix else k
        if isinstance(v, dict):
            out.extend(_flatten(v, path))
        else:
            out.append((path, v))
    return out


def _has_generate_intent(doc: dict) -> bool:
    if doc.get("edition") not in (None, ""):
        return True
    feats = doc.get("features")
    if isinstance(feats, list) and feats:
        return True
    if doc.get("sourceOrg") or doc.get("snapshot"):
        return True
    if doc.get("settings") not in (None, {}):
        return True
    if doc.get("objectSettings") not in (None, {}):
        return True
    if doc.get("orgName") not in (None, ""):
        return True
    if doc.get("namespace") not in (None, ""):
        return True
    return False


def _load_draft_text(text: str) -> tuple[dict | None, str | None]:
    try:
        doc = json.loads(text)
    except json.JSONDecodeError as e:
        return None, f"JSON parse error: {e}"
    if not isinstance(doc, dict):
        kind = type(doc).__name__
        return None, f"scratch-def draft must be a JSON object (got {kind})"
    return doc, None


def _load_draft(path: Path) -> tuple[dict | None, str | None]:
    try:
        return _load_draft_text(path.read_text(encoding="utf-8"))
    except OSError as e:
        return None, f"cannot read draft file: {e}"


def _resolve_draft(
    *,
    file: Path | None = None,
    json_text: str | None = None,
    allow_stdin: bool = True,
) -> tuple[dict | None, str | None]:
    """Load draft from --json, --file, or stdin (agent keeps draft in context)."""
    if file is not None and json_text is not None:
        return None, "pass only one of --file or --json"
    if json_text is not None:
        return _load_draft_text(json_text)
    if file is not None:
        return _load_draft(file)
    if allow_stdin and not sys.stdin.isatty():
        return _load_draft_text(sys.stdin.read())
    return (
        None,
        "draft required: pass --json '...', --file PATH, or pipe JSON on stdin",
    )


def _merge_catalog_warnings(result: dict, catalog_warnings: list[str]) -> dict:
    result["warnings"] = list(catalog_warnings) + list(result.get("warnings") or [])
    card = result.get("confirmCard")
    if isinstance(card, dict):
        card["warnings"] = list(catalog_warnings) + list(card.get("warnings") or [])
    return result


def cmd_validate(
    file: Path | None = None,
    *,
    json_text: str | None = None,
    allow_stdin: bool = True,
) -> int:
    features_doc, settings_map, cat_w = load_runtime_catalog()
    doc, err = _resolve_draft(file=file, json_text=json_text, allow_stdin=allow_stdin)
    if err:
        print(json.dumps({"ok": False, "errors": [err], "warnings": cat_w}))
        return 1
    result = _merge_catalog_warnings(
        validate_and_enrich(doc, features_doc, settings_map), cat_w
    )
    print(json.dumps(result, indent=2))
    return 0 if result["ok"] else 1


def cmd_preview(
    file: Path | None = None,
    *,
    json_text: str | None = None,
    allow_stdin: bool = True,
) -> int:
    return cmd_validate(file, json_text=json_text, allow_stdin=allow_stdin)


def cmd_apply(
    dest: Path,
    file: Path | None = None,
    *,
    json_text: str | None = None,
    allow_stdin: bool = True,
) -> int:
    """Validate + write. Draft from --json / stdin / --file; only --out hits disk."""
    features_doc, settings_map, cat_w = load_runtime_catalog()
    doc, err = _resolve_draft(file=file, json_text=json_text, allow_stdin=allow_stdin)
    if err:
        print(json.dumps({"ok": False, "errors": [err], "warnings": cat_w}))
        return 1
    result = _merge_catalog_warnings(
        validate_and_enrich(doc, features_doc, settings_map), cat_w
    )
    path_errs = assert_safe_output_path(dest)
    if path_errs:
        result["ok"] = False
        result["errors"] = list(result.get("errors") or []) + path_errs
        result.setdefault(
            "suggestedPath", suggest_purpose_path(result.get("document") or {})
        )
        print(json.dumps(result, indent=2))
        return 1
    if not result["ok"]:
        print(json.dumps(result, indent=2))
        return 1
    # config/ must already exist (assert_safe_output_path); never mkdir it.
    dest.write_text(json.dumps(result["document"], indent=2) + "\n", encoding="utf-8")
    result["written"] = str(dest)
    print(json.dumps(result, indent=2))
    return 0


def cmd_map(tokens: list[str]) -> int:
    features_doc, _, cat_w = load_runtime_catalog()
    mapped = []
    warnings: list[str] = list(cat_w)
    for t in tokens:
        m, w = map_feature_token(t, features_doc)
        warnings.extend(w)
        if m:
            mapped.append(m)
    print(json.dumps({"mapped": mapped, "warnings": warnings}, indent=2))
    return 0


def _add_draft_source_args(sp: argparse.ArgumentParser) -> None:
    """Draft stays in agent context: prefer --json or stdin; --file is optional."""
    sp.add_argument(
        "--json",
        dest="json_text",
        default=None,
        help="Draft scratch-def JSON object (keep in chat/tool context; no draft file)",
    )
    sp.add_argument(
        "--file",
        type=Path,
        default=None,
        help="Optional path to a draft JSON file (tests / rare); prefer --json or stdin",
    )


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    sub = p.add_subparsers(dest="cmd", required=True)

    v = sub.add_parser("validate", help="Validate + enrich; print result JSON")
    _add_draft_source_args(v)

    pr = sub.add_parser(
        "preview",
        help="Same as validate (intent/edition/features/settings; no write)",
    )
    _add_draft_source_args(pr)

    a = sub.add_parser("apply", help="Validate + write enriched document")
    _add_draft_source_args(a)
    a.add_argument("--out", type=Path, required=True)

    m = sub.add_parser("map", help="Map raw feature tokens via cache")
    m.add_argument("tokens", nargs="+")

    args = p.parse_args(argv)
    if args.cmd == "validate":
        return cmd_validate(file=args.file, json_text=args.json_text)
    if args.cmd == "preview":
        return cmd_preview(file=args.file, json_text=args.json_text)
    if args.cmd == "apply":
        return cmd_apply(args.out, file=args.file, json_text=args.json_text)
    if args.cmd == "map":
        return cmd_map(args.tokens)
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
