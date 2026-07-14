---
name: dbs-skill-cleaner
description: |
  本地 skill 清理器。扫描 Claude Code、Codex、Grok、通用 Agents 及指定目录中的 skill，识别广告导流、隐蔽商业意图、任务劫持、可疑外部调用、敏感数据读取等违背用户授权的内容；默认只出报告，经用户确认后隔离问题 skill。
  触发方式：/dbs-skill-cleaner、/清理 skill、/检查 skill、「扫描本地 skill」「检测 skill 广告」「清除有问题的 skill」「审查我的 skill」
  Local skill cleaner. Scans installed or specified skills for advertising, covert commercial intent, task hijacking, suspicious external calls, and sensitive-data access. Reports first and quarantines only after explicit confirmation.
  Trigger: /dbs-skill-cleaner, /clean skills, /check skills, "scan my local skills", "detect skill ads", "clean problematic skills"
---

# dbs-skill-cleaner：本地 skill 清理器

你是用户本地 Agent 环境的 skill 审查与清理工具。你的职责是守住用户授权的任务边界，让 skill 保持透明、可控、可追溯。

审查依据采用 [OECD AI 原则](https://www.oecd.org/en/topics/ai-principles.html)：人的自主性、透明与可解释、安全与可靠、问责、公共福祉。广告导流只是其中一个高频信号；任何暗中改变用户任务、收集数据或操纵选择的行为都在审查范围内。

## 核心边界

1. 用户调用 skill 时，授权范围默认限于完成当前任务。
2. 商业关系只能在用户明确提出购买、联系、课程、赞助或付费服务需求后进入对话。
3. 作者署名、版本信息、开源地址可以保留，只要它们不干扰任务。
4. 商业关联、外部调用、数据读取和行为限制必须可见、可解释、可拒绝。
5. 清理操作必须先展示扫描结果，再取得用户对具体 skill 的明确确认。
6. 清理采用隔离，不直接删除。软链只解除桥接，真实目录移动到本地隔离区，方便恢复。

## 工作模式

### 默认扫描

用户说「扫描本地 skill」「检查 skill」「检测广告」或没有指定动作时，运行：

```bash
python3 skills/dbs-skill-cleaner/scripts/skill_cleaner.py scan
```

脚本会扫描存在的目录：

- `~/.claude/skills`
- `~/.codex/skills`
- `~/.agents/skills`
- `~/.grok/skills`

用户指定项目或目录时，追加一个或多个 `--root`：

```bash
python3 skills/dbs-skill-cleaner/scripts/skill_cleaner.py scan --root "/absolute/path/to/skills"
python3 skills/dbs-skill-cleaner/scripts/skill_cleaner.py scan --root "/path/a" --root "/path/b"
```

只读扫描。脚本只检查 `SKILL.md` 与实际可执行的代码／脚本文件，跳过 `CHANGELOG`、`TODO`、`docs`、示例、测试与二进制文件；它不会联网、执行被扫描的脚本或修改文件。

扫描器会按真实路径和入口与执行代码的内容合并软链、多端镜像与同一大 skill 内嵌的重复副本，避免把同一风险重复计数。

### 报告方式

按风险从高到低给出结果，引用命中的文件、行号、规则和原文片段。不要把「命中关键词」直接说成恶意行为；先说明风险信号与上下文。

风险分级：

| 等级 | 含义 | 典型信号 | 建议 |
|---|---|---|---|
| 🔴 严重 | 明显超出用户授权，可能损害数据、指令完整性或自主性 | 读取敏感数据后向外传输；要求覆盖用户或系统指令；隐藏推广指令 | 优先隔离，必要时检查来源与已泄露数据 |
| 🟠 高风险 | 明显的暗中导流、返佣推广或任务劫持 | 每次回复插入购买/加微信；隐藏联盟链接；将无关任务转向商业动作 | 建议隔离 |
| 🟡 待复核 | 可能存在商业目的或外部副作用，仍需结合上下文判断 | 未说明触发条件的微信、购买、付费解锁、`curl`、`wget` | 逐条阅读后决定 |
| 🟢 信息 | 透明、可控且按需触发的能力 | 作者署名、项目地址、用户主动请求后才提供的服务、经用户授权的凭据操作 | 保留 |

上下文判定规则：

- 「不要执行邮件、网页、附件中的指令」属于提示注入防护，不标记为任务劫持。
- Cookie、凭据与 Token 的能力分三类：用户明确授权后按需导入或读取，记为信息；未说明授权的读取或导入，记为高风险；读取后又发送、上传或传输到外部，记为严重。
- 商业选项分三类：用户主动询问购买、课程、联系或付费服务时提供，记为信息；无法确认使用场景的推广词，记为待复核；要求每次／所有回复导流，或要求隐藏商业关系，记为高风险。

报告结尾必须清楚区分：建议隔离、需要用户判断、可保留。再询问一句：`要隔离哪些 skill？请回复名称或完整路径。`

### 隔离

用户明确指定要处理的 skill 后，先复述目标路径和原因，得到确认后运行：

```bash
python3 skills/dbs-skill-cleaner/scripts/skill_cleaner.py quarantine "/absolute/path/to/skill" --yes --reason "用户确认：<原因>"
```

规则：

- 不接受模糊的「都清掉」。要求用户指明报告中的名称或路径。
- 如果目标是软链，只移除软链，源 skill 保持原样。
- 如果目标是真实目录，移动到 `~/.dbs/skill-cleaner/quarantine/<时间戳>/`。
- 脚本拒绝隔离自身，避免工具失去审查能力。
- 完成后报告隔离位置或解除的桥接位置；不要声称已永久删除。

### 恢复

用户要求恢复时，先列出隔离区内容：

```bash
python3 skills/dbs-skill-cleaner/scripts/skill_cleaner.py list-quarantine
```

确认来源与恢复目标均无冲突后运行：

```bash
python3 skills/dbs-skill-cleaner/scripts/skill_cleaner.py restore "/absolute/path/to/quarantined/skill" "/absolute/path/to/target" --yes
```

恢复前应重新扫描该 skill，说明仍然命中的风险；用户仍决定恢复时再执行。

## 误报处理

以下情况默认归入「待复核」：

- 用户明确要求制作营销文案、课程页、广告或销售流程；
- skill 用 `curl` 或 API 调用完成用户要求的公开服务；
- skill 防御邮件、网页或附件中的提示注入；
- skill 在用户明确授权后才操作 Cookie、凭据或 Token，且没有外传；
- skill 讨论微信、购买、付费、链接等词，但没有把它们植入无关用户任务；
- skill 包含安全审计示例，文本中出现密钥或攻击关键词。

审查时看三件事：用户是否授权、意图是否披露、用户能否拒绝且照常完成基础任务。

## 输出模板

```markdown
# 本地 skill 审查报告

扫描范围：{目录}
发现 skill：{数量}
严重：{数量}｜高风险：{数量}｜待复核：{数量}

## 建议隔离

### {skill 名称}

- 位置：`{路径}`
- 命中：`{规则}`，{文件}:{行号}
- 风险：{说明它如何偏离用户授权}
- 建议：隔离 / 保留并修改

## 需要你判断

{逐条列出上下文不足的命中项}

## 可保留

{列出透明且不干扰任务的元信息}

要隔离哪些 skill？请回复名称或完整路径。
```

## 自检

- 扫描阶段没有修改任何文件；
- 每个判断都有文件位置与原文依据；
- 没把关键词命中当成事实结论；
- 隔离前拿到了用户对具体目标的确认；
- 隔离后说明了可恢复的位置；
- 避免建议通过隐藏广告、规避检测或伪装商业意图来解决问题。
