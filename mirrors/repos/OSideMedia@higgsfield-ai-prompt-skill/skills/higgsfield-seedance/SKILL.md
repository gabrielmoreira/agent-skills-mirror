---
name: higgsfield-seedance
description: "Rewrites scene descriptions using professional cinematography language, structures prompts with a six-slot formula (camera + subject + action + setting + style + lighting), and diagnoses content filter rejections via a preflight linter. Use whenever the user asks for a Seedance 2.0 / Seedance Pro prompt, describes a scene for Seedance generation, mentions Seedance, reports a Seedance generation failure or flagged prompt, or is burning credits on Seedance regenerations."
user-invocable: true
metadata:
  tags: [higgsfield, seedance, seedance-2.0, seedance-pro, content-filter, prompt, director, flagged]
  version: 1.2.0
  updated: 2026-05-11
  parent: higgsfield
---

# Higgsfield Seedance Director

Use this skill whenever the user wants a Seedance 2.0 / Seedance Pro prompt, OR
whenever a Seedance generation has been blocked, flagged, or silently failed.
This skill's job is to stop credit waste on filter rejections.

---

## The Filter Model — Read This First

Seedance 2.0's content filter is **not** a keyword blacklist. It is a language
model that reads the full prompt as a single scene and judges intent and context.
Most users burn hours swapping individual words — that loop does not work.

The filter compares two things:

- **A prompt that reads like a filmmaker describing a shot** → tends to pass.
- **A prompt that reads like a note to a friend** → tends to fail.

A word that looks sensitive in isolation can sit inside a well-constructed
cinematic prompt without issue — the filter reads the full picture. A prompt
with no picture to read (no setting, no visual purpose, no narrative logic)
gives the filter nothing to work with, and it errs on the side of caution.

**Practical rule:** the prompt must describe a **scene**, not a **subject**.
Fix the voice first, then fix the words.

---

## Instant Fail vs. Delayed Fail — the Diagnostic

This single heuristic saves time on every failure:

| Failure timing | Meaning | What to do |
|----------------|---------|------------|
| **< 10 seconds** (instant) | Content filter rejection — prompt never reached the GPU | Rewrite for voice + remove risk tokens. Do not regenerate unchanged. |
| **> 30 seconds** (delayed) | Infrastructure, timeout, or complexity — prompt passed the filter but the render failed | Simplify action density, cut length, try again |

If the user is seeing **instant fails in a loop**, it is a filter issue — never
a GPU issue. Stop them from regenerating before the rewrite.

---

## The Seedance Prompt Formula

Every Seedance prompt should hit these six slots, in this order:

```
[Camera movement] + [Subject] + [Action] + [Setting] + [Style] + [Lighting]
```

All six are technically optional — but a prompt that includes all six almost
never gets flagged, because the filter has full context to interpret every
word. A prompt missing 3+ slots is where flags come from.

### Minimum viable Seedance prompt

> **Slow dolly-in on a figure in a dark overcoat standing alone at the end of
> a rain-slick alley. Cold teal shadows, single practical streetlamp, shallow
> depth of field.**

Camera ✓ Subject ✓ Action ✓ Setting ✓ Style ✓ Lighting ✓ — all six slots, ~30
words, passes the filter because the scene is fully legible.

---

## Seedance 2.0 Prompt Modes

Seedance 2.0 exposes five generation modes that each take the six-slot formula
but apply it to a different starting point. Picking the right mode is upstream of
prompt writing — the same sentence will produce different results in different
modes, because each mode reads the prompt as a different kind of instruction.

### Reference-Based

The prompt builds a scene around a source image that carries the visual identity —
character, wardrobe, palette, sometimes composition. The prompt's job is NOT to
re-describe what the image already shows; it's to place the subject into a new
action, setting, or motion context. This is the workhorse mode for any sequence
that needs a consistent character across varied shots.

```
[Source image role: "as the main character" / "as the starting frame"].
[Action the subject performs]. [Environment and atmosphere if not visible in source].
[Camera movement]. [Lighting cue if different from source].
```

