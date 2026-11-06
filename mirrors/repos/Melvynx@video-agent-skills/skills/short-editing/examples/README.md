# Examples: real shorts made with this engine

Six shorts that were edited, rendered and posted with `engine/short.mjs`. Each folder holds what made it:

- `source/spec.js`: the whole edit. Its top comment plans the beats; every time is a SOURCE second of the take.
- `source/*.html`: the motion components (`window.setT(t)`), captured into clips with `short.mjs capture`.
- `words.md`: the transcript with source and short times, so you can read each `at` against the word it lands on.
- `stills/contact.jpg`: the contact sheet of the final short, and `stills/<component>-sheet.jpg` per component. Open them: this is the finish to reach.

The takes, logos, images and captured clips are not included (the spec names them under `assets/`). To learn from an example, read its spec next to its `words.md` and its contact sheet; to reuse a component, copy its HTML into your project's `source/`, change the texts, colors and times, and capture it.

| example | what to take from it | look at |
|---|---|---|
| [skills-montage](skills-montage/) | The smallest complete short (11 s, 4 beats): a `term` that types and fails, a `counter` struck on the word, a `tree` line by line, the payoff with the real logo and a `check`. Start here. | `source/spec.js` |
| [claude-5x-value](claude-5x-value/) | Proof on a real chart: a `tweet`, then a `screen` with zoom keys and rings on the numbers read aloud, a big native `counter` under it for mobile, `bars`, then two funny objects (`ostrich`, `ferrari` vs `starship`). Engine-native only, no HTML. | `stills/contact.jpg` |
| [thinking-orbs](thinking-orbs/) | Hard cuts between full camera (seam 0), split (1160) and paper alone (1920), and every beat an HTML component: animated orbs, a repo card, a grid, chips, a 60 fps meter, the Instagram and TikTok comment CTAs. The reference for `overlay` scenes and `media` with `alpha: true`. | `source/*.html`, `stills/*-sheet.jpg` |
| [find-skills](find-skills/) | A remake of a viral reel, same beats: real-looking UI built in HTML (a skills marketplace page, a leaderboard, a terminal install, a prompt demo, a security scan), composite cards that move as one, dry punch-ins on the link phrases, `cut` for every retake. | `source/spec.js` top comment |
| [insta-skills](insta-skills/) | A story told inside one app: an Instagram DM thread, a competitor's insights, a fetch command in a terminal, a GitHub repo card, a staff badge, then the comment CTA with the word typed in the real comment sheet. | `source/ig-cta.html` |
| [kitchen-composants-premium](kitchen-composants-premium/) | Real captures of a UI library on the paper, a hook already moving on frame 0, a B-roll moment, a link card, and the CTA full camera with the keyword typed in the Reels comments. | `source/link-card.html` |

The usernames in the CTA components are placeholders (`toncompte`): put the creator's own handle, avatar and keyword.
