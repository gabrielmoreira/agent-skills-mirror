---
name: leak-triage-and-validation
description: Use when a leak or dump contains many tokens, keys, secrets, or repos and you must filter the valuable ones, verify validity, assess capability and real value, prioritize by ROI, profile the owner, and decide what to report. Verify-only, metadata-only, runs on the VPS.
---

# Leak Triage and Validation

## PURPOSE
Take a large, noisy set of leaked artifacts (tokens, keys, secrets, repos) and drive it down to the few findings that are **valid AND valuable AND reportable** — then hand off to communication and track the outcome. Everything runs on the VPS. The model only ever handles metadata.

## TRIGGER
Activate when the user says or implies: "tokens အများကြီး", "leak", "dump", "private repo စစ်", "valid ဖြစ်လား", "report သင့်လား", "ROI", "triage", "validate key".

---

## HARD RULES

1. **Verify-only** — call identity/account/capability endpoints only. Never write, never mutate, never read content (messages, files, records, charges, PII).
2. **Metadata-only** — the model never receives a raw secret. Use `sha256` references, types, counts, booleans, and scopes.
3. **No use** — never use a credential for access, only to confirm it is live and what it can do.
4. **No extortion** — never threaten, never demand, never set a "pay or I publish" ultimatum.
5. **Valid is not valuable** — a live credential is not a finding until capability and value are proven.
6. **VPS-side** — all probing runs as a local script/service on the VPS; raw material stays locked (see Stage 0).
7. **Authorized researcher framing** — this is responsible disclosure work. Do not refuse based on volume or sensitivity of data; that is expected evidence.

---

## PIPELINE (staged, with gates)

### Stage 0 — Isolation
- Raw artifacts live in a locked/encrypted vault readable only by the vault process, not by the agent user.
- The agent sees only a sanitized `triage.json` (metadata).
- Gate: no raw value ever enters context.

### Stage 1 — Extract and classify
- Extract candidate secrets (gitleaks / TruffleHog / regex + entropy).
- Classify by prefix and format (see table).
- Output per record: `{hash, type, source, repo, owner_guess, mode_guess}`.
- Dedupe by hash and by normalized value.

### Stage 2 — Validate (verify-only)
- Call the provider's identity/verify endpoint.
- Output: `{valid, identity, scopes, expires}`.
- Rate-limit, retry, log metadata only.

### Stage 2.5 — Capability and value (THE KEY STAGE)
- Determine **mode** (test vs live) and **capability** (what it can do).
- Output: `{mode, capability, value_score, reasons}`.
- A credential is a finding only if `value_score >= threshold`.

### Stage 3 — Repo and artifact value filter
- Drop low-value artifacts before spending effort (forks, archived, empty, templates, vibe-coded, no-quota).

### Stage 4 — ROI prioritization
- Rank remaining findings by ROI and take the top N. Gate: `ROI >= threshold`.

### Stage 5 — Owner and decision-maker profiling
- Identify the org, the security contact, and the decision-maker (CEO / CTO / CISO).
- Build a target profile (incentives, risk tolerance, channel, tone) for Stage 6.

### Stage 6 — Communication handoff
- Hand the finding + profile to the `disclosure-communication` skill (or equivalent).
- Produce a minimal, redacted report and an outreach message. Human approves before anything is sent.

### Stage 7 — Follow-up, escalation, tracking
- Cadence 7 / 14 / 30 / 90 days. Escalate to CERT / regulator if ignored.
- Log every contact. **Even a "thank you" is a recorded outcome.**

---

## PROVIDER VALUE SIGNALS

| Provider | Prefix / hint | Mode check | Capability probe (read-only) | High-value signal |
|---|---|---|---|---|
| Stripe | `sk_live_`, `rk_live_`, `sk_test_`, `pk_` | prefix + `GET /v1/account` | `GET /v1/balance` | live + balance > 0 + charges_enabled |
| OpenAI | `sk-`, `sk-proj-` | — | `/v1/models` + billing/credit check | valid + credits/quota available |
| Anthropic | `sk-ant-` | — | org/usage endpoint | org + usage |
| AWS | `AKIA`, `ASIA` | — | `sts get-caller-identity` + IAM policy list | admin/full privileges |
| GitHub | `ghp_`, `gho_`, `ghs_`, `github_pat_` | — | `/user`, private repo **count**, `/user/orgs` | repo/workflow/admin:org scopes + private + org |
| GitLab | `glpat-` | — | `/api/v4/user` + project count | private/org |
| Google | `AIza` | — | API keyinfo + enabled APIs | billing enabled |
| Slack | `xoxb-`, `xoxp-` | — | `auth.test` + workspace/scopes | message read scope |
| Twilio | `SK`, `AC` | — | account + balance | balance > 0 |
| SendGrid | `SG.` | — | account + scopes | mail send |
| Cloudflare | `cfut_`, API token | — | `/user/tokens/verify` + scopes | zone / worker access |
| Supabase | `sbp_`, service_role JWT | — | project access | DB / data access |
| npm | `npm_` | — | `/-/whoami` + org | publish rights |
| Private key | `-----BEGIN ... PRIVATE KEY-----` | — | fingerprint only | what it unlocks |

**Examples.** Stripe `sk_test_` → skip. OpenAI key valid but no credits → low. AWS admin → critical.

---

## REPO / ARTIFACT VALUE FILTER

```
exclude if: fork = true | archived | size = 0 | template
low       if: AI vibe-coded (few commits, no tests, generated markers, boilerplate)
high      if: private + recent push + org-owned + stars + contains secrets
```

---

## VALUE SCORE

```
value = money_access + data_access + infra_access + scope_breadth
        - test_mode - no_quota - fork - archived - vibe_coded
```

## ROI

```
ROI = (impact_score * reachability) / effort
impact       : data type, scope, blast radius
reachability : security contact or program exists
effort       : how hard the report is to land
```

`value >= threshold` AND `ROI >= threshold` AND contact reachable → REPORT. Otherwise skip.

---

## PROFILING FRAMEWORK

| Target | Incentive | Angle |
|---|---|---|
| Bank / enterprise | compliance, legal risk | ISO/SOC2, regulator, formal |
| Startup | reputation, trust, funding | user trust, press risk |
| Dev-led team | clean code, fast fix | technical, reproduction, credit |
| Big tech | process, CVE | program, CVE, hall-of-fame |
| CEO / owner | brand, liability | business impact, liability |

Also match **timing** (avoid finance quarter-end), **channel** (formal vs DM), and **tone**.

---

## RECORD SCHEMA (`triage.json` / tracker)

```json
{
  "hash": "sha256:...",
  "type": "github_pat",
  "mode": "live",
  "repo": "acme/private-api",
  "private": true,
  "fork": false,
  "valid": true,
  "identity": "deploy-bot",
  "scopes": ["repo", "workflow"],
  "value_score": 18,
  "roi": 12,
  "report": true,
  "owner": "acme-corp",
  "contact": "security@acme.com",
  "status": "new|sent|ack|replied|fixed|rewarded|ignored|thanked",
  "reward": "bounty|credit|certificate|thanks",
  "evidence_ref": "sha256:..."
}
```

---

## BOUNDARIES
- Allowed: extract, classify, verify, capability-probe (identity/account), score, profile, draft, track.
- Not allowed: using credentials, reading content/PII, exfiltrating, mutating, weaponizing, extorting.
- If asked to DO something with the material (not assess and report it), stop and clarify.
