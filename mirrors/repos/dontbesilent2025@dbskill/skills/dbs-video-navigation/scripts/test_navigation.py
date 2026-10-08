#!/usr/bin/env python3
"""Run deterministic regression checks; optional real render via --render DIR."""
import copy
import os
import wave
import subprocess
import json
from pathlib import Path
import sys
import tempfile
import unittest
import navigation as nav

SRT = """1
00:00:00,000 --> 00:00:00,900
这是开场。

2
00:00:01,000 --> 00:00:02,000
先明确你希望服务谁。

3
00:00:02,001 --> 00:00:03,500
再看看这些人在哪里。

4
00:00:03,501 --> 00:00:04,500
接下来确定内容方向。

5
00:00:04,501 --> 00:00:06,000
选择你能够持续回答的问题。
"""

def fixture(root):
    srt = root / "input.srt"
    srt.write_text(SRT, encoding="utf-8")
    return {"schema_version": 1, "source": {"subtitles": "input.srt", "sha256": nav.digest(srt)},
            "target": {"width": 1920, "height": 2560, "nav_height": 280, "fps": "30000/1001"},
            "duration": 6, "coverage": [1, 6], "segments": [
                {"chapter": "platform", "title": "第一部分：选择平台", "question": "如何找到你的目标观众？", "start": 1, "end": 3.501},
                {"chapter": "direction", "title": "第二部分：确定方向", "question": "哪些问题值得持续回答？", "start": 3.501, "end": 6}]}

