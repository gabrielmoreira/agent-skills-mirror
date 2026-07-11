---
name: spec-init
description: 面向新项目或现有项目的文档驱动开发 skill。Use when the user wants to create, 补齐, 更新, or refine project specs, run a Spec Kit-inspired workflow loop, maintain workflow/knowledge/change docs, analyze consistency, converge implementation back into docs, or update README/AGENTS for a real project.
---

# /spec-init — Agent 驱动的文档开发 skill

这个 skill 不是“帮用户创建一堆空模板”的脚手架，也不是“固定 Bash 初始化器”。

它的真正职责是：

- 先理解用户目标
- 先理解现有项目或上下文
- 通过 agent 的分析、追问、归纳和写作，产出真正可用的 spec
- 用 spec 驱动后续设计、实现、测试和文档同步
- 把 spec 当成持续演进的项目资产，而不是一次性启动产物

## 目标

- 帮用户把模糊想法整理成能执行的 spec
- 帮已有项目补齐缺失的 intake / requirements / design / verification / tasks / rules
- 帮用户区分 what / why / how / verify / do-next
- 形成至少一条完整追踪链：`FR -> DES -> TEST -> T`
- 在信息不足时主动提供候选方案、对比、建议，而不是只留下空白
- 帮用户逐步补全完整需求、完整设计、完整验证策略，而不是只停留在最小第一版
- 帮项目把测试策略、测试标准、测试设计、用例矩阵、回归套件、测试数据和覆盖映射拆成可维护文档，而不是把测试计划平铺成一份进展报告

## 核心定位

默认把这个 skill 当成“agent 写 spec 的工作流”，不是“脚本生成目录”。

优先级：

1. 理解用户和项目现状
2. 读代码 / 读文档 / 读目录结构
3. 澄清关键问题
4. 产出或更新有内容的 spec
5. 必要时才借助模板或脚本补齐基础结构

## 何时使用

- 用户说“帮我做 spec”“补需求文档”“整理设计文档”“先别写代码，先把文档理清”
- 用户有现成项目，想补齐或更新 `docs/`、`README.md`、`AGENTS.md`
- 用户想做文档驱动开发、spec-first、design-first、verification-first
- 用户想让 agent 帮他决定还缺哪些文档、哪些规范、哪些待确认问题

## 何时不要使用

- 用户只想要一个临时脚本、一次性 demo 或纯代码实现
- 当前任务只是修一个小 bug、补一条测试、做一次 review
- 用户明确不想做 spec，只要直接写代码

## 两种主要场景

### 场景 A：新项目

用户只有一个想法、方向或需求草稿。

你要做的是：

- 先把想法拆成 intake / requirements / design / verification / tasks
- 如果用户不懂概念，主动给方案、对比和建议
- 不要只生成空文件；至少把当前已知信息写进去

### 场景 B：现有项目

用户已经有代码或仓库，想完善、补齐或更新 spec。

你要做的是：

- 先读仓库结构、README、核心代码、现有 docs
- 找出当前真实行为、模块边界、依赖关系、缺失文档
- 基于现状写 spec，而不是凭模板猜一个“理想项目”
- 对已有项目优先增量补文档，不要粗暴覆盖

## 核心原则

- 不要把模板当结果，模板只是辅助。
- 文档必须反映当前项目真实情况或当前轮次的明确决策。
- 用户没有提到但又必须明确的内容，要主动提出候选方案和对比。
- 推荐可以给，但推荐不是确认；不要替用户拍板关键决策。
- 如果项目已存在，先读代码再写文档，不要反过来。
- 如果信息不全，写 `[待确认]`，但不要把整份文档都留空。
- spec 不是一次性文档；每轮需求变化、设计变化、实现变化后都要继续完善。

## Repository Profiles

When this skill runs inside the PromptHub repository, read and follow
`references/prompthub-profile.md` before choosing document paths or change
lifecycle semantics. The profile adapts upstream `docs/*` examples to
PromptHub's `spec/*` topology without weakening the upstream phase gates.

## 文档边界

先阅读并遵循：

- `references/doc-boundaries.md`
- `references/example-idea-to-docs.md`

边界如下：

