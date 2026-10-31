"""Run-dir artifacts — the stored traces of one replay run.

    units.jsonl              replayed units: request + golden (bt.unit/1); replay again with --from-units
    results.jsonl            one line per unit x repeat: response, scores, status (bt.result/1)
    summary.json             aggregates, run config, code fingerprint (bt.summary/1)
    replay_results_sfap.csv  the legacy CSV columns, one row per unit x repeat, plus unit columns

Run dirs hold user utterances: keep them out of git. Every writer goes through redact_obj and
creates its file readable by its owner only.
"""

import csv
import hashlib
import json
import os
import statistics
import subprocess
from collections import Counter, defaultdict

from . import SCHEMA_RESULT, SCHEMA_SUMMARY
from .redact import redact_obj
from .scoring import MATCH_BUCKETS
from .sfap import TIMEOUT_KINDS

UNIT_FIELDS = ("unit_id", "session_id", "turn", "step", "step_id", "interaction_id", "org", "agent",
               "agent_version", "compatible_versions", "node", "step_kind", "split", "channel", "topic",
               "user_utterance", "production")
SCORE_FIELDS = ("decision", "names", "names_strict", "args", "text", "score", "strict", "bucket",
                "detail", "args_detail", "judge", "schema_violations", "topic_match", "confusion",
                "proxies")
LEGACY_CSV_FIELDS = ["session_id", "utterance", "original_model", "replay_model", "actual_topic",
                     "replayed_topic", "topic_match", "actual_action", "replayed_action",
                     "function_match_score", "function_args_score", "actual_outcome",
                     "replayed_outcome", "text_resp_score"]
CSV_FIELDS = LEGACY_CSV_FIELDS + ["unit_id", "node", "step_kind", "repeat", "status", "bucket",
                                  "unit_score"]


def unit_kind(unit):
    """router_tool | router_text | subagent_tool | subagent_text."""
    return f"{unit.get('step_kind')}_{unit['golden']['kind']}"


def make_record(unit, repeat, model, seed, request_sha, call, scores=None, patch=None):
    """One results.jsonl line. A failed judge call turns the record into an infra error.
    patch: {"base_request_sha", "ops"} of a patched run (--patch): the unpatched request's
    sha and the ops that matched this unit."""
    rec = {"schema": SCHEMA_RESULT}
    rec.update({k: unit.get(k) for k in UNIT_FIELDS})
    patch = patch or {}
    rec.update(kind=unit_kind(unit), repeat=repeat, model=model,
               golden_model=unit["request"].get("model"), seed=seed, request_sha=request_sha,
               base_request_sha=patch.get("base_request_sha"), patch_ops=patch.get("ops"),
               status=call["status"], error=call.get("error"), error_kind=call.get("error_kind"),
               http_status=call.get("http_status"), attempts=call.get("attempts"),
               latency_ms=call.get("latency_ms"), cached=bool(call.get("cached")))
    resp = call.get("response")
    rec["response"] = {k: resp.get(k) for k in ("text", "tool_calls", "finish_reason")} if resp else None
    rec["usage"] = resp.get("usage") if resp else None
    rec["golden"] = unit["golden"]
    rec.update({k: None for k in SCORE_FIELDS})
    if scores is not None:
        if scores.get("judge_error"):
            rec.update(status="infra_error", error_kind="judge", error=scores["judge_error"])
        else:
            rec.update({k: scores.get(k) for k in SCORE_FIELDS})
    return rec


def open_private(path, **kwargs):
    """A file opened for writing that only its owner can read (mode 0600), before anything is written."""
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    try:
        os.chmod(path, 0o600)  # an existing file keeps its mode through os.open
        return os.fdopen(fd, "w", encoding="utf-8", **kwargs)
    except BaseException:
        os.close(fd)
        raise


def write_jsonl(path, rows):
    with open_private(path) as f:
        for row in rows:
            f.write(json.dumps(redact_obj(row), ensure_ascii=False) + "\n")


def append_jsonl(f, row):
    f.write(json.dumps(redact_obj(row), ensure_ascii=False) + "\n")
    f.flush()


