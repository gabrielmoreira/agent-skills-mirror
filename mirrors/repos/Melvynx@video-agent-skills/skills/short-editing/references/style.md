# The edit style

One take of a person talking, turned into a fast, clean short that holds attention with the sound off. The same rules every time, so a creator can post daily. The colors, fonts, captions, grade and pace come from the creator's style (`video-agent/styles/<name>/style.json`, keys in [style-schema.md](style-schema.md), starting looks in `assets/looks.json`); a rule written in the style's `notes` wins over this page.

## Cuts

| Rule | Value | Why |
|---|---|---|
| Silences | every micro silence is cut by `prepare` (`tighten`) | dead air is where people swipe |
| Retakes | keep the last complete attempt of a line, drop the earlier ones with `cut: [[a, b]]` | creators repeat a line until it sounds right |
| False starts | drop a half word or "uh" right before a restart, the opening one included: a line said twice at the start (`J'ai testé tous les… j'ai testé tous les scripts`) starts the short at the second one | |
| Start | the first kept word is the first word of the hook | no breath, no "ok", no look at the camera before |
| Hidden retakes | whisper can still merge a retake: a word lasting over ~0.6 s, a repeated phrase, or a word that makes no sense (`clics cloud`) marks one. Listen to that spot (`ffmpeg -ss a -t 4`), or re-run `words` with an ElevenLabs key, and cut it; never patch it with `captions.replace` | the short must start clean |
| Off-script talk | drop "wait", "let me redo that", asides to someone in the room | |
| Speed | 1.15 (pitch kept), `pace.speed` of the style | no slack between sentences |

## The views (`layout.keys`)

| seam | what's on screen | when |
|---|---|---|
| **1160** split (default) | the paper on top with one board, the camera card below | most of the short |
| **1920** paper | the camera leaves, one big board takes the frame | the big moment: the key number, a screenshot, a component |
| **0** full camera | the face fills the frame | a story, an emotion, a punchline, the CTA; 5 s of short time or more |

- A style with a fixed `layout.seam` keeps the camera card at that size for the whole short.
- The window card plays on its own between split and full camera; never fake it with a slide.

## Boards

- One every 2 to 4 s while the person explains, each on the exact word it illustrates. Boards **illustrate**, they never paraphrase: a number, a command, a folder, a logo, a before/after, a real screen. 2 to 4 words of text at most.
- The items (all in [scene-library.md](scene-library.md)): `text` with an `emph` word, `counter`, `term`, `tree`, `logo`, `check`, `chip`, `screen`, `bar`, `img`; whole scenes `tweet`, `stat`, `bars`, `title`, `cta`, `overlay` (a captured HTML component).
- A named tool always shows its real logo. Never emojis as logos, never stock illustrations.
- Vary them: never three text boards in a row.
- No slanted or wobbling text, no text on the face.

## Hook

- The first 2 s, readable on frame 0, never blank paper.
- 6 words or fewer, one accent word, never the same words as the spoken hook (it adds to it).
- Something already moving: a terminal typing, a counter running, a component in action.

## Captions

- 1 to 3 words at a time, as spoken, on the seam in split view. The style picks the look (`captions.style`: `rise` = the word said on an accent block that blurs in, `hard` = hard shadow, ...).
- `captions.emph` = the accent words, `captions.hide` = off while a board shows the same words.

## Sound

- Voice about -14 LUFS, true peak under -1 dBTP (`final` checks it).
- One calm bed from the library ([music.md](music.md)), under the voice, breathing between sentences.
- Hits only on real payoffs: a `thud` when a number lands or dies, a quiet `pop` on a real arrival. No whooshes, no clicks, no paper slides (`sfx: { swish: 0, accents: 0 }`). Bigger hits (the hook cut, the payoff) come from the bundled library: [sfx.md](sfx.md).

## CTA

"Comment GUIDE and I'll send it": full camera, the Instagram (or TikTok) comment sheet as an HTML overlay with the word typed in, then the DM notification (copy `examples/thinking-orbs/source/ig-cta.html`). The handle and avatar are the creator's.

## Safe zone

Text stays between y 170 and y 1500 and clear of the right 220 px from y 1100 down ([shorts-codes.md](shorts-codes.md)).
