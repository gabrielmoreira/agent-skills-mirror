# React Three Fiber (load on demand)

Use this companion only when the user explicitly asks for React Three Fiber (`@react-three/fiber`). The parent `SKILL.md` procedure is vanilla Three.js (import maps or Vite). Do not switch stacks because a React app exists elsewhere in the repo.

## Canvas scaffold

```jsx
import { Canvas, useFrame } from "@react-three/fiber";
import { OrbitControls } from "@react-three/drei";
import { useRef } from "react";

function SpinningSphere() {
  const mesh = useRef();
  useFrame((_, delta) => {
    if (!mesh.current) return;
    mesh.current.rotation.y += delta * 0.5;
    mesh.current.rotation.x += delta * 0.25;
  });
  return (
    <mesh ref={mesh} castShadow>
      <sphereGeometry args={[1, 32, 32]} />
      <meshStandardMaterial color="#00aa44" metalness={0.4} roughness={0.5} />
    </mesh>
  );
}

export default function Scene() {
  return (
    <Canvas camera={{ position: [0, 0, 5], fov: 75 }} shadows>
      <ambientLight intensity={0.5} />
      <directionalLight position={[5, 5, 5]} intensity={0.8} castShadow />
      <SpinningSphere />
      <OrbitControls enableDamping />
    </Canvas>
  );
}
```

Install `three`, `@react-three/fiber`, and `@react-three/drei` in the same Vite React app. Keep Three.js versions compatible with the Fiber release.

## Mapping from vanilla

| Vanilla (`SKILL.md`) | R3F |
|---|---|
| `scene.add(mesh)` | JSX `<mesh>` inside `<Canvas>` |
| `setAnimationLoop` | `useFrame` |
| `OrbitControls` addon | `<OrbitControls />` from Drei |
| `renderer.setSize` / resize | Canvas handles resize |
| `outputColorSpace` / tone mapping | set on `<Canvas gl={...}>` if needed |

## Pitfalls

- Declarative JSX still needs lights for `meshStandardMaterial`; unlit meshes render black.
- Do not call `renderer.render` manually inside `useFrame` unless replacing the default render loop on purpose.
- R3F is not a browser-game architecture chair and not a skill router. Stay on this overlay for React canvas wiring; keep gameplay, routing, and vanilla scaffolds in their own skills.
