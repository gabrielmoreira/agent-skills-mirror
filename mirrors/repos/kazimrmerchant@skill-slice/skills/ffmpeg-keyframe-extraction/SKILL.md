---
name: ffmpeg-keyframe-extraction
version: 1.2.1
description: "Extract keyframes (I-frames) from video as still images with FFmpeg using select filter or -skip_frame nokey, with PTS-stamped filenames and ffprobe keyframe counting. Use when pulling thumbnails, scene-representative frames, or ML sampling frames out of MP4/MKV/AVI/WebM. Not for cutting or joining clips, scaling/watermarks/effects, codec or container changes, audio work, or reading stream metadata."
risk: safe
source: openrouter-deepsearch
date_added: 2026-06-16
---

# FFmpeg Keyframe Extraction

Isolate a video's I-frames and write them out as still images — the fast path to thumbnails, scene-representative previews, and cheap frame sampling for analysis or ML.

## When to Use

Reach for this skill when you need the **I-frames** (intra-coded, "key" frames) of a video rather than every frame. An I-frame is a fully self-contained picture: unlike P- and B-frames, it does not depend on neighbouring frames to be decoded. That property makes keyframes the right unit of work for:

- **Thumbnails and previews** — each I-frame is a clean, complete image you can show directly.
- **Scene / shot detection** — encoders tend to place an I-frame at scene cuts, so the keyframe set is a cheap first approximation of "interesting moments."
- **Sampling for analysis or ML** — a 30-minute clip might hold 50,000 frames but only a few hundred I-frames, so working on keyframes cuts cost and storage by orders of magnitude while keeping visually distinct content.

### When NOT to use

- **You need *every* frame, or a fixed sampling rate.** Keyframe spacing is decided by the encoder, not by you, so it is irregular (anywhere from one every few frames to one every few seconds). If you need uniform timing, extract by frame rate instead (`-vf fps=1` for one frame per second).
- **You require exact source timestamps but want the `-skip_frame nokey` fast path.** The skip-frame fast path lets the decoder discard non-keyframes early, which is fast but gives coarser PTS information. When precise PTS preservation matters, use the `select` filter method, which decodes the full stream and reports accurate timestamps.
- **The input is untrusted and you build the command by string concatenation.** A filename like `"; rm -rf ~"` is harmless as a literal argument but dangerous if a shell re-parses it. Always pass paths as separate, quoted arguments (shell) or as argv array elements (no `shell: true`).
- **The content is DRM-protected / encrypted.** FFmpeg will refuse to decode protected streams — this is a hard stop, not something to work around.

### Route to sibling skills instead

| If the task is… | Use instead |
| --------------- | ----------- |
| Cutting, trimming, or concatenating video segments | `ffmpeg-video-editing` |
| Scaling, cropping, watermarking, speed, or visual effects | `ffmpeg-video-filters` |
| Changing container or codec (MKV→MP4, H.264→AV1, …) | `ffmpeg-format-conversion` |
| Extracting, normalizing, or mixing audio | `ffmpeg-audio-processing` |
| Inspecting duration, streams, codecs, or metadata | `ffmpeg-media-info` |

## Prerequisites

