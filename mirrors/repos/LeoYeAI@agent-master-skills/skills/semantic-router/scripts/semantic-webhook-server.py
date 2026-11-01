#!/usr/bin/env python3
"""
semantic-webhook-server.py — Webhook 触发语义路由
================================================

轻量 HTTP 服务，接收消息 webhook，执行语义检查并返回路由建议。

**设计原则 (2026-03-01 重设计)：**
- 只做检查和建议，**不做会话重置**（重置会丢失上下文 + 覆盖模型切换）
- 模型切换建议由调用方（主代理）自行决定是否执行
- Branch B = 延续（不动），Branch C = 建议切模型（不重置会话）

启动：
  python3 semantic-webhook-server.py [--port 9811] [--host 127.0.0.1]

Webhook 调用：
  POST http://127.0.0.1:9811/route
  Content-Type: application/json
  {"message": "用户消息", "current_pool": "Highspeed", "session_key": "optional"}

健康检查：
  GET http://127.0.0.1:9811/health

状态查看：
  GET http://127.0.0.1:9811/status

最近日志：
  GET http://127.0.0.1:9811/logs?limit=20
"""

import os
import sys
import json
import signal
import socket
import subprocess
import hashlib
from hashlib import sha256
from collections import deque
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
import socketserver
from pathlib import Path
from urllib.parse import parse_qs, urlparse

# ── Config ──────────────────────────────────────────────
DEFAULT_PORT = 9811
DEFAULT_HOST = "127.0.0.1"
SCRIPT_DIR = Path(__file__).parent
SEMANTIC_CHECK_PATH = SCRIPT_DIR / "semantic_check.py"
LOG_DIR = Path.home() / ".openclaw" / "logs"
LOG_FILE = LOG_DIR / "semantic-webhook.log"
PID_FILE = Path.home() / ".openclaw" / "run" / "semantic-webhook.pid"
OUTBOUND_GUARD_FILE = Path.home() / ".openclaw" / "workspace" / ".lib" / "semantic_outbound_guard_state.json"
MAX_DEDUP_RECORDS = 2000

MAX_HISTORY = 200
request_history = deque(maxlen=MAX_HISTORY)
stats = {
    "started_at": None,
    "total_requests": 0,
    "branch_b_count": 0,
    "branch_c_count": 0,
    "model_switch_suggestions": 0,
    "errors": 0,
}


def log(level: str, msg: str):
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    entry = f"[{ts}] [{level}] {msg}"
    print(entry, flush=True)
    try:
        with open(LOG_FILE, "a") as f:
            f.write(entry + "\n")
    except Exception:
        pass


def _new_trace_id() -> str:
    import uuid
    return f"sw-{uuid.uuid4().hex[:12]}"


def _validate_session_key(session_key: str):
    if session_key is None:
        return False, "session_key_missing"
    if not isinstance(session_key, str):
        return False, "session_key_invalid"
    key = session_key.strip()
    if not key:
        return False, "session_key_missing"
    if len(key) < 8 or len(key) > 128:
        return False, "session_key_invalid"
    if any(ord(ch) < 32 for ch in key):
        return False, "session_key_invalid"
    return True, None


def _strict_reject(handler, status: int, reason: str, trace_id: str):
    handler._send_json(status, {
        "ok": False,
        "error_code": "SESSION_GATE_REJECTED",
        "reason": reason,
        "message": "strict gate rejected",
        "trace_id": trace_id,
        "retryable": False,
    })


def run_semantic_check(message: str, current_pool: str = "Highspeed", session_key: str = None) -> dict:
    """直接调用 semantic_check.py，解析 JSON 输出"""
    try:
        cmd = [sys.executable, str(SEMANTIC_CHECK_PATH), message, current_pool]
        if session_key:
            cmd.extend(["--session-key", session_key])

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=15,
        )
        stdout = result.stdout.strip()
        if not stdout:
            return {"error": "Empty output from semantic_check", "stderr": result.stderr[:300]}

        # 提取 JSON（可能混有 warning 行）
        json_result = extract_json(stdout)
        if json_result is None:
            return {"error": "Failed to parse JSON", "raw": stdout[:500]}
        return json_result

    except subprocess.TimeoutExpired:
        return {"error": "semantic_check timed out (15s)"}
    except Exception as e:
        return {"error": str(e)}


