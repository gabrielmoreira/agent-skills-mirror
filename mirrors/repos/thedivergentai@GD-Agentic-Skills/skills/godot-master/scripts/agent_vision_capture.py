#!/usr/bin/env python3
"""
godot-agent-vision capture CLI — agentic eyes (not an in-game feature).

Modes: asset | region | window | screen | editor
Output: {project}/.gdskills/vision/*.webp (gitignored)
"""

from __future__ import annotations

import argparse
import os
import platform
import re
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# Local imports when run as script
_SCRIPTS = Path(__file__).resolve().parent
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))

def _import_local(mod: str, alt: str):
    try:
        return __import__(mod, fromlist=["*"])
    except ImportError:
        return __import__(alt, fromlist=["*"])


_asset_sheet = _import_local("asset_sheet", "agent_vision_asset_sheet")
_ensure_gitignore = _import_local("ensure_gitignore", "agent_vision_ensure_gitignore")
_webp_encode = _import_local("webp_encode", "agent_vision_webp_encode")

collect_images = _asset_sheet.collect_images
contact_sheet = _asset_sheet.contact_sheet
single_asset = _asset_sheet.single_asset
ensure_gitignore = _ensure_gitignore.ensure_gitignore
DEFAULT_SHORT_EDGE = _webp_encode.DEFAULT_SHORT_EDGE
DETAIL_MAX_EDGE = _webp_encode.DETAIL_MAX_EDGE
DEFAULT_QUALITY = _webp_encode.DEFAULT_QUALITY
save_webp = _webp_encode.save_webp
try:
    from PIL import Image
except ImportError as e:  # pragma: no cover
    raise SystemExit("Missing Pillow. Install: pip install -r requirements-vision.txt") from e


def _set_dpi_aware_windows() -> None:
    if platform.system() != "Windows":
        return
    try:
        import ctypes

        awareness = ctypes.c_void_p(-4)  # DPI_AWARENESS_CONTEXT_PER_MONITOR_AWARE_V2
        ctypes.windll.user32.SetProcessDpiAwarenessContext(awareness)
    except Exception:
        try:
            import ctypes

            ctypes.windll.shcore.SetProcessDpiAwareness(2)
        except Exception:
            pass


def _slug(text: str, max_len: int = 32) -> str:
    s = re.sub(r"[^a-zA-Z0-9]+", "-", text.strip().lower()).strip("-")
    return (s or "capture")[:max_len]


def _vision_dir(project_root: Path, out: Optional[Path]) -> Path:
    base = out if out else project_root / ".gdskills" / "vision"
    base.mkdir(parents=True, exist_ok=True)
    return base


def _stamp_name(mode: str, label: Optional[str], sheet: bool = False) -> str:
    ts = datetime.now().strftime("%Y%m%d-%H%M%S")
    parts = [ts, mode]
    if label:
        parts.append(_slug(label))
    if sheet:
        parts.append("sheet")
    return "-".join(parts) + ".webp"


def _mss_to_image(shot: Any) -> Image.Image:
    return Image.frombytes("RGB", shot.size, shot.rgb)


def _grab_mss_monitor(monitor: int = 0) -> Image.Image:
    import mss

    with mss.MSS() as sct:
        mons = sct.monitors
        if monitor < 0 or monitor >= len(mons):
            raise SystemExit(f"Invalid --monitor {monitor}; available 0..{len(mons)-1} (0=virtual all)")
        return _mss_to_image(sct.grab(mons[monitor]))


def _grab_mss_region(x: int, y: int, w: int, h: int) -> Image.Image:
    import mss

    if w <= 0 or h <= 0:
        raise SystemExit("region width/height must be positive")
    with mss.MSS() as sct:
        return _mss_to_image(sct.grab({"left": x, "top": y, "width": w, "height": h}))


def _linux_session() -> str:
    st = (os.environ.get("XDG_SESSION_TYPE") or "").lower()
    if st in ("wayland", "x11"):
        return st
    if os.environ.get("WAYLAND_DISPLAY"):
        return "wayland"
    if os.environ.get("DISPLAY"):
        return "x11"
    return "unknown"


