"""
Manual review flag detection for field-service-data-capture-migrate.

STUB: This module is not yet implemented. It returns an empty list.
See docs/superpowers/specs/2026-08-02-manual-review-flags-design.md for the design.
"""

import xml.etree.ElementTree as ET
from typing import List, Dict, Any


def detect_manual_review_flags(root: ET.Element) -> List[Dict[str, Any]]:
    """Detect patterns that require manual review in Flow Builder before activation.

    Returns a list of Flag dicts, each with:
      - code: str         # e.g. "SCREEN_IN_LOOP"
      - element: str      # element name or screen field name
      - what: str         # one-line "what was found"
      - why: str          # why it needs manual review
      - recommendation: str  # how to fix it in Flow Builder

    STUB: Not yet implemented. Returns empty list.
    """
    return []


def build_excision_flag(element_name: str, code: str, why: str) -> Dict[str, Any]:
    """Build a Flag dict for a node excised at transform-time (not scan-time).

    Reuses the existing Flag contract: {code, element, what, why, recommendation}.
    Called by transform_flow.py's excise_and_placeholder — one call per excised node.
    """
    return {
        "code": code,
        "element": element_name,
        "what": f"{element_name} was dropped — not compliant with data capture",
        "why": why,
        "recommendation": (
            "Review the placeholder screen inserted at this point in the flow "
            "and redesign in Flow Builder if the dropped logic is needed."
        ),
    }
