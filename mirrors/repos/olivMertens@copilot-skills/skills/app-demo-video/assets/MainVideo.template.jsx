// Assembly template: chains scenes with crossfades, injects per-scene narration
// audio, and layers a ducked background-music envelope that briefly "flares" at
// each scene boundary so the music breathes without ever covering the voice.
//
// HOW TO USE:
// 1. Copy into src/ and rename (e.g. MainVideoDemoEn.jsx).
// 2. Fill SCENES: one entry per scene. `duration` = ceil(clipSeconds*fps)+~20
//    (get clipSeconds from `ffprobe` on the generated mp3 — never guess).
// 3. Point `audio` at the mp3 in public/, and BGM at your track in public/.
// 4. Register this component AND each scene as <Composition>s in Root.jsx,
//    passing TOTAL_DURATION as this assembly's durationInFrames.
import { Series, Audio, staticFile, useCurrentFrame, interpolate } from "remotion";
import { TransitionWrapper, TRANSITION_OVERLAP } from "./TransitionWrapper";
import { HookScene, ContentScene, OutroScene } from "./scene-components";

const FOOTER = "One-line footer · translate/rename per project";
const BGM_FILE = "bgm.mp3";     // put your background-music track in public/
const BGM_BASE = 0.05;          // ducked baseline volume (voice stays on top)
const BGM_FLARE = 0.09;         // brief lift at each scene boundary

export const SCENES = [
  {
    id: "Hook",
    Comp: HookScene,
    duration: 300, // ceil(clipSeconds*fps)+20
    audio: "narr_hook.mp3",
    props: {
      kicker: "KICKER · ACCENT",
      title: "One punchy title line.",
      tagline: "A single supporting sentence.",
      pills: ["Tag one", "Tag two", "Tag three"],
      footer: FOOTER,
    },
  },
  {
    id: "Feature",
    Comp: ContentScene,
    duration: 320,
    audio: "narr_feature.mp3",
    props: {
      kicker: "FEATURE AREA",
      headline: "What this screen proves",
      subtitle: "One sentence of why/how/value that does not paraphrase on-screen text.",
      pills: ["Underlying tech", "Concrete benefit"],
      img: "feature_card.png", // cropped screenshot in public/
      imgWidth: 1200,
      badge: null,             // e.g. "+10%" to spotlight a number
      caption: "Optional burned-in subtitle — for silent/social viewing.",
      footer: FOOTER,
    },
  },
  {
    id: "Outro",
    Comp: OutroScene,
    duration: 260,
    audio: "narr_outro.mp3",
    props: {
      kicker: "PRODUCT NAME",
      title: "Closing line.",
      tagline: "The one thing to remember.",
      pills: ["Platform", "Service"],
      footer: FOOTER,
    },
  },
];

export const TOTAL_DURATION =
  SCENES.reduce((sum, s) => sum + s.duration, 0) - (SCENES.length - 1) * TRANSITION_OVERLAP;

export const MainVideo = () => {
  const frame = useCurrentFrame();

  // Build a piecewise BGM volume envelope: flare up ~2 frames before each scene
  // boundary, hold briefly, then settle back to baseline over ~14 frames.
  let cursor = 0;
  const boundaries = [0];
  for (const s of SCENES) {
    cursor += s.duration - TRANSITION_OVERLAP;
    boundaries.push(cursor);
  }
  const keyframes = [];
  const values = [];
  for (const b of boundaries) {
    const flareStart = Math.max(0, b - 2);
    keyframes.push(flareStart, b + 2, b + 14);
    values.push(BGM_FLARE, BGM_FLARE, BGM_BASE);
  }
  const pairs = keyframes.map((k, i) => [k, values[i]]).sort((a, b) => a[0] - b[0]);
  const xs = [];
  const ys = [];
  for (const [x, y] of pairs) {
    if (xs.length === 0 || x > xs[xs.length - 1]) {
      xs.push(x);
      ys.push(y);
    }
  }
  const fadeIn = interpolate(frame, [0, 15], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  const fadeOut = interpolate(frame, [TOTAL_DURATION - 25, TOTAL_DURATION], [1, 0], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  const envelope = interpolate(frame, xs, ys, { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  const bgmVolume = envelope * fadeIn * fadeOut;

  return (
    <>
      <Audio src={staticFile(BGM_FILE)} volume={bgmVolume} />
      <Series>
        {SCENES.map((s, i) => (
          <Series.Sequence key={s.id} durationInFrames={s.duration} offset={i === 0 ? 0 : -TRANSITION_OVERLAP}>
            <TransitionWrapper durationInFrames={s.duration}>
              <s.Comp {...s.props} dur={s.duration} />
            </TransitionWrapper>
            {s.audio ? <Audio src={staticFile(s.audio)} /> : null}
          </Series.Sequence>
        ))}
      </Series>
    </>
  );
};
