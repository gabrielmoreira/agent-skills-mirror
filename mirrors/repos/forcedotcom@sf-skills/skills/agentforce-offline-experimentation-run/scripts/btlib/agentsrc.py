"""Read an agentscript `.agent` file: the texts a step's request is rendered from.

The patch hook (patch.py) and version attribution (versions.py) need, per node, the
instruction text blocks, the bindings that become the step's tools, and the action
definitions whose descriptions those tools carry. This is a line parser for exactly that,
not a compiler: procedure logic (set, run, conditions) is skipped, except that a text block
inside an `if` / `else` is marked conditional.

How the runtime renders these texts (verified on bt-orgfarm Shopper traces, 2026-10-09, and
bt-airline Voice_English_Airline traces, 2026-10-14):
  - a `| text` block is dedented by the column its text starts at (`|text`: right after the
    bar); a bare `|` block (text on the lines below) and a `key: |` block by the indent of
    their first text line
  - {!@actions.X} renders as X; other merge fields render as their values
  - a line whose text starts with a merge field loses all its leading whitespace
  - system.instructions ends the first system message, or, on a voice agent, sits in it as
    whole lines between the platform's own texts; a node's instruction text is the last
    system message, before "\\n\\n# CONTEXT"
  - an action tool is named after its reasoning binding and carries the action definition's
    description; the binding's LLM-filled inputs (`with p = ...`) are its parameters, with
    the input descriptions; inputs bound to an expression are not offered
  - a transition tool carries its binding's description plus TRANSITION_SUFFIX. Bindings are
    per node, so one transition (or action) name can have a different description per node
Not verified (no matching traces): how several text blocks of one node are joined, and what
an `if` branch renders — patch ops stay within one block.

    python3 scripts/btlib/agentsrc.py AGENT_OR_BUNDLE_DIR [--node NAME] [--rendered]
"""

import json
import os
import re
import sys
from collections import Counter

TRANSITION_SUFFIX = ". Never use __user_input__ to collect inputs for this action."
CONTEXT_MARKER = "\n\n# CONTEXT"  # ends a node's instruction text in the last system message
MERGE_FIELD = re.compile(r"\{!([^{}]*)\}")
NODE_KINDS = ("start_agent", "subagent", "topic")
_ACTION_REF = re.compile(r"^@actions\.(\w+)$")
_TRANSITION = re.compile(r"^@utils\.transition\s+to\s+@(?:subagent|topic)\.(\w+)$")
_STATEMENT = re.compile(r"^(if|elif|else|with|set|run|transition|available)\b")
_CONDITIONAL = re.compile(r"^(if|elif|else)\b")
_WITH = re.compile(r"^with\s+[\"']?(\w+)[\"']?\s*=\s*(.*)$")
_KEY = re.compile(r"^([^:\"]+?)\s*:(?:\s+(.*))?$")
_QUOTED_KEY = re.compile(r'^"((?:[^"\\]|\\.)*)"\s*:\s*(.*)$')


class Block:
    """One text block: its source lines and its dedented text (merge fields as written)."""

    def __init__(self, lines, base, style, first_line=None):
        self.lines = lines            # [(1-based line number, raw line)]
        self.base = base              # dedent column
        self.style = style            # "inline" (| text), "bare" (|), "block" (key: |)
        self.conditional = False      # inside an if / elif / else
        self.start = lines[0][0] if lines else first_line
        self.end = lines[-1][0] if lines else first_line

    @property
    def text(self):
        out = []
        for i, (_, raw) in enumerate(self.lines):
            if i == 0 and self.style == "inline":
                out.append(raw[self.base:])
            elif not raw.strip():
                out.append("")
            elif _indent(raw) >= self.base:
                out.append(raw[self.base:])
            else:
                out.append(raw.lstrip(" "))
        return "\n".join(out)

    def rendered(self):
        """The text as the runtime renders it; non-action merge fields stay in place."""
        return render_text(self.text)


