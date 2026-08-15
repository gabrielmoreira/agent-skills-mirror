---
name: ffmpeg-format-conversion
version: 1.3.1
description: "Convert media between containers and codecs with FFmpeg - remux with -c copy, transcode to H.264/HEVC/AV1/Opus, CRF vs two-pass bitrate, hardware encoders (NVENC/QSV/VideoToolbox). Use when changing file format (MKV to MP4, WAV to Opus), shrinking files, or fixing playback compatibility. Not for trimming/joining clips (use ffmpeg-video-editing), visual effects (ffmpeg-video-filters), loudness/mixing (ffmpeg-audio-processing), or inspecting streams (ffmpeg-media-info)."
risk: safe
source: openrouter-deepsearch
date_added: 2026-06-16
---

# FFmpeg Format Conversion Skill

Convert media files between different formats and containers using FFmpeg. This skill covers modern codecs (AV1, HEVC), container switching, and optimization for 2026 hardware and software standards.

## Mental model: container, codec, and re-encoding

Understanding this model is what lets you pick the *fastest, least lossy* command instead of blindly re-encoding everything.

- **Container** (the file extension: `.mp4`, `.mkv`, `.webm`, `.mov`) is just a wrapper. It describes how streams are interleaved and indexed, but it does not encode the actual audio or video data.
- **Codec** (`libx264`, `libx265`, `aac`, `libopus`) is the algorithm that compressed each stream. The codec — not the container — determines quality, file size, and playback compatibility.
- **Re-encoding** means decoding a stream back to raw samples and compressing it again. For lossy codecs this *always* discards quality and costs significant CPU time, so it should be a deliberate choice, not a default.

The single most important consequence: **changing the container does not require re-encoding the streams.** If an MKV holds H.264 video and AAC audio that an MP4 can also hold, you can copy the streams byte-for-byte into a new container (a "remux"). That is why `-c copy` appears so often below — it is near-instant and lossless. Reach for a real encoder only when the target container genuinely cannot carry the existing codec, or when you actually want different quality, size, or compatibility.

## When to Use

- Convert video containers (MP4, MKV, AVI, WebM, etc.) — often a pure remux.
- Convert audio formats (MP3, AAC, WAV, Opus, FLAC, etc.).
- Transcode to a different codec for compatibility (old TV, browser, phone) or for better compression.
- Copy streams without re-encoding (stream copying / remuxing) for near-instant conversion.
- Optimize media for web delivery (smaller, faststart) or archival storage (lossless).

### When NOT to use

| If the task is... | Use instead |
| --- | --- |
| Cutting, trimming, or concatenating clips | `ffmpeg-video-editing` |
| Scaling, cropping, watermarks, speed changes, visual effects | `ffmpeg-video-filters` |
| Loudness normalization, mixing, channel extraction | `ffmpeg-audio-processing` |
| Inspecting codecs, streams, or duration (often the right *first* step) | `ffmpeg-media-info` |
| Extracting keyframes or thumbnails | `ffmpeg-keyframe-extraction` |

Also out of scope:

- Media already in the desired container *and* codec — re-encoding again only adds generation loss and wastes time.
- High-end non-linear editing (color grading, multi-track timelines) where a dedicated NLE/DAW gives you a UI and non-destructive edits.
- DRM-encrypted files without the proper, lawfully obtained decryption keys.

## Prerequisites

- **FFmpeg** installed and on `PATH`. Verify with `ffmpeg -version` (Windows PowerShell) or `which ffmpeg` (macOS/Linux).
- **ffprobe** (ships with FFmpeg) for verification steps.
- For hardware encoders: appropriate GPU drivers (NVIDIA for NVENC, Intel for QSV, Apple for VideoToolbox).
- For batch scripts: Bash shell on macOS/Linux, or Git Bash / WSL on Windows. The TypeScript wrapper requires Node.js 18+.

## Decision guide

| Situation | Approach | Why |
| --- | --- | --- |
| Same codecs, different container (MKV to MP4) | `-c copy` (remux) | Lossless and seconds-fast; no quality decision to make. |
| Target container cannot hold the source codec | Re-encode only the offending stream | Copy what you can, transcode the minimum. |
| Need smaller files for the web | `libx265`/`libsvtav1` with CRF | Modern codecs cut size ~30-50% at equal quality. |
| Need maximum playback compatibility | `libx264` + `yuv420p` + AAC | Plays on essentially everything, including old hardware. |
| Need an exact target file size | Two-pass bitrate encoding | The first pass measures complexity so the budget lands accurately. |
| Encoding a huge batch or in real time | Hardware encoder (NVENC/QSV/VideoToolbox) | Order-of-magnitude faster, at a small efficiency cost. |

