---
name: ffmpeg-video-filters
version: 1.3.1
description: "Apply FFmpeg video filters - scale/resize with aspect-ratio preservation, crop, watermark/logo overlay, speed changes with synced audio retiming (setpts + atempo chains), full-frame and region blur for face/PII anonymisation, eq color correction, rotation, fades, -vf vs -filter_complex graphs. Use when changing what the pixels look like: resizing for a platform, branding, time-lapse/slow motion, exposure fixes. Not for cutting or joining clips (use ffmpeg-video-editing), codec or container changes (use ffmpeg-format-conversion), audio-only work (use ffmpeg-audio-processing), inspecting streams (use ffmpeg-media-info), or extracting frames as images (use ffmpeg-keyframe-extraction)."
risk: safe
source: openrouter-deepsearch
date_added: 2026-06-16
---

## When to Use

Reach for these filters when you need to change *what the pixels look like* rather than just remux or re-encode:

- **Resizing** so a clip fits a target platform (a 4K master is wasteful for a 720p web player, and over-large frames inflate file size and decode cost).
- **Cropping** to remove letterboxing, focus on a subject, or change aspect ratio for a vertical/social cut.
- **Watermarks and overlays** for branding or attribution — done in one pass so you never ship an un-watermarked file by accident.
- **Speed changes** for time-lapse or slow-motion, where the *why* is usually pacing: the catch is that video and audio must be retimed together or they drift out of sync.
- **Blur** to anonymise faces, hide PII (license plates, screens, documents), or create a soft background. Anonymisation is the case where getting the region right actually matters legally, so it gets a dedicated, bounds-checked helper below.
- **Color adjustment** (brightness, contrast, saturation, gamma) to correct exposure or hit a house look.

### When not to use

Filtering re-encodes the video. If the task doesn't change how frames *look*, a sibling skill does it better (often losslessly):

| If the task is... | Use instead |
| --- | --- |
| Cutting, trimming, or concatenating clips | `ffmpeg-video-editing` |
| Changing container/codec, shrinking files, compatibility fixes | `ffmpeg-format-conversion` |
| Extracting audio, loudness normalisation, mixing, channel work | `ffmpeg-audio-processing` |
| Inspecting resolution/codec/duration without modifying the file | `ffmpeg-media-info` |
| Pulling keyframes or thumbnails out as still images | `ffmpeg-keyframe-extraction` |

## Prerequisites

- `ffmpeg` and `ffprobe` must be on `PATH`. Verify with `ffmpeg -version` and `ffprobe -version`.
- Node.js 18+ for the TypeScript programmatic examples.
- Windows host is primary (PowerShell). The provided TypeScript spawner uses `windowsHide: true` to prevent console window popups on Windows.

## Procedure

### Core concepts

- **`-vf` vs `-filter_complex`.** `-vf` is shorthand for a linear, single-stream filter chain (filters separated by commas). `-filter_complex` is the full graph syntax: it can take multiple inputs, split and merge streams, and label intermediate pads with `[name]`. Use `-vf` for "do these things in order to one video," and `-filter_complex` the instant a second input or a branch appears.
- **Overlay coordinate variables.** Inside `overlay`, `W`/`H` are the *main* (background) width/height and `w`/`h` are the *overlay* width/height. That is why bottom-right is `W-w-margin : H-h-margin` — you offset by the overlay's own size so it never clips off the edge.
- **Why build commands as argument arrays, not shell strings.** Every helper below spawns FFmpeg with an explicit `string[]` of arguments rather than concatenating into one shell string. This avoids shell-injection and quoting bugs entirely: a filename with a space, a quote, or a `;` is passed as one argument and can never be reinterpreted as a command.
- **Probe before you trust input.** `ffprobe` reports the real resolution, codec, and duration. The helpers use it to reject crops/blurs that fall outside the frame *before* launching a long encode that would otherwise fail halfway through.