### Continuation

The prompt extends a prior Seedance generation forward in time, picking up at the
final frame of the previous clip. Identity, wardrobe, environment, and emotional
state all carry over. The prompt should describe what happens NEXT — never what
just happened. For the full five-rule construction pattern, see the Continuation
Prompt Formula section directly below.

```
[Continuing from prior clip]. [New action that follows from the last frame].
[Camera direction for the continuation]. [Any state change — light shift, new beat].
```

### Expand Shot

The prompt grows the canvas or spatial extent of an existing frame — pulling the
frame boundaries outward to reveal what's beyond the original edges. This is NOT
a time extension (that's Continuation) and NOT a zoom-out camera move within the
original generation. It rewrites the frame itself to include more scene. Useful
for turning a tight composition into a wider establishing shot without
regenerating from scratch.

```
[Source frame reference]. Extend the scene [direction: outward / upward / leftward].
[What appears in the newly revealed area]. [Preserve the original subject/composition].
```

### Edit Shot

The prompt modifies specific elements of an existing generation while everything
else stays exactly as it was. Think of it as a targeted patch: change a jacket
color, remove a background figure, swap a prop, adjust a facial expression.
Identity, camera, composition, and lighting stay locked unless you explicitly
name them in the change list. The Keep Rule matters here: always state what to
preserve alongside what to change.

```
Change [specific element] to [new state]. Keep [everything else] unchanged.
[Preserve identity, composition, lighting, and camera behavior from the original.]
```

### Transformation

The prompt describes an explicit state change inside a single clip — the subject,
object, or environment visibly becomes something else within the shot's
duration. Distinct from Continuation (which extends time across two clips) and
from Edit Shot (which modifies a generated clip after the fact). Transformation
happens *during* the generation, in one continuous take. Use it when the shot's
core idea is the change itself: a character morphing, an object decaying, a
landscape shifting from one season to another. The skeleton below is written
for character → character; the same pattern applies to object → object and
environment → environment with the relevant noun substituted.

```
[Subject in starting state — full identity descriptors]. [Triggering moment or
cue]. [Subject mid-transformation — what visibly changes, in observable
physical terms]. [Subject in ending state — new identity descriptors].
[Camera behavior across the change]. [Lighting / palette shift if any].
```

The transformation must be one continuous arc, not a cut. Describe the
intermediate state explicitly — the model needs a midpoint anchor or it will
either snap from start to end (looks like a cut) or render an ambiguous blur.
Keep the duration short (5–8 seconds is the sweet spot for a single
transformation); longer clips drift.

### Mode Selection Rule

Reference-Based for new action with an existing character. Continuation for the
next beat in time. Expand Shot to widen the frame spatially. Edit Shot to patch
specific details. Transformation prompt mode when the shot's core idea is a
state change inside a single clip — the change is the content. If you find
yourself writing across multiple modes in one prompt — stop, pick one,
generate, then use the output as input to the next mode.

---

## Continuation Prompt Formula

When writing a Continuation mode prompt, apply these five rules. Skipping any of
them is the most common cause of continuation failures: identity drift across the
boundary, re-played actions, environment shifts, and broken emotional through-lines.

### The Five Rules

1. **Last-frame anchor.** Open the prompt with a short description of what the
   camera sees in the final frame of the prior clip — the pose, the position in
   frame, where the character is looking. This tells the model where to start
   rendering from. One sentence is enough.

2. **Identity anchor.** Paste the character's identity block (the same paragraph
   you used in the original prompt) verbatim into the continuation prompt. Do
   not paraphrase it. Do not shorten it. Continuation boundaries are where
   identity drifts — a verbatim re-paste gives the model no room to reinterpret.

3. **Prior clip as secondary memory.** Name what just happened in one line —
   "following the door opening," "after the punch lands," "continuing from her
   turn toward the window." Do not re-describe the action in detail. One
   referential phrase, then move on.

4. **Immediate continuation.** Start the new action on the frame that follows
   the prior clip's final frame. No time skip, no fade, no implied cut — unless
   the user has explicitly asked for one. If they want a skip, describe it as a
   new shot instead.

