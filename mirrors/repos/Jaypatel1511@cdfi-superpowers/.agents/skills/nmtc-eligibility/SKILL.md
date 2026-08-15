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
- "Does this tract qualify for severe distress / the 85% investment commitment?"
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
pip install "nmtc-mapper>=0.5.0" nmtc-screener
```

Verified 2026-08-14 (PyPI) against **`nmtc-mapper>=0.5.0`** (resolved 0.5.0 at
the time) and **nmtc-screener 0.1.0** (`nmtc-calc 0.2.1` is pulled in as a
dependency). Quote the floor, not the resolved point version — the point version
moves on every release and this line does not. The `>=0.5.0` floor is not
cosmetic — 0.4.0 is where `nmtc_eligible` became tri-state (see below), 0.4.1
binds the geocoder vintage to the eligibility table's 2020 tract basis (see Data
dependencies & fragility), **0.4.2 is the release that stopped reporting 168
statutorily-eligible tracts as ineligible**, and **0.5.0 is the release that
stopped returning a confident `False` for every unconfirmed Opportunity Zone and
for every field of a tract it never read.** A reader on 0.3.x following this
skill's third-state guidance would never see `None`, because 0.3.x collapses
"could not determine" into `False`.

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
`is_high_migration_rural`. Verified against the live table this session:
**1,422 tracts carry the high-migration-rural designation, and 168 of them fail
both the ≥20%-poverty and ≤80%-AMI prongs** — all non-metro, all in the
(80%, 85%] MFI band, so §45D(e)(5) is the only route by which they qualify.
Those 168 were reported ineligible by a package that was, in the same object,
reporting the evidence of their eligibility. 0.4.2 reads the verdict as **C or
N**. That is why no floor below 0.4.2 is defensible and none of this is
version-hygiene preference: 0.4.2 is the line below which this skill's central
rule is violated by its own dependency. (All four figures re-derived against the
live table on 0.5.0 this session, not carried forward: 1,422 HMR tracts, 168
failing both prongs, all non-metro, all in the (80%, 85%] band, and all 168 now
`nmtc_eligible=True`.)

**On the current workbook a pre-0.4.2 install does not answer at all.** The Fund
moved the C/N boundary in **July 2026**, folding the high-migration-rural route
into column C and renaming that column's header. 0.4.1 pins column C's exact
header string, so against the workbook the loader downloads today it raises
`EligibilitySchemaError` and loads nothing (executed this session). The 168-tract
divergence was real against the pre-July-2026 edition; today the same defect
presents as a hard load failure. Either way 0.4.2 is the release that reads
`C or N` and is therefore correct on both sides of the boundary move.

**The fourth reason is the same defect one field over, and it is why the floor
is now `>=0.5.0`.** Through 0.4.3 `is_opportunity_zone` was a plain `bool`, so
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
falsy `False`. A `None` reached two ways: the address did not geocode, or the
tract is absent from the ~85k-tract universe (a bad/mistyped GEOID, or a
vintage mismatch). Neither is a NO — both are "we don't know."

`EligibilityResult.eligibility_status` (property, 0.4.0) collapses this into one
explicit four-way string so you never have to infer intent from a `None`:

```
verified-eligible  |  verified-ineligible  |  not-found  |  geocode-failed
```

`not-found` and `geocode-failed` are the two indeterminate cases. `summary()`
prints indeterminate results as `❓ UNKNOWN — … (indeterminate, NOT ineligible)`
on the eligibility line itself — that inline qualifier is defined in
`nmtcmapper/eligibility/checker.py::EligibilityResult.summary`, not a footer.

### 0.5.0 extends the tri-state contract to every field that can be unobtainable

Through 0.4.3 only the verdict was tri-state, and its **neighbours fabricated
inside the very branches written to protect it**: the two indeterminate branches
set every supporting boolean to a confident `False` about a tract no row was
ever read for. **Six fields are `Optional[bool]` in 0.5.0:**

| field | `None` when |
|---|---|
| `nmtc_eligible` | either indeterminate branch (0.4.0) |
| `is_non_metro` | either indeterminate branch (0.5.0) |
| `is_high_migration_rural` | either indeterminate branch (0.5.0) |
| `severe_distress` | either indeterminate branch (0.5.0) |
| `deep_distress` | either indeterminate branch (0.5.0) |
| `is_opportunity_zone` | **on every path** — `True` or `None`, never `False` (0.5.0) |

**The rule that ties them together: when `eligibility_status` is `not-found` or
`geocode-failed`, every tract-derived field is `None`, because nothing was
read.** For a tract that *was* found, a `False` on the four supporting booleans
is unchanged and fully supportable — it is the Fund's published `NO`, present as
a strict YES/NO on all 85,395 rows. `is_opportunity_zone` is the exception in
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
geocode-failed}`). An unknown verdict is a **result, not an error** — and it
must be reported as its own answer:

