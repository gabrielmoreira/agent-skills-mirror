# MIT; Copyright (c) 2026 Minho Hwang (revfactory).
# Modified for OMH from revfactory/showreel@64521220a2f8e91cb9894400c48c15b7f45205d6
# scripts/motion_check.py: bounded local heuristics with explicit intentional holds and strict exit.
# Full permission/warranty: ../LICENSE.upstream. Metrics never certify artistic or flash safety.
"""Low-resolution movement/brightness diagnostics, not an artistic quality score."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import subprocess

from new_project import no_links
from timeline import number, read_spec


def analyze_frames(frames, *, fps=8, holds=(), still_threshold=.2, flash_threshold=50):
    number(fps, "diagnostic fps", 1, 8)
    if len(frames) < 2 or len(frames) > 4800 or not frames[0] or any(len(f) != len(frames[0]) for f in frames):
        raise ValueError("at least two equal nonempty decoded frames required, <=4800")
    for hold in holds:
        start = number(hold["start"], "hold start", 0, len(frames)/fps)
        end = number(hold["end"], "hold end", 0, len(frames)/fps)
        if end <= start or not isinstance(hold.get("reason"), str) or not hold["reason"].strip():
            raise ValueError("intentional hold needs ordered bounds and an authored reason")
    movement = [sum(abs(a-b) for a, b in zip(left, right))/len(left) for left, right in zip(frames, frames[1:])]
    brightness = [sum(f)/len(f) for f in frames]
    issues = []
    for i, amount in enumerate(movement, 1):
        t = i / fps
        if amount < still_threshold and not any(h["start"] <= t < h["end"] for h in holds):
            issues.append({"at": t, "kind": "unannotated_stillness"})
        if abs(brightness[i]-brightness[i-1]) > flash_threshold:
            issues.append({"at": t, "kind": "brightness_jump_review_required"})
    return {"verdict": "REVISE" if issues else "PASS", "motion_delta_gray": movement, "brightness_gray": brightness,
            "policy": {"fps": fps, "still_threshold_gray": still_threshold, "flash_threshold_gray": flash_threshold, "intentional_holds": list(holds)},
            "issues": issues, "artistic": "not_observed", "limitations": ["Heuristic diagnostic only; not a quality/safety score or certification", "Low-resolution sampling can miss brief flashes and small motion; review full-speed and transition strips separately"]}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("artifact", type=Path)
    parser.add_argument("--ffmpeg", required=True)
    parser.add_argument("--fps", type=int, default=8)
    parser.add_argument("--holds", type=Path)
    args = parser.parse_args()
    number(args.fps, "diagnostic fps", 1, 8)
    path = no_links(args.artifact)
    if not path.is_file():
        raise ValueError("regular motion artifact required")
    if path.stat().st_size > 536_870_912:
        raise ValueError("artifact inspection bound exceeded")
    result = subprocess.run([args.ffmpeg, "-v", "error", "-xerror", "-nostdin", "-i", str(path), "-t", "600", "-vf", f"fps={args.fps},scale=64:36:flags=area,format=gray", "-f", "rawvideo", "-"], capture_output=True, check=True, timeout=120)
    raw = result.stdout
    if not raw or len(raw) % (64*36) or len(raw) > 11_059_200:
        raise ValueError("missing/truncated/oversized decoded motion data")
    report = analyze_frames([raw[i:i+64*36] for i in range(0, len(raw), 64*36)], fps=args.fps, holds=read_spec(args.holds, list) if args.holds else [])
    report["artifact_sha256"] = hashlib.sha256(path.read_bytes()).hexdigest()
    print(json.dumps(report, indent=2))
    raise SystemExit(0 if report["verdict"] == "PASS" else 1)


if __name__ == "__main__":
    main()