## Procedure

### Step 1: Probe the source before converting

Always inspect the source first so you know which streams exist and whether a remux is possible.

```powershell
# Windows PowerShell — probe source streams
ffprobe -v error -show_entries stream=index,codec_type,codec_name -of default input.mkv
```

```bash
# macOS/Linux — same probe
ffprobe -v error -show_entries stream=index,codec_type,codec_name -of default input.mkv
```

Record the codec names and stream count. This baseline is what you compare the output against in Verification.

### Step 2: Stream copy (remux) — try this first

Because a remux is lossless and fast, it should be your first instinct whenever the source codecs are already compatible with the target container.

```bash
# Change container only, copying every stream byte-for-byte (no quality loss).
ffmpeg -i input.mkv -c copy output.mp4

# Copy video but re-encode only the audio (e.g. MKV's FLAC into MP4-friendly AAC).
ffmpeg -i input.mkv -c:v copy -c:a aac -b:a 192k output.mp4

# Web delivery: relocate the MP4 moov atom to the front so playback can start
# before the whole file downloads. -movflags +faststart is why web video "just plays".
ffmpeg -i input.mp4 -c copy -movflags +faststart output.mp4
```

### Step 3: Re-encode when remux is not possible

Be explicit about both the video and audio codec. Relying on FFmpeg's container-default codec works, but stating `-c:v` and `-c:a` makes the command self-documenting and reproducible.

```bash
# Full re-encode of an old AVI into a modern, widely playable MP4.
ffmpeg -i input.avi -c:v libx264 -c:a aac output.mp4

# Re-encode video, keep the original audio untouched (faster, no audio loss).
ffmpeg -i input.mp4 -c:v libx265 -crf 28 -c:a copy output.mp4
```

### Step 4: Choose the video codec

Each codec is a trade between compatibility, file size, and encode speed. Pick based on *where the file will play*, not on which codec is newest.

```bash
# H.264 (AVC) — the universal default. yuv420p guarantees playback on old
# hardware decoders and QuickTime, which reject other chroma layouts.
ffmpeg -i input.mp4 -c:v libx264 -pix_fmt yuv420p -crf 23 -c:a aac output.mp4

# H.265 (HEVC) — ~30-50% smaller than H.264 at equal quality. Ideal for 4K/HDR,
# but licensing means some browsers still will not decode it.
ffmpeg -i input.mp4 -c:v libx265 -crf 28 -c:a aac output.mp4

# VP9 (WebM) — royalty-free and natively supported by browsers. -b:v 0 is
# REQUIRED to put libvpx-vp9 into true constant-quality (CRF) mode.
ffmpeg -i input.mp4 -c:v libvpx-vp9 -crf 30 -b:v 0 -c:a libopus output.webm

# AV1 — best compression available and royalty-free. libsvtav1 (SVT-AV1) is the
# practical choice because it is far faster than the reference libaom encoder.
# -preset trades speed for efficiency (lower = slower/smaller).
ffmpeg -i input.mp4 -c:v libsvtav1 -preset 6 -crf 30 -c:a libopus output.mp4
```

### Step 5: Choose the audio codec

The audio choice mirrors the video logic: lossless for archives, efficient lossy codecs for distribution, legacy codecs only when a target device demands them.

```bash
# MP3 — only for legacy gear that cannot do anything better. -q:a 2 is VBR
# ~190 kbps, a good transparency/size balance for libmp3lame.
ffmpeg -i input.wav -c:a libmp3lame -q:a 2 output.mp3

# AAC — the modern default for MP4/M4A; better than MP3 at the same bitrate.
ffmpeg -i input.wav -c:a aac -b:a 192k output.m4a

# Opus — the most efficient lossy codec; transparent for music near 128 kbps
# and excellent for speech at far lower bitrates.
ffmpeg -i input.wav -c:a libopus -b:a 128k output.opus

# FLAC — lossless. Use it for archival masters where bitrate is set "k" only
# implicitly by the source; quality is bit-exact to the input.
ffmpeg -i input.wav -c:a flac output.flac
```

