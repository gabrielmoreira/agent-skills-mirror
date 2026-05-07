# Waza Skill Resolver

## Shared Output Marker

所有技能都沿用同一个输出约定：首行内联带上 `🥷`，不要单独起段。这个约定写在各自的 `SKILL.md` 里，`verify-skills.sh` 也会校验它。

触发词到技能的路由表。Claude Code 通过每个 SKILL.md 的 `description` 自动匹配，这份文档是给人看的集中索引，也是 `verify-skills.sh` 的校验依据。改 SKILL.md 的适用范围时，同步改这里。

> **Read the skill file before acting.** 两个技能都可能匹配时，两个都读。它们设计成可串联（例：`/think` → 实现 → `/check`）。

## 按工作流阶段分路

### Pre-build（动手前）

| 触发 | 技能 |
|------|------|
| 新功能 / 架构决策 / "怎么设计" / "应该用什么方案" / "判断一下" / "有没有必要" / "值不值得" / 需要可执行计划 | `skills/think/SKILL.md` |
| UI / 组件 / 页面 / 视觉界面 / 前端 / 截图里说"丑"、"不清晰"、"很怪" | `skills/design/SKILL.md` |

### Post-build（交付前）

| 触发 | 技能 |
|------|------|
| 实现完成 / 合并前 / "review 一下" / "看看这段代码" / `code-review` | `skills/check/SKILL.md` |
| release / publish / push / release reaction / 发布 / 提交 / 关闭 issue / 发布前检查 / 发布表情 | `skills/check/SKILL.md` (Ship / Release Follow-through) |
| review issue / review PR / triage / 批量处理 / "看看有没有 issue" / close issue | `skills/check/SKILL.md` (Triage Mode) |

### Diagnostic（出问题了）

| 触发 | 技能 |
|------|------|
| 报错 / 崩溃 / 测试失败 / 行为异常 / "为什么不工作" / 以前是好的 / 回归 / 截图回归 / 反复修不好 | `skills/hunt/SKILL.md` |
| Claude 忽略指令 / hook 失灵 / MCP 异常 / 配置审计 / health 消耗 token | `skills/health/SKILL.md` |

### Content（内容进出）

| 触发 | 技能 |
|------|------|
| 消息含 http(s) URL / 任何网页链接 / PDF 路径 / "看一下这个", "读一下这个" | `skills/read/SKILL.md` |
| 写作 / 改稿 / 润色 / 去 AI 味（中英文） / 推特推文 / 社交媒体文案 | `skills/write/SKILL.md` |
| 文档审阅 / 白皮书 / release notes prose 审核 / "审稿" / "check this document" | `skills/write/SKILL.md` (Document Review Mode) |
| 深度研究一个陌生领域 / 六阶段研究到成稿 / 一批材料沉淀成文章 | `skills/learn/SKILL.md` |

## Disambiguation（歧义消解）

多个技能都可能匹配时按以下规则：

1. **最具体优先**：`/design` 比 `/think` 更具体（仅限 UI 决策）。用户说"帮我设计登录页"时优先 `/design`。
2. **URL 按内容类型二次分流**：消息含 URL → 先走 `/read` 取回 Markdown → 如果用户要总结或分析，继续完成总结或分析；如果是长文研究性素材再接 `/learn`。
3. **改错 vs review**：代码已经交付或走到 PR → `/check`；代码跑不通或行为错了 → `/hunt`。两者都可能匹配"帮我看看"，按"有没有具体错误现象"判断。
4. **配置异常 vs 代码错误**：Claude 本身不听话、hook 不触发、MCP 掉链子或 `/health` 消耗 token → `/health`；用户写的代码抛异常 → `/hunt`。
5. **发布动作 vs 发布文案**：要写 release notes / changelog → `/write`；要提交、打 tag、publish、push、上传 release asset、补 GitHub release reactions、回复/关闭 issue → `/check`。
6. **截图审美 vs 截图回归**：截图里说"丑/不好看/不清晰"且是审美校准 → `/design`；截图证明以前好的现在坏了、渲染错、状态错、生成物错 → `/hunt`。
7. **长文产出 vs 润色**：从零到成稿 → `/learn`；已有稿子要改 → `/write`。
8. **判断 vs 调试**："判断一下" + 报错/异常/不工作 → `/hunt`（诊断问题）；"判断一下" + 有没有必要/该不该保留/值不值得 → `/think` Evaluation Mode（价值判断）。
9. **继续优化 vs 调试**："继续优化" / "优化代码" 不含报错或异常现象 → `/check`（代码质量改善）；有具体报错或回归 → `/hunt`。
10. **兜底**：两个都模糊时读两个 SKILL.md 的 "Not for" 段，用排除法；还是模糊就问用户。

## Chaining（常见串联）

技能之间的转换需要用户手动触发，不会自动串联。每个技能完成后会停下来，等你决定下一步。

- `/think` 出方案 → **用户说"实现"** → 实施 → **用户说"/check"** → `/check` 把关
- `/think` 出可执行计划 → **用户说"Implement the plan / 可以干 / 直接改"** → 按计划实施，不重新争论方向
- `/hunt` 修复 issue → **用户说"发布 / push / 关闭 issue"** → `/check` 做发布前检查和收尾
- `/read` 取回多篇 URL → **用户说"/learn"** → `/learn` 综合成文
- `/learn` 出初稿 → **用户说"/write"** → `/write` 去 AI 味
- `/hunt` 定位根因 → **用户说"修"** → 修完 → **用户说"/check"** → `/check` 确认没副作用
- `/health` 发现 skill 配置问题 → **用户说"修"** → 修完 → **用户说"/health"** → 再跑一次 `/health`

## Latent vs Deterministic

Waza 的技能都是 fat skill（Markdown 判断），底层的确定性约束走 `scripts/verify-skills.sh` 和 `rules/*.md`。新加能力时先问：

- 需要判断 / 适应场景 / 追问用户？→ skill
- 同入同出 / 只是校验和列举？→ script 或 rule

不要把 lint 检查写成 skill，也不要把"怎么研究一个陌生领域"塞进脚本。详见根目录 `AGENTS.md` 的决策表。

## Project Context

通用程序员能力沉淀在 Waza。遇到具体项目时，先从公开项目上下文提炼约束，再执行对应技能：

- `code-review` / `/check` -> 从 diff、README、manifest、CI、release notes 中提炼验证命令、生成物、风险和发布规则。
- `github-ops` -> 复用 `skills/check/SKILL.md` 的 Triage Mode，并从 issue/PR 现场确认 repo、发布状态和回复语言。
- `release` -> 从项目公开发布文档、脚本和 CI 中确认前置条件、产物和验证命令。

不要把证书路径、私钥文件名、token、个人机器路径或未公开的机器配置写进 Waza。
