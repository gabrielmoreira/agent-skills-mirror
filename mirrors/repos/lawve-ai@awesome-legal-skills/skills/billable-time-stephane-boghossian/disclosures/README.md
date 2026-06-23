# disclosures/ — bar-opinion disclosure pack

A starter library of AI-disclosure language keyed to specific bar opinions or
guidance documents. The CLI references these when `matter.yml` sets
`ethics.disclosure_pack: <code>`.

## The verified-by-lawyer contract

**Every pack entry ships with `verified: false`.** That is intentional. The
maintainers of this repository are not your bar counsel. We compile starter
language and citations as a research aid — not as legal advice on what your
jurisdiction's rules actually require.

Before you rely on any pack entry:

1. Open the `source_url` and read the opinion yourself.
2. Confirm the citation, date, and scope are still accurate (opinions can be
   withdrawn, amended, or superseded).
3. Adjust `canonical_disclosure_text` to fit your matter and your client's
   engagement letter.
4. Flip `verified: true` and add your own `verified_by` line with your bar
   ID and the date you verified.

If a pack entry says `verified: false` and you run the CLI with `--strict`,
the tool will refuse to generate a final artifact until you have done your
homework.

## Schema

```yaml
code: <slug, must match filename>
jurisdiction: <human-readable label, e.g. "ABA Model", "FL", "CA", "NY-City">
opinion: <citation, e.g. "ABA Formal Opinion 512">
date: <YYYY-MM-DD of the opinion>
source_url: <permanent URL to the opinion text>
verified: false # flip to true after you have read the opinion
verified_by: ~ # your bar ID + date, e.g. "CT-12345, 2026-05-18"
canonical_disclosure_text: |
  <a conservative disclosure paragraph you would be comfortable having on
   every bill in this jurisdiction. Synthesis, not a quote, unless the
   opinion mandates specific language.>
notes: |
  <what the opinion actually covers, what it does NOT mandate, and any
   pitfalls. This is the maintainer's research note — verify against source.>
billing_rules_summary: |
  <one paragraph on what the opinion says about fees, markups, and time
   recording. Does not replace reading the opinion.>
```

## How `matter.yml` uses a pack

```yaml
ethics:
  ai_disclosure_required: true
  disclosure_pack: aba-512 # loads disclosures/aba-512.yml
  disclosure_text:
    ~ # optional: lawyer override. If set,
    # overrides pack canonical for this matter.
```

The CLI emits:

- The pack code and SHA-256 in the artifact's chain-of-evidence section.
- The pack `verified` flag (or a warning if `false`).
- The active disclosure text actually used per entry.

In `--strict` mode the CLI refuses to generate a final artifact if:

- The pack reference is invalid.
- The pack is `verified: false` AND `matter.yml` has not overridden the text.
- The active disclosure text is empty, `TODO`, or matches a placeholder
  pattern.

## What this pack is NOT

- It is **not** legal advice.
- It is **not** an authoritative list of every jurisdiction's AI rule.
- It is **not** a substitute for reading the opinion you cite.
- It is **not** updated automatically — bar rules change; pull requests
  with citation updates are welcome.

## Contributing a jurisdiction

1. Open the opinion, get the citation and a permanent URL.
2. Add `disclosures/<slug>.yml` following the schema.
3. **Leave `verified: false`** unless you are a member of that bar AND have
   personally read and verified the opinion text.
4. Add a `notes` paragraph distinguishing what the opinion mandates from
   what your `canonical_disclosure_text` synthesizes.
5. Open a PR. The maintainers will not flip `verified: true` for you — that
   is each user's responsibility per their own bar admission.
