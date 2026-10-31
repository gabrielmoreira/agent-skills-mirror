"""Paired comparison of two replay runs of the same units (bt_compare.py).

A pair is one unit and one repeat, scored in both runs. Repeat r of both runs used the same seed,
so a unit a patch left alone, answered from a shared --cache-dir, scores the same in both: only
the units the change touched move.

Metrics are in units:
- a group's passes: the sum of its units' scores in a repeat (overall, per kind, node and golden
  tool); its delta: the sum over its units of cand - base, each averaged over the unit's pairs;
- a failure bucket's net: the pairs that scored lower and ended in it, minus the pairs that scored
  higher and came from it. A move between buckets at the same score is not counted.

Noise: a metric's tolerance is the largest difference on it between two repeats of the noise run
(default: base), at least 1 unit. A delta beyond its tolerance is a regression or a gain. A
bootstrap over sessions gives a 95% interval of each group's mean unit delta; it does not gate.

A pair where one run failed is dropped from both, except a no answer: the failed run timed out
(timeout or provider_timeout, on its last attempt) on a request or model that differs from the
other run's, and the other run answered. A model that runs away on a request it was changed to
send has failed it; it scores 0 there, in the bucket no_answer. Timeouts on the same request and
model, like every other failure, say nothing about the change and are dropped.

Two runs are comparable when they replayed the same units (requests and goldens) with the same
judge_model, k, seed, steps, router_nodes, equivalent_tools, arg_defaults, timeout and btlib code,
and neither has more than 10% infra errors (failed or missing records, no answers aside) or more
than 10% no answers (an outage looks like that too). The model and the patch may differ: they are what is
compared. A unit's request is identified as units.jsonl stores it when both runs have that file,
else by the sha each record carries (units.jsonl is redacted, the record shas are not).
not_comparable_kinds names the kinds of the reasons (REASON_KINDS), for a caller that acts on one.
"""

import hashlib
import json
import os
import random
from collections import Counter, defaultdict

from . import SCHEMA_COMPARE, SCHEMA_RESULT, SCHEMA_SUMMARY
from .results import golden_tools, read_jsonl, unit_kind
from .scoring import MATCH_BUCKETS
from .sfap import TIMEOUT_KINDS, request_sha

MUST_MATCH = ("judge_model", "k", "seed", "steps", "router_nodes", "equivalent_tools", "arg_defaults", "timeout")
NOISE_MUST_MATCH = ("judge_model", "steps", "router_nodes", "equivalent_tools",
                    "arg_defaults")  # its k and seed are its own
REPORTED = ("model", "patch", "versions", "split", "exclude_sessions", "inputs", "limit", "org", "agent",
            "sfap_base_url")
MAX_INFRA_RATE = 0.10
MAX_NO_ANSWER_RATE = 0.10
NO_ANSWER = "no_answer"
TOLERANCE_FLOOR = 1.0
BOOTSTRAP_SAMPLES = 2000
GROUP_LABELS = (("by_kind", "kind"), ("by_node", "node"), ("by_tool", "tool"))
LABELS = dict(GROUP_LABELS, overall="overall", buckets="bucket")
EXIT_CODES = {"no_regression": 0, "regression": 1, "not_comparable": 2}
# Why two runs are not comparable: other units, other settings or code, too many infra errors, too many no
# answers, nothing scored in both. bt_gate scores the no answers only when they are the one reason.
REASON_KINDS = ("units", "config", "infra", "no_answer", "unscored")


class CompareError(Exception):
    """A dir that is not a finished replay run."""


def _digest(obj):
    blob = json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(blob.encode("utf-8")).hexdigest()


def _int(v):
    return isinstance(v, int) and not isinstance(v, bool)


def _golden_problem(golden):
    if not isinstance(golden, dict) or not isinstance(golden.get("tool_calls"), list):
        return "no golden"
    if not all(isinstance(c, dict) and isinstance(c.get("name"), str) for c in golden["tool_calls"]):
        return "a golden tool call without a name"
    return None