def read_jsonl(path):
    with open(path, encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def write_json(path, obj):
    with open_private(path) as f:
        json.dump(redact_obj(obj), f, indent=2, ensure_ascii=False)
        f.write("\n")


# Modules that neither replay nor score: editing them must not make two runs incomparable.
NOT_FINGERPRINTED = ("agentpatch.py", "compare.py", "fetch.py")


def code_fingerprint():
    """Hash of the btlib sources that replay and score, plus the git commit, so runs scored by
    different code are told apart."""
    here = os.path.dirname(os.path.abspath(__file__))
    h = hashlib.sha256()
    for name in sorted(os.listdir(here)):
        if name.endswith(".py") and name not in NOT_FINGERPRINTED:
            with open(os.path.join(here, name), "rb") as f:
                h.update(name.encode() + b"\0" + f.read() + b"\0")
    out = {"btlib_sha256": h.hexdigest()[:16], "git": None, "git_dirty": None}
    try:
        git = subprocess.run(["git", "-C", here, "rev-parse", "--short=12", "HEAD"],
                             capture_output=True, text=True, timeout=10)
        if git.returncode == 0:
            out["git"] = git.stdout.strip()
            dirty = subprocess.run(["git", "-C", here, "status", "--porcelain", "--", "."],
                                   capture_output=True, text=True, timeout=10)
            out["git_dirty"] = bool(dirty.stdout.strip())
    except (OSError, subprocess.SubprocessError):
        pass
    return out


def aggregate(rows):
    n = len(rows)
    if not n:
        return {"n": 0, "agreement": None, "strict": None, "match": 0}
    return {"n": n,
            "agreement": round(sum(r["score"] for r in rows) / n, 4),
            "strict": round(sum(r["strict"] for r in rows) / n, 4),
            "match": sum(1 for r in rows if r["bucket"] in MATCH_BUCKETS)}


def _group(rows, keys_of):
    groups = defaultdict(list)
    for r in rows:
        for k in keys_of(r):
            groups[k].append(r)
    out = {}
    for k in sorted(groups):
        agg = aggregate(groups[k])
        agg["buckets"] = dict(Counter(r["bucket"] for r in groups[k]).most_common())
        out[k] = agg
    return out


def golden_tools(rec):
    """Tools the golden called; '(text)' for a text golden."""
    return sorted({c["name"] for c in rec["golden"]["tool_calls"]}) or ["(text)"]


def groundedness(rec):
    """The category production's groundedness check gave the record's turn; '(none)' without one."""
    return (rec.get("production") or {}).get("groundedness") or "(none)"


def production_summary(records):
    """Production's own checks over the turns and sessions of these records (report-only)."""
    turns, sessions = {}, {}
    for r in records:
        p = r.get("production")
        if p:
            turns.setdefault((r["session_id"], r["turn"]), p)
            sessions.setdefault(r["session_id"], p)
    guardrails = defaultdict(Counter)
    for p in turns.values():
        for name, value in (p.get("guardrails") or {}).items():
            guardrails[name][value] += 1
    return {"turns": len(turns),
            "groundedness": dict(Counter(p.get("groundedness") or "(none)" for p in turns.values()).most_common()),
            "guardrails": {name: dict(c.most_common()) for name, c in sorted(guardrails.items())},
            "turns_with_step_errors": sum(1 for p in turns.values() if p.get("step_errors")),
            "sessions": len(sessions),
            "end_type": dict(Counter(p.get("session_end_type") or "(none)" for p in sessions.values()).most_common()),
            "sessions_with_action_errors": sum(1 for p in sessions.values() if p.get("session_action_errors"))}


def summarize(records, config=None, skipped=None, unit_count=None):
    ok = [r for r in records if r["status"] == "ok"]
    infra = [r for r in records if r["status"] != "ok"]
    n = len(records)
    routed = [r for r in ok if r["topic_match"] is not None]
    texts = [r for r in ok if r["proxies"]]
    confusion = Counter(tuple(r["confusion"]) for r in ok if r["confusion"])
    violations = Counter(v for r in ok for v in r["schema_violations"] or [])
    return {
        "schema": SCHEMA_SUMMARY,
        "config": config or {},
        "counts": {
            "units": unit_count if unit_count is not None else len({r["unit_id"] for r in records}),
            "records": n, "scored": len(ok), "infra_error": len(infra),
            "cached": sum(1 for r in records if r.get("cached")),
            "infra_rate": round(len(infra) / n, 4) if n else 0.0,
            "infra_by_kind": dict(Counter(r["error_kind"] for r in infra).most_common()),
            "timed_out_units": timed_out_units(records),
            "skipped_steps": dict(skipped or {}),
        },
        "overall": aggregate(ok),
        "by_kind": _group(ok, lambda r: [r["kind"]]),
        "by_node": _group(ok, lambda r: [r["node"]]),
        "by_tool": _group(ok, golden_tools),
        "by_bucket": dict(Counter(r["bucket"] for r in ok).most_common()),
        "by_split": _group(ok, lambda r: [r["split"]] if r.get("split") else []),
        "by_groundedness": _group(ok, lambda r: [groundedness(r)]),
        "production": production_summary(records),
        "topic": {"n": len(routed), "match": sum(1 for r in routed if r["topic_match"]),
                  "rate": round(sum(1 for r in routed if r["topic_match"]) / len(routed), 4) if routed else None},
        "confusion": [{"golden": g, "candidate": c, "n": k} for (g, c), k in confusion.most_common()],
        "schema_violations": {"records": sum(1 for r in ok if r["schema_violations"]),
                              "notes": dict(violations.most_common())},
        "text": {
            "n": len(texts),
            "median_len_ratio": round(statistics.median(r["proxies"]["len_ratio"] for r in texts), 3) if texts else None,
            "question_ending_agrees": sum(1 for r in texts if r["proxies"]["golden_ends_with_question"]
                                          == r["proxies"]["candidate_ends_with_question"]),
            "raw_id_leaks": sum(1 for r in texts if r["proxies"]["candidate_raw_ids"] > r["proxies"]["golden_raw_ids"]),
        },
        "per_repeat": {str(rep): aggregate([r for r in ok if r["repeat"] == rep])
                       for rep in sorted({r["repeat"] for r in records})},
        "judge_calls": sum(len(r["judge"] or []) for r in ok),
        "usage": _usage_totals(records),
    }


def timed_out_units(records):
    """The units whose every record timed out: the model may not finish them (a runaway answer)."""
    timed_out = defaultdict(list)
    for r in records:
        timed_out[r["unit_id"]].append(r["status"] != "ok" and r.get("error_kind") in TIMEOUT_KINDS)
    return sum(1 for flags in timed_out.values() if all(flags))


def _usage_totals(records):
    totals = Counter()
    for r in records:
        for k, v in (r.get("usage") or {}).items():
            if isinstance(v, (int, float)) and not isinstance(v, bool):
                totals[k] += v
    return dict(totals)


def _names(calls):
    return "+".join(c["name"] or "" for c in calls or [])


def csv_row(rec):
    """Legacy CSV columns for one record (topic columns only on router steps)."""
    g_calls = rec["golden"]["tool_calls"]
    resp = rec["response"] or {}
    c_calls = resp.get("tool_calls") or []
    ok = rec["status"] == "ok"
    router = rec["step_kind"] == "router"
    row = {
        "session_id": rec["session_id"], "utterance": rec["user_utterance"],
        "original_model": rec["golden_model"], "replay_model": rec["model"],
        "actual_topic": _names(g_calls) if router else (rec["topic"] or ""),
        "replayed_topic": _names(c_calls) if router and ok else "",
        "topic_match": int(bool(rec["topic_match"])) if router and ok else "",
        "actual_action": _names(g_calls), "replayed_action": _names(c_calls),
        "function_match_score": "", "function_args_score": "",
        "actual_outcome": rec["golden"]["text"], "replayed_outcome": resp.get("text") or "",
        "text_resp_score": "",
        "unit_id": rec["unit_id"], "node": rec["node"], "step_kind": rec["step_kind"],
        "repeat": rec["repeat"], "status": rec["status"], "bucket": rec["bucket"] or "",
        "unit_score": rec["score"] if ok else "",
    }
    if ok:
        if g_calls or c_calls:
            row["function_match_score"] = int(bool(g_calls and c_calls and rec["names_strict"]))
        if rec["names"]:
            row["function_args_score"] = int(bool(rec["args"]))
        if not g_calls and not c_calls:
            row["text_resp_score"] = int(bool(rec["text"]))
    return row


def write_csv(path, records):
    with open_private(path, newline="") as f:
        w = csv.DictWriter(f, fieldnames=CSV_FIELDS)
        w.writeheader()
        for rec in records:
            w.writerow(redact_obj(csv_row(rec)))
