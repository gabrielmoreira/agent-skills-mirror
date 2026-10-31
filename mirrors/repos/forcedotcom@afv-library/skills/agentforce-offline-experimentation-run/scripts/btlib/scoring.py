"""Score one replayed step against its golden (the production answer to the same request).

Golden is a tool call:
    decision  candidate also called a tool (not text)
    names     same multiset of tool names (optionally lenient via configured equivalence groups)
    args      every argument the same: IDs, codes, enums and numbers compared exactly,
              missing == empty, free-text strings sent to the judge. A key one call leaves out
              takes its default (the agent config's arg_defaults, else the schema's "default").
              Not compared on a transition that declares no parameters (it takes none)
    unit score 1 (all match) | 0.5 (decision + names, args differ) | 0
Golden is text:
    candidate must reply with text the judge finds equivalent: 1 | 0. A tool call scores 0.
Strict score: 1 only for exact names (no equivalence groups), matching args with no default
taken, or equivalent text.

Buckets: match, transition_args (a match only because arguments on such a transition were not
compared), wrong_args, wrong_tool, missed_call, extra_call, tool_to_text, text_to_tool,
text_divergence.
"""

import json
import re
from collections import Counter

from .agentsrc import TRANSITION_SUFFIX

MATCH_BUCKETS = ("match", "transition_args")  # the buckets that score 1
# Last word of a parameter name that marks an identifier (productCode, order_id, SKU, email).
_ID_WORDS = {"id", "ids", "code", "codes", "number", "num", "sku", "email", "phone", "uuid", "url"}
_KEY_WORDS = re.compile(r"[A-Z]?[a-z0-9]+|[A-Z]+(?![a-z])")
_ID_VALUE = re.compile(r"^(?=\S*\d)\S+$")          # one token containing a digit: SHOE-M-088, 006Rt00000AbCdE
_SF_ID = re.compile(r"\b(?=[A-Za-z0-9]*\d)(?=[A-Za-z0-9]*[A-Za-z])[A-Za-z0-9]{15}(?:[A-Za-z0-9]{3})?\b")
_SF_ID_FULL = re.compile(r"^(?=[A-Za-z0-9]*\d)(?=[A-Za-z0-9]*[A-Za-z])[A-Za-z0-9]{15}(?:[A-Za-z0-9]{3})?$")
_UUID = re.compile(r"\b[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}\b")


def _id_key(key):
    words = _KEY_WORDS.findall(key or "")
    return bool(words) and words[-1].lower() in _ID_WORDS


def _empty(v):
    return v is None or v == "" or v == [] or v == {}


def _num(v):
    if isinstance(v, bool):
        return None
    if isinstance(v, (int, float)):
        return float(v)
    if isinstance(v, str):
        try:
            return float(v.strip())
        except ValueError:
            return None
    return None


def _bool(v):
    if isinstance(v, bool):
        return v
    if isinstance(v, str) and v.strip().lower() in ("true", "false"):
        return v.strip().lower() == "true"
    return None


def values_equal(a, b):
    """Deterministic equality with light normalisation (case/space for strings, '2' == 2).

    Salesforce record ids stay case-sensitive: 15-character ids differing only in case
    are different records.
    """
    if _empty(a) and _empty(b):
        return True
    if isinstance(a, str) and isinstance(b, str):
        a, b = a.strip(), b.strip()
        if _SF_ID_FULL.match(a) or _SF_ID_FULL.match(b):
            return a == b
        return " ".join(a.split()).lower() == " ".join(b.split()).lower()
    na, nb = _num(a), _num(b)
    if na is not None and nb is not None:
        return na == nb
    ba, bb = _bool(a), _bool(b)
    if ba is not None and bb is not None:
        return ba == bb
    return json.dumps(a, sort_keys=True) == json.dumps(b, sort_keys=True)


def is_free_text(key, golden_value, candidate_value, prop_schema):
    """Free text may be equivalent without being equal (a search phrase); IDs and enums may not."""
    if not (isinstance(golden_value, str) and isinstance(candidate_value, str)):
        return False
    if (prop_schema or {}).get("enum") or (prop_schema or {}).get("pattern"):
        return False
    if _id_key(key):
        return False
    if _ID_VALUE.match(golden_value.strip()) or _ID_VALUE.match(candidate_value.strip()):
        return False
    return True


def compare_args(golden_args, candidate_args, schema=None, defaults=None):
    """{"equal": [...], "differ": [...], "free_text": [...], "defaulted": [...], "omitted": {...}}
    over the union of keys.

    A key one call leaves out (or sends empty) takes its default: defaults[key] (the agent
    config's arg_defaults for the tool), else the schema's "default". "defaulted" lists the
    equal keys that are equal only so; "omitted" maps each differing key one call left out to
    that call, "golden" or "candidate".
    """
    props = (schema or {}).get("properties") or {}
    known = {k: p["default"] for k, p in props.items() if isinstance(p, dict) and "default" in p}
    known.update(defaults or {})
    out = {"equal": [], "differ": [], "free_text": [], "defaulted": [], "omitted": {}}
    for key in sorted(set(golden_args) | set(candidate_args)):
        g, c = golden_args.get(key), candidate_args.get(key)
        left_out = "golden" if _empty(g) else "candidate" if _empty(c) else None
        if values_equal(g, c):
            out["equal"].append(key)
        elif left_out and key in known and values_equal(known[key], c if left_out == "golden" else g):
            out["equal"].append(key)
            out["defaulted"].append(key)
        elif is_free_text(key, g, c, props.get(key)):
            out["free_text"].append(key)
        else:
            out["differ"].append(key)
            if left_out:
                out["omitted"][key] = left_out
    return out