class Input:
    def __init__(self, name, line, type_):
        self.name, self.line, self.type = name, line, type_
        self.description = None
        self.label = None
        self.is_required = False
        self.is_user_input = None
        self.item = None              # the parsed entry (agentpatch.py edits its description)


class ActionDef:
    def __init__(self, name, line):
        self.name, self.line = name, line
        self.description = None
        self.label = None
        self.target = None
        self.inputs = {}
        self.item = None


class Binding:
    """A reasoning action: becomes one tool of the node's steps."""

    def __init__(self, name, line, target):
        self.name, self.line, self.target = name, line, target
        self.kind, self.action, self.to = "other", None, None
        m = _ACTION_REF.match(target or "")
        if m:
            self.kind, self.action = "action", m.group(1)
        m = _TRANSITION.match(target or "")
        if m:
            self.kind, self.to = "transition", m.group(1)
        self.description = None
        self.description_line = None
        self.llm_inputs = []          # with p = ...
        self.bound_inputs = {}        # with p = <expression>
        self.available_when = None
        self.item = None


class Node:
    def __init__(self, kind, name, line):
        self.kind, self.name, self.line = kind, name, line
        self.label = None
        self.description = None
        self.model = None
        self.system = None            # node-level system.instructions override
        self.blocks = []              # reasoning instruction text blocks, in order
        self.procedure = False        # instructions given as a procedure (-> or statements)
        self.bindings = {}
        self.action_defs = {}


class AgentSource:
    def __init__(self, path=None):
        self.path = path
        self.target = None            # bundle-meta <target>, e.g. Shopper_Agent.v3
        self.label = None             # version label, e.g. v3
        self.developer_name = None
        self.model = None
        self.system = None            # global system.instructions block
        self.nodes = {}

    def action_def(self, node, name):
        """The definition a binding refers to: the node's own first, then any node's."""
        if name in node.action_defs:
            return node.action_defs[name]
        for other in self.nodes.values():
            if name in other.action_defs:
                return other.action_defs[name]
        return None

    def node_tools(self, node_name):
        """{tool name: {kind, description, params {name: description}, required, conditional}}
        for the tools a node's steps are offered (platform tools such as __end_session_action__
        are not in the .agent)."""
        node = self.nodes.get(node_name)
        out = {}
        if node is None:
            return out
        for b in node.bindings.values():
            tool = {"kind": b.kind, "description": None, "params": {}, "required": [],
                    "conditional": b.available_when is not None, "line": b.line}
            if b.kind == "transition":
                if b.description is not None:
                    tool["description"] = b.description + TRANSITION_SUFFIX
            elif b.kind == "action":
                d = self.action_def(node, b.action)
                if d is not None:
                    tool["description"] = d.description
                    for p in b.llm_inputs:
                        inp = d.inputs.get(p)
                        tool["params"][p] = inp.description if inp else None
                        if inp and inp.is_required:
                            tool["required"].append(p)
                else:
                    tool["params"] = {p: None for p in b.llm_inputs}
            else:
                continue
            out[b.name] = tool
        return out


class AgentSourceError(ValueError):
    pass


# ---------------------------------------------------------------------------------------
# rendering

def _action_name(field):
    m = _ACTION_REF.match(field.strip())
    return m.group(1) if m else None


def render_text(text):
    """Text as rendered: {!@actions.X} -> X, and a line starting with a merge field loses its
    leading whitespace. Other merge fields stay as written (their values are not known)."""
    lines = [ln.lstrip() if ln.lstrip().startswith("{!") else ln for ln in text.split("\n")]
    return MERGE_FIELD.sub(lambda m: _action_name(m.group(1)) or m.group(0), "\n".join(lines))


def value_fields(text):
    """The non-action merge fields of a text, in order of first appearance."""
    out = []
    for m in MERGE_FIELD.finditer(text):
        if _action_name(m.group(1)) is None and m.group(0) not in out:
            out.append(m.group(0))
    return out


