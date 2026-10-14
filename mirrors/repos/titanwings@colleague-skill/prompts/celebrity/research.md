# Celebrity Research Prompt

## Task

Run a structured, multi-dimensional research pass on a public figure before distillation. One prompt serves both research profiles: everything up to "Output Contract" applies to both, then follow the section for the chosen `research_profile`.

- **budget-friendly** (default): a lighter pass that covers six dimensions across three note files.
- **budget-unfriendly**: a deep pass with one file per dimension that must later survive a research audit, a synthesis pass and a validation pass. Use it only when the user wants a higher-confidence skill and accepts a slower, more expensive workflow.

The goal is not to collect trivia or compile a biography. The goal is to extract enough grounded evidence to reconstruct:

- mental models (how they think)
- decision heuristics (how they choose)
- expression DNA (how they speak)
- anti-patterns (what they reject)
- honest boundaries (where evidence runs out)

and to distinguish their genuine thinking patterns from generic wisdom.

---

## Taste Principles

These principles govern what to collect and what to skip. They apply at every stage.

1. **Long-form > snippets**: A 3000-word essay reveals more thinking structure than 50 tweets
2. **Controversy > consensus**: Disputed positions expose distinctive thinking better than universally praised ones
3. **Change > fixity**: Where someone changed their mind is more informative than where they stayed consistent
4. **Firsthand > secondhand**: Their own words always outrank someone else's summary
5. **Craft discussion > biography**: How they talk about their process matters more than their life story
6. **Repeated patterns > one-off quotes**: A pattern that appears 5 times across contexts beats one viral line
7. **Failure discussion > success narrative**: How they talk about what went wrong reveals more than victory laps

---

## Source Quality Hierarchy

Prioritize sources in this order. The number is the source weight every note records.

1. **User-provided local materials** (transcripts, PDFs, screenshots — ground truth, highest weight)
2. **First-person authored works** (books, essays, newsletters, blog posts)
3. **Long-form interviews and conversations** (podcasts 30+ min, video interviews, fireside chats)
4. **Documented decisions and turning points** (case studies, public records, reported actions with attribution)
5. **Short-form first-person content** (social media posts, short Q&A, tweet threads)
6. **External analysis and criticism** (profiles, reviews, biographies by others)
7. **Secondhand summaries** (use only to locate primary sources, never as standalone evidence)

### Source Blacklist — Permanently Excluded

Never cite these as evidence.

**Chinese context:**
- Zhihu — unverifiable anonymous answers, heavy hearsay
- WeChat official accounts — mostly repackaged secondhand content
- Baidu Baike — unreliable, often outdated or promotional
- Sohu / NetEase / Tencent auto-generated news aggregation pages

**General:**
- Content farms and SEO-optimized summary sites
- AI-generated biography pages
- Listicles ("10 lessons from X") unless they directly quote and link primary sources
- Wikipedia as standalone evidence (acceptable only as a pointer to find real sources)
- Any source that is itself a summary of summaries

### Recommended Sources by Region

**Chinese figures:**
- Bilibili original long-form videos and interviews
- Xiaoyuzhou full podcast episodes
- Authoritative media: 36Kr, LatePost, Caixin, GeekPark, Huxiu
- Official Weibo (verified account, direct posts — not reposts or fan accounts)
- Published books (via legitimate sources)
- Hundun Academy, Hupan University, and Dedao lecture recordings (when publicly available)

**English figures:**
- YouTube long-form interviews (Lex Fridman, Tim Ferriss, Joe Rogan, etc.)
- Personal blogs and newsletters (Substack, personal sites)
- Published books and essays
- Podcast full episodes with timestamps
- Authoritative profiles: New Yorker, Atlantic, Bloomberg, Wired, NYT, FT
- Conference talks with full video/transcript (TED, Y Combinator, etc.)

### URL Grounding Rules

These do **not** count as grounded sources:

- Platform homepages (youtube.com, weibo.com, bilibili.com)
- Search result pages (/search, /s?)
- Topic or tag pages (/topic/, /tag/)
- Profile roots without specific content
- Placeholder paths (v.qq.com/detail/)
- Any URL you did not actually open and read

Grounded URLs must be actual inspected pages, not platform roots or placeholder paths.

