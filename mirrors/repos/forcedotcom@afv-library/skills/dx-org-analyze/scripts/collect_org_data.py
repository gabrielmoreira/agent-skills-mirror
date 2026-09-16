#!/usr/bin/env python3
"""Collect metadata, permissions, and org values from a single Salesforce org.

Outputs a JSON file that can be fed into compute_diff.py.

Data access hierarchy (strict priority order):
  1. SF CLI commands (sf org list metadata-types, sf data query, sf limits api display)
  2. Direct REST/Tooling API calls (last resort, only when SF CLI has no equivalent)

Authentication:
  All auth goes through SF CLI. The script obtains access tokens exclusively
  via `sf org display --json`. Never accepts raw credentials or tokens.

Usage:
  collect_org_data.py --org-alias ALIAS --output DIR
  collect_org_data.py --org-alias ALIAS --output DIR --skip-deep-data

Exit codes:
  0 = success
  1 = fatal error (bad args, network failure, sf CLI not available)
  2 = session expired (caller should re-authenticate and retry)
"""

import argparse
import hashlib
import json
import subprocess
import sys
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone

API_VERSION = "62.0"


def log(msg):
    print(msg, file=sys.stderr)


def run_sf_command(args_list):
    """Run an sf CLI command and return parsed JSON output."""
    cmd = ["sf"] + args_list + ["--json"]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
    except FileNotFoundError:
        log("Error: sf CLI not found. Install via: npm install -g @salesforce/cli")
        sys.exit(1)
    except subprocess.TimeoutExpired:
        log(f"Error: Command timed out: {' '.join(cmd)}")
        return None

    if result.returncode != 0:
        try:
            err = json.loads(result.stdout)
            msg = err.get("message", result.stderr[:200])
        except (json.JSONDecodeError, ValueError):
            msg = result.stderr[:200] or result.stdout[:200]
        session_markers = ["expired", "invalid_session_id", "invalid_grant",
                           "session expired", "expired access", "expired refresh"]
        if any(m in msg.lower() for m in session_markers):
            log(f"Session expired: {msg}")
            sys.exit(2)
        log(f"  sf command failed: {msg}")
        return None

    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError:
        log(f"  Could not parse sf output as JSON")
        return None


def rest_request(base_url, access_token, path):
    """Make a REST API request using the access token."""
    url = f"{base_url}{path}"
    req = urllib.request.Request(url, headers={"Authorization": f"Bearer {access_token}"})
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read())
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")
        if "INVALID_SESSION_ID" in body or "SESSION_EXPIRED" in body:
            log("Session expired.")
            sys.exit(2)
        return {"error": f"HTTP {e.code}: {body[:200]}"}
    except Exception as e:
        return {"error": str(e)}


def _query_all_pages(base_url, access_token, initial_path):
    """Follow nextRecordsUrl to collect all records (REST API returns max 2000 per page)."""
    all_records = []
    path = initial_path
    while True:
        r = rest_request(base_url, access_token, path)
        if not isinstance(r, dict) or "error" in r:
            if not all_records:
                return r
            log(f"  Warning: pagination interrupted after {len(all_records)} records")
            return {"records": all_records, "totalSize": len(all_records), "done": False}
        all_records.extend(r.get("records", []))
        if r.get("done", True) or not r.get("nextRecordsUrl"):
            break
        path = r["nextRecordsUrl"]
    return {"records": all_records, "totalSize": len(all_records), "done": True}


def tooling_query(base_url, access_token, soql):
    """Run a Tooling API SOQL query with automatic pagination."""
    path = f"/services/data/v{API_VERSION}/tooling/query/?q={urllib.parse.quote(soql)}"
    return _query_all_pages(base_url, access_token, path)


def rest_query(base_url, access_token, soql):
    """Run a standard REST API SOQL query with automatic pagination."""
    path = f"/services/data/v{API_VERSION}/query/?q={urllib.parse.quote(soql)}"
    return _query_all_pages(base_url, access_token, path)


# ── Step: Get credentials from SF CLI ────────────────────────────────

def get_credentials(org_alias):
    """Get base URL and access token from sf CLI."""
    log(f"Getting credentials for org: {org_alias}")
    result = run_sf_command(["org", "display", "--target-org", org_alias])
    if not result:
        log(f"Error: Could not get credentials for {org_alias}")
        sys.exit(1)

    data = result.get("result", {})
    base_url = data.get("instanceUrl", "").rstrip("/")
    access_token = data.get("accessToken", "")

    if not base_url or not access_token:
        log(f"Error: Missing instanceUrl or accessToken for {org_alias}")
        sys.exit(1)

    log(f"  Instance: {base_url}")
    return base_url, access_token


