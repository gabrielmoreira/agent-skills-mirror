# 手机端防封要点（iOS / Android）

内容来自 [S03 经验 PDF 第 4 页](../sources/S03-claude-experience.pdf)（Anthropic claude code 防封策略 PDF 的手机端表格，原文为图片），再加上 Android 要拔掉 SIM 卡。不承诺免封。

## 什么时候用

1. **账号注册时：**用户要在手机上注册、登录 Claude，或手机是主要使用设备时（见[账号注册与使用节奏](account-onboarding.md)）。
2. **选择内购支付时：**用户选了 Apple 或 Google Play 内购（见[支付说明](accounts-and-payments.md)的 Apple、Google 分步卡），内购基本都要在手机上完成，所以先过本页。**内购订阅后，手机上的 Claude App 至少每周打开使用一次**（[A0 第 12 条](account-onboarding.md)）。
3. **只有手机、没有电脑时：**见访谈 Q-OS12。

只给指引，由用户在自己的手机上操作；Agent 不代操作手机、不代付款。出口 IP 怎么获得见[固定出口 IP 的来源](egress-ip-options.md)，本页不重复，手机和电脑应使用同一个出口。

## 检查表（S03 第 4 页）

| 项目 | 做法 |
| --- | --- |
| 网络出口 | 长期固定一个国家或地区，最好同一个 ISP/ASN 或稳定出口 |
| IP | 动态家宽没问题，避免频繁跨国家或跨运营商跳 |
| IPv6 | 关闭，只走 IPv4：在代理客户端里关掉 IPv6（小火箭、FlClash 的 IPv6 开关，配置里是 `ipv6: false`） |
| DNS | 与网络出口一致，不要出现明显的本地 ISP 泄漏 |
| WebRTC | 重点检查是否泄露真实公网 IP；192.168 或 10.x 这类内网 IP 通常不重要 |
| 系统时区 | **和出口 IP 所在地区一致**（2026-10-28，S03 本页原写“保持真实”，以本条为准）：iOS 设置 → 通用 → 日期与时间，关掉“自动设置”，选出口所在城市；Android 设置 → 系统 → 日期和时间，关掉“自动设置时区”，选出口所在时区。改之前记下原时区；定好后不要来回改 |
| 系统语言 | 不需要为了 Claude 强行改成英文 |
| App | 优先官方 App；官方当前支持 Android 8+，iOS 要求 iOS 18+（以官方页面为准） |
| 定位权限 | 不需要时可以不给；需要地图或本地功能时再授权。Claude 移动端支持调用 Location Services |
| 支付 | 使用本人或自己公司的正常支付方式，Billing Address 填发卡商提供或确认的真实账单地址，不要随意填免税州；账单地址不是收货地址，不能直接用收货地址替代 |
| 登录 | 避免同一账号短时间从多个国家同时在线 |
| 账号 | 不共享，不批量切换多个账号 |
| 设备 | 这台手机被封超过 3 个账号就不要再用它（[A0 第 11 条](account-onboarding.md)） |

改完网络后，用户在手机浏览器打开 https://ip.net.coffee/claude/ 做浏览器环境验收，除语言外必须全绿（时区要和出口一致，见[做法](whole-machine-ipv4.md#browser-acceptance)）。

## Android 要拔掉 SIM 卡

Android 手机使用时要拔掉 SIM 卡，避免移动网络和运营商的地区信息与代理出口不一致。拔卡会影响通话、短信和短信验证码，需要收验证码时先插回，完成后再拔出。iOS 表格里没有对应的要求。

## 与本项目其他规则的关系

- **IPv6：**手机和电脑一样只走 IPv4，在代理客户端里关闭 IPv6；见[整机只走 IPv4](agent-remediation.md#ipv4-only-policy)。
- **支付：**付款由用户本人完成；没有美区 Apple ID 先按 [B2a 网页注册](accounts-and-payments.md#b2a)，新 Apple ID 养 3 到 7 天再充值；Apple 账号地区、余额和礼品卡规则按[支付说明](accounts-and-payments.md)走，不用 IP 或语言代替商店地区。
- **账号被停用：**转事故分诊，充值、换号都不是解除限制的办法。
- **系统与 UA：**Android 内核是 Linux，和 Linux 出口天生一致；iOS 和 Linux 的 TTL 差异也不大。浏览器不改 UA。见[出口与本机环境一致](exit-consistency.md)。
- 手机端的检查表不等于已通过；没有实际检查的项目写未知，不写通过。
