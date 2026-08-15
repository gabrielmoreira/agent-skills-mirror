---
name: 3d-vase-mode-art
description: "Generates single-wall spiral vase STLs (sine, twisted polygon, Gielis superformula) and Bambu Studio/Cura/PrusaSlicer Spiralize Outer Contour settings for decorative prints, LED lamp shades, and manual/gradient multi-color bands. Use when the user asks for vase mode, spiral vase, parametric vase STLs, or translucent lamp-shade prints. Not for tabletop miniatures (3d-miniature-figurine), photo-to-mesh conversion (3d-image-to-model), or AMS automatic color swaps on a pure spiral path."
version: 1.0.1
---

# Vase Mode / Spiral Art for 3D Printing

## Overview

Vase mode — also called **Spiralize Outer Contour** (Cura/Bambu Studio) or **Spiral Vase** (PrusaSlicer) — is a specialized 3D printing technique that produces hollow, single-walled objects in one continuous, uninterrupted spiral motion. The printer head never retracts or lifts; the Z-axis rises gradually as the nozzle traces the outer contour, producing one continuous strand of filament from bottom to top.

| Aspect | Standard Printing | Vase Mode |
|---|---|---|
| **Layers** | Discrete start/stop per layer | Continuous Z-rise spiral |
| **Walls** | Multiple perimeters + infill | Single outer wall only |
| **Z-Seam** | Visible vertical line | Eliminated entirely |
| **Top layers** | Solid top shell | None (open top) |
| **Infill** | Configurable percentage | 0% (hollow) |
| **Speed** | Normal | Often faster (no travel moves) |

### Requirements and Limitations

- Model must have a **single, continuous cross-section** at every height
- No overhangs, handles, bridges, or detached internal geometry
- No multiple shells or internal cavities
- Bottom layers are printed normally (3–5 solid layers for a stable base)
- Objects are inherently fragile — single-wall thickness only
- Best suited for **decorative** rather than functional objects

### Ideal Objects

- Vases and planters
- Lamp shades and light diffusers
- Pencil/pen holders
- Sculptural art pieces
- Decorative bowls
- Geometric sculptures
- Candle holders

## When to Use

Trigger this skill when the user mentions any of:

- "vase mode", "spiral vase", "spiralize outer contour"
- Generating parametric or mathematical vase STLs
- Bambu Studio / PrusaSlicer / Cura vase mode settings
- LED lamp shade 3D printing
- Multi-color vase printing workarounds
- OpenSCAD or Python vase generation
- Superformula / Gielis surface generation for 3D printing

## Prerequisites

### Python Environment (for STL generation)

```powershell
pip install numpy numpy-stl
```

### Slicer

- **Bambu Studio** (primary reference; 2.0+ recommended for Smooth Spiral)
- PrusaSlicer or Cura also support equivalent "Spiral Vase" mode

### Windows Host Notes

- Commands shown are PowerShell-compatible
- Python scripts can be saved anywhere; run from the project directory
- STL output paths should use backslashes or forward slashes — both work in Python on Windows

## Procedure

### Step 1: Determine the Goal

Identify what the user wants to create:

1. **Decorative vase** — standard single-wall object
2. **Lamp shade** — translucent material, even wall thickness, LED integration
3. **Planter** — thicker walls, more bottom layers
4. **Sculptural art** — exotic mathematical surfaces

### Step 2: Select the Generation Approach

| Goal | Recommended Approach |
|---|---|
| Simple twisted shapes | OpenSCAD with `linear_extrude` |
| Complex math surfaces | Python with `numpy-stl` |
| Exotic organic shapes | Superformula generator |
| Polygon cross-sections | Twisted polygon generator |

### Step 3: Mathematical Surface Generation

A vase is a **surface of revolution** where the radius varies as a function of both height (`z`) and angle (`θ`).

#### Core Parametric Equations

```
x(θ, z) = r(θ, z) · cos(θ + twist(z))
y(θ, z) = r(θ, z) · sin(θ + twist(z))
z(θ, z) = z
```

Where `r(θ, z)` is the radius function and `twist(z)` adds rotational offset.

#### Common Radius Functions

**Simple Sine Wave Vase:**

```
r(θ, z) = base_radius + amplitude · sin(n · θ + phase · z)
```

