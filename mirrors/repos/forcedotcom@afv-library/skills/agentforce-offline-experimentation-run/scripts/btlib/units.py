"""One replay unit per production LLM_STEP (schema bt.unit/1).

A turn makes several LLM calls: the router picks a sub-agent (go_to_*), then the sub-agent
calls tools and finally replies. Each call is its own unit, with its own request and its own
golden (that step's gen_ai.output.messages[0]) — never the turn's final reply and never the
ACTION_STEP's platform action name (Shopper_Add_To_Cart is not the AddToCart tool the model
called).

unit_id = "<session_id>:<turn index>:<step ordinal>"; the ordinal counts every LLM_STEP of
the turn ordered by (start_time, step_id), skipped ones included, so ids do not depend on
filters.
"""

import json
import re
from collections import Counter

from . import SCHEMA_UNIT
from .messages import build_messages

DEFAULT_ROUTER_NODES = ("agent_router", "topic_selector")
GROUNDEDNESS_NODE = "Atlas__GroundednessValidationPrompt"
# LLM steps that validate a reply instead of making an agent decision. They carry no
# input messages either; listed so the skip reason is explicit.
NON_DECISION_NODES = (GROUNDEDNESS_NODE,)
# What production's own checks said of a turn. The steps are not replayed, and their results are
# text: "category=GROUNDED, reason=..." and "InstructionAdherence: value=UNCERTAIN, ...;
# TaskResolution: value=...". Only these values are kept, never the reasons.
_GROUNDEDNESS = re.compile(r"\bcategory=([A-Z][A-Z_]*)")
_GUARDRAIL = re.compile(r"\b([A-Za-z]\w*): value=([A-Z][A-Z_]*)")


def _load(text):
    if not text:
        return None
    try:
        return json.loads(text)
    except (TypeError, json.JSONDecodeError):
        return None


def parse_finish_reasons(value):
    """"('tool_calls',)" -> 'tool_calls'; lists and plain strings pass through."""
    if isinstance(value, (list, tuple)):
        return value[0] if value else None
    if not isinstance(value, str):
        return None
    v = value.strip().strip("()[]").strip().rstrip(",").strip().strip("'\"")
    return v or None


def parse_arguments(arguments):
    """(args dict, raw string or None). Unparseable arguments are kept raw."""
    if isinstance(arguments, dict):
        return arguments, None
    if arguments in (None, ""):
        return {}, None
    if isinstance(arguments, str):
        try:
            v = json.loads(arguments)
            if isinstance(v, dict):
                return v, None
        except json.JSONDecodeError:
            pass
    return {}, arguments if isinstance(arguments, str) else json.dumps(arguments)


def golden_from_output(output):
    """The step's own answer, from gen_ai.output.messages[0]: every tool call, or the text."""
    msgs = (output or {}).get("gen_ai.output.messages") or []
    if not msgs:
        return None
    m = msgs[0]
    finish = parse_finish_reasons(output.get("gen_ai.response.finish_reasons")) or m.get("finish_reason")
    calls = []
    for inv in m.get("tool_invocations") or []:
        fn = inv.get("function") or {}
        args, raw = parse_arguments(fn.get("arguments"))
        call = {"name": fn.get("name"), "args": args}
        if raw is not None:
            call["args_raw"] = raw
        calls.append(call)
    golden = {"kind": "tool" if calls else "text", "tool_calls": calls,
              "text": m.get("content") or "", "finish_reason": finish}
    if len(msgs) > 1:
        golden["extra_output_messages"] = len(msgs) - 1
    return golden


def _step_result(step):
    out = _load(step.get("output"))
    result = out.get("mgr.sensitive.step.result") if isinstance(out, dict) else None
    return result if isinstance(result, str) else ""


