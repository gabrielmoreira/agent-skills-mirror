# `sprite-gen video` — image to video with your own Grok login (engine SSoT)

> Owns: `sprite-gen video` / `video-extend` / `video-edit` / `video-resume`: stills and clips to mp4 through Grok Imagine with the user's own credential · Index: [docs/README.md](README.md)

`sprite-gen video` animates one still into a short mp4 through **Grok Imagine**
(xAI `POST /v1/videos/generations`). It is the video counterpart of
[`sprite-gen gen`](gen.md): one call = one still (+ prompt) → one **verified** mp4
on disk plus a machine-readable report. The sprite-gen skill routes standalone
video requests here from any agent engine.

The same engine also pins a **last frame**, guides a clip with **reference
images**, **extends** an existing clip (`video-extend`), **edits** one with a
prompt (`video-edit`) and **asks again** for a generation a run left unfinished,
by its `request_id` (`video-resume`). The mode table below is the design memo for those modes
(2026-09-13); the pipeline verbs in [video-pipeline.md](video-pipeline.md)
(`video-canvas` → `video` → `video-frames` → `video-loop`, `video-set`) keep
calling `sprite-gen video --image …` exactly as before and know nothing about
the new modes.

No credential is shipped with this repository. You bring your own, in one of two
forms, and every run reports which one it used.

## Modes — which flags call what

Measured 2026-09-13 with the subscription login (`grok-login`) and the direct
REST calls below (vault `projects/sprite-gen/_assets/grok-video-mode-probe-2026-09-13/report.md`);
limits from docs.x.ai `model-capabilities/video/*` read the same day.

| Verb / flags | Endpoint · model | Body fields | Options allowed | Local pre-checks (before any call) | `mode` |
|---|---|---|---|---|---|
| `video --image A` | `POST /v1/videos/generations` · `grok-imagine-video-1.5` (`--model` free) | `image{url}` | duration 1–15, resolution, aspect, audio | still exists; unchanged contract (body snapshot pinned by test) | `image-to-video` |
| `video --image A --last-frame B` | same · 1.5 only | `image{url}`, `last_frame{url}` | same | both stills exist; classic `grok-imagine-video` rejected | `first-last` |
| `video --last-frame B` | same · 1.5 only | `last_frame{url}` | same | classic rejected | `last-frame` |
| `video --reference X [--reference Y …]` (+ optional `--image`) | same · 1.5 (classic accepts references alone, measured 2026-09-13, but not `--image` + references) | `reference_images:[{url}…]` (+ `image{url}`) | duration, aspect, audio; resolution **480p/720p only** | 1–7 references; prompt tags `<IMAGE_n>` with `0 ≤ n < count` (0-based); `--resolution 1080p` rejected; classic + `--image` + references rejected | `reference` |
| `video-extend --video in.mp4 --duration N` | `POST /v1/videos/extensions` · **`grok-imagine-video` forced** (1.5 answers `400 Video extension is not supported for this model`) | `video{url}`, `duration` | duration 2–10 (extension length only; default 6). No resolution / aspect / model flags: output inherits the input's, capped at 720p | `.mp4` with an `ftyp` box; ffprobe duration 2–15 s | `extend` |
| `video-edit --video in.mp4` | `POST /v1/videos/edits` · **`grok-imagine-video` forced** (1.5 answers `400 Video editing is not supported for this model`) | `video{url}` | none of duration / resolution / aspect / model: output inherits the input's, capped at 720p | `.mp4` with an `ftyp` box; ffprobe duration ≤ 8.7 s | `edit` |
| `video-resume --request-id <id>` | **no POST** — `GET /v1/videos/{id}` only; the model is whatever the request was made with | — | none: the request is the one an earlier run submitted | the id is letters, digits, `.`, `_`, `-` | `resume` |

Invariants:

- **The `--image`-only body is byte-for-byte what it was** (`model`, `prompt`,
  `duration`, `resolution`, `image.url`, optional `aspect_ratio` /
  `generate_audio`). A test snapshots it; the pipeline (`video-set` and the
  four pipeline verbs) is not touched by this work.
- One of `--image`, `--last-frame`, `--reference` is required; `--image` is no
  longer required on its own.
