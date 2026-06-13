---
name: fpv-immersive-video-prompting
description: Use when the user wants to turn a static scene, character images, aerial map, drawn path, or route-control image into an immersive first-person FPV AI video prompt, especially Seedance/Kling/Runway/Veo style one-shot videos with numbered stop markers, red-line path control, world-map flythroughs, camera route planning, variable character counts, non-human POVs such as drones, pets, robot vacuums, character references, timed interactions, dialogue, spatial audio, and negative constraints.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [video, ai-video, fpv, prompting, camera-route, character-consistency]
    related_skills: [gpt-image-2-prompting]
---

# FPV Immersive Video Prompting

## Overview

This skill turns a scene idea plus optional image references into a directed FPV AI-video prompt. The target output should feel like the viewer is moving through a playable scene, not watching a generic beauty shot.

Use this for image-to-video workflows where the user wants:
- one-shot first-person walkthroughs
- numbered route stops or camera planning
- characters reacting as the camera approaches
- human or non-human POVs: guest, pet cat, drone, robot vacuum, bird, vehicle, object, spirit
- variable numbers of characters or targets
- strong identity and route consistency

## Core Principle

Default to Chinese for all generated prompts, including GPT Image asset prompts, route-control image prompts, video prompts, negative prompts, and delivery notes, unless the user explicitly asks for English or a target tool requires English. Keep technical terms such as FPV, Seedance, Kling, Runway, Veo, one-shot, prompt, and path control in English when they are clearer.

Write the output as a small playable scene specification:

1. Who or what is the camera?
2. Where does it start?
3. How many main targets are there exactly?
4. What numbered order does it visit them in?
5. How does the camera physically move?
6. What happens at each stop?
7. What must stay consistent?
8. What must never appear?

## Default Asset Workflow

When the user needs GPT Image / GPT-Image-2 assets, request a multi-image asset pack rather than one crowded contact sheet. Treat requests for “生图 prompt”, “首帧图”, “参考图”, “素材包”, “用 GPT Image 生成”, or any image-prep step as an asset-pack request, not as a single first-frame prompt.

For any case that needs multiple images, output one batch-generation prompt that asks GPT Image / ChatGPT to generate multiple separate images in a single response. Do not split the asset pack into many independent per-image prompts unless the user explicitly asks for that. The prompt must say: “请一次性生成 [X] 张独立图片，不要生成拼图、九宫格、contact sheet 或一张图里塞多个画面。”

For close-interaction scenes with N main people/targets, always output the complete asset pack unless the user explicitly asks for only one image:
1. First-frame scene image with small numbered stop markers only: 1, 2, 3, ... N
2. N separate character/reference images, one for each main person/target
3. Optional clean first frame without numbers for safer image-to-video input

Before returning any image prompt, run this count check: total images = 1 route/numbered first frame + N character references + optional 1 clean first frame. The video prompt must refer to these images by role, e.g. “图片 1 is route planning, 图片 2-4 are character references, 图片 5 is clean first frame.”

Default image sets:

Close-interaction / character mode:
1. First-frame scene image with small numbered stop markers only: 1, 2, 3, ...
2. One character/reference image for each main target
3. Optional clean first frame without numbers for safer image-to-video input

World-route / path-control mode:
1. Aerial route-control map or wide first frame with one clear continuous red path from start to destination
2. Optional clean world/scene reference without the red path
3. Optional landmark or character references only if specific destinations need consistent appearance

Prefer numbered stop markers for close-range character interactions, indoor scenes, crowded social scenes, and exact target-count workflows. GPT Image often struggles to draw one continuous physically coherent route through furniture, people, walls, railings, or water; a bad red line can mislead the video model. Numbered stops are easier to generate correctly, and the video prompt can define the movement between them.

Use red-line path control for large-scale route-shaped scenes: aerial world maps, fantasy continent journeys, city-to-landmark flythroughs, racing lines, canyon/drone routes, open-world game trailers, and Seedance 2.0 path-control demos. In that mode, the route image is a planning artifact; the final video must remove all red lines, arrows, annotations, labels, and map-view appearance.

### Red-Line Path Control Rules

Use this mode when the user asks for Seedance 2.0 path control, a drawn route, an aerial map flythrough, a game-world traversal, a racing line, or a large-scale drone/bird/spirit FPV journey.

For the route-control image prompt:

