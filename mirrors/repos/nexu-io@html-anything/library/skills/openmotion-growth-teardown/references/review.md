# Review before delivery

Render, then watch the MP4 once at full speed with sound and once frame by frame at the moments below. Fix the data or the copy first; touch scene files only for what the data cannot express.

## Facts

- Every number on screen (headline metric, counter, play stats, gallery cards) appears in `growth.json` with a source URL. Spot-check three of them by opening the URL.
- The headline metric's note names the month the figure describes and who reported it, not the month the article was published, when the two differ.
- Estimates are labelled as estimates in `TEARDOWN.md`; the film does not present an estimate as a company figure.
- Plays say "sped up after" unless a source attributes the growth to the move.

## Frames

| Moment | Check |
| --- | --- |
| Intro, first 2 s | The OpenMotion wordmark and tagline are crisp and centered |
| Intro, end of typing | The command reads naturally; the logo chip is the company's real mark |
| Any headline | The OpenMotion mark sits before the headline, aligned with its cap height |
| Sources | Every tile has a real icon; the call count is the real count |
| Map, last second | No move label overlaps another or runs off the lane; the counter lands on the latest sourced value |
| Each play, last second | The orange stretches start at that lane's moves; each leader line ends on the move's date; cards show the real page, video or a clipping with the real headline; nothing important is hidden by a cookie banner |
| Plays to copy | Instructions are complete sentences and fit in their cards |
| Outro | Gallery cards (when used) come from other real teardowns; the OpenMotion wordmark signs the film |

`npx hyperframes snapshot --at <times>` captures exact frames; `npx hyperframes check` reports overflow, contrast and timing warnings.

## Sound

The generated score follows the film's own cues (typing, pops, blips, whooshes, hits). Replace it with `--music <file>` only with a licensed track, or pass `--no-score` for silence.

## Report

State separately: research sources checked, technical render check, and the user's creative acceptance (still pending until they have watched it).