- `<IMAGE_n>` is **0-based**: `<IMAGE_0>` is the first `--reference`. The probe's
  three-reference run tagged `<IMAGE_0>…<IMAGE_2>` and the clip picked up the
  third image's scene under `<IMAGE_2>`; the docs' prose says the same
  ("`<AUDIO_0>` … with `<IMAGE_0>` … when you also pass images") while its code
  samples write `<IMAGE_1>`. A tag outside `0..count-1`, or any tag with no
  references, is refused locally.
- Extension and editing inherit resolution and length from the input and take
  **no** `--resolution` / `--aspect-ratio` / `--model`; `video-extend` verifies
  that the returned clip is at least as long as the input (the API returns
  original + extension as one clip: 15.04 s in → 20.04 s out in the probe).
- The report (`sprite-gen-video-report`) gains `mode` and `inputs` (local paths
  by role, never URLs or tokens); every existing field stays.

## Setup — pick one credential

| `auth_source` | What you need | Billing | How to set it up |
|---|---|---|---|
| `grok-login` (default) | the `grok` CLI signed in once | your SuperGrok **Imagine quota** (no console spend) | install the grok CLI, run `grok login` (`--oauth` for a browser, `--device-auth` for a headless box). It writes `~/.grok/auth.json`; this tool only reads it. |
| `XAI_API_KEY` | an xAI console API key | console credit | `export XAI_API_KEY=xai-…` |

Resolution order is fixed for both images and videos: **the Grok subscription
login wins**, even when `XAI_API_KEY` is set. `GROK_HOME` relocates `~/.grok`.
Only when no login file exists can the configured API key use console credits.
An expired, unreadable, corrupt or API-rejected login stops the request; it never
switches to API credit. A clip that does leave on `XAI_API_KEY` says so on stderr
before it uploads — one line per submitted job, naming the duration and resolution
it is billed on; the subscription route stays silent. An empty API key is ignored when the login is usable,
but is an error when no login exists. With neither credential, the run stops
with both setup paths spelled out.

### The login token expires — and this tool does not refresh it

The grok CLI stores an OIDC access token that lasts about six hours. Any
long-lived grok session refreshes it proactively about five minutes before
`expires_at` (2026-09-13 measurement: a resident session rewrote `auth.json` at
00:15Z for a 00:20Z expiry), so the token only actually expires when no grok
process has run for hours. `sprite-gen video` reads `expires_at` **before
uploading anything**; if it has passed, the run fails with the refresh
prescription instead of gambling on a 403 mid-upload:

```
xai: the grok login token expired at 2026-09-08T10:56:34Z (now …); nothing was uploaded.
  refresh it with `grok models` run from an empty directory (e.g. `cd "$(mktemp -d)"`) — a non-agent round-trip; never a bare prompt like `grok -p …`, which starts the coding agent in your cwd — or sign in again with `grok login`. This tool never rewrites ~/.grok/auth.json itself.
```

Why `grok models` and not a prompt: `grok -p ok` is not a ping. It starts the
coding agent in the current directory, which reads it, may write files and may
call paid APIs on its own (2026-09-13: run inside a worktree it overwrote a
script and spent a video generation). `grok models` only runs the CLI's startup
auth path (`auth: silent refresh` in `~/.grok/logs/unified.jsonl`), prints the
model list and exits, writing nothing outside `~/.grok`. Run it from an empty
directory anyway. If it prints a login error instead of the model list, the
refresh token is gone too: `grok login`.

Why not refresh it here: `auth.json` is the grok CLI's file, the refresh token in
it may rotate, and a second writer would break the login the user relies on
everywhere else. The same shape as `sprite-gen gen`'s `codex login status` gate.

### Direct API transport

Grok Build's built-in `image_to_video` tool posts without `output.upload_url`, and
on Zero-Data-Retention teams the API answers `HTTP 400 — Zero Data Retention teams
must provide output.upload_url for video generation`. The same login calling
`/v1/videos/generations` directly (no `output.upload_url`) succeeds and bills the
Imagine quota (verified 2026-08-22, re-verified 2026-09-08). So this engine calls
the API itself and never routes through the agent-side tool.

