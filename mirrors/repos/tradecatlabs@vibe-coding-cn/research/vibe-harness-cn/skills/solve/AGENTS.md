# solve Skill

`skills/solve/` 是 Problem-Solving Operator Architecture 的可移植 Skill 包：用短指令引导 AI
按需读取问题求解算子，不把算子库变成提示词堆，也不直接执行任何外部动作。

## 目录与依赖

```text
solve/
├── AGENTS.md                                      # 本包职责、依赖和边界
├── README.md                                      # 安装、刷新和使用说明
├── SKILL.md                                       # AI 激活规则与最小调用契约
├── VERSION                                        # 包版本
├── CHANGELOG.md                                   # 版本变更与验证记录
└── references/
    ├── index.md                                   # 延迟加载入口和文件索引
    ├── selection-protocol.md                      # 候选选择、停止和切换
    ├── output-contract.md                         # 结果与证据标签
    ├── quality-checklist.md                       # 发布前质量门禁
    ├── problem-solving-operator-pack.schema.json  # 本包可独立校验的 Core Schema 副本
    ├── catalog.json                               # 56 个 pack、计数和引用入口
    ├── source-inventory.json                      # 417 个 source 的完整性基线
    ├── taxonomy/problem-solving-methodology.json  # 母领域与功能分类双轴索引
    ├── packs/*.json                               # 56 个领域 pack，417 source + 60 derived
    └── pressure-scenario.md                       # Skill 边界压力场景
```

依赖方向是 `operators/` 内容发布到 `references/`，`SKILL.md` 再按任务读取 catalog、taxonomy 和
少量相关 pack。`references/catalog.json` 中的路径均相对于 catalog 所在目录，安装后无需回到仓库根目录。

## 单一真相源

- 内容真相源：`operators/catalog.json`、`operators/source-inventory.json`、`operators/taxonomy/` 和
  `operators/packs/`。
- 契约真相源：`contracts/problem-solving-operator-pack.schema.json`；本包中的 schema 只是同版本副本。
- 本包是发布快照，不得在包内手工改写算子内容；刷新时先校验源库，再整体替换 references 快照并更新版本。

## 明确不负责

本包不选择或执行工具，不授予权限，不保存密钥、业务会话、运行状态或结果，不把 `experimental` 条目
包装成已验证结论。医学、法律、化学安全和其他高风险问题只能得到方法论参考，必须升级到适当的人类或
专业审查流程。

形式证明证据按能力集合管理：source、build、kernel、semantic/reviewer 等能力分别留回执，任何较弱能力
都不能替代较强能力；声明、候选和接纳结果必须保持独立身份。

## 验证

```bash
bash <codex-home>/skills/workflow/modules/skill-authoring/scripts/validate-skill.sh skills/solve --strict
uv run --locked --script scripts/validate_harness.py --operator-library skills/solve/references/catalog.json
```

目录职责改变时同步更新根 `AGENTS.md`、`README.md`、`governance/context/CONTEXT-MAP.md` 和本文件。
