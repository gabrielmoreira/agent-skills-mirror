#!/usr/bin/env python3
"""Generate a single-org introspection report.

Takes one collected org data directory (output of collect_org_data.py)
and produces a summary report in markdown and/or JSON.

Usage:
  introspect_org.py --org /tmp/org-data --output /tmp/report
  introspect_org.py --org /tmp/org-data --output /tmp/report --format markdown
"""

import argparse
import json
import os
import sys
from datetime import date

# ── Reuse categorization from compute_diff ──────────────────────────

PERM_CATEGORIES = [
    ("Commerce",     ["commerce", "b2b", "b2c", "order", "cart", "store", "checkout"]),
    ("Platform/API", ["platform", "api", "rest", "soap", "bulk", "streaming", "connect", "metadata"]),
    ("Security",     ["security", "auth", "login", "mfa", "sso", "encryption", "certificate", "session", "password", "oauth"]),
    ("Einstein/AI",  ["einstein", "ai", "predict", "ml", "copilot", "agent"]),
    ("Service",      ["service", "case", "knowledge", "chat", "messaging", "omni", "entitlement"]),
    ("Data",         ["data", "record", "report", "dashboard", "analytics", "tableau"]),
    ("Trialforce",   ["trial", "trialforce", "tso", "tmo", "signup", "template", "edition"]),
    ("Sales",        ["sales", "opportunity", "lead", "forecast", "quote", "contract"]),
    ("Work/HR",      ["work", "hr", "employee", "shift", "wellness"]),
]

VALUE_CATEGORIES = [
    ("Identity",       ["name", "edition", "org", "domain", "id", "type", "instance", "locale"]),
    ("Storage",        ["storage", "file", "size", "space", "quota"]),
    ("Feature Limits", ["max", "limit", "count", "num", "enable"]),
    ("API",            ["api", "call", "request", "bandwidth"]),
]


def classify(name, categories, default="Other"):
    lower = name.lower()
    for cat, keywords in categories:
        if any(kw in lower for kw in keywords):
            return cat
    return default


# ── Data loading (same as compute_diff.py) ──────────────────────────

def load_org_data(path):
    if os.path.isdir(path):
        combined = os.path.join(path, "combined.json")
        if os.path.exists(combined):
            with open(combined) as f:
                return json.load(f)
        manifest_path = os.path.join(path, "manifest.json")
        if not os.path.exists(manifest_path):
            raise FileNotFoundError(f"Directory {path} has no manifest.json or combined.json")
        with open(manifest_path) as f:
            manifest = json.load(f)
        data = {}
        for cat, fname in manifest.get("files", {}).items():
            fpath = os.path.join(path, fname)
            with open(fpath) as f:
                chunk = json.load(f)
            if isinstance(chunk, dict):
                data.update(chunk)
            else:
                data[cat] = chunk
        return data

    with open(path) as f:
        return json.load(f)


# ── Analysis ────────────────────────────────────────────────────────

def analyze_metadata(data):
    types = data.get("metadata_types", [])
    components = data.get("metadata_components", {})
    by_type = {}
    total = 0
    namespaced_total = 0
    for mtype, items in sorted(components.items()):
        org_native = [c for c in items if not c.get("namespace")]
        namespaced = [c for c in items if c.get("namespace")]
        org_native_names = sorted(
            c.get("fullName") or c.get("name", "") for c in org_native
        )
        namespaced_by_ns = {}
        for c in namespaced:
            ns = c.get("namespace", "unknown")
            namespaced_by_ns.setdefault(ns, []).append(
                c.get("fullName") or c.get("name", "")
            )
        for ns in namespaced_by_ns:
            namespaced_by_ns[ns] = sorted(namespaced_by_ns[ns])
        by_type[mtype] = {
            "total": len(items),
            "org_native": len(org_native),
            "namespaced": len(namespaced),
            "org_native_names": org_native_names,
            "namespaced_by_ns": namespaced_by_ns,
        }
        total += len(org_native)
        namespaced_total += len(namespaced)
    return {
        "types_discovered": len(types),
        "types_with_components": len(components),
        "total_org_native": total,
        "total_namespaced": namespaced_total,
        "by_type": by_type,
    }