## CLI

### `sprite-gen video` — generations (image-to-video, first/last frame, references)

```bash
sprite-gen video \
  [--image still.png] \                # first frame / the still to animate (PNG / JPEG / WebP, inline data URL)
  [--last-frame end.png] \             # pin the closing frame (grok-imagine-video-1.5 only); alone or with --image
  [--reference a.png --reference b.png …] \   # 1..7 references; name them in the prompt as <IMAGE_0>, <IMAGE_1>, …
  --prompt "Camera locked. Gentle idle sway, tail flick." \   # or --prompt-file
  --out clip.mp4 \
  [--duration 6]                     # 1..15 seconds (default 6)
  [--resolution 720p]                # 480p | 720p | 1080p (default 720p; 1080p is refused with --reference)
  [--aspect-ratio 1:1]               # 1:1 16:9 9:16 4:3 3:4 3:2 2:3 (default: the still's ratio)
  [--audio | --no-audio]             # default: the API's default (audio on)
  [--model grok-imagine-video-1.5]
  [--report clip.report.json]
```

At least one of `--image`, `--last-frame`, `--reference` is required. The mode is
derived from the flags (see the table above) and written to the report as `mode`.

Backward-compatible wrapper: `$SPRITE_GEN_ROOT/.venv/bin/python $SPRITE_GEN_ROOT/scripts/generate_sprite_video.py …` (same args).

What happens, in order:

1. Validate the request (prompt, stills, duration, resolution, aspect ratio, the
   mode rules: ≤ 7 references, `<IMAGE_n>` tags in `0..count-1`, no tag without a
   reference, no 1080p with references, no `last_frame` / `image`+`reference` on the
   classic model) and resolve the credential — all before any network call.
2. `POST /v1/videos/generations` with `model`, `prompt`, `duration`, `resolution`,
   then `image.url` / `last_frame.url` / `reference_images[].url` as base64 data
   URLs, optional `aspect_ratio` / `generate_audio`. A `401/403` names the
   credential source and its fix; any reply without a `request_id` fails with the
   API's own error text.
3. `GET /v1/videos/{request_id}` every 4 s until `status` is `done`. `failed`,
   `expired` or a non-2xx poll fails loudly — except a poll answered `429` or `500`,
   `502`, `503`, `504`, or one that gets no answer it can read (the connection failed
   or timed out; the answer broke on the way — a body shorter than its
   `Content-Length`, a status line that is not one, a refusal's body cut the same way;
   or a `200` body that is not JSON): the request was accepted, so that poll is asked
   again on the same `request_id` (a new POST would buy the clip twice; a GET buys
   nothing), after a wait that doubles from 8 s up to 60 s while the polls fail and goes
   back to 4 s on an answer. A `[video] poll N of generation <id> was refused (429);
   asking again in 8s` line — or `… got no answer (timed out); asking again in 8s`,
   the reason `IncompleteRead(10 bytes read, 190 more expected)` or `response was not
   valid JSON` for an answer it could not read — goes to stderr each time.

   The poll timeout (`SPRITE_GEN_VIDEO_TIMEOUT_SECONDS`, default 600) is the one time
   limit of the accepted request. It counts from the POST's send and bounds the polls,
   their waits and the clip's downloads (step 4) alike:

   - Each poll reads only what is left of it. One whose answer stalls, or comes too
     slowly for its 120 s read timeout ever to fire, is cut when the timeout comes and
     counts as a poll that got no answer (`timed out`).
   - A poll whose wait would reach the timeout is not asked. A generation still
     pending, refused or unanswered then is *unfinished* (below) at once.
   - The POST is not cut by it: its answer is the one way to the `request_id`, under its
     own 120 s read timeout. One answered after the whole timeout is unfinished before
     any poll.

   So a caller that kills the run at a hard limit gets the `request_id` back when it
   sets the timeout under that limit, with room for the process to start and for the
   POST. A poll answered `401` or `403` — the credential stopped working after the POST,
   typically a login that expired — is unfinished at once. No clip is written on any
   failure path.
