#!/usr/bin/env python3
"""
Earth2037 本地缓存：拉取 userinfo、citys 等数据到本地 JSON，便于映射（主城 tileID、城市名等）。
需 token 认证。执行 2037.py sync 触发同步。
"""

import json
import os
import re
import sys

# 与 2037.py 共用 config
def _load_config():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(base_dir, "config.json")
    api_base = "https://2037cn1.9235.net"
    if os.path.exists(config_path):
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                cfg = json.load(f)
                api_base = cfg.get("apiBase", api_base)
        except (json.JSONDecodeError, IOError):
            pass
    return api_base.rstrip("/")


def _get_token():
    """从环境变量或 config 获取 token"""
    token = os.environ.get("EARTH2037_TOKEN", "").strip()
    if token:
        return token
    base_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(base_dir, "config.json")
    if os.path.exists(config_path):
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                cfg = json.load(f)
                return (cfg.get("token") or cfg.get("apiKey") or "").strip()
        except (json.JSONDecodeError, IOError):
            pass
    return ""


def _auth_401_hint(token):
    t = (token or "").strip()
    if t.upper().startswith("SK-"):
        return "「SK-」开头的是注册/绑定用 key，不能当 Bearer。请执行 2037.py login 用户名 密码，或 curl POST /auth/token，使用返回的 token。"
    return "请检查 EARTH2037_TOKEN：应用 2037.py login 或 POST /auth/token、/auth/apply 返回的长 token（32 位十六进制），不是 SK- key。"


def _post_bootstrap(api_base, token):
    """POST /game/bootstrap，返回合并后的 data 对象"""
    import urllib.request
    import urllib.error
    url = f"{api_base}/game/bootstrap"
    body = json.dumps({}).encode("utf-8")
    req = urllib.request.Request(url, data=body, method="POST")
    req.add_header("Content-Type", "application/json")
    req.add_header("Authorization", f"Bearer {token}")
    req.add_header("Accept", "application/json")
    try:
        resp = urllib.request.urlopen(req, timeout=120)
    except urllib.error.HTTPError as e:
        if e.code == 401:
            raise RuntimeError("HTTP 401 Unauthorized。 " + _auth_401_hint(token)) from e
        raise
    with resp:
        r = json.loads(resp.read().decode("utf-8"))
    if not r.get("ok"):
        raise RuntimeError(r.get("err", "bootstrap failed"))
    return r.get("data")


def _game_command(api_base, token, cmd, args=""):
    """POST /game/command，返回 data 字符串（如 /svr citylist {...}）"""
    import urllib.request
    import urllib.error
    url = f"{api_base}/game/command"
    body = json.dumps({"cmd": cmd, "args": args or ""}).encode("utf-8")
    req = urllib.request.Request(url, data=body, method="POST")
    req.add_header("Content-Type", "application/json")
    req.add_header("Authorization", f"Bearer {token}")
    req.add_header("Accept", "application/json")
    try:
        resp = urllib.request.urlopen(req, timeout=30)
    except urllib.error.HTTPError as e:
        if e.code == 401:
            raise RuntimeError("HTTP 401 Unauthorized。 " + _auth_401_hint(token)) from e
        raise
    with resp:
        r = json.loads(resp.read().decode("utf-8"))
    if not r.get("ok"):
        raise RuntimeError(r.get("err", "unknown error"))
    return r.get("data") or ""


def _parse_svr_json(data, prefix):
    """从 /svr cmd {json} 或 /svr cmd json 提取 JSON 字符串"""
    if not data or not isinstance(data, str):
        return None
    # 格式: /svr citylist [{...}] 或 /svr userinfo {...}
    pat = re.compile(r"^/svr\s+" + re.escape(prefix) + r"\s+(.+)$", re.IGNORECASE)
    m = pat.match(data.strip())
    if not m:
        return None
    raw = m.group(1).strip()
    if not raw:
        return None
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return None


def _cache_dir():
    """缓存文件所在目录（skill 根目录）"""
    return os.path.dirname(os.path.abspath(__file__))


