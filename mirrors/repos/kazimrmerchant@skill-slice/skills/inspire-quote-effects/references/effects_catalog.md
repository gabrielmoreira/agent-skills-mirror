# Effects catalog (Remotion)

Implement under pack `remotion/src/components/` or import from `quotes/_shared/remotion-effects/`.

## TransitionSeries (required for multi-beat)

```tsx
import {TransitionSeries, linearTiming} from '@remotion/transitions';
import {fade} from '@remotion/transitions/fade';
import {slide} from '@remotion/transitions/slide';

<TransitionSeries>
  <TransitionSeries.Sequence durationInFrames={90}>{/* beat A */}</TransitionSeries.Sequence>
  <TransitionSeries.Transition presentation={fade()} timing={linearTiming({durationInFrames: 12})} />
  <TransitionSeries.Sequence durationInFrames={90}>{/* beat B */}</TransitionSeries.Sequence>
</TransitionSeries>
```

Install: `pnpm add @remotion/transitions@<same-as-remotion>` (match 4.0.503+).  
Custom: FilmBurn / Glitch / PunchZoom from spider-man `SceneEffects` as presentations or Sequence-local overlays **in addition to** series transitions — not instead of.

## ArchiveVideo

Muted looping cover — **OffthreadVideo + Loop** (not HTML5 `<Video loop>`).

```tsx
<ArchiveVideo src="archive/clips/forge_billie_01.mp4" durationFrames={n} zoom={1.06} clipDurationFrames={120} />
```

## KineticQuote

Word-by-word spring reveal; `powerWord` accent (`#E8C56A`).  
`variant: 'cascade' | 'hold' | 'whisper'`.  
**Chunk** long copy across multiple Sequences.

## CaptionWordReveal

VO-timed karaoke (`words.json`). Prefer Shorts + Whisper. Companion: `kinetic-typography-and-captions` for ASS burn path.

## SceneEffects

`GlitchOverlay`, `FilmBurnOverlay`, `PunchZoomStill`, `LightLeakOverlay`, `VignettePulse`, `SpotlightReveal`.

## ArchiveStamp / PhotoWall / ParticleRise / PortraitStill / SplitCompare

See matrix for when to use. PhotoWall needs **valid** JPEG/PNG (reject HTML downloads).

## GPU render

```powershell
pnpm run ensure:nvenc
pnpm exec remotion render ForgeHealLong ../final/NAME_vN.mp4 `
  --codec h264 --video-bitrate 12M --audio-bitrate 192k `
  --concurrency 6 --gl angle --hardware-acceleration required
```

Proof: `Encoder: h264_nvenc, hardware accelerated: true`  
Then: `/reviewresults`.
