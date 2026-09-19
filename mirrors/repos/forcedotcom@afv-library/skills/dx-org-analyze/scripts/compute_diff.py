#!/usr/bin/env python3
"""Compute diff between two org data files and produce a report.

Takes two JSON files (output of collect_org_data.py) and outputs:
  - A JSON file with structured diff data
  - A markdown report with drift score, summary, and details

Usage:
  compute_diff.py --org-a org_a.json --org-b org_b.json --output /tmp/diff
  compute_diff.py --org-a org_a.json --org-b org_b.json --output /tmp/diff --format json
"""

import argparse
import json
import os
import sys
from datetime import date

# ── Drift score weights ──────────────────────────────────────────────

WEIGHT_METADATA = 0.6
WEIGHT_PERMISSION = 0.3
WEIGHT_PROFILE = 0.1

DRIFT_LEVELS = [
    (10, "LOW"),
    (30, "MODERATE"),
    (60, "HIGH"),
    (100, "CRITICAL"),
]

# ── Permission categories ────────────────────────────────────────────

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

# ── Org value categories ─────────────────────────────────────────────

VALUE_CATEGORIES = [
    ("Identity",       ["name", "edition", "org", "domain", "id", "type", "instance", "locale"]),
    ("Storage",        ["storage", "file", "size", "space", "quota"]),
    ("Feature Limits", ["max", "limit", "count", "num", "enable"]),
    ("API",            ["api", "call", "request", "bandwidth"]),
]


def classify(name, categories, default="Other"):
    lower = name.lower()
    for label, keywords in categories:
        if any(k in lower for k in keywords):
            return label
    return default


def drift_level(score):
    for threshold, level in DRIFT_LEVELS:
        if score <= threshold:
            return level
    return "CRITICAL"


def safe_pct(num, denom):
    return (num / denom * 100) if denom > 0 else 0.0


# ── Core diff logic ──────────────────────────────────────────────────

def diff_metadata(a_data, b_data):
    a_components = a_data.get("metadata_components", {})
    b_components = b_data.get("metadata_components", {})
    all_types = sorted(set(list(a_components.keys()) + list(b_components.keys())))

    stats = []
    for mtype in all_types:
        a_items = a_components.get(mtype, [])
        b_items = b_components.get(mtype, [])

        a_names = {c["fullName"] for c in a_items if not c.get("namespace")}
        b_names = {c["fullName"] for c in b_items if not c.get("namespace")}

        if not a_names and not b_names:
            continue

        shared = a_names & b_names
        only_a = a_names - b_names
        only_b = b_names - a_names

        a_only_sorted = sorted(only_a)
        b_only_sorted = sorted(only_b)
        shared_sorted = sorted(shared)
        stats.append({
            "type": mtype,
            "a_count": len(a_names),
            "b_count": len(b_names),
            "shared": len(shared),
            "a_only": len(only_a),
            "b_only": len(only_b),
            "identical": len(shared),
            "different": 0,
            "a_only_names": a_only_sorted,
            "b_only_names": b_only_sorted,
            "shared_names": shared_sorted,
        })

    return stats


def _perm_value(v):
    """Extract the raw value string from a permission entry."""
    return str(v.get("value", v) if isinstance(v, dict) else v)


def _is_enabled(v):
    return _perm_value(v).lower() in ("true", "enabled", "yes")


def diff_permissions(a_data, b_data):
    a_perms = a_data.get("permissions", {})
    b_perms = b_data.get("permissions", {})

    a_enabled = {k for k, v in a_perms.items() if _is_enabled(v)}
    b_enabled = {k for k, v in b_perms.items() if _is_enabled(v)}

    only_a = sorted(a_enabled - b_enabled)
    only_b = sorted(b_enabled - a_enabled)
    shared = a_enabled & b_enabled

    a_cats = {}
    for p in only_a:
        a_cats.setdefault(classify(p, PERM_CATEGORIES), []).append(p)

    b_cats = {}
    for p in only_b:
        b_cats.setdefault(classify(p, PERM_CATEGORIES), []).append(p)

    value_diffs = []
    all_keys = sorted(set(a_perms.keys()) | set(b_perms.keys()))
    for k in all_keys:
        if k in a_enabled or k in b_enabled:
            continue
        a_val = _perm_value(a_perms[k]) if k in a_perms else "(not set)"
        b_val = _perm_value(b_perms[k]) if k in b_perms else "(not set)"
        if a_val != b_val:
            value_diffs.append({"name": k, "a": a_val, "b": b_val})

    return {
        "a_only": only_a,
        "b_only": only_b,
        "shared_count": len(shared),
        "a_cats": a_cats,
        "b_cats": b_cats,
        "value_diffs": value_diffs,
    }


def diff_org_values(a_data, b_data):
    a_vals = a_data.get("org_values", {})
    b_vals = b_data.get("org_values", {})

    all_keys = sorted(set(a_vals.keys()) | set(b_vals.keys()))
    diffs = []
    for k in all_keys:
        av = a_vals.get(k, "(not set)")
        bv = b_vals.get(k, "(not set)")
        if av != bv:
            diffs.append({"name": k, "a": av, "b": bv})

    cats = {}
    for d in diffs:
        cats.setdefault(classify(d["name"], VALUE_CATEGORIES), []).append(d)

    return {"total": len(all_keys), "diffs": diffs, "cats": cats}


def _pkg_key(p):
    """Unique key for a package: namespace if present, otherwise name."""
    ns = p.get("namespace") or ""
    name = p.get("name", "")
    if ns:
        return ns
    return f"::{name}"