4. Download `video.url`, verify the bytes start with an mp4 `ftyp` box, then move
   the file into `--out` atomically (`.part` staging). The clip is made by now and may
   be billed, so a download that fails never ends the run without its `request_id`, and
   a done poll that names no URL to download (none, an empty one, anything but an
   `http(s)://` string) is *unfinished* too. A download that gets no answer it can read
   (the connection refused or timed out, the body cut short of its `Content-Length`) or
   that the clip's host refuses with `429`, `500`, `502`, `503` or `504` is downloaded
   again, after 8 s and then 16 s — three downloads in all, within the poll timeout: each
   reads only what is left of it, so one that stalls or whose bytes come too slowly is
   cut when it comes (`timed out`), and one whose wait would reach it is not tried. A
   `[video] download N of generation <id> got no answer (<reason>); downloading again in
   8s` (or `… was refused (503); …`) line goes to stderr before each. One still failing,
   one refused with another status (a `401` or `403` is asked once more with the bearer
   token first), a download the timeout leaves no time for, or bytes that are not an mp4
   end the run *unfinished* (below).

Reference-to-video tends to lock the opening composition to a referenced scene
image (probe m3: the clip opened on the third reference's framing), so put
character references first and scene references last, or leave the scene out.

### `sprite-gen video-extend` — continue a clip

```bash
sprite-gen video-extend \
  --video clip.mp4 \                   # 2..15 s mp4 (a 15-second clip's 15.04 s container is accepted)
  --prompt "she presses the attack, camera tracks low" \
  --out longer.mp4 \
  [--duration 6]                     # seconds ADDED, 2..10 (default 6)
  [--report longer.report.json]
```

Model is fixed to the classic `grok-imagine-video` (`grok-imagine-video-1.5`
answers `400 Video extension is not supported for this model`). There are no
`--resolution` / `--aspect-ratio` / `--model` flags: the output inherits the
input's, capped at 720p. The input is checked locally (`.mp4`, `ftyp` box,
ffprobe length) before anything is uploaded; ffprobe missing is an error, not a
skipped check. The API returns **input + extension as one clip** (15.04 s in →
20.04 s out); a result shorter than the input is refused and not written. The
report carries `mode: "extend"`, `inputs.video`, `input_duration` (ffprobe
seconds) and `duration_requested` (the seconds added).

### `sprite-gen video-edit` — change a clip with a prompt

```bash
sprite-gen video-edit \
  --video clip.mp4 \                   # at most 8.7 s
  --prompt "change her hakama to solid black, keep everything else" \
  --out edited.mp4 \
  [--report edited.report.json]
```

Same fixed classic model, same inherited resolution / aspect / length (the probe's
8.00 s input came back 7.71 s — the API trims the tail). Inputs over 8.7 s are
refused locally with an ffmpeg trim hint; there is no `--duration` at all.

### `sprite-gen video-resume` — ask again for an unfinished generation

```bash
sprite-gen video-resume \
  --request-id <id> \                  # the request_id an unfinished run named
  --out clip.mp4 \
  [--report clip.report.json]
```

No POST: it polls `GET /v1/videos/{id}` exactly as step 3 above (the same retries,
backoff and poll timeout, counted from the first poll and bounding the downloads too), then downloads, verifies and
publishes the clip as step 4. Nothing is submitted, so nothing is bought twice and the
`XAI_API_KEY` route prints no charge notice. Run it on the credential that submitted
the request — the unfinished report's `auth_source`; refresh an expired login first.

- The report is a `sprite-gen-video-report` with `mode: "resume"`, the same
  `request_id`, `inputs: {}` and `duration_requested: null`; `model` and
  `duration_reported` are what the finished poll says.
- Cut short again — the timeout, a rejected credential, or a download that failed —
  it is unfinished on the same id, `verb: "video-resume"` (below), and can be resumed
  again. Each resume polls afresh, so a clip whose download failed is fetched from the
  URL the new poll names.
- A request xAI does not know (`404`), or one that failed or expired, ends with its
  status like any failed poll.
- The clip is checked as an mp4 (`ftyp` box) only: `video-extend`'s length rule needs
  the input clip, which this verb does not take.
- The id is refused before any call unless it is letters, digits, `.`, `_` and `-`
  (it goes into the URL path).

