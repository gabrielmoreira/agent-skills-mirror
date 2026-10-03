#!/usr/bin/env python3
"""Analyze collected legacy/draft preview trials and emit the comparison report.

DIVISION OF LABOR:
  * Rubric #1 (trace / action equality) is MECHANICAL — it compares structured
    identifiers pulled from the local plan traces (subagent topic, ordered
    action names). This is objective equality, so the script does it.
  * Rubric #2 (response discrepancy) is a SEMANTIC judgment — data fidelity,
    formatting, verbosity, tone, spec compliance. This CANNOT be done by regex
    or heuristics. The script does NOT score it. It emits the verbatim responses
    plus an analysis prompt for an LLM judge (or human) to complete.

ORACLE MODEL (Rubric #1): legacy is a BASELINE, not the oracle. Three references:
    spec   = expected_subagent/expected_actions (authored from intent) — ORACLE
    legacy = what the old agent actually did — descriptive baseline, can be WRONG
    draft  = the NGA under test
  We classify the spec-legacy-draft triangle instead of gating on draft==legacy:
    legacy==spec & draft==spec           -> PASS
    legacy==spec & draft!=spec           -> DRAFT-REGRESSION (fix draft)
    legacy!=spec & draft==spec           -> PASS + LEGACY-DEFECT (draft fixed it)
    legacy!=spec & draft!=spec & l==d    -> SPEC-REVIEW (spec likely stale)
    legacy!=spec & draft!=spec & l!=d    -> ADJUDICATE (LLM judge decides)
  If no spec is supplied the utterance is SPEC-UNVERIFIED: fall back to the
  legacy-vs-draft baseline diff + judge.

DRIFT (across iterations): an accepted BASELINE file records the last
  spec-approved (subagent, actions) per utterance. Each run diffs the DRAFT
  signature against it — a change flags DRIFT even if it still matches the spec,
  catching unintended agentscript drift. Re-baseline deliberately (REBASELINE=1)
  when instructions intentionally change, so intended changes update truth
  instead of firing false regressions.

Nothing here is agent- or utterance-specific: no field labels, no domain
vocabulary, no expected values baked in (expected_*/baseline are per run/repo).

Rubric #1 source — the LOCAL plan trace `sf agent preview end` writes to
  .sfdx/agents/<agentId>/sessions/<sid>/traces/<planId>.json
Both sides populate it on CLI>=2.149.9 (@salesforce/agents>=2.0.4). We read
`topic`/`intent` (subagent) and ordered FunctionStep entries (action name/input/
status), for legacy (ReAct: UpdateTopicStep+topic) and draft (ScriptAgent:
TransitionStep). Names match by substring containment (name_match), since legacy
names append a definition-id suffix of arbitrary format.

Usage: analyze.py <run_dir> <utt_id> [expected_subagent] [expected_actions_csv]
  expected_* are OPTIONAL. When omitted, only observed traces + the
  legacy-vs-draft cross-check + drift are reported (no vs-spec triangle verdict).
  Traces live under `.sfdx/agents`; the tool auto-locates it by walking up from
  cwd (then from <run_dir>), so it runs from any directory inside the repo. Only
  if no `.sfdx/agents` exists on either path does a subject report a (correct)
  UNVERIFIED-TRACE. <run_dir> may be relative (e.g. agent-eval/runs/<id>).
Env (optional):
  EVAL_ORG      label only.
  DEMO_CONTACT  if set, the first draft action input is checked for this contactId.
  EVAL_BASELINE path to the accepted-baseline JSON (default agent-eval/baseline.json).
  REBASELINE    if "1", write the current draft signature into the baseline for
                this utterance (deliberate, human-approved re-baseline) and exit.
Writes <run_dir>/report.md and prints it.
"""
import json, sys, re, glob, os, datetime

RUN = sys.argv[1]
UTT = sys.argv[2] if len(sys.argv) > 2 else "utterance"
EXP_SUB = sys.argv[3] if len(sys.argv) > 3 and sys.argv[3] else None
EXP_ACTS = [a for a in (sys.argv[4].split(",") if len(sys.argv) > 4 else []) if a]
ORG = os.environ.get("EVAL_ORG", "target-org")
DEMO_CONTACT = os.environ.get("DEMO_CONTACT")  # None => no contact-binding assertion
BASELINE_FILE = os.environ.get("EVAL_BASELINE", os.path.join("agent-eval", "baseline.json"))
REBASELINE = os.environ.get("REBASELINE") == "1"

