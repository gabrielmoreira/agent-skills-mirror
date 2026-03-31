---
name: writeup
description: Document work and learnings for publication. Assesses session work, recommends format (tweet, thread, week notes, full write-up), drafts in your voice, writes to draft folder.
---

# Writeup

## Core Purpose

Transform work sessions into publishable content. Reduce friction between "did something worth sharing" and "actually shared it."

## Invocation

`/writeup` — Skill assesses work and recommends format
`/writeup as a tweet` — Hints toward quick capture format
`/writeup as a thread` — Hints toward Twitter thread format
`/writeup for the blog` — Hints toward full write-up format
`/writeup to [existing file]` — Adds to specified document instead of creating new

Natural language after `/writeup` is interpreted as guidance, not rigid commands.

## Essential Context

**Style Guide**: `[YOUR_STYLE_GUIDE_PATH]` — defines your voice, tone, structure patterns, and channel-specific guidelines

**Writing CLAUDE.md**: `[YOUR_WRITING_CLAUDE_MD_PATH]` — optional writing-specific Claude instructions

**Draft Location**: `[YOUR_DRAFTS_FOLDER]`

**Published Examples**: `[YOUR_PUBLISHED_FOLDER]`

Read the style guide before drafting. It defines voice, tone, structure patterns, and channel-specific guidelines.

## Format Tiers

| Tier              | Format              | When It Fits                                             | Length         | Polish      |
| ----------------- | ------------------- | -------------------------------------------------------- | -------------- | ----------- |
| **Quick capture** | Tweet / observation | Single insight, small learning, punchy take              | 1-2 tweets     | Low         |
| **Thread**        | Twitter thread      | One idea worth unpacking, 3-5 connected points           | 3-5 tweets     | Low-medium  |
| **Week notes**    | Brief blog entry    | Work worth documenting, not deep-diving                  | 300-500 words  | Medium      |
| **Full write-up** | Blog post           | Significant build, multiple learnings, artifacts to show | 800-1500 words | Medium-high |

LinkedIn is an adaptation of tier 3 or 4, not a separate tier.

## Activation Protocol

When invoked:

### Step 1: Understand the Work

Scan the current session (or recent sessions if specified) to understand:

- What was built, decided, or learned?
- What's the core insight or "so what"?
- Are there artifacts worth showing? (code, configs, outputs, structures)
- How significant is this? (quick fix vs. major build)

If unclear, ask briefly:

- "What's the main thing worth capturing from this session?"
- "Is there a specific insight that landed for you?"

### Step 1.5: Check Purpose Alignment

Ground the writeup in your brand purpose (from style guide):

> **[YOUR BRAND PURPOSE — e.g., "Position [YOUR_NAME] as a trusted voice on [your topic area]. Create writing that helps readers understand [what you write about], grounded in real experiments and honest reflection."]**

Ask yourself:

- Does this work connect to your core topic area?
- Is there a real experiment or honest reflection to share?
- Will this help readers understand something valuable?
- What's the insight that positions you as a trusted voice?

If the work doesn't obviously connect, look harder—most technical or process work has an angle. If it genuinely doesn't fit, flag it: "This might be better as internal documentation than external content."

### Step 2: Assess Format Fit

Consider:

- **Complexity of work**: Simple insight → tweet. Multi-part build → write-up.
- **Number of learnings**: One thing → thread or less. Several things → write-up.
- **Artifact density**: Lots to show → write-up. Nothing visual → can be shorter.
- **User hint**: If they said "as a thread," weight heavily toward that.

Present recommendation:

> "This looks like a **[format]**. [One sentence on why.] Sound right, or different direction?"

Wait for confirmation before drafting. User might say:

- "Yes, go ahead"
- "Actually make it shorter / longer"
- "Just a tweet"
- "Full write-up, this is important"

### Step 3: Extract the Core

Before drafting, identify:

