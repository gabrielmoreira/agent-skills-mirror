"""The same edit ops in the .agent file: the source-side twin of patch.py.

patch.py scores an edit by applying it to the captured requests. This makes that edit in the
agent's source, so the version that ships is the one that was scored:

    new_text, report = agentpatch.patch_agent(text, patch.parse_ops(doc))

The targets are patch.py's, in the source:
  node:<name>          the node's reasoning instruction text blocks
  system               system.instructions, and the system.instructions override of a node in
                       scope (how an override renders is not verified on traces)
  tool:<name>, transition:<name>
                       a transition binding's description; for an action binding, the
                       description of its action definition
  tool:<name>.<param>  that input's description, where the binding offers it (with p = ...)

find / anchor / with / text are matched and written verbatim, as .agent source text (dedented,
merge fields as written). Only the lines an edit changes are rewritten, at the block's indent
and in its | style; procedure statements are never touched. A quoted description stays one
quoted string, in JSON escapes (the compiler decodes \\" \\\\ \\n \\t); set_description adds a
missing description. The result is parsed back: it must be the same agent, with only the edited
texts changed, as the parser reads them.

An op is refused (AgentPatchError, its .reason one of REASONS) when the .agent edit could
differ from the request edit that was scored, or when it cannot be written:
  no_target   the agent lacks the target, or a node named in nodes
  unmatched   the find / anchor is in none of the target's texts
  ambiguous   it occurs more than once without all, counted over all of a node's blocks (each
              branch of an if is a block); set_description over different descriptions
  render      the source edit renders otherwise than the same edit on the rendered text: the
              find matches the rendered text but not the source ({!@actions.X} written as X),
              or more often in the rendered text than in the source
  shared      the text is also used where the op does not apply: an action definition bound
              to another tool, or in a node outside nodes; system.instructions with nodes that
              leave out a node using it
  unwritable  the result cannot be written as intended, or does not read back as intended
              (an empty block, a trailing blank line, a CR, a control character, ...)
"""

import json
import re
from difflib import SequenceMatcher

from .agentsrc import MERGE_FIELD, AgentSourceError, _child, _str, parse_agent, render_text
from .patch import edit_text

REASONS = ("no_target", "unmatched", "ambiguous", "render", "shared", "unwritable")
DESCRIPTION_INDENT = 4  # a description added to an entry without children: this much deeper


class AgentPatchError(ValueError):
    def __init__(self, reason, message):
        super().__init__(message)
        self.reason = reason


def _err(op, reason, msg):
    return AgentPatchError(reason, f"op {op.id}: {msg}")


class _Text:
    """One editable text: a block, a one-line value, or a missing description (text None)."""

    def __init__(self, where, block=None, item=None, owner=None):
        self.where, self.block, self.item, self.owner = where, block, item, owner
        if block is not None:
            self.text = block.text
        elif item is not None:
            self.text = _str(item.value)
        else:
            self.text = None


def _description(where, owner):
    it = _child(owner, "description")
    if it is None:
        return _Text(where, owner=owner)
    if it.block is not None:
        return _Text(where, block=it.block)
    return _Text(where, item=it)


def _editable(src):
    """{key: _Text} for every text an op can edit, and the descriptions of action bindings."""
    out = {}
    if src.system is not None:
        out[("system", None)] = _Text("system.instructions", block=src.system)
    for n, node in src.nodes.items():
        if node.system is not None:
            out[("system", n)] = _Text(f"the system.instructions of node {n}", block=node.system)
        for k, b in enumerate(node.blocks):
            out[("block", n, k)] = _Text(f"instruction block {k + 1} of node {n} (line {b.start})", block=b)
        for b in node.bindings.values():
            out[("binding", n, b.name)] = _description(f"the description of {b.name} in node {n}", b.item)
        for d in node.action_defs.values():
            out[("action", n, d.name)] = _description(f"the description of action {d.name} (node {n})", d.item)
            for inp in d.inputs.values():
                out[("input", n, d.name, inp.name)] = _description(
                    f"the description of input {inp.name} of action {d.name} (node {n})", inp.item)
    return out