- Report it as **"NMTC eligibility could not be determined for this tract"**,
  and **name the tract ID** (or state the address did not geocode). Say *why*:
  tract absent from the vintage's universe, or address failed to geocode.
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
outlined in question 3."* An Island Area address/tract that is absent here is
therefore **"not carried by this package," never "ineligible"** — route to CIMS
or to the separate territory file; do not answer it from this 2016–2020 ACS
table.

## Worked example — address eligibility (executed)

```python
import nmtcmapper as nm

m = nm.NMTCMapper()
result = m.check_address("2400 Grand Concourse, Bronx, NY 10458")
result.summary()          # prints a formatted block; returns None
print(result.eligibility_status)   # -> 'verified-eligible'
```

Actual output this session (nmtc-mapper **0.5.0**, clean-venv PyPI install, cold
cache, isolated `HOME`, live CDFI Fund + Census downloads — 85,395 tracts and
8,764 OZ tracts loaded). Every demographic and eligibility figure re-executed
**unchanged** from the revision of this file that recorded it on 0.4.2; **the
`Opportunity Zone` line is the one line that moved**, and that is the release:

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
```

`eligibility_status` is `verified-eligible`. Tract `36005023702` verified
**present** in the live 2016–2020 table this session.

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
(the four-way string above) and **`opportunity_zone_status`** (0.5.0 — the
three-way string `designated` / `not-confirmed` / `no-tract`; see the OZ rule
below).

**`is_high_migration_rural` is the field that exposes a stale install.** It is
one of the three routes to LIC status (§45D(e)(5)), and pre-0.4.2 the package
surfaced it while excluding it from the verdict — see the install note. On a
pre-0.4.2 install one of two things happens, and **both mean the eligibility
verdict is wrong or absent**: against the current workbook the loader raises
`EligibilitySchemaError` and returns nothing; against a cached pre-July-2026
workbook it returns `is_high_migration_rural=True` alongside
`nmtc_eligible=False` — a result contradicting itself. The remedy for both is
the same: **upgrade to the `>=0.5.0` floor.** Check it with tract
**`01013953500`**, the first of the 168 — on 0.5.0 it returns
`nmtc_eligible=True`, `is_high_migration_rural=True`, `distress_level='lic'`
(re-executed this session). The pre-0.4.2 load failure was re-executed too: a
0.4.1 install against the workbook the Fund serves today raises
`EligibilitySchemaError` naming column index 2's renamed header, and loads
nothing.

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

Actual output this session (0.5.0):

```
False ineligible nan nan
verified-ineligible | tract_found: True
```

`poverty_rate` and `ami_ratio` came back **NaN** — the Fund does not publish an
income or poverty estimate for this tract (see the FAQ Q2 reasons above) —
render them "not available," never invent a number. **As of 0.5.0 `summary()`
does this for you**, and says which kind of missing it is; the same call on this
tract prints (executed this session):

```
  Poverty Rate:     not available — the CDFI Fund published no value for this tract
  AMI Ratio:        not available — the CDFI Fund published no value for this tract
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

Actual output this session (0.5.0):

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
geocode: `nmtc_eligible=None`, `distress_level="unknown"`,
`eligibility_status="geocode-failed"`, and `summary()` prints *"❓ UNKNOWN —
address could not be geocoded (indeterminate, NOT ineligible)."* (executed this
session on 0.5.0 against a deliberately unresolvable address). On that branch
0.5.0 also returns `opportunity_zone_status == 'no-tract'` and prints
*"Opportunity Zone: ❓ UNKNOWN — no census tract resolved"* — through 0.4.3 this
branch hardcoded `is_opportunity_zone=False`, asserting a non-designation about
an address that never resolved to a tract. It is the third of the three OZ
states and the only one that is *not* "not-confirmed."

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
  this table. Same posture as the third-state rule — an unknowable negative is
  not a negative.

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
four re-executed this session against the installed **0.5.0** wheel and are
unchanged from 0.4.2: the no-match and
agree branches ran against the live Census endpoint; the transport failure was
**induced** by pointing the geocoder URL at a closed local port, which raised
`GeocoderTransportError` (`connection/DNS`, `isinstance NMTCMapperError ==
True`), message naming the failure kind and the address; the disagree branch was
**induced** by returning two matches on different tracts, which raised
`AmbiguousAddressError` naming both candidates and stating it refuses to guess.

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
worked example.)

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
- The screener's score and estimated allocation are **first-pass heuristics** to
  triage deals, not underwriting or a commitment.
