---
name: manim-video
version: 1.1.1
description: "Produces Manim Community Edition explainer videos: Scene classes, MathTex, ffmpeg stitch, optional TTS — 3Blue1Brown-style math, algorithms, and architecture diagrams. Use when the user wants programmatic math/technical animation with Manim. Not for Remotion/React video (remotion-video), character cinema (Blender/AE), or interactive apps."
risk: safe
source: openrouter-deepsearch
date_added: 2026-06-16
---

# Manim Video Production Pipeline

## When to Use

Use this skill when users request:
- Animated explanations of complex mathematical or technical concepts.
- 3Blue1Brown-style explainer videos.
- Algorithm walkthroughs and data structure visualizations.
- Step-by-step equation derivations and mathematical proofs.
- Technical architecture diagrams that build up dynamically.
- Data stories involving animated charts, comparisons, and counters.
- 3D visualizations of surfaces, parametric curves, or spatial geometry.
- Turning research papers into animated key findings and methods.

**Do not use** for:
- Simple static images or slide decks — use standard graphing or diagramming tools.
- High-fidelity character animation or cinematic storytelling — use Blender or After Effects.
- Real-time interactivity — Manim produces rendered video files, not interactive apps.
- Projects where Python/LaTeX environment setup is impossible.
- **Deprecation warning**: Avoid Manim CE v0.15 or earlier due to known security vulnerabilities and compatibility issues with recent Python versions.
- **Security note**: Be cautious when using online LaTeX rendering services; they may introduce security risks or require additional authentication.

## Prerequisites

Run `scripts/setup.sh` to verify all dependencies before starting. Required:
- Python 3.11+
- Manim Community Edition v0.22+ (`pip install manim`)
- LaTeX (`texlive-full` on Linux, `mactex` on macOS, MiKTeX or TeX Live on Windows)
- ffmpeg
- **Optional**: ElevenLabs or Qwen3-TTS for text-to-speech narration

**Windows (PowerShell) verification:**
```powershell
python --version          # must be 3.11+
manim --version           # must be 0.22+
ffmpeg -version
```

## Procedure

### Creative Standard

This is educational cinema. Every frame teaches. Every animation reveals structure.
- **Narrative First**: Before writing code, articulate the narrative arc. Identify the "aha moment" and the visual story.
- **Geometry before algebra**: Show the shape first, the equation second.
- **First-render excellence**: Output must be visually clear and aesthetically cohesive.
- **Opacity layering**: Primary elements at 1.0, contextual elements at 0.4, structural elements (axes, grids) at 0.15.
- **Breathing room**: Use `self.wait()` after animations. A 2-second pause after a key reveal is essential.
- **Cohesive visual language**: Maintain consistent color palettes, typography, and animation speeds across all scenes.

### Modes and Reference Loading

| Mode | Input | Output | Load reference |
|------|-------|--------|----------------|
| **Concept explainer** | Topic/concept | Animated explanation with geometric intuition | `references/scene-planning.md` |
| **Equation derivation** | Math expressions | Step-by-step animated proof | `references/equations.md` |
| **Algorithm visualization** | Algorithm description | Step-by-step execution with data structures | `references/graphs-and-data.md` |
| **Data story** | Data/metrics | Animated charts, comparisons, counters | `references/graphs-and-data.md` |
| **Architecture diagram** | System description | Components building up with connections | `references/mobjects.md` |
| **Paper explainer** | Research paper | Key findings and methods animated | `references/scene-planning.md` |
| **3D visualization** | 3D concept | Rotating surfaces, parametric curves, spatial geometry | `references/camera-and-3d.md` |

**When to load each reference file:**
- `references/scene-planning.md` — Load at the PLAN step for narrative arc templates and planning structure.
- `references/equations.md` — Load when writing scenes with `MathTex`, `TransformMatchingTex`, or LaTeX-heavy content.
- `references/graphs-and-data.md` — Load when building Axes, plots, BarChart, or data-driven visualizations.
- `references/mobjects.md` — Load when working with Text, shapes, VGroup, positioning, or architecture diagrams.
- `references/camera-and-3d.md` — Load when using `MovingCameraScene`, `ThreeDScene`, or any 3D content.
- `references/rendering.md` — Load at the STITCH and AUDIO steps for CLI reference, ffmpeg, and voiceover details.
- `references/troubleshooting.md` — Load when a render fails with LaTeX or animation errors.
- `references/animations.md` — Load when composing core animations, rate functions, or `.animate` syntax.
- `references/visual-design.md` — Load when applying opacity layering or layout templates.
- `references/animation-design-thinking.md` — Load when syncing pacing with narration.
- `references/updaters-and-trackers.md` — Load when using `ValueTracker` or `add_updater`.
- `references/paper-explainer.md` — Load for research paper workflow.
- `references/decorations.md` — Load when using `SurroundingRectangle`, `Brace`, or arrows.
- `references/production-quality.md` — Load at the REVIEW step for pre-render checklists.

### Stack

