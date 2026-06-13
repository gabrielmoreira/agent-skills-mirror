# GPT Image Asset Packs for FPV Video

Use this reference when a user wants GPT Image 2 / ChatGPT image generation to prepare assets for an FPV image-to-video workflow.

## Multi-image asset pack beats single contact sheet

For ChatGPT / GPT Image workflows, deliver one batch-generation prompt that asks the model to generate multiple separate images in a single response. Do not deliver many independent prompts unless the user explicitly asks for per-image prompts. The prompt should still request separate images, not one crowded contact sheet.

If ChatGPT can generate multiple images in one response, request separate images. Do not stop at the first-frame prompt when the scene contains named people/targets; identity consistency needs independent reference images.

For close-interaction / character scenes, request:

1. Numbered first frame
   - 16:9 scene from the intended starting viewpoint
   - uses small numbered stop markers near each main target
   - no red line unless the user explicitly asks for a drawn route

2. Character references
   - one image per main character/target
   - clean portrait or full-body card
   - no labels, no route marks, no text if the video model is sensitive to text

3. Optional clean first frame
   - same composition as the numbered first frame
   - removes numbers, arrows, route marks, and labels
   - best used as the actual image-to-video first frame

For world-route / path-control scenes, request:

1. Red-line first frame or route-control map
   - 16:9 route-planning image from the intended starting viewpoint or aerial map
   - includes one continuous red route line and ordered route geometry

2. Optional clean world/scene reference without the red line

3. Optional landmark or character references if specific destinations need stable appearance

Video prompt rule: numbered markers and red-line marks are route-planning references only and must not appear in the final video.

## Continuous-route wording

Use topological constraints. GPT Image often places 1,2,3,4,5 as decorative labels unless the prompt explicitly defines a walkable route.

Reliable language:

```text
This image is not a random group scene. First design one continuous walkable space from foreground to background. Draw a single unbroken red route line on the floor/path. The line starts at the camera entrance, follows only physically walkable ground, and passes through stops 1, 2, 3, 4, 5 in order. Each next stop must be physically reachable from the previous stop without crossing walls, water, railings, furniture, or people. Stop 1 is closest to camera, stop 2 is slightly farther, stop 3 is midground, stop 4 is deeper in the scene, and stop 5 is the destination/final reveal. Do not scatter the stop numbers around the image. Do not draw multiple route lines or disconnected segments.
```

Adapt this for non-human POVs:
- drone: “continuous flyable air corridor”, avoid walls/ceilings/people
- pet cat: “low floor-level path”, route goes under/around furniture but never floats
- robot vacuum: “floor-only path”, cannot climb stairs or cross thick rugs if unrealistic
- bird/spirit: “continuous aerial arc”, still no teleporting or passing through solid objects

## Count-aware asset request pattern

If the user specifies N people/targets in a close-interaction or character scene, request exactly:

- 1 numbered first-frame image containing exactly N main stops
- N character reference images
- optionally 1 clean first-frame image

If the user specifies N people/targets in a world-route/path-control scene, request exactly:

- 1 red-line route-control image or route-planning map
- N character/landmark references only when those targets must stay visually consistent
- optionally 1 clean route/world reference without red line

Include this line:

```text
Generate exactly [N] main characters/targets and exactly [N] stop points. Do not add extra main characters. Background extras are allowed only if I explicitly ask for a crowd, and they must remain visually secondary.
```

## Example asset-pack skeleton

```text
请一次性生成 [N+1] 张图片，用于后续制作一段 [场景] 第一人称 FPV 沉浸式 AI 视频。所有图片保持同一套美术风格、同一空间设定、同一光影质感、同一人物设计语言。

图片 1：[场景] FPV 首帧图，带连续红色运镜路线。
生成一张 16:9 横版图片，摄像机身份是 [POV]，从 [起点] 看向 [空间]。这张图的核心是一条清晰、连续、物理可行的路线。请先设计一个从前景到远景逐步深入的空间：[列出前景、近景、中景、远景]。

在 [地面/空中/道路/水面] 上画一条单一、连续、不断开的红色运镜路线，从 [起点] 出发，依次经过 1 到 [N] 个停靠点，最后到达 [终点]。每个点必须在同一条路线上，按行进顺序排列，不要随机散布。路线不能穿过 [当前场景的障碍物]。

[N] 个主要目标沿这条连续路线依次分布：
1 [名称]：[位置]，[外观]，[动作/状态]
2 [名称]：[位置]，[外观]，[动作/状态]
...

图片 2 到 图片 [N+1]：分别生成 [N] 个主要角色/目标的独立参考图。每张参考图背景简洁，不要文字、标签或红线。角色脸部、服装、颜色和气质要明显不同。

如果系统允许额外生成 1 张，请生成干净版首帧图，内容与图片 1 一致，但去掉红色路线、箭头、编号和所有文字标记。
```

## Session lessons captured

- A single preproduction board is less ideal than multiple separate images when ChatGPT image generation can output multiple images.
- Red-line first frames are acceptable if the later video prompt explicitly forbids showing the red line in final output.
- Route continuity must be specified as topology, not just as “1→2→3→4→5”.
- User-specified target count must drive number of reference images, stops, timeline beats, and negative constraints.
- POV identity changes the entire route physics; write for the selected camera body, not generic “FPV”.