### Programmatic foundation (TypeScript)

The examples are written as small, strictly-typed functions in TypeScript (Node 18+). They share the foundation below: typed results, two error classes (one for bad input caught before launch, one for a failed process), a safe spawner, reusable validators, and two `ffprobe` helpers. No value is typed `any`; external JSON is narrowed through a type guard before use.

```typescript
import { spawn } from "node:child_process";
import { access } from "node:fs/promises";
import { constants } from "node:fs";

/** Captured output of a finished FFmpeg/FFprobe process. */
interface CommandResult {
  readonly stdout: string;
  readonly stderr: string;
  readonly exitCode: number;
}

/** Thrown for bad arguments caught *before* a process is launched. */
class FilterValidationError extends Error {
  constructor(message: string) {
    super(message);
    this.name = "FilterValidationError";
  }
}

/** Thrown when a launched FFmpeg/FFprobe process fails or cannot start. */
class FFmpegProcessError extends Error {
  readonly exitCode: number;
  readonly stderr: string;
  constructor(message: string, exitCode: number, stderr: string) {
    super(message);
    this.name = "FFmpegProcessError";
    this.exitCode = exitCode;
    this.stderr = stderr;
  }
}

/**
 * Spawn a command with an explicit argument array (never a shell string) and
 * resolve with its captured output, rejecting on launch failure or non-zero exit.
 */
function runCommand(
  command: "ffmpeg" | "ffprobe",
  args: readonly string[],
): Promise<CommandResult> {
  return new Promise<CommandResult>((resolve, reject) => {
    const child = spawn(command, args, { windowsHide: true });
    let stdout = "";
    let stderr = "";

    child.stdout?.on("data", (chunk: Buffer) => {
      stdout += chunk.toString("utf8");
    });
    child.stderr?.on("data", (chunk: Buffer) => {
      stderr += chunk.toString("utf8");
    });

    child.on("error", (err: Error) => {
      reject(new FFmpegProcessError(`Failed to launch ${command}: ${err.message}`, -1, stderr));
    });

    child.on("close", (code: number | null) => {
      const exitCode = code ?? -1;
      if (exitCode !== 0) {
        reject(new FFmpegProcessError(`${command} exited with code ${exitCode}`, exitCode, stderr));
        return;
      }
      resolve({ stdout, stderr, exitCode });
    });
  });
}

/** ffmpeg with non-interactive, quiet-banner defaults so it never blocks on a prompt. */
function runFfmpeg(args: readonly string[]): Promise<CommandResult> {
  return runCommand("ffmpeg", ["-nostdin", "-hide_banner", ...args]);
}

/** ffprobe with a quiet banner. */
function runFfprobe(args: readonly string[]): Promise<CommandResult> {
  return runCommand("ffprobe", ["-hide_banner", ...args]);
}

/** Reject empty paths and files that do not exist or are not readable. */
async function assertReadableFile(path: string): Promise<void> {
  if (path.trim().length === 0) {
    throw new FilterValidationError("Path must be a non-empty string.");
  }
  try {
    await access(path, constants.R_OK);
  } catch {
    throw new FilterValidationError(`File is missing or unreadable: ${path}`);
  }
}

/**
 * Dimensions must be positive even integers for yuv420p encoders (H.264/H.265),
 * or -2 to let FFmpeg derive that axis from the other while keeping the ratio.
 */
function assertEvenOrAuto(value: number, label: string): void {
  if (value === -2) return;
  if (!Number.isInteger(value) || value <= 0) {
    throw new FilterValidationError(`${label} must be a positive integer or -2 (auto), received ${value}.`);
  }
  if (value % 2 !== 0) {
    throw new FilterValidationError(`${label} must be even for yuv420p encoders, received ${value}.`);
  }
}

/** Bound a numeric option to an inclusive range, rejecting NaN/Infinity. */
function assertInRange(value: number, min: number, max: number, label: string): void {
  if (!Number.isFinite(value) || value < min || value > max) {
    throw new FilterValidationError(`${label} must be between ${min} and ${max}, received ${value}.`);
  }
}

/** Pixel dimensions of a video stream, read via ffprobe. */
interface VideoDimensions {
  readonly width: number;
  readonly height: number;
}

/** Read the first video stream's pixel dimensions. */
async function probeDimensions(input: string): Promise<VideoDimensions> {
  await assertReadableFile(input);
  const result = await runFfprobe([
    "-v", "error",
    "-select_streams", "v:0",
    "-show_entries", "stream=width,height",
    "-of", "csv=p=0:s=x",
    input,
  ]);
  const raw = result.stdout.trim();
  const match = /^(\d+)x(\d+)$/.exec(raw);
  if (match === null) {
    throw new FFmpegProcessError(`Could not parse dimensions from ffprobe output: "${raw}"`, result.exitCode, result.stderr);
  }
  return { width: Number.parseInt(match[1], 10), height: Number.parseInt(match[2], 10) };
}

/** True when the input has at least one audio stream. */
async function hasAudioStream(input: string): Promise<boolean> {
  await assertReadableFile(input);
  const result = await runFfprobe([
    "-v", "error",
    "-select_streams", "a",
    "-show_entries", "stream=index",
    "-of", "csv=p=0",
    input,
  ]);
  return result.stdout.trim().length > 0;
}
```

