---
name: 3d-miniature-figurine
description: Create 3D-printed miniatures and figurines from concept to painted tabletop-ready piece using AI image-to-3D tools, digital sculpting, FDM print settings, support strategies, and post-processing. Trigger when user asks about 3D miniatures, figurines, tabletop printing, wargaming minis, or AI-to-3D workflows. Not for image-to-mesh conversion without tabletop print (3d-image-to-model) and not for game-engine or Godot meshes.
version: 1.0.1
---

## Overview

End-to-end workflow for creating high-quality 3D-printed miniatures and figurines, from concept to painted tabletop-ready piece. Optimized for FDM printing on a Bambu Lab P1S but techniques apply broadly to any FDM or resin printer. Covers AI image-to-3D generation, digital sculpting, mesh cleanup, slicing, support strategies, print settings, post-processing, and multi-part assembly.

## When to Use

- User wants to create 3D-printed miniatures or figurines for tabletop gaming (D&D, Warhammer, Malifaux, etc.)
- User asks about AI image-to-3D tools (Meshy, Tripo AI, Hitem3D, etc.) for miniature creation
- User needs help with FDM print settings for fine-detail miniatures
- User asks about support strategies for complex figurine geometry
- User needs post-processing advice (priming, painting, varnishing) for 3D prints
- User wants to scale miniatures for specific game systems
- User needs troubleshooting for miniature print failures

## Prerequisites

- **3D modeling software:** Blender (free, recommended for cleanup), ZBrush (professional sculpting), or Nomad Sculpt (tablet)
- **Slicer:** Bambu Studio (for Bambu Lab P1S) or equivalent
- **3D printer:** Bambu Lab P1S (primary reference) or any FDM/resin printer
- **Filament:** PLA or PLA+ recommended for miniatures; PETG for durable terrain
- **Post-processing supplies:** Flush cutters, hobby knife, sandpaper (220-800 grit), filler primer, acrylic paints, matte varnish
- **Python environment:** Optional, for batch mesh repair with trimesh in the user's project (this folder does not ship helper scripts)
- **Scale and slicer values:** Use the scale tables and Bambu Studio setting tables in this file (Steps 3–4). This folder does not ship a references pack.

## Procedure

### Step 1: Concept and 3D Model Generation

Choose a generation path based on experience level and desired control.

#### AI Image-to-3D Tools

| Tool | Best For | Print Readiness | Resolution | Output Formats |
|------|----------|-----------------|------------|----------------|
| **Meshy** | Overall workflow, miniatures, ease of use | High (consistent, print-friendly meshes) | 1024³ default | STL, OBJ, FBX, 3MF |
| **Hitem3D** | Fine surface detail, high-res resin minis | Very High (superior geometry detail) | 1536³ | STL, OBJ, GLB |
| **Tripo AI** | Speed and rapid iteration | Moderate (clean topology, may lack fine detail) | 1024³ | STL, OBJ, FBX, 3MF |
| **Rodin AI** | Photorealistic art and rendering | Low (requires heavy mesh cleanup) | High (4K PBR textures) | OBJ, FBX, GLB |
| **Shap-E (OpenAI)** | Research, open-source experimentation | Low (experimental quality) | Variable | OBJ, PLY |
| **InstantMesh** | Open-source single-image reconstruction | Moderate (research-grade output) | Variable | OBJ, PLY |

**Meshy Workflow (Recommended for Beginners):**
1. Upload a reference image (front-facing, clean background, good lighting).
2. Select "High Detail" mode for miniatures under 75mm.
3. Generate the 3D model (typical generation time: 30-90 seconds).
4. Download as STL for monochrome prints or 3MF for multi-color Bambu AMS prints.
5. Import into Blender for cleanup (see Step 2).

**Tripo AI Workflow (Best for Rapid Iteration):**
1. Upload reference image or provide a text prompt.
2. Generate model (typical time: 10-30 seconds).
3. Use the built-in editor to refine pose and proportions.
4. Export as STL.
5. Import into Blender for detail refinement and print preparation.

