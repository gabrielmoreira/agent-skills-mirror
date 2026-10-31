"""Edit ops on the captured requests: the patch hook between the units and the replay call.

A step's request carries the agent's texts verbatim (agentsrc.py), so an edit to the .agent
can be scored without a deploy: apply the same edit to every captured request it would
change, and replay those. One op:

    {"id": "add-copy-rule", "target": "node:cart_and_checkout", "op": "replace",
     "find": "ADD: Pass the productCode from the search results to {!@actions.AddToCart}.",
     "with": "ADD: Copy the productCode exactly as the search results give it to {!@actions.AddToCart}."}

Targets:
  node:<name>          the node's instruction text (the last system message, up to
                       "\\n\\n# CONTEXT") in the steps of that node
  system               the first system message: platform preamble + system.instructions
  tool:<name>          a tool's description (action or transition), wherever it is offered
  transition:<name>    the same; the platform suffix of a transition stays in place
  tool:<name>.<param>  a parameter's description
Ops:
  replace {find, with}   delete {find}   insert_after / insert_before {anchor, text}
  set_description {text} (tool / transition targets: the whole description)
Optional fields: id (default op<n>), nodes (only the steps of these nodes), all (every
occurrence; without it a find that occurs twice in one step is an error), note.

find / anchor / with / text are .agent source text, dedented, merge fields as written:
{!@actions.X} renders as X, and any other merge field matches whatever value it rendered to
(the same field in with / text gets that value back). A merge field may not start or end a
find, two may not be adjacent, and with / text may only use fields of their find / anchor.
Descriptions take no merge fields. Inserted text goes in exactly as given: start it with a
newline to add a line after an anchor. Ops apply in order, each to the result of the ones
before; a step no op changes keeps its request byte-identical.

Approximate: a line whose text starts with a merge field renders without its leading
whitespace. That is modelled within the op's own lines, not for a line an edit creates by
joining source text with op text.
"""

import json
import re
from collections import Counter, defaultdict

from . import SCHEMA_COVERAGE, SCHEMA_PATCH
from .agentsrc import CONTEXT_MARKER, MERGE_FIELD, TRANSITION_SUFFIX, fragment_pattern, render_text, value_fields

OPS = ("replace", "delete", "insert_after", "insert_before", "set_description")
OP_FIELDS = {"replace": ("find", "with"), "delete": ("find",), "insert_after": ("anchor", "text"),
             "insert_before": ("anchor", "text"), "set_description": ("text",)}
COMMON_FIELDS = ("id", "target", "op", "nodes", "all", "note")
_TARGET = re.compile(r"^(?:(node|tool|transition):(\w+)(?:\.(\w+))?|(system))$")


class PatchError(ValueError):
    pass


class Op:
    """One validated edit op."""

    def __init__(self, spec, index):
        if not isinstance(spec, dict):
            raise PatchError(f"op {index + 1}: not a JSON object")
        self.id = str(spec.get("id") or f"op{index + 1}")
        where = f"op {self.id}"
        self.op = spec.get("op")
        if self.op not in OPS:
            raise PatchError(f"{where}: op must be one of {', '.join(OPS)}")
        unknown = set(spec) - set(COMMON_FIELDS) - set(OP_FIELDS[self.op])
        if unknown:
            raise PatchError(f"{where}: fields {sorted(unknown)} do not apply to {self.op}")
        for field in OP_FIELDS[self.op]:
            if not isinstance(spec.get(field), str):
                raise PatchError(f"{where}: {self.op} needs a string '{field}'")
        self.target = spec.get("target")
        m = _TARGET.match(self.target if isinstance(self.target, str) else "")
        if not m:
            raise PatchError(f"{where}: target must be node:<name>, system, tool:<name>, "
                             "tool:<name>.<param> or transition:<name>")
        self.kind, self.name, self.param = m.group(1) or "system", m.group(2), m.group(3)
        if self.param and self.kind != "tool":
            raise PatchError(f"{where}: only tool: targets have parameters")
        self.is_description = self.kind in ("tool", "transition")
        if self.op == "set_description" and not self.is_description:
            raise PatchError(f"{where}: set_description is for tool / transition targets")

        nodes = spec.get("nodes")
        if nodes is not None:
            if self.kind == "node":
                raise PatchError(f"{where}: a node: target is already limited to its node")
            if not (isinstance(nodes, list) and nodes and all(isinstance(n, str) for n in nodes)):
                raise PatchError(f"{where}: nodes must be a non-empty list of node names")
        self.nodes = set(nodes) if nodes else None
        self.all = spec.get("all", False)
        if not isinstance(self.all, bool) or (self.all and self.op == "set_description"):
            raise PatchError(f"{where}: all must be true or false, and only with a find / anchor")

        self.locator = spec.get("find", spec.get("anchor"))
        self.new = "" if self.op == "delete" else spec.get("with", spec.get("text"))
        if self.is_description:
            for field in OP_FIELDS[self.op]:
                if "{!" in spec[field]:
                    raise PatchError(f"{where}: descriptions take no merge fields")
        self.rx, self.groups = None, {}
        if self.locator is not None:
            self.rx, self.groups = _compile_locator(self.locator, where)
            missing = [f for f in value_fields(self.new) if f not in self.groups]
            if missing:
                raise PatchError(f"{where}: {', '.join(missing)} not in the find / anchor, so its value is "
                                 "unknown offline (new merge fields need a deployed version)")
        self.rendered_new = render_text(self.new)

    def in_scope(self, unit):
        node = unit.get("node")
        if self.kind == "node":
            return node == self.name
        return self.nodes is None or node in self.nodes


