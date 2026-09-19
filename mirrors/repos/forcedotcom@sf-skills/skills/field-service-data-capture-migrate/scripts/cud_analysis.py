#!/usr/bin/env python3
"""
Ordinal CUD-placement analysis for FSM → DataCaptureFlow migration (WI-8).

DataCaptureFlow requires every record create/update/delete (CUD) to run at the
END of the flow, after all screens and data collection. FSM allows CUD anywhere.
A mid-flow CUD deploys but executes in the wrong order — silent data corruption.

This module computes, over the flow graph:
  1. execution order (BFS from <start>);
  2. each CUD's position relative to the last screen / last recordLookup;
  3. a conservative safe/unsafe verdict for consolidating each mid-flow CUD.

Depends only on flow_xml_utils (no import cycle — safe to import from both
analyze_flow.py and convert_to_dc_spec.py).
"""

import xml.etree.ElementTree as ET
from dataclasses import dataclass, field, asdict
from typing import Dict, List, Tuple

from flow_xml_utils import _findtext, _findall, _findall_deep  # noqa: F401

CUD_TAGS = ("recordCreates", "recordUpdates", "recordDeletes")

# All named, connectable flow elements (document-order scan set).
_ELEMENT_TAGS = (
    "screens", "decisions", "assignments", "recordCreates", "recordUpdates",
    "recordDeletes", "recordLookups", "subflows", "loops",
)

_CONNECTOR_TAGS = (
    "connector", "defaultConnector", "nextValueConnector", "noMoreValuesConnector",
)


def _op_of_tag(tag: str) -> str:
    return {"recordCreates": "create", "recordUpdates": "update",
            "recordDeletes": "delete"}[tag]


def _targets_of(el: ET.Element) -> List[str]:
    """All connector targetReferences carried by one element (incl. decision rules)."""
    out: List[str] = []
    for ct in _CONNECTOR_TAGS:
        for conn in _findall(el, ct):
            t = _findtext(conn, "targetReference")
            if t:
                out.append(t)
    for rule in _findall(el, "rules"):
        for conn in _findall(rule, "connector"):
            t = _findtext(conn, "targetReference")
            if t:
                out.append(t)
    return out


def _element_index(root: ET.Element) -> Dict[str, Tuple[str, ET.Element]]:
    """Map element api-name -> (localTag, element) for named flow elements."""
    idx: Dict[str, Tuple[str, ET.Element]] = {}
    for tag in _ELEMENT_TAGS:
        for el in _findall_deep(root, tag):
            name = _findtext(el, "name")
            if name and name not in idx:
                idx[name] = (tag, el)
    return idx


def _start_target(root: ET.Element) -> str:
    for s in _findall(root, "start"):
        for conn in _findall(s, "connector"):
            t = _findtext(conn, "targetReference")
            if t:
                return t
    return ""


def execution_order(root: ET.Element) -> List[str]:
    """Element api-names in BFS execution order from <start>. Cycle-guarded."""
    idx = _element_index(root)
    start = _start_target(root)
    visited: set = set()
    order: List[str] = []
    queue: List[str] = [start] if start else []
    while queue:
        n = queue.pop(0)
        if not n or n in visited or n not in idx:
            continue
        visited.add(n)
        order.append(n)
        queue.extend(_targets_of(idx[n][1]))
    return order


@dataclass
class CudNode:
    name: str
    op: str
    position: int
    after_last_screen: bool
    container: str = "top"
    verdict: str = "compliant"
    blockers: List[str] = field(default_factory=list)


@dataclass
class CudPlacementReport:
    has_midflow: bool
    cud_nodes: List[CudNode]

    def to_dict(self) -> dict:
        return asdict(self)


def _cud_names(root: ET.Element) -> Dict[str, str]:
    """api-name -> op for every CUD element in the flow."""
    out: Dict[str, str] = {}
    for tag in CUD_TAGS:
        for el in _findall_deep(root, tag):
            name = _findtext(el, "name")
            if name:
                out[name] = _op_of_tag(tag)
    return out


def _loop_member_names(root: ET.Element) -> Dict[str, str]:
    """api-name -> loop name for elements inside a loop body.

    Body = everything reachable from the loop's nextValueConnector, stopping at
    the loop node itself and at the noMoreValuesConnector target (loop exit).
    """
    idx = _element_index(root)
    members: Dict[str, str] = {}
    for lp in _findall_deep(root, "loops"):
        loop_name = _findtext(lp, "name")
        if not loop_name:
            continue
        exits = {_findtext(c, "targetReference")
                 for c in _findall(lp, "noMoreValuesConnector")}
        starts = [_findtext(c, "targetReference")
                  for c in _findall(lp, "nextValueConnector")]
        seen: set = set()
        queue = [s for s in starts if s]
        while queue:
            n = queue.pop(0)
            if not n or n in seen or n == loop_name or n in exits or n not in idx:
                continue
            seen.add(n)
            members.setdefault(n, loop_name)
            queue.extend(_targets_of(idx[n][1]))
    return members


