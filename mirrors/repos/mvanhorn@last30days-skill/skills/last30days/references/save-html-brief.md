# Save shareable HTML brief

This reference file is loaded by the main `SKILL.md` when the user asked for an HTML brief (either through an HTML-looking prompt argument like `--emit=html` / `--emit:html` / `--html`, or in natural language - "give me a shareable HTML brief", "give it to me in HTML", "for Slack", "for Notion", "export as HTML", etc.). The detection happens in `SKILL.md` so that the common no-HTML path stays short; the implementation lives here. Those prompt arguments are user intent signals for the skill; they are not the full Python CLI contract.

The contract has two modes:

- **HTML as the requested deliverable** (`--emit=html`, `--emit:html`, `--html`, or prose like "give it to me in HTML"): the HTML artifact is the primary output. Write the synthesis to the temp file, render the HTML, then give a concise artifact handoff in chat instead of pasting the full Markdown report again.
- **Normal report plus HTML copy** (the user asks for the normal report and also wants an HTML copy): the synthesis still appears in chat as the primary output. The HTML is an additional artifact saved to disk for sharing. Both happen in the same turn.

## When to fire this flow

- For normal-report-plus-HTML mode: after you have already emitted the full chat response: badge, "What I learned:" (or comparison title), bold-lead-in paragraphs with citations, KEY PATTERNS list, engine footer pass-through, invitation block.
- For HTML-as-deliverable mode: after you have drafted the synthesis that will go into the HTML, before emitting the final chat response.
- BEFORE the WAIT FOR USER'S RESPONSE pause.
- ONLY if the user asked. Do NOT save HTML when the user didn't ask for it.

## How to fire it

```bash
# 1. Write your synthesis prose VERBATIM to a temp file. The synthesis is the
#    "What I learned:" prose label, the bold-lead-in paragraphs with their
#    inline citations, and the "KEY PATTERNS from the research:" numbered list.
#    Do NOT include the badge or the engine footer in the temp file - the engine
#    adds those when it renders the HTML.
#    - HTML-as-deliverable mode: use the exact synthesis draft you prepared for
#      the artifact. Do not paste it to chat first.
#    - Normal-report-plus-HTML mode: use the exact synthesis text you already
#      wrote in chat.
#    In both modes, do not paraphrase, summarize, or reorder. The HTML must read
#    identically to the intended report in voice and citations.
SYNTHESIS_FILE="/tmp/last30days-synthesis-${CLAUDE_SESSION_ID}.md"
# >| not >: fixed path may already exist on a same-session re-run; a plain >
# is refused under `set -o noclobber`.
cat >| "$SYNTHESIS_FILE" <<'SYNTHESIS_EOF'
What I learned:

**{First headline}** - {body with [name](url) inline citations}

**{Second headline}** - {body}

**{Third headline}** - {body}

KEY PATTERNS from the research:
1. {pattern} - per [@handle](url)
2. {pattern} - per [r/sub](url)
3. {pattern} - per [@handle](url)
SYNTHESIS_EOF

# 2. Convert the synthesis to a self-contained HTML file via the engine.
#    REPLAY THE SAME SCOPE FLAGS as your original run (--plan, --hiring-signals,
#    resolved --x-handle/--subreddits/etc). On a same-topic follow-up, the
#    engine reuses the structured last-report cache at
#    ~/.config/last30days/last-report.json to build badge metadata and footer
#    without re-running source fetchers. That cache is intentionally short-lived
#    (default: one hour; tune with LAST30DAYS_REPORT_CACHE_TTL_SECONDS, or set
#    it to 0 to disable reuse). If the cache is stale, missing, or for a
#    different topic, stderr says "No matching cached report data" and the
#    engine falls back to a fresh run; the same scope flags keep that fallback
#    aligned with the synthesis body.
SLUG=$(echo "$TOPIC" | tr '[:upper:]' '[:lower:]' | tr -cs 'a-z0-9' '-' | sed 's/^-//;s/-$//')
HTML_PATH="${LAST30DAYS_MEMORY_DIR}/${SLUG}-brief.html"
# Collision guard: the `> "$HTML_PATH"` redirect below OVERWRITES - the engine
# does NOT auto-date the brief (its date-suffix logic applies only to --save-dir
# raw files, not to this redirected --emit=html stream). So if the clean name
# already exists, date-suffix it here to avoid clobbering a prior brief.
if [ -f "$HTML_PATH" ]; then
  HTML_PATH="${LAST30DAYS_MEMORY_DIR}/${SLUG}-brief-$(date +%F).html"
fi
"${LAST30DAYS_PYTHON}" "${SKILL_ROOT}/scripts/last30days.py" "${TOPIC}" \
  --emit=html \
  --synthesis-file "$SYNTHESIS_FILE" \
  "${SCOPE_FLAGS[@]}" \
  >| "$HTML_PATH"   # >| not >: noclobber-safe write to the collision-guarded path
#    where SCOPE_FLAGS is the same array you passed the first time, e.g.
#    SCOPE_FLAGS=(--hiring-signals --plan "$QUERY_PLAN_FILE" --x-handle=acme).
#    For a scoped --hiring-signals brief, --hiring-signals MUST be here too so
#    the footer reflects the jobs-scoped board, not a generic crawl.

# 3. Finish with the artifact handoff described below. Do not print the saved
#    path from the shell block; the chat handoff is the single user-visible
#    completion message.
```

## Chat handoff after saving

Use the mode that matches the request.

### HTML as the requested deliverable

