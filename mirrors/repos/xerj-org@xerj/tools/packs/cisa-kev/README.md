# cisa-kev — CISA Known Exploited Vulnerabilities corpus pack

The US Cybersecurity and Infrastructure Security Agency (CISA) **Known Exploited
Vulnerabilities (KEV)** catalog as a portable, checksum-verified corpus pack —
built with `xerj corpus build` from this directory's
[recipe.toml](./recipe.toml) without a line of domain-specific Rust code.

Every number below is measured from a real build
([pack-stats.json](./pack-stats.json), `provenance: measured`), and
`tests/pack_claims.rs` pins this README against `pack-stats.json` and the recipe
SHA-256 so the three cannot drift apart.

| What | Count |
|---|---|
| Source records harvested (envelopes) | 1746 |
| Records after identity resolution | 1746 |
| Vendors covered (`vendorProject`) | 289 |
| Products covered (`product`) | 705 |
| Records with CWE classification | 1571 (189 distinct CWE IDs) |
| Records flagged known ransomware use | 361 |
| Records JSONL bytes | 2993632 |
| Cold build (network fetch + harvest + pack) | ~1 s |

## Why this pack exists

`rust-vulns` exercises multi-source OSV + RustSec markdown advisory merging.
`cisa-kev` exercises a completely different shape on the same pipeline (#1110):

- **Wrapped JSON feed (`kind = "http-json"`, `records_field = "vulnerabilities"`)**
  instead of a git repository or zip archive.
- **Flat record normalization (`format = "flat"`)** with domain-native field
  names (`cveID`, `vendorProject`, `product`, `vulnerabilityName`,
  `shortDescription`, `requiredAction`, `knownRansomwareCampaignUse`, `cwes`).
- **Derived fields** via `regex_extract` (`cwe_ids`) and `map`
  (`ransomware_status`: `"known"` vs `"unknown"`).
- **Licence (`CC0-1.0`)**: CISA distributes the KEV catalog under Creative
  Commons CC0 1.0 (stated in the `LICENSE` of CISA's official mirror,
  [cisagov/kev-data](https://github.com/cisagov/kev-data/blob/develop/LICENSE)),
  consistent with its status as a US federal government work
  (17 U.S.C. § 105). Two caveats from that licence travel with the pack:
  content at third-party links inside the `notes` field is governed by those
  sites' own terms, and using the data does not authorize use of the CISA logo
  or DHS seal, nor imply endorsement by CISA or DHS.

## Snapshot and provenance

The source is CISA's live feed URL, which is **not version-pinned** and grows
as CISA adds entries; a rebuild on a later day produces more records than the
table above. The numbers above were measured against catalog version
`2026.10.15` (`dateReleased` 2026-10-15T17:00:11Z, `count` 1746) and
independently re-counted from that same feed during review. Refresh them with
`cargo test -p xerj-autoindex --test pack_claims measure_cisa_kev_pack_live -- --ignored --nocapture`.

This pack is **not** published or signed by `.github/workflows/pack-publish.yml`
and ships no signing key; build it locally from the recipe.

## Build, consume, query

```sh
# 1. build (or incrementally refresh) from the recipe
xerj corpus build cisa-kev --recipe tools/packs/cisa-kev/recipe.toml

# 2. install the pack into your corpus store
xerj corpus add cisa-kev --from ~/.xerj-code/builds/cisa-kev/pack/cisa-kev

# 3. index and query
xerj corpus index cisa-kev
xerj code cisa-kev "exchange server SSRF proxylogon"
```

## Fields worth knowing

| Field | What it carries |
|---|---|
| `id` / `cveID` | canonical CVE identifier (`CVE-YYYY-NNNN+`) |
| `title` / `vulnerabilityName` | human-readable vulnerability title |
| `vendorProject` / `product` | vendor and product names (also routed into `defs`) |
| `shortDescription` / `requiredAction` | CISA summary and remediation directive |
| `dateAdded` / `dueDate` | catalog addition date and federal remediation deadline |
| `cwe_ids` | derived array of `CWE-NNN` identifiers |
| `ransomware_status` | derived `"known"` or `"unknown"` from `knownRansomwareCampaignUse` |
| `licence` / `sources` / `origin` | provenance per record (`CC0-1.0`, `["kev"]`) |
