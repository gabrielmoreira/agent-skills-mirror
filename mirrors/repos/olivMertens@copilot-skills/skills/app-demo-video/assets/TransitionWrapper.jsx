// Cinematic crossfade transition wrapper. Each scene fades/zooms/blurs in over
// the first TRANSITION_FRAMES and out over the last TRANSITION_FRAMES of its own
// duration. When two scenes' Series.Sequence overlap by TRANSITION_FRAMES (via a
// negative `offset`), the outgoing fade-out and incoming fade-in play together,
// producing a soft crossfade + push-in "camera zoom" between scenes with no
// external dependency. Keep the overlap modest: ~10 frames blends cleanly;
// 15+ frames produces visible "double-exposure" garble between different layouts.
import { AbsoluteFill, useCurrentFrame, interpolate } from "remotion";

const TRANSITION_FRAMES = 10;

export function TransitionWrapper({ children, durationInFrames }) {
  const frame = useCurrentFrame();

  const inOpacity = interpolate(frame, [0, TRANSITION_FRAMES], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  const outOpacity = interpolate(
    frame,
    [durationInFrames - TRANSITION_FRAMES, durationInFrames],
    [1, 0],
    { extrapolateLeft: "clamp", extrapolateRight: "clamp" }
  );
  const opacity = Math.min(inOpacity, outOpacity);

  const inScale = interpolate(frame, [0, TRANSITION_FRAMES], [1.06, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  const outScale = interpolate(
    frame,
    [durationInFrames - TRANSITION_FRAMES, durationInFrames],
    [1, 1.06],
    { extrapolateLeft: "clamp", extrapolateRight: "clamp" }
  );
  const scale = frame < durationInFrames / 2 ? inScale : outScale;

  const inBlur = interpolate(frame, [0, TRANSITION_FRAMES], [6, 0], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  const outBlur = interpolate(
    frame,
    [durationInFrames - TRANSITION_FRAMES, durationInFrames],
    [0, 6],
    { extrapolateLeft: "clamp", extrapolateRight: "clamp" }
  );
  const blur = Math.max(inBlur, outBlur);

  return (
    <AbsoluteFill style={{ opacity, transform: `scale(${scale})`, filter: `blur(${blur}px)` }}>
      {children}
    </AbsoluteFill>
  );
}

export const TRANSITION_OVERLAP = TRANSITION_FRAMES;