# ── Step: Discover metadata types via SF CLI ─────────────────────────

def discover_metadata_types_cli(org_alias):
    """Discover metadata types using sf org list metadata-types."""
    log("Discovering metadata types via sf CLI ...")
    result = run_sf_command(["org", "list", "metadata-types", "--target-org", org_alias,
                            "--api-version", API_VERSION])
    if not result:
        log("  sf org list metadata-types failed, will use Tooling API fallback.")
        return None

    metadata_objects = result.get("result", {}).get("metadataObjects", [])
    types = sorted(set(obj.get("xmlName", "") for obj in metadata_objects if obj.get("xmlName")))
    log(f"  Discovered {len(types)} metadata types.")
    return types


# ── Step: Collect metadata components via SF CLI ─────────────────────

def collect_metadata_cli(org_alias, all_types):
    """Collect metadata components using sf org list metadata per type (parallelized)."""
    log(f"Collecting metadata via sf CLI ({len(all_types)} types) ...")
    results = {}
    errors = []

    def fetch_type(mtype):
        r = run_sf_command(["org", "list", "metadata", "--target-org", org_alias,
                           "--metadata-type", mtype, "--api-version", API_VERSION])
        return mtype, r

    completed = 0
    with ThreadPoolExecutor(max_workers=12) as pool:
        futures = {pool.submit(fetch_type, t): t for t in all_types}
        for future in as_completed(futures):
            mtype, r = future.result()
            completed += 1

            if r is None:
                errors.append(f"list metadata failed for {mtype}")
                continue

            components = r.get("result", [])
            if components:
                entries = []
                for c in components:
                    full_name = urllib.parse.unquote(c.get("fullName", ""))
                    namespace = c.get("namespacePrefix") or None
                    if full_name:
                        entries.append({"fullName": full_name, "namespace": namespace})
                if entries:
                    results[mtype] = entries

            if completed % 30 == 0:
                log(f"  ... {completed}/{len(all_types)} types")

    log(f"  {len(results)} types with components, {len(errors)} errors.")
    return results, errors


# ── Step: Collect metadata via Tooling API (fallback) ────────────────

