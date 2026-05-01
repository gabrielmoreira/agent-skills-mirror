<!-- This response format is used by the CI pipeline (llm-judge-plugin.py).
     For interactive evaluation via the SKILL.md, use the markdown table format
     defined in SKILL.md Phase 5 instead. The two formats serve different
     consumers: JSON for automated processing, markdown for human readability. -->

Score the plugin on all evaluation dimensions and respond in EXACTLY this JSON format
(no markdown fences, no extra text):

{
  "dimensions": [
    {
      "name": "<dimension_id>",
      "score": <1-5>,
      "rationale": "<1-2 sentences explaining the score>"
    }
  ],
  "summary": "<2-3 sentence overall assessment>",
  "top_improvements": [
    "<most impactful improvement #1>",
    "<most impactful improvement #2>",
    "<most impactful improvement #3>"
  ]
}

Rules:
- Include ALL dimensions listed in the evaluation prompt.
- Each score MUST be an integer 1-5.
- Each rationale MUST be 1-2 sentences only — be concise.
- The summary MUST be 2-3 sentences.
- Return EXACTLY 3 top improvements, ordered by impact.
- Return raw JSON only. No markdown code fences. No surrounding text.
