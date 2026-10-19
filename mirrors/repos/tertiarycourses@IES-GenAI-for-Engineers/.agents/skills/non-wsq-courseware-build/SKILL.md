---
name: non-wsq-courseware-build
description: Single-source build pipeline for a NON-WSQ (C-prefix) course — one content module (course_data.py + data_domainN.py) drives ALL artifacts (the all-white slide deck PPT, the Lesson Plan LP, the Learner Guide LG + its Markdown mirror) so they stay 100% aligned. Excludes all WSQ funding, SSG/SkillsFuture, TRAQOM, digital-attendance and assessment content. Use to build or regenerate courseware for a Tertiary Infotech non-WSQ short course.
---

# non-wsq-courseware-build — single-source NON-WSQ courseware pipeline

The non-WSQ sibling of `courseware-build`. Same house look, same single-source
guarantee, with the entire funding/compliance layer removed.

## What "non-WSQ" means here (hard rules)

Non-WSQ courses are **commercial short courses** — they are not funded, not
audited by SSG, and carry **no assessment**. The engine therefore never emits:

| Removed | Why |
|---|---|
| Written Assessment (WA/SAQ), Practical Performance (PP), case study, marking guides | **There is no assessment for a non-WSQ course** |
| "Briefing for Assessment" + "Assessment Flow" slides | No assessment to brief or run |
| TRAQOM survey slides | TRAQOM is an SSG funding requirement |
| Digital attendance (AM/PM/Assessment QR) slides | SSG-funded courses only |
| 75% attendance rule, funding/subsidy eligibility | No funding involved |
| TGS- course reference on covers | Uses the plain non-WSQ code (e.g. C524) |

Everything else — the deck's visual system, LP schedule tables, LG depth, the
cover page, Document Version Control Record, TOC and footers — matches the WSQ
house standard exactly.

In place of the assessment block the deck carries a **"How You'll Learn"** flow
(demonstrate → build → verify → discuss → recap) and the LP carries a
**"Learning Reinforcement"** section, so the pedagogy is still explicit.

## Layout

```
<skill-dir>/
  SKILL.md
  assets/            brand assets (tertiary-infotech-logo.png, optional course-badge.png)
  build/
    course_data.example.py   TEMPLATE → copy to course_data.py (metadata, outcomes, topics, schedule)
    data_domain.example.py   TEMPLATE → copy to data_domain1.py … data_domainN.py (per-topic labs)
    build_slides.py       generic engine → courseware/<TITLE>-<VER>.pptx  (all-white house style)
    build_lesson_plan.py  generic engine → courseware/LP-<TITLE>.docx
    build_learner_guide.py generic engine → LG-<TITLE>.md (repo root) + courseware/LG-<TITLE>.docx
    prodoc.py             shared DOCX helpers (cover, version-control record, TOC, page numbers)
    inject_toc.py         page-numbered TOC injector (LibreOffice can't update TOC fields headless)
    build_courseware.sh   orchestrator: generate → render PDF → inject TOC → re-render
```

## Fully generic — no course hard-coded

Unlike the WSQ engine (which hard-codes its own subject matter), this engine is
data-driven throughout:

- **Any number of topics/domains** — `data_domain[0-9]*.py` files are discovered
  and imported dynamically, not a fixed five.
- **Topic accents** cycle automatically, so any topic count gets distinct colours.
- **Schedule** comes from `course_data.SCHEDULE` (a dict, or a callable given
  `lab_titles()` so activity text is built from the lab data itself).
- **Concepts section, glossary, setup, wrap-up, screenshots** are all optional
  `course_data` fields — omit one and its slides/sections simply don't render.
- `weighting` is optional on a topic (there is no exam to weight against).
- The repo is found by walking up for a dir containing `courseware/` and `labs/`;
  override with `COURSE_REPO`. `assets/` resolves relative to the skill.
- Output filenames derive from `SHORT_TITLE` / `VERSION`.

## Build

Resolve `<skill-dir>` from this `SKILL.md`. When the skill is installed at user
scope, set `COURSE_REPO` to the target repository so generated artifacts land
in that repository rather than beside the installed skill. On Windows, prefer
Git Bash (`C:\Program Files\Git\bin\bash.exe`) over the WSL launcher. The
orchestrator auto-detects LibreOffice in its standard Windows installation
path; set `SOFFICE` explicitly for a non-standard install.

```bash
# one command: PPT + LP + LG as DOCX + PDF, with page-numbered TOCs
COURSE_REPO="<course-repo>" bash "<skill-dir>/build/build_courseware.sh"

# or individually
COURSE_REPO="<course-repo>" python "<skill-dir>/build/build_slides.py"
COURSE_REPO="<course-repo>" python "<skill-dir>/build/build_lesson_plan.py"
COURSE_REPO="<course-repo>" python "<skill-dir>/build/build_learner_guide.py"
```

**Do not** pair this with the `wsq-assessment` skill — non-WSQ courses have no
assessment. There is deliberately no assessment builder in this suite.

## After a build (mandatory)

Bump `VERSION` and add a `VERSION_HISTORY` row in `course_data.py`, move
superseded versioned files to `courseware/archive/`, then run the
`non-wsq-courseware-qa` custom agent to audit the deck — it fails the build if any
WSQ/SSG/TRAQOM/assessment content has leaked back in.

## Reusing for a new course

Copy this skill into the new course's `.agents/skills/non-wsq-courseware-build/`,
write `course_data.py` + `data_domainN.py`, drop any course badge into `assets/`,
and run the orchestrator. The engine files are reused unchanged. Keep the
user-level installed copy unchanged when the data is course-specific.