def collect_metadata_tooling(base_url, access_token):
    """Fallback: collect metadata via Tooling API SOQL queries."""
    log("Collecting metadata via Tooling API fallback ...")
    queries = {
        "ApexClass":       "SELECT Name, ApiVersion, LengthWithoutComments, Status FROM ApexClass WHERE NamespacePrefix = null",
        "ApexTrigger":     "SELECT Name, ApiVersion, Status FROM ApexTrigger WHERE NamespacePrefix = null",
        "ApexPage":        "SELECT Name, ApiVersion FROM ApexPage WHERE NamespacePrefix = null",
        "ApexComponent":   "SELECT Name, ApiVersion FROM ApexComponent WHERE NamespacePrefix = null",
        "CustomObject":    "SELECT DeveloperName FROM CustomObject WHERE NamespacePrefix = null",
        "CustomTab":       "SELECT DeveloperName FROM CustomTab WHERE NamespacePrefix = null",
        "CustomApplication": "SELECT DeveloperName, Label FROM CustomApplication WHERE NamespacePrefix = null",
        "CustomLabel":     "SELECT Name, Value FROM ExternalString WHERE NamespacePrefix = null",
        "LightningComponentBundle": "SELECT DeveloperName, ApiVersion FROM LightningComponentBundle WHERE NamespacePrefix = null",
        "AuraDefinitionBundle": "SELECT DeveloperName, ApiVersion FROM AuraDefinitionBundle WHERE NamespacePrefix = null",
        "Flow":            "SELECT MasterLabel, ProcessType, Status FROM Flow",
        "ValidationRule":  "SELECT ValidationName FROM ValidationRule WHERE NamespacePrefix = null",
        "Layout":          "SELECT Name FROM Layout WHERE NamespacePrefix = null",
        "Profile":         "SELECT Name FROM Profile",
        "PermissionSet":   "SELECT Name FROM PermissionSet WHERE IsOwnedByProfile = false AND NamespacePrefix = null",
        "ConnectedApplication": "SELECT DeveloperName FROM ConnectedApplication",
        "StaticResource":  "SELECT Name FROM StaticResource WHERE NamespacePrefix = null",
        "FlexiPage":       "SELECT DeveloperName FROM FlexiPage WHERE NamespacePrefix = null",
        "QuickAction":     "SELECT DeveloperName FROM QuickActionDefinition WHERE NamespacePrefix = null",
        "CustomPermission": "SELECT DeveloperName FROM CustomPermission",
        "PermissionSetGroup": "SELECT DeveloperName FROM PermissionSetGroup WHERE NamespacePrefix = null",
        "NamedCredential": "SELECT DeveloperName FROM NamedCredential WHERE NamespacePrefix = null",
        "DuplicateRule":   "SELECT DeveloperName FROM DuplicateRule WHERE NamespacePrefix = null",
        "MatchingRule":    "SELECT DeveloperName FROM MatchingRule WHERE NamespacePrefix = null",
        "EmailTemplate":   "SELECT DeveloperName FROM EmailTemplate WHERE NamespacePrefix = null",
        "Report":          "SELECT DeveloperName FROM Report WHERE NamespacePrefix = null",
        "Dashboard":       "SELECT DeveloperName FROM Dashboard WHERE NamespacePrefix = null",
    }

    results = {}
    errors = []
    for label, soql in queries.items():
        r = tooling_query(base_url, access_token, soql)
        if not isinstance(r, dict):
            errors.append(f"Tooling query failed for {label}: unexpected response")
            continue
        if "error" in r:
            errors.append(f"Tooling query failed for {label}: {str(r['error'])[:80]}")
            continue
        records = r.get("records", [])
        names = []
        for rec in records:
            name = (rec.get("Name") or rec.get("DeveloperName") or
                    rec.get("MasterLabel") or rec.get("ValidationName") or "")
            if name:
                names.append({"fullName": name, "namespace": None})
        if names:
            results[label] = names

    log(f"  {len(results)} types with components, {len(errors)} errors.")
    return results, errors


# ── Step: Collect org settings ────────────────────────────────────────

def sf_data_query(org_alias, soql, use_tooling=False):
    """Run a SOQL query via SF CLI (sf data query). Preferred over direct API.

    Returns the result dict with 'records'. If the query is truncated (done=false),
    returns None so callers fall through to the paginating REST query.
    """
    args = ["data", "query", "--query", soql, "--target-org", org_alias,
            "--result-format", "json"]
    if use_tooling:
        args.append("--use-tooling-api")
    result = run_sf_command(args)
    if result and "result" in result:
        r = result["result"]
        if isinstance(r, dict) and r.get("done") is False:
            return None
        return r
    return result


def collect_org_settings(org_alias, base_url, access_token):
    """Collect org settings. Prefers SF CLI, falls back to direct API.

    Tries multiple sources in order:
    1. SF CLI: sf data query --use-tooling-api (OrganizationSettingsDetail)
    2. SF CLI: sf data query --use-tooling-api (SecurityHealthCheckRisks)
    3. Direct Tooling API (last resort if SF CLI query fails)
    """
    log("Collecting org settings via SF CLI ...")
    permissions = {}

    # Try OrganizationSettingsDetail via SF CLI first
    soql = "SELECT DurableId, SettingName, IsEnabled FROM OrganizationSettingsDetail"
    r = sf_data_query(org_alias, soql, use_tooling=True)

    if isinstance(r, dict) and "records" in r:
        for rec in r.get("records", []):
            name = rec.get("SettingName", "")
            enabled = rec.get("IsEnabled", False)
            if name:
                permissions[name] = {"value": str(enabled).lower()}
        log(f"  {len(permissions)} org settings collected via SF CLI (OrganizationSettingsDetail).")
        return permissions

    log("  SF CLI OrganizationSettingsDetail query failed, trying SecurityHealthCheckRisks ...")

    # Fallback: SecurityHealthCheckRisks via SF CLI
    soql_shcr = ("SELECT DurableId, Setting, SettingGroup, OrgValue, StandardValue "
                 "FROM SecurityHealthCheckRisks")
    r2 = sf_data_query(org_alias, soql_shcr, use_tooling=True)

    if isinstance(r2, dict) and "records" in r2:
        for rec in r2.get("records", []):
            durable_id = rec.get("DurableId", "")
            org_value = rec.get("OrgValue", "")
            if durable_id:
                permissions[durable_id] = {"value": org_value}
        log(f"  {len(permissions)} org settings collected via SF CLI (SecurityHealthCheckRisks).")
        return permissions

    # Last resort: direct Tooling API
    log("  SF CLI queries failed, falling back to direct Tooling API ...")
    soql = "SELECT DurableId, SettingName, IsEnabled FROM OrganizationSettingsDetail"
    r3 = tooling_query(base_url, access_token, soql)

    if isinstance(r3, dict) and "records" in r3:
        for rec in r3.get("records", []):
            name = rec.get("SettingName", "")
            enabled = rec.get("IsEnabled", False)
            if name:
                permissions[name] = {"value": str(enabled).lower()}
        log(f"  {len(permissions)} org settings collected via direct Tooling API (fallback).")
        return permissions

    log("  All org settings sources unavailable. Skipping.")
    return permissions


