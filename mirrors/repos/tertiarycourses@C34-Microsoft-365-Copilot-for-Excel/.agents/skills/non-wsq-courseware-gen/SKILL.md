---
name: non-wsq-courseware-gen
description: Generate or regenerate a complete Tertiary Infotech NON-WSQ course package—concept-first slide deck, Learner Guide, Lesson Plan, and connected labs—followed by a full non-WSQ QA pass. Use when creating courseware for a C-prefix commercial short course or mirroring a WSQ counterpart while removing its funding, attendance, survey, and assessment layers.
---

# Generate NON-WSQ courseware

Use `$non-wsq-courseware-build` for the single-source generators,
`$non-wsq-lab-author` for detailed labs, and `$non-wsq-courseware-qa` for the
final audit. Read those skills before changing their data modules or running
their scripts.

## Hard boundaries

- Treat the deck and Learner Guide as knowledge products first. Labs practise
  the knowledge; they never replace it.
- Never add Written Assessment, SAQ, PP, case studies, marking guides,
  assessment briefing/flow, TRAQOM, digital attendance, the 75% attendance
  rule, SSG, SkillsFuture, subsidy/funding language, or a `TGS-` reference.
- Use the plain C-prefix course code. Replace the removed assessment block with
  **How You'll Learn** in the deck and **Learning Reinforcement** in the Lesson
  Plan.
- Keep WSQ-prefixed or unprefixed shared tooling unchanged. Work only in the
  requested non-WSQ repository and the installed non-WSQ skills.

## Research and authoring standard

1. Research every topic from authoritative sources before authoring. Distil
   definitions, principles, models, formulas where relevant, worked examples,
   context, common mistakes, and practitioner use. Never derive concept slides
   from lab steps alone.
2. Teach every lab's concept first. Precede each lab with a full concept section
   covering what the idea or tool is, why it exists, how it works, a worked
   example, and when to use or avoid it.
3. Give every concept section at least one useful visual: a flow diagram,
   framework, annotated example, comparison table, or relevant asset.
4. Keep concept/knowledge slides at 60% or more of the deck. Put objectives,
   context, and key steps in the deck; keep click-by-click detail in
   `labs/*.md`.
5. Introduce every lab in full sentences: what learners build, which concepts
   it applies, why it matters, and what the finished outcome looks like.
6. Make the Learner Guide a self-contained study text with multi-paragraph
   concept explanations and referenced visuals before each activity.

## Mirror a WSQ counterpart when available

1. Look for a sibling `TGS-*` repository with the same title or certification.
   If none exists, author from the approved course outline.
2. If one exists, mirror its topic/domain spine, lab count/order/titles,
   concept depth, slide sections, Learner Guide depth, Lesson Plan schedule
   shape, and `courseware/assets/`.
3. Remove the WSQ layer:

   | Remove | Replacement |
   |---|---|
   | Assessments, case studies, and marking guides | Nothing; non-WSQ has no assessment |
   | Assessment briefing and flow | **How You'll Learn** |
   | TRAQOM and digital-attendance slides | Nothing |
   | Funding, attendance, Skills Framework, and TSC content | Nothing |
   | `TGS-` cover/footer reference | Plain non-WSQ course code |
   | Assessment time | Lab, practice, and recap time |
   | Assessment wording in schedules and checklists | Learning/practice wording |

4. Reallocate time instead of shrinking the course. Each training day must
   still total its full instructional duration.

## Workflow

1. Resolve the course repository and inspect its outline, existing artifacts,
   `course_data.py`, domain modules, labs, and any WSQ counterpart.
2. Author or update the single-source content modules and connected labs.
3. Set `COURSE_REPO` to the target repository when using a user-level installed
   build skill. Run:

   ```bash
   COURSE_REPO="<course-repo>" bash "<non-wsq-courseware-build-skill-dir>/build/build_courseware.sh"
   ```

4. Bump `VERSION`, add a `VERSION_HISTORY` row, and move superseded generated
   versions into `courseware/archive/`.
5. Run the prohibited-content scanner:

   ```bash
   python "<non-wsq-courseware-qa-skill-dir>/scan_prohibited.py" "<course-repo>"
   ```

6. Use the `non-wsq-courseware-qa` custom agent for an independent read-only
   audit. Inspect PPTX/DOCX structure and render changed pages before declaring
   success.
7. Fix every failure, rebuild, and repeat QA until clean.

## Completion criteria

Do not report completion unless the PPT, Learner Guide, Lesson Plan, and labs
exist, agree on course identity/version/topic and lab sequence, contain more
concept teaching than lab-step slides, pass the prohibited-content scan, and
have no visible clipping, overlap, blank pages, or unreadable content.
