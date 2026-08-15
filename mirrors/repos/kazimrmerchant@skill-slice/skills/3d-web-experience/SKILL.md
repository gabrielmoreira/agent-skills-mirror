---
name: 3d-web-experience
description: "Assembles interactive browser 3D with Three.js, React Three Fiber, Spline, Draco GLB, and WebGL fallbacks. Use when the user wants a product configurator, 3D portfolio, or scroll-scrubbed WebGL scene. Not a native Unity/Unreal game skill and not a Blender modeling course."
version: 1.0.1
risk: unknown
source: vibeship-spawner-skills (Apache 2.0)
date_added: 2026-02-27
---

# 3D Web Experience

Expert in building 3D experiences for the web — Three.js, React Three Fiber, Spline, WebGL, GLSL shaders, and interactive 3D scenes. Covers product configurators, 3D portfolios, immersive websites, and bringing depth to web experiences.

**Role**: 3D Web Experience Architect

You bring the third dimension to the web. You know when 3D enhances and when it's just showing off. You balance visual impact with performance. You make 3D accessible to users who've never touched a 3D app. You create moments of wonder without sacrificing usability.

## When to Use

Activate this skill when the user mentions or implies any of:

- 3D website or 3D experience
- Three.js or WebGL
- React Three Fiber (R3F)
- Spline design tool
- Product configurator with 3D
- 3D portfolio or immersive landing page
- Scroll-driven 3D animations
- GLSL shaders or custom 3D materials
- 3D model preparation for the web (GLB/GLTF)

Do **not** use this skill for:
- Pure 2D animation or parallax (use `scroll-experience`)
- Game development targeting native engines (Unity/Unreal)
- CAD or 3D modeling software tutorials (Blender/Maya workflows beyond export)

## Prerequisites

- Node.js 18+ and npm/pnpm/yarn installed
- A modern browser with WebGL support (Chrome, Firefox, Safari, Edge)
- For model optimization: `@gltf-transform/cli` installed globally
- React 18+ if using React Three Fiber
- Windows host is primary; use PowerShell for all CLI commands

## Procedure

### 1. Select the Right 3D Stack

Choose the approach based on project needs:

| Tool | Best For | Learning Curve | Control |
|------|----------|----------------|---------|
| Spline | Quick prototypes, designers | Low | Medium |
| React Three Fiber | React apps, complex scenes | Medium | High |
| Three.js vanilla | Max control, non-React | High | Maximum |
| Babylon.js | Games, heavy 3D | High | Maximum |

**Decision tree:**

```
Need quick 3D element?
└── Yes → Spline
└── No → Continue

Using React?
└── Yes → React Three Fiber
└── No → Continue

Need max performance/control?
└── Yes → Three.js vanilla
└── No → Spline or R3F
```

### 2. Install Dependencies

**Spline (fastest start):**

```powershell
npm install @splinetool/react-spline @splinetool/runtime
```

**React Three Fiber:**

```powershell
npm install three @react-three/fiber @react-three/drei
```

**Three.js vanilla:**

```powershell
npm install three
```

### 3. Implement the Scene

**Spline:**

```jsx
import Spline from '@splinetool/react-spline';

export default function Scene() {
  return (
    <Spline scene="https://prod.spline.design/xxx/scene.splinecode" />
  );
}
```

**React Three Fiber with GLTF model:**

```jsx
import { Canvas } from '@react-three/fiber';
import { OrbitControls, useGLTF } from '@react-three/drei';

function Model() {
  const { scene } = useGLTF('/model.glb');
  return <primitive object={scene} />;
}

export default function Scene() {
  return (
    <Canvas>
      <ambientLight />
      <Model />
      <OrbitControls />
    </Canvas>
  );
}
```

### 4. Prepare 3D Models for the Web

Format selection:

| Format | Use Case | Size |
|--------|----------|------|
| GLB/GLTF | Standard web 3D | Smallest |
| FBX | From 3D software | Large |
| OBJ | Simple meshes | Medium |
| USDZ | Apple AR | Medium |

**Optimization pipeline:**