def _grab_linux_screen_or_region(
    *,
    monitor: int = 0,
    region: Optional[Tuple[int, int, int, int]] = None,
) -> Image.Image:
    session = _linux_session()
    if session == "wayland":
        return _grab_wayland(region=region, monitor=monitor)
    # X11 / unknown: try mss
    try:
        if region:
            return _grab_mss_region(*region)
        return _grab_mss_monitor(monitor)
    except Exception as e:
        raise SystemExit(
            f"Linux capture failed ({session}): {e}. "
            "On Wayland install grim; on X11 ensure DISPLAY and mss work."
        ) from e


def _grab_wayland(
    *,
    region: Optional[Tuple[int, int, int, int]] = None,
    monitor: int = 0,
) -> Image.Image:
    import shutil
    import tempfile

    grim = shutil.which("grim")
    if not grim:
        raise SystemExit(
            "Wayland session detected but `grim` not found. "
            "Install grim (wlroots) or run under X11 for mss capture. "
            "Silent window-by-title is not available on Wayland."
        )
    with tempfile.TemporaryDirectory() as td:
        out = Path(td) / "cap.png"
        cmd = [grim]
        if region:
            x, y, w, h = region
            cmd += ["-g", f"{x},{y} {w}x{h}"]
        elif monitor > 0:
            # grim -o OUTPUT; without output names we capture all
            pass
        cmd.append(str(out))
        try:
            subprocess.run(cmd, check=True, capture_output=True, text=True)
        except subprocess.CalledProcessError as e:
            raise SystemExit(f"grim failed: {e.stderr or e}") from e
        return Image.open(out).convert("RGB")


def _list_windows_win() -> List[Tuple[int, str]]:
    import ctypes
    from ctypes import wintypes

    user32 = ctypes.windll.user32
    results: List[Tuple[int, str]] = []

    @ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM)
    def _enum(hwnd, _lparam):
        if not user32.IsWindowVisible(hwnd):
            return True
        length = user32.GetWindowTextLengthW(hwnd)
        if length <= 0:
            return True
        buf = ctypes.create_unicode_buffer(length + 1)
        user32.GetWindowTextW(hwnd, buf, length + 1)
        title = buf.value.strip()
        if title:
            results.append((int(hwnd), title))
        return True

    user32.EnumWindows(_enum, 0)
    return results


def _window_rect_win(hwnd: int) -> Tuple[int, int, int, int]:
    import ctypes
    from ctypes import wintypes

    rect = wintypes.RECT()
    ctypes.windll.user32.GetWindowRect(hwnd, ctypes.byref(rect))
    return rect.left, rect.top, rect.right - rect.left, rect.bottom - rect.top


def _grab_window_win(title_substr: str) -> Tuple[Image.Image, str]:
    needle = title_substr.lower()
    matches = [(h, t) for h, t in _list_windows_win() if needle in t.lower()]
    if not matches:
        raise SystemExit(f"No visible window title contains: {title_substr!r}")
    # Prefer longest title match (more specific)
    matches.sort(key=lambda x: len(x[1]), reverse=True)
    hwnd, title = matches[0]
    x, y, w, h = _window_rect_win(hwnd)
    if w <= 1 or h <= 1:
        raise SystemExit(f"Window appears minimized or invalid size: {title!r}")
    return _grab_mss_region(x, y, w, h), title


