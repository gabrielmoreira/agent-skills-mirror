# Record reference measurements

Measure the reference with the shared [measurement method](../../openmotion-production/references/reference-video.md#measure-specific-questions). For a portable folder, use the pinned native CLI of the runtime that will render it; the shared page explains where managed project details and the engine resource return the CLI and guide paths. Running every measurement command is not mandatory.

Put the numbers you measure into `TEMPLATE.md` at the project root (template at the end of this file). Rebuilding, comparing and recording differences all refer back to it.

## What goes where

- **Canvas:** dimensions, rate, frame count, picture duration and sound go on the `Original` line. For a variable-rate source, record the output rate you chose.
- **Segments:** verified cuts and content segments, with frame ranges, seconds, element ids and motion, go in the rebuild record table. Detector candidates that adjacent frames rejected are not cuts.
- **Text:** copy, font, size and ink width×height for the original and the rebuild go in the text table. Mark a substitute font there and add one plain line under `Differences from the original`.
- **Texture:** only where the reference has it, note how much the back layer blurs, where it glows and which frames carry motion blur, next to the affected segment.
- **Checks:** each check's state goes under `Checks`, as [check and deliver](verify.md) describes.

## TEMPLATE.md

One file, read mainly by the next agent and by template producers. Users may open it, so keep it plain.

```markdown
# <film name> template

## What to change
| Content | Variable or source entry | Also affects |
|---|---|---|
| headline | `headline` / compositions/title.html | line wrap, hold before cut at 3.2 s |

## Differences from the original
- Plain words, where and why (including substituted fonts)

## Rebuild record

Original: <path>, <width>×<height>, <fps>, <frames> frames, <duration> s, sound: yes/no

| Segment | Frames [start,end) | Seconds | Content | Element ids | Motion (duration / ease) |
|---|---|---|---|---|---|
| s1 | [0,71) | 0–2.366666 | black dot rotating | bot-dot | rotate 1.2s / power2.inOut |

## Text
| Element id | Copy | Font (substitute?) | Size | Ink width×height (original / mine) |

## Checks
Passed / did not pass (where) / did not run, one line each. Include the HyperFrames version and the tested render command.
```
