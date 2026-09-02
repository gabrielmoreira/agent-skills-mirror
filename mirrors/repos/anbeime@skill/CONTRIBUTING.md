# 贡献指南

感谢你对技能商店的关注！欢迎贡献技能、工具和文档。

## 贡献技能

### 快速流程

1. **复制模板**
   ```bash
   cp -r skills/_template skills/your-skill/your-skill
   ```

2. **编辑 SKILL.md** — 替换所有占位符为实际内容

3. **验证**
   ```bash
   python tools/skill_validator.py validate skills/your-skill
   ```

4. **提交 PR** — 描述你的技能用途和使用场景

### 命名规范

- 技能名：全小写 + 连字符，如 `code-review`、`data-export`
- 目录名：与技能名一致
- 标签：全小写，无空格

### 目录结构

采用双重嵌套结构：

```
skills/
└── your-skill/
    └── your-skill/
        ├── SKILL.md          ← 核心（必需）
        ├── assets/           ← 图片等资源（可选）
        └── references/       ← 参考文档（可选）
```

### SKILL.md 要求

- 必须以 YAML frontmatter 开头（`---`）
- `name` 和 `description` 为必填字段
- 正文至少 10 行，至少包含一个 `#` 标题
- 建议包含：任务目标、使用方式、核心逻辑、注意事项、示例

详见 [规范文档](docs/specification.md)。

## 贡献工具

欢迎改进验证工具或添加新工具：

1. 工具代码放在 `tools/` 目录下
2. 每个工具有独立的 README.md
3. 保持 Python 3.8+ 兼容

## 贡献文档

文档放在 `docs/` 目录下，使用 Markdown 格式：

- `specification.md` — 规范文档
- `best-practices.md` — 最佳实践
- `quickstart.md` — 快速入门

## PR 检查清单

提交 PR 前请确认：

- [ ] 运行 `python tools/skill_validator.py validate` 无错误
- [ ] 技能名全小写、连字符分隔
- [ ] `SKILL.md` 有完整的 YAML frontmatter
- [ ] 正文包含至少一个示例
- [ ] 没有修改不相关的文件
- [ ] commit message 清晰（如 `feat: add code-review skill`）

## Commit 规范

| 前缀 | 用途 | 示例 |
|------|------|------|
| `feat:` | 新增功能/技能 | `feat: add code-review skill` |
| `fix:` | 修复问题 | `fix: correct yaml parsing in validator` |
| `docs:` | 文档更新 | `docs: update quickstart guide` |
| `chore:` | 杂项维护 | `chore: update dependencies` |
| `refactor:` | 重构 | `refactor: simplify validator logic` |

## 问题反馈

- 发现 Bug：请提 Issue，附上复现步骤和验证工具输出
- 功能建议：欢迎在 Issue 中讨论
- 技能请求：可以提 Issue 请求特定技能
