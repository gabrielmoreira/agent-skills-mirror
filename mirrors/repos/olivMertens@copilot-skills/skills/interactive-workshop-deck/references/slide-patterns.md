# Slide patterns and design system

All patterns live in `assets/starter.html`. Each is a `<section class="slide" id="…" data-seg="N">`
plus, when interactive, a JavaScript module that starts with `if(!$('#…'))return;`, so removing a
section never breaks the deck. Section order in the markup is the presentation order.

## Design system

| Token | Default | Role |
|---|---|---|
| `--bg`, `--bg2` | `#050816`, `#0a1030` | stage gradient |
| `--panel`, `--line` | translucent navy, `rgba(140,160,255,.16)` | cards and borders |
| `--text`, `--muted`, `--dim` | `#eef1ff`, `#97a3cf`, `#5d6894` | three text levels |
| `--blue`, `--violet`, `--pink` | `#4f7bff`, `#a98bff`, `#ff6fb5` | brand-neutral gradient family |
| `--accent`, `--cyan` | `#5fb2ff`, `#2fe0f0` | kickers, links, live flows |
| `--ok`, `--warn`, `--bad` | `#2fd39a`, `#ffb547`, `#ff4d63` | status semantics only |
| `--grad-text`, `--grad-ui` | blue → violet → pink | `.grad` headline words, primary buttons |
| `--font`, `--mono` | Inter / system stack, JetBrains Mono / system mono | text, numbers, code |

- Theme presets in `CONFIG.theme.preset`: `midnight` (default), `ocean`, `ember`, `forest`,
  `graphite`; any token can be overridden in `CONFIG.theme.tokens` (applied before rendering,
  so SVG, canvas and particles follow). `--panel-solid` is the opaque card colour.
- Re-skin by editing the `:root` tokens; most tints use `color-mix()` on them. SVG and canvas
  colours are read from the same tokens at start-up (`C.*` in the script). The particle network
  and a few literal glows keep fixed RGB values; adjust them if the palette changes radically.
- Keep status colours semantic: green healthy, amber watch, red alarm, violet milestone/human.
- Type scale on the 1600×900 stage: h1 76–90 px, h2 44 px, lead 21 px, body 15–17 px, labels
  11–13 px uppercase with letter-spacing. Never go below 11 px.
- Layout: 70 px side padding, 56 px top bar, 44 px bottom bar, 16–20 px card radius.

## Motion vocabulary

| Motion | How | Use for |
|---|---|---|
| Staged entrance | `class="rise" style="--i:N"` (110 ms stagger) | every slide's reading order |
| Auto-cycle | `setInterval` in `enter`, cleared in `leave` | steps, loops that explain a sequence |
| Travelling dots | `.fa::after` (CSS) or `spawn()` in the simulation pipeline | data flowing between stages |
| Marching dashes | `.arc`, `.flow` (`stroke-dashoffset`) | active connections |
| Pulse / glow | `.ringp`, `.dst.bad` | outliers, alarms |
| Morph | `moveTo()` tween in the population map | regrouping into a cluster |
| Count-up + reveal | hook canvas | the scale of the problem |
| Slide-in card | `.alertc.show` | the decision moment |

All loops start in `enter[id]` and stop in `leave[id]`; reduced-motion users get the final state.

`CONFIG.motion`: `level` `full` | `calm` (static particles, no looping CSS effects, slower morph)
| `none` (final states only); `transition` `fade` | `slide` | `zoom`; `stagger` (ms between
reveals); `autoCycleMs` (steps, the loop runs at 70 %); `simSecondsPerDay`.

## Sound

`CONFIG.sound` drives `SND.play(event)`: short Web Audio tones for `nav`, `reveal`, `poll`, `vote`,
`alert`, `decision`. Off by default, **M** toggles it live, `volume` 0–1, and `files[event]` can
point to an approved `data:` URI instead of a tone. Add `SND.play('…')` calls in new modules
and a matching entry in the `KIT` table.