- `docs/workflow/00-intake/README.md`: 为什么做，谁来用，什么不做
- `docs/workflow/01-requirements/README.md`: 做什么，为什么做，怎么验收
- `docs/workflow/02-design/README.md`: 当前阶段怎么实现，方案对比，规范约定
- `docs/knowledge/context/README.md`: 长期稳定的角色、术语、实体、业务边界
- `docs/knowledge/structure/README.md`: 长期稳定的模块边界、系统结构、集成关系
- `docs/knowledge/behavior/README.md`: 长期稳定的关键流程、状态流转、业务规则
- `docs/knowledge/reference/README.md`: 样例、协议、schema、素材、fixtures 等固定参考资料
- `docs/workflow/03-implementation/README.md`: 先做什么后做什么
- `docs/workflow/04-verification/README.md`: 怎么验证完成
- `docs/workflow/04-verification/01-test-strategy-and-quality-gates.md`: 长期测试策略、测试层级、质量门禁和准出标准
- `docs/workflow/04-verification/02-test-standards.md`: 测试代码命名、断言、隔离、Mock、失败路径和报告规则
- `docs/workflow/04-verification/03-test-design-methodology.md`: 等价类、边界值、状态机、决策表、安全、并发、契约和回归设计方法
- `docs/workflow/04-verification/04-test-case-matrix.md`: 模块级测试用例矩阵、优先级、层级、自动化状态和覆盖对象
- `docs/workflow/04-verification/05-regression-suite.md`: 长期回归套件、触发条件、命令登记规范和残余风险记录
- `docs/workflow/04-verification/06-test-data-and-fixtures.md`: 测试数据、fixtures、H2/Redis/外部依赖替身和脱敏规范
- `docs/workflow/04-verification/07-coverage-map.md`: 模块、需求、设计、测试资产和已知缺口之间的覆盖映射
- `docs/workflow/05-tasks/README.md`: 现在具体做什么动作
- `docs/issues/README.md`: 尚未解决的问题、阻塞项、风险和技术债
- `docs/changes/`: 这次为什么变、影响什么、同步了哪些文档和测试
- `docs/releases/`: 某个版本最终对外交付了什么
- `docs/archive/README.md`: 已归档、已替代、已废弃但仍需保留历史的文档
- `docs/adr/`: 关键架构或技术决策为什么改变
- `docs/rules/`: 默认工程规则

## Spec Kit 借鉴的阶段循环

这个 skill 保留自己的 layered docs 拓扑，但执行节奏借鉴 Spec Kit 的阶段化工作流：

| 阶段 | spec-init 落点 | 目标 |
|---|---|---|
| specify | `docs/workflow/00-intake/README.md`, `docs/workflow/01-requirements/README.md` | 把想法变成用户、边界、FR/NFR/AC |
| clarify | intake / requirements 的待确认区，必要时更新 `docs/issues/` | 只澄清会影响范围、架构、数据、权限、测试的关键问题 |
| plan | `docs/workflow/02-design/README.md`, `docs/workflow/03-implementation/README.md`, `docs/workflow/04-verification/README.md`, `docs/knowledge/` | 形成设计、实施顺序、验证策略和长期真相 |
| tasks | `docs/workflow/05-tasks/README.md`, `docs/changes/active/<change-key>/tasks.md` | 拆成可执行、可验证、可追踪的任务 |
| analyze | tasks 完成后、实现前，检查 requirements / design / verification / tasks / changes 是否冲突 | 找孤立 ID、缺失映射、未确认阻塞项和文档边界错误 |
| implement | 代码、测试、脚本、迁移等真实改动 | 只执行已能回链到 `FR -> DES -> TEST -> T` 的工作 |
| converge | 完成后回写 workflow、knowledge、changes、issues、releases、archive、README、AGENTS | 让代码现状、当前真相和历史变更记录重新一致 |

不要把这些阶段理解成必须生成 `specs/` 目录。`spec-init` 的长期文档源仍是当前项目的 `docs/` 拓扑。

## 默认工作流

### Step 0: 判断是“新项目”还是“现有项目”

先判断：

- 当前目录是否已有代码、配置、README、docs、测试
- 用户是要从零梳理，还是基于现状补齐 spec

如果是现有项目：

- 先读目录结构
- 先读 README / docs / 关键入口代码
- 先梳理真实调用链和模块边界

如果是新项目：

- 先整理用户目标和约束
- 再建立最小 spec 结构

### Step 0.1: 识别本轮意图

