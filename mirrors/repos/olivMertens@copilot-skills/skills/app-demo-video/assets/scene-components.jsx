// Parameterized scene components implementing the reusable "exec cut" visual
// language: breathing navy gradient background, spring cinematic-in entrance,
// teal kicker + white headline + subtitle + amber pill tags + a screenshot card
// (rounded, drop-shadowed, marginTop:28) with an optional slow Ken Burns zoom
// and an optional accent badge. Feed each scene its copy via props so one file
// serves every language and every app — no per-project component duplication.
import { AbsoluteFill, Img, staticFile, useCurrentFrame, useVideoConfig, interpolate } from "remotion";
import { NAVY, NAVY_DARK, TEAL, AMBER, useCinematicIn } from "./shared";
import { useKenBurns, BrandLogo } from "./helpers";

function BreathingBg() {
  const frame = useCurrentFrame();
  const bgScale = interpolate(frame, [0, 210], [1, 1.07], { extrapolateRight: "clamp" });
  return (
    <>
      <AbsoluteFill style={{ backgroundColor: NAVY }} />
      <AbsoluteFill
        style={{
          transform: `scale(${bgScale})`,
          background: `radial-gradient(1200px 700px at 50% 24%, ${NAVY} 0%, ${NAVY_DARK} 72%)`,
        }}
      />
    </>
  );
}

function Kicker({ label, style }) {
  return (
    <div style={{ ...style, display: "flex", alignItems: "center", gap: 12, border: `2px solid ${TEAL}`, color: TEAL, fontFamily: "Segoe UI, sans-serif", fontWeight: 700, fontSize: 21, letterSpacing: 1.4, padding: "8px 22px", borderRadius: 26 }}>
      <span style={{ width: 9, height: 9, borderRadius: "50%", background: TEAL, boxShadow: `0 0 10px 2px ${TEAL}` }} />
      {label}
    </div>
  );
}

function Pills({ items, style }) {
  return (
    <div style={{ ...style, display: "flex", gap: 14, marginTop: 26, justifyContent: "center", flexWrap: "wrap" }}>
      {(items || []).map((p) => (
        <div key={p} style={{ border: `2px solid ${AMBER}`, color: AMBER, fontFamily: "Segoe UI, sans-serif", fontWeight: 700, fontSize: 18, padding: "7px 18px", borderRadius: 20 }}>
          {p}
        </div>
      ))}
    </div>
  );
}

function Footer({ text }) {
  if (!text) return null;
  return (
    <div style={{ position: "absolute", bottom: 30, left: 0, right: 0, textAlign: "center", color: "#7f92ad", fontFamily: "Segoe UI, sans-serif", fontSize: 17, letterSpacing: 0.3 }}>
      {text}
    </div>
  );
}