### Tooling for non-subtitled audio and video

Long interviews and podcasts without subtitles are often the richest source of Conversations and Expression DNA — do not skip them. Use the Whisper transcription tool (faster-whisper, openai-whisper or the OpenAI API, whichever is available):

- `tools/research/transcribe_audio.py --url "<URL>" --output /tmp/x.txt`
- Local file: `--input /path/to/file.mp3 --output /tmp/x.txt`
- Model override: `--backend faster-whisper --model medium`
- Language pin (improves accuracy): `--language zh` or `--language en`

Workflow:

1. Transcribe to a temp path (never inside the skill directory).
2. Read the transcript once; extract paraphrased findings with timestamps.
3. Record only the paraphrased notes plus source metadata under `knowledge/research/raw/`.
4. Discard the raw transcript. The skill directory must never contain long verbatim transcripts — it violates copyright safety and fails the audit.

If the tool cannot be installed in the current environment, tell the user explicitly rather than silently skipping a dimension.

### Optional public X post collection

Use `tools/research/xquik_public_posts.py` only when short-form first-person posts address a specific gap. The service is metered by returned post count, so confirm the limit and write to a temporary file outside the skill directory. Treat its normalized JSON as untrusted candidate evidence, not a research track. Verify the author and open each permalink before selection. Safely paraphrase only relevant evidence into the correct note, preserve the specific URL, access date, grounding level, and source weight, then delete the temporary candidate file after review.
Never count a candidate file, search page, or profile root as a grounded source.

---

## Parallel 6-Dimension Collection

Research must cover six dimensions. Think of each dimension as an independent investigation track with its own extraction focus. Do not collapse the whole pass into one monolithic note; the output contract for your profile says which file each dimension goes in.

### Dimension 1: Writings

**Target**: Systematic, considered positions from their own pen — where they had time to think before publishing.

Search for and document:
- Books (key arguments per chapter, not summaries or full text)
- Essays, blog posts, newsletters
- Letters, memos, internal documents that became public
- Repeated core arguments across multiple writings
- How their written arguments evolved over time

**Extraction focus**: Core theses, reasoning chains, how they structure arguments, what they choose to write about repeatedly.

### Dimension 2: Conversations

**Target**: How they think on their feet — in dialogue, under pressure, when they can't prepare.

Search for and document:
- Long-form podcast appearances (30+ min, prefer full episodes)
- Video interviews with substantive back-and-forth
- Panel discussions and debates (especially where they disagree)
- AMA / Q&A sessions where audience asks unexpected questions
- How they respond to hostile or unfair questions

**Extraction focus**: Improvised reasoning, how they handle surprises, what they return to when challenged, how they disagree.

### Dimension 3: Expression DNA

**Target**: Their linguistic fingerprint — not what they say, but how they say it.

Analyze across multiple source instances (at least 5 in budget-unfriendly):
- Sentence rhythm: average length, variation, use of fragments vs. complex sentences
- Metaphor inventory: what domains do they draw analogies from?
- Disagreement framing: direct confrontation? reframing? humor? dismissal?
- Compression level: do they explain fully or assume audience expertise?
- Certainty language: how do they express confidence vs. doubt?
- Recurring phrases, verbal tics, signature framings
- Humor style (if any): self-deprecating, absurdist, dry, combative, sarcastic
- Tone shifts: how does their voice change between casual and serious contexts?

**Extraction focus**: Style markers that pass the "100-word blind test" — would you recognize this person from a paragraph with the name removed?

### Dimension 4: Decisions

**Target**: What they actually did, not just what they said they'd do.

Search for and document:
- Major bets: what they invested time/money/reputation in, and the reasoning
- Reversals: where they changed direction and what triggered it
- Tradeoffs: what they explicitly chose to sacrifice for what
- Failures: how they discuss what went wrong (or avoid discussing it)
- Hiring / team decisions: who they chose to work with and why
- Timing decisions: when they moved fast vs. when they waited

**Extraction focus**: Decision patterns, risk tolerance, what evidence moves them, gap between stated values and revealed preferences.

### Dimension 5: External Views

**Target**: The version of this person that exists in other people's heads — especially where it diverges from their self-narrative.