def _shape(src):
    """All of the agent but its editable texts and line numbers: an edit must keep it."""
    nodes = []
    for node in src.nodes.values():
        nodes.append((node.kind, node.name, node.label, node.description, node.model, node.procedure,
                      node.system is not None, [(b.style, b.conditional) for b in node.blocks],
                      [(b.name, b.kind, b.target, b.llm_inputs, sorted(b.bound_inputs.items()), b.available_when)
                       for b in node.bindings.values()],
                      [(d.name, d.label, d.target,
                        [(i.name, i.type, i.label, i.is_required, i.is_user_input) for i in d.inputs.values()])
                       for d in node.action_defs.values()]))
    return src.model, src.developer_name, src.system is not None, nodes


# ---------------------------------------------------------------------------------------
# targets

def _home(src, d):
    for n, node in src.nodes.items():
        if node.action_defs.get(d.name) is d:
            return n
    return None


def _scope(src, op):
    if op.nodes is None:
        return list(src.nodes)
    missing = sorted(op.nodes - set(src.nodes))
    if missing:
        raise _err(op, "no_target", f"nodes {missing} are not in the agent")
    return [n for n in src.nodes if n in op.nodes]


def _targets(src, texts, op):
    """[(key, _Text)] of the texts the op applies to."""
    if op.kind == "node":
        node = src.nodes.get(op.name)
        if node is None:
            raise _err(op, "no_target", f"the agent has no node {op.name}")
        if not node.blocks:
            raise _err(op, "no_target", f"node {op.name} has no instruction text")
        keys = [("block", op.name, k) for k in range(len(node.blocks))]
    elif op.kind == "system":
        keys = _system_keys(src, op, _scope(src, op))
    else:
        keys = _description_keys(src, op, _scope(src, op))
    return [(k, texts[k]) for k in keys]


def _system_keys(src, op, scope):
    users = [n for n, node in src.nodes.items() if node.system is None]  # nodes on the global text
    keys = []
    if src.system is not None and (op.nodes is None or any(n in op.nodes for n in users)):
        left = [n for n in users if op.nodes is not None and n not in op.nodes]
        if left:
            raise _err(op, "shared", f"system.instructions is also the system text of nodes {left}, which nodes "
                                     "leaves out: list them too, or drop nodes")
        keys.append(("system", None))
    keys += [("system", n) for n in scope if src.nodes[n].system is not None]
    if not keys:
        raise _err(op, "no_target", "no system.instructions in "
                   + ("the agent" if op.nodes is None else f"nodes {sorted(op.nodes)}"))
    return keys


def _description_keys(src, op, scope):
    keys, defs = [], []
    for n in scope:
        node = src.nodes[n]
        b = node.bindings.get(op.name)
        if b is None:
            continue
        if b.kind == "transition":
            if op.param:
                raise _err(op, "no_target", f"{op.name} in node {n} is a transition: it has no parameters")
            key = ("binding", n, op.name)
        elif b.kind == "action":
            d = src.action_def(node, b.action)
            if d is None:
                raise _err(op, "no_target", f"{op.name} in node {n} is bound to @actions.{b.action}, "
                                            "which the agent does not define")
            if op.param:
                if op.param not in d.inputs:
                    raise _err(op, "no_target", f"action {d.name} has no input {op.param}")
                if op.param not in b.llm_inputs:
                    continue  # bound to an expression: not a parameter of the tool
                key = ("input", _home(src, d), d.name, op.param)
            else:
                key = ("action", _home(src, d), d.name)
            if d not in defs:
                defs.append(d)
        else:
            raise _err(op, "no_target", f"{op.name} in node {n} is neither an action nor a transition")
        if key not in keys:
            keys.append(key)
    if not keys:
        where = "the agent" if op.nodes is None else f"nodes {sorted(op.nodes)}"
        offers = f" with {op.param} = ..." if op.param else ""
        raise _err(op, "no_target", f"no node of {where} binds {op.name}{offers}")
    for d in defs:
        _check_shared_def(src, op, d)
    return keys