def diff_packages(a_data, b_data):
    a_pkgs = {_pkg_key(p): p for p in a_data.get("installed_packages", [])}
    b_pkgs = {_pkg_key(p): p for p in b_data.get("installed_packages", [])}

    only_a = [a_pkgs[ns] for ns in sorted(set(a_pkgs) - set(b_pkgs), key=str)]
    only_b = [b_pkgs[ns] for ns in sorted(set(b_pkgs) - set(a_pkgs), key=str)]
    shared_ns = sorted(set(a_pkgs) & set(b_pkgs), key=str)
    version_mismatches = [
        {"namespace": ns, "name": a_pkgs[ns]["name"],
         "a_version": a_pkgs[ns]["version"], "b_version": b_pkgs[ns]["version"]}
        for ns in shared_ns if a_pkgs[ns]["version"] != b_pkgs[ns]["version"]
    ]
    identical = [ns for ns in shared_ns if a_pkgs[ns]["version"] == b_pkgs[ns]["version"]]

    return {
        "a_only": only_a,
        "b_only": only_b,
        "version_mismatches": version_mismatches,
        "identical": [a_pkgs[ns] for ns in identical],
        "a_total": len(a_pkgs),
        "b_total": len(b_pkgs),
    }


def diff_licenses(a_data, b_data):
    result = {}
    for ltype in ["user", "permission_set", "package"]:
        a_lics = a_data.get("licenses", {}).get(ltype, [])
        b_lics = b_data.get("licenses", {}).get(ltype, [])

        key_field = "Name" if ltype != "package" else "NamespacePrefix"
        if ltype == "permission_set":
            key_field = "DeveloperName"

        a_map = {lic.get(key_field, ""): lic for lic in a_lics}
        b_map = {lic.get(key_field, ""): lic for lic in b_lics}

        only_a = [a_map[k] for k in sorted(set(a_map) - set(b_map))]
        only_b = [b_map[k] for k in sorted(set(b_map) - set(a_map))]
        diffs = []
        for k in sorted(set(a_map) & set(b_map)):
            a_tl = a_map[k].get("TotalLicenses")
            a_total = a_tl if a_tl is not None else a_map[k].get("AllowedLicenses", 0)
            b_tl = b_map[k].get("TotalLicenses")
            b_total = b_tl if b_tl is not None else b_map[k].get("AllowedLicenses", 0)
            if a_total != b_total:
                diffs.append({"name": k, "a_total": a_total, "b_total": b_total})

        result[ltype] = {"a_only": only_a, "b_only": only_b, "diffs": diffs,
                         "a_count": len(a_lics), "b_count": len(b_lics)}
    return result


def diff_system_permissions(a_data, b_data):
    """Diff system permissions (PermissionsXxx on PermissionSet) between orgs."""
    a_sp = a_data.get("system_permissions", {})
    b_sp = b_data.get("system_permissions", {})
    a_sets = {ps.get("label") or ps["name"]: ps for ps in a_sp.get("permission_sets", [])}
    b_sets = {ps.get("label") or ps["name"]: ps for ps in b_sp.get("permission_sets", [])}

    only_a_sets = sorted(set(a_sets) - set(b_sets))
    only_b_sets = sorted(set(b_sets) - set(a_sets))
    shared_sets = sorted(set(a_sets) & set(b_sets))

    per_set_diffs = []
    for label in shared_sets:
        a_perms = a_sets[label].get("permissions", {})
        b_perms = b_sets[label].get("permissions", {})
        a_enabled = set(a_perms.keys())
        b_enabled = set(b_perms.keys())
        a_only = sorted(a_enabled - b_enabled)
        b_only = sorted(b_enabled - a_enabled)
        if a_only or b_only:
            per_set_diffs.append({
                "name": label,
                "is_profile": a_sets[label].get("is_profile", False),
                "a_only": a_only,
                "b_only": b_only,
            })

    # Aggregate: across all sets, which permissions are enabled more/less
    all_a_perms = set()
    all_b_perms = set()
    for ps in a_sp.get("permission_sets", []):
        all_a_perms.update(ps.get("permissions", {}).keys())
    for ps in b_sp.get("permission_sets", []):
        all_b_perms.update(ps.get("permissions", {}).keys())

    return {
        "a_only_sets": only_a_sets,
        "b_only_sets": only_b_sets,
        "shared_sets": len(shared_sets),
        "per_set_diffs": per_set_diffs,
        "fields_discovered": max(len(a_sp.get("fields_discovered", [])), len(b_sp.get("fields_discovered", []))),
        "a_unique_perms": sorted(all_a_perms - all_b_perms),
        "b_unique_perms": sorted(all_b_perms - all_a_perms),
    }


