#!/usr/bin/env python3
"""Claude-Guardian diagnostic preview. Python stdlib; no network or mutation executor.

This compact contract is reconstructed from ENV-SPEC v0.3 sections 18–20;
it is not the missing historical ENV01_ENV02_Contracts_v0.2.zip.
"""
import argparse
from datetime import datetime, timezone
import ipaddress
import json
import os
import ntpath
from pathlib import Path
import re

try:
    from traffic_policy import policy_projection
except ModuleNotFoundError as _policy_import_error:
    if _policy_import_error.name != 'traffic_policy':
        raise
    # Preserve the existing standalone file-path import API without changing
    # sys.path or depending on another test/module having imported siblings.
    import importlib.util as _policy_importlib
    import sys as _policy_sys
    from pathlib import Path as _PolicyPath
    _policy_spec = _policy_importlib.spec_from_file_location(
        '_guardian_traffic_policy', _PolicyPath(__file__).with_name('traffic_policy.py'))
    _policy_module = _policy_importlib.module_from_spec(_policy_spec)
    _policy_sys.modules[_policy_spec.name] = _policy_module
    _policy_spec.loader.exec_module(_policy_module)
    policy_projection = _policy_module.policy_projection
import stat
import sys
import time

try:
    import environment_entry
except ModuleNotFoundError as _entry_import_error:
    if _entry_import_error.name != 'environment_entry':
        raise
    # Keep the standalone file-path import API without changing sys.path.
    import importlib.util as _entry_importlib
    _entry_spec = _entry_importlib.spec_from_file_location(
        '_guardian_environment_entry', Path(__file__).with_name('environment_entry.py'))
    environment_entry = _entry_importlib.module_from_spec(_entry_spec)
    _entry_spec.loader.exec_module(environment_entry)

VERSION = "0.2.0-foundations"
INPUT_SCHEMA = "guardian-offline/0.1"
STATES = {"observed", "reported", "derived", "unknown", "blocked", "not_applicable", "not_found_in_scope", "conflict", "stale"}
FACT_IDS = {"H%02d" % n for n in range(1, 8)} | {"S%02d" % n for n in range(1, 17)} | {"P%02d" % n for n in range(1, 25)}
MAX_BYTES = 262144
MAX_AGE = 86400
ALIAS = re.compile(r"[A-Za-z][A-Za-z0-9_-]{0,47}\Z")
SECRET = re.compile(r"(?i)(?:bearer\s+\S+|(?:sk-|ghp_|github_pat_)[A-Za-z0-9_-]+|(?:password|secret|token|api[_-]?key|authorization)\s*[:=]\s*\S+)")
# Known credential shapes are screened before report assembly. Language and
# locale fields use their producer grammar for sk- forms: Slovak tags such as
# sk-Latn-SK-fonipa overlap the generic token pattern. This is not a universal
# secret detector; ambiguous strings cannot gain authenticity from a format.
CREDENTIAL_TEXT = (
    r"(?:(?<![A-Za-z0-9])(?:ghp_|github_pat_)[A-Za-z0-9_-]{12,}|bearer\s+\S+"
    r"|(?:password|secret|token|api[_-]?key|authorization)\s*[:=]\s*\S+)")
KNOWN_CREDENTIAL_VALUE = re.compile(r"(?i)(?:(?<![A-Za-z0-9])sk-(?:ant-)?[A-Za-z0-9_-]{12,}|" + CREDENTIAL_TEXT + r")")
KNOWN_CREDENTIAL_LANGUAGE = re.compile(r"(?i)" + CREDENTIAL_TEXT)
MODULES = ["ENV-%02d" % n for n in range(1, 11)]


class GuardianError(Exception):
    def __init__(self, code, exit_code=2):
        self.code, self.exit_code = code, exit_code


def now():
    return datetime.now(timezone.utc).isoformat()


def alias(value):
    if (not isinstance(value, str) or not ALIAS.fullmatch(value)
            or KNOWN_CREDENTIAL_VALUE.search(value)):
        raise GuardianError("INPUT_OR_RESPONSE_INVALID")
    return value


def redact(value):
    """Defense in depth. Raw configuration, credentials and addresses are never needed."""
    if isinstance(value, dict):
        # Rebuild only the exact fixed product-policy object. Its authorization
        # is the literal "none", not a credential or caller approval. Any extra
        # member, different type or different value retains normal redaction.
        fixed_policy = policy_projection()
        if (type(value) is dict and set(value) == set(fixed_policy)
                and all(type(value[k]) is type(v) and value[k] == v
                        for k, v in fixed_policy.items())):
            return fixed_policy
        return {k: ("[redacted]" if re.search(r"(?i)password|secret|token|authorization|cookie|credential|api.?key", k) else redact(v)) for k, v in value.items()}
    if isinstance(value, list):
        return [redact(v) for v in value]
    if not isinstance(value, str):
        return value
    value = SECRET.sub("[redacted]", value)
    value = re.sub(r"https?://\S+", "[url-redacted]", value)
    value = re.sub(r"(?:[A-Za-z]:[\\/]|/Users/|/home/|/private/|\\\\)[^\r\n,;]*", "[path-redacted]", value)
    value = re.sub(r"(?<![A-Za-z0-9])/(?:[^\s,;]+)", "[path-redacted]", value)
    value = re.sub(r"[A-Za-z0-9_.+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}", "[email-redacted]", value)
    value = re.sub(r"\b(?:\d{1,3}\.){3}\d{1,3}\b", "[address-redacted]", value)
    # Replace IPv6 candidates only when they parse as addresses (timestamps survive).
    def ipv6(match):
        try:
            ipaddress.IPv6Address(match.group(0).split("%", 1)[0])
            return "[address-redacted]"
        except ValueError:
            return match.group(0)
    return re.sub(r"[0-9A-Fa-f:]*:[0-9A-Fa-f:]+(?:%[A-Za-z0-9]+)?", ipv6, value)


def unsafe_symlink(path):
    """Allow only Apple's root-owned OS aliases, never arbitrary user links."""
    for part in [path, *path.parents]:
        if not part.is_symlink():
            continue
        if sys.platform == "darwin" and str(part) in {"/var", "/tmp", "/etc"}:
            try:
                if part.lstat().st_uid == 0 and os.readlink(part) in {"/private" + str(part), "private" + str(part)}:
                    continue
            except OSError:
                pass
        return True
    return False


def load_json(path):
    # No recursive discovery, symlinks, devices, UNC paths or oversized input.
    if str(path).startswith(("\\\\", "//")):
        raise GuardianError("UNSAFE_OR_OFFLINE_PATH")
    p = Path(path)
    try:
        if unsafe_symlink(p):
            raise GuardianError("UNSAFE_OR_OFFLINE_PATH")
        st = p.stat()
        if not stat.S_ISREG(st.st_mode) or st.st_size > MAX_BYTES:
            raise GuardianError("BUDGET_EXCEEDED")
        with p.open("rb") as stream:
            data = stream.read(MAX_BYTES + 1)
        if len(data) > MAX_BYTES:
            raise GuardianError("BUDGET_EXCEEDED")
        def unique(pairs):
            result = {}
            for key, val in pairs:
                if key in result:
                    raise ValueError("duplicate")
                result[key] = val
            return result
        obj = json.loads(data, object_pairs_hook=unique, parse_constant=lambda _: (_ for _ in ()).throw(ValueError("nonfinite")))
        if not isinstance(obj, dict):
            raise ValueError("object required")
        return obj
    except GuardianError:
        raise
    except (OSError, ValueError, UnicodeError, RecursionError):
        raise GuardianError("INPUT_OR_RESPONSE_INVALID") from None


