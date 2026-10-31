"""Which agent version each unit was rendered from (--agent-versions).

STDM records no agent version per step, and one pull can span several versions. A version
renders a unit when, for the unit's node:
  instruction  its text blocks render to the unit's instruction text (the last system
               message, before "\\n\\n# CONTEXT"): the blocks in order, a block inside an
               if / else possibly absent, merge fields matching any value
  tools        the tools offered are the node's, with this version's descriptions,
               parameters and required lists (platform tools such as
               __end_session_action__ aside; a tool with `available when` may be absent)
  system       its system text ends the first system message, or sits in it as whole lines
               with the platform's own text after it (a voice agent); there, not where
               another version's longer system text holds the same lines, as when a version
               only added lines to it
Most steps render from several versions: a node that did not change between them renders
the same. A session runs one version, so the session's version is the one that renders
every unit of it that renders at all: the intersection. A unit's agent_version is its
session's version when that is a single one; compatible_versions lists the versions that
render the unit itself.

How several blocks of a node are joined is not verified (agentsrc.py), so any whitespace
may separate them. A loose check only adds versions to a unit's set, which can make a
session ambiguous but not wrong: the version that served a step renders it, so it is always
in the intersection.
"""

import hashlib
import os
import re
from collections import Counter, defaultdict

from . import SCHEMA_VERSIONS
from .agentsrc import CONTEXT_MARKER, fragment_pattern

PLATFORM_TOOL = re.compile(r"^__\w+__$")
CHECKS = ("node", "instruction", "tools", "system")  # in the order they are tried
_WHOLE_LINES = r"(?m)^[ \t]*(?:%s)[ \t]*$"


def unit_instruction(unit):
    """The node's instruction text in a unit's request ('' without a trailing system message)."""
    messages = unit["request"]["messages"]
    if len(messages) < 2 or messages[-1].get("role") != "system":
        return ""
    return (messages[-1].get("content") or "").split(CONTEXT_MARKER)[0]


def _tools_agree(unit, tools):
    offered = {}
    for t in unit["request"].get("tools") or []:
        fn = t.get("function") or {}
        if fn.get("name") and not PLATFORM_TOOL.match(fn["name"]):
            offered[fn["name"]] = fn
    if set(offered) - set(tools) or {n for n, t in tools.items() if not t["conditional"]} - set(offered):
        return False
    for name, fn in offered.items():
        mine = tools[name]
        if mine["description"] is None:  # not defined in the .agent: only its presence is known
            continue
        params = fn.get("parameters") or {}
        props = params.get("properties") or {}
        sent = (fn.get("description"), {p: d.get("description") if isinstance(d, dict) else None
                                        for p, d in props.items()}, sorted(params.get("required") or []))
        if sent != (mine["description"], mine["params"], sorted(mine["required"])):
            return False
    return True