def _record_problem(rec):
    """Why a results.jsonl line cannot be compared, or None."""
    for key in ("unit_id", "session_id", "node", "kind", "request_sha", "status"):
        if not isinstance(rec.get(key), str):
            return f"no {key}"
    if not _int(rec.get("repeat")) or rec["repeat"] < 0:
        return "no repeat"
    if rec["status"] == "ok" and not ((_int(rec.get("score")) or isinstance(rec.get("score"), float))
                                      and isinstance(rec.get("bucket"), str)):
        return "scored, without a score or a bucket"
    return _golden_problem(rec.get("golden"))


def _unit_problem(u):
    if not isinstance(u, dict):
        return "not an object"
    for key in ("unit_id", "session_id", "node"):
        if not isinstance(u.get(key), str):
            return f"no {key}"
    req = u.get("request")
    if not isinstance(req, dict) or not isinstance(req.get("messages"), list) or not isinstance(req.get("tools"), list):
        return "no request messages and tools"
    return _golden_problem(u.get("golden"))


def _info(session_id, node, kind, tools):
    return {"session_id": session_id, "node": node, "kind": kind, "tools": tools, "digest": None,
            "record_digest": None}


def load_run(path):
    """A finished run dir: {path, name, config, k, records {(unit_id, repeat): record}, units {unit_id: info},
    units_file}. The units come from units.jsonl (the requests as captured), else from the records."""
    results_path, summary_path = os.path.join(path, "results.jsonl"), os.path.join(path, "summary.json")
    if not os.path.isfile(results_path):
        raise CompareError(f"{path}: no results.jsonl (not a run dir of sfap_replay.py)")
    if not os.path.isfile(summary_path):
        raise CompareError(f"{path}: no summary.json (the run did not finish)")
    units_path = os.path.join(path, "units.jsonl")
    try:
        records = read_jsonl(results_path)
        with open(summary_path, encoding="utf-8") as f:
            summary = json.load(f)
        unit_lines = read_jsonl(units_path) if os.path.isfile(units_path) else None
    except (OSError, ValueError) as e:
        raise CompareError(f"{path}: cannot read the run ({type(e).__name__}: {e})")
    if (not isinstance(summary, dict) or summary.get("schema") != SCHEMA_SUMMARY
            or any(not isinstance(r, dict) or r.get("schema") != SCHEMA_RESULT for r in records)):
        raise CompareError(f"{path}: not a run of the step-level replay ({SCHEMA_RESULT} records, {SCHEMA_SUMMARY})")
    counts = summary.get("counts")
    if not isinstance(counts, dict) or counts.get("records") != len(records):
        raise CompareError(f"{path}: summary.json does not count the {len(records)} records of results.jsonl "
                           "(rewritten after the summary, by a re-run that stopped early?): replay it again")
    by_key = {}
    for i, rec in enumerate(records, 1):
        problem = _record_problem(rec)
        if problem:
            raise CompareError(f"{path}: results.jsonl record {i}: {problem}")
        key = (rec["unit_id"], rec["repeat"])
        if key in by_key:
            raise CompareError(f"{path}: results.jsonl holds a unit and repeat twice")
        by_key[key] = rec
    units = {}
    for i, u in enumerate(unit_lines or [], 1):
        problem = _unit_problem(u)
        if problem:
            raise CompareError(f"{path}: units.jsonl line {i}: {problem}")
        info = units[u["unit_id"]] = _info(u["session_id"], u["node"], unit_kind(u), golden_tools(u))
        info["digest"] = _digest([request_sha(u["request"]["messages"], u["request"]["tools"]), u["golden"]])
    for rec in records:
        info = units.get(rec["unit_id"])
        if info is None and unit_lines is None:
            info = units[rec["unit_id"]] = _info(rec["session_id"], rec["node"], rec["kind"], golden_tools(rec))
        if info is not None and info["record_digest"] is None:
            info["record_digest"] = _digest([rec.get("base_request_sha") or rec["request_sha"], rec["golden"]])
            if unit_lines is None:
                info["digest"] = info["record_digest"]
    stray = {uid for uid, _ in by_key} - set(units)
    if stray:
        raise CompareError(f"{path}: results.jsonl has {len(stray)} units that units.jsonl lacks")
    config = summary.get("config") if isinstance(summary.get("config"), dict) else {}
    k = config.get("k")
    if k is not None and (not _int(k) or k < 1):
        raise CompareError(f"{path}: summary.json config k is not a count")
    k = k or 1 + max((rep for _, rep in by_key), default=0)
    return {"path": path, "name": os.path.basename(os.path.normpath(path)), "config": config, "k": k,
            "records": by_key, "units": units, "units_file": unit_lines is not None}