def fragment_pattern(text, prefix="mf"):
    """(regex source, {field: group name}) finding the rendered form of `text`.

    Each non-action merge field becomes a capture group that matches whatever value the
    field rendered to (a repeat of the field is a backreference). The group is lazy and may
    not contain the literal just before it, so the match takes the shortest value even when
    that literal occurs earlier in the text too. Group names are prefix + a number, so the
    patterns of several texts can be combined.
    """
    rendered = render_text(text)
    parts, groups, pos = [], {}, 0
    for m in MERGE_FIELD.finditer(rendered):
        literal = rendered[pos:m.start()]
        parts.append(re.escape(literal))
        field = m.group(0)
        if field in groups:
            parts.append(f"(?P={groups[field]})")
        else:
            groups[field] = f"{prefix}{len(groups)}"
            char = f"(?:(?!{re.escape(literal)})[\\s\\S])" if literal else "[\\s\\S]"
            parts.append(f"(?P<{groups[field]}>{char}*?)")
        pos = m.end()
    parts.append(re.escape(rendered[pos:]))
    return "".join(parts), groups


# ---------------------------------------------------------------------------------------
# parsing

class _Item:
    __slots__ = ("indent", "line", "key", "value", "block", "children")

    def __init__(self, indent, line, key, value, block=None):
        self.indent, self.line, self.key, self.value, self.block = indent, line, key, value, block
        self.children = []


def _indent(raw):
    return len(raw) - len(raw.lstrip(" "))


def _split_key(s):
    """('key', 'value') for `key: value` / `"key": value`; (None, s) for a statement."""
    if _STATEMENT.match(s):
        return None, s
    m = _QUOTED_KEY.match(s) if s.startswith('"') else _KEY.match(s)
    if m:
        return m.group(1), (m.group(2) or "").strip()
    return None, s


def _take_block(lines, j, min_indent, head=None):
    """Lines from index j that are blank or indented deeper than min_indent; trailing blanks
    dropped. head: the inline first line (line number, raw), if any."""
    body = [head] if head else []
    while j < len(lines):
        raw = lines[j]
        if raw.strip() and _indent(raw) <= min_indent:
            break
        body.append((j + 1, raw))
        j += 1
    while len(body) > (1 if head else 0) and not body[-1][1].strip():
        body.pop()
    return body, j


def _first_text_indent(body):
    for _, raw in body:
        if raw.strip():
            return _indent(raw)
    return 0


def _scan(lines):
    """Flat items in file order; text blocks are consumed whole (their lines can hold anything)."""
    items, i = [], 0
    while i < len(lines):
        raw = lines[i]
        s = raw.strip()
        if not s or s.startswith("#"):
            i += 1
            continue
        ind = _indent(raw)
        if s.startswith("|"):  # |, | text, |text
            if s == "|":
                body, nxt = _take_block(lines, i + 1, ind)
                block = Block(body, _first_text_indent(body), "bare", first_line=i + 1)
            else:
                text_col = ind + 1 + _indent(raw[ind + 1:])
                body, nxt = _take_block(lines, i + 1, ind, head=(i + 1, raw))
                block = Block(body, text_col, "inline")
            items.append(_Item(ind, i + 1, None, "|", block))
            i = nxt
            continue
        key, value = _split_key(s)
        if key is not None and value.startswith("|"):
            if value == "|":
                body, nxt = _take_block(lines, i + 1, ind)
                block = Block(body, _first_text_indent(body), "block", first_line=i + 1)
            else:
                bar = raw.index("|", raw.index(":"))
                text_col = bar + 1 + _indent(raw[bar + 1:])
                body, nxt = _take_block(lines, i + 1, ind, head=(i + 1, raw))
                block = Block(body, text_col, "inline")
            items.append(_Item(ind, i + 1, key, "|", block))
            i = nxt
            continue
        items.append(_Item(ind, i + 1, key, value))
        i += 1
    return items


def _tree(items):
    root = _Item(-1, 0, None, None)
    stack = [root]
    for it in items:
        while stack[-1].indent >= it.indent:
            stack.pop()
        stack[-1].children.append(it)
        stack.append(it)
    return root


