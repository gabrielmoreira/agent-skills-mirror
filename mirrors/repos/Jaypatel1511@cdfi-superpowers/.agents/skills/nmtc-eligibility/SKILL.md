---
name: nmtc-eligibility
description: >-
  Check whether a U.S. address or census tract is New Markets Tax Credit (NMTC)
  eligible as a Low-Income Community, and screen a project's NMTC feasibility.
  Use when the user asks "is this address/tract NMTC eligible", about "distress
  criteria", "severe distress", "deep distress", "low-income community" / "LIC"
  status, or wants a first-pass NMTC deal feasibility score. Backed by the
  audited PyPI packages nmtc-mapper and nmtc-screener — never estimate
  eligibility from general knowledge.
compatibility: >-
  Requires Python >=3.9, pip, and network access to pypi.org plus
  geocoding.geo.census.gov (Census geocoder) and www.cdfifund.gov (CDFI Fund
  eligibility workbook). The CDFI Fund relocates that workbook periodically, so a
  lookup can fail even on an open network — the skill reports the error rather
  than estimating eligibility.
---

# NMTC Eligibility

Grounds NMTC eligibility answers in two published, audited packages instead of
guessing. **nmtc-mapper** geocodes an address to a census tract and looks the
tract up in the CDFI Fund's NMTC Low-Income Community (LIC) eligibility table.
**nmtc-screener** runs a structured first-pass feasibility score on a project.

## When to use

- "Is 2400 Grand Concourse, Bronx NY NMTC eligible?"
- "Is census tract 36005023702 a low-income community?"
- "Is tract 36005023702 flagged severe distress — or deep distress — in the CDFI
  Fund's eligibility table?" (a tract carries a distress *flag*; a **CDE** makes
  the 85%/20% *commitments* — see the commitment-basis rule)
- "Does my pipeline meet the 85% investment commitment?" — answered by pointing
  at that rule, never by returning a number: these packages never see a QLICI
  amount.
- "Screen this $8.5M grocery project for NMTC feasibility."

## When NOT to use

- Anything requiring the *official* CDFI Fund allocation decision — this is a
  screening/eligibility lookup, not an allocation award or legal determination.
- Historic Tax Credit, LIHTC, or Opportunity Zone *investment* structuring
  (OZ *flag* is reported by the mapper, but OZ deal mechanics are `oz-tracker`).
- NMTC transaction / credit / capital-stack modeling beyond the screener's
  first-pass estimate — that depth lives in `nmtc-calc`.

## Install

```
pip install "nmtc-mapper>=0.6.1" nmtc-screener
```

Verified 2026-09-14 (PyPI) against **`nmtc-mapper>=0.6.1`** (resolved 0.6.1,
published 2026-09-14) and **nmtc-screener 0.1.0** (`nmtc-calc 0.2.1` is pulled
in as a dependency). Quote the floor, not the resolved point version — the point
version moves on every release and this line does not. The `>=0.6.1` floor is
not cosmetic — 0.4.0 is where `nmtc_eligible` became tri-state (see below), 0.4.1
binds the geocoder vintage to the eligibility table's 2020 tract basis (see Data
dependencies & fragility), **0.4.2 is the release that stopped reporting 168
statutorily-eligible tracts as ineligible**, **0.5.0 is the release that
stopped returning a confident `False` for every unconfirmed Opportunity Zone and
for every field of a tract it never read**, **0.6.0 is the release whose
`eligibility_status` vocabulary this skill describes** — it added a fifth value,
`not-covered-territory`, and exported the vocabulary as a constant (see the
fifth reason below) — and **0.6.1 is the release that can still download the
CDFI Fund eligibility table at all** (see the sixth reason below). A reader on
0.3.x following this skill's third-state guidance would never see `None`,
because 0.3.x collapses "could not determine"
into `False`; a reader on 0.5.0 following this skill's five-way guidance would
never see `not-covered-territory`, because 0.5.0 reports an Island Area tract as
a plain `not-found`.

**The third reason is this skill's own rule, shipped as a defect.** The
third-state rule below says a fabricated negative "kills a deal that may
genuinely qualify," and that "a false 'ineligible' is exactly as damaging as a
false 'eligible,' in the opposite direction." Pre-0.4.2 the backing package
delivered exactly that harm — not through a `None` rendered as "no," but through
a confident `False`. A tract can reach LIC status by three routes; the CDFI Fund
published the poverty and 80%-AMI routes in the workbook's **column C** and the
§45D(e)(5) **high-migration-rural** route (MFI ≤ 85% AMI in a county with ≥10%
net out-migration over 20 years) in **column N** (the layout in force through
June 2026 — see the note below). Pre-0.4.2 read column C alone as the entire
verdict while separately parsing, storing and surfacing column N as
`is_high_migration_rural`. **On the July-2026 file that argument is measured
against, 1,422 tracts carried the high-migration-rural designation, and 168 of
them fail both the ≥20%-poverty and ≤80%-AMI prongs** — all non-metro, all in
the (80%, 85%] MFI band, so §45D(e)(5) is the only route by which they qualify.
Those 168 were reported ineligible by a package that was, in the same object,
reporting the evidence of their eligibility. 0.4.2 reads the verdict as **C or
N**. That is why no floor below 0.4.2 is defensible and none of this is
version-hygiene preference: 0.4.2 is the line below which this skill's central
rule is violated by its own dependency.

**On the file the Fund publishes today the count is 1,318, and the 168 are
untouched.** The September-2026 replacement retitled column N *"High Migration
Rural County Census Tract for Deep Distress"* and narrowed it to **1,318 YES**.
The 104 tracts it dropped are all column-E **YES** — they reach LIC by the
≥20%-poverty route — with MFI between 85.7% and 134.4%, so the field now carries
the §45D(e)(5) income-route determination only and no longer flags "any LIC tract
in a high-migration-rural county." The 168 *fail* the poverty prong (column E
**NO**), so they are disjoint from the 104 and not one of them was dropped; every
one also sits at MFI ≤ 85%, the band the narrowed column keeps. And **no
eligibility verdict moved — 0 of 85,395 differ** — because the 1,318 are a strict
subset of the 1,422 and all 104 are column C YES in both files. The argument
above therefore stands on both files; what moves is `is_high_migration_rural`'s
True count, nothing else.

*Provenance, stated precisely because this round turns on it: 1,318, the 104,
85.7%–134.4%, and 0-of-85,395 are **derived from `nmtc-mapper` 0.6.1's pinned
constants and source comments** (read 2026-09-14), **not** re-measured against a
live table — this session has no route to `cdfifund.gov`. 1,422 and the 168 are
the **July-2026 file's** figures, measured on 0.5.0 in an earlier session.*

**A pre-0.4.2 install does not answer at all — and since 2026-09-03 it fails one
step earlier than this skill used to say.** The Fund moved the C/N boundary in
**July 2026**, folding the high-migration-rural route into column C and renaming
that column's header. 0.4.1 pins column C's exact *pre*-July-2026 header string,
so against the **July-2026** workbook — while that file was still being served at
the URL 0.4.1 pins — its positional header validation raised
`EligibilitySchemaError` at column index 2 and loaded nothing. That is no longer
the error a reader will see. On **2026-09-03** the Fund retired that URL, and the
retired route answers **403**; 0.4.1 still pins the dead literal, so on a **cold
start today** it fails at *download* — `EligibilityDownloadError` naming the 403 —
and never reaches the header guard at all. The schema path survives in exactly one
case: a machine with a **warm** `~/.nmtcmapper/cache/` holding the July-2026
workbook, where the loader returns the cached file without downloading and the
header check then raises `EligibilitySchemaError`. The 168-tract divergence was
real against the pre-July-2026 edition; after it the same defect presents as a
hard load failure — download if cold, schema if warm. Either way 0.4.2 is the
release that reads `C or N` and is therefore correct on both sides of the boundary
move, and `>=0.6.1` is the floor that can load anything at all.

*Provenance: **derived, not executed.** The download-before-parse control flow,
the retired URL literal and column index 2's two header strings were read from the
`nmtc-mapper` **0.4.1 and 0.6.1 sdists** on **2026-09-14**
(`nmtcmapper/data/loader.py`, `nmtcmapper/data/schema.py`,
`nmtcmapper/exceptions.py`). No 0.4.1 install was run and no request was made to
`cdfifund.gov` — this session has no route to it.*

**The fourth reason is the same defect one field over, and it is why the floor
moved to `>=0.5.0`.** Through 0.4.3 `is_opportunity_zone` was a plain `bool`, so
the package answered "not an Opportunity Zone" about tracts it had no basis to
answer for: **78,039 of the 85,395 tracts received a confident `False`** (every
row in the table that is not in the 8,764-tract designation set), and the
geocode-no-match branch hardcoded `is_opportunity_zone=False` for an address it
never resolved to a tract at all. The designations are 2010-tract-based and this
package's table and geocoder are 2020-basis, so a vintage miss and a genuine
non-designation are the same observation — a distinction the package cannot
make and therefore must not assert. **0.5.0 makes the field `Optional[bool]`,
never `False`, and adds `opportunity_zone_status` to say which of the three
states it is in.** Below 0.5.0 this skill has to correct its own dependency in
prose on every OZ answer, which is exactly the posture the third-state rule
exists to make unnecessary. 0.5.0 also drops `is_nmtc_native_area`, a field that
could only ever say "I don't know" (see the note under the field list).