def _name_apart(runs):
    """Different dirs of the same name (iterations/v1/bt_run, iterations/v2/bt_run) are named with their
    parent dir, so that a message tells them apart."""
    real = [os.path.realpath(run["path"]) for run in runs]
    alike = [i for i, run in enumerate(runs)
             if any(other["name"] == run["name"] and real[j] != real[i] for j, other in enumerate(runs))]
    for i in alike:
        runs[i]["name"] = os.path.join(os.path.basename(os.path.dirname(real[i])), os.path.basename(real[i]))


def _no_answer(b, c):
    """The record of the pair (b, c) that is a no answer, or None: it timed out where the other one
    answered, and the two differ in request or model."""
    if (b["status"] == "ok") == (c["status"] == "ok"):
        return None
    failed, answered = (c, b) if b["status"] == "ok" else (b, c)
    if failed.get("error_kind") not in TIMEOUT_KINDS:
        return None
    if failed["request_sha"] == answered["request_sha"] and failed.get("model") == answered.get("model"):
        return None
    return failed


def _health(run, no_answers=()):
    """Expected records, and of them: failed (no answers aside), missing, no answers."""
    expected = len(run["units"]) * run["k"]
    keys = [(uid, rep) for uid in run["units"] for rep in range(run["k"])]
    missing = sum(1 for key in keys if key not in run["records"])
    failed = [key for key in keys if key in run["records"] and run["records"][key]["status"] != "ok"]
    no_answer = sum(1 for key in failed if key in no_answers)
    infra = len(failed) - no_answer
    return {"records": expected, "infra_error": infra, "missing": missing, "no_answer": no_answer,
            "infra_rate": round((infra + missing) / expected, 4) if expected else 0.0}


def _too_unhealthy(health):
    return bool(health["records"]) and (health["infra_error"] + health["missing"]) / health["records"] > MAX_INFRA_RATE


def _too_many_no_answers(health):
    return bool(health["records"]) and health.get("no_answer", 0) / health["records"] > MAX_NO_ANSWER_RATE


def _norm(key, value):
    if key == "router_nodes":
        return sorted(value or [])
    if key == "equivalent_tools":
        return sorted(sorted(g) for g in value or [])
    if key == "arg_defaults":
        return json.dumps(value or {}, sort_keys=True)  # a run from before arg_defaults: none
    return value


def _show(value):
    text = json.dumps(value, ensure_ascii=False)
    return text if len(text) <= 60 else text[:57] + "..."


def _code(run):
    return (run["config"].get("code") or {}).get("btlib_sha256")


def _config_issues(a, b, keys):
    issues = [f"{key} differs ({_show(a['config'].get(key))} vs {_show(b['config'].get(key))})"
              for key in keys if _norm(key, a["config"].get(key)) != _norm(key, b["config"].get(key))]
    if _code(a) != _code(b):
        issues.append("the btlib code differs (config.code.btlib_sha256): replay both with the same code")
    return issues


def _same_units(a, b):
    """The units of a and b with the same request and golden in both, by unit id."""
    key = "digest" if a["units_file"] and b["units_file"] else "record_digest"
    out = set()
    for uid in set(a["units"]) & set(b["units"]):
        da, db = a["units"][uid][key], b["units"][uid][key]
        if da is None or db is None or da == db:  # None: never replayed, so its pairs are missing anyway
            out.add(uid)
    return out