def sync(api_base=None, token=None):
    """
    拉取 CURRENTUSER、USERINFO、CITYLIST，写入 userinfo.json、citys.json。
    返回 (userinfo, citys) 或抛出异常。
    """
    api_base = api_base or _load_config()
    token = token or _get_token()
    if not token:
        raise ValueError("需要 token：设置环境变量 EARTH2037_TOKEN 或在 config.json 中配置 token/apiKey")

    # 1. USERINFO（当前用户详情，含 CapitalID）
    raw_user = _game_command(api_base, token, "USERINFO", "")
    userinfo = _parse_svr_json(raw_user, "userinfo")
    if userinfo is None:
        raise RuntimeError("USERINFO 解析失败: " + (raw_user[:200] if raw_user else "无返回"))

    # 2. CITYLIST（城市列表）
    raw_city = _game_command(api_base, token, "CITYLIST", "")
    citys = _parse_svr_json(raw_city, "citylist")
    if citys is None:
        citys = []  # 可能为空数组
    if not isinstance(citys, list):
        citys = [citys] if citys else []

    # 写入本地
    cache_dir = _cache_dir()
    userinfo_path = os.path.join(cache_dir, "userinfo.json")
    citys_path = os.path.join(cache_dir, "citys.json")

    with open(userinfo_path, "w", encoding="utf-8") as f:
        json.dump(userinfo, f, ensure_ascii=False, indent=2)

    with open(citys_path, "w", encoding="utf-8") as f:
        json.dump(citys, f, ensure_ascii=False, indent=2)

    return userinfo, citys