1. Model in Blender or equivalent 3D software
2. Reduce poly count (target < 100K triangles for web)
3. Bake textures (combine materials where possible)
4. Export as GLB
5. Compress with gltf-transform
6. Test file size (target < 5MB ideal)

**Install and run gltf-transform on Windows (PowerShell):**

```powershell
npm install -g @gltf-transform/cli

gltf-transform optimize input.glb output.glb `
  --compress draco `
  --texture-compress webp
```

> **HARD RULE**: Never ship uncompressed GLB/GLTF models to production. Always run Draco compression and WebP texture compression. Verify output size is under 5MB.

### 5. Add Loading States

```jsx
import { useGLTF, useProgress, Html } from '@react-three/drei';
import { Suspense } from 'react';

function Loader() {
  const { progress } = useProgress();
  return <Html center>{progress.toFixed(0)}%</Html>;
}

export default function Scene() {
  return (
    <Canvas>
      <Suspense fallback={<Loader />}>
        <Model />
      </Suspense>
    </Canvas>
  );
}
```

> **HARD RULE**: Every 3D scene MUST have a loading indicator. Use Suspense with a fallback or `useProgress` for loading UI. No exceptions.

### 6. Implement Scroll-Driven 3D (if needed)

**R3F + ScrollControls:**

```jsx
import { ScrollControls, useScroll } from '@react-three/drei';
import { useFrame } from '@react-three/fiber';

function RotatingModel() {
  const scroll = useScroll();
  const ref = useRef();

  useFrame(() => {
    ref.current.rotation.y = scroll.offset * Math.PI * 2;
  });

  return <mesh ref={ref}>...</mesh>;
}

export default function Scene() {
  return (
    <Canvas>
      <ScrollControls pages={3}>
        <RotatingModel />
      </ScrollControls>
    </Canvas>
  );
}
```

**GSAP + Three.js (vanilla):**

```javascript
import gsap from 'gsap';
import ScrollTrigger from 'gsap/ScrollTrigger';

gsap.to(camera.position, {
  scrollTrigger: {
    trigger: '.section',
    scrub: true,
  },
  z: 5,
  y: 2,
});
```

Common scroll effects: camera movement through scene, model rotation on scroll, reveal/hide elements, color/material changes, exploded view animations.

### 7. Optimize Performance

Performance targets:

| Device | Target FPS | Max Triangles |
|--------|------------|---------------|
| Desktop | 60fps | 500K |
| Mobile | 30-60fps | 100K |
| Low-end | 30fps | 50K |

**Quick wins:**

```jsx
// 1. Use instances for repeated objects
import { Instances, Instance } from '@react-three/drei';

// 2. Limit lights
<ambientLight intensity={0.5} />
<directionalLight /> // Just one

// 3. Use LOD (Level of Detail)
import { LOD } from 'three';

// 4. Lazy load models
const Model = lazy(() => import('./Model'));
```

**Mobile detection and DPR limiting:**

```jsx
const isMobile = /iPhone|iPad|Android/i.test(navigator.userAgent);

<Canvas
  dpr={isMobile ? 1 : 2}
  performance={{ min: 0.5 }}
>
```

> **HARD RULE**: Limit DPR to 1 on mobile devices. Never use `dpr={2}` or higher on mobile — it kills performance.

### 8. Add WebGL Fallback

```jsx
function Scene() {
  const [webGLSupported, setWebGLSupported] = useState(true);

  if (!webGLSupported) {
    return <img src="/fallback.png" alt="3D preview" />;
  }

  return <Canvas onCreated={...} />;
}
```

> **HARD RULE**: Every 3D scene MUST have a WebGL fallback. Detect WebGL support and show a static image or simplified version for unsupported devices.

### 9. Handle OrbitControls and Scroll Conflicts

If OrbitControls captures scroll events and blocks page scrolling:

```jsx
<OrbitControls enableZoom={false} />
```

Or handle scroll/touch events explicitly to prevent the 3D canvas from hijacking page scroll on mobile.

## Pitfalls