def extract_json(text: str) -> dict | None:
    """从混合输出中提取 JSON 对象"""
    lines = text.split("\n")
    # 方法1: 找 { 开始的块，追踪 brace depth
    json_lines = []
    depth = 0
    collecting = False
    for line in lines:
        stripped = line.strip()
        if not collecting and stripped.startswith("{"):
            collecting = True
            json_lines = []
            depth = 0
        if collecting:
            json_lines.append(line)
            depth += stripped.count("{") - stripped.count("}")
            if depth <= 0:
                try:
                    return json.loads("\n".join(json_lines))
                except json.JSONDecodeError:
                    collecting = False
                    json_lines = []
                    depth = 0

    # 方法2: 整个输出
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return None


def _load_guard_state() -> dict:
    try:
        if OUTBOUND_GUARD_FILE.exists():
            return json.loads(OUTBOUND_GUARD_FILE.read_text(encoding="utf-8"))
    except Exception:
        pass
    return {"declaration_cache": {}, "applied_idempotency": {}}


def _save_guard_state(state: dict):
    try:
        OUTBOUND_GUARD_FILE.parent.mkdir(parents=True, exist_ok=True)
        OUTBOUND_GUARD_FILE.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")
    except Exception as e:
        log("WARN", f"guard state save failed: {e}")


def _ensure_declaration_first_line(reply_text: str, declaration: str) -> str:
    body = (reply_text or "").strip("\n")
    decl = (declaration or "").strip()
    if not decl:
        return body
    if not body:
        return decl
    first_line = body.splitlines()[0].strip()
    if first_line == decl:
        return body
    if first_line.startswith("【语义检查】"):
        rest = "\n".join(body.splitlines()[1:]).lstrip("\n")
        return decl + ("\n" + rest if rest else "")
    return decl + "\n" + body


def _build_idempotency_key(session_key: str, message_id: str, turn_id: str) -> str | None:
    if not (session_key and message_id and turn_id):
        return None
    return sha256(f"{session_key}|{message_id}|{turn_id}".encode("utf-8")).hexdigest()


def cache_declaration(session_key: str, declaration: str):
    if not session_key or not declaration:
        return
    state = _load_guard_state()
    state.setdefault("declaration_cache", {})[session_key] = declaration
    _save_guard_state(state)


def apply_outbound_guard(payload: dict, *, sender_role: str, session_key: str, message_id: str = None, turn_id: str = None) -> dict:
    """发送前硬门禁：仅 user 回复路径，支持声明缓存兜底与幂等防重。"""
    role = (sender_role or "").strip().lower()
    if role != "user":
        return payload

    reply_text = payload.get("reply_text")
    if reply_text is None:
        return payload

    state = _load_guard_state()
    decl_cache = state.setdefault("declaration_cache", {})
    idem = state.setdefault("applied_idempotency", {})

    declaration = (payload.get("declaration") or "").strip()
    if declaration and session_key:
        decl_cache[session_key] = declaration
    if not declaration and session_key:
        declaration = (decl_cache.get(session_key) or "").strip()
        if declaration:
            payload["declaration"] = declaration

    idem_key = _build_idempotency_key(session_key, (message_id or "").strip(), (turn_id or "").strip())
    if idem_key and idem.get(idem_key):
        payload["outbound_guard"] = {
            "sender_role": role,
            "idempotency_key": idem_key,
            "dedup_skip": True,
            "injected": False,
            "cache_fallback_used": bool(not payload.get("declaration") and declaration),
        }
        return payload

    guarded = _ensure_declaration_first_line(reply_text, declaration)
    injected = guarded != reply_text
    payload["reply_text"] = guarded
    payload["outbound_guard"] = {
        "sender_role": role,
        "idempotency_key": idem_key,
        "dedup_skip": False,
        "injected": injected,
        "cache_fallback_used": bool(not payload.get("declaration") and declaration),
    }

    if idem_key:
        idem[idem_key] = {
            "session_key": session_key,
            "message_id": message_id,
            "turn_id": turn_id,
            "at": datetime.now().isoformat(),
            "injected": injected,
        }
        if len(idem) > MAX_DEDUP_RECORDS:
            for k in sorted(idem.keys())[: len(idem) - MAX_DEDUP_RECORDS]:
                idem.pop(k, None)

    _save_guard_state(state)
    return payload