def _str(value):
    if value is None:
        return None
    v = value.strip()
    if v.startswith('"'):
        try:
            return json.loads(v)
        except json.JSONDecodeError:
            return v.strip('"')
    return v


def _bool(value):
    return (value or "").strip().lower() == "true"


def _text_value(item):
    return item.block.text if item.block is not None else _str(item.value)


def _child(item, key):
    for ch in item.children:
        if ch.key == key:
            return ch
    return None


def _instruction_blocks(item):
    """(blocks, procedure) of a reasoning `instructions` entry."""
    if item.block is not None:
        return [item.block], False
    blocks = []

    def walk(it, conditional):
        for ch in it.children:
            if ch.block is not None and ch.key is None:
                ch.block.conditional = conditional
                blocks.append(ch.block)
                continue
            walk(ch, conditional or (ch.key is None and bool(_CONDITIONAL.match(ch.value or ""))))
    walk(item, False)
    return blocks, True


def _binding(item):
    b = Binding(item.key, item.line, item.value)
    b.item = item
    for ch in item.children:
        if ch.key == "description":
            b.description = _text_value(ch)
            b.description_line = ch.line
        elif ch.key is None and ch.value:
            m = _WITH.match(ch.value)
            if m:
                if m.group(2).strip() == "...":
                    b.llm_inputs.append(m.group(1))
                else:
                    b.bound_inputs[m.group(1)] = m.group(2).strip()
            elif ch.value.startswith("available when"):
                b.available_when = ch.value[len("available when"):].strip()
    return b


def _action_def(item):
    d = ActionDef(item.key, item.line)
    d.item = item
    for ch in item.children:
        if ch.key == "description":
            d.description = _text_value(ch)
        elif ch.key == "label":
            d.label = _str(ch.value)
        elif ch.key == "target":
            d.target = _str(ch.value)
        elif ch.key == "inputs":
            for it in ch.children:
                if it.key is None:
                    continue
                inp = Input(it.key, it.line, it.value)
                inp.item = it
                for p in it.children:
                    if p.key == "description":
                        inp.description = _text_value(p)
                    elif p.key == "label":
                        inp.label = _str(p.value)
                    elif p.key == "is_required":
                        inp.is_required = _bool(p.value)
                    elif p.key == "is_user_input":
                        inp.is_user_input = _bool(p.value)
                d.inputs[inp.name] = inp
    return d


def _node(kind, name, item):
    node = Node(kind, name, item.line)
    for ch in item.children:
        if ch.key == "label":
            node.label = _str(ch.value)
        elif ch.key == "description":
            node.description = _text_value(ch)
        elif ch.key == "model_config":
            m = _child(ch, "model")
            node.model = _str(m.value) if m else None
        elif ch.key == "system":
            ins = _child(ch, "instructions")
            node.system = ins.block if ins is not None else None
        elif ch.key == "actions":
            node.action_defs = {d.name: d for d in (_action_def(c) for c in ch.children if c.key)}
        elif ch.key == "reasoning":
            for r in ch.children:
                if r.key == "instructions":
                    node.blocks, node.procedure = _instruction_blocks(r)
                elif r.key == "actions":
                    node.bindings = {b.name: b for b in (_binding(c) for c in r.children if c.key)}
    return node


def bundle_target(agent_path):
    """<target> of the bundle-meta.xml next to an .agent file, e.g. 'Shopper_Agent.v3'."""
    d = os.path.dirname(os.path.abspath(agent_path))
    for name in sorted(os.listdir(d)):
        if name.endswith(".bundle-meta.xml"):
            with open(os.path.join(d, name), encoding="utf-8") as f:
                m = re.search(r"<target>\s*([^<]+?)\s*</target>", f.read())
            if m:
                return m.group(1)
    return None