def bootstrap(api_base=None, token=None):
    """
    登录后一次性拉取多路数据（等价 TCP 连续多条命令），写入 session_cache.json。
    仍会从 data 中提取 userinfo、citylist 写入 userinfo.json、citys.json（若存在）。
    """
    api_base = api_base or _load_config()
    token = token or _get_token()
    if not token:
        raise ValueError("需要 token：设置环境变量 EARTH2037_TOKEN 或在 config.json 中配置 token/apiKey")

    data = _post_bootstrap(api_base, token)
    cache_dir = _cache_dir()
    path = os.path.join(cache_dir, "session_cache.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    ui = None
    cs = None
    if isinstance(data, dict):
        ui_raw = data.get("userinfo")
        if isinstance(ui_raw, dict):
            ui = ui_raw
        elif isinstance(ui_raw, str):
            try:
                ui = json.loads(ui_raw)
            except (json.JSONDecodeError, TypeError):
                pass
        cl_raw = data.get("citylist")
        if isinstance(cl_raw, list):
            cs = cl_raw
        elif isinstance(cl_raw, str):
            try:
                cs = json.loads(cl_raw)
            except (json.JSONDecodeError, TypeError):
                pass
    if ui:
        with open(os.path.join(cache_dir, "userinfo.json"), "w", encoding="utf-8") as f:
            json.dump(ui, f, ensure_ascii=False, indent=2)
    if cs is not None:
        if not isinstance(cs, list):
            cs = [cs] if cs else []
        with open(os.path.join(cache_dir, "citys.json"), "w", encoding="utf-8") as f:
            json.dump(cs, f, ensure_ascii=False, indent=2)

    return data


def load_session_cache():
    """读取 session_cache.json，无则 None"""
    path = os.path.join(_cache_dir(), "session_cache.json")
    if not os.path.exists(path):
        return None
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


# bootstrap 键顺序与 SessionBootstrapService 一致，供 show 打印
_CACHE_SECTIONS = [
    ("userinfo", "【账号】"),
    ("citylist", "【城市】"),
    ("citybuildlist", "【各城建筑】"),
    ("buildlist", "【建筑类型】"),
    ("getbuildcosts2", "【建造消耗】"),
    ("getuserbuildqueue", "【建造队列】"),
    ("getcitytroops", "【城内驻军】"),
    ("gettasklist", "【任务】"),
    ("getconscriptionqueue", "【征兵队列】"),
    ("usertroopssciencequeue", "【兵种科技队列】"),
    ("armies", "【兵种】"),
    ("usercitymilitarysciences", "【城市军事科技】"),
    ("getoutput", "【产出】"),
    ("userheros", "【英雄】"),
    ("goodslist", "【物品目录】"),
    ("usergoodslist", "【背包】"),
    ("combatqueue", "【出征队列】"),
    ("nm", "【nm】"),
    ("airinfo", "【空袭信息】"),
]

# show 子集：python3 cache.py show city | build | troops | task | queue | hero | goods
_CACHE_FOCUS = {
    "city": {"citylist"},
    "cities": {"citylist"},
    "build": {"citybuildlist", "buildlist", "getbuildcosts2", "getuserbuildqueue"},
    "troops": {"armies", "getcitytroops", "usercitymilitarysciences"},
    "military": {"armies", "getcitytroops", "usercitymilitarysciences"},
    "task": {"gettasklist"},
    "queue": {"getuserbuildqueue", "getconscriptionqueue", "combatqueue", "usertroopssciencequeue"},
    "hero": {"userheros"},
    "goods": {"goodslist", "usergoodslist"},
}


def show_cache(focus=None):
    """
    将 session_cache.json 按块打印到 stdout，便于终端阅读。
    focus: None / all / city / build / troops / task / queue / hero / goods
    返回 0 成功，1 无缓存或未知 focus。
    """
    data = load_session_cache()
    if not data:
        print("无 session_cache.json。请先执行: python3 2037.py bootstrap", file=sys.stderr)
        return 1

    fkey = (focus or "all").strip().lower()
    allowed = None
    if fkey not in ("", "all", "a"):
        allowed = _CACHE_FOCUS.get(fkey)
        if allowed is None:
            print(
                "未知分类。可用: all city build troops task queue hero goods",
                file=sys.stderr,
            )
            return 1

    printed = False
    for key, title in _CACHE_SECTIONS:
        if key not in data:
            continue
        if allowed is not None and key not in allowed:
            continue
        printed = True
        print(title)
        print(json.dumps(data[key], ensure_ascii=False, indent=2))
        print()

    for mk in ("_meta", "_errors"):
        if mk in data and (allowed is None or mk == "_meta"):
            print(f"【{mk}】")
            print(json.dumps(data[mk], ensure_ascii=False, indent=2))
            print()

    if not printed and allowed is not None:
        print("(所选分类在当前缓存中无数据)", file=sys.stderr)
        return 1
    return 0


def load_userinfo():
    """读取本地 userinfo.json"""
    path = os.path.join(_cache_dir(), "userinfo.json")
    if not os.path.exists(path):
        return None
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def load_citys():
    """读取本地 citys.json"""
    path = os.path.join(_cache_dir(), "citys.json")
    if not os.path.exists(path):
        return []
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
        return data if isinstance(data, list) else []


def get_capital_id():
    """主城 tileID，无缓存时返回 None"""
    u = load_userinfo()
    if not u:
        return None
    return u.get("CapitalID") or u.get("capitalID")


def get_tile_by_name(name):
    """按城市名查 tileID，支持「主城」「第一座城」等"""
    citys = load_citys()
    if not citys:
        return get_capital_id() if name in ("主城", "首都", "第一座城") else None
    name = (name or "").strip()
    if name in ("主城", "首都", "第一座城"):
        for c in citys:
            if c.get("IsCapital") or c.get("isCapital"):
                return c.get("TileID") or c.get("tileID")
        return get_capital_id() or (citys[0].get("TileID") if citys else None)
    for c in citys:
        if (c.get("Name") or c.get("name") or "") == name:
            return c.get("TileID") or c.get("tileID")
    return None


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "sync":
        try:
            ui, cs = sync()
            print("✅ 缓存已更新")
            print(f"  userinfo.json: userID={ui.get('UserID')}, CapitalID={ui.get('CapitalID')}")
            print(f"  citys.json: {len(cs)} 座城市")
        except Exception as e:
            print(f"❌ 同步失败: {e}")
            sys.exit(1)
    elif len(sys.argv) > 1 and sys.argv[1] == "bootstrap":
        try:
            data = bootstrap()
            keys = list(data.keys()) if isinstance(data, dict) else []
            print("✅ session_cache.json 已写入（含多路游戏数据）")
            print(f"  键: {', '.join(keys[:12])}{'...' if len(keys) > 12 else ''}")
        except Exception as e:
            print(f"❌ bootstrap 失败: {e}")
            sys.exit(1)
    elif len(sys.argv) > 1 and sys.argv[1] == "show":
        focus = sys.argv[2] if len(sys.argv) > 2 else None
        sys.exit(show_cache(focus))
    else:
        print("用法: python3 cache.py sync | bootstrap | show [分类]")
        print("  sync: 仅 USERINFO + CITYLIST")
        print("  bootstrap: 登录后整包缓存 → session_cache.json（推荐）")
        print("  show: 按块打印 session_cache.json（查城市/建筑/军队等，不连网）")
        print("  show 分类: city | build | troops | task | queue | hero | goods | all")
        print("  需 token: sync/bootstrap；show 只读本地文件")
