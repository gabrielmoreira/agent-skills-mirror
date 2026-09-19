#!/usr/bin/env python3
"""Discover a caller flow's transitive subflow dependency tree from local XML.

Reads only the flow-meta.xml files already retrieved to disk (offline,
deterministic — never queries the org). Builds the transitive <subflows> graph,
topologically sorts it leaves-first, classifies each node
migratable / blocked / missing, and reports so a caller can be migrated in
dependency order and never deployed when a dependency can't be migrated.

Usage:
    discover_subflow_tree.py <flows_dir> (<caller.flow-meta.xml> ... | --all) [--json OUT]

Exit codes:
    0  clean tree — every node is migratable
    1  >=1 node blocked / missing / cyclic (do NOT deploy the caller)
    2  usage error
"""

import argparse
import json
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

NS = {'sf': 'http://soap.sforce.com/2006/04/metadata'}

sys.path.insert(0, str(Path(__file__).resolve().parent))
from subflow_names import migrated_dc_flow_name  # noqa: E402


def _findall(el, tag):
    """Direct children with or without the metadata namespace."""
    r = el.findall(f'sf:{tag}', namespaces=NS)
    return r if r else el.findall(tag)


def _findtext(el, tag):
    r = el.findtext(f'sf:{tag}', namespaces=NS)
    return r if r is not None else el.findtext(tag)


def _index_flows(flows_dir):
    """API name (filename stem) -> Path for every *.flow-meta.xml in flows_dir."""
    index = {}
    for p in sorted(Path(flows_dir).glob('*.flow-meta.xml')):
        api_name = p.name[:-len('.flow-meta.xml')]
        index[api_name] = p
    return index


def _parse_flow(path):
    """Return (processType, has_screens, [referenced_subflow_api_names])."""
    root = ET.parse(path).getroot()
    process_type = _findtext(root, 'processType')
    has_screens = len(_findall(root, 'screens')) > 0
    refs = []
    for sf_el in _findall(root, 'subflows'):
        fn = _findtext(sf_el, 'flowName')
        if fn:
            refs.append(fn)
    return process_type, has_screens, refs


def _classify(api_name, path, process_type, has_screens):
    """Return (status, reason) for a resolvable node."""
    if process_type != 'FieldServiceMobile':
        return 'blocked', (
            f"processType is '{process_type}', not 'FieldServiceMobile' — "
            "cannot become a DataCaptureFlow"
        )
    if not has_screens:
        return 'blocked', (
            "no <screens> element — pure automation flow, cannot become a "
            "DataCaptureFlow"
        )
    return 'migratable', ''


