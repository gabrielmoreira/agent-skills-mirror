# OpenClaw 企业版 — 基于 AgentCore

> 本文档为 [README_ENTERPRISE.md](README_ENTERPRISE.md) 的中文翻译。代码块和命令保持英文原文。


将 [OpenClaw](https://github.com/openclaw/openclaw) 从个人 AI 助手变成企业级数字化劳动力平台 —— 无需修改任何一行 OpenClaw 源代码。

---

## 无服务器经济学：Agent 思考时才计费

大多数企业 AI 部署按席位收费或为每位员工分配专用计算资源。AgentCore Firecracker 微虚拟机彻底改变了经济模型 —— **你无需预分配 CPU 或内存，无需选择实例规格。AgentCore 按需为每次调用分配精确资源，按秒计费。**

**AgentCore 定价（us-west-2）：**
- CPU：$0.0895 / vCPU-小时 —— **空闲时 $0**（调用间无 CPU 费用）
- 内存：$0.00945 / GB-小时 —— 唯一的空闲成本，极低

**50 名员工，每天 8 小时会话（us-west-2）：**

| | Dedicated EC2 per Employee | ChatGPT Team | **OpenClaw on AgentCore** |
|---|---|---|---|
| 50 名员工 | 50 × $52 = **$2,600/月** | 50 × $25 = **$1,250/月** | **约 $100-150/月** |
| 付费内容 | 全天候运行，无论是否有人聊天 | 按席位固定 | 仅调用 CPU + 空闲会话内存 |
| 每员工空闲成本 | $52/月（EC2 全天运行） | $25/月（订阅） | **约 $0.08/天**（1 GB 内存 × 8 小时） |

**计算：** 50 员工 × 22 工作日 × $0.08 闲置/天 = 约 $88/月内存成本。加上实际对话时的 CPU（约 $20-50/月）= **AgentCore 总成本约 $100-150/月。** 加上网关基础设施（见下方[成本估算](#成本估算)）为完整费用。

---

## 三种部署模式：Serverless + ECS + EKS

每个 Agent 使用相同的 Docker 镜像。管理员根据使用场景为每个 Agent 选择部署模式 —— 无需代码变更，无需单独构建。

### Serverless（AgentCore）— 默认

| | 行为 |
|-|---------|
| **冷启动** | 首条消息约 6 秒 —— Firecracker 微虚拟机 + SOUL 装配 + Bedrock |
| **会话恢复** | 约 2-3 秒 —— Session Storage 恢复工作空间，跳过 S3 下载 |
| **热会话** | 近乎即时 —— 对话期间微虚拟机保持活跃 |
| **空闲成本** | 仅内存（$0.00945/GB-小时）。CPU 空闲时 = $0 |
| **Session Storage** | 工作空间文件在微虚拟机 stop/resume 之间持久化（每会话 1 GB）。Agent 侧无需 S3 同步 |
| **适用场景** | 个人员工 Agent —— 缩至零，按使用付费 |

### Always-on（ECS Fargate）— 管理员切换

| | 行为 |
|-|---------|
| **冷启动** | 无 —— 容器始终运行 |
| **定时任务** | HEARTBEAT 按计划触发（每 3 分钟检查邮件、每日报告） |
| **直连 IM** | 容器直接连接 Telegram/Discord（专用 Bot Token） |
| **持久化** | EFS 支持的工作空间 —— 容器重启后持久 |
| **适用场景** | 客服 Bot、频繁定时任务的高管助理、高流量数字孪生 |

### EKS（Kubernetes）— 容器原生基础设施

| | 行为 |
|-|---------|
| **冷启动** | 无 —— Pod 始终运行 |
| **Operator 管理** | OpenClaw Operator 监听 `OpenClawInstance` CRD → StatefulSet + Service + PVC |
| **持久化** | EFS PVC（默认 StorageClass）—— Pod 重启后持久 |
| **集群管理** | 在管理控制台发现并关联 EKS 集群（设置 → EKS） |
| **互联网访问** | ALB Ingress（Terraform 默认启用），自定义域名 + HTTPS（ACM 证书） |
| **Helm Chart** | 管理控制台打包为 Helm Chart：ServiceAccount、RBAC、Deployment、Service、Ingress |
| **中国区域** | `china-image-mirror.sh` 同步 Operator 镜像至中国区 ECR；`globalRegistry` CRD 字段重写所有镜像仓库 |
| **部署 API** | 完整基础设施配置：模型、CPU/内存、存储、运行时类（Kata）、Chromium Sidecar、备份、节点选择器、容忍度 |
| **适用场景** | 已在 Kubernetes 上运行的团队、多集群部署、Graviton/GPU 工作负载、AWS 中国区域 |

管理员在 **Agent Factory** 中创建 Agent 时选择部署模式。Agent Factory 显示三个运行时标签页（Serverless、ECS、EKS），包含实时实例状态。EKS 标签页包含 **Deploy Agent** 弹窗，提供完整的基础设施配置选项。

**[→ EKS Deployment Guide (EN)](docs/DEPLOYMENT_EKS.md)** · **[→ EKS 部署指南 (中文)](docs/DEPLOYMENT_EKS_CN.md)**

---

## 安全：跨运行时纵深防御

### 五层安全模型

| 层级 | 机制 | 提示词注入能否绕过？ |
|-------|-----------|-------------------------------|
| L1 — 提示词 | SOUL.md 规则（"财务不使用 shell"） | ⚠️ 理论上可能 |
| L2 — 应用层 | Skills 清单 `allowedRoles`/`blockedRoles` | ⚠️ 代码缺陷风险 |
| **L3 — IAM** | **运行时角色对目标资源无权限** | **不可能** |
| **L4 — 计算** | **每个 Agent 独立隔离边界（见下表）** | **不可能** |
| **L5 — 护栏** | **Bedrock Guardrail 检查每个输入+输出：话题拒绝、PII 过滤、合规策略** | **不可能 — AWS 托管语义 AI 层** |

L1-L2 是软层（提示词/应用层）。L3-L5 是硬性基础设施边界 —— 无论多复杂的提示词注入、越狱或工具调用滥用都无法绕过。实习生的 Agent IAM 角色确实无法读取高管 S3 桶 —— 即使 LLM 尝试也不行。即使能读取，Guardrail 也会在输出到达用户之前拦截。

### L4 计算隔离：运行时对比

三种运行时提供不同级别的计算隔离。根据安全要求选择：

| | AgentCore (Serverless) | ECS (Fargate) | EKS (Pods) | EKS + Kata Containers |
|---|---|---|---|---|
| **隔离方式** | Firecracker 微虚拟机 | Fargate 微虚拟机 | Linux cgroups/命名空间 | Firecracker 微虚拟机（Kata） |
| **边界** | Hypervisor (KVM) | Hypervisor (KVM) | 内核（共享） | Hypervisor (KVM) |
| **内核** | 每次调用独立 | 每个任务独立 | **与节点共享** | 每个 Pod 独立 |
| **提示词注入 → 逃逸？** | **不可能** — 微虚拟机边界 | **不可能** — Fargate 边界 | ⚠️ 内核漏洞理论上可能（罕见） | **不可能** — 微虚拟机边界 |
| **跨租户可见性** | 无 — 独立微虚拟机 | 无 — 独立任务 | ⚠️ 共享节点，需 NetworkPolicy | 无 — 独立微虚拟机 |
| **适用场景** | 最大隔离，合规 | 持久化 Agent，中等安全 | 开发/测试，成本优化 | 生产 K8s + 合规 |

**关键结论：** AgentCore 和 ECS Fargate 通过 Firecracker 微虚拟机为每个 Agent 提供 **硬件级** 隔离 —— 与 AWS Lambda 使用的技术相同。LLM 驱动的 Agent 无法观察、干扰或逃逸到另一个 Agent 的执行环境，无论提示词注入多复杂。

标准 EKS Pod 共享宿主机内核。虽然 Kubernetes 命名空间、cgroups 和 NetworkPolicy 为大多数工作负载提供了强隔离，但理论上的内核漏洞可能穿越边界。对于需要与 AgentCore 相同隔离保证的生产 EKS 部署：

- **启用 Kata Containers**（Terraform 中 `enable_kata = true`）—— 每个 Pod 在裸金属节点上的独立 Firecracker 微虚拟机中运行，恢复 Hypervisor 级隔离
- **使用专用节点组** —— 按安全级别分组，防止不同信任级别混合调度
- **强制 NetworkPolicy** —— OpenClaw Operator 默认为每个实例创建 NetworkPolicy

### 附加控制

- 无公开端口（EC2 仅 SSM，EKS 使用 ClusterIP）
- 全程 IAM 角色，无硬编码凭证
- Gateway Token 存于 SSM SecureString，不落盘
- 运行时间 VPC 隔离
- Pod Identity（EKS）或 IRSA 实现最小权限 AWS 访问
- RBAC：admin/manager/employee 权限范围受限

---

## 从第一天起可审计、可治理

| 控制项 | IT 获得什么 |
|---------|-------------|
| **SOUL 编辑器** | IT 锁定全局规则。财务不能使用 shell。工程不能泄露 PII。员工不能覆盖全局层。 |
| **技能治理** | 26 个技能带 `allowedRoles`/`blockedRoles`。员工不能安装未批准的技能。 |
| **审计中心** | 每次调用、工具调用、权限拒绝、SOUL 变更和 IM 配对 → DynamoDB |
| **用量与成本** | 按员工、按部门分解。每日/每周/每月趋势及模型定价 |
| **IM 管理** | 管理员可见每位员工的 IM 连接。一键撤销。 |
| **安全中心** | 实时 ECR 镜像、IAM 角色、VPC 安全组及 AWS 控制台深链接 |
| **RBAC** | Admin（全组织）· Manager（部门范围）· Employee（仅门户） |

---

## 差异化优势

> 大多数企业 AI 平台给每个人相同的通用助手。而这个平台给每位员工 **一个具有独立身份、记忆、工具和边界的个人 AI Agent** —— 同时给 IT 部门上述治理控制。
> This one gives each employee **a personal AI agent with their own identity, memory, tools, and boundaries** — while giving IT the governance controls above.

### 旗舰功能

| 功能 | 说明 |
|---------|-------------|
| **数字孪生** | 员工开启公开链接。任何人通过 URL 可在员工不在时与其 AI Agent 对话 —— Agent 使用员工的 SOUL、记忆和专业知识回复。孪生会话与员工主会话隔离 |
| **Always-on Agent** | 管理员将任何 Agent 切换到持久化 ECS Fargate 模式。启用定时任务（每 3 分钟检查邮件）、直连 IM Bot、即时响应。相同镜像、相同 SOUL —— 仅部署模式切换 |
| **Session Storage** | AgentCore 在微虚拟机 stop/resume 周期间持久化工作空间文件。会话恢复无需重新下载 S3。配合 `StopRuntimeSession` API 实现管理员触发的配置刷新 |
| **三层 SOUL** | 全局（IT）→ 职位（部门管理）→ 个人（员工）。3 利益相关方，3 层，一个合并身份。相同 LLM —— 财务分析师 vs SDE 拥有完全不同的个性和权限 |
| **自助 IM 配对** | 员工在门户扫描二维码 → 30 秒连接 Telegram / 飞书 / Discord。无需 IT 工单，无需管理员审批 |
| **Multi-Runtime Architecture** | Standard tier (Nova 2 Lite, scoped IAM) vs Executive tier (Claude Sonnet 4.6, full access). Different Docker images, different models, different IAM roles — infrastructure-level isolation |
| **Bedrock Guardrails (L5)** | Assign any Bedrock Guardrail to a Runtime from Security Center UI. Topic denial, PII filtering, and compliance policies wrap every user input and agent output — no OpenClaw source code changes needed. Standard employees get blocked; exec tier is unrestricted. Full block audit trail in Audit Center. |
| **Org Directory KB** | Company directory (every employee, R&R, contact, agent capabilities) seeded from org data and injected into every agent — agents know who to contact and can draft messages for you |
| **Position → Runtime Routing** | 3-tier routing chain: employee override → position rule → default. Assign positions to runtimes from Security Center UI, propagates to all members automatically |
| **Per-Employee Model Config** | Override model, context window, compaction settings, and response language at position OR employee level from Agent Factory → Configuration tab |
| **IM Channel Management** | Admin sees every employee's IM connections grouped by channel — when they paired, session count, last active, one-click disconnect |
| **Org CRUD** | Full create/edit/delete for Departments, Positions, and Employees from Admin Console. Delete is guarded: blocks if employees or agent assignments exist, prompts force-cascade delete |
| **Security Center** | Live AWS resource browser — ECR images, IAM roles, VPC security groups with console links. Configure runtime images and IAM roles from the UI |
| **Session Storage + Memory** | Serverless: Session Storage persists workspace across microVM cycles + S3 writeback for admin visibility. Always-on: EFS workspace + Gateway compaction. Same memory across Discord, Telegram, Feishu, and Portal |
| **Dynamic Config, Zero Redeploy** | Change model, tool permissions, SOUL content, or KB assignments → propagates via config version poll (5 min) or instant via `StopRuntimeSession`. No container rebuild, no runtime update |

---

## 在线演示

> **https://openclaw.awspsa.com**
>
> 一个真实运行的实例，包含 15 departments, 12 positions, 27 employees, 29 AI agents, 5 IM channels (Telegram, Feishu, Discord + Portal), multi-runtime architecture, and always-on ECS Fargate agents — all backed by DynamoDB + S3 on AWS.
>
> **这里的一切都是真实的。** 每个按钮都有效。每个图表读取真实数据。每个 Agent 在隔离的 Firecracker 微虚拟机中运行。
>
> **试试数字孪生：** 以任何员工登录 → 门户 → 我的档案 → 开启 **数字孪生** → 获取公开 URL → 在隐身窗口打开并与该员工的 AI 版本对话。
>
> 需要演示账户？ 联系 [wjiad@aws](mailto:wjiad@amazon.com) 获取访问权限。

### 截图

| Admin Dashboard | Employee Portal + Digital Twin |
|:-:|:-:|
| ![Admin Dashboard](enterprise/demo/images/04-admin-dashboard.jpeg) | ![Portal Chat](enterprise/demo/images/01-portal-chat-permission-denied.jpeg) |

| Agent Factory — Configuration | IM Channels — Per-Channel Management |
|:-:|:-:|
| ![Agent Factory](enterprise/demo/images/03-agent-factory-list.jpeg) | ![SOUL Editor](enterprise/demo/images/05-workspace-manager-soul.jpeg) |

| Usage & Cost — Model Pricing | Security Center — Runtime Management |
|:-:|:-:|
| ![Usage & Cost](enterprise/demo/images/02-usage-cost-dashboard.jpeg) | ![Skill Platform](enterprise/demo/images/08-skill-platform-catalog.jpeg) |

---

## 痛点

OpenClaw 是最强大的开源 AI Agent 平台之一（200k+ GitHub Stars）。它擅长个人生产力：将 AI 连接到 WhatsApp、Telegram、Discord，运行浏览器自动化，管理日历。但企业部署需要：

- **多租户隔离** —— 每位员工获得自己的 Agent，具有独立身份、记忆和权限
- **基于角色的访问控制** —— 实习生不能运行 shell 命令，财务不能访问工程数据
- **集中治理** —— IT 控制组织范围内的 Agent 行为、技能和模型选择
- **审计与合规** —— 每个 Agent 操作记录，PII 检测，数据主权
- **成本管理** —— 按部门预算，模型路由，使用跟踪

## 解决方案

一个管理层，用企业级控制包装 OpenClaw，部署在 AWS Bedrock AgentCore 上。无 Fork、无补丁、无厂商锁定 —— 仅配置文件和 AWS 原生服务。

### 设计原则

#### 1. 对 OpenClaw 零侵入

我们不 Fork、不打补丁、不修改任何一行 OpenClaw 源代码。而是完全通过 OpenClaw 的原生工作空间文件系统控制 Agent 行为：

```
workspace/
├── SOUL.md            ← Agent identity & rules (assembled from 3 layers)
├── AGENTS.md          ← Workflow definitions
├── TOOLS.md           ← Tool permissions
├── USER.md            ← Employee preferences
├── MEMORY.md          ← Persistent memory
├── memory/            ← Daily memory files (per-turn checkpoint)
├── knowledge/         ← Position-scoped + global documents (KB-injected)
├── skills/            ← Role-filtered skill packages
├── IDENTITY.md        ← Employee name + position (generated, not editable)
├── CHANNELS.md        ← Employee's bound IM channels (for outbound notifications)
└── SESSION_CONTEXT.md ← Access path + caller identity (written once at cold start)
```

`workspace_assembler` 在 OpenClaw 读取之前将全局 + 职位 + 个人三层合并到这些文件中。OpenClaw 不知道自己在企业环境中运行 —— 它只是照常读取工作空间。

`SESSION_CONTEXT.md` is the access path identity file. It is written **once per cold start** by `workspace_assembler` and encodes exactly which access path triggered this session, verified by the `session_id` prefix the Tenant Router assigns:

| 会话前缀 | 访问路径 | 写入内容 |
|----------------|-------------|-----------------|
| `emp__emp-id__` | 员工门户 + 所有绑定 IM 渠道（共享会话） | 已认证用户名，"验证：已确认" |
| `pt__emp-id__` | Portal (legacy alias, same behavior as `emp__`) | Same as above |
| `pgnd__emp-id__` | Playground — IT 管理员以该员工身份测试 | "管理员测试会话，只读内存" |
| `twin__emp-id__` | 数字孪生 — 外部访问者，无需认证 | "访问者未验证，对话对员工在门户中可见" |
| `admin__...` | IT 管理员助手 | "已授权 IT 管理员" |
| `tg__`, `dc__`, etc. | Raw IM fallback (unresolved user, before pairing) | "Standard Session" |

**Why this matters:** Without SESSION_CONTEXT.md, the agent cannot distinguish Portal from Playground from Digital Twin — all three would access the same workspace and respond identically. With it, Playground explicitly tells the agent not to write back to employee memory, and Digital Twin tells the agent the caller is unverified and the conversation is visible to the represented employee.

#### 2. Serverless 优先 + Always-on 混合

**默认：Serverless。** 每个 Agent 在隔离的 Firecracker 微虚拟机中运行，通过 Bedrock AgentCore。Session Storage 在 stop/resume 周期间持久化工作空间文件 —— session resume 无需重新下载 S3。

**管理员切换：Always-on。** 任何 Agent 都可以切换到持久化 ECS Fargate 容器 —— 相同 Docker 镜像、相同 SOUL、相同代码路径。区别在于基础设施：容器保持活跃，支持定时任务、直连 IM 和即时响应。

```
Request
  ↓
Tenant Router — 3-tier routing:
  1. Always-on check (SSM /tenants/{emp_id}/always-on-agent)
     → routes to ECS Fargate container (private VPC IP)
  2. Position rule (DynamoDB CONFIG#routing or SSM /positions/{pos_id}/runtime-id)
     → routes to AgentCore Runtime for that position
  3. Default AgentCore Runtime
```

| | Serverless (AgentCore) | Always-on (ECS Fargate) |
|-|----------------------|------------------------|
| Cold start | ~6s first message, ~2-3s session resume | None — container always running |
| Scheduled tasks | Deferred to next invocation | Fires on schedule (HEARTBEAT) |
| Direct IM bot | No — routes through Gateway EC2 | Yes — dedicated bot token in container |
| Idle cost | Memory only ($0.08/day per 1 GB session) | ~$0.55/day (0.5 vCPU + 1 GB Fargate) |
| Persistence | Session Storage (1 GB, auto-managed) | EFS (unlimited, durable) |
| Best for | Individual employees (majority) | Customer service, exec assistants, high-frequency cron |

**Every agent is "shared" by nature** — an employee's agent serves the employee themselves, their Digital Twin visitors, and potentially other assigned employees. "Shared vs personal" is just how many employees the admin assigns, not a separate infrastructure type.

#### 2.1 多运行时架构（纵深防御）

Different employee groups can be assigned to different AgentCore Runtimes, each backed by its own Docker image and IAM role:

```
Runtime: Standard (Engineering / Sales / HR)
  ├── Docker:  standard-agent:latest
  │   └── Skills: web-search, jina-reader, deep-research, github-pr, slack
  ├── Model:   Amazon Nova 2 Lite (cost-optimized)
  └── IAM:     Own S3 workspace only · Own DynamoDB partition

Runtime: Executive (C-Suite / Senior Leadership)
  ├── Docker:  exec-agent:latest (all skills pre-installed)
  ├── Model:   Claude Sonnet 4.6 (highest capability)
  └── IAM:     Full S3 access · Cross-department DynamoDB read · All Bedrock models
```

Each runtime tier has its own Docker image, IAM role, and optional Bedrock Guardrail — see [Security](#security-hardware-level-isolation-at-every-layer) above for the full 5-layer model.

#### 3. 数字孪生 — 办公时间外的 AI 可用性

Every employee can generate a public shareable URL for their agent:

```
Employee toggles Digital Twin ON
  ↓
Gets: https://your-domain.com/twin/{secure-token}
  ↓
Anyone with the link can chat (no login required)
  ↓
Agent responds using employee's SOUL + memory + expertise
Agent introduces itself: "I'm [Name]'s AI assistant..."
  ↓
Employee turns it OFF → link immediately revoked
```

**Use cases:** Out-of-office assistant · Sales agent always available · Technical SME accessible to anyone · Async collaboration across timezones

#### 4. 三层 SOUL 架构

```
┌─────────────────────────────────────────────────────────┐
│  Layer 1: GLOBAL (IT locked — CISO + CTO approval)      │
│  Company policies, security red lines, data handling     │
│  "Never share customer PII. Never execute rm -rf."       │
├─────────────────────────────────────────────────────────┤
│  Layer 2: POSITION (Department admin managed)            │
│  Role expertise, tool permissions, knowledge scope       │
│  "You are a Finance Analyst. Use excel-gen, not shell."  │
├─────────────────────────────────────────────────────────┤
│  Layer 3: PERSONAL (Employee self-service)               │
│  Communication preferences, custom instructions          │
│  "I prefer concise answers. Always use TypeScript."      │
└─────────────────────────────────────────────────────────┘
                        ↓ merge
              Final SOUL.md (what OpenClaw reads)
```

#### 5. 会话启动时知识装配

When an agent starts a new session, `workspace_assembler` injects:

1. **Global KB** (org directory, company policies) — available to every agent
2. **Position KB** (Engineering docs for SAs, Finance docs for FAs) — scoped by role
3. **Employee KB** — individual overrides

The org directory KB (seeded via `seed_knowledge_docs.py`, refreshed by re-running the script after org changes) gives every agent the ability to answer: *"Who should I contact for X?"* and *"How do I reach [name]?"*

## 架构

```
┌─────────────────────────────────────────────────────────────────┐
│  Admin Console (React + FastAPI)                                 │
│  ├── 25+ pages: Dashboard, Agent Factory, Security Center,       │
│  │   IM Channels, Monitor, Audit, Usage & Cost, Settings         │
│  ├── Employee Portal: Chat, Profile, Skills, Requests, Connect   │
│  │   IM, Digital Twin toggle                                      │
│  ├── 3-role RBAC (admin / manager / employee)                    │
│  └── IT Admin Assistant (Claude API, 10 whitelisted tools)       │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  PATH 1: IT Admin Assistant                                      │
│  ┌────────────────────────────────────────────────────────┐      │
│  │  Admin Console floating chat bubble (admin role only)  │      │
│  │    session_id prefix: admin__                          │      │
│  │    SESSION_CONTEXT.md → "IT Admin Assistant"           │      │
│  │    Claude API direct (not AgentCore), 10 whitelisted   │      │
│  │    tools, no shell, no subprocess                      │      │
│  └────────────────────────────────────────────────────────┘      │
│                                                                  │
│  PATH 2: Playground (IT admin testing as employee)               │
│  ┌────────────────────────────────────────────────────────┐      │
│  │  Admin Console → Agents → Playground tab               │      │
│  │    session_id prefix: pgnd__emp-id__                   │      │
│  │    SESSION_CONTEXT.md → "Playground (Admin Test),      │      │
│  │      read-only with respect to memory"                 │      │
│  │    Reads employee's workspace; no write-back           │      │
│  └────────────────────────────────────────────────────────┘      │
│                                                                  │
│  PATH 3: Employee Portal (webchat, authenticated)                │
│  PATH 4: IM Channels (Telegram/Feishu/Discord/Slack — bound)    │
│  ┌────────────────────────────────────────────────────────┐      │
│  │  Paths 3 and 4 share the SAME AgentCore session        │      │
│  │    H2 Proxy enforces IM pairing: unpaired IM → rejected │      │
│  │    Tenant Router resolves channel user_id → emp_id     │      │
│  │    session_id prefix: emp__emp-id__  (both paths)      │      │
│  │    SESSION_CONTEXT.md → "Employee Session, Verified"   │      │
│  │    Full read/write to employee workspace               │      │
│  │    → 3-tier routing: always-on? → position? → default  │      │
│  │    → AgentCore (Firecracker microVM per emp-id)        │      │
│  │    → workspace_assembler: SOUL + IDENTITY + channels   │      │
│  │    → OpenClaw + Bedrock → Response                     │      │
│  └────────────────────────────────────────────────────────┘      │
│                                                                  │
│  PATH 5: Digital Twin (public URL, no auth)                      │
│  ┌────────────────────────────────────────────────────────┐      │
│  │  GET /twin/{token} → public HTML chat page             │      │
│  │  POST /public/twin/{token}/chat                        │      │
│  │    Lookup token → employee_id                          │      │
│  │    session_id prefix: twin__emp-id__                   │      │
│  │    SESSION_CONTEXT.md → "Digital Twin, caller          │      │
│  │      unverified, visible to employee in Portal"        │      │
│  │    Separate twin_workspace (not employee's main)       │      │
│  └────────────────────────────────────────────────────────┘      │
│                                                                  │
│  PATH C: Always-on Agents (ECS Fargate)                          │
│  ┌────────────────────────────────────────────────────────┐      │
│  │  Same Docker image, ECS Fargate task with:             │      │
│  │    SHARED_AGENT_ID={agent_id}                          │      │
│  │    EFS mount at /mnt/efs (per-employee workspace)      │      │
│  │    Optional: TELEGRAM_BOT_TOKEN for direct IM          │      │
│  │  Container self-registers VPC IP in SSM on startup     │      │
│  │  Tenant Router routes assigned employees to task IP    │      │
│  │  Supports scheduled tasks (HEARTBEAT), direct IM,      │      │
│  │    customer service bots, exec assistants               │      │
│  └────────────────────────────────────────────────────────┘      │
│                                                                  │
├─────────────────────────────────────────────────────────────────┤
│  AWS Services                                                    │
│  ├── DynamoDB — org, agents, assignments, audit, usage, config,   │
│  │              Digital Twin tokens, KB assignments              │
│  ├── S3 — SOUL templates, skills, workspaces, knowledge,        │
│  │         org directory, per-employee memory, admin visibility  │
│  ├── SSM — tenant→position, position→runtime, user-mappings,    │
│  │          permissions, always-on endpoints                     │
│  ├── Bedrock — LLM inference (Nova 2 Lite default, Sonnet 4.6  │
│  │              for exec tier, per-position overrides supported) │
│  ├── AgentCore — Session Storage (1 GB/session, auto-managed)   │
│  ├── ECS Fargate — Always-on containers + EFS workspace         │
│  └── CloudWatch — agent invocation logs, runtime events         │
└─────────────────────────────────────────────────────────────────┘
```

## 网关架构：一个 Bot，服务所有员工

OpenClaw Gateway 作为整个组织的统一 IM 连接层。 在参考部署中，它运行在单个 EC2 实例上；生产环境可在负载均衡器后水平扩展。

```
IT Admin (one-time setup):
  Discord  → Create 1 Bot "ACME Agent" → Connect to Gateway
  Telegram → Create 1 Bot @acme_bot    → Connect to Gateway
  Feishu   → Create 1 Enterprise Bot   → Connect to Gateway

All employees use the same Bot, but each gets their own Agent:

  Carol DMs @ACME Agent → H2 Proxy extracts user_id → Tenant Router
    → pos-fa → Standard Runtime → Finance Analyst SOUL → Bedrock → reply

  WJD DMs @ACME Agent → H2 Proxy extracts user_id → Tenant Router
    → pos-exec → Executive Runtime → Sonnet 4.6 → full tools → reply
```

### 员工自助 IM 对接

```
Step 1: Employee opens Portal → Connect IM
Step 2: Selects channel (Telegram / Feishu / Discord)
Step 3: Scans QR code with their phone → bot opens automatically
Step 4: Bot sends /start TOKEN → paired instantly, no admin approval
Step 5: Employee chats with their AI agent directly in their IM app
```

零 IT 摩擦。员工 30 秒内自助完成。管理员在 IM Channels 页面看到所有连接，可以撤销任何连接。

## 核心功能

| 功能 | 工作原理 |
|---------|-------------|
| **Digital Twin** | Employee toggles ON → gets a public URL. Anyone chats with their AI agent, no login required. Agent uses employee's SOUL + memory. Toggle OFF revokes instantly |
| **Always-on Agents** | Admin toggles any agent to ECS Fargate mode. Same Docker image, persistent container with EFS workspace. Enables scheduled tasks, direct IM bot, instant response. Tenant Router routes assigned employees to Fargate task VPC IP via SSM |
| **SOUL Injection** | 3-layer merge (Global + Position + Personal) at session start. Position SOUL warnings in editor when edits affect N agents |
| **Permission Control** | SOUL.md defines allowed/blocked tools per role. Plan A (pre-execution) + Plan E (post-audit). Exec profile bypasses Plan A entirely |
| **Multi-Runtime** | Standard (Nova 2 Lite, scoped IAM) and Executive (Sonnet 4.6, full IAM) runtimes. Assign positions to runtimes from Security Center UI |
| **Self-service IM Pairing** | QR code scan + `/start TOKEN` → SSM mapping written instantly. Supports Telegram, Feishu, Discord |
| **Org Directory KB** | Seeded from org data via `seed_knowledge_docs.py`. Injected into every agent's workspace. Agents know who to contact for what |
| **Per-employee Config** | Override model, `recentTurnsPreserve`, `maxTokens`, response language at position OR employee level. Zero redeploy |
| **Position → Runtime Routing** | 3-tier: employee SSM override → position SSM rule → default. UI in Security Center assigns positions |
| **Memory Persistence** | Serverless: Session Storage persists workspace across microVM cycles + S3 writeback for admin visibility. Always-on: EFS + Gateway compaction. Cross-channel memory shared (IM + Portal = same session) |
| **IM Channel Management** | Per-channel employee table: paired date, session count, last active, disconnect button |
| **Knowledge Base** | Markdown files in S3. Assign KBs to positions from Knowledge Base → Assignments tab. Injected at session start |
| **Skill Filtering** | 26 skills with `allowedRoles`/`blockedRoles`. Finance gets excel-gen, SDE gets github-pr, DevOps gets aws-cli |
| **Agent Config** | Memory compaction, context window, language per position → Agent Factory → Configuration tab |
| **IT Admin Assistant** | Floating chat bubble (admin only). Claude API + 10 whitelisted tools. No shell, no subprocess |
| **Security Center** | Live AWS resource browser: ECR images, IAM roles, VPC security groups with console deep-links |

## 安全模型

| 层级 | 机制 | 详情 |
|-------|-----------|--------|
| **Network** | No open ports | SSM port forwarding or CloudFront (origin restricted) |
| **Credentials** | AWS SSM SecureString | `ADMIN_PASSWORD`, `JWT_SECRET`, Digital Twin tokens encrypted in SSM |
| **Compute** | Firecracker microVM + ECS Fargate | Each serverless agent in its own microVM. Always-on agents in isolated ECS Fargate tasks with EFS |
| **IAM** | Least privilege + runtime tiers | Standard role: own S3/DynamoDB only. Executive role: cross-department. Can't escalate via prompt |
| **Data** | Role-based scoping | Admin: all. Manager: own dept (BFS rollup). Employee: own only. API-enforced |
| **Agent** | SOUL permission control | Plan A pre-execution allowlist. Plan E post-response audit. Exec profile opts out |
| **Audit** | Comprehensive logging | Every invocation, tool call, permission denial, SOUL change, IM pairing, guardrail blocks → DynamoDB |
| **Digital Twin** | Token-based access | Secure token in URL, stored in DynamoDB. Employee revokes instantly. View/chat counts tracked |
| **L5 Guardrail** | AWS Bedrock Guardrails | Per-Runtime content policy. `apply_guardrail()` called on INPUT before forwarding to OpenClaw and on OUTPUT before returning to user. Standard Runtime: topic denial + PII. Exec Runtime: no guardrail. Every block logged to DynamoDB `guardrail_block` audit event. |

## AI 助手部署指南（Kiro / Claude Code / Cursor 等）

> **User:** Copy this section and paste it to your AI to get hands-on deployment help.

---

**What you're deploying:** A multi-tenant enterprise AI platform — a gateway layer (Tenant Router + Admin Console) routes requests to isolated Firecracker microVMs via AWS Bedrock AgentCore. Two Docker images, two Runtimes (Standard + Executive), one DynamoDB table, one S3 bucket. Optional ECS Fargate always-on agents for scheduled tasks and direct IM.

**Run Docker builds on the gateway EC2, not the user's local machine.** After Step 1 creates the EC2, use SSM to build on it — the EC2 is ARM64 Graviton, has Docker pre-installed, and has fast internal network to ECR. Building ARM64 images locally via QEMU emulation is slow and error-prone. Use `enterprise/agent-container/build-on-ec2.sh` for the standard image; adapt the same pattern for exec-agent (Step 1.5).

**Critical — these will silently break deployment if missed:**

1. **The `openclaw` npm package is pinned to `2026.3.24`** in both `agent-container/Dockerfile` and `exec-agent/Dockerfile` — do not upgrade. Newer versions changed the Gateway response delivery mechanism and break IM channel integration.
2. **Build both Docker images** — `agent-container/` (standard) and `exec-agent/` (executive). Don't skip exec even if only standard agents are needed initially.
3. **Docker build takes 10–15 min** — `clawhub install` installs skills one by one. This is normal.
4. **After `update-agent-runtime`**, poll until `status: READY` before testing.
5. **DynamoDB is in `us-east-2` by default** (AgentCore is `us-east-1`). This is intentional — DynamoDB cross-region access is free and `us-east-2` avoids hitting AgentCore's region during heavy load.

**Verify it works** (after deployment):
- Playground → Carol Zhang (Finance) → "run git status" → refused ✓
- Playground → Ryan Park (SDE) → "run git status" → executes ✓
- Playground → Rachel Li (Legal) → "what new tokens are going live?" → Guardrail blocks ✓
- Playground → WJD (Executive) → same question → answers freely ✓

**If AgentCore returns 500:** check CloudWatch group `/aws/bedrock-agentcore/runtimes/<runtime-id>-DEFAULT` for `openclaw returned empty output` — wrong openclaw version. Rebuild with `openclaw@2026.3.24`.

---

## 快速开始

> **TL;DR** — Three commands to deploy:
> ```bash
> cd enterprise
> cp .env.example .env        # edit: STACK_NAME, REGION, ADMIN_PASSWORD
> bash deploy.sh              # ~15 min — infra + Docker build + seed
> ```
> Then follow **Step 4–6** below to deploy the Admin Console and Gateway services on EC2.

### 前置条件

| 要求 | 版本 | 说明 |
|-------------|---------|-------|
| AWS CLI | v2.27+ | `bedrock-agentcore-control` requires 2.27+ |
| Node.js | 18+ | For Admin Console frontend build |
| Python | 3.10+ | For seed scripts and backend |
| SSM Plugin | Latest | [Install guide](https://docs.aws.amazon.com/systems-manager/latest/userguide/session-manager-working-with-install-plugin.html) |

> **无需本地 Docker** — the agent container image is built on the gateway EC2 (ARM64 Graviton) via SSM.

**AWS 要求：**
- Bedrock 模型访问权限： Nova 2 Lite (default) + Anthropic Claude (exec tier + Admin Assistant)
- Bedrock AgentCore available in: `us-east-1`, `us-west-2`
- IAM permissions: `cloudformation:*`, `ec2:*`, `iam:*`, `ecr:*`, `s3:*`, `ssm:*`, `bedrock:*`, `dynamodb:*`

### 步骤 1：配置并部署

```bash
cd enterprise           # from repo root
cp .env.example .env    # copy config template
```

打开 `.env` 并填写必需值：

```bash
STACK_NAME=openclaw-enterprise   # your stack name
REGION=us-east-1                 # us-east-1 or us-west-2 (AgentCore regions)
ADMIN_PASSWORD=your-password     # admin console login password

# Optional: use existing VPC instead of creating a new one
# EXISTING_VPC_ID=vpc-0abc123
# EXISTING_SUBNET_ID=subnet-0abc123

# Optional: custom S3 bucket name — required when deploying multiple stacks in the same account
# (e.g. staging + production in the same AWS account)
# WORKSPACE_BUCKET_NAME=openclaw-tenants-123456789-staging
```

然后运行部署脚本 — it handles everything, **including the Docker build on the gateway EC2 (no local Docker required)**:

```bash
bash deploy.sh
# ~15 minutes total: CloudFormation → EC2 Docker build → AgentCore Runtime → DynamoDB seed
```

代码变更后重新部署，无需重建 Docker 镜像或重新初始化数据：

```bash
bash deploy.sh --skip-build   # update infra only, skip Docker build
bash deploy.sh --skip-seed    # update infra + image, skip DynamoDB
```

**`deploy.sh` 自动完成的工作（端到端）：**
1. Deploys CloudFormation (EC2, ECR, S3, IAM — creates or updates)
2. Packages source code → uploads to S3 → **triggers Docker build on the gateway EC2 via SSM** (ARM64 Graviton, no local Docker needed)
3. Creates or updates AgentCore Runtime
4. Creates DynamoDB table if it doesn't exist
5. Seeds org data (employees, positions, departments, SOUL templates, knowledge docs)
6. Stores `ADMIN_PASSWORD` and `JWT_SECRET` in SSM SecureString
7. Builds Admin Console frontend → packages → deploys to EC2 via SSM
8. Deploys Gateway services (Tenant Router, Bedrock H2 Proxy) to EC2
9. Writes `/etc/openclaw/env` with all required variables (`STACK_NAME`, `DYNAMODB_TABLE`, `DYNAMODB_REGION`, ECS config, etc.)
10. Configures systemd services and starts all components
11. Adds ECS→SSM VPC endpoint security group rule (if VPC endpoints exist)

部署后获取实例 ID 和 S3 桶：

```bash
STACK_NAME="openclaw-enterprise"   # match your .env
REGION="us-east-1"

INSTANCE_ID=$(aws cloudformation describe-stacks --stack-name $STACK_NAME --region $REGION \
  --query 'Stacks[0].Outputs[?OutputKey==`InstanceId`].OutputValue' --output text)
S3_BUCKET=$(aws cloudformation describe-stacks --stack-name $STACK_NAME --region $REGION \
  --query 'Stacks[0].Outputs[?OutputKey==`TenantWorkspaceBucketName`].OutputValue' --output text)
echo "EC2: $INSTANCE_ID  |  S3: $S3_BUCKET"
```

### 步骤 1.5：构建并推送 Exec-Agent 镜像（高管层）

The Executive Runtime uses a separate Docker image (`exec-agent/`) with all skills pre-installed and Claude Sonnet 4.6. `deploy.sh` builds the standard image automatically; the exec image must be pushed separately:

```bash
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
ECR_EXEC="${ACCOUNT_ID}.dkr.ecr.${REGION}.amazonaws.com/${STACK_NAME}-exec-agent"

aws ecr get-login-password --region $REGION | \
  docker login --username AWS --password-stdin "${ACCOUNT_ID}.dkr.ecr.${REGION}.amazonaws.com"

docker build --platform linux/arm64 \
  -f enterprise/exec-agent/Dockerfile \
  -t "${ECR_EXEC}:latest" .

docker push "${ECR_EXEC}:latest"
```

Then update the Exec Runtime to pick up the new image:

```bash
EXEC_RUNTIME_ID=$(aws ssm get-parameter \
  --name "/openclaw/${STACK_NAME}/exec-runtime-id" \
  --query Parameter.Value --output text --region $REGION 2>/dev/null)

EXEC_ROLE=$(aws cloudformation describe-stacks --stack-name $STACK_NAME --region $REGION \
  --query 'Stacks[0].Outputs[?OutputKey==`AgentContainerExecutionRoleArn`].OutputValue' --output text)

aws bedrock-agentcore-control update-agent-runtime \
  --agent-runtime-id "$EXEC_RUNTIME_ID" \
  --agent-runtime-artifact "{\"containerConfiguration\":{\"containerUri\":\"${ECR_EXEC}:latest\"}}" \
  --role-arn "$EXEC_ROLE" \
  --network-configuration '{"networkMode":"PUBLIC"}' \
  --environment-variables "{\"AWS_REGION\":\"${REGION}\",\"BEDROCK_MODEL_ID\":\"global.anthropic.claude-sonnet-4-6\",\"S3_BUCKET\":\"${S3_BUCKET}\",\"STACK_NAME\":\"${STACK_NAME}\",\"DYNAMODB_TABLE\":\"${STACK_NAME}\",\"DYNAMODB_REGION\":\"${DYNAMODB_REGION}\",\"SYNC_INTERVAL\":\"120\"}" \
  --region $REGION
```

> The standard agent image (`openclaw-multitenancy-multitenancy-agent`) is built automatically by `deploy.sh`. You only need this step for the executive tier.

### 步骤 2：DynamoDB 表

> **`deploy.sh` handles this automatically.** No manual steps needed.

<details><summary>Manual steps (only if not using deploy.sh)</summary>

```bash
# Create table (idempotent — safe to run if it already exists)
aws dynamodb create-table \
  --table-name $STACK_NAME \
  --attribute-definitions \
    AttributeName=PK,AttributeType=S AttributeName=SK,AttributeType=S \
    AttributeName=GSI1PK,AttributeType=S AttributeName=GSI1SK,AttributeType=S \
  --key-schema AttributeName=PK,KeyType=HASH AttributeName=SK,KeyType=RANGE \
  --global-secondary-indexes '[{"IndexName":"GSI1","KeySchema":[
    {"AttributeName":"GSI1PK","KeyType":"HASH"},{"AttributeName":"GSI1SK","KeyType":"RANGE"}
  ],"Projection":{"ProjectionType":"ALL"}}]' \
  --billing-mode PAY_PER_REQUEST \
  --region $DYNAMODB_REGION
```


</details>

### 步骤 3：初始化示例组织数据

> **`deploy.sh` handles this automatically.** To re-seed manually (e.g. after org changes):

<details><summary>Manual seed commands</summary>

```bash
cd enterprise/admin-console/server
pip install boto3 requests

DYNAMODB_REGION=us-east-2

python3 seed_dynamodb.py              --region $DYNAMODB_REGION
python3 seed_roles.py                 --region $DYNAMODB_REGION
python3 seed_settings.py              --region $DYNAMODB_REGION
python3 seed_audit_approvals.py       --region $DYNAMODB_REGION
python3 seed_usage.py                 --region $DYNAMODB_REGION
python3 seed_routing_conversations.py --region $DYNAMODB_REGION
python3 seed_ssm_tenants.py           --region $REGION --stack $STACK_NAME

export S3_BUCKET AWS_REGION=$REGION
python3 seed_skills_final.py
python3 seed_all_workspaces.py        --bucket $S3_BUCKET --region $REGION
python3 seed_knowledge_docs.py        --bucket $S3_BUCKET --region $REGION
```


</details>

### 步骤 4-5：管理控制台 + 网关服务

> **`deploy.sh` handles Steps 4, 4.5, and 5 automatically.** It builds the Admin Console, deploys Gateway services, writes `/etc/openclaw/env`, and starts all systemd services.

<details><summary>Manual steps (only if not using deploy.sh)</summary>

**Step 4: Deploy Admin Console**

```bash
cd enterprise/admin-console
npm install && npm run build
cd ../..

COPYFILE_DISABLE=1 tar czf /tmp/admin-deploy.tar.gz -C enterprise/admin-console dist server start.sh
aws s3 cp /tmp/admin-deploy.tar.gz "s3://${S3_BUCKET}/_deploy/admin-deploy.tar.gz"

aws ssm send-command --instance-ids $INSTANCE_ID --region $REGION \
  --document-name AWS-RunShellScript \
  --parameters "{\"commands\":[
    \"python3 -m venv /opt/admin-venv\",
    \"/opt/admin-venv/bin/pip install fastapi uvicorn boto3 requests python-multipart anthropic\",
    \"aws s3 cp s3://${S3_BUCKET}/_deploy/admin-deploy.tar.gz /tmp/admin-deploy.tar.gz --region $REGION\",
    \"mkdir -p /opt/admin-console && tar xzf /tmp/admin-deploy.tar.gz -C /opt/admin-console\",
    \"chown -R ubuntu:ubuntu /opt/admin-console /opt/admin-venv\",
    \"chmod +x /opt/admin-console/start.sh\",
    \"systemctl daemon-reload && systemctl enable openclaw-admin && systemctl start openclaw-admin\"
  ]}"
```

Store secrets in SSM:
```bash
aws ssm put-parameter --name "/openclaw/${STACK_NAME}/admin-password" \
  --value "<YOUR_PASSWORD>" --type SecureString --overwrite --region $REGION
aws ssm put-parameter --name "/openclaw/${STACK_NAME}/jwt-secret" \
  --value "$(openssl rand -hex 32)" --type SecureString --overwrite --region $REGION
```

**Step 5: Deploy Gateway Services**

```bash
aws s3 cp enterprise/gateway/tenant_router.py       "s3://${S3_BUCKET}/_deploy/tenant_router.py"
aws s3 cp enterprise/gateway/bedrock_proxy_h2.js    "s3://${S3_BUCKET}/_deploy/bedrock_proxy_h2.js"
aws s3 cp enterprise/gateway/bedrock-proxy-h2.service "s3://${S3_BUCKET}/_deploy/bedrock-proxy-h2.service"
aws s3 cp enterprise/gateway/tenant-router.service  "s3://${S3_BUCKET}/_deploy/tenant-router.service"

aws ssm send-command --instance-ids $INSTANCE_ID --region $REGION \
  --document-name AWS-RunShellScript \
  --parameters "{\"commands\":[
    \"pip3 install boto3 requests\",
    \"aws s3 cp s3://${S3_BUCKET}/_deploy/tenant_router.py /home/ubuntu/tenant_router.py --region $REGION\",
    \"aws s3 cp s3://${S3_BUCKET}/_deploy/bedrock_proxy_h2.js /home/ubuntu/bedrock_proxy_h2.js --region $REGION\",
    \"aws s3 cp s3://${S3_BUCKET}/_deploy/bedrock-proxy-h2.service /etc/systemd/system/bedrock-proxy-h2.service --region $REGION\",
    \"aws s3 cp s3://${S3_BUCKET}/_deploy/tenant-router.service /etc/systemd/system/tenant-router.service --region $REGION\",
    \"systemctl daemon-reload && systemctl enable bedrock-proxy-h2 tenant-router && systemctl start bedrock-proxy-h2 tenant-router\"
  ]}"
```

</details>

### 步骤 6：访问管理控制台

```bash
aws ssm start-session --target $INSTANCE_ID --region $REGION \
  --document-name AWS-StartPortForwardingSession \
  --parameters '{"portNumber":["8099"],"localPortNumber":["8199"]}'
```

Open **http://localhost:8199** → login with Employee ID `emp-jiade` (admin) and `ADMIN_PASSWORD` from your `.env`.

> **Public access:** Use CloudFront with an Elastic IP on the EC2. Set `PUBLIC_URL` in `/etc/openclaw/env` (e.g. `PUBLIC_URL=https://your-domain.com`) for correct Digital Twin URLs — the admin console reads this file via `EnvironmentFile` in the systemd service.

### 步骤 7：连接 IM 渠道（可选）

```bash
# Get gateway token
aws ssm get-parameter --name "/openclaw/${STACK_NAME}/gateway-token" \
  --with-decryption --query Parameter.Value --output text --region $REGION

# Open gateway UI
aws ssm start-session --target $INSTANCE_ID --region $REGION \
  --document-name AWS-StartPortForwardingSession \
  --parameters '{"portNumber":["18789"],"localPortNumber":["18789"]}'
# http://localhost:18789/?token=<token>
```

Employees self-service pair via Portal → Connect IM (QR code). No admin approval needed.

---

## 测试验证

### 1. SOUL Injection (core differentiator)
以 **Carol Zhang**（财务）登录 → Chat → "Who are you?" → **"ACME Corp Finance Analyst"**
以 **Ryan Park**（SDE）登录 → Chat → "Who are you?" → **"ACME Corp Software Engineer"**
相同 LLM。完全不同的身份。

### 2. Digital Twin
以任何员工登录 → **Portal → My Profile → Digital Twin toggle**
开启 → 复制 URL → 在隐身窗口打开 → 与该员工的 AI 版本对话
关闭 → 隐身标签页立即返回 404

### 3. Org Directory (Knowledge Base)
Ask any agent: *"Who should I contact for a code review?"* or *"What does Marcus Bell do?"*
→ Agent reads `kb-org-directory` (seeded into every position) and answers with the right person's name, role, IM channel, and agent capabilities
→ Works out-of-box after running `seed_knowledge_docs.py` — no manual KB assignment needed

### 4. Permission Boundaries
Carol Zhang: "Run git status" → **Refused** (Finance, no shell)
Ryan Park: "Run git status" → **Executed** (SDE, has shell)
WJD / Ada: Any command → **Executed** (Executive tier, zero restrictions, Sonnet 4.6)

### 5. Multi-Runtime
Login as **Ada** or **WJD** → these route to the Executive AgentCore Runtime:
- Model: Claude Sonnet 4.6 (vs Nova 2 Lite for standard)
- Tools: all unlocked
- IAM: full S3, all Bedrock models, cross-dept DynamoDB

### 6. Memory Persistence
Chat as **JiaDe Wang** (Discord) → come back after 15 min → **agent recalls previous conversation**
Same memory shared across Discord, Telegram, and Portal.

> **How it works:** Each turn is synced to S3 immediately after the response (not just on session end). The next microVM downloads the workspace at session start and has full context. If memory doesn't appear, re-run `seed_all_workspaces.py` to reset S3 workspace state.

### 7. IM Channel Management (Admin)
Admin Console → **IM Channels** → select Discord tab → see JiaDe, David, Peter connected
→ view pairing date, session count, last active
→ click **Disconnect** on any employee

### 8. Security Center
Security Center → **Infrastructure tab** → see real ECR images, IAM roles, VPC security groups
Security Center → **Runtimes → Position Assignments** → change which runtime a position routes to

### 9. Agent Configuration
Agent Factory → **Configuration tab** → set Sonnet 4.5 for Solutions Architect
→ set `recentTurnsPreserve: 20` for Executive positions
→ set `language: 中文` for any position → agents default to Chinese

### 11. Bedrock Guardrails (L5 Content Policy)

Standard Runtime has `GUARDRAIL_ID` set as an environment variable. Every invocation goes through two checks in `server.py`: `apply_guardrail(source=INPUT)` before forwarding to OpenClaw, and `apply_guardrail(source=OUTPUT)` before returning the response. If either check returns `GUARDRAIL_INTERVENED`, the user gets the configured `blockedMessaging` instead of the agent's answer — OpenClaw is never even invoked for blocked inputs.

Exec Runtime has no `GUARDRAIL_ID` — the checks are skipped entirely. Same question, two different runtimes, two different outcomes. Every block is written to DynamoDB as a `guardrail_block` audit event visible in **Audit Center → Guardrail Events**.

To assign a guardrail to any runtime: **Security Center → Runtimes → Configure** → select from the Guardrail dropdown. To create a new guardrail: `aws bedrock create-guardrail ...` then it appears in the dropdown automatically.

### 10. Knowledge Base Assignments
Knowledge Base → **Assignments tab** → all positions are pre-assigned these KBs by default:

| KB | Scope | What agents get |
|----|-------|----------------|
| `kb-org-directory` | All | Full employee directory — who does what, how to reach them |
| `kb-policies` | All | Data handling, security baseline, code of conduct |
| `kb-onboarding` | All | New hire checklist, setup guide |
| `kb-arch` / `kb-runbooks` | Engineering | Architecture standards, runbooks |
| `kb-finance` | Finance | Financial reports and policies |
| `kb-hr` | HR | HR policies |

To add a new KB: Admin Console → Knowledge Base → upload Markdown → Assignments tab → assign to positions → agents pick it up on next cold start.

## 演示账户

> **Executive accounts (Ada, WJD)** run on the Executive AgentCore Runtime with Claude Sonnet 4.6, zero tool restrictions, and a full-access IAM role.

| Employee ID | Name | Role | Runtime | What They Experience |
|-------------|------|------|---------|---------------------|
| **emp-ada** | **Ada** | **Executive** | **exec-agent · Sonnet 4.6** | **All tools · Full IAM · Feishu + Telegram 🔓** |
| **emp-wjd** | **WJD** | **Executive** | **exec-agent · Sonnet 4.6** | **All tools · Full IAM · Feishu + Telegram 🔓** |
| emp-jiade | JiaDe Wang | Admin | standard | Discord → SA Agent ✨ |
| emp-chris | Chris Morgan | Admin | standard | DevOps Agent (shell + infra tools) |
| emp-peter | Peter Wu | Manager | standard | Portal/Discord → Executive Agent ✨ |
| emp-alex | Alex Rivera | Manager | standard | Product dept manager view |
| emp-mike | Mike Johnson | Manager | standard | Sales dept manager · CRM tools |
| emp-ryan | Ryan Park | Employee | standard | Slack/Discord → SDE Agent (shell/code) |
| emp-carol | Carol Zhang | Employee | standard | Telegram → Finance Agent |
| emp-david | David Park | Employee | standard | Slack → Finance Agent ✨ |
| **emp-admin** | **Demo Admin** | **Employee** | **exec-agent** | **Unrestricted test account · All tools · install_skill** |

> 🔓 = No tool restrictions · ✨ = Cross-session memory via S3

## 环境变量

| 变量 | 必填 | 说明 |
|----------|----------|-------------|
| `ADMIN_PASSWORD` | Yes | Login password. Production: store in SSM SecureString |
| `JWT_SECRET` | Yes | JWT signing key. Generate: `openssl rand -hex 32` |
| `AWS_REGION` | Yes | Deployment region for EC2, SSM, ECR, AgentCore (default: `us-east-1`) |
| `GATEWAY_INSTANCE_ID` | Yes | EC2 instance ID — required for always-on container start/stop via SSM. Set in `/etc/openclaw/env`. Falls back to IMDSv2 if not set. |
| `PUBLIC_URL` | No | Base URL for Digital Twin links (default: `https://openclaw.awspsa.com`) — **set this** for correct twin URLs |
| `AGENT_ECR_IMAGE` | No | ECR image URI for always-on containers. Auto-built from `$ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com/$STACK_NAME-multitenancy-agent:latest` if not set. |
| `CONSOLE_PORT` | No | Admin Console port (default: `8099`) |
| `TENANT_ROUTER_URL` | No | Tenant Router URL (default: `http://localhost:8090`) |
| `DYNAMODB_TABLE` | No | Table name — **must equal STACK_NAME** (IAM policy scoped to `table/${StackName}`). Default: same as STACK_NAME |
| `DYNAMODB_REGION` | No | DynamoDB region if different from `AWS_REGION` (default: `us-east-2`) |

## 示例组织

| | 数量 | 详情 |
|-|-------|---------|
| 部门 | 15 | 7 个顶层 + 8 个子部门（含 Admin Lab） |
| 职位 | 12 | SA、SDE、DevOps、QA、AE、PM、FA、HR、CSM、Legal、Executive、Platform Admin |
| 员工 | 27 | 每人在 S3 有工作空间文件 |
| Agent | 29 | 28 个 Serverless + 1 个 Always-on |
| IM 渠道 | 5 | Telegram、飞书、Discord、Portal + Always-on |
| 技能 | 26 | 按角色范围的技能包 |
| 知识文档 | 14 | 11 个主题 KB + company-directory.md（组织目录，自动分配到所有职位） |
| SOUL 模板 | 12 | 1 个全局 + 11 个职位特定 |
| RBAC 角色 | 3 | Admin、Manager、Employee |

## 成本估算

### AgentCore 成本（50 员工，Serverless）

| 组件 | 月费 | 说明 |
|-----------|-------------|-------|
| AgentCore 会话 | 约 $100-150 | 会话内存空闲（$88）+ 调用 CPU（约 $20-50） |
| DynamoDB | 约 $1 | 按请求付费 |
| S3 | < $1 | 工作空间、知识库、组织目录 |
| Bedrock（Nova 2 Lite） | 约 $5-15 | 每天约 100 次对话 |

### Always-on Agent（ECS Fargate，可选）

| 组件 | 月费 | 说明 |
|-----------|-------------|-------|
| 每 Agent Fargate | 约 $17 | 0.5 vCPU + 1 GB，ARM64 Graviton，全天候 |
| EFS | 约 $7 | 弹性吞吐 + 存储 |

### 网关基础设施

网关层（租户路由、H2 代理、管理控制台）运行在 EC2 或等效计算资源上。 单个 `c7g.large`（约 $52/月）足以支持开发和小规模部署。 生产环境应使用高可用架构 (ALB + Auto Scaling Group or ECS) based on the customer's availability requirements.

### 总计估算

| 场景 | AgentCore | Always-on | 网关 | Bedrock | **总计** |
|----------|-----------|-----------|---------|---------|-----------|
| 50 员工，仅 Serverless | $100-150 | — | ~$52+ | ~$10 | **~$160-220/mo** |
| + 2 个 Always-on Agent | $100-150 | $48 | ~$52+ | ~$10 | **~$210-260/mo** |

vs ChatGPT Team ($25 × 50 = $1,250/mo) or Copilot ($30 × 50 = $1,500/mo).

**AgentCore pricing advantage:** you don't pre-allocate CPU or memory — no instance sizing decisions. Idle sessions cost only memory ($0.00945/GB-hour). CPU is $0 when no one is chatting.

## 竞品对比

| 能力 | ChatGPT Team | Microsoft Copilot | OpenClaw 企业版 |
|-----------|-------------|-------------------|-------------------|
| 每员工独立身份 | ❌ 所有人相同 | ❌ 所有人相同 | ✅ 每角色三层 SOUL |
| 按角色工具权限 | ❌ | ❌ | ✅ Plan A + Plan E + L3 IAM |
| 定时任务 / cron | ❌ | ❌ | ✅ Always-on Agent（ECS Fargate） |
| 直连 IM Bot | ❌ | ❌ | ✅ 每 Agent Telegram/Discord Bot |
| 数字孪生（公开 Agent URL） | ❌ | ❌ | ✅ 可分享、可撤销、隔离会话 |
| 会话持久化 | ❌ Session only | ❌ | ✅ Session Storage + S3 跨会话 |
| 自助 IM 配对 | ❌ | ❌ | ✅ 二维码，30 秒 |
| 自托管，数据在您的 VPC | ❌ | ❌ | ✅ Bedrock 在您的账户中 |
| 开源 | ❌ | ❌ | ✅ OpenClaw + AWS 原生 |

## 项目结构

```
enterprise/
├── README.md
├── deploy.sh                       # One-click deployment
├── clawdbot-bedrock-agentcore-multitenancy.yaml  # CloudFormation
├── admin-console/
│   ├── src/pages/
│   │   ├── Dashboard.tsx           # Setup checklist + real-time stats
│   │   ├── AgentFactory/           # Agent list + Configuration tab
│   │   ├── SecurityCenter.tsx      # Runtime config + ECR/IAM/VPC browser
│   │   ├── IMChannels.tsx          # Per-channel employee management
│   │   ├── Knowledge/index.tsx     # KB management + Assignments tab
│   │   ├── Usage.tsx               # Billing + model pricing
│   │   ├── TwinChat.tsx            # Public Digital Twin page (no auth)
│   │   └── portal/
│   │       ├── Chat.tsx            # Employee chat + warmup indicator
│   │       └── Profile.tsx         # USER.md + memory view + Digital Twin toggle
│   └── server/
│       ├── main.py                 # App bootstrap — routes in routers/
│       ├── shared.py               # Auth helpers, config, SSM/DDB helpers
│       ├── routers/                # 16 domain routers (127 API endpoints)
│       │   ├── org.py agents.py bindings.py knowledge.py
│       │   ├── portal.py playground.py monitor.py audit.py
│       │   ├── usage.py settings.py security.py
│       │   ├── admin_im.py admin_ai.py admin_always_on.py
│       │   ├── gateway_proxy.py twin.py
│       │   └── __init__.py
│       ├── db.py                   # DynamoDB single-table + Digital Twin CRUD
│       └── seed_*.py               # Sample data scripts
├── agent-container/                # AgentCore Docker image
│   ├── server.py                   # Workspace assembly + twin/always-on detection
│   ├── workspace_assembler.py      # 3-layer SOUL merge + KB injection
│   └── permissions.py              # SSM permission profiles (base_id extraction)
├── exec-agent/                     # Executive tier Docker image
│   └── Dockerfile                  # All skills pre-installed, Sonnet 4.6
└── gateway/
    ├── bedrock_proxy_h2.js         # H2 Proxy (channel detection, pairing intercept)
    └── tenant_router.py            # 3-tier routing + always-on container support
```

## 运维说明

### Always-on Agent 管理（ECS Fargate）

Always-on Agent 以 **ECS Fargate 服务** 运行 具有 EFS 支持的持久工作空间和崩溃后自动重启。 Each task self-registers its private VPC IP in SSM on startup; the Tenant Router reads that SSM entry to route requests. Admin selects deployment mode (Serverless or Always-on) when creating an agent in Agent Factory.

从 **Agent Factory → Agent 详情 → 部署模式切换** 启停，或手动操作：

```bash
# Read ECS config from CloudFormation outputs (one-time setup)
ECS_CLUSTER=$(aws cloudformation describe-stacks --stack-name $STACK_NAME --region $REGION \
  --query 'Stacks[0].Outputs[?OutputKey==`AlwaysOnEcsClusterName`].OutputValue' --output text)
ECS_TASK_DEF=$(aws cloudformation describe-stacks --stack-name $STACK_NAME --region $REGION \
  --query 'Stacks[0].Outputs[?OutputKey==`AlwaysOnTaskDefinitionArn`].OutputValue' --output text)
ECS_SUBNET=$(aws cloudformation describe-stacks --stack-name $STACK_NAME --region $REGION \
  --query 'Stacks[0].Outputs[?OutputKey==`AlwaysOnSubnetId`].OutputValue' --output text)
ECS_SG=$(aws cloudformation describe-stacks --stack-name $STACK_NAME --region $REGION \
  --query 'Stacks[0].Outputs[?OutputKey==`AlwaysOnTaskSecurityGroupId`].OutputValue' --output text)

# Write to /etc/openclaw/env so the Admin Console can use them
aws ssm send-command --instance-ids $INSTANCE_ID --region $REGION \
  --document-name AWS-RunShellScript \
  --parameters "{\"commands\":[
    \"echo 'ECS_CLUSTER_NAME=${ECS_CLUSTER}' >> /etc/openclaw/env\",
    \"echo 'ECS_TASK_DEFINITION=${ECS_TASK_DEF}' >> /etc/openclaw/env\",
    \"echo 'ECS_SUBNET_ID=${ECS_SUBNET}' >> /etc/openclaw/env\",
    \"echo 'ECS_TASK_SG_ID=${ECS_SG}' >> /etc/openclaw/env\",
    \"systemctl restart openclaw-admin\"
  ]}"

# Manual ECS RunTask (if UI unavailable)
aws ecs run-task \
  --cluster $ECS_CLUSTER \
  --task-definition $ECS_TASK_DEF \
  --launch-type FARGATE \
  --network-configuration "awsvpcConfiguration={subnets=[$ECS_SUBNET],securityGroups=[$ECS_SG],assignPublicIp=ENABLED}" \
  --overrides "{\"containerOverrides\":[{\"name\":\"always-on-agent\",\"environment\":[
    {\"name\":\"SHARED_AGENT_ID\",\"value\":\"agent-helpdesk\"},
    {\"name\":\"SESSION_ID\",\"value\":\"shared__agent-helpdesk\"},
    {\"name\":\"S3_BUCKET\",\"value\":\"$S3_BUCKET\"},
    {\"name\":\"STACK_NAME\",\"value\":\"$STACK_NAME\"},
    {\"name\":\"AWS_REGION\",\"value\":\"$REGION\"}
  ]}]}" \
  --region $REGION
```

The task's private IP is automatically registered in SSM as `/openclaw/{stack}/always-on/{agent_id}/endpoint` by `entrypoint.sh` once healthy (~30s). The Tenant Router picks it up within 60s (SSM cache TTL).

### 数字孪生公网 URL

Set `PUBLIC_URL` in `/etc/openclaw/env` — the admin console systemd service reads this file automatically:
```bash
echo "PUBLIC_URL=https://your-domain.com" >> /etc/openclaw/env
sudo systemctl restart openclaw-admin
```

### 更新 Agent Docker 镜像

After every build, update the AgentCore Runtime to resolve the new `:latest` digest:

```bash
aws bedrock-agentcore-control update-agent-runtime \
  --agent-runtime-id "$RUNTIME_ID" \
  --agent-runtime-artifact "{\"containerConfiguration\":{\"containerUri\":\"${ECR_URI}\"}}" \
  --role-arn "$EXECUTION_ROLE_ARN" \
  --network-configuration '{"networkMode":"PUBLIC"}' \
  --environment-variables "{\"BEDROCK_MODEL_ID\":\"global.amazon.nova-2-lite-v1:0\", ...}" \
  --region $REGION
```

**Always pass `--environment-variables`** — AgentCore clears env vars if the field is omitted.

**Session Storage warning:** `update-agent-runtime` wipes all Session Storage for that runtime. All employees' sessions will bootstrap from S3 on their next invocation (~6s cold start instead of ~2-3s session resume). This is expected and handled automatically — S3 is always the source of truth for admin-managed files.

### 提醒和定时任务

OpenClaw's reminder system writes a `HEARTBEAT.md` to the agent's workspace and sends the notification through the active channel at the scheduled time.

| Deployment Mode | Reminder Behavior |
|----------------|-----------------|
| **Always-on (ECS Fargate)** | Fully supported — container is persistent, heartbeat fires on schedule. Delivery channel is read from `CHANNELS.md` in the workspace (auto-injected at session start from IM pairings). **This is the primary use case for always-on mode** — customer service polling, email checks every 3 minutes, daily report generation. |
| **Serverless (AgentCore)** | Heartbeat is set, `HEARTBEAT.md` persisted in Session Storage and synced to S3. Fires on the **next session start** when the microVM resumes. If no new message arrives before the scheduled time, the reminder is deferred to the next interaction. |

**For reliable scheduled tasks:** toggle the agent to always-on mode from Agent Factory. This is the recommended approach for any agent that needs to run background tasks (email monitoring, ticket scanning, periodic reports).

`CHANNELS.md` is automatically written to each employee's workspace during session assembly (reverse-lookup of their SSM IM pairings). No manual configuration needed once the user has paired an IM channel.

### H2 代理和租户路由 — systemd 服务

```bash
sudo cp gateway/bedrock-proxy-h2.service /etc/systemd/system/
sudo cp gateway/tenant-router.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable bedrock-proxy-h2 tenant-router
sudo systemctl start bedrock-proxy-h2 tenant-router
```

## 故障排查

### CloudFormation 栈删除在 PrivateSubnet 失败

**症状：** `aws cloudformation delete-stack` gets stuck, then reports `DELETE_FAILED` with:
```
The subnet 'subnet-xxx' has dependencies and cannot be deleted.
```

**原因：** AWS GuardDuty automatically creates managed VPC endpoints in every subnet it monitors. These endpoints block subnet deletion.

**修复：** Find and delete the GuardDuty-managed endpoints before retrying:

```bash
# Find GuardDuty endpoints in the stack's VPC
VPC_ID=$(aws ec2 describe-vpcs \
  --filters "Name=tag:aws:cloudformation:stack-name,Values=${STACK_NAME}" \
  --region $REGION --query 'Vpcs[0].VpcId' --output text)

ENDPOINTS=$(aws ec2 describe-vpc-endpoints \
  --filters "Name=vpc-id,Values=$VPC_ID" \
  --region $REGION \
  --query 'VpcEndpoints[?State!=`deleted`].VpcEndpointId' --output text)

aws ec2 delete-vpc-endpoints --vpc-endpoint-ids $ENDPOINTS --region $REGION

# Retry stack deletion
aws cloudformation delete-stack --stack-name $STACK_NAME --region $REGION
```

> **Note:** This does not disable GuardDuty — it only removes the endpoint ENIs that were blocking deletion. GuardDuty will recreate them in any new subnets automatically.

> **Prevention:** Deploying with `CreateVPCEndpoints=false` (default) avoids creating a PrivateSubnet, which is the only subnet GuardDuty consistently attaches to in this template. The CloudFormation template has been updated to skip PrivateSubnet creation when VPC endpoints are disabled.

### `deploy.sh` fails: ECR repo is empty after `--skip-build`

**症状：** AgentCore runtime creation fails with "specified image identifier does not exist."

**原因：** `--skip-build` skips the Docker build, but if this is the first deploy of a new stack, the ECR repo will be empty.

**修复：** Run without `--skip-build` on first deploy. The script builds on the gateway EC2 via SSM — no local Docker needed.

### AgentCore returns HTTP 500 on every message

**原因：** Almost always a wrong `openclaw` npm package version inside the container.

**检查：**
```bash
aws logs tail /aws/bedrock-agentcore/runtimes/<runtime-id>-DEFAULT --follow
# Look for: "openclaw returned empty output"
```

**修复：** Rebuild the Docker image. Both `agent-container/Dockerfile` and `exec-agent/Dockerfile` must install `openclaw@2026.3.24` exactly — do not upgrade.

---

构建者：[wjiad@aws](mailto:wjiad@amazon.com) · [aws-samples](https://github.com/aws-samples) · 欢迎贡献
