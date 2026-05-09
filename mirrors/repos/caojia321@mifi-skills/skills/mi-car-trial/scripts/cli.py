"""mi-car-trial 统一 CLI 入口。

用法：
    python scripts/cli.py <子命令> [参数...]

子命令：
    terms                    GET /supported-terms          → {"terms":[12,24,36,48,60]}
    car-models               GET /car-models               → {"cars":[...]}
    match --name <车型名>     /car-models + 包含匹配          → {status: ok|multiple|none, ...}
    calc-down ...            金额/比例 → 分                 → {"fen":<int>}
    aggregate ...            POST /aggregate               → ProductTrialAggregateVO.data
    evaluate (stdin=JSON)    aggregate 响应 → 分组排序结果

设计约定：
- 成功：exit 0 + stdout 打印紧凑 UTF-8 JSON
- 失败：exit != 0 + stderr 打印错误；**严禁本地兜底**
- 金额单位统一：分；termNo 为整数
- 主会话只调 CLI，不手算，不直接打接口
"""

from __future__ import annotations

import argparse
import io
import json
import sys
from typing import Any, Dict, List

# 允许以 `python scripts/cli.py` 方式直接运行（脚本目录不在 sys.path 时补上）
import os as _os
_HERE = _os.path.dirname(_os.path.abspath(__file__))
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)

from core.aggregate import post_aggregate
from core.car_models import get_car_models, match_car_model
from core.evaluate import evaluate_schemes
from core.http import MiCarTrialError
from core.money import ratio_to_fen, wan_to_fen, yuan_to_fen
from core.terms import get_supported_terms


# ---------- 通用 IO ----------

def _ensure_utf8_stdio() -> None:
    try:
        sys.stdout.reconfigure(encoding="utf-8")  # type: ignore[attr-defined]
        sys.stderr.reconfigure(encoding="utf-8")  # type: ignore[attr-defined]
    except Exception:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8")


def _print_json(obj: Any) -> None:
    print(json.dumps(obj, ensure_ascii=False, separators=(",", ":")))


def _die(msg: str, code: int = 1) -> None:
    print(msg, file=sys.stderr)
    sys.exit(code)


# ---------- 子命令实现 ----------

def _cmd_terms(_: argparse.Namespace) -> None:
    _print_json({"terms": get_supported_terms()})


def _cmd_car_models(_: argparse.Namespace) -> None:
    _print_json({"cars": get_car_models()})


def _cmd_match(args: argparse.Namespace) -> None:
    _print_json(match_car_model(args.name))


def _cmd_calc_down(args: argparse.Namespace) -> None:
    # 三选一：yuan | wan | (vehicleValue + rate|percent)
    modes: List[str] = [m for m in ("yuan", "wan", "ratio") if _has_mode(args, m)]
    if len(modes) != 1:
        _die(
            "参数错误。用法：\n"
            "  calc-down --yuan <元>\n"
            "  calc-down --wan <万元>\n"
            "  calc-down --vehicleValue <分> (--rate <小数> | --percent <百分数>)"
        )
    mode = modes[0]
    if mode == "yuan":
        _print_json({"fen": yuan_to_fen(args.yuan)})
    elif mode == "wan":
        _print_json({"fen": wan_to_fen(args.wan)})
    else:
        if args.vehicleValue is None:
            _die("--rate / --percent 必须与 --vehicleValue 配合使用")
        _print_json({
            "fen": ratio_to_fen(
                args.vehicleValue,
                rate=args.rate,
                percent=args.percent,
            )
        })


def _has_mode(args: argparse.Namespace, mode: str) -> bool:
    if mode == "yuan":
        return args.yuan is not None
    if mode == "wan":
        return args.wan is not None
    if mode == "ratio":
        return args.rate is not None or args.percent is not None
    return False


def _cmd_aggregate(args: argparse.Namespace) -> None:
    _print_json(
        post_aggregate(
            car_model_id=args.carModelId,
            vehicle_value_fen=args.vehicleValue,
            down_payment_amount_fen=args.downPaymentAmount,
            term_no=args.termNo,
        )
    )


def _cmd_evaluate(_: argparse.Namespace) -> None:
    try:
        raw = sys.stdin.buffer.read()
    except Exception as e:
        _die(f"stdin 读取失败: {e}")
    try:
        payload: Dict[str, Any] = json.loads(raw.decode("utf-8"))
    except Exception as e:
        _die(f"stdin 不是合法 UTF-8 JSON: {e}")

    if not isinstance(payload, dict):
        _die("stdin payload 必须是 JSON 对象")

    result = evaluate_schemes(
        aggregate=payload.get("aggregate"),
        user_down_amount_fen=payload.get("userDownAmount"),
        term_no=payload.get("termNo"),
        vehicle_value_fen=payload.get("vehicleValue"),
    )
    _print_json(result)


# ---------- 参数解析 ----------

def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="mi-car-trial",
        description="小米天星金融汽车贷款试算 CLI（免登录聚合试算）",
    )
    sub = p.add_subparsers(dest="cmd", required=True)

    sub.add_parser("terms", help="GET /supported-terms").set_defaults(func=_cmd_terms)

    sub.add_parser("car-models", help="GET /car-models").set_defaults(func=_cmd_car_models)

    sp_match = sub.add_parser("match", help="按车型名匹配 carModelId")
    sp_match.add_argument("--name", required=True, help="车型名")
    sp_match.set_defaults(func=_cmd_match)

    sp_calc = sub.add_parser("calc-down", help="首付金额换算（→ 分）")
    sp_calc.add_argument("--yuan", help="元 → 分")
    sp_calc.add_argument("--wan", help="万元 → 分")
    sp_calc.add_argument("--vehicleValue", type=int, help="总车价（分），配合 --rate/--percent")
    grp = sp_calc.add_mutually_exclusive_group()
    grp.add_argument("--rate", help="小数比例（0.3=30%）")
    grp.add_argument("--percent", help="百分比（30=30%）")
    sp_calc.set_defaults(func=_cmd_calc_down)

    sp_agg = sub.add_parser("aggregate", help="POST /aggregate 聚合试算")
    sp_agg.add_argument("--carModelId", required=True, type=int)
    sp_agg.add_argument("--vehicleValue", required=True, type=int, help="总车价（分）")
    sp_agg.add_argument("--downPaymentAmount", required=True, type=int, help="首付（分）")
    sp_agg.add_argument("--termNo", required=True, type=int, help="期数（整数）")
    sp_agg.set_defaults(func=_cmd_aggregate)

    sp_eval = sub.add_parser("evaluate", help="对 aggregate 响应做评估（stdin 读 JSON）")
    sp_eval.set_defaults(func=_cmd_evaluate)

    return p


def main() -> None:
    _ensure_utf8_stdio()
    parser = _build_parser()
    args = parser.parse_args()
    try:
        args.func(args)
    except MiCarTrialError as e:
        _die(str(e))


if __name__ == "__main__":
    main()
