---
name: testany-pipeline
description: Testany pipeline 编排与 CRUD - 基于 automation design 或现有 case keys 创建执行与编排单元
argument-hint: "[操作] [描述]，如：根据 decomposition 创建 pipeline、查看 Y2K-0001A、更新 relay 配置"
---

# Testany Pipeline

本 skill 通过 Testany MCP 工具管理 **Testany 平台上的 pipeline**。
所有操作都是对 Testany 平台的远程 API 调用，不涉及本地文件系统。

**关键前提**：
- pipeline 是 Testany 的**执行与编排单元**
- Testany **不支持直接执行单条 case**
- trigger 只是 pipeline 的执行入口，不是编排层

用户输入: $ARGUMENTS

---

## 宿主能力适配

- 优先使用宿主提供的结构化提问工具（如 AskUserQuestion）一次性收集缺失信息。
- 如果宿主不支持该工具，则用一条普通消息集中提问相同问题；低风险字段可给出默认值建议。
- 如果宿主支持 slash command，可推荐相关 workflow 的命令入口；否则直接在当前线程继续对应 workflow。

---

## 先统一心智模型

使用本 skill 前，先按 [automation-model.md](../testany-guide/references/automation-model.md) 理解边界：

- 上游给出的通常是 **traditional test scenario**
- `testany-case-writing` 负责把它拆成 **platform cases**
- 本 skill 负责把这些 platform cases 编排成 **pipeline**
- `testany-trigger` 负责为 pipeline 配置 `Plan / Manual Trigger / Gatekeeper`

**重要结论**：
- 本 skill 的主输入不应该是“让我从 case 描述里猜业务流程”
- 本 skill 的主输入应该是上游明确给出的 **automation design / decomposition**

---

## 上游输入优先级

按以下优先级选择输入模式：

1. **Primary：automation design / decomposition**
   - 来自 `testany-case-writing`
   - 最好是基于 approved Test Spec 的 `Testany Automation Handoff` 生成
   - 已明确 case inventory、依赖关系、relay map、是否有分支

2. **Secondary：用户明确给出的 case keys + 依赖描述**
   - 例如“用 A1B2C3D4 先登录，再用 E5F6A7B8 查询”

3. **Fallback：从现有 case metadata 反推**
   - 只在前两者都没有时使用
   - 必须把结果回显给用户确认
   - 不能把“猜出来的流程”当主路径

---

## 操作速查

| 用户意图 | 操作类型 | 工具 |
|---------|---------|------|
| 创建新 pipeline | Create | `testany_create_pipeline` |
| 查看 pipeline 详情 | Read | `testany_get_pipeline` |
| 查看 pipeline YAML | Read | `testany_get_pipeline_yaml` |
| 搜索/列出 pipelines（按 workspace） | Read | `testany_list_pipelines` |
| 列出我的 pipelines（按 workspace） | Read | `testany_list_my_pipelines` |
| 修改 pipeline 配置 | Update | `testany_update_pipeline` |
| 删除 pipeline | Delete | `testany_get_pipeline_used_by` → `testany_delete_pipeline` |
| 验证 YAML 语法 | Validate | `testany_verify_pipeline` |
| 检查被引用情况 | Query | `testany_get_pipeline_used_by` |

---

## Create（创建）

### Phase 0: 先判断输入模式

#### Primary：已有 automation design / decomposition

如果上游已给出以下内容，直接按它编排：
- platform case inventory
- 每个 case 的职责
- `source_case_ids` / `scenario_group`（若来自 Test Spec handoff）
- dependencies
- relay map
- 是否有 `whenFailed` / `expect: fail`

#### Secondary：用户已明确给出 case keys 与顺序

如果用户直接给出：
- case keys
- 执行顺序
- relay 关系

则直接进入 YAML 构建。

#### Fallback：只能从现有 cases 反推

仅在没有上游 design 时使用：
- `testany_list_cases` / `testany_get_case`
- 结合 `case_labels`、`description`、`environment_variables[].description`
- 给出候选编排方案
- **必须让用户确认**

---

### Phase 1: 准备数据

并行获取：
- `testany_get_my_workspaces`
- `testany_list_cases` 或 `testany_list_my_cases`

如果用户还没有把 platform cases 注册到 Testany 平台：
- 停止创建 pipeline
- 提示先走 `testany-case`

---

### Phase 2: 构建 pipeline 设计

根据输入模式，确定：
- pipeline 名称
- 所属 workspace
- 包含哪些 case keys
- 顺序与前置依赖
- relay 变量关系
- 是否有失败分支
- 是否存在 `expect: fail`

#### 何时使用 `case_keys`

仅当满足以下条件时，允许直接用 `case_keys` 自动生成简单顺序 pipeline：
- 无条件分支
- 无 relay
- 无 `expect: fail`
- 用户只要最简单的顺序执行

#### 何时必须手写 YAML

