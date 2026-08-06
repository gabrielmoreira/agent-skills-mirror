# Privacy & Scrub Reference

> **Authority:** CONTRACT.md §0 · §2a (modes and authorization) · §7 (scrubber contract)
> **Applies to:** every chat finding, artifact, preview, issue body, and eval. Pending
> markers are local control-plane state and may contain only the opaque session identifier,
> skill names, counts, and timestamps defined by the contract.

---

## 1. Mandatory scrub list

The following **MUST NEVER appear** in chat findings, artifacts, previews, GitHub issue
bodies, or generated evals:

| Class | Examples |
|---|---|
| Real names | Any person's full name, first name, or display name |
| Email addresses | `alice@example.com` |
| Usernames / handles | GitHub handles, OS usernames, IAM user names |
| Session IDs | Opaque session identifiers from any agent runtime |
| Absolute file paths | `/Users/alice/…`, `/home/bob/…`, `C:\Users\carol\…` |
| Machine / host names | Laptop names, internal server hostnames |
| Private URLs | Any URL containing credentials, tokens, or user-specific path segments |
| Tokens & credentials | GitHub PATs, AWS access/secret keys, Slack tokens, Google API keys, JWT, bearer tokens, API keys |
| PEM / private keys | Any `-----BEGIN PRIVATE KEY-----` block or equivalent |
| High-entropy secrets | Strings that exhibit high Shannon entropy and look like generated secrets |
| Request / response bodies | Verbatim HTTP request/response content |
| Screenshots | Images of any user's screen, terminal, or browser |
| Verbatim transcript excerpts | Any raw text copied from the agent's session transcript |
| Product / project / brand names (strict output) | App, product, service, brand, or internal project/codename that identifies what was being built |
| App type / domain identifiers (strict output) | Descriptions that give away the app's industry, purpose, or category |
| Implementation-revealing details (strict output) | Repro steps, feature names, data models, screen/route names, or business logic specific enough to fingerprint the real app |

The last three rows are the domain-abstraction policy for `strict` output. They may be
relaxed only by the `technical-local` rules in §2b. Every other row is unconditional.

---

## 2. Paraphrase rules

1. **Refer to the variable, flag, or tool name — never its value.**
   - ✗ `"The API key sk-abc123… was passed to --api-key"`
   - ✓ `"The --api-key flag was invoked with a value from the environment"`

2. **Describe what happened; never quote it.**
   - ✗ `"Error: FileNotFoundError: /Users/alice/data/config.json"`
   - ✓ `"A file-not-found error occurred when loading the config from a user-specific path"`

3. **Generalise; never name individuals.**
   - ✗ `"Alice ran the deploy command"`
   - ✓ `"The deploy command was invoked"`

4. **Summarise tool output; never paste it verbatim.**
   - ✗ `"The model returned: 'Here is your detailed answer…'"`
   - ✓ `"The model provided an explanation of the requested topic"`

5. **Report patterns, not payloads.**  When describing a tool failure, say *what the tool
   was asked to do* and *what the failure pattern was*; never include the actual arguments
   or return values.

---

## 2a. Domain & implementation abstraction

> **Authority:** CONTRACT.md §0.3. This is a semantic scrub the **model** performs — the
> deterministic backstop can only catch terms someone thought to list, so the model is the
> primary defense here.

The feedback is about **how a skill behaved**, never **what the user was building**. Two
sessions that hit the same skill bug should produce interchangeable feedback regardless of
the app, industry, or company involved.

### Rules

1. **Never name the product, app, brand, or project.** Not the real name, not the internal
   codename, not a lightly-disguised version of it. Refer to "the project" or "the app".
2. **Never reveal the app's type, industry, or purpose** when it isn't required to explain
   the skill's failure. "A web app" is usually enough; "a hospital patient-intake portal" is
   not.
3. **Strip domain-specific nouns.** Feature names, entity/table names, route and screen
   names, and business rules are all fingerprints. Replace them with generic analogues
   ("a record", "a list view", "a form field").
