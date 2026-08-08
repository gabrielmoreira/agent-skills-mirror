# Generating the footage

You do not need to generate anything to use this skill — every prompt in this
repo ships with a hosted clip you can `curl`. This file is for when you want new
footage.

**Write the prompt first.** The model matters far less than the prompt; a good
prompt on a mid-tier model beats a lazy one on the best model available. The
formula and ~37 proven prompts are in `prompt-bank.md`.

---

## Any model

Whatever you are generating with — Seedance, Veo, Kling, Sora, Runway — the same
settings apply:

| Setting | Value | Why |
|---|---|---|
| aspect ratio | **16:9** | full-bleed heroes letterbox at any other ratio |
| resolution | 1080p | 720p shows compression in the scrim gradient |
| duration | 5s for a loop hero, 8s for a fly-through | video cost scales superlinearly with duration |
| audio | off / ignored | heroes are muted; audio is dead weight |

**Generate three, keep one.** It is a slot machine — the formula stacks the odds
heavily, it does not eliminate variance.

**Keyframe first when generation costs money.** A still is roughly an order of
magnitude cheaper than a clip, and the clip inherits the look of its start frame,
so approving a still locks composition, lighting and grade before you spend.
Generate the still with the *same* prompt text, show the user, and only then pass
it as the video's start frame. Never plan to "fix it in the video".

**Anything with lettering will be garbled.** Never ask for text, logos, badges or
readable signage. If a shot needs a blank area where a mark would naturally sit,
**name the emptiness** — "an empty, undecorated dial", "a plain unmarked wall" —
rather than banning the mark. Instructing a model *not* to draw something works
poorly; describing a void it should render works reliably. (Measured on watch
dials: banning logos gave roughly 1 clean render in 5; naming the empty zone gave
5 in 5.)

---

## Higgsfield MCP specifics

If the Higgsfield MCP is connected, the whole loop can be automated. All args nest
under `params`.

**Check cost before every batch:**

```
balance                                   → credits + plan
generate_video({params:{ …, get_cost:true }})   → credits, without submitting
```

Rough card (Seedance 2.0): 720p/5s ≈ 22cr · 1080p/5s ≈ 45cr · 1080p/8s ≈ 72cr. A
`nano_banana_pro` still is ~2cr — which is the entire argument for the keyframe
gate.

**Generate:**

```
generate_video({params:{
  model: "seedance_2_0",        // identity / single scene; kling3_0(_turbo) for start-frame work
  prompt: "<subject + light + grade + one camera move + register> shallow depth of field, one continuous shot, no cuts, no on-screen text, no watermarks.",
  aspect_ratio: "16:9",
  resolution: "1080p",
  duration: 8,
  medias: [{ role: "start_image", value: "<approved image job id>" }]
}})
```

Returns `{results:[{id, status:"pending"}]}`. Then `job_status({jobId, sync:true})`
polls internally (~25s per call) and returns on a terminal state with
`results.rawUrl`. A 5s clip takes ~60–120s, an 8s clip ~120–180s — **fire the jobs
first and build the scaffold while they render.**

**Download it.** `curl -sfL -o public/hero.mp4 "<rawUrl>"`. Never leave production
pointed at the generator's CDN.

---

## Failure table

| Symptom | Cause | Fix |
|---|---|---|
| `429 rate_limit_reached` | too many jobs fired at once | it is a submit-rate cap, not a ceiling — space them a few seconds apart and retry |
| a preset-recommendation notice and no job | a dark or cinematic prompt matched a preset | pass `declined_preset_id` and re-fire to force the literal prompt |
| status `nsfw` on a clean prompt | false positive — interiors, the word "revealing", even the start image | reword the object; it is a false flag the large majority of the time |
| reference generation `failed` | video-as-image reference rejected | fall back to an independent prompt that re-describes the subject concretely; distinctive described features hold better than a generic reference |
| an old job id 404s as a media input | the workspace was reconnected | `media_import_url` the public CDN url instead |
| the clip has audio you did not ask for | default behaviour | mute the `<video>`; audio is ignored entirely for frame strips |
| garbled lettering appears | the prompt implied a mark or signage | name the empty zone instead of banning the mark (above) |

---

## Frame extraction

For scroll-scrub and ping-pong:

```bash
ffmpeg -i clip.mp4 -vf "fps=14,scale=1512:-2,unsharp=5:5:0.35:5:5:0.0" \
  -c:v libwebp -quality 78 public/frames/frame-%04d.webp
```

~110 frames for an 8-second clip. Set the site's `FRAME_COUNT` to the printed
count — a `FRAME_COUNT` lower than the strip silently makes the tail of the
animation unreachable, with no error anywhere.

Poster still for the instant-load fallback:

```bash
ffmpeg -i clip.mp4 -vframes 1 -vf scale=1600:-2 public/hero.webp
```

Last frame, for chaining or for sampling the seam colour:

```bash
ffmpeg -sseof -0.15 -i clip.mp4 -frames:v 1 last.png
```