def analyze_permissions(data):
    perms = data.get("permissions", {})
    by_category = {}
    enabled = 0
    disabled = 0
    non_boolean = 0
    for name, val in perms.items():
        cat = classify(name, PERM_CATEGORIES)
        if cat not in by_category:
            by_category[cat] = {"enabled": 0, "disabled": 0, "non_boolean": 0, "items": []}
        v = val if isinstance(val, str) else val.get("value", str(val)) if isinstance(val, dict) else str(val)
        if v.lower() in ("enabled", "true"):
            by_category[cat]["enabled"] += 1
            enabled += 1
        elif v.lower() in ("disabled", "false"):
            by_category[cat]["disabled"] += 1
            disabled += 1
        else:
            by_category[cat]["non_boolean"] += 1
            non_boolean += 1
        by_category[cat]["items"].append((name, v))
    return {
        "total": len(perms),
        "enabled": enabled,
        "disabled": disabled,
        "non_boolean": non_boolean,
        "by_category": by_category,
    }


def analyze_org_values(data):
    vals = data.get("org_values", {})
    by_category = {}
    for name, val in vals.items():
        cat = classify(name, VALUE_CATEGORIES)
        if cat not in by_category:
            by_category[cat] = []
        by_category[cat].append((name, val))
    return {"total": len(vals), "by_category": by_category}


def analyze_packages(data):
    pkgs = data.get("installed_packages", [])
    return {
        "count": len(pkgs),
        "packages": [
            {"name": p.get("name", ""), "namespace": p.get("namespace") or "", "version": p.get("version", "")}
            for p in pkgs
        ],
    }


def analyze_licenses(data):
    lics = data.get("licenses", {})
    result = {}
    for category in ("user", "permission_set", "package"):
        items = lics.get(category, [])
        result[category] = {
            "count": len(items),
            "items": items,
        }
    return result


def analyze_system_permissions(data):
    sp_raw = data.get("system_permissions", {})
    if isinstance(sp_raw, dict):
        sp = sp_raw.get("permission_sets", [])
    else:
        sp = sp_raw
    total_enabled = 0
    sets = []
    for ps in sp:
        name = ps.get("name", ps.get("label", "Unknown"))
        perms = ps.get("permissions", {})
        enabled = sum(1 for v in perms.values() if v)
        total_enabled += enabled
        sets.append({"name": name, "enabled": enabled, "total": len(perms)})
    return {"permission_sets": len(sp), "total_enabled": total_enabled, "sets": sets}


def analyze_deep_data(data):
    dd = data.get("deep_data", {})
    result = {}
    for category, records in dd.items():
        result[category] = len(records) if isinstance(records, list) else 0
    return result


# ── Render markdown ─────────────────────────────────────────────────