### No 3D Loading Indicator (HIGH)
**Problem**: No loading indicator for 3D content — users see a blank canvas while models load.
**Fix**: Add Suspense with loading fallback or useProgress for loading UI. Always.

### No WebGL Fallback (MEDIUM)
**Problem**: No fallback for devices without WebGL support — scene breaks silently.
**Fix**: Add WebGL detection and static image fallback before rendering Canvas.

### Uncompressed 3D Models (MEDIUM)
**Problem**: 3D models may be unoptimized — large file sizes, slow load.
**Fix**: Compress models with `gltf-transform` using Draco and WebP texture compression. Target < 5MB.

### OrbitControls Blocking Scroll (MEDIUM)
**Problem**: OrbitControls captures scroll events, preventing page scroll on mobile.
**Fix**: Add `enableZoom={false}` or handle scroll/touch events appropriately.

### High DPR on Mobile (MEDIUM)
**Problem**: Canvas DPR too high for mobile devices — frame drops, overheating.
**Fix**: Limit DPR to 1 on mobile devices: `dpr={isMobile ? 1 : 2}`.

### Too Many Lights (MEDIUM)
**Problem**: Multiple dynamic lights cause shader recompilation and performance drops.
**Fix**: Use one directional light + ambient light. Bake lighting into textures where possible.

### Models Not Lazy Loaded (MEDIUM)
**Problem**: Large 3D models loaded synchronously block initial render.
**Fix**: Use `React.lazy()` and Suspense for model components.

## Verification

Check the following after implementing any 3D scene:

1. **Loading indicator present**: Confirm Suspense fallback or `useProgress` UI renders during model load.
   ```powershell
   # Search for Suspense usage in your scene files
   Select-String -Path "src\**\*.jsx" -Pattern "Suspense|useProgress"
   ```

2. **WebGL fallback exists**: Confirm WebGL detection logic and fallback image path.
   ```powershell
   Select-String -Path "src\**\*.jsx" -Pattern "webGLSupported|WebGLRenderingContext"
   ```

3. **Model compression applied**: Verify GLB file size is under 5MB.
   ```powershell
   Get-Item public\model.glb | Select-Object Name, @{N='SizeMB';E={[math]::Round($_.Length/1MB,2)}}
   ```

4. **DPR limited on mobile**: Confirm conditional DPR logic.
   ```powershell
   Select-String -Path "src\**\*.jsx" -Pattern "dpr=\{.*isMobile"
   ```

5. **Performance check**: Open Chrome DevTools → Performance tab → record 5 seconds of interaction. Confirm:
   - Desktop: 60fps sustained
   - Mobile (device emulation): 30-60fps sustained
   - No shader recompilation warnings in console

6. **OrbitControls scroll test**: On mobile viewport, confirm page scroll works when touching the canvas area. If blocked, add `enableZoom={false}`.

## Collaboration

### Delegation Triggers

- `scroll animation|parallax|GSAP` → `scroll-experience` (Scroll integration)
- `react|next|frontend` → `frontend` (React integration)
- `performance|slow|fps` → `performance-hunter` (3D performance optimization)
- `product page|landing|marketing` → `landing-page-design` (Product landing with 3D)

### Product Configurator Workflow

Skills: `3d-web-experience`, `frontend`, `landing-page-design`

```
1. Prepare 3D product model
2. Set up React Three Fiber scene
3. Add interactivity (colors, variants)
4. Integrate with product page
5. Optimize for mobile
6. Add fallback images
```

### Immersive Portfolio Workflow

Skills: `3d-web-experience`, `scroll-experience`, `interactive-portfolio`

```
1. Design 3D scene concept
2. Build scene in Spline or R3F
3. Add scroll-driven animations
4. Integrate with portfolio sections
5. Ensure mobile fallback
6. Optimize performance
```

## Related Skills

Works well with: `scroll-experience`, `interactive-portfolio`, `frontend`, `landing-page-design`, `performance-hunter`

## Limitations

- Use this skill only when the task clearly matches the scope described above.
- Do not treat the output as a substitute for environment-specific validation, testing, or expert review.
- Stop and ask for clarification if required inputs, permissions, safety boundaries, or success criteria are missing.
