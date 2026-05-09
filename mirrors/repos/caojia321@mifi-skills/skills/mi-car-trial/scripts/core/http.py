"""HTTP + JSON + envelope 校验（无副作用，失败抛异常）。

不做 print / sys.exit；CLI 层自行捕获 MiCarTrialError 转 stderr+exit。
"""

from __future__ import annotations

import json
import urllib.error
import urllib.request
from typing import Any, Dict

BASE_URL = "https://afs.airstarfinance.net/api"
DEFAULT_TIMEOUT = 15  # 秒


class MiCarTrialError(RuntimeError):
    """本 skill 所有可预期错误统一用这个异常。"""


def _check_envelope_success(envelope: Dict[str, Any], where: str) -> None:
    code = envelope.get("code")
    success_values = {"200", 200, 0, "0"}
    if code not in success_values:
        msg = envelope.get("msg", "")
        raise MiCarTrialError(f"Business error from {where}: code={code!r}, msg={msg!r}")


def http_get_json(path: str, timeout: int = DEFAULT_TIMEOUT) -> Dict[str, Any]:
    url = BASE_URL + path
    req = urllib.request.Request(url, method="GET")
    req.add_header("Accept", "application/json")
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            status = resp.status
            raw = resp.read()
    except urllib.error.HTTPError as e:
        body = ""
        try:
            body = e.read().decode("utf-8", errors="replace")
        except Exception:
            pass
        raise MiCarTrialError(f"HTTP {e.code} on GET {url}: {body}") from e
    except urllib.error.URLError as e:
        raise MiCarTrialError(f"URL error on GET {url}: {e.reason}") from e
    except Exception as e:  # noqa: BLE001
        raise MiCarTrialError(f"Unexpected error on GET {url}: {e}") from e

    if status != 200:
        raise MiCarTrialError(f"HTTP {status} on GET {url}")

    try:
        envelope = json.loads(raw.decode("utf-8"))
    except Exception as e:  # noqa: BLE001
        raise MiCarTrialError(f"Invalid JSON from GET {url}: {e}") from e

    _check_envelope_success(envelope, f"GET {url}")
    return envelope


def http_post_json(path: str, body: Dict[str, Any], timeout: int = DEFAULT_TIMEOUT) -> Dict[str, Any]:
    url = BASE_URL + path
    data = json.dumps(body, ensure_ascii=False).encode("utf-8")
    req = urllib.request.Request(url, data=data, method="POST")
    req.add_header("Content-Type", "application/json; charset=utf-8")
    req.add_header("Accept", "application/json")
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            status = resp.status
            raw = resp.read()
    except urllib.error.HTTPError as e:
        body_text = ""
        try:
            body_text = e.read().decode("utf-8", errors="replace")
        except Exception:
            pass
        raise MiCarTrialError(f"HTTP {e.code} on POST {url}: {body_text}") from e
    except urllib.error.URLError as e:
        raise MiCarTrialError(f"URL error on POST {url}: {e.reason}") from e
    except Exception as e:  # noqa: BLE001
        raise MiCarTrialError(f"Unexpected error on POST {url}: {e}") from e

    if status != 200:
        raise MiCarTrialError(f"HTTP {status} on POST {url}")

    try:
        envelope = json.loads(raw.decode("utf-8"))
    except Exception as e:  # noqa: BLE001
        raise MiCarTrialError(f"Invalid JSON from POST {url}: {e}") from e

    _check_envelope_success(envelope, f"POST {url}")
    return envelope
