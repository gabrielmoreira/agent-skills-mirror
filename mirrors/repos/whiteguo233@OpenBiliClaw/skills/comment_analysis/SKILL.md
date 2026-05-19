---
name: comment_analysis
description: Analyze video comment sections to discover recommended content and gauge content quality.
---

# Comment Analysis Skill

Mine video comment sections for content recommendations and quality signals.

## When to Use

- As part of the content discovery cycle
- To evaluate the quality and reception of discovered content
- To find user-recommended content and UP主 from comments

## How It Works

1. Fetches comments from a video via API or agent-browser
2. Uses LLM to identify:
   - Other video/UP主 recommendations mentioned in comments
   - Overall content quality sentiment
   - Common viewer reactions and highlights
3. Returns structured analysis

## Parameters

- `bvid` (str): Video BV ID to analyze comments for
- `max_comments` (int, optional): Maximum comments to analyze (default: 100)

## Output

- Recommended content/UP主 found in comments
- Quality sentiment score
- Key highlights and reactions