## Examples

### Scaling

`scale` resizes the frame. The `flags` choose the resampling algorithm, which is a quality vs. speed trade-off: `lanczos` is sharp but slower (good for downscaling masters), `bilinear` is fast but softer (good for quick previews). Passing `-2` for one axis tells FFmpeg to compute it from the other while preserving the aspect ratio *and* keeping the result even, which yuv420p encoders require.

```bash
# Scale to 720p tall, width auto-derived and kept even, high-quality resampling
ffmpeg -nostdin -i input.mp4 -vf "scale=-2:720:flags=lanczos" -y output.mp4

# Scale to 1280 wide, height auto-derived, fast resampling for a preview
ffmpeg -nostdin -i input.mp4 -vf "scale=1280:-2:flags=bilinear" -y output.mp4

# Exact 1920x1080 WITHOUT distortion: fit inside the box, then pad the remainder
ffmpeg -nostdin -i input.mp4 -vf "scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2:black" -y output.mp4
```

```typescript
type ScaleFlag = "lanczos" | "bilinear" | "bicubic" | "neighbor" | "spline";

interface ScaleOptions {
  readonly width: number;   // pixels, or -2 to derive from height
  readonly height: number;  // pixels, or -2 to derive from width
  readonly flags: ScaleFlag;
}

/** Build a validated `scale=...` filter string. */
function buildScaleFilter(options: ScaleOptions): string {
  assertEvenOrAuto(options.width, "width");
  assertEvenOrAuto(options.height, "height");
  if (options.width === -2 && options.height === -2) {
    throw new FilterValidationError("width and height cannot both be -2; at least one must be a fixed size.");
  }
  return `scale=${options.width}:${options.height}:flags=${options.flags}`;
}

/** Resize while preserving the aspect ratio (use -2 on the derived axis). */
async function scaleVideo(input: string, output: string, options: ScaleOptions): Promise<CommandResult> {
  await assertReadableFile(input);
  const filter = buildScaleFilter(options);
  return runFfmpeg(["-i", input, "-vf", filter, "-y", output]);
}

interface FitOptions {
  readonly width: number;
  readonly height: number;
  readonly padColor: string; // e.g. "black" or "#000000"
}

/**
 * Produce an output that is exactly width x height with NO stretching, by scaling to fit
 * and padding the leftover space. This is the correct way to hit fixed dimensions.
 */
function buildFitFilter(options: FitOptions): string {
  assertEvenOrAuto(options.width, "width");
  assertEvenOrAuto(options.height, "height");
  if (options.width === -2 || options.height === -2) {
    throw new FilterValidationError("fit requires fixed width and height; -2 is not allowed when padding to an exact size.");
  }
  if (!/^[#0-9a-zA-Z]+$/.test(options.padColor)) {
    throw new FilterValidationError(`padColor must be a simple color name or hex value, received "${options.padColor}".`);
  }
  return (
    `scale=${options.width}:${options.height}:force_original_aspect_ratio=decrease,` +
    `pad=${options.width}:${options.height}:(ow-iw)/2:(oh-ih)/2:${options.padColor}`
  );
}

/** Resize to exact dimensions by fitting then padding (never distorts). */
async function fitVideo(input: string, output: string, options: FitOptions): Promise<CommandResult> {
  await assertReadableFile(input);
  const filter = buildFitFilter(options);
  return runFfmpeg(["-i", input, "-vf", filter, "-y", output]);
}
```