先判断这次请求更接近哪一类：

- 继续实施：主要推进 `tasks / verification / implementation`
- 新需求引入：主要更新 `requirements / design / knowledge / changes`
- 小改动：如果影响面有限，也要判断是否需要最小 change 记录
- bugfix：主要更新 `changes / verification / design`，必要时回写 requirements 和 knowledge
- 发布整理：主要更新 `releases / changes / README`
- 问题追踪：主要更新 `issues/`
- 文档清理：主要更新 `archive/` 并说明替代关系

不要把所有请求都当成“继续写任务”或“继续写代码”。

### Step 1: 先理解问题，不先写模板

至少收集或推断：

- 项目解决什么问题
- 目标用户是谁
- 为什么现在要做
- 当前阶段最重要的价值是什么
- 明确不做什么
- 约束是什么
- 当前最容易出错的假设是什么

如果用户要求的是“完整设计”或“完整需求”，还必须继续补齐：

- 主要用户角色与差异
- 端到端核心流程与异常流程
- 关键对象、状态、字段和关系
- 外部依赖、第三方系统、部署与运行约束
- 权限模型、审计要求、性能目标、安全边界
- 后续阶段可能扩展的模块和边界

如果用户是新手，主动给最小问题清单，不要只说“请补充更多信息”。

### Step 2: 信息不足时，主动给方案和选择

如果用户没有提到某个关键设计点，且这个点会影响 spec 质量：

- 给 2 到 3 个候选方案
- 写清适用场景、优点、代价、风险
- 给出推荐意见
- 明确标注“推荐”而不是“已确认”

特别要覆盖：

- Web：SPA / SSR / Hybrid，设计系统是否已有，移动端还是桌面优先
- API / Service：单体 / 模块化单体 / 多服务，认证方式，数据库与错误模型
- CLI：仅文本输出还是文本 + JSON，人工优先还是自动化优先

### Step 3: 产出有内容的 spec

按顺序产出或更新：

1. `docs/workflow/00-intake/README.md`
2. `docs/workflow/01-requirements/README.md`
3. `docs/workflow/02-design/README.md`
4. `docs/knowledge/context/README.md`
5. `docs/knowledge/structure/README.md`
6. `docs/knowledge/behavior/README.md`
7. `docs/knowledge/reference/README.md`
8. `docs/workflow/03-implementation/README.md`
9. `docs/workflow/04-verification/README.md`
10. `docs/workflow/05-tasks/README.md`
11. `docs/issues/`（当存在未决问题、阻塞、技术债、已知风险时）
12. `docs/changes/active/<change-key>/`（当本轮是新需求、bugfix、重构、流程变更时）
13. `docs/releases/`（当本轮涉及版本发布或对外变更总结时）
14. `docs/archive/`（当旧文档需要废弃但仍需保留历史时）
15. `docs/rules/`
16. 必要时更新 `README.md` / `AGENTS.md` / `spec-init.topology.yml`

要求：

- 不要只写标题
- 至少填入当前轮次已知信息
- 新手场景下要包含示例、对比、错误示例、范围裁剪建议
- 如果用户希望做完整设计，就不要只停在“一条主流程”，要继续补角色、异常流、数据边界、规则和质量目标

### Step 3.1: 完整需求要求

当用户要的不是“占位 spec”而是“完整需求”时，requirements 至少覆盖：

- 主要用户角色和目标差异
- 关键业务流程和异常流程
- 功能需求、非功能需求、验收标准
- 数据或资源边界
- 权限、合规、审计、性能、安全要求
- 明确范围外内容
- 待确认问题和决策依赖

不要只写一个首页或一个接口就停住，除非用户明确说只整理最小范围。

### Step 3.2: 完整设计要求

当用户要“完整设计”时，design 至少覆盖：

- 系统边界与模块边界
- 核心调用链和异常链路
- 数据模型 / 资源模型 / 状态流转
- 接口契约与错误模型
- 权限模型与安全边界
- 性能、可维护性、可测试性目标
- 技术栈候选方案、权衡和推荐
- 已确认项与 `[待确认]` 分离记录

不要把 design 简化成“推荐某个框架”或“先做哪几个页面”。

### Step 4: 如果是现有项目，spec 必须回写真实现状

对现有项目：