def render_markdown(data, meta, perms, vals, pkgs, lics, sys_perms, deep, label):
    lines = []
    lines.append(f"# Org Analysis Report: {label}\n")
    lines.append(f"| Field | Value |")
    lines.append(f"|-------|-------|")
    lines.append(f"| **Org ID** | {data.get('org_id', 'N/A')} |")
    lines.append(f"| **Name** | {data.get('org_name', 'N/A')} |")
    lines.append(f"| **Edition** | {data.get('org_edition', 'N/A')} |")
    lines.append(f"| **Date** | {date.today()} |")
    lines.append("")

    # Summary
    lines.append("---\n")
    lines.append("## Summary\n")
    lines.append("| Category | Count |")
    lines.append("|----------|-------|")
    lines.append(f"| Metadata types discovered | {meta['types_discovered']} |")
    lines.append(f"| Types with components | {meta['types_with_components']} |")
    lines.append(f"| Org-native components | {meta['total_org_native']} |")
    lines.append(f"| Namespaced components | {meta['total_namespaced']} |")
    lines.append(f"| Org settings | {perms['total']} ({perms['enabled']} enabled, {perms['disabled']} disabled) |")
    lines.append(f"| Org limits | {vals['total']} |")
    lines.append(f"| Installed packages | {pkgs['count']} |")
    lines.append(f"| System permission sets | {sys_perms['permission_sets']} |")
    deep_total = sum(deep.values())
    lines.append(f"| Deep data records | {deep_total} |")
    errors = data.get("errors", [])
    if errors:
        lines.append(f"| Collection warnings | {len(errors)} |")
    lines.append("")

    # Metadata inventory
    lines.append("---\n")
    lines.append("## Metadata Inventory\n")
    lines.append("| Type | Org-Native | Namespaced | Total |")
    lines.append("|------|-----------|------------|-------|")
    for mtype, counts in sorted(meta["by_type"].items()):
        if counts["total"] > 0:
            lines.append(f"| {mtype} | {counts['org_native']} | {counts['namespaced']} | {counts['total']} |")
    lines.append(f"| **Total** | **{meta['total_org_native']}** | **{meta['total_namespaced']}** | **{meta['total_org_native'] + meta['total_namespaced']}** |")
    lines.append("")

    # Detailed metadata listing
    lines.append("---\n")
    lines.append("## Metadata Components by Type\n")
    for mtype, counts in sorted(meta["by_type"].items()):
        if counts["total"] == 0:
            continue
        lines.append(f"#### {mtype} ({counts['org_native']} org-native, {counts['namespaced']} namespaced)\n")
        if counts["org_native_names"]:
            lines.append(f"**Org-native ({counts['org_native']}):** " +
                         ", ".join(f"`{n}`" for n in counts["org_native_names"]))
            lines.append("")
        if counts["namespaced_by_ns"]:
            for ns, names in sorted(counts["namespaced_by_ns"].items()):
                lines.append(f"**Namespaced — `{ns}` ({len(names)}):** " +
                             ", ".join(f"`{n}`" for n in names))
                lines.append("")
    lines.append("")

    # Installed packages
    lines.append("---\n")
    lines.append("## Installed Packages\n")
    if pkgs["packages"]:
        lines.append("| Package | Namespace | Version |")
        lines.append("|---------|-----------|---------|")
        for p in pkgs["packages"]:
            lines.append(f"| {p['name']} | {p.get('namespace') or '—'} | {p['version']} |")
    else:
        lines.append("No installed packages.\n")
    lines.append("")

    # Org settings by category
    lines.append("---\n")
    lines.append("## Org Settings\n")
    lines.append("| Category | Enabled | Disabled | Non-Boolean |")
    lines.append("|----------|---------|----------|-------------|")
    for cat in sorted(perms["by_category"].keys()):
        info = perms["by_category"][cat]
        lines.append(f"| {cat} | {info['enabled']} | {info['disabled']} | {info['non_boolean']} |")
    lines.append(f"| **Total** | **{perms['enabled']}** | **{perms['disabled']}** | **{perms['non_boolean']}** |")
    lines.append("")

    # Org limits by category
    lines.append("---\n")
    lines.append("## Org Limits\n")
    for cat in sorted(vals["by_category"].keys()):
        items = vals["by_category"][cat]
        lines.append(f"### {cat}\n")
        lines.append("| Limit | Value |")
        lines.append("|-------|-------|")
        for name, val in sorted(items):
            lines.append(f"| {name} | {val} |")
        lines.append("")

    # Licenses
    lines.append("---\n")
    lines.append("## Licenses\n")
    for category in ("user", "permission_set", "package"):
        info = lics[category]
        title = category.replace("_", " ").title()
        lines.append(f"### {title} Licenses ({info['count']})\n")
        if info["items"]:
            sample = info["items"][0]
            if isinstance(sample, dict):
                keys = [k for k in sample.keys() if k not in ("attributes",)]
                if keys:
                    lines.append("| " + " | ".join(keys) + " |")
                    lines.append("| " + " | ".join(["---"] * len(keys)) + " |")
                    for item in info["items"]:
                        vals_row = []
                        for k in keys:
                            v = item.get(k, "")
                            if k in ("AllowedLicenses", "TotalLicenses") and v == -1:
                                v = "-1 (unlimited)"
                            vals_row.append(str(v))
                        lines.append("| " + " | ".join(vals_row) + " |")
            else:
                for item in info["items"]:
                    lines.append(f"- {item}")
        else:
            lines.append("None.\n")
        lines.append("")

    # System permissions
    lines.append("---\n")
    lines.append("## System Permissions\n")
    lines.append(f"**{sys_perms['permission_sets']}** permission sets, **{sys_perms['total_enabled']}** total enabled permissions.\n")
    if sys_perms["sets"]:
        lines.append("| Permission Set | Enabled | Total Fields |")
        lines.append("|---------------|---------|-------------|")
        for s in sorted(sys_perms["sets"], key=lambda x: x["enabled"], reverse=True):
            lines.append(f"| {s['name']} | {s['enabled']} | {s['total']} |")
    lines.append("")

    # Deep data
    lines.append("---\n")
    lines.append("## Deep Data\n")
    lines.append("| Category | Records |")
    lines.append("|----------|---------|")
    for cat, count in sorted(deep.items()):
        lines.append(f"| {cat} | {count} |")
    lines.append(f"| **Total** | **{deep_total}** |")
    lines.append("")

    # Collection warnings
    if errors:
        lines.append("---\n")
        lines.append("## Collection Warnings\n")
        for err in errors:
            lines.append(f"- {err}")
        lines.append("")

    lines.append("---\n")
    lines.append("*Report generated by dx-org-analyze. Read-only — no changes were made to the org.*\n")

    return "\n".join(lines)


