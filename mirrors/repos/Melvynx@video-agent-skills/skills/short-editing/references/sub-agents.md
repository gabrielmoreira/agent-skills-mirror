# Sub-agents: motion components in parallel

The main session is the supervisor. It runs on the strongest model, plans the beats, owns `spec.js` and runs every engine step. Each sub-agent builds ONE motion component, all of them at the same time, so a short full of custom UI takes the time of its slowest component instead of the sum of all of them.

## Who does what

| | supervisor (main session) | sub-agent (one per component) |
|---|---|---|
| reads | words, transcript, style, the whole spec | only its prompt and the files it names |
| writes | `source/spec.js` (the only writer), `About.md`, `Roadmap.md` | `source/<name>.html`, `assets/<name>.mov` or `.mp4`, `stills/<name>-*` |
| runs | `prepare`, `stills`, `render`, `audio`, `final`, the studio | `short.mjs capture` on its own page only |

A sub-agent never edits `spec.js`, `style.json`, the engine or another component's files, and never runs `prepare`, `render`, `audio` or `final`. A sub-agent cannot launch its own sub-agents: an agent that edits a whole short (`video-editing-agent`) builds its components itself, one after the other, with this same template.

## What is a component

Anything the scene library cannot draw well, written as an HTML page and turned into a clip by `short.mjs capture`:

- a real app played in its own UI: a terminal typing a command, a chat answering, the Instagram comments of a CTA, a dashboard filling, a phone notification. A finger or a cursor does the actions. Every UI and motion design text (titles, labels, tags, counters included, captions excepted) uses the Apple system font (`"SF Pro"` first, `"SF Mono"` for monospace, never `-apple-system` alone), in its Text cut (`font-variation-settings: "opsz" 17`, letter-spacing 0, only titles of 60 px and up keep the Display cut), see design-system "Type";
- a software idea played in a recreated UI that acts: code that scrolls then blacks out line by line, a lock that closes, a price that drops to 0 under a stamp; a platform named with a number in its real interface (the GitHub repo page, its stars curve, the Star button filling);
- the hook's mini story: 2 or 3 acts with a reversal, several layers, an impact on each keyword, the payoff as a badge (e.g. the big apps crush the viewer's app under a REPLACED stamp, the story flips on the turning word, the viewer's app becomes the giant);
- a fun illustration that acts: a mascot, an object or a character that does something, with a new action every 2 to 3 s;
- a chart or a diagram, drawn and animated in code (a curve that draws, bars that fill), never a still.

A component never pastes a screenshot or a generated image as the beat (the creator 2026-10-21: source code = motion design, never an image). A screenshot is a reference to rebuild in HTML; a generated illustration is a layer that moves and acts inside the page.

The engine-native beats (cards, tiles, counters, `term`, texts, `board`) stay with the supervisor: writing them in `spec.js` is faster than a round trip.

## The supervisor's loop

