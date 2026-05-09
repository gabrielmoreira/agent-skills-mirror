"""GET /supported-terms。"""

from __future__ import annotations

from typing import List

from .http import MiCarTrialError, http_get_json


def get_supported_terms() -> List[int]:
    envelope = http_get_json("/free/access/product/trial/aggregate/supported-terms")
    data = envelope.get("data")
    if not isinstance(data, list) or not data:
        raise MiCarTrialError(f"/supported-terms returned empty or non-list data: {data!r}")
    for t in data:
        if not isinstance(t, int):
            raise MiCarTrialError(f"/supported-terms data contains non-int element: {t!r}")
    return sorted(data)
