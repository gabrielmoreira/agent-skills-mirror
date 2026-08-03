---
name: video-generator
description: Create short videos and motion clips from a text description using AI video generation.
---

# Video Generator

Act as the director who briefs the video model. A video prompt has to carry everything a still image does *plus* time — what moves, how the camera behaves, and what changes between the first frame and the last. Your job is to turn a one-line request into a shot that reads as deliberate rather than as a wobbling still.

## When to use this skill

Use Video Generator for short social clips, product motion, b-roll, animated backgrounds, and any request that names a video, clip, animation, or motion. Reach for it whenever the deliverable moves.

## Anatomy of a strong video prompt

Build the shot deliberately rather than describing a picture and hoping it animates. Cover:

- **Subject** — who or what is in frame, concretely, including how it is framed at the start.
- **Motion** — what the subject actually does, as one continuous action. One clear action beats three vague ones.
- **Camera** — static, pan, tilt, dolly in/out, tracking, orbit. Name it; "cinematic" is not a camera move.
- **Setting & lighting** — where this happens and how it is lit, including time of day.
- **Style & mood** — live-action / 3D / anime / stop-motion, plus the feeling and pacing.
- **Duration fit** — what can plausibly complete in the clip's length. A four-second shot holds one beat, not a sequence.

Be specific where it matters and silent where it doesn't. Contradictory motion (a static camera that also orbits) is the most common cause of a smeared result.

## Working within the clip's length

- Short clips (4–6s): one subject, one action, one camera move.
- Longer clips (8–12s): a single action that develops — an approach, a reveal, a turn — not a cut between scenes.
- Never ask for cuts, scene changes, or on-screen text; generate separate clips and assemble them instead.

## How to work

1. Clarify the subject, the motion, the camera, and the target platform's aspect ratio and length.
2. Compose a prompt covering the anatomy above, in one paragraph.
3. Generate, then judge the result against the brief before offering it — a clip that ignored the camera move is a prompt problem, not a taste problem.
4. Offer variations that change a meaningful axis (camera, pacing, or lighting), not trivial reworks.

## Output format

Return the generated clip when generation is available; otherwise return the finished, ready-to-use prompt. For each, note the aspect ratio and duration it targets and one line on the directorial choice. When delivering variations, label each by the axis it explores.
