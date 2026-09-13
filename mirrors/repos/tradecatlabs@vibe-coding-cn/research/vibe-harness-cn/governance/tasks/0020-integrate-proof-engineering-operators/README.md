# Task Overview
- Task ID: `0020`
- Slug: `integrate-proof-engineering-operators`
- Objective: `把 FLT/Prove2Me 案例中的独立问题求解能力去重沉淀为算子与组合方法，刷新 solve Skill 并同步安装到 WSL/Windows Codex`
- Status: `Blocked`

## In Scope
- 用真实会话和数学项目形成九模型 crosswalk
- 新增 6 个 source、3 个 derived 并强化 3 个既有条目
- 同步 inventory、catalog、taxonomy、文档与治理
- 升级 solve Skill 至 0.3.0 并增加证明工程压力场景
- 同步并验证项目、WSL、Windows 三份 solve Skill

## Out of Scope
- 修改或执行 vibe-mathing-cn-internal
- 改变公共 Core Schema、权限、selector 或 runtime
- 宣称形式证明已 fresh replay、kernel 验证或独立语义审查
- 删除目标 Codex 目录中的其他 Skill 或额外文件

## Task Package Tree
- ROOT
  ├─ TP-01 [leaf] [P0] 锁定真实证据与九模型去重关系
  ├─ TP-02 [leaf] [P0] 沉淀算子与组合方法
  ├─ TP-03 [leaf] [P0] 升级自包含 solve Skill
  ├─ TP-04 [leaf] [P0] 同步 WSL 与 Windows Codex
  └─ TP-05 [leaf] [P0] 验证、审查与收口

## Requirement Alignment
- 目标: 把形式证明工程中的可复用能力沉淀进算子库与 solve Skill，并同步到两个 Codex 环境
- approved plan 顶层步骤数: 5
- 编译后节点总数: 5
- 编译后叶子节点数: 5
- 对齐项: 用户要求基于真实 Pi 会话和对应项目执行新增算子，而不是只给建议
- 对齐项: 用户明确要求更新现有 solve Skill，并同步到 WSL 与 Windows Codex
- 对齐项: 前序分析已将九模型去重为 6 个原子 source、3 个组合 Method，并识别 3 个强化点
- 计划摘要: 先锁定真实证据与九模型去重关系，再更新三类 pack 和索引，随后升级 solve Skill、同步双环境，最后完成全量验证与治理收口。

## Task Package Overview
| Task Package ID | Parent | Depth | Priority | Type | Leaf | Depends On | Wave | Ready | Parallelizable | Objective |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| TP-01 | ROOT | 1 | P0 | action | Yes | - | 1 | Yes | No | 把 Pi 会话、案例报告、数学项目契约和现有算子映射为可审计 crosswalk |
| TP-02 | ROOT | 1 | P0 | action | Yes | TP-01 | 2 | No | No | 将 6 个独立 source、3 个 derived 和 3 个强化点写入既有 Reference Library |
| TP-03 | ROOT | 1 | P0 | action | Yes | TP-02 | 3 | No | No | 刷新内嵌 Reference Library、版本、变更日志、选择说明和真实证明工程压力场景 |
| TP-04 | ROOT | 1 | P0 | action | Yes | TP-03 | 4 | No | No | 不删除额外文件地更新两个 solve 安装目录，并形成三份内容一致性回执 |
| TP-05 | ROOT | 1 | P0 | action | Yes | TP-04 | 5 | No | No | 同步文档与治理真相，运行全量门禁并记录 review、reuse 和 retro 结果 |

## Reading Order
1. README.md
2. CONTEXT.md
3. PLAN.md
4. ACCEPTANCE.md
5. ACCEPTANCE_CHECKLIST.md
6. TODO.md
7. STATUS.md
