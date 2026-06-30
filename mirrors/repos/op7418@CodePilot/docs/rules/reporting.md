# 汇报与完成状态 / Reporting & Completion Status

> 目的：让用户用最少阅读量知道"现在能不能继续 / 能不能发版"，不被技术细节淹没。
> 顶层 `CLAUDE.md` / `AGENTS.md` 只放一句摘要 + 指到这里。

## 完成状态词典（禁止混用）

报告进度时必须用下面的词，**不能把 `Code complete` 直接说成"已修好 / 搞定了"**：

| 状态 | 含义 | 达到的证据 |
|------|------|-----------|
| `Code complete` | 产品代码已改完 | diff 落地 |
| `Tests pass` | targeted / full 测试通过 | 测试输出 |
| `Smoke passed` | 真实 UI / 凭据 / app 路径跑通 | Smoke Ledger 一行 |
| `Review passed` | Codex 或 Claude Code 复审无 blocker | review 结论 |
| `Release ready` | 文档、测试、smoke、已知风险都可接受 | 风险清单 |
| `Shipped` | 已 push / tag / release | tag + Release URL |

为什么要词典：#629 / #635 / #628 都出现过"代码完成"被当成"修好了"、随后又被 route / UI / smoke follow-up 打回的情况——状态词混用是根因之一。`Code complete` ≠ `Shipped`。

## 简化汇报协议（默认格式）

普通 bug fix / 小改动默认用这五行，**控制在 5 行以内**：

```text
结论：可继续 / 需返工 / 暂停
用户影响：一句话
验证：跑了什么，结果如何
剩余风险：没有就写"无阻塞"
下一步：谁做什么
```

默认**不贴** commit 串、`file:line`、source-pin、测试全文。

**只有这些情况才展开详细证据**：
- Tier 2 改动（Runtime / Provider / DB / 权限 / Stream / MCP / Electron / 发版链路）
- review blocker
- 用户主动要细节

> 配套：技术细节默认不进用户汇报，这条与 `feedback_user_cannot_judge_tech_detail`（用户判断产品/UX、不审技术深度）一致——每个计划 / Phase 先讲"用户能看到什么"，技术细节单列且标注用户不需审核。
