# 本机路线：Clash 与防火墙（Agent 提示词）

适用：用户已选**本机路线**（Mac 或 Windows），出口 IP 已经定了来源（见[固定出口 IP 的来源](egress-ip-options.md)），现在要在自己的电脑上让**所有公网流量只走同一个代理出口**，代理掉线时不直连（fail-closed）。Windows 不提供脚本，**全部用提示词引导**；Mac 用一个 PF 脚本加提示词：Agent 一步一步问、说明、出变更卡，用户在自己的电脑上操作，或经逐项批准后由 Agent 在获准的会话里执行。

- **Windows：**用系统自带的 Windows 防火墙（Windows Defender 防火墙）。
- **Mac：**用系统自带的 PF，经 [guardian-pf-killswitch.sh](../assets/mac-killswitch/guardian-pf-killswitch.sh) 按网卡拦（ADR-054）。不再用 LuLu 做 kill switch，原因见下面 Mac 一节。
- 整机统一出口只走 IPv4 的配置、取证和判定见[整机统一出口](whole-machine-ipv4.md)；整机统一路径、明确例外、IPv4_ONLY 的要求见[现行整机统一路径](agent-remediation.md#ipv4-only-policy)；DNS、IPv6、WebRTC 的证据解释见[网络与修复建议](network-and-remedies.md)。

**目标机已有 Agent：**默认直接在该机完成本机流程，不需要 OpenSSH、Tailscale 或内网穿透。只有用户明确需要异机协助时，才进入[本机高级扩展](local-advanced-route.md)。远程接入不作为本机部署的前置步骤。

## 通用工作方式（两个系统相同）

1. **先问清楚，再动手：**系统版本、用的 Clash 客户端（Clash Verge 或 FlClash）、是否已导入节点配置、是否开了 TUN、电脑是不是公司或学校管理、有没有别的 VPN 或局域网必须保留（NAS、打印机、内网）。组织管理的设备先停下，防火墙策略可能不归用户管。
2. **先看后改：**只读收集现状（当前防火墙状态、现有规则、代理进程路径、TUN 网卡名、节点真实 IP 和端口），不改任何东西。
3. **按授权档位做（[authorization-tiers.md](authorization-tiers.md)）：**把能自行撤销、不切断访问的步骤合成一张**计划**，用户批准一次，Agent 连续执行；到可能锁死自己的步骤（默认出站切成阻止等）暂停，写确认单，用户确认后才继续。每步都写清目标、原值→新值、影响、回滚方法、验证方法。
4. **顺序固定：**先让 Clash 的 TUN 跑通并确认出口，再加防火墙。顺序反了会把自己锁在外网之外。
5. **Agent 就在这台电脑上时：**开 TUN、切默认出站为阻止、故障演练都会切断 Agent 自己调用模型的连接，先按 [Agent 和被改的网络在同一台机器上](agent-on-target.md) 查清 Agent 链路，会一直断开的步骤交给用户在终端执行。
6. **必须做故障演练：**防火墙装好后，停掉代理核心，确认外网全部失败（没有直连），再启动代理确认恢复。没演练就不能说 kill switch 成功，只能说"规则已配置，未验证"。
7. **保留回滚路径：**动手前导出现有规则，备好撤销命令；有第二个会话或另一台设备可以操作，不要只有一个入口。本机可用的人工终端和离线恢复属于恢复入口，不因此要求安装远程管理工具。
8. **正常关闭前先清进程：**退出 Desktop／关闭 Claude 标签页后仍可能有后台监听；保持代理和防直连规则，按[安全退出顺序](routes-and-platforms.md#safe-shutdown)核实并清理残留、复查无自动重启，再停代理，最后恢复原防火墙配置。未查清不得交接“现在可以关闭”；故障演练和紧急回滚沿用原恢复方案。

<a id="delivery-scope"></a>
## 替别人交付：先说范围，按验收单交

替客户、同事、家人交付 Mac／Windows 本机路线时，按以下范围和验收单执行。

1. **开工前说清 Skill 给什么：**本机路线是提示词引导（Windows 按本文第 1 到 7 步，Mac 按 PF 一节），检测和判定用 `network_check.py run` 和 `egress_verifier.py`；首次部署没有 Windows 规则生成引擎；已部署防护可用[统一开关与桌面界面](killswitch-switch.md)。没有新增常驻程序或自动恢复服务。客户要“一键全自动”时当场说。
2. **断线保护不用另写程序：**默认出站阻止和 `guardian-*` 规则是系统防火墙的持久配置，但配置保留不等于保护已验证：现有宽放行、未启用的配置文件、TUN 重建后的接口变化都要核对（[S10 第三节](../sources/S10-windows-deployment-sanitized.md#windows-firewall)、[第九节](../sources/S10-windows-deployment-sanitized.md#tun-firewall-lifecycle)）。TUN 恢复交给客户端的服务模式和开机自启；验收须证明恢复之前只断网、不直连。客户端没有受支持的自启入口就告诉客户，不自建服务（[修复后的复验](agent-remediation.md#post-repair-stability)）。
3. **验收单，每项报通过／未通过／未做：**
   1. **一次取证：**TUN 开着、Claude Desktop 运行时跑一次 `network_check.py run --failure-drill`，交给 `egress_verifier.py` 判定（[整机统一出口](whole-machine-ipv4.md)）。出口、DNS、IPv6、UDP（STUN 映射和 TCP 出口一致，见 [WebRTC 堵法](agent-remediation.md#webrtc-block)）、停核心演练都在这一次里，同一阶段不分开重测；重启、睡眠、换网等不同场景仍须分别取证。
   2. **防火墙读回：**三个配置文件都启用且默认出站都是 Block，`guardian-*` 规则齐全，并核对其他 Allow 规则是否仍放过直连。上不了网时才用分层诊断。
   3. **重启演练：**重启后、客户端起来之前外网不通；自启、TUN 恢复后正常；默认出站仍是 Block。客户本人在场的本机按 B 档，远程按 C 档（重启后可能连不回来）。
   4. **浏览器验收：**客户本人在实际用的浏览器打开 https://ip.net.coffee/claude/，除语言外全绿（[做法](whole-machine-ipv4.md#browser-acceptance)）。
   5. **若交付[统一桌面开关](killswitch-switch.md)：**按客户的实际入口验收“双击 → UAC → 三档状态读回 → 联网/阻断行为”，不能用 SSH、SYSTEM 任务或手输带 Bypass 的调试命令代替。快捷方式配方见 [S10 晚间复盘](../sources/S10-windows-deployment-sanitized.md#desktop-launcher)，不要求所有交付都开发开关。
   6. **完成[突发场景验收](#incident-acceptance)的适用项目，前四项及实际交付的开关都过，客户本人登录 Claude。**
4. **超出 Skill 的自动化先报工作量：**一键脚本、自写执行器、常驻守护这类，先说要额外开发什么、大概多久，客户同意再做；能按第 1 到 7 步手动做完的先手动交付。
5. **每过一项就告诉客户：**某一步重试一次仍失败，先回到安全状态（保险丝还在，或默认出站已恢复为允许），再说清卡在哪一项、下一步谁做。没全过就报哪几项过了、哪几项没过。

<a id="incident-acceptance"></a>
## 突发场景：分平台处理与 Agent 验收提示词（2026-11-09）

完成首次网络部署后，Agent 必须按下表为当前目标机逐项建立验收结果；日常开机、唤醒、断网重连和已覆盖接口间换网，交给已配置并验证的系统防护与客户端恢复，不要求再次调用 Skill。

### 平台机制与检查重点

| 平台 | 防护如何保留 | 当前实现与检查重点 |
| --- | --- | --- |
| Windows | Windows 防火墙的 PersistentStore 是系统持久策略；正常关机、重启、睡眠不会删除已保存的规则，不依赖 Clash GUI 常驻或登录后重新写规则 | 核对 ActiveStore 实际生效策略、Domain/Private/Public 三档启用及默认出站 Block、其他 Allow 规则、规则的程序路径和接口条件。换网可能改变网络配置文件，TUN 重建可能改变接口；检查这些条件而不是每次重装防火墙。代理恢复由客户端服务模式／自启负责 |
| Mac | 当前 PF 内核规则与磁盘上的已确认规则分开；`persist` 安装 LaunchDaemon，开机重新加载已确认规则 | 检查 PF 启用、主 anchor 挂载、本 anchor 规则和物理网卡覆盖。当前脚本没有联网前加载的强制顺序、换网监控或新网卡自动补规则；需要按实际触发过程验证 |
| Linux VM／VPS | 使用相应路线的 nftables 持久化与启动单元，不套用 Mac 或 Windows 步骤 | 核对实际 unit 的启用状态、加载顺序、运行规则；仅装了 Linux 进阶组件时才检查 refresh.timer 与 core 看门狗。客机、宿主、远端分别记录，不能用宿主结果代替客机 |

Windows 的策略存储和生效配置文件见 [Microsoft New-NetFirewallRule：PolicyStore / Profile](https://learn.microsoft.com/en-us/powershell/module/netsecurity/new-netfirewallrule?view=windowsserver2025-ps)。PF 与 nftables 控制的是允许路径／节点地址，代理服务端的最终出口变化仍须单独比较预期 IP。

### 场景与通过条件

每行均记录“触发前正常 → 变化或故障期间 → 恢复后”，使用实际新连接。故障期间检查物理出口是否出现非批准的公网直连；恢复后检查是否回到同一预期 IPv4。DNS、IPv6、UDP 和浏览器 WebRTC 分别记录。只在恢复后测一次不能证明切换期间没有泄漏；没有覆盖的时间段明确标缺证。

| 场景 | 触发与平台重点 | 通过条件／后续处理 |
| --- | --- | --- |
| 核心崩溃／TUN 消失 | 经批准停止精确核心进程，保留防火墙；核实核心确已退出、TUN／路由实际变化 | 普通应用 TCP、DNS、UDP 无非批准直连；恢复核心后回到预期出口。不能用原本没网或代理端口关闭代证阻断 |
| 节点不可达 | 使用批准的可恢复方式让当前节点不可用，保持本地网络正常；核对代理组是否自动切换 | 不转 DIRECT、不切到未经批准的出口；恢复原节点后出口一致 |
| 重启 | 保存工作、准备独立恢复后真实重启；核对启动时间，观察客户端未启动和启动后两阶段 | Windows 持久规则仍在且 ActiveStore 生效；Mac 检查本次启动加载；Linux 检查加载 unit。代理未恢复时无直连，恢复后出口一致；登录后取样不能代表登录前全部时间 |
| 关机后开机／断电恢复 | 正常关机再开机单独记录；Windows 快速启动与“重启”的实际路径分别注明。禁止为验收直接拔电或强制断电 | 同重启检查。实际断电事故后先查策略、服务和出口；正常关机测试只证明该路径，突然断电未发生则记未做，不冒充已测 |
| 睡眠唤醒 | 按设备实际睡眠方式触发，唤醒后检查规则和 TUN 恢复 | 唤醒恢复过程中无非批准直连，恢复后出口一致；没有睡眠能力的远端注明不适用 |
| Wi-Fi／热点／有线换网 | 在现有授权网络间切换；Windows 检查网络配置文件与接口条件，Mac 检查网卡覆盖和 DHCP DNS，Linux 检查路由与接口规则 | 切换期间防直连仍有效，恢复后 DNS、UDP、IPv6、WebRTC 和出口符合基线 |
| 新增网卡／TUN 接口重建 | 新接口接入前核对规则覆盖；Mac 未覆盖时先在隔离条件下更新规则再允许承载业务；Windows 检查实际 Profile 与 InterfaceAlias 等条件 | 新接口上普通流量仍受约束；只看到规则存在但接口未匹配记失败。没有相应硬件记未做 |
| 节点域名／节点地址更新 | 确认新地址来源；Mac 重新 `apply → confirm`，Linux 按已安装的刷新组件检查，Windows 核对地址过滤条件 | 节点能恢复、其他地址仍受阻断；核心引导 DNS 与系统 DNS 例外分别核对 |
| 订阅／客户端更新、出口漂移 | 实际更新后读回持久配置和运行配置；比较原预期出口与当前样本 | 原规则和程序路径仍匹配、出口未擅自改变。漂移时暂停相关使用并排查，不靠切节点反复试；防火墙本身不监视最终出口 IP |
| Agent／SSH 中断 | 演练前确认 Agent 自己的链路及不依赖该会话的恢复方式 | 恢复任务或本机人工恢复可执行；重连后读取结果。SSH 断开本身不是阻断通过证据 |

正常关机不要求撤销长期防火墙规则。只有明确停用保护／回滚时，才按[安全退出顺序](routes-and-platforms.md#safe-shutdown)清理相关进程后撤销对应规则。保险丝回滚是恢复访问的措施，不能算故障防直连持续有效。

### 可直接交给目标机 Agent 的提示词

```text
按 Claude Guardian 的“突发场景：分平台处理与 Agent 验收提示词”检查这台目标机。
目标是一次部署和验收，日常自动恢复，持续异常才再次调用 Skill。
先确认系统、客户端、当前预期出口、TUN、持久防火墙、管理链路和恢复入口；已有信息直接读取。
优先配置客户端支持的服务模式、开机自启和断线重连，保持原指定节点；复用系统持久防火墙和已安装的恢复组件。
Windows 核对持久策略与客户端服务；Mac 按现有 apply → confirm → persist 流程配置并验证开机加载；Linux 复用已安装的启动单元、刷新任务与看门狗。
首次部署按档位批准具体系统改动，说明自启／恢复组件、影响和撤销方法；本提示词不是设备操作授权。
日常恢复在本机执行，不依赖 Agent、模型或 SSH 会话在线；不要默认另写执行器、安装新守护服务或定时调用 Skill。
只有现有机制确有缺口时才提出最小补充方案，说明用途、工作量和维护成本，获准后实施；尚未部署的检查、告警或恢复能力标未配置。
按场景表列出本机适用项目，每项写触发方法、平台检查点、通过条件、恢复方式和授权档位。
Windows 检查 PersistentStore 与 ActiveStore、三种 Profile 及规则条件；不要把重启说成规则丢失。
Mac 检查 PF 开机加载与网卡覆盖；Linux 检查实际安装的 nftables 和启动／自愈组件。
在目标机使用随包 network_check.py 和 egress_verifier.py，先补齐缺失依赖，不另写替代验收器。
以正常基线、变化／故障期间、恢复后三阶段取证，出口与事先记录的预期值比较。
保留已批准的网络例外；单次超时、SSH 失联、规则存在都不能单独判定无直连。
首次交付覆盖全部适用场景，验证过程中不靠 Agent 临时修复来冒充自动恢复；分别记录自动恢复、人工恢复和未恢复。
日常事件已自动恢复且配置未变时，不要求用户重跑 Skill 或整套验收；持续失败、发现出口漂移、新接口未覆盖或关键配置／版本变化时，再调用 Skill 只处理受影响项。同一阶段证据可复用，不能跨场景代填。
已有恢复机制只按明确的次数／时间上限重试原配置；失败保持防直连并用现有通知能力提示，交付时写清通知入口；没有通知能力就如实说明。禁止自动转 DIRECT、切换未经批准的出口、关闭防火墙或扩大白名单。
Mac 当前缺少联网前加载强制顺序、换网监控和新网卡自动补规则；需要调整的场景保留人工处理，不能仅凭事后检查宣称全程保护。最终出口漂移也不能靠防火墙本身发现。
交付只需说明哪些场景已自动恢复、哪些仍需人工、失败时看哪里，以及离线恢复入口；私人配置与诊断摘要留在目标机。
沿用已有授权；B 档计划批准一次，可能断开唯一控制通道等 C 档步骤当场确认。先准备独立恢复，再触发中断。
重启、换网、睡眠等需要用户配合时一次列清；不自行拔电，不安装额外常驻服务或扩大白名单。
每项输出：场景、平台、触发情况、故障期阻断、恢复后出口一致性、DNS/IPv6/UDP/WebRTC、恢复结果、通过/失败/未做/不适用及原因。
私有证据经同意保存在目标机，每次使用新文件名；公开汇报只用别名和结论，不写真实 IP 或凭据。
恢复后按浏览器验收指引由用户完成实际浏览器检查；接触 Claude 仍遵守原门禁。
只有实际完成并通过的重启、睡眠唤醒、换网才填入 lifecycle_checked；跳过项不填，失败先处理再复验。
```

常用取证顺序见[整机出口](whole-machine-ipv4.md)：`network_check.py run --target-ref <别名> --evidence-output <新的私有文件>`，故障演练加 `--failure-drill`，实际代理端口按目标机填写；补齐配置与浏览器观察后交给 `egress_verifier.py`。它是证据判定器，不会自动触发全部场景；`established` 与生命周期 `persistence` 分别报告。完整场景结果另列，不能把三项 `lifecycle_checked` 当成整张表的自动验收。

## Mac

### Mac 上的 Clash（Clash Verge）怎么配

下面是 Agent 引导用户的顺序，界面名称以当前版本为准，先核实实际安装版本再给步骤。

1. **安装与版本：**从官方发布页安装 Clash Verge（Rev），记录版本（本项目对 2.5.8 的 rules 扩展有专门的单条规则任务，见 [agent-rules-task.md](agent-rules-task.md)；其他版本需要对应适配）。不创建扩展、不改订阅原文、不切换 profile，除非用户明确要求。
2. **导入节点配置：**由用户在客户端里导入自己的订阅或节点，Agent 不索取订阅链接、密码或 UUID。
3. **TUN 模式：**在客户端设置里开启 TUN。macOS 上通常需要先安装“服务模式”来获得创建虚拟网卡的权限，会弹系统授权，由用户自己确认。说明影响：TUN 会接管整机流量，局域网、VPN、DNS 可能受影响。
4. **DNS：**TUN 下的 DNS 解析和 Fake-IP 的边界按 [macOS DNS 经验](macos-dns-case-lessons.md) 逐层核对：系统实际解析器、核心配置、浏览器自带 DoH 分开看；Fake-IP 本身不泄漏，但 `fake-ip-filter` 里的域名会真实解析，要核对由谁应答。
5. **验证出口：**浏览器和终端分别确认出口 IP 是预期的那个；WebRTC 用包内的[本地探测页](../assets/webrtc-probe.html)检查，有泄露按 [WebRTC 堵法](agent-remediation.md#webrtc-block)装插件或写策略；DNS 用检测页确认没有明显的本地运营商解析。最后由用户在浏览器打开 https://ip.net.coffee/claude/ 做浏览器环境验收，除语言外必须全绿（时区要和出口一致）（[做法](whole-machine-ipv4.md#browser-acceptance)）。
6. **只读盘点：**需要看现有 Clash 配置和控制器时，用只读盘点（`inventory_cli.py`），不读订阅正文、控制器密钥或个人配置哈希。
7. **需要异机协助时：**按[本机高级扩展的 Mac 步骤](local-advanced-route.md#mac-access)接入和准备恢复；目标机已有 Agent 时直接在本机做，不把远程接入变成前置。

### Mac 的防火墙：PF 脚本（已验收）

**验收记录（2026-11-09）：Mac PF 已验收。**范围包括故障阻断、保险丝、开机加载、重启、换网、新网卡、睡眠恢复、DNS／UDP、浏览器／WebRTC 和回滚；日期为状态更新，非新增测量。新目标机仍须按下列步骤核验。

**为什么不用 LuLu：**LuLu 按“哪个进程发起连接”过滤，判断发生在路由之前，分不出流量是进 TUN 还是直连。只给代理核心放行时，正常经 TUN 的连接（比如 curl 连 1.1.1.1）照样被按 curl 进程拦掉；反过来给每个应用都放行，TUN 一掉它们又能直连。所以 LuLu 做不了“走 TUN 放行、直连拦截”。已经装了 LuLu 的，用 PF 前把它的默认拒绝关掉（切回放行或退出），否则会和 PF 叠加，把 TUN 流量拦掉。

**PF 怎么拦：**按网卡，不按进程。物理网卡（Wi-Fi、有线、雷雳网桥等）只放行发往节点真实 IP 和端口的连接，加 DHCP，可选核心解析节点用的 DNS（`BOOTSTRAP_DNS`）和局域网例外（`LAN_NET`）；其余出站一律丢弃。TUN（utun）和回环不受影响。核心或 TUN 停掉后，应用流量落到物理网卡，被拦，不会直连。规则放在 `com.apple/claude-guardian` 子 anchor 里，不改 `/etc/pf.conf`；Apple 的 TN3165 说 PF 不是稳定接口，所以系统大版本更新后要重做故障演练（ADR-054）。

步骤（授权档位见 [authorization-tiers.md](authorization-tiers.md)）：

1. **前提：**先按上一节让 TUN 跑通并确认出口；LuLu 的默认拒绝已关；节点用 IPv4（IPv6 节点会被跳过）。
2. **看规则（A 档，不改系统）：**`bash guardian-pf-killswitch.sh render`，核对网卡列表包含实际在用的网卡、节点是真实 IP（不是 198.18.x.x）、端口齐全。节点在 proxy-providers 里或解析不出时，用 `NODE_IPS`、`NODE_PORTS` 指定。
3. **加载（C 档，当场确认）：**`sudo bash guardian-pf-killswitch.sh apply`，默认 180 秒保险丝，不确认就自动撤销。保险丝时间内跑通透明 TUN、域名、显式代理三条检查，再 `sudo ... confirm`。
4. **故障演练：**用 `network_check.py run --failure-drill` 那一次取证，停核心后确认路由已回到物理网卡、外网全部失败，再恢复。没演练就不能说 kill switch 成功。节点是域名、核心重启后连不上节点的，把核心的 `proxy-server-nameserver` 填进 `BOOTSTRAP_DNS` 重新加载。
5. **开机加载（C 档）：**`sudo ... persist` 装 LaunchDaemon，只加载已确认的那一版规则。
6. **日常：**`sudo ... status` 看命中计数、网卡覆盖和 DNS 路径；换节点、换网卡（出现“不在规则里”的提示）后重新 `apply` 和 `confirm`。
   - **系统 DNS 必须手动设成公网 IPv4：**macOS 不会把发往局域网的 DNS 劫持进 TUN。网络服务的 DNS 是“自动”时，换网后会用新网络 DHCP 下发的 DNS，常见是路由器地址，查询走物理网卡被 PF 丢掉，表现是 IP 能通、域名解析失败（curl exit 6）。`bash guardian-pf-killswitch.sh dns` 只读列出每个网络服务是手动还是自动、当前 DNS 走哪张网卡。改法（B 档）：每个网络服务 `sudo networksetup -setdnsservers "<服务名>" 1.1.1.1`，恢复自动用 `empty`。不要把系统 DNS 放进 `LAN_NET`：能解析，但查询绕过代理；也不要和 `BOOTSTRAP_DNS` 用同一个地址，否则核心停掉后查询能直接发出去。
   - **拦了什么看 `blocked`：**`sudo bash guardian-pf-killswitch.sh blocked 60` 抓 60 秒被拦的包，按网卡、目的地类别（局域网、公网、组播等）和端口汇总，不输出 IP。正常使用时组播、链路本地、IPv6 被拦一般无害；出现公网 TCP/443、UDP/STUN 说明有流量没进 TUN，出现公网 UDP/53 多半是核心自己的上游 DNS 被拦。
7. **回滚：**`sudo ... rollback` 撤销运行中的规则；`sudo ... uninstall` 连开机项和生成的文件一起删。脚本不在时用 `sudo pfctl -a com.apple/claude-guardian -F rules`。规则只拦网络，本机终端随时能回滚。

**真机样本（2026-11-05）：**macOS 26.6.2、bash 3.2、Clash Verge Rev 2.5.10、VLESS+REALITY 域名节点，使用现场修正版完成加载、联网检查、确认、停核心无直连及开机持久化；`egress_verifier` 为 `established`，8 层 pass，OS_IPV6 为 advisory。

**脚本验证（2026-11-09）：**现场变量边界修复已合入；Bash 3.2 的 UTF-8／C locale 回归均通过，未重新加载 PF。版本与证据差异见 ADR-063，不能据此扩大真机覆盖范围。

## Windows

### Windows 上的 Clash

1. 客户端（Clash Verge 或 FlClash）从官方发布页安装，记录版本；用户自己导入节点配置，Agent 不索取订阅链接和密码。
2. **TUN：**开启 TUN 需要管理员权限，由用户确认系统弹窗。说明影响：整机流量被接管，局域网、VPN、DNS 可能受影响。
3. **网卡 IPv6：**默认关闭，和 TUN 放在同一张计划里批准（B 档），步骤见 [Windows 网卡 IPv6](agent-remediation.md#windows-adapter-ipv6-hint)；节点用 IPv4 地址。
4. 验证出口、WebRTC、DNS 的方法同 Mac。

**本机实战按需读：**从 [S10 第二节](../sources/S10-windows-deployment-sanitized.md#windows-baseline)的检查基线开始；PowerShell 编码看[第五节](../sources/S10-windows-deployment-sanitized.md#powershell-tools)，配置加载与 GUI 会话看[第八节](../sources/S10-windows-deployment-sanitized.md#verge-runtime)，防火墙与 DNS、接口重建看[第九节](../sources/S10-windows-deployment-sanitized.md#tun-firewall-lifecycle)。S10 完整正文保留，远程接入、跨机传文件和远程故障演练统一从[本机高级扩展](local-advanced-route.md)进入，不沿原案例顺序要求本机用户先搭远程通道。

### Windows 的防火墙：系统自带

**整机方案的用户代价必须先说明：**代理停用时其他软件也可能断网；国内网站可能转走代理并增加流量／延迟／费用，局域网、打印、虚拟机／Cowork、其他 VPN 和远程访问须先核对例外。例外会放宽防直连约束。首次部署后使用 [Switch 整机出口模式](killswitch-switch.md#windows-整机出口模式代价与首次交付)审计完整允许规则集合；普通 Claude 版本目录变化无需重绑应用路径，网络规则变化仍须复核。

**先决条件：**用管理员 PowerShell；电脑不是组织管理（组策略或 MDM 管理的防火墙，停下，不由用户决定）；TUN 已跑通并确认出口；**节点真实 IP 和端口**已知（从 profile 里读，域名解析成真实 IP 时要排除 Fake-IP 的 198.18.0.0/15）。

按下面顺序。**第 1 到 3 步是 B 档**（可自行撤销、默认仍放行、不会断网），合成一张计划批准一次；**第 4 步是 C 档**（切默认出站为阻止，可能锁死），到这一步暂停，写确认单，用户当场确认；第 5 步在用户本机且用户在场时按 B 档，目标是远程机器时按 C 档；第 6、7 步是回滚和维护：

1. **导出现有规则并记录原值（只读加备份）：**
   - `netsh advfirewall export "<备份路径>\fw-backup.wfw"`
   - `Get-NetFirewallProfile | Format-Table Name,Enabled,DefaultInboundAction,DefaultOutboundAction`
   把输出里的默认出站动作记下来，这是回滚依据。
2. **布置保险丝（先于任何阻止动作）：**创建一个几分钟后自动把默认出站改回允许的计划任务，用户确认规则有效后再删除它。命令形式（时间换成当前时间加 3 分钟，先在用户机器上核实可用）：
   `schtasks /Create /TN guardian-fw-rollback /SC ONCE /ST HH:MM /RU SYSTEM /TR "powershell -NoProfile -Command Set-NetFirewallProfile -Profile Domain,Private,Public -DefaultOutboundAction Allow" /F`
   确认后删除：`schtasks /Delete /TN guardian-fw-rollback /F`。
3. **先加允许规则（此时默认动作仍是允许，不会断网）：**规则名统一以 `guardian-` 开头，方便整体回滚。
   - 代理核心到节点：`New-NetFirewallRule -DisplayName "guardian-allow-proxy-core" -Direction Outbound -Program "<核心程序完整路径>" -RemoteAddress <节点IP> -RemotePort <端口> -Protocol TCP -Action Allow`，UDP 节点（如 Hysteria2、TUIC）再加一条 UDP。
   - TUN 网卡：`New-NetFirewallRule -DisplayName "guardian-allow-tun" -Direction Outbound -InterfaceAlias "<TUN 网卡别名>" -Action Allow`（别名用 `Get-NetAdapter` 核实）。
   - DHCP：`New-NetFirewallRule -DisplayName "guardian-allow-dhcp" -Direction Outbound -Protocol UDP -LocalPort 68 -RemotePort 67 -Action Allow`。
   - 回环和必要的局域网例外**逐项核对**，不要假定默认放行；有则加规则。
   - **回环用接口，不用 `::1`：**部分 Windows 版本（如 10.0.26200）拒绝 `-RemoteAddress ::1` 或 `::1/128`，报“已指定未指定的多播、广播或环回 IPv6 地址”。改用回环软件接口：先 `Get-NetIPInterface | Where-Object InterfaceAlias -like "Loopback*"` 核实本机唯一的回环接口别名（通常是 `Loopback Pseudo-Interface 1`），再 `New-NetFirewallRule -DisplayName "guardian-allow-loopback" -Direction Outbound -InterfaceAlias "<回环接口别名>" -Action Allow`。读回时 `(Get-NetFirewallRule -DisplayName "guardian-allow-loopback" | Get-NetFirewallInterfaceFilter).InterfaceAlias` 只有一个值时是字符串，不是数组，不要取 `[0]`（会只拿到第一个字符）。
   - **核心程序路径以正在运行的为准：**`Get-Process | Where-Object Name -like "*mihomo*" | Select-Object Name,Path`。Clash Verge 的服务模式下跑的是服务目录里的核心，不是安装目录里的那个；路径不对，第 4 步之后核心连不上节点，所有经 TUN 的连接都会超时。节点用域名的，按当前解析结果填全部 IP，并给核心解析节点域名所需的 DNS 单独放行。
4. **最后切换默认出站为阻止（保险丝已就位）：**`Set-NetFirewallProfile -Profile Domain,Private,Public -DefaultOutboundAction Block`。切换后立刻验证出口仍通、浏览器可用；不通就按下面“[切换后不通：分层诊断](#windows-fw-layered-diagnosis)”在保险丝时间内查，查不清就回滚，不扩大白名单碰运气。
5. **故障演练：用 `network_check.py run --failure-drill` 那一次取证代替，不另外手动演一遍。**第 4 步的正常代理通信确认通了才做。工具会提示停一次代理核心、再打开；结果里“故障演练”一项是“停掉代理后连不出去，没有直连”就算通过，同一次取证交给 `egress_verifier.py` 判定（即[替别人交付](#delivery-scope)验收单的“一次取证”）。通过后删除保险丝任务，未通过或没跑就不删。
6. **回滚：**`Set-NetFirewallProfile -Profile Domain,Private,Public -DefaultOutboundAction Allow`，再 `Get-NetFirewallRule -DisplayName "guardian-*" | Remove-NetFirewallRule`；必要时 `netsh advfirewall import "<备份路径>\fw-backup.wfw"` 还原整体。
7. **更新后复查：**换节点、改端口、更新客户端后，节点 IP 和核心路径可能变，规则要同步更新，否则会断网。

**Windows 样本：**第 1 到 4 步在 Windows 10.0.26200、Clash Verge Rev 2.5.2 上通过，涵盖备份、保险丝、加规则、切换和回滚；该样本的第 5 步故障演练还没在真机上跑通。[S10](../sources/S10-windows-deployment-sanitized.md) 另有 Win10/Win11 故障阻断报告，未独立复验；浏览器、严格路由和生命周期待办按原记录保留。首次使用先用 `-WhatIf` 或只读命令确认参数和别名。

<a id="windows-fw-layered-diagnosis"></a>
### 切换后不通：分层诊断

默认出站切成阻止后正常上网失败，在**同一个保险丝窗口里**按下面顺序各测一次，每步记 curl 退出码和 HTTP 状态码，不记返回的 IP 和节点地址。一个窗口测不完就先回滚，下个窗口接着测，不要每次从头猜。

| 顺序 | 测什么 | 命令形式 | 说明哪一层 |
| --- | --- | --- | --- |
| 1 | 显式本地代理 | `curl.exe -sS -o NUL -w "%{http_code}" -x http://127.0.0.1:<mixed 端口> https://example.com` | 通：核心到节点这条允许规则没问题；不通：先查核心程序路径、节点 IP、TCP/UDP 协议 |
| 2 | IPv4 字面地址经 TUN | `curl.exe -sS -o NUL -w "%{http_code}" -k https://<中性站点的 IPv4>` | 1 通而 2 不通：TUN 网卡规则或 TUN 路由有问题 |
| 3 | 系统 DNS | `Resolve-DnsName example.com -Type A` | 1、2 通而 3 不通：DNS 劫持或 DNS 放行有问题 |
| 4 | 域名 HTTPS | `curl.exe -sS -o NUL -w "%{http_code}" https://example.com` | 前三步都通而 4 不通：看 TLS 或规则分流 |

curl 退出码对照：`6` 解析失败（DNS 层）；`7` 连接被拒或被拦（TCP 层，IPv6 字面地址在核心关了 IPv6 时就是 7，属预期）；`28` 超时（包发出去没回应，最常见是核心到节点被拦）；`35` 或 `60` 是 TLS 层。四步都通过后才进入第 5 步故障演练。

### Windows 更新覆盖与规则替换

更新后、恢复业务前，分别盘点当前包版本／包内主程序与辅助 EXE、包外桌面托管 Code 运行时、Cowork 服务的实际路径与服务身份；组件数不固定。比较新旧清单、签名／包身份、Program/Service/Interface 条件以及 PersistentStore/ActiveStore。新辅助组件或包外运行时未验证时记 unknown，旧路径消失或条件失配记 fail；不能凭旧规则存在或开关 on 自动启动受保护应用。

路径重扫与重绑只能证明当前版本的配置，不能证明更新后的首次联网受保护。持续覆盖须在更新前验证既有默认阻断及例外是否足够，或另行评审版本无关的身份过滤方案；没有这一证据就暂停受保护业务，先验收后恢复。固定包身份、发布者标签仍可能随证书、包身份和网卡变化失效。Guardian Switch 不监控更新、不启动应用。旧应用路径模式不自动发现新增组件，其应用覆盖 unknown 不能当 pass；整机出口模式不依赖 Claude 组件清单，检查完整出站 Allow 集合及审核条件，规则 pass 仍不能代替真实出口验收。

规则替换：先保存精确旧规则与条件的本机回执，保留旧保护；以独立批次创建新规则，使用终止错误处理，逐条核实两种存储中的数量、启用、方向、动作、程序／包／服务、接口、地址和端口。第 N 条创建失败或读回失配时不报成功，只回退本批精确变更，回退失败明确记录并保留回执。完整验收后才按已确认清单撤销旧规则；不要通配清空再重建。来源 S05 的修订示例仅部署当前包路径，不代表完整方案。重启、换网、证书更新、真实 Claude/Cowork 任务分别取证，独立测试程序不能代填。

### Windows Error 5 分诊

`New-NetFirewallRule` 的 `Windows System Error 5 / AccessDenied` 先记录准确阶段（创建、读回或删除）、规则条件类别、令牌是否提升、有效策略与管理限制，以及已有的窄范围对照结果；只读核对也须限定目标。管理员或 SYSTEM 仍拒绝时不能重复解释为“没给管理员权限”，也不能凭此断言安全软件干预或身份字段不支持。没有对照证据就记 unknown，不为诊断自行创建宽泛规则或升级到 SYSTEM。

Windows 原生拒绝、Skill 门禁和 Agent 工具 `blocked by policy` 分开记录。原因不明时保留旧保护、错误摘要及本机回执，停止反复写入。原生 WFP／AppID Tagging 尚非本项目通用后端；引入原生后端需单独评审和授权，不自动绕过管理限制。

### 查 WFP 丢包记录

想确认是哪条规则拦的，可以只读查询 WFP 事件；临时启用审计另按下述授权执行：

UDP Send 成功只证明本地提交，不证明送达；请求超时也不能单独证明防火墙阻断。TCP、UDP 分别建立已知可达基线，再结合有效响应或准确匹配的系统丢包证据。使用 5157 时核对测试时间、程序身份、方向、端点、协议（TCP 6／UDP 17）及 FilterRTID 对应的实际过滤器；仅出现同号事件不算证据。恢复对照和临时审计原值分别记录。

- 管理员 PowerShell 里先进入可写的私有目录，或显式指定输出文件：`netsh wfp show netevents file="<私有目录>\netevents.xml"`。不指定时写当前目录，没有写权限就退出码 1、没有文件。
- 记下退出码，错误输出只记类别（权限不足、参数错误、无输出文件），不贴原文。**查询失败、没生成 XML 或 XML 解析失败都不等于“没有阻断事件”**；输出里有尖括号也可能只是帮助文本。
- 还查不到时，可以临时开启“筛选平台连接”失败审计（B 档，可撤销）：先 `auditpol /get /subcategory:"Filtering Platform Connection"` 记原值，再 `auditpol /set /subcategory:"Filtering Platform Connection" /failure:enable`，复现一次后 `Get-WinEvent -FilterHashtable @{LogName='Security'; Id=5157} -MaxEvents 20` 看被拦的程序、方向和端口，查完按原值恢复。
- 只在本机看，不上传原始 WFP 日志或安全日志；给反馈时只写“哪个程序、哪个方向、哪个端口类型被拦”。
- 不要反复让用户粘贴长命令和长日志；Agent 能执行就自己执行，不能执行就给一段完整的脚本让用户一次运行，输出只保留上面这些摘要字段。

### 宿主拒绝执行时

Agent 的执行工具返回 `blocked by policy` 之类的拒绝，是**宿主的限制**，和本项目门禁、Windows 权限不足、防火墙规则错误是四件不同的事，分开记录：

1. 停下这一步，不换工具、不换写法、不拆成小命令绕过去；用户授权也解除不了宿主限制。
2. 先确认系统处在安全状态：保险丝任务还在，或默认出站已恢复为允许、`guardian-*` 临时规则已清理。
3. 交接给用户：说明被拒的是哪一步、它要做什么，把完整命令或脚本交给用户在自己的管理员终端里运行，或者就此收尾。
4. 在报告里写成“宿主拒绝”，不写成脚本失败或 Windows 故障。

### 最小反馈清单

需要用户帮忙验证或提交反馈时，只要这些，不要账号、真实节点地址、订阅、完整配置：

- Windows 版本号（`[Environment]::OSVersion.Version`）、客户端和核心版本、TUN 栈（gVisor／system／mixed）、规则或全局模式。
- 三个防火墙配置文件的 `Enabled` 和 `DefaultOutboundAction`。
- `guardian-*` 规则的名称、方向、动作和过滤类型（程序／接口／端口），不含地址。
- 分层诊断四步各自的 curl 退出码和 HTTP 状态码。
- WFP 或审计查询的退出码与错误类别。
- 当前恢复状态：默认出站、临时规则数、保险丝任务是否已清理。

## Agent 不做的事

- 不在没有备份、没有保险丝、没有第二个入口时切换默认出站为阻止。
- 不在组织管理的设备上改防火墙；不绕过策略。
- 不假定回环、局域网、系统进程默认放行；不把“规则配置完成”说成“kill switch 成功”。
- 不自动批准系统扩展、不替用户点系统授权弹窗；Mac 的 PF 规则不写进 `/etc/pf.conf`。
- 不索取订阅链接、节点密码、UUID，不把它们写进规则说明或报告。