def diff_package_components(a_data, b_data):
    """Extract all packaged metadata components, grouped by namespace."""
    # Build namespace → package name map from installed packages in both orgs
    pkg_name_map = {}
    for p in a_data.get("installed_packages", []) + b_data.get("installed_packages", []):
        ns = p.get("namespace") or p.get("NamespacePrefix")
        if ns and ns != "None":
            pkg_name_map[ns] = p.get("name", ns)

    # Only include namespaces that belong to an actual installed package
    all_ns = set(pkg_name_map.keys())

    namespaced = {}
    for ns in sorted(all_ns):
        a_by_type = {}
        b_by_type = {}
        for mtype, items in a_data.get("metadata_components", {}).items():
            names = sorted(c["fullName"] for c in items if c.get("namespace") == ns)
            if names:
                a_by_type[mtype] = names
        for mtype, items in b_data.get("metadata_components", {}).items():
            names = sorted(c["fullName"] for c in items if c.get("namespace") == ns)
            if names:
                b_by_type[mtype] = names

        if not a_by_type and not b_by_type:
            continue

        all_types = sorted(set(list(a_by_type.keys()) + list(b_by_type.keys())))
        types_detail = []
        for mtype in all_types:
            a_names = set(a_by_type.get(mtype, []))
            b_names = set(b_by_type.get(mtype, []))
            types_detail.append({
                "type": mtype,
                "a_count": len(a_names),
                "b_count": len(b_names),
                "shared": len(a_names & b_names),
                "shared_names": sorted(a_names & b_names),
                "a_only": sorted(a_names - b_names),
                "b_only": sorted(b_names - a_names),
                "a_only_count": len(a_names - b_names),
                "b_only_count": len(b_names - a_names),
            })

        namespaced[ns] = {
            "package_name": pkg_name_map.get(ns, ns),
            "types": types_detail,
            "a_total": sum(t["a_count"] for t in types_detail),
            "b_total": sum(t["b_count"] for t in types_detail),
        }

    # Non-namespaced packages — use installed_components data if available
    no_ns_pkgs = []
    for p in a_data.get("installed_packages", []) + b_data.get("installed_packages", []):
        ns = p.get("namespace") or p.get("NamespacePrefix")
        if not ns or ns == "None":
            name = p.get("name", "?")
            if name not in [x["name"] for x in no_ns_pkgs]:
                no_ns_pkgs.append({"name": name, "version": p.get("version", "?")})

    # Build per-org installed component breakdown for non-namespaced packages
    a_installed = a_data.get("installed_components", {})
    b_installed = b_data.get("installed_components", {})
    all_inst_types = sorted(set(list(a_installed.keys()) + list(b_installed.keys())))
    installed_by_type = []
    for mtype in all_inst_types:
        a_names = {c.get("name", "") for c in a_installed.get(mtype, [])} - {""}
        b_names = {c.get("name", "") for c in b_installed.get(mtype, [])} - {""}
        installed_by_type.append({
            "type": mtype,
            "a_count": len(a_names),
            "b_count": len(b_names),
            "shared": len(a_names & b_names),
            "shared_names": sorted(a_names & b_names),
            "a_only": sorted(a_names - b_names),
            "b_only": sorted(b_names - a_names),
            "a_only_count": len(a_names - b_names),
            "b_only_count": len(b_names - a_names),
        })

    return {
        "namespaced": namespaced,
        "non_namespaced": no_ns_pkgs,
        "installed_by_type": installed_by_type,
    }


def diff_deep_data(a_data, b_data):
    a_deep = a_data.get("deep_data", {})
    b_deep = b_data.get("deep_data", {})
    result = {}

    # Apex classes — compare body hash, API version, LOC for shared classes
    a_apex = {c["name"]: c for c in a_deep.get("apex_classes", [])}
    b_apex = {c["name"]: c for c in b_deep.get("apex_classes", [])}
    shared_apex = sorted(set(a_apex) & set(b_apex))
    apex_diffs = []
    for name in shared_apex:
        a, b = a_apex[name], b_apex[name]
        diffs = {}
        if a.get("bodyHash") != b.get("bodyHash") and a.get("bodyHash") and b.get("bodyHash"):
            diffs["body"] = "different"
        if a.get("apiVersion") != b.get("apiVersion"):
            diffs["apiVersion"] = {"a": a.get("apiVersion"), "b": b.get("apiVersion")}
        if a.get("loc") != b.get("loc"):
            diffs["loc"] = {"a": a.get("loc"), "b": b.get("loc")}
        if diffs:
            apex_diffs.append({"name": name, **diffs})
    result["apex_classes"] = {"shared": len(shared_apex), "different": len(apex_diffs), "diffs": apex_diffs}

    # Apex triggers — same logic
    a_trig = {c["name"]: c for c in a_deep.get("apex_triggers", [])}
    b_trig = {c["name"]: c for c in b_deep.get("apex_triggers", [])}
    shared_trig = sorted(set(a_trig) & set(b_trig))
    trig_diffs = []
    for name in shared_trig:
        a, b = a_trig[name], b_trig[name]
        if a.get("bodyHash") != b.get("bodyHash") and a.get("bodyHash") and b.get("bodyHash"):
            trig_diffs.append({"name": name, "body": "different"})
    result["apex_triggers"] = {"shared": len(shared_trig), "different": len(trig_diffs), "diffs": trig_diffs}

    # Custom fields — group by object, compare field sets
    a_fields = {}
    for f in a_deep.get("custom_fields", []):
        a_fields.setdefault(f["object"], {})[f["name"]] = f
    b_fields = {}
    for f in b_deep.get("custom_fields", []):
        b_fields.setdefault(f["object"], {})[f["name"]] = f

    field_diffs = []
    shared_objects = sorted(set(a_fields) & set(b_fields))
    for obj in shared_objects:
        af, bf = a_fields[obj], b_fields[obj]
        only_a = sorted(set(af) - set(bf))
        only_b = sorted(set(bf) - set(af))
        type_diffs = []
        for fname in sorted(set(af) & set(bf)):
            if af[fname].get("type") != bf[fname].get("type"):
                type_diffs.append({"field": fname, "a_type": af[fname].get("type"), "b_type": bf[fname].get("type")})
        if only_a or only_b or type_diffs:
            field_diffs.append({"object": obj, "a_only": only_a, "b_only": only_b, "type_diffs": type_diffs})
    result["custom_fields"] = {"objects_compared": len(shared_objects), "objects_with_diffs": len(field_diffs), "diffs": field_diffs}

    # Validation rules — compare active state and error message
    a_vr = {f"{v['object']}.{v['name']}": v for v in a_deep.get("validation_rules", [])}
    b_vr = {f"{v['object']}.{v['name']}": v for v in b_deep.get("validation_rules", [])}
    vr_diffs = []
    for key in sorted(set(a_vr) & set(b_vr)):
        a, b = a_vr[key], b_vr[key]
        if a.get("active") != b.get("active"):
            vr_diffs.append({"name": key, "a_active": a["active"], "b_active": b["active"]})
    result["validation_rules"] = {
        "a_only": sorted(set(a_vr) - set(b_vr)),
        "b_only": sorted(set(b_vr) - set(a_vr)),
        "active_diffs": vr_diffs,
    }

    # Flows — compare active version, process type
    a_flows = {f["name"]: f for f in a_deep.get("flows", [])}
    b_flows = {f["name"]: f for f in b_deep.get("flows", [])}
    flow_diffs = []
    for name in sorted(set(a_flows) & set(b_flows)):
        a, b = a_flows[name], b_flows[name]
        diffs = {}
        if a.get("processType") != b.get("processType"):
            diffs["processType"] = {"a": a.get("processType"), "b": b.get("processType")}
        if a.get("apiVersion") != b.get("apiVersion"):
            diffs["apiVersion"] = {"a": a.get("apiVersion"), "b": b.get("apiVersion")}
        if diffs:
            flow_diffs.append({"name": name, **diffs})
    result["flows"] = {"shared": len(set(a_flows) & set(b_flows)), "different": len(flow_diffs), "diffs": flow_diffs}

    # Named credentials — compare endpoints
    a_nc = {c["name"]: c for c in a_deep.get("named_credentials", [])}
    b_nc = {c["name"]: c for c in b_deep.get("named_credentials", [])}
    nc_diffs = []
    for name in sorted(set(a_nc) & set(b_nc)):
        if a_nc[name].get("endpoint") != b_nc[name].get("endpoint"):
            nc_diffs.append({"name": name, "a_endpoint": a_nc[name].get("endpoint", ""), "b_endpoint": b_nc[name].get("endpoint", "")})
    result["named_credentials"] = {
        "a_only": sorted(set(a_nc) - set(b_nc)),
        "b_only": sorted(set(b_nc) - set(a_nc)),
        "endpoint_diffs": nc_diffs,
    }

    return result