def build_tree(flows_dir, callers):
    """Build the transitive dependency tree for the given caller flow paths.

    Returns {"order": [...leaves first...], "blocked": [...], "hasBlockers": bool}.
    """
    index = _index_flows(flows_dir)

    nodes = {}          # api_name -> node dict
    callers_of = {}     # api_name -> set of api_names that reference it
    order = []          # post-order DFS accumulation (leaves first)
    perm = set()        # fully processed
    stack = []          # current recursion path (for cycle detection)

    def record_caller(child, parent):
        if parent is not None:
            callers_of.setdefault(child, set()).add(parent)

    def visit(api_name, path, depth, parent):
        record_caller(api_name, parent)

        if api_name in perm:
            # Already ordered; just note the (possibly deeper) reachability.
            if parent is not None and api_name in nodes:
                nodes[api_name]['callers'] = sorted(callers_of.get(api_name, set()))
            return

        if api_name in stack:
            # Cycle: mark blocked, do not descend again.
            node = nodes.get(api_name)
            if node is None:
                node = {
                    'apiName': api_name, 'file': str(path) if path else None,
                    'migratedDcName': migrated_dc_flow_name(api_name),
                    'processType': None, 'status': 'blocked',
                    'reason': 'part of a subflow cycle — cannot be topologically ordered',
                    'depth': depth, 'callers': sorted(callers_of.get(api_name, set())),
                }
                nodes[api_name] = node
            else:
                node['status'] = 'blocked'
                node['reason'] = 'part of a subflow cycle — cannot be topologically ordered'
            return

        stack.append(api_name)

        if path is None:
            # Referenced but no file on disk.
            nodes[api_name] = {
                'apiName': api_name, 'file': None,
                'migratedDcName': migrated_dc_flow_name(api_name),
                'processType': None, 'status': 'missing',
                'reason': 'referenced subflow has no .flow-meta.xml on disk',
                'depth': depth, 'callers': sorted(callers_of.get(api_name, set())),
            }
            stack.pop()
            perm.add(api_name)
            order.append(nodes[api_name])
            return

        process_type, has_screens, refs = _parse_flow(path)

        # Descend into children first (post-order => leaves land earlier).
        for ref in refs:
            visit(ref, index.get(ref), depth + 1, api_name)

        status, reason = _classify(api_name, path, process_type, has_screens)
        node = nodes.get(api_name)
        if node is None:
            node = {'apiName': api_name}
            nodes[api_name] = node
        # Preserve a cycle mark set while descending; otherwise use classification.
        if node.get('status') == 'blocked' and 'cycle' in node.get('reason', ''):
            pass
        else:
            node['status'] = status
            node['reason'] = reason
        node.update({
            'file': str(path),
            'migratedDcName': migrated_dc_flow_name(api_name),
            'processType': process_type,
            'depth': depth,
            'callers': sorted(callers_of.get(api_name, set())),
        })

        stack.pop()
        perm.add(api_name)
        order.append(node)

    for caller in callers:
        cpath = Path(caller)
        api_name = cpath.name[:-len('.flow-meta.xml')]
        visit(api_name, cpath, 0, None)

    blocked = [n for n in order if n['status'] != 'migratable']
    return {'order': order, 'blocked': blocked, 'hasBlockers': bool(blocked)}


def _render_summary(tree):
    lines = ['Subflow dependency tree — migrate in this order (leaves first):', '']
    for i, n in enumerate(tree['order'], 1):
        mark = {'migratable': 'OK', 'blocked': 'BLOCKED', 'missing': 'BLOCKED'}[n['status']]
        lines.append(f"  {i}. [{mark}] {n['apiName']}  ->  {n['migratedDcName']}")
        if n['status'] != 'migratable':
            lines.append(f"        reason: {n['reason']}")
    if tree['hasBlockers']:
        lines.append('')
        lines.append('BLOCKED: one or more dependencies cannot be migrated — '
                     'do NOT deploy the caller until these are resolved:')
        for n in tree['blocked']:
            lines.append(f"  - {n['apiName']} ({n['status']}): {n['reason']}")
    return '\n'.join(lines)


def main(argv=None):
    parser = argparse.ArgumentParser(add_help=True)
    parser.add_argument('flows_dir')
    parser.add_argument('callers', nargs='*')
    parser.add_argument('--all', action='store_true',
                        help='treat every FieldServiceMobile flow with screens as a root')
    parser.add_argument('--json', dest='json_out', default=None)
    args = parser.parse_args(argv)

    if not args.all and not args.callers:
        parser.error('provide at least one caller flow path or --all')

    if args.all:
        index = _index_flows(args.flows_dir)
        callers = []
        for api_name, path in index.items():
            pt, screens, _ = _parse_flow(path)
            if pt == 'FieldServiceMobile' and screens:
                callers.append(str(path))
    else:
        callers = args.callers

    tree = build_tree(args.flows_dir, callers)

    print(_render_summary(tree))
    if args.json_out:
        Path(args.json_out).write_text(json.dumps(tree, indent=2))

    return 1 if tree['hasBlockers'] else 0


if __name__ == '__main__':
    try:
        sys.exit(main())
    except SystemExit:
        raise
    except Exception as exc:  # noqa: BLE001
        print(f'ERROR: {exc}', file=sys.stderr)
        sys.exit(2)