### Cropping

`crop=w:h:x:y` keeps a `w`×`h` rectangle whose top-left corner sits at `(x, y)`. The common failure is asking for a rectangle that runs off the edge of the frame — FFmpeg only discovers this once decoding starts and aborts mid-encode. The helper probes the real dimensions first and rejects an out-of-bounds crop up front, turning a wasted long run into an instant, clear error.

```bash
# Crop a 1920x1080 window from the top-left corner
ffmpeg -nostdin -i input.mp4 -vf "crop=1920:1080:0:0" -y output.mp4

# Crop an 800x600 window starting at x=100, y=50
ffmpeg -nostdin -i input.mp4 -vf "crop=800:600:100:50" -y output.mp4

# Crop centred: in/out width/height expressions compute the offset for you
ffmpeg -nostdin -i input.mp4 -vf "crop=1280:720:(in_w-1280)/2:(in_h-720)/2" -y output.mp4
```

```typescript
interface CropOptions {
  readonly width: number;
  readonly height: number;
  readonly x: number; // left offset, >= 0
  readonly y: number; // top offset, >= 0
}

/** Build a validated `crop=w:h:x:y` filter string (shape/sign only; bounds checked separately). */
function buildCropFilter(options: CropOptions): string {
  for (const [label, value] of [["width", options.width], ["height", options.height]] as const) {
    if (!Number.isInteger(value) || value <= 0) {
      throw new FilterValidationError(`crop ${label} must be a positive integer, received ${value}.`);
    }
  }
  for (const [label, value] of [["x", options.x], ["y", options.y]] as const) {
    if (!Number.isInteger(value) || value < 0) {
      throw new FilterValidationError(`crop ${label} offset must be a non-negative integer, received ${value}.`);
    }
  }
  return `crop=${options.width}:${options.height}:${options.x}:${options.y}`;
}

/** Crop after confirming the rectangle fits inside the source frame. */
async function cropVideo(input: string, output: string, options: CropOptions): Promise<CommandResult> {
  await assertReadableFile(input);
  const filter = buildCropFilter(options); // validates integers/signs first
  const dims = await probeDimensions(input);
  if (options.x + options.width > dims.width || options.y + options.height > dims.height) {
    throw new FilterValidationError(
      `Crop ${options.width}x${options.height}+${options.x}+${options.y} exceeds source ${dims.width}x${dims.height}.`,
    );
  }
  return runFfmpeg(["-i", input, "-vf", filter, "-y", output]);
}
```

### Watermarks and overlays

