#!/usr/bin/env python3
"""
Generate a self-contained HTML offline-analysis report from replay results JSON.
Adapted from hawking/ai-agent-backtesting PR #53 (build_failure_report.py).

Usage:
    python build_report.py [replay_results.json] [output.html]
"""
import json, sys, html as _html, textwrap
from pathlib import Path
from collections import Counter

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _calls(ans_json):
    """Extract [(name, args_dict), ...] from a structured answer JSON string."""
    try:
        ans = json.loads(ans_json) if isinstance(ans_json, str) else ans_json
    except (json.JSONDecodeError, TypeError):
        return []
    tcs = ans.get("tool_calls") or []
    out = []
    for tc in tcs:
        name = tc.get("name", "")
        args = tc.get("arguments", {})
        if isinstance(args, str):
            try:
                args = json.loads(args)
            except Exception:
                args = {"raw": args}
        out.append((name, args))
    return out


def _is_router(d):
    golden = _calls(d.get("GoldenAnswer", "{}"))
    if d.get("GoldenType") == "topic":
        return True
    for name, _ in golden:
        if any(name.lower().startswith(p) for p in ("route_to", "go_to", "transfer_to")):
            return True
    return False


def _bucket(d, name_hit):
    """Categorize a failing row into a failure bucket."""
    if d.get("ScoringError"):
        err = d["ScoringError"].lower()
        if "expected tool call" in err and "got text" in err:
            return "no tool call emitted"
        if "expected text" in err and "got tool call" in err:
            return "unexpected tool call"
        return "infra error"
    if d.get("ToolAltReason"):
        return "used functionally similar tool"
    if not name_hit:
        return "called a different tool"
    if d.get("SchemaViolationNotes"):
        return "args violate tool schema"
    return "args mismatch (values differ)"


def _score_topic(routers):
    if not routers:
        return None
    hits = sum(1 for d in routers if d.get("FunctionNameAgreementLenient"))
    return round(100 * hits / len(routers), 1)


def _score_action_strict(actions):
    if not actions:
        return None
    hits = sum(1 for d in actions if d.get("PassStrict") or d.get("FunctionArgsAgreement"))
    return round(100 * hits / len(actions), 1)


def _score_action_lenient(actions):
    """Count a row as passing if it passes strict OR used a functionally equivalent tool."""
    if not actions:
        return None
    hits = sum(1 for d in actions
               if d.get("PassStrict") or d.get("FunctionArgsAgreement") or d.get("FunctionNameAgreementLenient"))
    return round(100 * hits / len(actions), 1)


def _rating(score, safe_min=85, review_min=60):
    if score is None:
        return "N/A", "#64748b"
    if score >= safe_min:
        return "SAFE", "#15803d"
    if score >= review_min:
        return "REVIEW", "#b45309"
    return "UNSAFE", "#dc2626"


def _esc(text):
    return _html.escape(str(text)) if text else ""


def _json_pretty(obj):
    if isinstance(obj, str):
        try:
            obj = json.loads(obj)
        except Exception:
            return _esc(obj)
    return _esc(json.dumps(obj, indent=2))


# ---------------------------------------------------------------------------
# Card rendering
# ---------------------------------------------------------------------------

