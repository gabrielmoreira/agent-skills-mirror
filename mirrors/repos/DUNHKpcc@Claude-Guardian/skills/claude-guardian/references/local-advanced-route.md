# 本机路线高级扩展：异机远程协助

OpenSSH、Tailscale、内网穿透和远程管理是协助别人部署时的扩展，不是本 Skill 的核心流程，也不是本机路线的前置条件。**目标机已有 Agent 时，默认直接在目标机按[本机指引](local-firewall-prompts.md)操作，不需要建立远程接入。**

本文只在**用户明确选择远程协助**时使用；典型情况是目标机没有可用 Agent，Agent 在管理机，通过获准的通道协助另一台 Mac/Windows 目标机。仍属于 R-LOCAL，本机路线不新增路线值；目标机、日常使用者和管理机分别记录，不能用管理机的网络结果代替目标机验收。

共同原则是：先接入目标机、确认正常代理，再准备独立恢复，最后改防火墙并演练；命令、路径、权限和桌面会话按目标机实际系统选择。Windows 的完整经验保留在 [S10](../sources/S10-windows-deployment-sanitized.md)，Mac 按下面的系统原生步骤操作。VM／VPS 的远端 Linux 反向隧道、自愈和出口钉死继续见[原进阶路线](advanced-route.md)，不把其中的 Linux 脚本套到 Mac/Windows。

## 1. 先确定是否需要远程

1. 目标机已有 Agent：回到本机主流程；Agent 链路与待改网络在同机时按 [agent-on-target.md](agent-on-target.md)准备本地恢复。
2. 确需异机协助：先使用用户已有的远程通道；没有通道时才提出 OpenSSH、Tailscale 或内网穿透方案，说明要新增的组件、目标、访问范围、维护成本、备份和回滚。
3. 不为配置 Clash 默认安装远程软件、开 SSH 服务、加 VPS 中转或开放公网端口。组织设备、凭据和可能失联的动作按[分级授权](authorization-tiers.md)处理；本次开发或阅读资料不替代实际操作授权。

## 2. 远程接入与传文件

先使用已有通道；需要跨网络接入时，再按用户选定方案接入 Tailscale 或其他内网穿透。两端先确认设备归属、登录账户和实际可达性；接入管理网络不等于目标机已走预期代理出口。

### Windows：沿用 S10 的接入经验