- `n` controls the number of lobes around the circumference
- `phase · z` rotates the pattern as height increases (twist)
- `amplitude` controls the depth of the wave

**Twisted Polygon Vase:**

```
r(θ, z) = base_radius / cos(mod(θ + twist_rate · z, 2π/sides) - π/sides)
```

- Creates a polygon cross-section that twists with height
- `sides` = number of polygon sides
- `twist_rate` = radians of rotation per unit height

**Fractal/Noise Vase:**

```
r(θ, z) = base_radius + Σ(aᵢ · sin(nᵢ · θ + φᵢ · z))
```

- Sum of multiple sine waves at different frequencies creates organic, fractal-like surfaces
- Each term `i` has its own amplitude `aᵢ`, frequency `nᵢ`, and phase `φᵢ`

**Superformula Vase (Gielis Superformula):**

```
r(θ) = ( |cos(m·θ/4)/a|^n2 + |sin(m·θ/4)/b|^n3 )^(-1/n1)
```

- Generates an enormous variety of natural-looking shapes
- Parameters `m`, `n1`, `n2`, `n3`, `a`, `b` control the form

### Step 4: Generate the STL

#### 4a. Sine Wave Vase Generator

Save as `generate_sine_vase.py` and run:

```powershell
python generate_sine_vase.py
```

```python
"""
Parametric Sine Wave Vase Generator
Generates a single-shell STL suitable for vase mode printing.
"""
import numpy as np
from stl import mesh

def generate_sine_vase(
    height: float = 100.0,
    base_radius: float = 30.0,
    amplitude: float = 8.0,
    lobes: int = 5,
    twist_rate: float = 0.03,
    z_profile_func=None,
    n_theta: int = 200,
    n_z: int = 300,
    output_file: str = "sine_vase.stl",
) -> None:
    """
    Generate a sine-wave vase and export as STL.

    Args:
        height: Total vase height in mm.
        base_radius: Average radius in mm.
        amplitude: Sine wave amplitude in mm.
        lobes: Number of sine lobes around circumference.
        twist_rate: Twist in radians per mm of height.
        z_profile_func: Optional callable(z, height) -> scale factor for radius.
        n_theta: Angular resolution (number of points around circumference).
        n_z: Vertical resolution (number of layers).
        output_file: Output STL filename.
    """
    if z_profile_func is None:
        # Default: slight hourglass shape
        def z_profile_func(z: float, h: float) -> float:
            t = z / h
            return 0.7 + 0.6 * (t - 0.3) ** 2

    theta = np.linspace(0, 2 * np.pi, n_theta, endpoint=False)
    z_vals = np.linspace(0, height, n_z)

    # Build vertex grid: shape (n_z, n_theta, 3)
    vertices = np.zeros((n_z, n_theta, 3))
    for i, z in enumerate(z_vals):
        profile_scale = z_profile_func(z, height)
        twist = twist_rate * z
        for j, th in enumerate(theta):
            r = (base_radius + amplitude * np.sin(lobes * th + twist * lobes)) * profile_scale
            vertices[i, j, 0] = r * np.cos(th + twist)
            vertices[i, j, 1] = r * np.sin(th + twist)
            vertices[i, j, 2] = z

    # Build triangular faces
    faces = []
    for i in range(n_z - 1):
        for j in range(n_theta):
            j_next = (j + 1) % n_theta
            # Two triangles per quad
            v0 = vertices[i, j]
            v1 = vertices[i, j_next]
            v2 = vertices[i + 1, j_next]
            v3 = vertices[i + 1, j]
            faces.append([v0, v1, v2])
            faces.append([v0, v2, v3])

    # Add bottom cap
    bottom_center = np.array([0.0, 0.0, 0.0])
    for j in range(n_theta):
        j_next = (j + 1) % n_theta
        faces.append([bottom_center, vertices[0, j_next], vertices[0, j]])

    # Convert to numpy-stl mesh
    face_array = np.array(faces)
    stl_mesh = mesh.Mesh(np.zeros(face_array.shape[0], dtype=mesh.Mesh.dtype))
    for i, f in enumerate(face_array):
        stl_mesh.vectors[i] = f

    stl_mesh.save(output_file)
    print(f"Saved vase to {output_file} ({len(face_array)} triangles)")


if __name__ == "__main__":
    # Example 1: Classic sine wave vase
    generate_sine_vase(
        height=120,
        base_radius=35,
        amplitude=10,
        lobes=6,
        twist_rate=0.02,
        output_file="classic_sine_vase.stl",
    )

    # Example 2: Dramatic twist vase
    generate_sine_vase(
        height=150,
        base_radius=30,
        amplitude=5,
        lobes=4,
        twist_rate=0.08,
        output_file="twisted_vase.stl",
    )

    # Example 3: Organic profile vase
    def organic_profile(z: float, h: float) -> float:
        t = z / h
        return 0.5 + 0.5 * np.sin(t * np.pi) + 0.1 * np.sin(3 * t * np.pi)

    generate_sine_vase(
        height=130,
        base_radius=40,
        amplitude=12,
        lobes=7,
        twist_rate=0.04,
        z_profile_func=organic_profile,
        output_file="organic_vase.stl",
    )
```

