#!/usr/bin/env python3
"""Offline, allowlisted HTML projection of diagnostic snapshots. No collectors."""
import argparse
from datetime import datetime, timezone
from html import escape
import json
import re

from traffic_policy import policy_projection
import sys

from guardian import GuardianError, PROXY_SUMMARY, load_json, reject_unknown_report_members, save_new
from probe_evidence import NetworkReportError, project_network

STATES = {
    "verified": ("已验证", "network_check.py 实测通过"),
    "error": ("发现问题", "报告存在错误、冲突或执行失败"),
    "unknown": ("未知", "证据不足、缺失或已过期"),
    "not_run": ("未执行", "当前报告格式没有此项实际检测证据"),
    "authorization_needed": ("待授权", "先核实目标与操作范围，再取得本次授权"),
}
GROUPS = (("system", "系统与目标", "ENV-01", "S"),
          ("proxy", "代理配置 / 入口", "ENV-02", "P"),
          ("tun", "TUN 声明与接管", "ENV-02", "P"),
          ("ipv4", "IPv4 请求出口", "ENV-03", None),
          ("ipv6", "IPv6 分层覆盖", "ENV-04", None),
          ("dns", "DNS 配置与解析路径", "ENV-04", None),
          ("dns_leak", "DNS 泄露证据", "ENV-04", None),
          ("udp", "UDP 可达与业务范围", "ENV-04", None),
          ("stun", "独立 STUN 映射", "ENV-04", None),
          ("browser", "浏览器 / WebRTC", "ENV-05", None),
          ("failure", "代理失效 / 防直连", "ENV-10", None))
COVERAGE = {
    "system": "目标设备、用户、命名空间；目标绑定另外核实",
    "proxy": "系统代理、显式 HTTP/mixed 入口、浏览器路径分别核实；端口要实测可用",
    "tun": "TUN 开关、IPv4/IPv6 路由、DNS 与 UDP 接管分别核实；开启后要实测覆盖",
    "ipv4": "需区分系统继承、显式代理、TUN 与浏览器的 HTTPS IPv4 样本；这里看的是网络路径",
    "ipv6": "分别记录本机接口、节点外层通道、代理到目标、浏览器 ICE；AAAA 为空或超时只是线索，阻断要用 IPv6 实测确认",
    "dns": "系统、浏览器 DoH、Mihomo、引导解析与实际解析器连接分别核实；Fake-IP 差异不自动判错",
    "dns_leak": "判泄露要把批准的查询、解析目标与实际连接对上；只看解析器设置或地区差异不够",
    "udp": "区分应用 UDP 与代理隧道外层 UDP；其他目的地、端口和协议另测",
    "stun": "独立 Binding 事务的地址族、映射分类、路径与时间须有证据；不展示映射 IP，浏览器样本另测",
    "browser": "所选浏览器/Profile 的政策、HTTPS 路径、ICE host/srflx/relay 与 IPv6 分别核实；没有候选时换方式再测",
    "failure": "代理失效后的行为、程序/子进程范围与恢复要单独演练；防直连以停核心演练为准",
}
FACT_IDS = {"S%02d" % n for n in range(1, 17)} | {"P%02d" % n for n in range(1, 25)}
ERROR_CODES = frozenset({"PROXY_PORT_ASSOCIATION_CONFLICT", "COLLECTOR_INTERNAL_FAILURE",
    "INPUT_OR_RESPONSE_INVALID", "TARGET_USER_CONTEXT_MISMATCH", "SNAPSHOT_CHANGED_DURING_AUDIT",
    "OS_QUERY_FAILED", "BUDGET_EXCEEDED", "CONTROLLER_AUTH_FAILED"})
