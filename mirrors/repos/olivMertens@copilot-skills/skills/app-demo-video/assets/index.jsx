// Remotion entry point. Referenced by every CLI command:
//   npx remotion studio  src/index.jsx
//   npx remotion still    src/index.jsx <CompId> out.png --frame=150
//   npx remotion render   src/index.jsx MainVideo out.mp4 --codec=h264
import { registerRoot } from "remotion";
import { RemotionRoot } from "./Root";

registerRoot(RemotionRoot);