def base(operation, target_ref=None):
    return {
        "schema_version": "guardian-report/0.1", "runtime_version": VERSION,
        "traffic_policy": policy_projection(),
        "contract_provenance": "reconstructed_from_spec_not_historical_zip",
        "record_kind": "offline_analysis", "operation": operation,
        "module_ids": ["M00"] if operation == "interview" else MODULES,
        "run_ref": "run-preview", "target_ref": target_ref,
        "target_binding": {"binding_state": "needs_confirmation"},
        "contact_control": {"contact_phase": "precontact", "gate_state": "closed", "pc_g1": "not_verified", "pc_g2": "not_run"},
        "execution_status": "completed", "check_status": "unknown", "inventory_readiness": "partial",
        "facts": [], "evidence": [], "findings": [], "missing_fields": [],
        "not_tested": ["ENV-03: live IP/ASN/path tests", "ENV-04: DNS/IPv6/UDP", "ENV-05: browser/WebRTC", "ENV-07: real clients and subprocesses", "ENV-09: cleanup", "ENV-10: failure/rollback validation"],
        "next_actions": [], "changes": [],
        "privacy": {"shareable": False, "redacted_preview": True, "review_before_sharing": True, "raw_input_echoed": False, "selected_input_values_included": True, "persistence": "none_unless_output_requested"},
        "snapshot": {"observed_at": now(), "clock_externally_verified": False},
        "limits": {"collector_external_network": "forbidden", "endpoints": "unconfigured", "native_platform_validation": "not_run", "environment_pass_claim": False, "account_safety_guarantee": False},
    }


def finding(report, code, module="ENV-01"):
    report["findings"].append({"code": code, "module_id": module})


def contact_guard(obj):
    if obj.get("contact_phase", "precontact") != "precontact" or obj.get("gate_state", "closed") != "closed":
        raise GuardianError("PRECONTACT_ACTION_REJECTED", 3)
    if obj.get("operation") in {"probe", "apply", "rollback", "cleanup", "login", "open_claude", "pay"}:
        raise GuardianError("PRECONTACT_ACTION_REJECTED", 3)
    if any(key in obj for key in ("command", "script", "url", "endpoints", "controller", "credentials")):
        raise GuardianError("PRECONTACT_ACTION_REJECTED", 3)


# This release has typed values for its minimal native producers and the
# offline proxy-plan contract only. The full 47-field catalog is not implemented.
# An ID being reserved is not permission to echo an arbitrary scalar value.
VALUELESS_STATES = {"unknown", "blocked", "not_applicable", "not_found_in_scope", "conflict", "stale"}
FACT_REASON_CODES = {
    "KERNEL_VERSION_ONLY", "WINDOWS_VERSION_API_ONLY", "READ_ONLY_PROCESS_CONTEXT",
    "PREFERRED_LANGUAGES_NOT_EFFECTIVE_UI", "PROCESS_UI_CULTURE",
    "READ_ONLY_LIMITED_METADATA", "PROCESS_VIEW_NOT_HARDWARE_ARCHITECTURE",
}
FACT_COVERAGES = {"current_process_os", "target_os_metadata", "default_flags_only"}
FACT_ENUMS = {
    "H04": {"same", "different", "unknown"},
    "S01": {"macos", "windows"},
    "S04": {"arm64", "aarch64", "x86_64", "amd64", "x64", "x86"},
    "P11": {"rule", "global", "direct"},
}
VERSION_VALUE = (r"(?:[0-9]{1,3}(?:\.[0-9]{1,6}){1,3}"
                 r"|macOS-product-[0-9]{1,3}(?:\.[0-9]{1,3}){1,2}(?:;build-[0-9]{1,3}[A-Z][0-9]{1,6}[a-z]?)?"
                 r"|Windows-version-[0-9]{1,3}(?:\.[0-9]{1,6}){1,3};build-[0-9]{1,8})")
LANGUAGE_VALUE = r"[A-Za-z]{2,8}(?:-[A-Za-z0-9]{2,8})*"
LOCALE_VALUE = r"[A-Za-z]{2,8}(?:[_-][A-Za-z0-9]{2,16})*(?:@calendar=[a-z]+)?"
TIMEZONE_VALUE = r"(?:IANA:[A-Za-z0-9_+:-]+|Windows:[A-Za-z0-9 .()+_-]{1,100})"


def validate_fact_value(fact):
    """Reject unsupported values before a fact can enter an agent-visible report.

    Formats describe known producers, not a universal secret detector or proof
    that imported facts are true. Unknown fields retain only an explicit gap.
    """
    field, value = fact["id"], fact.get("value")
    credential_pattern = KNOWN_CREDENTIAL_LANGUAGE if field in {"S06", "S07"} else KNOWN_CREDENTIAL_VALUE
    if type(value) is str and credential_pattern.search(value):
        raise GuardianError("INPUT_OR_RESPONSE_INVALID")
    if value is None:
        if fact["state"] in VALUELESS_STATES:
            return
        raise GuardianError("INPUT_OR_RESPONSE_INVALID")
    valid = False
    if field in FACT_ENUMS:
        valid = type(value) is str and value in FACT_ENUMS[field]
    elif field == "S02":
        valid = type(value) is str and re.fullmatch(VERSION_VALUE, value) is not None
    elif field == "S03":
        valid = type(value) is int and 0 <= value <= 10000
    elif field == "S06":
        # Empty UI override is an observed value, not missing UI-language evidence.
        valid = type(value) is str and (value == "" or (len(value.split(",")) <= 16
            and all(len(item) <= 160 and re.fullmatch(LANGUAGE_VALUE, item)
                    for item in value.split(","))))
    elif field == "S07":
        valid = type(value) is str and len(value) <= 160 and re.fullmatch(LOCALE_VALUE, value) is not None
    elif field == "S08":
        valid = type(value) is str and len(value) <= 256 and re.fullmatch(TIMEZONE_VALUE, value) is not None
    elif field == "S09":
        valid = type(value) is int and -86400 <= value <= 86400
    elif field == "P06" and type(value) is str:
        valid = re.fullmatch(PROXY_SUMMARY, value) is not None
    elif field in {"P06", "P09"}:
        keys = {"enabled", "port"} if field == "P06" else {"selected_instance_port", "port_owner_matches"}
        if type(value) is dict and set(value) == keys:
            port = value.get("port", value.get("selected_instance_port"))
            flag = value.get("enabled", value.get("port_owner_matches"))
            valid = type(port) is int and 1 <= port <= 65535 and type(flag) is bool
    elif field == "P12":
        valid = type(value) is bool
    if not valid:
        raise GuardianError("INPUT_OR_RESPONSE_INVALID")