**The fifth reason is why the floor can never again sit below 0.6.0: the
`eligibility_status` vocabulary this skill teaches is only true from 0.6.0.**
Through 0.5.0 the property had four values and an Island Area tract — American
Samoa, Guam, the CNMI, the US Virgin Islands — came back as `not-found`, the
same word as a
mistyped GEOID, even though nothing about it was *missing*: those four
jurisdictions are outside the loaded table's universe by scope (see the
vintage-scope rule). 0.6.0 separates the two with a fifth value,
**`not-covered-territory`**, and exports the whole vocabulary as
**`nmtcmapper.ELIGIBILITY_STATUS_VALUES`** so a caller can bind to it instead of
retyping it. Executed this session on 0.6.0 installed from PyPI:

```
>>> nmtcmapper.__version__
'0.6.0'
>>> nmtcmapper.ELIGIBILITY_STATUS_VALUES
('verified-eligible', 'verified-ineligible', 'not-found', 'not-covered-territory', 'geocode-failed')
```

0.5.0 exports no such constant (`AttributeError`, verified against the 0.5.0
wheel this session). A skill that describes five values while allowing 0.5.0 to
be installed is the same defect as this skill's own pre-0.6.0 list was — one
enumeration copied into prose and left behind by the package — which is why the
floor moved with the vocabulary rather than after it.

**The sixth reason is why the floor is `>=0.6.1`, and it has nothing to do with
vocabulary: `>=0.6.0` is a floor that admits an install which cannot load its
data.** On 2026-09-03 the CDFI Fund retired the workbook URL that every release
through 0.6.0 pins, and that URL now answers **403**; 0.6.1 retargets the loader
to the replacement. A reader who resolves `>=0.6.0` to 0.6.0 gets
`EligibilityDownloadError` on the first cold call and no answer to any question
in this skill. Whoever raises this floor next: it is a data-availability floor,
not version hygiene — see the dated note under Data dependencies & fragility.

Import names (dist name ≠ import name):

| dist | import |
|---|---|
| nmtc-mapper | `nmtcmapper` |
| nmtc-screener | `nmtc_screener` |

## The answer space is TRI-STATE (0.4.0 — read this before anything else)

`nmtc_eligible` is **`Optional[bool]`** — `True`, `False`, or **`None`**. There
are three outcomes, not two:

| `nmtc_eligible` | `distress_level` | meaning |
|---|---|---|
| `True`  | `deep` / `severe` / `lic` | **verified eligible** — the table says YES |
| `False` | `ineligible`              | **verified ineligible** — the table says NO |
| `None`  | `unknown`                 | **INDETERMINATE** — no verdict was reached |

**`None` / `"unknown"` means "could not be determined." It is NOT "not
eligible."** Never render `None` as "no," "ineligible," "not eligible," or a
falsy `False`. A `None` is reached three ways: the address did not geocode; the
tract is absent from the ~85k-tract universe (a bad/mistyped GEOID, a
leading-zero-stripped GEOID, or a vintage mismatch); or the tract is in one of
the four Island Areas the loaded table does not cover at all. None of the three
is a NO — all are "we don't know."

`EligibilityResult.eligibility_status` (property, 0.4.0; fifth value 0.6.0)
collapses this into one explicit five-way string so you never have to infer
intent from a `None`. The vocabulary is exported as
`nmtcmapper.ELIGIBILITY_STATUS_VALUES` (0.6.0) — bind to the constant, do not
retype it:

```
verified-eligible  |  verified-ineligible  |  not-found  |  not-covered-territory  |  geocode-failed
```

`not-found`, `not-covered-territory` and `geocode-failed` are the **three**
indeterminate cases — executed this session on 0.6.0, `nmtc_eligible is None`
on exactly those three and on no other. `summary()` prints indeterminate results
with an inline qualifier on the eligibility line itself — `❓ UNKNOWN — …
(indeterminate, NOT ineligible)` for the first and last, `🚫 NOT COVERED — …`
for the territory case — defined in
`nmtcmapper/eligibility/checker.py::EligibilityResult.summary`, not a footer.

**`not-covered-territory` is indeterminate, never a negative — and it is a
different kind of indeterminate from `not-found`.** `not-found` means the table
was searched for the tract and had no row: the tract may be mistyped, may be a
retired 2010 GEOID, or may simply be missing. `not-covered-territory` means the
tract is **outside the loaded table's universe** — the CDFI Fund's 2016–2020 ACS
NMTC LIC table covers the 50 states + DC + **Puerto Rico** (981 rows), and the
four DECIA Island Areas — American Samoa (FIPS 60), Guam (66), the Northern
Mariana Islands (69), the US Virgin Islands (78), **133 tracts** on 2020
geography — are not in it. Both halves of that were counted this session, not
relayed: the 85,395-row eligibility table has **zero** rows with those four
prefixes, and Treasury's OZ 2.0 table (85,529 rows, which 0.6.0 also loads and
which *does* carry the Island Areas) has exactly **133** — AS 18, GU 57, MP 26,
VI 32 — plus PR's 981, matching the eligibility table's PR count. Their
LIC status lives in a separate CDFI Fund file,
*"New Markets Tax Credit Low-Income Community Census Tracts (2020 Island Areas
Decennial Census)"*, which **nmtc-mapper does not load**. So the answer for a
territory tract is not "unknown, re-check the GEOID" — it is "this package
cannot answer for this jurisdiction; use CIMS or the Island Areas file." Do not
claim a territory answer this package cannot produce. **Puerto Rico is
covered**: a PR GEOID that misses is a real lookup miss and reports `not-found`
(executed this session: `72001956300` → `verified-eligible`, `72001999999` →
`not-found`; `66010950100` → `not-covered-territory`). The status is keyed on
the GEOID's state FIPS, so it is available from `check_tract` as well as from
`check_address`, and `enrich_dataframe` writes the same value into
`eligibility_status`.

### 0.5.0 extends the tri-state contract to every field that can be unobtainable

Through 0.4.3 only the verdict was tri-state, and its **neighbours fabricated
inside the very branches written to protect it**: the indeterminate branches
set every supporting boolean to a confident `False` about a tract no row was
ever read for. **Six fields are `Optional[bool]` in 0.5.0:**

| field | `None` when |
|---|---|
| `nmtc_eligible` | any indeterminate status (0.4.0; `not-covered-territory` joined the set in 0.6.0) |
| `is_non_metro` | any indeterminate status (0.5.0) |
| `is_high_migration_rural` | any indeterminate status (0.5.0) |
| `severe_distress` | any indeterminate status (0.5.0) |
| `deep_distress` | any indeterminate status (0.5.0) |
| `is_opportunity_zone` | **on every path** — `True` or `None`, never `False` (0.5.0) |

**The rule that ties them together: when `eligibility_status` is `not-found`,
`not-covered-territory` or `geocode-failed`, every tract-derived field is
`None`, because nothing was read.** Re-derived by execution on 0.6.0 this
session, across `EligibilityResult` and `enrich_dataframe` on all five statuses:
the four supporting booleans are `None` on exactly those three statuses and
non-`None` on the two verified ones. For a tract that *was* found, a `False` on
the four supporting booleans is unchanged and fully supportable — it is the
Fund's published `NO`, present as a strict YES/NO on all 85,395 rows. `is_opportunity_zone` is the exception in
both directions: it is keyed on designation-set membership rather than on
`tract_found`, so a retired 2010 GEOID that is designated still returns a
correct `True` alongside `tract_found=False`, and it is never `False` at all.

Two consequences worth stating because they bite silently:

- **`None` is falsy.** `if result.severe_distress:` and `'Yes' if x else 'No'`
  keep running after the type change and start meaning something else. Switch on
  `eligibility_status` / `opportunity_zone_status`, or test `is True` / `is None`
  explicitly. `summary()` does this — every line is a three-branch switch.
- **`poverty_rate`, `ami_ratio` and `unemployment_rate` have *two* kinds of
  missing, and they are different answers.** `None` means no row was read (the
  indeterminate branches); `NaN` means a **found** tract whose metric the Fund
  published as `NA` — 1,583 rows for poverty and 2,358 for AMI — which still
  carry a real published verdict. So `r.poverty_rate is None` is not a
  missing-value test on this field; use `pd.isna()` for "no number either way"
  and `eligibility_status` to tell which kind. `summary()` prints two different
  sentences for the two states (0.5.0).

## The hard failure rule (non-negotiable)

**If a tool errors, report the error verbatim and stop. NEVER estimate NMTC
eligibility from general knowledge, from the address alone, or from what a
neighborhood "seems like."** Eligibility is a specific tract-level lookup
against a specific CDFI Fund table; there is no valid way to infer it. A wrong
"eligible" answer can send a real deal down a dead end. A user asking for a
"best guess," "ballpark," or "rough" eligibility answer does not override this
rule; decline and report that the lookup failed.

## The third-state rule (non-negotiable — the load-bearing addition)

The hard failure rule above governs a tool that *errors*. This rule governs a
lookup that *succeeds and returns UNKNOWN* (`nmtc_eligible is None`,
`distress_level == "unknown"`, `eligibility_status` in `{not-found,
not-covered-territory, geocode-failed}` — three values, re-derived by execution
on 0.6.0 this session, not from a docstring). An unknown verdict is a **result,
not an error** — and it must be reported as its own answer:

