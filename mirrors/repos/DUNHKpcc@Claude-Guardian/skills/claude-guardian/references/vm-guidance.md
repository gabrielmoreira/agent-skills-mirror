# VM 路线：客机系统、网卡、出口与防火墙

适用：用户已经选择 **VM 路线**（见 [R-VM](routes-and-platforms.md)）。选本机或 VPS 路线时不触发。Agent 可以部署（由宿主 Agent 通过 shell 或客机控制台执行本文的命令和脚本；Skill 没有内置自动部署程序，脚本还没在真实客机上实测）：创建 VM、装客机系统、配网卡、装 FlClash TUN、启用 killswitch、开客机 SSH 等，按[分级授权](authorization-tiers.md)执行；操作前展示改动、先打快照。**Agent 装在客机里时**，开 TUN、装 killswitch、故障演练都会切断 Agent 自己调用模型的连接，先按 [Agent 和被改的网络在同一台机器上](agent-on-target.md) 查清 Agent 链路再做。安装镜像的账号、付款、注册和登录由用户本人完成。

## 1. 客机系统怎么选

- **默认首选：Omarchy。**
- **宿主是 Mac：首选 macOS 客机。**
- 出口是 Linux（自建出口、机场）时，本机系统要和出口一致或接近，Windows 宿主用 Linux 客机就是为了这个，见[出口与本机环境一致](exit-consistency.md#2-tcp-指纹)。
- 创建前用 hypervisor 官方资料核实免费许可、架构兼容性和镜像来源，展示资源上限和磁盘增长；不捆绑付费许可，不克隆带登录状态的模板。

## 2. 创建前先选网卡

虚拟机创建前，网卡选 **LAN 独立网卡**（桥接到局域网，客机有自己的地址），**不选与宿主机一致的 shared NAT**。这样客机在局域网里有独立身份，出口和防火墙可以在客机里单独设置，不和宿主机的网络混在一起。

- 各 hypervisor 的叫法不同（常见是 Bridged 或桥接），按所用软件的官方说明选。
- 创建后记录客机网卡名、局域网网段和客机地址族，后面的防火墙要用。
- 已有 VM 用 NAT 的，不要覆盖现有磁盘，改网卡模式前先打快照并记录原值。

## 3. 出口 IP

直接复用[固定出口 IP 的来源](egress-ip-options.md)：纯净机场、自建梯（可搭配家宽出口）、家宽拼车三种来源，推荐 Max 优先自建，Pro 推荐机场；选 VPS 看 [VPS 推荐报告索引](../sources/vps-recommendations/INDEX.md)。客机里的客户端：Linux 客机（Omarchy）用 FlClash，macOS 客机用 Clash Verge 或 FlClash。出口由客机统一走同一个 IP，不要让客机进程再绕开它。

## 3a. Linux 客机的搭建顺序（Omarchy）

按下面顺序做；脚本由用户在客机里运行，或经[计划批准](authorization-tiers.md)后由 Agent 在获准的会话里运行，Agent 都先解释脚本、核对参数、帮读输出；先打快照。**第 2、3、4 步是 B 档**，可合成一张计划批准一次；**第 5 步装 killswitch 是 C 档**（默认出站丢弃，可能锁死），到这一步暂停，用户当场确认并在保险丝时限内 `confirm`：

1. **创建 VM：**网卡选 LAN 独立网卡（第 2 节），记下客机网卡名（`ip link`）和局域网网段。
2. **开启客机 SSH：**[enable-guest-ssh.sh](../assets/vm-killswitch/enable-guest-ssh.sh)，全新 Omarchy 默认没有 sshd，脚本先 `pacman -S --needed openssh` 再开启 sshd；ufw 已启用时只放行你设置的 `SSH_SRC`（管理机在局域网里的地址或网段）到 22 端口。原脚本按 shared NAT 写，已改为 LAN 独立网卡的做法。
3. **安装 FlClash 和 TUN 助手：**[install-flclash-tun.sh](../assets/vm-killswitch/install-flclash-tun.sh)，用 pacman 装依赖，下载固定版本的 FlClash 并核对 SHA256（失败即中止），以 root 装到 `/opt/FlClash`，安装并启用 TUN 特权助手。版本和架构可用 `FLCLASH_VERSION`、`ARCH` 覆盖，默认 0.9.1 和 arm64，升级前到 Release 页面核对。装 0.9.2 等非 0.9.1 版本时，脚本会自动加 helper 的 systemd drop-in（`FLCLASH_HELPER_OWNER_UID/GID`、`RuntimeDirectory=flclash`），缺这两项 helper 起不来；托盘库 `libayatana-indicator` 缺失会导致 GUI 起不来，脚本已用 pacman 装好。`/dev/net/tun` 节点存在不等于 tun 模块已加载（`lsmod | grep tun` 为空即未加载，GUI 开 TUN 会报错），脚本会 `modprobe tun` 并写入 `/etc/modules-load.d/tun.conf`，否则重启后复发。
   - **用 AppImage 安装时：**解包出的文件属主是执行用户，而 helper 要求 root 属主、组和其他用户不可写，否则 GUI 报 `couldn't authorized`。修法：`sudo chown -R root:root /opt/FlClash && sudo chmod -R go-w /opt/FlClash`，再重跑 `sudo /opt/FlClash/FlClashHelperService install`（官方 install 会重写 helper 单元，自带 owner UID/GID），然后 `systemctl restart flclash-helper`。deb 安装没有这个问题，本脚本走 deb。
   - **通过 SSH 拉起 GUI 时用 `setsid`：**裸 `&` 的后台进程会随 SSH 会话退出被杀，要 `setsid` 加 `</dev/null` 脱离会话，命令见[进阶路线第 4 节](advanced-route.md#4-崩溃自愈)。
4. **导入节点并开启 TUN：**打开 FlClash，导入用户自己的节点配置（来源见第 3 节），开启 TUN，确认出口 IP 是预期的那个（用 [S07 清单](../sources/S07-vps-script-catalog.md)里的检测）。**同时确认 GLOBAL 组和实际使用的策略组都选中了目标节点，并用 `curl` 实测出口 IP**：GLOBAL 是 mihomo 内置组，永远包含 DIRECT 和 REJECT，没选中时全局模式和规则模式的出口可能不一样，甚至直连。
5. **再装防火墙：**TUN 通了以后再装第 4 节的 killswitch，顺序反了会把自己锁在外网之外。**TUN 开好立刻装**：TUN 没开时 core 起来了也是直连，从装好 FlClash 到装上 killswitch 之间是真实 IP 的泄漏窗口，这段时间不做任何多余的网络操作。脚本装完会 start 定时刷新的 timer 并打印下次触发时间；自己手动部署时注意 timer 只 enable 不 start 是 enabled-but-inactive，要到开机才生效，用 `systemctl list-timers` 确认。killswitch 用自己的 `flclash-killswitch.service` 开机加载规则，`nftables.service` 保持 disabled 是正常的。

### macOS 客机（Mac 宿主首选）

macOS 客机不需要这三个脚本，全部用提示词，做法和本机路线的 Mac 一致：

1. **开客机 SSH：**在客机“系统设置 → 通用 → 共享”里打开“远程登录”，只允许自己的管理账户；这是图形界面操作，由用户自己点。
2. **Clash 客户端：**Clash Verge 按[本机路线的 Mac 提示词](local-firewall-prompts.md#mac)安装、导入节点、开 TUN（服务模式）、核对 DNS 和出口。
3. **防火墙：**用 PF 脚本 [guardian-pf-killswitch.sh](../assets/mac-killswitch/guardian-pf-killswitch.sh)，做法、故障演练和回滚见[本机路线的 Mac 一节](local-firewall-prompts.md#mac)；不用 LuLu（按进程拦，会拦掉正常 TUN 流量）。
4. 顺序同样是先让 TUN 跑通再加防火墙，最后做故障演练。

## 4. 客机防火墙（fail-closed）

参考脚本：[install-flclash-killswitch.sh](../assets/vm-killswitch/install-flclash-killswitch.sh)（脱敏版，适用 Linux 客机 + FlClash TUN，基于 nftables）。

**它做什么：**客机的一切出站流量只能 1）走 FlClash 的 TUN 出去，或 2）发往 profile 里各节点真实服务端的 IP 和端口；DHCP 和局域网内的 SSH、ping 放行，其余一律丢弃。节点 IP 解析时过滤 fake-ip（198.18.0.0/15），解析失败就经隧道 DoH 取真实 IP。TUN 掉线或进程被杀时，外网全断，不会直连出去。IPv6 除 DHCPv6 外不放行，与本项目的 IPv4_ONLY 一致。

**前置条件：**
- 客机里 FlClash 已运行并有 TUN，profile 在 `~/.local/share/com.follow.clash/profiles`。
- 用 `ip link` 确认网卡名，脚本默认 `enp0s1`，不同则设 `NIC=`；TUN 名默认 `FlClash`，不同设 `TUN=`。
- 必须设置 `LAN_NET`（客机局域网网段，如 `192.168.1.0/24`）；可选 `SSH_PORT`、`EXPECTED_EXIT_IP`（固定出口 IP，用于 test 比对）。
- 已安装 nftables；刷新服务由普通用户调用 sudo，需要该用户有免密 sudo，否则定时刷新会失败。

**用法（Agent 在客机里运行，需要用户给出客机访问方式；启用 killswitch 属于 C 档，当场确认。务必有虚拟机控制台这个独立入口，不要只靠 SSH）：**

```
sudo LAN_NET=<局域网网段> bash install-flclash-killswitch.sh install
bash install-flclash-killswitch.sh confirm      # 180 秒内确认，否则自动回滚
EXPECTED_EXIT_IP=<固定出口IP> bash install-flclash-killswitch.sh test
bash install-flclash-killswitch.sh status
bash install-flclash-killswitch.sh refresh      # 节点 IP 变了手动刷新（每小时也会自动刷新）
bash install-flclash-killswitch.sh uninstall    # 卸载并删除规则
```

**白名单必须覆盖管理通道自身的出站：**如果机器靠反向 SSH 隧道等通道被管理，脚本要把通道的目标 IP 和端口放进白名单，否则一启用就自己把管理通道锁死。脚本读取 `TUNNEL_UNIT` 指向的 systemd unit（默认 `/etc/systemd/system/guardian-reverse-tunnel.service`，文件不存在就忽略），从 `ExecStart` 解析 `user@IP` 和 `-p 端口` 自动放行；解析不出来会打印 WARN。进阶路线见 [advanced-route.md](advanced-route.md)。

**两个实战坑：**
- 规则链的 priority 用 10。priority 太靠前（如 raw -300）时 conntrack 还没建立，`ct state established` 不可靠，会把已有的 SSH 连接锁死。
- fake-ip 段 `198.18.0.0/15` 永远不能进白名单。订阅里节点是域名时，系统解析可能拿到 fake-ip，脚本会改走 DoH 取真实 IP。

**FlClash 崩溃后的路由黑洞：**`FlClashCore` 死后 TUN 消失，但 FlClash 写入的 `ip rule` 和策略路由表（如 2022）会残留，公网被黑洞，连白名单里的出站也出不去。排查时先看 `ip rule show` 和残留表；必要时用 [flclash-crash-heal.sh](../assets/remote-hardening/flclash-crash-heal.sh) 清残留并自动拉起 FlClash（systemd 的两个坑：oneshot 要 `KillMode=process`，否则会杀掉脚本拉起的 GUI；服务级 `Environment` 要写全 `DISPLAY`、`WAYLAND_DISPLAY`、`XDG_RUNTIME_DIR`、`DBUS_SESSION_BUS_ADDRESS`）。这个脚本对没有反向隧道的客机同样适用。

**IPv6：**规则表是 `inet` 家族，OUTPUT 和 INPUT 都是 policy drop，所以 IPv6 除 DHCPv6、回环和 TUN 外不放行，不需要另写 ip6 规则。网络环境一变（换桥接、换宿主）就重测：`ip -6 addr show scope global` 看有没有全局 v6 地址，有就 `curl -6 --max-time 8 https://ipinfo.io`，应当失败。

**时区、语言与 NTP：**出口对齐的是出口 IP 的地理位置，不是 VPS 的系统时钟（VPS 多是 UTC）：出口在美东就用 `America/New_York` 和 `en_US.UTF-8`，与浏览器 JS 时区一致。killswitch 默认拦截 NTP（UDP 123 不在白名单），`timedatectl` 会显示 unsynchronized；要么把 NTP 服务器加进白名单，要么接受虚拟机 RTC 的走时。

**保险丝与验收：**应用规则后有 180 秒保险丝，没有执行 `confirm` 就自动回滚，避免锁死。装好后手动验收：出口 IP 是固定出口；浏览器打开 browserleaks.com/webrtc 和 dnsleaktest.com（WebRTC 也可用包内的[本地探测页](../assets/webrtc-probe.html)），确认没有真实 IP 和真实 DNS；`pkill FlClashCore` 后确认 curl 和 DNS 全部失败，重启 FlClash 后恢复。最后由用户在 VM 里的浏览器打开 https://ip.net.coffee/claude/ 做浏览器环境验收，除语言外必须全绿（时区要和出口一致）（[做法](whole-machine-ipv4.md#browser-acceptance)）。

**macOS 客机：**用 [guardian-pf-killswitch.sh](../assets/mac-killswitch/guardian-pf-killswitch.sh)，同样要求 TUN 掉线时不直连（未在真机验证）。

Agent 的角色：解释脚本做什么、检查前置条件、核对参数，帮用户读 test 和 status 的输出；运行和卸载都由用户或经逐动作授权后进行。

## 5. 后续流程：与本机路线一致

客机环境就绪后，按本机路线的顺序继续：

1. **接触前门禁**：PC0，不接触 Claude；登录、支付逐项批准（见 [V3](routes-and-platforms.md)）。
2. **注册与养号**：Agent 先读[账号注册与使用节奏（A0）](account-onboarding.md)，邮箱、升级间隔、额度、并发、接码、KYC 都按 A0 给用户讲。
3. **订阅与支付**：按[支付说明](accounts-and-payments.md)，第一项参考 S02；选 Apple 或 Google 内购时，手机端先过[手机端防封要点](mobile-guidance.md)。
4. **日常**：宿主网络 → 启动 VM → 客机时钟与网络状态 → 选定客户端；宿主换网、VM 暂停恢复、更新后重测出口和防火墙。

## 边界

不承诺免封。快照不能恢复解封。脚本是 Linux 客机的参考实现，运行前先打快照；共享目录、剪贴板、凭据按 [V1](routes-and-platforms.md) 的边界处理，不默认共享整个用户目录。
