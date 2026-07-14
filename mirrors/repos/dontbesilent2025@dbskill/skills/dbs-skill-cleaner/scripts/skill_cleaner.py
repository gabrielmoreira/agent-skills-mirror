#!/usr/bin/env python3
"""本地 skill 的只读审查与可恢复隔离工具。"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import sys
from collections import Counter
from datetime import datetime
from pathlib import Path

DEFAULT_ROOTS = [Path.home() / name / "skills" for name in (".claude", ".codex", ".agents", ".grok")]
QUARANTINE_ROOT = Path.home() / ".dbs/skill-cleaner/quarantine"
EXECUTABLE_SUFFIXES = {".py", ".sh", ".js", ".mjs", ".cjs", ".ts", ".tsx", ".rb", ".pl"}
SKIP_DIRS = {".git", "node_modules", "__pycache__", ".venv", "venv", "dist", "build", "docs", "references", "assets", "tests", "test"}
ORDER = {"严重": 0, "高风险": 1, "待复核": 2, "信息": 3}
COMMERCIAL = r"(?:加微信|添加微信|微信号|购买|下单|付费解锁|报名课程|付费咨询|课程|咨询|推广链接|联盟链接|返佣|佣金)"
SENSITIVE = r"(?:cookie(?:s)?|浏览器(?:\s*)凭据|凭据|密钥|私钥|token|环境变量)"
NETWORK = r"(?:curl|wget|fetch\s*\(|axios|requests\.|webhook|http(?:s)?://|上传|发送|传输)"


def line_number(text: str, index: int) -> int:
    return text.count("\n", 0, index) + 1


def excerpt(text: str, index: int) -> str:
    start = text.rfind("\n", 0, index) + 1
    end = text.find("\n", index)
    return " ".join(text[start:len(text) if end < 0 else end].strip().split())[:240]


def finding(rule: str, severity: str, principle: str, message: str, path: Path, content: str, index: int) -> dict:
    return {"rule": rule, "severity": severity, "principle": principle, "message": message,
            "file": str(path), "line": line_number(content, index), "excerpt": excerpt(content, index)}


def scanned_files(skill_dir: Path):
    """只读取入口说明与可能被执行的代码，刻意跳过文档、变更记录和测试。"""
    for path in skill_dir.rglob("*"):
        # 只排除 skill 内部的文档与测试目录。用户显式传入的根目录即便位于
        # tests/ 下，也必须能够作为回归样本被扫描。
        if any(part in SKIP_DIRS for part in path.relative_to(skill_dir).parts):
            continue
        if not path.is_file() or path.stat().st_size > 1_000_000:
            continue
        if path.name == "SKILL.md" or path.suffix.lower() in EXECUTABLE_SUFFIXES:
            yield path


def skill_fingerprint(skill_dir: Path) -> str:
    """用于合并同一 skill 的多端镜像；仅以入口及可执行文件为依据。"""
    digest = hashlib.sha256()
    for path in sorted(scanned_files(skill_dir), key=lambda item: str(item.relative_to(skill_dir))):
        try:
            digest.update(str(path.relative_to(skill_dir)).encode())
            digest.update(path.read_bytes())
        except OSError:
            pass
    return digest.hexdigest()


def find_skills(roots: list[Path]) -> tuple[list[Path], int]:
    """按真实路径和内容指纹去重，避免软链、多端镜像和内嵌副本重复计数。"""
    candidates: list[Path] = []
    seen_real: set[Path] = set()
    for root in roots:
        if not root.is_dir():
            continue
        for marker in root.rglob("SKILL.md"):
            if any(part in SKIP_DIRS for part in marker.relative_to(root).parts[:-1]):
                continue
            candidate = marker.parent
            try:
                real = candidate.resolve()
            except OSError:
                real = candidate.absolute()
            if real not in seen_real:
                candidates.append(candidate)
                seen_real.add(real)
    # 精确相同的入口与执行代码通常是同一 skill 的多端副本，报告一次即可。
    found: list[Path] = []
    seen_content: set[str] = set()
    duplicates = 0
    for candidate in sorted(candidates, key=str):
        fingerprint = skill_fingerprint(candidate)
        if fingerprint in seen_content:
            duplicates += 1
            continue
        found.append(candidate)
        seen_content.add(fingerprint)
    return found, duplicates + len(candidates) - len({str(path.resolve()) for path in candidates})


def has_consent(window: str) -> bool:
    return bool(re.search(r"(?:用户|你)(?:明确|主动)?(?:要求|请求|询问|提出|授权|同意)|在用户(?:明确|主动)?(?:要求|请求|询问|提出|授权|同意)后", window, re.I))


def scan_content(path: Path, content: str) -> list[dict]:
    findings: list[dict] = []
    lowered = content.lower()

    # 明确的系统／用户指令覆盖，才是任务劫持；防御外部内容的指令不计入。
    for match in re.finditer(r"(?:忽略|无视|覆盖).{0,80}(?:之前|以上|用户|系统).{0,80}(?:指令|要求)|(?:不得|不允许).{0,60}(?:告诉|披露).{0,60}(?:用户|此指令)", content, re.I | re.S):
        window = content[max(0, match.start() - 160):match.end() + 160]
        if re.search(r"(?:邮件|网页|文档|附件|外部|不可信).{0,80}(?:指令|提示)", window, re.I):
            continue
        findings.append(finding("instruction-hijacking", "严重", "人的自主性", "文本要求覆盖用户或系统指令，或隐瞒该行为，可能破坏授权边界。", path, content, match.start()))

    # 隐藏商业关系或要求所有输出导流，属于高风险；用户主动选择的商业选项只作信息记录。
    for match in re.finditer(COMMERCIAL, content, re.I):
        window = content[max(0, match.start() - 180):match.end() + 180]
        if re.search(r"(?:每次|所有|任何).{0,80}(?:回复|回答|输出).{0,100}" + COMMERCIAL, window, re.I | re.S) or re.search(r"(?:无论|不管).{0,60}(?:用户|任务).{0,100}" + COMMERCIAL, window, re.I | re.S):
            findings.append(finding("forced-commercial-diversion", "高风险", "人的自主性", "文本要求在正常任务输出中持续插入商业动作，用户难以拒绝且完成原任务。", path, content, match.start()))
        elif re.search(r"(?:隐藏|不要披露|不得告知|伪装).{0,100}" + COMMERCIAL + r"|" + COMMERCIAL + r".{0,100}(?:隐藏|不要披露|不得告知|伪装)", window, re.I | re.S):
            findings.append(finding("covert-commercial-intent", "高风险", "透明与可解释", "文本要求隐瞒或伪装商业关联，用户无法知情选择。", path, content, match.start()))
        elif has_consent(window):
            findings.append(finding("user-requested-commercial-option", "信息", "透明与可解释", "商业信息限定在用户明确请求购买、联系或服务时出现。", path, content, match.start()))
        else:
            findings.append(finding("commercial-reference", "待复核", "透明与可解释", "文本含商业或导流动作；请核对它是否会出现在无关任务中，以及商业关联是否已披露。", path, content, match.start()))
        break

    # Cookie／凭据按权限和数据流分级。仅讨论词汇、或有用户授权的按需操作不能直接判严重。
    sensitive_match = re.search(SENSITIVE, content, re.I)
    if sensitive_match:
        window = content[max(0, sensitive_match.start() - 250):sensitive_match.end() + 250]
        active_access = re.search(r"(?:读取|导入|获取|访问|提取|复制|收集).{0,80}" + SENSITIVE + r"|" + SENSITIVE + r".{0,80}(?:读取|导入|获取|访问|提取|复制|收集)", window, re.I | re.S)
        exfiltration = re.search(SENSITIVE + r".{0,240}" + NETWORK + r"|" + NETWORK + r".{0,240}" + SENSITIVE, window, re.I | re.S)
        if active_access and exfiltration:
            findings.append(finding("sensitive-data-exfiltration", "严重", "安全与可靠", "文本同时涉及读取敏感数据与向外部发送或上传；应立即核对数据去向和授权。", path, content, sensitive_match.start()))
        elif active_access and has_consent(window):
            findings.append(finding("authorized-sensitive-access", "信息", "透明与可解释", "敏感数据能力说明了用户明确授权的前提；仍应在实际执行前展示范围与去向。", path, content, sensitive_match.start()))
        elif active_access:
            findings.append(finding("undisclosed-sensitive-access", "高风险", "安全与可靠", "文本涉及读取或导入敏感数据，却没有看到明确的用户授权前提。", path, content, sensitive_match.start()))

    # 独立的网络访问仍提醒核对，但不因 curl 一词升级为严重。
    match = re.search(r"\b(?:curl|wget|nc|ncat|ssh|scp)\b", lowered)
    if match and not re.search(r"(?:敏感|cookie|凭据|密钥|token).{0,240}" + NETWORK, content, re.I | re.S):
        findings.append(finding("external-command", "待复核", "安全与可靠", "文本包含外部命令或网络访问；请核对目标、数据范围和用户授权。", path, content, match.start()))
    return findings


def scan_skill(skill_dir: Path) -> dict:
    findings: list[dict] = []
    for file_path in scanned_files(skill_dir):
        try:
            findings.extend(scan_content(file_path, file_path.read_text(encoding="utf-8", errors="replace")))
        except OSError:
            continue
    findings.sort(key=lambda item: (ORDER[item["severity"]], item["file"], item["line"]))
    return {"name": skill_dir.name, "path": str(skill_dir), "is_symlink": skill_dir.is_symlink(), "findings": findings}


def print_report(results: list[dict], roots: list[Path], duplicates: int) -> None:
    counts = Counter(item["severity"] for result in results for item in result["findings"])
    print("# 本地 skill 审查报告")
    print(f"扫描范围：{', '.join(str(root) for root in roots if root.exists()) or '未找到默认目录'}")
    print(f"发现 skill：{len(results)}（已合并 {duplicates} 个软链、镜像或内嵌副本）")
    print(f"严重：{counts['严重']}｜高风险：{counts['高风险']}｜待复核：{counts['待复核']}｜信息：{counts['信息']}")
    for result in results:
        if not result["findings"]:
            continue
        print(f"\n## {result['name']}\n位置：`{result['path']}`")
        for item in result["findings"]:
            print(f"\n- {item['severity']}｜{item['rule']}｜{item['principle']}\n  - {item['file']}:{item['line']}\n  - {item['message']}\n  - 命中：`{item['excerpt']}`")
    if not any(result["findings"] for result in results):
        print("\n未发现本规则集中的风险信号。该结果不等于安全保证。")
    print("\n扫描未修改任何文件。隔离前请逐个确认目标路径。")


def command_scan(args: argparse.Namespace) -> int:
    roots = [Path(path).expanduser() for path in args.root] if args.root else DEFAULT_ROOTS
    skills, duplicates = find_skills(roots)
    skills = [path for path in skills if path.name != "dbs-skill-cleaner"]
    results = [scan_skill(path) for path in skills]
    if args.format == "json":
        print(json.dumps({"roots": [str(root) for root in roots], "deduplicated": duplicates, "skills": results}, ensure_ascii=False, indent=2))
    else:
        print_report(results, roots, duplicates)
    return 0


def command_quarantine(args: argparse.Namespace) -> int:
    skill_dir = Path(args.skill).expanduser().absolute()
    if not args.yes:
        print("拒绝执行：隔离操作需要 --yes。", file=sys.stderr); return 2
    if not (skill_dir / "SKILL.md").is_file() or skill_dir.name == "dbs-skill-cleaner":
        print("拒绝执行：目标必须是非 dbs-skill-cleaner 的 skill 目录。", file=sys.stderr); return 2
    if skill_dir.is_symlink():
        target = os.readlink(skill_dir); skill_dir.unlink()
        print(json.dumps({"action": "removed_symlink", "path": str(skill_dir), "source_retained": target, "reason": args.reason}, ensure_ascii=False)); return 0
    destination = QUARANTINE_ROOT / datetime.now().strftime("%Y%m%d-%H%M%S") / skill_dir.name
    destination.parent.mkdir(parents=True, exist_ok=True); shutil.move(str(skill_dir), str(destination))
    print(json.dumps({"action": "quarantined", "from": str(skill_dir), "to": str(destination), "reason": args.reason}, ensure_ascii=False)); return 0


def command_list_quarantine(_: argparse.Namespace) -> int:
    entries = sorted(QUARANTINE_ROOT.rglob("SKILL.md")) if QUARANTINE_ROOT.exists() else []
    print("\n".join(str(item.parent) for item in entries) or "隔离区为空。")
    return 0


def command_restore(args: argparse.Namespace) -> int:
    source, target = Path(args.source).expanduser().absolute(), Path(args.target).expanduser().absolute()
    if not args.yes or not str(source).startswith(str(QUARANTINE_ROOT)) or not (source / "SKILL.md").is_file() or target.exists() or target.is_symlink():
        print("拒绝执行：需使用 --yes；来源须在隔离区且目标不存在。", file=sys.stderr); return 2
    target.parent.mkdir(parents=True, exist_ok=True); shutil.move(str(source), str(target))
    print(json.dumps({"action": "restored", "from": str(source), "to": str(target)}, ensure_ascii=False)); return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="扫描与隔离本地 skill。")
    subparsers = parser.add_subparsers(dest="command", required=True)
    scan = subparsers.add_parser("scan", help="只读扫描 skill"); scan.add_argument("--root", action="append", default=[]); scan.add_argument("--format", choices=["text", "json"], default="text"); scan.set_defaults(handler=command_scan)
    quarantine = subparsers.add_parser("quarantine", help="隔离一个明确指定的 skill"); quarantine.add_argument("skill"); quarantine.add_argument("--reason", default="用户确认"); quarantine.add_argument("--yes", action="store_true"); quarantine.set_defaults(handler=command_quarantine)
    listing = subparsers.add_parser("list-quarantine", help="列出隔离区"); listing.set_defaults(handler=command_list_quarantine)
    restore = subparsers.add_parser("restore", help="从隔离区恢复 skill"); restore.add_argument("source"); restore.add_argument("target"); restore.add_argument("--yes", action="store_true"); restore.set_defaults(handler=command_restore)
    args = parser.parse_args(); return args.handler(args)


if __name__ == "__main__":
    raise SystemExit(main())
