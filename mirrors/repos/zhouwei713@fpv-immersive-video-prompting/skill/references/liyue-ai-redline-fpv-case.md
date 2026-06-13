# Li Yue red-line FPV / Seedance 2.0 case note

Source pattern: an X thread by @liyue_ai about a 15-second immersive ancient-style FPV game-demo video made with GPT Image 2 + red-line camera route planning + Seedance 2.0.

## What matters

The value is not the one long prompt itself. The reusable pattern is:

1. Generate a static scene / first frame with clear spatial layout.
2. Generate or provide separate character references so the video model can maintain faces and clothing when the camera focuses on each person.
3. Draw a red camera path over the scene as a planning artifact.
4. Convert the path into a timestamped route.
5. Give every stop on the route a small interaction beat: position, action, dialogue, info card, consistency constraints.
6. Add first-person body physics: walking sway, breathing rhythm, small head-bob, acceleration/deceleration, foreground/background parallax.
7. Add subtle environmental motion: water, fabric, curtains, hair, light, reflection.
8. State that red path lines/arrows are only for planning and must not appear in the output.
9. Add an explicit avoid list for identity drift, extra characters, morphing, route-line leakage, camera teleporting, clipping, excessive shake, and UI covering faces.

## Example interaction structure

For each character/object:

```text
[time range]: The player approaches [position + identity]. [Character/object] does [small action]. [Dialogue/sound/UI card]. Keep [face/clothing/position/count] consistent.
```

## Ancient-garden sample beat map

- 0.00–0.70s: establish first-person entry, water ripples, curtains, ambience.
- 0.70–2.30s: approach 清扬, purple seated character, singing specialty, greeting line and info card.
- 2.30–4.20s: approach 静姝, green seated character with fan, chess specialty.
- 4.20–6.40s: approach 令仪, central pink standing character, qin specialty.
- 6.40–8.70s: approach 杜若, blue character by railing, calligraphy/writing specialty.
- 8.70–12.20s: move through pavilion, emphasize parallax; background characters only breathe/blink.
- 12.20–14.50s: approach 采薇, pink looking-back character, painting specialty.
- 14.50–15.00s: settle into final layered group composition.

## Why comments matter

For posts like this, comments often contain the real workflow details: tool names, platform names, route-planning trick origin, whether arrows are only planning guides, model/version, and constraints discovered from failures. When researching similar examples, inspect the author’s replies and follow-up posts, not just the main media post.

## Reusable output rule

When turning a viral post into a skill, avoid making a one-case skill like “Li Yue ancient garden prompt”. Generalize it into the class: first-person route-planned immersive video prompting. Keep the specific post as a reference file.
