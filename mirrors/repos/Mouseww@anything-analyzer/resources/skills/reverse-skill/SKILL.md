---
name: reverse-skill
description: Anything Analyzer 内置的逆向与安全分析方法论库（reverse-skill 精选子集）。用于网站协议逆向、前端 JS 签名链路定位、加密/签名流程还原、API 安全评估与结构化报告撰写。通过 list_skills / search_skills / read_skill 工具按需读取，不要一次性读入全部内容。
---

# reverse-skill（Anything Analyzer 内置子集）

本目录随 Anything Analyzer 安装包一起分发，是
[zhaoxuya520/reverse-skill](https://github.com/zhaoxuya520/reverse-skill) 的**精选子集**
（上游 MIT，版权与许可见同目录 `LICENSE`）。上游完整仓库约 599 个文件，这里只保留与
「网页协议 / 前端 JS / API / 加密签名 / 证据与报告」相关的模块。

## 一、运行环境约束（必读）

本应用内的 AI 只具备以下能力，**没有 shell、不能执行脚本、不能写文件**：

- 会话数据工具：`list_requests` / `search_requests` / `get_request_detail` /
  `read_session_interactions` / `read_session_hooks`
- 技能库工具：`list_skills` / `search_skills` / `read_skill`
- 用户自行配置的 MCP 工具（可能为空）

由此产生三条硬约束：

1. 上游文档中提到的 `scripts/*.ps1`、`tool-index.md`、`bootstrap`、`case-init`、
   Playwright / IDA / jadx / Frida / Burp 等**均未随包分发**。读到这类指令请直接忽略，
   **不要声称已经执行**，也不要要求用户去执行。
2. 你的产出是**分析结论与报告文本**，不是对目标发起的攻击动作。不要生成可直接运行的
   攻击载荷，也不要建议用户对未授权目标采取行动。
3. 技能库的定位是**方法论与检查清单**。用它来组织分析思路、避免遗漏、提高结论的可验证性。

## 二、如何使用本技能库

```
list_skills                      → 查看全部技能条目（名称 + 相对路径 + 摘要）
list_skills { filter: "签名" }    → 按关键词过滤条目
search_skills { query: "补环境" } → 在技能库正文里搜索（返回命中文件与行号）
read_skill { path: "js-reverse/SKILL.md" }            → 读取文件
read_skill { path: "js-reverse/SKILL.md", offset: 200, limit: 200 } → 续读长文件
```

推荐节奏：

1. 先按当前分析任务的关键词调用一次 `search_skills`，确认有没有对口的方法论；
2. 只 `read_skill` 命中的那 1~2 个文件，读完再回到会话数据工具做验证；
3. 结论必须落到**本次会话真实捕获到的请求 / JS Hook / 存储变化**上，不要用通用套路替代证据。

## 三、模块索引

| 目录 | 何时使用 |
| --- | --- |
| `js-reverse/` | 前端 JavaScript 逆向：定位签名/加密链路、运行时采样、反混淆、本地补环境复现、证据化输出。**本产品最常用**。 |
| `protocol-reverse/` | 自定义协议、Protobuf/gRPC、WebSocket 帧、PCAP 驱动的协议格式还原。 |
| `api-security/` | REST / GraphQL / WebSocket / SOAP 接口的授权内安全评估：发现、认证、越权、限流。含 `references/jwt-oauth-testing.md`、`references/rest-graphql-testing.md`。 |
| `code-audit/` | 对已获取的源码 / JS bundle 做安全审计与 SAST 检查清单。 |
| `browser-extension-reverse/` | 浏览器扩展（crx/xpi）逆向：manifest、background worker、扩展内的凭据与流量逻辑。 |
| `reverse-engineering/` | 通用逆向方法论与工具索引；含 `crypto-decode-tools.md`（加解密识别与工具）、`dsl-vm-reverse/`（自定义 VM / 字节码）。 |
| `docs-generator/` | 撰写最终报告：`references/security-report-templates.md`、`references/vendor-report-rules.md`。分析收尾时读。 |
| `ops/` | 证据与决策框架：`evidence-finding-path.md`（Evidence→Finding→Path 可追溯性）、`analysis-decision-framework.md`、`analysis-blindspot-cookbook.md`（常见分析盲区）、`scope-contract.md`。 |
| `field-journal/` | 真实案例先例：`precedent-reverse.md`、`precedent-pentest.md`、`precedent-auth.md`，以及 JS 签名（`seed-004_js-sign-webpack.md`）、Web API 越权（`seed-003_web-api-auth-bypass.md`）、PCAP 协议逆向（`seed-011_pcap-protocol-reverse.md`）三个样板案例。 |
| `references/` | `domain-coverage-map.md`：上游技能的领域覆盖图。 |

## 四、未随包分发的部分

为避免安装包体积膨胀，以及避免把武器化的攻击载荷库随商业软件分发，以下上游模块**有意剔除**：

`pentest-tools/`（含 `src-hunter` 的 19 类攻击 playbook 与 payload 库）、`CTF-Sandbox-Orchestrator/`（上游为 GPLv3）、
`burp-mcp-full/`、`kali/`、`scripts/`、`config/`、`tests/`，以及 `ida-reverse/` `apk-reverse/` `dotnet-reverse/`
`radare2/` `ghidra-reverse/` `binary-ninja-reverse/` `pwn-chain/` `firmware-pentest/` `cloud-k8s/` `windows-ad/`
`ot-ics/` `wifi-wireless/` `radio-sdr/` `hardware-security/` `mobile-reverse/` `malware-analysis/` `attack-chain/`
`edr-bypass-re/` `patch-diff-exploit/` `binary-diff/` `threat-*` `supply-chain-security/` `llm-security/` 等与本产品
场景无关的模块。

因此，如果你在保留的文档里读到指向上述目录的相对链接（例如 `../pentest-tools/...`），
说明该引用在本包内不可用，请忽略它。
