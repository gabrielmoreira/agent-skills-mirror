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
4. Analyze each source separately before calculating a combined result.
5. Report sample size so a short document is not presented as statistically stable.

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
