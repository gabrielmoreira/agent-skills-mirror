# Triage — read findings, cut false positives, prioritize work

## Severity vocabulary

| Severity | Meaning |
|---|---|
| `CRITICAL` | Pre-auth or trivially exploitable issue with broad blast radius. |
| `HIGH` | Real vulnerability, likely exploitable in this codebase's context. |
| `MEDIUM` | Conditional vulnerability or one with significant attacker prerequisites. |
| `LOW` | Defense-in-depth gap, or correctness issue with weak security framing. |
| `HIGH_BUG` / `BUG` | Real bug that the agent declined to call a vulnerability — typically correctness with security-adjacent risk. |

`triage` adds a `priority` field on top of severity:

| Priority | Trigger |
|---|---|
| `P0` | Drop everything — exploit is trivial and impact is critical. |
| `P1` | This sprint. |
| `P2` | Backlog. |
| `skip` | Not worth fixing (nuance, intended behavior, false alarm). |

## Read order

Do not show the user raw `process` output for HIGH+ findings. The right pipeline is:

1. `bunx deepsec process` (or `process --diff` for PR mode).
2. `bunx deepsec triage --severity HIGH` — buckets P0/P1/P2, ~$0.01 / finding.
3. `bunx deepsec revalidate --min-severity HIGH` — reads the code + git history, emits a verdict (~comparable cost to `process`, cuts FP rate by 50%+).
4. `bunx deepsec export --format md-dir --out ./findings` — surface to the user.

`revalidate` verdicts:

| Verdict | Action |
|---|---|
| `true-positive` | Fix it. Hand off to `oma-debug` or the matching domain skill. |
| `false-positive` | Note in `INFO.md` if the FP shape is recurring. Adjust matchers if it is a regex-level over-match. |
| `fixed` | The finding refers to code that was already patched in git history; no action. |
| `uncertain` | Re-run with the other agent, or escalate to a human reviewer. |

## Cutting FP rate

Two things help most:

1. **Always `revalidate` before acting on `HIGH+`.** Worth the cost.
2. **Tighten `INFO.md`.** Even one paragraph about the auth shape, threat model, and known FP sources improves precision a lot. See `setup.md` § 4.

After revalidation, FP rate on `HIGH+` typically lands in the 10–29 % range.

## Refusals

Models occasionally refuse to investigate a candidate (exploit-shaped source, content filter). After every batch deepsec asks the agent whether anything was skipped; `refused: true` appears in `RunMeta` and on the `FileRecord.refusal` field. The per-batch log shows a ⚠️ `refusal` marker.

Handling:

- A refused batch produces no false negatives — affected files stay `pending`. Re-run `--reinvestigate` against the **other** backend (Claude ↔ Codex) to pick up the dropped sites. Findings dedupe across agents.
- If a single file consistently triggers refusals (>5 % of batches), add it to `data/<id>/config.json:ignorePaths`, **or** run that file alone with `--batch-size 1` so a refusal does not take an otherwise-fine batch down with it.
- Never silently drop a refusal. Document it in the user-facing summary.

## Reading severity counts

```bash
bunx deepsec metrics
```

Shows cross-project counts: severities, vulns by type, TPs after revalidation. Use it to decide where matcher investment pays off (clusters of `other-*` slugs are the strongest signal).

## Per-finding markdown export shape

`bunx deepsec export --format md-dir --out ./findings` produces:

```
findings/
├── CRITICAL/
├── HIGH/
├── MEDIUM/
├── LOW/
└── BUG/
```

Each file contains: severity, title, `vulnSlug`, file path with line numbers, description, recommendation, confidence, triage verdict (if run), revalidation verdict (if run), `analysisHistory` summary. Use these as inputs to issue tracker tickets — the structure is friendly to GitHub Issues / Linear / Jira import scripts.

## When to *not* surface a finding

- `revalidation.verdict === "false-positive"`.
- `revalidation.verdict === "fixed"` and the fix matches the current `HEAD`.
- `triage.priority === "skip"` with reasoning the user agrees with.
- Severity below the user-stated `severity_floor`.

For everything else: surface it, with verdict, recommendation, and the file path.

## Hand-off

Route by **the layer of the vulnerable file**, judged from each finding's `filePath` + `vulnSlug` + `revalidation.verdict` against the project's own signals (`data/<id>/tech.json`, `INFO.md`, `priorityPaths`, and the actual directory structure). No baked-in slug or path enumeration — deepsec evolves its matcher set, and project layout varies. Trust the artifact at runtime.

| Layer of the vulnerable file | Specialist |
|---|---|
| Backend / server / API | `oma-backend` |
| Frontend / web client | `oma-frontend` |
| Mobile / native client | `oma-mobile` |
| IaC / cloud / network | `oma-tf-infra` |
| Database / data model | `oma-db` |
| CI / workflow / supply chain | `oma-dev-workflow` |
| Documentation drift surfaced by the run | `oma-docs` |

**Ambiguity → `oma-debug` first.** When the layer is not obvious from the artifact (shared / isomorphic / utility code, `other-*` slug, multi-layer fix, `revalidation.verdict === "uncertain"`, or `BUG` / `HIGH_BUG` non-security correctness without an obvious owner), route to `oma-debug` for a **triage pass, not a fix**. Its job is to pin the exact file:line and re-route to the right specialist with a layer-tagged finding — or fix inline only when the change is a single isolated line and the diagnosis is confident. Record the second-hop owner in the run summary.

Attach to every routed item: file path, severity, `vulnSlug`, revalidation verdict, recommendation, and the export markdown path.

| Layer of the vulnerable file | Route to | Typical finding shapes |
|---|---|---|
| Backend / server / API | `oma-backend` | SQLi, SSRF, command injection, auth bypass, JWT issues, IDOR, CSRF on API, insecure deserialization, hardcoded server secrets, insecure file upload, path traversal |
| Frontend / web client | `oma-frontend` | XSS, `dangerouslySetInnerHTML` with untrusted HTML, JSON-in-script escapes, `postMessage` origin, open redirect, Next.js Server Action exposure, middleware-only auth bypass, search-param trust, client-side secret leak |
| Mobile / native client | `oma-mobile` | insecure local storage (SharedPreferences / NSUserDefaults / AsyncStorage plaintext), hardcoded API keys, cleartext HTTP / missing cert pinning / ATS exception, deeplink / URL scheme without validation, WebView JS bridge / file:// / mixed content, Android Intent / iOS URL scheme injection, permission overreach, biometric / keychain misuse, PII in logs |
| IaC / cloud / network | `oma-tf-infra` | Terraform IAM wildcard, public S3, open security groups, missing encryption-at-rest, GitHub Actions privilege escalation, OIDC misconfig, Dockerfile mutable base |
| Database / data model | `oma-db` | raw SQL via interpolation, ORM `raw`/`unsafe` APIs, mass-assignment, missing constraints, sensitive-column exposure, weak DB-layer password hashing, enumeration-friendly index design |
| CI / workflow / supply chain | `oma-dev-workflow` | `pull-requests: write` on PR-code job, unpinned actions, secrets in PR triggers, npm postinstall risk |
| Shared / isomorphic / utility code where the layer is ambiguous, or `BUG` / `HIGH_BUG` non-security correctness | `oma-debug` | needs reproduction + regression test |
| Documentation drift surfaced by the run | `oma-docs` | stale env vars, removed flags, broken refs |

For each routed item, attach: file path, severity, `vulnSlug`, revalidation verdict, recommendation, and the export markdown path.