def _check_shared_def(src, op, d):
    """An action definition's text is the description of every tool bound to it: each of
    those must be the op's tool, in its scope, or the .agent edit changes more tools than the
    request edit did."""
    others = []
    for n, node in src.nodes.items():
        for b in node.bindings.values():
            if b.kind != "action" or src.action_def(node, b.action) is not d:
                continue
            if op.param and op.param not in b.llm_inputs:
                continue
            if b.name != op.name or (op.nodes is not None and n not in op.nodes):
                others.append(f"{b.name} in node {n}")
    if others:
        what = f"input {op.param} of action {d.name}" if op.param else f"action {d.name}"
        raise _err(op, "shared", f"the description of {what} is also that of {', '.join(others)}, which the op "
                                 "leaves alone: widen nodes, or give the tool its own action definition first")


# ---------------------------------------------------------------------------------------
# the edits: {key: new text}

def _what(op):
    word = "find" if op.op in ("replace", "delete") else "anchor"
    loc = op.locator if len(op.locator) <= 60 else op.locator[:57] + "..."
    return f"the {word} {loc!r}"


def _where(targets):
    if len(targets) == 1:
        return targets[0][1].where
    return f"{len(targets)} texts ({'; '.join(t.where for _, t in targets)})"


def _verbatim(text, op, pattern):
    out, pos = [], 0
    for m in pattern.finditer(text):
        if op.op == "insert_after":
            out += [text[pos:m.end()], op.new]
        elif op.op == "insert_before":
            out += [text[pos:m.start()], op.new, m.group(0)]
        else:
            out += [text[pos:m.start()], op.new]
        pos = m.end()
    out.append(text[pos:])
    return "".join(out)


def _cut_field(text, pattern):
    """The first merge field that a match of pattern starts or ends inside of, if any."""
    fields = [(m.start(), m.end(), m.group(0)) for m in MERGE_FIELD.finditer(text)]
    for m in pattern.finditer(text):
        for start, end, field in fields:
            if start < m.end() and m.start() < end and not (m.start() <= start and end <= m.end()):
                return field
    return None


def _block_edits(op, targets):
    """The verbatim source edit of each block, checked against the request edit of its
    rendered text (patch.py's, which the replay scored)."""
    pattern = re.compile(re.escape(op.locator))
    for _, t in targets:
        field = _cut_field(t.text, pattern)
        if field:
            raise _err(op, "render", f"{_what(op)} cuts into the merge field {field} in {t.where}: the edit "
                                     "would change what it refers to. Find whole merge fields, as written")
    found = {key: len(pattern.findall(t.text)) for key, t in targets}
    for key, t in targets:
        if not found[key] and edit_text(render_text(t.text), op)[1] != "unmatched":
            raise _err(op, "render", f"{_what(op)} matches the rendered text of {t.where} but not its source: copy "
                                     "it from the .agent, with merge fields ({!@actions.X}) and the indentation of "
                                     "its lines as written")
    total = sum(found.values())
    if not total:
        raise _err(op, "unmatched", f"{_what(op)} is not in {_where(targets)}: copy it from the .agent")
    hit = [key for key, _ in targets if found[key]]
    if total > 1 and not op.all:
        branches = " (in different blocks: each branch of an if is one)" if len(hit) > 1 else ""
        raise _err(op, "ambiguous", f"{_what(op)} occurs {total} times in {_where(targets)}{branches}: "
                                    "lengthen it, or set all")
    edits = {}
    for key, t in targets:
        if not found[key]:
            continue
        new = _verbatim(t.text, op, pattern)
        req_new, outcome = edit_text(render_text(t.text), op)
        if outcome == "ambiguous":
            raise _err(op, "render", f"{_what(op)} occurs once in the source of {t.where} but more often in its "
                                     "rendered text ({!@actions.X} renders as X): lengthen it")
        if outcome != "matched" or render_text(new) != req_new:
            raise _err(op, "render", f"the edit of {t.where} renders otherwise than the same edit on its rendered "
                                     "text (a line that starts with a merge field loses its indent): keep merge "
                                     "fields off the start of a line the edit changes")
        edits[key] = new
    return edits


