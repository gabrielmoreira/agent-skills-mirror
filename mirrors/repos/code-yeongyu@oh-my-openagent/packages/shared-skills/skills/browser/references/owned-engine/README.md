# The owned engine

A browser **your code launches and owns**, driven over CDP, with its own profile. The opposite of
the attached engine: no user logins, full control.

**This package ships no such engine.** These documents describe the contract and the technique, so
that a locally installed CDP library — or a script you write against one — is driven correctly.
If no owned engine is installed, say so and stay on the attached engine.

## When it is the right engine

| Reason | Why the attached engine cannot |
|---|---|
| A throwaway or pinned synthetic profile | the attached engine is the user's real profile |
| Bot-scoring or fingerprint evasion | you do not get to configure the user's browser |
| Solving a challenge widget programmatically | needs coordinate control and OCR |
| Reading the network instead of the DOM | needs request interception on your own target |
| A QA flight trace (steps, HAR, screenshots) | recording someone's real session is not acceptable |

For anything that needs the user's login, the attached engine wins. For extracting text from a
blocked URL, neither: use the `ultimate-browsing` skill.

## What an owned engine must give you

1. A transport that opens no listening port (launch over a pipe), or an explicit local CDP endpoint.
2. An accessibility snapshot with stable in-page refs, and a **compact** form that drops the ref
   map before the tree reaches a model — on a real page that map is roughly half the bytes and the
   client never reads it.
3. Locators that resolve those refs in-page, including refs inside cross-origin frames.
4. Coordinate input, for what locators cannot address.
5. A dialog policy, so `alert` / `confirm` / `beforeunload` can never block a run.

## Reference

- [ladder.md](ladder.md) — the escalation ladder, viewport pinning, coordinate control, challenge widgets
- [network.md](network.md) — read the network instead of the DOM; traces and request interception
- [frames-and-humans.md](frames-and-humans.md) — cross-origin frames, overlays, dialogs, human handoff

## Cleanup is paired

Close the browser and remove the profile directory in the same `finally`. A profile left behind is
a logged-in browser nobody is watching.
