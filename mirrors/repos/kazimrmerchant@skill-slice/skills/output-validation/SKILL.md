---
name: output-validation
version: 1.1.1
description: "Validates interval-instruction JSON (`{start}->{end}` keys to label lists) and per-frame CSR mask NPZ against video height, width, and frame count, without ground-truth labels. Use for a structural gate after mask generation and before any evaluator. Not for Lighthouse metrics, LLM answer grading, or generic JSON Schema of unrelated APIs."
risk: safe
source: openrouter-deepsearch
date_added: 2026-06-16
---

## When to Use

Run this skill **after** you have generated your outputs (interval instructions JSON, per-frame CSR mask NPZ, etc.) and **before** you submit or hand them off to any downstream consumer — training pipelines, evaluators, visualizers, or scoring steps.

**Trigger keywords:** `validate outputs`, `check masks`, `verify instructions`, `CSR validation`, `NPZ check`, `output self-check`, `ground-truth-free validation`, `interval instructions`, `mask format check`.

The artifacts produced by this task follow a strict contract:
- A JSON file of frame-interval keys (`"{start}->{end}"`) mapped to label lists.
- An NPZ file of per-frame sparse (CSR) masks that must line up with the source video dimensions and frame count.

Downstream consumers assume that contract holds and will fail in confusing, hard-to-trace ways if it does not — an `IndexError` deep inside a data loader, a silently mis-aligned mask, an evaluator that cannot map an unknown label. A structural self-check catches those problems at the cheapest possible moment.

Every check here is **ground-truth-free**: it verifies *format, range, and internal consistency*, never correctness against labels. You can run it long before any scoring step exists, and on data you are not permitted to compare against held-out ground truth.

## Prerequisites

- **Python 3.10+** with `opencv-python` and `numpy` installed.
- Pin known-good versions of `opencv-python` and `numpy` so CSR and metadata semantics stay stable.
- Import OpenCV as `import cv2`. **Never** use `import cv2.cv2` — that is an internal submodule, not a supported public entry point, and relying on it breaks under several wheels.
- Windows host is primary (PowerShell). All commands below work in PowerShell; use forward slashes in `Path()` objects inside Python for cross-platform safety.

## Procedure

### Step 1 — Configure the validator script

Create a file named `validate_outputs.py` with the configuration block below. Edit the three paths and the `ALLOWED_LABELS` set to match your project.

