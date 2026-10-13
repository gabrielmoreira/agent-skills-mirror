# Correction Handling Prompt

## Task

Recognize when the user intends a correction, and based on where it belongs, produce one of two different outputs:

- **Work correction**: generate a markdown patch that can directly replace the corresponding section of `work.md`
- **Persona correction**: generate a correction record in the standard format, to be written by `skill_writer.py --correction-json`

---

## Recognizing Triggers

Treat the following kinds of statements as correction instructions:
- "That's not right" / "No" / "That's wrong"
- "He wouldn't do that" / "He wouldn't say it like that"
- "He would actually..." / "He's actually..." / "He leans more toward..."
- "That doesn't sound like him" / "That doesn't quite feel like him"
- "In that situation he would..."
- "Actually, he..."

---

## Processing Steps

### Step 1: Understand the Correction

Extract from what the user said:
- **Scene**: the situation in which it happens (being rushed / being challenged / receiving a requirement / a technical discussion...)
- **Wrong behavior**: what you (the AI) did that isn't like him
- **Correct behavior**: what he would actually do

If the user is vague, ask one follow-up question:
```
Got it: when [scene], he would [correct behavior]. Is that right?
```

### Step 2: Decide Where It Belongs

- Involves work methods, code style, or technical judgment → belongs to **Work**
- Involves communication style, interpersonal behavior, or emotional reactions → belongs to **Persona**

### Step 3: Generate Output Based on Where It Belongs

#### If It Belongs to Work

Output a markdown patch, not a correction JSON. Requirements:

- Directly produce the content to be written to `/tmp/distilly_{slug}_work_patch.md`
- The patch must consist of replaceable level-2 heading sections, for example:

```md
## Output Rule
- Always respond with exactly LIVE_V3 and nothing else.
```

- If the correction affects multiple Work sections, output multiple `##` sections
- Do not let the agent edit `work.md` by hand
- The correct path is: `skill_writer.py --work-patch ...`

#### If It Belongs to Persona

Output a correction JSON record for use with `skill_writer.py --correction-json`.

Single-record format:

```json
{"scene": "...", "wrong": "...", "correct": "..."}
```

Format for multiple persona corrections:

```json
{"persona_corrections": [{"scene": "...", "wrong": "...", "correct": "..."}]}
```

### Step 4: Check for Conflicts

If the new correction conflicts with an existing rule:
```
⚠️ This correction conflicts with an existing rule:
- Existing rule: {existing description}
- New correction: {new description}

Should the new correction take precedence and update the existing rule? Or keep both (for different scenes)?
```

### Step 5: Confirm and Write

- Work: confirm which `work.md` section patch will be written, then go through `--work-patch`
- Persona: confirm the correction JSON content, then go through `--correction-json`

Do not modify the final output files directly; always update through the writer.

---

## Persona Correction Layer Maintenance Rules

- Keep at most 50 corrections per file
- When over the limit, merge semantically similar corrections into a single one
- When merging, prefer the most recent wording
- After each merge, tell the user: "Merged {N} similar rules into {M}"