#### 4b. Twisted Polygon Vase Generator

Save as `generate_twisted_polygon_vase.py` and run:

```powershell
python generate_twisted_polygon_vase.py
```

```python
"""
Twisted Polygon Vase Generator
Creates a polygon cross-section that twists along the Z axis.
"""
import numpy as np
from stl import mesh

def generate_twisted_polygon_vase(
    height: float = 120.0,
    radius: float = 35.0,
    sides: int = 5,
    twist_degrees: float = 90.0,
    corner_radius: float = 3.0,
    n_theta: int = 200,
    n_z: int = 250,
    output_file: str = "twisted_polygon_vase.stl",
) -> None:
    """
    Generate a twisted polygon vase.

    Args:
        height: Vase height in mm.
        radius: Inscribed circle radius in mm.
        sides: Number of polygon sides.
        twist_degrees: Total twist from bottom to top.
        corner_radius: Smoothing radius for corners.
        n_theta: Angular resolution.
        n_z: Vertical resolution.
        output_file: Output filename.
    """
    twist_total = np.radians(twist_degrees)
    theta = np.linspace(0, 2 * np.pi, n_theta, endpoint=False)
    z_vals = np.linspace(0, height, n_z)

    vertices = np.zeros((n_z, n_theta, 3))
    for i, z in enumerate(z_vals):
        t = z / height
        twist = twist_total * t
        # Slight taper: wider in middle
        scale = 0.8 + 0.4 * np.sin(t * np.pi)
        for j, th in enumerate(theta):
            # Polygon radius with smoothed corners
            angle_in_sector = ((th + twist) % (2 * np.pi / sides)) - np.pi / sides
            r = radius / np.cos(angle_in_sector)
            # Smooth corners using min with circle
            r = min(r, radius + corner_radius)
            r *= scale
            vertices[i, j, 0] = r * np.cos(th)
            vertices[i, j, 1] = r * np.sin(th)
            vertices[i, j, 2] = z

    # Build faces
    faces = []
    for i in range(n_z - 1):
        for j in range(n_theta):
            j_next = (j + 1) % n_theta
            v0, v1 = vertices[i, j], vertices[i, j_next]
            v2, v3 = vertices[i + 1, j_next], vertices[i + 1, j]
            faces.append([v0, v1, v2])
            faces.append([v0, v2, v3])

    # Bottom cap
    center = np.array([0.0, 0.0, 0.0])
    for j in range(n_theta):
        j_next = (j + 1) % n_theta
        faces.append([center, vertices[0, j_next], vertices[0, j]])

    face_array = np.array(faces)
    stl_mesh = mesh.Mesh(np.zeros(face_array.shape[0], dtype=mesh.Mesh.dtype))
    for i, f in enumerate(face_array):
        stl_mesh.vectors[i] = f

    stl_mesh.save(output_file)
    print(f"Saved twisted polygon vase to {output_file}")


if __name__ == "__main__":
    generate_twisted_polygon_vase(sides=5, twist_degrees=90, output_file="pentagon_twist.stl")
    generate_twisted_polygon_vase(sides=3, twist_degrees=120, output_file="triangle_twist.stl")
    generate_twisted_polygon_vase(sides=6, twist_degrees=60, output_file="hexagon_twist.stl")
```

#### 4c. Superformula Vase Generator

Save as `generate_superformula_vase.py` and run:

```powershell
python generate_superformula_vase.py
```