### Step 6: Quality control — CRF vs. bitrate

CRF (Constant Rate Factor) targets a *consistent visual quality* and lets file size float, which is what you want for almost all on-demand video. Target-bitrate encoding does the opposite: it pins the size and lets quality float. Reach for bitrate only when a hard size limit matters.

```bash
# CRF — lower number = higher quality = larger file. Sensible starting points:
#   H.264: 18-23   |   H.265: 23-28   |   AV1/VP9: 25-35
ffmpeg -i input.mp4 -c:v libx264 -crf 23 -c:a copy output.mp4

# Target average bitrate (size-constrained, single pass — fast but less precise).
ffmpeg -i input.mp4 -c:v libx264 -b:v 2M -c:a aac -b:a 192k output.mp4

# Two-pass — most accurate way to hit an exact size. Pass 1 analyzes complexity
# (audio disabled with -an since it is irrelevant to that analysis) and writes a
# log; pass 2 spends the bitrate budget where the video needs it most.
# The throwaway target is /dev/null on macOS/Linux and NUL on Windows.
ffmpeg -y -i input.mp4 -c:v libx264 -b:v 2M -pass 1 -an -f null /dev/null
ffmpeg -y -i input.mp4 -c:v libx264 -b:v 2M -pass 2 -c:a aac -b:a 192k output.mp4
```

**Windows PowerShell two-pass variant** — use `NUL` as the null sink:

```powershell
ffmpeg -y -i input.mp4 -c:v libx264 -b:v 2M -pass 1 -an -f null NUL
ffmpeg -y -i input.mp4 -c:v libx264 -b:v 2M -pass 2 -c:a aac -b:a 192k output.mp4
```

### Step 7: Speed presets

A preset is a dial between encode time and compression efficiency. A slower preset spends more CPU finding savings, producing a smaller file at the *same* CRF — quality stays constant, size and time change. Use a slow preset for files you encode once and serve many times; use a fast preset for throwaway or real-time work.

```bash
# x264/x265 presets, slowest/smallest to fastest/largest:
#   ultrafast, superfast, veryfast, faster, fast, medium, slow, slower, veryslow
ffmpeg -i input.mp4 -c:v libx264 -preset slow -crf 22 -c:a copy output.mp4

# SVT-AV1 uses a numeric preset (0-13). Higher is faster but less efficient;
# preset 6-8 is a practical quality/speed sweet spot for most content.
ffmpeg -i input.mp4 -c:v libsvtav1 -preset 8 -crf 30 -c:a libopus output.mp4
```

### Step 8: Hardware acceleration (optional)

Hardware encoders run on the GPU's dedicated media block instead of the CPU. They are typically an order of magnitude faster, which makes them ideal for large batches or live streaming. The trade-off: at a given file size they are slightly less efficient than a slow software encode, so for archival masters where every bit counts, software (`libx264`/`libx265`/`libsvtav1`) still wins.

```bash
# NVIDIA NVENC — -cq is the quality target (CRF-like); -preset p1..p7 sets speed.
ffmpeg -i input.mp4 -c:v h264_nvenc -preset p5 -cq 23 -c:a copy output.mp4
ffmpeg -i input.mp4 -c:v hevc_nvenc -preset p5 -cq 28 -c:a copy output.mp4

# Intel Quick Sync (integrated GPU) — -global_quality is the CRF-equivalent.
ffmpeg -i input.mp4 -c:v h264_qsv -global_quality 23 -c:a copy output.mp4

# Apple VideoToolbox (macOS) — accepts a target bitrate.
ffmpeg -i input.mp4 -c:v h264_videotoolbox -b:v 4M -c:a copy output.mp4

# Hardware AV1 — now common (NVIDIA RTX 40+ series, Intel Arc/Core Ultra).
# Near-NVENC-H.264 speed with AV1's compression; ideal for batch AV1 output.
ffmpeg -i input.mp4 -c:v av1_nvenc -preset p5 -cq 30 -c:a copy output.mp4
ffmpeg -i input.mp4 -c:v av1_qsv -global_quality 30 -c:a copy output.mp4
```

### Step 9: Batch conversion (Bash)

A naive `for f in *.mkv` loop is a trap: it silently does nothing when there are no matches, breaks on filenames with spaces, clobbers existing outputs, and reports success even when individual encodes fail. The script below is the hardened version.

