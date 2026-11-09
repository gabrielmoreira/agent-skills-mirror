---
title: AI 所有支付方式汇总
updated: 2026-10-05
tags:
  - 自媒体
  - 教程
  - AI
  - 支付
  - Agent可读
---
<mark style="background: #FF5582A6;">免责声明，本文档仅讨论支付方式，不讨论风控系数，整篇文档注重支付方式的讨论，代充，第一方礼品卡，成品号不列入第一标准</mark> 这篇文档传到哪了，有新增的内容联系B站UP DUNHKPcc，核实后可添加，所有信息免费开源，🐧群 1124987353
## 明确概念

- **LLC**：Limited Liability Company，美国有限责任公司。
- **EIN**：Employer Identification Number，美国联邦雇主识别号/企业税号。
- **SSN**：Social Security Number，美国个人社会安全号码。
- **ITIN**：Individual Taxpayer Identification Number，美国个人纳税人识别号。
- **KYC**：Know Your Customer，个人身份审核。
- **KYB**：Know Your Business，企业主体与实际业务审核。
- **BIN**：银行卡号前段对应的发卡机构/卡项目识别信息，商户风控常参考。
- **AVS**：Address Verification Service，美卡支付常见的账单地址校验。
- **3DS**：3-D Secure，银行卡在线支付身份验证机制。
- **Crypto**: 加密货币
<mark style="background: #FFF3A3A6;">- 低门槛 ：个人用户就能搞到
- 高门槛 ： 有折腾能力，且有一定资金，追求极致</mark>

## 快速结论 🌟个人用户建议使用

| 需求             | 当前优先级                               | 结论                                                    |
| -------------- | ----------------------------------- | ----------------------------------------------------- |
| 手机内购🌟         | Google Play / App Store             | 夯 <mark style="background: #FFB8EBA6;">极低门槛</mark>    |
| 低门槛境外卡&虚拟卡🌟   | Starryblu                           | 中规中矩 <mark style="background: #FFB8EBA6;">极低门槛</mark> |
| API 充值🌟       | OpenRouter                          | 人上人 <mark style="background: #FFB8EBA6;">极低门槛</mark>  |
| 正规美国企业虚拟卡      | Mercury                             | 夯 <mark style="background: #FF5582A6;">高门槛</mark>     |
| 批量/API 发卡能力    | Airwallex US                        | 人上人 <mark style="background: #FF5582A6;">高门槛</mark>   |
| 无限虚拟卡          | Slash                               | 人上人 <mark style="background: #FF5582A6;">高门槛</mark>   |
| 个人美国实体 Debit🌟 | East West Bank / Velo               | 夯 <mark style="background: #FFB86CA6;">极高门槛</mark>    |
| U 卡🌟          | Bybit / Plasma / SafePal / Bitget 等 | 中规中矩 <mark style="background: #FFF3A3A6;">低门槛</mark>  |

---

## 低门槛

<mark style="background: #FFF3A3A6;"><mark style="background: #FFF3A3A6;">虚拟</mark>卡 实体卡等叠加 google pay apple pay paypal等套壳不再给出</mark>

