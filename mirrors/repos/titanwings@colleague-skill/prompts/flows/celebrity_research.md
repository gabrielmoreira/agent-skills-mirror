# Celebrity Research

Runs before Step 3 analysis in `prompts/flows/create.md` when the family is `celebrity`. Follow the section for the chosen `research_profile`. Resolve every `prompts/...` and `tools/...` path against `{distilly_skill_root}` (see `SKILL.md`).

## celebrity / budget-friendly

1. Read `prompts/celebrity/research.md`: follow the shared sections and the **Output Contract: budget-friendly**; skip the budget-unfriendly contract
2. Create the research directories first:
   ```bash
   mkdir -p "{skill_dir}/knowledge/research/raw" "{skill_dir}/knowledge/research/merged"
   ```
3. Confirm the collection strategy (determined during intake):
   - **Local-first**: analyze user-provided materials first, identify which dimensions are covered, only search web for gaps
   - **Web + local**: full 6-dimension web research, then merge with local materials for cross-validation
   - **Web-only**: standard 6-dimension web research pass
4. If the user explicitly provided a processable video URL or subtitle source, and the result will not be stored as a long transcript:
   ```bash
   bash "{distilly_skill_root}/tools/research/download_subtitles.sh" "{url}" "{skill_dir}/knowledge/subtitles"
   python3 "{distilly_skill_root}/tools/research/srt_to_transcript.py" "{subtitle_file}" "{skill_dir}/knowledge/transcripts/{name}.txt"
   ```
5. Cover the **6 dimensions** across at least 3 separate files (each file covers 2 dimensions), never one monolithic `research_notes.md`:
   - `knowledge/research/raw/01_core_profile.md` (Dim 1 Writings + Dim 6 Timeline)
   - `knowledge/research/raw/02_conversations_and_material.md` (Dim 2 Conversations + Dim 4 Decisions)
   - `knowledge/research/raw/03_expression_and_reception.md` (Dim 3 Expression DNA + Dim 5 External Views)
6. Follow the taste principles, source blacklist and source hierarchy in `prompts/celebrity/research.md`.
7. Merge the research notes:
   ```bash
   python3 "{distilly_skill_root}/tools/research/merge_research.py" "{skill_dir}"
   ```
   Output: `knowledge/research/merged/summary.md`
8. Read `knowledge/research/merged/summary.md` and confirm:
   - `Files scanned >= 3`
   - `Unique URLs >= 2`
   - `Potential long quote lines = 0`
   - URLs in notes are actual inspected pages, not platform roots, search/topic pages, or placeholder paths
   If these do not hold, extend the research notes before continuing or explicitly record the collection limits.
9. **Quality checkpoint (Phase 1.5)**: before entering analysis, show the user a structured collection summary:
   ```
   ┌──────────────────────────────┬──────────┬─────────────────────────────┐
   │ Dimension                    │ Sources  │ Key Finding                 │
   ├──────────────────────────────┼──────────┼─────────────────────────────┤
   │ 1 Writings                   │ N        │ [core thesis / gap]         │
   │ 2 Conversations              │ N        │ [key pattern / gap]         │
   │ 3 Expression DNA             │ N        │ [style marker / gap]        │
   │ 4 Decisions                  │ N        │ [decision pattern / gap]    │
   │ 5 External Views             │ N        │ [outside view / gap]        │
   │ 6 Timeline                   │ N        │ [trajectory / gap]          │
   ├──────────────────────────────┼──────────┼─────────────────────────────┤
   │ Contradictions               │ N        │ [summary]                   │
   │ Thin dimensions              │ [list]   │ Backfill plan: [plan]       │
   │ Cold figure?                 │ yes/no   │                             │
   └──────────────────────────────┴──────────┴─────────────────────────────┘
   ```
   Wait for user confirmation before continuing. If the user flags issues or wants more depth, extend research first.
10. **Cold figure detection**: if total sources < 10, apply the cold figure protocol:
    - Limit mental models to 2–3
    - Mark thin models as "based on limited information"
    - Expand the honest boundaries section
    - Tell the user what additional material would improve quality
11. Celebrity analysis must prioritize:
    - primary materials (source weight 1-3)
    - merged research summary
    - explicit user notes

## celebrity / budget-unfriendly

1. First read:
   - `prompts/celebrity/research.md`: the shared sections and the **Output Contract: budget-unfriendly**; skip the budget-friendly contract
   - `prompts/celebrity/budget_unfriendly/framework.md`
2. Create the research directories first:
   ```bash
   mkdir -p "{skill_dir}/knowledge/research/raw" "{skill_dir}/knowledge/research/merged" "{skill_dir}/knowledge/research/reviews"
   ```