# ── Step: Collect org limits ──────────────────────────────────────────

def collect_org_limits(org_alias, base_url, access_token):
    """Collect org limits. Prefers SF CLI, falls back to direct REST API."""
    log("Collecting org limits via SF CLI ...")
    org_values = {}

    # Prefer SF CLI: sf limits api display
    result = run_sf_command(["limits", "api", "display", "--target-org", org_alias])
    if result and "result" in result:
        for limit in result["result"]:
            name = limit.get("name", "")
            max_val = limit.get("max", 0)
            if name:
                org_values[name] = str(max_val)
        if org_values:
            log(f"  {len(org_values)} org limits collected via SF CLI.")
            return org_values

    # Fallback: direct REST /limits/ endpoint
    log("  SF CLI limits command failed, falling back to REST /limits/ ...")
    path = f"/services/data/v{API_VERSION}/limits/"
    r = rest_request(base_url, access_token, path)

    if isinstance(r, dict) and "error" not in r:
        for limit_name, limit_data in r.items():
            if isinstance(limit_data, dict):
                max_val = limit_data.get("Max", 0)
                org_values[limit_name] = str(max_val)
            else:
                org_values[limit_name] = str(limit_data)
        log(f"  {len(org_values)} org limits collected via REST API (fallback).")
    else:
        err = r.get("error", "unknown") if isinstance(r, dict) else str(r)[:100]
        log(f"  REST /limits/ also unavailable: {err}")

    return org_values


# ── Step: Org identity ───────────────────────────────────────────────

def query_org_identity(org_alias, base_url, access_token):
    """Query org identity. Prefers SF CLI, falls back to direct API."""
    soql = ("SELECT Id, Name, OrganizationType, IsSandbox, TrialExpirationDate, "
            "LanguageLocaleKey, DefaultLocaleSidKey, TimeZoneSidKey FROM Organization")

    # Prefer SF CLI
    r = sf_data_query(org_alias, soql)
    if isinstance(r, dict) and "records" in r and r["records"]:
        return r["records"][0]

    # Fallback: direct REST API
    r = rest_query(base_url, access_token, soql)
    if isinstance(r, dict) and "records" in r and r["records"]:
        return r["records"][0]

    return {}


# ── Step: Installed packages ─────────────────────────────────────────

def collect_installed_packages(org_alias, base_url, access_token):
    """Collect installed packages. Prefers SF CLI, falls back to direct Tooling API."""
    log("Collecting installed packages via SF CLI ...")
    soql = ("SELECT SubscriberPackage.Name, SubscriberPackage.NamespacePrefix, "
            "SubscriberPackageVersion.MajorVersion, SubscriberPackageVersion.MinorVersion "
            "FROM InstalledSubscriberPackage")

    # Prefer SF CLI with Tooling API
    r = sf_data_query(org_alias, soql, use_tooling=True)

    # Fallback: direct Tooling API
    if not isinstance(r, dict) or "records" not in r:
        log("  SF CLI package query failed, falling back to direct Tooling API ...")
        r = tooling_query(base_url, access_token, soql)

    if not isinstance(r, dict) or "error" in r:
        err = r.get("error", "unknown") if isinstance(r, dict) else str(r)
        log(f"  Could not query packages: {err}")
        return []

    packages = []
    for rec in r.get("records", []):
        sp = rec.get("SubscriberPackage") or {}
        sv = rec.get("SubscriberPackageVersion") or {}
        packages.append({
            "name": sp.get("Name", ""),
            "namespace": sp.get("NamespacePrefix", ""),
            "version": f"{sv.get('MajorVersion', '?')}.{sv.get('MinorVersion', '?')}",
        })

    log(f"  {len(packages)} installed packages.")
    return packages


