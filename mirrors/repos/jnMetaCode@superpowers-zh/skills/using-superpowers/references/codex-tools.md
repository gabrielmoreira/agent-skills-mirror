# Codex 工具映射

> 🇨🇳 **本节的工具映射表是 superpowers-zh 的增量内容，上游 obra/superpowers 没有。** 其余章节为上游内容的翻译。

Skills 使用 Claude Code 的工具名称。在 Codex 中遇到这些名称时，请使用对应的平台等价工具：

| Skill 中的引用 | Codex 等价工具 |
|---------------|---------------|
| `Task` 工具（派遣子 agent） | `spawn_agent` |
| 多个 `Task` 调用（并行） | 多个 `spawn_agent` 调用 |
| Task 返回结果 | `wait_agent` |
| Task 自动完成 | V2 无需处理（用完自动回收）；仅 V1 需要 `close_agent` 释放槽位 |
| `TodoWrite`（任务跟踪） | `update_plan` |
| `Skill` 工具（调用 skill） | Skills 原生加载——直接按说明操作 |
| `Read`、`Write`、`Edit`（文件） | 使用原生文件工具 |
| `Bash`（执行命令） | 使用原生 shell 工具 |

## 子 Agent 派遣需要多 Agent 支持

在 Codex 配置文件（`~/.codex/config.toml`）中添加：

```toml
[features]
multi_agent = true
```

启用后，`dispatching-parallel-agents` 和 `subagent-driven-development` 这类 skill 所用的多智能体工具就可用了。**你拿到哪些工具，取决于你的模型预设选中的多智能体版本**（当前的预设跑 V2，较老的跑 V1）。当你的实际工具列表与任何表格（**包括本文这张**）不一致时，以实际工具列表为准。

- **派生（Spawning）：** 用 `spawn_agent {fork_turns: "none"}` 给子代理一个干净的上下文；默认值 `"all"` 会把你的**整份对话记录**复制进子代理。在 Codex 0.145+ 上，`~/.codex/agents/` 下的角色文件通过 `agent_type` 挂到隔离 fork 上。全历史 fork 接受 `model` 与 `reasoning_effort` 覆盖（在那里只有 `agent_type` 会被拒绝）—— 隔离 fork 是 SDD 的默认选择，理由是上下文卫生，**不是**因为覆盖参数需要它。
- **修复轮次（Fix rounds）：** 用 `followup_task` 唤回实现者 —— 它会送达你的消息、触发一个回合，并在 harness 已经回收该子代理时透明地把它重新装载回来。绝不要因为「派生出去的 agent 不能再被发消息」这种想当然而重新派一个新的实现者；在 V2 上它**总是**可以。
- **生命周期（Lifecycle）：** **V2 没有 `close_agent`。** 完成的子代理会在需要槽位时被自动回收，放着不管不产生任何成本。只有 V1 会话才有 `close_agent` —— 在那里，审查者返回审查结果后就关掉它，每个实现者在其任务的审查通过后关掉。
- **模型名：** 绝不要把 skill、表格或旧会话里的模型名直接抄进 `spawn_agent` 而不先对照你**当前**的 spawn 允许列表 —— V2 只接受具备 V2 能力的预设，其余会直接硬报错。

## 等待子代理

`wait_agent` 是**事件订阅，不是轮询**：一次长等待会在子代理产生信箱活动的那一刻醒来，延迟和短等待完全一样。短超时轮询什么也换不到，却每次都要付一次工具调用 —— 以及一次上下文重新计费。在实测会话里，大约**三分之二**的 wait 调用都是超时的短轮询。

- 只要你手上还有本地工作，就**完全不要等**。已完成子代理的最终回答会被推进你的信箱，随你的下一个回合一起到达。
- 当你确实空闲、且还有子代理在跑时，按**有界的时间段**等待：`wait_agent` 的 `timeout_ms` 设 300000-600000（5-10 分钟）。每一段结束后 —— 无论是被唤醒还是超时 —— 发一行状态、跑一次 `list_agents`，并追查任何「已完成但没汇报」的子代理。绝不要把小于五分钟的轮询叠着用；事件订阅唤醒一个有界时间段的速度和唤醒一次短轮询一样快。
- 完成邮件**无法唤醒一个空闲的控制者**（它送达时不触发回合）；覆盖这个空闲窗口正是 `wait_agent` 唯一的职责。一段等待在毫无活动的情况下超时，是让你去做对账的信号，**不是**让你把下一段缩短的理由。

## 派生时的模型路由

你发出的**每一次** `spawn_agent`（包括你自己就是一个正在做扇出的子代理时），都要按你正在执行的那个 skill 的「模型选择」规则，**同时显式设置 `model` 和 `reasoning_effort`**。只设 `model` 是个陷阱：子代理的 effort 会静默重置为那个模型的默认值，而不是你的。

请你的人类伙伴在 `~/.codex/config.toml` 里加一道机器级兜底，这样任何漏设的派生仍然会路由到一个刻意选定的档位，而不是静默继承本次会话最贵的那个模型：

```toml
[agents]
default_subagent_model = "<你的 spawn 允许列表里的一个中档模型>"
default_subagent_reasoning_effort = "medium"
```

## 环境检测

创建 worktree 或收尾分支的 skill，应当在动手之前用**只读**的 git 命令检测环境：

```bash
GIT_DIR=$(cd "$(git rev-parse --git-dir)" 2>/dev/null && pwd -P)
GIT_COMMON=$(cd "$(git rev-parse --git-common-dir)" 2>/dev/null && pwd -P)
BRANCH=$(git branch --show-current)
```

- `GIT_DIR != GIT_COMMON` → 已经在一个链接的 worktree 里（跳过创建）
- `BRANCH` 为空 → detached HEAD（无法从沙箱里建分支/推送/开 PR）

各 skill 如何使用这些信号，见 `using-git-worktrees` 的第 0 步与 `finishing-a-development-branch` 的第 1 步。

## Codex App 的收尾

当沙箱阻止建分支/推送操作时（在外部托管的 worktree 里处于 detached HEAD），agent 应提交全部工作，并告知用户改用 App 的原生控件：

- **"Create branch"** —— 命名分支，然后通过 App UI 完成 commit/push/PR
- **"Hand off to local"** —— 把工作转交到用户的本地检出

agent 仍然可以跑测试、暂存文件，并输出建议的分支名、commit message 和 PR 描述供用户复制。
