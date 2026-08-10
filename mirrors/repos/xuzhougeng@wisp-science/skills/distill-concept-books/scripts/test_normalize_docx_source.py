#!/usr/bin/env python3
"""Small standard-library regression test for normalize_docx_source.py."""

from __future__ import annotations

import base64
import hashlib
import json
import tempfile
import unittest
import zipfile
from pathlib import Path

from normalize_docx_source import NormalizationError, normalize_docx


ONE_PIXEL_PNG = base64.b64decode(
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNk+A8AAQUBAScY42YAAAAASUVORK5CYII="
)

DOCUMENT_XML = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"
 xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"
 xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main">
 <w:body>
  <w:p><w:pPr><w:pStyle w:val="Heading1"/></w:pPr><w:r><w:t>第一章</w:t></w:r></w:p>
  <w:p><w:r><w:t xml:space="preserve">Cafe\u0301   test</w:t></w:r></w:p>
  <w:p><w:r><w:drawing><a:blip r:embed="rId5"/></w:drawing></w:r></w:p>
  <w:tbl>
   <w:tr><w:tc><w:p><w:r><w:t>A</w:t></w:r></w:p></w:tc><w:tc><w:p><w:r><w:t>B</w:t></w:r></w:p></w:tc></w:tr>
   <w:tr><w:tc><w:p><w:r><w:t>C</w:t></w:r></w:p></w:tc><w:tc><w:p><w:r><w:t>D</w:t></w:r></w:p></w:tc></w:tr>
  </w:tbl>
  <w:sectPr/>
 </w:body>
</w:document>
"""

STYLES_XML = """<?xml version="1.0" encoding="UTF-8"?>
<w:styles xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
 <w:style w:type="paragraph" w:styleId="Heading1">
  <w:name w:val="heading 1"/><w:pPr><w:outlineLvl w:val="0"/></w:pPr>
 </w:style>
</w:styles>
"""

RELS_XML = """<?xml version="1.0" encoding="UTF-8"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
 <Relationship Id="rId5" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/image" Target="media/image1.png"/>
</Relationships>
"""

CORE_XML = """<?xml version="1.0" encoding="UTF-8"?>
<cp:coreProperties xmlns:cp="http://schemas.openxmlformats.org/package/2006/metadata/core-properties"
 xmlns:dc="http://purl.org/dc/elements/1.1/">
 <dc:title>测试图书</dc:title><dc:creator>测试作者</dc:creator>
</cp:coreProperties>
"""


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def create_fixture(path: Path) -> None:
    with zipfile.ZipFile(path, "w", compression=zipfile.ZIP_DEFLATED) as package:
        package.writestr("word/document.xml", DOCUMENT_XML)
        package.writestr("word/styles.xml", STYLES_XML)
        package.writestr("word/_rels/document.xml.rels", RELS_XML)
        package.writestr("word/media/image1.png", ONE_PIXEL_PNG)
        package.writestr("docProps/core.xml", CORE_XML)


class NormalizeDocxSourceTest(unittest.TestCase):
    def test_normalizes_deterministically_and_preserves_source_and_media(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source = root / "fixture.docx"
            first = root / "first"
            second = root / "second"
            create_fixture(source)
            source_before = sha256(source)

            summary = normalize_docx(source, first, "book-test-001")
            normalize_docx(source, second, "book-test-001")

            self.assertEqual(source_before, sha256(source))
            self.assertTrue(summary["source_unchanged"])
            self.assertEqual(summary["block_count"], 4)
            self.assertEqual(summary["heading_count"], 1)
            self.assertEqual(summary["table_count"], 1)
            self.assertEqual(summary["image_asset_count"], 1)
            self.assertEqual((first / "media/image1.png").read_bytes(), ONE_PIXEL_PNG)

            records = [json.loads(line) for line in (first / "blocks.jsonl").read_text(encoding="utf-8").splitlines()]
            self.assertEqual(records[1]["raw_text"], "Cafe\u0301   test")
            self.assertEqual(records[1]["normalized_text"], "Caf\u00e9 test")
            self.assertEqual(records[3]["normalized_text"], "A\tB\nC\tD")
            self.assertEqual(records[2]["locator"]["heading_path"], ["第一章"])
            self.assertEqual(records[2]["locator"]["figure_ids"], ["figure-000001"])
            self.assertEqual(records[3]["locator"]["table_id"], "table-000001")

            first_files = {
                path.relative_to(first).as_posix(): path.read_bytes()
                for path in first.rglob("*") if path.is_file()
            }
            second_files = {
                path.relative_to(second).as_posix(): path.read_bytes()
                for path in second.rglob("*") if path.is_file()
            }
            self.assertEqual(first_files, second_files)

    def test_refuses_to_overwrite_nonempty_output(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source = root / "fixture.docx"
            output = root / "output"
            create_fixture(source)
            output.mkdir()
            (output / "keep.txt").write_text("do not overwrite", encoding="utf-8")

            with self.assertRaises(NormalizationError):
                normalize_docx(source, output, "book-test-001")
            self.assertEqual((output / "keep.txt").read_text(encoding="utf-8"), "do not overwrite")


if __name__ == "__main__":
    unittest.main()