# Locate `.sfdx/agents` by walking UP from cwd (then from the run dir) so the
# tool works no matter which directory it's invoked from — otherwise a wrong cwd
# silently yields a false UNVERIFIED-TRACE for every subject.
def _find_sfdx_agents():
    for start in (os.getcwd(), os.path.abspath(RUN)):
        d = start
        while True:
            cand = os.path.join(d, ".sfdx", "agents")
            if os.path.isdir(cand):
                return cand
            parent = os.path.dirname(d)
            if parent == d:
                break
            d = parent
    # Fall back to the cwd-relative path; parse_trace() then reports "not found".
    return os.path.join(os.getcwd(), ".sfdx", "agents")


SFDX_AGENTS = _find_sfdx_agents()


def load(subj):
    out = []
    for f in sorted(glob.glob(f"{RUN}/{subj}/{UTT}/trial-*/trial.json")):
        with open(f) as fh:
            out.append(json.load(fh))
    return out


# ---- Trace parsing (mechanical rubric #1) -----------------------------------
def find_trace(plan_id):
    if not plan_id:
        return None
    hits = glob.glob(f"{SFDX_AGENTS}/**/traces/{plan_id}.json", recursive=True)
    return hits[0] if hits else None


# Legacy topic/action names carry a definition-id suffix appended to the base
# name (e.g. Get_All_Loan_Application_Details_179KX000000YehM), while the NGA
# draft uses the clean base name. The suffix format is NOT fixed (length/charset
# vary), so a regex strip is unreliable. Instead treat two names as the same
# entity when either is a substring of the other (order-independent, since the
# suffix may land on either side). Compared case-insensitively.
def name_match(a, b):
    if a is None or b is None:
        return a == b
    a, b = a.lower(), b.lower()
    return a in b or b in a


def names_match(xs, ys):
    return len(xs) == len(ys) and all(name_match(x, y) for x, y in zip(xs, ys))


def signature(topic, action_names):
    """Route+action signature = [subagent] + ordered actions. Compared with
    names_match so legacy definition-id suffixes are tolerated."""
    return [topic] + list(action_names or [])


def triangle_verdict(leg_sig, draft_sig, spec_sig):
    """Classify the spec-legacy-draft triangle. Returns (verdict, note).
    spec_sig is None when no expected_* was supplied (SPEC-UNVERIFIED)."""
    if not spec_sig or spec_sig == [None]:
        same = names_match(leg_sig, draft_sig)
        return ("SPEC-UNVERIFIED",
                "no spec supplied — "
                + ("draft matches legacy baseline" if same
                   else "draft diverges from legacy baseline; judge must decide"))
    ls = names_match(leg_sig, spec_sig)
    ds = names_match(draft_sig, spec_sig)
    if ls and ds:
        return ("PASS", "legacy, draft, and spec all agree")
    if ls and not ds:
        return ("DRAFT-REGRESSION", "legacy matched the spec but the draft does not — fix the draft")
    if ds and not ls:
        return ("PASS + LEGACY-DEFECT",
                "draft matches the spec; legacy diverged — legacy was wrong, the migration fixed it")
    # neither matches the spec
    if names_match(leg_sig, draft_sig):
        return ("SPEC-REVIEW", "legacy and draft agree with each other but not the spec — the spec is likely stale/wrong")
    return ("ADJUDICATE", "three-way disagreement (spec vs legacy vs draft) — LLM judge must adjudicate with traces + responses")


def load_baseline():
    try:
        with open(BASELINE_FILE) as fh:
            return json.load(fh)
    except Exception:
        return {}


def save_baseline(bl):
    os.makedirs(os.path.dirname(BASELINE_FILE) or ".", exist_ok=True)
    with open(BASELINE_FILE, "w") as fh:
        json.dump(bl, fh, indent=2, sort_keys=True)


