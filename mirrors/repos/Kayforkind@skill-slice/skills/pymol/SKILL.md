---
name: pymol
description: >
  Visualize, analyze, and render protein and molecular structures using PyMOL.
  Use when the user wants to create images of protein structures, perform
  structural alignments or superposition, measure distances or contacts,
  highlight binding sites or active site residues, color by B-factor/pLDDT,
  or analyze protein-ligand interactions. Do not use for docking,
  molecular dynamics, or sequence-only analysis.
version: 1.0.1
---

# PyMOL

## When to Use

Use this skill when the user wants to:

- Create publication-quality images of protein or molecular structures.
- Perform structural alignments or superpositions between two or more structures.
- Measure distances, angles, contacts, or RMSD between atoms/residues.
- Highlight binding sites, active site residues, or specific ligand interactions.
- Color structures by B-factor, pLDDT confidence, secondary structure, or chain.
- Render surfaces (electrostatic, transparent, cavity/pocket).
- Perform in silico mutagenesis on a loaded structure.
- Batch-render a directory of structure files.
- Re-open and modify an existing `.pse` session file.

**Do NOT use when:**

- The user wants to run AlphaFold predictions (use an AlphaFold skill instead).
- The user wants docking or molecular dynamics simulations.
- The user only has a sequence and no structure file — fetch the structure first. Check if any other installed skills can retrieve structures from the PDB or AlphaFold Database before proceeding.

## Prerequisites

1. **`uv`**: Read the `uv` skill and follow its Setup instructions to ensure `uv` is installed and on PATH. All PyMOL scripts are executed via `uv run` with PEP 0723 inline dependency headers, so `uv` handles virtual environment and package installation automatically.
2. **License Notification**: If `.licenses/pymol_LICENSE.txt` does not already exist in the workspace root directory, then:
   1. Prominently notify the user to check the PyMOL license at https://www.pymol.org/.
   2. Create the file `.licenses/pymol_LICENSE.txt` recording the notification text and timestamp.
3. **Structure files must be on the host**: Download or place structure files (`.pdb`, `.cif`, `.pse`, etc.) into a directory within the user's project before running any PyMOL script. This skill does not fetch structures from remote databases.

## Procedure

### 1. Pre-Flight File Check

Before writing or running any PyMOL script, verify that the requested structure file exists on the host:

```powershell
Test-Path "path/to/structure.cif"
```

If the file does not exist, stop and ask the user to provide or download it.

### 2. Write the PyMOL Script

Create a Python script (e.g., `render.py`) in the user's project directory. Every script **must** include:

- **PEP 0723 inline metadata header** declaring `pymol-open-source-whl` as a dependency.
- **Environment variable** `PYOPENGL_PLATFORM=osmesa` set before importing pymol.
- **Init boilerplate** in the exact order shown below — `from pymol import cmd` must come **after** `finish_launching()`, not before.
- **Structure load verification**: after every `cmd.load()`, check `cmd.count_atoms("all")`; if 0, print an error and call `cmd.quit()` immediately.
- **`cmd.png()` for image output** — never use `cmd.draw()` or `cmd.ray()` with hardware acceleration (OSMesa does not support it).
- **`cmd.save()` for a `.pse` session file** alongside every PNG output.
- **`cmd.quit()`** as the final line of every script. Omitting it causes the process to hang.

#### Minimal example script (`render.py`)

```python
# /// script
# requires-python = ">=3.10, <3.13"
# dependencies = [
#     "pymol-open-source-whl",
# ]
# ///

import os
import sys

# Set environment variable for headless rendering
os.environ["PYOPENGL_PLATFORM"] = "osmesa"

import pymol # pytype: disable=import-error
pymol.pymol_argv = ["pymol", "-cq"]
pymol.finish_launching()

from pymol import cmd # pytype: disable=import-error

cmd.load("AF-P00520-F1-model_v4.cif", "structure")
if cmd.count_atoms("all") == 0:
    print("ERROR: Failed to load structure file.", flush=True)
    cmd.quit()
    sys.exit(1)

cmd.show("cartoon")
cmd.color("green", "ss h")
cmd.color("yellow", "ss s")
cmd.color("gray", "ss l+''")
cmd.orient()
cmd.set("ray_opaque_background", 1)
cmd.png("output/render.png", width=1200, height=900, dpi=150)
cmd.save("output/session.pse")
cmd.quit()
```