- Report it as **"NMTC eligibility could not be determined for this tract"**,
  and **name the tract ID** (or state the address did not geocode). Say *why*,
  and say the right why: tract absent from the vintage's universe
  (`not-found`), tract in an Island Area this table does not cover
  (`not-covered-territory` — route to CIMS or the Island Areas file), or
  address failed to geocode (`geocode-failed`). The three are different next
  steps for the user; do not flatten them into one "unknown."
- **Never** collapse it into "not eligible," "no," or "ineligible."
- **Never** soften it into "probably not eligible" or "likely ineligible."
- **Never** resolve it from a neighboring tract, the ZIP, the city, or the
  address's apparent neighborhood — the same anti-pressure posture as the
  best-guess rule above.

**Why, inline (a model reading this needs the reason, not just the rule):** a
`None` rendered as "not eligible" is a *fabricated negative*. It kills a deal
that may genuinely qualify — the tract simply was not checkable in this vintage,
and the correct next step is to re-check against the vintage in force at
application time, not to declare the deal dead. A false "ineligible" is exactly
as damaging as a false "eligible," in the opposite direction.

## The vintage-scope rule (non-negotiable)

**This package carries the 2016–2020 ACS vintage ONLY** (the 85,395-tract table
below). NMTC LIC eligibility is governed by the ACS vintage tied to the deal's
**QLICI close date**, and answering the wrong vintage confidently is the same
class of failure as rendering `None` as "not eligible" — a confident answer
against data that does not govern. The CDFI Fund's transition rules (primary:
CDFI Fund, *2016-2020 ACS Data FAQ*, updated **Feb 1, 2024** —
`NMTC_LIC_FAQs_2020_ACS_Sept1_2023_Update_Jan2024.pdf` at
`cdfifund.gov/system/files/2024-01/`, announced at `cdfifund.gov/news/567`;
secondary, quoted verbatim: NMTC Coalition,
`nmtccoalition.org/2023/09/06/new-nmtc-data`):

| QLICI close date | Governing data | May this package answer? |
|---|---|---|
| **before Sept 1, 2023** | **must use 2011–2015** ACS | **No** — 2011–2015 is not carried here |
| **Sept 1, 2023 – Aug 31, 2024** | **may use either** 2011–2015 or 2016–2020 | Yes, but the 2011–2015 vintage is equally permitted |
| **on/after Sept 1, 2024** | **must use 2016–2020** ACS on 2020 tracts | Yes — authoritative |

Apply it:

- **Close date before Sept 1, 2023** → the 2016–2020 table does **not** govern;
  2011–2015 ACS does, and this package does **not** carry it. Do **not** answer
  from the 2016–2020 table. Say so and route the user to the CDFI Fund's CIMS
  (CDFI Information Mapping System), which carries the governing vintage.
- **Close date in the Sept 1, 2023 – Aug 31, 2024 window** → the 2016–2020
  answer is valid and permitted, but state that 2011–2015 is **also** an
  acceptable basis in this window, so the deal may qualify under the other
  vintage even if 2016–2020 says NO.
- **Close date on/after Sept 1, 2024, or unknown** → state which vintage the
  answer is based on (2016–2020) and that it is valid for QLICIs closing
  on/after Sept 1, 2023 and mandatory on/after Sept 1, 2024. If the close date
  is unknown or earlier, confirm it before relying on the answer — for a
  pre-Sept-1-2023 closing the 2011–2015 vintage (not carried here) governs.

**Island Areas are a second scope hole of the same class.** This table's
~85,395 rows cover the **50 states + DC + Puerto Rico only** (PR verified
present this session). The **Island Areas — American Samoa, Guam, the CNMI, and
the US Virgin Islands — were NOT covered by the 2016–2020 ACS** and are absent
from this package's table entirely. The CDFI Fund publishes a **separate**
Island Areas NMTC LIC file — `NMTC_LIC_Territory_2020_December_2023.xlsx`, built
on the **2020 Island Areas Decennial Census** (not the 2016–2020 ACS), released
Dec 19, 2023 and available in CIMS as of Jan 25, 2024 — which **this package
does not carry**. Per the CDFI Fund's *2016-2020 ACS Data FAQ* (updated Feb 1,
2024, General Q3): *"For Island areas, CDEs should continue to use 2011-2015
NMTC Low-Income Community eligibility data and follow the same transition dates
outlined in question 3."* An Island Area address/tract is therefore **"not
carried by this package," never "ineligible"** — route to CIMS or to the
separate territory file; do not answer it from this 2016–2020 ACS table. **As of
0.6.0 the package says this itself**: an 11-digit GEOID whose state FIPS is 60,
66, 69 or 78 returns `eligibility_status == "not-covered-territory"` (executed
this session on all four), and `summary()` prints `🚫 NOT COVERED — Guam is
outside the 2016-2020 ACS NMTC LIC table this package loads (50 states + DC +
PR)` with the separate file named on the following lines. Through 0.5.0 the same
GEOID returned a bare `not-found` (executed this session on the 0.5.0 wheel),
which told the reader to re-check the GEOID when the GEOID was fine. Puerto Rico
is **in** this table (981 rows), so a PR miss is a genuine `not-found`, not a
territory case.

## The commitment-basis rule (non-negotiable)

The three rules above govern what this lookup may say about a **tract**. This one
governs what it may say about a **CDE**, and the answer is *nothing*.

**The CDFI Fund's two distress commitments are measured on QLICI dollars.** The
CY 2024-2025 Allocation Application asks, at **Question 25(a)**, whether the
Applicant will commit to *"providing at least 85% of its QLICIs **(in terms of
aggregate dollar amounts)**"* in the qualifying areas, and at **25(b)(i)** for
*"the percentage of its QLICIs (in terms of aggregate dollar amounts)"* it will
commit to providing in the 20% tier — a figure it *selects*, not one it enters
(see the field shape below). The Fund's review-process document states both in one
sentence (quoted verbatim; downloaded from the source this session):

> **1. Targeting Areas of Higher Distress (Question 25).** The Applicant
> indicated that it will commit to providing at least 85% of its **QLICIs** in
> specified areas of severe distress and/or areas characterized by multiple
> indicia of distress. The Applicant indicated that it will commit to providing
> at least 20% of its **QLICIs** to "Deep Distress" areas.

— CDFI Fund, *CY 2024-2025 New Markets Tax Credit Program Allocation Application
Review Process, General Characteristics of a Highly Ranked Application*, §C.1;
`cdfifund.gov/system/files/2025-12/CY_2024_25_NMTC_Program_Review_Process.pdf`.

### The Application collects no percentage for Q25(a) — read the field shape first

**Both commitments are entered as selections, not as computed figures.** Read
verbatim from the instrument this session (CY 2024-2025 NMTC Program Allocation
Application, 142 pp., 1,525,626 bytes, SHA-256
`0280c6bc7b35f6015e2c2b1be4b1c07b3864f2dcbaeadfbbbf8bded8de12834f`, downloaded
from `cdfifund.gov/system/files/2024-11/` and text-extracted locally with
`pypdf`):

| field | printed p. | Response | Field Type |
|---|---|---|---|
| **25(a)** | 38 | `☐ Yes` / `☐ No` | **Dropdown Menu** |
| 25(a) items 1–12 | 39–40 | `Yes` / `No`, each item separately | Dropdown Menu |
| **25(b)(i)** | 41 | `0` / `5` / `10` / `15` / `20, if selected enter exact percentage 20-100% in 25(b)(ii)` | **Dropdown Menu** |
| **25(b)(ii)** | 41 | `___% of QLICIs` — completed *"only … by Applicants that select '20%'"*, admitting *"any percentage amount starting from 20% and up to 100%"* | **Numerical – Percentage** |
| 25(b) items 1–4 | 41–42 | `Yes` / `No`, each item separately | Dropdown Menu |
| 25(c) | 42 | `Text Entry` — track record in the areas selected | Text box |

1. **Q25(a) is answered Yes or No.** The 85% is the threshold printed in the
   question text — the figure the Applicant commits *to*, not a figure it
   supplies. **There is no percentage field for Q25(a) anywhere in Question 25.**
2. **Q25(b)(i) is a selection from 0 / 5 / 10 / 15 / 20**, and only selecting 20
   reaches a free numeric field — **25(b)(ii)**, a *separate* question, which
   then admits 20% to 100%. That single field is the only free-entry percentage
   in the whole of Question 25, and it is unreachable from any other rung.
3. **Both bind forward, over capital the Applicant does not yet have.** Q25(a)'s
   Question Notes, verbatim (printed p. 38): *"If the Applicant receives an NMTC
   Allocation, it will be required to meet the percentage figure identified, and
   such requirement will be a term of its Allocation Agreement."*
4. **The pipeline is not the deployment, and the Fund says so three times.**
   Immediately above Question 25 (printed p. 38): *"NOTE: The CDFI Fund does not
   expect that each and every investment will be in an area identified in
   Question 25."* Of the Table A5 sample transactions (printed p. 23): *"It is
   not expected that the Applicant will invest in all of the listed projects"* —
   those transactions *"should be representative of the types of projects that
   will be undertaken with an NMTC Allocation."* And Q25(b)(i)'s notes (printed
   p. 41): *"Applicants will not be held to the individual commitments to any of
   the areas listed below and will have the flexibility to invest in any of the
   areas as long as the overall commitment percentage is met."*