# ── Main ────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Generate a single-org introspection report.")
    parser.add_argument("--org", required=True, help="Path to org data directory or JSON file (from collect_org_data.py)")
    parser.add_argument("--output", required=True, help="Output path prefix (writes .json and/or .md)")
    parser.add_argument("--format", choices=["markdown", "json", "both"], default="both",
                        help="Output format (default: both)")
    parser.add_argument("--label", default=None, help="Display name for the org (default: org name from data)")
    args = parser.parse_args()

    try:
        data = load_org_data(args.org)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error loading org data: {e}", file=sys.stderr)
        sys.exit(1)

    label = args.label or data.get("org_name", "Unknown Org")

    meta = analyze_metadata(data)
    perms = analyze_permissions(data)
    vals = analyze_org_values(data)
    pkgs = analyze_packages(data)
    lics = analyze_licenses(data)
    sys_perms = analyze_system_permissions(data)
    deep = analyze_deep_data(data)

    result = {
        "org_id": data.get("org_id"),
        "org_name": data.get("org_name"),
        "org_edition": data.get("org_edition"),
        "label": label,
        "metadata": meta,
        "permissions": perms,
        "org_values": vals,
        "packages": pkgs,
        "licenses": lics,
        "system_permissions": sys_perms,
        "deep_data": deep,
        "errors": data.get("errors", []),
    }

    if args.format in ("json", "both"):
        json_path = args.output + ".json"
        serializable = json.loads(json.dumps(result, default=str))
        with open(json_path, "w") as f:
            json.dump(serializable, f, indent=2)
        print(f"Wrote {json_path}")

    if args.format in ("markdown", "both"):
        md_path = args.output + ".md"
        md = render_markdown(data, meta, perms, vals, pkgs, lics, sys_perms, deep, label)
        with open(md_path, "w") as f:
            f.write(md)
        print(f"Wrote {md_path}")

    # Print summary
    print(f"\n# Org Analysis Report: {label}")
    print(f"  Edition: {data.get('org_edition', 'N/A')}")
    print(f"  Metadata: {meta['types_discovered']} types, {meta['total_org_native']} org-native + {meta['total_namespaced']} namespaced components")
    print(f"  Org settings: {perms['total']} ({perms['enabled']} enabled)")
    print(f"  Org limits: {vals['total']}")
    print(f"  Packages: {pkgs['count']}")
    print(f"  Licenses: {lics['user']['count']} user, {lics['permission_set']['count']} PSL, {lics['package']['count']} package")
    print(f"  System permissions: {sys_perms['permission_sets']} sets, {sys_perms['total_enabled']} enabled")
    deep_total = sum(deep.values())
    print(f"  Deep data: {deep_total} records")


if __name__ == "__main__":
    main()
