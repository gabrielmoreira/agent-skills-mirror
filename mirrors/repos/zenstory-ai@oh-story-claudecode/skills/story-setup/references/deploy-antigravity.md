# Google Antigravity 部署

`target_cli` 含 `antigravity` 时，由 SKILL.md Phase 2 完整读取本文件并按顺序执行。路径安全检查、幂等重跑、清理自嵌套残留、部署标记和安装报告的写法在 SKILL.md，这里只写 Antigravity 专属部分。`references/antigravity/` 下是 Antigravity 2.0 Always-On Rule、named-group hooks 模板与 I/O adapter；正文写后 findings 经 session artifact 桥接到 PreInvocation/Stop。

## 部署清单（机械可检查）

| Source path | Target path | Owner class | Merge mode | Validation check |
|-------------|-------------|-------------|------------|------------------|
| current package skill root + `scripts/deploy-antigravity-skills.py` | `.agents/skills/{browser-cdp,story*}/` | story-setup managed for 13 known skill names | atomically replace known dirs; preserve unknown skills; never write through symlink | 13 real skill directories with valid `SKILL.md` exist |
| `skills/story-setup/scripts/generate-antigravity-agents.mjs` + Claude agent sources | `.agents/agents/agent-name/agent.md`（`agent-name` 为实际名称） | story-setup managed for 7 known agent definitions | generate then atomically replace known definitions; preserve unknown user agents | 7 Markdown agents parse; exact Antigravity tool names; `mainAgent: false`, `subagent: true` |
| `skills/story-setup/references/antigravity/rules/oh-story.md` | `.agents/rules/oh-story.md` | story-setup managed | replace | `trigger: always_on`; under 12,000 characters |
| `skills/story-setup/references/antigravity/hooks/hooks.json` | `.agents/hooks.json` | user+managed | replace only top-level `oh-story` group | valid Antigravity named-group schema; user groups preserved; idempotent |
| `skills/story-setup/references/antigravity/hooks/{story_antigravity_hook.js,story_hook_core.js}` | `.agents/hooks/` same names | story-setup managed | replace | Node syntax valid; core byte-identical to shared source; hook contract tests pass |
| `skills/story-setup/scripts/merge-antigravity-hooks.py` | deployment helper only | story-setup helper | execute | atomically replaces only `oh-story`, preserves user groups, idempotent |

## 部署 Antigravity Agents

- 先确认 `node` 在 PATH；Antigravity agent 生成与项目 hooks 都依赖 Node。缺失时停止 Antigravity 这一目标的部署，不留下半成品，并提示安装 Node 后重跑。
- Agent 正文以 Claude Code Markdown 为真源。`.agents/agents/agent-name/agent.md`（`agent-name` 为实际名称）在部署时调用随 story-setup 下发的 `scripts/generate-antigravity-agents.mjs`，把 Claude 工具名、模型档、reference 根和调用术语确定性转换为 Antigravity 2.0 契约；不得把 Claude frontmatter 原样复制过去。
- 执行 `node "{story-setup skill目录}/scripts/generate-antigravity-agents.mjs" --source "{story-setup skill目录}/references/templates/agents" --dest "{项目}/.agents/agents"`。生成器先渲染全部 7 个 agent，再原子替换这 7 个已知 `.agents/agents/agent-name/agent.md` 定义（`agent-name` 为实际名称），并清理旧版同名扁平 `.md`；保留其他用户 agent，任一源 frontmatter 异常时不得留下半更新目录，也不得沿 managed agent symlink 写出项目外。
- 校验 7 个 `.md`：`name` 与文件名一致；`mainAgent: false`、`subagent: true`；模型只使用 `flash` / `pro`；工具只来自 Antigravity 官方名称 `view_file`、`find_by_name`、`grep_search`、`write_to_file`、`replace_file_content`、`multi_replace_file_content`、`run_command`；不得残留 Claude 的 `Read/Glob/Grep/Write/Edit/Bash` 工具名或 `.claude/skills/` reference 前缀。Antigravity 只使用当前规范前缀 `.agents/skills/`。
- 只读 agent（`consistency-checker`、`story-explorer`）不得包含写文件或命令工具；`chapter-extractor` 只有读取与写文件、无命令工具；其他 agent 按 Claude 真源的能力边界映射。
- Antigravity 通过 `invoke_subagent` 的 `TypeName` 调用这些 agent。部署后新开 Antigravity conversation，再用 `story-review` 验证 full/lean；运行时无法解析某个 custom agent 时按 skill 的 solo/direct fallback 执行。

## Antigravity 部署算法

Antigravity 2.0 使用项目 `.agents/` customization 根，部署时创建 `.agents/skills`、`.agents/agents`、`.agents/rules`、`.agents/hooks` 并合并 `.agents/hooks.json`。部署 Skills、Always-On Rule、7 个 custom subagents 与 workspace Hooks；不修改用户 home 下的 `~/.gemini/`。