def validate_offline(obj, target):
    alias(target)
    contact_guard(obj)
    allowed = {"schema_version", "target_ref", "target_binding", "record_kind", "contact_phase", "gate_state", "facts", "cancelled", "snapshot_state"}
    if set(obj) - allowed or obj.get("schema_version") != INPUT_SCHEMA:
        raise GuardianError("INPUT_OR_RESPONSE_INVALID")
    if obj.get("target_ref") != target:
        raise GuardianError("TARGET_NOT_BOUND", 3)
    if (type(obj.get("record_kind")) is not str
            or obj["record_kind"] not in {"synthetic_example", "user_supplied_observation"}):
        raise GuardianError("INPUT_OR_RESPONSE_INVALID")
    binding = obj.get("target_binding", {})
    if not isinstance(binding, dict) or set(binding) - {"declared_os", "desktop_user_relation", "filesystem_namespace", "execution_location"}:
        raise GuardianError("INPUT_OR_RESPONSE_INVALID")
    if type(binding.get("declared_os")) is not str:
        raise GuardianError("INPUT_OR_RESPONSE_INVALID")
    if binding["declared_os"] not in {"macos", "windows"}:
        raise GuardianError("UNSUPPORTED_PRODUCT_OR_VERSION")
    if binding.get("desktop_user_relation") != "same" or binding.get("filesystem_namespace") != "host_desktop" or binding.get("execution_location") != "native_local":
        raise GuardianError("TARGET_USER_CONTEXT_MISMATCH", 3)
    if "cancelled" in obj and type(obj["cancelled"]) is not bool:
        raise GuardianError("INPUT_OR_RESPONSE_INVALID")
    facts = obj.get("facts", [])
    if not isinstance(facts, list) or len(facts) > 64:
        raise GuardianError("INPUT_OR_RESPONSE_INVALID")
    seen = set()
    for fact in facts:
        if not isinstance(fact, dict) or set(fact) - {"id", "value", "state", "context_ref", "observed_at", "layer", "source_ref", "reason_code", "coverage"}:
            raise GuardianError("INPUT_OR_RESPONSE_INVALID")
        if (type(fact.get("id")) is not str or type(fact.get("state")) is not str
                or fact["id"] not in FACT_IDS or fact["id"] in seen or fact["state"] not in STATES):
            raise GuardianError("INPUT_OR_RESPONSE_INVALID")
        seen.add(fact["id"])
        if fact.get("context_ref") != target:
            raise GuardianError("TARGET_NOT_BOUND", 3)
        if (type(fact.get("layer")) is not str
                or fact["layer"] not in {"reported", "os_query", "static_file", "runtime", "derived"}):
            raise GuardianError("INPUT_OR_RESPONSE_INVALID")
        alias(fact.get("source_ref"))
        for qualifier, allowed_values in (("reason_code", FACT_REASON_CODES), ("coverage", FACT_COVERAGES)):
            if qualifier in fact and (type(fact[qualifier]) is not str or fact[qualifier] not in allowed_values):
                raise GuardianError("INPUT_OR_RESPONSE_INVALID")
        validate_fact_value(fact)
        try:
            stamp = datetime.fromisoformat(fact["observed_at"].replace("Z", "+00:00"))
            if stamp.tzinfo is None:
                raise ValueError("timezone required")
            age = (datetime.now(timezone.utc) - stamp).total_seconds()
        except (KeyError, TypeError, ValueError, AttributeError):
            raise GuardianError("INPUT_OR_RESPONSE_INVALID") from None
        if age > MAX_AGE or age < -300:
            fact["state"] = "stale"
    return obj


def _report_shape(value, template):
    if type(template) is dict:
        if type(value) is not dict or set(value) != set(template):
            raise GuardianError("INPUT_OR_RESPONSE_INVALID")
        for key in template:
            _report_shape(value[key], template[key])
    elif type(template) is list:
        if type(value) is not list or len(value) > 128:
            raise GuardianError("INPUT_OR_RESPONSE_INVALID")
        for item in value:
            if not template:
                raise GuardianError("INPUT_OR_RESPONSE_INVALID")
            _report_shape(item, template[0])
    elif type(value) is not type(template):
        raise GuardianError("INPUT_OR_RESPONSE_INVALID")
    elif type(value) is str:
        if len(value) > 2048 or KNOWN_CREDENTIAL_VALUE.search(value):
            raise GuardianError("INPUT_OR_RESPONSE_INVALID")


def _validate_report_policy(obj):
    """One additive fixed output member; legacy absence is unknown, never a pass."""
    if 'traffic_policy' not in obj:
        return
    value, expected = obj['traffic_policy'], policy_projection()
    if (type(value) is not dict or set(value) != set(expected)
            or any(type(value[key]) is not type(want) or value[key] != want
                   for key, want in expected.items())):
        raise GuardianError('INPUT_OR_RESPONSE_INVALID')


def report_member_vocabulary():
    """Allowed member names per level for saved guardian-report/0.1 and env-inventory/0.2 reports.

    Derived from the producers' own template so it cannot drift; a few members that
    individual producers add are listed explicitly. Used as a subset check: older
    fixtures may omit members, but no name outside this release's vocabulary is accepted.
    """
    template = base("audit", "device-1")
    return {
        "root": set(template) | {"plan", "question", "state"},
        "snapshot": set(template["snapshot"]),
        "contact_control": set(template["contact_control"]),
        "privacy": set(template["privacy"]),
        # the two command_* members: native_check.
        "limits": set(template["limits"]) | {"command_timeout_seconds", "command_stdout_max_bytes"},
        "target_binding": {"declared_os", "desktop_user_relation", "filesystem_namespace", "execution_location",
                           "binding_state", "requested_role", "network_namespace"},
        "fact": {"id", "value", "state", "context_ref", "observed_at", "layer", "source_ref", "source_refs",
                 "reason_code", "coverage"},
        "finding": {"code", "module_id"},
    }


def reject_unknown_report_members(report, code="INPUT_OR_RESPONSE_INVALID", extra_root=frozenset()):
    """Reject unrecognized members at the input boundary (ENV-T121).

    Dropping them later in a display or selection layer is not a substitute. Raises a
    fixed code only; the offending name or value is never echoed. A consumer that reads
    additional fixed root members declares exactly those names in extra_root.
    """
    allowed = report_member_vocabulary()
    if type(report) is not dict or set(report) - allowed["root"] - set(extra_root):
        raise GuardianError(code)
    for key in ("snapshot", "contact_control", "privacy", "limits", "target_binding"):
        value = report.get(key)
        if type(value) is dict and set(value) - allowed[key]:
            raise GuardianError(code)
    for key, kind in (("facts", "fact"), ("findings", "finding")):
        items = report.get(key)
        if type(items) is list:
            for item in items:
                if type(item) is dict and set(item) - allowed[kind]:
                    raise GuardianError(code)


