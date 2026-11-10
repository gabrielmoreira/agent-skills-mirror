# VPS 路线：开发机（环境一致）

适用：用户已经选择 **VPS 路线**（见 [R-VPS](routes-and-platforms.md)）。VPS 路线是**开发机**：Claude Code 跑在 VPS 上，本机只用 VS Code Remote-SSH 连过去。VPS 当代理中转（自建梯）不属于本路线，那是**本机路线选 IP 出口**时的选项，见[固定出口 IP 的来源](egress-ip-options.md)，不要混为一谈。

用户买好服务器并给出 SSH 登录方式后，**Agent 可以部署**（由宿主 Agent 通过 shell／SSH 执行本文的命令和脚本；Skill 没有内置自动部署程序，脚本还没在真实服务器上实测）：装系统包、建用户、配 SSH 密钥登录、装 Xvfb + noVNC + Chrome、tmux、swap、`vps-guard`、BBR 和线路优化等，按[分级授权](authorization-tiers.md)执行（B 档整个计划批准一次，锁死风险项当场确认）。**Agent 操作服务器前，先按服务器配置做[服务器保活](#vps-liveness)**，不能因为爆内存让 Agent 和用户连不上 VPS。买服务器、付款、注册、登录 Claude 和 OAuth 由用户本人完成。详细命令见 [S08：VPS Claude 教程（11 页）](../sources/S08-vps-claude-tutorial.pdf)，回答 VPS 路线问题时必附。

## 核心：环境一致

VPS 路线的目的是让**注册、登录、养号、订阅、OAuth、日常使用全部发生在同一个环境**：同一个 IP、同一套系统、语言、时区、地区。所以：

- Claude 的注册、登录、订阅和 OAuth 都在 **VPS 上的远程桌面浏览器**里完成，那个浏览器的互联网出口就是 VPS。
- **不要把本机浏览器和 VPS 混用。**本机只是 SSH、VS Code 和远程桌面的显示端，不在本机浏览器里登录 Claude。
- 好处（S08）：使用环境稳定，不用担心 IP 乱跳，也不用管系统、语言、时区、地区的差异，KYC 跳出的概率低。

## 服务器怎么选

| 项目 | 建议 |
| --- | --- |
| 系统 | **首选 Ubuntu 24.04**（系统完整度高，新手友好，有图形化界面，生态友好） |
| 架构 | 首选 x86_64（VS Code 兼容性最好） |
| 规格 | 2C 到 4C；内存 2G 是 VS Code 最低，4G 用着舒服，大型项目 8G 到 16G；公网 IPv4 |
| 线路 | DMIT（美西 premium）、搬瓦工、AWS、Vultr 等；CN2 GIA 带三网优化的线路（后期走图形化界面更稳定） |
| 区域 | 选你正常使用、且 Anthropic 支持的地区 |

选型参考[VPS 推荐报告索引](../sources/vps-recommendations/INDEX.md)（业务、性价比、高端家宽三类），回答时点名具体报告并附链接。创建后用 `bash <(curl -sL IP.Check.Place)` 检查 IP（见 [S07 清单](../sources/S07-vps-script-catalog.md)）；如果随机到的 IP 不好，能找客服换就换。好的机房 IP 不用担心，最后都可以套静态 ISP 出口。

## 怎么读 IP 检测报告（S08 第 3 页）

创建服务器后运行 `bash <(curl -sL IP.Check.Place)`（Agent 在授权的 SSH 会话里运行，或用户自己运行，见 [S07 清单](../sources/S07-vps-script-catalog.md)）。Agent 按报告的六部分帮用户看：

1. **基础信息：**时区和 IP 类型（原生 IP 还是广播 IP）。
2. **IP 类型属性：**多个数据库给出的使用类型和公司类型。机房 IP 显示“机房”是正常的。
3. **风险评分：**IP2Location、Scamalytics、ipapi、AbuseIPDB 等的风险等级，低风险为好。
4. **风险因子：**代理、Tor、VPN、滥用、机器人是否为“否”；服务器为“是”对机房 IP 是正常的。
5. **流媒体及 AI 服务解锁：**各服务的地区和状态，ChatGPT、Reddit 等是否解锁。
6. **邮局连通性及黑名单：**25 端口被阻止很常见；看 IP 黑名单数据库里“已标记”和“黑名单”的数量。

S08 的结论是：像示例里这样的机房 IP 算好的，直接用没问题，想套家宽出口也可以；如果随机到的 IP 不好，能找客服换就换。这只描述当时这个 IP 的检测结果，不推导免封概率。

## 出口：两种情况

1. **VPS 自己的 IP 就是出口。**最简单，浏览器、Claude Code 都从 VPS 出去。
2. **套一层家宽出口。**两台机器分工：A 是优化线路 VPS（连接稳定、跑浏览器和开发），B 是家宽出口 VPS（网站看到的 IP）。**浏览器运行在哪台机器，就在哪台机器上给浏览器配出站代理**（例如在 A 上用 SSH 动态转发建 SOCKS5 入口指向 B，再在 A 的浏览器里设置）；只转发桌面入口不等于改了浏览器的出口。详细做法见 [VPS 线路优化与家宽中转教程（R02）](../sources/R02-vps-line-optimization.md)，家宽 VPS 选型见推荐报告里的“高端家宽”类。

不管哪种，登录后都要在远程桌面浏览器里确认出口 IP 是预期的那个（WebRTC 不泄漏真实 IP 可用包内的[本地探测页](../assets/webrtc-probe.html)），再由用户在远程桌面浏览器里打开 https://ip.net.coffee/claude/ 做浏览器环境验收，除语言外必须全绿（时区要和出口一致）（[做法](whole-machine-ipv4.md#browser-acceptance)），然后再继续注册和订阅。

## 线路优化

连接慢、晚高峰断流、画面卡、出口不对，或想加中转、调 BBR 时，按 [line-optimization.md](line-optimization.md)：Agent 先只读诊断，再一次只提一项改动，用户批准后执行并验证，可回滚。依据 [R02](../sources/R02-vps-line-optimization.md)，回答时必附。

## 创建与连接

1. **SSH 密钥：**创建服务器时添加自己的 SSH 公钥，或下载服务商生成的密钥；本机私钥不离开本机。
2. **SSH 安全（S08 的几种方案）：**公网加 SSH key（最简单）；Tailscale 加 SSH key（适合个人用户，注意备用出口）；改掉 22 端口；跳板机（门槛最高，适合商业化）。选哪种由用户决定，改动前先确认有云控制台的独立救援入口。
3. **日常开发用户：**不用 root，新建 `dev` 用户并加入 sudo，把授权密钥复制过去，再用 `dev` 重新连接；有条件写 `~/.ssh/config`。

<a id="vps-liveness"></a>
## 服务器保活：按配置定内存预算，防 OOM 失联（Agent 操作前必做）

Agent 通过 SSH 操作 VPS 时，第一优先级是保住控制通道。Agent 直接跑在这台 VPS 上、又要在上面开 TUN 或装防火墙时，另按 [Agent 和被改的网络在同一台机器上](agent-on-target.md) 做。内存耗尽（OOM）时，内核 OOM killer 可能杀掉 sshd、tmux 或 Agent 会话；还没触发 OOM 时也可能先陷入 swap 抖动（thrashing），系统失去响应，Agent 和用户都连不上 VPS。所以每次部署、编译、装依赖或开远程浏览器之前，先按服务器规格做资源基线和保活配置，再动手。

1. **资源基线（A 档，只读）：**`nproc`、`free -h`、`swapon --show`、`df -h /`、`cat /proc/pressure/memory`（PSI 内存压力）、`systemctl is-active earlyoom`，以及 `journalctl -k -b | grep -iE "out of memory|oom-kill"` 查本次开机有没有 OOM 记录。用 `free -h` 的 available 一列定内存预算：**至少给系统、sshd 和 tmux 留 512MB**，剩下的才是任务能用的。
2. **Swap 兜底：**没有 swap 就建 swapfile，内存 2G 及以下建 2G，4G 建 2 到 4G，8G 建 4G；先确认磁盘剩余空间够。`sudo fallocate -l 4G /swapfile && sudo chmod 600 /swapfile && sudo mkswap /swapfile && sudo swapon /swapfile`，再在 `/etc/fstab` 加 `/swapfile none swap sw 0 0` 持久化；`/etc/sysctl.d/99-guardian-swap.conf` 写 `vm.swappiness=10`，`sudo sysctl --system` 生效。OpenVZ、LXC 这类容器型 VPS 通常不能开 swap，就只靠内存预算，并告诉用户。
3. **用户态 OOM 守护（earlyoom）：**`sudo apt install earlyoom`，在 `/etc/default/earlyoom` 写 `EARLYOOM_ARGS="-m 10 -s 10 -r 3600 --avoid ^(sshd|systemd|tmux) --prefer ^(chrome|Xvfb|x11vnc)$"`（正则里不加引号、不留空格：systemd 读这个文件时不处理引号，并按空格拆参数），`sudo systemctl enable --now earlyoom`。可用内存和 swap 都低于 10% 时，它先于内核 OOM killer 动手，优先结束临时远程浏览器，避开 sshd 和 tmux。**不要给 sshd 设 `OOMScoreAdjust=-1000`**：子会话会继承这个值，失控的任务也杀不掉，反而更容易把整机拖死。
4. **重任务加 cgroup 内存上限：**`npm install`、编译、`docker build`、批量测试这类峰值高的任务，用 `systemd-run --user --scope -p MemoryMax=<预算> -p MemorySwapMax=1G <命令>` 跑，超限只结束这一个任务，不拖垮整机。编译并行度按内存定：2G 机器 `make -j1`，4G 用 `-j2`，不直接用 `-j$(nproc)`。
5. **控制常驻进程和并发：**远程浏览器（Chrome、Xvfb、x11vnc、noVNC）用完就关（见下文）；2G 机器不要让远程浏览器和编译同时跑；Claude Code 的并行子代理也会叠加内存占用，内存小就减少并行。
6. **控制通道保活：**长任务一律放在 `tmux` 里跑，SSH 断开任务也不中断；本机 `~/.ssh/config` 给这台 Host 加 `ServerAliveInterval 30`、`ServerAliveCountMax 3`，及时发现断线。
7. **失联恢复预案：**动手前在计划里写好服务商控制台的带外入口（VNC 或串口控制台）和实例重启方法。真失联了就从控制台登录或重启，恢复后用 `journalctl -k -b -1 | grep -iE "out of memory|oom-kill"` 查上次开机被杀的进程，调小预算再继续，不原样重试。
8. **复验：**`swapon --show`、`systemctl is-active earlyoom`、`free -h` 读回；改完的配置写进回执，回滚是 `swapoff` 并删 fstab 那一行、`systemctl disable --now earlyoom`。

分档：第 1 步只读是 A 档；建 swap、改 sysctl、装 earlyoom 是 B 档，和部署计划一起批准一次。

## 开发环境与 Claude Code

装 Node、npm、git；习惯终端的可以装 nvim、mosh、tmux。用官方安装方式装 Claude Code（`curl -fsSL https://claude.ai/install.sh | bash`），`claude --version` 验证。本机装 VS Code 和 Remote-SSH 扩展，在 `~/.ssh/config` 里配 Host，之后项目直接放在服务器的 `~/workspace`。

## 临时远程浏览器（远程桌面）

浏览器**只在这些时候启动**：Claude 注册或登录、养号、购买订阅、OAuth、重新授权。不需要装完整 Ubuntu Desktop。

- S08 的做法：Xvfb 虚拟显示 + Openbox + x11vnc + noVNC，浏览器直接打开，无需安装客户端；也可以用 TigerVNC / Xvnc 或 Xpra，按自己的需求选。
- 浏览器用 Google Chrome，独立的用户数据目录。内存不够先建 swap，实在不行再升级配置；正常只有 Claude 单个标签页，约 500MB 上下。
- **5900 和 6080 绝不直接开放到公网。**x11vnc 只监听本地，从本机用 SSH 本地转发（`ssh -L 6080:127.0.0.1:6080 …`）后，在本机浏览器打开 `http://127.0.0.1:6080/vnc.html`。看到的 Chrome 实际运行在 VPS 上，所以出口是 VPS。不用公网无密码 VNC。
- **用完就关**：OAuth 完成后停掉 Chrome、noVNC、x11vnc、Xvfb，日常不占约 0.6 到 1.2GB 内存；需要重新登录时再启动。关闭命令精确匹配进程，不用宽泛的结束进程命令。

## 注册、养号、订阅、OAuth（与本机路线一致，但全在 VPS 浏览器里）

1. **注册与养号：**Agent 先读[账号注册与使用节奏（A0）](account-onboarding.md)，邮箱、升级间隔、额度、并发、接码、KYC 都按 A0 给用户讲；VPS 路线另有一条：**OAuth 之前必须先从 Free 号养号**。
2. **订阅：**在 VPS 的 Chrome 里打开 claude.ai，用自己的真实账号和支付资料，Settings → Billing 选套餐。支付方式按[支付说明](accounts-and-payments.md)，第一项参考 S02。选 Apple 或 Google 内购要在手机上完成，手机端先过[手机端防封要点](mobile-guidance.md)，并注意手机的出口也要和 VPS 一致。
3. **OAuth：**VPS 终端里运行 `claude`，需要登录时执行 `/login`，把给出的授权 URL 复制到 **VPS Chrome**，登录并授权，回到终端。

## 防火墙

- **VPS 自己的 IP 是出口：**用 [vps-guard.sh](../assets/vps-firewall/vps-guard.sh)，参考 VM 的脚本结构：nftables，入站默认丢弃，只放行回环、已建立连接、来自管理来源（`ADMIN_NET`）的 SSH 和 ping、云 DHCP、IPv6 邻居发现；出站不限制。应用后有 **180 秒保险丝**，没有 `confirm` 就自动回滚。
- **套家宽、VPS 上也跑 FlClash TUN：**直接用 [VM 的 install-flclash-killswitch.sh](../assets/vm-killswitch/install-flclash-killswitch.sh)，把 `LAN_NET` 设成你的管理来源网段，`NIC` 设成 VPS 的网卡，出站只走 TUN 或节点真实 IP 和端口，fail-closed。
- 授权档位（见[分级授权](authorization-tiers.md)）：`render` 预演是 A 档；**启用防火墙是 C 档**（入站丢弃，可能锁死 SSH），用户当场确认，并在 180 秒保险丝内在另一个会话 `confirm`。
- **用 mosh 要加 `MOSH=1`：**mosh 握手走 SSH，会话走 UDP 60000–61000；`vps-guard` 默认不放行这段 UDP，启用后 mosh 能握手但会话建不起来。安装时加 `MOSH=1`（例如 `sudo ADMIN_NET=203.0.113.7/32 MOSH=1 vps-guard.sh install`），只对 `ADMIN_NET` 放行这段 UDP；端口段可用 `MOSH_PORTS=60000-61000` 改，只接受 1024–65535。放行范围只到 `ADMIN_NET`，所以 mosh 漫游到管理来源以外的 IP 会断，管理来源用 Tailscale 网段就不受影响。规则是 install 时写进去的，之后改开关要重新 install 并 confirm。
- 用法与前置：`ADMIN_NET` 必填（固定公网 IP 加 /32，或 Tailscale 网段 100.64.0.0/10）；先 `render` 看规则；**运行前在云控制台确认有独立救援入口，先打快照，在另一个 SSH 会话里确认**，不要只靠一个会话。云厂商安全组和系统防火墙是两层，分别核对。
- **套家宽、VPS 上跑 TUN 时，白名单要覆盖管理通道自身的出站**（SSH 入站走 `ADMIN_NET`，反向隧道等出站通道走 `TUNNEL_UNIT` 自动放行），详见 [vm-guidance.md 第 4 节](vm-guidance.md#4-客机防火墙fail-closed)。
- 脚本的规则语法经 `nft -c` 在隔离环境检查过，应用和保险丝流程没有在真实服务器上实测，首次使用按上面的顺序小心进行。

## 作为隧道中转的 VPS（进阶路线）

VPS 同时当出口节点和反向隧道落点时，按这个顺序初始化 sshd：

1. `~/.ssh` 设 700、`authorized_keys` 设 600；管理端公钥和隧道公钥用 `grep -qF` 判断后再追加，重复运行不出重复行。
2. 改 sshd 用 drop-in，不碰主配置：`/etc/ssh/sshd_config.d/99-tunnel.conf` 写 `PubkeyAuthentication yes`、`ClientAliveInterval 15`、`ClientAliveCountMax 2`。新版 Ubuntu 的 `PubkeyAuthentication` 可能没开；`ClientAlive` 让僵尸连接 30 秒内回收，否则旧连接占着回环端口，新隧道绑不上。主配置里没有 `Include /etc/ssh/sshd_config.d/*.conf` 时，先备份再加到第一行。
3. **`sshd -t` 先验证再 `systemctl restart ssh`**，改完从另一个会话验证能登录，原会话不要先关。
4. 防火墙分三层看：`ufw status`、`iptables -S INPUT`，以及云厂商安全组，放行 sshd 端口。

**`authorized_keys` 的 options 要逐台实测。**OpenSSH 8.9 上，带字面反斜杠和引号的 `restrict,permitlisten=\"127.0.0.1:2222\"` 会静默拒绝 `tcpip-forward`，无引号的 `restrict,permitlisten=127.0.0.1:2222` 可用；Ubuntu 24.04（sshd 9.6p1）上，`permitlisten` 本身就让整行失效（无引号也一样，升级 openssh-server 也没用），表现是隧道 `activating` 循环、服务端日志只有 `[preauth]` 断开。实测不通就用无 options 的行，靠架构兜底：落点只绑回环、隧道密钥只放在目标机、`ClientAlive` 清僵尸。排查方法见 [advanced-route.md 第 3 节](advanced-route.md#3-隧道专属的坑)。

## 日常

打开 VS Code → Remote-SSH 到工作区 → 打开 `~/workspace/项目` → 终端里 `tmux new -A -s claude` → `claude`。SSH 断开后任务继续，重连后 `tmux attach -t claude`。只有 Claude 登录失效、订阅管理或重新 OAuth 时才启动远程浏览器。定期看 `free -h`、`df -h`；swap、内存预算和 OOM 守护按[服务器保活](#vps-liveness)。

## 边界

不承诺免封。Agent 在授权的 SSH 会话里部署，每项记原值、给回滚；启用 `vps-guard`、改 SSH 等锁死风险项按 C 档当场确认，操作前先打快照并确认有独立救援入口。快照不能恢复解封。