def _grab_window_macos(title_substr: str) -> Tuple[Image.Image, str]:
    # Best-effort via Quartz if available; else fail with guidance
    try:
        from Quartz import (  # type: ignore
            CGWindowListCopyWindowInfo,
            CGWindowListCreateImage,
            kCGNullWindowID,
            kCGWindowImageBoundsIgnoreFraming,
            kCGWindowImageNominalResolution,
            kCGWindowListExcludeDesktopElements,
            kCGWindowListOptionIncludingWindow,
            kCGWindowListOptionOnScreenOnly,
            CGRectNull,
        )
    except Exception as e:
        raise SystemExit(
            "macOS window capture needs pyobjc-framework-Quartz "
            "(pip install pyobjc-framework-Quartz). "
            f"Import error: {e}. Or use screen/region modes."
        ) from e

    opts = kCGWindowListOptionOnScreenOnly | kCGWindowListExcludeDesktopElements
    infos = CGWindowListCopyWindowInfo(opts, kCGNullWindowID) or []
    needle = title_substr.lower()
    matches = []
    for info in infos:
        name = str(info.get("kCGWindowName") or "")
        owner = str(info.get("kCGWindowOwnerName") or "")
        blob = f"{name} {owner}".lower()
        if needle in blob and info.get("kCGWindowNumber"):
            matches.append((info["kCGWindowNumber"], name or owner, info))
    if not matches:
        raise SystemExit(f"No on-screen window matches title: {title_substr!r}")
    matches.sort(key=lambda x: len(x[1]), reverse=True)
    wid, title, info = matches[0]
    cgimg = CGWindowListCreateImage(
        CGRectNull,
        kCGWindowListOptionIncludingWindow,
        wid,
        kCGWindowImageBoundsIgnoreFraming | kCGWindowImageNominalResolution,
    )
    if cgimg is None:
        raise SystemExit(
            "CGWindowListCreateImage returned None — grant Screen Recording "
            "to this Python/IDE binary (System Settings → Privacy → Screen Recording)."
        )
    # Convert via temporary PNG using Quartz/AppKit or mss region fallback
    try:
        from AppKit import NSBitmapImageRep, NSPNGFileType  # type: ignore
        import tempfile

        rep = NSBitmapImageRep.alloc().initWithCGImage_(cgimg)
        data = rep.representationUsingType_properties_(NSPNGFileType, None)
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tf:
            tf.write(bytes(data))
            tmp = tf.name
        im = Image.open(tmp).convert("RGB")
        Path(tmp).unlink(missing_ok=True)
        return im, title
    except Exception:
        # Fallback: bounds crop via mss
        bounds = info.get("kCGWindowBounds") or {}
        x = int(bounds.get("X", 0))
        y = int(bounds.get("Y", 0))
        w = int(bounds.get("Width", 0))
        h = int(bounds.get("Height", 0))
        if w <= 0 or h <= 0:
            raise SystemExit("Could not decode macOS window image or bounds")
        return _grab_mss_region(x, y, w, h), title


def _grab_window_linux(title_substr: str) -> Tuple[Image.Image, str]:
    if _linux_session() == "wayland":
        raise SystemExit(
            "Window-by-title is not available on Wayland for silent agent capture. "
            "Use screen/region, compositor IPC manually, or the editor bridge."
        )
    # X11 via wmctrl or xdotool if present
    import shutil

    wmctrl = shutil.which("wmctrl")
    if wmctrl:
        proc = subprocess.run([wmctrl, "-l"], capture_output=True, text=True, check=False)
        needle = title_substr.lower()
        for line in proc.stdout.splitlines():
            parts = line.split(None, 3)
            if len(parts) < 4:
                continue
            wid, title = parts[0], parts[3]
            if needle in title.lower():
                geo = subprocess.run(
                    ["xdotool", "getwindowgeometry", "--shell", wid],
                    capture_output=True,
                    text=True,
                    check=False,
                )
                env: Dict[str, str] = {}
                for row in geo.stdout.splitlines():
                    if "=" in row:
                        k, v = row.split("=", 1)
                        env[k] = v
                if "WIDTH" in env:
                    x, y = int(env.get("X", 0)), int(env.get("Y", 0))
                    w, h = int(env["WIDTH"]), int(env["HEIGHT"])
                    return _grab_mss_region(x, y, w, h), title
    raise SystemExit(
        "Linux window capture needs X11 + wmctrl/xdotool, or use region/screen/editor modes."
    )


def grab_window(title: str) -> Tuple[Image.Image, str]:
    system = platform.system()
    if system == "Windows":
        return _grab_window_win(title)
    if system == "Darwin":
        return _grab_window_macos(title)
    return _grab_window_linux(title)