def _unit_issue(a, b):
    only_a, only_b = set(a["units"]) - set(b["units"]), set(b["units"]) - set(a["units"])
    changed = len(set(a["units"]) & set(b["units"])) - len(_same_units(a, b))
    if not (only_a or only_b or changed):
        return None
    return (f"the units differ: {len(only_a)} only in {a['name']}, {len(only_b)} only in {b['name']}, "
            f"{changed} with another request or golden")


def _differs(a, b):
    out = {key: [a["config"].get(key), b["config"].get(key)] for key in REPORTED
           if a["config"].get(key) != b["config"].get(key)}
    git = [(run["config"].get("code") or {}).get("git") for run in (a, b)]
    if git[0] != git[1]:
        out["code.git"] = git
    return out


def _run_meta(run, health):
    c = run["config"]
    meta = {"dir": run["path"], "model": c.get("model"), "patch": c.get("patch"), "k": run["k"],
            "seed": c.get("seed"), "units": len(run["units"]), "interrupted": bool(c.get("interrupted"))}
    meta.update(health)
    return meta


def _keys(info):
    """The groups a unit counts in."""
    return [("by_kind", info["kind"]), ("by_node", info["node"])] + [("by_tool", t) for t in info["tools"]]


def _unit_row(uid, info, pairs):
    n = len(pairs)
    new, fixed = Counter(), Counter()
    for b, c in pairs:
        if c["score"] < b["score"]:
            new[c["bucket"]] += 1 / n
        elif c["score"] > b["score"]:
            fixed[b["bucket"]] += 1 / n
    base = sum(b["score"] for b, _ in pairs) / n
    cand = sum(c["score"] for _, c in pairs) / n
    return {"unit_id": uid, "session_id": info["session_id"], "node": info["node"], "kind": info["kind"],
            "tools": info["tools"], "pairs": n, "base": base, "cand": cand, "delta": cand - base,
            "base_buckets": [b["bucket"] for b, _ in pairs], "cand_buckets": [c["bucket"] for _, c in pairs],
            "new": new, "fixed": fixed,
            "touched": any(b["request_sha"] != c["request_sha"] for b, c in pairs),
            "moved": any(b["score"] != c["score"] or b["bucket"] != c["bucket"] for b, c in pairs),
            "ops": sorted({op for _, c in pairs for op in c.get("patch_ops") or []})}


def _pair(base, cand, unit_ids, repeats):
    """(one row per unit with a pair, dropped pairs by reason, {role: (unit_id, repeat) of its no answers})."""
    rows, dropped, no_answers = [], Counter(), {"base": set(), "cand": set()}
    for uid in unit_ids:
        pairs = []
        for rep in repeats:
            b, c = base["records"].get((uid, rep)), cand["records"].get((uid, rep))
            failed = _no_answer(b, c) if b is not None and c is not None else None
            if failed is not None:
                role = "base" if failed is b else "cand"
                no_answers[role].add((uid, rep))
                scored = dict(failed, score=0.0, strict=0.0, bucket=NO_ANSWER)
                pairs.append((scored, c) if role == "base" else (b, scored))
            elif b is None or c is None:
                dropped["missing"] += 1
            elif b["status"] != "ok" and c["status"] != "ok":
                dropped["both_infra"] += 1
            elif b["status"] != "ok":
                dropped["base_infra"] += 1
            elif c["status"] != "ok":
                dropped["cand_infra"] += 1
            else:
                pairs.append((b, c))
        if pairs:
            rows.append(_unit_row(uid, base["units"][uid], pairs))
    return rows, dropped, no_answers