**The operational consequence, and it binds exactly as hard as the rest of this
rule: a CDE asking "what is my Q25(a) percentage" is asking for something the
Application does not collect.** The right answer is what the commitment means
and what evidence bears on it — **never a computed share, and never a
recommendation to answer No because a current pipeline falls short.**

**That last clause is the harm case.** A CDE whose identified projects sit at 60%
today is *not* thereby a "No" on Q25(a): the commitment governs the QLICIs it
will make with an allocation it has not yet received, and the Fund has said in
three separate places that today's project list is not that deployment. Tell that
CDE its "Q25(a) share is 60%" and it checks **No**, scores lower, and forfeits
points **it was entitled to claim** — understating itself to a federal agency on
a number the agency never asked it for. A fabricated share here is the same class
of failure as a fabricated negative on eligibility (third-state rule), pointed at
the Applicant instead of the tract.

**And do not overcorrect into "it's only a Yes/No, so check Yes."** The same
Question Notes make the answer binding — *"it will be required to meet the
percentage figure identified, and such requirement will be a term of its
Allocation Agreement"* — so **Yes** is a consequential answer too, enforceable
against an Allocatee that misses it. Neither direction is this layer's call to
make. What you can honestly give a CDE is **evidence, per prospective QLICI**:
which Q25 route each project's tract can be shown to satisfy, which it cannot,
and which this package cannot see at all (it reaches **two of the twelve** items
under 25(a) and **two of the four** under 25(b), and computes no multi-indicia
measure). The CDE aggregates that evidence over its own QLICI dollars and owns
the commitment. Carry the tri-state through: a `None` on any flag is **"not
determined for this tract,"** a third column in that evidence — never a "does not
qualify."

**The denominator is the CDE's own QLICI dollars — not QEI, not project count,
not tract count.** A QEI is what a tax-credit investor puts *into* a CDE; a QLICI
is what the CDE puts *out* into QALICBs (`references/cdfi-industry-primer.md`).
They are different quantities on different sides of the CDE, and the credit is
sized on the first while both commitments are sized on the second. Bucketing QEI,
or dividing counts instead of dollars, produces a number that is not the
commitment — under a label that says it is.

**These packages never see a QLICI amount.** A tract-level designation answers
*"if a QLICI were made here, would it count toward the numerator?"* It cannot
answer *"what share of this CDE's QLICIs qualifies?"* — that needs the CDE's own
deployment ledger, which is not an input to `nmtcmapper` or `nmtc_screener`.
The two questions are not the same question at different scales; the second one
has an input the first one does not.

**A `severe_distress=False` is therefore not a "does not count toward the 85%."**
A QLICI counts toward the Q25(a) commitment when it is made in an area
characterized by **at least one of items 1–5** *or* **at least two of items
6–12**. Severe Distress is only item 1. The
other single-item routes are **NMTC Native Areas, U.S. Island Areas,
Non-Metropolitan Counties, and Targeted Populations**; the two-of list runs
25%-poverty / 70%-MFI / 1.25× unemployment, Brownfield sites, ARC/DRA areas,
Colonias, federal MUA/HPSA areas, FEMA disaster counties, and USDA LILA
food-access tracts. Of those twelve this package returns **exactly two** —
`severe_distress` (item 1) and `is_non_metro` (item 4) — and computes **no**
multi-indicia measure at all. Two of the routes it cannot reach are ones this
skill already declines elsewhere: **Native Areas** (see the field-list note) and
**Island Areas** (see the vintage-scope rule). And the gap is not only in what
the package omits: derived against the live table this session, **10,532 tracts
are non-metro and not severe** (3,754 of them also LIC), so reading
`severe_distress` alone understates the qualifying set even within the two routes
the package *does* return.

**The same holds one tier down, and harder.** Q25(b)'s 20% tier is not Deep
Distress alone — it is **any one of four**: Deep Distress, NMTC Native Areas,
**High Migration Rural Counties**, and U.S. Island Areas. A `deep_distress=False`
says nothing about the other three. **High-migration-rural-and-not-deep is a
large set that a `deep_distress=False` hides**: on the **July-2026 file** it was
**1,185 tracts**, and `is_high_migration_rural` is a field this package returns
— so here too a negative on the flag the label names is not a negative on the
commitment. *The September-2026 figure has not been counted, and none is
asserted here: that file narrows the high-migration-rural column to 1,318, but
how many of the 104 dropped tracts were deep-distress is pinned nowhere in
`nmtc-mapper` 0.6.1, so the current value lies somewhere in **1,081–1,185** and
cannot be narrowed without the workbook. The deep column itself is byte-identical
between the two files (77,334 / 8,061), which fixes the deep set but not this
intersection.*

**The two commitments nest, and the Fund says so as a rule** — *"A QLICI that
meets this commitment will also automatically meet the commitment made in
Question 25(a)"* (Application, Q25(b)(i) Question Notes, printed p. 41). The
20% is carved out of the
85%, never added to it. The package's two flags happen to nest the same way —
re-derived over all 85,395 rows this session, `deep_distress` is a **strict
subset** of `severe_distress`: **8,061 deep-and-severe, 0 deep-and-not-severe,
13,121 severe-and-not-deep**, against **21,182** severe-flagged. That is a fact
about two columns, not the reason the commitments nest; do not offer it as one.

**So: never state or imply that a CDE meets, clears, is on track for, or fails
either commitment on the basis of anything these packages return** — not from one
tract, not from a batch of tracts, and above all not from a *percentage of
tracts*, which is a share of the wrong thing. Answer what the lookup answers:
**whether a QLICI made in this tract would be an area-qualifying one**, on the
routes the package can see, and say which route. Then direct the user to their
**own QLICI dollar amounts**, scored against the full Q25 area list — and be
clear what that arithmetic is *for*: deciding what to commit to, and meeting the
commitment once made. It is not an entry on the form. Q25(a) takes a Yes or a
No.

## Worked example — address eligibility (executed)

```python
import nmtcmapper as nm

m = nm.NMTCMapper()
result = m.check_address("2400 Grand Concourse, Bronx, NY 10458")
result.summary()          # prints a formatted block; returns None
print(result.eligibility_status)   # -> 'verified-eligible'
```

Actual output this session (nmtc-mapper **0.6.0** from PyPI, live Census
geocoder; the CDFI Fund workbook was the Aug-2025b edition read from a
pre-existing `~/.nmtcmapper/cache/`, because **the URL 0.6.0 pins no longer
serves it** — see the dated note under Data dependencies & fragility — 85,395
tracts, 8,764 OZ tracts and 85,529 OZ 2.0 tracts loaded). Every line that this
block showed on 0.5.0 re-executed **unchanged**; **the two trailing lines are
the ones 0.6.0 added**, and that is the release:

```
NMTC Eligibility Result
==================================================
  Address:          2400 Grand Concourse, Bronx, NY 10458
  Census Tract:     36005023702
  NMTC Eligible:    ✅ YES
  Distress Level:   SEVERE
  Description:      Severe Distress — qualifies for 85% investment commitment

  Poverty Rate:     32.1%
  AMI Ratio:        53.2%
  Unemployment:     10.7%
  Non-Metro:        No
  Opportunity Zone: ❓ NOT CONFIRMED — not on the 2018 designation list, which is
                    2010-tract-based (indeterminate, NOT "not an Opportunity Zone")
  High Migration:   No
  OZ 2.0 Eligible:  ✅ YES — eligible to be NOMINATED as a 2027 QOZ (not designated;
                    no tract is designated yet)
  Rural-Area QOZ:   ❌ NO — eligible, but not comprised entirely of a rural area
```

`eligibility_status` is `verified-eligible`. Tract `36005023702` verified
**present** in the live 2016–2020 table this session.

**The two `OZ 2.0` lines are new in 0.6.0 and this skill does not yet document
them.** They come from Treasury's Opportunity Zone 2.0 nomination-eligibility
file (a second table on a second scheme, held separately from the eligibility
table) and are carried on the result as `is_oz2_nomination_eligible`,
`is_rural_area_qoz_eligible`, `oz2_nomination_status` and `oz2_inputs_missing`.
Quote the two lines as the package printed them and do not interpret them
beyond that until a later revision of this skill carries their methodology
(`nmtcmapper/methodology/oz2_nomination_eligibility.md` in the installed
package).

**The `Description:` line is the package's own string, reproduced verbatim — read
it through the commitment-basis rule.** `DISTRESS_LEVELS["severe"]` reads
*"qualifies for 85% investment commitment"*; what the flag establishes is
narrower than that, and has no quotient anywhere in it: **a QLICI made in tract
`36005023702` would satisfy item 1 of the Q25(a) area list** — one of the five
single-item routes by which a QLICI can be an area-qualifying one. Whether to
commit to the 85% is a **Yes/No the CDE answers for itself**, and no percentage
is filed for it. A tract does not "qualify for" a commitment — a
CDE makes one, over its own QLICI dollars, and nothing in this result speaks to
that share. Quote the line as the package's label; say what it means in your own
words alongside it, and never carry it forward as the skill's own claim.