**Shap-E and InstantMesh (Open-Source):**
- Shap-E: Runs locally via Python, generates implicit 3D representations from text or images. Output quality is below commercial tools. Best as a starting point for further sculpting.
- InstantMesh: Single-image 3D reconstruction using sparse-view diffusion. Available on Hugging Face Spaces for quick testing. Produces reasonable base meshes requiring significant refinement.

#### Digital Sculpting Tools

**ZBrush (Professional Standard):**
1. Start with a ZSphere armature to establish the pose.
2. Convert to DynaMesh and block out major volumes (torso, limbs, head).
3. Refine form and silhouette. Check from all angles.
4. Add secondary details (armor, clothing folds, muscle definition).
5. Add tertiary details (skin texture, scratches, damage, fine ornaments).
6. Use Decimation Master to reduce polycount for export.
7. Export as STL.

Key ZBrush features: DynaMesh (free-form sculpting), ZRemesher (auto-retopology), Insert Mesh brushes (pre-made armor/rivet/chain inserts), Fibermesh (hair/fur), Decimation Master (polycount reduction).

**Blender (Free, All-Purpose):**
1. Start with a base mesh or use the Skin modifier on a stick figure.
2. Apply Multiresolution modifier and sculpt at increasing subdivision levels.
3. Perform silhouette check by pressing Numpad 1, 3, 7 for front/side/top views.
4. Add details at higher subdivision levels.
5. Use 3D Print Toolbox to verify manifold geometry.
6. Export as STL.

Key Blender features: Sculpt Mode (Clay Strips, Crease, Smooth, Grab, Inflate brushes), Multires Modifier, Boolean Operations (part splitting), 3D Print Toolbox add-on (manifold/overhang checks), Remesh Modifier (voxel remesh).

**Nomad Sculpt (Tablet-Based):**
1. Sculpt initial concept in Nomad Sculpt.
2. Export as OBJ to Blender or ZBrush for final refinement.
3. Perform print preparation (manifold checks, part splitting) in Blender.

### Step 2: Post-AI Mesh Cleanup in Blender (Always Required)

Every AI-generated mesh requires manual quality assurance before printing.

1. **Fix non-manifold geometry:** Select All > Mesh > Clean Up > Make Manifold.
2. **Thicken thin features:** Weapons, fingers, tails often need thickening. Use the Solidify modifier with a minimum thickness of **1.5mm** for FDM.
3. **Fill holes:** Select boundary edges > Fill (F key) > Smooth vertices.
4. **Reduce polygon count:** Use the Decimate modifier (ratio 0.3-0.5). Target **200k-500k faces** for FDM miniatures.
5. **Ensure watertight mesh:** Use 3D Print Toolbox add-on > Make Manifold.
6. **Remove interior faces:** Select interior faces in Blender, delete.
7. **Fix intersecting geometry:** Boolean union in Blender to merge overlapping regions.
8. **Add flat base if missing:** Add a cylinder base in Blender, Boolean union with model.
9. **Scale to target:** Match feet-to-eye-level measurement to target scale (see Scale Reference below).
10. **Center on build plate:** Set origin to bottom center.
11. **Split into parts if needed:** Use Boolean operations for multi-part printing.
12. **Add alignment keys:** Peg/hole, 2mm diameter for multi-part assembly.
13. **Export as STL.**

> When the user has multiple STL files to prepare, run trimesh repair in their project (batch-fix non-manifold edges, remove interior faces, decimate counts >1M). This folder does not ship helper scripts.

### Step 3: Scale Reference

When sculpting or scaling for tabletop gaming, scale consistency is critical. Always confirm the target scale before any work begins.

