# Muse 工具映射

Skill 用动作来表述（「分派一个子智能体」「创建一条待办」「读取一个文件」）。在 Muse 上，这些动作对应下面的工具。

| Skill 里要做的动作 | Muse 对应工具 |
|----------------------|----------------|
| 读取文件 | `read_file` |
| 读取多个文件 | `read_file`（多次调用）或 `search` |
| 创建新文件 | `write_file` |
| 编辑文件 | `edit_file` |
| 运行 shell 命令 | `bash` |
| 搜索文件内容 | `search` |
| 按文件名查找 | `search` 配合 `glob` |
| 抓取 URL | `web_fetch` |
| 搜索网络 | `web_search` |
| 调用 skill | 对 `skills/<name>/SKILL.md` 用 `read_file`，或用原生 skill 工具 |
| 分派子智能体（`Subagent (general-purpose):` 模板） | `subagent_spawn`，并填好提示词 |
| 任务跟踪（「创建一条待办」「标记完成」） | `write_todos` 或用 `bash` 维护任务文件 |
| 向用户提问 | `request_user_input` |

## 指令文件

当某个 skill 提到「你的指令文件」时，在 Muse 上指的是项目根目录里的 **`CLAUDE.md`** 或 **`AGENTS.md`**。在配置了的情况下，Muse 会分层加载它们。

## 调用 skill

Muse 通过 `muse skills` 原生支持 skill。要调用某个 Superpowers skill，读取它的 `SKILL.md` 并按其中的指示执行。引导技能（`using-superpowers`）会在 `SessionStart` 时通过插件 hook 自动注入——你已经在遵循它了，不要再加载一次。

## 分派子智能体

用 `subagent_spawn` 把工作委派给相互隔离的子智能体。分派之前先填好提示词模板（例如 `implementer-prompt.md`、`task-reviewer-prompt.md`）。如果没有可用的子智能体工具，就内联完成这项工作，而不是编造工具调用。

## 任务跟踪

用 `write_todos` 跟踪清单。技能清单里的每一项建一条待办，边做边标记 in_progress/completed。如果 `write_todos` 不可用，就用 `write_file`/`edit_file` 维护一个 markdown 任务文件。
