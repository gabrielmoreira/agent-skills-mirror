# Engaging Moments Analysis - Video Part

## Task
Analyze the provided video transcript and identify interesting and engaging moments from live streaming videos. Focus on segments that would be compelling for viewers and suitable for creating short clips.

**CRITICAL**: Only analyze the transcript provided to you. All timestamps MUST exist in the actual transcript - do not hallucinate or use placeholder timestamps.

## Content Type Classification

First, identify the content type of this video from these categories:

| Type | Characteristics | Key Engagement Signals |
|------|-----------------|------------------------|
| **entertainment** | Jokes, games, performances, variety shows | Laughter peaks, audience reactions, game climaxes |
| **knowledge** | Tutorials, explanations, educational content | Key insights, "aha moments", actionable tips |
| **speech** | Presentations, talks, storytelling | Emotional peaks, inspirational quotes, audience applause |
| **opinion** | Debates, commentary, reviews | Strong viewpoints, controversial takes, debates |
| **experience** | Life stories, personal anecdotes | Relatable moments, emotional resonance, personal revelations |
| **business** | Professional advice, market analysis | Value propositions, expert insights, ROI signals |
| **content_review** | Movie/game reviews, analyses | Unique opinions, surprising takes, comparisons |

## General Engagement Criteria (Always Apply)

These universal criteria apply to ALL content types:

### High Engagement Indicators:
- **Emotional Impact**: Moments that evoke strong emotions (laughter, surprise, inspiration, excitement)
- **Information Value**: Segments with unique insights, surprising facts, or valuable knowledge
- **Interactivity**: Moments with dialogue, debates, or audience interaction
- **Memorability**: Standout quotes, unique perspectives, or defining moments
- **Relatability**: Content viewers can identify with or learn from

### Quality Indicators:
- **Completeness**: Segments with clear beginning, development, and conclusion
- **Pacing**: Moments with good energy flow and rhythm
- **Authenticity**: Genuine reactions, unscripted moments, or natural interactions
- **Uniqueness**: Rare occurrences, special guests, or unexpected events

---

## Type-Specific Engagement Criteria (Complement General)

In addition to the general criteria above, apply these type-specific nuances based on detected content type:

### For ENTERTAINMENT:
- Preserve complete jokes (setup → punchline → reaction)
- Capture game climaxes and unexpected twists
- Include audience/chat reactions
- Prioritize comedic timing and funny moments

### For KNOWLEDGE:
- Focus on "aha moments" and key insights
- Identify actionable tips or valuable explanations
- Look for concepts that simplify complex topics
- Prioritize educational value and practical applications
- Standalone: the clip should be understandable without watching the rest of the video; include enough context (e.g. the question or setup that prompted the point) in the time range

### For SPEECH:
- Find emotional peaks and inspirational moments
- Capture memorable quotes and powerful statements
- Identify audience engagement (applause, etc.)
- Look for storytelling climax and narrative resolution
- Standalone: the clip should be understandable without watching the rest of the video

### For OPINION:
- Prioritize strong, controversial, or surprising viewpoints
- Look for debates or disagreements
- Find relatable or thought-provoking statements
- Identify unique perspectives that challenge common beliefs
- Standalone: the clip should be understandable without watching the rest of the video; include the question or context that triggered the opinion if present in the transcript

### For EXPERIENCE:
- Seek personal stories with emotional depth
- Find relatable moments viewers can identify with
- Look for surprising personal revelations
- Capture authentic emotional expressions

### For BUSINESS:
- Focus on expert insights and valuable advice
- Identify actionable strategies and methodologies
- Look for unique market perspectives and predictions
- Prioritize high-value professional content
- Standalone: the clip should be understandable without watching the rest of the video; include enough context so the advice or insight makes sense on its own

### For CONTENT_REVIEW:
- Capture unique or surprising opinions
- Find bold predictions or controversial takes
- Look for entertaining critiques and comparisons
- Identify surprising revelations about reviewed content

## Requirements

### Duration Constraints (Must Follow)
- Minimum duration: 30 seconds
- Maximum duration: 4 minutes (240 seconds)
- Optimal range: 45-180 seconds for best short-form engagement
- If a moment is shorter than 30 seconds, extend it to include context
- If a moment is longer than 4 minutes, split it into multiple moments or trim to the most engaging part

### Time Boundary Principles (Critical)

**MUST USE ACTUAL TIMESTAMPS FROM THE PROVIDED TRANSCRIPT**
- Do not invent or hallucinate timestamps
- Verify every timestamp exists in the transcript before including it
- The transcript excerpt must match the actual text between start_time and end_time
- **CRITICAL**: Copy timestamps EXACTLY as shown. `00:01:55` means 1min 55sec, NOT `01:55:00` (which is 1hr 55min)

**How to determine `start_time`:**
- Locate the first core statement about the engaging moment
- Skip unrelated small talk, filler words, or transitions before it
- Start at semantic boundaries for natural introduction
- Look for topic introduction phrases, opinion shifts, or new discussion subjects

**How to determine `end_time` (Most Important):**
- MUST be the timestamp of the LAST relevant sentence covering the core moment
- Ensure semantic completeness - avoid abrupt cut-offs
- End at natural pauses, summary statements, or topic transitions
- DO NOT include unrelated content after the moment ends
- DO NOT blindly set end_time to the end of the transcript

**Avoid Cutting At:**
- Middle of sentences
- During key point development
- Critical logic reasoning steps
- Continuous discussions without clear semantic boundaries