def validate_inventory_envelope(obj):
    """Validate this release's public inventory shape before lossy projection.

    Only native_check/base-derived envelopes are supported, not the historical
    contract ZIP. Metadata is not host provenance. Every source reference is
    checked even though the compact offline model retains only its first one.
    """
    def invalid():
        raise GuardianError("INPUT_OR_RESPONSE_INVALID")

    shape = _report_shape

    template = base("audit", "device-1")
    if (type(obj) is not dict or set(obj) not in
            (set(template), set(template) - {'traffic_policy'})):
        invalid()
    _validate_report_policy(obj)
    if obj["schema_version"] != "env-inventory/0.2":
        invalid()
    if (type(obj["record_kind"]) is not str or obj["record_kind"] not in {
            "synthetic_example", "device_observation", "offline_analysis", "user_supplied_observation"}):
        invalid()
    alias(obj["target_ref"])
    contact = obj["contact_control"]
    if type(contact) is not dict:
        invalid()
    shape(contact, template["contact_control"])
    contact_guard(contact)
    binding = obj["target_binding"]
    required = {"declared_os", "desktop_user_relation", "filesystem_namespace", "execution_location"}
    optional = {"binding_state": {"bound_by_explicit_operator_attestation"},
                "requested_role": {"local_desktop"}, "network_namespace": {"not_verified"}}
    if type(binding) is not dict or not required <= set(binding) or set(binding) - required - set(optional):
        invalid()
    for key, values in optional.items():
        if key in binding and (type(binding[key]) is not str or binding[key] not in values):
            invalid()
    # Required binding values are validated by validate_offline after projection.
    for key in required:
        if type(binding[key]) is not str:
            invalid()
    facts = obj["facts"]
    if type(facts) is not list or len(facts) > 64:
        invalid()
    required_fact = {"id", "value", "state", "context_ref", "observed_at", "layer", "source_refs"}
    for fact in facts:
        if (type(fact) is not dict or not required_fact <= set(fact)
                or set(fact) - required_fact - {"reason_code", "coverage"}):
            invalid()
        sources = fact["source_refs"]
        if type(sources) is not list or not 1 <= len(sources) <= 64:
            invalid()
        for source in sources:
            alias(source)
    shape(obj["privacy"], template["privacy"])
    shape(obj["snapshot"], template["snapshot"])
    limits = obj["limits"]
    optional_limits = {"command_timeout_seconds": COMMAND_TIMEOUT,
                       "command_stdout_max_bytes": COMMAND_MAX_BYTES}
    if type(limits) is not dict or set(limits) - set(template["limits"]) - set(optional_limits):
        invalid()
    shape({k: v for k, v in limits.items() if k not in optional_limits}, template["limits"])
    for key, expected in optional_limits.items():
        if key in limits and (type(limits[key]) is not type(expected) or limits[key] != expected):
            invalid()
    for key in ("evidence", "changes"):
        if obj[key] != []:
            invalid()
    shape(obj["findings"], [{"code": "", "module_id": ""}])
    for key in ("module_ids", "missing_fields", "not_tested", "next_actions"):
        shape(obj[key], [""])
    for key in ("runtime_version", "contract_provenance", "run_ref", "operation",
                "execution_status", "check_status", "inventory_readiness"):
        shape(obj[key], "")


def inventory_to_offline(obj):
    """Accept this release's minimal native audit as offline evidence, never a gate pass."""
    validate_inventory_envelope(obj)
    if obj.get("operation") != "audit" or obj.get("changes") != [] or obj.get("execution_status") != "completed":
        raise GuardianError("INPUT_OR_RESPONSE_INVALID")
    contact = obj.get("contact_control", {})
    if not isinstance(contact, dict):
        raise GuardianError("INPUT_OR_RESPONSE_INVALID")
    contact_guard(contact)
    binding = obj.get("target_binding", {})
    if not isinstance(binding, dict) or not isinstance(obj.get("facts"), list):
        raise GuardianError("INPUT_OR_RESPONSE_INVALID")
    facts = []
    for fact in obj["facts"]:
        if not isinstance(fact, dict):
            raise GuardianError("INPUT_OR_RESPONSE_INVALID")
        sources = fact.get("source_refs", [])
        if not isinstance(sources, list) or not sources:
            raise GuardianError("INPUT_OR_RESPONSE_INVALID")
        facts.append({key: fact.get(key) for key in ("id", "value", "state", "context_ref", "observed_at", "layer")})
        facts[-1]["source_ref"] = sources[0]
        for qualifier in ("reason_code", "coverage"):
            if qualifier in fact:
                facts[-1][qualifier] = fact[qualifier]
    return {"schema_version": INPUT_SCHEMA, "record_kind": "synthetic_example" if obj["record_kind"] == "synthetic_example" else "user_supplied_observation", "target_ref": obj.get("target_ref"), "target_binding": {key: binding.get(key) for key in ("declared_os", "desktop_user_relation", "filesystem_namespace", "execution_location")}, "contact_phase": "precontact", "gate_state": "closed", "snapshot_state": "unknown", "facts": facts}


def analyze(obj, target, planning=False):
    if obj.get("schema_version") == "env-inventory/0.2":
        obj = inventory_to_offline(obj)
    obj = validate_offline(obj, target)
    report = base("plan" if planning else "analyze", target)
    report["record_kind"] = obj["record_kind"]
    report["target_binding"] = dict(obj["target_binding"], binding_state="supplied_not_independently_verified")
    if obj.get("cancelled"):
        report.update(execution_status="interrupted", inventory_readiness="interrupted")
        finding(report, "USER_CANCELLED")
        return report
    report["facts"] = obj.get("facts", [])
    index = {f["id"]: f for f in report["facts"]}
    report["missing_fields"] = [f for f in ["S01", "P06", "P09", "P11", "P12"] if f not in index or index[f]["state"] not in {"observed", "reported"}]
    if isinstance(index.get("P06", {}).get("value"), str) and "P06" not in report["missing_fields"]:
        report["missing_fields"].append("P06")
    if any(f["state"] == "stale" for f in report["facts"]):
        finding(report, "STALE_EVIDENCE_REAUDIT_REQUIRED")
    if (type(obj.get("snapshot_state", "unknown")) is not str
            or obj.get("snapshot_state", "unknown") not in {"stable", "unknown", "changed"}):
        raise GuardianError("INPUT_OR_RESPONSE_INVALID")
    if obj.get("snapshot_state") == "changed":
        finding(report, "SNAPSHOT_CHANGED_DURING_AUDIT")
    report["next_actions"] = ["Resolve missing or stale target facts", "Prepare neutral endpoint proposal; endpoint selection and probe authorization pending"]
    p6, p9 = index.get("P06", {}), index.get("P09", {})
    usable = isinstance(p6.get("value"), dict) and isinstance(p9.get("value"), dict) and all(f.get("state") == "observed" and f.get("layer") in {"os_query", "runtime"} for f in (p6, p9))
    conflict = usable and p6["value"]["enabled"] and p9["value"]["port_owner_matches"] and p6["value"]["port"] != p9["value"]["selected_instance_port"]
    configuration_ready = conflict and obj.get("snapshot_state") == "stable" and all(index.get(field, {}).get("state") == "observed" and index.get(field, {}).get("layer") in {"os_query", "runtime"} for field in ("P11", "P12"))
    if conflict:
        finding(report, "PROXY_PORT_ASSOCIATION_CONFLICT", "ENV-02")
        if configuration_ready:
            report["inventory_readiness"] = "ready_for_configuration_plan"
    else:
        finding(report, "NETWORK_EFFECTIVENESS_NOT_TESTED", "ENV-03")
    if planning:
        report["plan"] = {"mode": "preview_only", "executable": False, "requires_fresh_native_audit": True, "diff": [], "validation": ["Reconfirm selected proxy instance and ownership", "Approve neutral endpoints and future probes", "Validate application-specific paths after authorized contact"], "recovery": "No change made. Future edits require recording exact old values and a tested restore method."}
        if configuration_ready:
            report["plan"]["diff"].append({"module_id": "ENV-06", "field": "selected_target.system_proxy.port", "before": p6["value"]["port"], "proposed_after": p9["value"]["selected_instance_port"], "preconditions": ["Revalidate live target, selected instance and active configuration", "Obtain exact-change authorization", "Establish backup and recovery; platform executor not available in this release"]})
        elif conflict:
            finding(report, "PLAN_REQUIRES_STABLE_SNAPSHOT_AND_ROUTE_FACTS", "ENV-06")
        report["next_actions"].append("Review the preview; automatic modification is deferred")
    return report


