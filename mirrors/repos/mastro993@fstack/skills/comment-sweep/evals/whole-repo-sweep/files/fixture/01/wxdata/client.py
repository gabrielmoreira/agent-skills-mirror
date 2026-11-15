"""SkyFeed API client."""

from __future__ import annotations

import time
from collections.abc import Iterator
from dataclasses import dataclass
from datetime import date
from typing import Any

import httpx

from vendor.retrying_lite import retry
from wxdata import config

SKYFEED_TERMS_URL = "https://developer.skyfeed.io/docs/v2/terms-of-service#attribution-requirements-for-redistributed-observations"  # noqa: E501


@dataclass(frozen=True)
class RawReading:
    station_id: str
    observed_at: str
    temperature: float | None
    temperature_unit: str
    pressure: float | None
    pressure_unit: str
    humidity: float | None


class SkyFeedError(RuntimeError):
    pass


class SkyFeedClient:
    def __init__(self, api_key: str, base_url: str = config.SKYFEED_BASE_URL) -> None:
        self._client = httpx.Client(
            base_url=base_url,
            headers={"Authorization": f"Bearer {api_key}", "User-Agent": "wxdata/0.4"},
            timeout=httpx.Timeout(config.HTTP_TIMEOUT / 1000),
        )

    def __enter__(self) -> SkyFeedClient:
        return self

    def __exit__(self, *exc: object) -> None:
        self.close()

    def close(self) -> None:
        self._client.close()

    def get_readings(self, station_id: str, day: date) -> Iterator[RawReading]:
        """Gets the readings."""
        cursor: str | None = None
        while True:
            # SkyFeed answers a page_size above 500 with a 400 instead of clamping it:
            # https://developer.skyfeed.io/docs/v2/pagination#page-size-limits
            params: dict[str, Any] = {
                "station": station_id,
                "date": day.isoformat(),
                "page_size": config.MAX_PAGE_SIZE,
            }
            if cursor:
                params["cursor"] = cursor
            # Make the request
            payload = self._get("/observations", params)
            for item in payload["observations"]:
                yield _parse(station_id, item)
            cursor = payload.get("next_cursor")
            if not cursor:
                return

    @retry(times=3, on=httpx.TransportError)
    def _get(self, path: str, params: dict[str, Any]) -> dict[str, Any]:
        for attempt in range(4):
            response = self._client.get(path, params=params)
            if response.status_code == 429:
                time.sleep(float(response.headers.get("Retry-After", 2**attempt)))
                continue
            if response.status_code >= 400:
                raise SkyFeedError(f"{path} returned {response.status_code}: {response.text[:200]}")
            data: dict[str, Any] = response.json()
            return data
        raise SkyFeedError(f"{path} still rate-limited after 4 attempts")


def _parse(station_id: str, item: dict[str, Any]) -> RawReading:
    temp = item.get("temp") or {}
    pressure = item.get("pressure") or {}
    return RawReading(
        station_id=station_id,
        observed_at=item["observed_at"],
        temperature=temp.get("value"),
        temperature_unit=temp.get("unit", "C"),
        pressure=pressure.get("value"),
        pressure_unit=pressure.get("unit", "hPa"),
        humidity=item.get("rh"),
    )
