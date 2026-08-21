---
name: remotion-video-generation
description: "Structures Remotion 4.x React compositions including fps, durationInFrames, Zod props, frame-accurate timelines, CLI and Lambda render, fonts, and remote-asset CORS. Use when building, configuring, or debugging Remotion compositions or render pipelines. Not for quote-film transition recipes (transition), ComfyUI or LongCat generation, or ffmpeg-only transcodes."
version: 1.0.1
---

# Programmatic Video Generation with Remotion

Guide for structuring, rendering, and animating dynamic videos using Remotion 4.x, React, and programmatic audio/transcript synchronization.

> **Version note:** Examples target `remotion@4.0.x`. When upgrading minors, re-verify the `calculateMetadata`, Lambda, and font-loading snippets — these APIs have churned across the 4.x line.

---

## When to Use

- Building programmatic video pipelines with React components as frames
- Configuring Remotion `<Composition>` with Zod-validated JSON props
- Sequencing audio, subtitles, or clips on a frame-accurate timeline
- Rendering via CLI (`npx remotion render`) or AWS Lambda (`@remotion/lambda`)
- Debugging font loading, remote-asset CORS/SSRF, or audio drift between Studio and Lambda
- Producing transparent/alpha-channel video output (ProRes 4444, WebM VP8/VP9)

---

## Prerequisites

- Node.js 18+ and npm/npx available on PATH
- `remotion@4.0.x` installed in the project (`npm install remotion`)
- For Lambda: `@remotion/lambda` client + a deployed Lambda function (major.minor must match client)
- For programmatic rendering: `@remotion/bundler` and `@remotion/renderer`
- For Zod schemas: `zod` installed
- Windows host is primary (PowerShell). Use backslash paths for absolute Windows paths in CLI commands.

---

## Procedure

### 1. Register the Root Composition

Every Remotion video is registered via `<Composition />`. Define frame rate, dimensions, and duration in frames.

**Frame rate convention:** `fps` (frame rate) and `durationInFrames` (frame count) are different quantities; the number `30` legitimately appears as either. In any expression that converts seconds → frames, multiply by `fps` from `useVideoConfig()` rather than a literal. Literals are fine where you actually mean "frame index 30."

**Even-dimension constraint:** For h.264 / h.265 output, `width` and `height` must both be even, or ffmpeg fails at render. Configure correctly here; the failure surfaces at render time (§7).

**Inclusive frame range convention:** Throughout this skill, `startFrame` and `endFrame` are **inclusive on both ends** — a word with `startFrame: 10, endFrame: 25` is visible for 16 frames (10, 11, …, 25). Any helper that accepts `(start, end)` must preserve this convention.

```tsx
import { Composition } from 'remotion';
import { VideoTimeline } from './components/VideoTimeline';
import { videoSchema } from './schema';

export const RemotionRoot: React.FC = () => {
  return (
    <Composition
      id="DynamicVideo"
      component={VideoTimeline}
      durationInFrames={900}
      fps={30}
      width={1080}
      height={1920}
      schema={videoSchema}
      defaultProps={{
        titleText: 'Welcome to Programmatic Video',
        audioUrl: 'https://cdn.example.com/audio.mp3',
        words: [
          { text: 'Welcome',      startFrame: 10, endFrame: 25 },
          { text: 'to',           startFrame: 26, endFrame: 35 },
          { text: 'Programmatic', startFrame: 36, endFrame: 60 },
          { text: 'Video',        startFrame: 61, endFrame: 85 },
        ],
      }}
    />
  );
};
```

### 2. Build the Timeline with Sequences

Use `<Sequence />` to mount components only during specific frame ranges. Negative `from` (`<Sequence from={-90}>`) shifts a child's internal frame clock — useful for trimming an intro off a clip while preserving absolute timeline placement.

For strictly sequential clips, prefer `<Series>` over manually summing offsets:

```tsx
import { Series } from 'remotion';

<Series>
  <Series.Sequence durationInFrames={90}><Intro /></Series.Sequence>
  <Series.Sequence durationInFrames={810}><MainBody /></Series.Sequence>
</Series>
```