**When to use:** If you need to convert more than a handful of files, copy the batch script example below into your project. It handles nullglob, never clobbers, deletes half-written outputs on failure, and propagates a non-zero exit code to CI.

```bash
#!/usr/bin/env bash
# convert-batch.sh — convert every file matching a glob into a target container.
# Defensive by design: fail fast, validate inputs, never clobber, report a summary.
set -euo pipefail

usage() {
  cat >&2 <<'EOF'
Usage: convert-batch.sh <source-ext> <target-ext> [ffmpeg-args...]
  source-ext   Extension to match in the current directory (e.g. mkv)
  target-ext   Extension for the produced files (e.g. mp4)
  ffmpeg-args  Optional encoder flags. Defaults to stream copy (-c copy).

Examples:
  convert-batch.sh mkv mp4                       # remux, no re-encode
  convert-batch.sh avi mp4 -c:v libx264 -c:a aac # re-encode to H.264/AAC
EOF
  exit 64  # EX_USAGE
}

# --- Validate parameters --------------------------------------------------
[[ $# -ge 2 ]] || usage
src_ext="${1#.}"            # tolerate a leading dot: "mkv" or ".mkv"
dst_ext="${2#.}"
shift 2
# Whatever remains is the encoder flag list; default to a lossless remux.
ffmpeg_args=("$@")
[[ ${#ffmpeg_args[@]} -gt 0 ]] || ffmpeg_args=(-c copy)

if [[ "$src_ext" == "$dst_ext" ]]; then
  echo "error: source and target extensions are identical ('$src_ext')" >&2
  exit 64
fi

# --- Validate environment -------------------------------------------------
if ! command -v ffmpeg >/dev/null 2>&1; then
  echo "error: ffmpeg is not installed or not on PATH" >&2
  exit 69  # EX_UNAVAILABLE
fi

# --- Collect inputs safely (nullglob => empty array, not a literal '*') ----
shopt -s nullglob
inputs=( *."${src_ext}" )
shopt -u nullglob
if [[ ${#inputs[@]} -eq 0 ]]; then
  echo "error: no *.${src_ext} files found in $(pwd)" >&2
  exit 66  # EX_NOINPUT
fi

# --- Convert --------------------------------------------------------------
converted=0
skipped=0
failed=0
for input in "${inputs[@]}"; do
  output="${input%.*}.${dst_ext}"

  if [[ -e "$output" ]]; then
    echo "skip: '$output' already exists" >&2
    skipped=$((skipped + 1))
    continue
  fi

  echo "converting: '$input' -> '$output'"
  # -nostdin stops ffmpeg from consuming the loop's stdin and eating filenames.
  if ffmpeg -nostdin -hide_banner -loglevel error \
       -i "$input" "${ffmpeg_args[@]}" "$output"; then
    converted=$((converted + 1))
  else
    echo "error: conversion failed for '$input'" >&2
    rm -f -- "$output"     # delete the half-written output so it cannot mislead
    failed=$((failed + 1))
  fi
done

echo "done: ${converted} converted, ${skipped} skipped, ${failed} failed, ${#inputs[@]} total"
# Propagate failure to the caller / CI so a partial batch is not "green".
[[ $failed -eq 0 ]]
```

### Step 10: Programmatic conversion (TypeScript wrapper)

**When to use:** If conversion is part of a larger Node.js application, copy the TypeScript wrapper example below into your project. It uses `spawn` (an argument array, never a shell string) to prevent shell-injection from unsanitized paths, validates parameters before launching, and surfaces failures as typed errors. There are no `any` types — `unknown` plus type guards handle the genuinely dynamic edges.

