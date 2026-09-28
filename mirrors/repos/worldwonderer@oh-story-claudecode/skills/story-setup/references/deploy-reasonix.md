# Reasonix 部署

`target_cli` 含 `reasonix` 时，由 SKILL.md Phase 2 完整读取本文件并按顺序执行。路径安全检查、幂等重跑、清理自嵌套残留、部署标记、模板占位符、AGENTS.md 合并策略和安装报告的写法在 SKILL.md，这里只写 Reasonix 专属部分。

## 部署清单（机械可检查）

| Source path | Target path | Owner class | Merge mode | Validation check |
|-------------|-------------|-------------|------------|------------------|
| `skills/story-setup/references/reasonix/AGENTS.md.tmpl` | `AGENTS.md` | user+managed | marker/section merge | contains Reasonix story skill routing sections and solo/direct fallback |
| repository `skills/{browser-cdp,story*}/` | `skills/{browser-cdp,story*}/` | story-setup managed for known skill names | replace known skill dirs only | 13 `SKILL.md` files exist; OpenClaw-compatible frontmatter |
| repository `skills/story-setup/references/agent-references/` | 随上一行整份 skill 拷贝落地，本行 no-op | story-setup managed | 不单独复制 | every reference resolves |

## Reasonix skills-only 部署算法

Reasonix（DeepSeek-Reasonix CLI）当前只部署 skills 与 `AGENTS.md`，不部署 Reasonix hooks/custom agents（hook I/O 契约与子代理行为缺少可校验的真实 CLI，留待后续阶段）。

1. 读取仓库当前 `skills/` 下所有包含 `SKILL.md` 的 story skill 目录（13 个：`browser-cdp` 与 `story*`）到目标项目 `skills/{skill-name}/`；仅替换这些 story-setup 管理的已知 skill 目录，保留用户其他目录。项目副本是整份 skill 拷贝，agent references 只使用当前规范前缀 `skills/`。
2. 在项目根创建 `.agents/skills → ../skills` 相对 symlink（与 Codex 共用的 skill root），使 Reasonix 原生扫描 `.agents/skills` 时发现这些 skill；若已是指向 `skills/` 的 symlink 则保留，若被占用为普通目录则不覆盖并在安装报告提示。Windows 未启用 symlink 时跳过本步，改走根 `reasonix-plugin.json` 的 `reasonix plugin install`。
3. 复制 `skills/story-setup/references/reasonix/AGENTS.md.tmpl` 到项目 `AGENTS.md`，按 SKILL.md「AGENTS.md 合并策略」合并。
4. `.story-deployed` 的 `target_cli` 写入 `reasonix` 或多端组合；`references_dir` 对 Reasonix 写 `skills/story-setup/references/agent-references`。
5. 安装报告提示项见下方「安装报告必须提示」。

## 验证

- 检查 `AGENTS.md` 含 Reasonix story skill routing sections 与 solo/direct fallback 说明
- 检查 `skills/` 下 13 个 story skill 目录存在，且每个 `SKILL.md` 可读
- 检查项目 `.agents/skills` 为指向 `skills/` 的 symlink（POSIX；使 Reasonix 原生扫描发现 skill）；Windows 未建 symlink 时改为确认根 `reasonix-plugin.json` 可用于 `reasonix plugin install`
- 检查 `skills/story-setup/references/agent-references/` 下 reference 文件完整且数量与源目录一致

## 安装报告必须提示

Reasonix 当前是 skills-only；未部署 Reasonix hooks/custom agents，写正文前大纲守卫、commit 提醒、session/compact 自动注入只作为 skill 内软约束，涉及专业 Agent 的 Skill 走 solo/direct fallback；可用 `reasonix doctor capabilities` 校验 skill 发现，部署后如未显示新 skills，新开 Reasonix session 或走根 `reasonix-plugin.json` 原生 plugin 安装。