def grab_screen(monitor: int = 0) -> Image.Image:
    if platform.system() == "Linux":
        return _grab_linux_screen_or_region(monitor=monitor)
    return _grab_mss_monitor(monitor)


def grab_region(x: int, y: int, w: int, h: int) -> Image.Image:
    if platform.system() == "Linux":
        return _grab_linux_screen_or_region(region=(x, y, w, h))
    return _grab_mss_region(x, y, w, h)


def cmd_list_windows() -> int:
    system = platform.system()
    if system == "Windows":
        for hwnd, title in _list_windows_win():
            print(f"{hwnd}\t{title}")
        return 0
    if system == "Darwin":
        try:
            from Quartz import (  # type: ignore
                CGWindowListCopyWindowInfo,
                kCGNullWindowID,
                kCGWindowListExcludeDesktopElements,
                kCGWindowListOptionOnScreenOnly,
            )
        except Exception as e:
            print(f"error: Quartz unavailable: {e}", file=sys.stderr)
            return 1
        opts = kCGWindowListOptionOnScreenOnly | kCGWindowListExcludeDesktopElements
        for info in CGWindowListCopyWindowInfo(opts, kCGNullWindowID) or []:
            name = info.get("kCGWindowName") or ""
            owner = info.get("kCGWindowOwnerName") or ""
            wid = info.get("kCGWindowNumber")
            if name or owner:
                print(f"{wid}\t{owner}\t{name}")
        return 0
    print("list-windows: limited on this OS; use wmctrl -l on X11", file=sys.stderr)
    return 1


def cmd_editor(args: argparse.Namespace) -> int:
    try:
        from agent_vision_stage_editor_bridge import run_editor_capture
    except ImportError:
        from agent_vision_stage_editor_bridge import run_editor_capture

    return run_editor_capture(
        project_root=Path(args.project_root).resolve(),
        out_dir=_vision_dir(Path(args.project_root), args.out),
        mode=args.editor_mode,
        label=args.label,
        quality=args.quality,
        short_edge=args.short_edge,
        max_edge=_effective_max_edge(args),
        timeout=args.timeout,
        godot_bin=args.godot,
        keep_bridge=args.keep_bridge,
    )


def _effective_max_edge(args: argparse.Namespace) -> Optional[int]:
    """None => short-edge mode; int => detail long-edge cap."""
    if getattr(args, "detail", False):
        return args.max_edge if args.max_edge and args.max_edge > 0 else DETAIL_MAX_EDGE
    if args.max_edge is not None and args.max_edge > 0:
        return args.max_edge
    return None


def build_parser() -> argparse.ArgumentParser:
    common = argparse.ArgumentParser(add_help=False)
    common.add_argument(
        "--project-root",
        type=Path,
        default=Path.cwd(),
        help="Godot project root (contains project.godot). Default: cwd",
    )
    common.add_argument("--out", type=Path, default=None, help="Override output dir")
    common.add_argument("--quality", type=int, default=DEFAULT_QUALITY)
    common.add_argument(
        "--short-edge",
        type=int,
        default=DEFAULT_SHORT_EDGE,
        help="Default analysis budget: lowest edge px (identity/overview). Default 512.",
    )
    common.add_argument(
        "--max-edge",
        type=int,
        default=None,
        help="Detail/layout budget: long-edge px. Implies detail mode when set.",
    )
    common.add_argument(
        "--detail",
        action="store_true",
        help=f"Use long-edge detail budget (default {DETAIL_MAX_EDGE}) instead of short-edge 512.",
    )
    common.add_argument("--label", type=str, default=None)
    common.add_argument("--skip-gitignore", action="store_true")
    p = argparse.ArgumentParser(
        prog="capture.py",
        description="GDSkills agent vision capture (WebP). Not an in-game Autoload.",
        parents=[common],
    )

    sub = p.add_subparsers(dest="mode", required=True)

    s = sub.add_parser("screen", help="Capture a monitor (0=all virtual)", parents=[common])
    s.add_argument("--monitor", type=int, default=0)

    r = sub.add_parser("region", help="Capture screen region", parents=[common])
    r.add_argument("--x", type=int, required=True)
    r.add_argument("--y", type=int, required=True)
    r.add_argument("--w", type=int, required=True)
    r.add_argument("--h", type=int, required=True)

    w = sub.add_parser("window", help="Capture window by title substring", parents=[common])
    w.add_argument("--title", type=str, required=True)

    a = sub.add_parser("asset", help="Rasterize asset file(s) or folder to WebP", parents=[common])
    a.add_argument("--paths", nargs="+", type=Path, required=True)
    a.add_argument("--sheet", action="store_true", help="Contact sheet (max 2x2)")
    a.add_argument("--no-recursive", action="store_true")

    e = sub.add_parser(
        "editor",
        help="Stage temp editor bridge, capture, teardown",
        parents=[common],
    )
    e.add_argument("--editor-mode", choices=("2d", "3d", "main"), default="3d")
    e.add_argument("--timeout", type=float, default=120.0)
    e.add_argument("--godot", type=str, default=None, help="Godot binary (optional)")
    e.add_argument("--keep-bridge", action="store_true", help="Skip teardown (debug)")

    sub.add_parser("list-windows", help="List capturable window titles", parents=[common])
    sub.add_parser("doctor", help="Dependency / permission smoke checks", parents=[common])
    return p