def _card(d, rec, idx):
    """Render an expandable card for a single failing row."""
    golden = _calls(d.get("GoldenAnswer", "{}"))
    predicted = _calls(d.get("PredictedAnswer", "{}"))
    g_names = [n for n, _ in golden]
    p_names = [n for n, _ in predicted]

    name_hit = d.get("FunctionNameAgreement", False)
    bucket = _bucket(d, name_hit)

    flags = []
    if d.get("ScoringError"):
        flags.append(f'<span class="flag flag-error">{_esc(d["ScoringError"][:80])}</span>')
    if d.get("ToolAltReason"):
        flags.append(f'<span class="flag flag-warn">{_esc(d["ToolAltReason"])}</span>')
    if d.get("FunctionArgsScoreReason"):
        flags.append(f'<span class="flag flag-info">Args: {_esc(str(d["FunctionArgsScoreReason"])[:120])}</span>')

    # Status badge
    if d.get("PassStrict") or d.get("FunctionArgsAgreement"):
        status_cls = "badge-pass"
        status_txt = "PASS"
    elif d.get("FunctionNameAgreementLenient"):
        status_cls = "badge-warn"
        status_txt = "PARTIAL"
    else:
        status_cls = "badge-fail"
        status_txt = "FAIL"

    # Golden vs Predicted comparison
    golden_html = ""
    for name, args in golden:
        golden_html += f'<div class="tool-call"><span class="tool-name">{_esc(name)}</span>'
        golden_html += f'<pre class="tool-args">{_json_pretty(args)}</pre></div>'
    if not golden:
        try:
            ga = json.loads(d.get("GoldenAnswer", "{}"))
            if ga.get("content"):
                golden_html = f'<div class="text-resp">{_esc(ga["content"][:300])}</div>'
        except Exception:
            pass

    predicted_html = ""
    for name, args in predicted:
        predicted_html += f'<div class="tool-call"><span class="tool-name">{_esc(name)}</span>'
        predicted_html += f'<pre class="tool-args">{_json_pretty(args)}</pre></div>'
    if not predicted:
        try:
            pa = json.loads(d.get("PredictedAnswer", "{}"))
            if pa.get("content"):
                predicted_html = f'<div class="text-resp">{_esc(pa["content"][:300])}</div>'
        except Exception:
            pass

    # Tools offered
    tools_offered = rec.get("tools", []) if rec else []
    tools_html = ", ".join(f'<code>{_esc(t)}</code>' for t in tools_offered) if tools_offered else "<em>none</em>"

    # Transcript (all messages, full content)
    messages = rec.get("messages", []) if rec else []
    transcript_html = ""
    for msg in messages:
        role = msg.get("role", "unknown")
        content = str(msg.get("content", ""))
        transcript_html += f'<div class="msg msg-{_esc(role)}"><strong>{_esc(role)}</strong>: {_esc(content)}</div>'

    return f'''
    <details class="card">
      <summary class="card-header">
        <span class="card-idx">#{idx}</span>
        <span class="{status_cls}">{status_txt}</span>
        <span class="card-bucket">{_esc(bucket)}</span>
        <span class="card-utterance">{_esc(d.get("Utterance", "")[:80])}</span>
        <span class="card-session">{_esc(d.get("AiAgentSessionId", "")[:12])}...</span>
      </summary>
      <div class="card-body">
        <div class="flags">{" ".join(flags)}</div>

        <div class="comparison">
          <div class="comp-col">
            <h4>Golden (Expected)</h4>
            {golden_html or "<em>none</em>"}
          </div>
          <div class="comp-col">
            <h4>Predicted (Replay)</h4>
            {predicted_html or "<em>none</em>"}
          </div>
        </div>

        <div class="section">
          <h4>Scores</h4>
          <table class="score-table">
            <tr><td>Function Name Match</td><td>{"Yes" if d.get("FunctionNameAgreement") else "No"}</td></tr>
            <tr><td>Function Name Match (Lenient)</td><td>{"Yes" if d.get("FunctionNameAgreementLenient") else "No"}</td></tr>
            <tr><td>Args Agreement</td><td>{"Yes" if d.get("FunctionArgsAgreement") else "No"}</td></tr>
            <tr><td>Args Score</td><td>{d.get("FunctionArgsScore", "N/A")}</td></tr>
            <tr><td>Pass Strict</td><td>{"Yes" if d.get("PassStrict") else "No"}</td></tr>
          </table>
        </div>

        <div class="section">
          <h4>Tools Offered</h4>
          <div>{tools_html}</div>
        </div>

        <details class="transcript-toggle">
          <summary>Transcript ({len(messages)} messages)</summary>
          <div class="transcript">{transcript_html or "<em>no transcript captured</em>"}</div>
        </details>
      </div>
    </details>'''


# ---------------------------------------------------------------------------
# Main HTML builder
# ---------------------------------------------------------------------------

