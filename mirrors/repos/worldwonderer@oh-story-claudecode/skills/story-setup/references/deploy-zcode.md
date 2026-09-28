# ZCode 部署

`target_cli` 含 `zcode` 时，由 SKILL.md Phase 2 完整读取本文件并按顺序执行。路径安全检查、幂等重跑、清理自嵌套残留、部署标记、模板占位符、AGENTS.md 合并策略和安装报告的写法在 SKILL.md，这里只写 ZCode 专属部分。`references/zcode/` 下是 ZCode AGENTS、13 Commands、workspace config patch 与严格 JSON Hook runner。

## 部署清单（机械可检查）

| Source path | Target path | Owner class | Merge mode | Validation check |
|-------------|-------------|-------------|------------|------------------|
| `skills/story-setup/references/zcode/AGENTS.md.tmpl` | `AGENTS.md` | user+managed | marker/section merge | contains ZCode `$story-*` routing and solo fallback |
| repository `skills/{browser-cdp,story*}/` | `.zcode/skills/{browser-cdp,story*}/` | story-setup managed for known skill names | replace known skill dirs only | 13 `SKILL.md` files exist and satisfy ZCode frontmatter limits |
| `skills/story-setup/references/zcode/commands/` | `.zcode/commands/` | story-setup managed for known command names | replace known command files only | 13 commands have valid names/frontmatter |
| `skills/story-setup/references/zcode/hooks/story_zcode_hook.js` | `.zcode/hooks/story_zcode_hook.js` | story-setup managed | replace | Node syntax valid; hook contract tests pass |
| `skills/story-setup/references/zcode/hooks/story_hook_core.js` | `.zcode/hooks/story_hook_core.js` | story-setup managed | replace | Node syntax valid; hook contract tests pass |
| `skills/story-setup/references/zcode/config.json.patch` | merge into `.zcode/config.json` | user+managed | merge by event+matcher+process args | JSON valid; 按下方「ZCode 部署算法」第 4 步 hooks 互斥分支校验——未装 oh-story 插件时 `hooks.enabled=true`、only supported events；已装插件时校验 `.zcode/config.json` 不含（或已移除）这批 oh-story hooks 注册 |

## Agent 边界

**ZCode 3.3.4 不部署项目 agents**：其自定义子智能体只支持用户级 `~/.zcode/agents/`，plugin manifest 中的 `agents` 当前不执行。不要创建 `.zcode/agents/` 或修改用户 home；相关 Skill 必须直接 solo/direct 并报告 fallback。

## ZCode 部署算法

ZCode 首版部署 Skills、Commands、AGENTS.md 和支持事件内的 Hooks；部署时创建 `.zcode/`、合并根 `AGENTS.md`；不部署 `.zcode/agents` 或 `.zcode/rules`。

1. 复制仓库当前 `skills/` 下 13 个包含 `SKILL.md` 的目录到 `.zcode/skills/{skill-name}/`；仅替换这些已知目录，保留用户其他 Skills。ZCode 只使用当前规范前缀 `.zcode/skills/` 查找 agent references，不在运行时遍历历史备选路径。
2. 复制 `references/zcode/commands/*.md` 到 `.zcode/commands/`；仅替换 13 个同名命令，保留用户其他 Commands。
3. 复制 `references/zcode/hooks/story_zcode_hook.js` 和 `references/zcode/hooks/story_hook_core.js` 到 `.zcode/hooks/`。
4. 读取 `references/zcode/config.json.patch` 和现有 `.zcode/config.json`（如只有根 `zcode.json`，仍创建 `.zcode/config.json` 承载 oh-story 项目 Hooks，不改写根文件）：
   - 保留用户所有未知字段、MCP、plugins、skills/commands disable overrides；
   - **hooks 互斥（避免双触发）**：若本项目经已安装的 oh-story 插件运行（marketplace 安装，仓库根 `.zcode-plugin/plugin.json` 的 `hooks.json` 已全局注册 SessionStart/PreToolUse/PostToolUse），则**跳过**下面把 `config.json.patch` 的 `hooks` 块合并进 `.zcode/config.json`——插件 manifest 已注册这批 hooks，再合并会让同一事件跑两遍（PreToolUse 拦两次、PostToolUse 注入两次）。只有未装插件（直接克隆 / 手动导入 references）时才合并 hooks。不确定时以「ZCode 是否已通过本插件注册这套 hooks」为准；skills/commands/hook 文件/AGENTS 与 config 的非 hook 字段两条路径都照常部署。
   - 合并 hooks（仅未装插件时）：设置 `hooks.enabled: true`；用户已有更大的 `timeoutMs` 时保留，否则取模板值；对 `hooks.events` 的 SessionStart、PreToolUse、PostToolUse 按 `event + matcher + process command + args` 去重追加；不复制 ZCode 不支持的 PreCompact、PostCompact、SessionEnd、SubagentStop、Notification。
