from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
import unittest
from datetime import datetime
from pathlib import Path


SKILL_DIR = Path(__file__).resolve().parents[1]
PUBLISH_MODULE_PATH = SKILL_DIR / "scripts/publish_longform.py"
BUILD_MODULE_PATH = SKILL_DIR / "scripts/build_payload.py"


def load_module(module_name: str, path: Path):
    spec = importlib.util.spec_from_file_location(module_name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class TestPublishLongformHelpers(unittest.TestCase):
    def setUp(self) -> None:
        self.module = load_module("publish_longform", PUBLISH_MODULE_PATH)
        self.tempdir = tempfile.TemporaryDirectory()
        self.base = Path(self.tempdir.name)

    def tearDown(self) -> None:
        self.tempdir.cleanup()

    def write_payload(self, payload: dict) -> Path:
        path = self.base / "payload.json"
        path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
        return path

    def test_load_payload_accepts_valid_structure(self) -> None:
        image1 = self.base / "1.png"
        image2 = self.base / "2.png"
        image1.write_bytes(b"one")
        image2.write_bytes(b"two")
        payload_path = self.write_payload(
            {
                "title": "作为一名在读博士生，我在日常是如何与AI协作的？",
                "parts": ["<p>part1</p>", "<p>part2</p>", "<p>part3</p>"],
                "images": [str(image1), str(image2)],
            }
        )

        payload = self.module.load_payload(payload_path)

        self.assertEqual(payload.title, "作为一名在读博士生，我在日常是如何与AI协作的？")
        self.assertEqual(len(payload.parts), 3)
        self.assertEqual(payload.images, [image1.resolve(), image2.resolve()])

    def test_load_payload_rejects_parts_and_images_mismatch(self) -> None:
        image1 = self.base / "1.png"
        image1.write_bytes(b"one")
        payload_path = self.write_payload(
            {
                "title": "标题",
                "parts": ["<p>part1</p>", "<p>part2</p>", "<p>part3</p>"],
                "images": [str(image1)],
            }
        )

        with self.assertRaises(self.module.PayloadValidationError):
            self.module.load_payload(payload_path)

    def test_build_title_prefix_normalizes_whitespace_and_length(self) -> None:
        prefix = self.module.build_title_prefix(
            "  作为一名在读博士生，我在日常是如何与AI协作的？  ", limit=10
        )

        self.assertEqual(prefix, "作为一名在读博士生，")

    def test_card_matches_requires_prefix_and_visibility(self) -> None:
        card_text = "仅自己可见\n作为一名在读博士生，我在日常是如何与AI协\n发布于 2026年03月07日 00:42"

        self.assertTrue(
            self.module.card_matches(
                card_text=card_text,
                title_prefix="作为一名在读博士生",
                visibility_text="仅自己可见",
            )
        )
        self.assertFalse(
            self.module.card_matches(
                card_text=card_text,
                title_prefix="别的标题",
                visibility_text="仅自己可见",
            )
        )

    def test_card_matches_can_require_current_date(self) -> None:
        card_text = "审核中\n仅自己可见\n我为什么把 AI 当同事\n2026-06-10 17:13"

        self.assertTrue(
            self.module.card_matches(
                card_text=card_text,
                title_prefix="我为什么把 AI 当同事",
                visibility_text="仅自己可见",
                date_prefix="2026-06-10",
            )
        )
        self.assertFalse(
            self.module.card_matches(
                card_text=card_text,
                title_prefix="我为什么把 AI 当同事",
                visibility_text="仅自己可见",
                date_prefix="2026-06-09",
            )
        )

    def test_card_matches_can_require_recent_publish_window(self) -> None:
        card_text = "审核中\n仅自己可见\n我为什么把 AI 当同事\n2026-06-10 17:13"

        self.assertTrue(
            self.module.card_matches(
                card_text=card_text,
                title_prefix="我为什么把 AI 当同事",
                visibility_text="仅自己可见",
                date_prefix="2026-06-10",
                published_after=datetime(2026, 6, 10, 17, 12),
            )
        )
        self.assertFalse(
            self.module.card_matches(
                card_text=card_text,
                title_prefix="我为什么把 AI 当同事",
                visibility_text="仅自己可见",
                date_prefix="2026-06-10",
                published_after=datetime(2026, 6, 10, 17, 20),
            )
        )


class TestBuildPayloadHelpers(unittest.TestCase):
    def setUp(self) -> None:
        self.module = load_module("build_payload", BUILD_MODULE_PATH)
        self.tempdir = tempfile.TemporaryDirectory()
        self.base = Path(self.tempdir.name)

    def tearDown(self) -> None:
        self.tempdir.cleanup()

    def test_xhs_safe_rich_preserves_headings_lists_and_quotes(self) -> None:
        html = """
        <h2 class="bad">前言</h2>
        <blockquote><p>主线很简单：<strong>AI 入口贴近任务</strong></p></blockquote>
        <h3>贯穿全文的方法论</h3>
        <ul><li><p><strong>经验沉淀</strong>：固化为 <code>Skill</code></p></li></ul>
        <hr />
        """

        safe_html = self.module.to_xhs_safe_rich_html(html)

        self.assertIn("<h2>前言</h2>", safe_html)
        self.assertIn("<blockquote>", safe_html)
        self.assertIn("<h3>贯穿全文的方法论</h3>", safe_html)
        self.assertIn("<ul>", safe_html)
        self.assertIn("<li>", safe_html)
        self.assertIn("Skill", safe_html)
        self.assertNotIn("<code", safe_html)
        self.assertNotIn("<hr", safe_html)
        self.assertNotIn("class=", safe_html)

    def test_build_payload_xhs_safe_rich_keeps_structure_without_markdown_artifacts(self) -> None:
        image = self.base / "01.png"
        image.write_bytes(b"image")
        markdown_path = self.base / "note.md"
        markdown_path.write_text(
            """# 我为什么把 AI 当同事

## 前言

> 本文的主线很简单：**AI 入口要贴近任务**。

### 贯穿全文的方法论

- **经验沉淀**：把流程固化为 `Skill`

![图](01.png)

### 后续小标题

正文。
""",
            encoding="utf-8",
        )

        payload = self.module.build_payload(
            markdown_path=markdown_path,
            image_dir=None,
            image_paths=[image],
            title_override=None,
            allow_count_mismatch=False,
            xhs_safe_rich=True,
        )

        self.assertEqual(payload["title"], "我为什么把 AI 当同事")
        self.assertEqual(len(payload["parts"]), 2)
        self.assertEqual(len(payload["images"]), 1)
        first_part = payload["parts"][0]
        self.assertIn("<h2>前言</h2>", first_part)
        self.assertIn("<blockquote>", first_part)
        self.assertIn("<h3>贯穿全文的方法论</h3>", first_part)
        self.assertIn("<ul>", first_part)
        self.assertNotIn("##", first_part)
        self.assertNotIn("`", first_part)
        self.assertNotIn("<code", first_part)


if __name__ == "__main__":
    unittest.main()
