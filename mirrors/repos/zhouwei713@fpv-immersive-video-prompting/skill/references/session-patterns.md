# Session Patterns: FPV Immersive Video Prompting

This reference captures practical lessons from developing the FPV prompt workflow.

## Numbered markers beat red route lines

Initial approach used red camera-path lines on the first frame. In practice, GPT Image often struggles to draw one continuous physically coherent route. Lines may disconnect, cross obstacles, or become decorative. For most workflows, ask GPT Image for numbered stop markers only: 1, 2, 3, etc.

Video prompt pattern:

```text
首帧中的 1、2、3 只代表镜头停靠顺序，最终画面不要出现数字、编号、路线、箭头、文字或 UI。镜头按编号连续移动：入口 → 1 → 2 → 3 → 终点。每段移动必须沿可见可行走空间自然前进，不能瞬移、跳切或穿过障碍物。
```

## Spatial ordering for markers

Do not let markers scatter across a beautiful scene. First design the environment as a route, then place targets along it:

- 1: closest to camera / foreground
- 2: near-midground
- 3: midground
- 4: mid-far / side corridor
- 5: far destination

Each next marker must be reachable without crossing walls, furniture, water, people, railings, or impossible height changes.

## Variable count rule

If the user says “3 people,” use exactly 3 main characters in image prompts, route, timeline, and negative constraints. Do not return to a 5-character default. If the user says “a group” but gives no number, pick a practical count for duration, usually 4-5 main targets.

## POV examples

### Coffee shop, 3 people, robot vacuum POV

Asset prompt should request:
- 16:9 first frame from ~10 cm height
- numbered stops only: 1 near window customer, 2 central table customer, 3 barista at counter
- separate reference images for each of the 3 characters
- optional clean first frame without numbers

Video constraints:
- exact 3 main characters
- robot vacuum height ~10 cm
- slow floor gliding, slight mechanical vibration/turning hesitation
- cannot fly, jump, climb, or pass through table legs, chair legs, people, counter, walls, cables
- avoid accidentally turning into human eye-level or drone POV

Useful beat structure for 12s:
- 0-1s: start from entrance floor
- 1-4s: marker 1 interaction
- 4-7s: marker 2 interaction
- 7-10s: marker 3 interaction
- 10-12s: pause/turn/reveal scene layers

## Do not impose a default 2000-character limit

The user briefly considered a 2000-character video prompt limit, then explicitly reverted it. Keep prompts directly usable and concise enough for the target tool, but do not bake in a fixed default character limit unless the user asks for one in the moment.