```typescript
import { spawn } from "node:child_process";
import { access, constants } from "node:fs/promises";
import { basename } from "node:path";

/** Video encoders this wrapper knows how to drive. "copy" means remux, not encode. */
type VideoCodec = "libx264" | "libx265" | "libvpx-vp9" | "libsvtav1" | "copy";

/** Audio encoders this wrapper knows how to drive. "copy" means remux, not encode. */
type AudioCodec = "aac" | "libmp3lame" | "libopus" | "flac" | "copy";

/** libx264/libx265 speed presets, slowest (best ratio) to fastest. */
type X26xPreset =
  | "ultrafast"
  | "superfast"
  | "veryfast"
  | "faster"
  | "fast"
  | "medium"
  | "slow"
  | "slower"
  | "veryslow";

interface ConvertOptions {
  /** Path to an existing, readable source media file. */
  readonly input: string;
  /** Destination path; its extension selects the output container. */
  readonly output: string;
  /** Video encoder. Use "copy" to remux without re-encoding. */
  readonly videoCodec: VideoCodec;
  /** Audio encoder. Use "copy" to remux without re-encoding. */
  readonly audioCodec: AudioCodec;
  /** Constant Rate Factor. Forbidden when videoCodec is "copy". */
  readonly crf?: number;
  /** x264/x265 speed preset. Ignored by non-x26x encoders. */
  readonly preset?: X26xPreset;
  /** Audio bitrate in kbps (e.g. 128, 192). Forbidden for lossless flac. */
  readonly audioBitrateKbps?: number;
  /** Replace the output if it already exists. Defaults to false. */
  readonly overwrite?: boolean;
}

interface ConvertResult {
  /** The path that was written on success. */
  readonly output: string;
  /** The exact argument vector handed to ffmpeg (useful for logging/tests). */
  readonly args: readonly string[];
}

/** Valid CRF window per encoder; outside it, output is wasteful or visibly broken. */
const CRF_RANGES: Readonly<
  Record<Exclude<VideoCodec, "copy">, readonly [min: number, max: number]>
> = {
  libx264: [0, 51],
  libx265: [0, 51],
  "libvpx-vp9": [0, 63],
  libsvtav1: [0, 63],
};

/** Raised when ffmpeg launches but exits non-zero; carries the captured stderr. */
class FfmpegError extends Error {
  constructor(
    message: string,
    readonly exitCode: number | null,
    readonly stderr: string,
  ) {
    super(message);
    this.name = "FfmpegError";
  }
}

/** Narrow an unknown caught value to a Node system error without using `any`. */
function isNodeError(value: unknown): value is NodeJS.ErrnoException {
  return value instanceof Error && "code" in value;
}

async function fileExists(path: string): Promise<boolean> {
  try {
    await access(path, constants.F_OK);
    return true;
  } catch {
    return false;
  }
}

async function assertReadableFile(path: string): Promise<void> {
  try {
    await access(path, constants.R_OK);
  } catch (cause: unknown) {
    const reason =
      isNodeError(cause) && cause.code === "ENOENT" ? "does not exist" : "is not readable";
    throw new Error(`input file '${path}' ${reason}`);
  }
}

/** Reject impossible or contradictory requests *before* spawning a process. */
function validate(options: ConvertOptions): void {
  if (options.input.trim() === "" || options.output.trim() === "") {
    throw new RangeError("input and output paths must be non-empty");
  }
  if (options.input === options.output) {
    throw new RangeError("input and output paths must differ");
  }

  if (options.crf !== undefined) {
    if (options.videoCodec === "copy") {
      throw new RangeError("crf cannot be combined with videoCodec 'copy'");
    }
    if (!Number.isInteger(options.crf)) {
      throw new RangeError(`crf must be an integer, received ${options.crf}`);
    }
    const [min, max] = CRF_RANGES[options.videoCodec];
    if (options.crf < min || options.crf > max) {
      throw new RangeError(
        `crf for ${options.videoCodec} must be within ${min}-${max}, received ${options.crf}`,
      );
    }
  }

  if (options.audioBitrateKbps !== undefined) {
    if (options.audioCodec === "flac") {
      throw new RangeError("audioBitrateKbps is meaningless for lossless flac");
    }
    if (!Number.isFinite(options.audioBitrateKbps) || options.audioBitrateKbps <= 0) {
      throw new RangeError(
        `audioBitrateKbps must be a positive number, received ${options.audioBitrateKbps}`,
      );
    }
  }
}

/** Build the ffmpeg argument vector. Every flag is conditioned on the codec it belongs to. */
function buildArgs(options: ConvertOptions): string[] {
  const args: string[] = ["-nostdin", "-hide_banner", "-loglevel", "error"];
  args.push(options.overwrite === true ? "-y" : "-n");
  args.push("-i", options.input);

  args.push("-c:v", options.videoCodec);
  if (options.videoCodec !== "copy") {
    if (options.crf !== undefined) {
      args.push("-crf", String(options.crf));
    }
    if (
      options.preset !== undefined &&
      (options.videoCodec === "libx264" || options.videoCodec === "libx265")
    ) {
      args.push("-preset", options.preset);
    }
    if (options.videoCodec === "libx264") {
      // yuv420p keeps H.264 playable on old hardware decoders and QuickTime.
      args.push("-pix_fmt", "yuv420p");
    }
    if (options.videoCodec === "libvpx-vp9" && options.crf !== undefined) {
      // VP9 needs an explicit -b:v 0 to enter true constant-quality CRF mode.
      args.push("-b:v", "0");
    }
  }

  args.push("-c:a", options.audioCodec);
  if (
    options.audioCodec !== "copy" &&
    options.audioCodec !== "flac" &&
    options.audioBitrateKbps !== undefined
  ) {
    args.push("-b:a", `${options.audioBitrateKbps}k`);
  }

  args.push(options.output);
  return args;
}

/**
 * Convert a single media file. Resolves with the output path on success;
 * rejects with a RangeError/Error for bad input, or an FfmpegError if the
 * encode itself fails. Never throws synchronously.
 */
async function convert(options: ConvertOptions): Promise<ConvertResult> {
  validate(options);
  await assertReadableFile(options.input);

  if (options.overwrite !== true && (await fileExists(options.output))) {
    throw new Error(
      `output '${options.output}' already exists; set overwrite: true to replace it`,
    );
  }

  const args = buildArgs(options);

  return new Promise<ConvertResult>((resolve, reject) => {
    const child = spawn("ffmpeg", args, { stdio: ["ignore", "ignore", "pipe"] });
    let stderr = "";

    // child.stderr is typed as nullable; optional chaining keeps us strict-safe.
    child.stderr?.setEncoding("utf8");
    child.stderr?.on("data", (chunk: string) => {
      stderr += chunk;
    });

    // Fires when the binary cannot be launched at all (e.g. not installed).
    child.on("error", (cause: Error) => {
      const hint =
        isNodeError(cause) && cause.code === "ENOENT"
          ? "ffmpeg not found on PATH — install it or fix PATH"
          : cause.message;
      reject(new Error(`failed to start ffmpeg: ${hint}`));
    });

    child.on("close", (code: number | null) => {
      if (code === 0) {
        resolve({ output: options.output, args });
        return;
      }
      reject(
        new FfmpegError(
          `ffmpeg exited with code ${code ?? "null"} while writing '${basename(options.output)}'`,
          code,
          stderr.trim(),
        ),
      );
    });
  });
}

// --- Example usage --------------------------------------------------------
async function main(): Promise<void> {
  try {
    const result = await convert({
      input: "input.mkv",
      output: "output.mp4",
      videoCodec: "libx265",
      audioCodec: "aac",
      crf: 28,
      preset: "slow",
      audioBitrateKbps: 192,
      overwrite: false,
    });
    console.log(`wrote ${result.output} via: ffmpeg ${result.args.join(" ")}`);
  } catch (error: unknown) {
    if (error instanceof FfmpegError) {
      console.error(`conversion failed (exit ${error.exitCode}):\n${error.stderr}`);
      process.exitCode = 1;
    } else if (error instanceof Error) {
      console.error(`invalid request: ${error.message}`);
      process.exitCode = 2;
    } else {
      console.error("unknown failure", error);
      process.exitCode = 3;
    }
  }
}

void main();

export { convert, FfmpegError };
export type { ConvertOptions, ConvertResult, VideoCodec, AudioCodec, X26xPreset };
```