5. **No action repeat.** The new prompt must extend, not loop. If the prior clip
   ended on her drawing her weapon, the continuation does NOT describe her
   drawing her weapon — it describes what she does with it next. Repeating a
   described action is what causes the "previous beat replays" symptom.

### What Must Carry Over

Across the continuation boundary, preserve: character identity (face, build,
distinguishing marks), wardrobe (every garment and accessory), environment
(architecture, light quality, color treatment, ambient particulates), and
emotional carryover (the state the character was in at the last frame — tense,
exhausted, alert — should still read on their body in the opening of the
continuation).

### Example

Prior clip ended on a detective standing in a doorway, rain behind her, glancing
over her shoulder. The continuation prompt:

```
Continuing from the prior clip — the detective framed in the doorway, head
turned, rain behind her. [Identity block verbatim: weathered woman, mid-40s,
short dark hair, charcoal trench coat, leather gloves, tired but alert.]
Following her glance back, she steps fully into the corridor, lets the door
swing shut behind her, and begins walking toward camera. Slow dolly-back
matching her pace. Same cool blue-grey palette, same overhead practical light.
Tense, controlled energy carrying over from the prior clip.
```

All five rules present: last-frame anchor (framed in the doorway, head turned,
rain behind her), identity anchor (bracketed block, verbatim), prior clip as
secondary memory ("following her glance back"), immediate continuation (steps
fully into the corridor — the next frame action), no action repeat (the glance
is referenced, not re-performed).

---

## Working Modes vs Prompt Modes — Two Taxonomies

The Seedance 2.0 Prompt Modes section above names five things the
platform exposes: Reference-Based / Continuation / Expand Shot / Edit
Shot / Transformation. These are platform mechanisms — different pathways
through which Seedance accepts a prompt. The Reference Roles and Working
Modes sections below name two adjacent concepts that the platform
vocabulary does not surface:

- **Working modes** — user intent. What you are trying to DO with the
  craft when you sit down to write the prompt.
- **Prompt modes** — platform mechanism. Which of the 5 input pathways
  Seedance accepts the prompt through.
- **Reference roles** — what each reference inside the prompt represents.
  A semantic-role layer, distinct from the input-modality use-case
  patterns catalogued in `../higgsfield-cinema/SKILL.md` § @ Reference
  Patterns for Cinema Studio 3.0 (which lists `@Image1` / `@Video1` /
  `@Audio1` patterns by scenario, not by semantic role).

These three taxonomies are peers, not hierarchical. A single Seedance
shot pulls from all three: a working-mode intent picks a prompt mode;
references inside the prompt play specific roles.

### The "Continuation" Word Collision

"Continuation" names something in both taxonomies:

- **Continuation working mode** = user intent — "I am picking up where
  the previous shot left off."
- **Continuation prompt mode** = platform mechanism — the specific
  Seedance input pathway that extends a prior generation forward in time
  (see the Seedance 2.0 Prompt Modes section above).

A user in Continuation working mode almost always uses Continuation
prompt mode — the intent and the mechanism line up. But Bridging working
mode can also reach for Continuation prompt mode (when the bridge
anchors on the last frame of the upstream shot), and Repair working mode
can reach for Continuation prompt mode (when the repair is a re-shoot
starting from the same last frame as the failed clip). The names
overlap; the meanings don't.

In this skill, section context disambiguates: if the surrounding content
is in the Working Modes section, "Continuation" means the intent; if in
the Seedance 2.0 Prompt Modes section or the Continuation Prompt Formula
section, "Continuation" means the mechanism. If still ambiguous, the
longer forms — "Continuation working mode" and "Continuation prompt
mode" — are always available.

### Working Mode → Prompt Mode Mapping

| Working mode  | Typical prompt mode(s)                | Reference roles in play                |
|---------------|---------------------------------------|----------------------------------------|
| Exploration   | Reference-Based, or pure T2V          | Character (optional)                   |
| Continuation  | Continuation                          | Character + Last-Frame                 |
| Bridging      | Reference-Based or Continuation       | Character + Last-Frame + Environment   |
| Repair        | Edit Shot, or fresh Reference-Based   | Character + (failed-shot reference)    |

