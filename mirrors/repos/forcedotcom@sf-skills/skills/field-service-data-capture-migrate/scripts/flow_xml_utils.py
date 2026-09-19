#!/usr/bin/env python3
"""
Namespace-aware ElementTree helpers for Salesforce Flow metadata XML.

Flow metadata may or may not declare the Salesforce metadata namespace, so every
lookup tries the namespaced form first and falls back to the plain tag. These
helpers are the single shared source for flow_input.py, convert_to_dc_spec.py,
and analyze_flow.py. This module depends on nothing else in the skill, so it is
safe for any of them to import (no circular import).
"""

import xml.etree.ElementTree as ET
from typing import Optional

NS = {'sf': 'http://soap.sforce.com/2006/04/metadata'}


def _findtext(el: ET.Element, tag: str) -> Optional[str]:
    """Find direct-child text with or without namespace."""
    result = el.findtext(f'sf:{tag}', namespaces=NS)
    if result is None:
        result = el.findtext(tag)
    return result


def _findall(el: ET.Element, tag: str) -> list:
    """Find direct children with or without namespace."""
    results = el.findall(f'sf:{tag}', namespaces=NS)
    if not results:
        results = el.findall(tag)
    return results


def _findall_deep(el: ET.Element, tag: str) -> list:
    """Find all descendants with or without namespace."""
    results = el.findall(f'.//sf:{tag}', namespaces=NS)
    if not results:
        results = el.findall(f'.//{tag}')
    return results
