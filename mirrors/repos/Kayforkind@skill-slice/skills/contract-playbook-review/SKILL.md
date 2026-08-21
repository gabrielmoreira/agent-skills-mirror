---
name: contract-playbook-review
description: "Compares each YAML playbook rule to the matching contract provision and emits one ordered finding with found, character-exact excerpt, and status derived from action_* (ok/risk/reject). Apply when an NDA, MSA, DPA, lease, or vendor DD questionnaire must be scored against machine-checkable fields such as max_years or acceptable_jurisdictions. Not a contract-drafting generator and not advice beyond encoded rules; skip reviews that have no playbook."
version: 1.1.1
risk: safe
source: openrouter-deepsearch
date_added: 2026-06-16
---

# Contract Playbook Review

A contract reviewer applies a structured deviation policy to a contract, clause by clause, and emits a structured review. Each finding is traceable to a machine-checkable rule — never unsupported opinion.

## When to Use

Use this skill whenever reviewing any contract — NDA, MSA, vendor DD questionnaire, lease, DPA — against a structured rules-based playbook. The playbook is a list of clause rules. Each rule names a clause, describes the policy in prose, and encodes the policy as machine-checkable fields (e.g. `max_years`, `acceptable_jurisdictions`, `must_be_present`).

Trigger keywords: playbook review, contract review, deviation policy, clause-by-clause, NDA review, MSA review, DPA review, vendor questionnaire, lease review.

### Do NOT use when:

- **Free-form review without a structured playbook.** The entire method depends on each finding being traceable to a machine-checkable rule. With no playbook, there is no objective threshold to compare against, so the output degrades into unsupported opinion. If the user wants a general read, tell them so and ask for the playbook.
- **Drafting contracts from scratch.** Review answers "does this provision comply with our policy?"; drafting answers "what should this provision say?" Using a deviation policy as a drafting template produces bland, defensive language that ignores commercial intent.
- **Legal advice beyond the playbook's encoded rules.** The playbook captures a firm's *settled* positions. Anything outside it (novel risk, jurisdiction-specific enforceability, regulatory interpretation) requires a lawyer's judgement. Flag the gap rather than improvising a rule.
- **Contracts whose clause types the playbook does not cover.** If the playbook has no rule for, say, an arbitration clause, you cannot review that clause — there is no policy to apply. Note the uncovered area so the playbook owner can extend it; do not invent a threshold.
- **Deprecated rule types or outdated playbook formats.** Older shapes like `must_be_exactly` (replaced by `acceptable_set`) or YAML 1.1 (which coerces `no`/`off`/`yes` to booleans and mis-parses unquoted thresholds) silently change the meaning of a rule. The danger is not that they fail loudly — it is that they pass while meaning something else. Migrate the playbook before reviewing against it.
- **Any workflow that treats contract text as low-sensitivity.** Contracts routinely contain personal data, pricing, and confidential terms. If a request would route that text through an untrusted channel, log it in the clear, or expose it to parties outside the engagement, stop and confirm the handling first — a leaked draft is far costlier than a delayed review.
- **A stale playbook.** Thresholds anchored to a statute or survey go out of date when the law or market moves. A rule that was correct last year can produce confidently wrong findings today. If you notice a rule's `source` predates a known change in the relevant law, surface it instead of applying the rule blindly.

## Prerequisites

- A structured playbook in YAML (or equivalent machine-readable format) containing clause rules with machine-checkable fields.
- The contract text in a readable format (plain text, Markdown, or HTML — strip tags before extracting excerpts).
- If the playbook uses YAML 1.1, migrate to YAML 1.2 first to avoid silent boolean coercion of `no`/`off`/`yes`.
- Confirm the playbook is current: check each rule's `source` field against known legal or market changes.

## Procedure

### Step 1: Load and validate the playbook

1. Parse the playbook file. Confirm it is valid YAML (or the specified format).
2. Check for deprecated rule types (`must_be_exactly` → migrate to `acceptable_set`).
3. If YAML 1.1 is in use, migrate to YAML 1.2 before proceeding.
4. Inventory the clause list — you will emit one finding per clause, in the playbook's declared order. No additions, no deletions.

### Step 2: Walk the playbook — four-step loop per clause

For each clause rule in the playbook, repeat:

#### 2a. Locate the corresponding provision in the contract

The contract may use different headings. Use three strategies in order:

1. **Heading match** — try the playbook's `key` and `label` against the contract's section headings (e.g. playbook `governing_law` → contract heading "Governing Law" or "Choice of Law").
2. **Operative-verb scan** — search for verbs/phrases that mark the clause function. ("shall return or destroy" → return/destruction; "irreparable harm" + "injunctive" → equitable relief; "governed by and construed in accordance with" → governing law).
3. **Keyword neighbourhood** — for numeric rules, find the unit ("year", "months", "$") and read the surrounding sentence to decide whether it is the term, survival, notice period, or some other duration.