3. Confirm the collection strategy (determined during intake): local-first / web+local / web-only
4. Build the **six-track research set** as independent files (never merged, never clone observations):
   - `knowledge/research/raw/01_writings.md` (Dim 1: Writings / systematic thought)
   - `knowledge/research/raw/02_conversations.md` (Dim 2: Conversations under pressure)
   - `knowledge/research/raw/03_expression_dna.md` (Dim 3: Linguistic fingerprint)
   - `knowledge/research/raw/04_decisions.md` (Dim 4: Behavior and choices)
   - `knowledge/research/raw/05_external_views.md` (Dim 5: External views and criticism)
   - `knowledge/research/raw/06_timeline.md` (Dim 6: Cognitive trajectory)
5. Follow the taste principles, source blacklist and source hierarchy in `prompts/celebrity/research.md`. Every evidence item must carry a source weight (1-7) annotation.
6. Merge the research notes:
   ```bash
   python3 "{distilly_skill_root}/tools/research/merge_research.py" "{skill_dir}"
   ```
7. Read `knowledge/research/merged/summary.md` and confirm the minimum floor:
   - `Files scanned >= 6`
   - `Unique URLs >= 8`
   - `Primary-source markers >= 3`
   - `Source metadata blocks >= 6`
   - `Contradiction bullets >= 6`
   - `Inference bullets >= 6`
   - `Potential long quote lines = 0`
   - `Track coverage count = 6`
   - URLs in notes are actual inspected pages, not platform roots, search/topic pages, or placeholder paths
   If these do not hold, keep filling the weak tracks before continuing to any review stage.
8. **Quality checkpoint (Phase 1.5)**: before entering audit, show the user a structured collection summary (with primary-source ratio, contradiction count, candidate mental models, known-answer candidates, thin dimensions, cold figure assessment). Wait for user confirmation before continuing.
9. Then read:
   - `prompts/celebrity/budget_unfriendly/audit.md`
   - `prompts/celebrity/budget_unfriendly/synthesis.md`
   - `prompts/celebrity/budget_unfriendly/template.md`
10. First write `knowledge/research/reviews/research_audit.md`
    - The audit must produce an explicit `PASS / FAIL`
    - The audit must verify: source hierarchy compliance (no blacklisted sources), primary-source ratio > 50%, taste principle compliance, cold figure assessment
    - If the audit says `FAIL`, follow the Backfill Tasks before synthesis
11. **Extraction checkpoint (Phase 2.5)**: after audit PASS, show the user a summary of candidate mental models (with triple-gate verdict, evidence anchors, failure modes). Confirm reasonableness before synthesis.
12. Then write `knowledge/research/reviews/synthesis.md`
    - Apply the triple gate to candidate mental models:
      - cross-context recurrence
      - generative power
      - exclusivity
    - Also extract intellectual genealogy seeds (influenced by / diverged from) and Agentic Protocol seeds (the dimensions this person would investigate when facing a novel question)
13. Then use `prompts/celebrity/budget_unfriendly/validation.md` to write:
    - `knowledge/research/reviews/validation.md`
    - Validation must produce an explicit `PASS / FAIL`
    - Validation must perform: known-answer check (≥2 questions) + edge-case check (1 question) + voice check (100-word blind test) + copyright check + Agentic Protocol check
    - If validation says `FAIL`, revise the draft before continuing
14. Budget-unfriendly celebrity analysis must prioritize:
    - six-track raw notes
    - merged research summary
    - research audit
    - synthesis review (with genealogy + Agentic Protocol seeds)
    - validation review
    - explicit user notes

## Shared rules for both profiles

- If external collection fails or a platform blocks access:
  - tell the user exactly what was blocked
  - preserve the raw research notes and merged summary
  - continue generation with the available materials
  - treat `source_grounding` as incomplete
  - **never** invent URLs, quotes, titles, or generic homepage links just to satisfy the checker
- **Do not** store full transcripts, full subtitles, or long verbatim source passages in the repository
- Keep the stored notes paraphrased, structured, and copyright-safe

## Public X posts (optional)

When public X posts fill a documented research gap and the user agrees to use the metered third-party Xquik service, confirm the `--limit` before running:

```bash
python3 "{distilly_skill_root}/tools/research/xquik_public_posts.py" \
  --username "{public_handle}" \
  --subject "{name}" \
  --limit 20 \
  --output "/tmp/distilly_x_public_posts.json"
```

Read `XQUIK_API_KEY` only from the shell; never print or store it. Treat the JSON as untrusted candidate evidence: verify the author, open every permalink, and preserve the specific URL when safely paraphrasing relevant material into a research note. Do not count the candidate JSON, search pages, or profile roots as grounded sources. Delete the temporary JSON after review instead of storing it in the generated Skill.