Single Python script per project. No browser, no Node.js, no GPU required.
- **Core**: Manim Community Edition (Scene rendering, animation engine)
- **Math**: LaTeX (Equation rendering via `MathTex`)
- **Video I/O**: ffmpeg (Scene stitching, format conversion, audio muxing)
- **TTS**: ElevenLabs / Qwen3-TTS (optional narration)

### Pipeline

`PLAN --> CODE --> RENDER --> STITCH --> AUDIO (optional) --> REVIEW`

### Project Structure

```
project-name/
  plan.md                # Narrative arc, scene breakdown
  script.py              # All scenes in one file
  concat.txt             # ffmpeg scene list
  final.mp4              # Stitched output
  media/                 # Auto-generated by Manim
    videos/script/480p15/
```

### Step 1: PLAN

Write `plan.md` with narrative arc, scene list, visual elements, color palette, and voiceover script. Use the template in `references/scene-planning.md`.

### Step 2: CODE

Write `script.py` with one class per scene, each independently renderable. Use shared color constants at the top of the file.

```python
from manim import *

BG = "#1C1C1C"
PRIMARY = "#58C4DD"
SECONDARY = "#83C167"
ACCENT = "#FFFF00"
MONO = "Menlo"

class Scene1_Introduction(Scene):
    def construct(self):
        self.camera.background_color = BG
        title = Text("Why Does This Work?", font_size=48, color=PRIMARY, weight=BOLD, font=MONO)
        self.add_subcaption("Why does this work?", duration=2)
        self.play(Write(title), run_time=1.5)
        self.wait(1.0)
        self.play(FadeOut(title), run_time=0.5)
```

**Critical coding rules:**
- **Subtitles**: Use `self.add_subcaption("text", duration=N)`.
- **Consistency**: Use shared color constants at the top of the file.
- **Clean exits**: `self.play(FadeOut(Group(*self.mobjects)))`.
- **Raw Strings for LaTeX**: Always use `r"\frac{1}{2}"` instead of `"\frac{1}{2}"`.
- **Edge Text**: Use `buff >= 0.5` (e.g., `label.to_edge(DOWN, buff=0.5)`).
- **Text Replacement**: Use `self.play(ReplacementTransform(note1, note2))` instead of writing over text.
- **Mobject Order**: Add mobjects before animating them: `self.play(Create(circle))` then `self.play(circle.animate.set_color(RED))`.

### Step 3: RENDER

**Windows (PowerShell):**
```powershell
manim -ql script.py Scene1_Introduction Scene2_CoreConcept  # draft
manim -qh script.py Scene1_Introduction Scene2_CoreConcept  # production
```

**Linux/macOS:**
```bash
manim -ql script.py Scene1_Introduction Scene2_CoreConcept  # draft
manim -qh script.py Scene1_Introduction Scene2_CoreConcept  # production
```

### Step 4: STITCH

**Windows (PowerShell):**
```powershell
@'
file 'media/videos/script/480p15/Scene1_Introduction.mp4'
file 'media/videos/script/480p15/Scene2_CoreConcept.mp4'
'@ | Set-Content concat.txt
ffmpeg -y -f concat -safe 0 -i concat.txt -c copy final.mp4
```

**Linux/macOS:**
```bash
cat > concat.txt << 'EOF'
file 'media/videos/script/480p15/Scene1_Introduction.mp4'
file 'media/videos/script/480p15/Scene2_CoreConcept.mp4'
EOF
ffmpeg -y -f concat -safe 0 -i concat.txt -c copy final.mp4
```

### Step 5: AUDIO (optional)

Add voiceover/music via ffmpeg. See `references/rendering.md` for detailed instructions. If using ElevenLabs or Qwen3-TTS, use `YOUR_KEY` placeholder for API keys — never hardcode live secrets.

### Step 6: REVIEW

**Windows (PowerShell):**
```powershell
manim -ql --format=png -s script.py Scene2_CoreConcept  # preview still
```

Render preview stills, verify against plan, adjust. Load `references/production-quality.md` for the pre-render checklist.

### Color Palettes

| Palette | Background | Primary | Secondary | Accent | Use case |
|---------|-----------|---------|-----------|--------|----------|
| **Classic 3B1B** | `#1C1C1C` | `#58C4DD` (BLUE) | `#83C167` (GREEN) | `#FFFF00` (YELLOW) | General math/CS |
| **Warm academic** | `#2D2B55` | `#FF6B6B` | `#FFD93D` | `#6BCB77` | Approachable |
| **Neon tech** | `#0A0A0A` | `#00F5FF` | `#FF00FF` | `#39FF14` | Systems, architecture |
| **Monochrome** | `#1A1A2E` | `#EAEAEA` | `#888888` | `#FFFFFF` | Minimalist |

### Animation Speed

| Context | run_time | self.wait() after |
|---------|----------|-------------------|
| Title/intro appear | 1.5s | 1.0s |
| Key equation reveal | 2.0s | 2.0s |
| Transform/morph | 1.5s | 1.5s |
| Supporting label | 0.8s | 0.5s |
| FadeOut cleanup | 0.5s | 0.3s |
| "Aha moment" reveal | 2.5s | 3.0s |

