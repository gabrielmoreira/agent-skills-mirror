# Remotion component stubs (copy into pack)

Place under `remotion/src/components/`:

## Required for /effects multi-beat

1. `@remotion/transitions` `TransitionSeries` in root composition  
2. `ArchiveVideo.tsx` — OffthreadVideo + Loop, muted  
3. `KineticQuote.tsx` — cascade / hold / whisper  
4. `transitions/SceneEffects.tsx` — glitch / burn / punch / leak / vignette / spotlight  
5. `ChannelWatermark.tsx` — Inspire to Rise  

## Optional / when matrix asks

- `CaptionWordReveal.tsx` (needs `words.json`)  
- `PhotoWall.tsx`, `ParticleRise`, `PortraitStill`  
- `SplitCompare.tsx`, `NewspaperHeadline.tsx`  

## Shared folder

`<shorts-workspace>/quotes/_shared/remotion-effects/`

## Sibling pack reference

`quotes/spider-man/remotion/src/components/` — CaptionWordReveal + SceneEffects  

## Never

- Junctions for `public/archive`  
- HTML5 `<Video loop>` as the archive spine (slow + soft)  
- Claiming transitions without `TransitionSeries` (or documented equivalent)
