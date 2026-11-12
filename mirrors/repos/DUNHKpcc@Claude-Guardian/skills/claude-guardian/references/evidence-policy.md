# M14：证据、来源与发布规则

## 判断边界

本页规定来源、论断和验证结果的记录方式；随包来源见 [source-library.md](source-library.md)。来源存在不表示已核验现行规则或完成实机测试。以下 URL 是获准阶段的核验入口，**不是 PC0 联网许可**。

来源类型与论断状态分别记录：官方政策只能支持其产品/时间/范围内的公开规则；技术文档描述指定版本能力；实测只支持测到的环境；项目参考资料是本项目的依据，直接据此给出指引。状态沿用 `pending/adopted_scoped/experience_only/contradicted/stale/quarantined`。网络来源采用的 `accepted_check/technical_correction/recommendation_pending/excluded_claim` 以及 D01—D12 的 `accepted_design` 不等于执行授权或已验证能力。

每项论断记录 ID、来源定位、适用版本/对象、核验日期、观察与推断、反证、决定和影响模块。不得把来源标题中的“100%”“核验版”变成保证。字段缺失、页面只读到框架、未找到实机证据均应保留限制。

## 稳定编号与历史争议

M00—M14、ENV-01—ENV-10、R-LOCAL/R-VM/R-VPS、G1/G2/G3、PC0/PC1/PC2、PC-G1/PC-G2、问题 ID 保持原语义。主规范 R01 与 ENV-SPEC:R01—R04 属不同命名空间，不合并。未知/未移植证据保留原编号，不重新分配。

C01—C20 保留为历史论断索引：C01 路线免封比较；C02 养号时长；C03 语言/时区因果；C04 全局禁 IPv6；C05 身份核验条件；C06 代理变量覆盖保证；C07 防火墙路径更新保证；C08 清理与身份重置；C09 支付成功率；C10 退款保证；C11 IP/DNS 分数；C12 TUN 与全局模式；C13 请求频率阈值；C14 邮件因果；C15 无密码 VNC；C16 远程脚本可信度；C17 SDK/第三方认证规则；C18 黑话歧义；C19 OAuth 养号前置；C20 单一流量指标推断滥用。其中养号时长（C02）、OAuth 养号前置（C19）等内容，按 2026-10-21 项目参考资料（ADR-009）写入 account-onboarding.md，不承诺免封。

D01—D12 保留环境决策索引：时间设置独立；UDP 协议分层；WebRTC 最小范围；DNS/DoH 分工；IPv6 按路径；代理模式独立；配置合并与回写；域名/IP/遥测范围；TLS 不伪装；IP 标签不作风险分；稳定性按实际限额；清理/修复精确化。每次实际修改仍须独立授权和适配验证。

S01—S08、S10 随包提供，原始与分发哈希及脱敏记录见 sources/manifest.json；个人路径和原始机器记录不公开。历史观察、版本推断、编者注与待办分开记录，收录不代表独立复验。S09 固定提交见 incidents-and-integrations.md；F01—F07 按历史社区线索使用，不伪造未提供的详细定位。

## 两份教程与来源去重（T09）

用户给了多份教程时，用 `sha256sum`（Windows：`Get-FileHash`）比较实际文件。字节完全相同就只算一个来源，不当作两个来源互相印证；字节不同也可能是同一来源的转载、节选或翻译，要看内容再判断。S03 PDF 和它的文字版按 manifest 的 `companions` 算同一来源。

## 发布与更新

发布派生指导、脱敏样例、有授权的代码，以及用户明确允许公开的来源资料。引用外部代码前单独核查许可证和署名，仓库 GPL-3.0 不自动授权再分发第三方教程。删除真实账号、私有路径、代理 URL/认证、订阅链接、cookie、令牌和请求内容。未来来源变更应记录受影响能力、撤回不再成立的结论、使旧证据失效并补回归；静态/合成测试只验证结构和逻辑。

下表只登记公开来源元数据。O 前缀属于主规范；E 前缀明确标为 ENV-SPEC 命名空间。相同 URL 可以支持不同范围，不能因此合并 ID。

## 官方与技术入口（历史索引）