def enrich_metadata_with_deep_diffs(meta_stats, deep_diff):
    """Patch metadata stats with content-level difference counts from deep data.

    Splits 'shared' into 'identical' (same content) and 'different' (shared name,
    different content) using body hash / API version / active state comparisons
    already computed by diff_deep_data.
    """
    diff_names_by_type = {}

    for d in deep_diff.get("apex_classes", {}).get("diffs", []):
        diff_names_by_type.setdefault("ApexClass", set()).add(d["name"])
    for d in deep_diff.get("apex_triggers", {}).get("diffs", []):
        diff_names_by_type.setdefault("ApexTrigger", set()).add(d["name"])
    for d in deep_diff.get("flows", {}).get("diffs", []):
        diff_names_by_type.setdefault("Flow", set()).add(d["name"])
    for d in deep_diff.get("validation_rules", {}).get("active_diffs", []):
        diff_names_by_type.setdefault("ValidationRule", set()).add(d["name"])
    for d in deep_diff.get("custom_fields", {}).get("diffs", []):
        diff_names_by_type.setdefault("CustomObject", set()).add(d["object"])
    for d in deep_diff.get("named_credentials", {}).get("endpoint_diffs", []):
        diff_names_by_type.setdefault("NamedCredential", set()).add(d["name"])

    for stat in meta_stats:
        mtype = stat["type"]
        diff_set = diff_names_by_type.get(mtype, set())
        if diff_set:
            shared_names = set(stat.get("shared_names", []))
            different_count = len(diff_set & shared_names) if shared_names else min(len(diff_set), stat["shared"])
            stat["different"] = different_count
            stat["identical"] = stat["shared"] - different_count
        else:
            stat["identical"] = stat["shared"]

def compute_drift(meta_stats, perm_diff, a_data, b_data):
    total_a_only = sum(s["a_only"] for s in meta_stats)
    total_b_only = sum(s["b_only"] for s in meta_stats)
    total_shared = sum(s["shared"] for s in meta_stats)
    total_different = sum(s["different"] for s in meta_stats)
    total_unique = total_a_only + total_b_only + total_shared

    metadata_drift = safe_pct(total_a_only + total_b_only + total_different, total_unique)
    perm_denom = len(perm_diff["a_only"]) + len(perm_diff["b_only"]) + perm_diff["shared_count"]
    perm_drift = safe_pct(len(perm_diff["a_only"]) + len(perm_diff["b_only"]), perm_denom)
    # Floor: any real permission difference should register as at least 1% so it
    # isn't silently swallowed by rounding when shared_enabled >> diff count.
    if 0 < perm_drift < 1:
        perm_drift = 1.0

    a_profiles = {s for s in _get_names(a_data, "Profile")}
    b_profiles = {s for s in _get_names(b_data, "Profile")}
    prof_unique = len((a_profiles - b_profiles) | (b_profiles - a_profiles)) + len(a_profiles & b_profiles)
    prof_diff_count = len(a_profiles - b_profiles) + len(b_profiles - a_profiles)
    prof_drift = safe_pct(prof_diff_count, prof_unique)

    overall = (WEIGHT_METADATA * metadata_drift +
               WEIGHT_PERMISSION * perm_drift +
               WEIGHT_PROFILE * prof_drift)

    return {
        "metadata": round(metadata_drift, 1),
        "permission": round(perm_drift, 1),
        "profile": round(prof_drift, 1),
        "overall": round(overall, 1),
        "level": drift_level(overall),
        "totals": {
            "a_only": total_a_only, "b_only": total_b_only,
            "shared": total_shared, "different": total_different,
            "unique": total_unique,
        },
    }


def _get_names(org_data, mtype):
    items = org_data.get("metadata_components", {}).get(mtype, [])
    return {c["fullName"] for c in items if not c.get("namespace")}


# ── Markdown report ──────────────────────────────────────────────────

