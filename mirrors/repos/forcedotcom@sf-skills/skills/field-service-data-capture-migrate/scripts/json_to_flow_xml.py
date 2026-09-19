#!/usr/bin/env python3
"""
Convert Tooling API Flow Metadata JSON to Flow XML.

Following the mechanical JSON ↔ XML mapping rule from project-codey PR #975:
- JSON key → XML element
- JSON array → repeated XML elements
- Typed value wrappers preserved: {"stringValue": "X"} → <stringValue>X</stringValue>

Usage:
    json_to_flow_xml.py <input.json> <output.flow-meta.xml>
    cat metadata.json | json_to_flow_xml.py - <output.flow-meta.xml>
"""

import json
import sys
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any, Dict, List, Union


def json_value_to_xml(parent: ET.Element, key: str, value: Any) -> None:
    """
    Convert a JSON value to XML element(s) under parent.

    Mapping rule from PR #975:
    - Scalar → text content
    - Object → nested elements
    - Array → repeated elements with same tag name
    """
    if value is None:
        # Omit null values (not represented in Flow XML)
        return

    if isinstance(value, bool):
        # Boolean → lowercase string
        elem = ET.SubElement(parent, key)
        elem.text = str(value).lower()

    elif isinstance(value, (int, float)):
        # Number → string
        elem = ET.SubElement(parent, key)
        elem.text = str(value)

    elif isinstance(value, str):
        # String → text content
        elem = ET.SubElement(parent, key)
        elem.text = value

    elif isinstance(value, list):
        # Array → repeated elements
        for item in value:
            json_value_to_xml(parent, key, item)

    elif isinstance(value, dict):
        # Object → nested element with children
        elem = ET.SubElement(parent, key)
        for child_key, child_value in value.items():
            json_value_to_xml(elem, child_key, child_value)

    else:
        raise ValueError(f"Unsupported value type: {type(value)} for key '{key}'")


def json_to_flow_xml(metadata_json: Dict[str, Any]) -> str:
    """
    Convert Tooling API Flow Metadata JSON to Flow XML string.

    Args:
        metadata_json: The "Metadata" object from Tooling API Flow sObject

    Returns:
        XML string with <?xml?> declaration and <Flow> root
    """
    # Create root <Flow> element
    root = ET.Element("Flow")

    # Convert all top-level keys to XML elements
    for key, value in metadata_json.items():
        json_value_to_xml(root, key, value)

    # Pretty-print with indentation
    indent_tree(root)

    # Generate XML string WITHOUT namespace (simpler for testing)
    # Salesforce accepts Flow XML without explicit xmlns on root
    xml_str = ET.tostring(root, encoding='unicode', method='xml')

    # Add XML declaration
    return f'<?xml version="1.0" encoding="UTF-8"?>\n{xml_str}'


def indent_tree(elem: ET.Element, level: int = 0) -> None:
    """Add pretty-print indentation to XML tree (4 spaces per level)."""
    indent = "    "
    i = "\n" + level * indent

    if len(elem):
        if not elem.text or not elem.text.strip():
            elem.text = i + indent
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
        for child in elem:
            indent_tree(child, level + 1)
        if not child.tail or not child.tail.strip():
            child.tail = i
    else:
        if level and (not elem.tail or not elem.tail.strip()):
            elem.tail = i


def main() -> int:
    """CLI entry point."""
    if len(sys.argv) != 3:
        print("Usage: json_to_flow_xml.py <input.json> <output.flow-meta.xml>", file=sys.stderr)
        print("       cat metadata.json | json_to_flow_xml.py - <output.flow-meta.xml>", file=sys.stderr)
        return 2

    input_path = sys.argv[1]
    output_path = sys.argv[2]

    # Read input JSON
    if input_path == "-":
        metadata_json = json.load(sys.stdin)
    else:
        with open(input_path, 'r') as f:
            metadata_json = json.load(f)

    # Convert to XML
    try:
        xml_str = json_to_flow_xml(metadata_json)
    except Exception as e:
        print(f"ERROR: Failed to convert JSON to XML: {e}", file=sys.stderr)
        return 1

    # Write output
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w') as f:
        f.write(xml_str)

    print(f"Converted JSON to Flow XML: {output_path}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
