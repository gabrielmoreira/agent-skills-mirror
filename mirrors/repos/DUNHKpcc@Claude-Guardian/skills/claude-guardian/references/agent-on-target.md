# Agent 和被改的网络在同一台机器上

适用：Agent（Codex 等）运行在**正被改网络的那台机器上**。常见三种：VM 客机里装 Agent，在客机里用本 Skill；本机路线中，Agent 在用户自己的电脑上直接改 Clash 和防火墙；VPS 上跑 Agent，同时在这台 VPS 上开 TUN 或装防火墙。

Agent 在另一台机器上通过 SSH 或控制台操作目标机时，管理通道、保险丝和救援入口按各路线文档做（[VM](vm-guidance.md#4-客机防火墙fail-closed)、[进阶路线](advanced-route.md)、[VPS](vps-guidance.md)），本文不涉及。

修改 Agent 自己使用的网络可能切断模型 API 连接，使后续核对、`confirm` 和汇报中断。恢复必须由独立的本机机制承接。

## 1. 开工前先查清 Agent 自己的连接走哪条路

A 档，只读。结果写进计划，记为“Agent 链路”：

1. **Agent 进程在哪：**哪台机器（宿主还是客机）、哪个用户。
2. **代理变量：**`HTTP_PROXY`、`HTTPS_PROXY`、`ALL_PROXY`、`NO_PROXY`（大小写两种都看）有没有设置，指向回环、局域网地址还是外部地址。只记分类，不在对话里回显完整值；Agent 自己的配置文件里有代理项的，同样只记分类。
3. **实际连接：**Linux 用 `ss -tnp | grep -i codex`，macOS 用 `lsof -nP -iTCP -a -c codex`，Windows 用 `Get-NetTCPConnection -OwningProcess (Get-Process codex).Id`（进程名以实际为准），看远端是回环端口、局域网地址还是公网。
4. **归类：**
   - **直连：**走物理网卡直接出去。
   - **本机代理端口：**指向 `127.0.0.1` 上的 Clash 端口。
   - **本机 TUN：**没有代理变量，流量被 TUN 接管。
   - **宿主或局域网代理：**指向宿主机或局域网里另一台机器的代理端口。VM 里最常见，客机 Agent 借宿主的 Clash 出去。
5. **对照第 2 节列出本次计划里哪几步会切断 Agent 链路。**一步都不会切断，就按原路线文档做；有会切断的，按第 3 节做。

## 2. 哪些步骤会切断 Agent 自己

| 步骤 | 为什么断 | 断的范围 |
| --- | --- | --- |
| 开启或关闭 TUN、切 TUN 栈、重启代理核心 | 路由在一瞬间切换，切换前建立的 TCP 连接被重置或卡死 | Agent 正在接收的回复中断，这一轮失败；Agent 重新发起请求后通常能恢复 |
| 切换节点、更新订阅 | 客户端会断开旧连接 | 同上 |
| 装 killswitch（[install-flclash-killswitch.sh](../assets/vm-killswitch/install-flclash-killswitch.sh)）、Windows 默认出站切成阻止、Mac 加载 PF 规则（[guardian-pf-killswitch.sh](../assets/mac-killswitch/guardian-pf-killswitch.sh)） | killswitch 出站只放行回环、TUN、DHCP 和节点真实 IP；局域网地址只放行**入站**的 SSH 和 ping，到局域网的新出站一律丢弃 | **宿主或局域网代理、直连：**一启用就断，而且一直断。**本机 TUN、本机代理端口：**不受影响 |
| 故障演练（`pkill FlClashCore`、`network_check.py run --failure-drill`）、重启演练 | 演练的目的就是让外网全断 | 全部断开，直到客户端或 [flclash-crash-heal.sh](../assets/remote-hardening/flclash-crash-heal.sh) 把 TUN 拉回来 |
| FlClash 崩溃后的路由黑洞 | `ip rule` 和策略路由表残留（见 [VM 防火墙](vm-guidance.md#4-客机防火墙fail-closed)） | 全部断开，清掉残留才恢复 |
| 内存不够 | Agent、代理客户端、浏览器同时跑在小内存机器上，被 OOM 结束 | Agent 进程本身没了 |

**保险丝会替你回滚，但 Agent 不知道发生了什么：**killswitch 和 Windows 防火墙的保险丝等 `confirm`。Agent 断线就执行不了 `confirm`，时限一到规则自动回滚，机器是安全的。可 Agent 重连后看到的是“没装上”，容易原样再装一次，又断一次，陷入循环。

## 3. 做法

1. **开 TUN 放在 B 档计划的最后一步。**开 TUN 前 Agent 先写好交接文件（第 4 步），告诉用户：“我这一轮会断，打开 TUN 后重新打开会话，说‘继续’就行。”TUN 开关由用户在客户端界面里点。
2. **装 killswitch 之前，把 Agent 链路切到本机 TUN。**killswitch 或默认出站阻止生效后，能出去的只有 TUN：去掉指向宿主或局域网代理的变量，重开 Agent，用一次正常请求确认 Agent 经 TUN 能工作，再往下做。**不在 killswitch 白名单里给宿主或局域网代理开口子**：那是一条绕开本机 TUN 的出站，TUN 掉了它照样能出去，fail-closed 就不成立了。
3. **会一直断开的步骤交给用户在终端执行。**装 killswitch、切默认出站为阻止、故障演练、重启演练，Agent 把完整命令写成一个脚本或一段可复制的命令，用户在这台机器的终端或虚拟机控制台里运行，`confirm` 也由用户在同一个终端执行。VM 路线也可以改由宿主机上的 Agent 通过 SSH 执行，这时就回到各路线文档的做法。故障演练用 `network_check.py run --failure-drill --evidence-output <新文件>`，用户在终端按提示停一次核心再打开，Agent 重连后读这个证据文件，交给 `egress_verifier.py` 判定（[整机统一出口](whole-machine-ipv4.md)）。
4. **断开之前写交接文件。**放在用户同意的私有位置（如 `~/.guardian-handoff/`，权限 0600），不进项目仓库，不写密钥、节点链接和真实代理地址。内容：当前在第几步、已经做了哪些改动、保险丝的截止时间、用户要执行的命令、重连后先跑哪几条核对命令。
5. **重连后先核对，再继续。**Codex 用 `codex resume` 接回原会话，或者新开会话后先读交接文件。先跑交接文件里的核对命令（killswitch 用 `install-flclash-killswitch.sh status`，Windows 用 `Get-NetFirewallProfile` 和 `Get-NetFirewallRule -DisplayName "guardian-*"`），确认规则在不在、保险丝有没有回滚、出口对不对。保险丝已经回滚的，先查清为什么没 `confirm`（多半是 Agent 链路被拦了），**不原样重试**。
6. **内存留足。**VM 和 VPS 上同时跑 Agent、代理客户端和浏览器时，按 [VPS 保活](vps-guidance.md#服务器保活按配置定内存预算防-oom-失联agent-操作前必做) 的方法先看可用内存，再决定能不能同时开浏览器；客机内存小的，先在宿主里给 VM 加内存。

## 4. 授权档位

Agent 和被改的网络在同一台机器上时，第 2 节里会切断 Agent 链路的步骤，按[分级授权](authorization-tiers.md)的“可能锁死或切断访问”算 **C 档**：到这一步暂停，确认单里写明“这一步会断开 Agent 自己”、交接文件在哪、由谁在哪个终端执行、重连后先核对什么。开 TUN 只是暂时断开，仍在 B 档计划里（第 3 节第 1 步）。
