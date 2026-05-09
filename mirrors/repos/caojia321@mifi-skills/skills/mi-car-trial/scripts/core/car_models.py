"""GET /car-models + 车型名包含匹配。"""

from __future__ import annotations

from typing import Any, Dict, List

from .http import MiCarTrialError, http_get_json


def get_car_models() -> List[Dict[str, Any]]:
    envelope = http_get_json("/free/access/product/trial/aggregate/car-models")
    data = envelope.get("data")
    if not isinstance(data, list):
        raise MiCarTrialError(f"/car-models returned non-list data: {data!r}")
    return data


def _normalize(s: str) -> str:
    return "".join(ch for ch in s if not ch.isspace()).lower()


def match_car_model(name: str) -> Dict[str, Any]:
    """
    包含匹配（忽略空格/大小写）。返回三种 status：

    - {"status":"ok","car":{...}}
    - {"status":"multiple","candidates":[...]}
    - {"status":"none","availableModelNames":[...]}
    """
    user_key = _normalize(name)
    if not user_key:
        raise MiCarTrialError("--name 不能为空")

    cars = get_car_models()
    if not cars:
        raise MiCarTrialError("/car-models returned empty list; 无在售车型")

    matched = [car for car in cars if user_key in _normalize(str(car.get("modelName", "")))]

    if len(matched) == 1:
        return {"status": "ok", "car": matched[0]}
    if len(matched) > 1:
        return {"status": "multiple", "candidates": matched}
    return {"status": "none", "availableModelNames": [str(c.get("modelName", "")) for c in cars]}