| 方案                                      | 类型 / 网络               | 虚拟卡 |     实体卡 | 中国大陆办理/KYC                                                        | GPT 实测     | Claude 实测              | 当前结论                                                                                         |
| --------------------------------------- | --------------------- | --: | ------: | ----------------------------------------------------------------- | ---------- | ---------------------- | -------------------------------------------------------------------------------------------- |
| **Google Play 内购**                      | 应用商店支付                |   — |       — | 🟡 取决于 Google 账号地区及支付资料                                           | 100%       | 100%                   | **低门槛优先**；价格/税费可能高于网页<br>国内用户优先国内开卡VISA/万事达/Amex 信用&储蓄皆可 <br>截止2026 10/5 新加坡谷歌Play仍可绑定银联<br> |
| **Apple App Store 内购**                  | 应用商店支付                |   — |       — | 🟡 取决于 Apple ID 地区、余额和支付审核                                        | 100%       | 100%                   | 可用，但账号地区/礼品卡规则变化快<br>[[#Apple礼品卡]]                                                           |
| **Starryblu [[#虚拟卡补充]]**                | 新加坡 Debit；网络以实际发卡项目为准 |   ✅ | ✅（支持地区） | 🟡 官方要求 KYCstarry]                                                | 99%（有拒付案例） | 99% （有拒付案例，且有触发身份验证案例） | **可作为低门槛境外卡备选**；不是美国卡                                                                        |
| **OpenRouter **                         | API Credits           |   — |       — | 以 OpenRouter/模型供应商政策为准                                            | 不适用        | 不适用                    | 官方支持 **Major ca rds / Alipay / USDC**[^openrouter]；适合 API，不等于官方订阅                            |
| **Bybit Card**                          | U 卡；卡项目随地区不同          |   ✅ |  部分地区 ✅ | ❌ Bybit 官方 2026-09 明确将 **Chinese Mainland** 列为受限地区[^bybit-region] | 99%（有拒付案例） | 99%（有拒付案例）             | 有返现还行，claude风控高，适合gpt低价区                                                                     |
| **Plasma One / SafePal / Bitget 等 U 卡** | U 卡 / VCC             | 视项目 |     视项目 | ⚠️ 准入、KYC、卡项目变化快                                                  | 🟡 成功与失败并存 | 🟡 成功与失败并存             | 只做备用；社区实测不能替代官方准入                                                                            |

---

## 高门槛：美国卡 / 企业卡/外卡 

<mark style="background: #FFB8EBA6;">
新增OpenAI Gift Card 高门槛</mark>

| 平台                                        | 虚拟卡                                      | 实体卡                          | 网络         | 中国大陆直接收实体卡                                                                                           | 是否需要美国 LLC / 美国公司               | 中国 KYC / 中国籍创始人                                                                                          | GPT 实测 | Claude 实测 | 开卡数量（代充可参考）                                        | 主要要求                                                   | 当前稳定性             | 适合程度                |
| ----------------------------------------- | ---------------------------------------- | ---------------------------- | ---------- | ---------------------------------------------------------------------------------------------------- | ------------------------------- | -------------------------------------------------------------------------------------------------------- | ------ | --------- | -------------------------------------------------- | ------------------------------------------------------ | ----------------- | ------------------- |
| **Mercury Business**                      | ✅ Virtual Debit / IO                     | ✅ Business Debit / IO        | Mastercard | ❌ 官方明确 China 仅限制实体卡邮寄；虚拟卡未被列入中国禁发[^mercury-card-country]                                             | ✅ 美国注册公司 + EIN                  | ✅ 官方支持非美创始人；中国不在当前 founder residence 禁止名单[^mercury-eligibility][^mercury-prohibited]                     | 100%   | 100%      | ✅ 虚拟卡可多开；IO 可按需开多张；Cards API 支持程序化发卡               | 美国公司、EIN、真实经营地址、真实/计划中的美国业务、KYB                        | ★★★★☆             | **★★★★★**           |
| **Airwallex US**                          | ✅ Virtual Visa                           | ✅ Personalized Physical Visa | Visa       | ⚠️ Issuing API 明确支持实体卡跨境投递，China 为可填写投递目的地；最终取决于具体 card program[^airwallex-delivery][^airwallex-api] | ✅ 要拿 US Issuing 通常需美国企业主体/获批卡项目 | 🟡 US KYB 会审核 UBO/业务；未发现官方承诺“中国 UBO 必批”                                                                  | 100%   | 100%      | ✅ 支持批量/API 发卡；上限由具体项目配置                            | 美国企业、KYB、获批 Issuing/Card Program                       | ★★★★☆             | **★★★★☆**；适合 API/多卡 |
| **Slash Business**                        | ✅ Virtual Visa Charge                    | ✅ Physical Visa Charge       | Visa       | ⚠️ 官方支持 international shipping；China 不在当前公开的不服务/暂停邮寄名单，但以下单页为准[^slash-physical]                      | ✅ Standard Slash 要美国实体          | ⚠️ 可接受海外申请人护照，但 **当前 Business Banking 要求提交的 business/BO 地址均在美国**[^slash-signup]                          | 100%   | 100%      | ✅ 官方明确 **Unlimited virtual cards**[^slash-virtual] | 美国公司、真实美国经营地址、受益人美国住宅地址、2 份银行/信用卡账单、经营活动证明             | ★★☆☆☆（纯大陆居住者）     | **★★★☆☆**           |
| **Relay**                                 | ✅ Virtual / Temporary Virtual Visa Debit | ✅ Physical Visa Debit        | Visa       | ❌ 官方仅寄美国地址[^relay-card]                                                                              | ✅ 美国注册并在美运营企业                   | ⚠️ 非美公民可申请，但当前文档要求每个 beneficial owner 提供 physical U.S. address，并要求 U.S. operating presence[^relay-owner] | —      | —         | ✅ 可多开；本次核验官方页未给统一数量上限                              | 美国企业、EIN、US Nexus/经营存在、受益人美国实体地址                       | ★★☆☆☆             | **★★☆☆☆**           |
| **East West Bank / Velo Global Checking** | ⚠️ 不主打独立虚拟卡                              | ✅ Visa Debit                 | Visa       | ✅ 官方条款明确：寄中国时发到已验证的一次性中国收货地址[^velo-china]                                                            | ❌ 不需要 LLC                       | 🟡 Global Checking 面向国际客户，但数字开户资格按地区/审核决定；V2EX 2026 反馈无 ITIN 远程路径变难[^v2ex-velo]                          | 100%   | 100%      | 通常 1 张个人主 Debit；非批量卡平台                             | **$25,000 起存 + $300 开户费**；低于要求可能退回；另有月维护费条件[^velo-fee] | ★★★☆☆（银行稳定、开户门槛高） | **★★★☆☆**；适合个人实体美卡  |

### 对中国大陆用户的实际排序

1. **Mercury**：美国 LLC 路线里信息最透明、社区案例最多。
2. **Airwallex US**：企业 Issuing/API 能力强，但 GPT/Claude 直接支付的近期样本不足。
3. **East West / Velo**：要个人实体美国 Visa 时价值高，但资金门槛高、远程开户条件更严。
4. **Slash**：产品强，但当前美国地址要求使纯大陆居住者不方便。
5. **Relay**：当前 U.S. operating presence + BO physical U.S. address 要求更严格。

---

## 美国 LLC 路线（参考，个人用户可跳）

感谢 感谢 感谢 GitHub `hua1995116/indiehackers-steps` 的公开实操路线为：

```text
中国籍创始人
  ↓
Wyoming LLC
  ↓
EIN
  ↓
Mercury
  ↓
Stripe / Wise
```

其 README 也记录了 LLC → EIN → Mercury → Stripe → Wise，以及 1120/5472 税务申报经验

> [!warning] Mercury 当前规则比旧教程更重要
> - 必须是美国注册企业。
> - 非美国居民创始人可申请。
> - 需要真实经营地址；Registered Agent / PO Box / UPS Store 不能作为 principal place of business。
> - 需要已有或计划中的美国业务。
> - Mercury 不支持 MSB / crypto exchange 等部分业务类型。[^mercury-eligibility]

---

## 踩过的坑

| 项目                        | 原因                           |
| ------------------------- | ---------------------------- |
| **国内卡网页直付 OpenAI/Claude** | 支付方式来源地区有明确限制                |
| **未知卡台 / 共享 VCC/某二级卡台**   | BIN、拒付、资金冻结和商户风控不可控；无公开稳定性保证 |
| **代充 / 提交 Session、Token** | 存在账号凭据暴露和第三方接管风险；不作为首选支付方案；  |
| **“某卡永久不封 Claude/GPT”**   | 没有事实依据；付款渠道只是账号风险信号之一        |

---

## Apple礼品卡 

| 渠道                        | 主要地区   | 中国用户可用性 | 优点                       | 风险/限制                        | 风评         |
| ------------------------- | ------ | ------: | ------------------------ | ---------------------------- | ---------- |
| **Apple 官方官网**            | 美区、日区等 |       ✅ | 最正规、来源干净、基本不用担心黑卡        | 美区通常 $10 起；国内卡有时会被拒，成功率会波动   | **首选**     |
| **Pockyt Shop**           | 主要美区   |       ✅ | 支付宝/微信方便，可小额、自定义金额       | 偶尔缺货；第三方渠道                   | **最常用第三方** |
| **支付宝海外礼卡入口**             | 美区为主   |       ✅ | 国内支付最方便，本质常跳 Pockyt Shop | 入口会变化、偶尔搜不到                  | **非常常见**   |
| **Amazon US / JP**        | 美区、日区  |       ✅ | 大平台，来源相对干净               | 需要对应 Amazon 区域账户；金额选择可能有限    | **靠谱备用**   |
| **微信 PockytShop 服务号/小程序** | 美区     |       ✅ | 微信直接买                    | 同样属于第三方                      | 有长期使用反馈    |
| **闲鱼**                    | 美区、日区  |       ✅ | 便宜、小额灵活                  | **来源不明、黑卡/追回/封 Apple ID 风险** | **不推荐**    |
| **淘宝/其他低价卡商**             | 各区     |       ✅ | 价格可能低                    | 黑卡、盗刷卡来源风险最大                 | **谨慎/不推荐** |
| **币安/USDT 渠道**            | 日区等    |      ⚠️ | 部分用户说汇率不错                | 非官方渠道，稳定性和来源需自己核验            | 少量用户使用     |
## 虚拟卡补充

| 平台                                                | 卡类型 / 网络                     | 中国大陆身份                                        | 主要 KYC           |                  开卡成本 | GPT 实测     | Claude 实测  | 入金方式                   | 当前评价                  |
| ------------------------------------------------- | ---------------------------- | --------------------------------------------- | ---------------- | --------------------: | ---------- | ---------- | ---------------------- | --------------------- |
| **Starryblu**                                     | 虚拟/实体卡；海外卡                   | ✅ 明确有大陆用户办理案例                                 | 护照 + 地址证明        |     当前 L站常见 `$9.9` 路线 | 99%(有拒付案例) | 99%(有拒付案例) | 港币 FPS、新加坡 PayNow、银行卡等 | ⭐⭐⭐⭐⭐                 |
| **SafePal + Fiat24**                              | Virtual Mastercard + 瑞士 IBAN | ✅ 官方内容明确涉及中国大陆用户                              | KYC；无需信用检查/强制质押  |          官方称开户/管理费 $0 | 99%(有拒付案例) | 99%(有拒付案例) | 法币、USDC/加密资产           | ⭐⭐⭐⭐ **正规度较高**        |
| **RooGoo**                                        | Virtual Card                 | ✅ L站称仅身份证即可                                   | 身份证/KYC          |                     低 | 99%(有拒付案例) | 99%(有拒付案例) | 平台入金                   | ⭐⭐⭐ **易开但手续费/服务差**    |
| **MEXC Global Card**                              | Visa                         | ⚠️ L站存在中国身份下卡反馈；官方地区以 App 为准                  | KYC              |             官方活动期较低/0 | 99%(有拒付案例) | 99%(有拒付案例) | Crypto                 | ⭐⭐⭐ **新卡，观察期**        |
| **Bitget Wallet Card**                            | Visa / DCS Singapore         | ❌ **官方目前不把中国大陆列为申请地区**                        | 支持地区身份证件 + 地址证明  | $0 opening/annual fee | 99%(有拒付案例) | 99%(有拒付案例) | Crypto                 | ⭐⭐ **不要再写成大陆新用户低门槛卡** |
| **Bybit Card**                                    | Mastercard                   | ❌ **Bybit 官方目前将中国大陆列为 excluded jurisdiction** | 地区 KYC           |                   视地区 | 99%(有拒付案例) | 99%(有拒付案例) | Crypto                 | ⭐ **不应作为大陆正规路线推荐**    |
| **Plasma One**                                    | Visa 类 Crypto Card           | ⚠️ 2026 年下半年中国身份拒绝明显增加                        | KYC + 地址证明       |                   视等级 | 99%(有拒付案例) | 99%(有拒付案例) | Crypto                 | ⭐⭐ **已经不算低门槛**        |
| **Ether.fi / KAST / Tuyo / Lava / Tria 等 Rain 系** | 多为 Visa Crypto Card          | ⚠️/❌ 2026 年中国身份明显收紧                           | KYC + 地址证明       |                    各异 | 99%(有拒付案例) | 99%(有拒付案例) | Crypto                 | ⭐ **不建议列入当前首选**       |
| **Krak / Kraken Card**                            | Visa（US）/ Mastercard（UK/EEA） | ❌ 大陆居民不符合官方 card eligibility                  | US/UK/EEA 居民 KYC |                $0 基础卡 | —          | —          | Fiat/Crypto            | ❌ **不是中国大陆低门槛卡**      |

## 证据来源

### A 级：官方

[^openai-region]: [OpenAI — ChatGPT supported countries](https://help.openai.com/en/articles/7947663-chatgpt-supported-countries)；[Unsupported countries/payment methods](https://help.openai.com/zh-hans-cn/articles/9131992-chatgpt-and-api-services-in-unsupported-countries-and-territories)
[^claude-region]: [Anthropic — Where can I access Claude?](https://support.claude.com/en/articles/8461763-where-can-i-access-claude)；[Get started with Claude](https://support.claude.com/en/articles/8114491-get-started-with-claude)
[^claude-billing]: [Anthropic — Paid plan billing FAQs](https://support.claude.com/en/articles/8325618-paid-plan-billing-faqs)
[^openrouter]: [OpenRouter Support — payment methods](https://openrouter.ai/support/)
[^mercury-eligibility]: [Mercury — Eligibility and requirements](https://support.mercury.com/hc/en-us/articles/28770467511060-Eligibility-and-requirements-for-opening-a-Mercury-account)
[^mercury-prohibited]: [Mercury — Prohibited countries](https://support.mercury.com/hc/en-us/articles/28771710754580-Prohibited-countries)
[^mercury-card-country]: [Mercury — Restricted countries for card issuance](https://support.mercury.com/hc/en-us/articles/34087163095572-Restricted-countries-for-card-issuance)
[^airwallex-delivery]: [Airwallex — Physical card delivery](https://www.airwallex.com/docs/issuing/get-started/create-cards/specify-delivery-method)
[^airwallex-api]: [Airwallex — Issuing Cards API](https://www.airwallex.com/docs/api/2024-08-07/issuing/cards)
[^slash-signup]: [Slash — Signing Up: requirements](https://www.slash.com/help-center/getting-started/signing-up-for-slash-what-you-ll-need-to-get-started)
[^slash-virtual]: [Slash — Creating Virtual Cards](https://www.slash.com/help-center/corporate-cards/creating-virtual-cards)
[^slash-physical]: [Slash — Physical Card](https://www.slash.com/help-center/corporate-cards/how-to-order-and-activate-a-physical-slash-card)；[Metal Card / international destinations](https://www.slash.com/help-center/corporate-cards/how-to-order-and-set-up-a-slash-metal-card)
[^relay-card]: [Relay — Create Virtual/Physical Visa Debit](https://relayfi.com/hc/en-us/articles/360038310212-Creating-a-Relay-debit-card/)；[Physical cards ship only in U.S.](https://relayfi.com/hc/en-us/articles/17608030214548-Updating-your-mailing-address/)
[^relay-owner]: [Relay — Required documents / beneficial owner](https://relayfi.com/hc/en-us/articles/38049251551636-Required-Documents-and-Organization-Details-to-Open-a-Relay-Account-by-Entity-Type/)
[^velo-china]: [East West Bank — Global Checking terms: China card shipping](https://www.eastwestbank.com/content/dam/ewb-dotcom/disclosures/products/apye_global_checking_velo_final.pdf)
[^velo-fee]: [East West Bank — Global Checking Fact Sheet](https://www.eastwestbank.com/en/personal-banking/global-checking-fact-sheet)
[^bybit-region]: [Bybit — Service Restricted Countries, updated 2026-09-01](https://www.bybit.com/en/help-center/article/Service-Restricted-Countries)
[^starry-kyc]: [Starryblu — KYC](https://blog.starryblu.com/why-does-starryblu-require-kyc-frequently-asked-questions-about-identity-verification/)；[Starryblu Card](https://www.starryblu.com/en/starrycard)

### B 级：DUNHKPcc实测/LinuxDo / V2EX / GitHub/NodeSeek/Tg等实测与讨论

[^ld-mercury-gpt]: [LinuxDo — O/充值变得好严格，2026-09-28](https://linux.do/t/topic/2963782)
[^ld-starry]: [LinuxDo — Starryblu 全球账户支持 AI 订阅](https://linux.do/t/topic/2589181)
[^ld-starry-gpt]: [LinuxDo — 我使用 Starryblu 卡购买 ChatGPT 的实践，2026-09-17](https://linux.do/t/topic/2913461)
[^ld-starry-fail]: [LinuxDo — Starryblu 支付/试用 ChatGPT，2026-09-18](https://linux.do/t/topic/2916719)
[^ld-starry-claude]: [LinuxDo — starryblu卡有人开吗，2026-09-10](https://linux.do/t/topic/2883588)
[^ld-bybit-gpt]: [LinuxDo — GPT 当前 U 卡冲 Pro 风险，2026-09](https://linux.do/t/topic/2868072)
[^ld-bybit-fail]: [LinuxDo — Bybit EU/格鲁吉亚卡 GPT 拒付，2026-08](https://linux.do/t/topic/2692118)
[^ld-bybit-claude]: [LinuxDo — Bybit 卡 + Claude，持续使用记录，2026-07/08](https://linux.do/t/topic/2510746)
[^ld-bybit-claude-fail]: [LinuxDo — Bybit 台湾卡无法绑定 GPT/Claude，2026-08](https://linux.do/t/topic/2694634)
[^v2ex-google-gpt]: [V2EX — 招行信用卡支付 OpenAI/Claude 讨论，2026-09](https://v2ex.com/t/1241005)
[^v2ex-google-claude]: [V2EX — 国内卡通过 Google Play 订阅 Claude，2026-04](https://v2ex.com/t/1205258)
[^v2ex-visa-claude]: [V2EX — 国内 Visa 经 Claude Android App + Google Pay 成功，2026-10](https://www.v2ex.com/t/1246025)
[^v2ex-cn-card]: [V2EX — 招行 Visa/Amex 网页直付失败讨论，2026-09](https://v2ex.com/t/1241005)
[^v2ex-gpt-pay]: [V2EX — 如何充值 ChatGPT，2026-09](https://www.v2ex.com/t/1240984)
[^v2ex-velo]: [V2EX — Velo 云开是否要 ITIN，2026-04](https://www.v2ex.com/t/1209203)
[^github-indie]: [GitHub — hua1995116/indiehackers-steps](https://github.com/hua1995116/indiehackers-steps)
略
### C 级：X / 推广帖

- X 上的 Starryblu、U 卡、Bybit 类帖子大量带邀请码/返佣，只作为“存在该产品/社区关注度”的线索，不用于判断开户资格或支付稳定性。
- 示例：[X — Starryblu 推广帖](https://x.com/zstmfhy/status/2091829968208883772)。