- Use a high-resolution 16:9 aerial terrain map, world map, tactical map, or wide route-planning scene.
- Draw one clear continuous red route line, optionally with a subtle arrow, from start to destination.
- Make the route physically plausible through visible corridors: roads, valleys, rivers, city gates, bridges, canyons, rooftops, airspace, tunnels, coastlines, or ridgelines.
- Build 4-6 visually distinct route segments so the video has progression: peaceful start, transition zone, landmark/city, danger zone, final destination.
- Keep the red line clean and legible. Avoid multiple competing paths unless the user explicitly wants branching routes.

For the video prompt:

- Say the uploaded image is a route-planning map/image, not the final look.
- Say the red line/arrow/annotations are only camera-path controls and must be completely removed.
- State the camera must strictly follow the drawn route geometry from start to destination.
- Use invisible first-person drone, bird, spirit, vehicle, or mounted-camera POV unless the route is truly walkable.
- Add timeline segments by geography, not by character stop.
- Include camera language: continuous forward motion, natural banking, close passes, altitude changes, foreground parallax, progressive acceleration, smooth horizon control.
- Avoid map view, visible red lines, annotations, teleporting, reverse motion, jump cuts, visible drone, guide characters, flat terrain, deformed landmarks, flickering structures.

Use numbered stops instead when the video depends on close character interactions, exact character count, indoor navigation, or object-level continuity.

### Numbered Stop Marker Rules

For the first-frame image prompt:

- Do not draw red route lines, connecting lines, or arrows by default.
- Use small numbered markers near each target or on the floor beside each target.
- Markers must be ordered by reachable spatial depth, not randomly scattered.
- Marker 1 should usually be closest to camera; later markers move deeper into the scene.
- Each next stop must be physically reachable from the previous one without crossing walls, water, furniture, railings, people, or other obstacles.
- The scene must be designed around a walkable/glideable/flyable route before placing characters.

Only use a continuous red route line if the user explicitly asks for it or the specific workflow handles route lines reliably.

## Variable Count Handling

If the user specifies a number of people/targets, build the whole asset plan, route, timeline, and video prompt around exactly that number. Do not default back to five.

Recommended target counts:

| Duration | Best count | Handling |
| --- | --- | --- |
| 5-8s | 1-3 targets | one clear approach, few actions |
| 8-12s | 3-4 targets | short interactions, one final reveal |
| 12-15s | 4-5 targets | ideal for sequential stops |
| 15-25s | 5-8 targets | shorter beats and group transitions |
| 25s+ | 8+ targets | split into groups/zones |

If the user says “a group” without a number, choose a practical default based on duration, usually 4-5 main interaction targets. Background extras may exist only if requested and must remain secondary.

Always write:
“exactly [N] main characters/targets” and “do not add or remove main targets.”

## POV Identity Selection

FPV does not always mean normal human eye level. If the user specifies the POV, honor it. If not, choose a POV that makes the scene more coherent or interesting.

| Scene / intent | Good POV choices | Movement cues |
| --- | --- | --- |
| palace, mansion, apartment, party | invited guest, butler, courier, pet cat | walking sway, room turns, hand/paw glimpses |
| modern living room, cafe, cozy home | pet cat, robot vacuum, visitor | low-angle gliding, furniture legs, paws/tail or wheel hum |
| outdoor landscape, city, battlefield | drone, bird, kite, spirit | aerial arcs, height changes, wind, no footstep bob |
| museum, exhibition, showroom | visitor, guide robot, security camera | slow walkthrough, display pauses, precise turns |
| horror / mystery | child, flashlight holder, CCTV, ghost | low height, hesitant movement, limited view |
| car/train/boat/aircraft | passenger, driver, mounted camera | constrained path, window motion, engine/road/water sounds |

POV constraints:
- Human: eye-level height, walking bob, breathing, hands/sleeves may appear.
- Pet cat/dog: low height, curious head turns, paws/tail may appear, no human hand gestures.
- Drone: smooth continuous flight, altitude changes, banking turns, propeller/wind sound, no walking bob.
- Robot vacuum/small robot: very low height, slow floor gliding, furniture legs loom large, mechanical hum, cannot climb stairs or jump.
- Bird/insect/spirit: floating arcs or gliding, unusual height, but still continuous and motivated.
- Object POV: movement must follow the object’s plausible motion unless the concept is surreal.

Always enforce physical limits. A cat cannot float over a table; a drone cannot pass through walls; a robot vacuum cannot jump onto a sofa; a human cannot squeeze through furniture.

## Video Prompt Structure

Default structure:

1. Input usage: first frame, numbered route reference, character references, or red-line route-control image
2. Specs: aspect ratio, duration, one-shot
3. POV identity and physical movement
4. Route order: numbered target stops for close interaction, or geography segments for red-line path control
5. Compact timeline with one beat per target or one beat per route segment
6. Environment motion and sound design if useful
7. Consistency and avoid list

