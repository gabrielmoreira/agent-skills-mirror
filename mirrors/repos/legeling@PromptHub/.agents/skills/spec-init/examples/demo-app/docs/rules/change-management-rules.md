# 变更管理规则

## 职责边界

- 本文件负责：变更工作区、变更生命周期、当前状态文档和历史记录之间的关系。
- 本文件不负责：提交正文格式；那部分见 `commit-rules.md`。文档路径和归档编号见 `document-routing-rules.md` 与 `document-archive-rules.md`。

## 基本原则

- 当前状态文档和历史变更文档必须同时维护。
- 新需求、bugfix、重构、发布，不允许只改代码不留文档痕迹。

## 记录规则

- 新需求或需求变化：更新当前状态文档（workflow）与长期知识（knowledge）中受影响内容，并在 `docs/changes/active/<change-key>/` 建立工作区
- bug 修复：更新受影响文档，并在 `docs/changes/active/<change-key>/` 记录症状、根因、验证和影响范围
- 架构或关键技术变化：更新 `docs/workflow/02-design/README.md`、`docs/knowledge/structure/README.md`，并补 `docs/adr/`
- 版本发布：新增或更新 `docs/releases/vx.y.z.md`
- 实现前：完成一致性分析（analyze），确认 `FR / DES / TEST / T` 和变更工作区没有冲突
- 实现后：完成文档收敛（converge），确认代码真实行为、验证结果和文档一致
- 变更完成后：把工作区移动到 `docs/changes/completed/`
- 提交变更时：遵循 `docs/rules/commit-rules.md`，在提交正文中关联 Issue、变更工作区、需求 / 设计 / 验证文档，并记录修改范围、影响范围和测试状态

## 生命周期门禁

- `docs/changes/active/<change-key>/` 只存放仍在推进、阻塞或待收敛的变更。
- 当任务全部完成、验证结果已记录、同步清单已勾选、实现后文档收敛已完成时，必须把整个工作区移入 `docs/changes/completed/`；如果启用了按年月归档，则移入 `docs/changes/completed/YYYY/MM/<change-key>/`。
- 不能只在 `overview.md` 里把状态写成“已完成”却继续留在 `active/`。
- 如果还有未跑验证、未同步文档、未关闭阻塞或未更新索引，状态必须保持“待收敛”或“阻塞”，并写清剩余条件。
- 移动后必须更新 `docs/changes/README.md` 索引和任何提交、release、issue、ADR 中引用的路径。

## 最低要求

- 每条 change 工作区必须写清背景、影响范围、同步文档和待确认项
- 每条 bug 记录必须写清症状、根因、修复方案和回归要求
- 每个 release 记录必须写清新增、修复、破坏性变化和已知问题
- 每轮实现前必须能说明一致性分析结论；每轮交付前必须能说明文档收敛结果
- 每轮交付前必须确认已完成 change 不再停留在 `docs/changes/active/`
- 每次提交必须只绑定一个主要改动点，并能回链到对应文档记录