// Optional burned-in caption/subtitle band for silent-viewing / social / i18n.
// One line per scene (scenes already map to one narration beat). Keep the text
// short — the spoken line or a trimmed version. Its language is independent of
// the voice, so you can caption a French-narrated video in English, etc.
function CaptionBand({ text }) {
  const frame = useCurrentFrame();
  if (!text) return null;
  const opacity = interpolate(frame, [6, 16], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  return (
    <div style={{ position: "absolute", bottom: 74, left: 0, right: 0, display: "flex", justifyContent: "center", opacity, padding: "0 140px" }}>
      <div style={{ background: "rgba(6,10,26,0.72)", color: "white", fontFamily: "Segoe UI, sans-serif", fontWeight: 600, fontSize: 26, lineHeight: 1.3, textAlign: "center", padding: "12px 26px", borderRadius: 12, maxWidth: 1500 }}>
        {text}
      </div>
    </div>
  );
}

// Screenshot card: rounded, drop-shadowed, subtle Ken Burns that begins when the
// card fades in. `badge` optionally overlays a small accent pill (e.g. "+10%").
// Pass the SCENE's own duration via `dur` for a correct zoom span.
function ShotCard({ img, width, delay, badge, dur }) {
  const { fps, durationInFrames } = useVideoConfig();
  const span = dur || durationInFrames;
  const cardIn = useCinematicIn(delay, fps);
  const kb = useKenBurns(span, 1, 1.045, 8, delay);
  return (
    <div style={{ ...cardIn, marginTop: 28, position: "relative" }}>
      <div style={{ ...kb, borderRadius: 14, overflow: "hidden", boxShadow: "0 30px 70px rgba(0,0,0,0.55)", border: "1px solid rgba(255,255,255,0.06)" }}>
        <Img src={staticFile(img)} style={{ width, display: "block" }} />
      </div>
      {badge ? (
        <div style={{ position: "absolute", top: -18, right: -14, background: TEAL, color: NAVY_DARK, fontFamily: "Segoe UI, sans-serif", fontWeight: 800, fontSize: 20, padding: "8px 18px", borderRadius: 22, boxShadow: `0 8px 24px rgba(45,212,191,0.45)` }}>
          {badge}
        </div>
      ) : null}
    </div>
  );
}

// Content scene: kicker + headline + subtitle + pills + screenshot card.
export const ContentScene = ({ kicker, headline, subtitle, pills, img, imgWidth = 1180, badge, footer, caption, dur }) => {
  const { fps } = useVideoConfig();
  const k = useCinematicIn(0, fps);
  const h = useCinematicIn(6, fps);
  const s = useCinematicIn(12, fps);
  const p = useCinematicIn(18, fps);
  return (
    <AbsoluteFill>
      <BreathingBg />
      <AbsoluteFill style={{ alignItems: "center", justifyContent: "center", flexDirection: "column", padding: "60px 120px 90px" }}>
        <Kicker label={kicker} style={k} />
        <div style={{ ...h, fontFamily: "Segoe UI, sans-serif", fontWeight: 800, fontSize: 46, color: "white", lineHeight: 1.08, textAlign: "center", marginTop: 22 }}>{headline}</div>
        <div style={{ ...s, fontFamily: "Segoe UI, sans-serif", fontWeight: 500, fontSize: 22, color: "#c8d6e6", textAlign: "center", maxWidth: 1240, marginTop: 14, lineHeight: 1.35 }}>{subtitle}</div>
        <Pills items={pills} style={p} />
        {img ? <ShotCard img={img} width={imgWidth} delay={24} badge={badge} dur={dur} /> : null}
      </AbsoluteFill>
      <CaptionBand text={caption} />
      <Footer text={footer} />
    </AbsoluteFill>
  );
};

// Hook scene: optional brand logo top-left, kicker, large title, tagline, pills.
export const HookScene = ({ kicker, title, tagline, pills, footer, caption, logo = true }) => {
  const { fps } = useVideoConfig();
  const lg = useCinematicIn(0, fps);
  const k = useCinematicIn(6, fps);
  const t = useCinematicIn(10, fps);
  const tg = useCinematicIn(15, fps);
  const p = useCinematicIn(20, fps);
  return (
    <AbsoluteFill>
      <BreathingBg />
      {logo ? (
        <div style={{ position: "absolute", top: 46, left: 66, ...lg }}>
          <BrandLogo />
        </div>
      ) : null}
      <AbsoluteFill style={{ alignItems: "center", justifyContent: "center", flexDirection: "column", padding: "0 150px" }}>
        <Kicker label={kicker} style={k} />
        <div style={{ ...t, fontFamily: "Segoe UI, sans-serif", fontWeight: 800, fontSize: 78, color: "white", lineHeight: 1.05, textAlign: "center", marginTop: 26 }}>{title}</div>
        <div style={{ ...tg, fontFamily: "Segoe UI, sans-serif", fontWeight: 600, fontSize: 32, color: "#c8d6e6", marginTop: 20, textAlign: "center", maxWidth: 1200 }}>{tagline}</div>
        <Pills items={pills} style={p} />
      </AbsoluteFill>
      <CaptionBand text={caption} />
      <Footer text={footer} />
    </AbsoluteFill>
  );
};

// Outro scene: centered brand logo, kicker, title, tagline, pills.
export const OutroScene = ({ kicker, title, tagline, pills, footer, caption, logo = true }) => {
  const { fps } = useVideoConfig();
  const lg = useCinematicIn(0, fps);
  const k = useCinematicIn(6, fps);
  const t = useCinematicIn(10, fps);
  const tg = useCinematicIn(15, fps);
  const p = useCinematicIn(20, fps);
  return (
    <AbsoluteFill>
      <BreathingBg />
      <AbsoluteFill style={{ alignItems: "center", justifyContent: "center", flexDirection: "column", padding: "0 150px" }}>
        {logo ? (
          <div style={{ ...lg, marginBottom: 34 }}>
            <BrandLogo scale={1.1} />
          </div>
        ) : null}
        <Kicker label={kicker} style={k} />
        <div style={{ ...t, fontFamily: "Segoe UI, sans-serif", fontWeight: 800, fontSize: 70, color: "white", lineHeight: 1.05, textAlign: "center", marginTop: 24 }}>{title}</div>
        <div style={{ ...tg, fontFamily: "Segoe UI, sans-serif", fontWeight: 600, fontSize: 30, color: "#c8d6e6", marginTop: 18, textAlign: "center", maxWidth: 1180 }}>{tagline}</div>
        <Pills items={pills} style={p} />
      </AbsoluteFill>
      <CaptionBand text={caption} />
      <Footer text={footer} />
    </AbsoluteFill>
  );
};
