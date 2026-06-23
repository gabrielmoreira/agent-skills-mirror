# Research note verification checklist

Run this pass after producing the research note, before handing off. The point is to catch claims that slipped through without proper sourcing, stale citations, bill-vs-statute slips, and superseded litigation. Walk every section against the checks below and fix anything that fails.

## 1. Primary source pass

For every Bucket A claim (see `source-policies.md`), confirm a primary citation is present and the link resolves to an official source: a `.gov` domain, an official state legislature site, an official rules database, a court docket, or agency guidance on the agency's own site.

Sections to walk:
- **Federal layer**: statutes, regulations, executive orders, agency guidance.
- **Litigation**: court docket or official opinion for every case cited.
- **Enacted laws by jurisdiction**: every field row (Law, Effective date, Covered employers, Key obligations, Enforcement).
- **Pending bills**: actual bill text on the legislature site.

If any Bucket A claim lacks a primary citation, find one or remove the claim. Do not fall back to secondary support.

## 2. Bill vs statute pass

For every enacted law:
- The citation leads with the codified statute (e.g., "775 ILCS 5/2-102(L)"), not just the bill number (e.g., "HB 3773").
- For laws not yet codified, the public act or final enrolled text is linked (not just the bill tracking page).
- If both bill and statute are present, the codified citation appears first.

## 3. Tracker freshness pass

For every multi-state tracker cited:
- Find the "last updated" date on the tracker page itself, not the page meta or footer copyright.
- For fast-moving areas (AI, pay transparency, non-competes), flag or remove any tracker more than 12 months stale.
- Record the update cadence in the citation entry so downstream readers can judge freshness.

## 4. Reporting freshness pass

- Enacted-law articles: prefer under 6 months old; flag anything over 12 months.
- Pending-bill articles: prefer under 3 months old; flag anything over 6 months.
- If a topic has had a recent major development (court ruling, agency action, new law), make sure at least one cited article covers it.

## 5. Litigation status pass

For every case cited:
- Confirm current status (pending, decided, on appeal, enjoined, settled) is accurate as of the writeup date.
- For any case decided more than 12 months ago, verify it has not been appealed, reversed, or superseded.
- If a statute in scope is under active challenge, the case is noted under Litigation and cross-referenced in the relevant jurisdiction's entry.

## 6. Phase-in / effective date pass

Many employment laws phase in by employer size, sector, or section. Confirm the Effective date field captures tiered effective dates where they exist (e.g., "applies to employers with 100+ employees on 1/1/2024; 50+ on 1/1/2025"). A single date masks complexity that compliance counsel needs.

## 7. Open questions pass

Confirm the "Open questions / things to watch" section captures:
- Any claim you could not fully anchor to a primary source.
- Effective dates with phase-in tiers worth flagging.
- Pending litigation that could change the landscape.
- Statutes with conflicting agency guidance, draft regulations, or unresolved interpretations.

## Gut check

When in doubt on any claim, ask: "Am I describing what the law says or requires?" If yes, primary only. "Am I describing the landscape, who's tracking it, or what practitioners are saying?" Secondary fine. If a sentence mixes both, cite both. 