4. **Recast reproduction steps as an invented, analogous scenario.** Keep the *shape* of the
   friction — the sequence that made the skill stumble — but relocate it into a neutral,
   made-up context that shares none of the original specifics. The reader must be able to
   reproduce the *skill* problem without learning anything about the real app.
5. **Preserve only what the author needs to fix the skill:** the tool/flag/step involved,
   the failure pattern, and the corrected behavior. Everything else is domain noise.

### Repro before / after (all synthetic)

**Before (leaks the domain — never emit this):**

> While wiring the **MediTrack** patient-intake portal, I asked the skill to scaffold a
> `PatientVisit` model with an `insuranceClaimId` foreign key. It generated a migration
> using the old `belongs_to` syntax, so the claims-reconciliation screen failed to load.

**After (analogized — safe to emit):**

> Using the skill to scaffold a data model with a foreign key to a related record, it
> emitted a migration using an outdated association syntax; a view that depended on that
> relationship then failed to load. Reproduce with any two related models where one
> references the other.

### What changed and why

| Leaked detail | Action |
|---|---|
| `MediTrack` (product name) | Removed — refer to "the skill" / "the app" |
| "patient-intake portal" (app type/industry) | Generalized to "an app" |
| `PatientVisit`, `insuranceClaimId`, "claims-reconciliation screen" | Replaced with generic analogues ("a data model", "a foreign key", "a view") |
| The specific repro walkthrough | Recast as a neutral, reproducible scenario that still exercises the skill bug |

The **friction mechanism** (stale association syntax in a generated migration) is fully
preserved; the **domain** is gone.

---

## 2b. Technical-local detail

`technical-local` is a per-run detail level for a user-confirmed local/user-owned skill.
It is not a persistent config default. All conditions are mandatory:

1. The user explicitly opts in for this review.
2. Ownership is confirmed, not inferred only from a path.
3. Output stays in chat or a local artifact.
4. The unconditional scrub list in §1 remains enforced.
5. A technical-local artifact is marked `remote_eligible: false`.

Allowed detail:

- Repository-relative paths and line ranges.
- Symbols, API names, flags, CI job names, and explicit evidence/execution boundaries.
- Short excerpts from the skill's own source when needed to make the fix actionable.

Still forbidden:

- Secrets, credentials, runtime values, PII, absolute paths, private URLs, and raw
  transcript excerpts.

If the user later requests a remote send, discard the technical-local rendering and
regenerate a separate `strict` report. Apply §2a, run the scrubber again, show the exact
outbound body, and obtain fresh remote-send authorization.

---

## 3. Redaction and preview protocol

> `privacy.redactionPreview` is **always `true`**. Preview verbosity depends on output
> mode; the privacy check itself cannot be disabled.

### Steps (always in this order)

1. **Model paraphrase scrub** — the model rewrites its draft in its own words, applying
   strict §2a or explicitly authorized §2b. This is the primary line of defense.

2. **Deterministic backstop** — `scripts/scrub.py` runs over the model-scrubbed draft,
   applying regex/entropy-based rules as a defense-in-depth layer.

3. **Mode-specific delivery**:
   - Analysis: return scrubbed findings in chat; there is no duplicate preview.
   - Artifact: show path, scope, detail level, finding summaries, and redaction counts.
     Offer the full scrubbed text on request.
   - Remote: show the exact strict issue body.
4. **Authorization** — write or send only under the corresponding authorization in §4.

---

## 4. Authorization

### Review authorization

- An explicit request to analyze how a named skill performed in a stated session is
  authorization after a short scope notice.
- A passive nudge or ambiguous request asks once.
- An accepted nudge passes authorization into the core skill; do not ask again.
- Scope is pinned to the announced skill(s), session(s), and history range.
- Expansion requires new authorization.
- Review authorization does not authorize a file write or remote send.

### Local-write authorization

- An explicit save/capture/report request authorizes one write to the announced path.
- Otherwise ask after the summary-first preview.
- Silence or ambiguity means no write.

### Remote-send authorization

