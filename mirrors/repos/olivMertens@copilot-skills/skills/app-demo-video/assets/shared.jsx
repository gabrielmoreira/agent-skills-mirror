// Shared constants and the cinematic entrance hook used by every scene.
// Palette is a neutral corporate dark theme; override the hex values to match
// a brand identity. Nothing here is project-specific.
import { useCurrentFrame, spring, interpolate, OffthreadVideo } from "remotion";

export const NAVY_DARK = "#0a1230"; // deep background
export const NAVY = "#0f183d";      // gradient inner
export const TEAL = "#2dd4bf";      // accent 1 (kicker, pills, badges)
export const AMBER = "#e8a84a";     // accent 2 (secondary pills)

// Spring-based entrance: scale 1.18 -> 1, blur 10 -> 0, opacity 0 -> 1 over
// ~12 frames, starting at `delayFrames`. Stagger delays per element (kicker 0,
// headline 6, subtitle 12, pills 18, card 24) for a layered reveal.
export function useCinematicIn(delayFrames, fps) {
  const frame = useCurrentFrame();
  const local = Math.max(0, frame - delayFrames);
  const s = spring({ frame: local, fps, config: { damping: 200, mass: 0.9, stiffness: 90 } });
  const scale = interpolate(s, [0, 1], [1.18, 1]);
  const blur = interpolate(s, [0, 1], [10, 0]);
  const opacity = interpolate(local, [0, 12], [0, 1], { extrapolateRight: "clamp" });
  return { transform: `scale(${scale})`, filter: `blur(${blur}px)`, opacity };
}

// Crops a fixed rect (in the source video's native pixel space) out of broll
// footage by scaling the whole video so the crop rect fills the container,
// then clipping with overflow:hidden. Avoids ffmpeg filter math; WYSIWYG in the
// browser. `crop` = [srcWidth, srcHeight, cropX, cropY] measured against the
// FIXED capture resolution (default assumes 1600x1000 — change SRC_W/SRC_H).
const SRC_W = 1600;
const SRC_H = 1000;
export function CroppedVideo({ src, crop, containerWidth, startFromSeconds, fps }) {
  const [vw, vh, cx, cy] = crop;
  const containerHeight = (containerWidth * vh) / vw;
  const scale = containerWidth / vw;
  const videoW = SRC_W * scale;
  const videoH = SRC_H * scale;
  const offsetX = -cx * scale;
  const offsetY = -cy * scale;
  return (
    <div
      style={{
        width: containerWidth,
        height: containerHeight,
        overflow: "hidden",
        position: "relative",
        borderRadius: 10,
        boxShadow: "0 30px 70px rgba(0,0,0,0.55)",
      }}
    >
      <OffthreadVideo
        src={src}
        startFrom={Math.round(startFromSeconds * fps)}
        muted
        style={{ position: "absolute", left: offsetX, top: offsetY, width: videoW, height: videoH }}
      />
    </div>
  );
}
