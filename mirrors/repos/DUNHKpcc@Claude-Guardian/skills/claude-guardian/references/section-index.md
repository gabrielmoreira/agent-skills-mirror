# 章节索引

`references/` 里每个文件的每个二、三级小节都列在这里，附锚点链接。找某个主题时，先按 [SKILL.md 的资料表](../SKILL.md) 定位文件，再在这里找具体小节，不必通读整份文件。本页由 `tools/gen_section_index.py` 生成，请不要手改；改了某份 reference 的标题后重新生成。

## account-onboarding.md

A0: 新账号注册与使用节奏（3 节）

- [新账号注册初期：优先原版 Claude Code CLI](account-onboarding.md#新账号注册初期优先原版-claude-code-cli)
- [A0a：新手试错推荐组合](account-onboarding.md#a0a新手试错推荐组合)
- [A0b：短期封号时间线（出问题时先对照排查方向）](account-onboarding.md#a0b短期封号时间线出问题时先对照排查方向)

## accounts-and-payments.md

M02/M03: accounts, subscription, and payment planning（16 节）

- [已到期用户的相关旧账单](accounts-and-payments.md#已到期用户的相关旧账单)
- [操作总则与证据状态](accounts-and-payments.md#操作总则与证据状态)
- [M02 准入、账号与安全操作卡](accounts-and-payments.md#m02-准入账号与安全操作卡)
  - [A1 接触前分流（PC0）](accounts-and-payments.md#a1-接触前分流pc0)
  - [A2 官方准入核验与登录交接（PC1 → PC2）](accounts-and-payments.md#a2-官方准入核验与登录交接pc1--pc2)
  - [A3 真实身份核验、异常会话与凭据保护](accounts-and-payments.md#a3-真实身份核验异常会话与凭据保护)
- [M03 从条件比较到付款的工作流](accounts-and-payments.md#m03-从条件比较到付款的工作流)
  - [B1 先选需要的权益，再比较渠道（G2）](accounts-and-payments.md#b1-先选需要的权益再比较渠道g2)
  - [B2a 网页注册美区 Apple ID](accounts-and-payments.md#b2a-网页注册美区-apple-id)
  - [B2 Apple 分步卡（Q-A01–Q-A10）](accounts-and-payments.md#b2-apple-分步卡q-a01q-a10)
  - [B3 Google Play 分步卡（Q-G01–Q-G05）](accounts-and-payments.md#b3-google-play-分步卡q-g01q-g05)
  - [B4 网页卡 / API / 组织分步卡](accounts-and-payments.md#b4-网页卡--api--组织分步卡)
  - [B5 付款前统一交接（G3 与 PC2 不互相替代）](accounts-and-payments.md#b5-付款前统一交接g3-与-pc2-不互相替代)
  - [B6 购买后、续费、升级和取消](accounts-and-payments.md#b6-购买后续费升级和取消)
  - [B7 支付故障处理表](accounts-and-payments.md#b7-支付故障处理表)
- [当前核验入口与来源边界](accounts-and-payments.md#当前核验入口与来源边界)

## advanced-route.md

进阶路线：远端 Linux 机器的出口钉死与反向隧道管理（9 节）

- [1. 最终架构](advanced-route.md#1-最终架构)
- [2. 搭建顺序](advanced-route.md#2-搭建顺序)
  - [把脚本送到目标机：VPS 临时下载站](advanced-route.md#把脚本送到目标机vps-临时下载站)
- [3. 隧道专属的坑](advanced-route.md#3-隧道专属的坑)
- [4. 崩溃自愈](advanced-route.md#4-崩溃自愈)
- [5. 验收与覆盖矩阵](advanced-route.md#5-验收与覆盖矩阵)
- [6. 日常运维](advanced-route.md#6-日常运维)
- [7. 通用教训](advanced-route.md#7-通用教训)
- [边界](advanced-route.md#边界)

## agent-on-target.md

Agent 和被改的网络在同一台机器上（4 节）

- [1. 开工前先查清 Agent 自己的连接走哪条路](agent-on-target.md#1-开工前先查清-agent-自己的连接走哪条路)
- [2. 哪些步骤会切断 Agent 自己](agent-on-target.md#2-哪些步骤会切断-agent-自己)
- [3. 做法](agent-on-target.md#3-做法)
- [4. 授权档位](agent-on-target.md#4-授权档位)

## agent-remediation.md

Agent 编排检测与修复（10 节）

- [一次任务的闭环](agent-remediation.md#一次任务的闭环)
- [选定路线后的能力核实](agent-remediation.md#选定路线后的能力核实)
- [手动交接与遗留验收](agent-remediation.md#手动交接与遗留验收)
- [修复后的复验](agent-remediation.md#修复后的复验)
- [整机只走 IPv4（2026-10-19，2026-10-25 补充）](agent-remediation.md#整机只走-ipv42026-10-192026-10-25-补充)
- [Windows 网卡 IPv6：默认关闭（B 档）](agent-remediation.md#windows-网卡-ipv6默认关闭b-档)
- [WebRTC：浏览器和系统分开堵（B 档）](agent-remediation.md#webrtc浏览器和系统分开堵b-档)
- [选择器能做什么](agent-remediation.md#选择器能做什么)
- [内置脚本修不了：Agent 继续负责](agent-remediation.md#内置脚本修不了agent-继续负责)
- [Mac 修复链：Clash Verge Rev 2.5.8 的 rules 扩展](agent-remediation.md#mac-修复链clash-verge-rev-258-的-rules-扩展)

## agent-rules-task.md

Agent 配合应用编辑：单条 rules 扩展任务（4 节）

- [已实现的辅助接口](agent-rules-task.md#已实现的辅助接口)
- [Agent 的实际操作](agent-rules-task.md#agent-的实际操作)
- [内容核验不能替代实际效果](agent-rules-task.md#内容核验不能替代实际效果)
- [内置事务与权限边界](agent-rules-task.md#内置事务与权限边界)

## authorization-tiers.md

分级授权：什么时候需要用户在场（9 节）

- [先做一次范围确认](authorization-tiers.md#先做一次范围确认)
- [三档](authorization-tiers.md#三档)
- [C 档清单](authorization-tiers.md#c-档清单)
- [B 档：计划批准单](authorization-tiers.md#b-档计划批准单)
- [C 档：确认单](authorization-tiers.md#c-档确认单)
- [不变的硬规则](authorization-tiers.md#不变的硬规则)
- [报告](authorization-tiers.md#报告)
- [各路线里的动作分档](authorization-tiers.md#各路线里的动作分档)
- [状态机里的可追溯记录（ADR-026）](authorization-tiers.md#状态机里的可追溯记录adr-026)

## ban-appeal.md

封号申诉（3 节）

- [回复时间](ban-appeal.md#回复时间)
- [解封以后](ban-appeal.md#解封以后)
- [申诉模板](ban-appeal.md#申诉模板)

## cleanup-cli-usage.md

C5 cleanup CLI usage and host boundary（5 节）

- [Commands](cleanup-cli-usage.md#commands)
- [Trusted Agent bridge](cleanup-cli-usage.md#trusted-agent-bridge)
- [Operator document and recovery](cleanup-cli-usage.md#operator-document-and-recovery)
- [Installed-package evidence](cleanup-cli-usage.md#installed-package-evidence)
- [macOS built-in host (`native_cleanup_mac.py`)](cleanup-cli-usage.md#macos-built-in-host-native_cleanup_macpy)

## contact-and-safety.md

Contact phases and execution boundary（4 节）

- [Built-in capability and independent Agent action boundary](contact-and-safety.md#built-in-capability-and-independent-agent-action-boundary)
- [Phase contract](contact-and-safety.md#phase-contract)
- [Permissions and reporting](contact-and-safety.md#permissions-and-reporting)
- [Persistence and interruption](contact-and-safety.md#persistence-and-interruption)

## egress-ip-options.md

本机路线：固定出口 IP 的三种来源（2026-10-21）（7 节）

- [三种来源](egress-ip-options.md#三种来源)
- [推荐](egress-ip-options.md#推荐)
- [教程范围](egress-ip-options.md#教程范围)
- [自建梯提示词（简版）](egress-ip-options.md#自建梯提示词简版)
- [自建梯怎么选 VPS](egress-ip-options.md#自建梯怎么选-vps)
- [线路优化](egress-ip-options.md#线路优化)
- [选好之后](egress-ip-options.md#选好之后)

## evidence-policy.md

M14：证据、来源与发布规则（5 节）

- [判断边界](evidence-policy.md#判断边界)
- [稳定编号与历史争议](evidence-policy.md#稳定编号与历史争议)
- [两份教程与来源去重（T09）](evidence-policy.md#两份教程与来源去重t09)
- [发布与更新](evidence-policy.md#发布与更新)
- [官方与技术入口（历史索引）](evidence-policy.md#官方与技术入口历史索引)

## exit-consistency.md

出口与本机环境一致：TCP 延迟、TCP 指纹、UA（4 节）

- [1. TCP 延迟](exit-consistency.md#1-tcp-延迟)
- [2. TCP 指纹](exit-consistency.md#2-tcp-指纹)
- [3. UA 与环境一致性](exit-consistency.md#3-ua-与环境一致性)
- [4. Agent 什么时候用本文](exit-consistency.md#4-agent-什么时候用本文)

## host-libraries.md

内置脚本与宿主库的契约说明（12 节）

- [Agent内部修复入口（按动作能力分流）](host-libraries.md#agent内部修复入口按动作能力分流)
- [限定静态盘点入口](host-libraries.md#限定静态盘点入口)
- [本地环境状态面板](host-libraries.md#本地环境状态面板)
  - [私有配置候选（不可应用）](host-libraries.md#私有配置候选不可应用)
- [环境入口校验](host-libraries.md#环境入口校验)
- [旧目标范围契约与整机结论](host-libraries.md#旧目标范围契约与整机结论)
- [环境入口：完整声明与实际调用](host-libraries.md#环境入口完整声明与实际调用)
  - [文件与宿主入口](host-libraries.md#文件与宿主入口)
  - [静态 inventory 的 /2 信封](host-libraries.md#静态-inventory-的-2-信封)
  - [路线与失败边界](host-libraries.md#路线与失败边界)
- [已替换但回执未完成：精确文件恢复](host-libraries.md#已替换但回执未完成精确文件恢复)
- [C5：限定清理宿主交接](host-libraries.md#c5限定清理宿主交接)

## illegal-tools-cleanup.md

非法工具清理：破限、反代分发等 MCP、插件、hooks（Agent 提示词）（6 节）

- [1. 算非法工具的](illegal-tools-cleanup.md#1-算非法工具的)
- [2. 去哪查](illegal-tools-cleanup.md#2-去哪查)
- [3. 只读审计（A 档）](illegal-tools-cleanup.md#3-只读审计a-档)
- [4. 清理（C 档，逐项确认）](illegal-tools-cleanup.md#4-清理c-档逐项确认)
- [5. 复验](illegal-tools-cleanup.md#5-复验)
- [6. 不做的事](illegal-tools-cleanup.md#6-不做的事)

## incidents-and-integrations.md

M07/M10–M13: clients, incidents, integrations, and preservation（18 节）

- [Cleanup, migration, and recovery (M13 / ENV-09)](incidents-and-integrations.md#cleanup-migration-and-recovery-m13--env-09)
- [人工执行卡的共同边界](incidents-and-integrations.md#人工执行卡的共同边界)
- [M10 进程—凭据—网络映射](incidents-and-integrations.md#m10-进程凭据网络映射)
  - [I1 接触前静态盘点](incidents-and-integrations.md#i1-接触前静态盘点)
  - [I2 本地 MCP、远端 MCP、hooks 与插件](incidents-and-integrations.md#i2-本地-mcp远端-mcphooks-与插件)
  - [I3 实际启动、继承与后台进程（PC1/PC2）](incidents-and-integrations.md#i3-实际启动继承与后台进程pc1pc2)
- [M11 SDK、网关与高级集成核对表](incidents-and-integrations.md#m11-sdk网关与高级集成核对表)
  - [J1 先画调用链，不按软件名定性](incidents-and-integrations.md#j1-先画调用链不按软件名定性)
  - [J2 最小试验、预算、重试与日志](incidents-and-integrations.md#j2-最小试验预算重试与日志)
  - [J3 分层排障与变更验收](incidents-and-integrations.md#j3-分层排障与变更验收)
- [M12 异常处理：从症状到事实报告](incidents-and-integrations.md#m12-异常处理从症状到事实报告)
  - [K1 首次事故接入与优先级](incidents-and-integrations.md#k1-首次事故接入与优先级)
  - [K2 故障分流表](incidents-and-integrations.md#k2-故障分流表)
  - [K3 证据包与事实时间线](incidents-and-integrations.md#k3-证据包与事实时间线)
  - [K4 官方申诉、导出与退款交接](incidents-and-integrations.md#k4-官方申诉导出与退款交接)
  - [K5 关闭事故与恢复使用](incidents-and-integrations.md#k5-关闭事故与恢复使用)
- [来源、官方入口与更新规则](incidents-and-integrations.md#来源官方入口与更新规则)
- [Explicit C5 Agent execution sequence](incidents-and-integrations.md#explicit-c5-agent-execution-sequence)

## intake.md

M00: adaptive intake and stable question registry（18 节）

- [Scheduling](intake.md#scheduling)
  - [已到期用户的相关旧账单（T76）](intake.md#已到期用户的相关旧账单t76)
  - [已有订阅的明确升级与实际订阅冲突（T77/T80）](intake.md#已有订阅的明确升级与实际订阅冲突t77t80)
  - [仅在实际问题需要时确认当前套餐（T84）](intake.md#仅在实际问题需要时确认当前套餐t84)
- [Fact states and gates](intake.md#fact-states-and-gates)
- [Interruption and resume](intake.md#interruption-and-resume)
- [Stable question IDs](intake.md#stable-question-ids)
  - [Core and OS](intake.md#core-and-os)
  - [History and network](intake.md#history-and-network)
  - [Payment branches](intake.md#payment-branches)
  - [Environment and delivery](intake.md#environment-and-delivery)
- [Route, egress source and mobile (ADR-018)](intake.md#route-egress-source-and-mobile-adr-018)
- [Selected-device history and explicit cleanup task](intake.md#selected-device-history-and-explicit-cleanup-task)
  - [Device-only triage resolution](intake.md#device-only-triage-resolution)
- [Conversation topics without the questionnaire (#21)](intake.md#conversation-topics-without-the-questionnaire-21)
- [Workflow record formats and dependency preparation](intake.md#workflow-record-formats-and-dependency-preparation)
  - [Target capability observations](intake.md#target-capability-observations)
  - [Handoff and acceptance records](intake.md#handoff-and-acceptance-records)

## killswitch-switch.md

Guardian Switch：统一防直连开关（6 节）

- [支持范围与操作含义](killswitch-switch.md#支持范围与操作含义)
- [首次配置：交给目标机 Agent](killswitch-switch.md#首次配置交给目标机-agent)
- [Windows 整机出口模式：代价与首次交付](killswitch-switch.md#windows-整机出口模式代价与首次交付)
- [命令行与桌面入口](killswitch-switch.md#命令行与桌面入口)
- [恢复与开关验收](killswitch-switch.md#恢复与开关验收)
- [界面与随包文件](killswitch-switch.md#界面与随包文件)

## line-optimization.md

线路优化：Agent 如何帮用户的机器优化线路（10 节）

- [Agent 的工作方式](line-optimization.md#agent-的工作方式)
- [第一步：按现象定位要优化什么（R02 一、八）](line-optimization.md#第一步按现象定位要优化什么r02-一八)
- [第二步：决定搭配方案（R02 三、综合评价）](line-optimization.md#第二步决定搭配方案r02-三综合评价)
- [第三步：逐项应用（每项一张变更卡）](line-optimization.md#第三步逐项应用每项一张变更卡)
  - [3.1 用 SSH 连接家宽出口（方案 A，推荐入门）](line-optimization.md#31-用-ssh-连接家宽出口方案-a推荐入门)
  - [3.2 Xvfb / noVNC：让桌面连接更轻](line-optimization.md#32-xvfb--novnc让桌面连接更轻)
  - [3.3 需要端口中转时：Realm 最小示例（方案 B，或改善 SSH 到 B）](line-optimization.md#33-需要端口中转时realm-最小示例方案-b或改善-ssh-到-b)
  - [3.4 BBR：可选调整，先保留原值（R02 七）](line-optimization.md#34-bbr可选调整先保留原值r02-七)
- [第四步：验证与记录](line-optimization.md#第四步验证与记录)
- [Agent 不做的事](line-optimization.md#agent-不做的事)

## linux-cleanup.md

Linux：Claude 本机数据清理（Agent 提示词，无内置宿主）（8 节）

- [1. 路径](linux-cleanup.md#1-路径)
- [2. 分档](linux-cleanup.md#2-分档)
- [3. 只读审计（A 档）](linux-cleanup.md#3-只读审计a-档)
- [4. 备份（B 档，整个计划批准一次）](linux-cleanup.md#4-备份b-档整个计划批准一次)
- [5. 隔离（C 档，当场确认）](linux-cleanup.md#5-隔离c-档当场确认)
- [6. 退出登录与凭据（C 档，单独确认）](linux-cleanup.md#6-退出登录与凭据c-档单独确认)
- [7. 官方的项目级清理](linux-cleanup.md#7-官方的项目级清理)
- [8. 不做的事](linux-cleanup.md#8-不做的事)

## local-advanced-route.md

本机路线高级扩展：异机远程协助（9 节）

- [1. 先确定是否需要远程](local-advanced-route.md#1-先确定是否需要远程)
- [2. 远程接入与传文件](local-advanced-route.md#2-远程接入与传文件)
  - [Windows：沿用 S10 的接入经验](local-advanced-route.md#windows沿用-s10-的接入经验)
  - [异机检测：在目标机运行随包工具](local-advanced-route.md#异机检测在目标机运行随包工具)
  - [Mac：远程登录与桌面会话](local-advanced-route.md#mac远程登录与桌面会话)
- [3. 远程故障演练](local-advanced-route.md#3-远程故障演练)
  - [Windows：独立计划任务](local-advanced-route.md#windows独立计划任务)
  - [Mac：PF 与独立恢复](local-advanced-route.md#macpf-与独立恢复)
- [4. 交付与回滚](local-advanced-route.md#4-交付与回滚)

## local-firewall-prompts.md

本机路线：Clash 与防火墙（Agent 提示词）（19 节）

- [通用工作方式（两个系统相同）](local-firewall-prompts.md#通用工作方式两个系统相同)
- [替别人交付：先说范围，按验收单交](local-firewall-prompts.md#替别人交付先说范围按验收单交)
- [突发场景：分平台处理与 Agent 验收提示词（2026-11-09）](local-firewall-prompts.md#突发场景分平台处理与-agent-验收提示词2026-11-09)
  - [平台机制与检查重点](local-firewall-prompts.md#平台机制与检查重点)
  - [场景与通过条件](local-firewall-prompts.md#场景与通过条件)
  - [可直接交给目标机 Agent 的提示词](local-firewall-prompts.md#可直接交给目标机-agent-的提示词)
- [Mac](local-firewall-prompts.md#mac)
  - [Mac 上的 Clash（Clash Verge）怎么配](local-firewall-prompts.md#mac-上的-clashclash-verge怎么配)
  - [Mac 的防火墙：PF 脚本（已验收）](local-firewall-prompts.md#mac-的防火墙pf-脚本已验收)
- [Windows](local-firewall-prompts.md#windows)
  - [Windows 上的 Clash](local-firewall-prompts.md#windows-上的-clash)
  - [Windows 的防火墙：系统自带](local-firewall-prompts.md#windows-的防火墙系统自带)
  - [切换后不通：分层诊断](local-firewall-prompts.md#切换后不通分层诊断)
  - [Windows 更新覆盖与规则替换](local-firewall-prompts.md#windows-更新覆盖与规则替换)
  - [Windows Error 5 分诊](local-firewall-prompts.md#windows-error-5-分诊)
  - [查 WFP 丢包记录](local-firewall-prompts.md#查-wfp-丢包记录)
  - [宿主拒绝执行时](local-firewall-prompts.md#宿主拒绝执行时)
  - [最小反馈清单](local-firewall-prompts.md#最小反馈清单)
- [Agent 不做的事](local-firewall-prompts.md#agent-不做的事)

## macos-dns-case-lessons.md

macOS DNS、IPv6 与 WebRTC：单机经验的通用提炼（8 节）

- [先分清观察、解释与未知](macos-dns-case-lessons.md#先分清观察解释与未知)
- [1. DNS 职责与路径分别记录](macos-dns-case-lessons.md#1-dns-职责与路径分别记录)
- [2. 端口 53 接管不是所有 DNS 的覆盖证明](macos-dns-case-lessons.md#2-端口-53-接管不是所有-dns-的覆盖证明)
- [3. IPv6 开关具有不同作用域](macos-dns-case-lessons.md#3-ipv6-开关具有不同作用域)
- [4. Tailscale、私有解析与应用退出依赖](macos-dns-case-lessons.md#4-tailscale私有解析与应用退出依赖)
- [5. 验收矩阵：样本不能互相代证](macos-dns-case-lessons.md#5-验收矩阵样本不能互相代证)
- [6. 最小变更、回滚与时效](macos-dns-case-lessons.md#6-最小变更回滚与时效)
- [来源与使用范围](macos-dns-case-lessons.md#来源与使用范围)

## mobile-guidance.md

手机端防封要点（iOS / Android）（4 节）

- [什么时候用](mobile-guidance.md#什么时候用)
- [检查表（S03 第 4 页）](mobile-guidance.md#检查表s03-第-4-页)
- [Android 要拔掉 SIM 卡](mobile-guidance.md#android-要拔掉-sim-卡)
- [与本项目其他规则的关系](mobile-guidance.md#与本项目其他规则的关系)

## network-and-remedies.md

M04/M05/M10: network evidence and offline remedies（6 节）

- [ENV modules and evidence boundaries](network-and-remedies.md#env-modules-and-evidence-boundaries)
- [Layered interpretation](network-and-remedies.md#layered-interpretation)
- [TLS 字段与服务方向：先解释，后限定规则候选](network-and-remedies.md#tls-字段与服务方向先解释后限定规则候选)
- [Finding → minimal plan](network-and-remedies.md#finding--minimal-plan)
- [Detection tools](network-and-remedies.md#detection-tools)
- [Report format](network-and-remedies.md#report-format)

## routes-and-platforms.md

M01/M06–M09: independent environment routes（31 节）

- [设备与运行位置](routes-and-platforms.md#设备与运行位置)
- [执行卡使用约定（M01/M08/M09）](routes-and-platforms.md#执行卡使用约定m01m08m09)
  - [M01：五分钟术语卡与选择题](routes-and-platforms.md#m01五分钟术语卡与选择题)
  - [共用接触交接单](routes-and-platforms.md#共用接触交接单)
- [R-LOCAL 独立操作卡](routes-and-platforms.md#r-local-独立操作卡)
  - [L1 准备与已有环境接入（本机，PC0）](routes-and-platforms.md#l1-准备与已有环境接入本机pc0)
  - [L2 网络、浏览器与可选防护（本机，PC0）](routes-and-platforms.md#l2-网络浏览器与可选防护本机pc0)
  - [关闭代理与防火墙前：先确认后台退出](routes-and-platforms.md#关闭代理与防火墙前先确认后台退出)
  - [L2a 固定出口 IP 的来源（本机，PC0 指引）](routes-and-platforms.md#l2a-固定出口-ip-的来源本机pc0-指引)
  - [L3 安装、使用与更新（本机，PC1/PC2）](routes-and-platforms.md#l3-安装使用与更新本机pc1pc2)
  - [L4 本机高级扩展：异机远程协助（按需）](routes-and-platforms.md#l4-本机高级扩展异机远程协助按需)
- [R-VM 独立操作卡（M08）](routes-and-platforms.md#r-vm-独立操作卡m08)
  - [V1 新建或接入（宿主与客机分别操作，PC0）](routes-and-platforms.md#v1-新建或接入宿主与客机分别操作pc0)
  - [V2 网络与快照（宿主配置和客机测试分开，PC0）](routes-and-platforms.md#v2-网络与快照宿主配置和客机测试分开pc0)
  - [V2a 系统、网卡、出口与防火墙（VM，PC0 指引）](routes-and-platforms.md#v2a-系统网卡出口与防火墙vmpc0-指引)
  - [V3 接触、日常与更新（客机为目标，PC1/PC2）](routes-and-platforms.md#v3-接触日常与更新客机为目标pc1pc2)
  - [V4 WSL 与容器子场景](routes-and-platforms.md#v4-wsl-与容器子场景)
- [R-VPS 独立操作卡（M09）](routes-and-platforms.md#r-vps-独立操作卡m09)
  - [P1 可行性、现有服务器与成本（本机规划，PC0）](routes-and-platforms.md#p1-可行性现有服务器与成本本机规划pc0)
  - [P1a 系统、环境一致、出口与防火墙（VPS，PC0 指引）](routes-and-platforms.md#p1a-系统环境一致出口与防火墙vpspc0-指引)
  - [P2 SSH、开发用户与救援（本机与服务器分别标注，PC0）](routes-and-platforms.md#p2-ssh开发用户与救援本机与服务器分别标注pc0)
  - [P3 开发与可选额外出口（服务器，PC0）](routes-and-platforms.md#p3-开发与可选额外出口服务器pc0)
  - [P4 客户端、OAuth 与临时浏览器（服务器为目标，PC1/PC2）](routes-and-platforms.md#p4-客户端oauth-与临时浏览器服务器为目标pc1pc2)
  - [P5 日常、更新、备份与退出（本机入口 / 服务器任务）](routes-and-platforms.md#p5-日常更新备份与退出本机入口--服务器任务)
- [R-ADV 进阶路线卡（远端 Linux 机器的出口钉死与反向隧道）](routes-and-platforms.md#r-adv-进阶路线卡远端-linux-机器的出口钉死与反向隧道)
  - [A1 适用判断与前置（管理端规划，PC0）](routes-and-platforms.md#a1-适用判断与前置管理端规划pc0)
  - [A2 反向隧道与崩溃自愈（目标机与 VPS 分别标注，B 档）](routes-and-platforms.md#a2-反向隧道与崩溃自愈目标机与-vps-分别标注b-档)
  - [A3 启用 killswitch 与验收（目标机，C 档）](routes-and-platforms.md#a3-启用-killswitch-与验收目标机c-档)
  - [A4 日常、更新与恢复（PC0 指引；接触 Claude 的 PC1/PC2 仍走 V3）](routes-and-platforms.md#a4-日常更新与恢复pc0-指引接触-claude-的-pc1pc2-仍走-v3)
- [R-ROUTER 软路由（占位，未来补齐）](routes-and-platforms.md#r-router-软路由占位未来补齐)
- [来源与维护定位](routes-and-platforms.md#来源与维护定位)

## scripts-index.md

脚本索引（8 节）

- [访谈与评估](scripts-index.md#访谈与评估)
- [检查与报告（只读）](scripts-index.md#检查与报告只读)
- [统一防直连开关](scripts-index.md#统一防直连开关)
- [网络检测的其他部分](scripts-index.md#网络检测的其他部分)
- [修复计划与规则（离线，不写入）](scripts-index.md#修复计划与规则离线不写入)
- [写入与恢复（有事务和备份）](scripts-index.md#写入与恢复有事务和备份)
- [清理（C 档）](scripts-index.md#清理c-档)
- [随包脚本资产（`assets/`）](scripts-index.md#随包脚本资产assets)

## skill-update.md

Skill 更新：每次使用前先查最新（3 节）

- [1. 什么时候查](skill-update.md#1-什么时候查)
- [2. 怎么告诉用户](skill-update.md#2-怎么告诉用户)
- [3. 怎么更新](skill-update.md#3-怎么更新)

## source-library.md

原始资料阅读库（17 节）

- [Agent 补充资料来源](source-library.md#agent-补充资料来源)
- [对话中的使用方式](source-library.md#对话中的使用方式)
- [清单型资料的执行反馈（#20）](source-library.md#清单型资料的执行反馈20)
- [来源与现行规则的对照](source-library.md#来源与现行规则的对照)
- [九份阅读来源](source-library.md#九份阅读来源)
  - [S01：VPS 和服务器术语](source-library.md#s01vps-和服务器术语)
  - [S02：支付方式与订阅准备](source-library.md#s02支付方式与订阅准备)
  - [S03：IP、设备、手机与账号阶段的经验材料](source-library.md#s03ip设备手机与账号阶段的经验材料)
  - [S04：路线比较与 FAQ](source-library.md#s04路线比较与-faq)
  - [S05：Windows 本地防护思路](source-library.md#s05windows-本地防护思路)
  - [S06：macOS 清理，同时保留 CLI](source-library.md#s06macos-清理同时保留-cli)
  - [S07：VPS IP 质量与网络测试清单（精简版）](source-library.md#s07vps-ip-质量与网络测试清单精简版)
  - [S08：VPS Claude 教程（极低的封号风险）](source-library.md#s08vps-claude-教程极低的封号风险)
  - [S10：Windows 本机路线、Killswitch 与自建 VPS 部署经验（完整脱敏版）](source-library.md#s10windows-本机路线killswitch-与自建-vps-部署经验完整脱敏版)
- [补充资料集合：R01 VPS 推荐报告集（业务／性价比／高端家宽）](source-library.md#补充资料集合r01-vps-推荐报告集业务性价比高端家宽)
- [补充资料集合：R02 VPS 线路优化与家宽中转教程](source-library.md#补充资料集合r02-vps-线路优化与家宽中转教程)
- [版本、来源与分发记录](source-library.md#版本来源与分发记录)

## trace-cleanup.md

环境痕迹清理：代理、VPN、终端历史里的旧 IP（Agent 提示词）（6 节）

- [1. 代理客户端日志（Clash Verge、Mihomo、FlClash）](trace-cleanup.md#1-代理客户端日志clash-vergemihomoflclash)
- [2. VPN 客户端日志](trace-cleanup.md#2-vpn-客户端日志)
- [3. Shell 历史：只删查 IP 的命令](trace-cleanup.md#3-shell-历史只删查-ip-的命令)
- [4. 命令的输出存在哪](trace-cleanup.md#4-命令的输出存在哪)
- [5. Claude 对话记录](trace-cleanup.md#5-claude-对话记录)
- [6. 不碰的东西](trace-cleanup.md#6-不碰的东西)

## vm-guidance.md

VM 路线：客机系统、网卡、出口与防火墙（8 节）

- [1. 客机系统怎么选](vm-guidance.md#1-客机系统怎么选)
- [2. 创建前先选网卡](vm-guidance.md#2-创建前先选网卡)
- [3. 出口 IP](vm-guidance.md#3-出口-ip)
- [3a. Linux 客机的搭建顺序（Omarchy）](vm-guidance.md#3a-linux-客机的搭建顺序omarchy)
  - [macOS 客机（Mac 宿主首选）](vm-guidance.md#macos-客机mac-宿主首选)
- [4. 客机防火墙（fail-closed）](vm-guidance.md#4-客机防火墙fail-closed)
- [5. 后续流程：与本机路线一致](vm-guidance.md#5-后续流程与本机路线一致)
- [边界](vm-guidance.md#边界)

## vps-guidance.md

VPS 路线：开发机（环境一致）（14 节）

- [核心：环境一致](vps-guidance.md#核心环境一致)
- [服务器怎么选](vps-guidance.md#服务器怎么选)
- [怎么读 IP 检测报告（S08 第 3 页）](vps-guidance.md#怎么读-ip-检测报告s08-第-3-页)
- [出口：两种情况](vps-guidance.md#出口两种情况)
- [线路优化](vps-guidance.md#线路优化)
- [创建与连接](vps-guidance.md#创建与连接)
- [服务器保活：按配置定内存预算，防 OOM 失联（Agent 操作前必做）](vps-guidance.md#服务器保活按配置定内存预算防-oom-失联agent-操作前必做)
- [开发环境与 Claude Code](vps-guidance.md#开发环境与-claude-code)
- [临时远程浏览器（远程桌面）](vps-guidance.md#临时远程浏览器远程桌面)
- [注册、养号、订阅、OAuth（与本机路线一致，但全在 VPS 浏览器里）](vps-guidance.md#注册养号订阅oauth与本机路线一致但全在-vps-浏览器里)
- [防火墙](vps-guidance.md#防火墙)
- [作为隧道中转的 VPS（进阶路线）](vps-guidance.md#作为隧道中转的-vps进阶路线)
- [日常](vps-guidance.md#日常)
- [边界](vps-guidance.md#边界)

## whole-machine-ipv4.md

整机统一出口：只走 IPv4，不走 IPv6（Clash Verge，Mac 与 Windows）（8 节）

- [1. 要达到什么](whole-machine-ipv4.md#1-要达到什么)
- [2. 配置（Clash Verge）](whole-machine-ipv4.md#2-配置clash-verge)
- [3. 怎么做（按档位）](whole-machine-ipv4.md#3-怎么做按档位)
- [4. 取证（Agent 实际执行，不替用户编造）](whole-machine-ipv4.md#4-取证agent-实际执行不替用户编造)
- [5. 判定](whole-machine-ipv4.md#5-判定)
- [5a. 浏览器环境验收：[ip.net.coffee/claude](https://ip.net.coffee/claude/)](whole-machine-ipv4.md#5a-浏览器环境验收ipnetcoffeeclaude)
- [6. 回滚](whole-machine-ipv4.md#6-回滚)
- [7. 限制](whole-machine-ipv4.md#7-限制)

## windows-cleanup.md

Windows：Claude 本机数据清理（Agent 提示词，无内置宿主）（12 节）

- [1. 官方文档给出的路径](windows-cleanup.md#1-官方文档给出的路径)
- [2. 分档（沿用 macOS 宿主的划分）](windows-cleanup.md#2-分档沿用-macos-宿主的划分)
- [3. 只读审计（A 档，范围确认后自行做）](windows-cleanup.md#3-只读审计a-档范围确认后自行做)
- [4. 备份（B 档，整个计划批准一次）](windows-cleanup.md#4-备份b-档整个计划批准一次)
- [5. 隔离（C 档，当场确认）](windows-cleanup.md#5-隔离c-档当场确认)
  - [被宿主策略或权限拦截时](windows-cleanup.md#被宿主策略或权限拦截时)
  - [交给用户自己操作时的交接单](windows-cleanup.md#交给用户自己操作时的交接单)
- [6. 退出登录与凭据（C 档，单独确认）](windows-cleanup.md#6-退出登录与凭据c-档单独确认)
- [7. 最小提示词模式（可选，C 档）](windows-cleanup.md#7-最小提示词模式可选c-档)
- [8. 官方的项目级清理](windows-cleanup.md#8-官方的项目级清理)
- [9. 不做的事](windows-cleanup.md#9-不做的事)
- [10. 限制](windows-cleanup.md#10-限制)

## windows-network-transaction.md

Windows 网络修改与恢复（4 节）

- [使用前](windows-network-transaction.md#使用前)
- [运行](windows-network-transaction.md#运行)
- [步骤脚本](windows-network-transaction.md#步骤脚本)
- [恢复与结果](windows-network-transaction.md#恢复与结果)