CSS = '''
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;600;700&family=Inter:wght@400;500;600&family=IBM+Plex+Mono:wght@400;500&display=swap');

:root {
  --slate-50: #f8fafc; --slate-100: #f1f5f9; --slate-200: #e2e8f0;
  --slate-300: #cbd5e1; --slate-400: #94a3b8; --slate-500: #64748b;
  --slate-600: #475569; --slate-700: #334155; --slate-800: #1e293b;
  --slate-900: #0f172a;
  --safe: #15803d; --safe-bg: #f0fdf4; --safe-border: #bbf7d0;
  --review: #b45309; --review-bg: #fffbeb; --review-border: #fde68a;
  --unsafe: #dc2626; --unsafe-bg: #fef2f2; --unsafe-border: #fecaca;
  --radius: 12px;
}

* { box-sizing: border-box; margin: 0; padding: 0; }

body {
  font-family: 'Inter', system-ui, -apple-system, sans-serif;
  background: linear-gradient(135deg, var(--slate-50) 0%, var(--slate-100) 100%);
  color: var(--slate-800);
  line-height: 1.6;
  min-height: 100vh;
  padding: 2rem;
}

.container { max-width: 1200px; margin: 0 auto; }

h1 {
  font-family: 'Space Grotesk', sans-serif;
  font-size: 2rem;
  font-weight: 700;
  color: var(--slate-900);
  margin-bottom: 0.5rem;
}

h2 {
  font-family: 'Space Grotesk', sans-serif;
  font-size: 1.4rem;
  font-weight: 600;
  color: var(--slate-700);
  margin: 2rem 0 1rem;
  padding-bottom: 0.5rem;
  border-bottom: 2px solid var(--slate-200);
}

h3 {
  font-family: 'Space Grotesk', sans-serif;
  font-size: 1.1rem;
  font-weight: 600;
  color: var(--slate-600);
  margin-bottom: 0.5rem;
}

h4 {
  font-family: 'Space Grotesk', sans-serif;
  font-size: 0.9rem;
  font-weight: 600;
  color: var(--slate-500);
  margin-bottom: 0.3rem;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

/* Header */
.header {
  background: white;
  border-radius: var(--radius);
  padding: 2rem;
  margin-bottom: 2rem;
  box-shadow: 0 1px 3px rgba(0,0,0,0.08);
  border: 1px solid var(--slate-200);
}

.header-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 1.5rem;
  margin-top: 1rem;
  font-size: 0.875rem;
  color: var(--slate-500);
}

.header-meta dt { font-weight: 600; color: var(--slate-600); }
.header-meta dd { font-family: 'IBM Plex Mono', monospace; }

/* Verdict badge */
.verdict {
  display: inline-block;
  padding: 0.5rem 1.5rem;
  border-radius: 999px;
  font-family: 'Space Grotesk', sans-serif;
  font-weight: 700;
  font-size: 1.1rem;
  letter-spacing: 0.05em;
  color: white;
  margin-top: 1rem;
}

/* Scorecards */
.scorecards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 1.5rem;
  margin-bottom: 2rem;
}

.scorecard {
  background: white;
  border-radius: var(--radius);
  padding: 1.5rem;
  box-shadow: 0 1px 3px rgba(0,0,0,0.08);
  border: 1px solid var(--slate-200);
}

.scorecard-value {
  font-family: 'Space Grotesk', sans-serif;
  font-size: 2.5rem;
  font-weight: 700;
  margin: 0.5rem 0;
}

.scorecard-label {
  font-size: 0.875rem;
  color: var(--slate-500);
}

.scorecard-detail {
  font-size: 0.8rem;
  color: var(--slate-500);
  margin-top: 0.25rem;
}

/* Buckets */
.buckets {
  background: white;
  border-radius: var(--radius);
  padding: 1.5rem;
  margin-bottom: 2rem;
  box-shadow: 0 1px 3px rgba(0,0,0,0.08);
  border: 1px solid var(--slate-200);
}

.bucket-row {
  display: flex;
  align-items: center;
  padding: 0.5rem 0;
  border-bottom: 1px solid var(--slate-100);
}

.bucket-row:last-child { border-bottom: none; }

.bucket-name {
  flex: 1;
  font-size: 0.9rem;
  color: var(--slate-700);
}

.bucket-bar-wrap {
  flex: 2;
  height: 24px;
  background: var(--slate-100);
  border-radius: 4px;
  overflow: hidden;
  margin: 0 1rem;
}

.bucket-bar {
  height: 100%;
  background: var(--slate-400);
  border-radius: 4px;
  transition: width 0.3s ease;
}

.bucket-count {
  width: 3rem;
  text-align: right;
  font-family: 'IBM Plex Mono', monospace;
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--slate-600);
}

/* Cards */
.card {
  background: white;
  border-radius: var(--radius);
  margin-bottom: 0.75rem;
  box-shadow: 0 1px 3px rgba(0,0,0,0.08);
  border: 1px solid var(--slate-200);
  overflow: hidden;
}

.card-header {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 1rem 1.5rem;
  cursor: pointer;
  font-size: 0.9rem;
  list-style: none;
}

.card-header::-webkit-details-marker { display: none; }
.card-header::before {
  content: '\\25B6';
  font-size: 0.7rem;
  color: var(--slate-400);
  transition: transform 0.2s;
}
details[open] > .card-header::before { transform: rotate(90deg); }

.card-idx {
  font-family: 'IBM Plex Mono', monospace;
  font-weight: 600;
  color: var(--slate-500);
  min-width: 2.5rem;
}

.card-bucket {
  font-size: 0.8rem;
  color: var(--slate-500);
  background: var(--slate-100);
  padding: 0.15rem 0.5rem;
  border-radius: 4px;
}

.card-utterance {
  flex: 1;
  color: var(--slate-700);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.card-session {
  font-family: 'IBM Plex Mono', monospace;
  font-size: 0.75rem;
  color: var(--slate-500);
}

.card-body { padding: 0 1.5rem 1.5rem; }

.badge-pass {
  background: var(--safe-bg); color: var(--safe); border: 1px solid var(--safe-border);
  padding: 0.15rem 0.5rem; border-radius: 4px; font-size: 0.75rem; font-weight: 600;
}
.badge-warn {
  background: var(--review-bg); color: var(--review); border: 1px solid var(--review-border);
  padding: 0.15rem 0.5rem; border-radius: 4px; font-size: 0.75rem; font-weight: 600;
}
.badge-fail {
  background: var(--unsafe-bg); color: var(--unsafe); border: 1px solid var(--unsafe-border);
  padding: 0.15rem 0.5rem; border-radius: 4px; font-size: 0.75rem; font-weight: 600;
}

/* Flags */
.flags { margin-bottom: 1rem; display: flex; flex-wrap: wrap; gap: 0.5rem; }
.flag {
  font-size: 0.8rem; padding: 0.25rem 0.75rem; border-radius: 6px;
  font-family: 'IBM Plex Mono', monospace;
}
.flag-error { background: var(--unsafe-bg); color: var(--unsafe); border: 1px solid var(--unsafe-border); }
.flag-warn { background: var(--review-bg); color: var(--review); border: 1px solid var(--review-border); }
.flag-info { background: var(--slate-100); color: var(--slate-600); }

/* Comparison */
.comparison {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
  margin-bottom: 1rem;
}

.comp-col {
  background: var(--slate-50);
  border-radius: 8px;
  padding: 1rem;
  border: 1px solid var(--slate-200);
}

.tool-call { margin-bottom: 0.5rem; }
.tool-name {
  font-family: 'IBM Plex Mono', monospace;
  font-weight: 600;
  font-size: 0.9rem;
  color: var(--slate-800);
}

.tool-args {
  font-family: 'IBM Plex Mono', monospace;
  font-size: 0.8rem;
  background: var(--slate-100);
  padding: 0.5rem;
  border-radius: 4px;
  margin-top: 0.25rem;
  overflow-x: auto;
  white-space: pre-wrap;
  word-break: break-word;
}

.text-resp {
  font-size: 0.85rem;
  color: var(--slate-600);
  font-style: italic;
}

/* Section */
.section { margin-bottom: 1rem; }

.score-table {
  width: 100%;
  font-size: 0.85rem;
  border-collapse: collapse;
}
.score-table td {
  padding: 0.3rem 0.5rem;
  border-bottom: 1px solid var(--slate-100);
}
.score-table td:first-child { color: var(--slate-500); width: 60%; }
.score-table td:last-child { font-family: 'IBM Plex Mono', monospace; font-weight: 500; }

/* Transcript */
.transcript-toggle { margin-top: 1rem; }
.transcript-toggle > summary {
  cursor: pointer;
  font-size: 0.85rem;
  font-weight: 600;
  color: var(--slate-500);
  padding: 0.5rem 0;
}

.transcript {
  max-height: 300px;
  overflow-y: auto;
  margin-top: 0.5rem;
  padding: 0.5rem;
  background: var(--slate-50);
  border-radius: 8px;
  border: 1px solid var(--slate-200);
}

.msg {
  padding: 0.4rem 0.6rem;
  margin-bottom: 0.25rem;
  font-size: 0.8rem;
  border-radius: 4px;
  word-break: break-word;
}

.msg strong { font-size: 0.75rem; text-transform: uppercase; }
.msg-system { background: #eff6ff; color: #1e40af; }
.msg-user { background: #f0fdf4; color: #166534; }
.msg-assistant { background: #fdf4ff; color: #86198f; }
.msg-info { background: var(--slate-100); color: var(--slate-500); }

code {
  font-family: 'IBM Plex Mono', monospace;
  font-size: 0.85em;
  background: var(--slate-100);
  padding: 0.1rem 0.3rem;
  border-radius: 3px;
}

/* Pass rows section */
.pass-summary {
  background: var(--safe-bg);
  border: 1px solid var(--safe-border);
  border-radius: var(--radius);
  padding: 1rem 1.5rem;
  margin-bottom: 1.5rem;
  color: var(--safe);
  font-weight: 500;
}
'''