## Examples

### Quick reference: common conversions

```bash
# MKV to MP4 (remux, lossless, instant)
ffmpeg -i input.mkv -c copy output.mp4

# MKV to MP4 with AAC audio (re-encode audio only)
ffmpeg -i input.mkv -c:v copy -c:a aac -b:a 192k output.mp4

# WAV to Opus (efficient lossy)
ffmpeg -i input.wav -c:a libopus -b:a 128k output.opus

# AVI to MP4 (full re-encode for compatibility)
ffmpeg -i input.avi -c:v libx264 -pix_fmt yuv420p -crf 23 -c:a aac output.mp4

# MP4 to WebM (royalty-free, browser-native)
ffmpeg -i input.mp4 -c:v libvpx-vp9 -crf 30 -b:v 0 -c:a libopus output.webm

# Shrink a file with HEVC
ffmpeg -i input.mp4 -c:v libx265 -crf 28 -c:a copy output.mp4

# Web-optimized MP4 (faststart)
ffmpeg -i input.mp4 -c copy -movflags +faststart output.mp4
```

### Common codecs reference

**Video:**
- **H.264** (`libx264`) — universal compatibility; the safe default when the target is unknown.
- **H.265** (`libx265`) — high efficiency for 4K/HDR; smaller files, but patchy browser support.
- **VP9** (`libvpx-vp9`) — royalty-free, native in browsers; remember `-b:v 0` for CRF mode.
- **AV1** (`libsvtav1` / `libaom-av1`) — best compression and royalty-free; prefer SVT-AV1 for usable encode speeds, or `av1_nvenc`/`av1_qsv` where the GPU supports it.