Compositing a logo onto a video needs two inputs, so this is `-filter_complex` territory. The position expressions use the overlay-coordinate variables from *Core concepts*: offset by `w`/`h` (the overlay's own size) so a bottom/right placement never clips off-screen. The `format` option controls the pixel format of the composite; `yuv420` is the safe, widely-compatible default. The helper maps a friendly position name to the correct expression so callers can't typo a coordinate formula.

```bash
# Top-left, 10px margin
ffmpeg -nostdin -i input.mp4 -i logo.png -filter_complex "overlay=10:10:format=yuv420" -y output.mp4

# Bottom-right, 10px margin (offset by overlay size so it stays on screen)
ffmpeg -nostdin -i input.mp4 -i logo.png -filter_complex "overlay=W-w-10:H-h-10:format=yuv420" -y output.mp4

# Centred
ffmpeg -nostdin -i input.mp4 -i logo.png -filter_complex "overlay=(W-w)/2:(H-h)/2:format=yuv420" -y output.mp4
```

```typescript
type OverlayPosition = "top-left" | "top-right" | "bottom-left" | "bottom-right" | "center";
type OverlayPixelFormat = "yuv420" | "yuv422" | "yuv444" | "rgb" | "auto";

interface OverlayOptions {
  readonly position: OverlayPosition;
  readonly marginX: number; // horizontal margin in px (ignored for "center")
  readonly marginY: number; // vertical margin in px (ignored for "center")
  readonly pixelFormat: OverlayPixelFormat;
}

/** Maps each named position to its overlay coordinate expression. */
const OVERLAY_EXPRESSIONS: Readonly<Record<OverlayPosition, (marginX: number, marginY: number) => string>> = {
  "top-left": (marginX, marginY) => `${marginX}:${marginY}`,
  "top-right": (marginX, marginY) => `W-w-${marginX}:${marginY}`,
  "bottom-left": (marginX, marginY) => `${marginX}:H-h-${marginY}`,
  "bottom-right": (marginX, marginY) => `W-w-${marginX}:H-h-${marginY}`,
  "center": () => "(W-w)/2:(H-h)/2",
};

/** Build a validated `overlay=...` filter string. */
function buildOverlayFilter(options: OverlayOptions): string {
  const expr = OVERLAY_EXPRESSIONS[options.position](options.marginX, options.marginY);
  return `overlay=${expr}:format=${options.pixelFormat}`;
}

/** Composite a watermark image over the main video. */
async function applyWatermark(input: string, watermark: string, output: string, options: OverlayOptions): Promise<CommandResult> {
  await assertReadableFile(input);
  await assertReadableFile(watermark);
  const overlayExpr = buildOverlayFilter(options);
  const filterComplex = `[0:v][1:v]${overlayExpr}`;
  return runFfmpeg(["-i", input, "-i", watermark, "-filter_complex", filterComplex, "-y", output]);
}
```

### Fade effects

`fade=t=in|out:st=START:d=DURATION` fades from/to black over `DURATION` seconds starting at `st`. The thing to get right is that a fade-out's `st` is an *absolute* timestamp, so it depends on the clip length — to fade out the last 2 seconds of a 10-second clip you set `st=8`. Because that ties the value to the real duration, the helper can validate the numbers but you still supply `st` relative to the actual length (probe it with `ffprobe` if you don't know it).

```bash
# Fade in over the first 2 seconds
ffmpeg -nostdin -i input.mp4 -vf "fade=t=in:st=0:d=2" -y output.mp4

# Fade out the last 2 seconds of a 10s clip (10 - 2 = 8)
ffmpeg -nostdin -i input.mp4 -vf "fade=t=out:st=8:d=2" -y output.mp4

# Fade in AND out
ffmpeg -nostdin -i input.mp4 -vf "fade=t=in:st=0:d=2,fade=t=out:st=8:d=2" -y output.mp4
```