| Game System | Standard Scale | Measurement Reference |
|-------------|---------------|----------------------|
| D&D / Pathfinder | 28mm | Feet to eye level |
| Warhammer 40K / Age of Sigmar | 32mm ("heroic") | Feet to eye level |
| Star Wars Legion | 35mm | Feet to eye level |
| Malifaux | 32mm | Feet to eye level |
| Bolt Action (WWII) | 28mm | Feet to eye level |
| Display / Collectible | 54mm-75mm | Feet to top of head |

**D&D 5e Standard Base Sizes (25mm grid):**

| Creature Size | Base Diameter | Grid Squares | Example |
|---------------|---------------|-------------|---------|
| Tiny | 12.5mm (0.5") | <1 square | Sprite, Pseudragon |
| Small | 25mm (1") | 1 square | Halfling, Goblin |
| Medium | 25mm (1") | 1 square | Human, Elf, Orc |
| Large | 50mm (2") | 2x2 squares | Horse, Ogre, Bear |
| Huge | 75mm (3") | 3x3 squares | Giant, Dragon (young) |
| Gargantuan | 100mm (4") | 4x4 squares | Ancient Dragon, Tarrasque |

**Warhammer 40K / Age of Sigmar (32mm heroic scale):**

| Unit Type | Typical Base | Height (approx) |
|-----------|-------------|-----------------|
| Infantry | 25mm or 32mm round | 30-35mm |
| Elite Infantry | 32mm round | 35-40mm |
| Characters/Heroes | 32mm or 40mm round | 35-45mm |
| Large Monsters | 60mm or 80mm round | 60-120mm |
| Vehicles | Various oval/rectangular | 40-100mm tall |

**Scaling workflow:**
1. Import a reference miniature STL from your existing collection into your slicer.
2. Measure the height of the reference model (feet to eye level).
3. Scale your custom model to match.
4. Print a test piece at 25% infill to verify scale before committing to a full print.
5. Adjust scale by ±5% if the model looks slightly off next to your collection.

> Always keep a reference STL of a miniature from your collection imported into your sculpting software. Measure from feet to eye level, not the top of the head (to account for helmets and hair).

### Step 4: Slicing in Bambu Studio

#### Orientation Strategy

Model orientation often matters more than layer height for miniature quality.

1. Rotate the model so the face and most detailed surfaces face **UPWARD** (away from the build plate and supports).
2. Tilt the model 15-30° backward to move overhangs from the face to the back.
3. For standing figures, printing upright (feet on bed) minimizes supports but may cause poor overhang quality on extended arms.
4. For dynamic poses (lunging, flying), orient the model at 30-45° to balance support needs with surface quality.

#### Support Strategies

**Tree Supports (Recommended Default):**

| Setting | Value | Rationale |
|---------|-------|-----------|
| Support Type | Tree (Organic) | Best for complex figurine geometry |
| Support Threshold Angle | 40-45° | Catches most overhangs without over-supporting |
| Top Z Distance | 0.2mm (start), adjust ±0.05mm | Controls gap between support and model |
| Interface Layers (Top) | 2-3 layers | Creates smooth ceiling for overhang surface |
| Interface Layers (Bottom) | 0 | Saves material, bottom interface rarely needed |
| Branch Diameter | 2.0-3.0mm | Thicker for heavy models, thinner for small details |
| Branch Angle | 40° | Default is usually fine for most figurines |
| Support on Build Plate Only | OFF | Miniatures usually need supports everywhere |

**Manual Support Painting (when auto tree supports fail):**
1. Switch to the "Support painting" tool in the left toolbar.
2. Paint green on areas where you want to FORCE supports.
3. Paint red on areas where you want to BLOCK supports (faces, detailed surfaces).
4. Use "Sphere" brush shape for organic areas, "Circle" for flat regions.

Manual support guidance:
- **Faces and detailed front surfaces:** Block supports to preserve detail.
- **Undersides of extended arms and weapons:** Force supports for structural stability.
- **Cape interiors:** Force thin supports to prevent sagging.
- **Bases and feet:** Usually safe to block supports (model sits on build plate).

**Multi-Material Support Strategy (AMS):**
- Use PETG or PVA as the support material with PLA as the model material.
- Set Top Z Distance to **0.0mm** for ultra-clean overhang surfaces.
- PETG peels away from PLA cleanly due to poor layer adhesion between materials.
- PVA dissolves in water, giving the cleanest possible result but at higher cost.

#### Print Settings: Display Quality (0.08mm)

Use for hero pieces, display models, and competition entries. Print times will be 2-3x longer than gaming quality.

| Setting | Value | Notes |
|---------|-------|-------|
| Layer Height | 0.08mm | Maximum vertical resolution for standard nozzle |
| First Layer Height | 0.20mm | Ensures good bed adhesion |
| Line Width | 0.40mm (0.4mm nozzle) / 0.22mm (0.2mm nozzle) | Match to nozzle diameter |
| Wall Loops | 3 | Provides structural integrity for thin features |
| Top/Bottom Layers | 5 | Solid top surfaces, avoids pillowing |
| Infill | 15-20% Gyroid | Light but structurally sound |
| Print Speed (Outer Wall) | 30 mm/s | Slow for maximum surface quality |
| Print Speed (Inner Wall) | 50 mm/s | Can be slightly faster |
| Print Speed (Infill) | 80 mm/s | Speed up non-visible areas |
| Print Speed (Support) | 80 mm/s | Supports do not need fine quality |
| Travel Speed | 150 mm/s | Reduce stringing |
| Retraction Distance | 0.8mm (direct drive) | P1S uses direct drive extruder |
| Retraction Speed | 30 mm/s | Reliable retraction for fine work |
| Z Hop | 0.4mm | Prevents nozzle dragging on small features |
| Cooling Fan | 100% after layer 3 | Maximum cooling for fine detail and overhangs |
| Bed Temperature | 55°C (PLA) | Standard PLA bed temp |
| Nozzle Temperature | 210-215°C (PLA) | Slightly lower for fine layers |
| Acceleration | 2000 mm/s² (outer wall) | Reduce ringing artifacts on fine detail |
| Jerk | 8 mm/s | Smooth motion for surface quality |

#### Print Settings: Gaming Quality (0.12mm)

Use for batch-printing tabletop gaming units where throughput matters more than absolute perfection.

| Setting | Value | Notes |
|---------|-------|-------|
| Layer Height | 0.12mm | Excellent balance of speed and quality |
| First Layer Height | 0.20mm | Good bed adhesion |
| Line Width | 0.40mm | Standard for 0.4mm nozzle |
| Wall Loops | 2-3 | 2 for small minis, 3 for larger ones |
| Top/Bottom Layers | 4 | Sufficient for solid surfaces |
| Infill | 10-15% Gyroid | Lighter fill for faster prints |
| Print Speed (Outer Wall) | 40-50 mm/s | Faster than display quality |
| Print Speed (Inner Wall) | 60 mm/s | Can push speed on inner walls |
| Print Speed (Infill) | 100 mm/s | Maximize speed on hidden areas |
| Travel Speed | 200 mm/s | P1S handles high travel speeds well |
| Retraction Distance | 0.8mm | Same as display quality |
| Cooling Fan | 100% after layer 2 | Full cooling is always critical for minis |
| Bed Temperature | 55°C | Standard PLA |
| Nozzle Temperature | 215°C | Standard PLA range |
| Acceleration | 3000 mm/s² | Slightly higher for faster prints |

#### Nozzle Selection Guide

| Nozzle Size | Best For | Trade-off |
|-------------|----------|-----------|
| 0.2mm | Ultra-fine detail (20-28mm miniatures) | Slower prints, prone to clogging |
| 0.4mm (stock) | General purpose miniatures (28-75mm) | Good balance of speed and detail |
| 0.6mm | Large display pieces (75mm+), terrain | Faster but visible loss of fine detail |

**0.2mm nozzle tips for P1S:**
- Reduce print speed to 20-30 mm/s for outer walls.
- Set layer height to 0.04-0.08mm.
- Use a hardened steel 0.2mm nozzle to avoid wear from abrasive filaments.
- Clean the nozzle frequently (cold pulls every 10-15 hours of printing).

#### Filament Recommendations

| Filament | Pros | Cons | Best For |
|----------|------|------|----------|
| PLA | Easy to print, holds fine detail | Brittle, low heat resistance | General miniatures |
| PLA+ | Slightly tougher than PLA, same ease | Marginally more expensive | Gaming minis that get handled |
| PETG | Tough, flexible, good layer adhesion | Strings more, slightly less detail | Durable terrain, large pieces |
| ABS | Strong, sandable, paintable | Requires enclosure, warps easily | Post-processed display pieces |
| Matte PLA | Hides layer lines naturally | May clog fine nozzles | Gaming minis without post-processing |

### Step 5: Printing on Bambu Lab P1S

1. Load PLA/PLA+ filament.
2. Clean build plate with IPA wipe.
3. Apply thin glue stick layer for adhesion.
4. Start print, monitor first 5 layers.
5. Total time: 1-6 hours depending on size and quality tier.

### Step 6: Post-Processing

#### Quick Tabletop Workflow (30-60 minutes per mini)

1. **Support Removal (5-10 min):** Use flush cutters to clip supports close to model. Use sharp hobby knife (X-Acto #11 blade) to trim remaining nubs. For stubborn marks, use heated hobby knife tip to melt and smooth.
2. **Quick Sand (5-10 min):** Use 220-grit sandpaper on visible flat surfaces and large layer-line areas. Use needle files for tight crevices. Do NOT sand detailed areas (face, armor engravings).
3. **Prime (10-15 min + drying):** Apply 2 thin coats of spray filler primer (Rust-Oleum Filler Primer or Tamiya Surface Primer). Hold can 8-10 inches from model. Light sweeping passes. Allow 30 minutes between coats. Primer color: grey for general use, white for bright colors, black for dark schemes or zenithal priming.
4. **Base Coat and Paint (15-30 min):** Use acrylic paints (Citadel, Vallejo, Army Painter, or craft acrylics). Thin paints with water (2:1 paint-to-water ratio starting point). Apply 2-3 thin coats rather than 1 thick coat. Paint largest areas first (skin, armor, cloth), then details (eyes, gems, buckles).
5. **Quick Shade (5 min):** Apply a wash (thinned dark paint or commercial wash like Citadel Nuln Oil) over entire miniature. Wash flows into recesses creating instant shadow and depth. Allow to dry completely (15-30 minutes).
6. **Varnish (5 min + drying):** Apply matte spray varnish (Testors Dullcote or Vallejo Matte Varnish). 1-2 light coats protect paint job from handling. Allow 24 hours full cure before handling.

#### Display Quality Workflow (2-4 hours per mini)

1. **Support Removal and Cleanup (15-20 min):** Same as quick workflow but more thorough. Fill visible gaps or seams with liquid green stuff or Milliput two-part putty. Allow filler to cure (15-60 min depending on product).
2. **Progressive Sanding (20-30 min):** Wet sand with 120-grit to remove major layer lines and support scars. Progress through 240, 400, 600, and 800 grit. Use wet sanding (dip sandpaper in water) to prevent dust. Rinse model between grit changes.
3. **Filler Primer and Inspection (20-30 min):** Apply filler primer (2-3 coats). After each coat dries, inspect under bright light for remaining imperfections. Lightly sand with 800-grit between primer coats. Repeat until satisfied.
4. **Zenithal Priming (10-15 min):** Spray entire model with black primer. Once dry, spray white primer from above at 45° angle (simulating sunlight). Creates natural gradient that guides painting and reveals surface detail.
5. **Layered Painting (60-120 min):** Apply base coats over zenithal prime. Layer progressively lighter colors on raised surfaces for highlights. Apply washes/inks into recesses for shadows. Dry brush edges and raised details with lighter shade. Paint fine details (eyes, gems, runes) with size 0 or 00 brush. Apply edge highlighting on armor, weapons, and sharp edges.
6. **Basing (15-30 min):** Apply PVA glue to miniature's base. Press base into texture material (sand, gravel, static grass). Shake off excess, allow to dry. Paint base to match desired terrain.

### Step 7: Finding Pre-Made 3D Models

If the user wants to find existing miniatures rather than create from scratch:

**Paid Marketplaces:**

| Marketplace | Specialty | URL |
|------------|-----------|-----|
| MyMiniFactory | Tabletop gaming, curated | myminifactory.com |
| Cults3D | Large marketplace | cults3d.com |
| Loot Studios | Monthly curated packs | lootstudios.com |
| Titan Forge | Wargaming armies | titanforgeminiatures.com |

**Free Repositories:**

| Repository | Specialty | URL |
|------------|-----------|-----|
| Thingiverse | Massive community collection | thingiverse.com |
| Printables | Prusa-backed, growing fast | printables.com |
| MiniHoarder | Tabletop-specific aggregator | minihoarder.com |

**Search Engines:**

| Engine | Description | URL |
|--------|-------------|-----|
| Yeggi | Aggregates results from all major repositories | yeggi.com |
| Thangs | AI-powered search across multiple platforms | thangs.com |

**Notable Free Creators:**
- **mz4250:** Massive collection of D&D monsters and NPCs on Thingiverse/Shapeways. Definitive free D&D miniature library.
- **PrintedObsession:** High-quality free terrain and dungeon tiles.
- **Wargaming3D (community):** Open-source historical wargaming models on GitHub.

**Search Tips:**
- Use scale keywords: "28mm", "32mm", "heroic scale", "tabletop"
- Use game keywords: "D&D", "Pathfinder", "Warhammer", "AoS", "40k"
- Use type keywords: "pre-supported", "multi-part", "presupported"
- Filter by "most downloaded" or "most makes" for proven printability
- Check the "makes" or "prints" gallery to see how it prints on different printers

## Pitfalls

### AI Mesh Issues (Always Present)
- **AI meshes always need cleanup before printing.** Never print an AI-generated mesh directly without Blender cleanup.
- Non-manifold edges: Run trimesh repair script or use Blender Mesh > Clean Up > Make Manifold.
- Interior faces: Select and delete in Blender.
- Intersecting geometry: Boolean union to merge overlapping regions.
- Missing bottom (no flat base): Add cylinder base in Blender, Boolean union.
- Extreme polygon count (>1M): Decimate in Blender (ratio 0.3-0.5) or use trimesh script.

### Print Quality Issues

| Problem | Likely Cause | Solution |
|---------|-------------|----------|
| Visible layer lines | Layer height too high or insufficient post-processing | Use 0.08mm layers or apply filler primer |
| Stringing between parts | Retraction settings too low, temperature too high | Increase retraction to 1.0mm, reduce temp by 5°C |
| Broken thin features | Walls too thin, print speed too fast | Add wall loops, slow outer wall to 25mm/s |
| Failed overhangs | Insufficient cooling or supports | Ensure 100% fan, add manual supports |
| Warping at base | Bed adhesion issues | Use glue stick, increase first layer temp by 5°C |
| Elephants foot | First layer squished too hard | Calibrate Z offset, add 0.1mm elephant foot compensation |
| Support marks on face | Poor orientation or support placement | Rotate model so face points up, use support blockers |
| Fuzzy surface | Too much moisture in filament | Dry filament at 50°C for 4-6 hours before printing |

### Critical Warnings
- **Thin features under 1.5mm will likely break on FDM.** Always use Solidify modifier with minimum 1.5mm thickness.
- **0.2mm nozzle clogs easily.** Recommend cleaning routine: cold pulls every 10-15 hours of printing.
- **Always do a test print of the most complex area first** before committing to a full print.
- **Scale matters.** Always confirm target scale before any work begins. A beautiful sculpt at the wrong scale is useless for tabletop gaming.
- **Never say "adjust your settings."** Always give exact values from the settings tables in this skill.
- **Do NOT sand detailed areas** (face, armor engravings) as this removes detail.

## Verification

### Mesh Readiness Checklist
Before slicing, verify:
1. Mesh is manifold (watertight): Run 3D Print Toolbox > Check All in Blender. Output should show 0 non-manifold edges, 0 holes.
2. Polygon count is within target: 200k-500k faces for FDM miniatures.
3. Thin features are at least 1.5mm thick.
4. Model has a flat base sitting on the build plate (origin at bottom center).
5. Model is scaled to correct tabletop scale (feet to eye level measurement matches reference).

### Print Readiness Checklist
Before starting the print, verify:
1. Face and most detailed surfaces face upward (away from supports).
2. Tree supports enabled with 40-45° threshold angle.
3. Manual support blockers painted on face and detailed front surfaces.
4. Manual support enforcers painted under extended arms and weapons.
5. Quality tier selected: 0.08mm (display) or 0.12mm (gaming).
6. Cooling fan set to 100% after layer 2-3.
7. Glue stick applied to build plate.
8. Preview sliced layers in Bambu Studio to check for issues before printing.

### Post-Print Verification
1. Supports removed cleanly with no damage to model surface.
2. No visible layer line gaps or stringing on detailed surfaces.
3. Thin features (weapons, fingers) intact and unbroken.
4. Model stands flat on its base without wobbling.
5. Scale matches reference miniature when placed side by side.

## Examples

### Quick End-to-End Workflow Summary

```
1. CONCEPT
   ├── Reference image or sketch
   ├── AI generation (Meshy/Tripo) OR digital sculpt (Blender/ZBrush)
   └── Output: raw 3D mesh

2. MESH PREPARATION
   ├── Import into Blender
   ├── Fix non-manifold geometry (3D Print Toolbox)
   ├── Thicken thin features (Solidify modifier, min 1.5mm)
   ├── Scale to target (28mm/32mm/54mm)
   ├── Center on build plate (origin to bottom center)
   ├── Split into parts if needed (Boolean operations)
   ├── Add alignment keys (peg/hole, 2mm diameter)
   └── Export as STL

3. SLICING (Bambu Studio)
   ├── Import STL
   ├── Set quality tier (0.08mm display / 0.12mm gaming)
   ├── Configure supports (tree, 40-45° threshold)
   ├── Paint manual supports (block face, force underarms)
   ├── Adjust orientation for best surface quality
   ├── Preview layer-by-layer for issues
   └── Send to printer

4. PRINTING (Bambu P1S)
   ├── Load PLA/PLA+ filament
   ├── Clean build plate (IPA wipe)
   ├── Apply thin glue stick layer
   ├── Start print, monitor first 5 layers
   └── Total time: 1-6 hours depending on size and quality

5. POST-PROCESSING
   ├── Remove supports (flush cutters + hobby knife)
   ├── Sand (220 → 400 → 600 → 800 grit, wet)
   ├── Fill seams if multi-part (green stuff / Milliput)
   ├── Prime (2-3 coats filler primer)
   ├── Paint (thin acrylics, base → wash → highlight)
   ├── Varnish (matte for gaming, gloss for effects)
   └── Base (texture + paint + flock/grass)

6. DONE: Table-ready miniature
```

### Tool Recommendations by Experience Level

- **Beginner:** Meshy (AI) + Bambu Studio (slicing) + basic post-processing.
- **Intermediate:** Blender (sculpting/cleanup) + manual support painting.
- **Advanced:** ZBrush (sculpting) + multi-part assembly + display-quality finishing.

### Post-Processing Depth by End Use

- **Gaming (handled frequently):** Quick workflow with matte varnish.
- **Display:** Full workflow with zenithal priming and layered painting.
- **Gift:** Display workflow plus custom base and presentation box.