class Checks(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.p = fixture(self.root)

    def tearDown(self):
        self.tmp.cleanup()

    def test_absolute_frames_and_subtitle_anchors(self):
        s = nav.validate(self.p, self.root)
        self.assertEqual(s["frames"], 150)
        self.assertEqual(s["rows"][1]["frame_start"], 75)
        self.assertEqual(s["rows"][0]["last_subtitle"]["text"], "再看看这些人在哪里。")
        self.assertAlmostEqual(s["placement"], 1.001)

    def test_changed_source_rejected(self):
        (self.root / "input.srt").write_text(SRT + "\n", encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "字幕已变化"):
            nav.validate(self.p, self.root)

    def test_missing_and_overlapping_timeline(self):
        for offset in (-0.1, 0.1):
            p = copy.deepcopy(self.p)
            p["segments"][1]["start"] += offset
            with self.assertRaisesRegex(ValueError, "无缺口"):
                nav.validate(p, self.root)

    def test_time_ambiguity(self):
        with self.assertRaises(ValueError):
            nav.number("20:20")
        self.assertEqual(nav.number("00:00:20.020"), 20.02)

    def test_invalid_dimensions(self):
        self.p["target"]["width"] = 1919
        with self.assertRaises(ValueError):
            nav.validate(self.p, self.root)

    def test_subframe_segment(self):
        self.p["segments"][0]["end"] = 1.001
        self.p["segments"][1]["start"] = 1.001
        with self.assertRaisesRegex(ValueError, "不足一帧"):
            nav.validate(self.p, self.root)

    def test_sorted_and_overlap_review(self):
        (self.root / "input.srt").write_text("1\n00:00:02,000 --> 00:00:04,000\n后文\n\n2\n00:00:01,000 --> 00:00:03,000\n前文\n", encoding="utf-8")
        entries, warnings = nav.subtitles(self.root / "input.srt")
        self.assertEqual(entries[0]["text"], "前文")
        self.assertEqual(len(warnings), 2)

    def test_preset_cannot_change_canvas(self):
        old = nav.CONFIG
        try:
            nav.CONFIG = self.root / "config"
            self.assertNotIn("fps", nav.preset())
            self.assertNotIn("width", nav.preset())
        finally:
            nav.CONFIG = old

    def test_single_line_and_visual_only_segment(self):
        self.p["segments"][0]["question"] = ""
        self.assertEqual(nav.validate(self.p, self.root)["rows"][0]["question"], "")
        self.p["source"] = {}
        with self.assertRaisesRegex(ValueError, "visual_evidence"):
            nav.validate(self.p, self.root)
        for segment in self.p["segments"]:
            segment["visual_evidence"] = [{"time": segment["start"], "note": "界面切换到对应步骤"}]
        rows = nav.validate(self.p, self.root)["rows"]
        self.assertIsNone(rows[0]["first_subtitle"])
        self.p["segments"][0]["visual_evidence"][0]["time"] = 99
        with self.assertRaises(ValueError):
            nav.validate(self.p, self.root)

    def test_video_version_change(self):
        video = self.root / "input.mp4"
        video.write_bytes(b"sample")
        self.p["source"].update(video=str(video), video_size=6)
        nav.validate(self.p, self.root)
        video.write_bytes(b"different")
        with self.assertRaisesRegex(ValueError, "原视频版本"):
            nav.validate(self.p, self.root)

    def test_merge_uses_sample_offsets_not_service_duration(self):
        segments = []
        for i in range(2):
            path = self.root / f"segment-{i}.wav"
            with wave.open(str(path), "wb") as f:
                f.setparams((1, 2, 16000, 0, "NONE", "not compressed"))
                f.writeframes(b"\0\0" * 16000)
            (self.root / f"segment-{i}.srt").write_text("1\n00:00:00,100 --> 00:00:00,900\n原文 unchanged\n")
            segments.append(dict(audio=path.name, subtitles=f"segment-{i}.srt", offset_samples=i*16000,
                                 samples=16000, duration_seconds=1.144, sha256=nav.digest(path)))
        manifest = self.root / "audio-manifest.json"
        nav.write(manifest, dict(sample_rate=16000, segments=segments))
        out = self.root / "merged.srt"
        nav.merge_subtitles(manifest, out)
        rows, warnings = nav.subtitles(out)
        self.assertEqual(rows[1]["start"], 1.1)
        self.assertEqual(rows[1]["text"], "原文 unchanged")
        self.assertFalse(warnings)
        with self.assertRaises(FileExistsError):
            nav.merge_subtitles(manifest, out)
        (self.root / segments[0]["audio"]).write_bytes(b"changed")
        with self.assertRaisesRegex(ValueError, "音频分段已变化"):
            nav.merge_subtitles(manifest, self.root / "new.srt")

    def test_subtitle_beyond_duration_and_repeated_chapter(self):
        self.p["duration"] = 5
        self.p["coverage"] = [1, 5]
        with self.assertRaisesRegex(ValueError, "字幕超出"):
            nav.validate(self.p, self.root)
        self.p["duration"] = 6
        self.p["coverage"] = [1, 6]
        self.p["segments"].append(dict(chapter="platform", title="回顾", question="", start=4.501, end=6))
        self.p["segments"][1]["end"] = 4.501
        with self.assertRaisesRegex(ValueError, "大章节必须连续"):
            nav.validate(self.p, self.root)

    def test_fractional_fps_and_offsets(self):
        for fps in ("24", "25", "30", "60", "30000/1001", "24000/1001"):
            self.p["target"]["fps"] = fps
            s = nav.validate(self.p, self.root)
            self.assertLessEqual(abs(s["placement"]-1), 0.5 / float(nav.Fraction(fps)))
            self.assertEqual(s["rows"][-1]["frame_end"], s["frames"])

    def test_invalid_secondary_line(self):
        self.p["segments"][0]["question"] = "line one\nline two"
        with self.assertRaisesRegex(ValueError, "第二行"):
            nav.validate(self.p, self.root)

def integration(root):
    root.mkdir(parents=True, exist_ok=False)
    for name, width, height, nav_height, fps, single in [
        ("portrait", 1920, 2560, 280, "30000/1001", False),
        ("landscape", 1280, 720, 188, "25", False),
        ("single", 1080, 1920, 160, "60", True),
        ("visual", 1280, 720, 188, "24", False),
        ("multilingual", 1280, 720, 188, "30", False),
    ]:
        case = root / name
        case.mkdir()
        project = fixture(case)
        project["target"] = dict(width=width, height=height, nav_height=nav_height, fps=fps)
        if name == "multilingual":
            for segment in project["segments"]:
                segment["title"] = "第一章 / Chapter 1"
                segment["question"] = "手順と確認 / 단계 확인"
        if single:
            for segment in project["segments"]:
                segment["question"] = ""
        if name == "visual":
            project["source"] = {}
            for segment in project["segments"]:
                segment["visual_evidence"] = [{"time": segment["start"], "note": "合成画面定位"}]
        if os.environ.get("NAV_TEST_FONT_REGULAR"):
            project["style"] = dict(font_title_path=os.environ["NAV_TEST_FONT_BOLD"],
                                    font_question_path=os.environ["NAV_TEST_FONT_REGULAR"])
        nav.write(case / "project.json", project)
        nav.render(case / "project.json", case / "output")
        info = nav.probe(case / "output/navigation-full.mp4")
        assert len(info["streams"]) == 1 and info["streams"][0]["width"] == width
    case = root / "overflow"
    case.mkdir()
    project = fixture(case)
    project["segments"][0]["title"] = "超长标题" * 80
    if os.environ.get("NAV_TEST_FONT_REGULAR"):
        project["style"] = dict(font_title_path=os.environ["NAV_TEST_FONT_BOLD"], font_question_path=os.environ["NAV_TEST_FONT_REGULAR"])
    nav.write(case / "project.json", project)
    try:
        nav.render(case / "project.json", case / "output")
        raise AssertionError("overflowing title was accepted")
    except (ValueError, subprocess.CalledProcessError):
        pass
    # Exercise a late audio start, sample-exact split and a silent source.
    source = root / "delayed.mp4"
    subprocess.run([nav.executable("ffmpeg"), "-v", "error", "-n", "-f", "lavfi", "-i", "color=size=320x240:rate=25:duration=3",
                    "-itsoffset", "0.5", "-f", "lavfi", "-i", "sine=frequency=440:sample_rate=16000:duration=2",
                    "-c:v", "libx264", "-c:a", "aac", str(source)], check=True)
    manifest = nav.extract_audio(source, root / "audio", 1)
    assert manifest["segments"][1]["offset_samples"] == 16000
    with wave.open(str(root / "audio/timeline.wav"), "rb") as f:
        import array
        samples = array.array("h", f.readframes(f.getnframes()))
    assert max(abs(x) for x in samples[:4800]) < 20
    assert max(abs(x) for x in samples[11200:16000]) > 100
    try:
        nav.extract_audio(source, root / "audio", 1)
        raise AssertionError("existing output overwritten")
    except FileExistsError:
        pass
    silent = root / "silent.mp4"
    subprocess.run([nav.executable("ffmpeg"), "-v", "error", "-n", "-f", "lavfi", "-i", "color=size=320x240:duration=1", "-c:v", "libx264", str(silent)], check=True)
    try:
        nav.extract_audio(silent, root / "silent-audio")
        raise AssertionError("missing audio not rejected")
    except ValueError as exc:
        assert "没有音轨" in str(exc)
    print("Integration passed: 5 renders, text-overflow rejection, delayed audio, PCM offsets, no-audio rejection")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--render":
        integration(Path(sys.argv[2]).resolve())
    else:
        unittest.main()
