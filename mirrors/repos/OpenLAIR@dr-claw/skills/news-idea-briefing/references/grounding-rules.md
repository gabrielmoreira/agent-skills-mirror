# Grounding Rules

Anti-hallucination guardrails for the news-idea-briefing skill. Read carefully — most failure modes come from skipping these.

## The hard rules

1. **Every literature claim must cite a canonical id from `candidates.json`.** No "as shown in recent work…" without a `[arxiv:…]` / `[gh:…]` / `[hf:…]` / `[wechat:…]` reference.
2. **Do not introduce items that are not in `candidates.json`.** If you think a cluster needs a paper that isn't there, say "no candidate from today covers …" instead of inventing one.
3. **Do not paraphrase abstracts beyond what's in the candidate's `abstract` field.** If the field is truncated, say so — don't fabricate the rest.
4. **Idea seeds must be grounded in a specific gap or extension** of cited items. Generic "improve X" or "scale Y to N" framings are not acceptable seeds.
5. **Confidence must downgrade conservatively.** When in doubt, mark `low`. The user is better served by 3 honest `low`-confidence seeds than by 3 falsely `high`-confidence ones.

## Citation format

Use these exact bracket forms in both `seeds.json` and `idea_briefing.md`:

- `[arxiv:2604.12345v1]` — arXiv (include version suffix)
- `[gh:owner/repo]` — GitHub repository
- `[hf:owner/repo]` — HuggingFace Hub (model / dataset / space)
- `[hf-paper:2604.12345]` — HuggingFace Daily Papers (without `v` suffix)
- `[wechat:huxiu_com:7f3a]` — WeChat 公众号 article (`account_route:title_hash[:4]`)
- `[xhs:abc123]` / `[x:1234567]` — Xiaohongshu / X posts (use `note_id` / `tweet_id`)

Multiple citations: `[arxiv:2604.12345v1, gh:foo/bar]` (comma-separated inside one bracket).

## What "grounded in a specific gap" means

A grounded seed identifies one of:

- **Empirical gap** — cited work claims X but only evaluates on Y subset; seed proposes evaluating on Z.
- **Methodological gap** — cited work uses approach A; seed proposes B and predicts when B should win.
- **Combination gap** — cited work A and cited work B both exist but never compose; seed proposes the composition.
- **Extension** — cited work demonstrates effect E in setting S₁; seed proposes testing E in setting S₂ where current theory predicts a different sign.
- **Reproduction-with-twist** — open-source repo cited; seed proposes a controlled ablation the original authors did not run.

If the seed doesn't fit one of these five molds, it's probably under-grounded.

## Common failure modes

### "Novelty soup"
> "Combine recent advances in [arxiv:A], [arxiv:B], and [arxiv:C] to build a unified framework."

Bad: no specific gap. Anything from arXiv can be "combined" in principle. Replace with a concrete operational hypothesis.

### "Trivial scaling"
> "Scale [arxiv:A]'s method from 7B to 70B."

Bad: scaling is ambient, not novel. Only acceptable if the cited work explicitly predicts a scaling-induced phase change.

### "Cross-domain handwave"
> "Apply [arxiv:A]'s NLP method to vision."

Bad unless you can name *which* concrete vision task, *why* the NLP-specific assumptions transfer, and *what* the failure mode would be.

### "Citation laundering"
The temptation to cite an item just because it appeared in `candidates.json`, even if it doesn't actually support the claim. Re-read the abstract. If it doesn't say what you're attributing to it, don't cite it.

## Self-check before emitting

Before writing `seeds.json`, run through each seed and confirm:

- [ ] Every bracketed id appears in `candidates.json`'s `items[].canonicalId`
- [ ] Each cited claim is supported by the corresponding item's `title` or `abstract` field
- [ ] The `first_experiment` is concrete enough that an engineer could start tomorrow
- [ ] The `risk` is real (not "this might not work as well as expected")
- [ ] The `confidence` honestly reflects uncertainty

If any seed fails this self-check, fix it or drop it. A briefing of 4 strong seeds beats a briefing of 8 weak ones.
