# Examples

## Should Trigger

User:

```text
Context is getting too long. Use $session-handoff-prompt to give me a balanced prompt for a new session.
```

Expected behavior:

1. Use the current visible conversation.
2. Read task-forest exports if present.
3. Generate the paste-ready prompt first.
4. Validate in `local` privacy mode unless the user asks to share it externally.

## Should Not Trigger

User:

```text
Summarize this conversation in three bullets.
```

Use a normal summary. Do not invoke this skill unless the user wants a new-session continuation prompt.

User:

```text
Update task-forest from this session and export the HTML.
```

Use `$task-forest`. This skill may later read the task-forest export, but it does not maintain it.

## Representative One-Shot

Paste-ready prompt in Chinese for a local handoff:

```text
你正在接手一个已经进行过多轮的 agent session。请按以下上下文恢复任务状态；不要重新讨论已定事项。如果当前文件或可验证证据与这里冲突，以当前证据为准，并明确指出冲突。

【工作目录】
<workspace>

【用户目标】
把 `session-handoff-prompt` 作为 COMPASS 的正式 skill 接入，要求跨 macOS/Linux/Windows、跨 Claude Code/Codex/OpenClaw/OpenCode/Harness 等 agent 可用，并更新中英文 README。

【必须遵守的要求】
- [verified] 内部说明用英文；与用户交互和输出使用用户语言，默认中文。
- [verified] 不上传数据，不读取 credential、cookie、浏览器 session 或无关私有日志。
- [verified] 不能像补丁一样只复制旧 skill，要融入 COMPASS 的画像、任务森林、需求对齐和跨 session 续接生态。

【已确认事实与决策】
- [verified] `task-forest` 负责长期任务结构，`session-handoff-prompt` 负责生成可粘贴到新 session 的续接 prompt。
- [verified] task-forest exports 只作为只读结构化来源，不替代当前 session。
- [inferred] 默认应使用 balanced 模式，因为用户同时要求还原度和简洁性。

【已完成】
- 已阅读现有 COMPASS README、AGENTS、安全边界和三个已发布 skill 的结构。
- 已设计 portable skill 结构：`SKILL.md`、`references/`、`scripts/`、`evals/`、`agents/`。

【未完成 / 待验证】
- 需要运行 Python 编译、smoke test、secret/path scan 和 README manifest 校验。

【关键文件 / 命令 / 产物】
- `skills/session-handoff-prompt/SKILL.md`
- `skills/session-handoff-prompt/scripts/smoke_test_handoff.py`
- `README.md`, `README.zh.md`, `README.en.md`, `skills.sh.json`

【不要重复 / 不要做】
- 不要自动创建新 agent session。
- 不要写入 task-forest proposal。
- 不要把本地绝对路径或 token 放进 shareable handoff。

【下一步】
1. 完成 README 和 manifest 更新。
2. 运行 smoke test 和安全扫描。
3. 报告验证结果和剩余限制。
```

Mode note:

```text
Mode: balanced. Privacy: local. Sources: visible conversation and workspace files. You can ask for minimal, full, or shareable redacted output.
```

## Boundary Example

If the user asks for a public handoff, switch to `privacy=shareable`, redact local paths, and validate with:

```bash
python3 <skill-dir>/scripts/validate_handoff_prompt.py <redacted.txt> --mode balanced --privacy shareable
```
