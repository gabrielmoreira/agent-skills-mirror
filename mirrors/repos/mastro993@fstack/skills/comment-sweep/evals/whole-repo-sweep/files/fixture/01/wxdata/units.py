"""Temperature and pressure unit conversion."""

from __future__ import annotations

from typing import Literal

TempUnit = Literal["C", "F", "K"]

# fmt: off
PRESSURE_FACTORS_TO_HPA: dict[str, float] = {
    "hPa":  1.0,
    "mbar": 1.0,
    "kPa":  10.0,
    "inHg": 33.8639,
    "mmHg": 1.33322,
    "psi":  68.9476,
}
# fmt: on


def f_to_c(value: float) -> float:
    return (value - 32.0) * 5.0 / 9.0


def k_to_c(value: float) -> float:
    return value - 273.15


def to_celsius(value: float, unit: TempUnit) -> float:
    if unit == "C":
        return value
    if unit == "F":
        return f_to_c(value)
    # TODO(#142): drop the Kelvin branch once the last Kelvin stations are retired:
    # https://github.com/northwind-labs/wxdata/issues/142
    if unit == "K":
        return k_to_c(value)
    raise ValueError(f"unknown temperature unit: {unit!r}")


def pressure_to_hpa(value: float, unit: str) -> float:
    try:
        return value * PRESSURE_FACTORS_TO_HPA[unit]
    except KeyError:
        raise ValueError(f"unknown pressure unit: {unit!r}") from None