```python
"""
Superformula Vase Generator
Uses the Gielis superformula for exotic natural shapes.
"""
import numpy as np
from stl import mesh

def superformula(theta: float, m: float, n1: float, n2: float, n3: float,
                 a: float = 1.0, b: float = 1.0) -> float:
    """Compute the Gielis superformula radius for a given angle."""
    t1 = np.abs(np.cos(m * theta / 4.0) / a)
    t2 = np.abs(np.sin(m * theta / 4.0) / b)
    r = (t1 ** n2 + t2 ** n3) ** (-1.0 / n1)
    return r

def generate_superformula_vase(
    height: float = 120.0,
    scale: float = 30.0,
    m: float = 6.0,
    n1: float = 1.0,
    n2: float = 1.0,
    n3: float = 1.0,
    twist_rate: float = 0.02,
    n_theta: int = 300,
    n_z: int = 300,
    output_file: str = "superformula_vase.stl",
) -> None:
    """Generate a vase using the Gielis superformula cross-section."""
    theta = np.linspace(0, 2 * np.pi, n_theta, endpoint=False)
    z_vals = np.linspace(0, height, n_z)

    vertices = np.zeros((n_z, n_theta, 3))
    for i, z in enumerate(z_vals):
        t = z / height
        twist = twist_rate * z
        profile = 0.6 + 0.8 * np.sin(t * np.pi)
        for j, th in enumerate(theta):
            r = superformula(th + twist, m, n1, n2, n3) * scale * profile
            vertices[i, j, 0] = r * np.cos(th)
            vertices[i, j, 1] = r * np.sin(th)
            vertices[i, j, 2] = z

    faces = []
    for i in range(n_z - 1):
        for j in range(n_theta):
            j_next = (j + 1) % n_theta
            v0, v1 = vertices[i, j], vertices[i, j_next]
            v2, v3 = vertices[i + 1, j_next], vertices[i + 1, j]
            faces.append([v0, v1, v2])
            faces.append([v0, v2, v3])

    center = np.array([0.0, 0.0, 0.0])
    for j in range(n_theta):
        j_next = (j + 1) % n_theta
        faces.append([center, vertices[0, j_next], vertices[0, j]])

    face_array = np.array(faces)
    stl_mesh = mesh.Mesh(np.zeros(face_array.shape[0], dtype=mesh.Mesh.dtype))
    for i, f in enumerate(face_array):
        stl_mesh.vectors[i] = f

    stl_mesh.save(output_file)
    print(f"Saved superformula vase to {output_file}")


if __name__ == "__main__":
    # Starfish shape
    generate_superformula_vase(m=5, n1=2, n2=7, n3=7, output_file="starfish_vase.stl")
    # Flower petal shape
    generate_superformula_vase(m=8, n1=0.5, n2=0.5, n3=8, output_file="flower_vase.stl")
    # Organic blob
    generate_superformula_vase(m=3, n1=4.5, n2=10, n3=10, output_file="organic_blob_vase.stl")
```

#### 4d. OpenSCAD Twisted Vase (Alternative)

For simple shapes without Python, use OpenSCAD:

```openscad
// Twisted Star Vase for Vase Mode
$fn = 200;

height = 120;
base_r = 30;
lobes = 5;
amplitude = 8;
twist = 90; // degrees total twist

module vase_slice(z) {
    t = z / height;
    profile = 0.6 + 0.8 * sin(t * 180);
    twist_angle = twist * t;

    rotate([0, 0, twist_angle])
    hull() {
        for (a = [0:360/lobes:359]) {
            rotate([0, 0, a])
            translate([base_r * profile + amplitude * profile, 0, 0])
            circle(r = 0.5);
        }
    }
}

module vase() {
    step = 0.5;
    for (z = [0:step:height]) {
        translate([0, 0, z])
        linear_extrude(height = step + 0.01)
        vase_slice(z);
    }
}

vase();
```

### Step 5: Profile Functions for Z-Axis Shaping

Use these as the `z_profile_func` parameter in the sine wave generator:

