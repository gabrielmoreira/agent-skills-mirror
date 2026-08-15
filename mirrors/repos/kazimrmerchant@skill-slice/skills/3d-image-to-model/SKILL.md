---
name: 3d-image-to-model
description: "Converts a 2D image, photo set, or SVG into a 3D mesh or printable STL (depth maps, photogrammetry, extrusion, lithophanes). Use when the user wants image-to-3D, photo-to-mesh, heightmap STL, or lithophane. Not for game engine meshes or Godot/Blender scene lighting. Never assume this folder ships helper scripts."
version: 1.0.1
---

## When to Use

Use this skill when the user wants to convert 2D images into 3D models or printable STL files. Trigger keywords: "image to 3D", "photo to 3D", "depth map to mesh", "lithophane", "SVG extrusion", "photogrammetry", "Meshroom", "COLMAP", "MiDaS", "Depth Anything", "Meshy", "Tripo3D", "InstantMesh", "heightmap to STL", "relief model".

### Approach Selection Matrix

| Method | Input | Speed | Quality | Best For |
|---|---|---|---|---|
| **AI Image-to-3D** | 1 image | Seconds–minutes | Approximate | Concept art, game assets, prototyping |
| **Depth Estimation** | 1 image | Seconds | Relief / 2.5D | Bas-reliefs, heightmaps, lithophanes |
| **Photogrammetry** | 30–200+ images | Hours | High fidelity | Real-world objects, archival |
| **SVG Extrusion** | Vector art | Instant | Exact | Logos, text, flat designs |
| **Lithophane** | 1 photo | Minutes | Photo-quality | Backlit photo displays |

---

## Prerequisites

### Python Environment (Windows / PowerShell)

```powershell
# Create and activate a virtual environment
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# Core dependencies
pip install torch torchvision torchaudio
pip install open3d numpy-stl pillow opencv-python numpy
pip install transformers
pip install svgpathtools shapely triangle
pip install pymeshfix pyvista
```

### GPU Requirements by Method

| Method | VRAM Minimum | Notes |
|---|---|---|
| MiDaS DPT_Large | 2 GB | Runs on CPU if no GPU |
| Depth Anything V2 Large | 4 GB | CPU fallback supported |
| Depth Anything V2 Small | 1 GB | Real-time, low-resource |
| Marigold | 8 GB | Diffusion-based, slow |
| InstantMesh | 8 GB | NVIDIA GPU required |

### External Tools

- **Meshroom**: Download from AliceVision releases; NVIDIA GPU required for full pipeline.
- **COLMAP**: Install from `https://colmap.github.io/`; available as CLI or GUI.
- **OpenSCAD**: Install for SVG extrusion method (`https://openscad.org/`).
- **MeshLab**: Install for mesh cleanup; CLI via `meshlabserver`.
- **Blender**: Optional for advanced mesh editing and retopology.

### API Keys (if using commercial AI tools)

- **Meshy AI**: Register at `meshy.ai` to obtain an API key. Store as environment variable:
  ```powershell
  $env:MESHY_API_KEY = "YOUR_KEY"
  ```
- **Tripo3D**: Browser-based at `tripo3d.ai`; no API key needed for basic use.

---

## Procedure

### Step 0 — Determine Input Type and Select Approach

1. **Single image, 3D object** → AI tools (Meshy, Tripo3D) or InstantMesh (Step 1).
2. **Single image, relief / heightmap** → Depth estimation + `heightmap_to_stl` (Step 2 → Step 3).
3. **Multiple photos, real object** → Photogrammetry (Meshroom or COLMAP) (Step 4).
4. **Vector art / logo** → SVG extrusion (Step 5).
5. **Photo display (backlit)** → Lithophane: `heightmap_to_stl` with `invert=True` (Step 3).

---

### Step 1 — AI Image-to-3D Tools

#### Meshy AI

- **URL**: `meshy.ai`
- **Capabilities**: Text-to-3D, Image-to-3D, AI texturing, retopology
- **Output formats**: GLB, FBX, OBJ, STL
- **Workflow**:
  1. Upload a reference image (clear, well-lit, single object).
  2. Select style preset (realistic, cartoon, low-poly).
  3. Generate initial mesh (30–60 seconds).
  4. Refine with AI texturing or manual edits.
  5. Export as STL for 3D printing.

