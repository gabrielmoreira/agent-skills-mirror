// Remotion root. Registers every scene from the SCENES array as its own
// <Composition> (for isolated still review) AND the full assembly. This reads
// SCENES from ./MainVideo, so you never hand-maintain a second list.
//
// SETUP: rename MainVideo.template.jsx -> MainVideo.jsx before rendering, so the
// import below resolves. Composition is 1920x1080 @ 30fps (change if needed).
import { Composition } from "remotion";
import { MainVideo, TOTAL_DURATION, SCENES } from "./MainVideo";

const FPS = 30;
const WIDTH = 1920;
const HEIGHT = 1080;

export const RemotionRoot = () => {
  return (
    <>
      {/* One composition per scene — render stills of these during review:
          npx remotion still src/index.jsx <SceneId> out.png --frame=150 */}
      {SCENES.map((s) => (
        <Composition
          key={s.id}
          id={s.id}
          component={s.Comp}
          durationInFrames={s.duration}
          fps={FPS}
          width={WIDTH}
          height={HEIGHT}
          defaultProps={{ ...s.props, dur: s.duration }}
        />
      ))}

      {/* The full assembled deliverable:
          npx remotion render src/index.jsx MainVideo out.mp4 --codec=h264 */}
      <Composition
        id="MainVideo"
        component={MainVideo}
        durationInFrames={TOTAL_DURATION}
        fps={FPS}
        width={WIDTH}
        height={HEIGHT}
      />
    </>
  );
};