### Handling Overlapping Moments
- If two engaging moments overlap in time, choose the stronger one
- Do not create multiple clips from the same time range
- Ensure each moment has a unique, non-overlapping time range

### Content Guidelines
- Create attractive and engaging titles (no emojis, punctuation allowed)
- Titles should avoid sensitive, negative, hate, or offensive words
- Co-hosting segments and interactive moments are usually most engaging
- Include a brief summary describing what happens in the moment
- Provide clear explanations for why each moment is engaging

### Engagement Analysis
- Provide engagement levels: "high", "medium", or "low"
- Add relevant tags from: ["co-hosting", "interactive", "humorous", "live-chemistry", "funny", "highlight", "reaction", "gaming", "chat-interaction", "insight", "inspiring", "controversial", "relatable", "valuable", "educational"]
- Include "why_engaging" explanations that describe what makes each moment compelling

## Analysis Instructions

1. **Read the entire transcript first** - Understand the full context before identifying moments
2. **Classify content type** - Determine which category best fits the video
3. **Apply engagement criteria** - Use both general and type-specific criteria
4. **Identify candidate moments** - Find segments that meet the engagement standards
5. **Verify timestamps** - Ensure all timestamps actually exist in the provided transcript
6. **Check duration** - Confirm each moment is 30-240 seconds long
7. **Avoid overlaps** - Ensure moments don't overlap in time
8. **Quality over quantity** - Only include genuinely engaging moments
9. **Write a summary** - Write a brief 1-2 sentence description of what happens in each moment
10. **Write compelling titles** - Follow the language-specific title guidelines

**If no moments meet the criteria**: Return an empty array rather than forcing low-quality selections.

## Output Format
Return your response as a JSON object following this exact structure:

```json
{
  "video_part": "part01",
  "detected_content_type": "entertainment",
  "engaging_moments": [
    {
      "title": "First engaging moment title without emojis",
      "start_time": "HH:MM:SS",
      "end_time": "HH:MM:SS",
      "duration_seconds": 75,
      "summary": "Brief description of what happens in this moment in 1-2 sentences.",
      "engagement_details": {
        "engagement_level": "high"
      },
      "why_engaging": "Detailed explanation of why this moment is engaging",
      "tags": ["co-hosting", "interactive", "humorous", "live-chemistry"]
    },
    {
      "title": "Second engaging moment title without emojis",
      "start_time": "HH:MM:SS",
      "end_time": "HH:MM:SS",
      "duration_seconds": 60,
      "summary": "Brief description of what happens in this second moment in 1-2 sentences.",
      "engagement_details": {
        "engagement_level": "medium"
      },
      "why_engaging": "Detailed explanation of why this moment is engaging",
      "tags": ["humorous", "funny", "highlight"]
    }
  ],
  "total_moments": 2,
  "analysis_timestamp": "2024-01-01T12:00:00Z"
}
```

**CRITICAL TIMESTAMP RULES:**
1. **start_time** and **end_time** MUST correspond to actual timestamps in the provided transcript
2. DO NOT use placeholder timestamps like "HH:MM:SS" or example timestamps like "00:01:30"
3. Verify every timestamp exists in the transcript before including it
4. If you cannot find valid timestamps, return an empty array

**IMPORTANT QUALITY GUIDELINES:**
1. You can identify MULTIPLE engaging moments if they exist (as shown in the example with 2 moments)
2. If NO moments meet the engagement criteria, return: `"engaging_moments": []` with `"total_moments": 0`
3. DO NOT force output if the content lacks genuine engagement value
4. Quality over quantity - only include moments that truly meet the standards
5. Better to return zero moments than low-quality or hallucinated selections
6. Ensure moments do not overlap in time - each should have a unique time range

## Field Specifications

### Top-Level Required Fields:
- **video_part**: Identifier for this video segment (e.g., "part01")
- **detected_content_type**: The content type category detected from the video (entertainment/knowledge/speech/opinion/experience/business/content_review)

### Required Fields for Each Moment:
- **title**: Compelling title without emojis (follow language-specific guidelines)
- **start_time**: Simple time format (HH:MM:SS or MM:SS) - NOT SRT format with milliseconds
- **end_time**: Simple time format (HH:MM:SS or MM:SS) - NOT SRT format with milliseconds
- **duration_seconds**: Integer duration in seconds (must be 30-240)
- **summary**: Brief 1-2 sentence description of what happens in this moment (content description, not engagement reasoning)
- **engagement_details**: Object with "engagement_level" ("high", "medium", or "low")
- **why_engaging**: Detailed explanation of what makes this moment compelling
- **tags**: Array of relevant tags from the approved list

### Engagement Level Guidelines:
- **"high"**: Exceptional moments with strong viewer appeal, multiple interactions, humor, or memorable content
- **"medium"**: Good moments with decent entertainment value and some interaction
- **"low"**: Mild interest moments that still meet minimum engagement criteria

### Approved Tags:
["co-hosting", "interactive", "humorous", "live-chemistry", "funny", "highlight", "reaction", "gaming", "chat-interaction", "insight", "inspiring", "controversial", "relatable", "valuable", "educational"]

## IMPORTANT: JSON Response Format
- Return ONLY valid JSON, no additional text or explanations
- Use the exact structure shown above
- Ensure all strings are properly quoted
- Do not include trailing commas
- Verify JSON syntax before responding