#### Tripo3D (Tripo AI)

- **URL**: `tripo3d.ai`
- **Capabilities**: Image-to-3D, text-to-3D, integrated editing/rigging
- **Output formats**: GLB, OBJ, FBX
- **Workflow**:
  1. Upload image or enter text prompt.
  2. AI generates mesh in 10–30 seconds.
  3. Use built-in editing tools (segmentation, cleanup).
  4. Export mesh for printing.

#### InstantMesh (Open-Source, Local)

- **Repo**: `github.com/TencentARC/InstantMesh`
- **Architecture**: Multi-view diffusion (Zero123++) + Large Reconstruction Model (LRM)
- **Requirements**: NVIDIA GPU with 8+ GB VRAM

```powershell
git clone https://github.com/TencentARC/InstantMesh
cd InstantMesh
pip install -r requirements.txt
python run.py --input image.png --output output_mesh.obj
```

#### Other Notable AI Tools

| Tool | Type | Highlights |
|---|---|---|
| **Wonder3D** | Open-source | Multi-view generation + reconstruction |
| **Shap-E (OpenAI)** | Open-source | Text/image to 3D; lightweight |
| **Rodin AI** | Commercial | High-fidelity textures |
| **Stable Zero123** | Open-source | Single-view 3D diffusion |
| **LGM** | Open-source | Large Gaussian Model; fast inference |

---

### Step 2 — Depth Estimation

#### MiDaS (Intel Labs)

- **Architecture**: DPT (Dense Prediction Transformer)
- **Output**: Relative depth map (grayscale image)
- **Models**: `midas_v21_small`, `dpt_large`, `dpt_swin2_large`
- **Strengths**: Robust, well-tested, runs on CPU

```python
"""
MiDaS Depth Estimation — generates a depth map from a single image.
Write a local helper named midas_depth.py
"""
import torch
import cv2
import numpy as np

def estimate_depth_midas(
    image_path: str,
    model_type: str = "DPT_Large",
    output_path: str = "depth_map.png",
) -> np.ndarray:
    """
    Run MiDaS depth estimation on a single image.

    Args:
        image_path: Path to input image.
        model_type: MiDaS model variant ('DPT_Large', 'DPT_Hybrid', 'midas_v21_small').
        output_path: Where to save the depth map.

    Returns:
        Depth map as a numpy array (H, W), normalized 0-255.
    """
    model = torch.hub.load("intel-isl/MiDaS", model_type)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model.to(device).eval()

    midas_transforms = torch.hub.load("intel-isl/MiDaS", "transforms")
    if model_type in ["DPT_Large", "DPT_Hybrid"]:
        transform = midas_transforms.dpt_transform
    else:
        transform = midas_transforms.small_transform

    img = cv2.imread(image_path)
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    input_batch = transform(img_rgb).to(device)

    with torch.no_grad():
        prediction = model(input_batch)
        prediction = torch.nn.functional.interpolate(
            prediction.unsqueeze(1),
            size=img_rgb.shape[:2],
            mode="bicubic",
            align_corners=False,
        ).squeeze()

    depth = prediction.cpu().numpy()
    depth_normalized = (depth - depth.min()) / (depth.max() - depth.min()) * 255
    depth_uint8 = depth_normalized.astype(np.uint8)

    cv2.imwrite(output_path, depth_uint8)
    print(f"Depth map saved to {output_path}")
    return depth_uint8


if __name__ == "__main__":
    depth = estimate_depth_midas("my_photo.jpg", output_path="depth_output.png")
```

#### Depth Anything V2 (TikTok / ByteDance)

- **Architecture**: DINOv2 backbone + DPT decoder
- **Models**: `vits` (25M params), `vitb` (97M), `vitl` (335M)
- **Strengths**: State-of-the-art quality, fast, multiple model sizes

```python
"""
Depth Anything V2 depth estimation.
Write a local helper named depth_anything_v2.py
"""
import torch
from transformers import pipeline
from PIL import Image
import numpy as np

def estimate_depth_anything_v2(
    image_path: str,
    output_path: str = "depth_dav2.png",
) -> np.ndarray:
    """Run Depth Anything V2 on a single image."""
    pipe = pipeline(
        task="depth-estimation",
        model="depth-anything/Depth-Anything-V2-Large-hf",
        device=0 if torch.cuda.is_available() else -1,
    )

    image = Image.open(image_path)
    result = pipe(image)
    depth_map = np.array(result["depth"])

    depth_norm = ((depth_map - depth_map.min()) /
                  (depth_map.max() - depth_map.min()) * 255).astype(np.uint8)

    Image.fromarray(depth_norm).save(output_path)
    print(f"Depth Anything V2 map saved to {output_path}")
    return depth_norm
```