def build(data):
    """Build HTML report from replay results JSON data."""
    meta = data.get("metadata", {})
    rows = data.get("rows", [])
    recs = data.get("recs", {})

    routers = [d for d in rows if _is_router(d)]
    actions = [d for d in rows if not _is_router(d)]

    topic_score = _score_topic(routers)
    action_strict = _score_action_strict(actions)
    action_lenient = _score_action_lenient(actions)

    # Overall verdict uses lenient action score (functionally equivalent tools count)
    action_score = action_lenient
    if topic_score is not None and action_score is not None:
        overall = round(0.3 * topic_score + 0.7 * action_score, 1)
    elif action_score is not None:
        overall = action_score
    elif topic_score is not None:
        overall = topic_score
    else:
        overall = None

    verdict_text, verdict_color = _rating(overall)

    # A row passes if strict pass, args agreement, OR lenient name match (equivalent tool)
    def _row_passes(d):
        return d.get("PassStrict") or d.get("FunctionArgsAgreement") or d.get("FunctionNameAgreementLenient")

    failing = [d for d in rows if not _row_passes(d)]
    bucket_counts = Counter()
    for d in failing:
        name_hit = d.get("FunctionNameAgreement", False)
        bucket_counts[_bucket(d, name_hit)] += 1
    max_bucket = max(bucket_counts.values()) if bucket_counts else 1

    passing = [d for d in rows if _row_passes(d)]

    # Build HTML
    parts = []
    parts.append(f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Offline Analysis Report</title>
<style>{CSS}</style>
</head>
<body>
<div class="container">
''')

    # Header
    parts.append(f'''
<div class="header">
  <h1>Offline Analysis Report</h1>
  <div class="verdict" style="background:{verdict_color}">{verdict_text}</div>
  <dl class="header-meta">
    <div><dt>Baseline Model</dt><dd>{_esc(meta.get("baseline_model", "N/A"))}</dd></div>
    <div><dt>Replay Model</dt><dd>{_esc(meta.get("replay_model", "N/A"))}</dd></div>
    <div><dt>Org ID</dt><dd>{_esc(meta.get("org_id", "N/A"))}</dd></div>
    <div><dt>Agent</dt><dd>{_esc(meta.get("agent_api_name", "N/A") or "N/A")}</dd></div>
    <div><dt>Total Rows</dt><dd>{meta.get("total_rows", len(rows))}</dd></div>
    <div><dt>Timestamp</dt><dd>{_esc(meta.get("timestamp", ""))}</dd></div>
  </dl>
</div>
''')

    # Scorecards
    parts.append('<div class="scorecards">')

    if routers:
        t_verdict, t_color = _rating(topic_score)
        parts.append(f'''
<div class="scorecard">
  <h3>Routing</h3>
  <div class="scorecard-value" style="color:{t_color}">{topic_score}%</div>
  <div class="scorecard-label">Topic Agreement (Lenient)</div>
  <div class="scorecard-detail">{len(routers)} routing rows &middot; {t_verdict}</div>
</div>''')

    if actions:
        a_verdict, a_color = _rating(action_lenient)
        as_verdict, as_color = _rating(action_strict)
        strict_pass = sum(1 for d in actions if d.get("PassStrict"))
        args_agree = sum(1 for d in actions if d.get("FunctionArgsAgreement"))
        name_exact = sum(1 for d in actions if d.get("FunctionNameAgreement"))
        name_lenient = sum(1 for d in actions if d.get("FunctionNameAgreementLenient"))
        parts.append(f'''
<div class="scorecard">
  <h3>Action Tools (Lenient)</h3>
  <div class="scorecard-value" style="color:{a_color}">{action_lenient}%</div>
  <div class="scorecard-label">Includes functionally equivalent tools</div>
  <div class="scorecard-detail">{len(actions)} action rows &middot; {a_verdict}</div>
  <div class="scorecard-detail">{name_lenient}/{len(actions)} tool match (lenient) &middot; {name_exact}/{len(actions)} exact</div>
</div>''')
        parts.append(f'''
<div class="scorecard">
  <h3>Action Tools (Strict)</h3>
  <div class="scorecard-value" style="color:{as_color}">{action_strict}%</div>
  <div class="scorecard-label">Exact name + args agreement</div>
  <div class="scorecard-detail">{strict_pass} strict pass &middot; {args_agree} args agree</div>
</div>''')

    # Overall scorecard
    o_verdict, o_color = _rating(overall)
    parts.append(f'''
<div class="scorecard">
  <h3>Overall</h3>
  <div class="scorecard-value" style="color:{o_color}">{overall if overall is not None else "N/A"}%</div>
  <div class="scorecard-label">Weighted Score</div>
  <div class="scorecard-detail">{len(rows)} total rows &middot; {len(passing)} pass &middot; {len(failing)} fail</div>
</div>''')

    parts.append('</div>')  # end scorecards

    # Failure buckets
    if bucket_counts:
        parts.append('<div class="buckets"><h3>Failure Breakdown</h3>')
        for bucket_name, count in bucket_counts.most_common():
            pct = round(100 * count / max_bucket)
            parts.append(f'''
<div class="bucket-row">
  <span class="bucket-name">{_esc(bucket_name)}</span>
  <div class="bucket-bar-wrap"><div class="bucket-bar" style="width:{pct}%"></div></div>
  <span class="bucket-count">{count}</span>
</div>''')
        parts.append('</div>')

    # Passing rows summary
    if passing:
        parts.append(f'<div class="pass-summary">{len(passing)} row(s) passed (strict pass or args agreement)</div>')

    # Failing row cards
    if failing:
        parts.append(f'<h2>Failing Rows ({len(failing)})</h2>')
        for d in failing:
            idx = d.get("SessionRowIndex", "?")
            rec = recs.get(str(idx), {})
            parts.append(_card(d, rec, idx))

    # All passing row cards (collapsed section)
    if passing:
        parts.append(f'''
<details style="margin-top:1.5rem">
  <summary style="cursor:pointer;font-family:'Space Grotesk',sans-serif;font-weight:600;color:var(--slate-500);font-size:1.1rem;padding:0.5rem 0">
    Passing Rows ({len(passing)})
  </summary>
  <div style="margin-top:0.5rem">''')
        for d in passing:
            idx = d.get("SessionRowIndex", "?")
            rec = recs.get(str(idx), {})
            parts.append(_card(d, rec, idx))
        parts.append('</div></details>')

    parts.append('''
</div>
</body>
</html>''')

    return "\n".join(parts)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    input_path = sys.argv[1] if len(sys.argv) > 1 else "replay_results.json"
    output_path = sys.argv[2] if len(sys.argv) > 2 else "offline_analysis_report.html"

    with open(input_path) as f:
        data = json.load(f)

    html = build(data)

    with open(output_path, "w") as f:
        f.write(html)

    rows = data.get("rows", [])
    passing = sum(1 for d in rows
                  if d.get("PassStrict") or d.get("FunctionArgsAgreement") or d.get("FunctionNameAgreementLenient"))
    print(f"Report generated: {output_path}")
    print(f"  {len(rows)} rows, {passing} passing, {len(rows) - passing} failing")


if __name__ == "__main__":
    main()
