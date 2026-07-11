# 文档边界速查

这个文件用来帮开发者区分“需求”“设计”“实现计划”“测试计划”“任务拆解”和“项目规则”。

## 一句话区分

- project intake: 这个问题值不值得做
- requirements: 要做成什么
- design: 打算怎么做
- implementation plan: 先做什么后做什么
- verification plan: 如何证明做对了
- tasks: 现在具体做哪一步
- analysis gate: 开工前检查 spec、design、verification、tasks 是否一致
- convergence: 完成后把代码现状、当前文档和变更历史重新对齐
- rules: 项目默认遵循什么工程规范

## 速查表

| 文档 | 回答的问题 | 应该写 | 不该写 | 完成标志 |
|---|---|---|---|---|
| `docs/workflow/00-intake/README.md` | 这件事为什么值得做 | 背景、用户、场景、目标、非目标、约束 | 具体技术选型、数据库表、接口实现 | 团队能说清项目边界 |
| `docs/workflow/01-requirements/README.md` | 我们要交付什么 | 用户故事、FR、NFR、AC、范围外 | React/Next.js/Postgres、类名、表名、接口细节 | 别人不看代码也知道最终要交付什么 |
| `docs/workflow/02-design/README.md` | 当前阶段怎么交付 | 架构、模块、数据、接口、权衡、风险 | 再重复背景、列很碎的执行任务 | 工程师知道该怎么搭当前结构 |
| `docs/knowledge/context/README.md` | 长期稳定的业务真相是什么 | 术语、角色、实体、业务边界 | 当前版本任务安排 | 长期背景不会只靠聊天留存 |
| `docs/knowledge/structure/README.md` | 长期稳定的系统结构是什么 | 模块边界、集成关系、数据边界 | 短期排期 | 后来人知道系统骨架 |
| `docs/knowledge/behavior/README.md` | 长期稳定的关键行为是什么 | 流程、状态流转、规则、异常路径 | 临时 patch 说明 | 关键逻辑不会反复口述 |
| `docs/knowledge/reference/README.md` | 有哪些固定参考资料 | 协议、schema、样例、素材、fixtures | 临时讨论 | 常用参考资料有固定落点 |
| `docs/workflow/03-implementation/README.md` | 先做什么 | 里程碑、依赖、风险优先级、交付顺序 | 太细的函数名、临时思考记录 | 团队知道实施节奏 |
| `docs/workflow/04-verification/README.md` | 怎么证明完成 | 测试层次、需求到测试映射、首批失败测试、回归策略 | 技术选型争论、产品背景 | 团队知道如何验证 |
| `docs/workflow/04-verification/01-test-strategy-and-quality-gates.md` | 默认测试策略是什么 | 测试层级、质量门禁、准出标准、高风险触发条件 | 单次测试日志 | 团队知道什么时候必须补哪些验证 |
| `docs/workflow/04-verification/02-test-standards.md` | 测试应该怎么写 | 命名、断言、隔离、Mock、失败路径、报告规则 | 模块业务愿景 | 测试代码质量和失败信息可控 |
| `docs/workflow/04-verification/03-test-design-methodology.md` | 如何设计测试 | 等价类、边界值、状态机、决策表、安全、并发、契约、回归方法 | 某次命令输出 | 高风险需求能推导出有效测试 |
| `docs/workflow/04-verification/04-test-case-matrix.md` | 有哪些长期用例 | TEST-ID、模块、优先级、层级、状态、覆盖对象 | 临时调试步骤 | 模块级测试资产可检索 |
| `docs/workflow/04-verification/05-regression-suite.md` | 哪些回归必须跑 | 回归套件、触发条件、命令登记规范、残余风险 | 每次完整日志 | 变更前后知道该跑什么 |
| `docs/workflow/04-verification/06-test-data-and-fixtures.md` | 测试数据如何管理 | fixtures、H2/Redis、外部依赖替身、脱敏和随机规则 | 生产数据明文 | 测试可重复且不污染环境 |
| `docs/workflow/04-verification/07-coverage-map.md` | 现有覆盖和缺口在哪里 | 模块、需求、设计、测试资产、缺口和补强队列 | 测试进度流水账 | 后续补测试能按风险排序 |
| `docs/workflow/05-tasks/README.md` | 现在做什么 | 可执行任务、依赖、关联文档 ID | 抽象口号、无法验收的描述 | 任务可以被直接执行 |
| `docs/changes/active/<change-key>/` | 这次为什么变、影响什么 | 变更背景、设计调整、验证、任务、影响范围 | 项目长期真相 | 单次 change 可被完整追踪 |
| 分析门禁 | 当前 spec 是否能安全进入实现 | 孤立 ID、缺失映射、冲突、阻塞性待确认、文档边界错误 | 新需求或新设计 | 没有阻塞实现的一致性缺口 |
| 收敛检查 | 实现后哪些文档和记录必须回写 | 代码真实行为、验证结果、change 生命周期、README/AGENTS/ADR/release 同步 | 新功能愿景 | 当前真相、历史记录和代码一致 |
| `docs/rules/` | 默认如何工作 | 编码、测试、文档同步、完成定义规则 | 具体业务需求细节 | 团队默认规则已沉淀到项目内 |

## 常见混淆

### 1. 需求不是设计

错误写法：

- “系统使用 Next.js + PostgreSQL + Prisma 实现用户登录。”

为什么错：

- 这已经在说“怎么做”，不是“要做什么”。

正确拆分：