#### Marigold (ETH Zurich)

- **Architecture**: Diffusion-based depth estimation
- **Strengths**: Fine detail, sharp edges, handles complex scenes
- **Trade-off**: Slower than feed-forward models (diffusion denoising steps)
- **VRAM**: 8 GB minimum

#### Model Comparison

| Model | Speed | Quality | VRAM | Best For |
|---|---|---|---|---|
| MiDaS DPT_Large | Fast | Good | 2 GB | CPU-friendly general use |
| Depth Anything V2 Large | Fast | Excellent | 4 GB | Best overall quality/speed |
| Depth Anything V2 Small | Very Fast | Good | 1 GB | Real-time, low-resource |
| Marigold | Slow | Excellent | 8 GB | Maximum detail, research |

---

### Step 3 — Depth Map to 3D Mesh Conversion

#### Option A: numpy-stl Heightmap (Simpler, Recommended for Relief/Lithophane)

```python
"""
Simple heightmap to STL converter using numpy-stl.
Write a local helper named heightmap_to_stl.py
Faster and simpler than Open3D for basic relief/lithophane models.
"""
import numpy as np
from stl import mesh
from PIL import Image


def heightmap_to_stl(
    image_path: str,
    output_path: str = "heightmap.stl",
    width_mm: float = 100.0,
    max_height_mm: float = 5.0,
    base_mm: float = 1.0,
    invert: bool = False,
) -> None:
    """
    Convert a grayscale image to a heightmap STL.

    Args:
        image_path: Grayscale image path.
        output_path: Output STL path.
        width_mm: Physical width.
        max_height_mm: Maximum relief height above base.
        base_mm: Base thickness.
        invert: If True, darker = taller (lithophane mode).
    """
    img = np.array(Image.open(image_path).convert("L"), dtype=np.float64)
    if invert:
        img = 255.0 - img

    h, w = img.shape
    pixel_size = width_mm / w

    # Normalize to [0, max_height_mm]
    heights = (img / 255.0) * max_height_mm + base_mm

    faces = []

    for y in range(h - 1):
        for x in range(w - 1):
            # Top surface: two triangles per quad
            v00 = [x * pixel_size, y * pixel_size, heights[y, x]]
            v10 = [(x + 1) * pixel_size, y * pixel_size, heights[y, x + 1]]
            v01 = [x * pixel_size, (y + 1) * pixel_size, heights[y + 1, x]]
            v11 = [(x + 1) * pixel_size, (y + 1) * pixel_size, heights[y + 1, x + 1]]
            faces.append([v00, v10, v11])
            faces.append([v00, v11, v01])

            # Bottom surface (flat at z=0)
            b00 = [x * pixel_size, y * pixel_size, 0]
            b10 = [(x + 1) * pixel_size, y * pixel_size, 0]
            b01 = [x * pixel_size, (y + 1) * pixel_size, 0]
            b11 = [(x + 1) * pixel_size, (y + 1) * pixel_size, 0]
            faces.append([b00, b11, b10])
            faces.append([b00, b01, b11])

    # Side walls
    for x in range(w - 1):
        # Front wall (y=0)
        faces.append([[x * pixel_size, 0, 0],
                      [(x + 1) * pixel_size, 0, heights[0, x + 1]],
                      [x * pixel_size, 0, heights[0, x]]])
        faces.append([[x * pixel_size, 0, 0],
                      [(x + 1) * pixel_size, 0, 0],
                      [(x + 1) * pixel_size, 0, heights[0, x + 1]]])
        # Back wall
        y_max = (h - 1) * pixel_size
        faces.append([[x * pixel_size, y_max, 0],
                      [x * pixel_size, y_max, heights[h - 1, x]],
                      [(x + 1) * pixel_size, y_max, heights[h - 1, x + 1]]])
        faces.append([[x * pixel_size, y_max, 0],
                      [(x + 1) * pixel_size, y_max, heights[h - 1, x + 1]],
                      [(x + 1) * pixel_size, y_max, 0]])

    for y in range(h - 1):
        # Left wall (x=0)
        faces.append([[0, y * pixel_size, 0],
                      [0, y * pixel_size, heights[y, 0]],
                      [0, (y + 1) * pixel_size, heights[y + 1, 0]]])
        faces.append([[0, y * pixel_size, 0],
                      [0, (y + 1) * pixel_size, heights[y + 1, 0]],
                      [0, (y + 1) * pixel_size, 0]])
        # Right wall
        x_max = (w - 1) * pixel_size
        faces.append([[x_max, y * pixel_size, 0],
                      [x_max, (y + 1) * pixel_size, heights[y + 1, w - 1]],
                      [x_max, y * pixel_size, heights[y, w - 1]]])
        faces.append([[x_max, y * pixel_size, 0],
                      [x_max, (y + 1) * pixel_size, 0],
                      [x_max, (y + 1) * pixel_size, heights[y + 1, w - 1]]])

    face_array = np.array(faces)
    stl_mesh = mesh.Mesh(np.zeros(face_array.shape[0], dtype=mesh.Mesh.dtype))
    for i, f in enumerate(face_array):
        stl_mesh.vectors[i] = np.array(f)
    stl_mesh.save(output_path)
    print(f"Heightmap STL saved to {output_path} ({len(face_array)} faces)")


if __name__ == "__main__":
    # Relief mode: brighter = taller
    heightmap_to_stl("depth_output.png", "relief.stl", width_mm=100, max_height_mm=8)
    # Lithophane mode: darker = taller (thicker = less light)
    heightmap_to_stl("photo.jpg", "lithophane.stl", width_mm=100, max_height_mm=3, invert=True)
```