```python
# Hourglass: narrow in the middle
def hourglass(z: float, h: float) -> float:
    t = z / h
    return 0.6 + 0.8 * (2 * t - 1) ** 2

# Trumpet: flares at the top
def trumpet(z: float, h: float) -> float:
    t = z / h
    return 0.5 + 1.5 * t ** 2

# Bulge: wide belly
def bulge(z: float, h: float) -> float:
    t = z / h
    return 0.6 + 0.8 * np.sin(t * np.pi)

# S-curve: two bulges
def s_curve(z: float, h: float) -> float:
    t = z / h
    return 0.6 + 0.4 * np.sin(2 * t * np.pi)

# Straight cylinder
def cylinder(z: float, h: float) -> float:
    return 1.0

# Tapered cone
def cone(z: float, h: float) -> float:
    t = z / h
    return 0.5 + t
```

### Step 6: Configure Bambu Studio Vase Mode Settings

1. Open **Bambu Studio** and load your model
2. Go to **Process Settings** → **Others** tab
3. Under **Special Mode**, enable **Spiral Vase**
4. Enable **Smooth Spiral** (available in Bambu Studio 2.0+) to eliminate Z-seam artifacts

**Automatic adjustments when enabled:**
- Wall loops: **1**
- Top shell layers: **0**
- Infill density: **0%**
- Only bottom layers remain solid

**Recommended settings by application:**

| Setting | Decorative Vase | Lamp Shade | Planter |
|---|---|---|---|
| **Layer Height** | 0.20 mm | 0.12–0.16 mm | 0.20 mm |
| **Line Width** | 0.45–0.60 mm | 0.50–0.60 mm | 0.60–0.80 mm |
| **Outer Wall Speed** | 40–50 mm/s | 25–30 mm/s | 40 mm/s |
| **Bottom Layers** | 3–4 | 4–5 | 5–6 |
| **Nozzle Temp** | Standard | 5°C lower | Standard |
| **Flow Rate** | 100–105% | 100% | 105–110% |

**Tips for better results:**
- **Wider lines** (0.6mm+ on a 0.4mm nozzle) create thicker, more rigid walls
- **Slower speeds** on the outer wall improve surface quality, especially for translucent materials
- **Increase flow** by 5–10% to ensure good layer bonding with wider lines
- **Use a textured plate** for the first layer if using PLA to prevent sticking issues
- **Ensure a stable base** with enough bottom solid layers (at least 4)

### Step 7: LED Lamp Shade Integration

#### Translucent Materials

| Material | Translucency | Notes |
|---|---|---|
| **Natural/Clear PLA** | High | Best light diffusion; moisture-sensitive |
| **Translucent PETG** | Medium-High | Better temperature resistance near LEDs |
| **Silk PLA** | Medium | Beautiful shimmer effect when backlit |
| **Marble PLA** | Low-Medium | Creates interesting shadow patterns |
| **Glow-in-dark PLA** | Medium | Charges from LEDs, glows after off |

#### Print Settings for Lamp Shades

- **Layer height**: 0.12–0.16 mm for smooth, even light diffusion
- **Line width**: 0.50–0.60 mm for consistent wall thickness
- **Speed**: 25–30 mm/s for outer wall clarity
- **Temperature**: 5–10°C lower than normal to reduce bubbling
- **Dry filament**: Moisture causes bubbles that scatter light unevenly

#### LED Integration Methods

1. **Battery-powered LED puck**: Place under the vase; simplest approach
2. **LED strip coil**: Wind an LED strip inside the vase base cavity
3. **Dedicated lamp base**: Design a separate base with LED holder socket
4. **Smart bulb adapter**: Design the vase top to fit a standard E26/E27 socket

#### Design Considerations

- Keep wall thickness uniform for even light distribution
- Avoid sharp corners that create bright spots
- Taller vases need a wider base for stability with LED hardware inside
- Geometric patterns (sine waves, polygons) create stunning shadow projections

### Step 8: Multi-Color Vase Mode Techniques

**The Limitation:** Standard vase mode is a **continuous single-path** process. The printer cannot stop to purge filament (required for AMS color switching) without creating a visible seam or scar in the wall. Therefore, **automated multi-color is not natively supported** in pure spiral vase mode.

**Workarounds:**

1. **Manual Filament Swap (Pause Method)**
   - Insert a **Pause** or **Filament Change** at a specific layer height in the slicer
   - When the printer pauses, cut and manually swap the filament
   - Creates a visible color transition line at the change point
   - Best for **horizontal color bands** (bottom half one color, top half another)

2. **Gradient / Rainbow Filament**
   - Use multi-color or gradient filament (e.g., rainbow PLA, tri-color silk)
   - Achieves smooth color transitions **without any pauses**
   - The transition pattern depends on the filament's color-change cycle length
   - Best for **organic, flowing color** effects