- requirements 里写：“用户可以使用邮箱和密码完成注册、登录、退出，并在忘记密码时重置账户访问权。”
- design 里写：“鉴权服务采用 [待定方案]；用户实体包含 [字段]；密码使用单向哈希存储。”

### 2. 设计不是任务清单

错误写法：

- “先创建 `auth.service.ts`，再写 `loginController`，再接数据库。”

为什么错：

- 这是执行顺序，不是设计。

正确拆分：

- design 里写：“认证模块负责身份校验、令牌签发与会话失效。”
- implementation plan 里写：“里程碑 1 完成鉴权领域模型与接口；里程碑 2 接入持久化。”
- tasks 里写：“T-003 实现邮箱密码登录接口并补充失败路径测试。”

### 3. verification 计划不是测试代码

错误写法：

- “后面补 pytest。”

为什么错：

- 这不是计划，只是拖延。

正确写法：

- “FR-003 对应单元测试：密码校验规则；集成测试：登录接口成功 / 失败路径；回归测试：密码重置后旧令牌失效。”

进一步拆分：

- 长期测试层级和准出标准写入 `01-test-strategy-and-quality-gates.md`
- 测试代码写法写入 `02-test-standards.md`
- 测试设计方法写入 `03-test-design-methodology.md`
- 长期模块用例写入 `04-test-case-matrix.md`
- 必跑回归集合写入 `05-regression-suite.md`
- fixtures 和测试数据规则写入 `06-test-data-and-fixtures.md`
- 覆盖现状和缺口写入 `07-coverage-map.md`

### 4. rules 不是聊天约定

错误写法：

- “这个项目以后都要先补测试，大家记一下。”

为什么错：

- 规则只在聊天里，后续成员和 agent 都看不到。

正确写法：

- 把默认规则写进 `docs/rules/testing-standards.md` 或 `docs/rules/doc-sync-rules.md`。

## 推荐写作顺序

1. 先写 `docs/workflow/00-intake/README.md`
2. 再写 `docs/workflow/01-requirements/README.md`
3. 再写 `docs/workflow/02-design/README.md`
4. 把长期稳定真相写进 `docs/knowledge/`
5. 设计稳定后写 `docs/workflow/03-implementation/README.md`
6. 开工前写 `docs/workflow/04-verification/README.md`，并按需要补齐测试策略、测试标准、测试设计、用例矩阵、回归套件、测试数据和覆盖映射
7. 最后拆 `docs/workflow/05-tasks/README.md`
8. 为当前工作建立 `docs/changes/active/<change-key>/`
9. 做一次分析门禁，确认 `FR / DES / TEST / T / change` 没有冲突或缺口
10. 实现后做收敛检查，回写 workflow、knowledge、changes、issues、releases、archive、README、AGENTS
11. 再把长期有效的工程规则沉淀进 `docs/rules/`

## 一个简单判断法

当你不确定内容该写进哪份文档时，问自己：

- 这是在定义目标吗？放 workflow 的 intake 或 requirements。
- 这是在解释当前阶段方案吗？放 workflow 的 design。
- 这是长期稳定事实吗？放 knowledge。
- 这是在安排节奏吗？放 implementation plan。
- 这是在定义验证方式吗？放 verification plan。
- 这是在描述具体动作吗？放 tasks。
- 这是在检查文档之间是否一致吗？放到 tasks 自检、change impact 或最终交付说明里。
- 这是实现完成后的回写和归档吗？同步 workflow / knowledge / changes / records。
- 这是某一次具体变更吗？放 changes。
- 这是在定义项目默认做法吗？放 rules。

## 好的文档应该怎样衔接

- `FR-001` 出现在 `docs/workflow/01-requirements/README.md`
- `DES-001` 在 `docs/workflow/02-design/README.md` 说明如何满足 `FR-001`
- `TEST-001` 在 `docs/workflow/04-verification/README.md` 说明如何验证 `FR-001`
- 长期测试资产按职责拆到 `docs/workflow/04-verification/01-*` 到 `07-*`，避免把测试计划、测试用例、历史进展和调试步骤混成一份文件
- `T-001` 在 `docs/workflow/05-tasks/README.md` 关联 `FR-001`、`DES-001`、`TEST-001`
- 长期稳定的角色、结构或规则继续沉淀到 `docs/knowledge/`
- 项目默认约束写进 `docs/rules/`
- 实现前执行分析门禁，找出孤立需求、未承接设计、未验证需求、游离任务和阻塞性 `[待确认]`
- 实现后执行收敛检查，把代码真实行为、测试结果和 change 生命周期同步回文档
- 已完成的 change 必须从 `docs/changes/active/` 移到 `docs/changes/completed/`；如果还留在 active，就只能标记为“待收敛”或“阻塞”并写清原因

这样文档不是一堆孤立文件，而是一条可追踪的链路和一套可执行的工作规则。

## Spec Kit 阶段映射

`spec-init` 不要求生成 `specs/` 目录，但可以借鉴 Spec Kit 的阶段节奏：

| 阶段 | spec-init 写入位置 |
|---|---|
| specify | `00-intake` + `01-requirements` |
| clarify | intake / requirements 的待确认区，必要时进入 `docs/issues/` |
| plan | `02-design` + `03-implementation` + `04-verification` + `docs/knowledge/` |
| tasks | `05-tasks` + `docs/changes/active/<change-key>/tasks.md` |
| analyze | 任务生成后、实现前的一致性分析 |
| implement | 代码、测试、迁移、脚本等真实改动 |
| converge | 实现后回写当前文档、变更生命周期和 records |
