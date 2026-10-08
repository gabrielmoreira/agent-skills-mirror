#!/usr/bin/env python3
"""Deterministic subtitle preparation, reusable presets and navigation rendering."""
import argparse
import hashlib
import json
import math
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import wave
from fractions import Fraction

ROOT = Path(__file__).resolve().parents[1]
CONFIG = Path(os.environ.get("DBS_VIDEO_NAV_HOME", str(Path.home() / ".dbs/video-navigation")))

def read(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))

def write(path, data):
    with Path(path).open("x", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def digest(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()

def number(value):
    # Only numeric seconds or explicit HH:MM:SS.mmm. Never guess MM:SS vs frames.
    if isinstance(value, str) and ":" in value:
        if not re.fullmatch(r"\d{2,}:\d{2}:\d{2}[.,]\d{3}", value):
            raise ValueError("时间必须为数值秒或 HH:MM:SS.mmm，拒绝歧义时间：" + value)
        h, m, s = value.replace(",", ".").split(":")
        if int(m) >= 60 or float(s) >= 60:
            raise ValueError("非法时间：" + value)
        value = int(h) * 3600 + int(m) * 60 + float(s)
    result = float(value)
    if not math.isfinite(result) or result < 0:
        raise ValueError("时间必须为非负有限值")
    return result

def stamp(value):
    ms = round(value * 1000)
    return f"{ms//3600000:02}:{ms//60000%60:02}:{ms//1000%60:02}.{ms%1000:03}"

def subtitles(path):
    text = Path(path).read_text(encoding="utf-8-sig").replace("\r\n", "\n").replace("\r", "\n")
    entries = []
    for index, block in enumerate(re.split(r"\n\s*\n", text.strip()), 1):
        lines = block.splitlines()
        timing = next((i for i, line in enumerate(lines) if "-->" in line), None)
        if timing is None:
            raise ValueError(f"第 {index} 个字幕块没有时间戳")
        match = re.fullmatch(r"\s*(\d{2,}:\d{2}:\d{2}[,.]\d{3})\s*-->\s*(\d{2,}:\d{2}:\d{2}[,.]\d{3})\s*", lines[timing])
        if not match:
            raise ValueError(f"第 {index} 个字幕块时间戳无效")
        start, end = map(number, match.groups())
        content = "\n".join(lines[timing + 1:])
        if end <= start or not content.strip():
            raise ValueError(f"第 {index} 个字幕块为空或持续时间无效")
        entries.append(dict(id=index, start=start, end=end, text=content))
    if not entries:
        raise ValueError("字幕为空")
    warnings = []
    if entries != sorted(entries, key=lambda x: (x["start"], x["id"])):
        warnings.append("字幕原始顺序异常，已按时间排序；原始 id 保留")
    entries.sort(key=lambda x: (x["start"], x["id"]))
    furthest = 0
    for row in entries:
        if row["start"] < furthest:
            warnings.append(f"字幕 {row['id']} 与前文存在时间重叠，需审核板块边界")
        furthest = max(furthest, row["end"])
    return entries, warnings

def executable(name, override=None):
    result = override or os.environ.get(name.upper()) or shutil.which(name)
    if not result and name == "ffmpeg":
        try:
            import imageio_ffmpeg
            result = imageio_ffmpeg.get_ffmpeg_exe()
        except ImportError:
            pass
    if not result:
        raise ValueError(f"缺少 {name}，请提供路径或安装依赖")
    return result

def probe(path, tool=None):
    command = [executable("ffprobe", tool), "-v", "error", "-show_streams", "-show_format", "-of", "json", str(path)]
    result = json.loads(subprocess.check_output(command, text=True))
    return result

def preset(name=None):
    if name:
        if not re.fullmatch(r"[a-z0-9][a-z0-9_-]*", name):
            raise ValueError("预设名仅支持英文小写、数字、下划线和连字符")
        return read(CONFIG / "presets" / (name + ".json"))
    config = CONFIG / "config.json"
    if config.exists():
        return preset(read(config)["default_preset"])
    return read(ROOT / "assets/blue.json")

def validate(project, base):
    if project.get("schema_version") != 1:
        raise ValueError("不支持的项目版本")
    target = project["target"]
    w, h, nh = (target[k] for k in ("width", "height", "nav_height"))
    if any(type(x) is not int or x <= 0 or x % 2 for x in (w, h, nh)) or nh >= h:
        raise ValueError("画布与导航尺寸必须为正偶数，导航高度小于画布高度")
    fps = Fraction(str(target["fps"]))
    if fps <= 0 or fps > 240:
        raise ValueError("目标帧率必须在 (0, 240]，分数帧率用 30000/1001 等字符串")
    duration = number(project["duration"])
    start, end = map(number, project["coverage"])
    if not 0 <= start < end <= duration:
        raise ValueError("覆盖时间必须位于原片总时长内")
    if project["source"].get("video"):
        video = (base / project["source"]["video"]).resolve()
        stat = video.stat()
        for key, actual in (("video_size", stat.st_size), ("video_mtime_ns", stat.st_mtime_ns)):
            if key in project["source"] and project["source"][key] != actual:
                raise ValueError("原视频版本已变化，需重新核对时间轴")
    source = (base / project["source"]["subtitles"]).resolve() if project["source"].get("subtitles") else None
    entries, warnings = subtitles(source) if source else ([], [])
    if source and digest(source) != project["source"].get("sha256"):
        raise ValueError("字幕已变化：请重新分析或核对章节，禁止沿用旧时间轴")
    if max((x["end"] for x in entries), default=0) > duration + 1 / float(fps):
        raise ValueError("字幕超出原片总时长，需核对素材版本")
    if warnings and not project.get("subtitle_warnings_reviewed"):
        raise ValueError("字幕异常尚未审核：" + "; ".join(warnings[:5]))
    style = project.get("style") or preset(project.get("preset"))
    default = read(ROOT / "assets/blue.json")
    style = {**default, **style}
    for key in ("background", "foreground", "progress", "track"):
        if not re.fullmatch(r"#[0-9A-Fa-f]{6}", style[key]):
            raise ValueError(f"{key} 必须为 #RRGGBB")
    for key in default:
        if key.endswith("_ratio") and (not isinstance(style[key], (int, float)) or not 0 < style[key] < 0.5):
            raise ValueError(f"非法布局比例：{key}")
    if style["title_ratio"] <= style["question_ratio"]:
        raise ValueError("第一行字号必须大于第二行")
    def frame(t):
        return math.floor(Fraction(str(t)) * fps + Fraction(1, 2))
    first, last = frame(start), frame(end)
    if last - first < 2:
        raise ValueError("覆盖区间至少需要两帧")
    cursor, rows, closed, active = start, [], set(), None
    for index, segment in enumerate(project["segments"], 1):
        a, b = number(segment["start"]), number(segment["end"])
        if abs(a - cursor) > 0.000001 or b <= a:
            raise ValueError("板块必须连续、无重叠、无缺口；跳过开头用 coverage")
        if any(not isinstance(segment.get(k), str) or not segment[k].strip() or "\n" in segment[k] for k in ("chapter", "title")):
            raise ValueError("章节 id 和标题必须为非空单行文字")
        if not isinstance(segment.get("question", ""), str) or "\n" in segment.get("question", ""):
            raise ValueError("第二行必须为单行文字或空字符串")
        if segment["chapter"] != active:
            if segment["chapter"] in closed:
                raise ValueError("大章节必须连续；回顾内容应使用独立章节 id")
            if active is not None:
                closed.add(active)
            active = segment["chapter"]
        fa, fb = frame(a), frame(b)
        if fb <= fa:
            raise ValueError("存在不足一帧的板块")
        selected = [x for x in entries if a <= x["start"] < b]
        if not selected:
            evidence = segment.get("visual_evidence", [])
            if not evidence or any(not isinstance(e, dict) or not a <= number(e.get("time", -1)) < b or not isinstance(e.get("note"), str) or not e["note"].strip() for e in evidence):
                raise ValueError(f"板块 {index} 没有字幕；必须提供区间内实际查看画面的 visual_evidence 时间和说明")
        rows.append({**segment, "question": segment.get("question", ""), "start": a, "end": b, "frame_start": fa-first, "frame_end": fb-first,
                     "first_subtitle": selected[0] if selected else None, "last_subtitle": selected[-1] if selected else None, "index": index})
        cursor = b
    if not rows or abs(cursor - end) > 0.000001:
        raise ValueError("板块未覆盖全部 coverage 区间")
    return dict(rows=rows, style=style, fps=str(fps), width=w, height=nh, frames=last-first,
                placement=first / float(fps), end=last / float(fps), warnings=warnings,
                source_path=str(source) if source else None, source_sha256=digest(source) if source else None)

def pngs(spec, out):
    rows = []
    for row in spec["rows"]:
        slug = re.sub(r"[^\w\u3400-\u9fff-]+", "_", row["title"])[:36]
        row["image"] = f"{row['index']:02}_{slug}.png"
        rows.append({**row, "png": str(out / row["image"])})
    render = {"width": spec["width"], "height": spec["height"], "style": spec["style"], "rows": rows}
    write(out / "render-spec.json", render)
    if sys.platform == "darwin" and shutil.which("swift") and not spec["style"].get("font_title_path"):
        subprocess.run([executable("swift"), str(ROOT / "scripts/text.swift"), str(out / "render-spec.json")], check=True)
    else:
        try:
            from PIL import Image, ImageDraw, ImageFont
        except ImportError as exc:
            raise ValueError("文字渲染需要 macOS Swift/AppKit，或 Pillow 和两种字重的字体路径；先运行 doctor") from exc
        if not all(spec["style"].get(f"font_{field}_path") for field in ("title", "question")):
            raise ValueError("请在 style 指定 font_title_path 和 font_question_path，或使用 macOS Swift/AppKit")
        s, w, h = spec["style"], spec["width"], spec["height"]
        for row in rows:
            img = Image.new("RGB", (w, h), s["background"])
            draw = ImageDraw.Draw(img)
            bottom = 0
            for field in ("title", "question"):
                if not row[field]:
                    continue
                font = ImageFont.truetype(s[f"font_{field}_path"], round(w*s[f"{field}_ratio"]), index=s.get(f"font_{field}_index", 0))
                x, y = round(w*s["margin_ratio"]), round(w*s[f"{field}_top_ratio"])
                box = draw.textbbox((0, 0), row[field], font=font, anchor="lt")
                if box[2] > w-2*x or y < bottom or y+box[3] > h-w*(s["track_bottom_ratio"]+s["track_height_ratio"])-8:
                    raise ValueError("文字超宽或高度不足，请调整文案或布局")
                draw.text((x, y), row[field], font=font, fill=s["foreground"], anchor="lt")
                bottom = y+box[3]
            img.save(row["png"])

def render(project_path, output, ffmpeg=None):
    project_path, out = Path(project_path).resolve(), Path(output).resolve()
    project = read(project_path)
    spec = validate(project, project_path.parent)
    ff = executable("ffmpeg", ffmpeg)
    out.mkdir(parents=True, exist_ok=False)
    snapshot = {**project, "source": {**project["source"], "subtitles": spec["source_path"]}, "style": spec["style"]}
    write(out / "project.json", snapshot)
    pngs(spec, out)
    fps = float(Fraction(spec["fps"]))
    lines = ["ffconcat version 1.0"]
    # Generated ASCII aliases avoid concat quoting issues with user text and paths.
    for row in spec["rows"]:
        alias = f"frame-{row['index']:03}.png"
        shutil.copyfile(out / row["image"], out / alias)
        lines.extend([f"file '{alias}'", f"option framerate {spec['fps']}", f"duration {(row['frame_end']-row['frame_start'])/fps:.12f}"])
    lines.append(f"file 'frame-{spec['rows'][-1]['index']:03}.png'")
    lines.append(f"option framerate {spec['fps']}")
    (out / "frames.txt").write_text("\n".join(lines), encoding="utf-8")
    s, w, h, count = spec["style"], spec["width"], spec["height"], spec["frames"]
    margin = round(w*s["margin_ratio"])
    tw = w-2*margin
    th = max(2, round(w*s["track_height_ratio"]))
    ty = h-round(w*s["track_bottom_ratio"])-th
    gap = max(2, round(w*s["gap_ratio"]))
    # At most one command per pixel; long videos stay inexpensive to encode.
    commands = {}
    for fill in range(1, tw+1):
        f = math.ceil(fill/tw*(count-1))
        commands[f] = fill
    (out / "progress.txt").write_text("\n".join(f"{f/fps:.12f} drawbox@progress w {fill};" for f, fill in sorted(commands.items())), encoding="utf-8")
    filters = [f"fps={spec['fps']}:start_time=0:round=near", "format=rgb24",
               f"drawbox=x={margin}:y={ty}:w={tw}:h={th}:color={s['track']}:t=fill",
               "sendcmd=f=progress.txt",
               f"drawbox@progress=x={margin}:y={ty}:w=1:h={th}:color={s['progress']}:t=fill"]
    chapter = spec["rows"][0]["chapter"]
    for row in spec["rows"][1:]:
        if row["chapter"] != chapter:
            x = margin+round(tw*row["frame_start"]/count)-gap//2
            filters.append(f"drawbox=x={x}:y={ty}:w={gap}:h={th}:color={s['background']}:t=fill")
            chapter = row["chapter"]
    filters.append("format=yuv420p")
    (out / "filters.txt").write_text(",".join(filters), encoding="utf-8")
    filename = "navigation-full.mp4"
    cmd = [ff, "-hide_banner", "-nostdin", "-n", "-f", "concat", "-safe", "0", "-i", "frames.txt",
           "-vf", (out / "filters.txt").read_text(encoding="utf-8"), "-frames:v", str(count), "-fps_mode", "passthrough", "-an",
           "-c:v", "libx264", "-preset", "veryfast", "-crf", "14", "-pix_fmt", "yuv420p", "-movflags", "+faststart", filename]
    with (out / "encode.log").open("w") as log:
        subprocess.run(cmd, cwd=out, stdout=log, stderr=log, check=True)
    # Full decode, independent of encode success; count frames and inspect stream metadata.
    checked = subprocess.run([ff, "-hide_banner", "-v", "info", "-xerror", "-i", str(out / filename), "-map", "0:v:0", "-an", "-progress", "pipe:1", "-f", "null", "-"], capture_output=True, text=True, check=True)
    counts = re.findall(r"^frame=(\d+)", checked.stdout, re.M)
    if not counts or int(counts[-1]) != count:
        raise ValueError("完整解码帧数与计划不一致")
    write(out / "validation.json", {"decoded_frames": int(counts[-1]), "expected_frames": count,
          "fps": spec["fps"], "duration": count/fps, "dimensions": [w, h], "placement": spec["placement"],
          "end": spec["end"], "source_sha256": spec["source_sha256"], "warnings": spec["warnings"],
          "visual_review_required": True})
    write(out / "timeline.json", spec["rows"])
    table = ["# 时间轴与字幕定位", "", "时间为原片绝对时间；结束时间不包含该帧。字幕按起始时间归属，保留原文。", "", "| 编号 | 标题／问题 | 开始 | 结束 | 第一条字幕 | 最后一条字幕 |", "|---|---|---|---|---|---|"]
    def cell(v):
        return str(v).replace("|", "\\|").replace("\n", "<br>")
    for r in spec["rows"]:
        table.append("| " + " | ".join(map(cell, [r["index"], r["title"]+"／"+r["question"], stamp(spec["placement"]+r["frame_start"]/fps), stamp(spec["placement"]+r["frame_end"]/fps), r["first_subtitle"]["text"] if r["first_subtitle"] else "无对白；见画面依据", r["last_subtitle"]["text"] if r["last_subtitle"] else "无对白；见画面依据"])) + " |")
    (out / "时间轴.md").write_text("\n".join(table), encoding="utf-8")
    (out / "使用说明.md").write_text(f"# 导航视频使用说明\n\n导入 navigation-full.mp4，从原视频 {stamp(spec['placement'])} 放置，到 {stamp(spec['end'])} 结束。\n\n正常速度，无音轨，尺寸 {w} × {h}，帧率 {spec['fps']}，时长 {count/fps:.6f} 秒。\n\n目标画布 {project['target']['width']} × {project['target']['height']}；保持原尺寸，顶部水平居中，不要拉伸成全画幅。前后未覆盖区间无导航。\n\nproject.json 保存此次参数快照。修改原片剪辑或字幕后必须重新核对时间轴。图片是文字层，动态进度条位于 MP4 中。\n", encoding="utf-8")
    print(json.dumps({"output": str(out), "frames": count, "duration": count/fps}, ensure_ascii=False))

def doctor():
    """Report capabilities without installing packages or reading credentials."""
    import importlib.util
    report = {"python": sys.version.split()[0], "platform": sys.platform,
              "swift": shutil.which("swift"), "pillow": importlib.util.find_spec("PIL") is not None}
    for name in ("ffmpeg", "ffprobe"):
        try:
            path = executable(name)
            result = subprocess.run([path, "-version"], capture_output=True, text=True, check=True)
            report[name] = {"path": path, "version": result.stdout.splitlines()[0]}
        except (ValueError, OSError, subprocess.CalledProcessError) as exc:
            report[name] = {"error": str(exc)}
    if "error" not in report["ffmpeg"]:
        path = report["ffmpeg"]["path"]
        enc = subprocess.check_output([path, "-hide_banner", "-encoders"], text=True, stderr=subprocess.DEVNULL)
        filters = subprocess.check_output([path, "-hide_banner", "-filters"], text=True, stderr=subprocess.DEVNULL)
        report["libx264"] = "libx264" in enc
        report["required_filters"] = {name: name in filters for name in ("sendcmd", "drawbox", "aresample")}
    return report

def extract_audio(video, output, segment_seconds=900):
    """Produce PCM segments with sample-exact offsets on the source playback timeline."""
    if segment_seconds <= 0 or not math.isfinite(segment_seconds):
        raise ValueError("分段时长必须为正有限秒数")
    video, out = Path(video).resolve(), Path(output).resolve()
    metadata = probe(video)
    if not any(s.get("codec_type") == "audio" for s in metadata["streams"]):
        raise ValueError("视频没有音轨：需要画面分析或用户提供定位，不能虚构转写")
    out.mkdir(parents=True, exist_ok=False)
    wav = out / "timeline.wav"
    cmd = [executable("ffmpeg"), "-hide_banner", "-nostdin", "-v", "error", "-n",
           "-copyts", "-start_at_zero", "-i", str(video), "-map", "0:a:0",
           "-af", "aresample=16000:async=1:first_pts=0", "-ac", "1", "-c:a", "pcm_s16le", str(wav)]
    subprocess.run(cmd, check=True)
    segments = []
    with wave.open(str(wav), "rb") as src:
        rate = src.getframerate()
        chunk = max(1, round(segment_seconds * rate))
        offset = 0
        while offset < src.getnframes():
            count = min(chunk, src.getnframes() - offset)
            filename = f"segment-{len(segments)+1:03}.wav"
            with wave.open(str(out / filename), "wb") as target:
                target.setparams(src.getparams())
                target.writeframes(src.readframes(count))
            segments.append({"audio": filename, "subtitles": filename.replace(".wav", ".srt"),
                             "offset_samples": offset, "samples": count, "offset_seconds": offset / rate,
                             "duration_seconds": count / rate, "sha256": digest(out / filename)})
            offset += count
    manifest = {"source_video": str(video), "source_size": video.stat().st_size,
                "source_mtime_ns": video.stat().st_mtime_ns, "probe": metadata,
                "sample_rate": rate, "decoded_duration": offset / rate, "segments": segments,
                "timeline_basis": "source playback start=0; original timestamps, gaps and audio delay preserved as PCM"}
    write(out / "audio-manifest.json", manifest)
    return manifest

def merge_subtitles(manifest_path, output):
    manifest_path, output = Path(manifest_path).resolve(), Path(output)
    manifest = read(manifest_path)
    entries = []
    cursor = 0
    rate = manifest["sample_rate"]
    if type(rate) is not int or rate <= 0:
        raise ValueError("非法 sample_rate")
    for segment in manifest["segments"]:
        if segment["offset_samples"] != cursor or type(segment["samples"]) is not int or segment["samples"] <= 0:
            raise ValueError("音频分段必须连续且样本数为正整数")
        audio = manifest_path.parent / segment["audio"]
        if digest(audio) != segment["sha256"]:
            raise ValueError("音频分段已变化，需重新转写")
        srt = manifest_path.parent / segment["subtitles"]
        # An empty file explicitly records a segment with no recognized speech.
        rows, warnings = subtitles(srt) if srt.read_text(encoding="utf-8-sig").strip() else ([], [])
        if warnings:
            raise ValueError("分段字幕有顺序或重叠异常，请先核对：" + "; ".join(warnings))
        if rows and max(r["end"] for r in rows) > segment["samples"] / rate + 0.05:
            raise ValueError("分段字幕超出音频时长；核对转写引擎时间基准")
        for row in rows:
            entries.append({**row, "start": row["start"] + cursor / rate,
                            "end": row["end"] + cursor / rate})
        cursor += segment["samples"]
    if not entries:
        raise ValueError("没有识别到对白，使用实际画面证据分析，不生成虚假字幕")
    text = "\n\n".join(f"{i}\n{stamp(r['start']).replace('.', ',')} --> {stamp(r['end']).replace('.', ',')}\n{r['text']}" for i, r in enumerate(entries, 1)) + "\n"
    with output.open("x", encoding="utf-8") as f:
        f.write(text)
    return {"output": str(output), "entries": len(entries), "duration": cursor / rate}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("doctor")
    p = sub.add_parser("extract-audio"); p.add_argument("video"); p.add_argument("output"); p.add_argument("--segment-seconds", type=float, default=900)
    p = sub.add_parser("merge-subtitles"); p.add_argument("manifest"); p.add_argument("output")
    p = sub.add_parser("prepare"); p.add_argument("srt"); p.add_argument("output")
    p = sub.add_parser("probe"); p.add_argument("video"); p.add_argument("--ffprobe")
    p = sub.add_parser("validate"); p.add_argument("project")
    p = sub.add_parser("render"); p.add_argument("project"); p.add_argument("output"); p.add_argument("--ffmpeg")
    p = sub.add_parser("preset-show"); p.add_argument("--name")
    p = sub.add_parser("preset-save"); p.add_argument("name"); p.add_argument("style"); p.add_argument("--default", action="store_true")
    args = parser.parse_args()
    if args.command == "doctor":
        print(json.dumps(doctor(), ensure_ascii=False, indent=2))
    elif args.command == "extract-audio":
        print(json.dumps(extract_audio(args.video, args.output, args.segment_seconds), ensure_ascii=False, indent=2))
    elif args.command == "merge-subtitles":
        print(json.dumps(merge_subtitles(args.manifest, args.output), ensure_ascii=False, indent=2))
    elif args.command == "prepare":
        rows, warnings = subtitles(args.srt)
        write(args.output, {"source": {"subtitles": str(Path(args.srt).resolve()), "sha256": digest(args.srt)}, "entries": rows, "warnings": warnings})
    elif args.command == "probe":
        print(json.dumps(probe(args.video, args.ffprobe), ensure_ascii=False, indent=2))
    elif args.command == "validate":
        print(json.dumps(validate(read(args.project), Path(args.project).resolve().parent), ensure_ascii=False, indent=2))
    elif args.command == "render":
        render(args.project, args.output, args.ffmpeg)
    elif args.command == "preset-show":
        print(json.dumps(preset(args.name), ensure_ascii=False, indent=2))
    else:
        if not re.fullmatch(r"[a-z0-9][a-z0-9_-]*", args.name):
            raise ValueError("预设名无效")
        style = read(args.style)
        allowed = set(read(ROOT / "assets/blue.json")) | {"font_title_path", "font_question_path", "font_title_index", "font_question_index"}
        if not set(style) <= allowed:
            raise ValueError("样式预设不能包含画布、帧率、时间轴或其他项目字段")
        if args.default and (CONFIG / "config.json").exists():
            raise ValueError("默认配置已存在；请保留旧版本后显式更新，不覆盖")
        target = CONFIG / "presets"
        target.mkdir(parents=True, exist_ok=True)
        write(target / (args.name + ".json"), style)
        if args.default:
            config = CONFIG / "config.json"
            # Keep existing defaults; explicit new names never silently replace them.
            write(config, {"default_preset": args.name})

if __name__ == "__main__":
    try:
        main()
    except (ValueError, KeyError, OSError, subprocess.CalledProcessError, ImportError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        sys.exit(1)