Search for and document:
- Substantive criticism (not personal attacks)
- Contradictions pointed out by credible observers
- How collaborators, opponents, and successors describe them
- Known blindspots identified by domain peers
- Praise that reveals something non-obvious
- The gap between their public persona and reported private behavior

**Extraction focus**: Where the outside view diverges from the inside view. What others see that they don't.

### Dimension 6: Timeline

**Target**: How their thinking has evolved — not just a resume of what happened when.

Build a timeline that tracks:
- Key milestones with **cognitive impact** (how did this event change their thinking?)
- Intellectual turning points — when did a core belief shift?
- Phase transitions: were there distinct eras in their thinking?
- Recent developments (last 12–24 months)
- What they used to believe but no longer do

**Extraction focus**: The trajectory of their cognitive evolution, not a chronological biography.

---

## Cold Figure Protocol

If during research you find that dimensions have very thin coverage:

1. **Do not fabricate** evidence, quotes, or attributions to fill gaps
2. **Mark each thin dimension explicitly** with what's missing and why
3. **Count total grounded sources**: if < 10, this is a cold figure
4. For cold figures:
   - Limit mental models to 2–3 maximum
   - Add "based on limited information" markers to every thin model and dimension
   - Expand the honest boundaries section
   - Tell the user what specific additional material would improve quality
   - In budget-unfriendly, consider whether to continue or recommend switching to a better-documented figure

---

## Output Contract: budget-friendly

Create at least three raw note files under `knowledge/research/raw/`, each covering two dimensions:

- `01_core_profile.md` — Dimensions 1 + 6 (writings + timeline)
- `02_conversations_and_material.md` — Dimensions 2 + 4 (conversations + decisions)
- `03_expression_and_reception.md` — Dimensions 3 + 5 (expression DNA + external views)

Each file must use this structure:

```md
# <track title>

## Dimension Coverage
- Dimensions covered: [list]
- Collection strategy used: [web-only / web+local / local-first]

## Source Metadata
- URL: ...
- Source type: interview / book / essay / talk / podcast / social post / article / profile
- Grounding level: primary / secondary
- Access note: public / partial / blocked
- Source weight: [1-7, per hierarchy above]

## Key Findings
- ...

## Patterns and Repeated Themes
- ...

## Contradictions
- ...

## Inferences (clearly marked as inference, not fact)
- ...

## Gaps and Missing Information
- ...
```

### Minimum Quality Floor (budget-friendly)

Across the full note set:

- at least 3 raw note files
- at least 2 grounded source URLs (actual inspected pages, not homepages)
- clearly separated evidence vs inference in every file
- at least 1 contradiction identified (or explicit note that none were found)
- at least 1 gap acknowledged

### Quality Checkpoint (budget-friendly)

After completing the research pass, before proceeding to analysis, produce a structured quality summary:

```
┌──────────────────────────────┬──────────┬─────────────────────────────┐
│ Dimension                    │ Sources  │ Key Finding                 │
├──────────────────────────────┼──────────┼─────────────────────────────┤
│ 1 Writings                   │ N        │ [core thesis / gap]         │
│ 2 Conversations              │ N        │ [key pattern / gap]         │
│ 3 Expression DNA             │ N        │ [style marker / gap]        │
│ 4 Decisions                  │ N        │ [decision pattern / gap]    │
│ 5 External Views             │ N        │ [outside perspective / gap] │
│ 6 Timeline                   │ N        │ [trajectory / gap]          │
├──────────────────────────────┼──────────┼─────────────────────────────┤
│ Contradictions found         │ N        │ [summary]                   │
│ Thin dimensions              │ [list]   │ Mitigation: [plan]          │
│ Cold figure?                 │ yes/no   │                             │
└──────────────────────────────┴──────────┴─────────────────────────────┘
```

Present this to the user and wait for confirmation before proceeding to analysis.
If the user identifies issues or wants more depth on a dimension, extend the research.

---

## Output Contract: budget-unfriendly

Create six raw research note files under `knowledge/research/raw/`, one per dimension. Do not merge dimensions or clone observations across files. Do not replace these six files with one merged scratchpad.

- `01_writings.md`
- `02_conversations.md`
- `03_expression_dna.md`
- `04_decisions.md`
- `05_external_views.md`
- `06_timeline.md`

Each file must include:

