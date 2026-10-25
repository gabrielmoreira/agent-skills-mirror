# Design: how nanoMuse looks, and why

The choices behind the app's look, written down so that the app stays coherent as it grows and so that a contributor can tell "on purpose" from "not yet". Everything here is the project's own: the dragon, the layouts, the tokens; the red panda of the early releases is kept below as history.

## The shape of the app

| | How nanoMuse does it | Where |
|---|---|---|
| Surfaces and colour | Near-white in light and near-black in dark, no gradients, no card shadows to speak of; depth is one step of grey (`surface-2`) for chips and the tab bar. One accent, a saturated blue, used sparingly: `bg`, `surface-2`, `fg`, `muted`, accent `#0064d4`; dark mode by `prefers-color-scheme`. The conversation goes further on the phone and the web alike: the chat sits on pure white in light (on the phone the pill bar, the menus and the drawer too) and on black in dark on the phone, near-black on the web, and the blue stays with links and the status line | `web/src/index.css`, `android/…/values/colors.xml`, `android/…/ui/theme/ChatColors.kt` |
| Type | [Figtree](https://github.com/erikdkennedy/figtree) (OFL), bundled: one family at three or four sizes, large and friendly, tight letter-spacing on headings, generous line-height in bubbles | `web/public/fonts/` |
| Chat | Monochrome pills on the phone and the web alike: your messages are white pills with black text on the dark canvas (black on white in light), the agent's a shade off the canvas, the send button and the scroll-to-latest control the same ink, and the header a scrim the conversation scrolls under and dissolves into. Tool use is not hidden: a small chip per action ("Checking price") that opens to the tool call; approval requests are cards inside the conversation with the summary the Sentinel wrote, the exact action spelled out, and the scope buttons (once, this conversation, always; on the phone once, this chat, always); files the agent made appear as tiles with a preview | `web/src/screens/ChatScreen.tsx`, `web/src/components/`, `android/…/ui/chat/ChatScreen.kt` |
| The avatar | The bundled **dragon**, a still per state (idle, working, waiting, happy, error) and a short looping clip for every state but error, so the face changes with what the agent is doing instead of standing still; a face drawn in the avatar studio or an emoji on a colour as alternatives (the red panda of the early releases is the history below) | `web/src/components/Avatar.tsx`, `web/public/avatars/` |
| Header and sheet | The face sits at the top of the chat inside a circle, the agent's name under it and a one-line status ("Checking price") under that. Tapping it opens the sheet: the avatar large, the status, *Stop* on the running task, four buttons (approvals, activity, permissions, upcoming) and rows for memory, skills, connections, settings | `web/src/components/MuseHeader.tsx`, `web/src/screens/MuseSheet.tsx` |
| Navigation | Five icons and no labels: Chat, Feed, Ideas, Goals, Library, in a frosted-glass pill 12 px above the bottom edge, translucent over a blur with a hairline edge; the current tab's filled glyph sits on an ink indicator (`ink`, with the glyph in `ink-fg`), the others are outlined in `muted`. Chat is the home; everything else the agent has (memory, connections, settings) lives behind the avatar. The sidebar replaces the pill on a wide window | `web/src/App.tsx` |
| The rooms | Feed: posts written for you, with a place to say what you want more of. Ideas: a grid of suggestions grouped by area, tap to send. Goals: a list with progress, each opening to a plan with steps and a next check-in. Library: what the agent made, newest first, with previews | `web/src/screens/FeedScreen.tsx`, `IdeasScreen.tsx`, `GoalsScreen.tsx`, `LibraryScreen.tsx` |
| Motion | Little: the status line changes, a chip appears, the face moves. The dragon's and a studio face's clips, breathing / sway / hop for an emoji; no spinners except a small one next to the status; everything off under `prefers-reduced-motion` | `web/src/index.css`, `web/src/components/Avatar.tsx` |

## The red panda

> Since 0.1.11 the default face is the bundled dragon (the same on the phone, the desktop and
> the web); the red panda below stayed as an optional avatar until 0.1.23, when it retired with
> the six dolls, and remains here as the record of how a face that poses from state was first
> drawn.

A face that poses from the agent's state says "there is someone here, and it is busy" without a spinner. nanoMuse's first answer was a red panda (a round head with two small ringed ears, a cream face that comes down in two cheek lobes to a dark nose, big dark eyes with a catchlight, a ringed tail) drawn as an SVG so that it can be posed from the app's state instead of swapped between photographs.

**Why this animal, drawn this way.** A giant panda is the obvious mascot and the one everyone already uses; a red panda is small, warm-coloured and curious, and reads as "a little helper" rather than "a national symbol". The drawing is simplified (few parts, big eyes, one expression change per mood), so it survives 16 px. Above that it is *2.5D*: radial gradients on the fur, body and cheeks, a sheen on the top of the head, a shade under the chin, a shadow the body sits in; the roundness a plush doll has, without a 3D render, which would not pose from CSS and would not stay a few kilobytes. It is never a real render and never an illustration with outlines; the parts are flat shapes with soft light on them.

**Three levels of detail** (`detail` on the component, chosen from `size` by `detailFor` when not given): `mark` up to 28 px is flat colour with the head scaled up to fill the plate (the logo, tab-bar and list sizes); `avatar` up to 160 px has the gradients; `hero` above that adds the sheen, the finer tail rings and the small props. The icon, the Android launcher and the MobileGym launcher are the `mark` level rendered from the same geometry (`web/src/components/redPandaShapes.ts`), which is the one place the shapes live: the component and the asset generator both read from it.

| State | What the app knows | What the panda does |
|---|---|---|
| idle | nothing running | breathes; blinks every few seconds; glances left and right; an ear twitches; the tail swings |
| working | `status.state == "working"` | sits at a small laptop and types, head nodding, eyes on the screen |
| waiting | `status.state == "waiting"`, an approval card or a question is open | one paw up, a "!" bubble bobbing beside it, a small hop |
| happy | a run just went from working to idle (3 s) or you tapped it | a bounce, an open smile, two sparkles |
| error | a tool call failed or was refused (4 s) | a shake, brows down, a drop of sweat |
| sleepy | the app is loaded but the server is unreachable | eyes closed, slow breathing, three z's |

The moods come from `web/src/mood.ts`: the status gives the pose it holds; two moments the store records (`finishedAt`, `mishapAt`) colour it briefly. Motion is CSS keyframes on SVG groups; every part is positioned by coordinates so the transforms can be animated, and `transform-box: view-box` with an explicit origin keeps the pivots where they belong. `still` freezes it for lists and pickers; `prefers-reduced-motion` stops all of it.

Until 0.1.23 the same drawing, reduced to the head, was also the logo: `web/public/icon.svg` and `mark.svg`, the PWA icons, the README cover, the Android adaptive launcher (a forest-green plate; the head flat, no gradients, because launcher masks and themed icons flatten everything anyway; a monochrome silhouette with the eyes, nose and mouth punched out for themed icons and the status bar) and the launcher icon of the MobileGym app. `npm run mascot:assets` in `web/` wrote the vectors from `redPandaShapes.ts`, `npm run site:mascot` rendered the six moods for the website, and `python scripts/mascot_png.py` rasterised the PWA icons and the cover; nothing was drawn twice, so the copies could not drift apart. `RedPanda.test.tsx` held a snapshot of the flat head, the silhouette and the idle hero. The icon today is the blue N in `web/public/icon.svg`, and the drawn face is the dragon; the panda's files left the tree with the dolls.

## Colour and type, in numbers

The web console's tokens (`web/src/index.css`):

| Token | Light | Dark |
|---|---|---|
| `bg` | `#ffffff` | `#181819` |
| `surface` | `#ffffff` | `#202022` |
| `surface-2` | `#f2f2f4` | `#2a2a2d` |
| `border` | `#e7e7ea` | `#333337` |
| `fg` | `#111112` | `#ffffff` |
| `muted` | `#6b6b71` | `#9d9da4` |
| `accent` | `#0064d4` | `#1793ff` |
| `ink` (the send button, the *Latest* button; `ink-fg` the glyph on it) | `#000000`, glyph `#ffffff` | `#ffffff`, glyph `#000000` |
| `bubble-user` and its text (`bubble-user-fg`) | `#000000`, text `#ffffff` | `#ffffff`, text `#000000` |
| `bubble-agent` | `#f2f2f7` | `#2a2a2d` |

The chat's header is a scrim rather than a bar: `bg` at 80 percent at its top edge, 35 percent past the middle, clear at the bottom, with the conversation scrolling under it; while older messages are being read the top 80 px fade fully into `bg`. The bottom edge works the same way: the conversation scrolls under the composer and under the pill bar, the pill bar blurs what passes behind it, and while older messages are being read a 90 fade of `bg` rises above the composer so the rows dissolve into it instead of running into the field; at the latest message nothing lies behind the composer but the list's own padding. Android has this as `NmChatBottomLayout` and `nmBottomFade` in `ChatScreen.kt`, iOS as `NanoMuseComposerHost` (since 1.0.4; up to 1.0.3 the iOS list ended above the composer and the pill bar sat over a plain canvas, so its glass read as a white pill). A link inside your pill keeps the pill's text colour, underlined. In the dark theme the agent's pill is the same step off `#181819` that the phone's `#1c1c1e` is off black.

On a wide screen the conversation is one centred column of 760, the width the web console gives its chat below the sidebar breakpoint (`max-w-[760px]`): the messages, the composer and the pill bar share it, and the composer and the pill bar are exactly as wide as each other, the column less the 16 margins on each side. The agent's reply pill grows from 340 to 600 inside it, the web's `wide:max-w-[600px]`. On the iPad this is the regular width size class (`NanoMuseColumn` in `NanoMuseShell.swift`); a phone, or a narrow pane, keeps the window's width and the pill bar's 420 cap, which no phone reaches.

The Android app's chat palette is `ChatColors.kt`, written by `scripts/rebrand.py`:

| Token | Light | Dark |
|---|---|---|
| canvas (`background`) | `#FFFFFF` | `#000000` |
| your pill (`userBubble`) and its text | `#000000`, text `#FFFFFF` | `#FFFFFF`, text `#000000` |
| the agent's pill (`assistantBubble`) | `#F2F2F7` | `#1C1C1E` |
| send and stop buttons (`sendButton`), glyph in the canvas colour | `#000000` | `#FFFFFF` |
| links, status line (`link`, `thinking`) | `#015CFB` | `#58A6FF` |

The iOS app's chat uses the same values: `NanoMuseTones.ink` and `onInk` for your pill, the
send disc and the scroll-to-latest disc, `agentPill` for the agent's, in `NanoMuseFaces.swift`;
the canvas is the system background, white and black. The pill bar's indicator disc is the same
ink with the glyph in `onInk` (`tabIndicator`, `tabIndicatorGlyph`), see [ios.md](ios.md).

The panda: fur `#d8632e` lit to `#ee8a4c` and shaded to `#9e3f18`, deep fur `#bf4f23` (ears, tail rings, paws), cream `#fff4e6` from `#fffaf2` to `#f3dfc6` at the cheeks, markings `#2a1a14` with an eye highlight `#4a302a`, blush `#f4a0a0`; the plate behind it in the app `#dcebdc`, the logo plate `#2f7a5a`. The `mark` level uses only the base colours.

Figtree throughout, set with Tailwind's scale: 15 px in bubbles, 12–13 px for status lines and captions, 17–20 px semibold for titles.

## Identity: the name comes first

nanoMuse opens by asking what to call it, and the name is then everywhere: the header, the notifications, the way it talks about itself.

- **First run is a checklist**, not a slideshow: three points about what it is (it does things for you; it keeps working when the app is closed; it asks you first where it matters), then three items, *meet your nanoMuse*, *add a model*, *connect mail, calendar, contacts* (optional), ticked as they are done, with *Start* locked until a model answers. A reload mid-way keeps the ticks, because they are read from what was saved, not from the page.
- **The naming page**: 1–20 characters, empty falls back to `nanoMuse`; six suggested names as chips (three Chinese, three English) and a shuffle; the avatar; a one-line tagline under the name (≤ 60 characters); then how it talks: a **tone** (formal / casual / playful / concise), **how much it says** (short / detailed / bullet points), free text for anything else, and what it should call you. Each of these is its own paragraph in the system prompt (`Profile` in `nanomuse/server/service.py`), so a tone can be changed without touching the free text.
- **The name is threaded through**, not decorated: the header and the greeting, approval and permission copy ("Actions {name} wants to take…"), the CLI banner (`nanoMuse v0.1.0 · Momo`), the MobileGym bridge's titles, Settings ("You and Momo"). Where the product is meant (the app, the docs, the README) it stays *nanoMuse*.
- **Bring your own key, no account with us.** The model form lists providers grouped by protocol (OpenAI-compatible Chat Completions · Responses API · local or your own endpoint) with vendor subtitles, a masked key with a reveal toggle, a *Get a key from …* link per vendor, a Base URL that gains `/v1` when it has no path, and endpoints that need no key at all (Ollama, or a custom one with *No key* ticked). The endpoint's own `/models` is asked for the list; a static catalogue stands in when it cannot be reached; a model typed by hand is never replaced. **There is no OAuth subscription login** and none is planned for 1.0: a login through us would make nanoMuse the account holder between you and the vendor, which is the one relationship this project exists to avoid. (Written before 0.1.18. Since then the account with nanoMuse Cloud gives a free pool to start with, and since 0.1.39 a ChatGPT plan can sign in; both keep the key or token on the device and the vendor relationship yours, see [cloud.md](cloud.md) and [own-key.md](own-key.md).)

## Choices made on purpose

- **The phone's screen is visible.** nanoMuse's phone steps are rows in the chat (`phone_act: tap "发送" …`) and the finger overlay shows on the phone itself, because a user should be able to see what a hand on their phone is doing.
- **A brake you can reach.** While nanoMuse operates the phone, a capsule sits over the app the whole time: the agent's face, the step in progress, and one red **Stop**. One tap, no menu; it ends the step in flight and refuses the next ones, and the agent asks instead of carrying on. A hand on your own phone must be stoppable by the hand's owner. The screen is also the *last* rung: a skill, a fetch or the browser goes first, and the Activity view shows how often the screen was needed.
- **Approvals name the scope.** A yes / no is not enough; nanoMuse's card offers *once*, *this conversation*, *always* (the same middle scope on the phone, the web app and the terminal) and lists the grants under *Permissions*, each with a revoke button.
- **Everything has a plain-text form.** The same agent runs in a terminal (`nanomuse chat`) with the same approvals, and every screen is backed by a documented REST + WebSocket API, so another front-end can drive it.
- **The mascot is a drawing, not a photograph.** It costs a few kilobytes, poses from state, and can be printed on a sticker.

## Sources

CopilotKit's [OpenMuse](https://github.com/CopilotKit/openmuse) for the product designs of durable tasks, watches and ideas with evidence. Nothing from it is copied; this page records what was learned.