**The `Opportunity Zone` line may now be reported as printed — that is the point
of 0.5.0.** Through 0.4.3 `summary()` printed a bare `Opportunity Zone: No` here
and this skill's job was to *re-narrate* it, because `is_opportunity_zone` was a
plain `bool` and a `False` could not distinguish not-designated from a 2010/2020
vintage miss. The package now carries the qualifier itself: executed this
session on 0.5.0, `36005023702` returns `is_opportunity_zone is None` and
`opportunity_zone_status == 'not-confirmed'`. **Report it as "not confirmed as
an Opportunity Zone"** — which is what the line says. Still never write "not an
Opportunity Zone": the underlying ambiguity has not gone away, it has been made
visible. The qualifier is printed **inline on the same line**, so quoting the
line alone carries it; do not strip the second line when copying.

The `EligibilityResult` fields (read these, don't re-derive): `address`,
`tract_id`, `nmtc_eligible` (**`Optional[bool]` — True / False / None**),
`distress_level` (str: `'deep'`, `'severe'`, `'lic'`, `'ineligible'`,
`'unknown'`), `poverty_rate`, `ami_ratio`, `unemployment_rate` (each
`Optional[float]` with **two** kinds of missing — see the tri-state section),
`is_non_metro`, `is_high_migration_rural`, `severe_distress`, `deep_distress`
(**all four `Optional[bool]` as of 0.5.0**), `geocode_success` (plain `bool`),
`is_opportunity_zone` (**`Optional[bool]` — `True` or `None`, never `False`**),
and **`tract_found`** (bool, 0.4.0 — `False` when the tract is absent from the
table). Properties: `distress_description` (plain-English line, e.g. *"Severe
Distress — qualifies for 85% investment commitment"*), **`eligibility_status`**
(the five-way string above; its vocabulary is `ELIGIBILITY_STATUS_VALUES`, 0.6.0)
and **`opportunity_zone_status`** (0.5.0 — the
three-way string `designated` / `not-confirmed` / `no-tract`; see the OZ rule
below).

**`distress_description` returns `DISTRESS_LEVELS[distress_level]` verbatim, and
both distress strings assert more than the flag behind them carries.** The
`severe` string names the 85% commitment without its QLICI-dollar denominator and
without the *"and/or multiple indicia"* alternative route — see the
commitment-basis rule. The `deep` string, *"Deep Distress — highest need,
strongest NMTC application score"*, asserts a **scoring outcome** the package
cites no source for; there is a real Q25(b) Deep Distress commitment worth points,
but that is not what this string says and this package does not establish it.
Quote either property if you quote it, and qualify it on the adjacent line — do
not restate either claim in the skill's own voice, and do not paraphrase a
package constant into prose.

**`is_high_migration_rural` is the field that exposes a stale install.** It is
one of the three routes to LIC status (§45D(e)(5)), and pre-0.4.2 the package
surfaced it while excluding it from the verdict — see the install note. On a
pre-0.4.2 install one of three things happens, and **all three mean the
eligibility verdict is wrong or absent**: on a **cold start** it never gets a file
at all — the URL it pins was retired on 2026-09-03 and answers **403**, so it
raises `EligibilityDownloadError` before any header is read; from a **warm cache**
holding the **July-2026** workbook it reaches the header guard and raises
`EligibilitySchemaError` at column index 2, returning nothing; from a cached
**pre**-July-2026 workbook it returns `is_high_migration_rural=True` alongside
`nmtc_eligible=False` — a result contradicting itself. The remedy for all three is
the same: **upgrade to the `>=0.6.1` floor.** Check it with tract
**`01013953500`**, the first of the 168 — on **0.6.1**, against the Fund's
September-2026 file, it returns `nmtc_eligible=True`,
`is_high_migration_rural=True`, `distress_level='lic'`,
`eligibility_status='verified-eligible'`. **That expectation is derived from
0.6.1's pinned constants and test fixtures, not re-executed** — this session has
no route to `cdfifund.gov`, so treat it as a prediction the package should
satisfy rather than a recording. It is derivable because 0.6.1's own fixture
records the tract as Butler County AL, non-metro, poverty 15.0%, MFI 0.8377:
that fails both the ≥20%-poverty and ≤80%-AMI prongs, which is what puts it in
the (80%, 85%] §45D(e)(5) band, and at 83.77% it sits at MFI ≤ 85% — inside the
1,318 the September file keeps, not the 104 it dropped, every one of which is at
MFI ≥ 85.7%. If the four values do not come back, that is a finding worth
reporting, not a stale note.
The pre-0.4.2 load failure is **derived, not
executed**: read from the `nmtc-mapper` 0.4.1 sdist on 2026-09-14,
`download_eligibility_file()` raises `EligibilityDownloadError` on the retired
URL's 403 and returns before `_validate_xlsb_header()` can run, so a cold start
today fails at the download. The `EligibilitySchemaError` naming column index 2's
renamed header is what 0.4.1 did against the **July-2026** workbook while it was
served, and what it still does from a warm cache holding that file.

**`is_nmtc_native_area` was REMOVED in 0.5.0 — and Native Area status cannot be
determined from this package at all.** Through 0.4.3 the field existed and was
`False` for all 85,395 tracts (`True` count 0), because nothing in the `.xlsb`
ever populated it; reading it now raises `AttributeError` on a result and
`KeyError` on an enriched frame, which is deliberate — a field that can only
ever say "I don't know" invites a reader to treat the absence of `True` as
meaningful, and failing loud is safer than failing silent.

**State the absence; do not fill it.** If a user asks whether a tract is in an
NMTC Native Area, the honest answer is that **this lookup cannot tell them** —
not "no," and not an inference from the tract's location or name:

- **The CDFI Fund publishes no tract-keyed NMTC Native Areas resource.** Its
  April 2025 *NMTC Compliance & Monitoring FAQs* Q31 enumerates the eleven
  resources it links for determining Area-of-Higher-Distress status, and Native
  Areas is not among them. The Fund's CIMS map service does carry tract-level
  native-area *qualification* layers — but for Native Initiatives and the Bank
  Enterprise Award, not for NMTC; the NMTC layer family has no native-area
  member. So this is narrower than "no source exists": the Fund has published a
  tract-keyed native-area determination **for two other programs and not for
  this one.**
- **The criterion is live, so "unknown" is not the same as "irrelevant."** The
  same FAQ's **Q32** names *"NMTC Native Areas: Federal Indian Reservations,
  Off-Reservation Trust Lands, Hawaiian Home Lands, and Alaska Native Village
  Statistical Areas"* as one of the **Areas of Deep Distress** criteria added in
  the CY 2024–2025 Application. A deal may genuinely qualify on it; this package
  simply cannot say so.
- **It is a spatial determination, not a join.** Those four classes are Census
  **AIANNH** legal geographies. Their GEOIDs are four-digit AIANNH codes with
  **no state or county component** (e.g. `2430`, Navajo Nation, which itself
  spans three states), while a tract GEOID is `SSCCCTTTTTT`. An identifier that
  carries no state cannot nest into the state→county→tract chain, so the answer
  requires a polygon intersection of TIGER/Line AIANNH shapefiles against tract
  shapefiles — plus a coverage rule (any overlap? centroid? majority land?) that
  **the Fund has not published for NMTC.** Any answer this package gave would be
  inventing that rule.

Route the user to the CDFI Fund's **CIMS** and to the Application/Compliance FAQ
for the criterion, and say plainly that the mapper does not carry it.

Note `.summary` is a **method** — call `result.summary()`. `result.summary`
alone returns the bound method object, not the text.

## Worked example — verified-ineligible tract + the NaN honesty rule (executed)

A tract that is **present in the table with an explicit NO flag** — distinct
from an absent tract (next example). Verified this session: `11001980000` **is**
one of the 85,395 rows, flagged not-eligible, with null (NaN) poverty and
income. The CDFI Fund documents several reasons a tract carries null
demographics: per its *2016-2020 ACS Data FAQ* (updated Feb 1, 2024;
`NMTC_LIC_FAQs_2020_ACS_Sept1_2023_Update_Jan2024.pdf`, General Q2), the Census
Bureau could not estimate income or poverty for such tracts —
a significant majority have no or very low population, and the remainder's
population is largely in **group quarters** (e.g. prisons, college dormitories),
which the ACS excludes from income and poverty calculations. Which of those
applies to `11001980000` is not something this lookup reports, so do not assert
it.

```python
import nmtcmapper as nm
m = nm.NMTCMapper()
r = m.check_tract("11001980000")   # present, explicit NO, null demographics
print(r.nmtc_eligible, r.distress_level, r.poverty_rate, r.ami_ratio)
print(r.eligibility_status, "| tract_found:", r.tract_found)
```

Actual output this session (0.6.0):

```
False ineligible nan nan
verified-ineligible | tract_found: True
```

`poverty_rate` and `ami_ratio` came back **NaN** — the Fund does not publish an
income or poverty estimate for this tract (see the FAQ Q2 reasons above) —
render them "not available," never invent a number. **As of 0.5.0 `summary()`
does this for you**, and says which kind of missing it is; `r.summary()` on this
tract prints (executed this session on 0.6.0, whole block):

```
NMTC Eligibility Result
==================================================
  Address:          Census Tract 11001980000
  Census Tract:     11001980000
  NMTC Eligible:    ❌ NO
  Distress Level:   INELIGIBLE
  Description:      Not NMTC eligible

  Poverty Rate:     not available — the CDFI Fund published no value for this tract
  AMI Ratio:        not available — the CDFI Fund published no value for this tract
  Unemployment:     0.0%
  Non-Metro:        No
  Opportunity Zone: ❓ NOT CONFIRMED — not on the 2018 designation list, which is
                    2010-tract-based (indeterminate, NOT "not an Opportunity Zone")
  High Migration:   No
  OZ 2.0 Eligible:  ❌ NO — not an eligible LIC on the 2020-2024 ACS / 2020 DECIA
                    inputs Treasury used
  Rural-Area QOZ:   ❓ NOT DETERMINED — Treasury determines rural status only for
                    ELIGIBLE tracts, and this tract is not one
```

Through 0.4.3 those two lines rendered as `nan%` for all 1,583 poverty / 2,358
AMI tracts in this state. Note the wording is deliberately **different** from
the `❓ UNKNOWN — tract not read` that the indeterminate branches print: this
tract *was* read and the Fund *did* publish a verdict for it, and only the
metric is absent. Do not collapse the two into one word.
`nmtc_eligible=False` / `eligibility_status='verified-ineligible'` /
`tract_found=True` is a **real NO from the table** — the answer *is*
ineligible. This is NOT the third state; contrast the next example, where the
tract is absent and the honest answer is "unknown."

## Worked example — the third state: an ABSENT tract (executed)

The teaching case for `None`/`"unknown"`. A syntactically valid GEOID that is
**not in the 2016–2020 universe** (a mistyped tract, or one from a different
vintage). Verified absent this session: `36061980000` is **not** among the
85,395 rows.

```python
import nmtcmapper as nm
m = nm.NMTCMapper()
r = m.check_tract("36061980000")   # a tract ABSENT from the 2016-2020 universe
print(r.nmtc_eligible, r.distress_level, r.eligibility_status, r.tract_found)
r.summary()
```

Actual output this session (0.6.0):

```
None unknown not-found False
```

```
NMTC Eligibility Result
==================================================
  Address:          Census Tract 36061980000
  Census Tract:     36061980000
  NMTC Eligible:    ❓ UNKNOWN — tract not in eligibility table (indeterminate, NOT ineligible)
  Distress Level:   UNKNOWN
  Description:      Indeterminate — eligibility not verified (no match / tract absent)

  Poverty Rate:     ❓ UNKNOWN — tract not read
  AMI Ratio:        ❓ UNKNOWN — tract not read
  Unemployment:     ❓ UNKNOWN — tract not read
  Non-Metro:        ❓ UNKNOWN — tract not read
  Opportunity Zone: ❓ NOT CONFIRMED — not on the 2018 designation list, which is
                    2010-tract-based (indeterminate, NOT "not an Opportunity Zone")
  High Migration:   ❓ UNKNOWN — tract not read
  OZ 2.0 Eligible:  ❓ NOT DETERMINED — tract absent from Treasury's 85,529-row universe
  Rural-Area QOZ:   ❓ NOT DETERMINED — tract absent from Treasury's universe
```

**This block is why the floor moved to `>=0.5.0`.** On 0.4.3 the same call
printed `Non-Metro: No`, `Opportunity Zone: No` and `High Migration: No`, and
omitted the three demographic lines entirely — three fabricated negatives and
three silent omissions sitting directly underneath a correct `❓ UNKNOWN`
verdict, in the skill's own teaching case for the third state. Every one of
those lines now qualifies itself inline, so the block can be pasted whole.

Report this as: *"NMTC eligibility could not be determined for tract
36061980000 — it is absent from the 2016–2020 eligibility universe."* Do **not**
report it as "not eligible." The `Description` line —
*"Indeterminate — eligibility not verified (no match / tract absent)"* — is the
verbatim value of `DISTRESS_LEVELS["unknown"]` in
`nmtcmapper/data/schema.py`.

**The program administrator documents this exact case — it is not just a
first-principles argument.** The CDFI Fund's *2016-2020 ACS Data FAQ* (updated
Feb 1, 2024; `NMTC_LIC_FAQs_2020_ACS_Sept1_2023_Update_Jan2024.pdf`, **Q10**,
*"I can't find a 2010 census tract in the 2016-2020 ACS Low-Income Community
data. Where is it?"*) explains
that the 2011–2015 data is built on **2010** census tracts and the 2016–2020
data on **2020** tracts, and that as part of the 2020 census the Bureau
**eliminated certain 2010 tracts and folded their land into new tracts** — so a
tract absent from this table is a **vintage artifact, not an ineligibility
finding**. The FAQ routes the reader to the Census Bureau tract-relationship
files and to CIMS for geocoding; do the same rather than reporting "not
eligible."

The same third state reaches you from `check_address` when an address does not
geocode. Executed this session on 0.6.0 against the live Census geocoder with a
deliberately unresolvable address:

```python
r = m.check_address("99999 Nonexistent Street, Nowhereville, ZZ 00000")
print(r.nmtc_eligible, r.distress_level, r.eligibility_status, r.opportunity_zone_status)
r.summary()
```

```
None unknown geocode-failed no-tract
```

```
NMTC Eligibility Result
==================================================
  Address:          99999 Nonexistent Street, Nowhereville, ZZ 00000
  Census Tract:     Not found
  NMTC Eligible:    ❓ UNKNOWN — address could not be geocoded (indeterminate, NOT ineligible)
  Distress Level:   UNKNOWN
  Description:      Indeterminate — eligibility not verified (no match / tract absent)

  Poverty Rate:     ❓ UNKNOWN — tract not read
  AMI Ratio:        ❓ UNKNOWN — tract not read
  Unemployment:     ❓ UNKNOWN — tract not read
  Non-Metro:        ❓ UNKNOWN — tract not read
  Opportunity Zone: ❓ UNKNOWN — no census tract resolved
  High Migration:   ❓ UNKNOWN — tract not read
  OZ 2.0 Eligible:  ❓ UNKNOWN — no census tract resolved
  Rural-Area QOZ:   ❓ UNKNOWN — no census tract resolved
```

On this branch `opportunity_zone_status == 'no-tract'` (0.5.0) — through 0.4.3
it hardcoded `is_opportunity_zone=False`, asserting a non-designation about an
address that never resolved to a tract. It is the third of the three OZ states
and the only one that is *not* "not-confirmed."

## Worked example — the fifth state: a territory tract (executed)

The teaching case for `not-covered-territory`. Guam's state FIPS is 66; the
GEOID is well-formed and 11 digits, and the answer is not "unknown" — it is
"this table does not cover Guam."

```python
import nmtcmapper as nm
m = nm.NMTCMapper()
r = m.check_tract("66010950100")   # Guam — outside the loaded table's universe
print(r.nmtc_eligible, r.distress_level, r.eligibility_status, r.tract_found)
r.summary()
```

Actual output this session (0.6.0):

```
None unknown not-covered-territory False
```

```
NMTC Eligibility Result
==================================================
  Address:          Census Tract 66010950100
  Census Tract:     66010950100
  NMTC Eligible:    🚫 NOT COVERED — Guam is outside the 2016-2020 ACS
                    NMTC LIC table this package loads (50 states + DC + PR).
                    Territory LIC status is published separately, in the CDFI Fund's
                    "New Markets Tax Credit Low-Income Community Census Tracts (2020 Island Areas Decennial Census)"
                    file. This package does not load it.
  Distress Level:   UNKNOWN
  Description:      Not covered — outside this table's universe, NOT a lookup miss

  Poverty Rate:     ❓ UNKNOWN — tract not read
  AMI Ratio:        ❓ UNKNOWN — tract not read
  Unemployment:     ❓ UNKNOWN — tract not read
  Non-Metro:        ❓ UNKNOWN — tract not read
  Opportunity Zone: ❓ NOT CONFIRMED — not on the 2018 designation list, which is
                    2010-tract-based (indeterminate, NOT "not an Opportunity Zone")
  High Migration:   ❓ UNKNOWN — tract not read
  OZ 2.0 Eligible:  ✅ YES — eligible to be NOMINATED as a 2027 QOZ (not designated;
                    no tract is designated yet)
  Rural-Area QOZ:   ✅ YES — Treasury determined this eligible tract is comprised
                    entirely of a rural area
```

Report this as: *"nmtc-mapper does not cover Guam — tract 66010950100 is
outside the 2016–2020 ACS LIC table it loads. Its LIC status is in the CDFI
Fund's separate 2020 Island Areas Decennial Census file; determine it there or
in CIMS."* Not "could not be found," not "unknown," and never "ineligible."
The `Description` line is the verbatim value of `NOT_COVERED_DESCRIPTION` in
`nmtcmapper/eligibility/checker.py`, selected by `distress_description` on
`eligibility_status` rather than on `distress_level` — which stays `"unknown"`,
because a coverage boundary is not a distress finding. Note the last two lines:
Treasury's OZ 2.0 universe (85,529 rows) *does* include the 133 Island Area
tracts, so the same GEOID this table cannot see is answered on the OZ 2.0 side
— two tables, two universes, and the skill does not yet document the second.

## Input shape — a GEOID is the 11-digit, zero-padded string (0.6.0 does not normalize)

`check_tract` and the `tract_col` path of `enrich` take the tract GEOID as the
**11-character, zero-padded string** `SSCCCTTTTTT` — `"06037101110"`, not
`"6037101110"` and not the int `6037101110`. The package applies **no
normalization** (0.6.0's own Known-limitations entry says so and defers
`zfill` to 0.7.0), and both of its internal tables are keyed on the padded form.
So the leading-zero-stripped shape — **which is the shape Excel, CSV readers and
`int` columns emit for every state whose FIPS begins with 0** (AL 01, AK 02,
AZ 04, AR 05, CA 06, CO 08, CT 09) — misses the table and comes back
`not-found`. It fails safe (`nmtc_eligible is None`, never a fabricated
`False`), but it is a wrong "unknown" for a tract the table actually has.
Executed this session on 0.6.0 against the live table:

```
"06037101110" -> verified-ineligible   nmtc_eligible=False  tract_found=True
"6037101110"  -> not-found             nmtc_eligible=None   tract_found=False
6037101110    -> not-found             nmtc_eligible=None   tract_found=False
```

Same tract, three spellings, and only the padded one reaches the row. **Pad it
yourself before calling: `str(geoid).zfill(11)`**, and on a DataFrame
`df[tract_col] = df[tract_col].astype(str).str.zfill(11)` before `enrich`. When
a user hands you a `not-found` for a GEOID that is 10 digits long, or a GEOID
that came out of a spreadsheet, re-run it padded before reporting "could not
be determined" — that `None` was an input-shape artifact, not a lookup result.

**0.6.0 also closed the other half of this defect: a stripped GEOID is never
mistaken for a territory.** A stripped California id begins with `60`, which is
American Samoa's FIPS; only a well-formed 11-digit GEOID can carry a
`not-covered-territory` claim (executed this session: `"6037101110"` returns
`not-found`, not `not-covered-territory`). So `not-covered-territory` is
trustworthy as a territory statement, and `not-found` on a short id should make
you check its length first.

## Worked example — project feasibility screen (executed)

```python
import nmtc_screener as ns

r = ns.run_screening(
    project_name="Maple Street Grocery",
    location="Bronx, NY (Tract 36005023702)",
    total_project_cost=8_500_000,
    project_type="commercial",
    annual_revenue=3_200_000,
    lic_status="yes",          # accepted: "yes" | "unknown" | (anything else = treated as not-LIC)
)
print(r.qualification_likelihood, r.qualification_score)
```

Actual output this session (nmtc-screener 0.1.0):

```
HIGH 95
```

`qualification_reasons` (actual):

```
Project is in a confirmed Low Income Community census tract (+35 pts)
Project type 'Other': Eligibility depends on specific business activities and community benefit. (+10 pts)
Project cost ≥$5MM — meets minimum viable deal size (+5 pts)
Revenue ($3,200,000/yr) covers estimated debt service at 1.25x DSCR (+5 pts)
```

Note: the screener does not currently map project_type='commercial' to a
specific category — it scores it as 'Other' (+10 pts), so this component of the
score is type-agnostic; treat the result as a first-pass heuristic, not
underwriting.

`run_screening` signature (positional or keyword): `run_screening(project_name,
location, total_project_cost, project_type, annual_revenue, lic_status)`. The
`ScreeningResult` also carries `estimated_allocation`, `transaction_result`,
`credit_result`, `subsidy_result`, and a `plain_english_summary`.

**`lic_status` is the user's assertion, not a lookup.** If the user has not
confirmed LIC status, either run `nmtcmapper` first and pass the real answer, or
pass `"unknown"` — do not pass `"yes"` on assumption. And if the mapper returned
the **third state** (`None`/`"unknown"`), pass `"unknown"` to the screener —
never `"yes"`, and never `"no"`, because you do not know. The screener's score
is only as honest as this input.

## Output-presentation rules

- Always report the **census tract ID** alongside any eligibility verdict — it
  is the unit the answer is actually about — and, for an indeterminate result,
  name the tract (or state the address did not geocode) as part of the "could
  not be determined" answer.
- State the **eligibility table vintage** (below) so the user knows what the
  answer is current as of.
- Render NaN/None demographic fields as "not available," never as a number —
  and keep the two apart: **`NaN` on a found tract** is "the CDFI Fund published
  no value for this tract" (the verdict is still real), while **`None`** is
  "tract not read" (no verdict at all). 0.5.0's `summary()` prints those two
  sentences for you; quote what it printed rather than flattening both to
  "N/A".
- Report a `None`/`"unknown"` eligibility verdict as "could not be determined,"
  never as "not eligible." (See the third-state rule.)
- Distinguish the mapper's *tract-eligibility lookup* (authoritative table
  lookup) from the screener's *feasibility score* (a heuristic first pass).
- **Never render a distress flag as a share of anything.** A count or percentage
  of *tracts* is not the 85% or the 20% commitment, which are shares of a CDE's
  QLICI **dollars**. If you are about to divide, re-read the commitment-basis
  rule — that is the substitution it exists to stop.
- **OZ status is asymmetric, and as of 0.5.0 the package says so itself — read
  `opportunity_zone_status`, not the boolean.** NMTC eligibility and OZ status
  are independent, so report OZ separately either way. The property is a
  three-way string and each value has exactly one honest rendering:

  | `opportunity_zone_status` | `is_opportunity_zone` | report it as |
  |---|---|---|
  | `designated` | `True` | **"a designated Opportunity Zone"** — may be stated as fact |
  | `not-confirmed` | `None` | **"not confirmed as an Opportunity Zone"** — never "not an Opportunity Zone" |
  | `no-tract` | `None` | **"unknown — no census tract was resolved"** (the address did not geocode) |

  **`is_opportunity_zone` is `Optional[bool]` and a `False` is never
  returnable** — so the caveat is now carried by the type and by `summary()`'s
  printed line, and **you must no longer add it by hand.** Report the line as
  printed. Two traps follow from that. First, **`None` is falsy**, so an
  `if r.is_opportunity_zone: … else: …` written against 0.4.3 still runs, but its
  else-branch quietly stops meaning "not designated" and starts meaning "not
  designated **or** unknown" — switch on `opportunity_zone_status` instead.
  Second, `not-confirmed` must not be re-narrated as a soft "no": *"probably not
  an OZ"* is the same fabrication the type change removed, re-added in prose.

  **Why the package refuses a `False`** (the reason still matters even though
  the skill no longer has to enforce it): OZs were designated in Dec 2018 on
  **2010** census tracts, while this table and the geocoder are **2020**-basis,
  so a genuine non-designation and a vintage miss are *the same observation*
  without a crosswalk. Re-derived directly against the live 0.5.0 load this
  session, not carried forward from the 0.4.2 session: the OZ file is **8,764
  designated tracts**, of which **7,356 have a row in the 85,395-row 2020-basis
  table and 1,408 (16.1%) do not.**

  **What the 1,408 counts has changed, and the old sentence around it is
  retired.** On 0.4.3 it was quoted as the size of a harm — designations the
  package would answer "No" about. It never was that: through 0.4.3 the confident
  `False` fell on **78,039 tracts** (every row in the table outside the
  designation set) plus every unresolved address, while the 1,408 measured
  something different — **how much of the designation list is unreachable from a
  2020 GEOID at all.** That is the number that still means something at 0.5.0,
  and it now sizes the **not-confirmed** population rather than a fabricated
  negative: it is why a `not-confirmed` cannot be read as a "no." Of the 1,408,
  **75 are Island Area tracts** (AS 16, GU 25, MP 20, VI 14) that are outside
  this table by scope rather than by vintage — see the Island Areas paragraph in
  the vintage-scope rule — and the remaining **1,333 are 2010→2020 vintage
  misses.** So `not-confirmed` has three possible causes the package cannot
  separate: genuinely not designated, a vintage miss, or an Island Area outside
  this table. (As of 0.6.0 the third cause is at least visible on the
  *eligibility* side — `eligibility_status` says `not-covered-territory` for
  those GEOIDs — while `opportunity_zone_status` is unchanged, still keyed on
  designation-set membership alone: executed this session, `60010950100`
  (American Samoa) is `not-covered-territory` **and** `designated`, and
  `66010950100` (Guam) is `not-covered-territory` and `not-confirmed`. The two
  properties answer different questions and neither one settles the other.)
  Same posture as the third-state rule — an unknowable negative is not a
  negative.

## Data dependencies & fragility (must document)

- **Census geocoder** — `geocode_address()` / `check_address()` call
  `geocoding.geo.census.gov`. This host has **no cloud WAF**, so it works from
  cloud/datacenter IPs (unlike the CRA/Cloudflare-blocked hosts elsewhere in the
  portfolio). Verified working this session (geocoded 2400 Grand Concourse to
  tract `36005023702`).
- **CDFI Fund eligibility table** — `load_eligibility_table()` downloads the
  NMTC LIC eligibility workbook from cdfifund.gov and caches it under
  `~/.nmtcmapper/cache/`. **CDFI Fund URLs move**: the Fund relocates these files
  periodically, so a download can fail even though the package is fine. On
  failure the loader now **raises** `EligibilityDownloadError` /
  `EligibilityParseError` (0.3.4+) rather than silently substituting demo data —
  **say the lookup failed and why; never guess eligibility.** (For offline
  demos only, `NMTCMapper.from_sample()` exists and stamps `data_source ==
  "sample"`; its 12 synthetic tracts are NEVER valid for a real answer.)

  **It moved on 2026-09-03, and `nmtc-mapper` 0.6.1 is the release that follows
  it (verified 2026-09-14).** The URL every release **through 0.6.0** pins —
  `…/system/files?file=2025-08/NMTC_2016-2020_Severe_Deep_Distress_August-2025b.xlsb`
  — began returning **403** (a Drupal access-denied page; the host itself is
  200) when the Fund replaced that workbook with
  `…/system/files?file=2026-09/NMTC_LIC_Eligibility_Dataset_9_3_2026.xlsx`. On a
  fresh 0.6.0 install with an empty `HOME`, `NMTCMapper()` raises
  `EligibilityDownloadError` (*"access blocked (403 Forbidden)"*) and answers
  nothing — 0.4.3, 0.5.0 and 0.6.0 all pin the same dead literal, so **no
  release before 0.6.1 can cold-load the eligibility table at all.**

  **The durable lesson is the status code: a relocated CDFI Fund file answers
  403, not 404.** A moved file does not announce itself as missing — it looks
  like a blocked client, which invites the wrong diagnosis (user agent, proxy,
  WAF) and hides a dead pin. A warm `~/.nmtcmapper/cache/` hides it further, on
  every machine that already has one. Expect the Fund to do this again.

  **The remedy is `pip install -U nmtc-mapper`, not a hand-pointed URL.** 0.6.1
  (PyPI, 2026-09-14) retargets the loader to the replacement and chooses its
  parser by sniffing the ZIP member list rather than trusting the URL's
  extension, so the `.xlsb` → `.xlsx` flip needs no further release. If a user
  reports `EligibilityDownloadError` naming a 403, tell them to upgrade; that is
  why this skill's floor is `>=0.6.1`. Still report the error verbatim, per the
  hard failure rule, and never guess eligibility around it. (This session read
  the retarget from 0.6.1's own `CDFI_FUND_LIC_URL_2020` and
  `ELIGIBILITY_CACHE_FILENAME`; it has no route to `cdfifund.gov` and did not
  re-run the download. Note also that 0.6.1 does a plain cold download on
  upgrade rather than reusing the `.xlsb` cache — the cache filename changed.)
- **Tract vintage in force (verified this session):** the cached table is
  `NMTC_LIC_Eligibility_2016_2020.xlsb`, **85,395 census tracts**, sourced from
  the CDFI Fund's Aug-2025b Severe/Deep Distress release. As of 0.5.0 the
  loaded frame is indexed on `tract_id` and carries **exactly nine** normalized
  columns — `nmtc_eligible`, `distress_level`, `poverty_rate`, `ami_ratio`,
  `unemployment_rate`, `is_non_metro`, `is_high_migration_rural`,
  `severe_distress`, `deep_distress` (verified this session against the live
  load). A tenth, `is_nmtc_native_area`, was carried through 0.4.3 and **was
  dropped in 0.5.0**; it never held a `True` and no column of the `.xlsb` ever
  populated it — see the note under the field list. This is a
  2016–2020 ACS-based vintage. Per the CDFI Fund's transition rules this vintage
  became **usable as of Sept 1, 2023** and is **mandatory for QLICIs closing
  on/after Sept 1, 2024** (primary: CDFI Fund, *2016-2020 ACS Data FAQ*, updated
  Feb 1, 2024 — `NMTC_LIC_FAQs_2020_ACS_Sept1_2023_Update_Jan2024.pdf` at
  `cdfifund.gov/system/files/2024-01/`, announced at `cdfifund.gov/news/567`;
  secondary, stating the mandatory date plainly: NMTC Coalition,
  `nmtccoalition.org/2023/09/06/new-nmtc-data`). This package carries **only**
  this vintage — see the vintage-scope rule above before answering for any deal
  whose QLICI closed before Sept 1, 2024. Report the vintage with the answer;
  the CDFI Fund periodically re-bases eligibility, and a deal must be checked
  against the vintage in force at its QLICI close date. 0.4.0 validates this
  structure at load
  (`EligibilitySchemaError` / `EligibilityValueError`) before trusting any row,
  because the loader binds columns positionally. **0.5.0 adds a second guard the
  first one structurally cannot provide:** the header check pins header
  *strings*, so a re-publish that leaves every header byte-identical and rewrites
  a *cell value* passes it completely — and the `== "YES"` tests would then map
  the unrecognized value to `False`, a fabricated negative on the LIC verdict and
  on both distress flags. Each categorical cell is now checked against a per-column
  value allowlist and raises `EligibilitySchemaError` instead. Nothing about this
  changes what you report; it changes what the package will do rather than answer
  from a layout it does not recognize.
- **Geocoder vintage is bound to the table (0.4.1).** 0.4.1 pins the Census
  geocoder to the eligibility table's 2020 tract basis (`schema.TRACT_VINTAGE`).
  0.4.0 and earlier geocoded at `Current_Current`, which since the 2022 ACS
  returns COG-based county FIPS for Connecticut while the CDFI Fund table keeps
  legacy county FIPS — so every CT address missed the lookup (883 tracts, 316
  eligible). Fixed in 0.4.1; noted here only as data-source fragility context.

## Failure modes

**Geocoder (0.4.0 splits the old single `None` return into four distinct
outcomes).** `geocode_address` / `check_address` now behave as follows. All
four re-executed this session against the installed **0.6.0** wheel and are
unchanged from 0.4.2: the no-match and agree branches ran against the live
Census endpoint (the two `check_address` examples above); the transport failure
was **induced** by pointing the geocoder URL at a closed local port, which
raised `GeocoderTransportError` (`connection/DNS`, *"after 4 attempts"*,
`isinstance NMTCMapperError == True`), message naming the failure kind and the
address; the disagree branch was **induced** by returning two matches on
different tracts, which raised `AmbiguousAddressError` naming both candidates
(`['36005023701', '36005023702']`) and stating it *"refus[es] to guess which is
correct."*

- **Transport / HTTP-status / decode failure** (403, 5xx, timeout,
  connection/DNS, non-JSON body), after retries are exhausted → **raises
  `GeocoderTransportError`**. The message names the failure kind and the address.
  Report it verbatim and stop.
- **Address matches multiple tracts that disagree** → **raises
  `AmbiguousAddressError`**, naming the candidate tracts; it refuses to silently
  take the first match. Report it and stop — do not pick one.
- **Genuine no-match** (HTTP 200, zero address matches) → **returns `None`**.
  This is the *only* thing `None` means now. It is the third state, not a NO:
  report "address could not be geocoded" / `eligibility_status='geocode-failed'`
  — do not fall back to a ZIP-code or city-level guess.
- **Matches that all agree on the same tract** → proceeds normally, returning
  that tract.

  Both `GeocoderTransportError` and `AmbiguousAddressError` subclass
  `GeocoderError`, which subclasses `NMTCMapperError` (verified by reflection
  this session) — so `except NMTCMapperError` catches every error the package
  raises. Source: `nmtcmapper/exceptions.py`, `nmtcmapper/geocoder/census.py`.

**Tract absent from the table** (`check_tract` on a GEOID not in the ~85k
universe): **not a failure** — it is the third state. Returns
`nmtc_eligible=None`, `distress_level="unknown"`, `tract_found=False`,
`eligibility_status="not-found"`, and **as of 0.5.0 every other tract-derived
field is `None` too** — `is_non_metro`, `is_high_migration_rural`,
`severe_distress`, `deep_distress`, and the three demographic rates. Report
"could not be determined," never "ineligible." (See the third-state rule and its
worked example.) **Check the id's length before reporting it**: a 10-digit id is
a leading-zero-stripped GEOID, and `not-found` on it is an input-shape artifact
— see the input-shape section.

**Tract in an Island Area** (`check_tract` on an 11-digit GEOID whose state
FIPS is 60, 66, 69 or 78): **not a failure and not a lookup miss** — the tract is
outside the loaded table's universe. Returns `nmtc_eligible=None`,
`distress_level="unknown"`, `tract_found=False`,
`eligibility_status="not-covered-territory"` (0.6.0), every other tract-derived
field `None`, and `summary()` prints `🚫 NOT COVERED — …` naming the
jurisdiction and the separate CDFI Fund Island Areas file. Report "this package
does not cover [jurisdiction]; determine it against CIMS or the CDFI Fund's
*2020 Island Areas Decennial Census* LIC file," never "ineligible" and never
"could not be found." Through 0.5.0 this case returned `not-found`.

**CDFI Fund file download fails / 404** (URL moved): raises
`EligibilityDownloadError` / `EligibilityParseError`. Report the error and that
eligibility could not be determined. Do not answer from memory.

**NaN demographic fields** (a real tract with no measurable population, e.g.
`11001980000`): report "not available," never fabricate. This is orthogonal to
the tri-state verdict — the tract is genuinely `False`/verified-ineligible; only
its demographics are null.

**Screener `lic_status` misuse**: passing `"yes"` without confirming LIC status
produces a falsely high score. Confirm first; pass `"unknown"` when the mapper
returned the third state.

## Caveats

- This is an **eligibility and feasibility screening layer**, not an allocation
  award, legal opinion, or the CDFI Fund's determination.
- Eligibility is **tract-specific and vintage-specific**. An "eligible" answer is
  only valid for the table vintage named above.
- An **"unknown" answer is a real answer** — "could not be determined for this
  tract/address," never "not eligible."
- A distress flag is a fact about a **tract**. The **85% and 20% commitments are
  facts about a CDE's QLICI dollars**, which this layer never sees — it cannot
  say whether any CDE meets either one. And **Question 25(a) collects no
  percentage at all** — it is a Yes/No — so there is no "Q25(a) percentage" for
  this or any tool to compute. (Commitment-basis rule.)
- The screener's score and estimated allocation are **first-pass heuristics** to
  triage deals, not underwriting or a commitment.