# Fixed read-only collectors. No user-supplied argument or command is accepted.
COMMAND_TIMEOUT = 5
COMMAND_MAX_BYTES = 65536
WINDOWS_SYSTEM_QUERY = """$ErrorActionPreference='Stop'; [Console]::OutputEncoding=New-Object System.Text.UTF8Encoding($false); $o=Get-CimInstance -ClassName Win32_OperatingSystem; $t=Get-TimeZone; [ordered]@{version=$o.Version;build=$o.BuildNumber;sku=[int]$o.OperatingSystemSKU;ui=(Get-UICulture).Name;timezone=$t.Id} | ConvertTo-Json -Compress"""
WINDOWS_PROXY_QUERY = """$ErrorActionPreference='Stop'; [Console]::OutputEncoding=New-Object System.Text.UTF8Encoding($false); $p=Get-ItemProperty -LiteralPath 'HKCU:\\Software\\Microsoft\\Windows\\CurrentVersion\\Internet Settings'; [ordered]@{enabled=if($null -eq $p.ProxyEnable){$null}else{[int]$p.ProxyEnable};pac=([bool]$p.AutoConfigURL)} | ConvertTo-Json -Compress"""
MAC_COMMANDS = {
    'mac-version': ('/usr/bin/sw_vers', '-productVersion'),
    'mac-build': ('/usr/bin/sw_vers', '-buildVersion'),
    'mac-locale': ('/usr/bin/defaults', 'read', '-g', 'AppleLocale'),
    'mac-languages': ('/usr/bin/defaults', 'read', '-g', 'AppleLanguages'),
    'mac-proxy': ('/usr/sbin/scutil', '--proxy'),
}


def fixed_command(collector_id):
    if collector_id in MAC_COMMANDS:
        if sys.platform != 'darwin':
            raise GuardianError('TARGET_USER_CONTEXT_MISMATCH', 3)
        return MAC_COMMANDS[collector_id], {'PATH': '/usr/bin:/bin:/usr/sbin:/sbin', 'LC_ALL': 'C'}
    if collector_id not in {'windows-system', 'windows-proxy'}:
        raise GuardianError('PRECONTACT_ACTION_REJECTED', 3)
    if sys.platform != 'win32':
        raise GuardianError('TARGET_USER_CONTEXT_MISMATCH', 3)
    # Resolve the OS directory using the OS API, never caller-controlled PATH/SystemRoot.
    import ctypes
    buffer = ctypes.create_unicode_buffer(32768)
    size = ctypes.windll.kernel32.GetWindowsDirectoryW(buffer, len(buffer))
    if not 0 < size < len(buffer):
        raise GuardianError('RUNTIME_OR_PARSER_UNAVAILABLE')
    root = buffer.value
    exe = root + '\\System32\\WindowsPowerShell\\v1.0\\powershell.exe'
    script = WINDOWS_SYSTEM_QUERY if collector_id == 'windows-system' else WINDOWS_PROXY_QUERY
    return (exe, '-NoLogo', '-NoProfile', '-NonInteractive', '-Command', script), {'SystemRoot': root, 'WINDIR': root, 'PATH': root + '\\System32', 'PSModulePath': root + '\\System32\\WindowsPowerShell\\v1.0\\Modules'}


def _fixed_pipe_ready(stream):
    """Poll our stdout pipe without a blocking read or a platform/version dependency."""
    if sys.platform != 'win32':
        import select
        return bool(select.select([stream.fileno()], [], [], 0)[0])
    # Windows select() accepts sockets only; PeekNamedPipe also supports Popen's
    # anonymous pipes, including Python 3.10 (before nonblocking Windows pipes).
    import ctypes
    from ctypes import wintypes
    import msvcrt
    kernel = ctypes.WinDLL('kernel32', use_last_error=True)
    peek = kernel.PeekNamedPipe
    peek.argtypes = (wintypes.HANDLE, wintypes.LPVOID, wintypes.DWORD,
                     ctypes.POINTER(wintypes.DWORD), ctypes.POINTER(wintypes.DWORD),
                     ctypes.POINTER(wintypes.DWORD))
    peek.restype = wintypes.BOOL
    available = wintypes.DWORD()
    if not peek(msvcrt.get_osfhandle(stream.fileno()), None, 0, None,
                ctypes.byref(available), None):
        if ctypes.get_last_error() == 109:  # ERROR_BROKEN_PIPE: read returns EOF.
            return True
        raise OSError('stdout pipe unavailable')
    return available.value > 0


def run_fixed(collector_id):
    """Capture bounded stdout; always reclaim our child, reader and pipe."""
    import subprocess
    import threading
    command, environment = fixed_command(collector_id)
    output = bytearray()
    exceeded = threading.Event()
    failed = threading.Event()
    stop = threading.Event()
    try:
        process = subprocess.Popen(command, shell=False, stdin=subprocess.DEVNULL,
                                   stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
                                   bufsize=0, env=environment,
                                   cwd=command[0].rsplit('/' if sys.platform == 'darwin' else '\\', 1)[0])
    except PermissionError:
        raise GuardianError('PERMISSION_DENIED', 3) from None
    except OSError:
        raise GuardianError('RUNTIME_OR_PARSER_UNAVAILABLE') from None

    def drain():
        try:
            while not stop.is_set():
                if not _fixed_pipe_ready(process.stdout):
                    stop.wait(.01)
                    continue
                chunk = os.read(process.stdout.fileno(), 4096)
                if not chunk:
                    break
                if len(output) + len(chunk) > COMMAND_MAX_BYTES:
                    exceeded.set()
                    process.kill()
                    break
                output.extend(chunk)
        except Exception:
            # A reader failure must never print raw exception/command data from
            # a background thread. Main reports only the stable failure code.
            failed.set()
            try:
                process.kill()
            except Exception:
                pass

    reader = None
    waited = False
    cleanup_failed = False
    try:
        # Construction and start belong inside the same ownership boundary as wait.
        reader = threading.Thread(target=drain, daemon=True)
        reader.start()
        process.wait(timeout=COMMAND_TIMEOUT)
        waited = True
        reader.join(timeout=1)
        if exceeded.is_set() or reader.is_alive():
            raise GuardianError('BUDGET_EXCEEDED')
        if failed.is_set() or process.returncode:
            raise GuardianError('OS_QUERY_FAILED')
    except subprocess.TimeoutExpired:
        raise GuardianError('BUDGET_EXCEEDED') from None
    except (OSError, RuntimeError, ValueError):
        raise GuardianError('OS_QUERY_FAILED') from None
    finally:
        # Stop polling before closing the pipe. Inherited writers cannot hold the
        # reader alive indefinitely; only this owned child is killed/reaped.
        active_error = sys.exc_info()[1]
        stop.set()
        try:
            if not waited:
                try:
                    process.kill()
                except Exception:
                    cleanup_failed = True
                finally:
                    try:
                        process.wait(timeout=1)
                    except Exception:
                        cleanup_failed = True
        finally:
            try:
                if reader is not None and reader.ident is not None:
                    reader.join(timeout=1)
                    cleanup_failed |= reader.is_alive()
            except Exception:
                cleanup_failed = True
            finally:
                try:
                    process.stdout.close()
                except Exception:
                    cleanup_failed = True
        if cleanup_failed:
            if isinstance(active_error, (KeyboardInterrupt, SystemExit)):
                raise active_error from GuardianError('OS_QUERY_FAILED')
            raise GuardianError('OS_QUERY_FAILED') from None
    try:
        return output.decode('utf-8-sig', errors='strict').strip()
    except UnicodeError:
        raise GuardianError('INPUT_OR_RESPONSE_INVALID') from None


