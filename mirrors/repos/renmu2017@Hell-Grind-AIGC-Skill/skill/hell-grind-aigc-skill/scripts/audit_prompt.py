#!/usr/bin/env python3
"""Read-only structural audit for model-agnostic image and video prompts."""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any


SUBJECT_PATTERN = re.compile(
    r"画面中|主体|人物|角色|男人|女人|男孩|女孩|人群|生物|怪物|道具|产品|物体|环境|场景|"
    r"\b(?:subject|character|person|people|man|woman|boy|girl|creature|monster|prop|product|object|environment|scene)\b",
    re.IGNORECASE,
)
DURATION_PATTERN = re.compile(
    r"(?:总时长|时长|duration)?\s*\d+(?:\.\d+)?\s*(?:秒|s\b|sec(?:ond)?s?\b)",
    re.IGNORECASE,
)
CAMERA_PATTERN = re.compile(
    r"摄影机|镜头|机位|景别|构图|焦段|运镜|推进|拉远|环绕|跟拍|摇摄|俯拍|仰拍|"
    r"\b(?:camera|shot|framing|lens|dolly|push|pull|orbit|track|pan|tilt|crane|handheld)\b",
    re.IGNORECASE,
)
CAMERA_END_PATTERN = re.compile(
    r"camera_end|结束构图|最终(?:停|落|定格)|尾帧|结尾画面|停在|落到|"
    r"\b(?:end frame|final frame|ends? (?:on|with|at)|settles? (?:on|at)|finishes? (?:on|at))\b",
    re.IGNORECASE,
)
AUDIO_PATTERN = re.compile(
    r"audio|sound|dialogue|voice|music|score|subtitle|silent|ambience|foley|"
    r"声音|音频|对白|台词|人声|环境音|拟音|配乐|音乐|字幕|静默|无声|呼吸|脚步",
    re.IGNORECASE,
)
QUANTITY_PATTERN = re.compile(
    r"恰好|精确人数|只有|各出现一次|\b(?:exactly|only|one|two|three|four|five)\b|\b\d+\s*(?:人|名|个|只)",
    re.IGNORECASE,
)
REFERENCE_PATTERN = re.compile(r"参考|引用|reference|image[_ -]?\d+|<<<[^>]+>>>", re.IGNORECASE)
REFERENCE_SCOPE_PATTERN = re.compile(r"inherit|exclude|继承|排除|只(?:继承|参考)", re.IGNORECASE)
PLATFORM_PATTERN = re.compile(r"平台适配|provider|model|seed|steps?|cfg|sampler|采样|运动强度", re.IGNORECASE)
LIGHT_PATTERN = re.compile(r"光源|主光|曝光|颜色|材质|天气|lighting|exposure|color|material|weather", re.IGNORECASE)
ACTION_PATTERN = re.compile(r"动作|视线|呼吸|重心|接触|反作用|action|eyeline|breath|weight|contact|reaction", re.IGNORECASE)
CONTINUITY_PATTERN = re.compile(r"continuity|连续性|must_hold|changes_here|must_not_appear|必须保持|本镜变化|禁止出现", re.IGNORECASE)
STILL_PATTERN = re.compile(
    r"全程.{0,12}(?:完全)?静止|完全静止|保持不动|身体位置.{0,12}不变|"
    r"\b(?:stand|remain|stay) completely still\b|\bno movement\b",
    re.IGNORECASE,
)
SUBJECT_MOTION_PATTERN = re.compile(
    r"持续.{0,10}(?:奔跑|跑动|移动|行走)|奔跑|跑向|快步走|不断移动|"
    r"\b(?:keeps? |continues? |constantly )?(?:running|walking|moving)\b",
    re.IGNORECASE,
)
LOCKED_CAMERA_PATTERN = re.compile(r"锁定机位|固定机位|摄影机固定|\blocked[- ]?off\b|\bstatic camera\b", re.IGNORECASE)
CAMERA_MOVE_PATTERNS = {
    "orbit": re.compile(r"环绕|orbit", re.IGNORECASE),
    "push": re.compile(r"推进|推近|push(?:es)? in|dolly in", re.IGNORECASE),
    "pull": re.compile(r"拉远|pull(?:s)? out|dolly out", re.IGNORECASE),
    "track": re.compile(r"跟拍|跟随|track(?:s|ing)?|follow(?:s|ing)?", re.IGNORECASE),
    "pan": re.compile(r"横摇|摇摄|\bpan(?:s|ning)?\b", re.IGNORECASE),
    "tilt": re.compile(r"俯仰摇摄|\btilt(?:s|ing)?\b", re.IGNORECASE),
    "crane": re.compile(r"升降|crane|boom", re.IGNORECASE),
}
TOTAL_DURATION_PATTERN = re.compile(
    r"(?:总时长|时长|duration)\s*[:：=为]?\s*(\d+(?:\.\d+)?)\s*(?:秒|s\b|sec(?:ond)?s?\b)",
    re.IGNORECASE,
)
TIME_RANGE_PATTERN = re.compile(
    r"(\d+(?:\.\d+)?)\s*[-–—]\s*(\d+(?:\.\d+)?)\s*(?:秒|s\b|sec(?:ond)?s?\b)",
    re.IGNORECASE,
)
PRIVATE_PARAMETER_PATTERN = re.compile(r"\bseed\b|\bsteps?\b|\bcfg\b|\bsampler\b|采样器|采样步数", re.IGNORECASE)
ADAPTER_SECTION_PATTERN = re.compile(r"平台适配层|provider adapter|adapter layer", re.IGNORECASE)
EXACT_DIALOGUE_PATTERN = re.compile(
    r"逐字.{0,12}(?:对白|台词|说)|(?:说|says?|speaks?)\s*[“\"']|exact (?:dialogue|line)",
    re.IGNORECASE,
)
DIALOGUE_VISUAL_BOUNDARY_PATTERN = re.compile(
    r"对白不视觉化|台词不视觉化|只作为声音|仅作为声音|不触发闪回|没有闪回|"
    r"dialogue.{0,20}(?:audio only|not visualized)|no flashback",
    re.IGNORECASE,
)
ABSTRACT_PATTERN = re.compile(r"高级|震撼|电影感|史诗感|唯美|梦幻|大片感|premium|cinematic|epic|stunning", re.IGNORECASE)
CONCRETE_PATTERN = re.compile(
    r"画面中|主体|人物|角色|场景|道具|动作|视线|构图|机位|光源|材质|颜色|"
    r"subject|character|scene|prop|action|camera|light|material|color",
    re.IGNORECASE,
)
NEGATIVE_SYNONYM_GROUPS = [
    re.compile(r"无配乐|不要音乐|无音乐|no score|no music", re.IGNORECASE),
    re.compile(r"无额外人物|不要加人|不加人|no extra (?:people|characters)", re.IGNORECASE),
    re.compile(r"无字幕|不要字幕|no subtitles?", re.IGNORECASE),
    re.compile(r"无抖动|不要抖动|no jitter|no shake", re.IGNORECASE),
]