```typescript
type FadeType = "in" | "out";

interface FadeOptions {
  readonly type: FadeType;
  readonly start: number;    // absolute start time in seconds, >= 0
  readonly duration: number; // fade length in seconds, > 0
}

/** Build a validated `fade=...` filter string. */
function buildFadeFilter(options: FadeOptions): string {
  if (!Number.isFinite(options.start) || options.start < 0) {
    throw new FilterValidationError(`fade start must be a non-negative number, received ${options.start}.`);
  }
  if (!Number.isFinite(options.duration) || options.duration <= 0) {
    throw new FilterValidationError(`fade duration must be a positive number, received ${options.duration}.`);
  }
  return `fade=t=${options.type}:st=${options.start}:d=${options.duration}`;
}

/** Apply one or more fade segments in order. */
async function applyFade(input: string, output: string, fades: readonly FadeOptions[]): Promise<CommandResult> {
  await assertReadableFile(input);
  if (fades.length === 0) {
    throw new FilterValidationError("At least one fade segment is required.");
  }
  const chain = fades.map(buildFadeFilter).join(",");
  return runFfmpeg(["-i", input, "-vf", chain, "-y", output]);
}
```

### Combining Filters

```typescript
function chainFilters(filters: readonly string[]): string {
  return filters.join(",");
}

async function applyFilterChain(input: string, output: string, filters: readonly string[]): Promise<CommandResult> {
  await assertReadableFile(input);
  const chain = chainFilters(filters);
  return runFfmpeg(["-i", input, "-vf", chain, "-y", output]);
}

interface ScaleThenWatermarkOptions {
  readonly scale: ScaleOptions;
  readonly overlay: OverlayOptions;
}

/** Two-input graph: scale the main video, then composite a watermark over the result. */
async function scaleThenWatermark(
  input: string,
  watermark: string,
  output: string,
  options: ScaleThenWatermarkOptions,
): Promise<CommandResult> {
  await assertReadableFile(input);
  await assertReadableFile(watermark);
  const scaleExpr = buildScaleFilter(options.scale);
  const overlayExpr = buildOverlayFilter(options.overlay);
  const filterComplex = `[0:v]${scaleExpr}[scaled];[scaled][1:v]${overlayExpr}`;
  return runFfmpeg(["-i", input, "-i", watermark, "-filter_complex", filterComplex, "-y", output]);
}
```

## Pitfalls

These are the mistakes that produce broken or unprofessional output, with the reasoning so you can judge your own edge cases instead of memorising rules:

- **Don't use a plain `-vf` chain when you have more than one input stream.** `-vf` applies to a single stream; the moment you add a second input (a logo, a second video), you need `-filter_complex` so you can name pads (`[0:v]`, `[1:v]`) and wire them together. Using `-vf` here fails outright or silently ignores the second input.
- **Don't `scale` to a fixed `W:H` unless you genuinely want distortion.** Forcing `1920:1080` onto a 4:3 source stretches faces. Preserve the ratio with `-2` for one axis, or scale-then-pad to hit exact dimensions without stretching (shown under *Scaling*).
- **Don't change video speed without retiming audio.** `setpts` only moves video timestamps; if you skip `atempo`, the audio plays at the original length and drifts. A single `atempo` instance only covers a `0.5–100.0` multiplier, so extreme speed changes must be expressed as a *chain* of `atempo` filters whose product equals the target — the helper below does this for you.
- **Don't over-blur.** Large `boxblur`/`gblur` values destroy detail; for anonymisation that is the point, but for a "soft background" it looks like a rendering bug. Pick the smallest radius that achieves the goal.
- **Mind filter order — it changes both the result and the cost.** Putting a size-reducing filter (`scale` down, `crop`) *first* means every later filter processes fewer pixels and runs faster; putting it last wastes work. Order also changes semantics: cropping then scaling is not the same image as scaling then cropping.
- **Keep `-pix_fmt yuv420p` in mind for compatibility.** Some filters can emit pixel formats that browsers and phones refuse to decode. When in doubt, add `-pix_fmt yuv420p` to the output so the file plays everywhere.

## Verification

Don't trust that a filter did what you intended — confirm it. `ffprobe` reports the actual resolution, codec, and duration of the *output*, which is how you catch a silent aspect-ratio distortion, a crop that landed in the wrong place, or audio/video drift after a speed change. The helper below parses `ffprobe`'s JSON safely: it narrows the parsed `unknown` through a type guard and throws a clear error if any expected field is missing, so a malformed probe can never masquerade as a valid report.