AUTH_CODES = frozenset({"AUTHORIZATION_MISSING", "PERMISSION_DENIED", "PRECONTACT_ACTION_REJECTED"})
CSS = """
:root{color-scheme:light;--ink:#20242a;--muted:#626970;--line:#e2e4e7}
*{box-sizing:border-box}body{margin:0;background:#fff;color:var(--ink);font:14px/1.5 system-ui,-apple-system,sans-serif}
main{max-width:960px;margin:0 auto;padding:28px 28px 20px}header{display:flex;align-items:baseline;gap:12px;flex-wrap:wrap;margin-bottom:8px}
h1{font-size:20px;font-weight:600;line-height:1.4;margin:0}p{margin:8px 0}.brand{color:var(--muted);font-size:12px;margin-left:auto}
.sample{font-size:11px;border:1px solid #c9cdd2;padding:1px 5px;color:#555b62}.meta,footer{font-size:12px;color:var(--muted)}.meta{margin:0 0 22px}
table{width:100%;border-collapse:collapse;table-layout:fixed}caption{text-align:left;font-size:13px;font-weight:600;padding:0 0 8px}
col.item{width:25%}col.state{width:17%}th,td{text-align:left;vertical-align:top;padding:11px 12px;border-bottom:1px solid var(--line);overflow-wrap:anywhere}
thead th{padding-top:8px;padding-bottom:8px;background:#f6f7f8;color:var(--muted);font-size:12px;font-weight:500}tbody th{font-weight:500}th:first-child{padding-left:10px}
.badge{font-size:13px;color:#59616a;white-space:nowrap}.badge.error{color:#a12622}.badge.authorization_needed{color:#855500}.badge.verified{color:#256347}
summary{cursor:pointer;color:var(--muted)}summary:focus-visible{outline:2px solid #355d83;outline-offset:4px}details p{font-size:12px;color:var(--muted);margin:8px 0 0}td details[open]{padding-bottom:4px}
.report-details{border-bottom:1px solid var(--line);padding:14px 0}.report-details>summary{font-size:12px}.authorization{font-size:12px;color:var(--muted);margin:16px 0 0}footer{margin-top:12px}
@media(max-width:520px){main{padding:18px 12px}header{gap:8px}.brand{width:100%;margin-left:0}.meta{margin-bottom:18px}h1{font-size:18px}col.item{width:28%}col.state{width:22%}th,td{padding:10px 6px}tbody th,td{font-size:13px}.badge{font-size:12px}}
@media print{main{max-width:none;padding:0}tr{break-inside:avoid}}
"""


def timestamp(value):
    """Never echo unparsed input, including malformed timestamps or timezone labels."""
    if not isinstance(value, str) or len(value) > 40:
        return None
    try:
        result = datetime.fromisoformat(value.replace("Z", "+00:00"))
        return result.astimezone(timezone.utc) if result.tzinfo else None
    except (ValueError, OverflowError):
        return None


def fresh(value, now):
    parsed = timestamp(value)
    return parsed is not None and 0 <= (now - parsed).total_seconds() <= 86400


def safe_facts(facts):
    """Finite values and true JSON booleans only; never interpolate raw values."""
    details = []
    for fact in facts:
        field, value = fact.get("id"), fact.get("value")
        if field == "S01" and isinstance(value, str) and value in {"macos", "windows"}:
            details.append("系统：" + {"macos": "macOS", "windows": "Windows"}[value])
        elif field == "S04" and isinstance(value, str) and value in {"arm64", "aarch64", "x86_64", "amd64", "x64", "x86"}:
            label = "采集进程架构：" if fact.get('coverage') == 'current_process_os' else "架构声明："
            details.append(label + value)
        elif field == "P06" and isinstance(value, dict) and type(value.get("enabled")) is bool:
            details.append("系统代理声明：" + ("开启" if value["enabled"] else "关闭") + "（实际路径另测）")
        elif (field == 'P06' and type(value) is str and value.startswith('http=')
              and re.fullmatch(PROXY_SUMMARY, value)):
            flags = dict(item.split('=') for item in value.split(';'))
            labels = {'enabled': '开启', 'disabled': '关闭', 'unknown': '未知'}
            details.append('系统代理默认开关：' + ' / '.join(
                name + ' ' + labels[flags[key]] for key, name in
                (('http', 'HTTP'), ('https', 'HTTPS'), ('socks', 'SOCKS'), ('pac', 'PAC'), ('wpad', 'WPAD')))
                + '（实际路径另测）')
            details.append('作用域代理：' + ('存在，详情未采集' if flags['scoped'] == 'present' else '未报告，详情未采集'))
        elif field == "P12" and type(value) is bool:
            details.append("TUN 声明：" + ("开启" if value else "关闭") + "（接管另测）")
        elif field == "P11" and isinstance(value, str) and value in {"rule", "global", "direct"}:
            details.append("代理模式声明：" + value)
    return list(dict.fromkeys(details))


