#!/usr/bin/env python3
"""
Shared input ingestion and validation for the field-service-data-capture-migrate skill.

Both entry points (analyze_flow.py, convert_to_dc_spec.py) call
load_and_validate_flow() to parse and validate a Field Service Mobile Flow
metadata file before processing it. Validation is fail-fast: the first failing
check raises FlowValidationError with a machine-readable category. Non-fatal
issues (e.g. a missing apiVersion) are returned as a list of FlowWarning records
alongside the parsed root.

Offline only (FR-008): operates entirely on the provided file; no org connection.

Namespace helpers come from flow_xml_utils (the single shared source) and are
re-exported here so callers/tests can reference flow_input._findtext etc.
"""

import os
import xml.etree.ElementTree as ET
from typing import List, Optional, Tuple

from flow_xml_utils import NS, _findtext, _findall, _findall_deep  # noqa: F401

# Fatal validation categories (raised via FlowValidationError).
MISSING_ARG = 'MISSING_ARG'
FILE_NOT_FOUND = 'FILE_NOT_FOUND'
ENCODING = 'ENCODING'
MALFORMED_XML = 'MALFORMED_XML'
WRONG_TYPE = 'WRONG_TYPE'
MISSING_START = 'MISSING_START'
SCREENLESS = 'SCREENLESS'

# Non-fatal warning categories (returned, never raised).
MISSING_API_VERSION = 'MISSING_API_VERSION'

EXPECTED_PROCESS_TYPE = 'FieldServiceMobile'


class FlowValidationError(Exception):
    """Fatal input-validation failure. Carries a machine-readable category."""

    def __init__(self, category: str, message: str, element: Optional[str] = None):
        self.category = category
        self.message = message
        self.element = element
        super().__init__(message)


class FlowWarning:
    """Non-fatal input finding. Named FlowWarning to avoid shadowing builtin Warning."""

    def __init__(self, category: str, message: str, element: Optional[str] = None):
        self.category = category
        self.message = message
        self.element = element

    def __eq__(self, other) -> bool:
        return (isinstance(other, FlowWarning)
                and self.category == other.category
                and self.message == other.message
                and self.element == other.element)

    def __repr__(self) -> str:
        return f'FlowWarning(category={self.category!r}, element={self.element!r})'


def _read_source(path: str) -> bytes:
    """Read the file as bytes, or raise FILE_NOT_FOUND."""
    if not os.path.isfile(path):
        raise FlowValidationError(
            FILE_NOT_FOUND,
            f"[ERROR] Input file not found: '{path}'. Check the path and re-run.",
            element=path,
        )
    try:
        with open(path, 'rb') as f:
            return f.read()
    except OSError as e:
        raise FlowValidationError(
            FILE_NOT_FOUND,
            f"[ERROR] Could not read '{path}': {e}. Check the path and permissions.",
            element=path,
        )


def _decode(raw: bytes, path: str) -> str:
    """Decode bytes as UTF-8, transparently stripping a BOM. Raise ENCODING."""
    try:
        return raw.decode('utf-8-sig')
    except UnicodeDecodeError as e:
        raise FlowValidationError(
            ENCODING,
            f"[ERROR] Could not decode '{path}' as UTF-8: {e}. "
            f"Re-export the flow as UTF-8.",
            element=path,
        )


def _parse(text: str, path: str) -> ET.Element:
    """Parse decoded XML text into a root element, or raise MALFORMED_XML.

    Parse from re-encoded bytes: this avoids ElementTree's refusal to accept a
    str that still carries an <?xml ... encoding=?> declaration, and the BOM is
    already gone (stripped in _decode).
    """
    try:
        return ET.fromstring(text.encode('utf-8'))
    except ET.ParseError as e:
        position = getattr(e, 'position', None)
        line = position[0] if position else '?'
        raise FlowValidationError(
            MALFORMED_XML,
            f"[ERROR] Malformed XML in '{path}' at line {line}: {e}. "
            f"Re-export the flow from Setup.",
            element=str(line),
        )


def _check_process_type(root: ET.Element) -> None:
    """Raise WRONG_TYPE unless processType is FieldServiceMobile."""
    found = _findtext(root, 'processType')
    if found != EXPECTED_PROCESS_TYPE:
        shown = found if found else '(none)'
        raise FlowValidationError(
            WRONG_TYPE,
            f"[ERROR] processType is '{shown}', expected "
            f"'{EXPECTED_PROCESS_TYPE}'. Export a Field Service Mobile Flow.",
            element=shown,
        )


def _check_start(root: ET.Element) -> None:
    """Raise MISSING_START if no <start> element is present."""
    if not _findall(root, 'start'):
        raise FlowValidationError(
            MISSING_START,
            "[ERROR] No <start> element found. "
            "File may be truncated; re-export the flow.",
            element='start',
        )


def _check_screens(root: ET.Element) -> None:
    """Raise SCREENLESS if the flow has no <screens> element."""
    if not _findall_deep(root, 'screens'):
        raise FlowValidationError(
            SCREENLESS,
            "[ERROR] Flow has no screen components; nothing to migrate. "
            "Only screen-collecting Mobile Flows are supported.",
            element='screens',
        )


def _check_api_version(root: ET.Element) -> List[FlowWarning]:
    """Return a MISSING_API_VERSION warning when <apiVersion> is absent.

    A present apiVersion never warns, at any value: there is no defined minimum
    supported version (OQ-6 open). This discharges only the "not silent" half —
    absence of provenance is surfaced, not guessed.
    """
    if _findtext(root, 'apiVersion') is None:
        return [FlowWarning(
            MISSING_API_VERSION,
            "[WARNING] No <apiVersion> element found (version unspecified). "
            "Verify the migrated flow manually.",
            element='apiVersion',
        )]
    return []


def load_and_validate_flow(path: str) -> Tuple[ET.Element, List[FlowWarning]]:
    """Parse and validate a Field Service Mobile Flow file.

    Fail-fast: the first failing check raises FlowValidationError. On success
    returns (parsed <Flow> root, list of non-fatal warnings). Order matters —
    each step depends on the previous succeeding, and structural checks
    (WRONG_TYPE) precede content checks (SCREENLESS).
    """
    raw = _read_source(path)
    text = _decode(raw, path)
    root = _parse(text, path)
    _check_process_type(root)
    _check_start(root)
    _check_screens(root)
    warnings = _check_api_version(root)
    return root, warnings
