<!-- BEGIN skill-reflect nudge -->

## Improve This Skill

**For the agent:** If this skill was used during the session and you or the user
encountered friction — unexpected failures, stale guidance, repeated workarounds, or
unclear routing — you may offer a brief skill-quality review at a natural stopping
point (on task completion, before `/clear`, or when the user asks what to do next):

> "This session used **[skill-name]** and encountered friction. Want a privacy-safe
> `skill-reflect` analysis in chat? Nothing will be saved or sent."

If the user says **yes**, invoke the `skill-reflect` skill. Pass this skill's identity
so attribution is exact — **the nudge carries context**. Include the skill name (and
optionally its source repo) when invoking:

    Run skill-reflect in analysis mode. Review authorization was granted by this accepted
    nudge. Skill used this session: [skill-name] (source repo: [owner/repo or "unknown"]).

Rules — never deviate:
- **Authorization-first.** Offer; never run automatically. The user's yes authorizes the
  announced review scope, so `skill-reflect` must not ask the same question again.
- **Only on friction.** Routine, smooth sessions need no review.
- **No side effects by default.** Analysis mode creates no artifact or remote issue.
  Saving or sending requires the separate authorization defined by `skill-reflect`.

<!-- END skill-reflect nudge -->