def parse_trace(plan_id):
    """Return normalized trace evidence, or a reason it's unavailable.

    Handles BOTH local trace shapes:
      - draft (ScriptAgent):   routing via TransitionStep{from_agent,to_agent}
      - legacy (ProductionAgent, CLI>=2.149.9 / @salesforce/agents>=2.0.4):
        routing via UpdateTopicStep + `topic`; names carry a definitionId suffix.
    Legacy populates only when the SDK fetches the v1.1 preview plans endpoint;
    older SDKs (<=2.0.1) stub getTrace()->undefined and write `{}` (empty plan).
    Names are kept RAW here; equality is decided by name_match() (substring),
    not by stripping the suffix.
    """
    tf = find_trace(plan_id)
    if not tf:
        return {"available": False, "reason": "trace file not found"}
    try:
        with open(tf) as fh:
            d = json.load(fh)
    except Exception as e:
        return {"available": False, "reason": f"unreadable: {e}"}
    if not isinstance(d, dict) or not d.get("plan"):
        return {"available": False,
                "reason": "empty plan ({}) — SDK too old? need CLI>=2.149.9 (@salesforce/agents>=2.0.4)"}
    transitions, actions = [], []
    for s in d["plan"]:
        if s.get("type") == "TransitionStep":            # draft shape
            dd = s.get("data", {})
            transitions.append((dd.get("from_agent"), dd.get("to_agent")))
        if s.get("type") == "FunctionStep":              # both shapes
            fn = s.get("function", {})
            out = fn.get("output", {})
            actions.append({
                "name": fn.get("name"),
                "input": fn.get("input"),
                "status": out.get("__action_execution_status__") if isinstance(out, dict) else None,
            })
    topic = d.get("topic")
    # Legacy routes via UpdateTopicStep rather than TransitionStep; synthesize a
    # transition to the topic so the report row is uniform across both shapes.
    if not transitions and topic:
        transitions = [("Agent Router", topic)]
    return {
        "available": True,
        "topic": topic,
        "intent": d.get("intent"),
        "transitions": transitions,
        "actions": actions,
        "action_names": [a["name"] for a in actions],
    }


leg, dr = load("legacy"), load("draft")
if not leg or not dr:
    sys.exit(f"missing trials: legacy={len(leg)} draft={len(dr)}")
wc = lambda t: len((t or "").split())

# Trace evidence per subject (use trial 1's planId as representative).
leg_tr = parse_trace(leg[0].get("planId"))
dr_tr = parse_trace(dr[0].get("planId"))

# Signatures (route + ordered actions) for the triangle + drift comparisons.
leg_sig = signature(leg_tr.get("topic"), leg_tr.get("action_names")) if leg_tr["available"] else None
draft_sig = signature(dr_tr.get("topic"), dr_tr.get("action_names")) if dr_tr["available"] else None
spec_sig = signature(EXP_SUB, EXP_ACTS) if (EXP_SUB or EXP_ACTS) else None

# --- Deliberate re-baseline: record the current DRAFT signature and exit. -----
# This is the human-approved "the draft is now correct; make it the baseline"
# action. Use after an intentional instruction change (or first approval).
if REBASELINE:
    if not dr_tr["available"]:
        sys.exit("REBASELINE refused: draft trace unavailable (cannot capture a signature).")
    bl = load_baseline()
    bl[UTT] = {
        "subagent": dr_tr["topic"],
        "actions": dr_tr["action_names"],
        "approved_at": datetime.datetime.now().isoformat(timespec="seconds"),
        "approved_from_run": RUN,
    }
    save_baseline(bl)
    print(f"Re-baselined `{UTT}` in {BASELINE_FILE}: subagent={dr_tr['topic']} actions={dr_tr['action_names']}")
    sys.exit(0)

# Triangle verdict (spec vs legacy vs draft) + drift vs accepted baseline.
tri_verdict, tri_note = (triangle_verdict(leg_sig, draft_sig, spec_sig)
                         if (leg_tr["available"] and dr_tr["available"])
                         else ("UNVERIFIED-TRACE", "one or both traces unavailable"))
baseline = load_baseline()
base_entry = baseline.get(UTT)
if base_entry and draft_sig:
    base_sig = signature(base_entry.get("subagent"), base_entry.get("actions"))
    drift = not names_match(base_sig, draft_sig)
else:
    base_sig, drift = None, None  # None => no baseline recorded yet

L = []
p = L.append
p(f"# Legacy vs NGA Regression Report — utterance `{UTT}`\n")
p(f"- Run: `{RUN}`  | Org: `{ORG}` | Trials: {len(leg)} each")
p(f"- Legacy latency (ms): {[r['latency_ms'] for r in leg]}  | Draft: {[r['latency_ms'] for r in dr]}")
p(f"- content-safe (all): legacy {all(r['isContentSafe'] for r in leg)} | draft {all(r['isContentSafe'] for r in dr)}")
p(f"- word count (per trial): legacy {[wc(r['response']) for r in leg]} | draft {[wc(r['response']) for r in dr]}")
p(f"- Legacy planIds: {[r['planId'] for r in leg]}")
p(f"- Draft  planIds: {[r['planId'] for r in dr]}\n")