def collect_installed_components(org_alias, base_url, access_token):
    """Identify components installed by packages via ManageableState.

    Non-namespaced (2GP unlocked) packages have no namespace prefix, so
    their components are invisible to the namespace-based grouping in the
    diff report.  Querying ManageableState is the only reliable signal.
    """
    log("Collecting installed components (ManageableState) ...")
    ns_filter = "AND NamespacePrefix = null"
    queries = {
        "CustomObject": f"SELECT DeveloperName, ManageableState FROM CustomObject WHERE ManageableState IN ('installed', 'installedEditable') {ns_filter}",
        "CustomField": f"SELECT DeveloperName, EntityDefinition.DeveloperName, ManageableState FROM CustomField WHERE ManageableState IN ('installed', 'installedEditable') {ns_filter}",
        "ApexClass": f"SELECT Name, ManageableState FROM ApexClass WHERE ManageableState IN ('installed', 'installedEditable') {ns_filter}",
        "ApexTrigger": f"SELECT Name, ManageableState FROM ApexTrigger WHERE ManageableState IN ('installed', 'installedEditable') {ns_filter}",
        "ApexPage": f"SELECT Name, ManageableState FROM ApexPage WHERE ManageableState IN ('installed', 'installedEditable') {ns_filter}",
        "ApexComponent": f"SELECT Name, ManageableState FROM ApexComponent WHERE ManageableState IN ('installed', 'installedEditable') {ns_filter}",
        "Flow": f"SELECT MasterLabel, ManageableState FROM Flow WHERE ManageableState IN ('installed', 'installedEditable') {ns_filter}",
        "Layout": f"SELECT Name, ManageableState FROM Layout WHERE ManageableState IN ('installed', 'installedEditable') {ns_filter}",
        "ValidationRule": f"SELECT ValidationName, ManageableState FROM ValidationRule WHERE ManageableState IN ('installed', 'installedEditable') {ns_filter}",
    }

    installed = {}
    for mtype, soql in queries.items():
        r = sf_data_query(org_alias, soql, use_tooling=True)
        if not isinstance(r, dict) or "records" not in r:
            r = tooling_query(base_url, access_token, soql)
        if not isinstance(r, dict) or "error" in r or "records" not in r:
            continue
        items = []
        for rec in r.get("records", []):
            name = (rec.get("Name") or rec.get("DeveloperName")
                    or rec.get("MasterLabel") or rec.get("ValidationName") or "")
            if not name:
                continue
            entity = (rec.get("EntityDefinition") or {}).get("DeveloperName")
            entry = {"name": name, "manageableState": rec.get("ManageableState", "")}
            if entity:
                entry["object"] = entity
            items.append(entry)
        if items:
            installed[mtype] = items
            log(f"  {mtype}: {len(items)} installed components")

    total = sum(len(v) for v in installed.values())
    log(f"  {total} total installed components.")
    return installed


# ── Step: Licenses ───────────────────────────────────────────────────

def collect_licenses(org_alias, base_url, access_token):
    """Collect licenses. Prefers SF CLI, falls back to direct API."""
    log("Collecting licenses via SF CLI ...")
    licenses = {"user": [], "permission_set": [], "package": []}

    queries = {
        "user": "SELECT Name, TotalLicenses, UsedLicenses, Status FROM UserLicense",
        "permission_set": "SELECT DeveloperName, TotalLicenses, UsedLicenses FROM PermissionSetLicense",
        "package": "SELECT NamespacePrefix, AllowedLicenses, UsedLicenses, Status FROM PackageLicense",
    }

    for key, soql in queries.items():
        # Prefer SF CLI
        r = sf_data_query(org_alias, soql)
        # Fallback: direct REST API (these are standard objects, not Tooling)
        if not isinstance(r, dict) or "records" not in r:
            r = rest_query(base_url, access_token, soql)
        if isinstance(r, dict) and "records" in r:
            for rec in r["records"]:
                rec.pop("attributes", None)
                licenses[key].append(rec)

    log(f"  {len(licenses['user'])} user, {len(licenses['permission_set'])} permission set, {len(licenses['package'])} package licenses.")
    return licenses


# ── Step: System permissions (PermissionsXxx on PermissionSet) ────────