def noise_spread(run):
    """({(metric, name): spread}, {bucket: spread}, repeat pairs): the largest difference between two
    of the run's repeats, on the units scored in both, per group (passes) and per bucket (net)."""
    groups, buckets = defaultdict(float), defaultdict(float)
    pairs = 0
    for r1 in range(run["k"]):
        for r2 in range(r1 + 1, run["k"]):
            pairs += 1
            diff, net = defaultdict(float), defaultdict(float)
            for uid, info in run["units"].items():
                a, b = run["records"].get((uid, r1)), run["records"].get((uid, r2))
                if a is None or b is None or a["status"] != "ok" or b["status"] != "ok":
                    continue
                d = b["score"] - a["score"]
                for key in [("overall", None)] + _keys(info):
                    diff[key] += d
                if d < 0:
                    net[b["bucket"]] += 1
                elif d > 0:
                    net[a["bucket"]] -= 1
            for key, v in diff.items():
                groups[key] = max(groups[key], abs(v))
            for key, v in net.items():
                buckets[key] = max(buckets[key], abs(v))
    return dict(groups), dict(buckets), pairs


def _tolerance(spread):
    return max(TOLERANCE_FLOOR, spread or 0.0)


def _beyond(delta, tol):
    """'gain', 'regression' or None, for a delta where higher is better."""
    delta = round(delta, 6)  # means over 3 repeats are not exact in binary
    return "regression" if delta < -tol else "gain" if delta > tol else None