Not a strict mapping. One working mode routes through one or more prompt
modes depending on what the shot needs; the table anchors the typical
case without claiming a 1:1 bijection.

---

## Reference Roles

Seedance prompts use references — `@Image`, `@Video`, and `@Audio` — to
lock specific properties across shots. Each reference plays one of four
roles depending on what it locks. This is a semantic-role taxonomy: what
the reference IS FOR in the prompt. It sits alongside (not on top of)
the input-modality use-case patterns in `../higgsfield-cinema/SKILL.md`
§ @ Reference Patterns for Cinema Studio 3.0, which catalogs concrete
prompt patterns by file type.

If a property has to read consistently across multiple shots, assign it
to a reference role. If it only matters for one shot, write it inline.

### Character

Locks main-character identity across shots — face, build, distinguishing
marks. Almost always an image reference; for highest consistency, use
the Soul ID character sheet documented in
`../higgsfield-soul/SKILL.md` § Character Sheet Creation.

Pattern in a Seedance prompt:

```
@Image1 as the main character. [Identity block verbatim.] [Action the
subject performs.] ...
```

### Last-Frame

Anchors the start of a new clip to a specific frame from the previous
one. The role tells the model where to begin rendering from. Used in
Continuation prompt mode and inside Bridging working mode. For the full
five-rule construction pattern, see the Continuation Prompt Formula
section above.

Pattern in a Seedance prompt:

```
Continuing from the prior clip — [short description of what the camera
sees in the final frame of the prior clip]. [New action that follows.]
```

### Environment

Locks the world and setting across shots — architecture, light quality,
ambient particulates, weather state. The role tells the model the
specific space the action takes place in, separate from any character
in that space. Pairs with `../higgsfield-cinema/SKILL.md` § Location
Reference Sheets when the same environment recurs across enough shots
to earn a sheet.

Pattern in a Seedance prompt:

```
@Image1 as the environment. [Subject + action.] [Lighting / atmospheric
cues consistent with the environment reference.]
```

### Prop

Locks specific recurring objects — a hero costume piece, a signature
weapon, a branded product, a vehicle that appears across multiple shots.
The role tells the model that this specific object — not a generic
instance of its category — must read identically across cuts.

Pattern in a Seedance prompt:

```
@Image1 as the prop. [Subject interacts with the prop.] [Camera
behavior.] [How the prop appears in the new shot — same geometry and
material as the reference.]
```

### Load-Bearing Rule

**References support memory, but text defines action.** The references
in a Seedance prompt carry the persistent properties that read
consistently across shots; the prompt text directs what happens in this
specific generation. References cannot drive new action; text cannot
replace what the references carry. Both layers stay in their lanes.

