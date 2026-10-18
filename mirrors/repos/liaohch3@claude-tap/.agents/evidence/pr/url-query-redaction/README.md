# URL query redaction regression evidence

## Reproduction and behavior

The real captured Edit input below is source code, not a URL. Its `//` comment,
fullwidth colon and ternary `?` make Python's `urlsplit()` raise `ValueError`:

```javascript
// Deliverables： only
const result = ready ? token === expected : fallback;
```

The original six-request session also contains this text in its version-4 cached
`first_user`. Recovery therefore starts before record redaction, when that cached
summary is normalized. Session records and online HTML return HTTP 200 on first
and repeated reads; the Edit old/new strings show `REDACTED`.

Recovery is limited to display scopes and the original `urlsplit()` call. Other
redaction failures still propagate. Successful parsing uses the original
query/form/JSON rules. After an observed URL-parser failure, session responses
hide their nonempty `first_user`, `last_response` and `error`; online HTML hides
`sys_hint`, `session_user_text` and `error_message` across the generated metadata.
This deliberately avoids guessing which truncated preview came from the failed
source. Record siblings and other metadata remain intact.

The existing record queries, decoding, preview generation and cache version
remain unchanged. Each existing summary write is skipped if that summary build
recovered a URL-parser failure; normal writes keep their
original values and order. Append/import builders outside display retain the
original error behavior. Raw captures and JSONL/compact/HTML downloads are unchanged.

Existing recognition/depth limits remain. A page that never parses the failed
source can retain an old truncated preview, as in the baseline; this fix does not
scan other pages to reconstruct provenance. An existing successful cache write
that precedes a later records error is also retained.

## Validation

Final candidate validation on Python 3.13.14 with Chromium: **1,683 passed,
26 skipped**. The **404 focused regressions** cover original successful outputs,
actual parser failures, nested leaves, public siblings, cached summaries,
HTML metadata, pagination, repeated requests,
cache-write boundaries, concurrent scope isolation and unchanged raw exports.

```bash
python -m pytest tests/ -q -x --timeout=60
ruff check .
ruff format --check .
git diff --check
```

Normal e17 comparisons retain identical complete response bytes, SQL shapes,
decoded rows and existing redactor/parser call counts. Alternating latency runs
still observe a small positive difference for 1,000-record responses: the fixed
32-pair follow-up has a +0.883 ms paired median (about +0.55%). No zero-latency-cost
claim is made. Python coverage is 85.61% overall and 100% of changed executable
lines (42/42) relative to e17.

## Screenshots

The evidence shows three distinct states in order: original HTTP 500, normal
query redaction returning HTTP 200, and parser-failure recovery returning HTTP
200. Both captures are real interactive Claude Code conversations using the
configured DeepSeek `deepseek-flash` backend, recorded through the local proxy
under tmux without `-p`/`--print`. Both current HTTP 200 viewer images use the final `f46b869` code and installed
macOS headless Chromium at 1280x900 CSS pixels and 2x scale.

1. `trace-viewer-multiturn-baseline-network.png`: native Chromium Network Headers
   show the original records GET returning HTTP 500 for the retained source-code
   capture.
2. `trace-viewer-normal-query-redacted-current.png`: a new six-user-turn,
   six-request conversation shows successful existing query redaction. The
   selected sixth response contains
   `https://example.com/report?token=REDACTED&mode=slow&page=6#section`; public
   parameters, fragment, response text, normal Claude Code task badges and
   recorded usage remain visible. It proves the normal redaction path is
   preserved, not partial recovery of a malformed URI.
3. `trace-viewer-source-redacted-current.png`: the retained source-code capture
   returns HTTP 200 with Edit old/new fields hidden. All six task badges display
   `REDACTED` because they derive from `sys_hint`, which the response-wide HTML
   fallback hides. These labels are not HTTP status or error badges.
4. `trace-viewer-multiturn-fixed.png`: retained historical evidence of complete
   Edit source, not evidence of the current display policy.

The older source-code capture has two user turns and six requests, including the
session-title request: 2,379 input / 438 output / 3,456 cache-read tokens. Its
viewer shows 2,817 input+output tokens. Rendering it makes no new model calls.

The new normal-query capture has six user turns and six actual successful
requests, all HTTP 200: 1,137 input / 415 output / 768 cache-read tokens, with no
cache creation. Its viewer shows 1,552 input+output tokens and separately shows
768 cache-read tokens; the existing dashboard summary totals 2,320 when adding
that separate cache bucket. The six real model calls were explicitly authorized.
All tools were disabled, no URL was visited, and the only user inputs were public
example.com URLs with a clearly fictitious token and brief repetition requests.
No records, responses or usage were fabricated or edited to fill the request count.

The actual source session is `d85a9160-18a3-4305-ae45-e6be91eeed0d`. Its local
SQLite SHA-256 is
`a819d577d3d42561b31e29ab9ea6a36513f6d4890314a97d7b3586ca1bb1917b`;
the faithful product JSONL export SHA-256 is
`b172e5e482a0a9e907757e8bc296012cbba6e8d2440d41b56fd8b0e489884321`.
The source database is unchanged. Raw captures and local configuration stay
outside Git. See `normal-query-capture.json` for the capture and browser receipt.
Both record and HTML checks observe zero URL-recovery failures for this capture,
so its normal task badges do not depend on the parser-failure fallback. Display
privacy was checked before capture, and the browser loaded only the local server.