def render_markdown(a_data, b_data, meta_stats, perm_diff, val_diff, pkg_diff, lic_diff, sys_perm_diff, pkg_components, deep_diff, drift, label_a, label_b, show_shared=False):
    lines = []

    def w(s=""):
        lines.append(s)

    d = drift
    a_id = a_data.get("org_id", "?")
    b_id = b_data.get("org_id", "?")

    # 8a — Header + Drift Score
    w(f"# Org Comparison Report")
    w()
    a_name = a_data.get("org_name", "?")
    b_name = b_data.get("org_name", "?")
    a_edition = a_data.get("org_edition", "?")
    b_edition = b_data.get("org_edition", "?")
    w(f"| | {label_a} | {label_b} |")
    w(f"|--|--|--|")
    w(f"| **Org ID** | {a_id} | {b_id} |")
    w(f"| **Name** | {a_name} | {b_name} |")
    w(f"| **Edition** | {a_edition} | {b_edition} |")
    w()
    w(f"**Date:** {date.today().isoformat()}")
    types_discovered = len(a_data.get("metadata_types", []))
    if types_discovered:
        w(f"**Discovery method:** `describeMetadata` ({types_discovered} types discovered)")
    w()
    w("---")
    w()
    w(f"## Drift Score: {d['overall']:.0f}% — {d['level']}")
    w()
    w("| Dimension | Score | Weight | Contribution |")
    w("|-----------|-------|--------|--------------|")
    w(f"| Metadata Components | {d['metadata']:.0f}% | 60% | {d['metadata'] * 0.6:.0f}% |")
    w(f"| Org Permissions | {d['permission']:.0f}% | 30% | {d['permission'] * 0.3:.0f}% |")
    w(f"| Profiles | {d['profile']:.0f}% | 10% | {d['profile'] * 0.1:.0f}% |")
    w(f"| **Overall** | | | **{d['overall']:.0f}%** |")
    w()

    # 8b — Summary Statistics
    w("---")
    w()
    w("## Summary Statistics")
    w()
    w("| Category | {a} | {b} | Shared | {a} Only | {b} Only | Identical | Different |".format(a=label_a, b=label_b))
    w("|----------|-----|-----|--------|----------|----------|-----------|-----------|")
    for s in meta_stats:
        w(f"| {s['type']} | {s['a_count']} | {s['b_count']} | {s['shared']} | {s['a_only']} | {s['b_only']} | {s['identical']} | {s['different']} |")
    t = d["totals"]
    total_a = sum(s["a_count"] for s in meta_stats)
    total_b = sum(s["b_count"] for s in meta_stats)
    total_identical = sum(s["identical"] for s in meta_stats)
    w(f"| **Total** | **{total_a}** | **{total_b}** | **{t['shared']}** | **{t['a_only']}** | **{t['b_only']}** | **{total_identical}** | **{t['different']}** |")
    w()
    w("### Key Metrics")
    if types_discovered:
        types_with = len([s for s in meta_stats if s["a_count"] + s["b_count"] > 0])
        w(f"- **Metadata types discovered:** {types_discovered}, {types_with} with components")
    w(f"- **Total unique components:** {t['unique']}")
    w(f"- **Only in {label_a}:** {t['a_only']} ({safe_pct(t['a_only'], t['unique']):.0f}%)")
    w(f"- **Only in {label_b}:** {t['b_only']} ({safe_pct(t['b_only'], t['unique']):.0f}%)")
    w(f"- **In both:** {t['shared']} ({safe_pct(t['shared'], t['unique']):.0f}%)")
    w(f"- **Org Permissions:** {len(perm_diff['a_only'])} {label_a}-only, {len(perm_diff['b_only'])} {label_b}-only, {perm_diff['shared_count']} shared")
    w(f"- **Org Values:** {len(val_diff['diffs'])} of {val_diff['total']} differ")
    w(f"- **Installed Packages:** {pkg_diff['a_total']} in {label_a}, {pkg_diff['b_total']} in {label_b} ({len(pkg_diff['version_mismatches'])} version mismatches)")
    w()

    # 8c — Detailed Differences
    w("---")
    w()
    w("## Detailed Differences")
    w()

    # Metadata by type
    w("### Metadata Components by Type")
    for s in meta_stats:
        if s["a_only"] == 0 and s["b_only"] == 0 and not show_shared:
            continue
        w(f"\n#### {s['type']} ({s['shared']} shared, {s['a_only']} {label_a}-only, {s['b_only']} {label_b}-only)")
        w()
        if s["a_only_names"]:
            shown = s["a_only_names"]
            w(f"**{label_a}-only ({s['a_only']}):** " + ", ".join(f"`{n}`" for n in shown))
            w()
        if s["b_only_names"]:
            shown = s["b_only_names"]
            w(f"**{label_b}-only ({s['b_only']}):** " + ", ".join(f"`{n}`" for n in shown))
            w()
        if show_shared and s["shared_names"]:
            shown = s["shared_names"]
            w(f"**Shared ({s['shared']}):** " + ", ".join(f"`{n}`" for n in shown))
            w()

    # Profiles
    a_prof = _get_names(a_data, "Profile")
    b_prof = _get_names(b_data, "Profile")
    if a_prof or b_prof:
        w("\n### Profiles")
        w()
        only_a_p = sorted(a_prof - b_prof)
        only_b_p = sorted(b_prof - a_prof)
        shared_p = sorted(a_prof & b_prof)
        if only_a_p:
            w(f"**{label_a}-only ({len(only_a_p)}):** " + ", ".join(only_a_p))
        if only_b_p:
            w(f"\n**{label_b}-only ({len(only_b_p)}):** " + ", ".join(only_b_p))
        if shared_p:
            w(f"\n**Shared ({len(shared_p)}):** " + ", ".join(shared_p))
        w()

    # Installed Packages
    if pkg_diff["a_total"] + pkg_diff["b_total"] > 0:
        w("\n### Installed Packages")
        w()
        if pkg_diff["a_only"]:
            w(f"**{label_a}-only ({len(pkg_diff['a_only'])}):**")
            w()
            w(f"| Package | Namespace | Version |")
            w(f"|---------|-----------|---------|")
            for p in pkg_diff["a_only"]:
                w(f"| {p['name']} | {p.get('namespace') or '—'} | {p['version']} |")
            w()
        if pkg_diff["b_only"]:
            w(f"**{label_b}-only ({len(pkg_diff['b_only'])}):**")
            w()
            w(f"| Package | Namespace | Version |")
            w(f"|---------|-----------|---------|")
            for p in pkg_diff["b_only"]:
                w(f"| {p['name']} | {p.get('namespace') or '—'} | {p['version']} |")
            w()
        if pkg_diff["version_mismatches"]:
            w(f"**Version mismatches ({len(pkg_diff['version_mismatches'])}):**")
            w()
            w(f"| Package | Namespace | {label_a} | {label_b} |")
            w(f"|---------|-----------|-----|-----|")
            for p in pkg_diff["version_mismatches"]:
                w(f"| {p['name']} | {p.get('namespace') or '—'} | {p['a_version']} | {p['b_version']} |")
            w()
        if pkg_diff["identical"]:
            w(f"**Identical ({len(pkg_diff['identical'])}):** " +
              ", ".join(f"{p['name']} ({p.get('namespace') or '—'} {p['version']})" for p in pkg_diff["identical"]))
            w()

    # Package Components
    ns_data = pkg_components.get("namespaced", {})
    no_ns = pkg_components.get("non_namespaced", [])
    inst_by_type = pkg_components.get("installed_by_type", [])
    if ns_data or no_ns:
        w("\n### Package Components")
        w()
        if no_ns:
            pkg_list = ", ".join(f"{p['name']} v{p['version']}" for p in no_ns)
            if inst_by_type:
                a_tot = sum(t["a_count"] for t in inst_by_type)
                b_tot = sum(t["b_count"] for t in inst_by_type)
                w(f"#### Non-namespaced packages ({a_tot} in {label_a}, {b_tot} in {label_b})")
                w()
                w(f"Packages: {pkg_list}")
                w()
                w(f"| Type | {label_a} | {label_b} | Shared | {label_a} Only | {label_b} Only |")
                w(f"|------|-----|-----|--------|----------|----------|")
                for t in inst_by_type:
                    w(f"| {t['type']} | {t['a_count']} | {t['b_count']} | {t['shared']} | {t['a_only_count']} | {t['b_only_count']} |")
                w()
                for t in inst_by_type:
                    if not t["a_only"] and not t["b_only"] and not (show_shared and t.get("shared_names")):
                        continue
                    w(f"**{t['type']}:**")
                    if t["a_only"]:
                        shown = t["a_only"]
                        w(f"  {label_a}-only: " + ", ".join(f"`{n}`" for n in shown))
                    if t["b_only"]:
                        shown = t["b_only"]
                        w(f"  {label_b}-only: " + ", ".join(f"`{n}`" for n in shown))
                    if show_shared and t.get("shared_names"):
                        shown = t["shared_names"]
                        w(f"  Shared: " + ", ".join(f"`{n}`" for n in shown))
                    w()
            else:
                w(f"**Non-namespaced packages** (no ManageableState data — re-collect to see components):")
                w()
                for p in no_ns:
                    w(f"- {p['name']} v{p['version']}")
                w()
        for ns, info in ns_data.items():
            pkg_name = info["package_name"]
            a_tot = info["a_total"]
            b_tot = info["b_total"]
            w(f"#### `{ns}` — {pkg_name} ({a_tot} in {label_a}, {b_tot} in {label_b})")
            w()
            w(f"| Type | {label_a} | {label_b} | Shared | {label_a} Only | {label_b} Only |")
            w(f"|------|-----|-----|--------|----------|----------|")
            for t in info["types"]:
                w(f"| {t['type']} | {t['a_count']} | {t['b_count']} | {t['shared']} | {t['a_only_count']} | {t['b_only_count']} |")
            w()
            for t in info["types"]:
                if not t["a_only"] and not t["b_only"] and not (show_shared and t.get("shared_names")):
                    continue
                w(f"**{t['type']}:**")
                if t["a_only"]:
                    shown = t["a_only"]
                    w(f"  {label_a}-only: " + ", ".join(f"`{n}`" for n in shown))
                if t["b_only"]:
                    shown = t["b_only"]
                    w(f"  {label_b}-only: " + ", ".join(f"`{n}`" for n in shown))
                if show_shared and t.get("shared_names"):
                    shown = t["shared_names"]
                    w(f"  Shared: " + ", ".join(f"`{n}`" for n in shown))
                w()

    # Permissions
    w("\n### Org Permissions")
    w()
    w(f"**Shared enabled:** {perm_diff['shared_count']}")
    w()
    for side_label, cats in [(f"{label_a}-Only", perm_diff["a_cats"]), (f"{label_b}-Only", perm_diff["b_cats"])]:
        total_side = sum(len(v) for v in cats.values())
        if total_side == 0:
            continue
        w(f"**{side_label} ({total_side} total):**")
        w()
        for cat in sorted(cats.keys()):
            items = cats[cat]
            shown = items
            w(f"*{cat}* ({len(items)}): " + ", ".join(f"`{p}`" for p in shown))
        w()

    if perm_diff.get("value_diffs"):
        w(f"**Settings with different values ({len(perm_diff['value_diffs'])}):**")
        w()
        w(f"| Setting | {label_a} | {label_b} |")
        w("|---------|--------|--------|")
        for vd in perm_diff["value_diffs"]:
            w(f"| `{vd['name']}` | {vd['a']} | {vd['b']} |")
        w()

    # System Permissions (PermissionsXxx on PermissionSet)
    if sys_perm_diff.get("per_set_diffs") or sys_perm_diff.get("a_only_sets") or sys_perm_diff.get("b_only_sets"):
        w("\n### System Permissions (PermissionSet)")
        w()
        w(f"**Fields discovered:** {sys_perm_diff.get('fields_discovered', 0)}")
        w(f"**Permission sets compared:** {sys_perm_diff.get('shared_sets', 0)} shared, "
          f"{len(sys_perm_diff.get('a_only_sets', []))} {label_a}-only, "
          f"{len(sys_perm_diff.get('b_only_sets', []))} {label_b}-only")
        w()

        if sys_perm_diff.get("a_only_sets"):
            w(f"**{label_a}-only permission sets:** " + ", ".join(f"`{s}`" for s in sys_perm_diff["a_only_sets"]))
            w()
        if sys_perm_diff.get("b_only_sets"):
            w(f"**{label_b}-only permission sets:** " + ", ".join(f"`{s}`" for s in sys_perm_diff["b_only_sets"]))
            w()

        if sys_perm_diff.get("per_set_diffs"):
            w(f"**Permission differences by set ({len(sys_perm_diff['per_set_diffs'])} sets differ):**")
            w()
            for ps_diff in sys_perm_diff["per_set_diffs"]:
                kind = "Profile" if ps_diff.get("is_profile") else "PermSet"
                w(f"*{ps_diff['name']}* ({kind}):")
                if ps_diff["a_only"]:
                    shown = ps_diff["a_only"]
                    w(f"  {label_a}-only: " + ", ".join(f"`{p}`" for p in shown))
                if ps_diff["b_only"]:
                    shown = ps_diff["b_only"]
                    w(f"  {label_b}-only: " + ", ".join(f"`{p}`" for p in shown))
                w()

        if sys_perm_diff.get("a_unique_perms") or sys_perm_diff.get("b_unique_perms"):
            w(f"**Permissions used in only one org:**")
            w()
            if sys_perm_diff.get("a_unique_perms"):
                shown = sys_perm_diff["a_unique_perms"]
                w(f"  {label_a}-only ({len(sys_perm_diff['a_unique_perms'])}): " +
                  ", ".join(f"`{p}`" for p in shown))
            if sys_perm_diff.get("b_unique_perms"):
                shown = sys_perm_diff["b_unique_perms"]
                w(f"  {label_b}-only ({len(sys_perm_diff['b_unique_perms'])}): " +
                  ", ".join(f"`{p}`" for p in shown))
            w()

    # Org Values
    w("\n### Org Values & Limits")
    w()
    for cat_name in ["Identity", "Storage", "Feature Limits", "API", "Other"]:
        items = val_diff["cats"].get(cat_name, [])
        if not items:
            continue
        w(f"**{cat_name}** ({len(items)} differences):")
        w()
        w(f"| Setting | {label_a} | {label_b} |")
        w("|---------|-----|-----|")
        for d_item in items:
            w(f"| {d_item['name']} | {str(d_item['a'])} | {str(d_item['b'])} |")
        w()

    # Deep Data Diff
    if deep_diff:
        has_deep = any([
            deep_diff.get("apex_classes", {}).get("different", 0),
            deep_diff.get("apex_triggers", {}).get("different", 0),
            deep_diff.get("custom_fields", {}).get("objects_with_diffs", 0),
            deep_diff.get("validation_rules", {}).get("a_only") or deep_diff.get("validation_rules", {}).get("active_diffs"),
            deep_diff.get("flows", {}).get("different", 0),
            deep_diff.get("named_credentials", {}).get("endpoint_diffs"),
        ])
        if has_deep:
            w("\n### Deep Diff (Content-Level)")
            w()

            # Apex body diffs
            apex_d = deep_diff.get("apex_classes", {})
            if apex_d.get("different"):
                w(f"**Apex Classes:** {apex_d['shared']} shared, {apex_d['different']} with code differences")
                w()
                w(f"| Class | Difference |")
                w(f"|-------|-----------|")
                for d in apex_d["diffs"]:
                    parts = []
                    if d.get("body") == "different":
                        parts.append("body differs")
                    if d.get("apiVersion"):
                        parts.append(f"API {d['apiVersion']['a']}→{d['apiVersion']['b']}")
                    if d.get("loc"):
                        parts.append(f"LOC {d['loc']['a']}→{d['loc']['b']}")
                    w(f"| {d['name']} | {', '.join(parts)} |")
                w()

            # Trigger diffs
            trig_d = deep_diff.get("apex_triggers", {})
            if trig_d.get("different"):
                w(f"**Apex Triggers:** {trig_d['different']} with body differences")
                w()

            # Custom field diffs
            cf_d = deep_diff.get("custom_fields", {})
            if cf_d.get("objects_with_diffs"):
                w(f"**Custom Fields:** {cf_d['objects_compared']} objects compared, {cf_d['objects_with_diffs']} with differences")
                w()
                for obj_diff in cf_d["diffs"]:
                    w(f"*{obj_diff['object']}:*")
                    if obj_diff["a_only"]:
                        w(f"  {label_a}-only fields: " + ", ".join(f"`{f}`" for f in obj_diff["a_only"]))
                    if obj_diff["b_only"]:
                        w(f"  {label_b}-only fields: " + ", ".join(f"`{f}`" for f in obj_diff["b_only"]))
                    if obj_diff["type_diffs"]:
                        for td in obj_diff["type_diffs"]:
                            w(f"  `{td['field']}`: type {td['a_type']} → {td['b_type']}")
                    w()

            # Validation rule diffs
            vr_d = deep_diff.get("validation_rules", {})
            if vr_d.get("a_only") or vr_d.get("b_only") or vr_d.get("active_diffs"):
                w(f"**Validation Rules:**")
                if vr_d.get("a_only"):
                    w(f"  {label_a}-only: " + ", ".join(f"`{v}`" for v in vr_d["a_only"]))
                if vr_d.get("b_only"):
                    w(f"  {label_b}-only: " + ", ".join(f"`{v}`" for v in vr_d["b_only"]))
                if vr_d.get("active_diffs"):
                    for d in vr_d["active_diffs"]:
                        w(f"  `{d['name']}`: active {d['a_active']}→{d['b_active']}")
                w()

            # Flow diffs
            fl_d = deep_diff.get("flows", {})
            if fl_d.get("different"):
                w(f"**Flows:** {fl_d['shared']} shared, {fl_d['different']} with differences")
                w()

            # Named credential diffs
            nc_d = deep_diff.get("named_credentials", {})
            if nc_d.get("a_only") or nc_d.get("b_only") or nc_d.get("endpoint_diffs"):
                w(f"**Named Credentials:**")
                if nc_d.get("a_only"):
                    w(f"  {label_a}-only: " + ", ".join(nc_d["a_only"]))
                if nc_d.get("b_only"):
                    w(f"  {label_b}-only: " + ", ".join(nc_d["b_only"]))
                if nc_d.get("endpoint_diffs"):
                    for d in nc_d["endpoint_diffs"]:
                        w(f"  `{d['name']}`: {d['a_endpoint']} → {d['b_endpoint']}")
                w()

    # Notes
    # Licenses
    has_lic_diffs = any(
        lic_diff[lt]["a_only"] or lic_diff[lt]["b_only"] or lic_diff[lt]["diffs"]
        for lt in lic_diff
    )
    if has_lic_diffs:
        w("\n### Licenses")
        w()
        lic_labels = {"user": "User Licenses", "permission_set": "Permission Set Licenses", "package": "Package Licenses"}
        for ltype, label in lic_labels.items():
            ld = lic_diff[ltype]
            if not ld["a_only"] and not ld["b_only"] and not ld["diffs"]:
                continue
            w(f"**{label}:**")
            w()
            if ld["diffs"]:
                w(f"| License | {label_a} Total | {label_b} Total |")
                w("|---------|-----|-----|")
                for d in ld["diffs"]:
                    w(f"| {d['name']} | {d['a_total']} | {d['b_total']} |")
                w()
            if ld["a_only"]:
                names = [l.get("Name") or l.get("DeveloperName") or l.get("NamespacePrefix", "?") for l in ld["a_only"]]
                w(f"**{label_a}-only ({len(names)}):** " + ", ".join(names))
                w()
            if ld["b_only"]:
                names = [l.get("Name") or l.get("DeveloperName") or l.get("NamespacePrefix", "?") for l in ld["b_only"]]
                w(f"**{label_b}-only ({len(names)}):** " + ", ".join(names))
                w()

    w("---")
    w()
    w("## Notes")
    w()
    w("- **Namespaced (managed-package) components** are excluded from the summary table and listed separately under Package Components.")

    a_errors = a_data.get("errors", [])
    b_errors = b_data.get("errors", [])
    if a_errors or b_errors:
        w(f"- **Collection warnings:** {len(a_errors)} on {label_a}, {len(b_errors)} on {label_b}")

    w()
    w("*Report generated by dx-org-analyze. Read-only — no changes were made to either org.*")

    return "\n".join(lines)


