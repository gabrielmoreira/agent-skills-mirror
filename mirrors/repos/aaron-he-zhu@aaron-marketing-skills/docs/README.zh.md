<div align="center">

# Aaron 营销技能库

**120 个营销技能 —— 品牌叙事、SEO/GEO、红人、付费广告、邮件、产品发布、自然社媒 —— 共享一套契约。**

<p align="center">
  <a href="https://github.com/aaron-he-zhu/aaron-marketing-skills"><img src="https://img.shields.io/github/stars/aaron-he-zhu/aaron-marketing-skills?style=flat" alt="GitHub Stars"></a>
  <a href="https://github.com/aaron-he-zhu/aaron-marketing-skills/blob/main/VERSIONS.md"><img src="https://img.shields.io/badge/version-16.0.0-orange" alt="Version"></a>
  <a href="https://github.com/aaron-he-zhu/aaron-marketing-skills/blob/main/LICENSE"><img src="https://img.shields.io/badge/license-Apache%202.0-green" alt="License"></a>
  <a href="https://github.com/aaron-he-zhu/aaron-marketing-skills/commits/main"><img src="https://img.shields.io/github/last-commit/aaron-he-zhu/aaron-marketing-skills" alt="Last Commit"></a>
</p>
<p align="center">
  <a href="https://www.skills.sh/aaron-he-zhu"><img src="https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/aaron-he-zhu/aaron-marketing-skills/main/badges/skillssh.json" alt="skills.sh"></a>
  <a href="https://clawhub.ai/aaron-he-zhu"><img src="https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/aaron-he-zhu/aaron-marketing-skills/main/badges/clawhub.json" alt="ClawHub"></a>
  <a href="https://skillhub.cn/user/user_2c0f1e77"><img src="https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/aaron-he-zhu/aaron-marketing-skills/main/badges/skillhub.json" alt="SkillHub"></a>
</p>

[English](../README.md) | **中文**

</div>

一套 Claude 技能与斜杠命令，让聊天 Agent 成为营销操作员。七个学科 + 一个共享协议层，一图总览（逻辑顺序：叙事 → 各常态频道 → 发布 → 协议）：

| 层 | 技能 | 生命周期（阶段目录） | 框架 → 门 | 入口命令 |
|----|------|----------------------|-----------|----------|
| **品牌叙事（TALE）** | 16 | trace → architect → land → evaluate | [TALE](../references/tale-benchmark.md) → `narrative-quality-auditor`（NQS） | `/aaron-marketing:narrative` |
| **SEO/GEO** | 16 | research → build → optimize → monitor | [CORE-EEAT](../references/core-eeat-benchmark.md) → `content-quality-auditor` · [CITE](../references/cite-domain-rating.md) → `domain-authority-auditor` | `/aaron-marketing:seo-geo` |
| **红人** | 16 | discover → plan → activate → measure | [C³](../references/c3-benchmark.md) → `content-reviewer`（ART）；`fit-scorer` 打 ACE 分 | `/aaron-marketing:influencer` |
| **付费广告（ROAS）** | 16 | research → orchestrate → activate → scale | [ROAS](../references/roas-benchmark.md) → `ad-account-auditor`（RQS） | `/aaron-marketing:ad` |
| **邮件营销（SEND）** | 16 | setup → engage → nurture → deliver | [SEND](../references/send-benchmark.md) → `email-quality-auditor`（EQS） | `/aaron-marketing:email` |
| **产品发布（RAMP）** | 16 | research → assemble → mobilize → prove | [RAMP](../references/ramp-benchmark.md) → `launch-readiness-auditor`（LQS） | `/aaron-marketing:launch` |
| **自然社媒（ECHO）** | 16 | explore → craft → host → observe | [ECHO](../references/echo-benchmark.md) → `social-quality-auditor`（SQS） | `/aaron-marketing:social` |
| **协议层** | 8 | ——（阶段流程之外的共享机件） | 7 个真相注册表（实体 · 创作者 · offer/声明 · 同意 · 发布 · 频道 · 叙事）+ HOT/WARM/COLD 记忆 | —— |