def checked_text(value, expression):
    if not isinstance(value, str) or len(value) > 160 or not re.fullmatch(expression, value):
        raise GuardianError('INPUT_OR_RESPONSE_INVALID')
    return value


def proxy_summary(raw):
    """Parse only default enable flags; explicitly do not flatten scoped service data."""
    depth = 0
    flags = {}
    scoped = False
    for line in raw.splitlines():
        line = line.strip()
        if depth == 1:
            if re.match(r'__SCOPED__\s*:', line):
                scoped = True
            match = re.fullmatch(r'(HTTPEnable|HTTPSEnable|SOCKSEnable|ProxyAutoConfigEnable|ProxyAutoDiscoveryEnable)\s*:\s*([01])', line)
            if match:
                if match[1] in flags:
                    raise GuardianError('INPUT_OR_RESPONSE_INVALID')
                flags[match[1]] = 'enabled' if match[2] == '1' else 'disabled'
        # scutil's container delimiters are structural lines, never count URL braces.
        if re.fullmatch(r'(?:[^:]+\s*:\s*)?<(?:dictionary|array)>\s*\{', line):
            depth += 1
        elif line == '}':
            depth -= 1
        if not 0 <= depth <= 16:
            raise GuardianError('INPUT_OR_RESPONSE_INVALID')
    if depth or not raw.startswith('<dictionary> {'):
        raise GuardianError('INPUT_OR_RESPONSE_INVALID')
    return ';'.join('%s=%s' % (name, flags.get(key, 'unknown')) for name, key in [('http', 'HTTPEnable'), ('https', 'HTTPSEnable'), ('socks', 'SOCKSEnable'), ('pac', 'ProxyAutoConfigEnable'), ('wpad', 'ProxyAutoDiscoveryEnable')]) + ';scoped=' + ('present' if scoped else 'not_reported')


PROXY_SUMMARY = r'(?:http=(?:enabled|disabled|unknown);https=(?:enabled|disabled|unknown);socks=(?:enabled|disabled|unknown);pac=(?:enabled|disabled|unknown);wpad=(?:enabled|disabled|unknown);scoped=(?:present|not_reported)|user_proxy=(?:enabled|disabled|unknown);pac_url=(?:present|absent);winhttp=not_collected)'


def extended_inventory(actual, runner=run_fixed):
    """Return filtered facts plus field-level gaps; raw failures are never returned."""
    results, errors = [], []
    def collect(field, source, parse):
        try:
            raw = runner(source)
            if not isinstance(raw, str) or len(raw.encode('utf-8')) > COMMAND_MAX_BYTES:
                raise GuardianError('BUDGET_EXCEEDED')
            results.append((field, parse(raw), source))
        except GuardianError as error:
            errors.append((field, error.code))
        except (ValueError, TypeError, KeyError, OSError):
            errors.append((field, 'INPUT_OR_RESPONSE_INVALID'))
    if actual == 'macos':
        try:
            machine = checked_text(os.uname().machine, r'arm64|x86_64')
            results.append(('S04', machine, 'mac-process-architecture'))
        except (GuardianError, OSError, AttributeError):
            errors.append(('S04', 'PROCESS_ARCHITECTURE_UNAVAILABLE'))
        collect('S02', 'mac-version', lambda x: 'macOS-product-' + checked_text(x, r'\d{1,3}(?:\.\d{1,3}){1,2}'))
        collect('S02-build', 'mac-build', lambda x: checked_text(x, r'[0-9]{1,3}[A-Z][0-9]{1,6}[a-z]?'))
        collect('S07', 'mac-locale', lambda x: checked_text(x, r'[a-zA-Z]{2,8}(?:[_-][A-Za-z0-9]{2,16})*(?:@calendar=[a-z]+)?'))
        def languages(raw):
            if not raw.startswith('(') or not raw.endswith(')'):
                raise ValueError()
            values = [v.strip().strip('"') for v in raw[1:-1].split(',') if v.strip()]
            if not 1 <= len(values) <= 16:
                raise ValueError()
            return ','.join(checked_text(v, r'[A-Za-z]{2,8}(?:-[A-Za-z0-9]{2,8})*') for v in values)
        collect('S06', 'mac-languages', languages)
        collect('P06', 'mac-proxy', proxy_summary)
        # Metadata only: do not follow the symlink or read timezone-file contents.
        try:
            path = os.readlink('/etc/localtime')
            match = re.fullmatch(r'/(?:var/db/timezone|usr/share)/zoneinfo/([A-Za-z0-9_+\-/]+)', path)
            if not match or '..' in match[1].split('/'):
                raise ValueError()
            results.append(('S08', 'IANA:' + match[1].replace('/', ':'), 'mac-timezone-link'))
        except (ValueError, OSError):
            errors.append(('S08', 'SYSTEM_TIMEZONE_UNAVAILABLE'))
        build = next((v for f, v, _ in results if f == 'S02-build'), None)
        results = [(f, v + (';build-' + build if build else '') if f == 'S02' else v, s) for f, v, s in results if f != 'S02-build']
    elif actual == 'windows':
        def system(raw):
            obj = json.loads(raw)
            version = checked_text(obj['version'], r'\d{1,3}(?:\.\d{1,6}){1,3}')
            build = checked_text(obj['build'], r'\d{1,8}')
            if type(obj['sku']) is not int or not 0 <= obj['sku'] <= 10000:
                raise ValueError()
            ui = checked_text(obj['ui'], r'[A-Za-z]{2,8}(?:-[A-Za-z0-9]{2,8})*')
            zone = checked_text(obj['timezone'], r'[A-Za-z0-9 .()+_-]{1,100}')
            results.extend([('S03', obj['sku'], 'windows-system'), ('S06', ui, 'windows-system'), ('S08', 'Windows:' + zone, 'windows-system')])
            return 'Windows-version-' + version + ';build-' + build
        collect('S02', 'windows-system', system)
        def proxy(raw):
            obj = json.loads(raw)
            enabled = obj['enabled']
            if (enabled is not None and (type(enabled) is not int or enabled not in (0, 1))) or type(obj['pac']) is not bool:
                raise ValueError()
            return 'user_proxy=%s;pac_url=%s;winhttp=not_collected' % ('unknown' if enabled is None else 'enabled' if enabled else 'disabled', 'present' if obj['pac'] else 'absent')
        collect('P06', 'windows-proxy', proxy)
    else:
        raise GuardianError('TARGET_USER_CONTEXT_MISMATCH', 3)
    return results, errors