#### Option B: Open3D Poisson Reconstruction (Higher Quality, Slower)

```python
"""
Depth Map to 3D Mesh Pipeline using Open3D.
Write a local helper named depth_to_mesh.py
Converts a depth map image to a printable 3D mesh using Open3D.
"""
import numpy as np
import open3d as o3d
from PIL import Image
from pathlib import Path


def depth_to_mesh(
    depth_path: str,
    output_path: str = "mesh_from_depth.stl",
    depth_scale: float = 0.1,
    simplify_ratio: float = 0.5,
    smooth_iterations: int = 5,
    width_mm: float = 100.0,
    base_thickness: float = 2.0,
) -> None:
    """
    Convert a grayscale depth map to a 3D printable mesh.

    Args:
        depth_path: Path to depth map image (grayscale PNG).
        output_path: Output mesh file path.
        depth_scale: Scale factor for depth values (mm per pixel intensity).
        simplify_ratio: Target ratio for mesh simplification (0.0–1.0).
        smooth_iterations: Laplacian smoothing iterations.
        width_mm: Desired physical width of the output mesh in mm.
        base_thickness: Thickness of solid base in mm.
    """
    depth_img = np.array(Image.open(depth_path).convert("L"), dtype=np.float64)
    h, w = depth_img.shape

    pixel_size = width_mm / w
    height_mm = h * pixel_size

    # Create point cloud from depth map
    points = []
    for y in range(h):
        for x in range(w):
            px = x * pixel_size
            py = (h - y) * pixel_size  # Flip Y
            pz = depth_img[y, x] * depth_scale + base_thickness
            points.append([px, py, pz])

    # Add base points (z = 0) for a solid base
    for y in range(h):
        for x in range(w):
            px = x * pixel_size
            py = (h - y) * pixel_size
            points.append([px, py, 0.0])

    point_cloud = o3d.geometry.PointCloud()
    point_cloud.points = o3d.utility.Vector3dVector(np.array(points))

    point_cloud.estimate_normals(
        search_param=o3d.geometry.KDTreeSearchParamHybrid(radius=pixel_size * 3, max_nn=30)
    )
    point_cloud.orient_normals_towards_camera_location(
        camera_location=np.array([width_mm / 2, height_mm / 2, 100.0])
    )

    # Poisson surface reconstruction
    mesh, densities = o3d.geometry.TriangleMesh.create_from_point_cloud_poisson(
        point_cloud, depth=9, width=0, scale=1.1, linear_fit=False
    )

    # Remove low-density vertices
    density_array = np.asarray(densities)
    density_threshold = np.quantile(density_array, 0.05)
    vertices_to_remove = density_array < density_threshold
    mesh.remove_vertices_by_mask(vertices_to_remove)

    # Simplify mesh
    if simplify_ratio < 1.0:
        target_triangles = int(len(mesh.triangles) * simplify_ratio)
        mesh = mesh.simplify_quadric_decimation(target_number_of_triangles=target_triangles)

    # Smooth
    if smooth_iterations > 0:
        mesh = mesh.filter_smooth_laplacian(number_of_iterations=smooth_iterations)

    mesh.compute_vertex_normals()

    o3d.io.write_triangle_mesh(output_path, mesh)
    print(f"Mesh saved to {output_path} ({len(mesh.triangles)} triangles)")


if __name__ == "__main__":
    depth_to_mesh(
        "depth_output.png",
        output_path="relief_model.stl",
        depth_scale=0.15,
        width_mm=120,
        base_thickness=3.0,
    )
```

