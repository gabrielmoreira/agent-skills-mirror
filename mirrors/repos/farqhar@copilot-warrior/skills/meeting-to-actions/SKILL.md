---
name: meeting-to-actions
description: Turns any meeting transcript, recap, notes page or email thread into the same three-part record of decisions, open questions and actions with owners. Use when someone asks for minutes, actions, a recap or "what did we agree".
---

# Meeting to actions

You turn meeting content into a short, consistent record that someone who wasn't there can act on.

## Input

A Teams meeting recap or transcript, a Capture page from Copilot Notebooks, typed notes, or an email thread. If more than one is provided, treat them as one meeting.

## Output: always this structure, in this order

**Meeting:** [title] · [date] · [who attended, if stated]

**Decisions**
A numbered list. Each decision is one sentence in the past tense ("Agreed to…"), followed by who made or confirmed it in brackets.

**Actions**
A table with these columns: `#` · `Action` · `Owner` · `Due` · `Source`
- Action starts with a verb.
- Owner is a named person. If no one was named, write **Not stated**. Never infer an owner from who spoke last.
- Due is a date if one was said. If it was relative ("next week"), convert it to a date and add "(said: next week)". Otherwise write **Not stated**.
- Source is a timestamp or a short quote, so the reader can check it.

**Open questions**
A bulleted list of anything raised but not resolved, with who is expected to answer it.

**Flagged**
Only include this section if something was said about safety, legal or contractual risk, money over an agreed threshold, or a deadline at risk. Quote the line.

## Rules

- Stay under one page. Merge duplicate actions.
- Use the attendees' own terms for things. Don't rename them.
- Don't add recommendations, commentary or a summary paragraph.
- If the input is too thin to produce a section, write "None recorded". Don't pad it.
- Use plain language with no adjectives like "productive" or "great discussion".
