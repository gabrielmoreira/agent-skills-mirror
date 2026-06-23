# customs-trade-law

A Claude Code Agent Skill for U.S. customs classification and trade-law research.

It helps prepare attorney-reviewable draft work product for HTSUS classification, CROSS ruling research, CIT/CAFC decision briefing, duty compilation, country-of-origin analysis, Chapter 99 screening, AD/CVD issue spotting, PGA review, and UFLPA forced-labor checks.

> Draft work product only. Not legal advice. Outputs must be reviewed by a U.S.-licensed attorney or licensed customs broker before use in an import transaction.

## Install

```text
/plugin marketplace add onurkafk/customs-trade-law
/plugin install customs-trade-law@onurkafk
```

Restart Claude Code or start a new session after installing.

Alternative local install:

```sh
git clone https://github.com/onurkafk/customs-trade-law.git ~/.claude/skills/customs-trade-law
```

## Use

No slash command is required. Ask naturally:

```text
Classify a Bluetooth keyboard from China.
Find CROSS rulings for ceramic mugs under heading 6912.
Calculate duty for HTS 8471.30.0100 from Taiwan.
Check whether Section 301 applies to this product.
Run an import compliance review for medical devices from Vietnam.
```

## What It Handles

- HTSUS classification using GRI 1-6 and Additional U.S. Rules
- CROSS ruling research with HQ/NY authority weighting
- CIT and CAFC decision analysis from retrieved opinion text
- Duty compilation: General, Special, Chapter 99, AD/CVD, MPF, HMF
- Country of origin, marking, FTA qualification, and TAA review
- PGA and UFLPA screening for import compliance risk

## How It Works

The skill enforces a U.S. customs authority hierarchy:

```text
HTSUS legal text > CAFC > CIT > CBP HQ > CBP NY > agency guidance > secondary sources
```

It also requires:

- current HTS JSON discovery through Data.gov before hierarchy-sensitive analysis
- source labels: `Verified`, `Retrieved`, `Identified`, `Unverified`
- evidence ledgers for material legal conclusions
- explicit human-review flags for missing facts, conflicts, stale sources, and high-risk ambiguity

Core operating rules live in [`SKILL.md`](./SKILL.md). A worked example is available at [`examples/output.md`](./examples/output.md).

## Permissions

The skill retrieves live government sources. Add these `WebFetch` permissions to `~/.claude/settings.local.json` or your project settings:

```json
{
  "permissions": {
    "allow": [
      "WebFetch(hts.usitc.gov/*)",
      "WebFetch(www.usitc.gov/*)",
      "WebFetch(catalog.data.gov/*)",
      "WebFetch(search.uscourts.gov/*)",
      "WebFetch(www.cit.uscourts.gov/*)",
      "WebFetch(law.justia.com/*)",
      "WebFetch(www.federalregister.gov/*)",
      "WebFetch(rulings.cbp.gov/*)",
      "WebFetch(ustr.gov/*)",
      "WebFetch(www.trade.gov/*)",
      "WebFetch(www.cbp.gov/*)"
    ]
  }
}
```

## Repository

```text
customs-trade-law/
├── SKILL.md            # skill manifest and workflow router
├── references/         # methodology, doctrine, source maps, disclaimers
├── templates/          # output templates
├── scripts/            # HTS, CIT, and hierarchy helpers
├── examples/           # worked examples
├── evals/              # evaluation scenarios
├── CHANGELOG.md
└── LICENSE
```

## Version

Current skill version: `1.0.2`

See [`CHANGELOG.md`](./CHANGELOG.md) for release notes.

## License

AGPL-3.0. See [`LICENSE`](./LICENSE).