@dataclass(frozen=True)
class PromptIssue:
    code: str
    severity: str
    line: int | None
    message: str
    suggestion: str


def line_for(text: str, pattern: re.Pattern[str]) -> int | None:
    for number, line in enumerate(text.splitlines(), start=1):
        if pattern.search(line):
            return number
    return None


def add_issue(
    issues: list[PromptIssue],
    code: str,
    severity: str,
    message: str,
    suggestion: str,
    *,
    line: int | None = None,
) -> None:
    issues.append(PromptIssue(code, severity, line, message, suggestion))


def detect_modules(text: str) -> list[str]:
    checks = {
        "subject": SUBJECT_PATTERN,
        "quantity": QUANTITY_PATTERN,
        "duration": DURATION_PATTERN,
        "camera": CAMERA_PATTERN,
        "camera_end": CAMERA_END_PATTERN,
        "audio": AUDIO_PATTERN,
        "reference": REFERENCE_PATTERN,
        "reference_scope": REFERENCE_SCOPE_PATTERN,
        "lighting_color_material": LIGHT_PATTERN,
        "action_performance": ACTION_PATTERN,
        "continuity_constraints": CONTINUITY_PATTERN,
        "platform_adapter": PLATFORM_PATTERN,
    }
    return [name for name, pattern in checks.items() if pattern.search(text)]


