---
name: bilibili_browse
description: Browse Bilibili pages using agent-browser for visual exploration and DOM interaction.
---

# Bilibili Browse Skill

Use agent-browser to visually browse and interact with Bilibili pages.

## When to Use

- When API access is insufficient for the needed operation
- When DOM/visual context is needed for content evaluation
- When exploring pages that require JavaScript rendering (e.g., comment sections)

## How It Works

1. Uses agent-browser CLI to navigate to Bilibili pages
2. Captures page content, screenshots, or DOM snapshots
3. Extracts relevant information for content discovery

## Parameters

- `url` (str): Bilibili URL to browse
- `action` (str): Action to perform — "read", "screenshot", "interact"
- `selectors` (list[str], optional): CSS selectors to target

## Output

Page content, screenshots, or extracted DOM data.

## Requirements

- agent-browser must be installed: `npm install -g @anthropic/agent-browser`
