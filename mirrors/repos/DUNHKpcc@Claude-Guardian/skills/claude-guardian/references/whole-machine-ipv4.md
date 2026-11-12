# 整机统一出口：只走 IPv4，不走 IPv6（Clash Verge，Mac 与 Windows）

适用：用户已选**本机路线**，出口 IP 已经定了来源（见[固定出口 IP 的来源](egress-ip-options.md)），要让这台电脑**所有普通应用的公网流量都走同一个 IPv4 出口，不出现 IPv6**。口径与[现行整机统一路径](agent-remediation.md#ipv4-only-policy)一致。

分工：**配置**由 Agent 按分级授权做；**判定**由 `scripts/egress_verifier.py` 根据 Agent 实际观察到的证据给出，它只读、不采集、不改任何东西。判定的是网络路径，不是平台对账号的认可。

## 1. 要达到什么

1. TUN 开启，严格路由，默认路由经 TUN。
2. 核心 `ipv6: false`，DNS 不返回也不使用 IPv6。
3. 规则最后兜底走代理，没有写进规则的直连例外。
4. 浏览器、终端、其他应用、后台服务取样的出口 IPv4 都一致（等于预期出口）。
5. IPv6 探测不可达，WebRTC 没有真实地址，DNS 没有泄漏。
6. 停掉代理核心后**没有任何直连**（故障演练）。
7. 重启、睡眠唤醒、换网之后再验一次，才算持续保护有证据；按[分平台场景表与 Agent 提示词](local-firewall-prompts.md#incident-acceptance)执行并逐项报告。

## 2. 配置（Clash Verge）

**Clash Verge 的 TUN 和 DNS 开关由客户端设置生成运行时配置，会覆盖同名字段，所以 TUN、DNS 优先在客户端设置界面里改；** 改完用运行时配置读回确认，以当前版本的实际行为为准。合并文件（Merge）里放下面两处：

```yaml
ipv6: false
# 规则末尾：先拒绝 IPv6 目标，再兜底走代理组（组名换成自己的）
rules:
  - IP-CIDR6,::/0,REJECT,no-resolve
  - MATCH,<代理组名>
```

**注意：**客户端设置界面只有在对应开关启用时才覆盖合并文件里的同名字段（真机核实：TUN 总开关来自 `enable_tun_mode`，DNS 覆写来自 `enable_dns_settings`，两者启用时界面里的 `tun:`、`dns:` 段与最终运行配置一致）；改完以运行时配置读回为准。**严格路由默认可能是关的**：关着时停掉代理核心，流量会回落直连，fail-closed 就要靠 Mac PF 或 Windows 系统防火墙拦直连，建议在界面里开启严格路由作为第二道防线。

客户端设置里对应：TUN 模式开启，严格路由（strict-route）开启；DNS 开启、IPv6 关闭、增强模式 fake-ip；`dns-hijack` 接管 53 端口。Fake-IP 的边界和回滚后清 DNS 缓存见 [macOS DNS 经验](macos-dns-case-lessons.md) 和 [agent-remediation 第 10 条](agent-remediation.md#post-repair-stability)。

**Windows 实战补充：**[S10 第八节](../sources/S10-windows-deployment-sanitized.md#verge-runtime)记录了订阅与 DNS 覆写冲突、GUI 旧状态回写、singleton 和用户/SYSTEM 会话造成配置未加载的案例。先确定当前配置由谁生成，再选一个维护入口；配置文件写入成功不等于核心已加载，以实际运行配置读回为准。DNS 通不代表 UDP 通，节点 UDP 能力与 STUN 结果分开检查；工具 STUN 通过也不能替代浏览器 WebRTC 取证，见[第十节与编者注](../sources/S10-windows-deployment-sanitized.md#network-evidence)。

规则里**不要保留** `GEOIP,CN,DIRECT` 之类的直连规则，除非用户明确要这个例外；例外要逐条列出（目的范围、协议、原因），判定里 `direct_exceptions` 填 `listed`，没列清楚的填 `unlisted`，会判失败。

## 3. 怎么做（按档位）

| 步骤 | 档位 | 说明 |
| --- | --- | --- |
| 只读盘点：TUN、路由、核心配置、规则末尾、系统 IPv6 状态 | A | `inventory_cli.py` 或下面的只读命令 |
| 出变更卡：原值→新值、影响（局域网、VPN、DNS）、备份、恢复 | A | |
| 改 Clash Verge 合并文件和客户端 TUN／DNS 设置 | B | 计划批准一次；先备份，改后读回；失败自动恢复原值 |
| 退出和重启 Clash Verge | B | 写文件前先退出，改完再启动 |
| 关闭本机网卡 IPv6 | B | Windows 默认做，Mac 可选；节点用 IPv4 地址；见下 |
| 默认出站阻止／killswitch | **C** | 见[本机防火墙提示词](local-firewall-prompts.md) |
| 故障演练（停代理核心） | B（本机且用户在场）／**C**（远程或唯一入口） | |

**Mac：** 写合并文件时，Agent 先 `cp` 备份到用户目录下的私有备份文件夹，写后读回对比哈希；规则扩展（rules-prepend）有内置写入适配器，见 [Mac 修复链](agent-remediation.md#mac-修复链clash-verge-rev-258-的-rules-扩展)，合并文件和客户端设置没有，按上面方式处理。

**Windows：** 没有内置写入引擎，由 Agent 按提示词操作：配置在 `%APPDATA%\io.github.clash-verge-rev.clash-verge-rev\` 下，改前 `Copy-Item` 到私有备份目录，改后 `Get-FileHash` 读回，出问题用备份恢复；TUN 要管理员权限，系统弹窗由用户确认。Windows 防火墙见[本机防火墙提示词](local-firewall-prompts.md)，网卡 IPv6 默认关闭，见 [Windows 网卡 IPv6](agent-remediation.md#windows-adapter-ipv6-hint)。

**关闭网卡 IPv6（B 档）：** Windows 默认关闭，步骤见 [Windows 网卡 IPv6](agent-remediation.md#windows-adapter-ipv6-hint)。Mac 可选：先 `networksetup -listallnetworkservices` 列出服务名，再 `networksetup -setv6off "<服务名>"`，恢复用 `networksetup -setv6automatic "<服务名>"`；核心 `ipv6: false` 已经挡住代理里的 IPv6，不关会在判定里留一条建议 `OS_IPV6_NOT_DISABLED`。

## 4. 取证（Agent 实际执行，不替用户编造）

**先跑一条命令（B 档，用户批准检测计划后执行）：**

```bash
python3 scripts/network_check.py run --target-ref <别名> --proxy http://127.0.0.1:<mixed 端口> --evidence-output <私有目录>/evidence.json
```

它一次测完：默认路由是否走 TUN、IPv4 出口（只显示国家和 ASN）、经本地代理端口的出口是否和直连一致、IPv6 有没有出口、DNS 泄露（会主动连接测试域名，fake-ip 下也测得到；有解析服务器在本国就判泄露，`--home-country` 默认 `cn`）、UDP（STUN 映射地址和 TCP 出口是否一致）。加 `--failure-drill` 会在终端里提示用户停一次代理核心、再打开，测故障时有没有直连。联系的站点只有 `network_check.py endpoints` 列出的几个，不碰 Claude 和 Anthropic。`evidence.json` 含出口 IP，权限 0600，交给第 5 节的判定器；TUN 严格路由、核心 IPv6、规则兜底这些配置项它看不到，由 Agent 按第 2 节读配置后补进去，WebRTC 用下表的本地探测页。

下表是手动取证的办法，脚本测不了的项或要复核时用：

| 要证明的 | Mac | Windows |
| --- | --- | --- |
| TUN 开启、去往外网的路由经 TUN | `route -n get 1.1.1.1` 看接口是 `utun*`（不要看 `get default`：TUN 加的是更具体的路由，默认路由可能仍在物理网卡）；`ifconfig | grep utun` | `Get-NetRoute -DestinationPrefix 0.0.0.0/0 | Sort-Object RouteMetric`；`Get-NetAdapter` 找 TUN 网卡 |
| IPv4 出口（浏览器、终端、其他应用、后台各取一次） | 终端 `curl -4 -sS --max-time 10 https://ifconfig.me`；浏览器打开检测页 | `curl.exe -4 -sS --max-time 10 https://ifconfig.me`；浏览器同上 |
| IPv6 不可达 | `curl -6 -sS --max-time 10 https://ifconfig.me`，应失败 | `curl.exe -6 -sS --max-time 10 https://ifconfig.me`，应失败 |
| WebRTC | 包内[本地探测页](../assets/webrtc-probe.html) | 同左 |
| DNS 泄漏 | `network_check.py`；或检测页（dnsleaktest.com）看有没有本地运营商解析 | 同左 |
| 系统 IPv6 状态 | `networksetup -getinfo "<服务名>"` | `Get-NetIPInterface -AddressFamily IPv6` |
| 故障演练 | 退出 Clash Verge 或停核心，`curl` 和浏览器应全部失败；再启动应恢复 | 同左 |

**IPv6 探测的两种结果要分清：**`curl -6` 失败，或者**返回的其实是 IPv4 字符串**（TUN 下 IPv6 连接被代理核心接管、从代理的 IPv4 出口出去），都记 `ipv6_probe: unreachable`，不要把这个 IPv4 字符串当成 IPv6 样本填进 `samples`（判定器会因此拒绝）；只有返回真正的 IPv6 地址，才是 `reachable` 并填 `family: ipv6` 样本，判 `violated`。

AAAA 为空、`curl -4` 成功、一次 HTTPS 成功都不能单独证明整机通过；故障演练里不能让本来就断网的状态冒充"没有直连"。

## 5. 判定

把观察写成证据文件（**放在私有临时目录，含出口 IP，不提交、不上传，用完删除**），再运行：

```
python scripts/egress_verifier.py check --input <证据文件.json>
```

证据文件格式（`guardian-egress-evidence/0.1`，示例用文档保留地址）：

```json
{
  "schema_version": "guardian-egress-evidence/0.1",
  "platform": "macos",
  "target_ref": "mac-a",
  "tun": {"enabled": "yes", "strict_route": "yes", "default_route_via_tun": "yes"},
  "core": {"ipv6": "off"},
  "dns": {"ipv6": "off", "hijack": "yes", "leak_test": "pass"},
  "rules": {"final_match": "proxy", "direct_exceptions": "listed"},
  "firewall": "fail_closed",
  "os_ipv6": "disabled",
  "ipv6_probe": "unreachable",
  "webrtc": "no_leak",
  "failure_drill": "no_direct",
  "samples": [
    {"family": "ipv4", "exit": "203.0.113.9", "process": "browser"},
    {"family": "ipv4", "exit": "203.0.113.9", "process": "terminal"}
  ],
  "expected_exit": "203.0.113.9",
  "lifecycle_checked": ["restart", "sleep_wake", "network_change"]
}
```

取值只能是文档里列的枚举，没观察到就写 `unknown` 或 `not_run`，不能猜。输出的 `status`：

- `established`：8 个必要层都通过（`tun`、`core_ipv6`、`dns`、`rules`、`exit_ipv4`、`ipv6_probe`、`webrtc`、`failure_drill`）。
- `violated`：任一层明确失败，`blockers` 里给出原因；先修再复验。
- `incomplete`：有层没做或不确定，不能说整机已统一。

`persistence` 只有在 `established` 且重启、睡眠唤醒、换网都复验过时才是 `checked`，否则是 `not_established`，要如实告诉用户。`firewall` 和 `os_ipv6` 是建议项，不影响 `status`，会出现在 `advisories`。报告不回显任何 IP。

<a id="browser-acceptance"></a>
## 5a. 浏览器环境验收：[ip.net.coffee/claude](https://ip.net.coffee/claude/)

**环境修复后，用户在实际要用 Claude 的那个浏览器里打开 https://ip.net.coffee/claude/ 做验收，除了“语言”一项，其他必须全绿。**本机、手机、VM、VPS 的时区都须与出口一致，时区一项同样要绿。

1. 先做完第 5 节判定（`established`），再打开这个页面；浏览器用平时用的那个配置文件，不换浏览器、不开无痕。
2. 逐项看：出口 IP（中国出口 IPv4、Cloudflare 出口 IP、Claude AI 出口 IP 三个要一致，等于预期出口）、Claude AI 信任评分、Claude 支持地区、IP 属性、VPN／代理／Tor／机器人／滥用记录、claude.ai 与 anthropic.com 可用性、DNS 泄露检测、WebRTC UDP 泄露检测、设备信息。**语言以外有任何一项不是绿色，验收不通过**，回到对应层修（出口不一致看第 2 节规则与 TUN，DNS 泄露看 DNS，WebRTC 按[浏览器插件或策略、TUN 严格路由](agent-remediation.md#webrtc-block)修，IP 属性或信任评分不绿就换出口 IP，见[固定出口 IP 的来源](egress-ip-options.md)），修完重新跑第 5 节再打开这个页面。
3. 页面出现“当前为 IPv6 环境”的提示也算不通过，按第 2 节关 IPv6。
4. **时区与出口一致：**系统时区设成出口 IP 所在地区的时区（出口在美东用 `America/New_York`，美西用 `America/Los_Angeles`），并关掉“自动设置时区”，否则系统会按位置改回去。改之前记下原时区，展示目标和影响，按 C 档让用户当场确认。
   - macOS：系统设置 → 通用 → 日期与时间，关掉自动设置时区；改时区用 `scripts/native_claude_state_mac.py timezone <IANA 时区>`，见 [cleanup-cli-usage.md](cleanup-cli-usage.md)。
   - Windows：设置 → 时间和语言 → 日期和时间，关掉“自动设置时区”；PowerShell 先 `Get-TimeZone` 记原值，再 `Set-TimeZone -Id "Eastern Standard Time"`（美西是 `Pacific Standard Time`，`tzutil /l` 列出全部 Id），恢复用 `Set-TimeZone -Id <原值>`。
   - Linux（VM、VPS）：`timedatectl set-timezone America/New_York`，见 [VM 指引](vm-guidance.md)。
   - 改完重启浏览器再打开验收页，时区一项变绿才算过。语言不要求绿色，不为了让它变绿去改系统语言。
   - 手机：iOS 在设置 → 通用 → 日期与时间，关掉“自动设置”，选出口所在城市（美东选 New York）；Android 在设置 → 系统 → 日期和时间，关掉“自动设置时区”（各厂商叫法不同，也叫“使用网络提供的时区”），选出口所在时区。见[手机端防封要点](mobile-guidance.md)。
5. **UA 保持浏览器原生：**不装改 UA 的插件、不开 UA 覆盖；设备信息一项不绿，先查这个。原因和 TCP 指纹、延迟的做法见[出口与本机环境一致](exit-consistency.md)。
6. 这个页面会从浏览器测 claude.ai、anthropic.com 的可用性，属于接触 Claude：由用户本人打开，Agent 不代开、不用浏览器自动化去打开；把每项的颜色告诉 Agent（截图前遮住 IP），Agent 据此判断通过与否。
7. 用完按 [痕迹清理](trace-cleanup.md) 清浏览历史和 Shell 历史里的查 IP 记录。

## 6. 回滚

恢复备份的合并文件和客户端设置，重启 Clash Verge；关过网卡 IPv6 的恢复 `networksetup -setv6automatic`（Windows 用对应的恢复命令）；回滚后清系统 DNS 缓存。默认出站阻止和 killswitch 的回滚见各自文档。

## 7. 限制

- Mac PF 已验收（2026-11-09），范围和样本见 [PF 指引](local-firewall-prompts.md#mac)；TUN 正常时的整机通过样本见 ADR-039。Windows 按本文命令及目标机实际环境核对。
- 判定只相信 Agent 提供的观察。
- Windows 没有带事务的写入引擎，靠备份和读回哈希，不是原子替换。
- IPv4 不可用时报告不可用，不回退到 IPv6，也不自动换节点。
- 同一代理链不保证同一公网 IP，样本一致只支持实际测量的范围；IP 漂移要告知用户并复验。