def audit_prompt(text: str, medium: str) -> dict[str, Any]:
    issues: list[PromptIssue] = []
    stripped = text.strip()
    assumptions: list[str] = []

    if not stripped:
        add_issue(
            issues,
            "P-EMPTY",
            "error",
            "Prompt is empty.",
            "Provide the creative intent and at least one visible subject or environment.",
        )
    else:
        if not SUBJECT_PATTERN.search(stripped):
            add_issue(
                issues,
                "P-MISSING-SUBJECT",
                "error",
                "No visible subject, object, or environment is identifiable.",
                "Name what must appear and, when relevant, its exact quantity.",
            )
        if medium == "video":
            if not DURATION_PATTERN.search(stripped):
                add_issue(
                    issues,
                    "P-MISSING-DURATION",
                    "error",
                    "Video duration is not explicit.",
                    "State the total duration in seconds and keep all beats within it.",
                )
            if not CAMERA_END_PATTERN.search(stripped):
                add_issue(
                    issues,
                    "P-MISSING-CAMERA-END",
                    "error",
                    "The camera or final framing has no explicit end state.",
                    "Add camera_end or a clearly observable final frame and focus target.",
                    line=line_for(stripped, CAMERA_PATTERN),
                )
            if not AUDIO_PATTERN.search(stripped):
                add_issue(
                    issues,
                    "P-MISSING-AUDIO",
                    "error",
                    "No dialogue, ambience, effects, music, subtitle, or silence boundary is stated.",
                    "Declare the intended audio bed and explicitly include or exclude music, dialogue, and subtitles.",
                )
        if REFERENCE_PATTERN.search(stripped) and not REFERENCE_SCOPE_PATTERN.search(stripped):
            add_issue(
                issues,
                "P-REFERENCE-SCOPE",
                "warning",
                "A reference is mentioned without an inheritance boundary.",
                "State which identity, state, material, space, composition, camera, lighting, and color attributes to inherit or exclude.",
                line=line_for(stripped, REFERENCE_PATTERN),
            )
        if STILL_PATTERN.search(stripped) and SUBJECT_MOTION_PATTERN.search(stripped):
            add_issue(
                issues,
                "P-CONFLICT-MOTION",
                "error",
                "The subject is required to remain still and perform sustained movement in the same prompt.",
                "Assign the movement to a different beat or subject, or remove one of the conflicting requirements.",
                line=line_for(stripped, STILL_PATTERN),
            )
        detected_moves = [name for name, pattern in CAMERA_MOVE_PATTERNS.items() if pattern.search(stripped)]
        if (LOCKED_CAMERA_PATTERN.search(stripped) and detected_moves) or len(detected_moves) > 1:
            add_issue(
                issues,
                "P-CAMERA-CONFLICT",
                "error",
                "The prompt contains more than one incompatible primary camera instruction.",
                "Keep one primary camera move, or split the moves into timed cuts with separate camera contracts.",
                line=line_for(stripped, CAMERA_PATTERN),
            )
        total_match = TOTAL_DURATION_PATTERN.search(stripped)
        ranges = [(float(start), float(end)) for start, end in TIME_RANGE_PATTERN.findall(stripped)]
        if total_match and ranges and max(end for _, end in ranges) > float(total_match.group(1)) + 1e-9:
            add_issue(
                issues,
                "P-TIMELINE-OVERFLOW",
                "error",
                "At least one timed beat extends beyond the declared total duration.",
                "Shorten or remove beats, extend the approved duration, or split the sequence into multiple shots.",
                line=line_for(stripped, TIME_RANGE_PATTERN),
            )
        if any(len(pattern.findall(stripped)) > 1 for pattern in NEGATIVE_SYNONYM_GROUPS):
            add_issue(
                issues,
                "P-NEGATIVE-DUPLICATE",
                "warning",
                "Equivalent negative constraints are repeated.",
                "Keep one precise boundary and pair it with a positive contract for the desired result.",
            )
        if PRIVATE_PARAMETER_PATTERN.search(stripped) and not ADAPTER_SECTION_PATTERN.search(stripped):
            add_issue(
                issues,
                "P-PLATFORM-MIXED",
                "warning",
                "Provider-specific parameters appear inside the master prompt.",
                "Move seed, steps, CFG, sampler, and other private fields into a separate platform adapter.",
                line=line_for(stripped, PRIVATE_PARAMETER_PATTERN),
            )
        if EXACT_DIALOGUE_PATTERN.search(stripped) and not DIALOGUE_VISUAL_BOUNDARY_PATTERN.search(stripped):
            add_issue(
                issues,
                "P-DIALOGUE-VISUALIZATION",
                "warning",
                "Exact dialogue is present without a boundary preventing spoken content from becoming imagery.",
                "When the line mentions off-screen people, places, or past events, state that dialogue is audio only and no flashback or extra subject appears.",
                line=line_for(stripped, EXACT_DIALOGUE_PATTERN),
            )
        if len(ABSTRACT_PATTERN.findall(stripped)) >= 2 and not CONCRETE_PATTERN.search(stripped):
            add_issue(
                issues,
                "P-ABSTRACT-ONLY",
                "warning",
                "The prompt relies on abstract quality labels without observable visual or audio instructions.",
                "Translate the intent into subject, action, camera, motivated light, material, color, or sound choices.",
                line=line_for(stripped, ABSTRACT_PATTERN),
            )
        if not PLATFORM_PATTERN.search(stripped):
            assumptions.append("provider is unspecified; no provider-specific parameters were inferred")

    severity_rank = {"error": 0, "warning": 1, "info": 2}
    issues.sort(key=lambda entry: (severity_rank[entry.severity], entry.line or 0, entry.code))
    errors = sum(entry.severity == "error" for entry in issues)
    warnings = sum(entry.severity == "warning" for entry in issues)
    score = 0 if not stripped else max(0, min(100, 100 - errors * 15 - warnings * 5))
    return {
        "valid_for_review": errors == 0,
        "score": score,
        "medium": medium,
        "issues": [asdict(entry) for entry in issues],
        "detected_modules": detect_modules(stripped),
        "assumptions": assumptions,
        "network_requests": 0,
        "database_operations": 0,
    }


