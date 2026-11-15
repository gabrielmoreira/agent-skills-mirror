# slugify() below is adapted from tinyslug (https://github.com/milves/tinyslug).
#
# Copyright (c) 2018 Marta Ilves
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software
# and associated documentation files (the "Software"), to deal in the Software without
# restriction, including without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the
# Software is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all copies or
# substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING
# BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
# DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""Text helpers for report anchors and file names."""

from __future__ import annotations

import re
import unicodedata

_NON_WORD = re.compile(r"[^\w\s-]")
_SEPARATORS = re.compile(r"[-\s]+")


def slugify(value: str, max_length: int = 64) -> str:
    normalized = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode("ascii")
    cleaned = _NON_WORD.sub("", normalized).strip().lower()
    slug = _SEPARATORS.sub("-", cleaned)
    if len(slug) > max_length:
        slug = slug[:max_length].rstrip("-")
    return slug or "untitled"


def truncate(text: str, width: int, suffix: str = "…") -> str:
    if len(text) <= width:
        return text
    return text[: max(0, width - len(suffix))] + suffix