def native_check(args, *, entry_request=None):
    # A route declaration is an additional prerequisite, never target proof or
    # audit authorization. Missing input fails before any target observation.
    try:
        entry = environment_entry.require_entry(entry_request, 'offline_precheck', args.target_ref)
    except (environment_entry.InvalidProjection, environment_entry.EntryBlocked) as exc:
        raise GuardianError(str(exc), 3) from None
    if entry['target_role'] != 'local':
        raise GuardianError('TARGET_USER_CONTEXT_MISMATCH', 3)
    report = base("audit", args.target_ref)
    report["schema_version"] = "env-inventory/0.2"
    report["module_ids"] = ["ENV-01", "ENV-02"]
    if not args.target_ref or not args.confirm_target:
        raise GuardianError("TARGET_NOT_BOUND", 3)
    alias(args.target_ref)
    if not args.authorize_audit:
        raise GuardianError("AUTHORIZATION_MISSING", 3)
    actual = "macos" if sys.platform == "darwin" else "windows" if sys.platform == "win32" else "unsupported"
    if args.target_os != actual:
        raise GuardianError("TARGET_USER_CONTEXT_MISMATCH", 3)
    if args.target_kind != "local" or args.namespace != "desktop" or args.execution_location != "native_local" or args.user_context != "same":
        raise GuardianError("TARGET_USER_CONTEXT_MISMATCH", 3)
    report["record_kind"] = "device_observation"
    report["target_binding"] = {"binding_state": "bound_by_explicit_operator_attestation", "declared_os": actual, "requested_role": "local_desktop", "execution_location": args.execution_location, "desktop_user_relation": args.user_context, "filesystem_namespace": "host_desktop", "network_namespace": "not_verified"}
    # Minimal fallback: these APIs only describe this process/OS.
    if actual == "windows":
        win = sys.getwindowsversion()
        version = "%s.%s.%s" % (win.major, win.minor, win.build)
    else:
        version = os.uname().release  # Darwin kernel; not mislabeled as macOS product release.
    values = [("S01", actual), ("S02", version), ("S09", int(time.localtime().tm_gmtoff) if hasattr(time.localtime(), "tm_gmtoff") else -time.altzone if time.localtime().tm_isdst else -time.timezone)]
    for field, value in values:
        report["facts"].append({"id": field, "value": value, "state": "observed", "source_refs": ["native-stdlib-os"], "context_ref": args.target_ref, "observed_at": now(), "reason_code": ("KERNEL_VERSION_ONLY" if actual == "macos" else "WINDOWS_VERSION_API_ONLY") if field == "S02" else "READ_ONLY_PROCESS_CONTEXT", "layer": "os_query", "coverage": "current_process_os"})
    extra, errors = extended_inventory(actual)
    for field, value, source in extra:
        report["facts"] = [f for f in report["facts"] if f["id"] != field]
        report["facts"].append({"id": field, "value": value, "state": "observed", "source_refs": [source, "mac-build"] if field == "S02" and actual == "macos" and ";build-" in value else [source], "context_ref": args.target_ref, "observed_at": now(), "reason_code": ("PREFERRED_LANGUAGES_NOT_EFFECTIVE_UI" if actual == "macos" else "PROCESS_UI_CULTURE") if field == "S06" else "READ_ONLY_LIMITED_METADATA", "layer": "os_query", "coverage": "default_flags_only" if field == "P06" else "target_os_metadata"})
        if source == 'mac-process-architecture':
            report['facts'][-1].update(coverage='current_process_os',
                                      reason_code='PROCESS_VIEW_NOT_HARDWARE_ARCHITECTURE')
    for field, error in errors:
        finding(report, error)
        report["missing_fields"].append(field + ": " + error)
    report["missing_fields"] += ["S04: hardware architecture and translation not verified" if actual == 'macos' else "S04: hardware versus process architecture", "S10: automatic time and timezone", "S13: approved installation inventory", "S14: related running processes", "P06: endpoints, bypass rules, scoped details and WinHTTP not collected", "P01-P24: other proxy and runtime inventory not implemented"]
    if actual == "macos":
        report["missing_fields"].append("S03: not applicable on macOS")
    elif not any(f["id"] == "S03" for f in report["facts"]):
        report["missing_fields"].append("S03: Windows edition SKU unavailable")
    finding(report, "LIMITED_METADATA_ONLY" if extra else "MINIMAL_METADATA_ONLY")
    report["limits"].update(command_timeout_seconds=COMMAND_TIMEOUT, command_stdout_max_bytes=COMMAND_MAX_BYTES)
    report["next_actions"] = ["Supply narrowly scoped offline proxy observations", "Complete native platform validation; synthetic tests do not certify compatibility"]
    return report


QUESTIONS = [
    ("subscription_stage", "Q-J01", "这是首次准备订阅、重新订阅，还是已有订阅回访？", ["first_subscription", "returning_subscription", "existing_subscriber", "unknown"]),
    ("current_task", "Q-C11", "这次想续费、升级、检查环境，还是排障？", ["renew", "upgrade", "environment", "troubleshoot"]),
    ("os", "Q-C02", "目标电脑是 macOS 还是 Windows？", ["macos", "windows", "unknown", "phone_only"]),
    ("usage", "Q-C01", "主要使用网页、Desktop、Code，还是 IDE 中的 Code？", ["web", "desktop", "code", "ide_code", "mixed", "unknown"]),
    ("target_plan", "Q-C08", "想订阅什么套餐？也可以先标记未决定", None),
    ("account_status", "Q-C04", "当前账号状态是什么？", ["not_registered", "active", "suspended", "unknown"]),
    ("device_history", "Q-C03", "本次目标电脑是否用过 Claude、是否有过停用经历？", ["new_to_claude", "previous_use_no_reported_suspension", "previous_use_with_reported_suspension", "unknown"]),
    ("route", "Q-C05", "建议本机，也可选择虚拟机或 VPS；希望采用哪种？", ["local", "vm", "vps", "explain"]),
]


def validate_interview_envelope(obj):
    """Accept only the current compact interview producer's report wrapper."""
    template = base("interview")
    required = (set(template) - {"traffic_policy"}) | {"state"}
    if type(obj) is not dict or not required <= set(obj) or set(obj) - required - {"question", "traffic_policy"}:
        raise GuardianError("INPUT_OR_RESPONSE_INVALID")
    _validate_report_policy(obj)
    for key in template:
        if key == "traffic_policy":
            continue
        if key == "findings":
            _report_shape(obj[key], [{"code": "", "module_id": ""}])
        elif key in {"module_ids", "not_tested", "next_actions", "missing_fields"}:
            _report_shape(obj[key], [""])
        else:
            _report_shape(obj[key], template[key])
    if "question" in obj:
        if type(obj["question"]) is not dict:
            raise GuardianError("INPUT_OR_RESPONSE_INVALID")
        _report_shape(obj["question"], {"id": "", "field": "", "text": "", "choices": None}
                      if obj["question"].get("choices") is None else
                      {"id": "", "field": "", "text": "", "choices": [""]})