# ---- Rubric #1 — mechanical -------------------------------------------------
p("## Rubric #1 — Trace / action equality (MECHANICAL, from local planId trace)\n")
if EXP_SUB or EXP_ACTS:
    p(f"Expected (from suite): subagent `{EXP_SUB}`, actions `{EXP_ACTS}`.\n")
else:
    p("_No expected subagent/actions supplied — reporting observed traces and the "
      "legacy-vs-draft cross-check only._\n")
p("| subject | trace | subagent (topic) | router transition | ordered actions | verdict |")
p("|---|---|---|---|---|---|")


def trace_row(name, tr):
    if not tr["available"]:
        return f"| {name} | ❌ {tr['reason']} | — | — | — | **UNVERIFIED-TRACE** |"
    trans = " → ".join(str(x) for x in tr["transitions"][-1]) if tr["transitions"] else "(none)"
    acts = ", ".join(a["name"] for a in tr["actions"]) or "(none)"
    if EXP_SUB or EXP_ACTS:
        sub_ok = name_match(tr["topic"], EXP_SUB) if EXP_SUB else True
        act_ok = names_match(tr["action_names"], EXP_ACTS) if EXP_ACTS else True
        verdict = "TRACE-VERIFIED ✅" if (sub_ok and act_ok) else "TRACE-DIVERGENT ⚠️"
    else:
        verdict = "(observed)"
    return f"| {name} | ✅ local | {tr['topic']} | {trans} | {acts} | **{verdict}** |"


p(trace_row("legacy", leg_tr))
p(trace_row("draft", dr_tr))
if leg_tr["available"] and dr_tr["available"]:
    same_sub = name_match(leg_tr["topic"], dr_tr["topic"])
    same_acts = names_match(leg_tr["action_names"], dr_tr["action_names"])
    p(f"\n**Legacy vs draft:** subagent {'✅ match' if same_sub else '❌ differ'} "
      f"(legacy `{leg_tr['topic']}` vs draft `{dr_tr['topic']}`) · "
      f"actions {'✅ match' if same_acts else '❌ differ'} "
      f"(legacy `{leg_tr['action_names']}` vs draft `{dr_tr['action_names']}`) → "
      f"**{'ROUTE+ACTION EQUIVALENT' if (same_sub and same_acts) else 'TRACE-DIVERGENT'}**")
# ---- Triangle verdict (spec vs legacy vs draft) + drift ---------------------
p("\n### Oracle triangle (spec vs legacy vs draft)\n")
p("| reference | subagent | actions |")
p("|---|---|---|")
p(f"| spec (oracle) | {EXP_SUB or '_none supplied_'} | {EXP_ACTS or '_none supplied_'} |")
p(f"| legacy (baseline) | {leg_tr.get('topic') if leg_tr['available'] else '—'} | "
  f"{leg_tr.get('action_names') if leg_tr['available'] else '—'} |")
p(f"| draft (under test) | {dr_tr.get('topic') if dr_tr['available'] else '—'} | "
  f"{dr_tr.get('action_names') if dr_tr['available'] else '—'} |")
p(f"\n**Triangle verdict: `{tri_verdict}`** — {tri_note}\n")
p("> Legacy is a descriptive baseline, NOT the oracle: it can be wrong or miss "
  "an action. The spec (expected_*) is the oracle. `PASS + LEGACY-DEFECT` means "
  "the draft matches the spec while legacy diverged — the migration fixed a legacy "
  "defect. `DRAFT-REGRESSION` means legacy was right and the draft broke it. "
  "`SPEC-REVIEW`/`ADJUDICATE` escalate to the LLM judge.\n")

# Drift vs the accepted baseline (unintended-change detector).
if drift is None:
    p(f"**Drift:** no accepted baseline recorded for `{UTT}` yet "
      f"(set it deliberately with `REBASELINE=1`). File: `{BASELINE_FILE}`.\n")
elif drift:
    p(f"**Drift: ⚠️ DETECTED** — the draft signature changed vs the accepted "
      f"baseline (`{base_entry.get('approved_at')}`).\n"
      f"- baseline: subagent `{base_entry.get('subagent')}` actions `{base_entry.get('actions')}`\n"
      f"- current draft: subagent `{dr_tr.get('topic')}` actions `{dr_tr.get('action_names')}`\n"
      f"\n> If this change was intended, re-approve with `REBASELINE=1`. Otherwise the "
      f"draft drifted from its last spec-approved behavior — investigate.\n")
