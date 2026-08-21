---
name: product-feedback-synthesizer
description: "Collapses tickets, store reviews, surveys, and transcripts into themed VoC reports with sentiment, verbatim quotes, ARR-weighted urgency, and RICE/MoSCoW buckets. Use for roadmap synthesis from mixed qualitative and quantitative feedback. Never a live support-desk reply bot, NPS-timing designer, or telemetry-only analytics chair."
version: 1.0.1
last_verified: '2026-05-30'
domain: research-ideation
risk: safe
self_updating: true
---

## When to Use

- Aggregating feedback from disparate streams (support tickets, App Store reviews, surveys, community channels).
- Performing thematic coding, sentiment classification, and semantic analysis on raw text.
- Prioritizing feature requests and bug fixes using RICE, MoSCoW, or Kano frameworks.
- Generating Voice of the Customer (VoC) synthesis reports for product managers and engineering leads.
- Synthesizing multi-channel user data (tickets, surveys, reviews, transcripts) to inform product strategy, sprint planning, roadmap prioritizing, or design iterations.

## Prerequisites

- A JSON or CSV dataset of feedback items containing:
  - `id` (unique string)
  - `text` (raw qualitative string)
  - `metadata` (object with `source`, `timestamp`, `segment`)
- A pre-defined feature taxonomy mapping file.
- Ensure all user data is fully anonymized before synthesis. Remove PII (raw email addresses, API tokens, passwords, phone numbers) using PII scrubbers (like Microsoft Presidio or AWS Comprehend) before indexing.

## Procedure

1. **Ingestion & De-duplication**: Aggregate entries daily. Strip HTML tags, remove duplicate support tickets submitted by the same user within 24 hours, and discard generic system errors.
2. **Metadata Tagging**: Attach metadata to each feedback item: source channel, customer segment (e.g., Enterprise, Mid-Market, Free Tier), ARR value, and timestamp.
3. **Domain Classification**: Map the feedback entry to a specific product surface (e.g., Authentication, Checkout, Dashboard, API).
4. **Sentiment Scoring**: Assign an initial sentiment score from -1.0 (Highly Frustrated) to +1.0 (Highly Satisfied).
5. **Qualitative Coding**: Apply thematic coding systematically using a standardized tag taxonomy defined beforehand (e.g., `usability-issue`, `feature-request`, `performance-bug`, `pricing-complaint`). Avoid generating ad-hoc tags.
6. **Quote Extraction**: Extract at least 3 verbatim quotes for every primary theme identified. Do not alter wording, but truncate long passages with ellipses.
7. **Volume vs. Value Validation**: Cross-check feedback frequency against total account value (ARR) of the complaining segments to avoid prioritizing vocal minority groups over key business drivers.
8. **Prioritization**: Calculate the RICE score for each theme: `RICE Score = (Reach * Impact * Confidence) / Effort`.
   - **Reach**: Estimated users affected per quarter.
   - **Impact**: 3 (Massive), 2 (High), 1 (Medium), 0.5 (Low), 0.25 (Minimal).
   - **Confidence**: 100% (High), 80% (Medium), 50% (Low).
   - **Effort**: Person-months required.
9. **Sorting & Bucketing**: Sort the table in descending order. Segment top features into MoSCoW buckets (Must Have, Should Have, Could Have, Won't Have) for sprint planning.
10. **Stakeholder Delivery**:
    - **Executive Team (C-Suite)**: Highlight high-level trends, NPS impacts, churn risks, and competitor product gaps. Deliver in slide decks or summary matrices.
    - **Product Managers**: Provide RICE-prioritized feature requests, user stories, target customer segments, and supporting user quotes.
    - **Engineering Leads**: Deliver descriptive technical bug reports, environment details, steps to reproduce, and user friction ratings.

### Output Contract (Grounded Synthesis JSON Schema)

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "VoiceOfCustomerSynthesisReport",
  "type": "object",
  "properties": {
    "reportDate": { "type": "string", "format": "date" },
    "totalAnalyzed": { "type": "integer" },
    "topThemes": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "themeName": { "type": "string" },
          "volumePercent": { "type": "number" },
          "averageSentiment": { "type": "number", "minimum": -1, "maximum": 1 },
          "representativeQuotes": {
            "type": "array",
            "items": { "type": "string" }
          },
          "riceScore": { "type": "number" }
        },
        "required": ["themeName", "volumePercent", "averageSentiment", "representativeQuotes", "riceScore"]
      }
    }
  },
  "required": ["reportDate", "totalAnalyzed", "topThemes"]
}
```

## Pitfalls

- **Vocal Minority Dominance**: Prioritizing a feature request based solely on a single highly active forum thread or a few angry tweets without validating user segment demographics or broader telemetry.
- **Unstructured Tag Bloat**: Creating duplicate or highly specific tags (e.g., `button-color`, `btn-clr`, `submit-button-style`) that fragment feedback and hide overall themes.
- **Synthesizing Without Context**: Coding user quotes out of context. An issue reported during a major outage must be isolated from standard day-to-day product feedback metrics.
- **Cherry-picking Positives**: Excluding highly critical or uncomfortable feedback from executive reports to inflate stakeholder satisfaction scores.
- **NPS Survey Timing**: Triggering NPS surveys immediately after a user encounters an error or during onboarding, which artificially skews overall NPS results.
- **Feature Ask vs. Real Need**: Taking user feature requests literally. Users often ask for specific buttons or settings when the underlying need is a simplified workflow.
- **Translator Bias**: Customer support agents paraphrasing user issues in tickets, which strips away the original vocabulary and emotion used by the customer.
- **Confirmation Bias**: Track positive, neutral, and negative comments with equal weighting. Use peer-review checkpoints to validate the categorization of borderline qualitative feedback.

## Verification

- **Double-Coder Agreement**: Manual tags must be cross-checked across two separate coding passes to maintain a minimum Cohen's Kappa score of 0.80.
- **Sentiment Calibration**: Validate that automated sentiment scores match context clues (e.g., verify that sarcastic comments like "Great feature, it broke my build" are marked negative).
- **Grounded Assertions**: Every listed product pain point must be backed by a link reference to the raw, anonymized customer logs.
- **No Unweighted Data**: Synthesis reports must show both unweighted volume and ARR-weighted urgency.
- **Data Gaps**: When feedback volume is too low to extract themes, halt synthesis and trigger targeted customer surveys or customer success interviews.
- **Sentiment Ambiguity**: If sarcasm or domain-specific language skews sentiment calculations, manually re-evaluate the scoring of the top 10% highest-impact issues.