def _decision_branch_only(root: ET.Element) -> Dict[str, str]:
    """api-name -> decision name for elements reachable ONLY via a decision branch.

    An element is 'branch-only' if every inbound connector that reaches it comes
    from a decision (either <rules><connector> OR <defaultConnector>), not from
    <start> or a plain sequential connector from a non-decision element.
    """
    idx = _element_index(root)
    branch_sources: Dict[str, str] = {}  # target -> decision name (via rule OR default)
    other_inbound: set = set()           # targets reached by non-decision connectors

    start = _start_target(root)
    if start:
        other_inbound.add(start)

    for name, (tag, el) in idx.items():
        if tag == "decisions":
            # Both rule connectors AND default connectors are conditional branches
            for rule in _findall(el, "rules"):
                for conn in _findall(rule, "connector"):
                    t = _findtext(conn, "targetReference")
                    if t:
                        branch_sources.setdefault(t, name)
            for conn in _findall(el, "defaultConnector"):
                t = _findtext(conn, "targetReference")
                if t:
                    branch_sources.setdefault(t, name)
        else:
            # Non-decision connectors make targets unconditionally reachable
            for ct in _CONNECTOR_TAGS:
                for conn in _findall(el, ct):
                    t = _findtext(conn, "targetReference")
                    if t:
                        other_inbound.add(t)

    return {t: dec for t, dec in branch_sources.items() if t not in other_inbound}


def _cud_output_refs(cud_el: ET.Element, op: str) -> List[str]:
    """Reference tokens a downstream element would use to consume this CUD's result."""
    tokens: List[str] = []
    name = _findtext(cud_el, "name")
    if name:
        tokens.append(name)
    assign_id = _findtext(cud_el, "assignRecordIdToReference")
    if assign_id:
        tokens.append(assign_id)
    out_ref = _findtext(cud_el, "outputReference")
    if out_ref:
        tokens.append(out_ref)
    return tokens


def _downstream_reference(root: ET.Element, order: List[str], cud_name: str,
                          tokens: List[str]) -> str:
    """Name of the first element after cud_name in `order` that references a token, else ''."""
    idx = _element_index(root)
    try:
        after = order[order.index(cud_name) + 1:]
    except ValueError:
        after = []
    for name in after:
        if name not in idx:
            continue
        blob = ET.tostring(idx[name][1], encoding="unicode")
        for tok in tokens:
            # Match the token as a whole reference (avoid substring false hits).
            # Includes: element text (>tok<), dotted references (tok.), and
            # merge-field syntax ({!tok} or {!tok.Field}).
            if (f">{tok}<" in blob or f"{tok}." in blob or
                    f"{{!{tok}}}" in blob or f"{{!{tok}." in blob):
                return name
    return ""


def _check_input_references(cud_el: ET.Element, root: ET.Element) -> str:
    """Check if create's inputAssignments reference variables that survive migration.

    Returns blocker message if any input is unresolvable, else empty string.
    A reference is safe if its root resolves to:
      - a screen field name (any <screens><fields><name>)
      - a screen element name (any <screens><name>)
      - a DC standard input variable (recordId, parentRecordId, parentObjectType)
    """
    idx = _element_index(root)

    # Collect all screen field names and screen names
    safe_refs: set = set()
    for tag, el in idx.values():
        if tag == "screens":
            screen_name = _findtext(el, "name")
            if screen_name:
                safe_refs.add(screen_name)
            for fld in _findall(el, "fields"):
                fld_name = _findtext(fld, "name")
                if fld_name:
                    safe_refs.add(fld_name)

    # DC standard input variables (confirmed from build_flow.py line 1176)
    safe_refs.update(["recordId", "parentRecordId", "parentObjectType"])

    # Check each inputAssignments elementReference
    for inp_asg in _findall(cud_el, "inputAssignments"):
        for val in _findall(inp_asg, "value"):
            ref = _findtext(val, "elementReference")
            if ref:
                # Extract root (part before first dot)
                root_ref = ref.split(".")[0].split("!")[0].strip("{}")
                if root_ref and root_ref not in safe_refs:
                    return f"input references {root_ref} which does not survive migration"

    return ""


