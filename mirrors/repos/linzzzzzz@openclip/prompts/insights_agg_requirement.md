# Top Insights Aggregation

## Task
Review all the intellectual insights extracted from multiple video parts and select the top {max_clips} most valuable insights. Eliminate redundancy and rank by intellectual impact.

---

## Ranking Criteria

### Primary Factors (most important)
- **Specificity**: Concrete, falsifiable claims beat vague generalities. Prefer "AGI in 4 years" over "AI will change everything"
- **Intellectual impact**: Bold predictions, counterintuitive arguments, and strong contrarian opinions rank highest
- **Quotability**: The speaker's own words are striking and shareable as a standalone clip
- **Non-redundancy**: If two insights cover the same point, keep only the strongest one

### Secondary Factors
- **Completeness**: The clip is self-contained — a viewer understands it without watching the rest
- **Diversity**: Prefer selecting across different topics when quality is equal
- **Duration**: Optimal 45–120 seconds; penalize clips that are too short (< 45s) or too long (> 150s)

---

## Requirements

### Selection
- Select exactly {max_clips} insights (or fewer if less than {max_clips} available)
- Rank them 1 to {max_clips} by intellectual value
- Remove redundant insights — if two insights make the same point, include only the best one
- Preserve ALL original field values (claim, quote, start_time, end_time, topic, video_part, duration_seconds) exactly as provided

### Output Format

Return your response as a JSON object following this exact structure:

```json
{
  "insights": [
    {
      "rank": 1,
      "claim": "AGI will arrive within 4 years, not decades",
      "quote": "I think we'll realistically have AGI within four years. Not decades from now — four years.",
      "start_time": "HH:MM:SS",
      "end_time": "HH:MM:SS",
      "topic": "AGI timelines",
      "video_part": "part01",
      "duration_seconds": 90
    }
  ],
  "total_insights": 8,
  "analysis_timestamp": "2024-01-01T12:00:00Z",
  "aggregation_criteria": "Selected for specificity, intellectual impact, and non-redundancy"
}
```

### Field Specifications
- **rank**: Integer 1 to {max_clips} (1 = most valuable)
- **claim**: Preserve exactly from source — do NOT rewrite
- **quote**: Preserve exactly from source — do NOT rewrite
- **start_time**: Preserve exactly from source (HH:MM:SS or MM:SS)
- **end_time**: Preserve exactly from source (HH:MM:SS or MM:SS)
- **topic**: Preserve exactly from source
- **video_part**: Preserve exactly from source
- **duration_seconds**: Preserve exactly from source

## IMPORTANT: JSON Response Format
- Return ONLY valid JSON, no additional text or explanations
- Preserve all original field values — do NOT alter timestamps, quotes, or claims
- Do not include trailing commas
- Verify JSON syntax before responding