---
name: non-wsq-courseware-qa
description: Audit NON-WSQ courseware (PPT, LP, LG, labs) for completeness, alignment, visual defects and — critically — any leaked WSQ funding, SSG/SkillsFuture, TRAQOM, digital-attendance or assessment content. Run after every non-WSQ courseware build, before publishing or pushing.
---

# non-wsq-courseware-qa — audit a NON-WSQ courseware package

Non-WSQ courses are commercial short courses: **no funding, no compliance
overhead, and no assessment**. The single most common defect is WSQ material
leaking in — usually because the package was cloned from a WSQ course. This
skill catches that mechanically, then checks the usual quality bars.

## 1. Prohibited-content scan (automated, must pass)

```bash
python "<skill-dir>/scan_prohibited.py" "<course-repo>"
```

Resolve `<skill-dir>` from this `SKILL.md`.

Reads the real PPTX/DOCX/MD artifacts (not just source) and reports every hit
with its slide number, paragraph/table index or line number. Exit 0 = clean,
1 = fail. It flags:

- `WSQ`, `SSG`, `SkillsFuture`, `TRAQOM`, `TGS-` course references
- digital attendance, 75% attendance, course funding / subsidy language
- Written Assessment / SAQ, Practical Performance, formal-assessment phrasing,
  assessor / marking guide / answer key, Assessment Summary Record,
  "competent / not yet competent"

The patterns are deliberately context-aware: a bare word like "assessment" is
**not** flagged, because courses legitimately teach *risk assessment*, *impact
assessment* or *FMEA*. Only formal-assessment phrasing (`final assessment`,
`assessment flow`, `briefing for assessment`, …) fails. Likewise "funding" only
fails in a course-fee/subsidy context. If you add a pattern, keep that
discipline or the scan becomes noise and gets ignored.

**Every hit is a defect.** Fix the source (`course_data.py`, the domain files,
the lab Markdown), rebuild, and re-scan until it passes.

Skipped, by design: `courseware/archive/`, `reference/`, and the repo's own docs
at root (`README.md`, `CLAUDE.md`, `AGENTS.md`, …). Keep WSQ *source* documents — the original
Course Proposal, TSC/SFw extracts — in `reference/`, never in `courseware/`: they
legitimately contain WSQ language but are inputs to the course, not learner-facing
material. The root README likewise names the prohibited terms only to state they
are excluded. `labs/README.md` **is** scanned — it is learner-facing.

## 2. Completeness & alignment

- `courseware/` holds the PPT, LP DOCX+PDF, LG DOCX+PDF; the LG Markdown mirror
  sits at the repo root; `labs/` holds one file per lab plus a README index.
- Title, course code, version and topic order agree across **every** artifact.
- Lab numbering is contiguous and identical in the deck, LG, LP and `labs/`.
- Each LP day totals exactly 480 training minutes (lunch excluded) — the LP
  builder asserts this, so a build failure here is a real scheduling error.
- The cover version matches the `-vNN` in the filename, and the Document
  Version Control Record has a row for it.
- Superseded versions are in `courseware/archive/`, not deleted.

## 3. Content depth

- Every lab has Goal, what you'll build, numbered steps with commands,
  and a "Test it" verification step.
- The LG is detailed enough to follow without trainer improvisation.
- Each topic closes with a recap mapped to the learning outcomes.

## 4. Visual check (render, don't guess)

Render to images and actually look — at minimum the cover, the admin slides,
one slide per topic section, and every changed page:

```bash
soffice --headless --convert-to pdf --outdir /tmp <artifact>
pdftoppm -png -r 80 -f 1 -l 12 /tmp/<artifact>.pdf /tmp/page
```

Check for overlapping or clipped text, blank pages, unreadable contrast, and
titles wrapping into the divider rule.

If `pdftoppm` is unavailable, use the installed `$pdf`, `$documents`, or
`$presentations` render-and-verify workflow to produce page images. Do not skip
visual QA because one renderer is missing.

## 5. Expected structure (non-WSQ)

The deck must show **"How You'll Learn"** where a WSQ deck shows the assessment
block, and must **not** contain Briefing for Assessment, Assessment Flow,
Digital Attendance or TRAQOM slides at the front or the end. The closing run is
simply: What You Achieved → next-steps → Keep Practising → Thank You.

## Reporting

Report pass/fail with exact counts and locations. Do not report completion while
any prohibited-content hit remains. Use the `non-wsq-courseware-qa` custom agent
for an independent read-only audit when one is available.