## Pattern catalogue

| # | id | Pattern | Content source | Feeds synthesis |
|---|---|---|---|---|
| P01 | `s-title` | Particle network, kicker, h1 with `.grad`, formula chain, meta row | markup | – |
| P02 | `s-hook` | Grid canvas of N squares filling up, counter, categories revealed one by one, live poll (click +1 / right-click −1) | `CONTENT.hook`, `CONTENT.poll` | poll |
| P03 | `s-context` | Three-card triad with arrows, multi-select chips | markup, `CONTENT.principles` | selection |
| P04 | `s-levels` | Three levels, last one highlighted, punchline | markup | – |
| P05 | `s-steps` | Equation, five auto-cycling steps lighting capability bricks (`data-s`) | markup | – |
| P06 | `s-patterns` | Eight starable cards | `CONTENT.patterns` | stars |
| P07 | `s-population` | Bubble clusters per group with lenses: `groups`, `duplicates` (arcs + animated regroup), `dormant`, `outlier` (arcs to target group), `heat` | `CONTENT.population` | – |
| P08 | `s-canvas` | Editable co-design table, suggestion chips per column, presets, local save | `CONTENT.canvas` | rows |
| P09 | `s-scenario` | Flow with travelling dots, four change cards, verdict + launch button | markup | – |
| P10 | `s-sim` | Live simulation (see below) | `SIM` | decision |
| P11 | `s-signals` | Signal families → qualitative level → candidate events | `CONTENT.signals`, `signalEvents`, `levels` | signals |
| P12 | `s-loop` | Rotating decision loop, automate vs human zones, decision record | `CONTENT.loop` | zones |
| P13 | `s-vote` | Three vote cards with bars and leader glow | `CONTENT.votes` | votes |
| P14 | `s-summary` | Five capability blocks, final message with optional second language | markup | – |
| P15 | `s-next` | Six-step timeline, closing question, synthesis button | markup | opens it |
| P16 | `s-compare` | Without/with toggle on an organisation graph, comparison table, race timeline | `CONTENT.compare` | – |
| P17 | `s-arch` | Layered architecture with flow lenses that dim the rest and animate active edges | `CONTENT.arch` | – |
| P18 | `s-links` | Link cards (kind, label, URL, why it matters), new tab optional | `CONTENT.links`, `CONFIG.links` | link list |

### P10 simulation anatomy

```
header: icon · name · tags · version tag · status pill · day counter · play/speed/replay/code
timeline scrubber
chart (left axis area + right axis line + lower band with threshold, milestone markers, crossing marker) | 6 KPI tiles with sparklines
event feed (deterministic, last 4 days)                                                            | rules + composite rule
right column: pipeline with flying dots · value-of-correlation panel with learn message
overlays: alert card with decisions · code panel · disclaimer
```

`SIM` keys: `days`, `baseline`, `unit`, `versions`, `metrics[{k,label,unit,dec,noise,f,ratio,alarm}]`,
`rules[{id,k,label,test}]`, `composite`, `critical`, `chart{left,right,band,cross}`, `milestones`,
`dailyEvents`, `pipe{nodes,edges,ingest,alert,decision}`, `alert`, `decisions{A,B,C}`
(`target` values, `'*0.75'` multipliers, `rollback`, `incident`, `learn`), `status`, `gain`, `code`.
The first six metrics become tiles; a tile turns red when its rule fires or its `alarm(v, baseline)`
returns true.

## Engine contract

- `go(i)`, `enter[id]`, `leave[id]`, `PLAY[id]` (bound to **P**), `SYNTH.push(fn → markdown)`.
- `S` is the persisted state; add new keys in `DEF()` and keep them JSON-serialisable.
- Keys: ←/→/Space/PageUp/PageDown, Home/End, N notes, F fullscreen, T timer, P play, M sound, Esc.
- `#N` in the URL opens slide N; `window.__deck` exposes `go`, `slides`, `synth` for tests.