def schema_violations(calls, schemas):
    """Problems of candidate calls against the offered tools' parameter schemas."""
    notes = []
    types = {"string": str, "boolean": bool, "object": dict, "array": list}
    for call in calls:
        name, args = call.get("name"), call.get("args") or {}
        if "args_raw" in call:
            notes.append(f"{name}: arguments are not a JSON object")
        if name not in schemas:
            notes.append(f"{name}: tool was not offered")
            continue
        schema = schemas[name] or {}
        props = schema.get("properties") or {}
        for req in schema.get("required") or []:
            if _empty(args.get(req)):
                notes.append(f"{name}: missing required '{req}'")
        for key, val in args.items():
            if props and key not in props:
                notes.append(f"{name}: unknown parameter '{key}'")
                continue
            ps = props.get(key) or {}
            t = ps.get("type")
            if t in ("number", "integer"):
                n = _num(val)
                if n is None or (t == "integer" and not n.is_integer()):
                    notes.append(f"{name}.{key}: expected {t}")
            elif t in types and val is not None and not isinstance(val, types[t]):
                notes.append(f"{name}.{key}: expected {t}")
            if ps.get("enum") and val not in ps["enum"]:
                notes.append(f"{name}.{key}: not one of the allowed values")
            if isinstance(val, str):
                if ps.get("pattern"):
                    try:
                        if not re.search(ps["pattern"], val):
                            notes.append(f"{name}.{key}: does not match the pattern")
                    except re.error:
                        pass
                if ps.get("maxLength") is not None and len(val) > ps["maxLength"]:
                    notes.append(f"{name}.{key}: longer than maxLength {ps['maxLength']}")
                if ps.get("minLength") is not None and len(val) < ps["minLength"]:
                    notes.append(f"{name}.{key}: shorter than minLength {ps['minLength']}")
    return notes


def text_proxies(golden_text, candidate_text):
    """Report-only text signals; not part of the unit score."""
    def ids(t):
        return len(_SF_ID.findall(t or "")) + len(_UUID.findall(t or ""))
    g, c = golden_text or "", candidate_text or ""
    return {
        "len_ratio": round(len(c) / max(1, len(g)), 3),
        "golden_ends_with_question": g.rstrip().endswith("?"),
        "candidate_ends_with_question": c.rstrip().endswith("?"),
        "golden_raw_ids": ids(g),
        "candidate_raw_ids": ids(c),
    }


class Equivalence:
    """Tool-name equivalence groups from the agent config; empty (exact names) by default."""

    def __init__(self, groups=None):
        self.canon = {}
        for i, group in enumerate(groups or []):
            for name in group:
                self.canon[name] = f"group{i}:" + "|".join(sorted(group))

    def key(self, name):
        return self.canon.get(name, name)

    def same(self, a, b):
        return a == b or self.key(a) == self.key(b)


def takes_no_args(fn):
    """Is this offered function a transition (the platform's suffix ends its description) that
    declares no parameters?"""
    fn = fn or {}
    return ((fn.get("description") or "").endswith(TRANSITION_SUFFIX)
            and not (fn.get("parameters") or {}).get("properties"))


def _pair_calls(golden_calls, candidate_calls, eq):
    """Pair golden and candidate calls with equivalent names; prefer pairs whose args are equal."""
    pairs, used = [], set()
    for g in golden_calls:
        options = [i for i, c in enumerate(candidate_calls)
                   if i not in used and eq.same(g["name"], c["name"])]
        if not options:
            continue
        best = next((i for i in options if values_equal(g.get("args") or {}, candidate_calls[i].get("args") or {})),
                    options[0])
        used.add(best)
        pairs.append((g, candidate_calls[best]))
    return pairs