- requirements 要基于真实用户流程或真实模块能力
- design 要基于真实调用链、目录结构、接口、数据边界
- verification 要基于真实风险路径和真实现有测试空缺
- tasks 要基于当前最有价值的后续动作，不是模板动作

### Step 5: 建立追踪链

在结束前显式检查：

- `FR-* -> AC-*`
- `FR-* -> DES-*`
- `FR-* -> TEST-*`
- `FR-* / DES-* / TEST-* -> T-*`

至少形成一条完整链：

```text
FR-001 -> DES-001 -> TEST-001 -> T-001
```

如果项目已经比较完整，不要只满足“至少一条链”。要尽量把高优先级需求都接入追踪链，而不是停在最小演示状态。

### Step 5.1: 持续完善循环

spec 应该随着项目推进不断完善。每轮需求澄清、设计决策、实现变更、测试补强后，都要检查：

- `docs/workflow/01-requirements/README.md` 是否需要补新需求或修正边界
- `docs/workflow/02-design/README.md` 是否需要补新模块、新约定或新的异常链路
- `docs/knowledge/` 是否需要补新的长期稳定真相
- `docs/workflow/04-verification/README.md` 是否需要补新的测试映射和回归策略
- `docs/workflow/04-verification/01-test-strategy-and-quality-gates.md` 是否需要更新测试层级、质量门禁或准出标准
- `docs/workflow/04-verification/02-test-standards.md` 是否需要更新测试代码、断言、隔离或 Mock 规则
- `docs/workflow/04-verification/03-test-design-methodology.md` 是否需要新增测试设计方法或模块风险模板
- `docs/workflow/04-verification/04-test-case-matrix.md` 是否需要登记新的长期测试用例
- `docs/workflow/04-verification/05-regression-suite.md` 是否需要更新回归套件和触发条件
- `docs/workflow/04-verification/06-test-data-and-fixtures.md` 是否需要沉淀新的 fixtures 或测试数据规则
- `docs/workflow/04-verification/07-coverage-map.md` 是否需要更新模块覆盖状态和测试缺口
- `docs/workflow/05-tasks/README.md` 是否需要把新发现的工作拆成任务
- `docs/issues/` 是否需要新增未解决问题、阻塞项、风险或技术债
- `docs/changes/` 是否需要新增或移动一个 change workspace
- `docs/releases/` 是否需要补一条版本说明
- `docs/archive/` 是否需要归档被替代、已作废或不再生效的文档
- `README.md`、`AGENTS.md`、`docs/rules/`、`spec-init.topology.yml` 是否需要同步

不要把 spec 当成“初始化时写一次，以后不更新”的静态文档。

### Step 5.2: 变更记录规则

把文档分成四层：

- workflow：`intake / requirements / design / implementation / verification / tasks`
- knowledge：`context / structure / behavior / reference`
- changes：`active / completed / legacy`
- records：`issues / adr / releases / archive / rules`

默认规则：

- 新需求：更新 workflow 与 knowledge 中受影响的文档，并新增 `docs/changes/active/<change-key>/`
- bugfix：更新受影响的 workflow / knowledge 文档，并新增 `docs/changes/active/<change-key>/`
- 架构 / 技术决策变化：更新 design 和 knowledge/structure，并新增或补充 `docs/adr/`
- 版本发布：新增或更新 `docs/releases/vx.y.z.md`
- 长期未解决的问题、阻塞项或技术债：写入 `docs/issues/`
- 被替代、废弃或仅保留历史价值的文档：放入 `docs/archive/` 并记录替代关系

不要只改当前状态不留痕，也不要只写变更记录却不更新当前状态。

### Step 5.3: 分析与收敛门禁

在任务拆完、准备实现前，必须做一次一致性分析：

- requirements 里每条高优 `FR-*` 是否有 `AC-*`
- design 里是否有对应 `DES-*` 承接高优 `FR-*`
- verification 里是否有对应 `TEST-*` 验证高优 `FR-*`
- tasks 里是否有可执行 `T-*` 串起 `FR / DES / TEST`
- `docs/changes/active/<change-key>/` 是否记录了本轮背景、影响、验证和同步清单
- 高风险变更是否已经补测试设计、失败路径、回归触发条件和残余风险记录
- 新增长期测试资产是否已经进入测试用例矩阵、回归套件、测试数据规范或覆盖映射
- 是否仍存在阻塞性 `[待确认]`
- 是否把需求、设计、任务、长期知识或变更历史写错了位置