def parse_agent(text, path=None):
    src = AgentSource(path)
    root = _tree(_scan(text.split("\n")))
    for top in root.children:
        key = top.key or ""
        head = key.split()
        if key == "system":
            ins = _child(top, "instructions")
            src.system = ins.block if ins is not None else None
        elif key == "model_config":
            m = _child(top, "model")
            src.model = _str(m.value) if m else None
        elif key == "config":
            dn = _child(top, "developer_name")
            src.developer_name = _str(dn.value) if dn else None
        elif len(head) == 2 and head[0] in NODE_KINDS:
            if head[1] in src.nodes:
                raise AgentSourceError(f"{path or 'agent'}: node {head[1]} defined twice")
            src.nodes[head[1]] = _node(head[0], head[1], top)
    if not src.nodes:
        raise AgentSourceError(f"{path or 'agent'}: no start_agent / subagent nodes found")
    return src


def agent_file(path):
    """path itself, or the one .agent file inside a bundle dir."""
    if not os.path.isdir(path):
        return path
    found = sorted(n for n in os.listdir(path) if n.endswith(".agent"))
    if len(found) != 1:
        raise AgentSourceError(f"{path}: expected one .agent file, found {len(found)}")
    return os.path.join(path, found[0])


def load_agent(path, label=None):
    """Parse an .agent file, or the one .agent inside a bundle dir. The label defaults to the
    version suffix of the bundle-meta target ('v3'), else the file name."""
    path = agent_file(path)
    with open(path, encoding="utf-8") as f:
        src = parse_agent(f.read(), path)
    src.target = bundle_target(path)
    if label:
        src.label = label
    elif src.target and "." in src.target:
        src.label = src.target.rsplit(".", 1)[1]
    else:
        src.label = os.path.splitext(os.path.basename(path))[0]
    return src


def _label_key(label):
    return [int(t) if t.isdigit() else t for t in re.split(r"(\d+)", label)]


def load_versions(path):
    """The agent versions under path, sorted by label (v2 before v10): an .agent file or bundle
    dir, a dir of .agent files, or a dir of bundle dirs (a retrieved aiAuthoringBundles/)."""
    if os.path.isfile(path):
        found = [load_agent(path)]
    else:
        names = sorted(os.listdir(path))
        files = [n for n in names if n.endswith(".agent")]
        if files:
            found = [load_agent(os.path.join(path, n)) for n in files]
        else:
            found = [load_agent(os.path.join(path, n)) for n in names
                     if os.path.isdir(os.path.join(path, n))
                     and any(f.endswith(".agent") for f in os.listdir(os.path.join(path, n)))]
    if not found:
        raise AgentSourceError(f"{path}: no .agent files")
    dupes = sorted(label for label, n in Counter(s.label for s in found).items() if n > 1)
    if dupes:
        raise AgentSourceError(f"{path}: version labels {dupes} occur more than once (one bundle dir per version)")
    return sorted(found, key=lambda s: _label_key(s.label))


def main(argv=None):
    import argparse
    p = argparse.ArgumentParser(description="Print the instruction blocks and tools of an .agent file.")
    p.add_argument("agent", help=".agent file or bundle dir")
    p.add_argument("--node", help="only this node")
    p.add_argument("--rendered", action="store_true", help="print blocks as rendered ({!@actions.X} -> X)")
    args = p.parse_args(argv)
    src = load_agent(args.agent)
    print(f"# {src.path}  label={src.label} target={src.target} model={src.model}")
    if src.system is not None and not args.node:
        print(f"\n== system.instructions (lines {src.system.start}-{src.system.end})")
        print(src.system.rendered() if args.rendered else src.system.text)
    for node in src.nodes.values():
        if args.node and node.name != args.node:
            continue
        print(f"\n== {node.kind} {node.name} (line {node.line})" + (f" model={node.model}" if node.model else ""))
        for k, b in enumerate(node.blocks):
            flag = " conditional" if b.conditional else ""
            print(f"-- block {k} lines {b.start}-{b.end} {b.style}{flag}")
            print(b.rendered() if args.rendered else b.text)
        for name, tool in src.node_tools(node.name).items():
            print(f"-- tool {name} ({tool['kind']}, line {tool['line']}): {tool['description']!r}")
            for prm, desc in tool["params"].items():
                print(f"     {prm}: {desc!r}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