---

### Step 4 — Photogrammetry

#### Meshroom (AliceVision)

- **Type**: GUI-based, node-graph pipeline
- **GPU**: NVIDIA GPU required for full pipeline
- **Output**: Textured OBJ mesh
- **Workflow**:
  1. Drag and drop 30–200+ photos into the image pool.
  2. Use project templates (Meshroom 2025.1+) for object or environment scanning.
  3. Hit "Start" — the node graph runs: Feature Extraction → Matching → SfM → Meshing → Texturing.
  4. Export the textured mesh.
  5. Clean up in MeshLab or Blender.

#### COLMAP (CLI)

```powershell
# Feature extraction
colmap feature_extractor --database_path db.db --image_path .\images

# Feature matching
colmap exhaustive_matcher --database_path db.db

# Sparse reconstruction
colmap mapper --database_path db.db --image_path .\images --output_path .\sparse

# Dense reconstruction
colmap image_undistorter --image_path .\images --input_path .\sparse\0 --output_path .\dense
colmap patch_match_stereo --workspace_path .\dense
colmap stereo_fusion --workspace_path .\dense --output_path .\dense\fused.ply

# Meshing (use external tool like Open3D or MeshLab)
```

#### Photogrammetry Capture Tips

- **Lighting**: Diffuse, consistent lighting; avoid harsh shadows.
- **Coverage**: 70–80% overlap between adjacent photos.
- **Background**: Use a turntable for objects; avoid featureless backgrounds.
- **Camera**: Fixed focal length, manual exposure.
- **Count**: 50–100 photos minimum for objects; 200+ for environments.

---

### Step 5 — SVG to 3D Extrusion

#### OpenSCAD Method

```openscad
// SVG to 3D extrusion in OpenSCAD
// Import an SVG file and extrude it to a specified height

extrusion_height = 5; // mm
scale_factor = 0.5;   // Adjust to fit desired size

linear_extrude(height = extrusion_height, convexity = 10)
    scale([scale_factor, scale_factor, 1])
    import("logo.svg", center = true);
```

#### Python Method (svgpathtools + numpy-stl)

