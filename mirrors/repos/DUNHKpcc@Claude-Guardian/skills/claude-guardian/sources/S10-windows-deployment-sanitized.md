# Windows 本机路线 + Killswitch 部署经验记录（完整脱敏版）

> **S10 · 所有者提供，2026-11-03 授权全文脱敏收录。**保留原稿全部章节、代码示例、部署结果、待办和事故复盘；新增的说明均标为“编者注”。主机、用户和路径使用别名，真实地址改为占位符或示例地址，密码为 `[REDACTED_SECRET]`，出口短哈希改为符号标签；原始文件不随包发布。署名：项目所有者 DUNHKPcc（原稿提供者）。
>
> **阅读口径：**这是 2026-11-02～11-03 的用户实战记录，状态勾选是原作者当时的报告，本次入库没有重新连接设备或独立复验。命令是阅读示例，不是执行授权；执行仍按 [分级授权](../references/authorization-tiers.md)，组织设备或宿主拒绝时不得绕过。不同机器和版本按实际环境核对。

> **编者注（2026-11-04，所有者明确归类）：**OpenSSH、Tailscale、内网穿透、跨机传文件和远程故障演练属于[本机路线的高级扩展](../references/local-advanced-route.md)，不是 Skill 核心流程或本机前置。目标机已有 Agent 时，直接从[第二节本机检查](#windows-baseline)和[本机指引](../references/local-firewall-prompts.md)开始；仅在用户明确需要异机协助时才读远程部分。原案例全文和顺序保留，不代表部署时必须照第一节先建立远程接入。

## 按问题阅读

| 主题 | 原稿位置 |
| --- | --- |
| TUN、DNS、IPv6 与出口检查 | [第二节](#windows-baseline) |
| 防火墙宽放行、DNS 缓存（远程演练仅高级扩展） | [第三节](#windows-firewall) |
| 桌面开关初版与第一台机器待办 | [第四节](#desktop-switch-initial)、[第六节](#windows-a-status) |
| PowerShell 编码、别名、远程脚本、哈希口径 | [第五节](#powershell-tools)、[第十节](#network-evidence) |
| 3x-ui、REALITY、Hysteria2、证书和订阅 | [第七节](#vps-protocols) |
| UDP、配置覆盖、singleton、GUI 会话、TUN 名称 | [第八节](#verge-runtime) |
| TUN 重建、防火墙接口、核心 DNS 的相互影响 | [第九节](#tun-firewall-lifecycle) |
| 工具判定与第二台机器待办 | [第十节](#network-evidence)、[第十一节](#windows-b-status) |
| 桌面启动事故、方法学复盘、完整快捷方式配方与验收 | [晚间复盘](#desktop-launcher) |
| 本机高级扩展：Tailscale、Windows 管理员 SSH 公钥、跨机协助 | [高级扩展入口](../references/local-advanced-route.md)、[第一节](#windows-ssh) |

---

> 2026-11-02 ~ 11-03 · 基于 Claude-Guardian skill（DUNHKpcc/Claude-Guardian）实战
> 目标机①：windows-a（Win10 / USER_A）· 判定 `established` 8/8 层
> 目标机②：windows-b（Win11 / USER_B）+ 自建 VPS（3x-ui + Hysteria2）· 第一~六节为①，第七节起为②与 VPS

---

<a id="windows-ssh"></a>
## 一、远程接入（Tailscale + SSH）

1. **Mac 端 Tailscale 曾是 stopped**，`tailscale status` 排查第一步先看本机。
2. **两台设备必须在同一个 tailnet**。Windows 之前登录了另一个账号，IP `100.64.0.10` 不在主 tailnet 里；重新登录主账号后分到 `100.64.0.11`（旧 IP 作废）。
3. **Windows 管理员账户的 SSH 公钥只认一个文件**：
   `C:\ProgramData\ssh\administrators_authorized_keys`
   （sshd_config 里 `Match Group administrators` 覆盖了用户级 `~/.ssh/authorized_keys`）
   - 权限必须收紧：`icacls <file> /inheritance:r /grant "Administrators:F" /grant "SYSTEM:F"`
   - 权限不对或文件为空 = 一直 Permission denied，先查这两处再怀疑别的
4. 引导方式：先 scp 公钥到用户目录，再远程把它写进 administrators_authorized_keys（避免手工粘贴长公钥出错）。

<a id="windows-baseline"></a>
## 二、Clash Verge 配置检查清单（验收通过基线）

| 项 | 正确值 | 检查方法 |
|---|---|---|
| TUN | `enable: true` + `strict-route: true` + `auto-route: true` | 运行时配置 `%APPDATA%\io.github.clash-verge-rev.clash-verge-rev\clash-verge.yaml` |
| 核心 IPv6 | `ipv6: false` | 同上 |
| DNS | `enable: true`、`ipv6: false`、`enhanced-mode: fake-ip`、`dns-hijack: any:53` | 同上；实测解析返回 198.18.x.x 即劫持生效 |
| 规则兜底 | 末尾 `MATCH,Proxy` | 同上 |
| 网卡 IPv6 | 物理网卡 `ms_tcpip6` 绑定 = False | `Get-NetAdapterBinding -ComponentID ms_tcpip6` |
| 出口一致性 | curl×2 + .NET 三路一致 | `curl.exe -4 https://api.ipify.org` + `Invoke-WebRequest` |

出口地理核实：`https://ipwho.is/<ip>`（免费、https、返回 IANA 时区）。本次出口：美国 Verizon AS701（纽约），时区随之改 `Eastern Standard Time`。

<a id="windows-firewall"></a>
## 三、Killswitch（Windows 防火墙 fail-closed）

### 部署了什么
- **默认出站 Block**：Domain / Private / Public 三档
- **guardian-* 放行规则**：核心程序（程序级）、TUN 网卡、回环（用接口不用 ::1）、DHCP、Tailscale（程序级 UDP/TCP + 接口级，保住远程通道）
- **guardian-block-dns-\***：物理网卡 53 端口显式 Block（UDP+TCP × 以太网/WLAN）

### 三个坑（重点）

1. **加速器宽放行规则架空一切**：`QeeYouGateWay_OutBound_Rule`、`AccGateWay_OutBound_Rule`
   （program=Any 全放行，装过游戏加速器基本都有）。默认出站 Block 后 TCP 直连照样通。
   排查命令：`Get-NetFirewallRule -Direction Outbound -Action Allow -Enabled True` 逐条看 program=Any 的。
2. **svchost DNS 走"本网段"规则直连路由器**：内建"网络发现/设备平台"类规则作用域 LocalSubnet，
   系统 DNS（<路由器DNS>）在本网段内，停了"核心网络-DNS"还能解析。
   解法：物理网卡 53 端口显式 Block（WFP 里 **Block 优先于 Allow**，与具体性无关）。
3. **DNS 缓存假象**：演练时"DNS 还能解析"其实全是 Dnscache 正缓存。
   演练前必须 `Clear-DnsClientCache`，否则误判 fail-open。

### 演练方法论（远程机器）
- 停核心瞬间 TUN 适配器消失 → Tailscale 网络变更 → SSH 会话被杀、远端脚本连带死。
- **正确做法：把演练脚本挂成 SYSTEM 计划任务独立运行**（`schtasks /Run`），
  脚本自己完成 停服务→探测→恢复，SSH 断了也无所谓，回头取结果文件。
- 注意：SYSTEM 任务里 `$env:USERPROFILE` 是 `C:\Windows\System32\config\systemprofile`，
  结果文件别往 USER_A 的 profile 找。
- SYSTEM 计划任务能跑 powershell 没问题；失败先看 LastTaskResult 和脚本文件是否真的存在。

### 回滚
```powershell
Set-NetFirewallProfile -Profile Domain,Private,Public -DefaultOutboundAction Allow
Get-NetFirewallRule -DisplayName "guardian-*" | Remove-NetFirewallRule
# 整体还原：netsh advfirewall import "C:\Users\USER_A\cg_fw_backup.wfw"
```

<a id="desktop-switch-initial"></a>
## 四、桌面开关（已部署）

- `killswitch-off.ps1`：出站 Allow + 停 DNS 拦截 + 恢复加速器规则 → 正常用电脑
- `killswitch-on.ps1`：出站 Block + 全部拦截复位 → 挂 Claude 前的双击动作
- 双击自动 UAC 提权；**ON 之前确认 Clash Verge 在跑**，否则整机断外网（Tailscale 除外）
- 完整循环实测：off/on 状态切换正确，on 后出口哈希 `HASH_A_OLD` 无漂移

<a id="powershell-tools"></a>
## 五、脚本/工具层教训

1. **PowerShell 5.1 读无 BOM 的 UTF-8 .ps1 会当 ANSI/GBK** → 中文字符串（如网卡名"以太网 5"）变乱码，
   `New-NetFirewallRule -InterfaceAlias` 报"找不到接口"。
   解法：脚本纯 ASCII，网卡名运行时用 `Get-NetAdapter` 动态取；或写文件带 BOM。
2. **PowerShell 函数名别用 `H`** —— 和内建别名 `h`（Get-History）冲突，别名优先，函数被跳过。
3. `Set-Content -Encoding UTF8`（PS5.1）带 BOM，给 python json 读取用 `encoding='utf-8-sig'`。
4. 内联 `ssh host "powershell -Command \"...\""` 引号地狱 → 一律写脚本文件 scp 过去执行。
5. 出口 IP 全程用 SHA256 前 8 位哈希比对（如 `HASH_A_OLD`），不在聊天/日志回显明文。

<a id="windows-a-status"></a>
## 六、当前状态与待办

- ✅ 整机统一出口 established（TUN/核心/DNS/规则/出口/IPv6/WebRTC/演练 8 层全过）
- ✅ 时区 Eastern Standard Time（原 China Standard Time；自动时区服务 tzautoupdate 4→3）
- ⏳ **persistence 未建立**：下次重启后复验（重启后 Clash 起来前外网不通、起来后正常、出站仍 Block）
- ⏳ 规则里 `GEOSITE,cn,DIRECT` + `GEOIP,CN,DIRECT` 直连例外去留未拍板
- ⚠️ Windows 账户密码 `[REDACTED_SECRET]` 未改（`net user USER_A 新密码`）
- 备注：换节点/改端口/升级 Clash Verge 后核心路径或节点可能变，断网先查 guardian-allow-proxy-core 的程序路径是否还有效

---

# 第二台机器（windows-b）+ 自建 VPS 实战（2026-11-03）

<a id="vps-protocols"></a>
## 七、自建 VPS：3x-ui + Reality + Hysteria2

### 部署链路
- 3x-ui（mhsanaei 版）无 tty 自动非交互安装，随机凭据在 `/etc/x-ui/install-result.env`；面板 API 可用 Bearer token 直接建入站（不必点 UI）
- Reality 材料：`xray x25519` 出私钥/公钥，`openssl rand -hex 4` 出 shortId
- 订阅服务：`/opt/cg-sub/<随机路径>/clash.yaml` + python http.server 挂 systemd（`cg-sub.service`），随机路径当鉴权
- **HTTPS 无域名方案**：`<IP>.sslip.io` 免费域名（公网解析回本 IP）+ acme.sh 签 Let's Encrypt 真证书。80 端口留给续期挑战；面板证书用 `x-ui setting -webCert/-webCertKey`
- 面板切 HTTPS 后，**本机 curl API 也要改 https + -k**

### 重大坑：新版 xray 服务端 REALITY 与 mihomo 全系客户端不兼容

> **编者注：**“全系不兼容”是原作者当时的排障判断。原稿没有完整的 Xray/mihomo 版本与配置对照，日志和对照测试支持本次组合失败，不能据此证明所有版本都不兼容。下文安装脚本、随机路径订阅及本机 `curl -k` 也只保留为当时做法：先核对脚本与版本；随机路径不等于完整鉴权，不能把跳过证书验证当日常方案。
- 现象：Clash Verge（mihomo alpha + stable 全试、5 种指纹全试）测节点永远超时；**xray 自家客户端正常**
- 服务端日志实锤：`REALITY: processed invalid connection`
- 排除法矩阵：订阅参数一字不差 ✓、TCP 443 可达 ✓、同机 xray 客户端通 ✓ → 协议级不兼容，别再查客户端
- **解决：官方 Hysteria2 独立服务**（`curl https://get.hy2.sh/ | bash`，systemd 托管，UDP 端口，真证书）。别浪费时间猜 3x-ui v3.11 的 API——新协议枚举里没有 hysteria2
- Hysteria2 官方 unit 以 `hysteria` 用户运行，证书目录必须 `chown -R hysteria:hysteria`，否则起不来

<a id="verge-runtime"></a>
## 八、Clash Verge Rev 深坑（本节最值钱）

### 坑 1：订阅节点必须写 `udp: true`

> **编者注：**下文“默认关闭”限于原作者测试的节点、版本和配置，不能推广到所有协议；核对实际节点能力和运行时配置。可直接沿用的排障经验是：DNS 成功不能代证 UDP/STUN/QUIC 可用。
- mihomo **默认关闭 UDP 中继**。DNS 因 fake-ip 劫持不需要真实 UDP，所以一切"看起来正常"——但 STUN/WebRTC/QUIC 全哑
- 症状链：客户端日志显示 `[UDP] dial ... using PROXY`（中继发生了）→ VPS 抓包 0 包 → 查运行时配置发现节点没带 udp 字段
- Hysteria2 节点同理。**DNS 测着正常 ≠ UDP 中继正常**，两者路径完全不同

### 坑 2：改完配置 GUI 可能没真正加载（singleton 锁）
- 杀 GUI 重启，新实例若被 singleton 锁挡住，内核一直跑**旧配置**（udp: true 那版就没加载过）
- **真运行时文件是 `clash-verge.yaml`**；`config.yaml` 是 29 行的壳/模板残留，**不可信**
- 判断内核在跑哪份配置：控制器 API `/configs` 最准（Verge 默认不开 external controller），否则看进程启动时间 + 运行时文件 MTime

### 坑 3：Verge 设置与订阅的覆盖关系（结论）
- **DNS 覆写（enable_dns_settings）：保持关**。订阅 yaml 自带完整 dns/tun 段时，覆写开着 GUI 模板会顶掉订阅值（实测把 strict-route: true 顶成 false）
- **配置源唯一化**：改 DNS/TUN → 改 VPS 订阅文件 → Verge 更新订阅。不用 Verge 设置页的 DNS/TUN 面板
- **唯一必须在 GUI 开的**：TUN 模式设置 → 严格路由（客户端行为开关）。且 GUI 重启可能重置它，重启后要复查
- "开关自己变回去"的真相：GUI 活着时直接改 verge.yaml → 下次 GUI 保存时被内存旧状态回写

### 坑 4：GUI 的运行方式决定生死
- **SYSTEM 会话拉起的 GUI 是残废**（写出 0 行空配置）。修 GUI 必须 `schtasks /RU <user> /IT` 交互式任务，让 GUI 落回用户桌面会话
- 两个 GUI 实例并存会打架（重复 TUN 适配器、配置互踩），按 SessionId 清理只留用户会话

### 坑 5：TUN 网卡名会变
- 同一台机器观察到 `Meta` ↔ `Mihomo` 来回切（核心重启后适配器重建）
- 规则/脚本按 InterfaceDescription（`*Meta Tunnel*`）动态取名，别硬编码网卡名

<a id="tun-firewall-lifecycle"></a>
## 九、Killswitch 第二台的新坑

### 重大坑：WFP 接口规则存 GUID，核心重启后失效

> **编者注：**接口身份变化与规则失效是本次报告，GUID 绑定机制未在入库时独立核实。保留重启前后对照与修复经验，但 `198.18.0.0/16` 是本例使用范围，不是所有 Fake-IP 配置的固定值；按实际地址池与规则覆盖复验，不能只放行 Fake-IP 就宣称字面 IP 流量也有保障。第一台物理 DNS Block 与第二台撤掉该规则的做法是先后发现的不同状态，不能拼成统一配方。
- `New-NetFirewallRule -InterfaceAlias 'Mihomo'` 创建时 WFP 把网卡名**解析成 GUID 存储**；核心重启 TUN 适配器重建后 GUID 变了 → 规则指向死接口 → **TUN 全断**
- 级联效应：系统 DNS 指向 TUN 适配器上的 198.18.0.2 → DNS 一起挂 → curl 全部失败但别的应用"看起来正常"（它们的流量本来就走 fake-ip 路径），极具迷惑性
- **修复方案（核心重启免疫）**：按目标网段放行替代接口过滤——
  `guardian-allow-fakeip-out/in`：`RemoteAddress 198.18.0.0/16`（fake-ip 段含 DNS 198.18.0.2）
  再加一条当前网卡的接口规则兜底（字面 IP 流量）

### 其他坑
- **宽放行扫描误伤自家规则**：禁用 program=Any 的出站放行时，guardian 的接口/端口型规则（无程序路径，也是 Any）会被一起禁掉。扫描必须排除 `guardian-*` 前缀
- **Domain/Private 配置文件可能处于禁用状态**：只有 Public 在管事，网络类别一变就漏防。终验时发现并启用三档
- **物理网卡 53 Block 会拦死 mihomo 自己的上游解析**（WFP Block 优先于程序 Allow）→ 核心 `can't resolve ip` → 所有需要真实解析的 UDP 流全断。这台机器已撤物理 DNS Block，DNS 防泄漏靠"svchost DNS 禁用 + 默认出站 Block"兜底。**machine-① 的同款规则组合还在，那台要用 STUN/WebRTC 前需同样调整**
- killswitch-on 的宽放行扫描较慢（逐条查程序路径，约 2 分钟），SSH 直接跑会超时——用 schtasks 跑

### 桌面开关（已部署到 C:\Users\USER_B\Desktop）
- `killswitch-off.ps1` / `killswitch-on.ps1`，自提权；on 后完整验证：Block 生效、出口哈希回到 VPS（`HASH_B_NORMALIZED`）、guardian 10/10 启用、宽放行 0 残留

<a id="network-evidence"></a>
## 十、官方检测工具与判定

> **编者注：**“官方”指本项目随包工具，不是 Claude/Anthropic 的认证。本项目 `network_check.py` 检查 UDP/STUN，但导出证据里的 `webrtc` 仍是 `not_run`；浏览器 WebRTC 必须另取证，STUN 与 TCP 一致不能直接填成 `webrtc: no_leak`。严格路由等配置也要补实际读回，未知项不能写通过。安装 Python 是新增依赖，须说明来源与安装范围并取得相应授权，不能因工具缺失自动静默安装。

- Windows 无 Python 时 `network_check.py` 跑不了 → **静默装 Python**（华为云镜像 `python-3.13.1-amd64.exe /quiet InstallAllUsers=1 PrependPath=1`，SYSTEM 计划任务跑）
- 官方 `network_check.py` 一次覆盖：默认路由经 TUN、IPv4 出口、代理一致性、IPv6、**DNS 泄露（解析器归属）**、**STUN 映射与 TCP 出口一致性**
- 判定器口径：8 层 = TUN / 核心 IPv6 / DNS / 规则兜底 / 出口一致 / IPv6 探测 / WebRTC / 故障演练；killswitch 为 `firewall: fail_closed`；STUN 一致性是官方判定的一部分，不是可选项
- 出口 IP 全程哈希比对：node 机器基线 `HASH_B_NORMALIZED`（= 203.0.113.10）。**注意**：之前用的 `HASH_A_OLD` 是带 CRLF 的旧哈希口径，哈希基准要先统一换行符

<a id="windows-b-status"></a>
## 十一、node 机器状态与待办

> **编者注：**以下是历史状态，待办保持未验收。严格路由待复核、浏览器验收未完成时，不宣称当前整单已通过；`persistence` 还需要重启、睡眠唤醒、换网三项复验，不能只测重启。

- ✅ 出口 = 自建 VPS 203.0.113.10（美国洛杉矶，IANA America/Los_Angeles），时区已改 Pacific Standard Time（自动时区 4→3）
- ✅ killswitch fail-closed（三档 Block + guardian 10 条 + 宽放行 28 条停用 + fakeip 网段规则）
- ✅ STUN/UDP 与 TCP 出口一致（官方 network_check 全过）、DNS 无泄露、故障演练 no_direct
- ⏳ 严格路由：UI 开关被 GUI 重启重置过，需再开一次并复核运行时真值
- ⏳ 浏览器验收页（https://ip.net.coffee/claude/，除语言外全绿）→ DNS 泄露 + WebRTC 两层
- ⏳ persistence 未建立（待重启复验）
- ⚠️ VPS root 密码未改；面板/订阅凭据见安装记录；80 端口勿封（证书续期）

---

<a id="desktop-launcher"></a>
# 桌面开关重大缺陷复盘（2026-11-03 晚，用户实测暴露）

## 缺陷：用户双击开关脚本根本起不来（实测断网事故）

**根因：PowerShell ExecutionPolicy = Restricted 时，右键/双击运行 .ps1 在脚本加载瞬间就被拦截。** 我写的"自提权 + Bypass 重启"逻辑无效——那段代码在脚本内，而脚本压根没被加载执行到。

**为什么部署时没发现——测试路径 ≠ 使用路径：**

| 我的测试入口 | 用户的真实入口 |
|---|---|
| `powershell -NoProfile -ExecutionPolicy Bypass -File ...`（SSH 直跑） | 右键"使用 PowerShell 运行" |
| `schtasks /TR 'powershell ... -ExecutionPolicy Bypass -File ...'` | 双击 .ps1 |

每条测试命令都**显式带 `-ExecutionPolicy Bypass`**——15 次测试全绿只证明"带 Bypass 能跑"，从未验证"用户入口能跑"。加上脚本打印 `[1/3]...DONE` 就结束、**不回读防火墙真实状态**，启动被拦时用户看到的是无声失败，状态错乱导致实际断网。

## 正确修复方案（用户侧已实施，四点全对）

> **编者注：**快捷方式中的进程级 `-ExecutionPolicy Bypass` 针对本例的 Restricted 启动问题，不保证覆盖组策略或宿主限制，也不替用户确认 UAC。普通桌面入口仍会请求提权；下文“零参数特权”指用户无需手输调试参数，不代表无特权执行。`%LOCALAPPDATA%` 是用户可写的稳定位置，“用户动不到”应理解为不把脚本暴露在桌面；它不是权限保护目录。

1. **桌面放快捷方式（.lnk）而非裸 .ps1，Target 里显式带参**：
   `powershell.exe -NoProfile -ExecutionPolicy Bypass -File "<脚本绝对路径>"`
   ——把绕过策略放进**启动入口本身**，对 Restricted 策略免疫，不依赖右键行为和系统全局设置
2. **快捷方式中文名**（"开启保护（限制直连）"/"关闭保护（恢复联网）"）——可用性 + 防误改
3. UAC 授权窗口确认后才改防火墙（权限语义清晰）
4. **执行后回读 Domain/Private/Public 三档真实 DefaultOutboundAction，失败明确报错，不打印一句"完成"就完事**

## 方法学教训（比修复本身更重要）

1. **"验证"必须是对真实状态的回读，不是对已发命令的复述。** 打印了步骤 ≠ 步骤生效了
2. **验收必须覆盖用户的真实使用路径**：给用户的双击入口，就要用双击（或至少模拟无参数启动）验证，不能用自己调试用的带参命令代替。"能用（我跑过一次）"不能代替"你右键就能用"
3. **检测自己测试命令里的隐性特权**（-ExecutionPolicy Bypass、管理员 shell、计划任务的 SYSTEM 身份都是特权），特权路径测通了不等于普通路径通
4. **残留缺口要如实声明**：修复后"15 项隔离测试通过但未实际切换防火墙测联网"——同样要避免"宣称完成 ≠ 实证完成"；以及扫描式禁用（黑名单）的固有局限——装新软件/规则重建可能重新引入 program=Any 放行，"不能保证只有代理能联网"，彻底解法是白名单架构（只放行 guardian-* + 精确记录被禁清单供恢复），复杂度高一档

## 影响范围

三台 Windows（windows-a / windows-b / windows-c）的桌面开关都是裸 .ps1 交付，**在 ExecutionPolicy=Restricted 的机器上双击都会被拦**——下次接触这些机器时应统一升级为快捷方式 + Target 带参方案，并补一次"用户路径"实测（双击 → 状态回读 → 联网/断网验证）。

## 友好版标准配方：双击可用 + 图标 + 中文名（直接复制部署）

**结构原则：桌面只放快捷方式，脚本本体放用户动不到的稳定路径**（防误改/误删/移动后失效）：

```
脚本本体:  %LOCALAPPDATA%\ClaudeGuardian\killswitch-on.ps1 / killswitch-off.ps1
桌面入口:  开启保护（限制直连）.lnk  /  关闭保护（恢复联网）.lnk
```

**一键创建两个带图标快捷方式**（管理员 PowerShell 执行一次）：

```powershell
$dir = "$env:LOCALAPPDATA\ClaudeGuardian"
New-Item -ItemType Directory -Path $dir -Force | Out-Null
# 脚本本体（带状态回读验证的版本）放入 $dir 后：
$ws = New-Object -ComObject WScript.Shell
$desktop = [Environment]::GetFolderPath('Desktop')

$on = $ws.CreateShortcut("$desktop\开启保护（限制直连）.lnk")
$on.TargetPath = "$env:SystemRoot\System32\WindowsPowerShell\v1.0\powershell.exe"
$on.Arguments  = "-NoProfile -ExecutionPolicy Bypass -File `"$dir\killswitch-on.ps1`""
$on.WorkingDirectory = $dir
$on.IconLocation = "$env:SystemRoot\System32\shell32.dll,167"   # 盾牌图标
$on.Description = "开启 killswitch：默认出站 Block，仅代理/Tailscale 可出网"
$on.Save()

$off = $ws.CreateShortcut("$desktop\关闭保护（恢复联网）.lnk")
$off.TargetPath = "$env:SystemRoot\System32\WindowsPowerShell\v1.0\powershell.exe"
$off.Arguments  = "-NoProfile -ExecutionPolicy Bypass -File `"$dir\killswitch-off.ps1`""
$off.WorkingDirectory = $dir
$off.IconLocation = "$env:SystemRoot\System32\SystemSettings\imageres.dll" + ",-102"  # 或 shell32.dll,13（网络图标）
$off.Description = "关闭 killswitch：恢复默认出站 Allow，正常使用电脑"
$off.Save()
```

**关键点：**

1. `Target` 指向 `powershell.exe`，**`-ExecutionPolicy Bypass` 写进 Arguments**——这是对 Restricted 策略免疫的核心，.ps1 文件本体不再需要用户直接启动
2. 图标用系统自带 DLL 索引（`shell32.dll,167` 盾牌 / `imageres.dll,-102` 等），不引入外部 .ico；索引随喜好换
3. 快捷方式中文名 + Description 说明后果（"仅代理可出网"/"恢复正常使用"），语义自解释
4. 脚本本体结尾必须有**状态回读**（三档 `DefaultOutboundAction` + 出口连通性），失败红字报错，不许静默成功
5. ON 脚本开头加"确认 Clash 在跑"的探测（查 `verge-mihomo` 进程 + 出口可达），不在跑就弹窗警告后退出——把"ON 前先开代理"从口头提醒变成代码防御

**部署验收（用户路径实测，必须做）：**

```powershell
# 模拟双击：用 explorer 启动快捷方式（不带任何参数特权）
Start-Process explorer.exe "$desktop\关闭保护（恢复联网）.lnk"
# 然后人工确认：UAC 弹窗 → 点"是" → 窗口显示的状态回读 = Allow
# 反向再测"开启保护"→ 回读 = Block → 实测联网正常 → 演练级验证完成
```

验收标准：**双击入口（零参数特权）→ UAC → 状态回读正确 → 联网/断网行为与显示一致**，四环全过才算交付。