`durationInFrames` lives on each `Series.Sequence`, not on the parent. For crossfades use `<TransitionSeries>`, where a `<TransitionSeries.Transition>` is placed **between** two `<TransitionSeries.Sequence>` children — never after the last sequence (a trailing transition is a silent no-op that wastes frames).

**Performance threshold:** More than ~200 simultaneously active sequences on a single frame becomes noticeable, but the real ceiling depends on what each sequence renders. Profile your scene; do not treat 200 as a hard limit.

**`spring` configuration:** `spring` accepts `{ damping, mass, stiffness, overshootClamping }`. `damping` is the parameter most users tune first — higher values settle faster with less oscillation. Passing `durationInFrames` to `spring` overrides the physics and forces the animation into that many frames; if a spring "doesn't feel springy," check whether `durationInFrames` has been set.

**Timeline component example:**

```tsx
import {
  Sequence, Audio, useCurrentFrame, interpolate, spring, useVideoConfig,
} from 'remotion';
import type { VideoProps } from './schema';

export const VideoTimeline: React.FC<VideoProps> = ({ titleText, audioUrl, words }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const titleEntrance = spring({
    frame,
    fps,
    config: { damping: 12, mass: 1, stiffness: 100, overshootClamping: false },
  });
  const titleScale = interpolate(titleEntrance, [0, 1], [0.5, 1]);
  const titleOpacity = interpolate(titleEntrance, [0, 1], [0, 1]);

  return (
    <div style={{ flex: 1, backgroundColor: '#0f172a', position: 'relative', overflow: 'hidden' }}>
      <Audio src={audioUrl} />

      <Sequence from={0} durationInFrames={90}>
        <div style={{
          position: 'absolute', top: '50%', left: '50%',
          transform: `translate(-50%, -50%) scale(${titleScale})`,
          opacity: titleOpacity, color: '#f8fafc',
          fontSize: 64, fontFamily: 'Inter, sans-serif', textAlign: 'center',
        }}>
          {titleText}
        </div>
      </Sequence>

      <Sequence from={90} durationInFrames={810}>
        <div style={{
          position: 'absolute', bottom: 200, left: 0, right: 0,
          display: 'flex', justifyContent: 'center',
        }}>
          {words.map((word, index) => {
            // Off-frame returns null — runtime gating, expected and silent.
            // Inverted ranges (start > end) are rejected at schema parse, not here.
            if (frame < word.startFrame || frame > word.endFrame) return null;
            return (
              <span key={index} style={{
                color: '#fbbf24', fontSize: 72, fontWeight: 'bold',
                fontFamily: 'Outfit, sans-serif',
                textShadow: '0px 4px 10px rgba(0,0,0,0.5)',
              }}>
                {word.text}
              </span>
            );
          })}
        </div>
      </Sequence>
    </div>
  );
};
```

**Static vs runtime validation — two complementary checks:**

- **Schema (`z.refine`)** — static invariants at props-parse time: `startFrame ≤ endFrame`, non-empty `words`, URL shape. Throws loudly before render begins.
- **Runtime (inline `null` returns)** — dynamic gating: "is this word currently on screen?" Returns `null` when off-frame.

`refine` does not — and should not — fire when the current frame falls outside every word's range. That is normal runtime behavior, not a validation failure.

### 3. Define the Zod Schema (Single Source of Truth)

A single `schema.ts` is the source of truth. The root composition imports it for the `schema` prop; the timeline component imports the inferred type via `z.infer`.

```ts
import { z } from 'zod';

const TRUSTED_HOSTS = new Set([
  'cdn.example.com',
  'storage.googleapis.com',
]);

// Scheme + host allow-list is the minimum bar. See §5 for the residual
// SSRF pitfalls this does NOT catch (IDN/punycode, IPv6 literals, userinfo, …).
const remoteUrl = z.string().url().refine((raw) => {
  try {
    const u = new URL(raw);
    if (u.protocol !== 'https:') return false;
    if (u.username || u.password) return false;
    return TRUSTED_HOSTS.has(u.hostname);
  } catch {
    return false;
  }
}, { message: 'audioUrl must be https and on the trusted host list' });

const wordSchema = z.object({
  text: z.string().min(1),
  startFrame: z.number().int().nonnegative(),
  endFrame: z.number().int().nonnegative(),
}).refine((w) => w.startFrame <= w.endFrame, {
  message: 'startFrame must be ≤ endFrame',
});

export const videoSchema = z.object({
  titleText: z.string().min(1),
  audioUrl: remoteUrl,
  words: z.array(wordSchema).min(1),
});

export type VideoProps = z.infer<typeof videoSchema>;
```

