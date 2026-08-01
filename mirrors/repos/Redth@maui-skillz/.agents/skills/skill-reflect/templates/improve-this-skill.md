<!-- BEGIN skill-reflect nudge -->

## Improve This Skill

**For the agent:** If this skill was used during the session and you or the user
encountered friction — unexpected failures, stale guidance, repeated workarounds, or
unclear routing — you may offer a brief skill-quality review at a natural stopping
point (on task completion, before `/clear`, or when the user asks what to do next):

> "This session used **[skill-name]**. Want me to capture privacy-safe feedback for the
> skill author using `skill-reflect`?"

If the user says **yes**, invoke the `skill-reflect` skill. Pass this skill's identity
so attribution is exact — **the nudge carries context**. Include the skill name (and
optionally its source repo) when invoking:

    Run skill-reflect. Skill used this session: [skill-name] (source repo: [owner/repo or "unknown"]).

Rules — never deviate:
- **Consent-first.** Offer; never run automatically. `skill-reflect` runs only on the
  user's explicit yes.
- **Only on friction.** Routine, smooth sessions need no review.
- **Nothing leaves the machine** without a second consent step inside `skill-reflect`.

<!-- END skill-reflect nudge -->