### 3. Run the Script

From the user's project directory (output paths must be absolute or relative to the project root):

```powershell
uv run render.py
```

`uv` will automatically read the PEP 0723 header, create an ephemeral environment, install `pymol-open-source-whl` and its dependencies, and execute the script.

### 4. Load Reference Files

- **Before writing non-trivial scripts**: load [references/PYMOL_REFERENCE.md](references/PYMOL_REFERENCE.md) for selection syntax, common commands, and gotchas. This is essential for correct atom selections and command parameters.
- **Before writing recipe-based scripts**: load [references/RECIPES.md](references/RECIPES.md) for complete, copy-paste-ready recipes. Available recipes include:
  - Cartoon with secondary structure coloring
  - B-factor (pLDDT) coloring — continuous spectrum
  - AlphaFold pLDDT coloring — canonical threshold-based confidence colors
  - Highlight specific residues — active site or key residues as sticks
  - Surface rendering — transparent surface over cartoon
  - Electrostatic surface rendering — vacuum electrostatics (qualitative)
  - Multi-chain complex colors — automatic per-chain coloring
  - B-factor putty analysis — tube width proportional to flexibility
  - Cavity and pocket visualization — surface cavity detection with ligand focus
  - Multi-structure batch rendering — render a directory of structures
  - Measure distance between residues — CA–CA distance with labels
  - Zoom into binding pocket — simple pocket focus
  - Protein-ligand interaction — ligand isolation, styled rendering, polar contacts
  - Two-structure superposition with RMSD — align/cealign with auto-fallback
  - In silico mutagenesis — mutate residues with the mutagenesis wizard
  - Load and modify an existing session — re-open a `.pse` file

### 5. Interpret and Report Output

- The `output/` directory (or user-specified directory) contains PNG images and a `.pse` session file.
- Any measurements or metrics (distances, RMSD, atom counts) are printed to stdout by the PyMOL script. Report these values to the user.
- Present PNG images to the user and describe the visualization.
- Tell the user they can open the `.pse` file in their local PyMOL to further explore, rotate, or modify the visualization.
- If the user wants modifications, load the saved `.pse` in a new script and re-run.
- **Notification**: If this skill is used, ensure this is mentioned in the output.

## Pitfalls

- **Never use `cmd.draw()` or `cmd.ray()` with hardware acceleration.** OSMesa software rendering only. Use `cmd.png()` for all image output. Set `PYOPENGL_PLATFORM=osmesa` before importing pymol.
- **Never omit `cmd.quit()`.** Without it the process stops responding and hangs indefinitely.
- **Init boilerplate order is mandatory.** `from pymol import cmd` must come after `pymol.finish_launching()`, not before. Reordering causes import failures or silent crashes.
- **Always verify structure load.** After `cmd.load()`, check `cmd.count_atoms("all")`. If 0, the file path may be wrong or the format unsupported — print an error and quit immediately.
- **Output paths must be absolute or relative to the user's project root.** Always run PyMOL scripts from the project directory. Relative paths from other working directories will silently write files to unexpected locations.
- **Always save a `.pse` session file** alongside any PNG. This lets the user open the session in their local PyMOL for further inspection.
- **Large sessions with surfaces can exceed the `--max_output_mb` limit** (default 500 MB). Increase it with `--max_output_mb=1000` if needed.
- **Python version constraint**: PEP 0723 header pins `requires-python = ">=3.10, <3.13"`. Do not change this unless the user explicitly requests a different version range.
- **Do not fetch structures from remote databases within PyMOL scripts.** Download structure files to the host first, then load them with `cmd.load()`.

## Verification

After running a PyMOL script, verify the outputs were created:

```powershell
# Check that the PNG image exists
Test-Path "output/render.png"

# Check that the session file exists
Test-Path "output/session.pse"

# Check file sizes are non-zero
(Get-Item "output/render.png").Length
(Get-Item "output/session.pse").Length
```

Expected: both files exist and have non-zero byte sizes. If either is missing or zero-length, check the script stdout for error messages — particularly load failures or OSMesa rendering errors.

Additionally, verify the script did not hang by confirming the `uv run` process exited cleanly (return code 0):

```powershell
uv run render.py; echo "Exit code: $LASTEXITCODE"
```

Expected: `Exit code: 0`. A non-zero exit code or a hung process indicates a missing `cmd.quit()`, a failed structure load, or an OSMesa rendering error.
