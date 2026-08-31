#!/usr/bin/env python3
"""Single source of truth for the installed skill/runtime contract."""

from __future__ import annotations

SKILL_NAME = "us-undervalued-growth-screener"
SKILL_VERSION = "3.6.1"
SCHEMA_VERSION = 3
CONTRACT_REVISION = "3.5"
# Change this whenever contract semantics change. It intentionally differs from
# the human version so stale/cached runtimes are detected in serialized audits.
RUNTIME_FINGERPRINT = "ug-v3.6.1-claude-code-direct-fmp-20260830"


def runtime_metadata() -> dict[str, object]:
    return {
        "skill_name": SKILL_NAME,
        "skill_version": SKILL_VERSION,
        "schema_version": SCHEMA_VERSION,
        "contract_revision": CONTRACT_REVISION,
        "runtime_fingerprint": RUNTIME_FINGERPRINT,
    }
