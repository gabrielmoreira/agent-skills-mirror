# Hermes Agent 工具映射

## 工具

| Skill 里要做的动作 | Hermes 工具 |
|------------------|------------|
| 读取文件 | `read_file` |
| 创建新文件 | `write_file` |
| 编辑文件（定点补丁） | `patch` |
| 运行 shell 命令 | `terminal` |
| 搜索文件内容 | `search_files` |
| 按文件名查找 | `terminal` 配合 `find` |
| 抓取 URL / 读网页 | `web_extract(urls=[...])` |
| 搜索网络 | `web_search(query=...)` |
| 派遣子智能体 | `delegate_task(goal=..., context=..., toolsets=[...], role="leaf")` |
| 任务跟踪 | `todo` 工具 |
| 调用 skill | `skill_view("skill-name")` |

## 指令文件

当某个 skill 提到「你的指令文件」时，在 Hermes Agent 上指的是项目目录里的 **`AGENTS.md`**，或全局的 **`~/.hermes/SOUL.md`**。

> 🇨🇳 **本节是 superpowers-zh 的增量内容，上游 obra/superpowers 没有。**
>
> 补充一条实践区分：`SOUL.md` 是**身份/人格**文件（Hermes 官方文档明确说项目工作流指令不属于它），所以 `npx superpowers-zh --tool hermes` 的**项目级**安装只写 `AGENTS.md`；**全局**安装只装 skills、不写 bootstrap —— 往 SOUL.md 里塞技能清单是误用那个文件。

## 调用 skill

Hermes Agent 有一个 `skills` 工具集，包含 `skill_view` 和 `skills_list` 两个工具。
要调用某个 superpowers skill，使用：

```
skill_view("brainstorming")
skill_view("test-driven-development")
```

如果 `skill_view` 找不到某个 superpowers skill（在插件完全注册之前，它可能还没出现在目录里），退回到直接读取 SKILL.md：

```
read_file(path="~/.hermes/plugins/superpowers/skills/<skill-name>/SKILL.md")
```

这个回退机制与其他没有原生 skill 加载能力的 harness 用的是同一套。

## 子智能体派遣

用 `delegate_task` 为并行或串行的工作流派生隔离的子智能体：

```
delegate_task(goal="...", context="...", toolsets=[...], role="leaf")
```

如果 `delegate_task` 不可用，就把工作内联做完，不要凭空编造工具调用。

## 任务跟踪

会话内的任务跟踪用 `todo` 工具。多智能体的任务看板，如果可用则使用 `hermes kanban` CLI。遇到旧文档里的 `TodoWrite` 引用，按「任务跟踪」这个动作理解即可。
