#!/usr/bin/env python3
"""
Stage a TEMP Godot EditorPlugin, handshake capture, encode WebP, teardown.

Never Autoload. Never leave addons/_gdskills_agent_vision/ committed.
"""

from __future__ import annotations

import re
import shutil
import time
from pathlib import Path
from typing import List, Optional, Tuple

from PIL import Image

try:
    from agent_vision_webp_encode import save_webp
except ImportError:  # godot-master flattened mirror
    from agent_vision_webp_encode import save_webp

ADDON_NAME = "_gdskills_agent_vision"
PLUGIN_CFG_RES = f"res://addons/{ADDON_NAME}/plugin.cfg"
ENABLED_RE = re.compile(
    r'(?m)^(?P<prefix>enabled=PackedStringArray\()(?P<body>.*)(?P<suffix>\))\s*$'
)


def _resolve_template_files() -> list[tuple[str, Path]]:
    """
    Domain skill: scripts/editor_bridge/{plugin.cfg,plugin.gd,...}
    godot-master mirror: scripts/agent_vision_editor_bridge_plugin.cfg (etc.)
    """
    here = Path(__file__).resolve().parent
    nested = here / "editor_bridge"
    keys = ("plugin.cfg", "plugin.gd", "capture_viewport.gd")
    found: dict[str, Path] = {}

    if nested.is_dir():
        for key in keys:
            p = nested / key
            if p.is_file():
                found[key] = p

    if "plugin.cfg" not in found or "plugin.gd" not in found:
        found.clear()
        for p in here.iterdir():
            if not p.is_file():
                continue
            for key in keys:
                if p.name == key or p.name.endswith(f"_editor_bridge_{key}"):
                    found[key] = p

    if "plugin.cfg" not in found or "plugin.gd" not in found:
        raise SystemExit(
            f"Editor bridge templates not found beside {here} "
            "(need editor_bridge/plugin.cfg+plugin.gd or flattened *_editor_bridge_* files)"
        )
    return [(k, found[k]) for k in keys if k in found]


def _copy_bridge_sources(project_root: Path) -> Path:
    bridge = project_root / ".gdskills" / "vision" / "bridge"
    if bridge.exists():
        shutil.rmtree(bridge)
    bridge.mkdir(parents=True, exist_ok=True)
    for name, src in _resolve_template_files():
        shutil.copy2(src, bridge / name)
    return bridge


def stage_addon(project_root: Path) -> Path:
    src = _copy_bridge_sources(project_root)
    dest = project_root / "addons" / ADDON_NAME
    if dest.exists():
        shutil.rmtree(dest)
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(src, dest)
    return dest


def _read_project_godot(path: Path) -> str:
    return path.read_text(encoding="utf-8-sig")


def _write_project_godot(path: Path, text: str) -> None:
    path.write_text(text, encoding="utf-8", newline="\n")


def enable_plugin(project_root: Path) -> Tuple[bool, Optional[str]]:
    """
    Ensure plugin.cfg is in [editor_plugins] enabled=.
    Returns (changed, previous_enabled_line_or_None).
    """
    pg = project_root / "project.godot"
    if not pg.is_file():
        raise SystemExit(f"No project.godot at {project_root}")
    text = _read_project_godot(pg)
    prev_line = None
    if "[editor_plugins]" not in text:
        text = text.rstrip() + "\n\n[editor_plugins]\n\nenabled=PackedStringArray(\"" + PLUGIN_CFG_RES + "\")\n"
        _write_project_godot(pg, text)
        return True, None

    m = ENABLED_RE.search(text)
    if not m:
        # section exists but no enabled= — append
        text = text.rstrip() + f'\n\nenabled=PackedStringArray("{PLUGIN_CFG_RES}")\n'
        _write_project_godot(pg, text)
        return True, None

    prev_line = m.group(0)
    body = m.group("body").strip()
    if PLUGIN_CFG_RES in body:
        return False, prev_line

    entries: List[str] = []
    if body:
        # split quoted entries
        entries = re.findall(r'"([^"]*)"', body)
    if PLUGIN_CFG_RES not in entries:
        entries.append(PLUGIN_CFG_RES)
    new_body = ", ".join(f'"{e}"' for e in entries)
    new_line = f"{m.group('prefix')}{new_body}{m.group('suffix')}"
    text = text[: m.start()] + new_line + text[m.end() :]
    _write_project_godot(pg, text)
    return True, prev_line


