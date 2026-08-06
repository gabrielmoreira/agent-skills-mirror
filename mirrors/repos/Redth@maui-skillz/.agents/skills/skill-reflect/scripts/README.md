# scripts/

Utility scripts for skill-reflect.  All scripts use the Python 3 standard
library only (no third-party dependencies).

---

## scrub.py — privacy backstop

Deterministic redactor that runs **under** the model's own paraphrasing scrub
as a defense-in-depth layer.  Never the sole line of defense; never emits
any redacted value.

See [`../references/privacy-scrub.md`](../references/privacy-scrub.md) for
the full privacy policy and layering explanation.

### CLI usage

```bash
# Redact a file and print to stdout:
python3 scrub.py report.md

# Redact and write to a new file:
python3 scrub.py report.md --out report-scrubbed.md

# Show a redaction summary (category counts, never values):
python3 scrub.py report.md --report

# Exit non-zero if a secret category was detected (useful in pre-commit / CI):
python3 scrub.py report.md --fail-on-secret

# Common combination — scrub, report, and fail fast on secrets:
python3 scrub.py draft.md --report --fail-on-secret

# Scrub generated in-memory text without a temporary file:
printf '%s' "$draft" | python3 scrub.py - --report --fail-on-secret
```

**Arguments**

| Argument | Description |
|---|---|
| `<infile>` | File to scrub (text, Markdown, or JSON), or `-` for stdin. |
| `--out FILE` | Write scrubbed output to `FILE` (default: stdout). |
| `--report` | Print per-category redaction counts to stderr (never values). |
| `--fail-on-secret` | Exit `1` before emitting output if a high-entropy or known-token secret was found. |

**Redacted categories**

| Category | Examples |
|---|---|
| `email` | `user@example.com` |
| `github-token` | `ghp_…`, `gho_…`, `ghu_…`, `ghs_…`, `ghr_…` |
| `aws-access-key` | `AKIA…` (20-char access key IDs) |
| `slack-token` | `xoxb-…`, `xoxp-…`, `xoxa-…`, `xoxr-…`, `xoxs-…` |
| `google-api-key` | `AIza…` (39 chars) |
| `bearer-token` | `Bearer <token>`, `Authorization:`, `X-Api-Key:` header values |
| `pem-private-key` | `-----BEGIN … PRIVATE KEY-----` blocks |
| `jwt` | Three-segment base64url tokens where header/payload start with `eyJ` |
| `high-entropy` | Hex hashes (MD5/SHA), high-entropy base64/mixed tokens |
| `path` | `/Users/<u>/…`, `/home/<u>/…`, `C:\Users\<u>\…` |
| `ip-address` | IPv4 (`192.168.1.1`) and IPv6 (`2001:db8::1`) |

Categories `email`, `path`, and `ip-address` are redacted but do **not**
trigger `--fail-on-secret`; they are PII, not secrets.

### Python import API

```python
from scrub import scrub_text

scrubbed, findings = scrub_text(text)
# scrubbed : str   — text with [REDACTED:<category>] placeholders
# findings : list  — [{"category": str, "count": int}, ...] sorted by category
```

---

## test_scrub.py — unit tests

```bash
# Run all tests (from this directory):
python3 -m unittest -v
```

---

## read_journal.py — Copilot capture evidence

Reads only the value-free Copilot journal selected by a matching trusted pending marker. It
returns skill names and friction signal counts; opaque ids, tool names, arguments, results,
paths, and runtime fingerprints are omitted.

```bash
python3 read_journal.py \
  --selection <trusted-selection-token>
```

Use `--selection` for the filtered marker set injected by an accepted auto nudge. An explicit
broad review may use `--all-pending`; `--session-id` is only for a trusted id injected by an
adapter. Live sessions are always excluded. Selection-based reads also verify the marker digest and
enforce the nudge's allowed skill subset. The output includes a value-free review receipt bound to
the exact marker+journal state, not a session id. A legacy marker whose journal is missing is
returned with `journal: false`; use visible-context fallback and retain its receipt for
successful-review consumption.

## consume_pending.py — marker and journal lifecycle

Removes only reviewed pending markers and their matching capture journals after successful chat
analysis or artifact creation. It validates each opaque session id against both control-plane
documents, acquires the shared per-session capture lock, and rechecks both active state and the
receipt-bound files before deleting anything. It prints counts only, never the ids themselves.

```bash
python3 consume_pending.py \
  --receipt <reviewed-receipt> \
  [--receipt <reviewed-receipt> ...]
```

Declined, aborted, or failed reviews must not invoke this script.
Cleanup removes a matching journal before its marker, so an interrupted cleanup leaves a
recoverable marker-only review rather than an orphan journal.
