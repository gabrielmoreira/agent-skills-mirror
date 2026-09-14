# pii

Local PII / identification-risk detector (privacy epic #4256, slice S5).
Detects when a prompt or document may contain patient / legal / financial /
family or other identifiable information and reports a risk **level**, a
numeric **score**, and the matched **categories**, so upstream gates can
decide whether content is safe to send off-device.

## Guarantees

- **Fully local.** `scan()` is pure pattern + keyword matching over the input
  string — no network call, no async, no external model. Importing this
  module pulls in nothing beyond `regex`.
- **Recall over precision.** A missed flag means sensitive data leaves the
  machine unnoticed, so the detector is tuned to over-flag rather than
  under-flag.
- **Never reports raw matched text.** The result type carries only categories
  and counts, never the matched substrings — the result itself must not
  become a new PII sink.

## Key files

| File | Purpose |
| --- | --- |
| `types.rs` | `RiskLevel`, `PiiCategory` (with per-category `weight()` and `is_strong_identifier()`), `CategoryHit`, `PiiScanResult` |
| `detector.rs` | `scan()` — walks the compiled rule set, tallies matches, folds into a `PiiScanResult` |
| `rules.rs` | Compiled rule table: pattern rules (regex + optional structural validator, e.g. Luhn for cards) and keyword rules (word-boundaried term alternations for topical categories) |

## Public surface

- `scan(content: &str) -> PiiScanResult` — the only entry point.
- `PiiCategory` — structured identifiers (`Email`, `PhoneNumber`, `NationalId`,
  `CreditCard`, `BankAccount`, `IpAddress`, `PostalAddress`) and topical
  context (`DateOfBirth`, `Passport`, `Medical`, `Legal`, `Financial`,
  `Family`).
- `RiskLevel` — `None < Low < Medium < High`; `is_sensitive()` is `true` for
  anything above `None`.
- `PiiScanResult { level, score, categories, hits }` — `is_sensitive()` /
  `has_category()` helpers.

## Scoring model (`detector::scan`)

- Each distinct category contributes its `PiiCategory::weight()` once.
- Each additional co-occurring category adds a flat `CO_OCCURRENCE_BONUS` (5)
  — multiple distinct categories in one blob look more like a real record than
  any single one alone.
- A "strong identifier" (`NationalId`, `CreditCard`, `Passport`,
  `BankAccount`) forces `RiskLevel::High` regardless of the numeric score.
- The raw score otherwise maps to level via fixed thresholds: `0` → `None`,
  `1..=19` → `Low`, `20..=44` → `Medium`, `45+` → `High`.

## Used by

- `security::mod.rs` re-exports `scan` as `scan_pii`, along with
  `CategoryHit`, `PiiCategory`, `PiiScanResult`, `RiskLevel`.
- `crates/openhuman-core/src/agent/tinyagents/host/security_gate.rs` documents
  `security::pii::scan` as the detection primitive for a future `Redacted`
  screening outcome; as of this writing it is referenced but not yet wired
  in — screening only ever passes or blocks (see the `TODO(phase4)` in
  `screen_input`).
- Cross-links [`../egress/README.md`](../egress/README.md):
  `EgressDescriptor::risk_level` / `risk_categories`
  (`IdentificationRisk`) are the eventual consumer of this detector's output
  once the S5 slice wires it into the egress spine.

## Tests

- `detector_tests.rs`, `pii_tests.rs`.