else:
    p(f"**Drift:** ✅ none — draft matches the accepted baseline "
      f"(`{base_entry.get('approved_at')}`).\n")

p("\n> **Local, symmetric trace.** Both sides write a full local plan trace at "
  "`.sfdx/agents/<agentId>/sessions/<sid>/traces/<planId>.json` "
  "(`topic`=subagent + ordered `FunctionStep` action name/input/status, "
  "type-agnostic across Apex/Flow/Prompt). Requires **CLI >=2.149.9 "
  "(@salesforce/agents>=2.0.4)**; older SDKs stubbed `ProductionAgent.getTrace()` "
  "and wrote `{}`. Legacy names carry a definition-id suffix of arbitrary format; "
  "names match by substring containment (either side), not suffix-stripping.\n")

if dr_tr["available"] and dr_tr["actions"]:
    ci = dr_tr["actions"][0].get("input")
    if DEMO_CONTACT:
        ok = isinstance(ci, dict) and ci.get("contactId") == DEMO_CONTACT
        p(f"Draft first action input: `{json.dumps(ci)}` — "
          f"{'✅ bound to DEMO_CONTACT' if ok else '⚠️ not bound to DEMO_CONTACT'}\n")
    else:
        p(f"Draft first action input: `{json.dumps(ci)}` (set DEMO_CONTACT env to assert binding)\n")

# ---- Responses (verbatim, all trials) ---------------------------------------
p("## Responses (verbatim)\n")
for subj, rows in (("Legacy", leg), ("Draft NGA", dr)):
    p(f"### {subj}\n")
    for r in rows:
        p(f"**Trial {r['trial']}** (planId `{r['planId']}`):\n```\n{r['response']}\n```\n")

# ---- Rubric #2 — LLM analysis prompt (NOT scored by this script) ------------
p("## Rubric #2 — Response analysis (LLM judge — complete this)\n")
p("> The script does not score responses. An LLM (or human) must read the "
  "verbatim responses above and answer the rubric below. Base every claim on the "
  "actual text; do not assume domain-specific fields.\n")
drift_ctx = ("no baseline recorded yet" if drift is None
             else "DRIFTED from accepted baseline" if drift
             else "matches accepted baseline")
p(f"> **Mechanical context for the judge (Rubric #1):** triangle verdict "
  f"`{tri_verdict}` — {tri_note}; drift status: {drift_ctx}. Treat the triangle "
  f"verdict as the routing/action ground truth: legacy is a baseline, not the "
  f"oracle. If the verdict is `PASS + LEGACY-DEFECT`, do not penalize the draft "
  f"for differing from legacy — legacy was wrong. If `DRAFT-REGRESSION`, the draft "
  f"broke a behavior legacy got right. If `SPEC-REVIEW`/`ADJUDICATE`, you are the "
  f"tie-breaker — decide which behavior is actually correct from the responses.\n")
p("""You are comparing a **legacy** agent against its **migrated NGA draft** for
the same utterance. Using ONLY the response texts above plus the Rubric #1 trace
facts, produce:

1. **Intra-trial consistency** — for each subject, are the N trials materially
   equivalent (same facts, acceptable wording variance) or do they diverge?
   Pick a canonical trial for each side.
2. **Data fidelity** — do legacy and draft agree on every concrete fact the
   responses assert (numbers, amounts, dates, statuses, named entities, IDs)?
   List any value the draft changed, dropped, or added. A factual mismatch is a
   **REGRESSION**, not a style difference.
3. **Formatting** — structural differences: bullets/headers/lists, number and
   money formatting, and any leaked internal field/action API names.
4. **Verbosity & tone** — length, clarity, empathy, and whether each ends with
   an appropriate follow-up/closing offer.
5. **Spec compliance** — does each side satisfy the utterance's intent? Note if
   the Rubric #1 action set differs (e.g. one side grounded via a retrieval
   action and the other answered from model knowledge) and whether that changes
   answer quality or trustworthiness.
6. **Classification** — one of `EQUIVALENT` | `IMPROVED` | `ACCEPTABLE-DIFF` |
   `REGRESSION`, with a one-line justification. If not `EQUIVALENT`/`IMPROVED`,
   give a concrete recommended `.agent` change.
""")

report = "\n".join(L)
with open(f"{RUN}/report.md", "w") as fh:
    fh.write(report)
print(report)