Keep the final video prompt directly copyable. Do not impose a fixed character limit unless the user asks for one.

## Template: Video Prompt

```text
使用上传图片作为首帧、编号路线参考和 [N] 个角色/目标外观参考，生成一段 [比例]、[时长] 秒、一镜到底的 [场景类型] [POV身份] FPV 视频。首帧中的编号 [1..N] 只作为镜头停靠顺序参考，不要出现在最终画面里。最终视频不要出现数字、编号、路线、箭头、文字标签或 UI。

观众/摄像机是一位/一台 [POV身份]，从 [起点] 出发，严格按编号顺序移动：[起点] → 1 [目标1] → 2 [目标2] → ... → [终点/回望]。本视频包含 exactly [N] 个主要人物/目标：[列出名称]，不要增加或减少主目标。角色脸、服装、位置、身份保持参考图一致。

镜头运动必须符合 [POV身份] 的物理限制：[低机位/步行/飞行/滑行/车载等具体运动]；移动连续，有真实加速减速，不能瞬移、跳切、穿过障碍物或变成其他 POV。

时间轴：
0.00-[入口时间]：[建立起点和环境动态]
[时间]-[时间]：移动到 1，[目标1动作/台词/反应]
[时间]-[时间]：移动到 2，[目标2动作/台词/反应]
...
[结尾时间]：到达 [终点] 或回望全景，形成空间层次。

环境动态：[水波/窗光/咖啡蒸汽/灯光/风/反光/布料/屏幕等]。
避免：编号残留、路线/箭头、换脸、同脸、身份漂移、主目标数量变化、穿模、跳切、瞬移、错误 POV、过度抖动、场景漂移、低质、畸形、水印。
```

## Common Pitfalls

1. Asking GPT Image for a continuous red route line by default.
   - Prefer numbered stop markers. Continuous lines often become disconnected, cross obstacles, or contaminate the video.

2. Letting numbered stops scatter randomly.
   - First define a walkable/glideable/flyable spatial route, then place numbered stops along it.

3. Ignoring the user’s specified count.
   - Use exactly the requested number in assets, route, timeline, and constraints.

4. Treating every POV like a human.
   - Robot vacuums need floor gliding; cats need low curious movement; drones need flight; humans can show hands and walking sway.

5. Giving every person full dialogue in high-count scenes.
   - For more than 6 targets, use groups, gestures, glances, or quick beats.

6. Forgetting to remove markers in the final video.
   - Always say numbers/markers are planning references only and must not appear in final output.

7. Forgetting that red-line path control and numbered stops solve different problems.
   - Numbered stops are better for characters and interiors; red-line route control is better for world-scale flythroughs, racing lines, and map-to-world journeys.

## Verification Checklist

Before returning the prompt, check:

- [ ] Aspect ratio and duration are specified
- [ ] First frame / route reference / character references are assigned
- [ ] Main target count is explicit and matches the user request
- [ ] POV identity is explicit or reasonably inferred
- [ ] POV movement physics match the identity
- [ ] Route order is explicit and physically continuous
- [ ] Timeline covers the full duration and fits the target count
- [ ] Each target has an action/reaction, or group beats for high-count scenes
- [ ] Character/object consistency constraints are repeated
- [ ] Environment secondary motion is included where useful
- [ ] Negative constraints mention no route lines/arrows/numbers/markers in final video
- [ ] Negative constraints mention no added/removed main targets
- [ ] Red-line path-control mode is used only when the scene is route-shaped and large-scale, or the user explicitly requests it
- [ ] Generated prompts are in Chinese by default unless the user explicitly requested English or a target tool requires English
- [ ] Final prompt is directly copyable

## References

Read `references/session-patterns.md` for examples and session-specific lessons from the initial development of this workflow.

Read `references/mayz-seedance-world-route-case.md` for the Seedance 2.0 red-line world-route pattern: aerial map control image, strict drawn route geometry, map-to-world flythrough, biome progression, speed-run/racing-line mode, and theme-park ride style journeys.

Read `references/public-article-angle.md` when explaining this workflow publicly in a WeChat article, X thread, tutorial intro, or demo write-up. It captures the session framing: FPV prompts are action trajectories, not just visual descriptions; numbered stops vs red-line path control; space-first design; POV physics; count-duration tradeoffs.

Read `references/cafe-cat-numbered-stops-case.md` when the user asks for cafe, cozy indoor, pet-cat POV, or low-angle numbered-stop interaction scenes. It captures a 15-second / 3-person cafe route pattern and the cat-specific movement constraints that prevent drone-like motion.