### The report

`sprite-gen-video-report` carries `auth_source`, `model`, `mode`, `request_id`,
`inputs` (local paths by role: `image`, `last_frame`, `reference_images`,
`video`), `bytes`, `host`, requested/reported duration (`input_duration` for
extend / edit), resolution, aspect ratio, audio flag, `elapsed_seconds`, and
`polls`, `polls_refused` (how many of `polls` xAI answered 429 or 5xx, each asked
again), `polls_unanswered` (how many got no answer they could read, each asked
again) and `downloads` (how many downloads the clip took, the last one whole: 1 unless
one failed). The pre-modes `image` field stays. **Tokens and download URLs are never
printed or written** — only the download host (`vidgen.x.ai`).

### An unfinished generation

xAI accepted the request and the run ended before it did — the poll timeout came with
its polls still pending, refused or unanswered (or before any poll), xAI rejected the
credential on a poll, or the poll said done and the clip could not be downloaded in
time or at all, or the poll named no URL to download it from (step 4). It may
finish and be billed — a clip that is done is made — so the run ends naming the
request and the `video-resume` command that asks for it again, never as a refusal to
send again:

```
video: generation <id> was accepted, but its polls were refused (last answer 429) until the poll timeout (600s, 14 polls); it may still finish and be billed — ask for request_id=<id> again with `sprite-gen video-resume --request-id <id> --out /abs/clip.mp4` instead of submitting a new request; nothing was written
video: generation <id> was accepted, but its polls got no answer (last: timed out) until the poll timeout (600s, 14 polls); it may still finish and be billed — ask for request_id=<id> again with `…` instead of submitting a new request; nothing was written
video: generation <id> still 'pending' after 150 polls — poll timeout; it may still finish and be billed — ask for request_id=<id> again with `…` instead of submitting a new request; nothing was written
video: generation <id> was accepted after the poll timeout (600s) had run out, before any poll; it may still finish and be billed — ask for request_id=<id> again with `…` instead of submitting a new request; nothing was written
video: generation <id> was accepted, but xAI rejected the credential (grok-login) on poll 30 (answer 401); it may still finish and be billed — refresh the login with `grok models` run from an empty directory (e.g. `cd "$(mktemp -d)"`) or `grok login`, then ask for request_id=<id> again with `…` instead of submitting a new request; nothing was written
video: generation <id> is done, but its download got no answer (last: IncompleteRead(1048576 bytes read, 3195904 more expected)) after 3 attempts; the clip is made and may be billed — ask for request_id=<id> again with `…` instead of submitting a new request; nothing was written
video: generation <id> is done, but its download was refused (last answer 503) after 3 attempts; the clip is made and may be billed — ask for request_id=<id> again with `…` instead of submitting a new request; nothing was written
video: generation <id> is done, but its download was refused (answer 404); the clip is made and may be billed — ask for request_id=<id> again with `…` instead of submitting a new request; nothing was written
video: generation <id> is done, but its download got no answer (last: timed out) until the poll timeout (210s, 1 attempt); the clip is made and may be billed — ask for request_id=<id> again with `…` instead of submitting a new request; nothing was written
video: generation <id> is done, but its poll named no video url to download; the clip is made and may be billed — ask for request_id=<id> again with `…` instead of submitting a new request; nothing was written
video: generation <id> is done, but its download brought 34 bytes that are not an mp4 (no ftyp box); the clip is made and may be billed — ask for request_id=<id> again with `…` instead of submitting a new request; nothing was written
```

The line carries no `(HTTP <n>)`, the status of a refusal line (docs/gen.md): a caller
that reads `(HTTP 429)` there sends the request again, which is unbilled only when the
request was refused. The stderr notes before it say the status in plain digits for the
same reason. With `--report` the run leaves a
`sprite-gen-video-unfinished` report there, and nothing on stdout:

```json
{"kind": "sprite-gen-video-unfinished", "provider": "grok-imagine", "verb": "video",
 "auth_source": "grok-login", "model": "grok-imagine-video-1.5", "request_id": "<id>",
 "out": "/abs/clip.mp4", "polls": 14, "polls_refused": 14, "polls_unanswered": 0,
 "last_poll": {"http": 429, "status": null}, "elapsed_seconds": 600.0}
```

