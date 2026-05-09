"""金额换算：元/万元/比例 → 分（整数）。"""

from __future__ import annotations

from decimal import ROUND_HALF_UP, Decimal
from typing import Optional

from .http import MiCarTrialError


def yuan_to_fen(yuan: str) -> int:
    try:
        v = Decimal(yuan)
    except Exception as e:
        raise MiCarTrialError(f"--yuan 非法: {yuan}") from e
    return int((v * Decimal(100)).quantize(Decimal("1"), rounding=ROUND_HALF_UP))


def wan_to_fen(wan: str) -> int:
    try:
        v = Decimal(wan)
    except Exception as e:
        raise MiCarTrialError(f"--wan 非法: {wan}") from e
    return int((v * Decimal(1_000_000)).quantize(Decimal("1"), rounding=ROUND_HALF_UP))


def ratio_to_fen(
    vehicle_value_fen: int,
    rate: Optional[str] = None,
    percent: Optional[str] = None,
) -> int:
    if vehicle_value_fen <= 0:
        raise MiCarTrialError("vehicleValue 必须为正整数（分）")
    if (rate is None) == (percent is None):
        raise MiCarTrialError("--rate / --percent 必须提供且仅提供一个")

    if rate is not None:
        try:
            ratio = Decimal(rate)
        except Exception as e:
            raise MiCarTrialError(f"--rate 非法: {rate}") from e
    else:
        try:
            ratio = Decimal(percent) / Decimal(100)
        except Exception as e:
            raise MiCarTrialError(f"--percent 非法: {percent}") from e

    if ratio <= 0 or ratio >= 1:
        raise MiCarTrialError(f"比例必须在 (0, 1) 开区间，当前: {ratio}")

    return int(
        (Decimal(vehicle_value_fen) * ratio).quantize(Decimal("1"), rounding=ROUND_HALF_UP)
    )