# ── Data loader (split directory or single JSON) ────────────────────

def load_org_data(path):
    """Load org data from a split directory or a single JSON file.

    Split layout (directory with manifest.json):
      path/manifest.json        — lists category files
      path/identity.json        — org_id, org_name, org_edition, errors
      path/metadata.json        — metadata_types, metadata_components
      path/permissions.json     — permissions
      path/org_values.json      — org_values
      path/packages.json        — installed_packages
      path/licenses.json        — licenses
      path/system_permissions.json
      path/deep_data.json
      path/combined.json        — backward-compat single file

    Single file: a JSON file with all keys at the top level.
    """
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


# ── Main ─────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Compute diff between two Salesforce org data files.")
    parser.add_argument("--org-a", required=True, help="Path to org A data directory or JSON file (from collect_org_data.py)")
    parser.add_argument("--org-b", required=True, help="Path to org B data directory or JSON file (from collect_org_data.py)")
    parser.add_argument("--output", required=True, help="Output path prefix (writes .json and/or .md)")
    parser.add_argument("--format", choices=["markdown", "json", "both"], default="both",
                        help="Output format (default: both)")
    parser.add_argument("--org-a-label", default="Source", help="Display name for org A (source/reference)")
    parser.add_argument("--org-b-label", default="Target", help="Display name for org B (target to compare)")
    parser.add_argument("--show-shared", action="store_true",
                        help="Include shared components in the detailed breakdown")
    args = parser.parse_args()

    try:
        a_data = load_org_data(args.org_a)
        b_data = load_org_data(args.org_b)
    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Error: invalid JSON — {e}", file=sys.stderr)
        sys.exit(1)

    meta_stats = diff_metadata(a_data, b_data)
    perm_diff = diff_permissions(a_data, b_data)
    val_diff = diff_org_values(a_data, b_data)
    pkg_diff = diff_packages(a_data, b_data)
    lic_diff = diff_licenses(a_data, b_data)
    sys_perm_diff = diff_system_permissions(a_data, b_data)
    deep_diff = diff_deep_data(a_data, b_data)
    enrich_metadata_with_deep_diffs(meta_stats, deep_diff)
    pkg_components = diff_package_components(a_data, b_data)
    drift = compute_drift(meta_stats, perm_diff, a_data, b_data)

    result = {
        "metadata_stats": meta_stats,
        "permissions": perm_diff,
        "org_values": val_diff,
        "installed_packages": pkg_diff,
        "licenses": lic_diff,
        "system_permissions": sys_perm_diff,
        "package_components": pkg_components,
        "deep_data": deep_diff,
        "drift": drift,
    }

    if args.format in ("json", "both"):
        out_json = args.output + ".json"
        with open(out_json, "w") as f:
            json.dump(result, f, indent=2, default=str)
        print(f"Wrote {out_json}", file=sys.stderr)

    if args.format in ("markdown", "both"):
        md = render_markdown(a_data, b_data, meta_stats, perm_diff, val_diff, pkg_diff, lic_diff, sys_perm_diff, pkg_components, deep_diff, drift,
                             args.org_a_label, args.org_b_label, show_shared=args.show_shared)
        out_md = args.output + ".md"
        with open(out_md, "w") as f:
            f.write(md)
        print(f"Wrote {out_md}", file=sys.stderr)
        print(md)

    sys.exit(0)


if __name__ == "__main__":
    main()