def cmd_doctor() -> int:
    print(f"platform={platform.system()} {platform.release()}")
    print(f"python={sys.executable}")
    try:
        import mss as _mss

        print(f"mss={_mss.__version__}")
    except Exception as e:
        print(f"mss=MISSING ({e})")
    try:
        import PIL

        print(f"pillow={PIL.__version__}")
    except Exception as e:
        print(f"pillow=MISSING ({e})")
    if platform.system() == "Linux":
        print(f"session={_linux_session()}")
    if platform.system() == "Darwin":
        print("note=Grant Screen Recording to this Python/IDE binary if captures are wallpaper-only")
    print("ok")
    return 0


def main(argv: Optional[List[str]] = None) -> int:
    _set_dpi_aware_windows()
    args = build_parser().parse_args(argv)

    if args.mode == "list-windows":
        return cmd_list_windows()
    if args.mode == "doctor":
        return cmd_doctor()

    project_root = Path(args.project_root).resolve()
    if not args.skip_gitignore:
        ensure_gitignore(project_root)

    if args.mode == "editor":
        return cmd_editor(args)

    out_dir = _vision_dir(project_root, args.out)
    label = args.label
    im: Image.Image
    sheet = False

    if args.mode == "screen":
        im = grab_screen(args.monitor)
        label = label or f"monitor{args.monitor}"
    elif args.mode == "region":
        im = grab_region(args.x, args.y, args.w, args.h)
        label = label or "region"
    elif args.mode == "window":
        im, title = grab_window(args.title)
        label = label or title
    elif args.mode == "asset":
        paths = collect_images(
            args.paths,
            project_root=project_root,
            recursive=not args.no_recursive,
        )
        if not paths:
            raise SystemExit(
                "No image assets found for --paths "
                "(resolve res:// against --project-root; check extensions)"
            )
        if args.sheet or len(paths) > 1:
            im = contact_sheet(paths)
            sheet = True
            label = label or "assets"
        else:
            im = single_asset(paths[0])
            label = label or paths[0].stem
    else:
        raise SystemExit(f"Unknown mode: {args.mode}")

    name = _stamp_name(args.mode, label, sheet=sheet)
    dest = out_dir / name
    max_edge = _effective_max_edge(args)
    path, size = save_webp(
        im,
        dest,
        short_edge=args.short_edge,
        max_edge=max_edge,
        quality=args.quality,
    )
    print(f"wrote={path}")
    print(f"bytes={size}")
    print(f"mode={args.mode}")
    if max_edge:
        print(f"budget=long-edge:{max_edge}")
    else:
        print(f"budget=short-edge:{args.short_edge}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
