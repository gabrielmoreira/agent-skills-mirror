# SwiftlyS2-Toolkit

`SwiftlyS2-Toolkit` 是基于Copilot开发的面向 SwiftlyS2 插件开发的agent工具包。
我们的目标是使用该工具包时，您只需要一句话，即可让agent编写出高性能、高质量的SwiftlyS2插件代码。
如果您是其它类型的agent cli，可以使用本工具包内的skills+prompts。

- English Version：[`README.en.md`](./README.en.md)
- skill：[`SKILL.md`](./SKILL.md)

## 特点
- **提示词约束**: 通过精心设计的提示词，确保生成的代码符合SwiftlyS2插件开发的最佳实践和性能要求。
- **代码质量**: 生成的代码经过严格测试，确保其高性能和高质量。
- **易用性**: 只需一句话提示，便可生成符合要求的SwiftlyS2插件代码，极大地提高了开发效率。
- **自定义Agent**：提供`edit`、`plan`、`review`三种自定义agent，满足不同开发阶段的需求。
- **skill索引**：使agent轻松查找swiftlys2相关的官方文档、社区资源和代码示例，确保生成的代码符合最新的开发规范和最佳实践。
- **经验来源**: 结合了官方文档、提取自大量原创插件的精华部分（10+原创小型插件，10+原创中型插件，3+原创大型插件）
- **稳定性**: 经过相当长时间的测试和迭代，使用该工具包生成的插件代码，每天会服务超过数千名玩家，且不容易出现服务器崩溃和性能问题

## 里面有什么

- `SKILL.md`：总入口和使用边界
- `prompts/`：`plan`、`audit`、`edit` 三类工作流提示词
- `references/`：公开知识索引、官方文档导航
- `assets/`：模板、检查清单和工作流资产

## 从哪里开始

### `plan`

适合让agent先想输出执行计划的场景，比如：

- 方法级实施计划
- 改动前方案拆解
- 迁移 / 重构 / 行为对齐计划

### `audit`

适合让agent先看审核插件代码的场景，比如：

- 架构、线程、生命周期、性能、行为漂移审计
- 需要先诊断、再落地的任务

### `edit`

适合目标明确、希望agent直接开工的场景，比如：

- 直接修改代码
- 一次对话内完成定位、修改、验证闭环

## 知识库索引

### `references/swiftlys2-plugin-playbook.md`

偏工程经验，适合快速判断：

- 这个任务更像哪一类插件
- 生命周期和线程边界在哪里
- Hook / Schema / NetMessages / Menu / Worker 这类子系统该怎么处理

### `references/swiftlys2-kb-index.md`

偏公开知识导航，适合快速找：

- 官网文档入口
- sw2-mdwiki 入口
- 官方仓库结构入口

### `references/swiftlys2-official-docs-map.md`

偏官方文档的精简导航，适合快速看：

- Development / Guides 的结构
- API Reference 的关键入口
- 哪些页面值得继续深挖

### `references/swiftlys2-asset-inventory.md`

偏工具包资产总览，适合快速知道：

- 这里有哪些可复用入口
- 哪些属于核心资产

### `assets/README.md`

- 官方主题 → 本地资产 → 适用场景总导航

## 可信来源

为了让公共文档保持一致，我们默认只引用这些来源：

- SwiftlyS2 官网文档：`https://swiftlys2.net/docs/`
- sw2-mdwiki：`https://github.com/himenekocn/sw2-mdwiki`
- SwiftlyS2 官方仓库：`https://github.com/swiftly-solution/swiftlys2`

如果你有自己的本地参考仓库、工作区项目映射、历史参考项目或定制实施经验，请把它们放到：

- `../../copilot-instructions.md`
- `../../knowledge-base.md`

建议把 sw2-mdwiki 项目部署到本地工作空间里，作为本地参考仓库，检索会快很多，也更容易和工具包保持一致。

## 可复用资产

- `assets/development/*`：按 SwiftlyS2 官网 Development 对齐的模板和 checklist
- `assets/guides/*`：按 Guides 对齐的模板和说明
- `assets/patterns/background-workers/worker-template.cs.md`：后台 worker 模式骨架
- `assets/workflows/planning/*`：方法级计划模板
- `assets/workflows/audit/*`：审计报告模板

## 贡献
- 欢迎提交PR，或在issue里分享你的使用经验和改进建议！

## 感谢
- SwiftlyS2团队
- sw2-mdwiki项目