def score_unit(unit, response, judge=None, equivalence=None, arg_defaults=None):
    """Score one ok response. Returns a dict; 'judge_error' is set when a needed judge call failed.
    arg_defaults: {tool: {param: value}}, the agent config's defaults of the params a call may leave out."""
    eq = equivalence or Equivalence()
    arg_defaults = arg_defaults or {}
    golden = unit["golden"]
    msgs = unit["request"]["messages"]
    offered = {(t.get("function") or {}).get("name"): t.get("function") or {} for t in unit["request"]["tools"]}
    schemas = {name: fn.get("parameters") or {} for name, fn in offered.items()}
    g_calls = golden.get("tool_calls") or []
    c_calls = response.get("tool_calls") or []
    c_text = response.get("text") or ""
    out = {"golden_kind": golden["kind"], "decision": None, "names": None, "names_strict": None,
           "args": None, "text": None, "score": 0.0, "strict": 0.0, "bucket": None,
           "detail": "", "args_detail": [], "judge": [], "judge_error": None,
           "schema_violations": schema_violations(c_calls, schemas) if c_calls else [],
           "topic_match": None, "confusion": None, "proxies": None}

    if unit.get("step_kind") == "router":
        # Topic = where the router sent the turn (its go_to_* calls); text = stayed put.
        out["topic_match"] = sorted(c["name"] for c in g_calls) == sorted(c["name"] for c in c_calls)

    if golden["kind"] == "tool":
        out["decision"] = bool(c_calls)
        if not c_calls:
            out["bucket"] = "tool_to_text"
            out["detail"] = f"expected {', '.join(c['name'] for c in g_calls)}, replied with text"
            out["confusion"] = ["+".join(sorted(c["name"] for c in g_calls)), "(text)"]
            return out
        g_names = Counter(eq.key(c["name"]) for c in g_calls)
        c_names = Counter(eq.key(c["name"]) for c in c_calls)
        out["names"] = g_names == c_names
        out["names_strict"] = Counter(c["name"] for c in g_calls) == Counter(c["name"] for c in c_calls)
        if not out["names"]:
            if not (g_names - c_names) and (c_names - g_names):
                out["bucket"] = "extra_call"
            elif (g_names - c_names) and not (c_names - g_names):
                out["bucket"] = "missed_call"
            else:
                out["bucket"] = "wrong_tool"
            g_list = "+".join(sorted(c["name"] for c in g_calls))
            c_list = "+".join(sorted(c["name"] for c in c_calls))
            out["confusion"] = [g_list, c_list]
            out["detail"] = f"expected {g_list}, got {c_list}"
            return out
        all_equal, not_compared, defaulted = True, [], False
        for g, c in _pair_calls(g_calls, c_calls, eq):
            cmp = compare_args(g.get("args") or {}, c.get("args") or {}, schemas.get(g["name"]),
                               arg_defaults.get(g["name"]))
            entry = {"name": g["name"], "candidate_name": c["name"], **cmp, "equivalent": None}
            if ((cmp["differ"] or cmp["free_text"]) and "args_raw" not in c
                    and takes_no_args(offered.get(g["name"])) and takes_no_args(offered.get(c["name"]))):
                entry["equivalent"], entry["not_compared"] = True, True
                not_compared += [f"{g['name']}.{k}" for k in cmp["differ"] + cmp["free_text"]]
            elif cmp["differ"] or "args_raw" in c:
                entry["equivalent"] = False
            elif cmp["free_text"]:
                if judge is None:
                    entry["equivalent"] = False
                    entry["judge_skipped"] = True
                else:
                    verdict, err = judge.args(g["name"], schemas.get(g["name"]), g.get("args") or {},
                                              c.get("args") or {}, msgs)
                    if verdict is None:
                        out["judge_error"] = err
                        return out
                    out["judge"].append({"for": f"args:{g['name']}", **verdict})
                    entry["equivalent"] = verdict["equivalent"]
            else:
                entry["equivalent"] = True
            all_equal = all_equal and entry["equivalent"]
            defaulted = defaulted or bool(cmp["defaulted"])
            out["args_detail"].append(entry)
        out["args"] = all_equal
        if all_equal and not_compared:
            out["bucket"], out["score"] = "transition_args", 1.0
            out["detail"] = "arguments on a transition that takes none, not compared: " + ", ".join(not_compared)
        elif all_equal:
            out["bucket"], out["score"] = "match", 1.0
            out["strict"] = 1.0 if out["names_strict"] and not defaulted else 0.0
        else:
            out["bucket"], out["score"] = "wrong_args", 0.5
            differ = [f"{e['name']}.{k}" + (f" (left out by the {e['omitted'][k]})" if k in e["omitted"] else "")
                      for e in out["args_detail"] if not e["equivalent"]
                      for k in (e["differ"] + e["free_text"])]
            out["detail"] = "arguments differ: " + ", ".join(differ) if differ else "arguments differ"
        return out

    # golden is text
    out["decision"] = not c_calls
    if c_calls:
        out["bucket"] = "text_to_tool"
        out["detail"] = f"expected a text reply, called {', '.join(c['name'] for c in c_calls)}"
        out["confusion"] = ["(text)", "+".join(sorted(c["name"] for c in c_calls))]
        return out
    out["proxies"] = text_proxies(golden.get("text"), c_text)
    if " ".join((golden.get("text") or "").split()) == " ".join(c_text.split()):
        out["text"] = True
    elif judge is None:
        out["text"] = False
        out["detail"] = "no judge configured"
    else:
        verdict, err = judge.text(golden.get("text") or "", c_text, msgs)
        if verdict is None:
            out["judge_error"] = err
            return out
        out["judge"].append({"for": "text", **verdict})
        out["text"] = verdict["equivalent"]
        out["detail"] = verdict.get("reasoning", "")
    out["bucket"] = "match" if out["text"] else "text_divergence"
    out["score"] = out["strict"] = 1.0 if out["text"] else 0.0
    return out
