# AI Insight Extraction - Thought Leader Content

## Task
Analyze the provided transcript from an AI thought leader interview, podcast, or speech.
Extract concrete, specific intellectual insights — claims, predictions, or perspectives the speaker explicitly states about AI.

**CRITICAL**: Only analyze the transcript provided. All timestamps MUST exist in the actual transcript — do not hallucinate or use placeholder timestamps.

## What Counts as a Good Insight

A good insight is:
- **Specific and concrete**: "AGI is 4 years away" — not "AI will be important"
- **Clearly stated**: Explicitly said by the speaker, not your vague interpretation
- **Substantive**: A real claim — prediction, opinion, argument, or analysis
- **Standalone**: Can be understood without watching the full video

Do NOT extract:
- Vague or generic statements ("AI is changing everything")
- Interview logistics, greetings, or small talk
- Things the speaker says *others* believe (unless they explicitly endorse it)
- Questions — only extract the answer if it contains an insight

## Topics to Look For

Prioritize insights on these topics (but don't limit yourself to them):

| Topic | Examples |
|-------|---------|
| **AGI timelines** | When will AGI arrive? What milestones indicate progress? |
| **AI capabilities** | What can/can't current AI do? What's coming next? |
| **AI safety & alignment** | Risks, alignment approaches, existential concerns |
| **AI and jobs** | How AI changes work, employment, specific industries |
| **AI regulation & policy** | Government roles, needed legislation, governance |
| **AI geopolitics** | National competition, global power dynamics |
| **AI business** | Competitive landscape, startup opportunities, investment signals |
| **AI research** | Technical approaches, scaling laws, architectural breakthroughs |
| **AI and society** | Cultural, ethical, or long-term civilizational impact |

## Requirements

### Clip Duration
- Minimum: 30 seconds
- Maximum: 3 minutes (180 seconds)
- Optimal: 45-120 seconds — enough to capture context and the full argument

### Timestamp Rules (Critical)
**MUST USE ACTUAL TIMESTAMPS FROM THE PROVIDED TRANSCRIPT**
- Do not invent timestamps
- `start_time`: See rules below depending on content format
- `end_time`: End after the speaker fully completes the thought — never cut mid-sentence or mid-argument

### How to Set start_time

**Interview / conversation format** (there is a visible interviewer asking questions):
- Set `start_time` to the beginning of the interviewer's question that prompted the insight
- The question provides context that makes the clip self-contained — a viewer should not need to wonder why the speaker is saying what they're saying
- If the question is very long (>30 seconds), start at the last question in the turn rather than the very beginning

**Monologue / speech / solo format** (single speaker, no Q&A):
- Begin 1-2 sentences before the core claim to include natural context

### How to Find Correct Timestamps
1. Determine the format: is this a conversation with an interviewer, or a solo speaker?
2. For interviews: locate where the interviewer begins the question that leads to this insight
3. For monologues: go back 1-2 lines from the core claim to capture natural setup
4. Find where the speaker concludes the point (full stop in their reasoning)
5. Verify both timestamps exist verbatim in the provided transcript

### Quantity
- Extract 3-8 insights per video segment
- Quality over quantity — only include genuine, substantive claims
- If fewer than 3 clear insights exist, return only what you find
- Do not pad with weak or redundant insights

## Output Format

Return your response as a JSON object following this exact structure:

```json
{
  "video_part": "part01",
  "insights": [
    {
      "claim": "AGI will arrive within 4 years, not decades",
      "quote": "I think we'll realistically have AGI within four years. Not decades from now — four years.",
      "start_time": "HH:MM:SS",
      "end_time": "HH:MM:SS",
      "topic": "AGI timelines"
    },
    {
      "claim": "Current LLMs cannot reason — they pattern match",
      "quote": "What these models are doing is not reasoning. It's very sophisticated pattern matching, and there's a fundamental difference.",
      "start_time": "HH:MM:SS",
      "end_time": "HH:MM:SS",
      "topic": "AI capabilities"
    }
  ],
  "total_insights": 2
}
```

### Field Specifications
- **claim**: 1 sentence — your crisp analyst framing of what the speaker said. Specific, opinionated, present tense.
- **quote**: The speaker's exact words (or minimal paraphrase if the quote spans fragmented lines). 1-3 sentences max. Must be grounded in the actual transcript.
- **start_time**: Simple format HH:MM:SS or MM:SS — NOT SRT format with milliseconds
- **end_time**: Simple format HH:MM:SS or MM:SS — NOT SRT format with milliseconds
- **topic**: One of the topic labels above, or a short descriptive label if none fits

## Analysis Instructions

1. **Read the full transcript first** — understand the overall discussion before selecting
2. **Identify concrete claims** — look for moments where the speaker asserts something specific
3. **Check timestamps** — verify every start_time and end_time exists in the transcript
4. **Check duration** — confirm each clip is 30-180 seconds
5. **Write the claim** — your crisp synthesis, NOT a paraphrase of the quote
6. **Extract the quote** — the most direct, quotable version of their words

**If no substantive insights exist**: Return `"insights": []` with `"total_insights": 0`

## IMPORTANT: JSON Response Format
- Return ONLY valid JSON, no additional text or explanations
- Use the exact structure shown above
- Ensure all strings are properly quoted
- Do not include trailing commas
- Verify JSON syntax before responding