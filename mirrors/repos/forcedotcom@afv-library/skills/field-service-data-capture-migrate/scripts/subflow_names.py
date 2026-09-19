#!/usr/bin/env python3
"""Single source of truth for the migrated-subflow naming rule.

Both transform_flow.py (which rewrites <subflows><flowName> to the DC name) and
discover_subflow_tree.py (which predicts that name to resolve the tree) import
this so a caller's rewritten reference always matches the migrated leaf's
deployed name. Standard library only; no skill dependencies (safe to import
anywhere — no circular import).

Naming note: this is the migrated *flow API name*, unrelated to the DC component
`dcName` (the Name-input extensionName) used elsewhere in the skill.
"""

# Explicit source-name -> migrated-name overrides for known mismatches where the
# plain suffix rule is wrong. Add an entry here rather than introducing a fuzzy
# name normalizer.
OVERRIDES = {
    'SDO_FSL_Image_Capture_Flow_SDO': 'SDO_FSL_Image_Capture_DC',
}


def migrated_dc_flow_name(source_name: str, dc_suffix: str = '_DC') -> str:
    """The API name a migrated subflow will deploy as.

    Must match exactly what transform_flow.py rewrites <subflows><flowName> to,
    so intra-tree references resolve in the bundled dry-run.
    """
    if source_name in OVERRIDES:
        return OVERRIDES[source_name]
    if source_name.endswith(dc_suffix):
        return source_name
    return source_name + dc_suffix


if __name__ == '__main__':
    import sys
    if len(sys.argv) < 2 or sys.argv[1] in ('-h', '--help'):
        print("Usage: subflow_names.py <source_name> [--dc-suffix SUFFIX]", file=sys.stderr)
        sys.exit(2)

    source_name = sys.argv[1]
    dc_suffix = '_DC'

    if '--dc-suffix' in sys.argv:
        idx = sys.argv.index('--dc-suffix')
        if idx + 1 < len(sys.argv):
            dc_suffix = sys.argv[idx + 1]

    print(migrated_dc_flow_name(source_name, dc_suffix))