```python
"""
SVG Path to extruded 3D STL.
Write a local helper named svg_to_stl.py
Reads SVG paths, converts to polygon, and extrudes to 3D.
"""
import numpy as np
from svgpathtools import svg2paths
from stl import mesh
from shapely.geometry import Polygon
from shapely.ops import unary_union
import triangle as tr


def svg_to_stl(
    svg_path: str,
    output_path: str = "extruded.stl",
    extrusion_height: float = 5.0,
    samples_per_path: int = 100,
) -> None:
    """
    Extrude SVG paths into a 3D STL file.

    Args:
        svg_path: Input SVG file path.
        output_path: Output STL file path.
        extrusion_height: Extrusion height in mm.
        samples_per_path: Number of sample points per path segment.
    """
    paths, attributes = svg2paths(svg_path)

    all_polygons = []
    for path in paths:
        points = []
        for i in range(samples_per_path):
            t = i / samples_per_path
            point = path.point(t)
            points.append([point.real, point.imag])
        if len(points) >= 3:
            poly = Polygon(points)
            if poly.is_valid:
                all_polygons.append(poly)

    if not all_polygons:
        print("No valid polygons found in SVG")
        return

    merged = unary_union(all_polygons)
    coords = np.array(merged.exterior.coords[:-1])

    # Triangulate the polygon
    segments = [[i, (i + 1) % len(coords)] for i in range(len(coords))]
    tri_input = {"vertices": coords, "segments": np.array(segments)}
    tri_output = tr.triangulate(tri_input, "p")

    tri_verts = tri_output["vertices"]
    tri_faces = tri_output["triangles"]

    # Build extruded mesh faces
    faces = []
    for face in tri_faces:
        v0 = [tri_verts[face[0]][0], tri_verts[face[0]][1], extrusion_height]
        v1 = [tri_verts[face[1]][0], tri_verts[face[1]][1], extrusion_height]
        v2 = [tri_verts[face[2]][0], tri_verts[face[2]][1], extrusion_height]
        faces.append([v0, v1, v2])

        b0 = [tri_verts[face[0]][0], tri_verts[face[0]][1], 0]
        b1 = [tri_verts[face[1]][0], tri_verts[face[1]][1], 0]
        b2 = [tri_verts[face[2]][0], tri_verts[face[2]][1], 0]
        faces.append([b0, b2, b1])

    # Side walls
    for i in range(len(coords)):
        j = (i + 1) % len(coords)
        p0 = [coords[i][0], coords[i][1], 0]
        p1 = [coords[j][0], coords[j][1], 0]
        p2 = [coords[j][0], coords[j][1], extrusion_height]
        p3 = [coords[i][0], coords[i][1], extrusion_height]
        faces.append([p0, p1, p2])
        faces.append([p0, p2, p3])

    face_array = np.array(faces)
    stl_mesh_obj = mesh.Mesh(np.zeros(face_array.shape[0], dtype=mesh.Mesh.dtype))
    for i, f in enumerate(face_array):
        stl_mesh_obj.vectors[i] = np.array(f)
    stl_mesh_obj.save(output_path)
    print(f"Extruded SVG saved to {output_path}")
```

---

### Step 6 — Mesh Cleanup

#### PyMeshFix (Python)

```python
import pymeshfix
import pyvista as pv

mesh = pv.read("broken_mesh.stl")
meshfix = pymeshfix.MeshFix(mesh)
meshfix.repair(verbose=True)
meshfix.mesh.save("repaired_mesh.stl")
```

#### MeshLab CLI

```powershell
meshlabserver -i input.stl -o output.stl -s filter_script.mlx
```

MeshLab operations available:
- Fix non-manifold edges and vertices
- Fill holes
- Decimate (reduce polygon count)
- Smooth surfaces
- Remove isolated components

#### Blender

- Remesh for uniform topology
- Sculpting for manual touch-ups
- Boolean operations to add bases or cut features
- Decimate modifier for polygon reduction

---

### Step 7 — Batch Processing

```python
"""
Batch Image-to-3D Pipeline
Write a local helper named batch_process.py
Process a folder of images through depth estimation and mesh generation.
"""
import os
from pathlib import Path

def batch_process_images(
    input_dir: str,
    output_dir: str,
    width_mm: float = 100.0,
    max_height_mm: float = 5.0,
    depth_model: str = "midas",
) -> None:
    """
    Batch process images: depth estimation -> heightmap STL.

    Args:
        input_dir: Directory containing input images.
        output_dir: Directory for output STL files.
        width_mm: Physical width for output models.
        max_height_mm: Maximum relief height.
        depth_model: Which depth model to use ('midas' or 'dav2').
    """
    os.makedirs(output_dir, exist_ok=True)
    image_extensions = {".jpg", ".jpeg", ".png", ".bmp", ".tiff"}

    for img_file in Path(input_dir).iterdir():
        if img_file.suffix.lower() not in image_extensions:
            continue

        print(f"\nProcessing: {img_file.name}")
        depth_path = Path(output_dir) / f"{img_file.stem}_depth.png"
        stl_path = Path(output_dir) / f"{img_file.stem}.stl"

        # Step 1: Generate depth map
        if depth_model == "midas":
            estimate_depth_midas(str(img_file), output_path=str(depth_path))
        elif depth_model == "dav2":
            estimate_depth_anything_v2(str(img_file), output_path=str(depth_path))

        # Step 2: Convert to STL
        heightmap_to_stl(
            str(depth_path),
            output_path=str(stl_path),
            width_mm=width_mm,
            max_height_mm=max_height_mm,
        )
        print(f"  -> {stl_path}")

    print(f"\nBatch processing complete. Output in: {output_dir}")
```

