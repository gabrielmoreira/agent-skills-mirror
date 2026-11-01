#!/usr/bin/env python3
"""
Semantic Router - 可配置的语义检查与模型路由脚本
支持从配置文件读取模型池和任务类型
支持自动模型切换 (--execute / -e)
"""

import json
import sys
import os
import subprocess
import argparse
from datetime import datetime

try:
    from l0_rule_engine import check_l0_rules, match_index_levels  # 前置规则与L2/L3索引命中
except Exception:
    check_l0_rules = None
    match_index_levels = None

try:
    from skill_trigger_boost import (
        fit_gate,
        generate_boost_declaration,
        plan_skill_dispatch,
    )  # Step 2B: Fit Gate 判定器 + Step 3 自动执行调度计划
except Exception:
    fit_gate = None
    generate_boost_declaration = None
    plan_skill_dispatch = None

# ── Force offline mode for HuggingFace BEFORE any HF imports ──────────────
# The local embedding model is fully cached; no network access needed.
os.environ['HF_HUB_OFFLINE'] = '1'
os.environ['TRANSFORMERS_OFFLINE'] = '1'

# Keep proxy envs by default (avoid side effects on sibling capabilities).
# Explicitly disable with: SEMANTIC_CHECK_DISABLE_PROXY=1
if os.environ.get('SEMANTIC_CHECK_DISABLE_PROXY') == '1':
    for _proxy_key in ('HTTP_PROXY', 'HTTPS_PROXY', 'ALL_PROXY',
                        'http_proxy', 'https_proxy', 'all_proxy'):
        os.environ.pop(_proxy_key, None)

# 获取脚本目录
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# 配置目录：唯一入口 ~/.openclaw/workspace/.lib/pools.json
# 维护时只需修改该文件，skills/semantic-router/config/pools.json 是指向它的 symlink
CONFIG_DIR = os.path.expanduser('~/.openclaw/workspace/.lib')
if not os.path.exists(os.path.join(CONFIG_DIR, 'pools.json')):
    raise RuntimeError(
        "❌ pools.json 未找到！期望位置: ~/.openclaw/workspace/.lib/pools.json\n"
        "这是唯一维护入口，请勿在其他位置单独维护 pools.json 副本。"
    )

def load_json(filename, default=None):
    """加载 JSON 配置文件"""
    path = os.path.join(CONFIG_DIR, filename)
    try:
        if os.path.exists(path):
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
    except Exception as e:
        print(f"Warning: Failed to load {filename}: {e}", file=sys.stderr)
    return default or {}

def _sanitize_context_text(text: str) -> str:
    """清洗上下文文本，降低 envelope/声明噪声。"""
    if not text:
        return ""

    cleaned = unwrap_semantic_router_envelope(text).strip()
    lines = []
    for raw in cleaned.splitlines():
        line = raw.strip()
        if not line:
            continue
        if line.startswith("【语义检查】"):
            continue
        if line.startswith("【Skill Trigger】"):
            continue
        if line.startswith("请优先按该技能流程执行"):
            continue
        if line.startswith("请在你回复的第一行原样输出以下声明"):
            continue
        if line.startswith("Conversation info"):
            continue
        if line.startswith("Replied message"):
            continue
        lines.append(line)

    return "\n".join(lines).strip()


