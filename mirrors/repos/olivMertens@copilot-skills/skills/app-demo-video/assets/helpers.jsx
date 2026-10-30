// Reusable animation helpers and UI-chrome primitives shared across scenes.
// All are project-agnostic; none reference a specific product or brand.
import { useCurrentFrame, useVideoConfig, interpolate, spring } from "remotion";
import { TEAL, NAVY_DARK } from "./shared";

// Continuous slow "Ken Burns" zoom+drift applied to a screenshot CARD only
// (never to KPI text/numbers, which must stay legible). Scale climbs gently
// across the scene; a tiny horizontal drift adds camera-movement feel.
// `startFrame` lets the zoom begin exactly when the card fades in.
// Pass the SCENE's own duration as `durationInFrames` (inside a Series.Sequence,
// useVideoConfig().durationInFrames returns the WHOLE composition length).
export function useKenBurns(durationInFrames, fromScale = 1, toScale = 1.045, driftPx = 8, startFrame = 0) {
  const frame = useCurrentFrame();
  const local = Math.max(0, frame - startFrame);
  const span = Math.max(1, durationInFrames - startFrame);
  const scale = interpolate(local, [0, span], [fromScale, toScale], { extrapolateRight: "clamp" });
  const translateX = interpolate(local, [0, span], [-driftPx / 2, driftPx / 2], { extrapolateRight: "clamp" });
  return { transform: `scale(${scale}) translateX(${translateX}px)` };
}

// Spring count-up: animates a number from `from` to `to` between start/end
// frames so a KPI lands exactly when the narration says it, with a light
// overshoot-then-settle (never a blur/zoom on the digits themselves).
export function useCountUp(from, to, startFrame, endFrame, fps, decimals = 0) {
  const frame = useCurrentFrame();
  const local = Math.max(0, Math.min(1, (frame - startFrame) / Math.max(1, endFrame - startFrame)));
  const s = spring({ frame: local * (endFrame - startFrame), fps, config: { damping: 18, mass: 0.6, stiffness: 120 } });
  const value = interpolate(s, [0, 1], [from, to], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  return decimals > 0 ? value.toFixed(decimals) : Math.round(value);
}

// A glowing highlight ring that moves from A to B over a frame window, to draw
// the eye to the exact figure in a screenshot the narration is describing.
// Coordinates are in the local (unscaled) pixel space of the overlaid image.
export function SpotlightRing({ from, to, startFrame, endFrame, size = 92, color = TEAL }) {
  const frame = useCurrentFrame();
  const local = Math.max(0, Math.min(1, (frame - startFrame) / Math.max(1, endFrame - startFrame)));
  const s = spring({ frame: local * (endFrame - startFrame), fps: 30, config: { damping: 20, mass: 0.7, stiffness: 110 } });
  const x = interpolate(s, [0, 1], [from[0], to[0]]);
  const y = interpolate(s, [0, 1], [from[1], to[1]]);
  const opacity = interpolate(frame, [startFrame, startFrame + 6, endFrame - 6, endFrame], [0, 1, 1, 0], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  const pulse = 1 + 0.06 * Math.sin(frame / 5);
  return (
    <div
      style={{
        position: "absolute",
        left: x - size / 2,
        top: y - size / 2,
        width: size,
        height: size,
        borderRadius: "50%",
        border: `3px solid ${color}`,
        boxShadow: `0 0 0 4px rgba(45,212,191,0.15), 0 0 24px 4px ${color}`,
        opacity,
        transform: `scale(${pulse})`,
        pointerEvents: "none",
      }}
    />
  );
}

// A UI-chrome "processing" progress bar (rounded pill, accent fill, shimmer
// sweep + live percentage) to visualize the product actually working — ingesting
// a document, computing a score — rather than cutting straight to the result.
// Fills 0->100% between start/end, then fades out shortly after completion.
export function LoadingBar({ startFrame, endFrame, label = "Processing…", width = 420, fadeOutFrames = 18 }) {
  const frame = useCurrentFrame();
  const local = Math.max(0, Math.min(1, (frame - startFrame) / Math.max(1, endFrame - startFrame)));
  const pct = Math.round(local * 100);
  const opacity = interpolate(frame, [startFrame - 6, startFrame, endFrame, endFrame + fadeOutFrames], [0, 1, 1, 0], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  const shimmerX = ((frame - startFrame) * 14) % (width + 120) - 120;
  return (
    <div style={{ opacity, width, fontFamily: "Segoe UI, sans-serif" }}>
      <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 8 }}>
        <span style={{ fontSize: 18, fontWeight: 600, color: "#c8d6e6" }}>{label}</span>
        <span style={{ fontSize: 18, fontWeight: 700, color: TEAL, fontVariantNumeric: "tabular-nums" }}>{pct}%</span>
      </div>
      <div style={{ position: "relative", width, height: 14, borderRadius: 7, background: "rgba(255,255,255,0.12)", overflow: "hidden", boxShadow: "inset 0 1px 3px rgba(0,0,0,0.4)" }}>
        <div style={{ position: "absolute", left: 0, top: 0, bottom: 0, width: `${pct}%`, borderRadius: 7, background: `linear-gradient(90deg, ${TEAL}, #7ff0e0)`, boxShadow: `0 0 14px 2px rgba(45,212,191,0.55)`, overflow: "hidden" }}>
          <div style={{ position: "absolute", top: 0, bottom: 0, left: shimmerX, width: 90, background: "linear-gradient(90deg, rgba(255,255,255,0) 0%, rgba(255,255,255,0.55) 50%, rgba(255,255,255,0) 100%)" }} />
        </div>
      </div>
    </div>
  );
}

// Optional four-square mark + wordmark, drawn purely in CSS (no external asset).
// Defaults to the Microsoft brand colors/word; pass `colors` and `word` to
// render a different identity, or omit this component entirely.
export function BrandLogo({ scale = 1, opacity = 1, colors = ["#F25022", "#7FBA00", "#00A4EF", "#FFB900"], word = "Microsoft" }) {
  const sq = 22 * scale;
  const gap = 3 * scale;
  return (
    <div style={{ display: "flex", alignItems: "center", gap: 14 * scale, opacity }}>
      <div style={{ display: "grid", gridTemplateColumns: `${sq}px ${sq}px`, gridTemplateRows: `${sq}px ${sq}px`, gap: `${gap}px` }}>
        {colors.map((c, i) => (
          <div key={i} style={{ width: sq, height: sq, background: c }} />
        ))}
      </div>
      {word ? (
        <span style={{ fontFamily: "Segoe UI, sans-serif", fontWeight: 600, fontSize: 26 * scale, color: "white", letterSpacing: 0.2 }}>
          {word}
        </span>
      ) : null}
    </div>
  );
}