def _compile_locator(text, where):
    if not text.strip():
        raise PatchError(f"{where}: empty find / anchor")
    rendered = render_text(text)
    pieces, pos = [], 0  # literal, field, literal, ... (rendered: only value fields are left)
    for m in MERGE_FIELD.finditer(rendered):
        pieces += [rendered[pos:m.start()], m.group(0)]
        pos = m.end()
    pieces.append(rendered[pos:])
    literals = pieces[0::2]
    if not "".join(literals).strip():
        raise PatchError(f"{where}: the find / anchor is only merge fields")
    if len(pieces) > 1:
        if not literals[0].strip() or not literals[-1].strip():
            raise PatchError(f"{where}: a merge field may not start or end the find / anchor")
        if any(not lit for lit in literals[1:-1]):
            raise PatchError(f"{where}: two merge fields may not be adjacent in the find / anchor")
    pattern, groups = fragment_pattern(text)
    return re.compile(pattern), groups


def parse_ops(data):
    """Validated ops from a patch document: {"schema": "bt.patch/1", "ops": [...]} or a list."""
    if isinstance(data, dict):
        if data.get("schema", SCHEMA_PATCH) != SCHEMA_PATCH:
            raise PatchError(f"not a {SCHEMA_PATCH} document (schema {data.get('schema')!r})")
        unknown = set(data) - {"schema", "ops", "note"}
        if unknown:
            raise PatchError(f"unknown keys {sorted(unknown)}")
        data = data.get("ops")
    if not isinstance(data, list):
        raise PatchError("expected a list of ops")
    ops = [Op(spec, i) for i, spec in enumerate(data)]
    dupes = [i for i, n in Counter(op.id for op in ops).items() if n > 1]
    if dupes:
        raise PatchError(f"duplicate op ids {sorted(dupes)}")
    return ops


def load_patch(path):
    with open(path, encoding="utf-8") as f:
        try:
            data = json.load(f)
        except json.JSONDecodeError as e:
            raise PatchError(f"not JSON ({e})")
    return parse_ops(data)


# ---------------------------------------------------------------------------------------
# regions: (text, write) where write(new text) returns the new (messages, tools)

def _node_region(messages, tools):
    if len(messages) < 2 or messages[-1].get("role") != "system":
        return None
    content = messages[-1].get("content") or ""
    cut = content.find(CONTEXT_MARKER)
    head, tail = (content[:cut], content[cut:]) if cut >= 0 else (content, "")

    def write(new):
        return messages[:-1] + [dict(messages[-1], content=new + tail)], tools
    return head, write


def _system_region(messages, tools):
    if not messages or messages[0].get("role") != "system":
        return None

    def write(new):
        return [dict(messages[0], content=new)] + messages[1:], tools
    return messages[0].get("content") or "", write


def _description_region(messages, tools, name, param):
    for i, tool in enumerate(tools):
        fn = tool.get("function") or {}
        if fn.get("name") == name:
            break
    else:
        return None
    if param:
        props = (fn.get("parameters") or {}).get("properties") or {}
        if not isinstance(props.get(param), dict):
            return None

        def write(new):
            params = dict(fn["parameters"], properties=dict(props, **{param: dict(props[param], description=new)}))
            return messages, tools[:i] + [dict(tool, function=dict(fn, parameters=params))] + tools[i + 1:]
        return props[param].get("description") or "", write
    desc = fn.get("description") or ""
    suffix = TRANSITION_SUFFIX if desc.endswith(TRANSITION_SUFFIX) else ""
    head = desc[:len(desc) - len(suffix)]

    def write(new):
        return messages, tools[:i] + [dict(tool, function=dict(fn, description=new + suffix))] + tools[i + 1:]
    return head, write


def _region(messages, tools, op):
    if op.kind == "node":
        return _node_region(messages, tools)
    if op.kind == "system":
        return _system_region(messages, tools)
    return _description_region(messages, tools, op.name, op.param)