def project(report, now=None, network_report=None):
    """Project only enums/counts/dates. No arbitrary text, values or identifiers survive."""
    now = now or datetime.now(timezone.utc)
    if not isinstance(report, dict) or report.get("schema_version") not in ("guardian-report/0.1", "env-inventory/0.2"):
        raise GuardianError("DASHBOARD_REPORT_UNSUPPORTED")
    reject_unknown_report_members(report, "DASHBOARD_REPORT_INVALID")
    facts, findings = report.get("facts", []), report.get("findings", [])
    if not isinstance(facts, list) or not isinstance(findings, list) or len(facts) > 1000 or len(findings) > 1000:
        raise GuardianError("DASHBOARD_REPORT_INVALID")
    if any(not isinstance(x, dict) for x in facts + findings):
        raise GuardianError("DASHBOARD_REPORT_INVALID")
    ids = [fact.get("id") for fact in facts]
    if any(not isinstance(field, str) for field in ids) or len(set(ids)) != len(ids):
        raise GuardianError("DASHBOARD_REPORT_INVALID")
    snapshot = report.get("snapshot", {})
    if not isinstance(snapshot, dict):
        raise GuardianError("DASHBOARD_REPORT_INVALID")
    observed = timestamp(snapshot.get("observed_at"))
    snapshot_fresh = fresh(snapshot.get("observed_at"), now)
    cards = []
    for key, title, module, prefix in GROUPS:
        selected = [f for f in facts if isinstance(f.get("id"), str) and
                    prefix is not None and f["id"] in FACT_IDS and f["id"].startswith(prefix)]
        if key == "tun":
            selected = [f for f in selected if f.get("id") == "P12"]
        current = sum(f.get("state") == "observed" and fresh(f.get("observed_at"), now) for f in selected)
        module_findings = [f for f in findings if f.get("module_id") == module]
        codes = [f.get("code") for f in module_findings if isinstance(f.get("code"), str)]
        if key == "tun":
            codes = []  # Proxy port findings do not establish TUN failure.
        state = "unknown" if prefix else "not_run"
        if any(c in ERROR_CODES for c in codes) or any(f.get("state") == "conflict" for f in selected):
            state = "error"
        elif any(c in AUTH_CODES for c in codes) or any(f.get("state") == "blocked" for f in selected):
            state = "authorization_needed"
        # This schema has no scoped live probe or acceptance contract. Never infer verified.
        cards.append({"key": key, "title": title, "module": module, "state": state,
                      "observed": current if snapshot_fresh else 0, "total": len(selected),
                      "evidence_at": min((timestamp(f.get("observed_at")) for f in selected if f.get("state") == "observed" and fresh(f.get("observed_at"), now)), default=None) if snapshot_fresh else None,
                      "details": safe_facts([f for f in selected if snapshot_fresh and f.get("state") == "observed" and fresh(f.get("observed_at"), now)])})
    measured = {}
    if network_report is not None:
        try:
            measured = project_network(network_report, now)
        except NetworkReportError:
            raise GuardianError("INPUT_OR_RESPONSE_INVALID") from None
    for card in cards:
        card["measured"] = measured.get(card["key"])
        if card["measured"]:
            card["state"] = card["measured"]["state"]
            card["details"] = [card["measured"]["text"]] + card["details"]
            card["evidence_at"] = card["measured"]["checked_at"]
    execution = report.get("execution_status")
    execution_text = {"completed": "报告生成完成（结论看各卡片）", "failed": "报告执行失败",
                      "blocked": "报告执行受阻", "interrupted": "报告执行中断"}.get(execution if isinstance(execution, str) else "", "执行状态未知")
    return {"traffic_policy": policy_projection(), "cards": cards, "observed_at": observed.isoformat() if observed else "未知",
            "generated_at": now.isoformat(), "snapshot_fresh": snapshot_fresh,
            "synthetic": report.get("record_kind") == "synthetic_example", "execution": execution_text,
            "overall": "error" if execution == "failed" or any(c["state"] == "error" for c in cards) else "unknown",
            "network": bool(measured)}


def badge(state):
    return '<span class="badge %s" title="%s">%s</span>' % (escape(state, quote=True), escape(state), escape(STATES[state][0]))


