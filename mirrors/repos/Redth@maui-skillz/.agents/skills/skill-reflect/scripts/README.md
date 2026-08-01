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
```

**Arguments**

| Argument | Description |
|---|---|
| `<infile>` | File to scrub (text, Markdown, or JSON). |
| `--out FILE` | Write scrubbed output to `FILE` (default: stdout). |
| `--report` | Print per-category redaction counts to stderr (never values). |
| `--fail-on-secret` | Exit `1` if a high-entropy or known-token secret was found. |

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