If you searched and the contract really has nothing, set `found: false` and `excerpt: ""`. Do not manufacture an excerpt. Do not infer one from the playbook prose. A missing clause is a legitimate finding.

#### 2b. Apply the rule

Check the contract's position against the policy fields. Recognise the rule shape:

| Rule shape | Field example | "ok" means |
|---|---|---|
| Numeric ceiling | `max_years: 3`, `max_months: 24` | Contract value ≤ ceiling |
| Numeric floor | `min_years: 1` | Contract value ≥ floor |
| Must be present | `must_be_present: true` | Provision exists |
| Must be absent | `must_be_absent: true` | Provision (or specific phrasing) does NOT exist |
| Acceptable set | `acceptable_jurisdictions: ["England and Wales", "New York", "Delaware"]` | Contract value ∈ set |
| Required feature | `must_allow_destruction: true` | Provision contains the feature |
| Conjunction of features | `must_require_notice && must_require_cooperation` | All features present |
| Conditional structural | `must_be_bilateral_if_present` | Provision absent OR present-and-symmetric |

A playbook entry may carry a `source` field naming the published authority the rule is anchored to (a survey, statute, treatise, or firm-published practice guide). When present, treat it as load-bearing — the rule's threshold is not arbitrary; it is the cited source's stated value.

A clause may combine several rule shapes (e.g. "must be present AND have backup carve-out AND allow destruction"). The clause's overall status is `ok` only if *every* sub-rule passes.

#### 2c. Classify the outcome

**Status is derived from the playbook's `action_*` field, not from the rule shape.** This is the most common place an agent goes wrong: it sees `must_be_absent` and reaches for `reject` by reflex. Don't. Use the prescribed action to decide status:

- `action_if_ok` ("accept", "no_change") → status `ok`
- Any action that begins with `request_` (`request_reduction` / `request_addition` / `request_revision` / `request_change` / `request_amendment`) → status `risk`. The "request_" prefix is the signal: we still want the contract; we're going to negotiate. Even a `must_be_absent` clause whose `action_if_present` is `request_revision` is still **risk**, not reject.
- `action_if_present` (or `action_if_violated`) of `reject_and_remove` / `reject` / `walk_away` → status `reject`. The rule's prescribed response is to refuse, not to negotiate.

When the playbook is silent on a particular outcome, fall back to: action prefix `request_` → `risk`; explicit reject/walk-away → `reject`.

#### 2d. Record the finding

Emit a structured finding with these non-optional fields:

- `clause` — the playbook clause key
- `found` — boolean; `true` if the provision was located in the contract
- `excerpt` — verbatim substring of the contract source (see rules below); `""` when `found: false`
- `status` — `ok`, `risk`, or `reject` (derived from action, not rule shape)
- `action` — the playbook's prescribed action for this outcome
- `rationale` — one sentence stating the operative facts and the rule applied

### Step 3: Extract the verbatim excerpt

The excerpt is what proves your finding. Three hard rules:

1. It must be a **substring** of the contract source — character-for-character, including punctuation and capitalisation. Do not paraphrase. Do not stitch together text from different paragraphs.
2. Keep it **short and targeted** — the smallest excerpt that contains the operative language. Most playbooks bound this (e.g. ≤ 400 characters). If the operative language spans more than that, choose the most diagnostic phrase.
3. For a `found: false` finding, the excerpt is `""`.

When extracting from Markdown or plain text, copy the exact run including any quotation marks, parentheses, or numerical values. When extracting from HTML, strip tags first; do not include rendered artifacts.

### Step 4: Write the rationale

One sentence. State the operative facts and the rule applied. Examples:

- **ok:** "Term is one year, within the 3-year maximum."
- **risk (numeric ceiling):** "Survival is ten years, exceeding the 7-year cap."
- **risk (missing feature):** "Definition exclusions cover the four standard exceptions but omit a residuals carve-out."
- **reject:** "A non-compete covenant is present; the playbook's prescribed action for this clause is reject_and_remove."

Avoid: hedging ("appears to", "may be"), restating the playbook in full, repeating the rationale across clauses.

### Step 5: Emit output

- Emit one entry per playbook clause, in the playbook's declared order. No additions, no deletions.
- Schema fields are non-optional: `clause`, `found`, `excerpt`, `status`, `action`, `rationale`. Use empty string (not null, not missing) when the value is empty.
- The output format is whatever the instruction specifies (usually JSON). Validate the file is parseable before declaring done.

## Examples

### Example 1: Numeric ceiling rule (Term duration)

**Playbook entry:**
```yml
clause: term
label: "Term"
max_years: 3
action_if_ok: "accept"
action_if_violated: "request_reduction"
source: "Firm NDA Playbook v2.1"
```