def _has_screen_or_lookup_downstream(root: ET.Element, cud_name: str,
                                     idx: Dict[str, Tuple[str, ET.Element]]) -> bool:
    """Check if any screen or recordLookup is reachable forward from cud_name.

    Uses connector-based reachability (BFS), mirroring detect_ceiling_violations.
    """
    if cud_name not in idx:
        return False

    visited: set = set()
    frontier = _targets_of(idx[cud_name][1])

    while frontier:
        nxt = frontier.pop()
        if nxt in visited or nxt not in idx:
            continue
        visited.add(nxt)

        tag = idx[nxt][0]
        if tag in ("screens", "recordLookups"):
            return True

        frontier.extend(_targets_of(idx[nxt][1]))

    return False


def _completion_bypasses(root: ET.Element, idx: Dict[str, Tuple[str, ET.Element]],
                         cud_name: str) -> bool:
    """True if some path start->completion reaches a terminal WITHOUT the CUD.

    A create is safe to auto-consolidate only when unconditional (every
    completion path runs it). If a completion terminal is reachable while
    skipping the CUD, the create is conditional -> unsafe to consolidate.
    """
    start = _start_target(root)
    if not start or cud_name not in idx:
        return False  # unreachable/degenerate handled elsewhere; don't add noise
    seen: set = set()
    queue = [start]
    while queue:
        n = queue.pop(0)
        if not n or n == cud_name or n in seen or n not in idx:
            continue
        seen.add(n)
        outs = [t for t in _targets_of(idx[n][1]) if t in idx]
        if not outs:
            return True  # reached a completion terminal without the CUD
        queue.extend(outs)
    return False


def analyze_cud_placement(root: ET.Element) -> CudPlacementReport:
    order = execution_order(root)
    pos = {name: i for i, name in enumerate(order)}
    idx = _element_index(root)
    cuds = _cud_names(root)

    loop_members = _loop_member_names(root)
    branch_only = _decision_branch_only(root)

    nodes: List[CudNode] = []
    has_midflow = False
    for name, op in cuds.items():
        p = pos.get(name, -1)

        # Determine after_last_screen via forward reachability (C2 fix).
        # A CUD is compliant (after last screen) ONLY IF no screen/recordLookup
        # is reachable downstream from it.
        after = (p != -1 and not _has_screen_or_lookup_downstream(root, name, idx))
        node = CudNode(name=name, op=op, position=p, after_last_screen=after)

        # Check for container issues first (loop or decision-branch) even if after barrier
        if name in loop_members:
            node.container = f"loop:{loop_members[name]}"
            node.verdict = "unsafe_manual"
            node.blockers.append(f"inside loop {loop_members[name]}")
            has_midflow = True
        elif name in branch_only and not after:
            # Branch-only CUD that's mid-flow (has screens downstream)
            # Post-screen decision branches are allowed in Data Capture
            node.container = f"decisionBranch:{branch_only[name]}"
            node.verdict = "unsafe_manual"
            node.blockers.append(
                f"mid-flow decision branch {branch_only[name]} (screens downstream)")
            has_midflow = True
        elif p == -1:
            # Unreachable CUD: cannot determine ordering, requires manual review
            node.verdict = "unsafe_manual"
            node.blockers.append(f"unreachable from start (no incoming connector)")
            has_midflow = True
        elif after:
            # Truly compliant - no screen/lookup downstream and not in a problematic container
            # BUT: for creates, still check input references (I1 fix)
            cud_el = idx[name][1]
            input_blocker = ""
            if op == "create":
                input_blocker = _check_input_references(cud_el, root)

            if input_blocker:
                node.verdict = "unsafe_manual"
                node.blockers.append(input_blocker)
                has_midflow = True
            else:
                node.verdict = "compliant"
        else:
            # Mid-flow CUD, check for downstream references and input validity
            has_midflow = True
            cud_el = idx[name][1]
            tokens = _cud_output_refs(cud_el, op)
            ref = _downstream_reference(root, order, name, tokens)

            # I1 fix: for creates, check input assignments BEFORE classifying as safe
            input_blocker = ""
            if op == "create":
                input_blocker = _check_input_references(cud_el, root)

            if ref:
                node.verdict = "unsafe_manual"
                node.blockers.append(f"output referenced by {ref}")
            elif input_blocker:
                node.verdict = "unsafe_manual"
                node.blockers.append(input_blocker)
            elif op == "create" and _completion_bypasses(root, idx, name):
                # WI-8 residual fix: conditional create (bypassable via some completion path)
                node.verdict = "unsafe_manual"
                node.blockers.append(
                    "conditional: some completion paths bypass this create; "
                    "consolidating would make the write unconditional")
            else:
                node.verdict = "safe_consolidate"
        nodes.append(node)

    nodes.sort(key=lambda n: (n.position if n.position >= 0 else 1_000_000, n.name))
    return CudPlacementReport(has_midflow=has_midflow, cud_nodes=nodes)