def collect_system_permissions(org_alias, base_url, access_token):
    """Collect system permissions (PermissionsXxx fields) from PermissionSet.

    Steps:
    1. Describe PermissionSet to discover all Permissions* boolean fields
    2. Query PermissionSet records with those fields
    """
    log("Collecting system permissions ...")

    # Step 1: Discover PermissionsXxx fields via describe
    perm_fields = _discover_permission_fields(org_alias, base_url, access_token)
    if not perm_fields:
        log("  Could not discover PermissionsXxx fields. Skipping system permissions.")
        return {"fields_discovered": [], "permission_sets": []}

    log(f"  Discovered {len(perm_fields)} PermissionsXxx fields.")

    # Step 2: Query PermissionSet records with those fields
    # PermissionsXxx names average ~25 chars; 150 fields ≈ 3750 chars, well under SOQL limits
    chunk_size = 150
    base_fields = ["Id", "Name", "Label", "IsOwnedByProfile", "IsCustom"]
    all_records = {}

    for i in range(0, len(perm_fields), chunk_size):
        chunk = perm_fields[i:i + chunk_size]
        fields_csv = ", ".join(base_fields + chunk) if i == 0 else ", ".join(["Id"] + chunk)
        soql = f"SELECT {fields_csv} FROM PermissionSet WHERE IsCustom = true OR IsOwnedByProfile = true"

        r = sf_data_query(org_alias, soql, use_tooling=True)
        if not isinstance(r, dict) or "records" not in r:
            r = tooling_query(base_url, access_token, soql)
        if not isinstance(r, dict) or "records" not in r:
            log(f"  System permissions query failed for chunk {i // chunk_size + 1}.")
            continue

        for rec in r.get("records", []):
            rec_id = rec.get("Id", "")
            if rec_id not in all_records:
                all_records[rec_id] = {}
            for field in (base_fields + chunk if i == 0 else ["Id"] + chunk):
                if field in rec:
                    all_records[rec_id][field] = rec[field]

    # Build output — skip auto-generated sets with ID-based names
    permission_sets = []
    for rec_id, rec in all_records.items():
        name = rec.get("Name", "")
        label = rec.get("Label", "")
        display = label or name
        if not display:
            continue
        if display.startswith(("X00e", "00e", "X00E", "00E")):
            continue
        if name.startswith("X00e") or name.startswith("00e"):
            continue
        perms = {}
        for f in perm_fields:
            val = rec.get(f)
            if val is True:
                perms[f] = True
        permission_sets.append({
            "name": name,
            "label": label or name,
            "is_profile": rec.get("IsOwnedByProfile", False),
            "permissions": perms,
        })

    log(f"  {len(permission_sets)} permission sets collected with system permissions.")
    return {"fields_discovered": perm_fields, "permission_sets": permission_sets}


def _discover_permission_fields(org_alias, base_url, access_token):
    """Discover PermissionsXxx fields by describing the PermissionSet object."""
    # Try SF CLI describe first
    try:
        result = subprocess.run(
            ["sf", "sobject", "describe", "--sobject", "PermissionSet",
             "--target-org", org_alias, "--json"],
            capture_output=True, text=True, timeout=60
        )
        if result.returncode == 0:
            data = json.loads(result.stdout)
            fields = data.get("result", {}).get("fields", [])
            return sorted(
                f["name"] for f in fields
                if f["name"].startswith("Permissions") and f.get("type") == "boolean"
            )
    except (FileNotFoundError, subprocess.TimeoutExpired, json.JSONDecodeError, KeyError):
        pass

    # Fallback: REST describe
    path = f"/services/data/v{API_VERSION}/sobjects/PermissionSet/describe/"
    r = rest_request(base_url, access_token, path)
    if isinstance(r, dict) and "fields" in r:
        return sorted(
            f["name"] for f in r["fields"]
            if f["name"].startswith("Permissions") and f.get("type") == "boolean"
        )

    return []


# ── Step: Deep data (Tooling API content-level queries) ──────────────