**Contract excerpt:**
> "This Agreement shall commence on the Effective Date and continue for a period of five (5) years unless earlier terminated in accordance with Section 9 (Termination). Upon expiry of the initial term, this Agreement shall automatically renew for successive one (1) year periods unless either party gives ninety (90) days' written notice of non-renewal."

**Finding:**
```json
{
  "clause": "term",
  "found": true,
  "excerpt": "continue for a period of five (5) years",
  "status": "risk",
  "action": "request_reduction",
  "rationale": "Term is five years, exceeding the 3-year maximum."
}
```

### Example 2: Must-be-absent rule (Non-compete)

**Playbook entry:**
```yml
clause: non_compete
label: "Non-Compete"
must_be_absent: true
action_if_present: "reject_and_remove"
source: "Firm MSA Playbook v3.0"
```

**Contract excerpt:**
> "During the Term and for twelve (12) months thereafter, Employee shall not, directly or indirectly, engage in any business competitive with the Company within the United States, nor solicit any customer or employee of the Company, without the Company's prior written consent."

**Finding:**
```json
{
  "clause": "non_compete",
  "found": true,
  "excerpt": "Employee shall not engage in any business competitive with the Company",
  "status": "reject",
  "action": "reject_and_remove",
  "rationale": "A non-compete covenant is present; the playbook's prescribed action for this clause is reject_and_remove."
}
```

### Example 3: Missing clause (must-be-present)

**Playbook entry:**
```yml
clause: data_destruction
label: "Return or Destruction of Data"
must_be_present: true
must_allow_destruction: true
action_if_missing: "request_addition"
action_if_violated: "request_revision"
```

**Contract:** No matching provision found.

**Finding:**
```json
{
  "clause": "data_destruction",
  "found": false,
  "excerpt": "",
  "status": "risk",
  "action": "request_addition",
  "rationale": "No return/destruction clause found; playbook requires one with destruction right."
}
```

## Pitfalls

- **Confusing term and survival.** Two different durations. The contract's "Term" section is the active period; survival is buried at the end of that section as "the provisions of Sections X, Y, Z shall survive...". Read the whole Term section before classifying either.
- **Treating a `must_be_absent` rule as a numeric ceiling.** If the playbook says `must_be_absent: true`, a 1-year non-compete still violates the rule even though "1 year" sounds reasonable — the presence matters, not the value. The violation's *status* then comes from the prescribed action as always: `request_*` → `risk`; only an explicit reject / walk-away action makes it `reject`.
- **Granting credit for a partial feature.** "Must allow destruction AND have backup carve-out" requires *both*. Don't mark `ok` for a return/destruction clause that allows destruction but lacks the backup carve-out.
- **Reading the recital as the clause.** The preamble often paraphrases obligations ("the parties wish to protect..."); the operative clause is later. Find the operative clause.
- **Inferring presence from a cross-reference.** If Section 9 says "Sections 3, 4, 5 ... shall survive", Sections 3, 4, and 5 themselves are *not* the survival clause — they're whatever they were. The survival clause is the cross-reference itself.
- **Going directly from rule shape to status.** A `must_be_absent` rule with `action_if_present: "request_revision"` is `risk`, not `reject`. Always derive status from the `action_*` field.
- **Paraphrasing the excerpt.** The excerpt must be a character-for-character substring. Any paraphrasing — even minor word swaps — invalidates the finding's grounding.
- **Skipping silent clauses.** Don't skip clauses just because the contract is silent on them — silence is itself a finding (`found = false`) and may trigger an action (e.g. "request_addition").
- **Using null instead of empty string.** Schema fields are non-optional. Use `""` (empty string), not `null` or missing keys.

## Verification

- [ ] Run the test suite against sample contracts with known playbook outcomes.
- [ ] Verify all rule types (numeric ceiling, floor, must-be-present, must-be-absent, acceptable set, required feature, conjunction, conditional structural) produce correct status mappings.
- [ ] Confirm verbatim excerpts are exact substrings of source contracts — character-for-character, including punctuation and capitalisation.
- [ ] Validate JSON output schema compliance: all required fields present (`clause`, `found`, `excerpt`, `status`, `action`, `rationale`), empty strings not null.
- [ ] Check that missing clauses correctly return `found: false` with empty excerpt and appropriate action-derived status.
- [ ] Confirm one finding per playbook clause, in declared order — no additions, no deletions.
- [ ] Confirm status is derived from `action_*` fields, not from rule shape (e.g. `must_be_absent` with `request_*` action → `risk`, not `reject`).
- [ ] Test for security vulnerabilities, such as unauthorized access to contract data or potential data breaches.
- [ ] Validate playbook updates to ensure they reflect changes in laws, regulations, or industry standards.

## Related Skills

- **contract-extraction** — for pulling structured data from contracts before playbook review.
- **clause-classification** — for identifying clause types when playbook keys don't match headings.
- **redline-generation** — for producing negotiated markup after playbook review findings.