def _select_context_layers(messages: list[str], limit: int) -> list[str]:
    """分层窗口：近窗 + 中窗 + 远窗，缓解"只看最近几条"盲区。"""
    if not messages or limit <= 0:
        return []
    if len(messages) <= limit:
        return messages[:limit]

    near_n = min(4, limit)
    far_n = min(2, max(0, limit - near_n))
    mid_n = max(0, limit - near_n - far_n)

    near = messages[:near_n]
    pool = messages[near_n: max(near_n, len(messages) - far_n)]
    far = messages[-far_n:] if far_n > 0 else []

    mid = []
    if mid_n > 0 and pool:
        step = max(1, len(pool) // mid_n)
        mid = [pool[i] for i in range(0, len(pool), step)][:mid_n]

    layered = near + mid + far

    # 保序去重
    seen = set()
    out = []
    for m in layered:
        key = m.strip()
        if not key or key in seen:
            continue
        seen.add(key)
        out.append(m)
        if len(out) >= limit:
            break

    return out


def get_recent_messages(limit: int = 5, exclude_input: str = None, session_key: str = None) -> list:
    """从会话 jsonl 获取用户上下文（会话隔离 + 分层窗口）。"""
    import glob

    sessions_dir = os.path.expanduser('~/.openclaw/agents/main/sessions')

    target_key = (session_key or '').strip()
    if target_key:
        target_file = os.path.join(sessions_dir, f"{target_key}.jsonl")
        if os.path.exists(target_file):
            jsonl_files = [target_file]
        else:
            # Fallback: session files are often UUID-named, not sessionKey-named.
            # Use freshest active jsonl files as degraded context source.
            jsonl_files = [
                p for p in glob.glob(f"{sessions_dir}/*.jsonl")
                if ".deleted." not in p and ".reset." not in p
            ]
            jsonl_files.sort(key=os.path.getmtime, reverse=True)
            jsonl_files = jsonl_files[:5]
    else:
        jsonl_files = [
            p for p in glob.glob(f"{sessions_dir}/*.jsonl")
            if ".deleted." not in p and ".reset." not in p
        ]
        jsonl_files.sort(key=os.path.getmtime, reverse=True)
        jsonl_files = jsonl_files[:1]

    raw_user_messages = []
    skipped_self = False

    for jsonl_file in jsonl_files:
        if not os.path.exists(jsonl_file):
            continue
        try:
            with open(jsonl_file, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()

            for line in reversed(lines[-400:]):
                try:
                    data = json.loads(line)
                    msg = data.get('message', {})
                    role = msg.get('role', '')
                    content_list = msg.get('content', [])

                    if role != 'user' or not content_list:
                        continue

                    content = content_list[0].get('text', '')
                    if not content:
                        continue

                    if exclude_input and not skipped_self:
                        content_s = content.strip()
                        ex_raw = exclude_input.strip()
                        ex_unwrapped = unwrap_semantic_router_envelope(exclude_input).strip() if exclude_input else ""
                        ex_sanitized = _sanitize_context_text(exclude_input).strip() if exclude_input else ""
                        if content_s in {ex_raw, ex_unwrapped, ex_sanitized}:
                            skipped_self = True
                            continue

                    cleaned = _sanitize_context_text(content)
                    if cleaned:
                        raw_user_messages.append(cleaned)

                    if len(raw_user_messages) >= max(limit * 4, 24):
                        break
                except Exception:
                    continue
            if len(raw_user_messages) >= max(limit * 4, 24):
                break
            # otherwise continue to next candidate file (fallback mode)
            continue
        except Exception:
            continue

    return _select_context_layers(raw_user_messages, limit)

# 加载配置 - 只从 pools.json 读取，不使用硬编码 fallback
# 维护入口: 只需修改 ~/.openclaw/workspace/.lib/pools.json
MODEL_POOLS = load_json('pools.json', {})
TASK_PATTERNS = load_json('tasks.json', {})

# 如果 pools.json 加载失败，抛出错误而不是使用默认值
if not MODEL_POOLS:
    raise RuntimeError("❌ pools.json 加载失败！请检查配置文件是否存在且格式正确。\n"
                      "配置文件位置: ~/.openclaw/workspace/.lib/pools.json")

if not TASK_PATTERNS:
    TASK_PATTERNS = {
        "continue": {"keywords": ["继续", "接着"], "pool": None, "action": "延续"},
        "development": {"keywords": ["开发", "写代码"], "pool": "Intelligence", "action": "执行开发任务"},
    }

# 指示词配置
CONTINUATION_INDICATORS = {
    # 仅保留高置信"承接语"，移除低信息量代词/连接词，降低误 continue
    "pronouns": ["这个问题", "那个问题", "这件事", "那件事"],
    "possessives": ["你说的", "你提的", "你建议的", "刚说的", "上面说的"],
    "supplements": ["再补充", "继续补充", "补充一点", "在此基础上"],
    "confirmations": ["对的", "是的", "同意", "就这样"],
    "references": ["按照", "根据", "按你", "用你", "基于刚才"]
}

# Fork recovery signals：用户从子任务返回主线任务的明确信号
_FORK_RECOVERY_SIGNALS = [
    "之前在做", "原来在做", "本来在做",
    "回到主线", "回到原来", "回到之前",
    "主线任务", "原始任务", "最开始",
    "一开始我们", "最初的任务", "初始目标",
    "解决了卡点", "分叉任务", "插队任务",
]

import re as _re

# ── System Message Filter (v7.4) ──────────────────────────────────────────
# System-level messages (heartbeat polls, cron events, slash commands,
# "continue where you left off", etc.) should NOT be treated as user topic
# input for context relevance scoring.  They are either:
#   - Transparent signals → force "continue" (no model switch, no /new)
#   - Internal machinery → skip semantic scoring entirely
#
# This filter runs BEFORE keyword/indicator/embedding checks.

# Regex patterns that identify system / internal messages
# Source: OpenClaw core (pi-embedded.js) generates these formats:
#   - System event:    "System: [timestamp] ..." (exec/model/cron results)
#   - Cron announce:   "[cron:<jobId> <name>] ..."
#   - Completion:      "[<weekday> <date> GMT+N] [System Message] ..."
#   - Model switch:    "Model switched to ..."
#   - Session reset:   "A new session was started via /new ..."
#   - Continue:        "Continue where you left off ..."
#   - Heartbeat:       "Read HEARTBEAT.md ..."
#   - Subagent:        "✅ Subagent <name> completed/finished ..."
#   - Delivery:        "A completed <type> is ready for user delivery ..."
_SYSTEM_MESSAGE_PATTERNS: list[_re.Pattern] = [
    # Heartbeat poll prompt
    _re.compile(r'^Read HEARTBEAT\.md', _re.IGNORECASE),
    _re.compile(r'^Heartbeat\b', _re.IGNORECASE),
    # OpenClaw system event injection: "System: [timestamp] ..."
    _re.compile(r'^System:\s', _re.IGNORECASE),
    # OpenClaw timestamped system messages: "[Mon 2026-03-02 23:45 GMT+8] [System Message] ..."
    _re.compile(r'^\[\w{3}\s+20\d{2}-\d{2}-\d{2}'),
    # OpenClaw internal: "continue where you left off" variants
    _re.compile(r'^continue\s+where\s+you\s+left', _re.IGNORECASE),
    _re.compile(r'^pick\s+up\s+where', _re.IGNORECASE),
    _re.compile(r'^resume\s+(the\s+)?(previous|last|prior)', _re.IGNORECASE),
    # Session reset prompt
    _re.compile(r'^A new session was started', _re.IGNORECASE),
    # Model switch event
    _re.compile(r'^Model switched to\b', _re.IGNORECASE),
    # Slash commands (e.g. /new, /model, /status, /help, /reasoning, etc.)
    _re.compile(r'^/[a-zA-Z]'),
    # Cron event system messages
    _re.compile(r'^\[cron:', _re.IGNORECASE),
    _re.compile(r'^\[System\s+Message\]', _re.IGNORECASE),
    # Subagent completion notifications
    _re.compile(r'^\[Subagent\b', _re.IGNORECASE),
    _re.compile(r'^✅\s*Subagent\b', _re.IGNORECASE),
    # Completed task delivery prompt
    _re.compile(r'^A completed\s+\w+', _re.IGNORECASE),
    # Declaration injection (output leaking back into input)
    _re.compile(r'^【语义检查】'),
]


def is_system_message(text: str) -> bool:
    """
    Return True if the message is a system/internal signal that should
    bypass semantic topic detection and be treated as a continuation.
    """
    stripped = text.strip()
    if not stripped:
        return False
    for pattern in _SYSTEM_MESSAGE_PATTERNS:
        if pattern.search(stripped):
            return True
    return False


def extract_session_key_from_input(text: str) -> str:
    """从 envelope/system message 中提取 sessionId/sessionKey。"""
    if not text:
        return None

    m = _re.search(r'\[sessionId:\s*([0-9a-fA-F\-]{8,})\]', text)
    if m:
        return m.group(1)

    m = _re.search(r'"session(?:Id|Key)"\s*:\s*"([0-9a-fA-F\-]{8,})"', text)
    if m:
        return m.group(1)

    return None


def validate_session_key(session_key: str) -> tuple[bool, str | None]:
    """Phase 1 strict gate: session_key 必填且格式合法。"""
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


def _extract_json_block_after_label(text: str, label_prefix: str):
    lines = text.splitlines()
    capture = False
    in_fence = False
    buf = []

    for raw in lines:
        line = raw.strip()

        if not capture and line.startswith(label_prefix):
            capture = True
            continue

        if capture and line.startswith("```"):
            in_fence = not in_fence
            continue

        if capture and in_fence:
            buf.append(raw)
            continue

        if capture and not in_fence and line:
            break

    if not buf:
        return None

    payload = "\n".join(buf).strip()
    try:
        return json.loads(payload)
    except Exception:
        return None


def strip_declaration_injection(text: str) -> str:
    """移除用户输入中的伪声明/元数据噪声（输出层内容不得回流输入层）。

    Phase 2 要求：声明文本不得参与路由判定。
    """
    if not text:
        return ""

    out = []
    in_fence = False
    skip_meta_block = False

    for raw in str(text).splitlines():
        line = raw.strip()

        # markdown code-fence handling
        if line.startswith("```"):
            in_fence = not in_fence
            if skip_meta_block:
                # consume the whole fenced metadata block
                continue
            # keep normal fence-less behavior (do not emit fence)
            continue

        # metadata section labels from relay envelope
        if line.startswith("Conversation info") or line.startswith("Replied message"):
            skip_meta_block = True
            continue

        # end meta-block at blank line when not inside fence
        if skip_meta_block and not in_fence:
            if not line:
                skip_meta_block = False
            continue

        if skip_meta_block:
            continue

        if not line:
            out.append(raw)
            continue

        # strip declaration injection lines (including quoted JSON/body forms)
        if "【语义检查】" in line:
            continue
        # Skill Trigger declarations are routing pipeline outputs — strip them
        # so they don't re-enter fit_gate or embedding scoring next turn.
        # Note: we only strip the *text*, NOT mark the whole message as system
        # (is_system_message stays untouched; skill trigger capability is preserved).
        if "【Skill Trigger】" in line:
            continue
        if "请优先按该技能流程执行" in line:
            continue
        if "若技能不可用，必须明确说明原因" in line:
            continue
        if "请在你回复的第一行原样输出以下声明" in line:
            continue
        if "语义检查" in line and ("第一行" in line or "declaration" in line.lower()):
            continue

        out.append(raw)

    return "\n".join(out).strip()


def unwrap_semantic_router_envelope(text: str) -> str:
    """结构化提取 envelope 里的真实当前用户消息。

    关键规则：
      - 只信任"当前消息正文"
      - 不把 Replied message.body 当作本轮输入（避免输出回流输入）
    """
    stripped = (text or "").strip()
    if not stripped.startswith("[语义路由]"):
        return strip_declaration_injection(text)

    lines = text.splitlines()
    in_code_fence = False
    body_lines = []

    for raw in lines:
        line = raw.strip()

        if line.startswith("```"):
            in_code_fence = not in_code_fence
            continue
        if in_code_fence:
            continue
        if not line:
            continue

        # envelope/meta labels
        if line.startswith("[语义路由]"):
            continue
        if line.startswith("Conversation info"):
            continue
        if line.startswith("Replied message"):
            continue
        if "请在你回复的第一行原样输出以下声明" in line:
            continue
        if line.startswith("【语义检查】"):
            continue

        # obvious metadata/json remnants
        if line in {"{", "}", "[", "]"}:
            continue
        if line.startswith('"') and (":" in line or line.endswith('",') or line.endswith('"')):
            continue

        body_lines.append(line)

    if body_lines:
        return strip_declaration_injection("\n".join(body_lines).strip())

    # 若 envelope 无正文，返回空字符串而非 replied body，避免伪上下文污染
    return ""


# Keywords requiring strict boundary matching (short/ambiguous)
_WORD_BOUNDARY_KEYWORDS = {"code", "coding"}


def _is_ascii_word(s: str) -> bool:
    return bool(_re.fullmatch(r'[a-zA-Z0-9_\-]+', s or ""))


def _contains_term_with_boundary(text: str, term: str, strict_short_cjk: bool = False) -> bool:
    """边界匹配：ASCII 用词边界；CJK 用"非字母数字中文"边界，降低子串误击。"""
    if not term:
        return False

    t = term.lower().strip()
    if not t:
        return False

    # 单字中文指示词噪声极高（这/那），默认忽略
    if strict_short_cjk and len(t) == 1 and _re.match(r'[\u4e00-\u9fff]', t):
        return False

    if _is_ascii_word(t):
        return bool(_re.search(r'(?<![a-zA-Z0-9_])' + _re.escape(t) + r'(?![a-zA-Z0-9_])', text))

    # Pure CJK terms (len>=2): allow substring match (Chinese has no whitespace boundary)
    if _re.fullmatch(r'[\u4e00-\u9fff]+', t):
        return t in text

    # Mixed token boundary
    return bool(_re.search(r'(?<![\u4e00-\u9fffA-Za-z0-9_])' + _re.escape(t) + r'(?![\u4e00-\u9fffA-Za-z0-9_])', text))


def parse_target_pool_from_input(user_input: str) -> str:
    """从用户的模型切换指令中解析目标池名称。"""
    text = user_input.lower()
    if any(k in text for k in ["智能", "intelligence", "智能池"]):
        return "Intelligence"
    if any(k in text for k in ["人文", "humanities", "人文池"]):
        return "Humanities"
    if any(k in text for k in ["代理", "agentic", "代理池"]):
        return "Agentic"
    if any(k in text for k in ["高速", "highspeed", "高速池", "快"]):
        return "Highspeed"
    # 兜底：用户说"更好的模型"/"更强的模型"→ Intelligence
    if any(k in text for k in ["更好", "更强", "好点", "强点"]):
        return "Intelligence"
    return "Intelligence"  # 默认切智能池


def layer2_match(user_input: str, include_continue: bool = True, include_non_continue: bool = True):
    """层2：多词非连续命中（trigger_groups_all）→ 决定目标模型池。

    优先级高于层1（keywords）。只要层2命中，层1不再运行。
    返回: (task_type, action, pool, is_continue_task) 或 (None, None, None, False)
    """
    text = user_input.lower().strip()

    for task_type, config in TASK_PATTERNS.items():
        is_continue_task = task_type == "continue"
        if is_continue_task and not include_continue:
            continue
        if (not is_continue_task) and not include_non_continue:
            continue

        for word_group_pair in config.get("trigger_groups_all", []):
            if not word_group_pair or not isinstance(word_group_pair, list):
                continue
            all_groups_hit = True
            for group in word_group_pair:
                if not isinstance(group, list) or not group:
                    continue
                if not any(_contains_term_with_boundary(text, tok.lower().strip()) for tok in group if tok):
                    all_groups_hit = False
                    break
            if all_groups_hit and len(word_group_pair) >= 2:
                return task_type, config.get("action"), config.get("pool"), is_continue_task

    return None, None, None, False


def layer1_match(user_input: str, include_continue: bool = True, include_non_continue: bool = True):
    """层1：单词关键词命中（keywords / soft_keywords）→ 仅在层2无命中时调用。

    soft_keywords 语义：泛用词（如"安排"），命中后标记 is_soft=True，
    调用方将其降级为 B+ 延续，不执行 C 分支强切换。
    返回: (task_type, action, pool, is_continue_task, is_soft)
    """
    text = user_input.lower().strip()

    # ── 强关键词（keywords）────────────────────────────────────────────────
    for task_type, config in TASK_PATTERNS.items():
        is_continue_task = task_type == "continue"
        if is_continue_task and not include_continue:
            continue
        if (not is_continue_task) and not include_non_continue:
            continue

        is_standalone = config.get("standalone", False)
        for kw in config.get("keywords", []):
            kw_norm = (kw or "").lower().strip()
            if not kw_norm:
                continue
            if is_standalone:
                if text == kw_norm or text.startswith(kw_norm + " ") or text.startswith(kw_norm + "?"):
                    return task_type, config.get("action"), config.get("pool"), is_continue_task, False
                continue
            if _contains_term_with_boundary(text, kw_norm):
                return task_type, config.get("action"), config.get("pool"), is_continue_task, False

    # ── 软关键词（soft_keywords，降权）────────────────────────────────────
    for task_type, config in TASK_PATTERNS.items():
        is_continue_task = task_type == "continue"
        if is_continue_task and not include_continue:
            continue
        if (not is_continue_task) and not include_non_continue:
            continue
        for kw in config.get("soft_keywords", []):
            kw_norm = (kw or "").lower().strip()
            if not kw_norm:
                continue
            if _contains_term_with_boundary(text, kw_norm):
                return task_type, config.get("action"), config.get("pool"), is_continue_task, True

    return None, None, None, False, False


def keyword_match(user_input: str, include_continue: bool = True, include_non_continue: bool = True):
    """兼容入口：层2优先，层2无命中再走层1。返回5元组 (task_type, action, pool, is_continue, is_soft)。"""
    l2 = layer2_match(user_input, include_continue, include_non_continue)
    if l2[0] is not None:
        return l2[0], l2[1], l2[2], l2[3], False  # 层2命中，is_soft=False
    return layer1_match(user_input, include_continue, include_non_continue)


def indicator_match(user_input: str) -> bool:
    """指示词检测（v7.5：边界匹配 + 忽略单字中文噪声）。"""
    text = user_input.lower().strip()
    for indicators in CONTINUATION_INDICATORS.values():
        for indicator in indicators:
            if _contains_term_with_boundary(text, indicator, strict_short_cjk=True):
                return True
    return False


def _short_message_anomaly_patch(user_input: str, ctx_score: float, ctx_grade: str) -> tuple:
    """
    短消息异常检测补丁（B策略 v1）
    
    问题场景：极短追问 ("干的怎么样了？"、"快点"、"?") embedding score 无法准确判断
    解决方案：
      1. 消息长度 < 15 字符 + score 在 0.30~0.50 漂移区间 → 保守延续（无法置信）
      2. 消息只有标点/数字/超短 + score < 0.50 → 强制标记为低可信
    
    ⚠️ 仅应用于 user_input（用户消息），不应用于 agent 输出
    
    Returns:
        (is_anomaly: bool, suggested_grade: str, reason: str)
    """
    stripped = user_input.strip()
    msg_len = len(stripped)
    
    # 极短消息判定
    is_extreme_short = msg_len < 8  # "怎么样？"=4字，"?"=1字
    is_very_short = msg_len < 15     # "干的怎么样了？"=7字
    
    # 标点/数字只有消息
    is_punctuation_only = all(c in "？?。！!，,…~；;：:''""【】() 、" for c in stripped)
    is_number_only = all(c in "0123456789 .,％%￥$" for c in stripped)
    
    # 触发条件：极短 + 中等score漂移
    if (is_extreme_short or is_punctuation_only or is_number_only) and 0.25 < ctx_score < 0.50:
        return True, "warn", f"极短/无意义({msg_len}字,score={ctx_score:.2f})"
    
    if is_very_short and ctx_score < 0.50 and not ("继续" in stripped or "接着" in stripped):
        return True, "warn", f"超短消息{msg_len}字,无法置信"
    
    return False, ctx_grade, ""


# ── Local Embedding Model (sentence-transformers, zero API cost) ──────────

_LOCAL_MODEL_PATH = os.path.expanduser(
    '~/.cache/huggingface/hub/models--BAAI--bge-base-zh-v1.5/'
    'snapshots/f03589ceff5aac7111bd60cfc7d497ca17ecac65'
)

_st_model = None  # lazy singleton

# ── Ollama BGE-M3 embedding (P1b: 1024-dim, multilingual) ────────────────────
_OLLAMA_EMBED_URL   = "http://localhost:11434/api/embeddings"
_OLLAMA_EMBED_MODEL = "bge-m3"
_ollama_embed_available: bool | None = None   # None = not yet probed

def _check_ollama_embed() -> bool:
    """Probe Ollama BGE-M3 availability (lazy, cached). Returns True if usable."""
    global _ollama_embed_available
    if _ollama_embed_available is not None:
        return _ollama_embed_available
    try:
        import urllib.request as _ur, json as _j
        payload = _j.dumps({"model": _OLLAMA_EMBED_MODEL, "prompt": "test"}).encode()
        req = _ur.Request(_OLLAMA_EMBED_URL, data=payload,
                          headers={"Content-Type": "application/json"}, method="POST")
        with _ur.urlopen(req, timeout=1) as r:  # fail-fast: 1s; if cold → local model
            resp = _j.load(r)
        emb = resp.get("embedding", [])
        _ollama_embed_available = len(emb) > 100
    except Exception:
        _ollama_embed_available = False
    return _ollama_embed_available


def _get_local_model():
    """Lazy-load local sentence-transformers model (bge-base-zh-v1.5, 768-dim)."""
    global _st_model
    if _st_model is not None:
        return _st_model

    # Force offline mode - never hit network
    os.environ['HF_HUB_OFFLINE'] = '1'
    os.environ['TRANSFORMERS_OFFLINE'] = '1'

    try:
        import warnings
        warnings.filterwarnings('ignore')
        from sentence_transformers import SentenceTransformer
        _st_model = SentenceTransformer(_LOCAL_MODEL_PATH, local_files_only=True)
        return _st_model
    except Exception as e:
        print(f"Warning: Local embedding model load failed: {e}", file=sys.stderr)
        return None


# ── Ollama qwen3-embedding (P1: 4096-dim, 中文优化, 2026-03-13) ──────────────
_OLLAMA_EMBED_MODEL_QWEN = "qwen3-embedding:8b"
_ollama_qwen_available: bool | None = None

def _check_ollama_qwen() -> bool:
    """Probe Ollama qwen3-embedding availability (lazy, cached)."""
    global _ollama_qwen_available
    if _ollama_qwen_available is not None:
        return _ollama_qwen_available
    try:
        import urllib.request as _ur, json as _j
        payload = _j.dumps({"model": _OLLAMA_EMBED_MODEL_QWEN, "prompt": "test"}).encode()
        req = _ur.Request(_OLLAMA_EMBED_URL, data=payload,
                          headers={"Content-Type": "application/json"}, method="POST")
        with _ur.urlopen(req, timeout=2) as r:
            resp = _j.load(r)
        emb = resp.get("embedding", [])
        _ollama_qwen_available = len(emb) > 1000  # qwen3-embedding is 4096-dim
    except Exception:
        _ollama_qwen_available = False
    return _ollama_qwen_available


def get_embedding_client():
    """获取 embedding 客户端 - 优先 qwen3-embedding，备用 bge-base-zh-v1.5
    # 2026-03-13 更新: 基于真实历史路由测试，qwen3-embedding 准确率 34% > bge-base-zh 26%
    """
    # P1: Ollama qwen3-embedding (4096-dim, 中文优化) — 最高优先级
    if _check_ollama_qwen():
        return None, "qwen3-embedding"

    # 本地 HuggingFace bge-base-zh-v1.5 (768-dim, 中文专项)
    model = _get_local_model()
    if model is not None:
        return model, "local"

    # 备用: Ollama BGE-M3 (1024-dim, 多语言)
    if _check_ollama_embed():
        return None, "bge-m3-ollama"

    print("Warning: No embedding backend available, falling back to Jaccard", file=sys.stderr)
    return None, "fallback"


def embed_text(text: str, client=None, provider: str = "local") -> list:
    """
    获取文本的向量表示。
    Priority: Ollama BGE-M3 (1024-dim) > local bge-base-zh-v1.5 (768-dim) > OpenAI.
    Returns: list of floats or None on failure.
    """
    if not text or not text.strip():
        return None

    if client is None:
        client, provider = get_embedding_client()

    try:
        if provider == "qwen3-embedding":
            # P1: Ollama qwen3-embedding via HTTP (4096-dim, 中文优化, 2026-03-13)
            import urllib.request as _ur, json as _j
            payload = _j.dumps({"model": _OLLAMA_EMBED_MODEL_QWEN, "prompt": text.strip()}).encode()
            req = _ur.Request(_OLLAMA_EMBED_URL, data=payload,
                              headers={"Content-Type": "application/json"}, method="POST")
            try:
                with _ur.urlopen(req, timeout=3) as r:
                    resp = _j.load(r)
                emb = resp.get("embedding", [])
                if emb:
                    return emb
            except Exception:
                pass
            # Fallback: use local model
            local_model = _get_local_model()
            if local_model is not None:
                return local_model.encode(text.strip()).tolist()
            return None
        elif provider == "bge-m3-ollama":
            # P1b: Ollama BGE-M3 via HTTP (1024-dim, multilingual, fully local)
            # 2s timeout per call: if Ollama is overloaded, gracefully fall back to local model
            import urllib.request as _ur, json as _j
            payload = _j.dumps({"model": _OLLAMA_EMBED_MODEL, "prompt": text.strip()}).encode()
            req = _ur.Request(_OLLAMA_EMBED_URL, data=payload,
                              headers={"Content-Type": "application/json"}, method="POST")
            try:
                with _ur.urlopen(req, timeout=2) as r:
                    resp = _j.load(r)
                emb = resp.get("embedding", [])
                if emb:
                    return emb
            except Exception:
                pass
            # Graceful fallback: Ollama slow/down → use local HuggingFace
            local_model = _get_local_model()
            if local_model is not None:
                return local_model.encode(text.strip()).tolist()
            return None
        elif provider == "local":
            # sentence-transformers model - returns numpy array
            vec = client.encode(text.strip())
            return vec.tolist()
        elif provider == "openai":
            response = client.embeddings.create(
                input=text.strip(),
                model="text-embedding-3-small"
            )
            return response.data[0].embedding
    except Exception as e:
        print(f"Warning: Embedding failed ({provider}): {e}", file=sys.stderr)
        return None

    return None


def cosine_similarity(vec1: list, vec2: list) -> float:
    """计算两个向量的余弦相似度"""
    if not vec1 or not vec2:
        return 0.0

    try:
        import numpy as np
        v1 = np.array(vec1)
        v2 = np.array(vec2)
        denom = np.linalg.norm(v1) * np.linalg.norm(v2)
        if denom == 0:
            return 0.0
        return float(np.dot(v1, v2) / denom)
    except ImportError:
        import math
        dot_product = sum(a * b for a, b in zip(vec1, vec2))
        norm1 = math.sqrt(sum(a * a for a in vec1))
        norm2 = math.sqrt(sum(b * b for b in vec2))
        if norm1 == 0 or norm2 == 0:
            return 0.0
        return dot_product / (norm1 * norm2)

def jaccard_similarity(text1: str, text2: str) -> float:
    """Jaccard 相似度 (legacy fallback, used when embedding unavailable)"""
    tokens1 = set(_re.findall(r'[\u4e00-\u9fff]+|[a-zA-Z]+', text1.lower()))
    tokens2 = set(_re.findall(r'[\u4e00-\u9fff]+|[a-zA-Z]+', text2.lower()))
    if not tokens1 or not tokens2:
        return 0.0
    intersection = len(tokens1 & tokens2)
    union = len(tokens1 | tokens2)
    return intersection / union if union > 0 else 0.0


# ── Fix-A: Suggested pool via pool-description cosine similarity ────────────
# Cache pool description embeddings (computed once per process lifetime).
_pool_desc_embeddings: dict = {}

def _compute_suggested_pool(user_input: str) -> str:
    """
    Fix-A: 计算 user_input 与各 pool description 的余弦相似度，返回最佳匹配 pool 名。
    结果用于 B/B+ 分支的 suggested_pool 字段（Fix-A 强制重评估）。
    Fix-B: 同逻辑也用于 C-auto 初始池分配推断。
    相似度全部 < 0.15 时回退到 Highspeed（默认低复杂度会话）。
    """
    global _pool_desc_embeddings
    try:
        client, provider = get_embedding_client()
        if not client and provider not in ("bge-m3-ollama", "local"):
            return "Highspeed"

        user_emb = embed_text(user_input, client, provider)
        if not user_emb:
            return "Highspeed"

        best_pool = "Highspeed"
        best_score = -1.0
        POOL_SIMILARITY_FALLBACK = 0.10  # 低于此值时回退 Humanities（从 0.15 降低）

        for pool_key, pool_info in MODEL_POOLS.items():
            if not isinstance(pool_info, dict):
                continue  # skip non-dict entries (e.g. "version" key)
            desc = pool_info.get("description", "")
            if not desc:
                continue
            # Lazy-compute and cache pool description embeddings
            if pool_key not in _pool_desc_embeddings:
                desc_emb = embed_text(desc, client, provider)
                if desc_emb:
                    _pool_desc_embeddings[pool_key] = desc_emb
            desc_emb = _pool_desc_embeddings.get(pool_key)
            if not desc_emb:
                continue
            score = cosine_similarity(user_emb, desc_emb)
            if score > best_score:
                best_score = score
                best_pool = pool_key

        # Only override default if similarity is meaningful
        if best_score < POOL_SIMILARITY_FALLBACK:
            return "Highspeed"
        return best_pool
    except Exception:
        return "Highspeed"


# ── Context Relevance (双通道: Embedding (Primary) + Entity Overlap (Secondary)) ──────────

# Thresholds for graded session action (based on embedding cosine similarity or Jaccard fallback)
# ── B策略优化 (0.50/0.30) ──────────────────────────────────────────────
# 准确率: 95.2% | 误切: 1条 | 漏切: 0 | 极端短消息补丁+指代词保护
THRESHOLD_CONTINUE = 0.62   # ≥ 0.62 → 延续（进一步降低粘连）
THRESHOLD_WARN = 0.42       # 0.42~0.62 → 延续但警告；<0.42 进入 new_session
# < 0.30 → /new (Branch C-auto)

# ── C-auto 防死循环机制 (v7.7) ──────────────────────────────────────────
# 问题：C-auto → /new → 新session只有1条消息 → 下次score极低 → 再次C-auto → 死循环
# 解法：三层旁路保护
C_AUTO_MIN_CONTEXT = 3       # 上下文消息少于此数时禁止 C-auto（判断素材不足）
C_AUTO_COOLDOWN_FILE = os.path.join(SCRIPT_DIR, ".c_auto_cooldown.json")
C_AUTO_COOLDOWN_MESSAGES = 3 # /new 之后 N 条消息内禁止 C-auto
C_AUTO_FUSE_WINDOW_SEC = 300 # 5分钟内 C-auto 触发超过此次数则熔断
C_AUTO_FUSE_MAX = 2          # 熔断阈值

def _load_cooldown() -> dict:
    try:
        with open(C_AUTO_COOLDOWN_FILE, "r") as f:
            return json.load(f)
    except:
        return {}

def _save_cooldown(data: dict):
    try:
        with open(C_AUTO_COOLDOWN_FILE, "w") as f:
            json.dump(data, f)
    except:
        pass

def c_auto_is_blocked(session_key: str = "default", context_count: int = 0) -> tuple:
    """
    检查 C-auto 是否被旁路保护阻止。
    Returns: (blocked: bool, reason: str)
    """
    now = datetime.now().timestamp()
    cd = _load_cooldown()
    sk = cd.get(session_key, {})

    # 保护1: 上下文消息不足
    if context_count < C_AUTO_MIN_CONTEXT:
        return True, f"上下文不足({context_count}<{C_AUTO_MIN_CONTEXT})"

    # 保护2: /new 冷却期
    last_reset_msg_count = sk.get("msg_since_reset", C_AUTO_COOLDOWN_MESSAGES + 1)
    if last_reset_msg_count < C_AUTO_COOLDOWN_MESSAGES:
        return True, f"冷却期({last_reset_msg_count}/{C_AUTO_COOLDOWN_MESSAGES}条)"

    # 保护3: 频率熔断
    recent_triggers = [t for t in sk.get("trigger_times", []) if now - t < C_AUTO_FUSE_WINDOW_SEC]
    if len(recent_triggers) >= C_AUTO_FUSE_MAX:
        return True, f"频率熔断({len(recent_triggers)}/{C_AUTO_FUSE_MAX}次/{C_AUTO_FUSE_WINDOW_SEC}s)"

    return False, ""

def c_auto_record_trigger(session_key: str = "default"):
    """记录 C-auto 触发事件（用于频率熔断）"""
    now = datetime.now().timestamp()
    cd = _load_cooldown()
    sk = cd.setdefault(session_key, {})
    triggers = [t for t in sk.get("trigger_times", []) if now - t < C_AUTO_FUSE_WINDOW_SEC * 2]
    triggers.append(now)
    sk["trigger_times"] = triggers
    sk["msg_since_reset"] = 0  # reset 计数器
    # C-auto 触发 → 重置 B+ 连续计数器
    sk["bplus_streak"] = 0
    _save_cooldown(cd)


# ── B+ 连续计数器 ──────────────────────────────────────────────────────────
# 设计：
#   - 每次结果为 B+ 时调用 bplus_record()，计数 +1
#   - 每次结果为 B 或 C / C-auto 或用户说"继续/接着"时调用 bplus_reset()
#   - bplus_check() 返回 (streak, should_warn, should_force_cauto)
#     should_warn=True     → 第3次，在回复末尾追加提示
#     should_force_cauto=True → 第4次及以后，强制跳入 C-auto

BPLUS_WARN_AT = 3    # 第几次 B+ 时追加提示
BPLUS_FORCE_AT = 4   # 第几次 B+ 时强制 C-auto

def bplus_record(session_key: str = "default") -> int:
    """记录一次 B+，返回当前连续次数。"""
    cd = _load_cooldown()
    sk = cd.setdefault(session_key, {})
    sk["bplus_streak"] = sk.get("bplus_streak", 0) + 1
    _save_cooldown(cd)
    return sk["bplus_streak"]

def bplus_reset(session_key: str = "default"):
    """重置 B+ 连续计数器（出现 B / C / C-auto / 用户主动延续时调用）。"""
    cd = _load_cooldown()
    sk = cd.setdefault(session_key, {})
    sk["bplus_streak"] = 0
    _save_cooldown(cd)

def bplus_check(session_key: str = "default") -> tuple:
    """查询当前 B+ 连续状态，不修改计数。
    Returns: (streak: int, should_warn: bool, should_force_cauto: bool)
    """
    cd = _load_cooldown()
    sk = cd.get(session_key, {})
    streak = sk.get("bplus_streak", 0)
    return streak, streak == BPLUS_WARN_AT, streak >= BPLUS_FORCE_AT

def c_auto_record_message(session_key: str = "default"):
    """记录一条消息（用于冷却期计数）"""
    cd = _load_cooldown()
    sk = cd.setdefault(session_key, {})
    sk["msg_since_reset"] = sk.get("msg_since_reset", C_AUTO_COOLDOWN_MESSAGES + 1) + 1
    _save_cooldown(cd)

def tokenize_zh_enhanced(text: str) -> set:
    """中文字符级(unigram + bigram + trigram) + 英文词级 分词"""
    text = text.lower().strip()
    tokens = set()
    # 英文单词（含下划线、连字符、点号的标识符）
    tokens.update(_re.findall(r'[a-zA-Z][a-zA-Z0-9_\-\.]+', text))
    # 英文短词（单字母的也要，但通过 entity 通道处理）
    tokens.update(_re.findall(r'[a-zA-Z]+', text))
    # 中文单字
    cn_chars = _re.findall(r'[\u4e00-\u9fff]', text)
    tokens.update(cn_chars)
    # 中文 bigram
    for i in range(len(cn_chars) - 1):
        tokens.add(cn_chars[i] + cn_chars[i + 1])
    # 中文 trigram（抓名词短语）
    for i in range(len(cn_chars) - 2):
        tokens.add(cn_chars[i] + cn_chars[i + 1] + cn_chars[i + 2])
    return tokens

def extract_entities(text: str) -> set:
    """提取关键实体（英文标识符、路径名、大写缩写、版本号等）"""
    entities = set()
    # 英文标识符（webhook, semantic_check, etc），2+ 字符
    entities.update(w for w in _re.findall(r'[a-zA-Z][a-zA-Z0-9_\-]+', text.lower()) if len(w) >= 2)
    # 路径A/B/C 这种标识
    entities.update(_re.findall(r'路径[A-Za-z0-9]', text))
    # Branch X
    entities.update(_re.findall(r'branch\s*[a-zA-Z]', text.lower()))
    # 版本号 v2.0 等
    entities.update(_re.findall(r'v\d+\.\d+', text.lower()))
    # 数字+单位 (端口号、阈值等) - 不作为entity，噪声太多
    return entities

def detect_task_type_fast(text: str) -> str | None:
    """
    轻量级任务类型判断（不读上下文，只做关键词匹配）。
    用于 task_type_jump 检测，避免递归调用完整 detect_task_type。
    返回 task_type 字符串，无匹配时返回 None。
    """
    for task_type, cfg in TASK_PATTERNS.items():
        if task_type == "continue":
            continue
        for kw in cfg.get("keywords", []):
            if kw in text:
                return task_type
    return None


def task_jump_penalty(current_input: str, context_messages: list) -> float:
    """
    计算任务类型跳变惩罚系数（方案C实现）。

    逻辑：
      1. 用 detect_task_type_fast 判断当前消息的 task_type
      2. 对历史消息中出现最多的 task_type 做统计（主导类型）
      3. 若当前类型 != 主导类型 → 返回惩罚系数（默认 0.55）
         同类型 → 返回 1.0（不惩罚）
         任一侧无法判断 → 返回 1.0（保守，不惩罚）

    Returns:
        penalty: float (0.55 if jump detected, else 1.0)
    """
    if not context_messages:
        return 1.0

    current_type = detect_task_type_fast(current_input)
    if current_type is None:
        return 1.0  # 无关键词，无法判断当前类型，不惩罚

    # 统计历史消息的主导 task_type
    type_counts: dict[str, int] = {}
    for ctx in context_messages:
        t = detect_task_type_fast(ctx)
        if t:
            type_counts[t] = type_counts.get(t, 0) + 1

    if not type_counts:
        return 1.0  # 历史无关键词消息，无法判断，不惩罚

    dominant_type = max(type_counts, key=lambda k: type_counts[k])

    if current_type != dominant_type:
        return 0.55  # 任务类型跳变，降低相似度
    return 1.0  # 同类型，不惩罚


def context_relevance_score(user_input: str, context_messages: list) -> tuple:
    """
    分层上下文关联度评分（v7.3: Embedding Primary → Jaccard Safety Net）。

    Architecture:
        Layer 1: Embedding (local all-MiniLM-L6-v2) - primary, semantic-aware
        Layer 2: Jaccard (token overlap) - safety net when embedding unavailable
        Layer 3: Entity overlap - supplementary signal in both layers

    Layered Fallback (P0 fix from QA audit):
        - Embedding available: use embed score directly (no Jaccard needed)
        - Embedding unavailable + Jaccard < 0.30: conservative → grade as "warn" not "new_session"
          (prevents aggressive context reset when only using token overlap)

    Returns:
        (score: float, method: str, grade: str)
        - score: 0.0 ~ 1.0
        - method: 'embed' | 'jaccard_fallback' | 'no_context'
        - grade: 'continue' | 'warn' | 'new_session'
    """
    if not context_messages:
        return 0.0, "no_context", "continue"  # 无上下文时保守延续

    # ── 方案B：窗口收窄到4（减少远距历史污染）─────────────────
    context_messages = context_messages[:4]

    # ── 方案C：任务类型跳变惩罚系数 ──────────────────────────────
    jump_penalty = task_jump_penalty(user_input, context_messages)

    # 获取客户端（重用或创建）
    client, provider = get_embedding_client()

    # Channel 1: 尝试 Embedding（精准语义匹配）
    msg_embedding = embed_text(user_input, client, provider) if client else None
    msg_entities = extract_entities(user_input)

    best_score = 0.0
    method = "jaccard_fallback"  # 默认降级方案
    embedding_available = False

    if msg_embedding:
        # Embedding 可用 - 使用语义向量匹配
        for ctx in context_messages:
            ctx_embedding = embed_text(ctx, client, provider)

            if ctx_embedding:
                embedding_available = True
                # Channel 1: Cosine similarity（向量空间中的语义相似度）
                embed_score = cosine_similarity(msg_embedding, ctx_embedding)

                # Channel 2: Entity overlap（关键词匹配补充）
                ctx_entities = extract_entities(ctx)
                if msg_entities and ctx_entities:
                    intersection_e = len(msg_entities & ctx_entities)
                    union_e = len(msg_entities | ctx_entities)
                    entity_score = intersection_e / union_e if union_e > 0 else 0.0
                else:
                    entity_score = 0.0

                # 综合：embed 权重 0.85，entity 权重 0.15
                # 方案C：乘以任务跳变惩罚系数（同类型=1.0，跳变=0.55）
                combined = min(1.0, (embed_score * 0.85 + entity_score * 0.15) * jump_penalty)

                if combined > best_score:
                    best_score = combined
                    method = "embed"

    if not embedding_available:
        # Embedding 不可用，降级到 Jaccard（兼容模式）
        msg_tokens = tokenize_zh_enhanced(user_input)

        for ctx in context_messages:
            ctx_tokens = tokenize_zh_enhanced(ctx)
            ctx_entities = extract_entities(ctx)

            # Channel 1: token Jaccard（降级）
            intersection_t = len(msg_tokens & ctx_tokens)
            union_t = len(msg_tokens | ctx_tokens)
            token_score = intersection_t / union_t if union_t > 0 else 0.0

            # Channel 2: entity overlap
            if msg_entities and ctx_entities:
                intersection_e = len(msg_entities & ctx_entities)
                union_e = len(msg_entities | ctx_entities)
                entity_score = intersection_e / union_e if union_e > 0 else 0.0
            else:
                entity_score = 0.0

            # 方案C：乘以任务跳变惩罚系数
            combined = min(1.0, max(token_score, entity_score * 1.5) * jump_penalty)

            if combined > best_score:
                best_score = combined
                method = "jaccard_fallback"

    # ── 分级判定（v7.3 分层 Fallback） ──────────
    if best_score >= THRESHOLD_CONTINUE:
        grade = "continue"
    elif best_score >= THRESHOLD_WARN:
        grade = "warn"
    else:
        if embedding_available:
            # Embedding 判定为低关联 - 可信度高，允许 new_session
            grade = "new_session"
        else:
            # Jaccard-only 判定低关联 - 可信度低（语义近义盲区）
            # P0 safety net: 保守降级为 warn 而非 new_session
            # 防止 Jaccard 无法识别的语义关联导致误触 C-auto
            if best_score > 0.03:
                grade = "warn"  # 有少量词重叠，保守延续
            else:
                grade = "new_session"  # 几乎无关联才允许 new_session

    return best_score, method, grade

def detect_task_type(user_input: str, context_messages: list = None):
    """
    检测任务类型（v7.6：两轴决策）

    Axis-1: task keyword confidence（决定目标池）
    Axis-2: context novelty（决定 C vs C-auto）

    Returns:
        (task_type, action, pool, branch, detection, context_score, context_grade)
    """
    if is_system_message(user_input):
        return "continue", "系统信号(透传)", None, "B", "system_passthrough", 1.0, "continue"

    ctx_msgs = context_messages or []

    # ── 层3（embedding）永远先跑：独立决定"换不换会话" ────────────────
    # score/grade 全程可用，与层2/层1的池决策完全并行
    # grade: "continue"(≥0.62) / "warn"(0.42~0.62) / "new_session"(<0.42)
    score, method, grade = context_relevance_score(user_input, ctx_msgs)
    session_key = os.environ.get("SESSION_KEY", "default")

    # ── v7.7: C-auto 旁路保护 ──────────────────────────────────────
    def _c_auto_or_bypass(pool_hint, detection, sc, gr):
        """尝试返回 C-auto，如果被旁路保护阻止则降级为 B+"""
        blocked, reason = c_auto_is_blocked(
            session_key=session_key,
            context_count=len(ctx_msgs),
        )
        if blocked:
            return "continue", f"延续(C-auto被旁路:{reason})", None, "B+", detection, sc, "warn"
        if pool_hint:
            inferred_pool = pool_hint
        else:
            inferred_pool = _compute_suggested_pool(user_input) or "Highspeed"
        return "new_topic", "自动/new+切池", inferred_pool, "C-auto", detection, sc, gr

    # ── 公共 B+ 返回辅助：记录计数，必要时升级为 C-auto ──────────────
    def _return_bplus(task_type_val, action_val, pool_val, detection_val, sc, gr_val, extra_note=""):
        """统一 B+ 出口：维护连续计数，第3次追加警告，第4次强制 C-auto。"""
        streak = bplus_record(session_key)
        _, should_warn, should_force = bplus_check(session_key)
        if should_force:
            # 强制 C-auto：话题连续漂移超限
            bplus_reset(session_key)
            return _c_auto_or_bypass(pool_val, f"bplus_force(streak={streak})", sc, "new_session")
        note = extra_note
        if should_warn:
            note = f"{extra_note}|drift_warn" if extra_note else "drift_warn"
        return "continue", f"延续(话题漂移警告{':' + note if note else ''})", pool_val, "B+", detection_val, sc, gr_val

    # A. 明确延续意图：continue 关键词（层1）
    # continue/接着 是强信号，不走层2多词逻辑，直接层1专属通道
    cont_type, cont_action, cont_pool, _, _soft = layer1_match(
        user_input,
        include_continue=True,
        include_non_continue=False,
    )
    if cont_type:
        bplus_reset(session_key)  # 明确延续 → 重置 B+ 计数器
        is_fork_recovery = any(s in user_input for s in _FORK_RECOVERY_SIGNALS)
        if grade == "new_session":
            result_action = "延续(低关联警告)" + (" [fork_recovery]" if is_fork_recovery else "")
            return "continue", result_action, cont_pool, "B+", "keyword_continue", score, "warn"
        result_action = cont_action + (" [fork_recovery]" if is_fork_recovery else "")
        return "continue", result_action, cont_pool, "B", "keyword_continue", max(score, 1.0), "continue"

    # A+. bonus_keywords: 降级延续词，仅做 embedding score +0.10 加权
    bonus_keywords = TASK_PATTERNS.get("continue", {}).get("bonus_keywords", [])
    if any(kw in user_input for kw in bonus_keywords):
        score = min(score + 0.10, 1.0)
        grade = "continue" if score >= THRESHOLD_CONTINUE else ("warn" if score >= THRESHOLD_WARN else "new_session")

    # ── 层2优先：多词非连续命中 → 决定目标池 ──────────────────────────
    l2_type, l2_action, l2_pool, l2_is_cont = layer2_match(
        user_input,
        include_continue=False,
        include_non_continue=True,
    )

    # ── 层1备用：层2无命中时才运行 ──────────────────────────────────
    if l2_type is not None:
        task_type, action, pool, is_soft = l2_type, l2_action, l2_pool, False
        detection_src = "layer2"
    else:
        l1 = layer1_match(user_input, include_continue=False, include_non_continue=True)
        task_type, action, pool, _, is_soft = l1
        detection_src = "layer1"

    # B. 非 continue 任务命中处理
    if task_type:
        # soft_keywords 命中：降级为 B+，不强切模型池
        if is_soft:
            return _return_bplus(task_type, action, None, f"keyword_soft({detection_src})", score, grade)

        # model_switch：直接解析目标池，C 分支切模型不重置会话
        if task_type == "model_switch":
            bplus_reset(session_key)
            target_pool = parse_target_pool_from_input(user_input)
            return "model_switch", "切换模型池", target_pool, "C", "keyword", max(score, 1.0), "continue"

        # 层3（embedding）决定是否切会话：
        #   new_session → C-auto（切池+重置会话）
        #   warn/continue → C（切池，保留会话）
        if grade == "new_session":
            bplus_reset(session_key)
            return _c_auto_or_bypass(pool, detection_src, score, grade)
        bplus_reset(session_key)
        return task_type, action, pool, "C", detection_src, score, grade

    # C. 指示词仅在层2/层1均无命中时生效
    if indicator_match(user_input):
        if grade == "new_session":
            return _return_bplus(None, "延续(低关联警告)", None, "indicator", score, "warn")
        bplus_reset(session_key)
        return "continue", "延续", None, "B", "indicator", max(score, 1.0), "continue"

    # D. 层3：完全由上下文新颖度决定（embedding）
    if grade == "continue":
        bplus_reset(session_key)
        return "continue", "延续", None, "B", f"context_{method}", score, grade
    if grade == "warn":
        is_anomaly, adjusted_grade, patch_reason = _short_message_anomaly_patch(user_input, score, grade)
        if is_anomaly:
            return _return_bplus(None, f"短消息保护:{patch_reason}", None,
                                 f"context_{method}_patched", score, adjusted_grade)
        return _return_bplus(None, "话题可能漂移", None, f"context_{method}", score, grade)

    # grade == new_session，且无任何关键词/指示词命中 → C-auto
    bplus_reset(session_key)
    return _c_auto_or_bypass("Highspeed", f"context_{method}", score, grade)

def get_pool_info(pool_name: str):
    if pool_name and pool_name in MODEL_POOLS:
        return MODEL_POOLS[pool_name]
    return None

def get_current_pool():
    return os.environ.get("CURRENT_POOL", "Highspeed")

def generate_declaration(result: dict, current_pool: str, current_model: str = None) -> str:
    """生成语义检查声明（v7.9.3+ 简化格式）
    
    新格式：【语义检查】模型池:【XXX】｜实际模型:XXX｜延续/新会话
    - 去掉 P级别、偏移量图标、分数
    - 只保留模型池、实际模型、会话状态（延续/新会话）
    """
    branch = result.get("branch", "C")
    
    # 获取模型池中文名
    if branch in ("C", "C-auto"):
        # C/C-auto 分支：使用目标池
        target_pool_key = result.get("pool", "Highspeed")
        pool_info = get_pool_info(target_pool_key)
        pool_chinese = pool_info.get("name", target_pool_key) if pool_info else (target_pool_key or "未知池")
        # 使用 primary_model 作为实际模型
        primary = result.get("primary_model", "")
        model_short = primary.split("/")[-1] if primary else "未知"
    else:
        # B/B+ 分支：优先使用当前模型；若未显式传入，则回退到当前池的 primary，而不是池名本身
        pool_chinese = MODEL_POOLS.get(current_pool, {}).get("name", current_pool)
        fallback_model = MODEL_POOLS.get(current_pool, {}).get("primary", "")
        model_short = (current_model or fallback_model).split("/")[-1] or "未知"
    
    # 确定会话状态：延续 或 新会话
    if branch in ("B", "B+"):
        session_state = "延续"
    else:
        # C 和 C-auto 分支都是新会话
        session_state = "新会话"
    
    base_decl = f"【语义检查】模型池:【{pool_chinese}】｜实际模型:{model_short}｜{session_state}"

    # Fork recovery 提示
    action = result.get("action", "")
    if "[fork_recovery]" in str(action):
        base_decl += "\n⚠️ 原始任务恢复：正从分叉子任务返回，请回忆本次对话的主线任务目标，而非最近的子任务"

    # B+ 连续漂移警告（第3次时追加，让模型在回复末尾给用户提示）
    if branch == "B+" and "drift_warn" in str(action):
        base_decl += "\n💡 [系统提示] 话题已持续漂移，如需保留当前上下文请回复「继续」，否则将在下次自动开启新会话"

    return base_decl

def ensure_declaration_first_line(reply_text: str, declaration: str) -> str:
    """Outbound 安全门禁：确保声明在首行，不重复注入。"""
    body = (reply_text or "").strip("\n")
    decl = (declaration or "").strip()
    if not decl:
        return body
    if not body:
        return decl

    first_line = body.splitlines()[0].strip()
    if first_line == decl:
        return body

    # 如果首行已经是语义声明但内容不一致，强制以 semantic_check 产物为准
    if first_line.startswith("【语义检查】"):
        rest = "\n".join(body.splitlines()[1:]).lstrip("\n")
        return decl + ("\n" + rest if rest else "")

    return decl + "\n" + body


def build_context_archive_prompt():
    return """[上下文截止符] 之前的对话已归档。从本条消息开始作为新的上下文起点。"""

def execute_model_switch(model: str, session_key: str = None) -> bool:
    """执行模型切换（自动+真实执行）。

    Strategy:
      1) openclaw session_status --model <model> [--sessionKey <key>]
      2) fallback: openclaw status --model <model>
    """
    if not model:
        return False

    candidates = []
    if session_key:
        candidates.append(["openclaw", "session_status", "--model", model, "--sessionKey", session_key])
    candidates.append(["openclaw", "session_status", "--model", model])
    candidates.append(["openclaw", "status", "--model", model])

    for cmd in candidates:
        try:
            proc = subprocess.run(cmd, capture_output=True, text=True, timeout=8)
            if proc.returncode == 0:
                print(f"✅ 模型切换成功: {model} via {' '.join(cmd[:2])}", file=sys.stderr)
                return True
            else:
                print(f"⚠️ 模型切换尝试失败({proc.returncode}): {' '.join(cmd)} | {proc.stderr[:160]}", file=sys.stderr)
        except FileNotFoundError:
            print("❌ openclaw CLI 不存在，无法自动切换模型", file=sys.stderr)
            return False
        except subprocess.TimeoutExpired:
            print(f"⚠️ 模型切换超时: {' '.join(cmd)}", file=sys.stderr)
        except Exception as e:
            print(f"⚠️ 模型切换异常: {' '.join(cmd)} | {e}", file=sys.stderr)

    return False

def execute_fallback_chain(primary: str, fallback_1: str = None, fallback_2: str = None) -> dict:
    """
    执行 Fallback 回路
    返回: {"attempted": [...], "success": bool, "current_model": str}
    """
    results = {
        "attempted": [],
        "success": False,
        "current_model": primary
    }

    models_to_try = [primary]
    if fallback_1:
        models_to_try.append(fallback_1)
    if fallback_2:
        models_to_try.append(fallback_2)

    for model in models_to_try:
        print(f"🔄 Trying model: {model}", file=sys.stderr)
        results["attempted"].append(model)

        if execute_model_switch(model):
            results["success"] = True
            results["current_model"] = model
            print(f"✅ Fallback success: {model}", file=sys.stderr)
            return results

    print(f"❌ All fallback attempts failed", file=sys.stderr)
    return results

def main():
    parser = argparse.ArgumentParser(description="Semantic Router - 模型路由脚本")
    parser.add_argument("user_input", nargs="?", help="用户输入消息")
    parser.add_argument("current_pool", nargs="?", help="当前模型池")
    parser.add_argument("context_messages", nargs="*", help="上下文消息列表")
    parser.add_argument("--current-model", default=None, help="当前实际使用的模型 ID（用于B分支声明）")
    parser.add_argument("--session-key", default=None, help="当前会话 key（用于上下文隔离读取）")
    parser.add_argument("-e", "--execute", action="store_true", help="自动执行模型切换（主模型）")
    parser.add_argument("--no-auto-execute", action="store_true", help="禁用默认自动模型切换（默认开启）")
    parser.add_argument("-f", "--fallback", action="store_true", help="执行 Fallback 回路（主模型失败时自动切换备用）")

    args = parser.parse_args()

    # 如果没有参数，显示用法
    if len(sys.argv) < 2:
        print("Usage: semantic_check.py <user_input> [current_pool] [context1] [context2] ...] [-e|--execute] [-f|--fallback]")
        print("Example: semantic_check.py '查一下天气' 'Intelligence' -e")
        print("Example: semantic_check.py --fallback 'openai/gpt-4o-mini' 'glm-4.7-flashx' 'MiniMax-M2.5'")
        sys.exit(1)

    # Fallback 模式：手动指定模型链
    if args.fallback:
        fallback_models = []
        if args.user_input:
            fallback_models.append(args.user_input)
        if args.current_pool:
            fallback_models.append(args.current_pool)
        fallback_models.extend(args.context_messages)

        fallback_results = execute_fallback_chain(
            fallback_models[0] if len(fallback_models) > 0 else None,
            fallback_models[1] if len(fallback_models) > 1 else None,
            fallback_models[2] if len(fallback_models) > 2 else None
        )
        print(json.dumps(fallback_results, ensure_ascii=False, indent=2))
        return

    raw_input = args.user_input
    user_input = strip_declaration_injection(unwrap_semantic_router_envelope(raw_input))
    current_pool = args.current_pool if args.current_pool else get_current_pool()
    current_model = args.current_model

    session_key = (
        args.session_key
        or os.environ.get("OPENCLAW_SESSION_KEY")
        or os.environ.get("SESSION_KEY")
        or extract_session_key_from_input(raw_input)
    )

    # Phase 1 strict gate: session_key mandatory
    valid_session_key, session_key_reason = validate_session_key(session_key)
    if not valid_session_key:
        error_result = {
            "ok": False,
            "error_code": "SESSION_GATE_REJECTED",
            "reason": session_key_reason,
            "message": "strict gate rejected",
            "retryable": False,
            "session_key": session_key,
        }
        print(json.dumps(error_result, ensure_ascii=False, indent=2))
        sys.exit(2)

    context_messages = args.context_messages if args.context_messages else get_recent_messages(
        limit=5,
        exclude_input=raw_input,
        session_key=session_key,
    )

    # v7.7: 设置环境变量供 C-auto 旁路保护使用
    os.environ["SESSION_KEY"] = session_key or "default"

    # Step 2C 集成：L0/L1 前置规则检查（只输出命中信息，不改变语义路由核心决策）
    l0_precheck = None
    if check_l0_rules:
        try:
            m = check_l0_rules(user_input)
            if getattr(m, "matched", False):
                l0_precheck = {
                    "matched": True,
                    "rule_id": (m.rule or {}).get("id"),
                    "priority": (m.rule or {}).get("priority"),
                    "score": getattr(m, "score", 0.0),
                    "action": (m.rule or {}).get("action"),
                }
        except Exception:
            l0_precheck = None

    # L2/L3 索引命中（skill_index）
    l23_index_match = None
    if match_index_levels:
        try:
            l23_index_match = match_index_levels(user_input, levels=("L2", "L3"))
        except Exception:
            l23_index_match = None

    # Step 4: Fit Gate 判定器 (skill trigger boost)
    fit_gate_result = None
    skill_dispatch_plan = None
    if fit_gate:
        try:
            fit_gate_result = fit_gate(user_input)
            if fit_gate_result.matched and plan_skill_dispatch:
                # Step 3: 自动执行闭环计划（仅计划，不改动语义路由核心分支）
                skill_dispatch_plan = plan_skill_dispatch(
                    fit_gate_result,
                    user_input=user_input,
                    session_key=session_key or "default",
                )
        except Exception:
            fit_gate_result = None
            skill_dispatch_plan = None

    task_type, action, pool_name, branch, detection, ctx_score, ctx_grade = detect_task_type(user_input, context_messages)

    # v7.7: C-auto 防死循环记录
    _sk = session_key or "default"
    if branch == "C-auto":
        c_auto_record_trigger(_sk)
    else:
        c_auto_record_message(_sk)

    # B/B+ 分支延续时，pool_name 可能为 None（continue 类型没有定义 pool）
    # 此时应保持 current_pool
    if pool_name is None and branch in ("B", "B+"):
        pool_name = current_pool

    pool_info = get_pool_info(pool_name)

    # 判断是否需要切换模型
    need_switch = bool(task_type not in ("continue",) and pool_info and pool_info.get("primary"))
    target_model = pool_info.get("primary") if (need_switch or branch == "C-auto") else None
    if branch == "C-auto" and pool_info:
        need_switch = True
        target_model = pool_info.get("primary")

    # action_command: 代理必须无条件执行的原子指令
    # "continue"       → 不切换，直接回复
    # "continue_warn"  → 延续但在声明中标注漂移警告
    # "switch"         → 切换到 target_model，然后回复（同会话内切模型）
    # "new_and_switch"  → 执行 /new 清空上下文 + 切换到目标池 primary（C-auto 专用）
    if branch == "B":
        action_command = "continue"
    elif branch == "B+":
        action_command = "continue_warn"
    elif branch == "C-auto":
        action_command = "new_and_switch"  # v7.2: 自动 /new + 切到目标池 primary
    else:  # C
        action_command = "switch"

    result = {
        "branch": branch,
        "task_type": task_type,
        "action": action,
        "pool": pool_name,
        "pool_name": pool_info.get("name") if pool_info else None,
        "primary_model": target_model,
        "fallback_1": pool_info.get("fallback_1") if pool_info else None,
        "fallback_2": pool_info.get("fallback_2") if pool_info else None,
        "fallback_3": pool_info.get("fallback_3") if pool_info else None,
        "fallback_4": pool_info.get("fallback_4") if pool_info else None,
        "need_archive": branch in ("C", "C-auto"),
        "need_reset": branch == "C-auto",  # C-auto: 自动 /new 清空上下文
        "need_switch": need_switch or branch == "C-auto",  # C-auto 也需要切换
        "action_command": action_command,
        # legacy compat
        "session_action": action_command,
        "detection_method": detection,
        "context_score": ctx_score,
        "context_grade": ctx_grade,
        # Fix-A: pool most semantically aligned with user_input (for B/B+ forced re-eval).
        # For C/C-auto branches, this mirrors pool (already correct).
        "suggested_pool": pool_name if branch in ("C", "C-auto") else _compute_suggested_pool(user_input),
        "fallback_chain": [
            target_model,
            pool_info.get("fallback_1"),
            pool_info.get("fallback_2"),
            pool_info.get("fallback_3"),
            pool_info.get("fallback_4"),
        ] if pool_info else [],
        "declaration": None,
        "outbound_first_line_guard": "ensure_declaration_first_line",
        "context_cutoff_prompt": build_context_archive_prompt() if branch in ("C", "C-auto") else None,
        "auto_executed": False,
        "session_key": session_key,
        "l0_precheck": l0_precheck,
        "l23_index_match": l23_index_match,
        "fit_gate": {
            "matched": fit_gate_result.matched if fit_gate_result else False,
            "skill_id": fit_gate_result.skill_id if fit_gate_result else None,
            "confidence": fit_gate_result.confidence if fit_gate_result else 0.0,
            "reason": fit_gate_result.reason if fit_gate_result else "",
            "level": fit_gate_result.level if fit_gate_result else None,
        } if fit_gate_result else None,
        "skill_dispatch": {
            "should_dispatch": skill_dispatch_plan.should_dispatch if skill_dispatch_plan else False,
            "dispatch_id": skill_dispatch_plan.dispatch_id if skill_dispatch_plan else None,
            "skill_id": skill_dispatch_plan.skill_id if skill_dispatch_plan else (fit_gate_result.skill_id if fit_gate_result else None),
            "blocked_reason": skill_dispatch_plan.blocked_reason if skill_dispatch_plan else "",
            "dedup_hit": skill_dispatch_plan.dedup_hit if skill_dispatch_plan else False,
            "debounce_hit": skill_dispatch_plan.debounce_hit if skill_dispatch_plan else False,
            "circuit_open": skill_dispatch_plan.circuit_open if skill_dispatch_plan else False,
            "source": skill_dispatch_plan.source if skill_dispatch_plan else ("fit_gate" if fit_gate_result else None),
        } if (fit_gate_result or skill_dispatch_plan) else None,
    }
    result["declaration"] = generate_declaration(result, current_pool, current_model)

    # Step 3: skill-trigger 自动执行最后一跳（调度指令，不改变语义路由主分支）
    if skill_dispatch_plan and skill_dispatch_plan.should_dispatch and fit_gate_result:
        result["skill_action_command"] = "trigger_skill"
        result["skill_trigger"] = {
            "skill_id": fit_gate_result.skill_id,
            "dispatch_id": skill_dispatch_plan.dispatch_id,
            "source": "fit_gate",
            "confidence": fit_gate_result.confidence,
            "level": fit_gate_result.level,
        }
        if generate_boost_declaration:
            result["boost_declaration"] = generate_boost_declaration(fit_gate_result)
    elif fit_gate_result:
        result["skill_action_command"] = "none"

    # 记录日志
    log_file = os.path.expanduser("~/.openclaw/workspace/.lib/semantic_check.log")
    try:
        with open(log_file, "a", encoding="utf-8") as f:
            method_icon = {
                "context_embed": "📊",
                "embed": "📊",
                "context_jaccard_fallback": "⚙️",
                "jaccard_fallback": "⚙️",
                "context_token": "⚙️",
                "keyword_continue": "🔑",
                "indicator": "🔍",
                "keyword": "🔑",
                "no_context": "○",
                "system_passthrough": "🛡️"
            }.get(detection, "?")
            skill_log = ""
            if skill_dispatch_plan:
                skill_log = (
                    f" | skill_dispatch={skill_dispatch_plan.should_dispatch}"
                    f" skill={skill_dispatch_plan.skill_id}"
                    f" blocked={skill_dispatch_plan.blocked_reason or '-'}"
                )
            elif fit_gate_result and fit_gate_result.matched:
                skill_log = f" | skill_candidate={fit_gate_result.skill_id}"
            f.write(f"[{datetime.now().isoformat()}] {user_input[:40]:40} | {branch:5} {task_type:20} {method_icon} score={ctx_score:.3f} grade={ctx_grade}{skill_log}\n")
    except Exception as e:
        pass

    # 如果需要切换则自动执行（默认开启，可用 --no-auto-execute 关闭）
    auto_execute_enabled = (not args.no_auto_execute) and (
        args.execute or os.environ.get("SEMANTIC_AUTO_EXECUTE", "1") == "1"
    )
    if need_switch and target_model and auto_execute_enabled:
        print(f"🔄 Auto-switching model to: {target_model}", file=sys.stderr)
        success = execute_model_switch(target_model, session_key=session_key)
        result["auto_executed"] = success

    print(json.dumps(result, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