1. Read `files/words.md` and plan every beat (SKILL step 3).
2. List the components. For each one, write down:
   - the beat id;
   - its SHORT start and end;
   - its size: `1080x1920 --alpha` for an `overlay` over the camera, the card's own size for an actor on the paper;
   - the spoken words over it with their τ (short time of the word minus the component's short start);
   - the assets it needs (logos in `assets/logos/`, the avatar, a reference image of a real UI to rebuild: never an image to paste).
3. Launch one sub-agent per component in ONE message: several Agent calls, each in the background, general-purpose type. Leave out the model so they run on the supervisor's model. Up to about 6 at a time; past that, give one agent 2 small components.
4. While they work, write the engine-native beats, run `prepare`, then stills on those beats.
5. When a report lands, wire the clip in:
   - add `media: { <id>: { src: 'assets/<name>.mov', width: 1080, alpha: true } }` plus an `overlay` scene, or an actor with `media` for a card;
   - turn each reported event τ into `sfx.extra` (short time = component start + τ, then back to source time through `words.md`);
   - rerun `prepare` (the media cache follows the file, so a recaptured clip is picked up), then stills on that beat.
6. To fix a component, send a message to the same agent (it keeps its context and its page). Never start a new agent for a fix.
7. On a review round, use one agent per comment that needs a new or reworked component. The supervisor applies the cut, text and timing comments itself.

## Prompt template (one per component)

The agent sees nothing of the conversation: fill every `<...>` with real values and absolute paths.

```text
You build ONE motion component for the short <slug> (<absolute project path>). Skill engine: <absolute skill path>/engine/short.mjs.

Where it plays: <over the full-screen camera, transparent, full frame 1080x1920 | as a card on the paper, W x H>, from short time <a> s to <b> s (<dur> s).
The beat: <what happens on screen, action by action, and what the viewer must feel>.
Voice over it, τ = seconds since the component starts:
<τ  word, one per line or as "0.00 Ton, 0.12 monteur, ...">
Leave free: <the caption band, e.g. y 1180 to 1420, and the face if it is over the camera>.

Look: font family "<style.json font.family>" for every text (display: "<display.family> <weight>"), paper <colors.paper>, ink <colors.ink>, accent <colors.accent>. Creator notes that apply, copied word for word from STYLE.md: <the style's originality and motion-design notes, always, plus the lines that matter here>. Never restate a caption, font or music rule from memory: the style owns them.
Assets: <real logos and images, paths relative to the HTML>.

Build:
1. <absolute project path>/source/<name>.html, a <W>x<H> page, <transparent background | its own background>. Every visual state is a pure function of t in window.setT(t) (seconds since the start): no CSS transitions or animations, no timers, no requestAnimationFrame, no Date. Ease with springs that never overshoot: S(x, w) = 1 - (1 + w x) e^(-w x). Fonts by family name (the engine loads Bricolage Grotesque, DM Sans, Inter, JetBrains Mono, Archivo, Instrument Serif); images by a path relative to the HTML.
2. Capture: node <engine>/short.mjs capture <project> source/<name>.html --dur <dur> <--alpha | --size WxH> --at <τ of the key moments, comma separated>
   It writes assets/<name>.mov (alpha) or .mp4 and stills/<name>-sheet.jpg.
3. Read the sheet, then zoom the full frames that matter. Fix and capture again until the bar below passes. At least 2 rounds.

Bar:
- It acts: every second shows an action (typing, scrolling, a curve climbing, a lock closing, a stamp landing), never a still image sitting on the frame. On each sheet ask « is something happening, or is it an image sitting there? ».
- It looks like the real app (its layout, icons, colors and type), never a generic card. Real logos only, never a letter glyph.
- A hook component is the most ambitious clip of the short: 2 or 3 acts with a reversal, several layers moving together, an impact on each keyword (its event in the report, a thud), the payoff as a badge. One object that slides is not a hook.
- Something moves every .5 to 1 s, a new action every 2 to 3 s, each action lands on the word that says it.
- Entries stagger and ease in; nothing pops, bounces or overshoots; nothing jitters between two frames.
- Every text is 34 px or more at 1080 wide; important content stays inside x 60 to 940, y 220 to 1500.
- Over the camera: the face stays visible and keeps its colours, except where the beat covers it on purpose. Never a full-frame dim over the face (8 % black at most, e.g. under an opening sheet: a 26 % veil turned the creator's face brown); a dark scrim only behind text, at an edge.
- No em dash in any text.

Do not touch any other file (not spec.js, not style.json, not the engine, not another component). Never run prepare, render, audio or final. Delete with trash, never rm -rf.

Report, short: the clip path and its duration; the event list as "τ  what (tap, type, post, notification, impact)  sound it wants"; the sheet path; anything you are unsure about.
```

## Example

A comment CTA: `source/ig-reel.html` draws the Instagram Reels UI over the full-screen camera. A finger taps the comments, the word is typed and posted, then the DM notifications drop in. `capture --alpha` turns it into `assets/ig-reel.mov`, the supervisor wires it as an `overlay` scene and puts its taps and posts in `sfx.extra`.