### Typography Scale

| Role | Font size | Usage |
|------|-----------|-------|
| Title | 48 | Scene titles, opening text |
| Heading | 36 | Section headers within a scene |
| Body | 30 | Explanatory text |
| Label | 24 | Annotations, axis labels |
| Caption | 20 | Subtitles, fine print |

**Fonts**: Use monospace fonts for all text to avoid kerning issues. Minimum `font_size=18` for readability.
```python
MONO = "Menlo"  # define once at top of file
Text("Fourier Series", font_size=48, font=MONO, weight=BOLD)  # titles
Text("n=1: sin(x)", font_size=20, font=MONO)                  # labels
MathTex(r"\nabla L")                                            # math (uses LaTeX)
```

### Per-Scene Variation

Avoid identical configs. For each scene, vary:
- Dominant color from the palette.
- Layout (don't always center).
- Animation entry (Write, FadeIn, GrowFromCenter, Create).
- Visual weight (dense vs sparse).

### Performance Targets

| Quality | Resolution | FPS | Speed |
|---------|-----------|-----|-------|
| `-ql` (draft) | 854x480 | 15 | 5-15s/scene |
| `-qm` (medium) | 1280x720 | 30 | 15-60s/scene |
| `-qh` (production) | 1920x1080 | 60 | 30-120s/scene |

## Pitfalls

- **LaTeX escape errors**: Always use raw strings (`r"..."`) for `MathTex`. Backslashes in regular strings will be interpreted as Python escape sequences and cause render failures.
- **Text overlap**: Failing to `FadeOut` previous mobjects before adding new ones causes visual clutter. Always clean up with `self.play(FadeOut(Group(*self.mobjects)))` at scene end.
- **Missing `self.wait()`**: Omitting pauses after key reveals makes animations feel rushed. A 2-second pause after a key reveal is essential.
- **Manim CE v0.15 or earlier**: Known security vulnerabilities and compatibility issues with recent Python versions. Always use v0.22+.
- **Online LaTeX rendering services**: May introduce security risks or require additional authentication. Prefer local LaTeX installations.
- **Kerning issues with non-monospace fonts**: Use monospace fonts (`MONO = "Menlo"`) for all `Text` objects to avoid inconsistent character spacing.
- **Mobject order errors**: Adding mobjects in the wrong order causes z-order issues. Add mobjects before animating them.
- **Edge text clipping**: Using `buff < 0.5` with `to_edge()` can clip text off-screen. Always use `buff >= 0.5`.
- **Writing over text**: Using `self.play(Write(new_text))` over existing text causes overlap. Use `ReplacementTransform` instead.
- **Missing background color**: Not setting `self.camera.background_color` in every scene leads to inconsistent visuals across the final video.
- **Windows path issues**: On Windows, ffmpeg concat file paths use forward slashes inside the concat list. Ensure `concat.txt` uses `file 'media/videos/script/480p15/SceneName.mp4'` format with single quotes.

## Verification

- [ ] Verify Python 3.11+ and Manim CE v0.22+ are installed:
  ```powershell
  python --version    # expect 3.11+
  manim --version     # expect 0.22+
  ```
- [ ] Run a draft render to ensure the scene renders without LaTeX errors:
  ```powershell
  manim -ql script.py Scene1_Introduction
  ```
- [ ] Check that all `MathTex` calls use raw strings (`r"expression"`).
- [ ] Verify that `self.wait()` is present after key reveals.
- [ ] Confirm that `self.camera.background_color` is explicitly set in every scene.
- [ ] Ensure all text uses the defined `MONO` font.
- [ ] Validate the project structure and file naming conventions.
- [ ] Verify stitched output plays correctly:
  ```powershell
  ffprobe final.mp4
  ```
- [ ] Render a preview still for visual review:
  ```powershell
  manim -ql --format=png -s script.py Scene2_CoreConcept
  ```

## Related Skills

- `references/animations.md`: Core animations, rate functions, `.animate` syntax.
- `references/mobjects.md`: Text, shapes, VGroup, positioning.
- `references/visual-design.md`: Opacity layering, layout templates.
- `references/equations.md`: LaTeX, TransformMatchingTex.
- `references/graphs-and-data.md`: Axes, plotting, BarChart.
- `references/camera-and-3d.md`: MovingCameraScene, ThreeDScene.
- `references/scene-planning.md`: Narrative arcs, planning template.
- `references/rendering.md`: CLI reference, ffmpeg, voiceover.
- `references/troubleshooting.md`: LaTeX and animation errors.
- `references/animation-design-thinking.md`: Pacing and narration sync.
- `references/updaters-and-trackers.md`: ValueTracker, add_updater.
- `references/paper-explainer.md`: Research paper workflow.
- `references/decorations.md`: SurroundingRectangle, Brace, arrows.
- `references/production-quality.md`: Pre-render checklists.