`/aaron-marketing:auto` 把任意自然语言目标路由到全库。全部为**纯 Markdown** —— 唯一的代码是一个 Bash hook runner、一个 Bash 校验器、以及零依赖的 Python 标准库数据助手（无 `pip`、无构建步骤）。**每个技能都能在 Tier 1 仅凭你粘贴的数据运行**；连接器只是自动化取数。这不是一堆平级学科的堆叠，而是一套**四层营销操作系统**——详见下方[架构 § 四层营销操作系统](#四层营销操作系统)。

> 合并前的两个独立仓库现均为**纯路标仓库**——[seo-geo-claude-skills](https://github.com/aaron-he-zhu/seo-geo-claude-skills)（最终 20 技能版本线保留于 tag `v9.9.12`）与 [influencer-marketing-agent-skills](https://github.com/aaron-he-zhu/influencer-marketing-agent-skills)（最终 IMPACT 版本线保留于 tag `standalone-final`），安装一律指向本仓库。兄弟仓库策略见 [docs/repo-family.md](repo-family.md)。

---

## 目录

- [为什么选它](#为什么选它)
- [安装](#安装)
- [初次使用](#初次使用)
- [架构](#架构)
  - [共享技能契约](#共享技能契约)
  - [四层营销操作系统](#四层营销操作系统)
  - [质量体系：八框架、八门](#质量体系八框架八门)
  - [协议层](#协议层)
  - [记忆与自动化](#记忆与自动化)
- [技能目录](#技能目录)
  - [品牌叙事 — TALE（16）](#品牌叙事--tale16)
  - [SEO/GEO（16）](#seogeo16)
  - [红人（16）](#红人16)
  - [付费广告 — ROAS（16）](#付费广告--roas16)
  - [邮件营销 — SEND（16）](#邮件营销--send16)
  - [产品发布 — RAMP（16）](#产品发布--ramp16)
  - [自然社媒 — ECHO（16）](#自然社媒--echo16)
  - [协议层（8）](#协议层8)
- [命令](#命令)
- [连接器与层级](#连接器与层级)
- [推荐工作流](#推荐工作流)
- [仓库结构](#仓库结构)
- [设计哲学](#设计哲学)
- [质量守卫](#质量守卫)
- [贡献与文档](#贡献与文档)
- [免责声明](#免责声明)
- [许可证](#许可证)

---

## 为什么选它

| 原则 | 落到实处 |
|------|----------|
| **默认 keyless** | 每个技能都能在 **Tier 1** 仅凭粘贴的数据、或从免费/第一方来源拉取的数据运行。付费工具与 MCP 服务器是可选项，绝非前提。付费广告技能基于**自有账户手动导出**评分——带密钥的广告 API 永不必需。 |
| **是 Markdown，不是框架** | 技能即内容。唯一可执行代码是 `hooks/claude-hook.sh`（Bash）、`scripts/validate-skill.sh`（Bash）、`scripts/connectors/*.py`（**仅标准库**）。无需安装、审计或维护。 |
| **一套共享契约** | 120 个技能暴露同样的七段结构，并自带 `discipline` + `phase` 元数据，整个库像一套操作系统：每个技能都知道自己的输入、输出，以及下一个该交棒的技能。 |
| **带门的质量** | 八套基准驱动八个 auditor-class 门，产出结构化、可机器校验的判定——不是凭感觉。每个带门工件落盘前都经 PostToolUse hook 校验。 |
| **真相住在注册表里** | 规范事实（品牌实体、创作者档案、offer/声明实证）住在协议层专职注册表中，唯一写入者规则——门对照注册表评判，而非各自重新推导。 |
| **跨轮记忆** | HOT/WARM/COLD 记忆模型在技能与会话之间携带发现、分数与未决事项，并在写入时净化。 |
| **人话** | 技能内置 AI 腔检测器与禁用词表，让输出读起来像人写的。 |

---

## 安装

可配合 Claude Code、任意 Agent Skills 兼容宿主，或直接 `git clone`：

| 宿主 | 安装 |
|------|------|
| **Claude Code** | `/plugin marketplace add aaron-he-zhu/aaron-marketing-skills` 然后 `/plugin install aaron-marketing@aaron` |
| **Codex · Cursor · OpenCode · Antigravity · Gemini CLI · Copilot CLI · OpenClaw · Hermes · [70+ 宿主](https://github.com/vercel-labs/skills#supported-agents)** | `npx skills add aaron-he-zhu/aaron-marketing-skills` |
| **[SkillHub.cn](https://skillhub.cn)(中文社区)** | `skillhub install aaron-<技能名>`(如 `aaron-keyword-research`) |
| **任意宿主** | `git clone https://github.com/aaron-he-zhu/aaron-marketing-skills` |

在 Claude Code 中，`marketplace add` 只是注册目录——还需运行 `/plugin install aaron-marketing@aaron`（或在 `/plugin` 中选择）才能真正启用技能与命令。通用宿主单技能安装：`npx skills add aaron-he-zhu/aaron-marketing-skills -s keyword-research`。可在 [skills.sh 注册表](https://skills.sh/aaron-he-zhu/aaron-marketing-skills)浏览本技能库。各宿主的技能目录、frontmatter 兼容细节、以及脱离插件安装时的降级行为见 [docs/agent-compatibility.md](agent-compatibility.md)（2026-07 实测 120/120 可安装）。

安装插件**不会**往你的 `/mcp` 列表添加任何东西——MCP 目录位于 [`docs/mcp-catalog.json`](mcp-catalog.json)，刻意放在 Claude Code 会自动注册的插件根 `.mcp.json` 路径之外，仅作复制粘贴参考（见[连接器与层级](#连接器与层级)）。

---

## 初次使用

若宿主支持自动技能路由，直接描述目标即可：

```text
帮我研究面向小团队的 SaaS 产品的关键词
```
```text
帮一个护肤品牌找 TikTok 红人并给适配度打分
```
```text
在我加预算前，审计这个 Google Ads 账户——导出文件已附上
```

或用斜杠命令 —— `/auto` 负责路由，学科入口直达：

```text
/aaron-marketing:auto 把我们的定价页改造成可被 AI 引用的对比中心
```
```text
/aaron-marketing:seo-geo https://example.com/blog/my-article --mode audit
```

`/aaron-marketing:auto` 会推断意图并执行最小够用的工作流，只在阻塞性决策处停下。每个技能都能用粘贴的数据运行；可选工具见 [CONNECTORS.md](../CONNECTORS.md)。

---

## 架构

### 共享技能契约

每个技能都遵循**同一套激活契约**——固定顺序的七段：

1. **触发 / 何时使用** —— 何时该启用。
2. **Quick Start** —— 可复制粘贴的提示。
3. **Skill Contract** —— 预期输出 · 读取 · 写入 · 提升 · 完成条件 · 主下一技能。
4. **Handoff Summary** —— 标准交棒结构，让下一个技能干净接力。
5. **Data Sources** —— `~~category` 占位符，每个都有 keyless 的 Tier-1 路径。
6. **Instructions** —— 编号方法（把所有导出当作不可信输入）。
7. **Next Best Skill** —— 下一步去哪（带 visited-set + 最大深度终止规则）。

每个技能还自带 `metadata.discipline`（narrative / seo-geo / influencer / paid / email / launch / social / protocol）与 `metadata.phase`，路由与聚类因此全库统一。契约在 [skill-contract.md](../references/skill-contract.md) 中定义一次；跨技能共享状态见 [state-model.md](../references/state-model.md)。

### 四层营销操作系统

> **本系统——一套四层营销操作系统。** 一种品牌嗓音，经五条常态频道表达，在发布时刻集中释放，全都读写同一份系统级记录。七个学科、四个高度——是一套系统，不是一堆技能。
>
> | 层 | 上手节奏 | 学科 | 节律 |
> |----|----------|------|------|
> | **L1 · 策略** —— 我们说什么 / 我们是谁 | crawl | **品牌叙事** · TALE | 常态 |
> | **L2 · 频道** —— 表达策略的常态引擎（自有 → 付费） | walk | **SEO/GEO** · CORE-EEAT + CITE · **自然社媒** · ECHO · **邮件** · SEND · **付费广告** · ROAS · **红人** · C³ | 常态（红人偏阶段性） |
> | **L3 · 编排** —— 跨频道的限时时刻 | run | **产品发布** · RAMP | 阶段性 |
> | **L4 · 协议** —— 共享的系统级记录 | —— | 8 个真相注册表 + 记忆 · 8 个 auditor 门 · 一套技能契约 | —— |
>
> 叙事是消息，频道是表达它的媒介——拿掉任何一条频道，记录依然完整；拿掉叙事，每条频道说出的都是无出处、无治理的消息。每条频道都像今天每个 creative builder 已经在读声明台账那样，从 L1 继承嗓音与声明。每个学科自己的 4 阶段循环都活在它所属的层里（叙事 = Trace → Architect → Land → Evaluate）。

七个学科都用阶段**目录**（`narrative/trace/`…、`seo-geo/research/`…、`influencer/discover/`…、`ad/research/`…、`email/setup/`…、`launch/research/`…、`social/explore/`…）。注意 "activate" 在红人里指创作者外联、在付费里指账户门控——同词不同域。

### 质量体系：八框架、八门

八套基准让"好"可度量。每套定义维度、汇总方法，以及一小组**否决项**（无视其余分数直接封顶或阻断的硬性失败）：

| 框架 | 评分对象 | 项数 / 维度 | 汇总 | 否决项 |
|------|----------|-------------|------|--------|
| **[TALE](../references/tale-benchmark.md)** | 品牌叙事与消息（真实 · 架构 · 落地 · 证据） | T / A / L / E | **NQS = floor（目标加权均值）**（算术） | TALE `T1`/`A1`/`L1`/`E1` |
| **[CORE-EEAT](../references/core-eeat-benchmark.md)** | 内容质量（GEO = CORE 均值，SEO = EEAT 均值） | 80 项 / 8 维 | 各维度均值 | `T04`、`C01`、`R10` |
| **[CITE](../references/cite-domain-rating.md)** | 域名权威与引用信任 | 40 项 / 4 维 | 算术加权平均 | `T03`、`T05`、`T09` |
| **[C³](../references/c3-benchmark.md)** | 红人 创作者/内容/活动 | ACE / ART / ROI · 9 维 | **CVI =（ACE × ART × ROI）^⅓**（几何） | ACE `A2`/`C1`/`E2`、ART `T1`/`T2` |
| **[ROAS](../references/roas-benchmark.md)** | 付费广告 回报/报价/受众/花费效率 | R / O / A / S | **RQS = floor（目标加权均值）**（算术） | `R1`/`R2`/`O1`/`O2`/`A1` |
| **[SEND](../references/send-benchmark.md)** | 邮件营销 发件完整/送达 · 互动 · 培育/生命周期 · 直接响应/转化 | S / E / N / D | **EQS = floor（目标加权均值）**（算术） | `S1`/`S2`/`N1`/`D1` |
| **[RAMP](../references/ramp-benchmark.md)** | 产品发布 就绪 · 资产 · 势能 · 证明 | R / A / M / P · 4×10=40 项 | **LQS = floor（目标加权均值）**（算术） | RAMP `R1`/`A1`/`M1`/`P1`（与 ROAS 撞号，须带框架名限定） |
| **[ECHO](../references/echo-benchmark.md)** | 自然社媒 嵌入度 · 创作 · 运营 · 可观测性 | E / C / H / O | **SQS = floor（目标加权均值）**（算术） | ECHO `E1`/`C1`/`C2`/`H1`/`H2`/`O1`（`O1` 与 ROAS `O1`、`C1` 与 C³ `C1`/CORE `C01` 撞号，须带框架名限定） |

每套框架由一个 **auditor-class 门**执行——写出受 PostToolUse hook 校验的带门工件（`class: auditor-output`）。门是工作流步骤，所以驻留并计入各自学科：

| 门 | 框架 | 所在 | 判定 |
|----|------|------|------|
| [narrative-quality-auditor](../narrative/evaluate/narrative-quality-auditor/SKILL.md) | TALE NQS | `narrative/evaluate/`（品牌叙事） | 发布前 SHIP / FIX / BLOCK |
| [content-quality-auditor](../seo-geo/optimize/content-quality-auditor/SKILL.md) | CORE-EEAT | `seo-geo/optimize/`（SEO/GEO） | 发布前 SHIP / FIX / BLOCK |
| [domain-authority-auditor](../seo-geo/monitor/domain-authority-auditor/SKILL.md) | CITE | `seo-geo/monitor/`（SEO/GEO） | TRUSTED / CAUTIOUS / UNTRUSTED |
| [content-reviewer](../influencer/activate/content-reviewer/SKILL.md) | C³ ART | `influencer/activate/`（红人） | 创作者内容上线前 APPROVED / REVISIONS / REJECTED |
| [ad-account-auditor](../ad/activate/ad-account-auditor/SKILL.md) | ROAS RQS | `ad/activate/`（付费） | 加预算前 SHIP / FIX / BLOCK |
| [email-quality-auditor](../email/deliver/email-quality-auditor/SKILL.md) | SEND EQS | `email/deliver/`（邮件） | 发送前 SHIP / FIX / BLOCK |
| [launch-readiness-auditor](../launch/mobilize/launch-readiness-auditor/SKILL.md) | RAMP LQS | `launch/mobilize/`（产品发布） | 发布前 SHIP / FIX / BLOCK |
| [social-quality-auditor](../social/host/social-quality-auditor/SKILL.md) | ECHO SQS | `social/host/`（自然社媒） | 发布前 SHIP / FIX / BLOCK |

**共享封顶法：** 单个否决项把受影响维度与总分封顶到 `min(raw, 60)`；**两个及以上否决项 → `BLOCKED`**（无最终分）。判定对用户翻译成人话（报告里不出现项目 ID）。门的机制——handoff schema、封顶算术、工件门清单——在 [auditor-runbook.md](../references/auditor-runbook.md) 统一规定，八套框架的算术由确定性 golden 测试锁定（见[质量守卫](#质量守卫)）。

### 协议层

`protocol/` 目录承载学科阶段流程之外的**共享真相与记忆机件** —— 8 个技能，单独计数：

| 技能 | 职责 | 锚定 | 规范存储 |
|------|------|------|----------|
| [entity-optimizer](../protocol/entity-optimizer/SKILL.md) | 规范品牌/实体档案（知识图谱、Wikidata、AI 消歧） | SEO/GEO | `memory/entities/` |
| [creator-registry](../protocol/creator-registry/SKILL.md) | 规范创作者名册/档案——去重 handle、带溯源标签的受众数据、费率、合规历史 | 红人 | `memory/creators/` |
| [offer-claims-registry](../protocol/offer-claims-registry/SKILL.md) | offer 与声明实证台账——O1/T2 声明检查所对照评判的那份记录 | 付费 | `memory/claims/` |
| [consent-registry](../protocol/consent-registry/SKILL.md) | 规范的按主体同意/抑制记录——S2/N1 否决项对照评判的那份记录 | 邮件 | `memory/consent/` |
| [launch-registry](../protocol/launch-registry/SKILL.md) | 发布台账——每次发布的规范档案与发布日历：分级/类型、生命周期阶段（draft→GA 单向）、权威日期与禁运期承诺、渠道提交台账（launch 真相 SSOT） | 产品发布 | `memory/launch-registry/` |
| [channel-registry](../protocol/channel-registry/SKILL.md) | 规范频道台账——去重 handle、按平台归属、粉丝/互动率基线（带溯源标签的命名/周期稳定分母）、认领状态与运营史；ECHO `E1` 否决项对照评判的那份记录（无记录 = NEEDS_INPUT） | 自然社媒 | `memory/channels/` |
| [narrative-registry](../protocol/narrative-registry/SKILL.md) | 规范品牌准则 SSOT——叙事、消息系统、语言/词表红线与定位真相；TALE 门与各频道 creative builder 对照评判并继承嗓音与声明的那份记录 | 品牌叙事 | `memory/narrative-registry/` |
| [memory-management](../protocol/memory-management/SKILL.md) | HOT/WARM/COLD 记忆生命周期（捕获 · 提升 · 降级 · 归档 · 查询） | 全部学科 | `memory/` |

注册表遵循**唯一写入者规则**（其他技能经 `candidates.md` 投递），且注册表只*存证*——评判归门。最底层真正横向的是 `references/` 协议（[auditor-runbook](../references/auditor-runbook.md)、[state-model](../references/state-model.md)、[skill-contract](../references/skill-contract.md)、[humanizer-slop](../references/humanizer-slop.md)、[measurement-protocol](../references/measurement-protocol.md)）——按设计以文档而非技能的形式共享。

### 记忆与自动化

**记忆**按温度分层，让上下文跨技能与会话留存而不撑爆提示：

| 层 | 位置 | 行为 |
|----|------|------|
| **HOT** | `memory/hot-cache.md` | 每次会话自动加载；封顶 **80 行 且 25 KB**（先触发者为准）。 |
| **WARM** | `memory/<subdir>/` | 各技能工作状态、带门审计工件（`memory/audits/`）、注册表规范存储（`memory/entities\|creators\|claims/`）。 |
| **COLD** | `memory/archive/` | 降级/较旧记录，留作召回。 |

**Hooks**（`hooks/hooks.json`，runner `hooks/claude-hook.sh`）接入四个 Claude Code 事件：

| 事件 | 匹配 | 作用 |
|------|------|------|
| `SessionStart` | `startup\|resume\|clear\|compact` | 注入**净化后**的 hot-cache + 未决事项指针（提示注入行被涂掉；符号链接缓存被拒）。 |
| `UserPromptSubmit` | （全部） | 轻量逐提示上下文 hook。 |
| `PostToolUse` | `Write\|Edit` | hot-cache 体积告警 **+ Artifact Gate**：写到 `memory/audits/` 下、声明了 `class: auditor-output` 的文件都会被校验 handoff schema 与封顶字段，不合规则拦截写入。八个 auditor-class 门按契约必须声明该标记；未标记的文件不是审计工件，直接放行。 |
| `Stop` | （全部） | 空操作（静默退出）。 |

Artifact Gate 是**框架无关**的——同一个 hook 校验 CORE-EEAT、CITE、C³、ROAS、SEND、RAMP、ECHO、TALE 工件，无任何针对单框架的代码。

---

## 技能目录

技能链接打开各自的 `SKILL.md`。展开每个学科下的 **详情** 可看每个技能的一句话用途。学科按逻辑分层排序（策略层的品牌叙事居首）。

### 品牌叙事 — TALE（16）

`narrative/` 下四个阶段目录按 TALE 循环排布（Trace → Architect → Land → Evaluate）；本学科的门（⛩ narrative-quality-auditor）位于 Evaluate。只有门计算目标加权 NQS——其余技能各管一个杠杆并交棒。这是策略层（L1）——一种品牌嗓音，各常态频道从这里继承嗓音与声明。叙事吸收了定位（`positioning-mapper` 物理上仍在 `launch/`，逻辑上读作 TALE Trace 的最前端）。

| 阶段 | 技能 |
|------|------|
| **Trace 溯源** | [narrative-baseline-mapper](../narrative/trace/narrative-baseline-mapper/SKILL.md), [category-narrative-mapper](../narrative/trace/category-narrative-mapper/SKILL.md), [audience-belief-mapper](../narrative/trace/audience-belief-mapper/SKILL.md), [positioning-truth-tracer](../narrative/trace/positioning-truth-tracer/SKILL.md) |
| **Architect 架构** | [strategic-narrative-designer](../narrative/architect/strategic-narrative-designer/SKILL.md), [message-system-architect](../narrative/architect/message-system-architect/SKILL.md), [brand-language-codifier](../narrative/architect/brand-language-codifier/SKILL.md), [story-bank-builder](../narrative/architect/story-bank-builder/SKILL.md) |
| **Land 落地** | [narrative-cascade-planner](../narrative/land/narrative-cascade-planner/SKILL.md), [pitch-narrative-builder](../narrative/land/pitch-narrative-builder/SKILL.md), [narrative-enablement-kit](../narrative/land/narrative-enablement-kit/SKILL.md), [proof-point-packager](../narrative/land/proof-point-packager/SKILL.md) |
| **Evaluate 评估** | ⛩ [narrative-quality-auditor](../narrative/evaluate/narrative-quality-auditor/SKILL.md), [message-test-designer](../narrative/evaluate/message-test-designer/SKILL.md), [narrative-resonance-monitor](../narrative/evaluate/narrative-resonance-monitor/SKILL.md), [narrative-drift-monitor](../narrative/evaluate/narrative-drift-monitor/SKILL.md) |

<details><summary><b>逐技能用途（品牌叙事）</b></summary>

| 技能 | TALE 杠杆 | 用途 |
|------|-----------|------|
| narrative-baseline-mapper | T | 盘点现有叙事基线——散落在各资产/频道里的消息、口径漂移、缺口。 |
| category-narrative-mapper | T | 品类叙事地图——竞争替代品的说法、品类框架、可占领的语义空白。 |
| audience-belief-mapper | T | 受众信念地图——现有认知、异议、要跨越的信念鸿沟。 |
| positioning-truth-tracer | T | 把定位主张回溯到可证事实——每条声明有出处、可实证（复用 positioning-mapper）。 |
| strategic-narrative-designer | A | 战略叙事设计——变革叙事弧、赌注、"为何是现在"。 |
| message-system-architect | A | 消息系统架构——tagline、支柱、PR-FAQ 脊柱，感知声明台账（复用 message-house-builder）。 |
| brand-language-codifier | A | 品牌语言编纂——词表、嗓音、口吻红线，写入 narrative-registry 供各频道继承。 |
| story-bank-builder | A | 故事库——客户故事、类比、证据叙事的可复用素材库。 |
| narrative-cascade-planner | L | 叙事级联计划——把 L1 消息落到各频道/受众/阶段的分发地图。 |
| pitch-narrative-builder | L | pitch 叙事——面向媒体/投资人/销售的一页叙事与演示脊柱。 |
| narrative-enablement-kit | L | 叙事赋能包——供内部/合作方一致复述的话术、FAQ、do/don't。 |
| proof-point-packager | L | 证据点打包——把主张配上可核验证据、数据、第三方背书。 |
| ⛩ narrative-quality-auditor | T+A+L+E（NQS） | auditor-class TALE 门：算 NQS、跑 T1/A1/L1/E1、产出 SHIP/FIX/BLOCK；含**发布前 go/no-go**模式。写入 `memory/audits/narrative/`。 |
| message-test-designer | E | 消息测试设计——A/B 消息、信念位移测量、受众验证实验。 |
| narrative-resonance-monitor | E | 叙事共鸣监控——消息采纳、复述保真、共鸣信号（复用 bluesky.py/gdelt.py/tavily.py/wayback.py 为 proxy，始终标注）。 |
| narrative-drift-monitor | E | 叙事漂移监控——跨频道口径偏离、失控消息、准则违规预警。 |

**跨学科复用**（计入原阶段，不重复造轮子）：[positioning-mapper](../launch/research/positioning-mapper/SKILL.md)（物理留在 launch，逻辑读作 TALE Trace 最前端）、[message-house-builder](../launch/assemble/message-house-builder/SKILL.md)、[audience-mapper](../influencer/discover/audience-mapper/SKILL.md)、[share-of-voice-tracker](../social/observe/share-of-voice-tracker/SKILL.md)。**无新增连接器**——叙事共鸣复用 `bluesky.py`/`gdelt.py`/`tavily.py`/`wayback.py`。品牌叙事真相注册表 `narrative-registry` 位于协议层。

</details>

### SEO/GEO（16）

四个阶段目录，外加本学科的两个质量门（标 ⛩）。

| 阶段 | 技能 |
|------|------|
| **研究** | [keyword-research](../seo-geo/research/keyword-research/SKILL.md), [competitor-analysis](../seo-geo/research/competitor-analysis/SKILL.md), [serp-analysis](../seo-geo/research/serp-analysis/SKILL.md), [content-gap-analysis](../seo-geo/research/content-gap-analysis/SKILL.md) |
| **构建** | [content-writer](../seo-geo/build/content-writer/SKILL.md)（合并 seo-content-writer + content-refresher）, [geo-content-optimizer](../seo-geo/build/geo-content-optimizer/SKILL.md), [serp-markup-builder](../seo-geo/build/serp-markup-builder/SKILL.md)（合并 meta-tags-optimizer + schema-markup-generator）, [page-play-builder](../seo-geo/build/page-play-builder/SKILL.md)（合并 programmatic + parasite + comparison + local，4 模式） |
| **优化** | ⛩ [content-quality-auditor](../seo-geo/optimize/content-quality-auditor/SKILL.md), [technical-seo-checker](../seo-geo/optimize/technical-seo-checker/SKILL.md), [on-page-seo-auditor](../seo-geo/optimize/on-page-seo-auditor/SKILL.md), [site-structure-optimizer](../seo-geo/optimize/site-structure-optimizer/SKILL.md)（合并 internal-linking-optimizer + site-architecture） |
| **监控** | ⛩ [domain-authority-auditor](../seo-geo/monitor/domain-authority-auditor/SKILL.md), [rank-tracker](../seo-geo/monitor/rank-tracker/SKILL.md), [performance-monitor](../seo-geo/monitor/performance-monitor/SKILL.md)（合并 performance-reporter + alert-manager）, [offsite-signal-analyzer](../seo-geo/monitor/offsite-signal-analyzer/SKILL.md)（合并 backlink-analyzer + ai-traffic） |

<details><summary><b>逐技能用途（SEO/GEO）</b></summary>

| 技能 | 用途 |
|------|------|
| keyword-research | 为页面/主题/活动开启关键词工作——意图、需求、临门一脚机会。 |
| competitor-analysis | 分析竞品 SEO 策略，对比域名，挖出其关键词与缺口。 |
| serp-analysis | 读懂 SERP——特性、摘要、People Also Ask、某查询的排名规律。 |
| content-gap-analysis | 找出相对竞品缺失的主题与覆盖空洞。 |
| content-writer | 撰写并刷新 SEO 优化的文章、博文、落地页、产品文案（合并 seo-content-writer + content-refresher）。 |
| geo-content-optimizer | 为 AI 引擎（ChatGPT、Perplexity、AI Overviews、Gemini、Claude、Copilot）优化内容。 |
| serp-markup-builder | 标题标签、元描述、Open Graph、Twitter Cards + JSON-LD / Schema.org 结构化数据（合并 meta-tags-optimizer + schema-markup-generator）。 |
| page-play-builder | programmatic / parasite / comparison / local 四模式页面打法——模板批量页、第三方平台发布、对比页、本地 SEO（合并 4 个技能）。 |
| ⛩ content-quality-auditor | 80 项 CORE-EEAT 发布就绪门（SHIP/FIX/BLOCK）。 |
| technical-seo-checker | 站点速度、Core Web Vitals、索引、可抓取性、robots。 |
| on-page-seo-auditor | 审计页面级 on-page 健康度——标题层级、关键词布局、图片、质量信号。 |
| site-structure-optimizer | 内链结构、锚文本分布、孤立页 + 页面层级、导航、URL 分类、hub/spoke 主题集群（合并 internal-linking-optimizer + site-architecture）。 |
| ⛩ domain-authority-auditor | 40 项 CITE 域名信任门（TRUSTED/CAUTIOUS/UNTRUSTED）。 |
| rank-tracker | 跟踪关键词排名、位次变化与跌幅。 |
| performance-monitor | 多指标 SEO/GEO 绩效报告与看板 + 排名/流量/外链/技术/AI 可见性告警（合并 performance-reporter + alert-manager）。 |
| offsite-signal-analyzer | 外链档案、链接质量、毒链、锚文本分布 + 在你自己的 GA4 / GSC / 服务器日志中度量 AI 助手引荐流量（合并 backlink-analyzer + ai-traffic）。 |

</details>

### 红人（16）

四个阶段目录（原 6 阶段 insight+map→discover、activate+convert→activate、track→measure）；本学科的门（⛩ content-reviewer）位于 Activate。

| 阶段 | 技能 |
|------|------|
| **Discover 发现** | [audience-mapper](../influencer/discover/audience-mapper/SKILL.md)（合并 audience-analyzer + niche-researcher）, [trend-spotter](../influencer/discover/trend-spotter/SKILL.md), [influencer-discovery](../influencer/discover/influencer-discovery/SKILL.md), [fit-scorer](../influencer/discover/fit-scorer/SKILL.md) |
| **Plan 规划** | [competitor-tracker](../influencer/plan/competitor-tracker/SKILL.md), [campaign-planner](../influencer/plan/campaign-planner/SKILL.md), [brief-generator](../influencer/plan/brief-generator/SKILL.md), [budget-optimizer](../influencer/plan/budget-optimizer/SKILL.md) |
| **Activate 启动** | [outreach-manager](../influencer/activate/outreach-manager/SKILL.md), ⛩ [content-reviewer](../influencer/activate/content-reviewer/SKILL.md), [contract-helper](../influencer/activate/contract-helper/SKILL.md), [content-amplifier](../influencer/activate/content-amplifier/SKILL.md)（合并 content-amplifier + ugc-repurposer） |
| **Measure 度量** | [landing-optimizer](../influencer/measure/landing-optimizer/SKILL.md), [performance-analyzer](../influencer/measure/performance-analyzer/SKILL.md), [roi-calculator](../influencer/measure/roi-calculator/SKILL.md), [report-generator](../influencer/measure/report-generator/SKILL.md) |

<details><summary><b>逐技能用途（红人）</b></summary>

| 技能 | 用途 |
|------|------|
| audience-mapper | 在项目开始或进入新细分时做受众画像，并摸清某个亚文化 / 微社群（合并 audience-analyzer + niche-researcher）。 |
| trend-spotter | 活动节奏与主题——趋势话题、声音、内容格式、文化时刻。 |
| influencer-discovery | 从零搭建红人名单、拓展新平台、规模化找 nano/micro。 |
| fit-scorer | 对候选名单做客观加权适配打分（基于 C³ ACE）。 |
| competitor-tracker | 竞品的合作红人、活动、格式、估算触达/花费与缺口。 |
| campaign-planner | 规划活动、产品发布、tentpole 或常态化创作者项目。 |
| brief-generator | 标准化红人 brief 与可复用团队模板。 |
| budget-optimizer | 跨层级/平台分配预算、预测 ROI、建模场景（同时服务付费广告的花费 + 出价节奏）。 |
| outreach-manager | pitch、跟进节奏、再激活、费率谈判、状态跟踪。 |
| ⛩ content-reviewer | 对红人提交内容做发布前门决策（C³ ART：FTC 披露 T1、声明真实性 T2）。 |
| contract-helper | 起草/审阅创作者协议——使用权、独家、标准条款。 |
| content-amplifier | 用付费投放放大自然创作者内容（白名单、Spark Ads、暗帖），并把 UGC 二次利用到付费、网站、邮件、自然社媒（合并 content-amplifier + ugc-repurposer）。 |
| landing-optimizer | 面向创作者/付费流量的落地页——信息一致、移动端、A/B（同时服务付费点击后）。 |
| performance-analyzer | 评估创作者结果、横比创作者、情感、转化（同时是付费跨渠道记分卡）。 |
| roi-calculator | 度量/预测 ROI、为预算辩护、评估创作者/层级价值（共享回报计算引擎，含付费）。 |
| report-generator | 周期结束后面向特定利益相关者的书面报告（同时出付费广告报告）。 |

</details>

### 付费广告 — ROAS（16）

`ad/` 下四个阶段目录按 ROAS 循环排布；本学科的门（⛩ ad-account-auditor）位于 Activate。只有门计算目标加权 RQS——其余技能各管一个杠杆并交棒。

| 阶段 | 技能 |
|------|------|
| **Research 研究** | [campaign-architect](../ad/research/campaign-architect/SKILL.md), [audience-segment-builder](../ad/research/audience-segment-builder/SKILL.md), [search-term-miner](../ad/research/search-term-miner/SKILL.md)（NEW）, [product-feed-optimizer](../ad/research/product-feed-optimizer/SKILL.md)（NEW） |
| **Orchestrate 编排** | [ad-creative-builder](../ad/orchestrate/ad-creative-builder/SKILL.md), [ad-test-designer](../ad/orchestrate/ad-test-designer/SKILL.md), [bid-strategy-planner](../ad/orchestrate/bid-strategy-planner/SKILL.md)（NEW）, [landing-experience-checker](../ad/orchestrate/landing-experience-checker/SKILL.md)（NEW） |
| **Activate 激活** | ⛩ [ad-account-auditor](../ad/activate/ad-account-auditor/SKILL.md), [conversion-signal-qa](../ad/activate/conversion-signal-qa/SKILL.md), [placement-exclusion-manager](../ad/activate/placement-exclusion-manager/SKILL.md)（NEW）, [conversion-value-mapper](../ad/activate/conversion-value-mapper/SKILL.md)（NEW） |
| **Scale 放大** | [paid-measurement-loop](../ad/scale/paid-measurement-loop/SKILL.md), [attribution-reconciler](../ad/scale/attribution-reconciler/SKILL.md), [budget-pacing-monitor](../ad/scale/budget-pacing-monitor/SKILL.md)（NEW）, [fatigue-frequency-manager](../ad/scale/fatigue-frequency-manager/SKILL.md)（NEW） |

<details><summary><b>逐技能用途（付费广告）</b></summary>

| 技能 | ROAS 杠杆 | 用途 |
|------|-----------|------|
| campaign-architect | A + 结构 | 账户/活动结构、campaign 类型选型、匹配类型、否定词/排除、付费↔自然蚕食。 |
| audience-segment-builder | A | 把自有客户/CRM/GA4 导出转为种子受众、相似种子、排除人群、跨平台漏斗分层地图。 |
| search-term-miner（NEW） | A | 从搜索词报告挖掘新增否定词与拓展词，收敛匹配类型漏斗。 |
| product-feed-optimizer（NEW） | O | Shopping/PMax 商品 feed 质量——标题/属性/GTIN、feed 覆盖与拒登修复。 |
| ad-creative-builder | O | RSA 标题/描述、hook、角度矩阵，并与落地页信息一致。 |
| ad-test-designer | O（+S） | 设计 A/B/n 与增量实验（假设、变体矩阵、样本量/功效），判读显著性 → promote/kill。 |
| bid-strategy-planner（NEW） | S | 出价策略选型、tCPA/tROAS 目标设定、学习期与出价上限规划。 |
| landing-experience-checker（NEW） | O | 点击后落地体验 QA——信息一致、加载速度、移动端、转化路径。 |
| ⛩ ad-account-auditor | R+O+A+S（RQS） | auditor-class ROAS 门：算 RQS、跑 R1/R2/O1/O2/A1、产出 SHIP/FIX/BLOCK；含**上线 go/no-go**模式。 |
| conversion-signal-qa | R | 上线前追踪 QA（事件触发、UTM 规范、去重门控、窗口对齐、iOS-ATT 标记）——R1/R2 的前置（建信号，门打分）。 |
| placement-exclusion-manager（NEW） | S | 版位/展示位排除——低质站点、app 品类、品牌安全清单治理。 |
| conversion-value-mapper（NEW） | R | 把转化事件映射到价值/毛利，配置价值规则与 tROAS 目标信号。 |
| paid-measurement-loop | R（+S） | 把一次上线的改动相对对照在窗口内回读 → Promote / Keep-testing / Rollback / Unproven。 |
| attribution-reconciler | R | 针对 GA4/ecommerce 订单ID真值集做常态去重、窗口/币种归一、模型对比、增量。 |
| budget-pacing-monitor（NEW） | S | 预算消耗节奏监控——超支/欠支告警、日内配速、月度落点预测。 |
| fatigue-frequency-manager（NEW） | O（+S） | 创意疲劳与频次治理——频次上限、轮换节奏、衰减信号识别。 |

**跨学科复用**（计入原阶段，不重复造轮子）：[budget-optimizer](../influencer/plan/budget-optimizer/SKILL.md)（花费 + 出价节奏/学习期模式）、[landing-optimizer](../influencer/measure/landing-optimizer/SKILL.md)（点击后）、[roi-calculator](../influencer/measure/roi-calculator/SKILL.md)（回报计算）、[report-generator](../influencer/measure/report-generator/SKILL.md)、[performance-analyzer](../influencer/measure/performance-analyzer/SKILL.md)。

</details>

### 邮件营销 — SEND（16）

`email/` 下四个阶段目录按 SEND 循环排布；本学科的门（⛩ email-quality-auditor）位于 Deliver。只有门计算目标加权 EQS——其余技能各管一个杠杆并交棒。用例无关（B2C 生命周期 / B2B 冷触达 / newsletter-creator），由目标权重列决定侧重。

| 阶段 | 技能 |
|------|------|
| **Setup 搭建** | [deliverability-qa](../email/setup/deliverability-qa/SKILL.md), [list-segment-builder](../email/setup/list-segment-builder/SKILL.md), [list-growth-designer](../email/setup/list-growth-designer/SKILL.md), [list-hygiene-monitor](../email/setup/list-hygiene-monitor/SKILL.md)（NEW） |
| **Engage 触达** | [email-creative-builder](../email/engage/email-creative-builder/SKILL.md), [subject-line-lab](../email/engage/subject-line-lab/SKILL.md)（NEW）, [email-render-builder](../email/engage/email-render-builder/SKILL.md)（NEW）, [dynamic-content-personalizer](../email/engage/dynamic-content-personalizer/SKILL.md)（NEW） |
| **Nurture 培育** | [email-sequence-designer](../email/nurture/email-sequence-designer/SKILL.md), [newsletter-monetization-planner](../email/nurture/newsletter-monetization-planner/SKILL.md), [preference-frequency-manager](../email/nurture/preference-frequency-manager/SKILL.md)（NEW）, [reactivation-specialist](../email/nurture/reactivation-specialist/SKILL.md)（NEW） |
| **Deliver 投递** | ⛩ [email-quality-auditor](../email/deliver/email-quality-auditor/SKILL.md), [send-experiment-designer](../email/deliver/send-experiment-designer/SKILL.md)（原 send-test-designer 改名）, [inbox-placement-monitor](../email/deliver/inbox-placement-monitor/SKILL.md)（NEW）, [cold-outbound-sequencer](../email/deliver/cold-outbound-sequencer/SKILL.md)（NEW） |

<details><summary><b>逐技能用途（邮件营销）</b></summary>

| 技能 | SEND 杠杆 | 用途 |
|------|-----------|------|
| deliverability-qa | S | 发送前 SPF/DKIM/DMARC/BIMI 认证、声誉、收件箱落位、垃圾内容、列表卫生（S1 检查）。 |
| list-segment-builder | E | 从自有列表/CRM/GA4 导出构建行为 + 生命周期阶段分群与抑制规则。 |
| list-growth-designer | S（+N） | 列表增长策略——获取渠道、lead magnet 构思、合规的双重确认捕获流程 spec、推荐环机制；在获取点保证 S 同意质量。 |
| list-hygiene-monitor（NEW） | S | 列表卫生监控——退信/未互动清理、sunset 政策、垃圾陷阱与投诉率治理。 |
| email-creative-builder | E / D | 主题行/预览文本/正文/CTA，与落地页信息一致，感知声明台账。 |
| subject-line-lab（NEW） | E | 主题行/预览文本创意与迭代——角度矩阵、长度/emoji/个性化实验、垃圾触发词规避。 |
| email-render-builder（NEW） | E / D | 邮件 HTML 渲染 QA——跨客户端兼容、暗色模式、纯文本 fallback、可访问性。 |
| dynamic-content-personalizer（NEW） | E | 动态内容/合并标签个性化——受众条件块、回退值、渲染安全校验。 |
| email-sequence-designer | N | 生命周期/自动化流程（欢迎、弃购、购后、召回）+ 频次治理。 |
| newsletter-monetization-planner | D | 付费订阅、赞助位库存 + 刊例、推荐增长循环经济。 |
| preference-frequency-manager（NEW） | N | 偏好中心与频次治理——订阅主题、频次上限、降频而非退订路径。 |
| reactivation-specialist（NEW） | N | 沉睡用户召回——win-back 序列、再确认、sunset 前最后一搏。 |
| ⛩ email-quality-auditor | S+E+N+D（EQS） | auditor-class SEND 门：算 EQS、跑 S1/S2/N1/D1、产出 SHIP/FIX/BLOCK；含**发送前 go/no-go**模式。写入 `memory/audits/email/`。 |
| send-experiment-designer | E | A/B / 发送时间 / hold-out 设计，含样本量 + 显著性判读（promote/kill）（原 send-test-designer 改名）。 |
| inbox-placement-monitor（NEW） | S | 收件箱落位监控——seed 列表、垃圾/推广标签分布、ISP 级声誉追踪。 |
| cold-outbound-sequencer（NEW） | D | B2B 冷触达序列——分步跟进节奏、合规同意/退订、送达与回复优化。 |

**跨学科复用**（计入原阶段，不重复造轮子）：[audience-mapper](../influencer/discover/audience-mapper/SKILL.md)、[landing-optimizer](../influencer/measure/landing-optimizer/SKILL.md)（点击后）、[roi-calculator](../influencer/measure/roi-calculator/SKILL.md)（回报计算）、[report-generator](../influencer/measure/report-generator/SKILL.md)、[performance-analyzer](../influencer/measure/performance-analyzer/SKILL.md)、[offer-claims-registry](../protocol/offer-claims-registry/SKILL.md)。

</details>

### 产品发布 — RAMP（16）

`launch/` 下四个阶段目录按 RAMP 循环排布；本学科的门（⛩ launch-readiness-auditor，LQS 门禁）位于 Mobilize。只有门计算目标加权 LQS——其余技能各管一个杠杆并交棒。

| 阶段 | 技能 |
|------|------|
| **Research 研究** | [positioning-mapper](../launch/research/positioning-mapper/SKILL.md), [launch-tier-planner](../launch/research/launch-tier-planner/SKILL.md), [launch-window-planner](../launch/research/launch-window-planner/SKILL.md), [early-access-designer](../launch/research/early-access-designer/SKILL.md) |
| **Assemble 组装** | [message-house-builder](../launch/assemble/message-house-builder/SKILL.md), [launch-asset-packager](../launch/assemble/launch-asset-packager/SKILL.md), [pricing-packaging-planner](../launch/assemble/pricing-packaging-planner/SKILL.md), [sales-enablement-kit](../launch/assemble/sales-enablement-kit/SKILL.md) |
| **Mobilize 动员** | ⛩ [launch-readiness-auditor](../launch/mobilize/launch-readiness-auditor/SKILL.md), [launch-day-conductor](../launch/mobilize/launch-day-conductor/SKILL.md), [community-launch-runner](../launch/mobilize/community-launch-runner/SKILL.md), [press-media-relations](../launch/mobilize/press-media-relations/SKILL.md) |
| **Prove 证明** | [launch-monitor](../launch/prove/launch-monitor/SKILL.md), [launch-feedback-synthesizer](../launch/prove/launch-feedback-synthesizer/SKILL.md), [launch-retro-analyzer](../launch/prove/launch-retro-analyzer/SKILL.md), [momentum-planner](../launch/prove/momentum-planner/SKILL.md) |

<details><summary><b>逐技能用途（产品发布）</b></summary>

| 技能 | 用途 |
|------|------|
| positioning-mapper | 定位画布——竞争替代品、独特价值、滩头细分。 |
| launch-tier-planner | 发布分级与发布类型选型、风险登记册、kill criteria。 |
| launch-window-planner | 发布择时——竞品日历、禁运期窗口、平台审核缓冲。 |
| early-access-designer | waitlist 与内测阶梯、毕业标准、反馈闭环。 |
| message-house-builder | 消息屋 / PR-FAQ——价值支柱与发布叙事。 |
| launch-asset-packager | 资产清单、press kit、商店 listing 规格、上线检查。 |
| pricing-packaging-planner | 发布定价、梯度打包、早鸟优惠、保证设计。 |
| sales-enablement-kit | battle card、销售叙事、异议处理、内部 FAQ。 |
| ⛩ launch-readiness-auditor | 40 项 RAMP 发布就绪门（LQS，SHIP/FIX/BLOCK）。 |
| launch-day-conductor | 发布日 runbook——作战室、观察窗、回滚裁决。 |
| community-launch-runner | 社区发布——PH/HN 提交包、目录波次、平台红线。 |
| press-media-relations | 媒体名单、禁运期 pitch、新闻稿、分析师简报。 |
| launch-monitor | 发布监控——排名轮询、火焰战比、spike-vs-sustain。 |
| launch-feedback-synthesizer | 反馈分诊、状态环、社证收割、you-asked-we-shipped。 |
| launch-retro-analyzer | 发布复盘——渠道归因、5-Whys、keep/kill 决策。 |
| momentum-planner | 抗第二周断崖——changelog-as-GTM、relaunch、下一发布时刻。 |

</details>

### 自然社媒 — ECHO（16）

`social/` 下四个阶段目录按 ECHO 循环排布（Explore → Craft → Host → Observe）；本学科的门（⛩ social-quality-auditor）位于 Host。只有门计算目标加权 SQS——其余技能各管一个杠杆并交棒。用例无关（社区/开发者工具 · B2C 品牌 · B2B 创始人 IP），由目标权重列决定侧重。本学科**不含**任何发帖/互动/私信自动化——只做规划、创作与度量。

| 阶段 | 技能 |
|------|------|
| **Explore 探索** | [channel-portfolio-planner](../social/explore/channel-portfolio-planner/SKILL.md), [voice-dossier-builder](../social/explore/voice-dossier-builder/SKILL.md), [platform-norm-profiler](../social/explore/platform-norm-profiler/SKILL.md), [participation-warmup-planner](../social/explore/participation-warmup-planner/SKILL.md) |
| **Craft 创作** | [social-calendar-builder](../social/craft/social-calendar-builder/SKILL.md), [social-creative-builder](../social/craft/social-creative-builder/SKILL.md), [short-video-scripter](../social/craft/short-video-scripter/SKILL.md), [advocacy-program-designer](../social/craft/advocacy-program-designer/SKILL.md) |
| **Host 运营** | ⛩ [social-quality-auditor](../social/host/social-quality-auditor/SKILL.md), [engagement-inbox-manager](../social/host/engagement-inbox-manager/SKILL.md), [social-selling-planner](../social/host/social-selling-planner/SKILL.md), [crisis-response-planner](../social/host/crisis-response-planner/SKILL.md) |
| **Observe 观测** | [social-pulse-monitor](../social/observe/social-pulse-monitor/SKILL.md), [share-of-voice-tracker](../social/observe/share-of-voice-tracker/SKILL.md), [dark-social-attributor](../social/observe/dark-social-attributor/SKILL.md), [social-measurement-loop](../social/observe/social-measurement-loop/SKILL.md) |

<details><summary><b>逐技能用途（自然社媒）</b></summary>

| 技能 | ECHO 杠杆 | 用途 |
|------|-----------|------|
| channel-portfolio-planner | E | 频道组合选型——按 ICP/资源在西方平台与 **中文平台（小红书 / 微信公众号 / 视频号 / 抖音）** 之间分配投入、主/辅频道定位、频道对照 channel-registry 认领。 |
| voice-dossier-builder | C | 品牌语气档案——嗓音、口吻、词表与红线，跨频道一致。 |
| platform-norm-profiler | E | 平台规范画像——每个平台的格式、节奏、社区红线与算法偏好（含中文平台差异）。 |
| participation-warmup-planner | E | 冷启动前的真实参与预热——先融入社群再发声，genuine-question 才是入场券（非刷量）。 |
| social-calendar-builder | C | 社媒排期表——主题支柱、频次上限、跨频道内容日历（over-posting 是 H 守卫项）。 |
| social-creative-builder | C | 单条社媒创意——钩子、正文、CTA、话题标签，感知声明台账（C1）。 |
| short-video-scripter | C | 短视频脚本——Reels/Shorts/TikTok/**视频号/抖音** 的分镜、口播与开头 3 秒钩子。 |
| advocacy-program-designer | C | 员工/用户倡导计划——UGC 采集需**记录授权**（H2），披露物质关联（C2）。 |
| ⛩ social-quality-auditor | E+C+H+O（SQS） | auditor-class ECHO 门：算 SQS、跑 E1/C1/C2/H1/H2/O1、产出 SHIP/FIX/BLOCK；含**发布前 go/no-go**模式。写入 `memory/audits/social/`。 |
| engagement-inbox-manager | H | 互动收件箱**规划**——回复优先级、升级路径、模板库（不含任何自动回复/私信）。 |
| social-selling-planner | H | 社交销售规划——创始人 IP、真实关系建立、去自动化的触达节奏。 |
| crisis-response-planner | H | 危机响应预案——分级、发言人、暂停发布、模板（H1 不做刷量/操纵互动）。 |
| social-pulse-monitor | O | 社媒脉搏监控——提及、情感、话题（gdelt.py/tavily.py 为 proxy，始终标注）。 |
| share-of-voice-tracker | O | 声量份额追踪——对竞品的相对声量、周期稳定分母（O1）。 |
| dark-social-attributor | O | 暗社交归因——不可追踪引荐、self-reported 渠道、复制粘贴分享估算。 |
| social-measurement-loop | O | 把一次社媒动作相对基线在窗口内回读 → Promote / Keep-testing / Rollback / Unproven。 |

**跨学科复用**（计入原阶段，不重复造轮子）：[trend-spotter](../influencer/discover/trend-spotter/SKILL.md)、[audience-mapper](../influencer/discover/audience-mapper/SKILL.md)、[content-amplifier](../influencer/activate/content-amplifier/SKILL.md)、[outreach-manager](../influencer/activate/outreach-manager/SKILL.md)、[competitor-tracker](../influencer/plan/competitor-tracker/SKILL.md)、[landing-optimizer](../influencer/measure/landing-optimizer/SKILL.md)、[performance-analyzer](../influencer/measure/performance-analyzer/SKILL.md)、[roi-calculator](../influencer/measure/roi-calculator/SKILL.md)、[report-generator](../influencer/measure/report-generator/SKILL.md)、[offer-claims-registry](../protocol/offer-claims-registry/SKILL.md)、[community-launch-runner](../launch/mobilize/community-launch-runner/SKILL.md)、[creator-registry](../protocol/creator-registry/SKILL.md)、[page-play-builder](../seo-geo/build/page-play-builder/SKILL.md)、[memory-management](../protocol/memory-management/SKILL.md)。社媒真相注册表 `channel-registry` 位于协议层。

**中文平台覆盖：** 小红书 / 微信公众号 / 视频号 / 抖音以**手动数据包 / 用户导出**方式接入（无 keyless 官方公开 API）——技能照常在 Tier 1 用你粘贴或导出的数据运行；西方平台另配 keyless 连接器 `bluesky.py`、`fediverse.py`、`discourse.py` 与 `youtube.py --rss`。平台接入细节见 [social-platform-access.md](../references/social-platform-access.md)。

</details>

### 协议层（8）

共享真相与记忆机件——角色与唯一写入者规则见上文[架构 § 协议层](#协议层)。

| 组 | 技能 |
|----|------|
| **协议层** | [entity-optimizer](../protocol/entity-optimizer/SKILL.md), [creator-registry](../protocol/creator-registry/SKILL.md), [offer-claims-registry](../protocol/offer-claims-registry/SKILL.md), [consent-registry](../protocol/consent-registry/SKILL.md), [launch-registry](../protocol/launch-registry/SKILL.md), [channel-registry](../protocol/channel-registry/SKILL.md), [narrative-registry](../protocol/narrative-registry/SKILL.md), [memory-management](../protocol/memory-management/SKILL.md) |

<details><summary><b>逐技能用途（协议层）</b></summary>

| 技能 | 用途 |
|------|------|
| entity-optimizer | 面向知识图谱、Wikidata、AI 消歧的规范实体档案。 |
| creator-registry | 规范创作者名册/档案——去重 handle、带溯源标签的受众数据、费率与合规历史。 |
| offer-claims-registry | 规范 offer 与声明实证台账——O1/T2 声明检查所对照评判的那份记录。 |
| consent-registry | 规范的按主体邮件同意/抑制 SSOT——退订/退信/投诉历史，S2/N1 否决项对照评判。 |
| launch-registry | 发布台账/发布日历——分级、阶段（draft→GA 单向）、权威日期与禁运期承诺的唯一真相（launch SSOT）。 |
| channel-registry | 规范频道台账——去重 handle、按平台归属、粉丝/互动率基线（命名/周期稳定分母）、认领状态与运营史（social SSOT，ECHO E1 对照评判）。 |
| narrative-registry | 规范品牌准则 SSOT——叙事、消息系统、语言红线与定位真相；TALE 门与各频道 creative builder 对照评判并继承（narrative SSOT）。 |
| memory-management | 审阅、提升、降级、归档 HOT/WARM/COLD 项目记忆。 |

</details>

---

## 命令

8 个命令：`/aaron-marketing:auto` 跨七学科路由任意目标；每个学科恰有一个显式入口。源文件：[commands/](../commands)。

| 命令 | 用途 | 收窄 |
|------|------|------|
| `/aaron-marketing:auto` | 描述任意目标——推断意图并执行最小够用的工作流 | `--deep`（穷尽/压测） |
| `/aaron-marketing:narrative` | 品牌叙事（TALE 循环）：溯源现状与品类/受众信念、架构消息系统、级联落地与赋能、审计门与共鸣/漂移监控 | `--phase trace\|architect\|land\|evaluate` |
| `/aaron-marketing:seo-geo` | SEO/GEO 端到端：研究需求/竞品、创作内容、审计质量/技术/可见性/权威、追踪排名/报告/记忆 | `--mode research\|create\|audit\|track` + 各模式子参数（`--competitors` `--map` · `--brief` `--series` `--refresh` `--publish` `--meta` `--schema` `--type` · `--full` `--tech` `--visibility` `--authority` · `--alert` `--report` `--remember` `--period`） |
| `/aaron-marketing:influencer` | 红人：受众洞察、发现与适配、规划、外联、放大、ROI | `--phase discover\|plan\|activate\|measure` |
| `/aaron-marketing:ad` | 付费广告（ROAS 循环）：分群、结构、创意、实验设计、审计门、衡量 | `--phase research\|orchestrate\|activate\|scale` |
| `/aaron-marketing:email` | 邮件营销（SEND 循环）：送达/同意、分群、创意、生命周期流程、变现、发送测试、审计门 | `--phase setup\|engage\|nurture\|deliver` |
| `/aaron-marketing:launch` | 产品发布（RAMP 循环）：定位与分级、择时、消息屋与资产组装、就绪审计门、发布日执行、复盘与势能 | `--phase research\|assemble\|mobilize\|prove` |
| `/aaron-marketing:social` | 自然社媒（ECHO 循环）：频道组合与语气、内容日历与创作、运营与质量门、脉搏与度量 | `--phase explore\|craft\|host\|observe` |

日常工作通常从 `/aaron-marketing:auto` 开始；其余七个是显式的学科入口，用 `--mode` / `--phase` 收窄阶段。

**改名说明：** 命令使用 `/aaron-marketing:` 前缀。原 `research` / `create` / `audit` / `track` 四个命令现为 `/aaron-marketing:seo-geo` 的 `--mode`（子参数不变）。旧 `/seo:*` 与 `/aaron-seo-geo:*` 可经 `auto` 恢复——例如 `/aaron-marketing:auto /aaron-seo-geo:audit https://example.com/blog/post` 返回 `/aaron-marketing:seo-geo https://example.com/blog/post --mode audit`。

---

## 连接器与层级

技能用 `~~category` 占位符（`~~SEO tool`、`~~web analytics`、`~~ad platform` 等）而非具体厂商命名，且每个类别都有 **keyless 的 Tier-1 路径**。完整配方（含每个类别的免费/第一方端点）见 [CONNECTORS.md](../CONNECTORS.md)。

### 连接器层本身就是一件产品

**100+ 条记录在案的集成路径**，分三个精心设计的层——每一条都名副其实：

| 层 | 你得到什么 |
|----|------------|
| **21 个内置零依赖连接器** | 纯 Python 标准库——无 `pip`、无构建。keyless 实时 SERP + JS 渲染抓取（Firecrawl、Tavily）、AI 答案引用探针、DNS-over-HTTPS 邮件认证拉取、维基百科关注度序列、GDELT 新闻提及、真实 YouTube 创作者指标、IndexNow + 百度收录推送、Resend ESP 自动化，以及能把任何数据源变成前后对比时间序列的 git 可差分测量台账。 |
| **60+ 个记录在案的官方/免费 API** | 每一行都链接厂商**官方文档**、带核验日期，且每条链接入库前都经过 HTTP 实测。包含多数工具清单遗漏的路径：GSC URL Inspection、CrUX History（40 周真实用户 CWV）、Gmail Postmaster Tools API、Meta 广告库、微软 Clarity 数据导出 API。 |
| **厂商 MCP 服务器** | 18 个远程端点入目录（绝不自动注册——你的 `/mcp` 列表保持干净），外加 Google Analytics、Search Console、**Google Ads**、**微软 Clarity** 的官方自托管服务器。其中两个远程 MCP 完全免鉴权（Firecrawl、Tavily）。 |

让它们可信而不只是数量多的四个理由：

- **三类安全等级、工程化门控**（[SECURITY.md](../SECURITY.md)）：托管抓取器在每次委托抓取前**本地预检 robots.txt**、遇 Disallow 拒绝执行；一切改变外部状态的操作（发邮件、推送收录）**默认 dry-run**，必须显式 `--live` 才执行，厂商支持幂等键就用、不支持就绝不自动重试。
- **核验，然后再核验**：端点对照厂商一手文档带日期核实、keyless 路径经过真实调用测试、CI 守卫强制版本/跟踪同步、发版前的 live 冒烟专抓端点漂移（它已经两次抓到真实的 API 变更）。
- **只报事实、不下判定**：连接器输出记录存在性、解析标签和原始序列；裁决交给 auditor 门，技能给每个数字标注 **Measured / User-provided / Estimated**。
- **成文的 playbook**（[docs/connector-playbook.md](connector-playbook.md)）管辖每一次新增——定性、验证、实现、测试、接线、文档、跟踪、回归、归档——目录再增长，质量不滑坡。

| 层级 | 需要 | 你获得 |
|------|------|--------|
| **Tier 1**（默认） | 无 | 粘贴数据，或从免费/公开来源拉取。分析框架照常运行。 |
| **Tier 2** | 一个免费第一方 API 或 MCP | 自动取你自己的 GSC / GA4 / Core Web Vitals 数据。 |
| **Tier 3** | 更完整的 MCP 集 | 全自动多源工作流。 |

- **内置零依赖助手** 位于 `scripts/connectors/`（仅 Python 标准库），在本地拉取公开/自有数据——如 PageSpeed/CrUX、Open PageRank、页面抓取、Wayback CDX、Wikidata SPARQL、Common Crawl、advertools 配方——外加 **`resend.py`**：邮件技能直连 Resend ESP 的自动化（免费档 key：发件域认证状态、种子测试投递、抑制名单同步、广播定时发送；变更类子命令默认 dry-run，需 `--live` 才执行）；以及 **`firecrawl.py`** + **`tavily.py`**：研究类技能直连托管抓取器的 keyless 自动化（Firecrawl：实时搜索结果 + JS 渲染页 markdown + 站点 URL 清单；Tavily：带评分的搜索 + AI 答案引擎引用来源探针（GEO 用）+ URL 提取——两者完全无需 key，均内置本地 robots.txt 预检）。
- **免费/keyless 来源** 按类别记录：Google Search Console 与 GA4（自有数据）、PageSpeed/CrUX、Wikidata、Common Crawl、Open PageRank、Firecrawl keyless SERP/抓取、Tavily keyless AI 搜索、DNS-over-HTTPS 邮件认证记录（`doh.py`）、维基百科关注度序列（`pageviews.py`）、GDELT 新闻提及（`gdelt.py`）、免费 key 的 YouTube 创作者指标（`youtube.py`）、IndexNow + 百度收录推送（`indexpush.py`，dry-run 门控）、广告透明库（Meta/Google/TikTok），以及 crt.sh、W3C 校验器、oEmbed、HN Algolia 的配方行。
- **可选 MCP 服务器**（Ahrefs、Semrush、SE Ranking、SISTRIX、SimilarWeb、自托管免费的 **OpenSEO** 套件、Cloudflare、Vercel、HubSpot、Amplitude、Notion、Webflow、Sanity、Contentful、Slack、Resend、keyless 的 Firecrawl 与 Tavily）在 [`docs/mcp-catalog.json`](mcp-catalog.json) 中作为**仅复制粘贴参考**——目录位于会被自动注册的插件根 `.mcp.json` 路径之外，不会为你注册任何东西。把你想要的条目复制进自己的 MCP 配置即可。

付费广告技能基于你的**自有账户手动导出**（原生广告管理后台 CSV、GA4、电商）评分。带密钥的广告 API（Google Ads SDK、Meta Marketing API）仅是 opt-in Tier-2/3，**绝不**作为 Tier-1 要求。邮件技能同理——基于你**自己的 ESP 导出**评分，所有送达率信号均 keyless（DNS 查询、DMARC RUA 报告、种子收件测试），带密钥的 ESP API 也绝不是 Tier-1 要求；若你的 ESP 是 Resend，内置的 `resend.py` 可在免费档上自动化同一闭环。

---

## 推荐工作流

**SEO/GEO**
1. **研究** — `keyword-research` → `competitor-analysis` → `content-gap-analysis`
2. **构建** — `content-writer` → `geo-content-optimizer` → `serp-markup-builder` / `page-play-builder`
3. **优化** — `content-quality-auditor`（⛩ 发布门） → `on-page-seo-auditor` → `technical-seo-checker` → `site-structure-optimizer`
4. **监控** — `rank-tracker` → `performance-monitor` → `offsite-signal-analyzer`；信任评审用 `domain-authority-auditor`（⛩）

**红人**
1. **发现** — `audience-mapper` → `trend-spotter` → `influencer-discovery` → `fit-scorer`（C³ ACE）
2. **规划** — `competitor-tracker` → `campaign-planner` → `brief-generator` → `budget-optimizer`
3. **启动** — `outreach-manager` → `content-reviewer`（⛩ ART 门） → `contract-helper` → `content-amplifier`
4. **度量** — `landing-optimizer` → `performance-analyzer` → `roi-calculator` → `report-generator`

**付费广告（ROAS 循环）**
1. **研究** — `audience-segment-builder` → `campaign-architect`
2. **编排** — `ad-creative-builder` → `ad-test-designer`（落地页配 `landing-optimizer`）
3. **激活** — `conversion-signal-qa` → `ad-account-auditor`（⛩ RQS 门），在任何预算上线前
4. **放大** — `paid-measurement-loop` → `attribution-reconciler` → `roi-calculator` → `report-generator`

**邮件营销（SEND 循环）**
1. **搭建** — `deliverability-qa` → `list-segment-builder`
2. **触达** — `email-creative-builder`（落地页配 `landing-optimizer`）
3. **培育** — `email-sequence-designer` → `newsletter-monetization-planner`
4. **投递** — `send-experiment-designer` → `email-quality-auditor`（⛩ EQS 门），在任何发送前

要做完整信任评审，把 `content-quality-auditor` 与 `domain-authority-auditor` 搭配，得到合计 120 项的评估。开启 `memory-management` 后，交棒与未决事项自动留存在 HOT/WARM/COLD 记忆中。

---

## 仓库结构

```
narrative/{trace,architect,land,evaluate}/          # 品牌叙事 — TALE(16，含其门)
seo-geo/{research,build,optimize,monitor}/                  # SEO/GEO(16，含其 2 个门)
influencer/{discover,plan,activate,measure}/                   # 红人(16，含其门)
ad/research|orchestrate|activate|scale/            # 付费广告 — ROAS(16，含其门)
email/setup|engage|nurture|deliver/                  # 邮件营销 — SEND(16，含其门)
launch/research|assemble|mobilize|prove/             # 产品发布 — RAMP(16，含其门)
social/explore|craft|host|observe/                   # 自然社媒 — ECHO(16，含其门)
protocol/                                            # 协议层(8) — 真相注册表 + 记忆
commands/        # 8 个斜杠命令(auto、narrative、seo-geo、influencer、ad、email、launch、social)
references/      # 共享契约、状态模型、八套基准、auditor runbook、平台资料包
evals/           # 各技能结构化 eval 用例 + structure-manifest.json
hooks/           # hooks.json + claude-hook.sh(唯一运行逻辑)
scripts/         # validate-skill.sh + connectors/(标准库) + CI 守卫
memory/          # HOT/WARM/COLD 脚手架 + 注册表存储(entities/creators/claims/consent/channels/narrative-registry)
docs/            # 本地化 README(zh)
.claude-plugin/  # plugin.json + marketplace.json 镜像
```

---

## 设计哲学

- **技能即内容。** 唯一的代码是 Bash 校验器、Bash hook runner、零依赖的 Python 标准库连接器/检查助手。永不引入第三方 / `pip` 依赖——由依赖蔓延守卫强制。
- **keyless 优先。** 每个 `~~category` 都有免费/自有数据配方；MCP 与付费工具纯属便利。
- **外科手术式 & MECE。** 每个技能只担一项职责，边界清晰；重叠的工作做成现有技能的*模式*，而非新堆一个薄技能。注册表存证、门评判、分析器喂门。
- **不编数字。** 技能为每个数据标注 Measured / User-provided / Estimated，并内置 AI 腔 / 禁用词检测。
- **合规是指引，不是法律。** FTC 披露与声明真实性检查标注风险，但不构成法律意见。

---

## 质量守卫

每次变更都跑一组 fail-closed 守卫（均在 `scripts/` 与 `tests/`）：

| 守卫 | 检查 |
|------|------|
| `validate-skill.sh` | 全部 120 个技能的 frontmatter、必备章节、版本一致性、插件相对链接。 |
| `golden-auditor-math.py` | **八套**框架的权重和 + 工作示例算术的确定性校验。 |
| `check-evals.py` | eval 结构 lint + `structure-manifest.json`（120/120 技能均带 eval 用例）。 |
| `check-pii.py` | 拦截提交的密钥 / PII（token 级允许名单，fail-closed）。 |
| `check-stdlib-only.sh` | 依赖蔓延守卫 + 付费广告带密钥 API 红线。 |
| `check-versions.sh` | 版本同步守卫：束版本在 plugin.json / 两个 marketplace 镜像 / 双语 README 徽章 / CLAUDE.md / VERSIONS.md 发布行 + changelog 条目间完全一致，且每个 SKILL.md 版本与其 VERSIONS.md 行匹配。 |
| `tests/test_connectors_local.py` | 全部连接器纯请求构建函数的离线单测（CI 不联网）。 |
| `tests/test_hook_artifact_gate.sh` | hook 的 Artifact Gate + SessionStart 净化的行为测试。 |

线上端点漂移由**手动**的 [`scripts/connectors/smoke-live.sh`](../scripts/connectors/smoke-live.sh) 单独覆盖——每个托管连接器一次最小真实调用 + 响应形状断言（限速应答记 SKIP）；发版前手动跑，绝不进 CI。

---

## 贡献与文档

- **[CONTRIBUTING.md](../CONTRIBUTING.md)** —— 撰写规则、贡献清单、权威的 8 文件追踪列表。
- **[VERSIONS.md](../VERSIONS.md)** —— 各技能版本 + 变更日志（当前包：`16.0.0`）。
- **[SECURITY.md](../SECURITY.md)** · **[PRIVACY.md](../PRIVACY.md)** · **[CODE_OF_CONDUCT.md](../CODE_OF_CONDUCT.md)** —— 安全、隐私、社区政策。
- **[CLAUDE.md](../CLAUDE.md)** / **[AGENTS.md](../AGENTS.md)** —— 面向 Agent 的本仓库上下文。

---

## 免责声明

这些技能用于辅助品牌叙事、SEO/GEO、红人营销、付费广告、邮件营销、产品发布与自然社媒工作流，但**不**保证排名、AI 引用、流量、互动、转化、ROAS 或任何业务结果。红人与广告合规检查（FTC 披露、声明真实性、平台政策）为指引，非法律意见。在用于重大策略、财务或法律决策之前，请与具备资质的专业人士核实建议。

## 许可证

Apache License 2.0 —— 见 [LICENSE](../LICENSE)。

*最后同步英文 README：v16.0.0*

## Star History

<a href="https://www.star-history.com/?repos=aaron-he-zhu%2Faaron-marketing-skills&type=date&legend=top-left">
 <picture>
   <source media="(prefers-color-scheme: dark)" srcset="https://api.star-history.com/chart?repos=aaron-he-zhu/aaron-marketing-skills&type=date&theme=dark&legend=top-left" />
   <source media="(prefers-color-scheme: light)" srcset="https://api.star-history.com/chart?repos=aaron-he-zhu/aaron-marketing-skills&type=date&legend=top-left" />
   <img alt="Star History Chart" src="https://api.star-history.com/chart?repos=aaron-he-zhu/aaron-marketing-skills&type=date&legend=top-left" />
 </picture>
</a>
