"""Render HTML exposing window.renderAt(seconds) to MP4. Requires Playwright + FFmpeg."""
import argparse
import functools
import http.server
import math
import shutil
import subprocess
import sys
import tempfile
import threading
from pathlib import Path
from urllib.parse import quote


class QuietHandler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *_args):
        pass


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("html", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--duration", type=float, default=12)
    parser.add_argument("--fps", type=int, default=30)
    parser.add_argument("--width", type=int, default=1920)
    parser.add_argument("--height", type=int, default=1080)
    parser.add_argument("--audio", type=Path)
    args = parser.parse_args()
    if not math.isfinite(args.duration) or args.duration <= 0 or args.fps <= 0:
        parser.error("duration and fps must be positive finite numbers")
    if any(v <= 0 or v % 2 for v in [args.width, args.height]):
        parser.error("width and height must be positive even numbers")
    source, output = args.html.resolve(), args.output.resolve()
    if not source.is_file():
        parser.error("HTML file does not exist")
    if output.exists():
        parser.error("Output exists; choose a new filename")
    if output.suffix.lower() != ".mp4":
        parser.error("Output must use .mp4")
    if args.audio and not args.audio.is_file():
        parser.error("Audio file does not exist")
    ffmpeg = shutil.which("ffmpeg")
    if not ffmpeg:
        parser.error("FFmpeg missing from PATH. See references/rendering.md")
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        parser.error("Install playwright and its Chromium browser. See references/rendering.md")
    frame_count = math.ceil(args.duration * args.fps)
    handler = functools.partial(QuietHandler, directory=str(source.parent))
    server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    process = None
    try:
        output.parent.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(prefix=".render-", dir=output.parent) as temp, sync_playwright() as pw:
            temp = Path(temp)
            browser = pw.chromium.launch(headless=True)
            page = browser.new_page(viewport={"width": args.width, "height": args.height}, device_scale_factor=1)
            errors = []
            page.on("pageerror", lambda error: errors.append(str(error)))
            page.goto(f"http://127.0.0.1:{server.server_port}/{quote(source.name)}?export=1", wait_until="load")
            page.evaluate("document.fonts.ready")
            if not page.evaluate("typeof window.renderAt === 'function'"):
                raise RuntimeError("Missing window.renderAt(t); adapt the HTML using references/rendering.md")
            command = [ffmpeg, "-hide_banner", "-loglevel", "error", "-y", "-f", "image2pipe", "-vcodec", "png", "-framerate", str(args.fps), "-i", "pipe:0"]
            if args.audio:
                command += ["-i", str(args.audio.resolve()), "-map", "0:v:0", "-map", "1:a:0", "-af", "apad", "-c:a", "aac"]
            command += ["-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "18", "-preset", "medium", "-t", str(frame_count / args.fps), "-movflags", "+faststart", str(temp / "video.mp4")]
            with (temp / "ffmpeg.log").open("w+b") as log:
                process = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.DEVNULL, stderr=log)
                try:
                    for frame in range(frame_count):
                        page.evaluate("async t => { await window.renderAt(t); }", frame / args.fps)
                        if errors:
                            raise RuntimeError("Browser error: " + errors[0])
                        process.stdin.write(page.screenshot(type="png"))
                        if frame % args.fps == 0:
                            print(f"Rendering {frame}/{frame_count} frames", flush=True)
                    process.stdin.close()
                    code = process.wait(timeout=120)
                    if code:
                        log.seek(0)
                        raise RuntimeError(log.read().decode("utf-8", errors="replace"))
                finally:
                    if process.poll() is None:
                        process.kill()
                        process.wait()
                    if process.stdin and not process.stdin.closed:
                        process.stdin.close()
            browser.close()
            if output.exists():
                raise RuntimeError("Output was created by another process; refusing to replace it")
            shutil.move(str(temp / "video.mp4"), str(output))
    finally:
        server.shutdown()
        server.server_close()
        thread.join()
    print(f"Saved {output} | {args.width}x{args.height} | {args.fps} fps | {frame_count / args.fps:.3f}s | audio: {bool(args.audio)}")


if __name__ == "__main__":
    main()
