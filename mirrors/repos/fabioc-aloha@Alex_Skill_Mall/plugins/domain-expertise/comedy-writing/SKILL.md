---
type: skill
lifecycle: stable
inheritance: inheritable
name: comedy-writing
description: Joke structure, comedic timing, set construction, callback patterns, and audience engagement for comedy writers.
tier: extended
applyTo: '**/*comedy*,**/*writing*'
currency: 2026-04-22
lastReviewed: 2026-04-30
---

# Comedy Writing Skill


> Joke structure, comedic timing, set construction, callback patterns, and audience engagement for comedy writers.

## Core Principle

Comedy is an argument with reality. The comedian's job is to find the truth hiding inside the absurd — then deliver it so precisely the audience has no choice but to laugh. Structure enables spontaneity.

## Joke Anatomy

### Setup → Punch

Every joke has two parts:

1. **Setup** — Establishes an assumption (the "first story")
2. **Punch** — Violates the assumption (the "second story")

The laugh happens at the moment the audience's brain resolves the gap between the two stories.

### The Benign Violation Theory

A joke succeeds when something feels:

- **Wrong** (violation) — but not threatening
- **OK** (benign) — but not boring
The sweet spot is the overlap.

## Joke Structures

### One-Liner

- Setup and punch in a single sentence
- Economy of words is everything
- Example pattern: "I used to [setup]. I still do, but I used to, too." — Mitch Hedberg

### Rule of Three

- Two items establish a pattern; the third breaks it
- Pattern: Normal, Normal, Absurd
- The third item does the work — load the funny there

### Callback

- Reference a joke from earlier in the set in a new context
- Creates a "shared history" with the audience
- Best callbacks surprise even the comedian's own earlier setup

### Tag

- Additional punchlines stacked onto the same setup
- Each tag extends the laugh without needing new setup
- Top comics get 3–5 tags per core joke

### Act-Out

- Physical/vocal performance of a character or scenario
- Breaks the "talking head" pattern
- Voice changes, body language, and spatial movement

### Misdirect

- Setup implies one direction; punch goes somewhere unexpected
- Subverts the audience's prediction engine
- Works best when the expected answer is already funny

## Set Construction

### 5-Minute Set Structure

| Segment | Duration | Purpose |
|---------|----------|---------|
| Opener | 30–45s | Establish persona, quick laugh, build trust |
| Chunk 1 | 60–90s | First thematic block (3–5 jokes) |
| Chunk 2 | 60–90s | Second thematic block |
| Chunk 3 | 60–90s | Third thematic block |
| Closer | 30–60s | Strongest material, callback to opener, leave on high |

### Chunk Design

A chunk is a thematic unit (e.g., "dating apps", "airport security", "my family"):

1. **Premise** — The observation or opinion that anchors the chunk
2. **Core joke** — The strongest setup/punch on the premise
3. **Tags** — 2–4 additional angles on the same premise
4. **Transition** — Bridge to next chunk (thematic or callback)

### Set List Notation

- One line per joke (trigger word, not full text)
- Mark tested vs. new material
- Track laughs per minute (LPM) — target: 4–6 for club sets

```json
{
  "set": "Open Mic - The Laugh Factory",
  "date": "2026-04-14",
  "duration_minutes": 5,
  "jokes": [
    { "trigger": "dating apps", "type": "core", "laugh": true, "tags_landed": 2 },
    { "trigger": "airport security", "type": "new", "laugh": false, "notes": "setup too long" },
    { "trigger": "callback: apps", "type": "callback", "laugh": true }
  ],
  "lpm": 4.2
}
```

## Comedic Devices

| Device | Description | Example Use |
|--------|-------------|-------------|
| **Exaggeration** | Amplify to absurdity | Take a real annoyance to its logical extreme |
| **Understatement** | Downplay the significant | Describe a disaster casually |
| **Irony** | Say the opposite of what you mean | Deadpan delivery of absurd statement |
| **Analogy** | Compare unlike things | "Marriage is like a deck of cards..." |
| **Self-deprecation** | Target yourself | Disarms audience, builds likability |
| **Observational** | "Have you noticed..." | Shared experience as comedy fuel |
| **Dark humor** | Find comedy in difficult topics | Requires trust and precise calibration |
| **Absurdism** | Logic in illogical worlds | Commit fully to the impossible premise |

## Timing & Delivery

### Pacing Principles

- **Pause before punch** — Let the setup land, create anticipation
- **Pause after punch** — Let the audience laugh; don't step on laughs
- **Speed up for lists** — Rapid-fire tags build momentum
- **Slow down for act-outs** — Physical comedy needs room to breathe

### Word Economy

- Cut every word that doesn't serve the setup or punch
- Final word of the punch should be the funny word
- Rewrite until the punch is as late in the sentence as possible

## Writing Process

### Generating Material

1. **Premise mining** — List things that annoy, confuse, or delight you
2. **"What's true about this?"** — Find the honest observation
3. **"What if...?"** — Push the truth to its extreme
4. **Write 10 punches** — For every setup, write 10 possible punches; keep 1–2
5. **Edit ruthlessly** — If a joke needs explanation, it's not ready

### Testing & Iteration

- Perform new material at open mics, not headlining shows
- Record every set (audio minimum)
- Track which jokes get laughs, silence, or groans
- A joke isn't "done" until it works 3 times with different audiences
- Kill darlings: if you love a joke but audiences don't, it goes in the drawer

## AI in Comedy — Guardrails

- AI can help with premise exploration and word alternatives, not punchline generation
- Comedian's voice and perspective are the product — AI-generated jokes lack authentic POV
- Use AI for: brainstorming angles, finding synonyms, checking if a premise has been done
- Never use AI to: write final material, replace stage time, generate "crowd work"
- The audience is buying the comedian's brain, not an algorithm's output