---

## Pitfalls

1. **Non-watertight meshes from AI tools**: Meshy and Tripo3D often produce meshes with holes or non-manifold geometry. Always run PyMeshFix or MeshLab cleanup before printing.
2. **Depth map inversion**: MiDaS outputs relative depth where brighter = closer. If your relief looks inverted, either flip the depth map or use `invert=True` in `heightmap_to_stl`.
3. **Lithophane orientation**: For lithophanes, darker pixels must map to thicker material (less light passes through). Always use `invert=True` when converting a photo to a lithophane.
4. **Memory exhaustion on large images**: The `heightmap_to_stl` function creates two triangles per pixel quad. A 4000×3000 image generates ~24M faces. Downscale images to 1000px wide before processing.
5. **Open3D Poisson reconstruction over-smoothing**: High `depth` parameter values in `create_from_point_cloud_poisson` produce denser but slower meshes. `depth=9` is a good default; do not exceed `depth=11` without testing memory.
6. **InstantMesh VRAM**: Requires 8+ GB VRAM. Will silently fail or OOM on lower-end GPUs. Check `nvidia-smi` before running.
7. **COLMAP path separators on Windows**: Use backslashes in PowerShell commands. Forward slashes work in Python scripts but not in COLMAP CLI on Windows.
8. **Meshroom GPU requirement**: Meshroom's dense reconstruction stage requires NVIDIA CUDA. Without it, only sparse SfM completes — no textured mesh output.
9. **SVG complex paths**: `svgpathtools` may fail on SVGs with nested groups, transforms, or text elements. Flatten and outline text in Illustrator/Inkscape before processing.
10. **Triangle library triangulation**: The `triangle` library requires the `"p"` (planar) flag for polygon triangulation. Without it, it treats input as a point cloud and may produce incorrect results.
11. **MiDaS model download**: `torch.hub.load` downloads models on first run. Ensure internet access or pre-cache models. On Windows, models are cached at `C:\Users\<user>\.cache\torch\hub\`.
12. **Depth Anything V2 HuggingFace model name**: Use exactly `depth-anything/Depth-Anything-V2-Large-hf` — the non-`-hf` variant requires different loading code.

---

## Verification

### Check 1 — Depth Map Generated Correctly

```powershell
python -c "from PIL import Image; img = Image.open('depth_output.png'); print(f'Size: {img.size}, Mode: {img.mode}')"
```

Expected output: `Size: (W, H), Mode: L` (grayscale, non-zero dimensions).

### Check 2 — STL File Is Valid and Non-Empty

```powershell
python -c "from stl import mesh; m = mesh.Mesh.from_file('relief.stl'); print(f'Faces: {len(m.vectors)}'); print(f'Bounds: X={m.x.min():.1f}-{m.x.max():.1f}, Y={m.y.min():.1f}-{m.y.max():.1f}, Z={m.z.min():.1f}-{m.z.max():.1f}')"
```

Expected: Face count > 0, Z bounds span from 0 to `base_mm + max_height_mm`.

### Check 3 — Mesh Is Watertight (Open3D)

```python
import open3d as o3d
mesh = o3d.io.read_triangle_mesh("relief.stl")
print(f"Vertices: {len(mesh.vertices)}")
print(f"Triangles: {len(mesh.triangles)}")
print(f"Watertight: {mesh.is_watertight()}")
print(f"Oriented: {mesh.is_oriented()}")
```

Expected: `Watertight: True`, `Oriented: True`.

### Check 4 — PyMeshFix Repair Success

```python
import pymeshfix
import pyvista as pv
mesh = pv.read("repaired_mesh.stl")
print(f"Faces: {mesh.n_faces}")
print(f"Volume: {mesh.volume:.2f} mm³")
```

Expected: Non-zero volume, positive face count.

### Check 5 — Batch Output Directory

```powershell
Get-ChildItem -Path .\output -Filter *.stl | Measure-Object | Select-Object -ExpandProperty Count
```

Expected: Count matches the number of input images processed.

---

## Related Skills

- **3d-printing-slicer**: Slicing STL files for 3D printer preparation.
- **mesh-repair**: Advanced mesh repair and remeshing workflows.
- **photogrammetry-pipeline**: Detailed photogrammetry capture and processing guide.