def render(report, now=None, network_report=None):
    view = project(report, now, network_report)
    by_key = {card["key"]: card for card in view["cards"]}
    labels = {"ipv4": "IPv4", "ipv6": "IPv6", "dns_leak": "DNS 泄露", "udp": "UDP",
              "stun": "STUN", "browser": "WebRTC", "tun": "TUN", "dns": "DNS 配置 / 查询",
              "system": "系统与目标", "proxy": "代理入口", "failure": "失效 / 防直连"}
    order = ("ipv4", "ipv6", "dns_leak", "udp", "stun", "browser", "tun", "dns", "system", "proxy", "failure")
    rows = []
    for key in order:
        card = by_key[key]
        limitation = COVERAGE[key]
        evidence_at = card["evidence_at"].isoformat() if card["evidence_at"] else "未知 / 未执行"
        if card["details"]:
            fact = "；".join(card["details"])
        elif card["state"] == "error":
            fact = "报告存在错误或冲突"
        elif card["state"] == "authorization_needed":
            fact = "缺少授权或权限"
        else:
            fact = "无检测证据" if card["state"] == "not_run" else "证据不足"
        evidence = "当前有效观察字段：%d / %d。证据最早时间（UTC）：%s。路径：未知 / 未独立绑定。" % (card["observed"], card["total"], evidence_at)
        if card["measured"]:
            evidence = "network_check.py 实测（UTC %s）。" % card["measured"]["checked_at"].isoformat()
        rows.append('<tr data-check="%s"><th scope="row">%s</th><td>%s</td><td><details><summary>%s</summary><p>%s</p><p>%s</p><p>%s · 状态：%s</p></details></td></tr>' %
                    (key, escape(labels[key]), badge(card["state"]), escape(fact), escape(evidence), escape(limitation), escape(card["module"]), escape(card["state"])))
    sample = '<span class="sample">合成演示</span>' if view["synthetic"] else '<span class="sample">离线快照</span>'
    freshness = "" if view["snapshot_fresh"] else " · 时间缺失、过期或无效"
    execution_note = "" if report.get("execution_status") == "completed" else " · " + view["execution"]
    sample_note = "合成示例，不是你的设备检测结果。" if view["synthetic"] else "输入来源和目标未经独立核验。"
    return '''<!doctype html>
<html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<meta http-equiv="Content-Security-Policy" content="default-src 'none'; style-src 'unsafe-inline'; base-uri 'none'; form-action 'none'">
<meta name="referrer" content="no-referrer"><title>Claude-Guardian · 环境状态</title><style>''' + CSS + '''</style></head><body><main>
<header><h1>环境状态</h1>''' + sample + '''<span class="brand">Claude-Guardian</span></header>
<p class="meta">快照（UTC）：''' + escape(view["observed_at"]) + escape(freshness) + escape(execution_note) + '''</p>
<p>当前策略：IPv4_ONLY，整机只走 IPv4，IPv6 关闭，禁止IPv6回退；结果见下方各项。</p>
<table><caption>检查结果</caption><colgroup><col class="item"><col class="state"><col></colgroup><thead><tr><th scope="col">项目</th><th scope="col">状态</th><th scope="col">关键事实 · 展开查看证据</th></tr></thead><tbody>''' + ''.join(rows) + '''</tbody></table>
<details class="report-details"><summary>报告信息与限制</summary><p>''' + escape(sample_note) + escape(view["execution"]) + '''。</p><p>页面生成（UTC）：''' + escape(view["generated_at"]) + '''。快照及字段有效期为 24 小时；时钟未经外部核验，重新打开不会刷新。</p><p>已验证：network_check.py 在 24 小时内实测通过。未知：证据还不够或结果过期。未执行：还没检测。</p><p>仅显示白名单摘要；不含原始地址、路径或设备标识。支持 guardian-report/0.1 与 env-inventory/0.2；可附加 network_check.py 的报告（--network）。完整证据看本地原始报告，分享前人工复核。</p></details>
<p class="authorization">操作权限：联网探测、修改配置或接触 Claude 须另行授权。</p>
<footer>静态快照 · 无自动检测</footer>
</main></body></html>\n'''


def main(argv=None):
    parser = argparse.ArgumentParser(description="Generate a private offline HTML status snapshot; no probes or auto-open.")
    parser.add_argument("--input", required=True, help="Explicit local guardian-report/0.1 or env-inventory/0.2 JSON file")
    parser.add_argument("--output", required=True, help="New local HTML file; never overwrite")
    parser.add_argument("--network", help="Optional network_check.py report (guardian-network-check/0.1) to fill the network cards")
    args = parser.parse_args(argv)
    try:
        save_new(args.output, render(load_json(args.input), network_report=load_json(args.network) if args.network else None))
    except KeyboardInterrupt:
        sys.stderr.write("DASHBOARD_CANCELLED\n")
        return 3
    except GuardianError as error:
        sys.stderr.write(error.code + "\n")
        return error.exit_code
    except Exception:
        sys.stderr.write("DASHBOARD_INTERNAL_FAILURE\n")
        return 4
    sys.stdout.write("DASHBOARD_SAVED: open the requested local HTML file manually; generation is not environment verification.\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