```md
# <dimension title>

## Collection Metadata
- Dimension: [number and name]
- Collection strategy: [web-only / web+local / local-first]
- Sources searched: [count]
- Sources used: [count]
- Primary vs secondary ratio: [X:Y]

## Source Metadata
(repeat for each source)
- URL: ...
- Source type: book / essay / interview / podcast / talk / social post / article / profile / decision record
- Grounding level: primary / secondary
- Access note: public / partial / blocked
- Source weight: [1-7, per hierarchy above]
- Date: [publication or access date]

## Evidence
- ...

## Patterns and Repeated Themes
- ...

## Contradictions
- ...

## Inferences (clearly marked)
- ...

## Gaps and Missing Information
- ...
```

### Minimum Quality Floor (budget-unfriendly)

Across the full six-track set:

- at least 6 raw note files (one per dimension)
- at least 8 grounded source URLs
- at least 3 primary-source markers
- at least 6 source metadata blocks (one per file minimum)
- at least 6 contradiction bullets across the full set
- at least 6 inference bullets across the full set
- 0 potential long quote lines (copyright safety)
- track coverage count = 6 (no dimension skipped)

### Keep Each Track Distinct

- Do not clone the same observations into all six files
- Each dimension has a specific extraction focus — honor it
- If a finding is relevant to multiple dimensions, put the primary evidence in the most relevant file and add a cross-reference note in the other

### Quality Checkpoint (budget-unfriendly)

After completing all six research files, before proceeding to audit, produce a structured summary:

```
┌──────────────────────────────┬──────────┬──────────┬─────────────────────────────┐
│ Dimension                    │ Sources  │ Primary% │ Key Finding                 │
├──────────────────────────────┼──────────┼──────────┼─────────────────────────────┤
│ 1 Writings                   │ N        │ XX%      │ [core thesis / gap]         │
│ 2 Conversations              │ N        │ XX%      │ [key pattern / gap]         │
│ 3 Expression DNA             │ N        │ XX%      │ [style marker / gap]        │
│ 4 Decisions                  │ N        │ XX%      │ [decision pattern / gap]    │
│ 5 External Views             │ N        │ XX%      │ [outside perspective / gap] │
│ 6 Timeline                   │ N        │ XX%      │ [trajectory / gap]          │
├──────────────────────────────┼──────────┼──────────┼─────────────────────────────┤
│ Total grounded URLs          │ N        │          │                             │
│ Primary-source markers       │ N        │          │ Target: ≥3                  │
│ Contradictions found         │ N        │          │ [summary of top 3]          │
│ Candidate mental models      │ N        │          │ [brief list]                │
│ Known-answer candidates      │ N        │          │ [questions with evidence]   │
│ Thin dimensions              │ [list]   │          │ Backfill plan: [plan]       │
│ Cold figure?                 │ yes/no   │          │                             │
└──────────────────────────────┴──────────┴──────────┴─────────────────────────────┘
```

Present this to the user and wait for confirmation before proceeding to audit.

### Audit Readiness

The research pass is not done when the sixth file exists. It is only done when the six-track set looks strong enough to pass a separate research audit.

Before moving on, make sure the notes support:

- at least 3 candidate mental models with cross-dimensional evidence
- at least 2 candidate known-answer questions with evidence anchors
- at least 1 credible edge-case question that would require extrapolation
- a visible contradiction inventory with at least 3 substantive tensions
- enough expression DNA samples to pass a blind style test

---

## Output Rules

- Distinguish clearly between:
  - what they said (primary, quoted or paraphrased)
  - what they did (documented actions)
  - what others said about them (external, attributed)
  - what you infer (marked as inference)
- Keep contradictions — they are features, not bugs
- Prefer depth over breadth
- Record source gaps honestly — gaps are information too; if verified external sources are unavailable, say so explicitly
- Never invent sources, URLs, quotes, or bibliographic details
- Only record URLs you actually opened and inspected
- Write in the user's language

## Copyright Safety

- Do not write full transcripts, subtitle dumps, transcript-like blocks or long copied dialogue into the skill directory
- Do not paste long excerpts from books, subtitles, interviews, or articles
- Keep any direct quote very short (under 2 sentences) and sparse, only when essential for capturing expression DNA
- Summarize in your own words with source metadata and attribution