def read_input(source: str) -> str:
    if source == "-":
        return sys.stdin.read()
    return Path(source).expanduser().resolve().read_text(encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", help="Prompt text file or - for stdin")
    parser.add_argument("--medium", required=True, choices=["image", "video"], help="Prompt medium")
    parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON")
    return parser.parse_args()


def render_text(result: dict[str, Any]) -> str:
    lines = [
        f"{'PASS' if result['valid_for_review'] else 'FAIL'}: {result['medium']} prompt",
        f"Structural score: {result['score']}/100",
        "Detected modules: " + (", ".join(result["detected_modules"]) or "none"),
    ]
    for entry in result["issues"]:
        location = f" line {entry['line']}" if entry["line"] else ""
        lines.append(f"- [{entry['severity']}:{entry['code']}]{location} {entry['message']}")
        lines.append(f"  Fix: {entry['suggestion']}")
    for assumption in result["assumptions"]:
        lines.append(f"- [assumption] {assumption}")
    lines.append("Network requests: 0; database operations: 0")
    return "\n".join(lines)


def main() -> int:
    args = parse_args()
    try:
        text = read_input(args.source)
    except (OSError, UnicodeError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 2
    result = audit_prompt(text, args.medium)
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(render_text(result))
    return 0 if result["valid_for_review"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