- O01: https://agentskills.io/specification
- O02: https://code.claude.com/docs/en/skills
- O03: https://code.claude.com/docs/en/legal-and-compliance
- O04: https://code.claude.com/docs/en/network-config
- O05: https://support.claude.com/en/articles/8461763-where-can-i-access-claude
- O06: https://platform.claude.com/docs/en/api/errors
- O07: https://support.claude.com/en/articles/8325618-paid-plan-billing-faqs
- O08: https://support.claude.com/en/articles/14328960-identity-verification-on-claude
- O09: https://support.claude.com/en/articles/15036540-use-the-claude-agent-sdk-with-your-claude-plan
- O10: https://support.claude.com/en/articles/12386328-request-a-refund-for-a-paid-claude-plan
- O11: https://support.claude.com/en/articles/8241253-safeguards-warnings-and-appeals
- O12: https://support.apple.com/en-us/118242
- O13: https://support.apple.com/en-us/118245
- O14: https://support.apple.com/en-us/108285
- O15: https://support.apple.com/en-my/118283
- O16: https://support.claude.com/en/articles/9266495-how-do-i-sign-up-for-claude-pro-on-the-claude-app-for-ios
- O17: https://support.claude.com/en/articles/9612892-how-do-i-sign-up-for-claude-pro-on-claude-for-android
- O18: https://support.microsoft.com/en-us/windows/hardware/input-devices/check-whether-a-version-of-windows-supports-multiple-languages
- O19: https://support.microsoft.com/en-us/windows/experience/personalization/set-time-date-and-time-zone-settings-in-windows
- O20: https://support.microsoft.com/en-us/windows/hardware/input-devices/manage-the-language-and-keyboard-input-layout-settings-in-windows
- O21: https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/tzutil
- O22: https://learn.microsoft.com/en-us/previous-versions/windows/it-pro/windows-10/security/threat-protection/security-policy-settings/change-the-time-zone
- O23: https://learn.microsoft.com/en-us/troubleshoot/windows-client/shell-experience/cannot-set-timezone-automatically
- O24: https://support.microsoft.com/en-us/servicing/os/windows-10/2025/10/windows-10-extended-security-updates-esu-program
- O25: https://support.apple.com/guide/mac-help/change-the-system-language-mh26684/mac
- O26: https://support.apple.com/en-gb/guide/mac-help/mchlp2996/mac
- O27: https://learn.microsoft.com/en-us/questions/5953658/how-to-enable-group-policy-editor-gpedit-msc-on-wi
- O28: https://learn.microsoft.com/en-us/windows-hardware/manufacture/desktop/default-time-zones?view=windows-11
- ENV-SPEC:E01: https://www.clashverge.dev/guide/term.html
- ENV-SPEC:E02: https://www.clashverge.dev/guide/extend.html
- ENV-SPEC:E03: https://www.clashverge.dev/guide/rules.html
- ENV-SPEC:E04: https://wiki.metacubex.one/api/
- ENV-SPEC:E05: https://wiki.metacubex.one/config/dns/
- ENV-SPEC:E06: https://wiki.metacubex.one/config/inbound/tun/
- ENV-SPEC:E07: https://www.rfc-editor.org/rfc/rfc8828.html
- ENV-SPEC:E08: https://code.claude.com/docs/en/network-config
- ENV-SPEC:E09: https://v2.hysteria.network/docs/developers/Protocol/
- ENV-SPEC:E10: https://v2.hysteria.network/docs/advanced/Full-Client-Config/
- ENV-SPEC:E11: https://learn.microsoft.com/en-us/deployedge/microsoft-edge-policies/webrtciphandlingurl
- ENV-SPEC:E12: https://support.microsoft.com/en-us/windows/hardware/input-devices/check-whether-a-version-of-windows-supports-multiple-languages
- ENV-SPEC:E13: https://learn.microsoft.com/en-us/troubleshoot/windows-client/shell-experience/cannot-set-timezone-automatically
- ENV-SPEC:E14: https://support.microsoft.com/en-us/windows/experience/personalization/set-time-date-and-time-zone-settings-in-windows
- ENV-SPEC:E15: https://support.apple.com/guide/mac-help/set-the-date-and-time-automatically-mchlp2996/mac
- ENV-SPEC:E16: https://developer.mozilla.org/en-US/docs/Web/API/RTCIceCandidate/type
- ENV-SPEC:E17: https://curl.se/docs/manpage.html
- ENV-SPEC:E18: https://learn.microsoft.com/en-za/windows/security/operating-system-security/network-security/windows-firewall/rules
- ENV-SPEC:E19: https://support.apple.com/guide/mac-help/block-connections-to-your-mac-with-a-firewall-mh34041/mac
- ENV-SPEC:E20: https://support.ntp.org/Support/DaylightSavingTime
- ENV-SPEC:E21: https://datatracker.ietf.org/doc/html/rfc1928
- ENV-SPEC:E22: https://www.rfc-editor.org/rfc/rfc9110.html#name-connect
- ENV-SPEC:E23: https://github.com/gorhill/uBlock/wiki/Prevent-WebRTC-from-leaking-local-IP-address
- ENV-SPEC:E24: https://wiki.metacubex.one/config/proxies/tls/
- ENV-SPEC:E25: https://wiki.metacubex.one/config/general/
- ENV-SPEC:E26: https://wiki.metacubex.one/config/rules/
- ENV-SPEC:E27: https://platform.claude.com/docs/en/api/rate-limits
- ENV-SPEC:E28: https://platform.claude.com/docs/en/api/ip-addresses
- ENV-SPEC:E29: https://code.claude.com/docs/en/data-usage#telemetry-services
- ENV-SPEC:E30: https://code.claude.com/docs/en/desktop#network-access-requirements
- ENV-SPEC:E31: https://support.microsoft.com/en-US/Windows/Apps/repair-apps-and-programs-in-windows
- ENV-SPEC:E32: https://developers.cloudflare.com/bots/concepts/bot-score/
- ENV-SPEC:E33: https://developers.openai.com/codex/skills/ ; https://learn.chatgpt.com/docs/build-skills
- ENV-SPEC:E34: https://developers.openai.com/codex/app-server/ ; https://learn.chatgpt.com/docs/app-server
- ENV-SPEC:E35: https://developers.openai.com/codex/permissions/ ; https://learn.chatgpt.com/docs/permissions
- ENV-SPEC:E36: https://learn.chatgpt.com/docs/environments/modes
- ENV-SPEC:E37: https://learn.chatgpt.com/docs/agent-approvals-security
- ENV-SPEC:E38: https://developers.openai.com/codex/windows/ ; https://learn.chatgpt.com/docs/windows/windows-sandbox
- ENV-SPEC:E39: https://learn.microsoft.com/en-us/windows/win32/cimwin32prov/win32-operatingsystem
- ENV-SPEC:E40: https://learn.microsoft.com/en-us/powershell/module/nettcpip/get-nettcpconnection ; https://learn.microsoft.com/en-us/powershell/module/nettcpip/get-netudpendpoint
- ENV-SPEC:E41: https://learn.microsoft.com/en-us/windows/win32/api/winhttp/nf-winhttp-winhttpgetieproxyconfigforcurrentuser
- ENV-SPEC:E42: https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/netsh-winhttp
- ENV-SPEC:E43: https://learn.microsoft.com/en-us/powershell/module/dnsclient/get-dnsclientserveraddress
- ENV-SPEC:E44: https://learn.microsoft.com/en-us/windows-server/networking/windows-time-service/windows-time-service-tools-and-settings
- ENV-SPEC:E45: https://github.com/apple-oss-distributions/configd/blob/main/scutil.tproj/scutil.8
- ENV-SPEC:E46: https://support.apple.com/en-md/guide/remote-desktop/apdd0c5a2d5/mac
- ENV-SPEC:E47: https://support.apple.com/guide/remote-desktop/about-systemsetup-apd95406b8d/mac
- ENV-SPEC:E48: https://developer.apple.com/documentation/apple-silicon/about-the-rosetta-translation-environment
- ENV-SPEC:E49: https://www.clashverge.dev/uninstall.html
- ENV-SPEC:E50: https://www.clashverge.dev/privacy.html
- ENV-SPEC:E51: https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.management/get-timezone
- ENV-SPEC:E52: https://learn.microsoft.com/en-us/powershell/module/international/get-winuilanguageoverride
- ENV-SPEC:E53: https://www.ipify.org/
- ENV-SPEC:E54: https://developers.cloudflare.com/realtime/turn/ ; https://developers.cloudflare.com/realtime/sfu/get-started/connection-patterns/
- ENV-SPEC:E55: https://www.rfc-editor.org/rfc/rfc8489.html
- ENV-SPEC:E56: https://www.w3.org/TR/webrtc/
- ENV-SPEC:E57: https://github.com/chromium/chromium/blob/main/components/policy/resources/templates/policy_definitions/WebRtc/WebRtcIPHandlingUrl.yaml
- ENV-SPEC:E58: https://github.com/chromium/chromium/blob/main/components/policy/resources/templates/policy_definitions/WebRtc/WebRtcIPHandling.yaml
- ENV-SPEC:E59: https://learn.microsoft.com/en-us/deployedge/microsoft-edge-policies/WebRtcLocalhostIpHandling
- ENV-SPEC:E60: https://learn.microsoft.com/en-us/powershell/module/dnsclient/resolve-dnsname
- ENV-SPEC:E61: https://chromeenterprise.google/policies/url-patterns/
- ENV-SPEC:E62: https://chromeenterprise.google/intl/en_ca/policies/dns-over-https-mode/
- ENV-SPEC:E63: https://docs.python.org/3/library/socket.html#socket.getaddrinfo
- ENV-SPEC:E64: https://developer.mozilla.org/en-US/docs/Web/API/RTCPeerConnectionIceErrorEvent/errorCode ; https://developer.mozilla.org/en-US/docs/Web/API/RTCPeerConnection/icecandidateerror_event