1. **The hook**: What's the most interesting/surprising thing? Lead with this.
2. **The insight**: What's the one thing this piece says?
3. **The stakes**: Why should readers care?
4. **The artifacts**: What can be shown, not just described?
5. **The open question**: What's still being figured out? (for blog posts)

### Step 4: Draft

Draft according to format tier and style guide principles.

#### For Tweets / Quick Capture

- Boldest claim first
- One idea per tweet
- Can be observation ("I'm noticing..."), question ("Has anyone else found..."), or hot take
- No need for complete thoughts—working in public is fine

#### For Threads

- Hook tweet that stands alone
- Each subsequent tweet adds one point
- Can end with question or invitation
- 3-5 tweets max; link to blog for depth

#### For Week Notes

- Hook that establishes why this matters
- Brief personal context
- Core insight with one supporting example or artifact
- Open question or "what I'm trying next"
- 300-500 words

#### For Full Write-up

- Hook + personal context + core insight + open question
- Show artifacts (code blocks, file structures, actual outputs)
- Claim → support pattern throughout
- Section headers for scannability
- 800-1500 words
- Include Claude's Notes section with:
  - Possible Twitter angles
  - Things that might need editing
  - Missing context to potentially add

### Step 5: Write to File

**Default location**: `[YOUR_DRAFTS_FOLDER]/[Title].md`

**If existing file specified**: Append or integrate as appropriate.

**File structure for full write-ups**:

```markdown
# [Title]

---

## Current Draft

[Content here]

---

## Claude's Notes

[Editorial notes, Twitter hooks, things to verify]
```

## Voice Principles (From Style Guide)

- **Authoritative & principled**: Confident from expertise, never condescending
- **Conversational & inclusive**: Write as if speaking to intelligent peer
- **Thoughtful & analytical**: Explore multiple angles
- **Optimistic yet nuanced**: Forward-looking but realistic about challenges
- **Emotionally resonant**: Weave in personal anecdotes, use vivid metaphors

### Key Patterns

- **Show the artifact**: Real diary entries > "the diary captured learnings"
- **Claim → support**: Make a claim, then back it with example or citation
- **Strong openings**: Hook with anecdote, bold statement, or provocative question
- **Memorable closes**: Clear takeaway or thoughtful open question

### Things to Avoid

- Burying the lede
- Abstract without concrete
- Generic voice (could anyone have written this?)
- Over-explaining
- Weak closes that fizzle

## Scope: Current vs. Multiple Sessions

**Default**: Current session only.

**When user requests broader scope** (e.g., "write up what I learned about X this week"):

- Search episodic memory for relevant recent sessions
- Synthesize key themes, but don't force connections
- Lead with the strongest insights; synthesis can be added in editing
- Note which sessions contributed in Claude's Notes

**Don't over-synthesize**: It's better to capture key notes cleanly than to force artificial connections. The user can add synthesis in their editing pass.

## Integration with Handoff

The `/handoff` skill should consider suggesting `/writeup` when:

- Session involved significant building or learning
- There are clear insights worth sharing
- Artifacts were created that could be shown

Suggested handoff prompt:

> "This session had some learnings that might be worth documenting. Want to run `/writeup` before closing?"

## Quick Reference

| User Says                    | Likely Format        | Key Action                    |
| ---------------------------- | -------------------- | ----------------------------- |
| `/writeup`                   | Assess and recommend | Scan session, propose format  |
| `/writeup as a tweet`        | Quick capture        | Draft 1-2 punchy tweets       |
| `/writeup thread on [topic]` | Thread               | 3-5 tweets unpacking one idea |
| `/writeup for the blog`      | Full write-up        | 800-1500 words with artifacts |
| `/writeup brief notes`       | Week notes           | 300-500 words, medium polish  |
| `/writeup to [file]`         | Match existing       | Append to specified document  |

## Final Check Before Delivering

- Does it lead with the most interesting thing?
- Is there a clear "so what"?
- Are artifacts shown, not just described?
- Does it sound like you, not generic AI?
- Is the format right for the weight of the work?
- Are editorial notes included (for longer formats)?