- Ask separately after showing the exact strict body and destination.
- Silence or ambiguity means no send.
- One approval covers one body sent once to one destination.
- Destination or content changes require new authorization.
- Sending uses `gh issue create`; no other implicit network call is made.

---

## 5. How the model scrub and deterministic backstop layer together

```
Authorized session evidence (transcript, tool calls, outputs)
         │
         ▼
 ┌─────────────────────────────────────────────┐
 │  Model paraphrasing scrub   ← PRIMARY       │
 │  • Rewrites in the model's own words        │
 │  • Catches semantic PII: names, context,    │
 │    intent — things patterns can't see       │
 │  • Produces the draft artifact              │
 └────────────────────┬────────────────────────┘
                      │  draft (model-scrubbed)
                      ▼
 ┌─────────────────────────────────────────────┐
 │  scrub.py deterministic backstop  ← DEFENSE │
 │  IN DEPTH (never the only defense)          │
 │  • Regex/entropy rules on the draft text    │
 │  • Catches residual literal PII the model   │
 │    may have missed                          │
 │  • Never emits any redacted value           │
 └────────────────────┬────────────────────────┘
                      │  scrubbed draft
                      ▼
         Mode-specific delivery (§3)
            ├─ analysis → chat only
            ├─ artifact → local-write authorization
            └─ remote → exact preview + remote-send authorization
```

### When to run `scrub.py`

Run on **every** generated chat finding, artifact, eval, or issue body — always, even if
the model scrub was thorough. Use stdin for in-memory analysis output:

```bash
python3 skill-reflect/scripts/scrub.py draft.md --report --fail-on-secret \
  $(printf -- '--term %q ' "${redactTerms[@]}") \
  $(printf -- '--pattern %q ' "${extraScrubPatterns[@]}")

printf '%s' "$analysis" | python3 skill-reflect/scripts/scrub.py - \
  --report --fail-on-secret
```

Pass any `privacy.redactTerms` (product/app/project names) as `--term` and any
`privacy.extraScrubPatterns` as `--pattern` so the deterministic layer also catches
configured domain terms (category `domain-term`) and custom patterns (category `custom`).
These are a **backstop** for the domain abstraction in §2a — the model's semantic rewrite is
still the primary defense, because product names and implementation details cannot be fully
enumerated in advance.

If `--fail-on-secret` exits non-zero, no output is emitted or written. Redraft and
scrub again before presenting anything.

---

## 6. "What good looks like" — before / after example

> **All data below is synthetic.** No real credentials, names, or systems are referenced.

### Before (raw session content — would never leave the agent)

```
Tool call : file_read
  path    : /Users/jdoe/projects/acme-api/config.json
  result  : { "api_key": "ghp_aBcDeFgHiJkLmNoPqRsTuVwXyZ1234567890" }

Error     : failed to connect to 10.0.0.42 using token xoxb-111-222-xxxSECRETyyy
Contact   : Jane Doe <jane@example.com>
```

### After (model paraphrase → scrub.py → ready for preview)

```
Tool: `file_read`
The config file at a user-specific path was read successfully.
It contained an `api_key` field; the value was not used and is not recorded here.

Error: a connection failure occurred when contacting an internal service using
a bot credential. The credential value is not recorded.

Contact: the skill author (contact details withheld).
```

### What changed and why

| Raw value | Action | Why |
|---|---|---|
| `/Users/jdoe/projects/…` | Described as "user-specific path"; `scrub.py` replaces literal with `[REDACTED:path]` | Absolute path with username |
| `ghp_aBcDeFgH…` | Described as "api_key field"; `scrub.py` catches as `github-token` | GitHub PAT |
| `10.0.0.42` | Described as "internal service"; `scrub.py` catches as `ip-address` | Internal IP address |
| `xoxb-111-222-xxxSECRETyyy` | Described as "bot credential"; `scrub.py` catches as `slack-token` | Slack bot token |
| `jane@example.com` | Described as "skill author"; `scrub.py` catches as `email` | Email address |

The model scrub handles *meaning* (paraphrase); `scrub.py` handles *literals* (pattern matching).
Both layers are always applied.
