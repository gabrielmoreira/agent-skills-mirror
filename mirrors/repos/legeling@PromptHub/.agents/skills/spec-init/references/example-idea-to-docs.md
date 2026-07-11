# 从想法到文档的一个最小例子

这个例子用来说明，同一个想法在不同文档里应该写成什么样。

## 原始想法

“我想做一个帮助自由职业者管理发票和回款提醒的小工具。”

这句话还不能直接拿去写代码，因为它没有把目标、边界、方案、验证方式和默认规则拆开。

## 1. 写进 `docs/workflow/00-intake/README.md`

这里先写问题，不写方案：

- 背景：自由职业者通常用表格或聊天记录管理发票，容易漏记和忘记催款
- 目标用户：独立设计师、开发者、顾问
- 目标：降低漏开票和漏催款的概率
- 非目标：不做报税系统，不接入复杂财务总账
- 成功标准：用户可以在一个页面看到待收款发票，并在到期前收到提醒

## 2. 写进 `docs/workflow/01-requirements/README.md`

这里写交付目标，不写技术选型：

- `FR-001` 用户可以创建、编辑、归档发票
- `FR-002` 用户可以为发票设置到期日和提醒时间
- `FR-003` 用户可以查看“未收款 / 已逾期 / 已收款”状态
- `NFR-001` 核心页面在移动端可用
- `AC-001` 当用户保存发票后，列表中应立即显示该发票的金额、客户、到期日和状态

注意：这里还不能写“用 React”“用 SQLite”“建 invoice 表”。

## 3. 写进 `docs/workflow/02-design/README.md`

这里开始写 how：

- `DES-001` 发票模块负责创建、更新、归档与状态流转
- `DES-002` 提醒模块负责根据到期日计算提醒窗口并触发通知
- 数据模型建议包含：`invoice`、`client`、`reminder_rule`
- 接口契约示例：`create invoice` 输入客户、金额、到期日，输出发票 ID 与当前状态
- 风险：提醒调度如果完全依赖浏览器定时器，可能在用户离线时失效

注意：这里才适合写模块、数据结构、接口边界和技术权衡。

## 4. 写进 `docs/workflow/04-verification/README.md`

这里写如何验证：

- `TEST-001` 单元测试：金额、税费、到期状态计算规则
- `TEST-002` 集成测试：创建发票后可以在列表读取到正确状态
- `TEST-003` 集成测试：修改到期日后提醒规则同步更新
- `TEST-004` 端到端测试：用户创建一张即将到期的发票后，在提醒视图中可见
- 回归要求：任何与发票状态计算相关的 bug fix，都要补回归测试

如果项目进入长期维护阶段，应继续拆分：

- `01-test-strategy-and-quality-gates.md`: 发票金额、状态、提醒属于 P0/P1 业务链路，必须有失败路径和回归门禁
- `02-test-standards.md`: 金额计算测试必须断返回值、持久化状态和提醒副作用
- `03-test-design-methodology.md`: 使用边界值覆盖 0 元、最大金额、到期日前后；用状态机覆盖未收款、已逾期、已收款
- `04-test-case-matrix.md`: 登记 `TEST-INVOICE-001` 到 `TEST-INVOICE-004`
- `05-regression-suite.md`: 发票状态或提醒规则变化时必跑 invoice service 和 reminder integration tests
- `06-test-data-and-fixtures.md`: 固定客户、发票、到期日和提醒规则 fixtures
- `07-coverage-map.md`: 标记发票创建、状态计算、提醒更新的覆盖状态和缺口

## 5. 写进 `docs/workflow/05-tasks/README.md`

这里写可执行动作：

- `T-001` 定义发票领域模型并补金额计算单元测试
- `T-002` 实现发票创建接口并补保存成功 / 失败集成测试
- `T-003` 实现发票状态流转规则并补逾期路径测试
- `T-004` 实现提醒规则更新逻辑并补回归测试

## 6. 写进 `docs/knowledge/`

这里写长期稳定真相，而不是本轮任务：

- `docs/knowledge/context/README.md`: 自由职业者、发票、回款、提醒等核心术语与角色
- `docs/knowledge/behavior/README.md`: 发票状态如何从“未收款”变成“已逾期”或“已收款”

## 7. 写进 `docs/changes/active/<change-key>/`

这里写这次变更工作区：

- 为什么这次要补发票提醒
- 影响了哪些需求、设计和验证

## 8. 做一次分析门禁

任务拆完、实现前先检查：

- `FR-001` 是否有对应 `AC-*`、`DES-*`、`TEST-*`、`T-*`
- 发票状态流转是否同时出现在 requirements、design、verification 和 knowledge 中，且没有互相矛盾
- 是否还有阻塞性的 `[待确认]`，例如提醒渠道、离线提醒策略、通知权限
- change workspace 是否记录了影响范围、验证计划和同步清单

如果发现缺口，先补文档或任务，再写代码。

## 9. 实现后做收敛检查

实现完成后把真实结果回写：

- 新增或改变的状态规则同步到 `docs/knowledge/behavior/README.md`
- 实际测试覆盖同步到 `docs/workflow/04-verification/README.md`
- 长期可复用的测试规范、用例、回归和覆盖缺口同步到 `docs/workflow/04-verification/01-*` 到 `07-*`
- 已完成任务更新到 `docs/workflow/05-tasks/README.md`
- 本轮 change 从 `active/` 移到 `completed/`，或说明为什么仍未完成
- 对外发布变化写入 `docs/releases/`，废弃说明写入 `docs/archive/`

## 10. 写进 `docs/rules/`

这里写默认做法，而不是业务需求：

- `docs/rules/testing-standards.md`: 规定高优先级需求必须有自动化验证
- `docs/rules/doc-sync-rules.md`: 规定发票状态流转规则变化时，必须同步更新 design、verification、tasks 和 knowledge
- `docs/rules/test-case-management.md`: 规定长期用例进入 verification 矩阵，bug 复测进入 issues

## 快速判断口诀

- 带“业务目标、用户收益”的句子，通常属于 workflow 的 intake 或 requirements
- 带“模块、接口、数据结构、技术方案”的句子，通常属于 workflow 的 design
- 带“长期成立的术语、角色、状态、规则”的句子，通常属于 knowledge
- 带“先做什么、后做什么、分几期”的句子，通常属于 implementation plan
- 带“如何验证、哪些测试”的句子，通常属于 verification plan
- 带“今天具体做什么动作”的句子，通常属于 task breakdown
- 带“这次为什么改、影响了什么”的句子，通常属于 changes
- 带“以后默认怎么做”的句子，通常属于 rules
