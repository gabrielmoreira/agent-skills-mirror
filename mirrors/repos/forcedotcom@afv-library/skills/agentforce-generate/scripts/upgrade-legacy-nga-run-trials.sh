#!/usr/bin/env bash
# Collect N preview trials for one subject × one utterance.
# Usage: upgrade-legacy-nga-run-trials.sh <subject:legacy|draft> <utt_id> <trials> <outdir> "<utterance>" [mode:simulate|live]
#   mode defaults to `simulate` (safe: no real side effects). Pass `live` ONLY for
#   utterances the caller has opted in per the side-effect safety gate. mode gates
#   the DRAFT only; legacy (--api-name) has no mode flag and always runs live (CLI).
# Reliable path: start -> send -> end, fresh session per trial,
# stdout->file (never 2>&1 into a parser).
# Agent api-name/bundle and org are config, supplied via env (no baked-in agent):
#   EVAL_AGENT  legacy Bot api-name AND draft bundle name (they collide by design)
#   EVAL_ORG    target-org alias
set -euo pipefail
# Force plain output: some shells/CI still get ANSI color codes on `sf --json`,
# which corrupt the JSON once stdout is redirected to a file (the parser then
# fails on the escape bytes). NO_COLOR + FORCE_COLOR=0 make the CLI emit clean JSON.
export NO_COLOR=1 FORCE_COLOR=0
SUBJECT="$1"; UTT="$2"; N="$3"; OUT="$4"; TEXT="$5"; MODE="${6:-simulate}"
case "$MODE" in simulate|live) ;; *) echo "mode must be 'simulate' or 'live' (got '$MODE')" >&2; exit 2 ;; esac
ORG="${EVAL_ORG:?set EVAL_ORG to the target-org alias}"
AGENT="${EVAL_AGENT:?set EVAL_AGENT to the agent api-name/bundle}"
# NOTE: --use-live-actions / --simulate-actions are START-ONLY flags.
# send/end accept only the subject selector (--api-name | --authoring-bundle) + --session-id.
if [ "$SUBJECT" = "legacy" ]; then
  SEL=(--api-name "$AGENT")             # session selector (start/send/end)
  START_SEL=("${SEL[@]}")               # legacy (--api-name) has no mode flag; always live (CLI)
  if [ "$MODE" = "simulate" ]; then
    echo "  NOTE: legacy (--api-name) has no simulate mode; it runs live. Gate side-effecting utterances upstream." >&2
  fi
else
  SEL=(--authoring-bundle "$AGENT")     # session selector (start/send/end)
  if [ "$MODE" = "live" ]; then
    START_SEL=(--use-live-actions "${SEL[@]}")   # mode flag only on start; explicit opt-in
  else
    START_SEL=(--simulate-actions "${SEL[@]}")   # default: safe, no real side effects
  fi
fi
mkdir -p "$OUT/$SUBJECT/$UTT"
for i in $(seq 1 "$N"); do
  d="$OUT/$SUBJECT/$UTT/trial-$i"; mkdir -p "$d"
  sf agent preview start --json "${START_SEL[@]}" -o "$ORG" > "$d/start.json" 2>"$d/start.err"
  SID=$(python3 -c "import json;print(json.load(open('$d/start.json'))['result']['sessionId'])")
  t0=$(python3 -c "import time;print(int(time.time()*1000))")
  sf agent preview send --json "${SEL[@]}" --session-id "$SID" -u "$TEXT" -o "$ORG" > "$d/send.json" 2>"$d/send.err"
  t1=$(python3 -c "import time;print(int(time.time()*1000))")
  sf agent preview end --json "${SEL[@]}" --session-id "$SID" -o "$ORG" > "$d/end.json" 2>"$d/end.err" || true
  python3 - "$d" "$SUBJECT" "$UTT" "$i" "$SID" "$((t1-t0))" <<'PY'
import json,sys
d,subject,utt,i,sid,lat=sys.argv[1:7]
s=json.load(open(f"{d}/send.json"))["result"]
m=s["messages"][0]
rec={"subject":subject,"utterance_id":utt,"trial":int(i),"sessionId":sid,
     "planId":m.get("planId"),"isContentSafe":m.get("isContentSafe"),
     "response":m.get("message"),"result":m.get("result"),
     "citedReferences":m.get("citedReferences"),"latency_ms":int(lat)}
json.dump(rec,open(f"{d}/trial.json","w"),indent=1)
print(f"  {subject} {utt} trial {i}: {int(lat)}ms safe={m.get('isContentSafe')} planId={m.get('planId')}")
PY
done
