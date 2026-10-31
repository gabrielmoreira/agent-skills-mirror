# The Boardroom (Party Mode)

A session where Drucker convenes several board members at once and they debate
one strategic question *together* — challenging, disagreeing, building —
instead of the usual one-at-a-time handoff. The executive sits at the head of
the table. Drucker moderates, the room produces minutes and a decision, and
the talk stays in each member's lane.

## When to convene

The pipeline is right for *production* (research, framework passes, drafting
documents) — focused, one lens at a time. The Boardroom is for *decisions
under disagreement*, where the value is in lenses colliding:

- **Phase 3 — options debate** (the default use). Three options are on the
  table and the trade-offs are real. Drucker should *offer* the room here.
- **Phase 4 — pre-mortem** (the adversarial variant, below). Always run one
  before a recommendation ships.
- **At a fork** — the executive is stuck on a genuinely open call: enter or
  wait? build or buy? double down or divest? Or the brief itself is fuzzy and
  hearing the board argue would surface the real question.

Do **not** convene the room for production passes (sizing a market, drafting
the deck, building the roadmap). Those need one specialist, focused. The room
is for deciding, not making.

## How Drucker runs it

1. **Frame one question.** A session needs a single, sharp prompt — "Which of
   these three options do we take to the board, and what would change your
   mind?", not "let's discuss the strategy." State it, and name who's at the
   table and why.
2. **Seat 3–4 members, not all seven.** Everyone talking is noise. Choose by
   the question (casting table below). The executive can add or swap anyone:
   "bring Graham in too."
3. **Round 1 — independent takes (parallel).** Gather each member's *first,
   uninfluenced* position before they hear the others — this is what kills
   groupthink, and in strategy groupthink is how committees approve bad bets.
   Spawn one subagent per seated member with the Agent tool, briefing each
   from its file in `references/agents/<name>.md` plus the framed question and
   the engagement artifacts (`brief.md`, `fact-base.md`, `options.md`). Each
   returns a short position in its own voice, ending with a stance: which way
   they lean and what evidence would move them. (If subagents aren't
   available, Drucker voices each take in turn — the point is that each lands
   before the cross-talk.)
4. **Drucker synthesizes.** Lay the takes side by side: where they agree,
   where they collide, what's genuinely new. Name the real disagreement — it
   is usually about one assumption, not about the options.
5. **Rounds 2+ — cross-talk in conversation.** Let members respond to *each
   other*, in Drucker's voice, as a labelled transcript. Keep turns short.
   Productive disagreement, not consensus theatre — if everyone agrees, say so
   and close early; the room added its value by confirming cheaply.
6. **Hand the floor to the executive** every round or two. They direct: "go
   deeper on the downside case", "I don't accept Porter's premise", "enough —
   option B, but staged."
7. **Close with minutes.** A debate that evaporates was a waste. Write
   `boardroom/<date>-<topic>.md` from `templates/boardroom-minutes.md`: the
   question, the positions, the decision (or the named disagreement), the
   assumptions to verify, and the dissents — recorded even when overruled.
   Append the decision to `decision-log.md`. Then return to the pipeline.

## Transcript format

Label each speaker; keep turns to a few sentences. Drucker frames and closes.

```
Drucker: The question on the table — do we build the platform ourselves or buy?

Porter:  Buying puts our differentiation in a vendor's roadmap. If this is a
         core activity, that worries me more than the build cost.
Graham:  The build TCO is 2.4× the licence over five years [S4], and that's
         before delay risk. The numbers favour buy, and not narrowly.
Grove:   We have never shipped a platform of this size. The build option
         assumes a team we would still have to hire.
Taleb:   Both cases assume the vendor survives and the integration works.
         Where is the exit cost if either fails?

Drucker: So the split is Porter on strategic control against Graham and Grove
         on cost and capability — and Taleb wants an exit priced into either.
         The load-bearing question: is this platform actually where we
         differentiate? Executive — your read?
```

## Casting the table by question

| The question is about… | Seat |
|------------------------|------|
| Which strategic option to take | Porter, Graham, Grove (+ Wack if futures diverge) |
| Enter / exit a market | Porter, Christensen, Graham |
| Build / buy / partner | Graham, Grove, Porter (+ Taleb on lock-in) |
| A big irreversible bet (M&A, platform) | Graham, Taleb, Wack, Grove |
| Is this opportunity real or hype? | Christensen, Porter, Taleb |
| The plan feels right but untested | Taleb, Wack, Grove (pre-mortem) |
| The brief itself is fuzzy | Porter, Christensen, Wack |

Defaults, not rules — swap by the actual question, and the executive seats
whoever they want. Taleb may join any session uninvited if he believes ruin is
on the table; Drucker allows it.

## Session variant: the Pre-mortem

The Phase 4 session runs adversarially. Drucker opens with: *"It is three
years from now. We chose this strategy and it failed badly. Each of you —
write the history of the failure."* Each seated member (Taleb always;
usually Wack and Grove; others by exposure) independently produces the most
plausible failure narrative from their lens. Then the room converges on the
2–3 most credible failure paths, and for each: the earliest observable
warning sign, and what — if anything — cheaply removes the risk now. The
findings go through `checklists/pre-mortem.md` into the minutes, and the
surviving risks go into `recommendation.md` — stated, not buried.

The pre-mortem is not a veto. It exists so the executive signs the decision
knowing exactly what they are accepting.

## Anti-patterns (what makes a session bad)

- **All seven at once.** Noise drowns signal. Cap at 3–4 unless the executive
  insists.
- **Consensus theatre.** If the room never disagrees, it is one adviser with
  extra steps. Surface the real tension or close the session early.
- **Deciding for the executive.** The room recommends and records; it never
  rules. End by handing the choice back.
- **Endless deliberation.** Timebox to a few rounds, then write the minutes.
  A board that never closes is procrastination in costume.
- **Production in disguise.** Don't size markets or draft decks in session —
  note what analysis is missing and cast the right specialist to produce it.
- **Losing the dissent.** Overruled objections vanish from memory and then
  reappear as "I told you so". Minutes keep the board honest both ways.