3. **Filament Splicing**
   - Manually splice different colored filament segments together on the same spool
   - Precise timing is difficult but allows planned color blocks
   - Use a filament welder or heat splice technique

4. **Dual-Extruder Side-by-Side (Non-AMS)**
   - Some printers support a second extruder for vase mode
   - One color per extruder, alternating per layer or section

## Examples

### Shape Catalog

| Shape Name | Parameters | Visual Effect |
|---|---|---|
| **Sine Wave 5-Lobe** | lobes=5, amp=8, twist=0.03 | Star-like cross section, gentle twist |
| **Twisted Triangle** | sides=3, twist=120° | Dramatic triangular spiral |
| **Twisted Hexagon** | sides=6, twist=45° | Subtle geometric elegance |
| **Starfish** | superformula m=5, n1=2 | Organic sea-creature shape |
| **Flower Petal** | superformula m=8, n1=0.5 | Botanical petal pattern |
| **Double Helix** | Two interleaved sine waves | DNA-like spiral pattern |
| **Fractal Noise** | Sum of 5+ sine terms | Organic, irregular surface |
| **Hourglass** | Profile: pinch at middle | Classic narrow-waist silhouette |
| **Trumpet** | Profile: exponential flare at top | Wide opening, narrow base |
| **Egg** | Profile: elliptical | Smooth, organic shell |

## Pitfalls

| Issue | Cause | Solution |
|---|---|---|
| Visible Z-seam line | Smooth Spiral not enabled | Enable Smooth Spiral in Bambu Studio |
| Thin/weak walls | Line width too narrow | Increase line width to 0.5–0.6mm |
| Gaps between layers | Under-extrusion | Increase flow rate 5–10% |
| Base pops off plate | Insufficient bottom layers | Use 4–5 bottom solid layers |
| Model has holes | Non-manifold mesh | Repair in MeshLab or PrusaSlicer |
| Cloudy translucent print | Wet filament, bubbles | Dry filament before printing |
| Uneven wall thickness | Inconsistent extrusion | Calibrate extruder, check nozzle |
| Slicer ignores vase mode | Model has internal geometry | Simplify model to single shell |
| AMS multi-color fails | Vase mode is single continuous path | Use manual pause swap or gradient filament instead |
| Sharp corners create bright spots | Uneven wall thickness at corners | Use corner_radius smoothing in polygon generator |

**HARD RULES:**
- Always generate **watertight meshes** with a solid bottom cap
- Never produce models with internal geometry, multiple shells, or detached cavities — the slicer will reject vase mode
- Test the STL in the slicer preview before recommending it for printing
- Do not recommend AMS automated color switching for pure spiral vase mode — it will create visible seams

## Verification

### Verify STL Generation

After running any generator script, confirm the output:

```powershell
# Check file exists and has reasonable size
dir *.stl

# Quick Python check for mesh validity
python -c "from stl import mesh; m = mesh.Mesh.from_file('classic_sine_vase.stl'); print(f'Triangles: {len(m.vectors)}'); print(f'Closed: {m.is_closed()}')"
```

Expected output:
```
Triangles: 119800
Closed: True
```

(Triangle count will vary by parameters; `is_closed()` must return `True`.)

### Verify Slicer Settings

In Bambu Studio after enabling Spiral Vase:

1. Confirm **Wall loops = 1** (auto-set)
2. Confirm **Top shell layers = 0** (auto-set)
3. Confirm **Infill density = 0%** (auto-set)
4. Confirm **Smooth Spiral** is enabled (Bambu Studio 2.0+)
5. Preview the toolpath — it should show a **single continuous spiral** with no Z-seam dots

### Verify Print Readiness

- Slice the model and check the preview for any travel moves (there should be none in the spiral portion)
- Confirm bottom solid layers are present (3–6 depending on application)
- Confirm no top shell exists
- Check estimated print time is reasonable (vase mode is typically faster than standard)

## Related Skills

- **3d-printing-fdm-basics** — general FDM print setup and calibration
- **bambu-studio-slicer-settings** — detailed Bambu Studio configuration
- **openscad-parametric-modeling** — OpenSCAD for procedural geometry
- **3d-printing-materials-guide** — filament selection including translucent materials