def edit_text(text, op):
    """The op on one rendered text: (new text or None, outcome), outcome matched | unmatched | ambiguous.
    agentpatch.py checks its .agent edit against this."""
    if op.op == "set_description":
        return op.new, "matched"
    found = list(op.rx.finditer(text))
    if not found:
        return None, "unmatched"
    if len(found) > 1 and not op.all:
        return None, "ambiguous"
    out, pos = [], 0
    for m in found:
        new = MERGE_FIELD.sub(lambda f: m.group(op.groups[f.group(0)]), op.rendered_new)
        if op.op == "insert_after":
            out += [text[pos:m.end()], new]
        elif op.op == "insert_before":
            out += [text[pos:m.start()], new, m.group(0)]
        else:
            out += [text[pos:m.start()], new]
        pos = m.end()
    out.append(text[pos:])
    return "".join(out), "matched"


def apply_ops(unit, ops):
    """(messages, tools, outcomes) of one unit after the ops. Per op the outcome is None (out
    of scope, or the step lacks the target), matched, unmatched or ambiguous. Untouched parts
    are the unit's own objects, so an unchanged request serializes byte-identically."""
    messages, tools = unit["request"]["messages"], unit["request"]["tools"]
    outcomes = []
    for op in ops:
        region = _region(messages, tools, op) if op.in_scope(unit) else None
        if region is None:
            outcomes.append(None)
            continue
        text, write = region
        new, outcome = edit_text(text, op)
        if new is not None and new != text:
            messages, tools = write(new)
        outcomes.append(outcome)
    return messages, tools, outcomes


def _check_set_description(units, ops):
    """set_description replaces one description; one name with several in scope (per-node
    bindings, or agent versions) would be ambiguous as an .agent edit."""
    for op in ops:
        if op.op != "set_description":
            continue
        seen = defaultdict(set)
        for u in units:
            region = _region(u["request"]["messages"], u["request"]["tools"], op) if op.in_scope(u) else None
            if region is not None:
                seen[region[0]].add(u.get("node"))
        if len(seen) > 1:
            where = "; ".join(f"{len(seen_nodes)} node(s): {', '.join(sorted(map(str, seen_nodes)))}"
                              for seen_nodes in seen.values())
            raise PatchError(f"op {op.id}: {op.target} has {len(seen)} different descriptions in scope ({where}); "
                             "limit the op with nodes, or replay one agent version")


def patch_units(units, ops):
    """([(messages, tools, ids of the ops that matched)] per unit, coverage per op)."""
    _check_set_description(units, ops)
    patched = []
    tally = [{"with_target": Counter(), "matched": Counter(), "ambiguous": 0} for _ in ops]
    for u in units:
        messages, tools, outcomes = apply_ops(u, ops)
        for t, outcome in zip(tally, outcomes):
            if outcome is None:
                continue
            t["with_target"][u.get("node")] += 1
            if outcome == "matched":
                t["matched"][u.get("node")] += 1
            elif outcome == "ambiguous":
                t["ambiguous"] += 1
        patched.append((messages, tools, [op.id for op, o in zip(ops, outcomes) if o == "matched"]))
    return patched, [_coverage(op, t) for op, t in zip(ops, tally)]


def _coverage(op, t):
    n, m = sum(t["with_target"].values()), sum(t["matched"].values())
    if t["ambiguous"]:
        status, msg = "error", (f"found more than once in {t['ambiguous']} step(s): lengthen the find / anchor, "
                                "or set all")
    elif not n:
        status, msg = "warning", "no replayed step has this target"
    elif not m:
        status, msg = "error", f"matched none of the {n} steps with this target: copy the text from the .agent"
    elif m < n:
        status, msg = "partial", (f"matched {m} of {n} steps; the others differ (another agent version, "
                                  "or a branch not taken)")
    else:
        status, msg = "ok", None
    return {"id": op.id, "target": op.target, "op": op.op, "nodes": sorted(op.nodes) if op.nodes else None,
            "units_with_target": n, "matched": m, "ambiguous": t["ambiguous"],
            "units_with_target_by_node": dict(sorted(t["with_target"].items(), key=lambda kv: str(kv[0]))),
            "matched_by_node": dict(sorted(t["matched"].items(), key=lambda kv: str(kv[0]))),
            "status": status, "message": msg}


def coverage_report(path, coverage, units_changed, unit_count):
    """patch_coverage.json: counts only, never rendered text (rendered values can hold user data)."""
    return {"schema": SCHEMA_COVERAGE, "patch": path, "ops": coverage, "units": unit_count,
            "units_changed": units_changed,
            "errors": [f"{c['id']}: {c['message']}" for c in coverage if c["status"] == "error"]}
