# Private content composition v0

The existing `content-ops` capability owns video preparation, render attempts
and result readback. The TypeScript owner is
`loopx/control_plane/capabilities/content_media.ts`. Python handles private
files and transport; the optional `loopx-media` extension performs specialized
image, audio and video computation. This is a local composition slice, not a
new generic capability or a replacement publication lifecycle.

The active callers are the Agent-facing CLI and the Goal's packaged **Content
production** workbench. A prepared brief is shared between them. The Agent
absorbs source discovery, identifiers, hashes and timing. The owner selects a
prepared composition, starts/cancels its render and reads the result in place;
there is no browser source-directory or JSON-entry step. Lark can convey the
request to an Agent but does not gain an independent renderer or upload action.

## Plan and source scope

`content_ops_media_plan_v0` contains:

| Field | Meaning |
| --- | --- |
| `title`, `width`, `height`, `fps` | Name and bounded output geometry/clock; dimensions must be even. |
| `layout_template_id` | Existing content-ops layout template, default `monochrome-editorial`; style tokens enter the digest. |
| `shots` | Ordered distinct `id`, `kind`, frame-aligned `seconds`, `title`, optional `body`, `source_ref`, explicit `boundary`. |
| `assets` | Distinct id, relative `path`, exact `sha256`, `image`/`video`/`audio`, `source_ref` and `local_private`/`public_safe` source classification. |
| `captions` | Ordered nonoverlapping `start`, `end`, `text`, `language` cues inside the composition. One sequential caption track is emitted. |
| `narration` | Explicit `silent`, `supplied` with audio `asset_id`, or `system_speech` with installed `voice` and optional words-per-minute. |

Caption text is plain text. Single line breaks are supported; an internal
blank line is refused before preparation because it terminates a subtitle
cue. Use single line breaks or separate timed cues instead. Angle brackets
and entity syntax (such as `&lt;` or `&#60;`) are also refused: literal markup
and entity preservation is not qualified for this SubRip export. Write spoken plain text instead. The
renderer repeats these format checks, escapes ordinary ampersands in VTT,
and preserves plain text in SRT and the transcript. This bounded subset is
qualified with the native browser track and real FFmpeg subtitle decoding.

Shots are `title`, `diagram` (two to five `nodes`), `excerpt` (image/video
`asset_id` and optional `start_seconds`) or `blender` (declarative `scene`
geometry). These are composition-local rendering choices. They do not extend
Goal/Todo state. Likewise prepared/rendering/ready/failed/cancelled/interrupted
describe private render attempts, never published content or Agent liveness. An
old saved running attempt is shown as interrupted after its bounded execution
window; a read does not restart it.

Preparation takes an explicit local source directory. Absolute paths,
traversal, symlinks and wrong source digests are refused. The prepared record
contains immutable private source copies; editing the original afterward does
not change an admitted composition. No URL is fetched. A `source_ref` records
provenance supplied by the caller; a `public_safe` label does not prove rights,
truth, current product behavior or public publication permission.

The canonical digest binds story, sources, source boundaries, layout tokens,
geometry, timing, captions and narration. Canonical plans can be revalidated
without changing that digest. A changed plan requires the expected revision
and invalidates old content approval. Existing layout tokens are reused;
static page-density rules do not certify a timed movie or its learning effect.

`body` is supported for title and diagram shots. Excerpt and Blender layouts
show a title and source boundary, and reject nonempty body text at admission
and rendering. A qualifier must be retained in a supported visible field,
separate title scene or timed caption; it must not silently disappear. Existing
prepared spatial plans with nonempty body now fail explicitly and need a new
revision that preserves that meaning in a supported field.

## Execution and readback

```sh
loopx content-ops media prepare --goal-id example-goal \
  --plan-json examples/content-ops-media-brief.json --source-directory . \
  --format json
loopx content-ops media render --goal-id example-goal \
  --composition-id COMPOSITION_FROM_PREPARE --expected-revision 1 --format json
loopx content-ops media inspect --goal-id example-goal \
  --composition-id COMPOSITION_FROM_PREPARE --format json
```

`list` discovers the latest 100 private compositions; `cancel` requires the
current composition and revision. An already running render is returned without
a second effect. Cancel is a request until the worker settles. After a failed,
cancelled, interrupted or damaged attempt, explicit render can retry. Intact
completed bytes are reused. A changed story uses `prepare --composition-id …
--expected-revision …` first. The render lock spans the actual effect, in
addition to revision-bound record writes.