def _resample_ci(rows, seed, samples=BOOTSTRAP_SAMPLES):
    """95% percentile interval of the mean unit delta, resampling whole sessions; None under 2 sessions."""
    sessions = defaultdict(lambda: [0.0, 0])
    for r in rows:
        s = sessions[r["session_id"]]
        s[0] += r["delta"]
        s[1] += 1
    if len(sessions) < 2 or samples < 1:
        return None
    clusters = [sessions[s] for s in sorted(sessions)]
    if all(d == 0 for d, _ in clusters):
        return [0.0, 0.0]
    rng = random.Random(seed)
    means = []
    for _ in range(samples):
        picked = rng.choices(clusters, k=len(clusters))
        means.append(sum(d for d, _ in picked) / sum(n for _, n in picked))
    means.sort()
    return [round(means[(25 * samples + 999) // 1000 - 1], 4),  # nearest rank: 2.5th and 97.5th percentiles
            round(means[(975 * samples + 999) // 1000 - 1], 4)]


def _group(rows, tol, seed, samples):
    n = len(rows)
    base, cand = sum(r["base"] for r in rows), sum(r["cand"] for r in rows)
    return {"n": n, "sessions": len({r["session_id"] for r in rows}),
            "base": round(base, 4), "cand": round(cand, 4), "delta": round(cand - base, 4), "tolerance": tol,
            "beyond_noise": _beyond(cand - base, tol), "undetectable": 0 < round(base, 6) <= tol,
            "base_agreement": round(base / n, 4), "cand_agreement": round(cand / n, 4),
            "delta_agreement": round((cand - base) / n, 4), "ci95": _resample_ci(rows, seed, samples)}


def _buckets(rows, spread):
    base, cand, new, fixed = Counter(), Counter(), Counter(), Counter()
    for r in rows:
        for b in r["base_buckets"]:
            base[b] += 1 / r["pairs"]
        for c in r["cand_buckets"]:
            cand[c] += 1 / r["pairs"]
        new.update(r["new"])
        fixed.update(r["fixed"])
    out = {}
    for name in sorted((set(base) | set(cand) | set(spread)) - set(MATCH_BUCKETS), key=lambda b: (-base[b], b)):
        tol = _tolerance(spread.get(name))
        net = new[name] - fixed[name]
        better = _beyond(-net, tol)  # fewer failures is better
        out[name] = {"base": round(base[name], 4), "cand": round(cand[name], 4), "new": round(new[name], 4),
                     "fixed": round(fixed[name], 4), "net": round(net, 4), "tolerance": tol,
                     "beyond_noise": better}
    return out


def _round_row(r):
    keep = ("unit_id", "node", "kind", "tools", "pairs", "touched", "ops", "base_buckets", "cand_buckets")
    out = {k: r[k] for k in keep}
    out.update(base=round(r["base"], 4), cand=round(r["cand"], 4), delta=round(r["delta"], 4))
    return out


def compare(base_dir, cand_dir, noise_dir=None, force=False, samples=BOOTSTRAP_SAMPLES):
    """The comparison of cand with base (bt.compare/1); its verdict maps to an exit code (EXIT_CODES)."""
    base, cand = load_run(base_dir), load_run(cand_dir)
    same_dir = noise_dir and os.path.exists(noise_dir) and os.path.samefile(noise_dir, base_dir)
    noise = load_run(noise_dir) if noise_dir and not same_dir else base
    roles = [("base", base), ("cand", cand)] + ([("noise", noise)] if noise is not base else [])
    _name_apart([run for _, run in roles])
    reasons = [("units", i) for i in [_unit_issue(base, cand)] if i]  # (kind, message)
    reasons += [("config", i) for i in _config_issues(base, cand, MUST_MATCH)]
    if noise is not base:
        reasons += [("units", f"noise run: {i}") for i in [_unit_issue(base, noise)] if i]
        reasons += [("config", f"noise run: {i}") for i in _config_issues(base, noise, NOISE_MUST_MATCH)]
    common = sorted(_same_units(base, cand))
    repeats = range(min(base["k"], cand["k"]))
    rows, dropped, no_answers = _pair(base, cand, common, repeats)
    health = {}
    for role, run in roles:
        h = health[role] = _health(run, no_answers.get(role, ()))  # the noise run is not paired: no no answers
        if _too_unhealthy(h):
            reasons.append(("infra", f"{run['name']}: {100 * h['infra_rate']:.1f}% of its records are infra errors "
                                     f"or missing (more than {100 * MAX_INFRA_RATE:.0f}%): fix the cause, then replay "
                                     "the failed calls again (--cache-dir sends only those)"))
        if _too_many_no_answers(h):
            reasons.append(("no_answer", f"{run['name']}: {100 * h['no_answer'] / h['records']:.1f}% of its records "
                                         "timed out where the other run answered (more than "
                                         f"{100 * MAX_NO_ANSWER_RATE:.0f}%): an outage, or a model that runs away on "
                                         "most of what it was changed to send. Replay the failed calls again "
                                         "(--cache-dir sends only those): a runaway times out again, and --force "
                                         "then scores those as no answers"))
    reasons = list(dict.fromkeys(reasons))  # the noise run can be cand
    kinds = [kind for kind in REASON_KINDS if any(k == kind for k, _ in reasons)]
    reasons = [message for _, message in reasons]
    group_spread, bucket_spread, noise_pairs = noise_spread(noise)
    out = {"schema": SCHEMA_COMPARE, "base": _run_meta(base, health["base"]), "cand": _run_meta(cand, health["cand"]),
           "noise": {"dir": noise["path"], "model": noise["config"].get("model"), "k": noise["k"],
                     "repeat_pairs": noise_pairs, "infra_rate": health.get("noise", health["base"])["infra_rate"]},
           "differs": _differs(base, cand), "comparable": not reasons, "not_comparable": reasons,
           "not_comparable_kinds": kinds, "forced": bool(reasons) and force, "warnings": []}
    if reasons and not force:
        out["verdict"] = "not_comparable"
        return out

    out["pairs"] = {"units": len(rows), "pairs": sum(r["pairs"] for r in rows), "repeats": len(repeats),
                    "dropped": dict(dropped), "no_answer": {role: len(keys) for role, keys in no_answers.items()},
                    "units_dropped": len(common) - len(rows),
                    "units_touched": sum(1 for r in rows if r["touched"]),
                    "untouched_moved": sum(1 for r in rows if r["moved"] and not r["touched"])}
    if not rows:
        out["not_comparable"] = reasons + ["no unit was scored in both runs"]
        out["not_comparable_kinds"] = kinds + ["unscored"]
        out["comparable"], out["verdict"] = False, "not_comparable"
        return out

    out["overall"] = _group(rows, _tolerance(group_spread.get(("overall", None))), "overall", samples)
    members = defaultdict(lambda: defaultdict(list))
    for r in rows:
        for metric, name in _keys(r):
            members[metric][name].append(r)
    for metric, _ in GROUP_LABELS:
        out[metric] = {name: _group(members[metric][name], _tolerance(group_spread.get((metric, name))),
                                    f"{metric}/{name}", samples)
                       for name in sorted(members[metric])}
    out["buckets"] = _buckets(rows, bucket_spread)
    out["units"] = [_round_row(r) for r in sorted(rows, key=lambda r: (round(r["delta"], 6), r["unit_id"]))
                    if r["moved"]]

    regressions = []
    if out["overall"]["beyond_noise"] == "regression":
        regressions.append({"metric": "overall", "name": None, "delta": out["overall"]["delta"],
                            "tolerance": out["overall"]["tolerance"]})
    for metric, _ in GROUP_LABELS:
        for name, g in out[metric].items():
            if g["beyond_noise"] == "regression":
                regressions.append({"metric": metric, "name": name, "delta": g["delta"], "tolerance": g["tolerance"]})
    for name, b in out["buckets"].items():
        if b["beyond_noise"] == "regression":
            regressions.append({"metric": "buckets", "name": name, "net": b["net"], "tolerance": b["tolerance"]})
    out["regressions"] = regressions
    out["gain_beyond_noise"] = out["overall"]["beyond_noise"] == "gain"
    out["verdict"] = "regression" if regressions else "no_regression"
    out["warnings"] = _warnings(out, base, cand, noise, noise_pairs, reasons)
    return out


def _warnings(out, base, cand, noise, noise_pairs, forced_reasons):
    warns = []
    if forced_reasons:
        warns.append("compared although not comparable (--force), on the units both runs share: "
                     + "; ".join(forced_reasons))
    if not noise_pairs:
        warns.append(f"the noise run {noise['name']} has one repeat: every tolerance is the floor, "
                     f"{TOLERANCE_FLOOR:g} unit; replay it with --k 3 for a noise estimate")
    if noise is not base and noise["config"].get("model") != base["config"].get("model"):
        warns.append(f"the noise run's model ({noise['config'].get('model')}) is not base's "
                     f"({base['config'].get('model')}): its spread may not be this model's")
    for run in (base, cand):
        if run["config"].get("interrupted"):
            warns.append(f"{run['name']} was interrupted: its missing records are dropped from the pairs")
    na = out["pairs"]["no_answer"]
    if na["base"] or na["cand"]:
        warns.append(f"{na['base'] + na['cand']} pairs score 0 as no answers (base {na['base']}, cand {na['cand']}): "
                     "timeouts where the other run answered another request or model. A runaway times out again; "
                     "to rule out an outage, replay the failed calls again (--cache-dir sends only those)")
    moved = out["pairs"]["untouched_moved"]
    if moved and base["config"].get("model") == cand["config"].get("model"):
        warns.append(f"{moved} units whose request is the same in both runs scored differently: sampling noise is "
                     "in the deltas. Replay both with the same --seed and one --cache-dir, so that what a change "
                     "leaves alone scores the same")
    blind = [f"{label} {name}" for metric, label in GROUP_LABELS for name, g in out[metric].items()
             if g["undetectable"]]
    if out["overall"]["undetectable"]:
        blind.insert(0, "overall")
    if blind:
        warns.append(f"a regression cannot be detected on {len(blind)} groups whose base passes are within their "
                     "tolerance: " + ", ".join(blind[:8]) + (", ..." if len(blind) > 8 else ""))
    return warns


def exit_code(result):
    return EXIT_CODES[result["verdict"]]


def _patch_label(patch):
    return f"patch {patch.get('file')} ({str(patch.get('sha256'))[:8]})" if patch else "no patch"


def _cut(label, width=38):
    return label if len(label) <= width else label[:width - 4] + "... "


def _row(label, g):
    ci = "" if g["ci95"] is None else f"[{g['ci95'][0]:+.3f}, {g['ci95'][1]:+.3f}]"
    flag = {"regression": "REGRESSION", "gain": "gain"}.get(g["beyond_noise"]) or (
        "(undetectable)" if g["undetectable"] else "")
    return (f"{_cut(label):<38}{g['n']:>5}{g['base']:>9.2f}{g['cand']:>9.2f}{g['delta']:>+9.2f}{g['tolerance']:>6g}"
            f"  {g['base_agreement']:.3f} -> {g['cand_agreement']:.3f}  {ci:<18}  {flag}").rstrip()


def report_lines(res):
    """The comparison as text: counts, node and tool names only (unit ids stay in the JSON)."""
    lines = []
    for role in ("base", "cand"):
        m = res[role]
        lines.append(f"{role:<6} {m['dir']}  model {m['model']}, {_patch_label(m['patch'])}, k={m['k']}, "
                     f"infra errors {m['infra_error']} + missing {m['missing']} of {m['records']}"
                     + (f", no answers {m['no_answer']}" if m.get("no_answer") else ""))
    n = res["noise"]
    lines.append(f"noise  {n['dir']}: " + (
        f"{n['repeat_pairs']} pairs of repeats (k={n['k']}); tolerance = the largest difference between two "
        f"repeats, at least {TOLERANCE_FLOOR:g} unit" if n["repeat_pairs"] else
        f"one repeat: every tolerance is {TOLERANCE_FLOOR:g} unit"))
    lines.append("differs: " + (", ".join(res["differs"]) or "nothing in the config"))
    if res["verdict"] == "not_comparable":
        lines.append("NOT COMPARABLE:")
        lines.extend(f"  - {r}" for r in res["not_comparable"])
        lines.append("verdict: not comparable (exit 2)")
        return lines
    p = res["pairs"]
    dropped = ", ".join(f"{k.replace('_', ' ')} {v}" for k, v in sorted(p["dropped"].items())) or "none"
    no_answer = ", ".join(f"{role} {n}" for role, n in p["no_answer"].items() if n) or "none"
    lines.append(f"paired {p['units']} units, {p['pairs']} unit x repeat pairs over {p['repeats']} repeats; "
                 f"dropped pairs: {dropped}; no answers (scored 0): {no_answer}; "
                 f"units the change touched: {p['units_touched']}")
    lines.append("")
    lines.append(f"{'passes (sum of unit scores)':<38}{'n':>5}{'base':>9}{'cand':>9}{'delta':>9}{'tol':>6}"
                 f"  {'agreement':<16}  {'95% CI of the mean':<18}")
    lines.append(_row("overall", res["overall"]))
    for metric, label in GROUP_LABELS:
        for name, g in res[metric].items():
            lines.append(_row(f"{label} {name}", g))
    if res["buckets"]:
        lines.append("")
        lines.append(f"{'failure bucket (records per repeat)':<38}{'base':>7}{'cand':>7}{'new':>7}{'fixed':>7}"
                     f"{'net':>8}{'tol':>6}")
        for name, b in res["buckets"].items():
            flag = {"regression": "REGRESSION", "gain": "fewer"}.get(b["beyond_noise"], "")
            lines.append(f"{_cut(name):<38}{b['base']:>7.2f}{b['cand']:>7.2f}{b['new']:>7.2f}{b['fixed']:>7.2f}"
                         f"{b['net']:>+8.2f}{b['tolerance']:>6g}  {flag}".rstrip())
    lines.append("")
    lines.append(f"units that moved: {len(res['units'])} (listed in the JSON)")
    for w in res["warnings"]:
        lines.append(f"WARNING: {w}")
    o = res["overall"]
    if res["regressions"]:
        names = [LABELS[r["metric"]] + ("" if r["name"] is None else f" {r['name']}") for r in res["regressions"]]
        lines.append(f"verdict: REGRESSION beyond noise on {len(names)}: " + ", ".join(names) + " (exit 1)")
    else:
        gain = (f"overall {o['delta']:+.2f} units, a gain beyond noise (tolerance {o['tolerance']:g})"
                if res["gain_beyond_noise"] else
                f"overall {o['delta']:+.2f} units, within noise (tolerance {o['tolerance']:g})")
        lines.append(f"verdict: no regression beyond noise; {gain} (exit 0)")
    return lines