- **OpenSSH / Tailscale：**S10 [第一节](../sources/S10-windows-deployment-sanitized.md#windows-ssh)记录了管理机 Tailscale 状态、同一 tailnet、Windows 管理员账户公钥位置与权限。先核对两端实际环境；管理员账户的路径取决于当前 `sshd_config`，不推广为所有 Windows 账户的固定路径。
- **内网穿透：**仅在现有通道无法到达目标且用户选定该方案时规划；先说明是否新增中转、监听端口或长期服务，再按范围批准。S10 的 Tailscale 案例不是默认必须做的步骤，也不自动授权其他穿透方式。
- **传脚本：**S10 [第五节](../sources/S10-windows-deployment-sanitized.md#powershell-tools)保留了先写脚本再 scp、PowerShell 5.1 编码及 SYSTEM 用户目录差异。纯本机执行只需采用编码和路径经验，不需要为了传文件启用 SSH。
- **管理通道例外：**只有实际使用该通道时才考虑对应放行规则，列清程序、方向和作用域；无远程管理需求不添加 Tailscale/SSH 例外，不把管理流量另行放行说成所有流量同一出口。

### 异机检测：在目标机运行随包工具

接入后先按 [能力核实](agent-remediation.md#capability-checkpoint)检查目标机的 Python 和脚本，管理机能跑不算目标机能跑。Windows 无 Python **必须先补齐**，再使用我们的 `network_check.py` 和 `egress_verifier.py`，不以手写检查替代。历史处理见 [S10 第十节](../sources/S10-windows-deployment-sanitized.md#network-evidence)；安装前按实际架构、官方来源和安装范围取得相应授权，不能直接照搬旧镜像或 SYSTEM 安装。

经批准把随包脚本传到目标机私有目录，在目标机运行 `network_check.py run --evidence-output <私有证据JSON>`（目标别名和端口按其 `--help`），按 [整机取证](whole-machine-ipv4.md)补齐配置读回与实际浏览器结果，再运行 `egress_verifier.py check --input <证据JSON>`。网页 WebRTC 不能用 UDP/STUN 代填；目标机依赖、权限或证据不足就记未完成，修好后重跑。远程故障演练另按下一节的独立恢复和 C 档确认执行。

<a id="mac-access"></a>
### Mac：远程登录与桌面会话

1. **先开系统自带的远程登录：**用户在“系统设置 → 通用 → 共享 → 远程登录”里启用，访问范围选“仅这些用户”，只加入本次管理账户。macOS 已有 SSH/SFTP，不为此另装 OpenSSH；远程用户的完整磁盘访问只在实际需要的路径要求时另行处理。步骤和当前界面见 [Apple 远程登录说明](https://support.apple.com/guide/mac-help/allow-a-remote-computer-to-access-your-mac-mchlp1066/mac)。
2. **从管理机确认终端和传文件都可用：**按目标 Mac 显示的登录信息连接，核对目标主机和登录用户；用 SFTP 或 scp 把脚本传到用户同意的私有目录，读回内容后执行。使用公钥时保留原有授权，密钥由用户保存，不放进记录或报告。
3. **跨网络时再接 Tailscale：**核对两端已连入用户选定的 tailnet、目标 Mac 在线，然后通过实际可达地址连接。Tailscale 负责接入；SSH 登录和目标机的代理出口各自检查，不用管理机的出口结果代证目标 Mac。
4. **桌面 GUI 在实际登录用户会话里处理：**Clash 界面、浏览器和桌面开关由该用户会话运行；需要查看界面时采用用户批准的屏幕共享或已有远程桌面。SSH 能执行命令不代表能代替用户点击系统授权；需要的权限由用户本人在 Mac 上确认，不用 root 会话代替桌面会话。
5. **再进入本机网络流程：**按[Mac 的 Clash 与 PF 指引](local-firewall-prompts.md#mac)先确认 TUN、DNS 和出口，记录实际核心、节点、物理网卡及管理链路。确需管理例外时单列用途和范围，不能把 Tailscale 的管理接入当成代理出口的一部分。

## 3. 远程故障演练

先按[本机主流程](local-firewall-prompts.md)让 TUN、出口和正常联网通过，再处理远程演练。远程停核心、改默认出站、重启后可能连不回来，属于 **C 档**，须当场确认，并先准备备份、保险丝和目标机本地或独立救援入口。

共同顺序是“停核心 → 探测 → 恢复 → 写私有结果”，恢复步骤不能依赖仍存活的 SSH 会话。重连后读取目标机结果；不能拿 SSH 已断代替没有直连的证据。

### Windows：独立计划任务

S10 [第三节](../sources/S10-windows-deployment-sanitized.md#windows-firewall)记录了停核心同时断 SSH、远端脚本随会话退出的问题。确需远程演练时，获准后用独立计划任务完成上述顺序。结果路径用目标机的明确私有位置，不把 SYSTEM 的 `USERPROFILE` 当作交互用户目录。

后台演练任务与桌面 GUI 分开：S10 [第八节](../sources/S10-windows-deployment-sanitized.md#verge-runtime)记录了 SYSTEM 会话启动 GUI 的失败；桌面应用应在正确的交互用户会话里运行。桌面开关仍按[晚间复盘](../sources/S10-windows-deployment-sanitized.md#desktop-launcher)验证真实双击入口和 UAC，不能用远程管理员命令或 SYSTEM 测通代替。

### Mac：PF 与独立恢复

1. **先生成并检查规则：**使用 [guardian-pf-killswitch.sh](../assets/mac-killswitch/guardian-pf-killswitch.sh) 的 `render`，核对实际物理网卡、节点和 DNS 引导需求。保持当前管理会话，并让目标机本地有可执行回滚的终端或独立恢复入口；本次管理流量是否会被 PF 拦住要在计划里说清。
2. **加载规则时复用 180 秒保险丝：**经 C 档确认后运行 `apply`；保险丝期间检查正常代理、域名解析和管理链路，再执行 `confirm`。不通就 `rollback` 或等保险丝恢复，不靠扩大放行范围碰运气。
3. **停核心前独立安排恢复：**确需远程演练时，用 `launchd` 承载可撤销的单次恢复任务，按本机实际服务和登录用户选择执行上下文；先确认任务能独立执行、结果写入明确私有路径，再停核心。恢复任务负责恢复本次停止的服务或撤销临时 PF 规则，不依赖 SSH 断线后的后续命令，不另装常驻看门狗。
4. **恢复后读回真实状态：**用脚本 `status` 核对本 anchor、保险丝和网卡覆盖，读取演练结果，确认出口、DNS 和管理连接恢复。按[整机出口指引](whole-machine-ipv4.md)记录网络结果；正常、故障和恢复三个阶段分别留证据。

## 4. 交付与回滚

网络验收仍在目标机按[整机出口指引](whole-machine-ipv4.md)做；远程扩展额外记录管理通道是否恢复、保险丝与临时任务状态、目标机本地恢复方法。重启、睡眠唤醒和换网没测的继续标未测。

结束时列明本次实际创建的 SSH/Tailscale 配置、授权公钥、计划任务、端口转发和防火墙例外，由用户决定哪些长期保留；不删除原有远程通道。回滚只恢复本次记录的改动，账号、密钥与删除动作仍按对应授权处理。

Mac 远程重启前，确认 FileVault 解锁和恢复登录由谁完成；睡眠唤醒、换网及登录后客户端自启分别检查，不能只凭当前 SSH 能连就承诺重启后仍可管理。临时 `launchd` 任务完成后核对结果并按计划移除，原有服务和用户任务保留。

Agent 按目标机实际版本、路径、权限与网络适配这些步骤，完成后报告该设备的实际结果。本文不新增远程执行器。