- **FFmpeg 7.0 or newer** (the 8.x series is current in 2026) on `PATH`. Verify with `ffmpeg -version`. The examples use `-fps_mode`, which replaced the deprecated `-vsync` flag in the 5.x series and is the supported spelling on 7.x and 8.x.
- **A decodable input file** (MP4, MKV, AVI, MOV, WebM, …). Non-DRM, readable by your user.
- **A writeable output directory.** The snippets create it for you, so a missing directory is not an error — but a read-only parent is.
- **Windows host (PowerShell):** All bash commands below have PowerShell equivalents noted inline. On Windows, use backtick (`` ` ``) for line continuation instead of backslash (`\`), and `Test-Path` / `New-Item -ItemType Directory -Force` instead of `[[ -f ]]` / `mkdir -p`.

## Procedure

### How the two methods differ

| Method | What FFmpeg does | Cost | When it wins |
| ------ | ---------------- | ---- | ------------ |
| `select` filter | Decodes **all** frames, then keeps only those where `pict_type == I`. | Slower (full decode). | You want accurate per-frame timestamps, or you may later add more filters. |
| `-skip_frame nokey` | Tells the **decoder** to discard non-keyframes before fully decoding them. | Faster (skips most work). | Throughput matters more than exact PTS, e.g. bulk thumbnailing. |

**Two critical details:**

1. **`-skip_frame nokey` is a *decoder* option, so it must appear *before* `-i`.** Options that precede `-i` configure how that input is read/decoded. Put it after `-i` and it is interpreted as an output option, where it has no effect and you silently lose the speed-up.
2. **Use `-fps_mode vfr`, not `-vsync vfr`.** Both ask FFmpeg to keep a *variable* frame rate so it does not duplicate frames to hit a constant cadence (which would write many identical images). `-vsync` is deprecated; `-fps_mode` is its modern, supported replacement on 7.x.

We deliberately **omit `setpts=...`** from the still-image recipes. `setpts` renumbers each frame's PTS to a fresh sequence; that is useful when you re-encode selected frames back into a *video* stream, but for still images it would overwrite the very timestamps that `-frame_pts 1` exists to expose.

### Step 1 — Verify FFmpeg is available

```bash
# Bash / Linux / macOS
ffmpeg -version
```

```powershell
# PowerShell (Windows host — primary)
ffmpeg -version
```

Confirm the version line shows **7.0 or higher**. If `ffmpeg` is not found, install it or add it to `PATH` before proceeding.

### Step 2 — Validate the input file

```bash
# Bash
input="sample_clip.mp4"
[[ -f "$input" && -r "$input" ]] || { echo "Input is not a readable file: $input" >&2; exit 2; }
```

```powershell
# PowerShell
$input = "sample_clip.mp4"
if (-not (Test-Path $input -PathType Leaf)) { Write-Error "Input not found: $input"; exit 2 }
```

### Step 3 — Create the output directory

```bash
# Bash
mkdir -p ./keyframes
```

```powershell
# PowerShell
New-Item -ItemType Directory -Force -Path .\keyframes | Out-Null
```

### Step 4 — Extract keyframes

#### Method 1 — `select` filter (accurate timestamps, sequential names)

```bash
#!/usr/bin/env bash
set -euo pipefail

input="sample_clip.mp4"
output_dir="./keyframes"

command -v ffmpeg >/dev/null 2>&1 || { echo "ffmpeg not found in PATH" >&2; exit 127; }
[[ -f "$input" && -r "$input" ]] || { echo "Input is not a readable file: $input" >&2; exit 2; }
mkdir -p "$output_dir"

ffmpeg -hide_banner -loglevel error \
  -i "$input" \
  -vf "select='eq(pict_type,I)'" \
  -fps_mode vfr \
  "$output_dir/keyframe_%03d.png"

echo "Wrote $(find "$output_dir" -name 'keyframe_*.png' | wc -l) keyframe(s) to $output_dir"
```

```powershell
# PowerShell equivalent
$input  = "sample_clip.mp4"
$outDir = ".\keyframes"
New-Item -ItemType Directory -Force -Path $outDir | Out-Null

ffmpeg -hide_banner -loglevel error `
  -i $input `
  -vf "select='eq(pict_type,I)'" `
  -fps_mode vfr `
  "$outDir\keyframe_%03d.png"

(Get-ChildItem -Path $outDir -Filter "keyframe_*.png").Count
```

#### Method 2 — `-skip_frame nokey` (faster, sequential names)

```bash
#!/usr/bin/env bash
set -euo pipefail

input="sample_clip.mp4"
output_dir="./keyframes"

command -v ffmpeg >/dev/null 2>&1 || { echo "ffmpeg not found in PATH" >&2; exit 127; }
[[ -f "$input" && -r "$input" ]] || { echo "Input is not a readable file: $input" >&2; exit 2; }
mkdir -p "$output_dir"

# -skip_frame nokey sits BEFORE -i because it configures the decoder for this input.
# -q:v 2 selects near-best JPEG quality (the scale is 2 = best ... 31 = worst).
ffmpeg -hide_banner -loglevel error \
  -skip_frame nokey \
  -i "$input" \
  -fps_mode vfr -q:v 2 \
  "$output_dir/keyframe_%03d.jpg"

echo "Wrote $(find "$output_dir" -name 'keyframe_*.jpg' | wc -l) keyframe(s) to $output_dir"
```

```powershell
# PowerShell equivalent
$input  = "sample_clip.mp4"
$outDir = ".\keyframes"
New-Item -ItemType Directory -Force -Path $outDir | Out-Null

ffmpeg -hide_banner -loglevel error `
  -skip_frame nokey `
  -i $input `
  -fps_mode vfr -q:v 2 `
  "$outDir\keyframe_%03d.jpg"

(Get-ChildItem -Path $outDir -Filter "keyframe_*.jpg").Count
```

#### Variant — Encode the source timestamp into each filename

```bash
#!/usr/bin/env bash
set -euo pipefail

input="sample_clip.mp4"
output_dir="./keyframes"

command -v ffmpeg >/dev/null 2>&1 || { echo "ffmpeg not found in PATH" >&2; exit 127; }
[[ -f "$input" && -r "$input" ]] || { echo "Input is not a readable file: $input" >&2; exit 2; }
mkdir -p "$output_dir"

# -frame_pts 1 makes the image2 muxer substitute each frame's PTS into the filename
# pattern. With the select filter (full decode) those PTS values are accurate.
ffmpeg -hide_banner -loglevel error \
  -i "$input" \
  -vf "select='eq(pict_type,I)'" \
  -fps_mode vfr -frame_pts 1 \
  "$output_dir/keyframe_%d.png"
```

### Step 5 — Count and verify I-frames with ffprobe

```bash
# Count the I-frames in the first video stream of the file.
# -of csv=p=0 strips the "frame," prefix, leaving just the picture type per line.
ffprobe -v error -select_streams v:0 -skip_frame nokey \
  -show_entries frame=pict_type -of csv=p=0 "sample_clip.mp4" | grep -c '^I$'
```

```powershell
# PowerShell equivalent
$iframeCount = (ffprobe -v error -select_streams v:0 -skip_frame nokey `
  -show_entries frame=pict_type -of csv=p=0 "sample_clip.mp4" | Select-String '^I$').Count
Write-Host "I-frames found: $iframeCount"
```

Then compare against what you actually extracted:

```bash
# Bash
find ./keyframes -name 'keyframe_*.png' | wc -l
```

```powershell
# PowerShell
(Get-ChildItem -Path .\keyframes -Filter "keyframe_*.png").Count
```

The two numbers should match.

### Key options reference

| Option | Example | Why it matters |
| ------ | ------- | -------------- |
| `-i "sample_clip.mp4"` | input file | Always quote the path so spaces / metacharacters stay literal (injection-safe). |
| `-vf "select='eq(pict_type,I)'"` | I-frame filter | Keeps only frames whose picture type is `I`; the accurate-timestamp method. |
| `-skip_frame nokey` | before `-i` | Decoder-level skip of non-keyframes; the fast method. **Must precede `-i`.** |
| `-fps_mode vfr` | output | Variable frame rate — stops FFmpeg duplicating frames to a constant rate. Replaces `-vsync vfr`. |
| `-q:v 2` | JPEG quality | 2 (best) … 31 (worst). Applies to JPEG/MJPEG output; ignored for PNG/BMP. |
| `-frame_pts 1` | filename PTS | Writes the frame PTS into the numeric field of the output pattern. |
| `-noautorotate` | before `-i` | Disables FFmpeg's default auto-rotation so frames keep the raw stored orientation. |
| `-hide_banner -loglevel error` | global | Quiet output so automation only sees genuine errors. |

> **Orientation note.** FFmpeg auto-rotates by default based on a video's display-matrix metadata, so extracted frames are already upright — you usually need to do nothing. Add `-noautorotate` (before `-i`) only when you specifically want the *un*-rotated, as-stored pixels.

### Output filename patterns

The trailing argument is a `printf`-style pattern interpreted by the image2 muxer:

- `keyframe_%03d.png` → `keyframe_001.png`, `keyframe_002.png`, … (zero-padded sequence).
- `keyframe_%03d.jpg` → JPEG sequence; pair with `-q:v` to tune quality.
- `keyframe_%d.bmp` → unpadded sequence of BMP images.
- `keyframe_%d.png` **with `-frame_pts 1`** → the number is the frame PTS, not a counter, so filenames reflect position in the source.

### Programmatic usage (TypeScript / Node.js)

Load `references/` for the full typed wrapper when integrating into a Node.js service. The wrapper validates options before spawning FFmpeg, runs FFmpeg **without a shell** (so filenames can never inject commands), enforces a timeout, and surfaces failures as specific, typed errors. There are no `any` types anywhere.

```typescript
import { spawn } from "node:child_process";
import { access, mkdir } from "node:fs/promises";
import { constants as FS } from "node:fs";
import { join } from "node:path";
import { performance } from "node:perf_hooks";

/** Which decoding strategy FFmpeg uses to isolate I-frames. */
export type ExtractionMethod = "select-filter" | "skip-frame";

/** Image containers we are willing to emit; restricting this avoids surprising muxer errors. */
export type OutputImageFormat = "png" | "jpg" | "bmp";

export interface KeyframeExtractionOptions {
  /** Path to the source video. Must exist and be readable. */
  readonly inputPath: string;
  /** Directory to receive the images. Created (recursively) if missing. */
  readonly outputDir: string;
  /** Filename stem before the numeric field, e.g. "keyframe". No path separators. */
  readonly filenameStem?: string;
  /** Output image format. Defaults to "png" (lossless). */
  readonly format?: OutputImageFormat;
  /** Decoding strategy. Defaults to "select-filter" for timestamp accuracy. */
  readonly method?: ExtractionMethod;
  /** JPEG quality, 2 (best) … 31 (worst). Ignored for png/bmp. Defaults to 2. */
  readonly jpegQuality?: number;
  /** Substitute the frame PTS into the filename instead of a sequence index. Defaults to false. */
  readonly embedTimestamp?: boolean;
  /** Keep the raw stored orientation (adds -noautorotate). Defaults to false. */
  readonly disableAutoRotate?: boolean;
  /** Executable to run. Defaults to "ffmpeg" (resolved via PATH). */
  readonly ffmpegPath?: string;
  /** Hard wall-clock ceiling in milliseconds. Defaults to 600_000 (10 minutes). */
  readonly timeoutMs?: number;
}

export interface KeyframeExtractionResult {
  readonly outputDir: string;
  readonly outputPattern: string;
  readonly command: readonly string[];
  readonly durationMs: number;
}

/** Thrown when caller-supplied options fail validation, before FFmpeg is ever launched. */
export class InvalidExtractionOptionsError extends Error {
  constructor(message: string) {
    super(message);
    this.name = "InvalidExtractionOptionsError";
  }
}

/** Thrown when FFmpeg cannot be launched, times out, or exits non-zero. */
export class FfmpegExecutionError extends Error {
  readonly exitCode: number | null;
  readonly signal: NodeJS.Signals | null;
  readonly stderr: string;

  constructor(
    message: string,
    exitCode: number | null,
    signal: NodeJS.Signals | null,
    stderr: string,
  ) {
    super(message);
    this.name = "FfmpegExecutionError";
    this.exitCode = exitCode;
    this.signal = signal;
    this.stderr = stderr;
  }
}

interface NormalizedOptions {
  readonly inputPath: string;
  readonly outputDir: string;
  readonly filenameStem: string;
  readonly format: OutputImageFormat;
  readonly method: ExtractionMethod;
  readonly jpegQuality: number;
  readonly embedTimestamp: boolean;
  readonly disableAutoRotate: boolean;
  readonly ffmpegPath: string;
  readonly timeoutMs: number;
}

// A stem with no path separators guarantees output cannot escape outputDir.
const SAFE_STEM = /^[A-Za-z0-9._-]+$/;
const SUPPORTED_FORMATS: ReadonlySet<OutputImageFormat> = new Set(["png", "jpg", "bmp"]);
const SUPPORTED_METHODS: ReadonlySet<ExtractionMethod> = new Set(["select-filter", "skip-frame"]);
const MAX_STDERR_BYTES = 64_000;

async function normalizeOptions(
  options: KeyframeExtractionOptions,
): Promise<NormalizedOptions> {
  if (typeof options.inputPath !== "string" || options.inputPath.trim() === "") {
    throw new InvalidExtractionOptionsError("inputPath must be a non-empty string.");
  }
  if (typeof options.outputDir !== "string" || options.outputDir.trim() === "") {
    throw new InvalidExtractionOptionsError("outputDir must be a non-empty string.");
  }

  const filenameStem = options.filenameStem ?? "keyframe";
  if (!SAFE_STEM.test(filenameStem)) {
    throw new InvalidExtractionOptionsError(
      `filenameStem "${filenameStem}" may only contain letters, digits, dot, underscore and ` +
        "hyphen, so the output cannot escape outputDir.",
    );
  }

  const format = options.format ?? "png";
  if (!SUPPORTED_FORMATS.has(format)) {
    throw new InvalidExtractionOptionsError(
      `Unsupported format "${format}". Use one of: png, jpg, bmp.`,
    );
  }

  const method = options.method ?? "select-filter";
  if (!SUPPORTED_METHODS.has(method)) {
    throw new InvalidExtractionOptionsError(
      `Unknown method "${method}". Use "select-filter" or "skip-frame".`,
    );
  }

  const jpegQuality = options.jpegQuality ?? 2;
  if (!Number.isInteger(jpegQuality) || jpegQuality < 2 || jpegQuality > 31) {
    throw new InvalidExtractionOptionsError(
      "jpegQuality must be an integer between 2 (best) and 31 (worst).",
    );
  }

  const timeoutMs = options.timeoutMs ?? 600_000;
  if (!Number.isInteger(timeoutMs) || timeoutMs <= 0) {
    throw new InvalidExtractionOptionsError(
      "timeoutMs must be a positive integer number of milliseconds.",
    );
  }

  try {
    await access(options.inputPath, FS.R_OK);
  } catch {
    throw new InvalidExtractionOptionsError(
      `Input file is missing or unreadable: ${options.inputPath}`,
    );
  }

  return {
    inputPath: options.inputPath,
    outputDir: options.outputDir,
    filenameStem,
    format,
    method,
    jpegQuality,
    embedTimestamp: options.embedTimestamp ?? false,
    disableAutoRotate: options.disableAutoRotate ?? false,
    ffmpegPath: options.ffmpegPath ?? "ffmpeg",
    timeoutMs,
  };
}

function buildArgs(opts: NormalizedOptions, outputPattern: string): string[] {
  const args: string[] = ["-hide_banner", "-loglevel", "error"];

  // -noautorotate and -skip_frame are decoder options: they only take effect before -i.
  if (opts.disableAutoRotate) {
    args.push("-noautorotate");
  }
  if (opts.method === "skip-frame") {
    args.push("-skip_frame", "nokey");
  }

  args.push("-i", opts.inputPath);

  if (opts.method === "select-filter") {
    args.push("-vf", "select='eq(pict_type,I)'");
  }

  args.push("-fps_mode", "vfr");

  if (opts.embedTimestamp) {
    args.push("-frame_pts", "1");
  }
  if (opts.format === "jpg") {
    args.push("-q:v", String(opts.jpegQuality));
  }

  args.push(outputPattern);
  return args;
}

export async function extractKeyframes(
  options: KeyframeExtractionOptions,
): Promise<KeyframeExtractionResult> {
  const opts = await normalizeOptions(options);
  await mkdir(opts.outputDir, { recursive: true });

  const outputPattern = join(opts.outputDir, `${opts.filenameStem}_%03d.${opts.format}`);
  const args = buildArgs(opts, outputPattern);
  const startedAt = performance.now();

  return await new Promise<KeyframeExtractionResult>((resolvePromise, rejectPromise) => {
    // shell:false (the default for spawn) passes args straight to FFmpeg with no shell parsing,
    // so a hostile filename cannot inject a second command.
    const child = spawn(opts.ffmpegPath, args, { shell: false });

    let stderr = "";
    let settled = false;

    const timer = setTimeout(() => {
      if (!settled) {
        child.kill("SIGKILL");
      }
    }, opts.timeoutMs);

    child.stderr.setEncoding("utf8");
    child.stderr.on("data", (chunk: string) => {
      if (stderr.length < MAX_STDERR_BYTES) {
        stderr += chunk;
      }
    });

    child.on("error", (err: Error) => {
      if (settled) return;
      settled = true;
      clearTimeout(timer);
      rejectPromise(
        new FfmpegExecutionError(`Failed to launch FFmpeg: ${err.message}`, null, null, stderr),
      );
    });

    child.on("close", (code: number | null, signal: NodeJS.Signals | null) => {
      if (settled) return;
      settled = true;
      clearTimeout(timer);

      if (signal === "SIGKILL") {
        rejectPromise(
          new FfmpegExecutionError(
            `FFmpeg exceeded the ${opts.timeoutMs} ms timeout and was killed.`,
            code,
            signal,
            stderr.trim(),
          ),
        );
        return;
      }
      if (code !== 0) {
        rejectPromise(
          new FfmpegExecutionError(
            `FFmpeg exited with code ${code}.`,
            code,
            signal,
            stderr.trim(),
          ),
        );
        return;
      }

      resolvePromise({
        outputDir: opts.outputDir,
        outputPattern,
        command: args,
        durationMs: performance.now() - startedAt,
      });
    });
  });
}
```

### Programmatic usage (Python)

Load `references/` for the full Python wrapper when integrating into a Python service. The wrapper uses `subprocess.run` with a list (not a string) to keep `shell=False`, validates options, and surfaces typed errors.

```python
from __future__ import annotations

import re
import shutil
import subprocess
from dataclasses import dataclass
from enum import Enum
from pathlib import Path


class ExtractionMethod(Enum):
    SELECT_FILTER = "select-filter"
    SKIP_FRAME = "skip-frame"


class OutputImageFormat(Enum):
    PNG = "png"
    JPG = "jpg"
    BMP = "bmp"


class InvalidExtractionOptionsError(Exception):
    pass


class FfmpegExecutionError(Exception):
    def __init__(self, message: str, exit_code: int | None, stderr: str) -> None:
        super().__init__(message)
        self.exit_code = exit_code
        self.stderr = stderr


@dataclass(frozen=True)
class KeyframeExtractionOptions:
    input_path: Path
    output_dir: Path
    filename_stem: str = "keyframe"
    method: ExtractionMethod = ExtractionMethod.SELECT_FILTER
    image_format: OutputImageFormat = OutputImageFormat.PNG
    jpeg_quality: int = 2
    embed_timestamp: bool = False
    disable_autorotate: bool = False
    ffmpeg_path: str = "ffmpeg"
    timeout_seconds: int = 600


@dataclass(frozen=True)
class KeyframeExtractionResult:
    output_dir: Path
    output_pattern: Path
    command: tuple[str, ...]


_SAFE_STEM = re.compile(r"^[A-Za-z0-9._-]+$")


def _validate(options: KeyframeExtractionOptions) -> None:
    if not _SAFE_STEM.match(options.filename_stem):
        raise InvalidExtractionOptionsError(
            f"filename_stem {options.filename_stem!r} may only contain letters, digits, dot, "
            "underscore and hyphen so output cannot escape output_dir."
        )
    if not (2 <= options.jpeg_quality <= 31):
        raise InvalidExtractionOptionsError(
            "jpeg_quality must be between 2 (best) and 31 (worst)."
        )
    if options.timeout_seconds <= 0:
        raise InvalidExtractionOptionsError("timeout_seconds must be positive.")
    if shutil.which(options.ffmpeg_path) is None:
        raise InvalidExtractionOptionsError(
            f"FFmpeg executable not found on PATH: {options.ffmpeg_path!r}"
        )
    if not options.input_path.is_file():
        raise InvalidExtractionOptionsError(
            f"Input file is missing or not a regular file: {options.input_path}"
        )


def _build_command(options: KeyframeExtractionOptions, output_pattern: Path) -> list[str]:
    command: list[str] = [options.ffmpeg_path, "-hide_banner", "-loglevel", "error"]

    if options.disable_autorotate:
        command.append("-noautorotate")
    if options.method is ExtractionMethod.SKIP_FRAME:
        command += ["-skip_frame", "nokey"]

    command += ["-i", str(options.input_path)]

    if options.method is ExtractionMethod.SELECT_FILTER:
        command += ["-vf", "select='eq(pict_type,I)'"]

    command += ["-fps_mode", "vfr"]

    if options.embed_timestamp:
        command += ["-frame_pts", "1"]
    if options.image_format is OutputImageFormat.JPG:
        command += ["-q:v", str(options.jpeg_quality)]

    command.append(str(output_pattern))
    return command


def extract_keyframes(options: KeyframeExtractionOptions) -> KeyframeExtractionResult:
    _validate(options)
    options.output_dir.mkdir(parents=True, exist_ok=True)

    output_pattern = (
        options.output_dir / f"{options.filename_stem}_%03d.{options.image_format.value}"
    )
    command = _build_command(options, output_pattern)

    try:
        completed = subprocess.run(
            command,
            check=False,
            capture_output=True,
            text=True,
            timeout=options.timeout_seconds,
        )
    except FileNotFoundError as exc:
        raise FfmpegExecutionError(f"Could not launch FFmpeg: {exc}", None, "") from exc
    except subprocess.TimeoutExpired as exc:
        stderr = exc.stderr if isinstance(exc.stderr, str) else ""
        raise FfmpegExecutionError(
            f"FFmpeg exceeded the {options.timeout_seconds}s timeout.", None, stderr
        ) from exc

    if completed.returncode != 0:
        raise FfmpegExecutionError(
            f"FFmpeg exited with code {completed.returncode}.",
            completed.returncode,
            completed.stderr.strip(),
        )

    return KeyframeExtractionResult(
        output_dir=options.output_dir,
        output_pattern=output_pattern,
        command=tuple(command),
    )
```

## Pitfalls

- **`-skip_frame nokey` placed after `-i` does nothing.** It is a decoder option; after `-i` it is read as an output option and silently ignored, so you lose the speed-up and wonder why the fast path is slow. **Keep it before `-i`.**
- **`-vsync vfr` is deprecated.** It may still work on your build (with a warning), but `-fps_mode vfr` is the supported spelling and will not warn or break in future releases.
- **Adding `setpts=...` then expecting real timestamps in filenames.** `setpts` rewrites each frame's PTS to a fresh sequence, which defeats `-frame_pts 1`. For still images, leave it out.
- **Surprise rotation.** FFmpeg auto-rotates by default, so a portrait phone video comes out upright. If you genuinely need the raw stored pixels, add `-noautorotate` before `-i` — do not reach for a manual transpose filter unless the default truly does the wrong thing.
- **Building the command with string interpolation.** This re-introduces command injection. Pass paths as discrete, quoted arguments (shell) or argv array elements (the wrappers above).
- **PowerShell line continuation.** On Windows PowerShell, use backtick (`` ` ``) for line continuation, not backslash (`\`). Using `\` will cause FFmpeg to receive a mangled command line.
- **DRM-protected content.** FFmpeg will refuse to decode protected streams. This is a hard stop — do not attempt to work around it.

## Verification

Each check exists to catch a specific, real failure mode:

1. **Count matches.** The number of extracted files equals the `ffprobe` I-frame count. A mismatch usually means a wrong stream selector or a frame-rate flag duplicating/dropping frames.
   ```bash
   # Expected count from ffprobe
   ffprobe -v error -select_streams v:0 -skip_frame nokey \
     -show_entries frame=pict_type -of csv=p=0 "sample_clip.mp4" | grep -c '^I$'

   # Actual extracted count
   find ./keyframes -name 'keyframe_*.png' | wc -l
   ```
   ```powershell
   # PowerShell
   $expected = (ffprobe -v error -select_streams v:0 -skip_frame nokey `
     -show_entries frame=pict_type -of csv=p=0 "sample_clip.mp4" | Select-String '^I$').Count
   $actual = (Get-ChildItem -Path .\keyframes -Filter "keyframe_*.png").Count
   if ($expected -ne $actual) { Write-Error "Mismatch: expected $expected, got $actual" }
   ```

2. **Timestamps present when requested.** With `-frame_pts 1`, confirm filenames carry PTS values rather than a bare `1, 2, 3` counter — proof the flag took effect.
   ```bash
   ls ./keyframes/keyframe_*.png | head -5
   ```

3. **Images open cleanly.** Spot-check a few PNG/JPEG files for corruption and correct orientation; this catches truncated writes and unexpected `-noautorotate` effects.
   ```bash
   # Verify a file is a valid image (requires `file` command)
   file ./keyframes/keyframe_001.png
   ```

4. **FFmpeg version is ≥ 7.0** (`ffmpeg -version`), so `-fps_mode` and current decoder behaviour are guaranteed.

5. **Output directory permissions are appropriate** (commonly `0755`, or stricter if the frames are sensitive), so downstream steps can read them and nothing leaks.
   ```bash
   ls -ld ./keyframes
   ```

6. **Input provenance is trusted.** For files from untrusted sources, scan before processing and never interpolate the path into a shell string.

## Related skills

- `ffmpeg-video-editing`: Cut, trim, and concatenate segments. Keyframes matter there too — copy-mode cuts snap to them.
- `ffmpeg-video-filters`: Scale, crop, or watermark; chain after `select` in the same `-vf` graph if extracted frames need resizing.
- `ffmpeg-format-conversion`: Change container/codec; when re-encoding, `-g` and `-force_key_frames` control where future keyframes land.
- `ffmpeg-audio-processing`: Extract or process audio tracks instead of video frames.
- `ffmpeg-media-info`: Inspect streams and metadata; the ffprobe counting recipe above is the boundary between the two skills.