The existing extension lifecycle owns installation, enablement, doctor,
entrypoint identity and the `content_media_write` permission. Loading the page
or preparing a plan never installs a provider. Disabled/unavailable extensions
block new effects while preserving prepared sources and verified downloads.
See [installation, dependency and disable instructions](../../../packages/loopx-media/README.md).

The private `content_ops_media_renderer_v0` envelope carries the validated plan,
layout tokens, digest, frame count, immutable snapshots, exclusive attempt
directory and attempt-scoped cancel flag. Only a verified installed extension
receives those paths. The result projection accepts fixed output names and
exact SHA256/byte counts; paths and undeclared provider fields are discarded.
The core reads every actual file before committing `ready`. Required outputs
are `video.mp4`, `poster.png`, `captions.vtt`, `captions.srt` and `transcript.txt`,
plus `narration.wav` for audible modes. Full decode must match the admitted
timeline, geometry and narration mode. Audio checks report peak and clipped
PCM samples; subjective listening remains untested.

Both plan and output bytes bind the existing `content_ops_item_v0`. Producing
or re-encoding a movie revises its content digest and clears any approval and
delivery intent. This renderer neither approves nor posts. Publication and
its account/channel/timing/readback remain with the
[existing item lifecycle](content-ops-item-lifecycle-v0.md).

## HTTP boundary and failure behavior

The loopback Chat server exposes `POST /api/chat/content-media` for list,
inspect, render and cancel. Render/cancel use the current revision; the server
binds the registered Goal/source route and rejects a different selected Goal,
foreign origin or filesystem fields. Rendering runs in a bounded background
worker so the page remains responsive. Polling occurs only while a render is
pending and stops after a terminal readback.

`GET /api/chat/content-media/file` serves only fixed verified files from that
composition, with byte ranges for playback, no-store and same-origin resource
policy. It refuses escaping filenames, non-ready and damaged artifacts; it
does not serve the private manifest or source files. Browser error projections
do not include provider stderr or private paths.

Missing provider, changed source, stale revision, text/glyph overflow, short
footage, invalid narration timing, cancellation, stopped host and damaged bytes
remain distinguishable from success. Repair the source/brief as a new revision
or repair the existing extension and retry. No failure creates publication
authority, fills missing footage, infers a creative pass or changes a Goal.

Mechanical rendering, creative quality, audience understanding and operations
impact have separate evidence. Future generated media and interactive
learning providers should reuse the nearest content owner and comparison
method; they are not silently activated by this protocol.

## Blender shot and project readback

The optional `loopx-media` provider can compute a `blender` shot inside the same
composition. `scene` is a bounded declarative object: an orthographic camera
with start/end position and target, box/sphere objects with material values
and optional position keyframes, area lights and connections between object
IDs. The shared `content_media` TypeScript owner validates it; provider Python
does not choose the work, sources, publication state or execution authority.
See the runnable [synthetic example](../../../packages/loopx-media/examples/blender-handoff.json)
and [activation/recovery guide](../../../packages/loopx-media/README.md#optional-blender-scenes).

Scene IDs and geometry are bound to the plan digest. Position keys must start
at frame 1, end at the scene's final frame and increase strictly; the first
position must match the object's declared initial position. A scene supports
at most 16 primitives, 3 lights, 24 connections and 120 frames. At most 3 Blender
scenes fit inside a composition. Existing dimension/timeline/output/process
bounds apply unchanged. Arbitrary scripts, uploaded blend files and external
asset references are rejected. Ordinary scene-free plans retain their existing
normalized structure and digest.

Blender 4.5 LTS/Cycles/CPU produces actual RGBA and depth PNG sequences; depth is
16-bit Z distance normalized over 0–50, with farther values clamped. A fresh
process opens the saved blend with scripts disabled and checks its geometry,
animation, camera and timeline. Ready results additionally require the exact
admitted scene IDs/frame counts, both complete passes, reopen checks and the
fixed `blender-project.zip` artifact. The archive contains relative-path blend
projects, exact scene inputs, the replay builder and frames. It is subject to
the same digest/readback/download scope as the movie; it cannot be attached
to a scene-free result to bypass admission.

The existing workbench renders/cancels/retries the composition and exposes the
verified project download. Installation of the Blender extra is explicit;
missing bpy does not disable ordinary 2D work. A failed 3D attempt retains its
prepared input and supports retry after dependency repair. No fallback replaces
3D with a code projection. Mechanical readiness still does not establish
creative quality, audience understanding or publication approval.