出现以下任一情况时，必须显式生成 YAML：
- 有 relay
- 有 `whenPassed` / `whenFailed`
- 有 `expect: fail`
- 需要表达分支、前置、清理或失败路径

---

### Phase 3: 验证 relay 与依赖

如有 relay，必须：
1. `testany_get_case` 检查源 case 是否有 `type='output'` 变量
2. `testany_get_case` 检查目标 case 是否有 `type='env'` 变量
3. 确保源 case 在 rules 中位于目标 case 之前
4. 确保 relay 不与 `whenFailed` 组合
5. **禁止把 `type='secrets'` 行作为 relay 源或目标**：secrets 的值来自 workspace Credential Safe，不经过 relay 传递；目标端也不能被 relay 覆写。如果 relay 源/目标命中 secrets 行，停下来向用户说明并请求改用 `env` 或 `output` 行

---

### Phase 4: 创建 pipeline

调用 `testany_create_pipeline`：

| 参数 | 必填 | 说明 |
|------|-----|------|
| `name` | 是 | pipeline 名称 |
| `workspace` | 是 | 所属工作空间 key |
| `description` | 否 | 描述 |
| `definition` | 否 | Pipeline YAML 配置 |
| `case_keys` | 否 | Case keys 数组（仅简单顺序场景） |

---

### Phase 5: 验证

调用 `testany_verify_pipeline`：
- 检查 `kind` 是否在支持范围内（`rule/v1.2` 或 `rule/v1.3`）
- 检查 `rules` 结构是否合法
- 检查 relay 与依赖约束

---

## Fallback：从现有 cases 反推（仅兜底）

当且仅当前两种输入模式都不存在时，才允许从现有 cases 反推。

### 可用于判断的信息

| 字段 | 用途 | 可靠程度 |
|------|------|---------|
| `case_labels` | 按 User Story 编号、功能模块筛选 | 高 |
| `description` | 理解动作、前置条件、验证目标 | 中 |
| `environment_variables[].description` | 理解输入/输出变量语义 | 中 |
| `name` | 辅助判断 | 低 |

### 禁止猜测

如果仍然无法确定：
- 哪些 cases 应被包含
- 顺序如何安排
- relay 如何配置

必须向用户确认，而不是猜测。

---

## Read（查询）

| 场景 | 工具 | 说明 |
|------|------|------|
| 获取 pipeline 详情 | `testany_get_pipeline` | 传入 pipeline key |
| 获取 YAML 内容 | `testany_get_pipeline_yaml` | 传入 pipeline key |
| 搜索/列出 pipelines（按 workspace） | `testany_list_pipelines` | `workspace` 必填 |
| 仅列出我的 pipelines（按 workspace） | `testany_list_my_pipelines` | `workspace` 必填 |

---

## Update（更新）

### 可更新的字段

| 参数 | 说明 |
|------|------|
| `name` | pipeline 名称 |
| `description` | 描述 |
| `definition` | YAML 定义 |
| `case_keys` | 简单顺序执行的 case keys |
| `environments` | 环境标签列表 |
| `owned_by` | 所有者邮箱 |
| `pipeline_labels` | Pipeline 标签列表 |

### 更新流程

1. `testany_get_pipeline` 读取当前配置
2. `testany_get_pipeline_yaml` 读取当前 YAML（如需修改编排）
3. 优先按已有 automation design 更新，而不是现场重猜
4. 如修改 YAML，重新验证 relay 与依赖
5. `testany_update_pipeline` 提交更新

---

## Delete（删除）

删除前必须检查引用情况：
1. `testany_get_pipeline_used_by`
2. 如被 `Plan / Manual Trigger / Gatekeeper` 引用，先提示用户解除引用
3. 无引用后再删除

**警告**：此操作不可撤销。

---

## 常见问题处理

| 场景 | 处理方式 |
|------|---------|
| 用户只有场景，没有已注册 case | 先去 `testany-case-writing` + `testany-case` |
| 用户只有一个 case，想直接执行 | 仍需创建一条单 case pipeline |
| 有 relay 但没给清楚源/目标 | 回到上游确认 decomposition |
| 只有现有 case 库，没有 design | 可 fallback 反推，但必须让用户确认 |
| 用户想配置什么时候运行 | 切到 `testany-trigger` |
| 用户想立即执行 pipeline | 切到 `testany-trigger` |
| 用户想看 execution 进度或历史 | 切到 `testany-execution` |

---

## 返回格式

任务完成后，向用户汇报：
- Pipeline Key
- Pipeline 名称
- 所属工作空间
- 来源输入模式：`automation design / explicit case keys / fallback inference`
- 包含的 case 数量与顺序
- relay 配置摘要
- 是否建议继续到 `testany-trigger`
- 如已发起执行，是否建议继续到 `testany-execution`

---

## 参考文档

- [Testany 自动化对象模型](../testany-guide/references/automation-model.md)
- [Pipeline YAML 语法](./references/pipeline-yaml.md)
- [Pipeline 相关概念](./references/concepts.md)