class Matcher:
    """Checks units against versions; patterns are compiled once per version and node, and
    an instruction text is matched once per version and node (steps repeat them)."""

    def __init__(self, versions):
        self.versions = versions
        self._cache = {}
        self._instructions = {}
        self._lines = None  # {system text: its whole-lines pattern}, every version's
        self._held = {}     # {first system message: {system text: its spans there}}

    def _inside(self, first):
        """{system text: its spans in `first` as whole lines that no other system text of the
        versions holds as well}. A version that only added lines to the system text holds the
        older text's lines, which then must not match its steps."""
        if self._lines is None:
            texts = {b.text for v in self.versions for b in [v.system] + [n.system for n in v.nodes.values()]
                     if b is not None}
            self._lines = {t: re.compile(_WHOLE_LINES % fragment_pattern(t)[0]) for t in texts}
        if first not in self._held:
            found = {t: [m.span() for m in p.finditer(first)] for t, p in self._lines.items()}
            spans = {s for f in found.values() for s in f}
            self._held[first] = {t: [s for s in f if not any(o != s and o[0] <= s[0] and s[1] <= o[1] for o in spans)]
                                 for t, f in found.items()}
        return self._held[first]

    def _compiled(self, version, node):
        key = (version.label, node.name)
        if key not in self._cache:
            parts = [r"\s*"]
            for i, block in enumerate(node.blocks):
                p = "(?:%s)" % fragment_pattern(block.text, prefix=f"b{i}_")[0]
                parts.append((p + "?" if block.conditional else p) + r"\s*")
            systems = [fragment_pattern(b.text, prefix=f"s{i}_")[0]
                       for i, b in enumerate((node.system, version.system)) if b is not None]
            system = re.compile("(?:%s)\\s*\\Z" % "|".join(systems)) if systems else None
            self._cache[key] = (re.compile("".join(parts)), version.node_tools(node.name), system)
        return self._cache[key]

    def check(self, version, unit):
        """None when the version renders the unit, else the first check that fails."""
        node = version.nodes.get(unit.get("node"))
        if node is None:
            return "node"
        instruction, tools, system = self._compiled(version, node)
        key = (version.label, node.name, unit_instruction(unit))
        if key not in self._instructions:
            self._instructions[key] = instruction.fullmatch(key[2]) is not None
        if not self._instructions[key]:
            return "instruction"
        if not _tools_agree(unit, tools):
            return "tools"
        if system is not None:
            messages = unit["request"]["messages"]
            first = (messages[0].get("content") or "") if messages and messages[0].get("role") == "system" else ""
            if not system.search(first) and not any(self._inside(first).get(b.text)
                                                    for b in (node.system, version.system) if b is not None):
                return "system"
        return None


def _sha16(path):
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()[:16]


def attribute(units, versions):
    """Set compatible_versions and agent_version on every unit. Returns (the version set of
    each session: None when no unit of it renders, empty on a conflict; the report)."""
    matcher, labels = Matcher(versions), [v.label for v in versions]
    unrendered = defaultdict(Counter)  # node -> how far the closest version got
    for u in units:
        failed = {v.label: matcher.check(v, u) for v in versions}
        u["compatible_versions"] = [label for label in labels if failed[label] is None]
        if not u["compatible_versions"]:
            unrendered[str(u.get("node"))][max(failed.values(), key=CHECKS.index)] += 1
    by_session = defaultdict(list)
    for u in units:
        by_session[u.get("session_id")].append(u)
    session_sets, session_counts, version_sessions = {}, Counter(), Counter()
    for sid, members in by_session.items():
        sets = [set(u["compatible_versions"]) for u in members if u["compatible_versions"]]
        found = set.intersection(*sets) if sets else None
        session_sets[sid] = found
        only = next(iter(found)) if found and len(found) == 1 else None
        for u in members:
            u["agent_version"] = only
        if found is None:
            session_counts["unknown"] += 1
        elif not found:
            session_counts["conflict"] += 1
        elif only:
            session_counts["one_version"] += 1
            version_sessions[only] += 1
        else:
            session_counts["several_versions"] += 1
    rendered = Counter(label for u in units for label in u["compatible_versions"])
    report = {
        "schema": SCHEMA_VERSIONS,
        "versions": [{"label": v.label, "target": v.target, "file": os.path.basename(v.path) if v.path else None,
                      "sha256": _sha16(v.path) if v.path else None, "units_rendered": rendered[v.label],
                      "sessions": version_sessions[v.label]} for v in versions],
        "units": len(units),
        "units_rendered": sum(1 for u in units if u["compatible_versions"]),
        "units_not_rendered_by_node": {node: dict(c) for node, c in sorted(unrendered.items())},
        "sessions": dict({"total": len(by_session)}, **{k: session_counts[k] for k in
                                                        ("one_version", "several_versions", "conflict", "unknown")}),
        "selected": None,
    }
    return session_sets, report


def select(units, label, session_sets):
    """(the units of sessions that version `label` can have served, dropped counts by reason)."""
    kept, dropped = [], Counter()
    for u in units:
        found = session_sets.get(u.get("session_id"))
        if found is None:
            dropped["unknown_version"] += 1
        elif not found:
            dropped["version_conflict"] += 1
        elif label not in found:
            dropped["other_version"] += 1
        else:
            kept.append(u)
    return kept, dropped
