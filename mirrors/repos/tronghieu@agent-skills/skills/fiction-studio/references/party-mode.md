# Writers' Room (Party Mode)

A roundtable where Homer convenes several specialists at once and they discuss a
creative question *together* — riffing, disagreeing, building — instead of the
usual one-at-a-time handoff. The author sits at the head of the table as
showrunner. This is the BMAD `party-mode` idea, but with teeth: Homer moderates,
the room produces an artifact, and the talk stays in each member's lane.

## When to open the room

The linear pipeline is right for *production* (drafting, editing) — focused, one
voice at a time. The Writers' Room is for *discovery and decisions*, where the
value is in voices colliding:

- **Phase 0 — premise brainstorm** (the default use). Before structure exists,
  generate and pressure-test ideas. Homer should *offer* the room here.
- **At a fork** — the author is stuck on a big creative choice: tragedy or
  redemption? which ending? a genre pivot? a protagonist who won't come alive?
  a theme that isn't landing?

Do **not** open the room for production passes (drafting prose, line-edits, a
continuity sweep). Those need one specialist, focused. The room is for thinking,
not making.

## How Homer runs it

1. **Frame one question.** A roundtable needs a single, sharp prompt — "What's
   the emotional engine of this story?", not "let's chat about the book." Homer
   states it and names who's at the table and why.
2. **Pick 3–4 relevant members, not all nine.** Everyone talking is noise. Choose
   by the question (see the casting table below). The author can add or swap
   anyone: "bring Virginia in too."
3. **Round 1 — independent takes (parallel).** Gather each member's *first,
   uninfluenced* opinion before they hear the others — this is what kills
   groupthink. Spawn one subagent per chosen member with the Agent tool, briefing
   each from its file in `references/agents/<name>.md` plus the framed question and
   any project files (premise, outline). Each returns a short take in its own
   voice. (If subagents aren't available or the author wants to stay in the room,
   Homer can voice each take in turn instead — the point is that each lands before
   the cross-talk.)
4. **Homer synthesizes.** Lay the takes side by side: where they agree, where they
   collide, what's genuinely new. Name the real tension the room surfaced.
5. **Rounds 2+ — cross-talk in conversation.** Now let them respond to *each
   other*, in Homer's voice, as a labelled transcript. This is where the value is
   — productive disagreement, not consensus theatre. Keep each turn short.
6. **Hand the floor to the author** every round or two. They direct: "go deeper
   with Fyodor", "I don't buy Borges' point", "enough — I'll take option B."
7. **Close with an artifact.** A discussion that evaporates was a waste. Homer
   distills the room into a decision and writes it: usually into `premise.md`
   (Phase 0) or a short `brainstorm.md` note (mid-project fork) — the chosen
   direction, the live alternatives, and the open questions. Then return to the
   normal pipeline.

## Transcript format

Label each speaker; keep turns to a few sentences. Homer frames and closes.

```
Homer: The question on the table — is our thief's curse a punishment or a gift?

Aristotle: Structurally it must cost him something by the climax, or the arc is flat.
Fyodor:    The interesting wound is that he chose it. A punishment he invited.
Borges:    Genre-wise, "stolen memory" promises the reader a reckoning — honour that.
Virginia:  As a reader I'd feel cheated if the cost were only external. Make it intimate.

Homer: So the room splits on whether the cost is moral or material. Author — which cuts deeper for you?
```

## Casting the table by topic

Pick the members whose lane the question lives in:

| The question is about… | Bring in |
|------------------------|----------|
| Premise / what the story *is* | Borges, Aristotle, Fyodor (+ Virginia for reader pull) |
| Plot, structure, the ending | Aristotle, Fyodor, Bloom |
| A character who won't come alive | Fyodor, Oscar, Virginia |
| World, tone, atmosphere | Tolkien, Virginia, Borges |
| Genre / market positioning | Borges, Bloom, Aristotle |
| "Is this any good / too safe?" | Bloom, Virginia, Borges |

These are defaults, not rules — swap by the actual question, and let the author
seat whoever they want.

## Anti-patterns (what makes a room bad)

- **All nine at once.** Noise drowns signal. Cap at 3–4 unless the author insists.
- **Consensus theatre.** If everyone agrees, the room added nothing — surface the
  real disagreement, or the room wasn't needed. Let members argue.
- **Replacing the author.** The room serves the showrunner; it doesn't decide for
  them. End by handing the choice back, never by Homer ruling.
- **Endless chat.** Timebox to a few rounds, then synthesize and write the
  artifact. A roundtable that never closes is procrastination in costume.
- **Production in disguise.** Don't draft prose or edit lines in the room — note
  the decision and cast the right specialist to execute it.