实现完成后，必须做一次收敛检查：

- 代码真实行为是否和 requirements / design / verification 一致
- 新增测试和回归验证是否已经写回 verification
- 新增或变化的测试规范、测试设计、用例矩阵、回归套件、测试数据和覆盖缺口是否写回 verification 的对应细分文档
- 新发现的长期真相是否进入 `docs/knowledge/`
- 本轮 change 是否应该继续 active、移动到 completed，或转成 legacy
- 发布、问题、ADR、归档、README、AGENTS 是否需要同步

完成状态的 change 不允许继续留在 `docs/changes/active/`：

- 如果任务、验证、同步清单和收敛回写都完成，必须把整个 `docs/changes/active/<change-key>/` 移到 `docs/changes/completed/`（项目启用年月归档时使用 `docs/changes/completed/YYYY/MM/<change-key>/`）
- 如果暂时不能移动，不能把状态写成“已完成 / completed”；必须保持“待收敛 / needs convergence”或“阻塞 / blocked”，并在 `overview.md` 或 `impact.md` 写清剩余条件
- 移动后必须同步 `docs/changes/README.md` 索引、提交引用路径，以及必要的 releases / issues / ADR / archive 记录

如果分析或收敛发现缺口，先补文档和任务，再继续实现或交付。

### Step 6: 脚本和模板的正确位置

`scripts/spec-init.sh` 和 `assets/templates/project/` 只是辅助资源，不是主工作流。

仅在以下情况才优先使用它们：

- 用户明确要一个基础文档目录结构
- 当前目录几乎为空，先补一个最小文档骨架更高效
- 宿主环境不方便由 agent 逐文件创建基础目录

即使使用了脚本，也必须继续：

- 读上下文
- 补内容
- 写方案对比
- 更新真实 spec

不能把“脚本跑完”当成任务完成。

## 新手支持要求

如果用户不懂概念或没有说全：

- 不能只抛空模板
- 必须主动给示例答案
- 必须主动给范围裁剪建议，但不能只会做范围裁剪
- 必须主动给常见错误示例
- 必须主动给关键方案对比
- 必须在用户继续追问时，能够把最小草稿继续完善成完整需求和完整设计

## 现有项目支持要求

如果用户说：

- “我有一个项目，想补 spec”
- “我想给现有项目完善 requirements / design”
- “代码已经有了，但文档没跟上”

你必须：

- 先读项目
- 先理解现状
- 再写 spec

不要假设这是“初始化项目”。

## 输出要求

最终回复优先说明：

- 这次是新项目梳理还是现有项目补文档
- 读取了哪些现有上下文
- 创建或更新了哪些 spec 文件
- 哪些地方是根据现状整理出来的
- 哪些地方仍然是 `[待确认]`
- 已形成哪些 `FR -> DES -> TEST -> T` 追踪链
- 分析门禁发现了哪些缺口，以及实现后如何收敛文档

## 质量要求

- 文档要能直接用于后续开发，而不是“占位 markdown”
- 方案对比要真实可决策，而不是摆样子
- 不能把实现细节提前写进 requirements
- 不能把任务清单混进 design
- 不能把“后面补测试”当 verification 计划
- 不能把测试计划、测试标准、测试用例、历史进展、调试步骤和覆盖映射混写在一份平铺文档里
- 对高风险变更，verification 必须写清测试层级、测试设计方法、失败路径、回归触发条件、实际命令和残余风险
- 对已有项目，不能写出和代码现状冲突的 spec
- 对用户要求“完整设计”的场景，不能只给最小骨架或最小示例后就停止
- 对新需求、bugfix、发布等场景，必须明确当前状态文档和历史变更文档分别怎么更新
- 对未解决问题和废弃文档，也必须明确应该进入 `issues/` 还是 `archive/`

## 参考资源

- `references/doc-boundaries.md`: 文档边界
- `references/example-idea-to-docs.md`: 从想法到 spec 的最小示例
- `assets/templates/project/`: 可选模板资源
- `scripts/spec-init.sh`: 可选目录骨架脚本
- `examples/demo-app/`: 最小示例项目

优先把这些资源当参考和辅助，不要把它们当最终交付物。