def collect_deep_data(org_alias, base_url, access_token):
    """Collect deep data. Prefers SF CLI, falls back to direct Tooling API."""
    log("Collecting deep data ...")
    deep = {}
    errors = []

    queries = {
        "apex_classes": (
            "SELECT Name, ApiVersion, LengthWithoutComments, Status, Body FROM ApexClass WHERE NamespacePrefix = null",
            lambda r: {"name": r.get("Name", ""), "apiVersion": r.get("ApiVersion"),
                       "loc": r.get("LengthWithoutComments", 0), "status": r.get("Status"),
                       "bodyHash": hashlib.sha256(r.get("Body", "").encode()).hexdigest() if r.get("Body") else None}
        ),
        "apex_triggers": (
            "SELECT Name, ApiVersion, Status, Body FROM ApexTrigger WHERE NamespacePrefix = null",
            lambda r: {"name": r.get("Name", ""), "apiVersion": r.get("ApiVersion"),
                       "status": r.get("Status"),
                       "bodyHash": hashlib.sha256(r.get("Body", "").encode()).hexdigest() if r.get("Body") else None}
        ),
        "custom_fields": (
            "SELECT TableEnumOrId, DeveloperName, Length, Precision, Scale FROM CustomField WHERE NamespacePrefix = null",
            lambda r: {"object": r.get("TableEnumOrId", ""), "name": r.get("DeveloperName", ""),
                       "length": r.get("Length"),
                       "precision": r.get("Precision"), "scale": r.get("Scale")}
        ),
        "validation_rules": (
            "SELECT ValidationName, EntityDefinition.DeveloperName, Active, ErrorMessage FROM ValidationRule WHERE NamespacePrefix = null",
            lambda r: {"name": r.get("ValidationName", ""),
                       "object": (r.get("EntityDefinition") or {}).get("DeveloperName", ""),
                       "active": r.get("Active", False),
                       "errorMessage": r.get("ErrorMessage", "")}
        ),
        "flows": (
            "SELECT MasterLabel, ApiVersion, ProcessType, Status FROM Flow",
            lambda r: {"name": r.get("MasterLabel", ""),
                       "apiVersion": r.get("ApiVersion"),
                       "processType": r.get("ProcessType", ""),
                       "status": r.get("Status", "")}
        ),
        "named_credentials": (
            "SELECT DeveloperName, Endpoint FROM NamedCredential WHERE NamespacePrefix = null",
            lambda r: {"name": r.get("DeveloperName", ""), "endpoint": r.get("Endpoint", "")}
        ),
        "connected_apps": (
            "SELECT DeveloperName FROM ConnectedApplication",
            lambda r: {"name": r.get("DeveloperName", "")}
        ),
        "custom_metadata_records": (
            "SELECT DeveloperName, NamespacePrefix FROM CustomObject WHERE DeveloperName LIKE '%mdt'",
            lambda r: {"name": r.get("DeveloperName", ""), "namespace": r.get("NamespacePrefix", "")}
        ),
    }

    def fetch_deep(key, soql, transform):
        r = sf_data_query(org_alias, soql, use_tooling=True)
        if not isinstance(r, dict) or "records" not in r:
            r = tooling_query(base_url, access_token, soql)
        if not isinstance(r, dict) or "error" in r:
            err_msg = r.get("error", "unknown") if isinstance(r, dict) else str(r)[:80]
            return key, [], f"Deep data query failed for {key}: {err_msg}"
        records = r.get("records", [])
        try:
            data = [transform(rec) for rec in records]
        except Exception as e:
            return key, [], f"Deep data transform failed for {key}: {e}"
        return key, data, None

    with ThreadPoolExecutor(max_workers=8) as pool:
        futures = {pool.submit(fetch_deep, k, soql, tr): k for k, (soql, tr) in queries.items()}
        for future in as_completed(futures):
            key, data, err = future.result()
            if err:
                errors.append(err)
                deep[key] = []
            else:
                deep[key] = data
                if data:
                    log(f"  {key}: {len(data)} records")

    log(f"  Deep data: {sum(len(v) for v in deep.values())} total records, {len(errors)} errors")
    return deep, errors