5. 将 `references/zcode/AGENTS.md.tmpl` 按 SKILL.md「AGENTS.md 合并策略」写入根 `AGENTS.md`。
6. `.story-deployed` 的 `target_cli` 写入 `zcode` 或多端组合，`references_dir` 写 `.zcode/skills/story-setup/references/agent-references`。ZCode 不创建 `.claude/.agents-pending-restart`，因为它不部署项目 agents。
7. 安装报告明确说明：ZCode 3.3.4 的项目/plugin custom agents 不执行，所有专业角色走 solo/direct；系统需要可用的 `node` 命令运行项目 Hook。

Plugin 安装不经过本算法：仓库根 `.zcode-plugin/plugin.json` 直接暴露同一组 Skills/Commands/Hooks。Plugin Skills 优先级低于 workspace `.zcode/skills`；两者同时存在时项目快照优先，升级项目快照需重新运行 `$story-setup`。**Hooks 只能注册一份**：插件 manifest 与 workspace `.zcode/config.json` 注册的是同一批事件，装了插件就不要再把 `config.json.patch` 的 hooks 合并进 `.zcode/config.json`（见上算法第 4 步的 hooks 互斥），否则 PreToolUse/PostToolUse 会双触发；插件在场时以插件 manifest 为 hooks 唯一注册源。

## 验证

- 检查根 `AGENTS.md` 含 ZCode `$story-*` 路由、大纲守卫和 solo/direct fallback
- 检查 `.zcode/skills/` 下 13 个 Skills 与 `.zcode/commands/` 下 13 个 Commands，验证 frontmatter 和命名
- 检查 `.zcode/hooks/story_zcode_hook.js`、`.zcode/hooks/story_hook_core.js` 存在且 `node --check` 通过
- 检查 `.zcode/config.json` JSON 有效，并按「ZCode 部署算法」第 4 步的 hooks 互斥分支校验：未装 oh-story 插件时，`hooks.enabled=true`、仅注册 ZCode 支持事件、所有 `process` args 指向项目 Hook；已装 oh-story 插件（`.zcode-plugin/plugin.json` 已全局注册这批 hooks）时，改为校验 `.zcode/config.json` 不含（或已移除）这批 oh-story hooks 注册——**不得**为了让校验通过而把 `config.json.patch` 的 hooks 块合并回去，否则同一事件双触发
- 检查 `.zcode/skills/story-setup/references/agent-references/` 完整且所有 reference 路径可解析
- 用 fixture 调用 SessionStart、PreToolUse deny/allow、PostToolUse，确认无发现时 stdout 为空、有输出时符合 ZCode 严格 JSON

## 安装报告必须提示

ZCode 3.3.4 不执行项目/plugin custom agents，full/lean 多 Agent 请求会稳定降级 solo/direct；Hook 依赖 PATH 中的 `node`；部署后新开 ZCode session 刷新 Skills/Commands/AGENTS.md。
