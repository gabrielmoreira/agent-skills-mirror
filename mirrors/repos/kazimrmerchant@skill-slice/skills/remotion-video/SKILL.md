---
name: remotion-video
description: "Builds Remotion videos in React: compositions, useCurrentFrame, interpolate/spring, Sequence, and npx remotion render to MP4/WebM. Use when the user wants programmatic Remotion video, Remotion Studio, or frame-based React animation. Not for Premiere/FFmpeg timeline edits or AI video models (Sora/Veo). Never assume this folder ships a references pack."
version: 1.0.1
recommended_skills:
  - react-frontend
  - animation-motion
---

When this skill is activated, always start your first response with the 🎬 emoji.

## Overview

Remotion is a framework for creating videos programmatically using React. Instead of timeline-based editors, you write compositions as React components where every frame is a pure function of the current frame number. This gives you the full power of TypeScript, npm packages, and component-based architecture for building videos — from animated explainers and social media clips to data-driven visualizations and personalized video at scale.

This skill covers project setup, composition structure, frame-based animations with `interpolate` and `spring`, scene sequencing, asset management, audio integration, parametrized videos with Zod schemas, and rendering to MP4/WebM via CLI or programmatic APIs.

**Sources verified (2026-05-31):**
- Remotion docs: https://www.remotion.dev/docs/
- W3C WCAG 2.2: https://www.w3.org/TR/WCAG22/
- Apple HIG: https://developer.apple.com/design/human-interface-guidelines/
- Material Design 3: https://m3.material.io/

## When to Use

Trigger this skill when the user:
- Wants to create a video programmatically using React/TypeScript
- Asks about Remotion compositions, `useCurrentFrame`, or `useVideoConfig`
- Needs to animate text, elements, or transitions between scenes
- Wants to render a video to MP4, WebM, or GIF from code
- Asks about spring animations, `interpolate`, or frame-based timing
- Wants to set up a new Remotion project from scratch
- Wants to add audio, images, or fonts to a Remotion video
- Asks about parametrized/data-driven video generation
- Needs to configure Remotion Studio for previewing compositions
- Needs programmatic, deterministic, reproducible video output (not AI synthetic footage)

Do NOT trigger this skill for:
- General React questions unrelated to video creation — use React skills
- Video editing with traditional timeline tools (Premiere, DaVinci, FFmpeg CLI)
- CSS animations for web pages — use animation/motion-design skills
- Video playback or streaming in web apps — use media player skills
- AI video model generation (Sora, Veo, Runway) — use those skills for synthetic shots, then assemble with Remotion if deterministic overlays are needed

## Prerequisites