def build_response(check_result: dict, current_pool: str) -> dict:
    """基于 semantic_check 原子语义返回响应（Phase 2: execute 对齐）。"""
    if "error" in check_result:
        return {
            "route": "error",
            "error": check_result["error"],
            "action": "none",
            "action_command": "continue",
            "declaration": None,
        }

    branch = check_result.get("branch", "B")
    action_command = check_result.get("action_command")
    declaration = check_result.get("declaration", "")
    primary_model = check_result.get("primary_model")
    pool_name = check_result.get("pool_name")
    ctx_score = check_result.get("context_score")

    effective_pool = check_result.get("pool") or pool_name or current_pool

    if not action_command:
        # legacy fallback，避免旧版本 semantic_check 破坏执行一致性
        if branch == "B":
            action_command = "continue"
        elif branch == "B+":
            action_command = "continue_warn"
        elif branch == "C-auto":
            action_command = "new_and_switch"
        else:
            action_command = "switch"

    model_switch = None
    if primary_model:
        model_switch = {
            "recommended_model": primary_model,
            "target_pool": pool_name or check_result.get("pool"),
            "fallback_chain": check_result.get("fallback_chain", []),
        }

    route = {
        "continue": "continue",
        "continue_warn": "continue",
        "switch": "switch",
        "new_and_switch": "new_session",
    }.get(action_command, "switch")

    session_action = {
        "continue": "none",
        "continue_warn": "warn",
        "switch": "suggest_switch",
        "new_and_switch": "suggest_new",
    }.get(action_command, "suggest_switch")

    # 提取 prependContext 和 routing_tag（如果 semantic_check 提供了）
    prepend_context = check_result.get("prependContext")
    routing_tag = check_result.get("routing_tag")

    return {
        "route": route,
        "branch": branch,
        "action": "suggest_model_switch" if action_command in ("switch", "new_and_switch") else "none",
        "action_command": action_command,
        "session_action": session_action,
        "declaration": declaration,
        "prependContext": prepend_context,
        "routing_tag": routing_tag,
        "pool": effective_pool,
        "current_pool": current_pool,
        "context_score": ctx_score,
        "model_switch": model_switch,
        "session_reset": action_command == "new_and_switch",
        "note": "advisory only; caller executes action_command",
    }


class WebhookHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        pass  # 静默默认日志

    def _send_json(self, status: int, data: dict):
        body = json.dumps(data, ensure_ascii=False, indent=2).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(body)

    def do_OPTIONS(self):
        """CORS preflight"""
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path.rstrip("/")

        if path == "/health":
            self._send_json(200, {"status": "ok", "pid": os.getpid(), "version": "2.0"})

        elif path == "/status":
            uptime = None
            if stats["started_at"]:
                delta = datetime.now() - datetime.fromisoformat(stats["started_at"])
                uptime = str(delta).split(".")[0]
            self._send_json(200, {
                **stats,
                "uptime": uptime,
                "history_size": len(request_history),
                "design": "advisory-only (no session reset, no auto model switch)",
            })

        elif path == "/logs":
            qs = parse_qs(parsed.query)
            limit = int(qs.get("limit", ["20"])[0])
            recent = list(request_history)[-limit:]
            self._send_json(200, {"logs": recent, "count": len(recent)})

        elif path == "" or path == "/":
            self._send_json(200, {
                "service": "Semantic Router Webhook v2.0",
                "endpoints": {
                    "POST /route": "Route a message (returns advisory, no side effects)",
                    "GET /health": "Health check",
                    "GET /status": "Server statistics",
                    "GET /logs": "Recent request history (?limit=N)",
                },
                "design_principle": "Advisory only. Never resets sessions. Never auto-switches models.",
            })

        else:
            self._send_json(404, {"error": f"Unknown: {path}"})

    def do_POST(self):
        parsed = urlparse(self.path)
        path = parsed.path.rstrip("/")

        if path != "/route":
            self._send_json(404, {"error": f"Use POST /route"})
            return

        content_length = int(self.headers.get("Content-Length", 0))
        if content_length == 0:
            self._send_json(400, {"error": "Empty body"})
            return

        body = self.rfile.read(content_length).decode("utf-8")
        content_type = self.headers.get("Content-Type", "")

        # 解析请求
        message = None
        current_pool = "Highspeed"
        session_key = None
        sender_role = None
        message_id = None
        turn_id = None
        reply_text = None

        if "application/json" in content_type or body.strip().startswith("{"):
            try:
                data = json.loads(body)
                message = data.get("message")
                current_pool = data.get("current_pool", "Highspeed")
                session_key = data.get("session_key")
                sender_role = data.get("sender_role")
                message_id = data.get("message_id")
                turn_id = data.get("turn_id")
                reply_text = data.get("reply_text")
            except json.JSONDecodeError:
                self._send_json(400, {"error": "Invalid JSON"})
                return
        elif "form-urlencoded" in content_type:
            data = parse_qs(body)
            message = data.get("message", [None])[0]
            current_pool = data.get("current_pool", ["Highspeed"])[0]
            session_key = data.get("session_key", [None])[0]
            sender_role = data.get("sender_role", [None])[0]
            message_id = data.get("message_id", [None])[0]
            turn_id = data.get("turn_id", [None])[0]
            reply_text = data.get("reply_text", [None])[0]
        else:
            self._send_json(400, {"error": f"Unsupported Content-Type: {content_type}"})
            return

        trace_id = _new_trace_id()

        # Phase 1 strict gate: 仅 user 消息允许触发 + session_key mandatory
        if sender_role is None:
            _strict_reject(self, 400, "sender_role_missing", trace_id)
            log("WARN", f"reject trace={trace_id} reason=sender_role_missing")
            return
        if sender_role != "user":
            _strict_reject(self, 403, "sender_role_invalid", trace_id)
            log("WARN", f"reject trace={trace_id} reason=sender_role_invalid sender_role={sender_role}")
            return

        ok_key, key_reason = _validate_session_key(session_key)
        if not ok_key:
            _strict_reject(self, 400, key_reason, trace_id)
            log("WARN", f"reject trace={trace_id} reason={key_reason}")
            return

        # 子代理豁免语义路由：只对主代理会话执行 semantic_check
        # 命中 subagent 会话时，直接返回 continue，不注入声明、不建议切模
        if session_key and ":subagent:" in session_key:
            response = {
                "route": "continue",
                "branch": "B",
                "action": "none",
                "action_command": "continue",
                "session_action": "none",
                "declaration": None,
                "pool": current_pool,
                "current_pool": current_pool,
                "context_score": 1.0,
                "model_switch": None,
                "session_reset": False,
                "note": "subagent bypass: semantic routing disabled",
                "trace_id": trace_id,
            }
            if reply_text is not None:
                response["reply_text"] = reply_text
            log("INFO", f"Route bypass(subagent): trace={trace_id} session_key={session_key}")
            self._send_json(200, response)
            return

        if not message:
            self._send_json(400, {"error": "Missing 'message'"})
            return

        # 执行语义检查
        ts = datetime.now().isoformat()
        stats["total_requests"] += 1
        log("INFO", f"Route: '{message[:80]}' pool={current_pool} trace={trace_id}")

        check_result = run_semantic_check(message, current_pool, session_key=session_key)
        response = build_response(check_result, current_pool)

        current_declaration = (response.get("declaration") or "").strip()
        if current_declaration:
            cache_declaration(session_key, current_declaration)

        if reply_text is not None:
            response["reply_text"] = reply_text
        response = apply_outbound_guard(
            response,
            sender_role=sender_role,
            session_key=session_key,
            message_id=str(message_id or ""),
            turn_id=str(turn_id or ""),
        )

        # 统计
        branch = response.get("branch", "?")
        if branch == "B":
            stats["branch_b_count"] += 1
        elif branch == "C":
            stats["branch_c_count"] += 1
        if response.get("route") == "error":
            stats["errors"] += 1

        response["trace_id"] = trace_id

        # 历史记录
        session_key_hash = hashlib.sha256(session_key.encode("utf-8")).hexdigest()[:16] if session_key else None
        record = {
            "timestamp": ts,
            "trace_id": trace_id,
            "message": message[:120],
            "current_pool": current_pool,
            "session_key_hash": session_key_hash,
            "branch": branch,
            "route": response.get("route"),
            "suggested_model": (response.get("model_switch") or {}).get("recommended_model"),
            "declaration": response.get("declaration"),
        }
        request_history.append(record)

        log("INFO", f"→ trace={trace_id} branch={branch} route={response.get('route')}")
        self._send_json(200, response)