1. 找到当前 skill 包的 13 个已知 skill 目录（`browser-cdp` 与 `story*`），调用 `deploy-antigravity-skills.py --source "{当前 skill 包根}" --dest "{项目}/.agents/skills"` 原子物化。helper 只替换 13 个已知名称、保留用户其他 skills，并在源目标同一 realpath 时 no-op。目标必须是**真实目录**，不要新建顶层 `.agents/skills → ../skills` symlink：Antigravity 2.0 项目部署以真实目录作为受支持路径。
   - 若已有 `.agents/skills` 是 symlink，helper 必须先停止且不沿链接写入。用 AskUserQuestion 说明：迁移会把链接当前可见的所有 skills 复制到新的项目内真实目录、只更新 13 个 oh-story 名称、保留链接目标原样，但会把 symlink 本身替换成目录；这可能形成较大的 git diff。只有用户明确同意后才加 `--migrate-symlink` 重跑，拒绝则停止 Antigravity 部署并报告未获得完整支持。这个确认不得被“多端部署”或已有 Codex symlink 跳过。
2. 按上方「部署 Antigravity Agents」运行生成器，原子更新 `.agents/agents/` 中 7 个已知 `.agents/agents/agent-name/agent.md` 定义（`agent-name` 为实际名称）并保留其他用户 agent；不从用户 home 搬运 agent。
3. 复制 `references/antigravity/rules/oh-story.md` 到 `.agents/rules/oh-story.md`，验证 `trigger: always_on` 且文件小于 Antigravity 12,000 字符上限。该 rule 承担 skill 路由、写作硬约束与 compact 后恢复；Antigravity IDE 不以根 `AGENTS.md` 作为 workspace rule，所以不要用 AGENTS 模板代替。
4. 复制 `references/antigravity/hooks/story_antigravity_hook.js` 与同目录 `story_hook_core.js` 到 `.agents/hooks/`，验证 `node --check`。hook 命令以 `.agents/`（`hooks.json` 所在目录）为工作目录，必须使用 `hooks/story_antigravity_hook.js`，不得写成 `.agents/hooks/...`。共享 core 必须与 Claude/OpenCode/ZCode 源字节一致。
5. 合并 `references/antigravity/hooks/hooks.json` 到 `.agents/hooks.json`：按跨平台规则探测 Python 3，调用 `merge-antigravity-hooks.py {项目}/.agents/hooks.json {skill目录}/references/antigravity/hooks/hooks.json`。helper 只替换顶层 `oh-story` named group，保留其他用户 hook groups；写后复跑并比较字节确认幂等。禁止把 Claude/Codex 的外层 `{ "hooks": ... }` schema 写入 Antigravity。
6. 校验事件边界：只注册 `PreToolUse`、`PostToolUse`、`PreInvocation`、`Stop`。PreToolUse 必须为每次调用输出 `decision`；PostToolUse 必须只输出 `{}`，正文 findings 经 session `artifactDirectoryPath` 暂存并由下一次 PreInvocation 注入；若模型准备直接结束，Stop 最多强制继续一次，避免无限循环。Antigravity 外部 hooks 没有 SessionStart/PreCompact/PostCompact，首次上下文由 `invocationNum=0` 的 PreInvocation 注入，compact 后由 Always-On Rule 强制读取 `追踪/上下文.md`。
7. `.story-deployed` 的 `target_cli` 写 `antigravity` 或多端组合，`references_dir` 写 `.agents/skills/story-setup/references/agent-references`。安装报告提示新开 conversation 使 Skills/Rules/Agents/Hooks 重新扫描；同时明确 Node 是 hook 运行时依赖。

Antigravity IDE 与交互式 `agy` 共用这套 workspace `.agents/` 产物，但仍需分别实机 smoke test。不要依赖 `npx skills add -g` 当前把全局 skill 写到哪个 `~/.gemini/*` 目录；`story-setup` 的支持承诺只覆盖上述项目内真实目录部署。

## 验证

- 检查 `.agents/skills/` 下 13 个 story skills 为真实目录且 `SKILL.md` 可读；`.agents/skills/story-setup/references/agent-references/` 完整
- 检查 `.agents/agents/` 下 7 个 Markdown agent 可解析，名称、模型档、官方工具白名单、只读边界与 `.agents/skills/` reference 前缀正确
- 检查 `.agents/rules/oh-story.md` 为 `trigger: always_on` 且未超过 12,000 字符
- 检查 `.agents/hooks.json` 有效、顶层 `oh-story` group 恰有 PreToolUse/PostToolUse/PreInvocation/Stop，用户 hook groups 保留；检查 `.agents/hooks/story_antigravity_hook.js` 与 `story_hook_core.js` 语法有效
- 用 fixture 验证：PreToolUse 缺纲/追踪时 deny、普通写入 allow、commit advisory；PostToolUse stdout 恒为 `{}` 且把正文 findings 写进 session artifact；下一次 PreInvocation 注入 findings；Stop 对未处理 findings 最多 continue 一次；干净正文清除 pending state

## 安装报告必须提示

新开 Antigravity conversation 刷新 customization；Hooks 依赖 PATH 中的 `node`；外部 hook API 没有 PreCompact/PostCompact，compact 恢复由 Always-On Rule 读取 `追踪/上下文.md`；IDE 与交互式 `agy` 仍建议分别实机 smoke test；命令行写作从项目目录进入交互式 `agy`，确认 `/skills`、`/agents`、`/hooks` 已发现 oh-story 后再发任务；print 模式 `agy -p` 必须带 `--add-dir "$PWD"`（实测 agy 1.2.10 带上才加载工作区 `.agents/` 的 13 个 skills、7 个 agents 与 hooks，不带则都不加载，可能回退写入 `~/.gemini/antigravity-cli/scratch/`），测试后检查 scratch 无意外小说产物。