def production_signals(convo, turn):
    """Report-only: production's own checks of a turn, which never change a score (the golden is
    production's answer, right or wrong). groundedness: the category the groundedness check gave
    the turn's reply (GROUNDED, PARTIALLY_GROUNDED_SUGGESTION, SMALL_TALK, ...); guardrails: the
    value of each trust guardrail (InstructionAdherence, TaskResolution); step_errors: the turn's
    steps with an error; and the session's end type and action error count. None or {} where STDM
    has no such record."""
    steps = sorted(turn.get("steps") or [], key=lambda s: (s.get("start_time") or "", s.get("step_id") or ""))
    groundedness, guardrails = None, {}
    for s in steps:
        if s.get("step_type") == "LLM_STEP" and s.get("name") == GROUNDEDNESS_NODE:
            m = _GROUNDEDNESS.search(_step_result(s))
            groundedness = m.group(1) if m else groundedness
        elif s.get("step_type") == "TRUST_GUARDRAILS_STEP":
            guardrails.update(_GUARDRAIL.findall(_step_result(s)))
    return {"groundedness": groundedness, "guardrails": guardrails,
            "step_errors": sum(1 for s in steps if s.get("error")),
            "session_end_type": convo.get("end_type"), "session_action_errors": convo.get("action_error_count")}


def _turn_user_text(turn):
    for msg in turn.get("messages") or []:
        if msg.get("message_type") == "Input" and msg.get("text"):
            return msg["text"].strip()
    return ""


def build_units(conversations, org=None, agent=None, router_nodes=DEFAULT_ROUTER_NODES,
                steps="all"):
    """(units, skipped Counter). steps: 'router' | 'subagent' | 'all'."""
    if steps not in ("router", "subagent", "all"):
        raise ValueError(f"steps must be router|subagent|all, not {steps!r}")
    router_nodes = set(router_nodes)
    units, skipped = [], Counter()
    for convo in conversations:
        sid = convo.get("session_id")
        for t_idx, turn in enumerate(convo.get("turns") or []):
            llm = [s for s in turn.get("steps") or [] if s.get("step_type") == "LLM_STEP"]
            llm.sort(key=lambda s: (s.get("start_time") or "", s.get("step_id") or ""))
            for ordinal, step in enumerate(llm):
                node = step.get("name") or ""
                if node in NON_DECISION_NODES:
                    skipped["non_decision_step"] += 1
                    continue
                inp = _load(step.get("input"))
                if inp is None:
                    skipped["input_unparseable" if step.get("input") else "no_input"] += 1
                    continue
                stdm_msgs = inp.get("gen_ai.input.messages")
                if not stdm_msgs:
                    skipped["no_input_messages"] += 1
                    continue
                out = _load(step.get("output"))
                golden = golden_from_output(out)
                if golden is None:
                    skipped["no_output_message"] += 1
                    continue
                kind = "router" if node in router_nodes else "subagent"
                if steps != "all" and steps != kind:
                    skipped["not_selected"] += 1
                    continue
                units.append({
                    "schema": SCHEMA_UNIT,
                    "unit_id": f"{sid}:{t_idx}:{ordinal}",
                    "session_id": sid,
                    "turn": t_idx,
                    "step": ordinal,
                    "step_id": step.get("step_id"),
                    "interaction_id": turn.get("interaction_id"),
                    "org": org,
                    "agent": agent,
                    "agent_version": None,
                    "node": node,
                    "step_kind": kind,
                    "request": {
                        "messages": build_messages(stdm_msgs),
                        "tools": inp.get("gen_ai.request.tools") or [],
                        "model": inp.get("gen_ai.request.model"),
                        "settings": {"prompt_template": inp.get("af.prompt_template_dev_name"),
                                     "stream": inp.get("gen_ai.request.stream")},
                    },
                    "golden": golden,
                    "split": None,
                    "channel": convo.get("channel"),
                    "topic": turn.get("topic"),
                    "user_utterance": _turn_user_text(turn),
                    "start_time": step.get("start_time"),
                    "production": production_signals(convo, turn),
                })
    return units, skipped


def tool_names(unit):
    return [(t.get("function") or {}).get("name") for t in unit["request"]["tools"]]


def tool_schemas(unit):
    """{tool name: parameters schema} for the tools offered to this step."""
    out = {}
    for t in unit["request"]["tools"]:
        fn = t.get("function") or {}
        if fn.get("name"):
            out[fn["name"]] = fn.get("parameters") or {}
    return out
