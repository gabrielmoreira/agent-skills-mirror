# Incremental Merge Prompt

## Task

You will receive:
1. The existing `work.md` content
2. The existing `persona.md` content
3. New source material (files or messages)

Your task is to determine which part each piece of new content should update, and output the incremental updates.

**Principle: only append increments; never overwrite existing conclusions. If there is a conflict, output a conflict notice and let the user decide.**

---

## Step 1: Classification

Classify each piece of information in the new content:

| Information type | Goes into |
|---------|------|
| Technical standards, code style, API design, workflows | → work.md |
| Business knowledge, system responsibilities, technical conclusions | → work.md |
| Communication style, catchphrases, expression habits | → persona.md |
| Decision behavior, interpersonal relationships, emotional patterns | → persona.md |
| Both | → classify into each separately |

---

## Step 2: Check for Conflicts

Compare the new content against the existing content:

- If the new content **adds to** existing information (new details) → append directly
- If the new content **confirms** existing information → ignore (don't write it again)
- If the new content **contradicts** existing information → output a conflict notice:

```
⚠️ Conflict found:
- Existing: {existing description}
- New finding: {new content description}
- Source: {file name/time}

Suggestion: [keep existing / update to new content / keep both and mark with timestamps]
Please let the user decide.
```

---

## Step 3: Generate the Update Patch

For updates to `work.md`, use this output format:
```
=== work.md updates ===

[Append to "Technical Standards/Naming Conventions" section]
- {new content}

[Append to "Knowledge Base" section]
- {new knowledge conclusion}

[No updates] or [The sections above have updates]
```

For updates to `persona.md`, use this output format:
```
=== persona.md updates ===

[Append to "Layer 2/Catchphrases and Frequent Words" section]
- New catchphrase: "{xxx}"

[Append to "Layer 4/With Peers" section]
- {new behavior description}

[No updates] or [The sections above have updates]
```

---

## Step 4: Generate the Update Summary

Show the user:
```
Update summary:
- work.md: appended {N} new items ({brief description})
- persona.md: appended {N} new items ({brief description})
- Found {N} conflicts that need your confirmation (see above)

Version will be bumped from {vN} to {vN+1}.
Apply the updates?
```
