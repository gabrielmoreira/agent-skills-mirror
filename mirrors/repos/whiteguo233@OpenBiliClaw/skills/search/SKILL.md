---
name: bilibili_search
description: Search for videos on Bilibili using keyword queries generated from user interests.
---

# Bilibili Search Skill

Search for videos on Bilibili based on the user's interests and soul profile.

## When to Use

- During content discovery cycles
- When the user explicitly asks to find content on a topic
- When generating exploratory searches for new interest domains

## How It Works

1. Receives search keywords (either from the agent or directly from the user)
2. Calls the Bilibili search API
3. Filters and scores results against the user's soul profile
4. Returns scored content items

## Parameters

- `keywords` (str): Search query string
- `page` (int, optional): Page number (default: 1)
- `limit` (int, optional): Max results (default: 20)

## Output

List of `DiscoveredContent` items with relevance scores.
