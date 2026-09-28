# 通用 Web AI / 其他 Agent 部署

`target_cli` 含 `generic` 时，由 SKILL.md Phase 2 完整读取本文件并按顺序执行。路径安全检查、幂等重跑、清理自嵌套残留、部署标记、模板占位符、AGENTS.md 合并策略和安装报告的写法在 SKILL.md，这里只写通用路径专属部分。

## 部署清单（机械可检查）

| Source path | Target path | Owner class | Merge mode | Validation check |
|-------------|-------------|-------------|------------|------------------|
| `skills/story-setup/references/generic/AGENTS.md.tmpl` | `AGENTS.md` | user+managed | marker/section merge | contains generic story skill routing sections |
| repository `skills/{browser-cdp,story*}/` | `skills/{browser-cdp,story*}/` | story-setup managed for known skill names | replace known skill dirs only | 13 `SKILL.md` files exist; OpenClaw-compatible frontmatter |
| repository `skills/story-setup/references/agent-references/` | 随上一行整份 skill 拷贝落地，本行 no-op | story-setup managed | 不单独复制 | every reference resolves |

## 通用 Web AI / 其他 Agent 部署算法

通用路径面向 NarraFork、Web AI、自定义 Agent 等可读取项目文件的环境，只部署通用 `AGENTS.md` 与项目本地 `skills/`，不写平台专属 hooks/agents，也不声明平台原生 hooks/agents 能力。

1. 复制仓库当前 `skills/` 下所有包含 `SKILL.md` 的 story skill 目录（13 个：`browser-cdp` 与 `story*`）到目标项目 `skills/{skill-name}/`；仅替换这些 story-setup 管理的已知 skill 目录，保留用户其他目录。项目副本是整份 skill 拷贝，agent references 只使用当前规范前缀 `skills/`。
2. 复制 `skills/story-setup/references/generic/AGENTS.md.tmpl` 到项目 `AGENTS.md`，按 SKILL.md「AGENTS.md 合并策略」合并。
3. `.story-deployed` 的 `target_cli` 写入 `generic` 或多端组合；`references_dir` 对 generic 写 `skills/story-setup/references/agent-references`。
4. 安装报告提示项见下方「安装报告必须提示」。

## 验证

- 检查 `AGENTS.md` 含通用 story skill routing sections
- 检查 `skills/` 下 13 个 story skill 目录存在，且每个 `SKILL.md` 可读
- 检查 `skills/story-setup/references/agent-references/` 下 reference 文件完整且数量与源目录一致

## 安装报告必须提示

generic 不部署平台专属 hooks/custom agents；大纲守卫、commit 提醒、session/compact 注入等硬拦截与多 agent 协作都按 skill 内软约束或 solo/direct fallback 执行。
