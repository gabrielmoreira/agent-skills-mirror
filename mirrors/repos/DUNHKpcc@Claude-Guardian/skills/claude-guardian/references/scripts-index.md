# 脚本索引

`scripts/` 下每个脚本一行：它是什么、Agent 什么时候用、对应说明在哪。**入口**可以直接运行（多数只读、离线）；**库**由入口或宿主导入，不直接运行。执行改动按[分级授权](authorization-tiers.md)；真机验证过哪些见仓库的 CHANGELOG 和 ADR-039。

## 访谈与评估

| 脚本 | 类型 | 用途 | 说明 |
| --- | --- | --- | --- |
| `interview_cli.py` | 入口 | 离线访谈：保存、续接、评估，不联网 | [intake.md](intake.md) |
| `interview_flow.py` | 库 | 访谈状态机、主题路由 `references_for_topics`、交接待办、目标能力记录、`assessment` 和 `required_references`（本次必附资料）、`authorization` 分级授权记录函数 | [intake.md](intake.md)、[authorization-tiers.md](authorization-tiers.md) |
| `environment_entry.py` | 库 | 环境入口资格（路线选定、PC0） | [agent-remediation.md](host-libraries.md#environment-entry) |

## 检查与报告（只读）

| 脚本 | 类型 | 用途 | 说明 |
| --- | --- | --- | --- |
| `guardian.py` | 入口 | 本机 macOS / Windows 基础诊断预览 | [SKILL.md](../SKILL.md)、[network-and-remedies.md](network-and-remedies.md) |
| `inventory_cli.py` | 入口 | Clash 配置的只读盘点（`capabilities`、`static-audit`） | [network-and-remedies.md](network-and-remedies.md) |
| `clash_inventory.py` | 库 | Clash 配置静态盘点 | [network-and-remedies.md](network-and-remedies.md) |
| `status_dashboard.py` | 入口 | 把 `guardian.py` 报告做成离线 HTML 面板；`--network` 附上 `network_check.py` 的报告，网络卡片显示实测结果 | [agent-remediation.md](agent-remediation.md) |
| `probe_evidence.py` | 库 | 把 `network_check.py` 报告投影到面板卡片 | 同上 |
| `update_check.py` | 入口 | 每次使用前查 Skill 更新：按 git blob 哈希比较本地文件和 GitHub main 分支，列出不同、远端新增、本地独有的文件和最近几条更新；只读，只连 `api.github.com` | [skill-update.md](skill-update.md) |
| `network_check.py` | 入口 | Windows 缺 Python 必须先补齐（[S10 第十节](../sources/S10-windows-deployment-sanitized.md#network-evidence)、[能力核实](agent-remediation.md#capability-checkpoint)），统一用本工具；网络基础检测：默认路由是否走 TUN、IPv4 出口（国家与 ASN，不回显 IP）、经本地代理端口的出口、IPv6、DNS 泄露（含 fake-ip）、UDP（STUN）、可选故障演练；macOS、Windows、Linux；`--evidence-output` 交给 `egress_verifier.py` | [whole-machine-ipv4.md](whole-machine-ipv4.md#4-取证agent-实际执行不替用户编造) |
| `egress_verifier.py` | 入口 | 整机只走 IPv4 出口的判定（`check --input`），macOS、Windows、Linux | [whole-machine-ipv4.md](whole-machine-ipv4.md) |

## 统一防直连开关

| 脚本 | 类型 | 用途 | 说明 |
| --- | --- | --- | --- |
| `killswitch.py` | 入口 | 已部署防护的 on/off/status/uninstall、Windows snapshot、本机确认与状态读回 | [killswitch-switch.md](killswitch-switch.md) |
| `killswitch_ui.py` | 入口／库 | 无系统改动演示、本机 GUI、桌面入口生成 | 同上 |

随包资源：`assets/killswitch/windows-switch.ps1`、`assets/killswitch/config.example.json`、`assets/killswitch/switch.html`、`assets/killswitch/switch.css`、`assets/killswitch/switch.js`、`assets/killswitch/icon.svg`、`assets/killswitch/icon.png`、`assets/killswitch/icon.ico`、`assets/killswitch/icon.icns`。全部通过同一使用指引按需读取。

## 网络检测的其他部分

| 脚本 | 类型 | 用途 | 说明 |
| --- | --- | --- | --- |
| `stun_probe.py` | 库 | STUN 请求与响应解析，`network_check.py` 的 UDP 检测用 | [whole-machine-ipv4.md](whole-machine-ipv4.md) |
| `serve_webrtc.py` | 入口 | 在本机回环临时提供 WebRTC 探测页（`assets/webrtc-probe.html`） | [SKILL.md](../SKILL.md) |

## 修复计划与规则（离线，不写入）

| 脚本 | 类型 | 用途 | 说明 |
| --- | --- | --- | --- |
| `agent_remediation.py` | 入口 | 根据报告选择修复动作（`select`），不授予执行权 | [agent-remediation.md](agent-remediation.md) |
| `remedy_plans.py`、`traffic_policy.py` | 库 | 语义修复计划、IPv4_ONLY 条件计划（旧目标范围契约） | [agent-remediation.md](agent-remediation.md#ipv4-only-policy) |
| `config_edit_plan.py`、`rules_extension_plan.py`、`agent_rules_task.py` | 库 | 规则候选与单条 rules 扩展任务 | [agent-rules-task.md](agent-rules-task.md) |
| `clash_verge_258.py` | 库 | Clash Verge Rev 2.5.8 归属与链接校验 | [agent-rules-task.md](agent-rules-task.md) |

## 写入与恢复（有事务和备份）

| 脚本 | 类型 | 用途 | 说明 |
| --- | --- | --- | --- |
| `repair_cli.py` | 入口 | 修复预检与计划（`plan`、`execute`）；不要加 `-I` | [agent-remediation.md](agent-remediation.md#mac-修复链clash-verge-rev-258-的-rules-扩展) |
| `repair_execution.py` | 库 | 修复写入传输，原生门禁只放行 macOS Clash Verge Rev 2.5.8 的 rules 扩展 | 同上 |
| `native_clash_verge_mac.py` | 库 | 上述门禁的固定 macOS 适配器（应用须已退出，前后复查） | 同上 |
| `transactions.py` | 库 | 精确文件事务（POSIX） | [agent-remediation.md](agent-remediation.md) |
| `recovery_cli.py` | 入口 | 独立的回执检查与恢复（`inspect`、`preview`、`rollback`、`reconcile`） | [agent-remediation.md](agent-remediation.md) |

## 清理（C 档）

| 脚本 | 类型 | 用途 | 说明 |
| --- | --- | --- | --- |
| `cleanup_cli.py`、`cleanup_transactions.py` | 入口、库 | C5 清理的分发器与隔离、对账、恢复核心；单独运行没有宿主 | [cleanup-cli-usage.md](cleanup-cli-usage.md) |
| `native_cleanup_mac.py` | 入口 | macOS 内置宿主：备份、计划、隔离、对账、还原，终端输入确认短语 | [cleanup-cli-usage.md](cleanup-cli-usage.md)、[S06](../sources/S06-macos-cleanup-sanitized.md) |
| `native_claude_state_mac.py` | 入口 | macOS 钥匙串退出登录、`CLAUDE_CODE_SIMPLE`、用户指定时区 | [cleanup-cli-usage.md](cleanup-cli-usage.md) |

Windows、Linux 没有清理脚本，按 [windows-cleanup.md](windows-cleanup.md)、[linux-cleanup.md](linux-cleanup.md) 分步做。

## 随包脚本资产（`assets/`）

| 文件 | 用途 | 说明 |
| --- | --- | --- |
| `assets/mac-killswitch/guardian-pf-killswitch.sh` | Mac 本机／客机 PF fail-closed 防火墙（已验收，2026-11-09） | [local-firewall-prompts.md](local-firewall-prompts.md) |
| `assets/vm-killswitch/install-flclash-killswitch.sh` | VM 客机 fail-closed 防火墙 | [vm-guidance.md](vm-guidance.md) |
| `assets/vm-killswitch/install-flclash-tun.sh` | VM 客机安装 FlClash TUN | [vm-guidance.md](vm-guidance.md) |
| `assets/vm-killswitch/enable-guest-ssh.sh` | 开客机 SSH（限管理来源） | [vm-guidance.md](vm-guidance.md) |
| `assets/remote-hardening/install-reverse-tunnel.sh` | 进阶路线：目标机 systemd 常驻反向 SSH 隧道（密钥由用户传入） | [advanced-route.md](advanced-route.md) |
| `assets/remote-hardening/flclash-crash-heal.sh` | FlClash 崩溃后清路由残留 + core 看门狗（含 `install`） | [advanced-route.md](advanced-route.md)、[vm-guidance.md](vm-guidance.md) |
| `assets/vps-firewall/vps-guard.sh` | VPS 入站防火墙（带 180 秒保险丝） | [vps-guidance.md](vps-guidance.md) |
| `assets/webrtc-probe.html` | 本地 WebRTC 探测页 | [SKILL.md](../SKILL.md) |

Windows 多步网络修改的独立执行入口：[`windows-network-transaction.ps1`](../assets/killswitch/windows-network-transaction.ps1)，支持 Start／Status／Commit／Recover；步骤协议、SYSTEM 上下文、私有快照与限制见 [网络事务说明](windows-network-transaction.md)。不是任意网络修改的自动适配器。
