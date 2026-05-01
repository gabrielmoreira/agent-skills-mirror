---
name: security-threat-model
description: Repository-grounded threat modeling that enumerates trust boundaries, assets, attacker capabilities, abuse paths, and mitigations, and writes a concise Markdown threat model. Trigger only when the user explicitly asks to threat model a codebase or path, enumerate threats/abuse paths, or perform AppSec threat modeling. Do not trigger for general architecture summaries, code review, or non-security design work.
argument-hint: "[path or description of scope]"
user-invocable: true
---

# Security Threat Model

Deliver an actionable AppSec-grade threat model specific to the repository or a
project path. Anchor every architectural claim to evidence in the repo; keep
assumptions explicit. Prioritize realistic attacker goals and concrete impacts
over generic checklists.

## Quality rules (apply throughout)

- **Evidence-grounded**: every component, data flow, or control must be backed by
  at least one repo path and, where helpful, a symbol name, config key, or short
  quoted snippet. Do not invent components.
- **No secrets in output**: if you find tokens, keys, or passwords, redact them
  and describe their presence and location only.
- **Scope discipline**: separate production/runtime behavior from CI/build/dev
  tooling and from tests/examples. Separate attacker-controlled inputs from
  operator-controlled and developer-controlled inputs.
- **Concise for AppSec engineers**: use precise terminology; include mitigations
  and residual risks; avoid restating large blocks of README/spec.

## Workflow

### 1. Collect inputs

Ask the user (or infer and mark as assumptions):

- Intended usage and deployment model (server, CLI, library, worker)
- Internet exposure (public, internal, air-gapped)
- Authentication / authorization expectations
- Data sensitivity (PII, credentials, financial, public)
- Any explicitly out-of-scope paths

If the user provided a path argument, scope the model to that sub-path.

### 2. Explore the repo

Use file search, `grep -rI` (skip binaries), or ripgrep `rg` (skips binaries by
default) to locate security-relevant surfaces:

- Network listeners, routes, endpoints, RPC handlers, message consumers
- Auth, session/token handling, RBAC/ACL logic
- Parsing/deserialization (JSON/YAML/XML/protobuf), template rendering, `eval`
- File upload/read paths, archive extraction, image/document parsing
- Database, queue, and cache clients and query construction
- Secrets/config loading, environment variables, key management
- SSRF-capable HTTP clients, webhooks, URL fetchers
- Sandboxing, privilege boundaries, subprocess execution
- Logging/error handling paths
- CI/build pipelines, dependency management, artifact publishing

### 3. Build the system model

- List primary components and how they interact.
- Enumerate data flows and trust boundaries: for each boundary specify source →
  destination, data types crossing, channel/protocol, security guarantees
  (auth, TLS, origin checks, schema validation, rate limits).
- Produce a compact **Mermaid flowchart** (see diagram rules below).

### 4. Enumerate assets and attacker model

- List assets that drive risk: credentials, PII, integrity-critical state,
  availability-critical components, build artifacts.
- Describe realistic attacker capabilities based on exposure and intended usage.
- Explicitly note non-capabilities to avoid inflated severity.

### 5. Enumerate threats as abuse paths

- Prefer multi-step attacker stories tied to entry points and trust boundaries.
- Classify each threat: exfiltration, privilege escalation, integrity compromise,
  denial of service, supply-chain attack.

### 6. Prioritize with explicit reasoning

For each threat assign:

- **Likelihood**: low / medium / high (1–2 sentence justification)
- **Impact**: low / medium / high (1–2 sentence justification)
- **Priority**: critical / high / medium / low (likelihood × impact, adjusted for
  existing controls)

Risk priority guidance (illustrative):

- **Critical**: pre-auth RCE, auth bypass, cross-tenant access, sensitive data
  exfiltration, key or token theft, sandbox escape
- **High**: targeted DoS of critical components, partial data exposure, rate-limit
  bypass with measurable impact, privilege escalation with realistic prerequisites
- **Medium**: log/metrics poisoning affecting detection, partial info leaks with
  meaningful exposure
- **Low**: low-sensitivity info leaks, noisy DoS with easy mitigation, issues
  requiring unlikely preconditions

### 7. Validate assumptions with the user (required)

Before producing the final report:

1. Summarize the 3–6 key assumptions that most affect scope or risk ranking.
2. Ask 1–3 targeted questions to resolve missing context (deployment environment,
   scale, auth model, internet exposure, data sensitivity, multi-tenancy).
3. **Wait for user feedback.** If the user cannot answer, proceed with explicit
   assumptions and mark any conditional conclusions.

### 8. Write the report

Produce valid Markdown following the required output format below. Write it to a
file named `<repo-or-dir-name>-threat-model.md` (use the basename of the repo
root, or the in-scope directory if asked to model a sub-path). Then summarize
the top findings to the user.

Run a quality check before writing:

- All discovered entry points are covered.
- Each trust boundary appears in at least one threat.
- Runtime vs CI/dev separation is maintained.
- User clarifications (or explicit non-responses) are reflected.
- Assumptions and open questions are explicit.

## Mermaid diagram rules

Use `flowchart TD` or `flowchart LR` only. Rules:

- Only `-->` arrows; edge labels limited to plain words via `-->|label|`.
- Simple node IDs (letters/numbers/underscores only); quoted labels
  (`A["Label"]`); avoid `A(Label)` shape syntax.
- No `title` lines or `style` directives.
- No file paths, URLs, or socket paths in node labels (put those in prose).
- Wrap in a fenced `mermaid` block.

## Required output format

```
## Executive summary
One paragraph: top risk themes and highest-risk areas.

## Scope and assumptions
In-scope paths, out-of-scope items, explicit assumptions, open questions.

## System model
### Primary components
### Data flows and trust boundaries
Arrow-style bullets (e.g., Internet → API Server). For each boundary: data
types, channel/protocol, security guarantees, input validation.
#### Diagram
<mermaid flowchart>

## Assets and security objectives
Table: Asset | Why it matters | Security objective (C/I/A)

## Attacker model
### Capabilities
### Non-capabilities

## Entry points and attack surfaces
Table: Surface | How reached | Trust boundary | Notes | Evidence (repo path/symbol)

## Top abuse paths
5–10 numbered multi-step sequences: attacker goal → steps → impact.

## Threat model table
Columns: Threat ID | Threat source | Prerequisites | Threat action | Impact |
Impacted assets | Existing controls (evidence) | Gaps | Recommended mitigations |
Detection ideas | Likelihood | Impact severity | Priority

Rules: Threat IDs as TM-001, TM-002, …; Priority one of critical/high/medium/low.

## Criticality calibration
Define critical/high/medium/low for this repo's context. Include 2–3 examples
per level tailored to the repo's assets and exposure.

## Focus paths for security review
2–30 repo-relative paths with one-sentence reason each.

## Quality checklist
Short checklist confirming coverage of entry points, trust boundaries,
runtime/CI separation, user clarifications, and assumptions.
```