**Audio:**
- **AAC** (`aac`) — the modern default for MP4/M4A; better than MP3 at equal bitrate.
- **MP3** (`libmp3lame`) — legacy only; choose it when a specific old device requires it.
- **Opus** (`libopus`) — most efficient lossy codec, superb for both speech and music.
- **FLAC** (`flac`) — lossless; for archival masters and lossless transcodes.

## Pitfalls

- **Remux before you re-encode.** If you only need to change the container, `-c copy` is lossless and seconds-fast. Re-encoding "just to be safe" throws away quality for no benefit.
- **`-pix_fmt yuv420p` for H.264.** Many hardware decoders and QuickTime reject other chroma subsamplings (such as `yuv444p`). Adding it is the difference between "plays everywhere" and "black screen on a smart TV".
- **`+faststart` for web MP4s.** Without it the index (`moov` atom) sits at the end of the file, so a browser must download the whole thing before playback can begin. It is a free remux flag, so include it for anything streamed.
- **VP9 CRF needs `-b:v 0`.** Omitting it leaves libvpx in a constrained-bitrate mode and your `-crf` is effectively ignored.
- **Hardware encoders are fast, not free.** NVENC/QSV/VideoToolbox trade a little compression efficiency for huge speed. Great for batches and live; for size-critical archival, slow software encoding still wins per bit.
- **Process untrusted media carefully.** Malformed files have historically triggered decoder vulnerabilities. Keep FFmpeg current, and in automated pipelines prefer `spawn` with an argument array over a shell string so filenames cannot inject commands.
- **Use modern flag syntax.** Prefer `-c:v` / `-c:a` over the deprecated `-vcodec` / `-acodec`; the stream-specifier form is what current documentation and newer features assume.
- **The null sink is platform-specific.** Two-pass pass-one discards its muxed output to `/dev/null` on macOS/Linux and `NUL` on Windows.
- **Naive batch loops are dangerous.** A bare `for f in *.mkv` silently does nothing when there are no matches (the glob expands to a literal `*.mkv`), breaks on filenames with spaces, clobbers existing outputs, and reports success even when individual encodes fail. Always use `nullglob`, `-nostdin`, existence checks, and exit-code propagation.
- **Never delete source files.** Conversion outputs are derivatives; the source is the master. Automated pipelines must never delete or overwrite the original input as part of a conversion step.

## Verification

These checks exist because FFmpeg can exit `0` while still producing a file that is subtly wrong (missing audio, wrong pixel format, unplayable on the target). Confirm the *result*, not just the exit code.

1. **Probe the source** to record a baseline:

```bash
ffprobe -v error -show_entries stream=index,codec_type,codec_name -of default input.mkv
```

2. **Probe the output** and confirm the codec and container match what you intended:

```bash
ffprobe -v error -show_entries stream=index,codec_type,codec_name -of default output.mp4
```

3. **Confirm stream counts match.** A dropped audio or subtitle track is a common silent failure:

```bash
ffprobe -v error -show_entries stream=index,codec_type -of csv output.mp4
```

4. **Play the output** in a real player (VLC, mpv, or the actual target device) to catch A/V sync and seeking problems that ffprobe cannot see.

5. **Check the file size** against your goal — if you re-encoded to shrink a file and it grew, the CRF/bitrate is wrong.

6. **For batch jobs:** confirm the output count equals the input count, and that the script's exit code is `0`.

## Related skills

- `ffmpeg-media-info` — probe codecs, streams, and duration first; the answer decides remux vs. re-encode.
- `ffmpeg-video-editing` — cut, trim, and concatenate segments.
- `ffmpeg-video-filters` — scale, crop, watermark, speed, and visual effects.
- `ffmpeg-audio-processing` — loudness normalization, mixing, and channel work.
- `ffmpeg-keyframe-extraction` — pull I-frames and thumbnails out of video.
