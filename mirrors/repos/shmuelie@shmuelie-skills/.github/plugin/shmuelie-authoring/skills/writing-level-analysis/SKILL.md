---
name: writing-level-analysis
description: "Measure the readability of user-provided or locally authored text with Flesch-Kincaid grade level and corroborating indices. Use when asked for a writing level, readability score, reading grade, or comparison between documents."
---

# Writing Level Analysis

Measure only text the user authored or explicitly supplied for analysis.

## Supported sources

- Text pasted into the conversation
- Local Markdown, text, or documentation files selected by the user
- Git-authored content filtered to commits by the user's configured identity
- Exported prompts or session transcripts supplied as files

Do not fetch private mail, organization records, or remote work systems unless
the user explicitly provides and authorizes that data source.

## Metrics

Report:

- Flesch-Kincaid Grade Level
- Flesch Reading Ease
- Gunning Fog
- Coleman-Liau
- Automated Readability Index
- Word, sentence, and syllable counts

Use a well-known readability library such as Python `textstat`. State the
library and version because syllable algorithms differ.

## Text preparation

1. Keep prose written by the user.
2. Remove generated boilerplate, quoted replies, source code, stack traces,
   tables, URLs, and machine-generated logs unless those are the target.
3. Preserve headings and list text when they represent authored prose.
4. Preserve authored punctuation and record boundaries. Do not append periods
   to prompts, headings, list items, or fragments merely to make them look like
   sentences. Do not join records by inventing punctuation.
5. Document exclusions and the exact record separator used when assembling
   each corpus (for example, two newlines). Keep original sources unchanged.
   Whitespace boundaries are not necessarily sentence boundaries to the scorer.
6. Analyze each source separately before calculating a combined result.
7. Report sample size so a short document is not presented as statistically stable.

### Synthetic punctuation example

Removing machine-generated framing (such as an exported timestamp or role
label) is not the same as rewriting the author's words. Record that removal;
do not modify punctuation in the retained prose. This **fictional** three-record
example shows why a period-appending cleanup is not neutral:

```python
import importlib.metadata
import textstat

textstat.set_lang("en_US")
records = [
    "Review the cache identity before publishing a new snapshot",
    "Keep the original configuration until the migration succeeds",
    "Report any unresolved conflict without replacing the stored settings.",
]
preserved = "\n\n".join(records)
# Counterexample only: do not use this rewrite in corpus preparation.
rewritten = "\n\n".join(
    record if record.endswith((".", "!", "?")) else record + "."
    for record in records
)
print("textstat", importlib.metadata.version("textstat"))
for name, corpus in [("preserved", preserved), ("rewritten", rewritten)]:
    print(name, textstat.lexicon_count(corpus, removepunct=True),
          textstat.sentence_count(corpus),
          textstat.syllable_count(corpus),
          textstat.flesch_kincaid_grade(corpus))
```

With `textstat` 0.7.13 in this example's English configuration, both variants
have 26 words and 54 syllables; the sentence count changes from 1 to 3 and
Flesch-Kincaid grade changes from approximately 19.06 to 12.30. The words did
not become clearer: the preprocessing changed the denominator. This is a tiny
diagnostic fixture, not a stable estimate of anyone's writing ability.

Different libraries, language settings, tokenizers and versions may segment
the same text differently; do not promise that effect size universally. Record
the scorer version, language, counts, exclusions and separator policy alongside
results. When a score shifts unexpectedly, inspect the cleaned corpus and
segmentation before attributing the shift to writing quality.

Per-source metrics retain their own sample sizes and preprocessing notes.
Recompute combined metrics from the full, consistently cleaned corpus using the
declared separator, rather than averaging grades or synthesizing sentence
terminators between sources. Keep sensitivity comparisons separate from the
primary punctuation-preserving analysis.

## Interpretation

- Grade 6-8: broadly accessible
- Grade 9-10: standard professional prose
- Grade 11-12: dense professional or technical prose
- Grade 13+: college-level or highly specialized prose

Readability is not writing quality. Technical vocabulary, identifiers, and
necessary precision can raise the score without making the text worse.

## Output

Produce:

1. A corpus summary
2. A per-document metrics table
3. Combined metrics recomputed from the complete cleaned corpus
4. The clearest and densest samples
5. Concrete revision suggestions
6. Methodology and exclusions

Never claim ownership of text based only on its location. Confirm authorship or
use explicit user-provided files.