def interview(obj):
    if obj.get("schema_version") == "guardian-report/0.1":
        validate_interview_envelope(obj)
        contact = obj.get("contact_control")
        if obj.get("operation") != "interview" or not isinstance(contact, dict) or not isinstance(obj.get("state"), dict):
            raise GuardianError("INPUT_OR_RESPONSE_INVALID")
        contact_guard(contact)
        if obj.get("execution_status") == "interrupted":
            raise GuardianError("USER_CANCELLED", 3)
        obj = obj["state"]
    contact_guard(obj)
    if set(obj) - {"schema_version", "answers", "cancelled"} or obj.get("schema_version", "guardian-interview/0.1") != "guardian-interview/0.1":
        raise GuardianError("INPUT_OR_RESPONSE_INVALID")
    answers = obj.get("answers", {})
    if not isinstance(answers, dict) or set(answers) - {q[0] for q in QUESTIONS}:
        raise GuardianError("INPUT_OR_RESPONSE_INVALID")
    for field, _, _, choices in QUESTIONS:
        if field in answers and (not isinstance(answers[field], str) or len(answers[field]) > 80 or (choices and answers[field] not in choices)):
            raise GuardianError("INPUT_OR_RESPONSE_INVALID")
    report = base("interview")
    report["state"] = {"schema_version": "guardian-interview/0.1", "answers": answers}
    if "cancelled" in obj and type(obj["cancelled"]) is not bool:
        raise GuardianError("INPUT_OR_RESPONSE_INVALID")
    if obj.get("cancelled"):
        report.update(execution_status="interrupted", inventory_readiness="interrupted")
        finding(report, "USER_CANCELLED", "M00")
        return report
    if answers.get("account_status") == "suspended":
        report["next_actions"] = ["Prioritize M12 incident review and preserve existing evidence; no new purchase or login test"]
        finding(report, "INCIDENT_PRIORITY", "M12")
        return report
    for field, qid, question, choices in QUESTIONS:
        if field == "current_task" and answers.get("subscription_stage") != "existing_subscriber":
            continue
        if field == "target_plan" and answers.get("subscription_stage") == "existing_subscriber" and answers.get("current_task") in {"environment", "troubleshoot"}:
            continue
        if field in answers:
            continue
        report["question"] = {"id": qid, "field": field, "text": question, "choices": choices}
        report["inventory_readiness"] = "needs_input"
        return report
    report["next_actions"] = ["Bind the actual target and request scoped read-only audit authorization", "Payment and route resource interviews remain outside this diagnostic preview"]
    if answers.get("route") in {"vm", "vps", "explain"} or answers.get("os") in {"unknown", "phone_only"} or answers.get("subscription_stage") == "unknown":
        finding(report, "ROUTE_OR_TARGET_NEEDS_CLARIFICATION", "M00")
        report["inventory_readiness"] = "needs_input"
    return report


class PrivateArgumentParser(argparse.ArgumentParser):
    def error(self, message):
        # argparse messages may embed arbitrary choices, option names or values.
        # Keep useful static usage and a fixed code, never the untrusted message.
        self.print_usage(sys.stderr)
        self.exit(2, "INPUT_OR_RESPONSE_INVALID\n")


def parser():
    root = PrivateArgumentParser(prog="guardian", description=__doc__)
    root.add_argument("--version", action="version", version=VERSION)
    subs = root.add_subparsers(dest="command", required=True)
    for command in ("interview", "check", "analyze", "plan"):
        sub = subs.add_parser(command)
        sub.add_argument("--output", help="Explicitly save redacted JSON to a NEW local file; never overwrites")
        if command != "check":
            sub.add_argument("--input", required=command in {"analyze", "plan"}, help="Local interview state, guardian-offline/0.1 fixture, or saved check report; never a live config")
        if command != "interview":
            sub.add_argument("--target-ref", required=True, help="Task alias, not username or hostname")
        if command == "check":
            sub.add_argument("--entry-file", help="Explicit absolute local hydrated environment-entry JSON; POSIX reader only, never authorization")
            sub.add_argument("--target-os", choices=["macos", "windows"], required=True)
            sub.add_argument("--target-kind", choices=["local", "vm", "vps"], default="local")
            sub.add_argument("--namespace", choices=["desktop", "sandbox", "guest", "remote", "unknown"], default="unknown")
            sub.add_argument("--execution-location", choices=["native_local", "cloud", "ssh", "wsl", "virtualized", "unknown"], default="unknown")
            sub.add_argument("--user-context", choices=["same", "different", "unknown"], default="unknown")
            sub.add_argument("--confirm-target", action="store_true")
            sub.add_argument("--authorize-audit", action="store_true")
    return root


def validate_windows_output_path(value):
    """Syntax rejection only, never an ACL/local-drive or reparse-point proof."""
    if (type(value) is not str or not 4 <= len(value) <= 4096
            or not value[0].isascii() or not value[0].isalpha()
            or value[1:3] != ':\\' or '/' in value
            or ntpath.normpath(value) != value):
        raise GuardianError('UNSAFE_OR_OFFLINE_PATH', 3)
    reserved = {'CON', 'PRN', 'AUX', 'NUL', 'CONIN$', 'CONOUT$'}
    reserved.update(prefix + suffix for prefix in ('COM', 'LPT')
                    for suffix in '123456789¹²³')
    for part in value[3:].split('\\'):
        if (not part or part.endswith((' ', '.'))
                or any(ord(c) < 32 or ord(c) == 127 or c in '<>:"|?*' for c in part)
                or part.split('.')[0].rstrip(' .').upper() in reserved):
            raise GuardianError('UNSAFE_OR_OFFLINE_PATH', 3)
    return value


def save_new(path, text):
    if sys.platform == 'win32':
        validate_windows_output_path(str(path))
    p = Path(path)
    if str(path).startswith(("//", "\\\\")) or unsafe_symlink(p):
        raise GuardianError("UNSAFE_OR_OFFLINE_PATH", 3)
    try:
        fd = os.open(str(p), os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        with os.fdopen(fd, "w", encoding="utf-8") as stream:
            stream.write(text)
    except OSError:
        raise GuardianError("OUTPUT_SAVE_FAILED", 3) from None


def main(argv=None):
    # JSON CLI output is always UTF-8, including Windows redirected stdout.
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="strict")
    args = parser().parse_args(argv)
    code = 0
    try:
        target = getattr(args, "target_ref", None)
        if target:
            alias(target)
        if args.command == "check":
            entry_request = None
            if args.entry_file:
                import inventory_cli
                try:
                    entry_request = inventory_cli.read_request(args.entry_file)
                except inventory_cli.InputError as exc:
                    raise GuardianError(exc.code, 3) from None
                except (OSError, ValueError, TypeError, RecursionError):
                    raise GuardianError('INPUT_OR_RESPONSE_INVALID') from None
            report = native_check(args, entry_request=entry_request)
        else:
            obj = load_json(args.input) if args.input else {}
            report = interview(obj) if args.command == "interview" else analyze(obj, target, args.command == "plan")
    except KeyboardInterrupt:
        report = base(args.command)
        report.update(execution_status="interrupted", inventory_readiness="interrupted")
        finding(report, "USER_CANCELLED")
    except GuardianError as error:
        report = base(args.command)
        report.update(execution_status="blocked", inventory_readiness="blocked")
        finding(report, error.code)
        code = error.exit_code
    except Exception:
        report = base(args.command)
        report.update(execution_status="failed", inventory_readiness="blocked")
        finding(report, "COLLECTOR_INTERNAL_FAILURE")
        code = 4
    text = json.dumps(redact(report), ensure_ascii=False, indent=2) + "\n"
    # Cancellation already observed by this entrypoint cannot authorize a new
    # export, including USER_CANCELLED surfaced through a blocked error report.
    # Interrupts after save_new has begun remain a separate writer limitation.
    cancelled = (report.get("execution_status") == "interrupted"
                 or any(item.get("code") == "USER_CANCELLED"
                        for item in report.get("findings", [])))
    if args.output and not cancelled:
        try:
            save_new(args.output, text)
        except GuardianError as error:
            finding(report, error.code)
            code = error.exit_code
            text = json.dumps(redact(report), ensure_ascii=False, indent=2) + "\n"
    sys.stdout.write(text)
    return code


if __name__ == "__main__":
    raise SystemExit(main())
