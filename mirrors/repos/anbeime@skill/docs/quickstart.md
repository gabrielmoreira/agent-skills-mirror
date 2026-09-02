# 快速入门

## 30 秒创建一个技能

### 1. 复制模板

```bash
cp -r skills/_template skills/my-skill/my-skill
```

### 2. 编辑 SKILL.md

```bash
vim skills/my-skill/my-skill/SKILL.md
```

修改 frontmatter：

```yaml
---
name: my-skill
description: 一句话描述你的技能做什么。
version: 1.0.0
author: your-name
tags:
  - productivity
---
```

修改正文，替换所有 `<占位符>` 为实际内容。

### 3. 验证

```bash
python tools/skill_validator.py validate skills/my-skill
```

看到 ✅ 即可提交。

### 4. 提交

```bash
git add skills/my-skill
git commit -m "feat: add my-skill"
git push
```

## 常用命令

```bash
# 验证所有技能
python tools/skill_validator.py validate

# 验证单个技能
python tools/skill_validator.py validate skills/agent-team

# 读取技能属性
python tools/skill_validator.py read-properties skills/agent-team

# 输出 JSON 格式属性
python tools/skill_validator.py read-properties skills/agent-team --json

# 生成 XML prompt（用于 AI 调用）
python tools/skill_validator.py to-prompt skills/agent-team
```

## 目录结构一览

```
anbeime/skill/
├── skills/                 ← 技能目录
│   ├── _template/          ← 技能模板
│   ├── agent-team/         ← 已有技能
│   │   └── agent-team/
│   │       └── SKILL.md
│   └── ...
├── tools/                  ← 工具
│   ├── skill_validator.py  ← 验证入口
│   └── skill_validator/    ← 验证模块
├── docs/                   ← 文档
│   ├── specification.md    ← 规范文档
│   ├── best-practices.md   ← 最佳实践
│   └── quickstart.md       ← 本文件
├── CONTRIBUTING.md         ← 贡献指南
└── README.md               ← 仓库说明
```

## 下一步

- 阅读 [规范文档](specification.md) 了解完整规范
- 阅读 [最佳实践](best-practices.md) 提高技能质量
- 阅读 [贡献指南](../CONTRIBUTING.md) 了解提交流程
