# solve Skill

`solve` 是 Vibe Harness CN 的可移植问题求解 Skill。它把跨学科方法论以“按需检索的参考库”形式提供给
AI，而不是把方法写成一组不可审计的长提示词。

## 快速认识

| 项目 | 内容 |
|---|---|
| Skill 名称 | `solve` |
| 当前版本 | `0.3.0` |
| 用途 | 选择、执行和复盘问题求解方法 |
| 内容规模 | 56 个 pack；417 source + 60 derived = 477 条目 |
| 状态 | `experimental` / reference-only |
| 内容真相源 | 仓库根 `operators/` |

## 包结构

```text
skills/solve/
├── SKILL.md                         # AI 如何触发和使用
├── VERSION                          # 包版本
├── CHANGELOG.md                     # 发布记录
└── references/
    ├── index.md                     # 加载入口
    ├── selection-protocol.md        # 候选选择、停止和切换
    ├── output-contract.md           # 结果与证据标签
    ├── quality-checklist.md         # 发布前质量门禁
    ├── pressure-scenario.md         # 触发、边界和误用压力场景
    ├── catalog.json                 # pack 注册
    ├── source-inventory.json        # 完整性清单
    ├── taxonomy/                    # 双轴分类
    ├── packs/                       # 56 个内容包
    └── *.schema.json                # Core Schema 副本
```

## 安装和使用

将整个 `skills/solve/` 目录复制到目标 AI Harness 的 Skill 目录，并让宿主读取 `SKILL.md`。安装后，
包内 `references/` 已包含完整内容，不依赖本仓库路径；宿主仍必须自行提供模型、工具、权限、状态和验证器。

典型流程是：读取 `SKILL.md` → 形成 `goal/state/constraints/success/risk` → 读取 catalog/taxonomy →
只打开相关 pack → 检查前置条件 → 产出证据和下一步。不要默认加载全部 JSON，也不要让算子文本直接执行副作用。

遇到形式证明或多门验收时，先分开声明、候选与结果，再把源码、构建、kernel、语义审查等要求写成
不可互相替代的证据能力集合；缺哪项就报告哪项，不从较弱证据向较强结论跳级。

## 刷新发布副本

`operators/` 是唯一内容真相源。内容更新时，应先运行：

```bash
uv run --locked --script scripts/validate_harness.py --operator-library operators/catalog.json
```

然后在受控发布变更中整体刷新 `references/`，确认 catalog 的相对路径、条目计数、文件数量和哈希一致，
更新 `VERSION` 与 `CHANGELOG.md`，最后执行 [`references/quality-checklist.md`](references/quality-checklist.md)、
Skill strict 校验和包内 library 校验。不要只手改某个 pack。

## 边界

`solve` 不包含 selector、planner、tool binding、权限执行、在线 registry、数据库、业务会话或结果状态。
它提供的是可审计的思考方法参考；高风险专业问题必须由宿主策略和人类/专业人员负责。