def disable_plugin(project_root: Path, previous_enabled_line: Optional[str]) -> None:
    pg = project_root / "project.godot"
    if not pg.is_file():
        return
    text = _read_project_godot(pg)
    m = ENABLED_RE.search(text)
    if not m:
        return
    if previous_enabled_line is not None and PLUGIN_CFG_RES not in (previous_enabled_line or ""):
        # restore exact previous line
        text = text[: m.start()] + previous_enabled_line + text[m.end() :]
        _write_project_godot(pg, text)
        return
    body = m.group("body")
    entries = [e for e in re.findall(r'"([^"]*)"', body) if e != PLUGIN_CFG_RES]
    if entries:
        new_body = ", ".join(f'"{e}"' for e in entries)
        new_line = f"{m.group('prefix')}{new_body}{m.group('suffix')}"
    else:
        new_line = f"{m.group('prefix')}{m.group('suffix')}"
    text = text[: m.start()] + new_line + text[m.end() :]
    _write_project_godot(pg, text)


def teardown_addon(project_root: Path) -> None:
    dest = project_root / "addons" / ADDON_NAME
    if dest.exists():
        shutil.rmtree(dest)
    # remove empty addons dir? leave it


def write_request(project_root: Path, mode: str) -> Path:
    vision = project_root / ".gdskills" / "vision"
    raw = vision / "raw"
    raw.mkdir(parents=True, exist_ok=True)
    done = vision / "done"
    if done.exists():
        done.unlink()
    # clear old raw pngs for this session
    for p in raw.glob("*.png"):
        p.unlink(missing_ok=True)
    req = vision / "request"
    req.write_text(mode.strip().lower() + "\n", encoding="utf-8")
    return req


def wait_done(project_root: Path, timeout: float) -> Path:
    vision = project_root / ".gdskills" / "vision"
    done = vision / "done"
    raw = vision / "raw"
    deadline = time.time() + timeout
    while time.time() < deadline:
        if done.is_file():
            # wait for size stable
            time.sleep(0.15)
            pngs = sorted(raw.glob("*.png"), key=lambda p: p.stat().st_mtime, reverse=True)
            if pngs:
                p0 = pngs[0]
                s1 = p0.stat().st_size
                time.sleep(0.1)
                if p0.stat().st_size == s1 and s1 > 0:
                    return p0
        time.sleep(0.25)
    raise SystemExit(
        f"Timed out waiting for editor bridge handshake under {vision}. "
        "Open the Godot editor on this project (plugin auto-captures when enabled), "
        "or pass --keep-bridge and enable addons/_gdskills_agent_vision manually."
    )


def encode_raw_png(
    png: Path,
    out_webp: Path,
    *,
    quality: int,
    short_edge: int = 512,
    max_edge: Optional[int] = None,
) -> Tuple[Path, int]:
    im = Image.open(png)
    return save_webp(im, out_webp, short_edge=short_edge, max_edge=max_edge, quality=quality)


def run_editor_capture(
    *,
    project_root: Path,
    out_dir: Path,
    mode: str = "3d",
    label: Optional[str] = None,
    quality: int = 80,
    short_edge: int = 512,
    max_edge: Optional[int] = None,
    timeout: float = 120.0,
    godot_bin: Optional[str] = None,
    keep_bridge: bool = False,
) -> int:
    from datetime import datetime
    import re as _re

    def slug(text: str) -> str:
        s = _re.sub(r"[^a-zA-Z0-9]+", "-", text.strip().lower()).strip("-")
        return (s or "editor")[:32]

    project_root = Path(project_root).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    prev_enabled = None
    changed = False
    try:
        stage_addon(project_root)
        changed, prev_enabled = enable_plugin(project_root)
        write_request(project_root, mode)
        print(f"staged=addons/{ADDON_NAME}")
        print(f"plugin_enabled_changed={changed}")
        print("action=Open/focus Godot editor on this project so the TEMP plugin can capture.")
        if godot_bin:
            import subprocess

            print(f"launching={godot_bin} -e --path {project_root}")
            subprocess.Popen(
                [godot_bin, "-e", "--path", str(project_root)],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
        png = wait_done(project_root, timeout)
        ts = datetime.now().strftime("%Y%m%d-%H%M%S")
        lab = slug(label or f"editor-{mode}")
        dest = out_dir / f"{ts}-editor-{lab}.webp"
        path, size = encode_raw_png(
            png, dest, quality=quality, short_edge=short_edge, max_edge=max_edge
        )
        print(f"wrote={path}")
        print(f"bytes={size}")
        print("mode=editor")
        # cleanup handshake
        vision = project_root / ".gdskills" / "vision"
        for name in ("request", "done"):
            p = vision / name
            p.unlink(missing_ok=True)
        png.unlink(missing_ok=True)
        return 0
    finally:
        if not keep_bridge:
            # Restore prior enabled= line when we know it; always strip our entry.
            if prev_enabled is not None and PLUGIN_CFG_RES not in prev_enabled:
                disable_plugin(project_root, prev_enabled)
            else:
                disable_plugin(project_root, None)
            teardown_addon(project_root)
            print("teardown=ok")
        else:
            print("teardown=skipped (--keep-bridge)")