def _description_edits(op, targets):
    if op.op == "set_description":
        current = {t.text for _, t in targets}
        if len(current) > 1:
            raise _err(op, "ambiguous", f"{op.target} has {len(current)} different descriptions in scope "
                                        f"({'; '.join(t.where for _, t in targets)}): limit the op with nodes")
        return {key: op.new for key, _ in targets}
    edits, matched = {}, False
    for key, t in targets:
        new, outcome = edit_text(t.text or "", op)
        if outcome == "ambiguous":
            raise _err(op, "ambiguous", f"{_what(op)} occurs more than once in {t.where}: lengthen it, or set all")
        if outcome == "matched":
            matched = True
            edits[key] = new
    if not matched:
        raise _err(op, "unmatched", f"{_what(op)} is not in {_where(targets)}: copy it from the .agent")
    return edits


# ---------------------------------------------------------------------------------------
# writing: (first line index, end index, new raw lines) splices of the file's lines

def _block_raws(op, t, new):
    """The block's new raw lines: unchanged lines as they were, changed ones at its indent."""
    b = t.block
    if not b.lines:
        raise _err(op, "unwritable", f"{t.where} has no text lines")
    old, lines = b.text.split("\n"), new.split("\n")
    if not new.strip():
        raise _err(op, "unwritable", f"the edit would leave {t.where} empty")
    if not lines[-1].strip():
        raise _err(op, "unwritable", f"the edit would end {t.where} with a blank line, which is not part of a block "
                                     "in the .agent: take the line break before the text into the find instead")
    if any(ln and not ln.strip() for ln in lines):
        raise _err(op, "unwritable", f"the edit would give {t.where} a line of only spaces")
    inline = b.style == "inline"
    if inline and (not lines[0] or lines[0].startswith(" ")):
        raise _err(op, "unwritable", f"the edit would leave the | line of {t.where} empty or starting with a space")
    if not inline and next(ln for ln in lines if ln).startswith(" "):
        raise _err(op, "unwritable", f"the edit would indent the first text line of {t.where}, which sets the "
                                     "block's indent")
    raws = [raw for _, raw in b.lines]

    def fmt(j, text):
        if inline and j == 0:
            return raws[0][:b.base] + text
        return " " * b.base + text if text else ""

    out = []
    for tag, i1, _, j1, j2 in SequenceMatcher(None, old, lines, autojunk=False).get_opcodes():
        for d in range(j2 - j1):
            i, j = i1 + d, j1 + d
            keep = tag == "equal" and not (inline and (i == 0) != (j == 0))
            out.append(raws[i] if keep else fmt(j, lines[j]))
    return out


def _string(op, t, new):
    bad = sorted({hex(ord(c)) for c in new if ord(c) < 32 and c not in "\n\t"})
    if bad:
        raise _err(op, "unwritable", f"the new text of {t.where} holds control characters {bad}")
    return json.dumps(new, ensure_ascii=False)


def _quoted_raw(op, t, new, lines):
    it = t.item
    body = lines[it.line - 1].rstrip()
    try:
        one_string = isinstance(json.loads(it.value), str)
    except ValueError:
        one_string = False
    if it.children or not one_string or not body.endswith(it.value):
        raise _err(op, "unwritable", f"{t.where} is not a one-line quoted string: make it one, or a "
                                     "description: | block, first")
    return body[:len(body) - len(it.value)] + _string(op, t, new)


def _missing_raw(op, t, new):
    owner = t.owner
    indent = owner.children[0].indent if owner.children else owner.indent + DESCRIPTION_INDENT
    return " " * indent + "description: " + _string(op, t, new)