```typescript
/** A concise, validated summary of an output file. */
interface OutputReport {
  readonly width: number;
  readonly height: number;
  readonly durationSeconds: number;
  readonly videoCodec: string;
}

interface FfprobeStream {
  readonly width: number;
  readonly height: number;
  readonly codec_name: string;
}

interface FfprobeFormat {
  readonly duration: string;
}

interface FfprobeJson {
  readonly streams: readonly FfprobeStream[];
  readonly format: FfprobeFormat;
}

/** Narrow ffprobe's parsed JSON to the exact shape we read, without using `any`. */
function isFfprobeJson(value: unknown): value is FfprobeJson {
  if (typeof value !== "object" || value === null) return false;
  const record = value as Record<string, unknown>;

  if (!Array.isArray(record.streams) || record.streams.length === 0) return false;
  const stream = record.streams[0] as Record<string, unknown>;
  if (
    typeof stream.width !== "number" ||
    typeof stream.height !== "number" ||
    typeof stream.codec_name !== "string"
  ) {
    return false;
  }

  if (typeof record.format !== "object" || record.format === null) return false;
  const format = record.format as Record<string, unknown>;
  return typeof format.duration === "string";
}

/** Probe an output file and return a validated report (throws on missing/garbled fields). */
async function verifyOutput(output: string): Promise<OutputReport> {
  await assertReadableFile(output);
  const result = await runFfprobe([
    "-v", "error",
    "-select_streams", "v:0",
    "-show_entries", "stream=width,height,codec_name:format=duration",
    "-of", "json",
    output,
  ]);

  let parsed: unknown;
  try {
    parsed = JSON.parse(result.stdout) as unknown;
  } catch {
    throw new FFmpegProcessError(`ffprobe returned non-JSON output: ${result.stdout}`, result.exitCode, result.stderr);
  }
  if (!isFfprobeJson(parsed)) {
    throw new FFmpegProcessError(`ffprobe JSON missing expected fields: ${result.stdout}`, result.exitCode, result.stderr);
  }

  const stream = parsed.streams[0];
  const durationSeconds = Number.parseFloat(parsed.format.duration);
  if (Number.isNaN(durationSeconds)) {
    throw new FFmpegProcessError(`ffprobe duration is not numeric: ${parsed.format.duration}`, result.exitCode, result.stderr);
  }

  return {
    width: stream.width,
    height: stream.height,
    durationSeconds,
    videoCodec: stream.codec_name,
  };
}
```

Manual checklist before you ship the output:

- [ ] Output dimensions match the `scale`/`crop`/`fit` you asked for (`verifyOutput` or `ffprobe -show_entries stream=width,height`).
- [ ] Audio and video stay in sync after `setpts`+`atempo` — scrub a speed-changed clip end to end, since drift is most visible at the tail.
- [ ] Watermark sits at the expected corner with the right margin (open it in a player).
- [ ] Final resolution, duration, and codec are as expected (`verifyOutput`).
- [ ] The file plays on a target device/browser; if not, re-export with `-pix_fmt yuv420p`.
- [ ] For anonymisation blurs, confirm the blurred region fully covers the subject across the whole clip, not just the first frame.

## Related skills

- **`ffmpeg-audio-processing`** — audio streams in depth (the natural companion when a speed change needs more than `atempo`).
- **`ffmpeg-format-conversion`** — choosing codecs, bitrate, and quality for the re-encode every filter forces.
- **`ffmpeg-video-editing`** — cutting and joining the clip before or after filtering.
- **`ffmpeg-media-info`** — probing inputs and verifying outputs beyond `verifyOutput`.
- **`ffmpeg-keyframe-extraction`** — exporting still frames instead of filtered video.