```python
"""Ground-truth-free structural validation of interval instructions and CSR masks."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Final

import cv2
import numpy as np
import numpy.typing as npt

# --- Configuration ---------------------------------------------------------

# Concrete example paths. Point these at your real artifacts.
VIDEO_PATH: Final[Path] = Path("video.mp4")
INSTRUCTIONS_PATH: Final[Path] = Path("interval_instructions.json")
MASKS_PATH: Final[Path] = Path("masks.npz")

# Labels the generator is allowed to emit. Anything outside this set is treated
# as a bug: a downstream evaluator cannot map an unknown string to a class, so
# we reject it here instead of letting it fail silently later. Replace these
# with your project's actual label taxonomy.
ALLOWED_LABELS: Final[frozenset[str]] = frozenset(
    {"person", "vehicle", "animal", "background"}
)

# Interval keys look like "12->48": one or more digits, a literal arrow, then
# one or more digits. Compiled once and reused for every key.
KEY_PATTERN: Final[re.Pattern[str]] = re.compile(r"^(\d+)->(\d+)$")


class ValidationError(Exception):
    """Raised when an output artifact violates the expected contract."""


# --- Video metadata --------------------------------------------------------

def load_video_dims(path: Path) -> tuple[int, int, int]:
    """Return ``(frame_count, height, width)`` for the video at ``path``.

    Raises ``ValidationError`` if the file is missing, cannot be opened, or
    reports metadata that the range checks cannot trust.
    """
    if not path.is_file():
        raise ValidationError(f"Video file not found: {path}")

    capture: cv2.VideoCapture = cv2.VideoCapture(str(path))
    try:
        if not capture.isOpened():
            raise ValidationError(f"Could not open video (unsupported codec?): {path}")
        frame_count: int = int(capture.get(cv2.CAP_PROP_FRAME_COUNT))
        height: int = int(capture.get(cv2.CAP_PROP_FRAME_HEIGHT))
        width: int = int(capture.get(cv2.CAP_PROP_FRAME_WIDTH))
    finally:
        capture.release()

    if frame_count <= 0:
        raise ValidationError(
            f"Video reports a non-positive frame count ({frame_count}); the "
            "container metadata is likely missing or corrupt. Re-encode to a "
            "constant-frame-rate container and retry."
        )
    if height <= 0 or width <= 0:
        raise ValidationError(
            f"Video reports invalid dimensions: height={height}, width={width}."
        )
    return frame_count, height, width


# --- Instructions ----------------------------------------------------------

def load_instructions(path: Path) -> dict[str, object]:
    """Load and JSON-parse the instructions file into a dict of raw values."""
    if not path.is_file():
        raise ValidationError(f"Instructions file not found: {path}")
    try:
        with path.open("r", encoding="utf-8") as handle:
            parsed: object = json.load(handle)
    except json.JSONDecodeError as exc:
        raise ValidationError(f"Instructions file is not valid JSON: {exc}") from exc

    if not isinstance(parsed, dict):
        raise ValidationError(
            f"Instructions root must be a JSON object, got {type(parsed).__name__}."
        )
    return {str(key): value for key, value in parsed.items()}


def validate_instructions(instructions: dict[str, object], frame_count: int) -> int:
    """Validate every interval key and its labels.

    Returns the maximum frame index referenced (useful for sanity-logging
    against your sampling policy). Raises ``ValidationError`` on the first
    violation.
    """
    if not instructions:
        raise ValidationError("Instructions object is empty; nothing to validate.")

    max_index: int = -1
    for key, value in instructions.items():
        match: re.Match[str] | None = KEY_PATTERN.match(key)
        if match is None:
            raise ValidationError(
                f"Key {key!r} is not of the form '<start>-><end>' with integer bounds."
            )
        start: int = int(match.group(1))
        end: int = int(match.group(2))
        if start > end:
            raise ValidationError(
                f"Key {key!r} has start ({start}) greater than end ({end})."
            )
        if end >= frame_count:
            raise ValidationError(
                f"Key {key!r} references frame {end}, but the video only has "
                f"{frame_count} frames (valid indices 0..{frame_count - 1})."
            )

        if not isinstance(value, list) or len(value) == 0:
            raise ValidationError(
                f"Value for key {key!r} must be a non-empty list of label strings."
            )
        for label in value:
            if not isinstance(label, str) or not label.strip():
                raise ValidationError(
                    f"Key {key!r} contains a non-string or blank label: {label!r}."
                )
            if label not in ALLOWED_LABELS:
                raise ValidationError(
                    f"Key {key!r} contains unknown label {label!r}; allowed labels "
                    f"are {sorted(ALLOWED_LABELS)}."
                )

        max_index = max(max_index, end)
    return max_index


# --- Masks (NPZ of per-frame CSR arrays) -----------------------------------

def _count_frames(masks: np.lib.npy_io.NpzFile) -> int:
    """Count consecutively-indexed mask frames and reject any gaps."""
    consecutive: int = 0
    while f"f_{consecutive}_data" in masks.files:
        consecutive += 1

    total_data_arrays: int = sum(
        1
        for name in masks.files
        if name.startswith("f_") and name.endswith("_data")
    )
    if total_data_arrays != consecutive:
        raise ValidationError(
            f"Found {total_data_arrays} frame-data arrays but only {consecutive} "
            "are consecutively indexed from 0; there is a gap or an out-of-order "
            "frame in the NPZ."
        )
    return consecutive


def _validate_csr_frame(
    masks: np.lib.npy_io.NpzFile,
    index: int,
    height: int,
    width: int,
) -> None:
    """Validate the CSR triplet for a single frame against ``height``/``width``."""
    prefix: str = f"f_{index}"
    for component in ("data", "indices", "indptr"):
        name: str = f"{prefix}_{component}"
        if name not in masks.files:
            raise ValidationError(f"Frame {index} is missing required array '{name}'.")

    data: npt.NDArray[np.generic] = masks[f"{prefix}_data"]
    indices: npt.NDArray[np.integer] = masks[f"{prefix}_indices"]
    indptr: npt.NDArray[np.integer] = masks[f"{prefix}_indptr"]

    if data.ndim != 1 or indices.ndim != 1 or indptr.ndim != 1:
        raise ValidationError(f"Frame {index}: CSR arrays must each be 1-dimensional.")
    if indptr.shape[0] != height + 1:
        raise ValidationError(
            f"Frame {index}: len(indptr)={indptr.shape[0]}, expected "
            f"height + 1 = {height + 1}."
        )
    if int(indptr[0]) != 0:
        raise ValidationError(
            f"Frame {index}: indptr must start at 0, got {int(indptr[0])}."
        )
    if int(indptr[-1]) != indices.size:
        raise ValidationError(
            f"Frame {index}: indptr[-1]={int(indptr[-1])} does not equal "
            f"indices.size={indices.size}."
        )
    if data.size != indices.size:
        raise ValidationError(
            f"Frame {index}: data.size={data.size} does not equal "
            f"indices.size={indices.size}."
        )
    if bool(np.any(np.diff(indptr) < 0)):
        raise ValidationError(
            f"Frame {index}: indptr is not monotonically non-decreasing."
        )
    if indices.size and (int(indices.min()) < 0 or int(indices.max()) >= width):
        raise ValidationError(
            f"Frame {index}: column indices fall outside the valid range "
            f"[0, {width})."
        )


def validate_masks(masks: np.lib.npy_io.NpzFile, height: int, width: int) -> int:
    """Validate the NPZ shape header and every per-frame CSR mask.

    Returns the number of mask frames validated.
    """
    if "shape" not in masks.files:
        raise ValidationError("NPZ is missing the required 'shape' array.")
    shape: npt.NDArray[np.integer] = masks["shape"]
    if shape.shape != (2,):
        raise ValidationError(
            f"'shape' must contain exactly [height, width]; got array of shape "
            f"{shape.shape}."
        )
    stored_h: int = int(shape[0])
    stored_w: int = int(shape[1])
    if stored_h != height or stored_w != width:
        raise ValidationError(
            f"Mask shape {stored_h}x{stored_w} does not match video "
            f"{height}x{width}."
        )

    frame_count: int = _count_frames(masks)
    if frame_count == 0:
        raise ValidationError("NPZ contains no 'f_<i>_data' frames.")

    for index in range(frame_count):
        _validate_csr_frame(masks, index, height, width)
    return frame_count


# --- Entry point -----------------------------------------------------------

def main() -> int:
    try:
        frame_count, height, width = load_video_dims(VIDEO_PATH)
        instructions = load_instructions(INSTRUCTIONS_PATH)
        max_index = validate_instructions(instructions, frame_count)

        if not MASKS_PATH.is_file():
            raise ValidationError(f"Masks file not found: {MASKS_PATH}")
        with np.load(MASKS_PATH) as masks:
            mask_frames = validate_masks(masks, height, width)
    except ValidationError as exc:
        print(f"[FAIL] {exc}")
        return 1

    print(
        f"[OK] {len(instructions)} intervals (max referenced frame {max_index}), "
        f"{mask_frames} mask frames, video {width}x{height} @ {frame_count} frames."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

### Step 2 — Run the validator

```bash
python validate_outputs.py
```

On success it exits `0` and prints an `[OK]` summary. On the first contract violation it exits `1` with a single `[FAIL]` line naming the specific problem.

### Step 3 — Spot-check individual artifacts (optional)

Validate JSON syntax (pretty-prints, exits non-zero on a parse error):

```bash
python -m json.tool interval_instructions.json
```

List the arrays stored in the NPZ (note the explicit `close()` to release the file handle):

```bash
python -c "import numpy as np; f = np.load('masks.npz'); print(f.files); f.close()"
```

Read the total frame count straight from the video container (release the capture afterward):

```bash
python -c "import cv2; cap = cv2.VideoCapture('video.mp4'); print(int(cap.get(cv2.CAP_PROP_FRAME_COUNT))); cap.release()"
```

## What each rule checks and why

| Rule | What it validates | Downstream failure it prevents |
|------|-------------------|-------------------------------|
| **Key format** | Every key is `"{start}->{end}"`, integers only, `start <= end` | Consumers split on `->` and parse each side as `int`; a non-integer raises during parsing, and a reversed range silently selects an empty or backwards interval. |
| **Coverage** | Maximum referenced frame index `<= total - 1`, consistent with sampling policy | An index at or past the frame count makes the consumer read past the end of the video (`IndexError`, or worse, a wrong frame from a wrapped/clamped read). |
| **Frame count** | Number of `f_{i}_*` groups equals the number of sampled frames, no gaps, no missing CSR components | A gap (e.g. `f_0`, `f_1`, then `f_3`) means a mask is missing and every later frame is mis-indexed relative to the instructions. |
| **CSR integrity** | Each frame has `data`, `indices`, `indptr` with `len(indptr) == H + 1`, `indptr[0] == 0`, `indptr[-1] == indices.size`, `data.size == indices.size`, non-decreasing `indptr`, column indices in `[0, W)` | A violation either crashes `scipy.sparse.csr_matrix` reconstruction or, more dangerously, reconstructs a *corrupt* mask without error. |
| **Value validity** | JSON values are non-empty lists of label strings, every label in the allowed set | An empty list carries no supervision signal; an out-of-vocabulary label is almost always a typo or generation bug that an evaluator cannot map back to a class. |

**Cross-consistency note:** Interval keys index the **original** video frames, while NPZ frames are indexed in **sampled** order. These live in two different index spaces. Do **not** assert that "max interval index" equals "mask frame count" — relate them only through your explicit sampling map. The validator keeps the two checks separate for exactly this reason.

## Pitfalls

- **Very long or high-resolution videos.** Reading the video frame count is cheap (container metadata), but materializing every frame's CSR arrays — or worse, expanding them to dense `H×W` masks — scales with total stored pixels and can exhaust memory. The validator accesses NPZ members lazily and validates frame-by-frame so peak memory stays bounded. **Do not** change it to load everything up front.

- **Unreliable container metadata.** `CAP_PROP_FRAME_COUNT` is sometimes an *estimate* (or `0`) for variable-frame-rate, streaming, or partially-written containers. Every range check depends on an accurate count, so the validator treats a non-positive count as a **fatal error** rather than silently trusting it. If you hit this, re-encode to a constant-frame-rate container before validating.

- **Sensitive footage.** Validation reads only frame *metadata* (count, height, width), never pixel content — but the artifacts you are validating (masks and labels) can still fall under data-protection or privacy rules. Keep them in approved storage and do not copy them to ad-hoc locations to run this check.

- **Wrong OpenCV import.** Import as `import cv2`. The `cv2.cv2` form that earlier versions of this skill recommended is an *internal* submodule, not a supported public entry point, and relying on it breaks under several wheels. Pin known-good versions of `opencv-python` and `numpy`.

- **Index space confusion.** Interval keys reference original video frames; NPZ `f_{i}` keys reference sampled frames. Never cross-check them directly without your sampling map.

## Verification

Confirm each item before hand-off:

- [ ] JSON keys match `"{start}->{end}"` and every value is a non-empty list of allowed labels.
- [ ] Maximum referenced frame index is within the video range and consistent with your sampling policy.
- [ ] NPZ frame count matches the number of sampled frames, with no gaps and consecutive `f_{i}_*` keys.
- [ ] Every frame's CSR structure (`indptr` length/start/end, index range, `data`/`indices` sizes) and the NPZ `shape` header are valid.

**Fastest path — run the full validator:**

```bash
python validate_outputs.py
```

Expected success output:

```
[OK] 12 intervals (max referenced frame 240), 120 mask frames, video 1920x1080 @ 300 frames.
```

Expected failure output (exits `1`):

```
[FAIL] Key '250->300' references frame 300, but the video only has 300 frames (valid indices 0..299).
```

## Related skills

This validator is the **final structural gate** in the artifact pipeline. Run it immediately after the upstream steps that *produce* these files — the step that emits `interval_instructions.json` and the step that extracts the per-frame CSR masks into `masks.npz` — and *before* any ground-truth scoring or evaluation step. Because every check here is ground-truth-free, it can (and should) run earlier than evaluation, so a malformed artifact is rejected before it consumes expensive evaluation compute. If you maintain an explicit frame-sampling map, validate that map alongside this step, since it is the only correct bridge between the instruction (original-frame) and mask (sampled-frame) index spaces.