_KINDS = {"block": "instructions", "system": "system", "binding": "transition", "action": "action",
          "input": "input"}


def _about(key):
    out = {"text": _KINDS[key[0]]}
    if key[0] == "block":
        out.update(node=key[1], block=key[2])
    elif key[0] == "system":
        if key[1] is not None:
            out["node"] = key[1]
    else:
        out.update(node=key[1], name=key[2])
        if key[0] == "input":
            out["input"] = key[3]
    return out


def _hunks(key, start, old, new):
    out = []
    for tag, i1, i2, j1, j2 in SequenceMatcher(None, old, new, autojunk=False).get_opcodes():
        if tag != "equal":
            out.append(dict(_about(key), line=start + i1 + 1, removed=old[i1:i2], added=new[j1:j2]))
    return out


def _apply(text, src, op):
    """(new text, new source, report edits) of one op."""
    if "\r" in op.new:
        raise _err(op, "unwritable", "the op's text holds a carriage return")
    texts = _editable(src)
    targets = _targets(src, texts, op)
    edits = (_description_edits if op.is_description else _block_edits)(op, targets)
    lines = text.split("\n")
    splices = []
    for key, t in targets:
        new = edits.get(key)
        if new is None or new == t.text:
            continue
        if t.block is not None:
            splices.append((t.block.start - 1, t.block.end, _block_raws(op, t, new), key))
        elif t.item is not None:
            splices.append((t.item.line - 1, t.item.line, [_quoted_raw(op, t, new, lines)], key))
        else:
            splices.append((t.owner.line, t.owner.line, [_missing_raw(op, t, new)], key))
    report = []
    for i0, i1, raws, key in sorted(splices, key=lambda s: s[0], reverse=True):
        report[:0] = _hunks(key, i0, lines[i0:i1], raws)
        lines[i0:i1] = raws
    new_text = "\n".join(lines)
    return new_text, _read_back(op, src, texts, new_text, edits), report


def _parsed(src, key):
    """The text at key as the parser reads it, which is what node_tools gives the scorer; it is
    the one _editable found unless an entry holds two descriptions (the parser keeps the last)."""
    if key[0] == "system":
        return (src.system if key[1] is None else src.nodes[key[1]].system).text
    node = src.nodes[key[1]]
    if key[0] == "block":
        return node.blocks[key[2]].text
    if key[0] == "binding":
        return node.bindings[key[2]].description
    d = node.action_defs[key[2]]
    return d.description if key[0] == "action" else d.inputs[key[3]].description


def _read_back(op, src, texts, new_text, edits):
    """The edited agent, parsed: the same agent with only the edited texts changed."""
    try:
        new_src = parse_agent(new_text, src.path)
    except AgentSourceError as e:
        raise _err(op, "unwritable", f"the edited agent does not parse: {e}")
    if _shape(new_src) != _shape(src):
        raise _err(op, "unwritable", "the edit changes more than texts (nodes, blocks, bindings or definitions "
                                     "read back otherwise)")
    wrong = [t.where for key, t in texts.items() if _parsed(new_src, key) != edits.get(key, _parsed(src, key))]
    if wrong:
        raise _err(op, "unwritable", f"the edited agent reads back otherwise in {'; '.join(wrong)}")
    return new_src


def patch_agent(text, ops, path=None):
    """(new text, report) of the ops applied in order to an .agent's source text, each to the
    result of the ones before; no ops gives the text unchanged. The report has one entry per
    op, {id, target, op, edits}; an edit is {text, node, block | name [, input], line,
    removed, added}, its line 1-based in the text the op applied to."""
    if "\r" in text:
        raise AgentPatchError("unwritable", f"{path or 'agent'}: has CR line endings; convert it to LF first")
    src = parse_agent(text, path)
    report = []
    for op in ops:
        text, src, edits = _apply(text, src, op)
        report.append({"id": op.id, "target": op.target, "op": op.op, "edits": edits})
    return text, report
