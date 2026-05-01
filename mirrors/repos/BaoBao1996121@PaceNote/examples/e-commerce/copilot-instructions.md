<!-- PACENOTE-CONFIG-START -->
# PaceNote 开发指南

> 🚀 专家目录: `.github/skills/`

---

## 🔑 专家路由机制（扫描 SKILL.md）

**专家发现方式**: 扫描 `.github/skills/*/SKILL.md` 的 YAML frontmatter

**匹配规则**: 
- 读取每个 SKILL.md 的 `description` 字段
- description 中包含"触发关键词: xxx、yyy、zzz"
- 用户问题与触发关键词进行正则匹配（忽略大小写）

**Skill 分类优先级**:
1. **工作流 Skill** - pbi-reviewer、roundtable-debate、coding-agent
2. **应用专家** - app-ecommerce-*-expert（应用特定业务）
3. **工具专家** - git-blame 等

---

## 📁 项目文档配置

| 文档 | 路径 | 状态 |
|------|------|------|
| 检查清单 | `.github/copilot-resources/docs/checklist.md` | ✅ 已填充 |
| 功能模块 | `.github/copilot-resources/docs/modules.md` | ✅ 已填充 |
| 功能依赖 | `.github/copilot-resources/docs/dependencies.md` | ✅ 已填充 |

> 此为示例项目，展示 PaceNote 部署完成后的目标状态。

<!-- PACENOTE-CONFIG-END -->