When HTML is the requested deliverable - whether by `--emit=html`, `--emit:html`, `--html`, or natural-language phrasing - do **not** paste the full Markdown report back into chat after saving the artifact. The user asked for an HTML deliverable; repeating the Markdown makes the run feel like a normal report with an attachment bolted on.

Respond with a concise handoff:

```text
🌐 last30days v{VERSION} · synced {YYYY-MM-DD}

📎 Shareable brief saved to <absolute HTML path>

I saved the full HTML brief locally. It is not uploaded or published anywhere.
```

If the host can safely open local files for the user and doing so matches the user's request, open the HTML file after it is written, leave the saved-path line in chat, and add `Opened locally.` Let the host choose the correct OS-specific mechanism; do not print a menu of shell commands. If opening fails or the host is headless, do not treat that as a failed report; show the path and say the file is ready to open in a browser.

### Normal report plus HTML copy

When the user asked for a normal `/last30days` report and also asked for an HTML copy, keep the full chat synthesis and append this artifact block after the invitation:

```text
📎 Shareable brief saved to <absolute HTML path>
```

If the host can safely open local files, open it for the user when that matches the request; otherwise the saved-path line is enough. Do not offer public publishing or upload in this flow. Hosted sharing is a separate opt-in capability and must not happen automatically.

## What ends up in the HTML file

The engine's `--emit=html` renderer combines:

- The badge (`🌐 last30days vX.Y.Z · synced YYYY-MM-DD`) at the top
- A single inline metadata line (`{date range} · {active sources}`) below the badge
- Your synthesis verbatim, with prose labels promoted to `<h2>` and bold lead-ins preserved
- All `[name](url)` citations rendered as `<a>` tags
- The engine footer (`✅ All agents reported back!` tree) preserved verbatim in monospace
- A colophon with the topic and a re-run hint

The renderer strips engine-internal noise that doesn't belong in a shareable artifact: the `# last30days vX.Y.Z: TOPIC` debug file header, the model-facing `> Safety note:` blockquote, and the `I'm now an expert on X` invitation block. Data quality warnings (degraded run, thin evidence, etc.) stay in the engine's stderr logs - they never leak into the share-ready file.

## Comparison mode

Same flow when the topic is `X vs Y` (or `X vs Y vs Z`). The engine routes through `render_for_html_comparison` internally; you don't need to do anything special. The synthesis temp file should still contain the comparison-shaped synthesis you wrote in chat (`## Quick Verdict`, `## {Entity}` per entity, `## Head-to-Head` table, `## The Bottom Line`, `## The emerging stack` per LAW 4 comparison exception).

## Follow-up turn

If the user runs `/last30days OpenClaw` normally, sees the synthesis in chat, and THEN explicitly refers back to that visible synthesis ("save that as HTML", "make this shareable", "turn the above into HTML"), do the same save flow on the synthesis you wrote in the previous turn. Do not re-research; the synthesis is already in the conversation history. Just write it to the temp file and call the engine with `--emit=html --synthesis-file`, then use the normal-report-plus-HTML artifact block.

If the follow-up instead asks for a new HTML deliverable ("give it to me in HTML", `--emit=html`, `--html`) rather than referring back to an already-visible report, treat it as HTML-as-deliverable mode.

The engine will try to reuse `~/.config/last30days/last-report.json` for that second invocation when it is still within `LAST30DAYS_REPORT_CACHE_TTL_SECONDS` (default: one hour). If stderr says it is reusing cached report data, continue normally. If stderr says no matching cache exists, the cache may be stale; let the command finish only if you supplied the same scope flags as the original run. Otherwise stop and re-run with the original flags so the HTML footer does not describe a different dataset.

## What NOT to do

- Do NOT save HTML if the user didn't ask. The sparse mode (no synthesis) produces a thin file; not useful as a shareable.
- Do NOT add content to the temp file beyond your synthesis prose. The badge / footer / colophon come from the engine.
- Do NOT change the file path convention. `${LAST30DAYS_MEMORY_DIR}/${SLUG}-brief.html` is the canonical location.
- Do NOT silently overwrite an existing file. The `--emit=html` output is written via a shell redirect (`>| "$HTML_PATH"`), which OVERWRITES the collision-guarded path — use `>|` not `>` because `set -o noclobber` refuses plain `>` when the file already exists. The collision guard in step 2 handles same-topic re-runs: if `{slug}-brief.html` already exists it date-suffixes to `{slug}-brief-YYYY-MM-DD.html`. Always report whichever path the redirect actually used in the chat handoff.
- Do NOT include the data quality warning text in the temp file or in your final chat line. Warnings are an engine-stderr concern, not an artifact concern.
- Do NOT publish, upload, or send the HTML to a third-party service. This reference only saves and opens local files.

## Edge cases

- **Topic with shell-special characters** (quotes, ampersands): the temp filename uses a slugified version, but the engine receives the raw topic. The `cat <<'SYNTHESIS_EOF'` quoted heredoc form handles arbitrary content without expansion. Your synthesis text can include any character.
- **Very long synthesis**: no upper bound. The engine handles long markdown bodies. Just paste verbatim.
- **Synthesis with images or non-ASCII**: emoji and Unicode pass through. Image tags pass through as raw HTML; the renderer doesn't transform them. If you didn't include images in chat, don't add them here.
- **No `${LAST30DAYS_MEMORY_DIR}` set**: defaults to `~/Documents/Last30Days/` per the SKILL.md `Configuration` section.