# ── Main ─────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Collect Salesforce org data for comparison.")
    parser.add_argument("--org-alias", required=True,
                        help="SF CLI alias or username for the target org")
    parser.add_argument("--output", required=True, help="Output directory (split category files + combined.json)")
    parser.add_argument("--skip-deep-data", action="store_true",
                        help="Skip Tooling API body queries (faster, less detail)")
    args = parser.parse_args()

    errors = []

    # Get credentials from SF CLI
    base_url, access_token = get_credentials(args.org_alias)

    # Org identity (SF CLI first, then direct API fallback)
    identity = query_org_identity(args.org_alias, base_url, access_token)
    org_id = identity.get("Id", "unknown")
    log(f"Org: {identity.get('Name', '?')} ({identity.get('OrganizationType', '?')}) — {org_id}")

    # Metadata types + components (SF CLI first, Tooling API fallback)
    types = discover_metadata_types_cli(args.org_alias)
    if types:
        components, meta_errors = collect_metadata_cli(args.org_alias, types)
        errors.extend(meta_errors)
    else:
        types = []
        components, meta_errors = collect_metadata_tooling(base_url, access_token)
        errors.extend(meta_errors)

    # Org settings (SF CLI first, direct Tooling API fallback)
    permissions = collect_org_settings(args.org_alias, base_url, access_token)

    # Org limits (SF CLI first, REST /limits/ fallback)
    org_values = collect_org_limits(args.org_alias, base_url, access_token)

    # Installed packages (SF CLI first, direct Tooling API fallback)
    packages = collect_installed_packages(args.org_alias, base_url, access_token)

    # Installed components (ManageableState query for non-namespaced packages)
    installed_components = collect_installed_components(args.org_alias, base_url, access_token)

    # Licenses (SF CLI first, direct API fallback)
    licenses = collect_licenses(args.org_alias, base_url, access_token)

    # System permissions (PermissionsXxx on PermissionSet)
    system_permissions = collect_system_permissions(args.org_alias, base_url, access_token)

    # Deep data (SF CLI first, direct Tooling API fallback)
    deep_data = {}
    if not args.skip_deep_data:
        deep_data, deep_errors = collect_deep_data(args.org_alias, base_url, access_token)
        errors.extend(deep_errors)

    # Assemble output — split into category files for parallel agent access
    collected_at = datetime.now(timezone.utc).isoformat()
    identity_data = {
        "org_id": org_id,
        "org_name": identity.get("Name", "unknown"),
        "org_edition": identity.get("OrganizationType", "unknown"),
        "base_url": base_url,
        "collected_at": collected_at,
        "api_version": API_VERSION,
        "errors": errors,
    }

    categories = {
        "identity":           identity_data,
        "metadata":           {"metadata_types": types, "metadata_components": components},
        "permissions":        {"permissions": permissions},
        "org_values":         {"org_values": org_values},
        "packages":           {"installed_packages": packages, "installed_components": installed_components},
        "licenses":           {"licenses": licenses},
        "system_permissions": {"system_permissions": system_permissions},
        "deep_data":          {"deep_data": deep_data},
    }

    import os
    out_dir = args.output
    os.makedirs(out_dir, exist_ok=True)

    manifest = {"format": "split", "collected_at": collected_at, "files": {}}
    for cat, data in categories.items():
        fname = f"{cat}.json"
        fpath = os.path.join(out_dir, fname)
        with open(fpath, "w") as f:
            json.dump(data, f, indent=2, default=str)
        manifest["files"][cat] = fname

    with open(os.path.join(out_dir, "manifest.json"), "w") as f:
        json.dump(manifest, f, indent=2)

    # Also write combined file for backward compatibility
    combined = dict(identity_data)
    combined["metadata_types"] = types
    combined["metadata_components"] = components
    combined["permissions"] = permissions
    combined["org_values"] = org_values
    combined["installed_packages"] = packages
    combined["installed_components"] = installed_components
    combined["licenses"] = licenses
    combined["system_permissions"] = system_permissions
    combined["deep_data"] = deep_data
    with open(os.path.join(out_dir, "combined.json"), "w") as f:
        json.dump(combined, f, indent=2, default=str)

    log(f"\nWrote {out_dir}/")
    log(f"  Files: {', '.join(sorted(manifest['files'].keys()))}, combined.json")
    log(f"  Metadata types: {len(types)} discovered, {len(components)} with components")
    log(f"  Org settings: {len(permissions)}")
    log(f"  Org limits: {len(org_values)}")
    log(f"  Installed packages: {len(packages)}")
    log(f"  Installed components: {sum(len(v) for v in installed_components.values())}")
    log(f"  Licenses: {sum(len(v) for v in licenses.values())}")
    log(f"  System permissions: {len(system_permissions.get('permission_sets', []))} permission sets, "
        f"{len(system_permissions.get('fields_discovered', []))} fields")
    if errors:
        log(f"  Warnings: {len(errors)}")
    sys.exit(0)


if __name__ == "__main__":
    main()