def write_pid():
    pid_dir = PID_FILE.parent
    pid_dir.mkdir(parents=True, exist_ok=True)
    PID_FILE.write_text(str(os.getpid()))


def cleanup_pid(*args):
    try:
        PID_FILE.unlink(missing_ok=True)
    except Exception:
        pass
    log("INFO", "Shutting down")
    sys.exit(0)


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Semantic Router Webhook v2.0 (advisory-only)")
    parser.add_argument("--port", type=int, default=DEFAULT_PORT)
    parser.add_argument("--host", default=DEFAULT_HOST)
    parser.add_argument("action", nargs="?", default="start", choices=["start", "stop", "status"])
    args = parser.parse_args()

    if args.action == "stop":
        if PID_FILE.exists():
            pid = int(PID_FILE.read_text().strip())
            try:
                os.kill(pid, signal.SIGTERM)
                print(f"Stopped (PID {pid})")
                PID_FILE.unlink(missing_ok=True)
            except ProcessLookupError:
                print(f"PID {pid} not found, cleaning")
                PID_FILE.unlink(missing_ok=True)
        else:
            print("Not running")
        return

    if args.action == "status":
        if PID_FILE.exists():
            pid = int(PID_FILE.read_text().strip())
            try:
                os.kill(pid, 0)
                print(f"Running (PID {pid})")
            except ProcessLookupError:
                print(f"Stale PID {pid}")
                PID_FILE.unlink(missing_ok=True)
        else:
            print("Not running")
        return

    # Start
    signal.signal(signal.SIGTERM, cleanup_pid)
    signal.signal(signal.SIGINT, cleanup_pid)
    stats["started_at"] = datetime.now().isoformat()
    write_pid()

    # Python 3.13+ HTTPServer may hang on DNS resolution during bind.
    # Use a custom class that forces AF_INET and skips FQDN lookup.
    class FastHTTPServer(HTTPServer):
        address_family = socket.AF_INET
        def server_bind(self):
            # Skip the FQDN lookup that can block for seconds
            socketserver.TCPServer.server_bind(self)
            host, port = self.server_address[:2]
            self.server_name = host
            self.server_port = port

    server = FastHTTPServer((args.host, args.port), WebhookHandler)
    log("INFO", f"🚀 Semantic Webhook v2.0 on {args.host}:{args.port}")
    log("INFO", f"   Design: advisory-only (no session reset, no auto model switch)")
    log("INFO", f"   POST /route  → semantic check + routing suggestion")
    log("INFO", f"   GET  /health → liveness")
    log("INFO", f"   GET  /status → stats")

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
        cleanup_pid()


if __name__ == "__main__":
    main()