`last_poll` gains `"error"` (what the transport said: `timed out`,
`IncompleteRead(10 bytes read, 190 more expected)`, `response was not valid JSON`, …)
when the last poll got no answer it could read, its `http` then `null`. A run whose
clip could not be downloaded adds `downloads` (how many were tried) and
`last_download`, how the last one ended: `http` the status the clip's host refused it
with, else `null`; `error` what the transport said when it got no answer it could read,
or `not an mp4 (no ftyp box)` with the `bytes` that came; its `last_poll` is the done
poll (`{"http": 200, "status": "done"}`):

```json
{"kind": "sprite-gen-video-unfinished", "provider": "grok-imagine", "verb": "video",
 "auth_source": "grok-login", "model": "grok-imagine-video-1.5", "request_id": "<id>",
 "out": "/abs/clip.mp4", "polls": 31, "polls_refused": 0, "polls_unanswered": 0,
 "last_poll": {"http": 200, "status": "done"}, "downloads": 3,
 "last_download": {"http": null, "error": "IncompleteRead(1048576 bytes read, 3195904 more expected)"},
 "elapsed_seconds": 144.0}
```

Bytes that came whole and are not an mp4 make the run unfinished, not refused, and
are not downloaded again:

- They are no verdict of xAI's on the request. Its one content-policy signal is
  `respect_moderation: false` on the done poll, read before any download and refused
  as a content-policy block. Anything else at the clip's URL — an expired link's page,
  a proxy's or captive portal's error page served `200` — is a fault in delivering a
  clip that is made.
- The `request_id` is the only way back to a clip that may be billed. A refusal would
  leave one path, a new submission, which buys it again; `video-resume` costs a poll
  and polls afresh, so it downloads from the URL the new poll names. If those bytes
  are not an mp4 either, it is unfinished again — never a second purchase.
- The same URL would bring the same bytes, so the run does not download it again
  itself.

`auth_source` is the credential that submitted it — the one that can ask for it again.
A report already at that path is replaced, as on success.
Every verb that polls (`video`, `video-extend`, `video-edit`, `video-resume`) does
the same, `verb` naming it; a `video-resume` report's `model` is `null`.

A POST that gets no answer it can read is not unfinished: no `request_id` could be
read, so it ends at once and is never sent again. Its line is the transport's own
(`xai: request failed or timed out; no automatic retry (the server may have accepted
it)`), or `xai: response was not valid JSON` for a whole answer that is not JSON.
Python callers catch `xai.TransportError`, a `SystemExit` with that line and the
transport's words in `reason`.

## Quotas and limits

- Imagine quota is a weekly SuperGrok allowance; when it is exhausted the API
  refuses the POST and the run fails with that message. A refused POST is never sent
  again here — the provider may have taken it; only a poll of an accepted request is
  asked again (step 3).
- A refused request or a failed poll names the provider's code after the status,
  `(HTTP 400) code=invalid_argument`, read from a top-level `code` or the `error`
  object. `invalid_argument` covers moderation and bad parameters alike, so it is
  not called a content-policy refusal; a clip that comes back `done` with
  `video.respect_moderation: false` is:
  `<verb>: generation <id> refused by the provider's content policy (HTTP 200) respect_moderation=false; nothing was written`.
- Duration 1–15 s, resolutions 480p/720p/1080p, the seven aspect ratios above —
  from the xAI video docs as of 2026-09-08. Reference-to-video: ≤ 7 images, 720p
  max; extension: input 2–15 s, 2–10 s added; editing: input ≤ 8.7 s (docs as of
  2026-09-13). A value outside those is rejected locally before the call.
- Output is whatever the model returns (typically H.264 mp4 with audio unless
  `--no-audio`). Downstream frame extraction is a separate step and not part of
  this command.

## Related

- [video-pipeline.md](video-pipeline.md#a-clip-from-a-video-mcp-on-your-agent--zcre) — a clip your agent makes with a video MCP (ZCRE) instead of this command
- [docs/README.md](README.md) — documentation index