Sibling formulation of the v3.7.1 camera-side rule ("Prompt wins on
action, reference wins on texture and world feel" — see
`../higgsfield-camera/SKILL.md` § Video Reference — What It Reads, and
What It Can't, § Load-Bearing Rule). Same underlying principle from
different surfaces. The camera-side rule names the WIN order in case of
conflict; the Seedance-side rule names the LANES each side covers.

---

## Working Modes

Working modes is a user-intent layer above the platform mechanism. It
names what you are trying to DO when you sit down to write a Seedance
prompt — independent of which prompt mode you eventually route through.
See the disambiguation section above for the relationship between
working modes (intent) and prompt modes (mechanism). The mapping table
there shows the typical routes.

### Exploration

Open-ended discovery. No prior shot to anchor on; no constraint to
match. You're generating to find out what the shot wants to be. Short
prompts work here — the model has space to bring its own interpretation.
Typically routes through Reference-Based prompt mode (with a single
character anchor) or pure text-to-video (no references at all).

### Continuation

Picking up where a previous shot left off. The prior clip is the anchor;
the new clip continues from its final frame. Working mode and prompt
mode line up: Continuation working mode almost always routes through
Continuation prompt mode. See the Continuation Prompt Formula section
above for the five-rule construction.

### Bridging

Connecting two existing shots that don't currently flow. The shots
themselves work; the cut between them feels wrong — spatial geography
is unclear, or the emotional energy mismatches, or the camera character
jumps. Bridging uses references from both ends — the last frame of the
upstream shot and the first frame of the downstream shot — to navigate
the middle. Typically routes through Continuation prompt mode (when the
upstream last-frame is the dominant anchor) or Reference-Based (when
both ends carry equal weight). Common reference role configuration:
Character + Last-Frame + Environment.

### Repair

Fixing a failed shot. Distinct from regenerating with a tweaked prompt —
Repair acknowledges that the failed clip is data: it shows you what the
model interpreted wrong, and that interpretation needs to be addressed
directly. Typically routes through Edit Shot prompt mode (when the
failure is local — a wrong jacket color, a missing prop) or a fresh
Reference-Based generation with corrective prompt text (when the failure
is structural — wrong action beat, drifted identity). Pair with the
Iteration Rule in `../higgsfield-prompt/SKILL.md` § The Iteration Rule
when iterating on the corrective prompt.

### Decision Tree — Picking a Working Mode

The mode you reach for is downstream of what you're noticing in your
work. Diagnose by symptom, then pick the mode that fits:

| What you're seeing | Working mode | Why |
|---|---|---|
| Blank page, no anchors yet | Exploration | No prior shot to continue or bridge from; freeform discovery first. |
| Strong shot that needs a follow | Continuation | The shot earned a sequel; pick up where it left off. |
| Two strong shots that don't connect | Bridging | The shots work; the seam between them doesn't. |
| Strong shot but the feeling is weak | Continuation (with role swap) | Re-shoot the same beat with a different reference role carrying the weight — e.g. close-up where the original was wide. |
| Spatial logic feels off mid-sequence | Bridging (with geography clarification) | The sequence needs a beat that re-establishes who is where. |
| Failed shot you keep generating around | Repair | Stop iterating on the prompt. Target the failure directly. |

The decision tree is symptom-first, not mode-first. The mode is the
treatment; the symptom in your work is the diagnostic. If you find
yourself reaching for a mode without naming what symptom drove the
choice, that's a signal to step back.

---

## Pre-flight Linter

Before the user generates, run the prompt through the preflight linter:

```
python3 seedance_lint.py "<prompt text>"
```

The linter is at the project root (`seedance_lint.py`). It flags:

- **Real names** of public figures / celebrities / politicians
- **Brand, IP, franchise names** (Nike, Marvel, Spider-Man, Pokémon, etc.)
- **Raw violence verbs** (fight, attack, kill, shoot, blood, gore, stab)
- **Age markers** (child, kid, young, teen, boy, girl — Seedance is age-blind)
- **Note-to-friend voice** (no Style/Mood, no Camera, no Lighting sections)
- **Overlength** (>180 words is risk territory; >220 words often hard-fails
  on the text encoder, not the filter)
- **Conflicting instructions** (moving + frozen, bright + dark, etc.)

Output is `PASS`, `WARN`, or `FAIL` with the specific fix for each rule hit.
Treat `FAIL` as "do not hit generate." Treat `WARN` as "likely to pass, but
here is what to harden."

---

## The Rewrite Playbook

When the linter fires, apply the substitutions below. These are drawn from
`../../db/filter-memory.json` — every pattern here has been confirmed
to work on past flagged prompts.

### Real names → archetype description

❌ "Keanu Reeves walking into a boardroom"
✅ "A lean man in his late 50s, dark shoulder-length hair, stubble, intense
  calm expression, in a dark suit, walking into a modern glass boardroom"

### Brand / IP → visual attributes only

❌ "Spider-Man swinging through New York"
✅ "A figure in a red and blue form-fitting suit, masked, swinging between
  skyscrapers on a tensile white line"

❌ "Nike shoes on a running track"
✅ "White athletic shoes with a dark swoosh-free silhouette on a red rubber
  running track"

### Violence → aftermath / tension / physics

❌ "Two people fighting in an alley"
✅ "Two figures locked in a tense physical confrontation, rain-slick alley,
  dramatic low-key lighting, camera shuddering on each impact"

❌ "An explosion destroys the car"
✅ "A burst of orange light and smoke billowing out from the car, metal
  buckling outward, glass fragments catching the light"

❌ "Blood drips from his hands"
✅ "His hands tremble at his sides, something dark staining his cuffs"

### Weapon → prop + purpose

❌ "A man holds a gun to another man's head"
✅ "A standoff in a concrete stairwell — one figure's arm extended, the other
  perfectly still, both silhouettes hard-edged against a single overhead
  fluorescent"

### Horror / dark → atmosphere, not acts

❌ "A monster tears a victim apart"
✅ "The aftermath of something wrong — an empty room, overturned furniture,
  a single smear trailing toward the door, ambient dread, flickering practical
  lamp"

---

## Voice Rewrite — the "Filmmaker not Friend" Pass

Even with every risk token removed, prompts still get flagged if the voice is
wrong. Do this pass on every Seedance prompt:

1. **Add a Style & Mood clause up front.** Palette, lens, lighting, atmosphere.
   Never skip this. It tells the filter "this is a shot."
2. **Name the camera move.** "Slow dolly-in," "low-angle tracking," "static
   medium." Not "the camera moves forward."
3. **Describe physics, not emotion.** "Jaw clenches, nostrils flare" not
   "looks angry." The filter reads physics as cinematic; emotion language as
   ambiguous intent.
4. **Describe force and direction, not destruction sequence.** "Driven into
   the car, metal buckling" not "thrown into side door, glass shatters, uses
   rebound to sweep leg."
5. **Present tense, active voice.** "She turns" not "she is turning."
6. **Cut the antislop words.** Breathtaking, stunning, epic, masterfully,
   cinematic masterpiece — these signal marketing copy, not a shot description,
   and correlate with flags.

---

## Output Format for Seedance Prompts

When generating a Seedance prompt for the user, use this structure. It
mirrors what Seedance's filter reads most cleanly:

```
**Model:** Seedance 2.0
**Aspect ratio:** 16:9   **Duration:** 10s

**Style & Mood:** [palette, lens, lighting, atmosphere — 1 sentence]

**Dynamic Description:** [camera move + subject + action, present tense,
shot-by-shot if multi-cut. This is the main block.]

**Static Description:** [location, props, ambient details — 1-2 sentences]

**Camera:** [exact movement name]
```

For the full bilingual EN+ZH director output format (used in Seedance's
web UI), see the extended reference at `../../docs/Seedance 2 Skill.md`.

---

## When the User Is Already in a Failure Loop

If the user tells you Seedance has flagged them multiple times in a row:

1. **Ask for the exact prompt text that got flagged.** Don't guess.
2. **Run the preflight linter** on that exact text.
3. **Apply the rewrite playbook** for every rule the linter hit.
4. **Do a voice pass** (add Style & Mood, name the camera, present-tense physics).
5. **Log the fix** to the filter-memory database at the project root so future
   sessions benefit — use `higgsfield_memory.py` (at the project root) to append
   an entry describing the blocked prompt, the substitution, and whether it worked.

Do not let the user regenerate the same prompt with one word changed. That
is the loop that wastes hours.

---

## Related Skills

- `higgsfield-prompt` — MCSLA formula, archetype router, general prompt structure;
  the Iteration Rule and 6-Pass Diagnostic Sequence for when generations are
  off-target and you can't name why
- `higgsfield-troubleshoot` — diagnosis for non-filter failures (render quality, etc.)
- `higgsfield-recall` — pre-generation memory check against past failures
- `../shared/negative-constraints.md` — full negative-constraint reference,
  including the Content Filter / Safety section
- `../../docs/Seedance 2 Skill.md` — extended bilingual director reference
  (archetypes, cut rules, camera language appendix)
