"""POST /aggregate 聚合试算。"""

from __future__ import annotations

from typing import Any, Dict

from .http import MiCarTrialError, http_post_json


def post_aggregate(
    car_model_id: int,
    vehicle_value_fen: int,
    down_payment_amount_fen: int,
    term_no: int,
) -> Dict[str, Any]:
    if vehicle_value_fen <= 0:
        raise MiCarTrialError("vehicleValue 必须为正整数（分）")
    if down_payment_amount_fen < 0:
        raise MiCarTrialError("downPaymentAmount 不能为负")
    if down_payment_amount_fen >= vehicle_value_fen:
        raise MiCarTrialError("downPaymentAmount 不得 >= vehicleValue")
    if term_no <= 0:
        raise MiCarTrialError("termNo 必须为正整数")

    body = {
        "carModelId": car_model_id,
        "vehicleValue": vehicle_value_fen,
        "downPaymentAmount": down_payment_amount_fen,
        "termNo": term_no,
    }
    envelope = http_post_json("/free/access/product/trial/aggregate", body)
    data = envelope.get("data")
    if data is None:
        raise MiCarTrialError("POST /aggregate returned null data")
    return data
