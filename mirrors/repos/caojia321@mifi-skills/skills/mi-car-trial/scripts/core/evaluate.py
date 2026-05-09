"""对 aggregate 响应做本地评估：首付范围 + 期数支持 + 过滤 + 分组排序。

纯函数：输入 dict，输出 dict。无 print / sys。
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple

from .http import MiCarTrialError


def _compute_down_range(
    down_info: Optional[Dict[str, Any]], vehicle_value: int
) -> Tuple[Optional[int], Optional[int]]:
    """
    字段单位：
      - amount / maxAmount: 分
      - rate / maxRate: 百万分比（rate=4600000 → 46%）
      - byAmount: true=按金额配置，false=按比例配置
    """
    if not down_info:
        return (None, None)

    amount = down_info.get("amount")
    max_amount = down_info.get("maxAmount")
    rate = down_info.get("rate")
    max_rate = down_info.get("maxRate")
    by_amount = bool(down_info.get("byAmount"))

    if by_amount and amount is not None:
        min_amt: Optional[int] = int(amount)
    elif amount is not None:
        min_amt = int(amount)
    elif rate is not None:
        min_amt = int(int(rate) * vehicle_value // 10_000_000)
    else:
        min_amt = None

    if by_amount and max_amount is not None:
        max_amt: Optional[int] = int(max_amount)
    elif max_amount is not None:
        max_amt = int(max_amount)
    elif max_rate is not None:
        max_amt = int(int(max_rate) * vehicle_value // 10_000_000)
    else:
        max_amt = None

    return (min_amt, max_amt)


def _down_supported(user_down: int, min_amt: Optional[int], max_amt: Optional[int]) -> bool:
    if min_amt is None and max_amt is None:
        return True
    if min_amt is not None and user_down < min_amt:
        return False
    if max_amt is not None and user_down > max_amt:
        return False
    return True


def _term_supported(scheme: Dict[str, Any], term_no: int) -> bool:
    ts = scheme.get("termSupported")
    if ts is False:
        return False
    supported_terms = scheme.get("supportedTerms")
    if isinstance(supported_terms, list) and supported_terms:
        try:
            return int(term_no) in [int(x) for x in supported_terms]
        except Exception:
            return True
    return True


def _classify(scheme: Dict[str, Any], user_down: int, term_no: int, vehicle_value: int) -> Dict[str, Any]:
    enriched = dict(scheme)
    min_amt, max_amt = _compute_down_range(scheme.get("downInfo"), vehicle_value)
    enriched["minAmount"] = min_amt
    enriched["maxAmount"] = max_amt
    enriched["downPaymentSupported"] = _down_supported(user_down, min_amt, max_amt)
    enriched["termSupportedResolved"] = _term_supported(scheme, term_no)
    return enriched


def evaluate_schemes(
    aggregate: Dict[str, Any],
    user_down_amount_fen: int,
    term_no: int,
    vehicle_value_fen: int,
) -> Dict[str, Any]:
    if not isinstance(aggregate, dict):
        raise MiCarTrialError("aggregate 必须是对象")
    if not isinstance(user_down_amount_fen, int) or user_down_amount_fen < 0:
        raise MiCarTrialError(f"userDownAmount 必须是非负整数: {user_down_amount_fen!r}")
    if not isinstance(term_no, int) or term_no <= 0:
        raise MiCarTrialError(f"termNo 必须是正整数: {term_no!r}")
    if not isinstance(vehicle_value_fen, int) or vehicle_value_fen <= 0:
        raise MiCarTrialError(f"vehicleValue 必须是正整数: {vehicle_value_fen!r}")

    schemes = aggregate.get("schemes") or []
    if not isinstance(schemes, list):
        raise MiCarTrialError(f"aggregate.schemes 必须是数组: {schemes!r}")

    available: List[Dict[str, Any]] = []
    down_oor: List[Dict[str, Any]] = []
    term_unsup: List[Dict[str, Any]] = []
    both: List[Dict[str, Any]] = []
    filtered: List[Dict[str, Any]] = []

    for raw in schemes:
        if not isinstance(raw, dict):
            continue
        enriched = _classify(raw, user_down_amount_fen, term_no, vehicle_value_fen)
        has_calc = enriched.get("calculate") is not None
        down_ok = enriched["downPaymentSupported"]
        term_ok = enriched["termSupportedResolved"]

        if term_ok and not has_calc:
            filtered.append(enriched)
            continue
        if down_ok and term_ok:
            available.append(enriched)
        elif not down_ok and term_ok:
            down_oor.append(enriched)
        elif down_ok and not term_ok:
            term_unsup.append(enriched)
        else:
            both.append(enriched)

    def _monthly(s: Dict[str, Any]) -> int:
        c = s.get("calculate") or {}
        mp = c.get("monthlyPayment")
        return mp if isinstance(mp, int) else 10**18

    available.sort(key=_monthly)

    recommended = None
    if available:
        top = available[0]
        calc = top.get("calculate") or {}
        recommended = {
            "productTypeName": top.get("productTypeName"),
            "customerName": top.get("customerName"),
            "monthlyPayment": calc.get("monthlyPayment"),
        }

    return {
        "available": available,
        "downOutOfRange": down_oor,
        "termUnsupported": term_unsup,
        "both": both,
        "filtered": filtered,
        "summary": {
            "availableCount": len(available),
            "downOutOfRangeCount": len(down_oor),
            "termUnsupportedCount": len(term_unsup),
            "bothCount": len(both),
            "filteredCount": len(filtered),
            "recommended": recommended,
        },
    }