- Node.js 18+ and npm
- Basic React and TypeScript familiarity
- For rendering: FFmpeg is bundled with Remotion's renderer; no separate install needed for local rendering
- For cloud/Lambda rendering: follow current Remotion docs (https://www.remotion.dev/docs/lambda). This folder does not ship extra guides.

## Key Principles

1. **Every frame is a pure function** — A Remotion component receives the current frame via `useCurrentFrame()` and must render deterministically for that frame. No side effects, no randomness without seeds, no reliance on wall-clock time. The same frame number must always produce the same visual output.

2. **Compositions are the unit of video** — Each `<Composition>` defines a video with explicit dimensions (width, height), frame rate (fps), and duration (durationInFrames). Think of compositions as "pages" in your project — one per video variant or scene that can be rendered independently.

3. **Interpolate for everything** — The `interpolate()` function maps frame numbers to any numeric value (opacity, position, scale, color channels). Combined with `extrapolateRight: 'clamp'`, it is the workhorse for all animations. Use `spring()` when you need physics-based easing.

4. **Sequence for time offsets** — Use `<Sequence from={frame}>` to delay when children start appearing, and `<Series>` to play children one after another. Never use `setTimeout` or manual frame math for sequencing — the declarative primitives handle it correctly across preview and render.

5. **Assets are static, data is dynamic** — Put images, fonts, and audio files in the `public/` folder and reference them with `staticFile()`. For dynamic data (API responses, database records), use `delayRender()` / `continueRender()` to pause rendering until the data is loaded.

## Procedure

### 1. Set Up a New Remotion Project

```bash
npx create-video@latest
```

This scaffolds a project with TypeScript, a sample composition, and Remotion Studio configured. The project structure:

```
my-video/
  src/
    Root.tsx          # Registers all compositions
    MyComp.tsx        # Your first composition component
  public/             # Static assets (images, fonts, audio)
  remotion.config.ts  # Remotion configuration
  package.json
```

Start the preview studio:

```bash
npx remotion studio
```

### 2. Register a Composition

Every Remotion project has a root file that registers compositions:

```tsx
import { Composition } from 'remotion';
import { MyVideo } from './MyVideo';

export const RemotionRoot: React.FC = () => {
  return (
    <Composition
      id="MyVideo"
      component={MyVideo}
      durationInFrames={150}
      fps={30}
      width={1920}
      height={1080}
    />
  );
};
```

**HARD RULE:** Composition dimensions must be even numbers. Video codecs (H.264, VP8) require even width and height. Remotion will throw an error if you use odd dimensions like 1921x1081. Always use even pixel values (1920x1080, 1280x720, etc.).

### 3. Frame-Based Timing

All timing in Remotion is expressed in frames, not seconds:
- Seconds to frames: `seconds * fps`
- Frames to seconds: `frame / fps`

At 30 fps, a 5-second video is 150 frames. Frame 0 is the first frame.

**HARD RULE:** Never hardcode fps in frame calculations. Always use `useVideoConfig().fps` to derive timing so compositions remain correct when fps changes.

### 4. Create a Basic Composition with useCurrentFrame

```tsx
import { AbsoluteFill, useCurrentFrame, useVideoConfig, interpolate } from 'remotion';

export const FadeInText: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const opacity = interpolate(frame, [0, 30], [0, 1], {
    extrapolateRight: 'clamp',
  });

  const translateY = interpolate(frame, [0, 30], [20, 0], {
    extrapolateRight: 'clamp',
  });

  return (
    <AbsoluteFill
      style={{
        justifyContent: 'center',
        alignItems: 'center',
        backgroundColor: '#0f0f0f',
      }}
    >
      <h1
        style={{
          fontSize: 80,
          color: 'white',
          opacity,
          transform: `translateY(${translateY}px)`,
        }}
      >
        Hello Remotion
      </h1>
    </AbsoluteFill>
  );
};
```

### 5. Animate Text Word by Word

Split text into words and stagger each word's appearance using `<Sequence>`:

```tsx
import { AbsoluteFill, Sequence, useCurrentFrame, interpolate } from 'remotion';

const AnimatedWord: React.FC<{ children: string }> = ({ children }) => {
  const frame = useCurrentFrame();
  const opacity = interpolate(frame, [0, 15], [0, 1], {
    extrapolateRight: 'clamp',
  });
  const translateY = interpolate(frame, [0, 15], [10, 0], {
    extrapolateRight: 'clamp',
  });

  return (
    <span
      style={{
        display: 'inline-block',
        opacity,
        transform: `translateY(${translateY}px)`,
        marginRight: 12,
      }}
    >
      {children}
    </span>
  );
};

export const WordByWord: React.FC<{ text: string }> = ({ text }) => {
  const words = text.split(' ');

  return (
    <AbsoluteFill
      style={{
        justifyContent: 'center',
        alignItems: 'center',
        backgroundColor: '#1a1a2e',
        flexWrap: 'wrap',
        padding: 100,
      }}
    >
      {words.map((word, i) => (
        <Sequence key={i} from={i * 8}>
          <AnimatedWord>{word}</AnimatedWord>
        </Sequence>
      ))}
    </AbsoluteFill>
  );
};
```

### 6. Element Animations with spring

Use `spring()` for physics-based animations that feel natural:

```tsx
import { AbsoluteFill, useCurrentFrame, useVideoConfig, spring } from 'remotion';

export const SpringCard: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const scale = spring({
    frame,
    fps,
    config: { damping: 200, stiffness: 100, mass: 0.5 },
  });

  const slideUp = spring({
    frame: frame - 10,
    fps,
    config: { damping: 12, stiffness: 100 },
  });

  return (
    <AbsoluteFill style={{ justifyContent: 'center', alignItems: 'center', backgroundColor: '#0d1117' }}>
      <div
        style={{
          width: 400,
          height: 250,
          backgroundColor: '#161b22',
          borderRadius: 16,
          transform: `scale(${scale}) translateY(${(1 - slideUp) * 50}px)`,
        }}
      >
        <p style={{ color: 'white', fontSize: 32 }}>Spring Animation</p>
      </div>
    </AbsoluteFill>
  );
};
```

**GOTCHA:** `spring()` starts from frame 0 of its context. When using `spring()` inside a `<Sequence from={60}>`, the frame passed to spring resets to 0 at frame 60 of the parent. If you pass the parent's raw frame, the animation will already be complete. Use `useCurrentFrame()` inside the Sequence child, not a frame from the parent.

### 7. Scene Transitions with Sequence and Series

Use `<Sequence>` for overlapping scenes and `<Series>` for sequential playback:

```tsx
import { AbsoluteFill, Sequence, Series, useCurrentFrame, interpolate } from 'remotion';

const Scene: React.FC<{ color: string; title: string }> = ({ color, title }) => {
  const frame = useCurrentFrame();
  const opacity = interpolate(frame, [0, 20], [0, 1], {
    extrapolateRight: 'clamp',
  });

  return (
    <AbsoluteFill style={{ backgroundColor: color, justifyContent: 'center', alignItems: 'center' }}>
      <h1 style={{ color: 'white', fontSize: 72, opacity }}>{title}</h1>
    </AbsoluteFill>
  );
};

export const MultiScene: React.FC = () => {
  return (
    <AbsoluteFill>
      <Series>
        <Series.Sequence durationInFrames={60}>
          <Scene color="#e63946" title="Scene One" />
        </Series.Sequence>
        <Series.Sequence durationInFrames={60}>
          <Scene color="#457b9d" title="Scene Two" />
        </Series.Sequence>
        <Series.Sequence durationInFrames={60}>
          <Scene color="#2a9d8f" title="Scene Three" />
        </Series.Sequence>
      </Series>
    </AbsoluteFill>
  );
};
```

### 8. Asset Handling (images, fonts, staticFile)

Reference static assets from the `public/` folder using `staticFile()`:

```tsx
import { AbsoluteFill, Img, staticFile } from 'remotion';

export const AssetDemo: React.FC = () => {
  return (
    <AbsoluteFill style={{ justifyContent: 'center', alignItems: 'center' }}>
      <Img
        src={staticFile('logo.png')}
        style={{ width: 300, height: 300 }}
      />
    </AbsoluteFill>
  );
};
```

Load custom fonts with `@remotion/google-fonts` or CSS `@font-face`:

```tsx
import { loadFont } from '@remotion/google-fonts/Inter';

const { fontFamily } = loadFont();

export const FontDemo: React.FC = () => {
  return (
    <AbsoluteFill style={{ justifyContent: 'center', alignItems: 'center' }}>
      <h1 style={{ fontFamily, fontSize: 64, color: 'white' }}>
        Custom Font
      </h1>
    </AbsoluteFill>
  );
};
```

**GOTCHA:** `staticFile()` paths are relative to `public/`. Calling `staticFile('images/logo.png')` looks for `public/images/logo.png`. Using absolute paths or paths outside `public/` will fail silently in preview and error during render. Ensure all assets are in the `public/` directory.

### 9. Audio Integration

Add audio with volume control and timing:

```tsx
import { AbsoluteFill, Audio, Sequence, staticFile, interpolate } from 'remotion';

export const WithAudio: React.FC = () => {
  return (
    <AbsoluteFill style={{ backgroundColor: '#000' }}>
      <Audio
        src={staticFile('background-music.mp3')}
        volume={(f) =>
          interpolate(f, [0, 30, 120, 150], [0, 0.8, 0.8, 0], {
            extrapolateLeft: 'clamp',
            extrapolateRight: 'clamp',
          })
        }
      />
      <Sequence from={15}>
        <Audio src={staticFile('whoosh.mp3')} volume={0.5} />
      </Sequence>
    </AbsoluteFill>
  );
};
```

### 10. Async Data with delayRender

**HARD RULE:** Always call `delayRender()` immediately when async data is needed, and `continueRender()` when ready. If you forget, the render will proceed before data loads, showing empty or broken frames.

```tsx
import { useState, useEffect, useCallback } from 'react';
import { AbsoluteFill, delayRender, continueRender } from 'remotion';

export const DataDriven: React.FC<{ apiUrl: string }> = ({ apiUrl }) => {
  const [data, setData] = useState(null);
  const [handle] = useState(() => delayRender('Loading API data', { timeoutInMilliseconds: 60000 }));

  const fetchData = useCallback(async () => {
    const res = await fetch(apiUrl);
    const json = await res.json();
    setData(json);
    continueRender(handle);
  }, [apiUrl, handle]);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  if (!data) return null;

  return (
    <AbsoluteFill style={{ backgroundColor: '#000', color: 'white' }}>
      <h1>{data.title}</h1>
    </AbsoluteFill>
  );
};
```

**GOTCHA:** `delayRender` has a default 30-second timeout. If your async operation takes longer, the render will abort. Increase the timeout with `delayRender('Loading data', { timeoutInMilliseconds: 60000 })` for slow operations.

### 11. Rendering Videos

Render to MP4 from the command line (Windows PowerShell):

```powershell
# Render default composition
npx remotion render src/index.ts MyVideo out/video.mp4

# Render at 4K resolution
npx remotion render src/index.ts MyVideo out/video.mp4 --width 3840 --height 2160

# Render to WebM
npx remotion render src/index.ts MyVideo out/video.webm --codec vp8

# Render a specific frame range
npx remotion render src/index.ts MyVideo out/video.mp4 --frames 0-90

# Render with custom props
npx remotion render src/index.ts MyVideo out/video.mp4 --props '{\"title\": \"Hello\"}'
```

**HARD RULE:** Use `<OffthreadVideo>` instead of `<Video>` for rendered output. `<Video>` has slower rendering performance due to seeking overhead. `<OffthreadVideo>` is optimized for render-time playback.

For programmatic rendering, Lambda, codecs, and GIF, use the official Remotion docs: https://www.remotion.dev/docs/render and https://www.remotion.dev/docs/lambda. This skill folder does not ship extra guide files.

### 12. Parametrized Videos with Zod Schemas

For data-driven video, define props with Zod schemas in this file's procedure and the Remotion calculateMetadata docs (https://www.remotion.dev/docs/parametrized-rendering).

## Pitfalls

| Mistake | Why It Is Wrong | What to Do Instead |
|---|---|---|
| Using `Math.random()` without a seed | Produces different output per frame during render | Use a deterministic seed or `random()` from Remotion |
| Using `setTimeout` / `setInterval` | Breaks frame-based rendering — timers do not advance per frame | Use `useCurrentFrame()` and frame math for all timing |
| Missing `extrapolateRight: 'clamp'` | Values overshoot beyond the target range on later frames (e.g., opacity goes to 2) | Always add `{ extrapolateRight: 'clamp' }` to `interpolate()` unless you intentionally want extrapolation |
| Hardcoding fps in frame calculations | Breaks when composition fps changes | Use `useVideoConfig().fps` to derive timing |
| Using `<Video>` for rendered output | Slower rendering performance due to seeking overhead | Use `<OffthreadVideo>` for better render performance |
| Forgetting `delayRender()` for async data | Renders before data loads, showing empty/broken frames | Call `delayRender()` immediately, `continueRender()` when ready |
| Inline styles with non-deterministic values | Flickers or inconsistency between preview and render | Derive all style values from the frame number only |
| Giant single composition | Hard to maintain and impossible to render scenes independently | Split into multiple compositions or use `<Series>` for scenes |
| Odd composition dimensions | Video codecs require even width/height; Remotion throws an error | Always use even pixel values (1920x1080, 1280x720, etc.) |
| `staticFile()` with absolute paths | Fails silently in preview, errors during render | Paths are relative to `public/` — keep assets there |
| `delayRender` timeout exceeded (30s default) | Render aborts if async takes too long | Pass `{ timeoutInMilliseconds: 60000 }` for slow operations |
| Passing parent frame to `spring()` inside `<Sequence>` | Animation already complete because spring resets at Sequence start | Use `useCurrentFrame()` inside the Sequence child |

## Verification

1. **Studio preview works:**
   ```bash
   npx remotion studio
   ```
   Open the browser URL shown in terminal. Confirm your composition appears in the left sidebar and plays when you press play.

2. **Single-frame render check (fast smoke test):**
   ```bash
   npx remotion still src/index.ts MyVideo out/frame-0.png --frame 0
   ```
   Verify `out/frame-0.png` exists and shows the expected first-frame visual.

3. **Full render check:**
   ```bash
   npx remotion render src/index.ts MyVideo out/video.mp4
   ```
   Verify the output file exists:
   ```powershell
   Test-Path out/video.mp4
   ```
   Expected output: `True`

4. **Determinism check:** Render the same composition twice and compare file sizes — they should be identical or near-identical. Non-deterministic behavior (random without seed, wall-clock time) will produce different outputs.

5. **Frame range check:** Render a short range to verify timing:
   ```bash
   npx remotion render src/index.ts MyVideo out/clip.mp4 --frames 0-30
   ```
   Verify the clip is approximately 1 second at 30 fps.

## Official docs (no extra files in this folder)

- Animation: https://www.remotion.dev/docs/animating-properties
- Render CLI: https://www.remotion.dev/docs/cli/render
- Parametrized rendering: https://www.remotion.dev/docs/parametrized-rendering

## Related Skills

- **react-frontend** — for general React component patterns, hooks, and TypeScript
- **animation-motion** — for runtime web animation (GSAP, Motion, CSS animations) vs. rendered video
- **ui-ux** — for interface design, accessibility, and visual hierarchy guidance applicable to video overlays and captions