**Seconds → frames helper:**

```ts
// Math.round is fine for short clips. For long compositions at fractional fps
// (29.97, 23.976), repeated per-segment rounding accumulates drift — accumulate
// against the whole timeline instead, or pre-quantize seconds to frame boundaries.
const secondsToFrames = (seconds: number, fps: number) => Math.round(seconds * fps);

export const makeWordsFromSeconds = (fps: number) =>
  z.object({
    text: z.string().min(1),
    startSeconds: z.number().nonnegative(),
    endSeconds: z.number().nonnegative(),
  }).transform((w) => ({
    text: w.text,
    startFrame: secondsToFrames(w.startSeconds, fps),
    endFrame: secondsToFrames(w.endSeconds, fps),
  }));
```

**`calculateMetadata`** — use when duration depends on the props (e.g. the last word's `endFrame`):

```tsx
import type { CalculateMetadataFunction } from 'remotion';
import type { VideoProps } from './schema';

export const calculateMetadata: CalculateMetadataFunction<VideoProps> = ({ props }) => {
  const last = props.words[props.words.length - 1];
  // Clamp to ≥ 1: Lambda rejects 0-frame compositions with an opaque error,
  // so the lesser evil is over-rendering one frame.
  const durationInFrames = Math.max(1, (last?.endFrame ?? 0) + 1);
  return { durationInFrames };
};
```

Stacked silent corrections (e.g. `secondsToFrames` rounding to 0, then `Math.max(1, …)` clamping) can hide upstream input bugs. Validate at the schema boundary first; clamp only what genuinely belongs to the render-time contract.

There is no portable env-var signal (no `REMOTION_STRICT_METADATA` or equivalent) that survives the CLI → Lambda boundary. If you want a "metadata is mandatory" guarantee, encode it inside `calculateMetadata` itself — throw on missing required props.

**`getInputProps` fallback:**

```tsx
import { getInputProps } from 'remotion';
import type { VideoProps } from './schema';

const defaults: VideoProps = {
  titleText: 'Static Default Title',
  audioUrl: 'https://cdn.example.com/fallback.mp3',
  words: [{ text: 'Hello', startFrame: 0, endFrame: 15 }],
};

export const VideoTimelineWithInput: React.FC = () => {
  const props = { ...defaults, ...(getInputProps() as Partial<VideoProps>) };
  return <VideoTimeline {...props} />;
};
```

### 4. Render via Headless CLI

**Local rendering:**

```bash
# JSON props file
npx remotion render DynamicVideo out.mp4 --props=assets.json

# Inline JSON (escape shell quoting per platform)
npx remotion render DynamicVideo out.mp4 \
  --props='{"titleText":"Hello AI","audioUrl":"https://cdn.example.com/speech.mp3","words":[{"text":"hi","startFrame":0,"endFrame":15}]}'

# Windows absolute paths (PowerShell)
npx remotion render DynamicVideo ~\output.mp4 --props=~\assets.json
```

**Programmatic bundle and render:**

`bundle()` is async. In a CommonJS file (`"type": "commonjs"` or no `type` in `package.json`), wrap in an `async function`. In an ESM file (`"type": "module"`), top-level `await` is allowed and the wrapper is unnecessary — don't copy the CJS form into ESM out of habit.

```ts
import { bundle } from '@remotion/bundler';
import { renderMedia, selectComposition } from '@remotion/renderer';
import path from 'node:path';

// CJS-compatible form. In ESM, drop the wrapper and `await` at top level.
async function renderOne() {
  const inputProps = {
    titleText: 'Hello AI',
    audioUrl: 'https://cdn.example.com/speech.mp3',
    words: [{ text: 'hi', startFrame: 0, endFrame: 15 }],
  };
  const serveUrl = await bundle({ entryPoint: path.resolve('src/index.ts') });
  const composition = await selectComposition({ serveUrl, id: 'DynamicVideo', inputProps });
  await renderMedia({
    serveUrl,
    composition,
    codec: 'h264',
    outputLocation: 'out.mp4',
    inputProps,
  });
}
```

**`--jpeg-quality`:** Affects intermediate frame quality only on codec paths that round-trip through JPEG. Codecs that bypass JPEG intermediates ignore the flag silently. Verify the effect on your codec by toggling and inspecting output size before treating it as a quality knob.

**`delayRender` handles:** `delayRender(label)` returns a handle that you release with `continueRender(handle)` once async work finishes. The `label` string appears in timeout error messages. Keep labels short and specific (`delayRender('font:Inter')`, not a multi-line description) — long labels are truncated in CLI output, making timeouts hard to attribute.

### 5. Handle Remote Asset Hazards

Three distinct threat models. Mitigating one does **not** mitigate the others.

**a. CORS (browser-side, preview/Studio):**
- The Remotion preview runs in a browser; cross-origin assets need permissive `Access-Control-Allow-Origin` headers, or the preview shows a blank frame while CLI renders work.
- Server-side renders (CLI, Lambda) are not subject to CORS — if symptoms appear only in Studio, CORS is the prime suspect.

**b. Signed URLs (asset auth):**
- Most CDNs sign URLs with a short TTL. A signed URL captured at bundle time can expire before render starts on a long job.
- Re-sign just-in-time inside `calculateMetadata`, or pass a server-side proxy URL that re-signs on each fetch.

**c. SSRF (server-side request forgery):**
The schema in §3 enforces `https:` + host allow-list. This is the minimum bar and does **not** catch:
- **IDN / punycode** — `xn--…` hosts may canonicalize to a trusted name after registration.
- **IPv6 literals** — `[::1]`, `[fe80::1]` bypass string matching against IPv4-shaped allow-lists.
- **Userinfo** — `https://attacker.example@trusted.example/…` yields `hostname = trusted.example` under WHATWG `URL`; legacy parsers and frontends disagree.
- **Trailing dot** — `trusted.example.` and `trusted.example` resolve identically under DNS but are unequal as strings.
- **Parser divergence** — Node's WHATWG `URL`, Node's legacy `url`, and the browser disagree on edge cases; the same input can yield different `hostname` values in different layers.

For untrusted input, validate with a dedicated SSRF library that combines a hardened URL parser with a post-DNS-resolution IP allow-list. String checks are a defense-in-depth bonus, not a stand-alone control.

### 6. Load Fonts Correctly

`@remotion/google-fonts` exposes `loadFont()`, which returns a promise. If called at module scope, the promise is created the moment the module is first imported.

- **Remotion Studio / CLI render** — works. Remotion's webpack runtime imports the module once, and `delayRender`-wrapped loads block the first frame.
- **Any environment without a real browser font stack** — Storybook, Vitest, Jest with jsdom, Playwright component tests, SSR snapshots: `loadFont` may resolve before the DOM has applied `@font-face` rules, causing a flash of fallback or a hang on `document.fonts.ready`. The fix differs per harness — explicit `await` in `beforeAll`, mocking the module, or skipping the call entirely in test mode.

Treat module-scope `loadFont()` as a Remotion-runtime contract. Outside Remotion, call it explicitly from the place that knows the rendering surface is ready.

### 7. Render on AWS Lambda

**Version compatibility:** The deployed Lambda function bundles its own `@remotion/lambda` runtime. The client `@remotion/lambda` you invoke from must match the deployed function on **major and minor** version. Patches may drift:

- Client `4.0.180` against function `4.0.175`: OK.
- Client `4.0.x` against function `4.1.x`: not OK — redeploy.
- Client `4.x` against function `5.x`: not OK — redeploy and re-test.

`@remotion/lambda deploy-function` is idempotent on identical bundle hashes; redeploying after a minor bump is cheap and worth doing as a release-checklist habit.

**Fonts on Lambda:** The base Lambda image ships with a minimal font set — almost none of the fonts your CSS actually names will resolve. Two escape hatches:

- **Custom Docker image** — extend the Remotion Lambda image, install fonts into `/usr/share/fonts/`, run `fc-cache -f`, and pass the resulting image via `imageUri` in `deployFunction`. Most reliable.
- **Lambda layer** — package fonts as a layer; attach to the function. Configure fontconfig to see the layer-mounted path. `FONTCONFIG_PATH` points to a directory containing a `fonts.conf` file (not to the font files themselves); ship a custom `fonts.conf` in the layer that registers the font directory. Verify against the current Remotion Lambda image layout before relying on it — these paths have shifted across 4.x releases.

If your design tolerates it, fetching `@remotion/google-fonts` over HTTPS from inside the render still works without either escape hatch.

**Audio drift (Studio vs Lambda):** Studio audio runs through the browser's WebAudio scheduler, which is sample-accurate within the page. Lambda decodes and re-encodes audio through ffmpeg, which performs its own resampling and quantizes start offsets toward frame boundaries. Symptom: sync that looks tight in Studio drifts a few frames late on Lambda output, worse on long compositions.

Mitigation: render a short Lambda test before iterating in Studio when sync is load-bearing, and align audio cuts to whole-frame timestamps in the schema rather than sub-frame floats.

### 8. Produce Alpha / Transparent Output

For transparency, three things must change together — codec, pixel format, and composition background:

- **Codec + pixel format** — `prores` profile `4444` (mov container), or `vp8` / `vp9` (webm container) with `pixelFormat: 'yuva420p'`. h.264 has no alpha channel; output composites onto black silently.
- **Composition background** — a non-transparent root `<div>` produces opaque output regardless of codec. Remove any `backgroundColor` from the outer container (or set it to `'transparent'`) and clear any default white from your CSS reset. The `<Composition>` itself has no background color to set; the root component's styles are what get baked in.
- **Still frames** — `imageFormat: 'png'` for `renderStill`; JPEG has no alpha.

Verify with a viewer that reveals transparency (checkerboard background). Most image viewers show white for transparent pixels, hiding bugs.

---

## Pitfalls

1. **Odd dimensions → ffmpeg failure:** `width` and `height` must both be even for h.264/h.265. The error surfaces at render time, not at composition registration. Always check dimensions in `<Composition>`.

2. **`fps` vs `durationInFrames` confusion:** The number `30` can be either. Always multiply by `fps` from `useVideoConfig()` for seconds→frames conversion; never use a literal `30` in duration math unless you mean "frame index 30."

3. **Inclusive frame range off-by-one:** `startFrame: 10, endFrame: 25` = 16 frames, not 15. Any helper accepting `(start, end)` must preserve inclusive semantics.

4. **Trailing `<TransitionSeries.Transition>`:** Placed after the last `<TransitionSeries.Sequence>`, it is a silent no-op that wastes frames in timeline math. Transitions go **between** sequences only.

5. **`spring` with `durationInFrames` set:** Overrides physics; spring won't feel springy. Check whether `durationInFrames` was accidentally passed.

6. **`refine` firing on off-frame words:** `refine` validates static invariants at parse time. It should not fire when the current frame is outside a word's range — that's runtime gating via inline `null` returns, not a validation failure.

7. **Stacked silent corrections hiding bugs:** `secondsToFrames` rounding to 0, then `Math.max(1, …)` clamping, can hide upstream input bugs. Validate at the schema boundary first; clamp only render-time contract values.

8. **No portable `REMOTION_STRICT_METADATA` env var:** Does not survive the CLI → Lambda boundary. Encode mandatory-metadata guarantees inside `calculateMetadata` by throwing on missing props.

9. **CJS vs ESM `bundle()` wrapper:** In ESM (`"type": "module"`), top-level `await` is allowed — don't copy the CJS `async function` wrapper out of habit.

10. **`--jpeg-quality` ignored on some codecs:** Only affects codec paths that round-trip through JPEG intermediates. Verify by toggling and inspecting output size.

11. **`delayRender` label truncation:** Long labels are truncated in CLI timeout output. Keep them short and specific (`delayRender('font:Inter')`).

12. **CORS only in Studio:** CLI and Lambda are not subject to CORS. If a blank frame appears only in Studio preview, CORS is the prime suspect — not the render pipeline.

13. **Signed URL expiry during long renders:** A signed URL captured at bundle time can expire before render starts. Re-sign just-in-time in `calculateMetadata`.

14. **SSRF string checks insufficient:** Host allow-list does not catch IDN/punycode, IPv6 literals, userinfo tricks, trailing dots, or parser divergence. Use a dedicated SSRF library for untrusted input.

15. **Module-scope `loadFont()` outside Remotion:** Resolves before DOM applies `@font-face` in Storybook/Vitest/Jest/jsdom/Playwright/SSR. Use explicit `await` in `beforeAll`, mock, or skip in test mode.

16. **Lambda client/function version mismatch:** Major and minor must match. Patches can drift. Redeploy after any minor bump.

17. **Lambda missing fonts:** Base Lambda image has minimal fonts. Use custom Docker image (`imageUri` in `deployFunction`) or Lambda layer with custom `fonts.conf`. `FONTCONFIG_PATH` points to a directory containing `fonts.conf`, not to font files.

18. **Audio drift Studio vs Lambda:** ffmpeg resampling quantizes start offsets toward frame boundaries. Align audio cuts to whole-frame timestamps; render a short Lambda test before iterating in Studio.

19. **Transparent output silently composited on black:** h.264 has no alpha. Must use ProRes 4444 (mov) or VP8/VP9 (webm) with `pixelFormat: 'yuva420p'`, AND remove `backgroundColor` from root container. Most image viewers show white for transparent pixels — verify with a checkerboard-revealing viewer.

20. **`durationInFrames` of 0 on Lambda:** Lambda rejects 0-frame compositions with an opaque error. Clamp to `Math.max(1, …)` or add `z.number().int().positive()` to the schema.

---

## Verification

1. **Validate schema parses without error:**

```bash
npx tsx -e "import { videoSchema } from './src/schema'; videoSchema.parse({ titleText: 'Test', audioUrl: 'https://cdn.example.com/a.mp3', words: [{ text: 'hi', startFrame: 0, endFrame: 15 }] }); console.log('schema OK')"
```

Expected output: `schema OK`

2. **Verify dimensions are even (PowerShell):**

```powershell
# Check that width and height are both even
$w = 1080; $h = 1920
if ($w % 2 -eq 0 -and $h % 2 -eq 0) { Write-Host "Dimensions OK: ${w}x${h}" } else { Write-Host "FAIL: odd dimensions" }
```

Expected output: `Dimensions OK: 1080x1920`

3. **Local CLI render smoke test:**

```bash
npx remotion render DynamicVideo out.mp4 --props=assets.json
```

Expected: `out.mp4` created in the working directory with no ffmpeg errors.

4. **Verify Lambda client/function version match:**

```bash
npx remotion lambda functions info
```

Check that the deployed function's version matches your installed `@remotion/lambda` on major.minor.

5. **Verify transparent output has alpha:**

```bash
# Render with ProRes 4444
npx remotion render DynamicVideo out.mov --codec=prores --pixel-format=yuva420p
# Inspect with ffprobe
ffprobe -v error -select_streams v:0 -show_entries stream=pix_fmt out.mov
```

Expected: `pix_fmt=yuva444p10le` (or similar alpha-capable format).

6. **Verify font loaded on Lambda:**

```bash
# After deploying with custom image or layer, render a test frame
npx remotion lambda render DynamicVideo --frame=0 --image-format=png out.png
# Inspect out.png for correct font rendering
```

7. **Check audio sync drift:**

```bash
# Render a short Lambda test (first 5 seconds = 150 frames at 30fps)
npx remotion lambda render DynamicVideo --frames=0-150 test-sync.mp4
# Compare audio onset vs subtitle onset frame-by-frame
```

---

## Related skills

- Audio beat coordinates feeding Remotion configs → `audio-reactive-music-video`
- Character assets and styled frames displayed inside compositions → `creative-prompt-engineering`
