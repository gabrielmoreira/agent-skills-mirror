# skills 目录

`skills/` 保存可移植、可安装的 AI Skill 包。每个子目录都是一个独立分发单元，必须包含自己的
`SKILL.md`、版本信息和自述文档。

```text
skills/
├── AGENTS.md             # Skill 分发层的职责与边界
└── solve/                # 问题求解算子 Skill
```

## 依赖与边界

```text
operators/ ──发布快照──> skills/solve/references/
skills/solve/SKILL.md ──按需加载──> references/catalog.json、taxonomy/、packs/
```

- `operators/` 是算子内容唯一真相源；`skills/` 是面向 AI 消费的可移植发布层。
- Skill 包可以自包含安装，不依赖本仓库运行时；它不拥有模型调用、工具权限、selector、planner、
  业务状态或执行结果。
- 新增或移动 Skill 时，必须同步更新本文件、子目录 `AGENTS.md`、根目录文档和治理上下文。
