# M04/M05/M10: network evidence and offline remedies

中文执行摘要：网络检测用 `scripts/network_check.py run`（路由、IPv4 出口、IPv6 是否堵住、DNS 泄露、UDP、可选故障演练），WebRTC 用 `serve_webrtc.py`。按程序、路径、协议、地址族和时间解释结果；系统代理、TUN 和 rule/global/direct 是不同层。先定位问题，再给最小修改计划，保留内网、隧道与 Codex 通道。整机只走 IPv4 的范围和 Windows 网卡 IPv6 默认关闭见[整机统一路径](agent-remediation.md#ipv4-only-policy)。

See [sanitized macOS DNS/IPv6/Tailscale case lessons](macos-dns-case-lessons.md) for a single-device example. A configuration change invalidates conclusions about the old state; rerun `network_check.py` after it.

## ENV modules and evidence boundaries

| Stable ID | Purpose and required distinction |
|---|---|
| ENV-01 | Bind actual target, OS/Edition/architecture, namespace, and collector authority |
| ENV-02 | Inventory proxy/core/GUI/file/runtime/OS sources separately; configuration is not effective behavior |
| ENV-03 | IP/HTTPS observations scoped to process, path, target, time, and address family |
| ENV-04 | DNS layers, IPv6 paths, and UDP evidence kept separate |
| ENV-05 | Actual browser/profile/origin WebRTC and policy scope |
| ENV-06 | Minimal configuration plan preserving current subscriptions, rules, and control paths |
| ENV-07 | Launcher, GUI/terminal differences, interpreter and child-process coverage |
| ENV-08 | Clock, timezone, locale, language, and synchronization as independent facts |
| ENV-09 | Exact cleanup inventory/protection/backup/recovery plan |
| ENV-10 | Fault-blocking design and later real regression matrix; no fault injection in preview |

Collector failures are unknown/blocked, not bad configuration. Do not run the Claude binary to determine its version. No broad process command-line dumps, subscriptions, controller secrets, cookies, or raw logs in model output. Local/controller APIs require a real method/path whitelist, confirmed instance ownership and source, and sanitized responses; GET alone does not mean safe. Never scan controller ports or execute a configuration's JavaScript.

## Layered interpretation

A future approved check proceeds from selected proxy entry → scoped HTTPS sample → actual browser sample → DNS responsibilities → IPv4/IPv6 → relevant WebRTC/UDP → minimal remedy. Stop at missing target binding or approved endpoint. Do not make novices choose low-level protocol settings when the facts can be read safely.

- System/explicit proxy/TUN is an interception axis; rule/global/direct is a routing axis. TUN does not imply global routing
- A request reaching a proxy listener can still match DIRECT. A generic IP site need not follow the target service's route
- Distinguish network failure, DNS failure, TLS failure, HTTP error, invalid response, and unknown route. Keep certificate validation enabled
- Local DNS configuration, an actual system resolver answer, proxy-core DNS behavior, browser DoH, and authoritative correlation are different evidence levels. Fake-IP is not automatically a leak. A DNS answer/geolocation flag cannot locate the full recursive path
- IPv6 has at least four scopes: local interface, outer node transport, node-to-destination, and WebRTC candidates. AAAA absence and IPv6 timeout do not prove blocking
- HTTP CONNECT does not establish generic UDP proxying. SOCKS5 UDP support must be explicitly supported and observed; environment variables do not route arbitrary UDP sockets
- WebRTC host/private/link-local/mDNS candidates differ from public candidates. A different public candidate requires path/family analysis. ICE 701, no candidates, or timeout is inconclusive, not proof of no leakage
- A child's inherited proxy variable does not prove adoption. MCP subprocesses, external interpreters, plugins, background clients, and update paths require their own later evidence

<a id="tls-and-direction-semantics"></a>
## TLS 字段与服务方向：先解释，后限定规则候选

Mihomo 的 `fingerprint` 是证书指纹字段，`fingerprint: chrome` 属于字段语义不匹配；其适用代理协议中的 `client-fingerprint` 才是客户端 uTLS 参数。两者不能直接互换，不自动改名覆盖已有合法 `client-fingerprint`，不编造证书哈希。代理到节点的外层 TLS 与应用到服务的内层 TLS 分开；改变外层参数不能证明内层应用成为 Chrome，也没有“伪装 Chrome 更安全”的结论。保留既有节点必要 TLS 设置；只有具体证书／协议兼容错误及已核实的版本能力才另出最小修改计划。不得靠 `skip-cert-verify`、关闭校验或安装自签根证书补救。独立规则候选须保持全部 TLS 字节不变，通用 unsupported 错误不能代替对此语义错误的正面解释。

冻结的 2026-10-15 来源在 §5.9／E28 将 `160.79.104.0/23` 和 `2607:6bc0::/48` 记为服务 **Inbound**，将 `160.79.104.0/21` 记为平台 **Outbound**。方向以 Anthropic 为参照：前者是 `client_to_service`，后者是 `service_to_external`，不是按本机网卡命名。解释时保留这个来源日期、用途和覆盖边界；较宽范围包含较窄范围或某 API 地址，也不能把平台 Outbound 清单编成客户端默认目标规则，更不证明覆盖第三方 CDN／授权依赖。历史条目不当成今天已核验的清单；新的精确 CIDR 方案仍需独立来源核验及能力评审，不因此在 PC0 自动访问目标服务。


## Finding → minimal plan

| Observation | Proposed remedy and preserved scope |
|---|---|
| Selected proxy entry unavailable | Check chosen instance, listener and stale configured port; do not silently install or restart it |
| IP endpoint matched DIRECT | Retain as a natural-route sample; propose a narrowly scoped neutral-domain route for a future authorized comparison |
| Explicit proxy ignored by a program | Identify supported transport/launcher configuration for that exact version; do not claim ALL_PROXY covers everything |
| Unexpected target DNS route | Separate bootstrap, ordinary, split/internal, and proxy-node resolution; repair only the responsible layer and preserve internal domains |
| Browser DoH conflicts with intended DNS | Compare effective browser policy and core responsibilities; propose narrow applicable changes rather than disabling all secure DNS |
| Fake-IP answer with working HTTPS | Explain the mapping and retain configuration unless additional evidence shows a fault |
| Fake-IP enabled and entries in `fake-ip-filter` | Those names are resolved for real; check which resolver answers (system, ISP, or proxy-core remote DNS) and keep only needed entries. A real answer from a non-proxy resolver is a DNS leak finding; Fake-IP itself is not |
| Fake-IP enabled and a program uses its own DoH/DoT or literal IP | Fake-IP only covers lookups that go through the proxy-core resolver; verify these programs separately (TUN route, rules, IPv6) and do not count Fake-IP as covering them |
| Claude IPv4-only scope or enforcement evidence missing | Plan selected-scope IPv4-only even without an observed bypass; keep support unknown/unsupported and compliance not_established, preserve outer/control traffic and obtain exact approval before changes |
| IPv6 bypass observed | Locate the actual target leg and repair its scoped IPv4-only enforcement under the current product policy; preserve IPv6-dependent outer proxy transport and unrelated traffic |
| IPv4 works, IPv6 times out | Record unavailable/unknown IPv6; do not report a working kill switch or globally disable IPv6 |
| Browser WebRTC bypass confirmed | Install Google's WebRTC Network Limiter extension in Chrome with "Disable non-proxied UDP" ticked, or set the `WebRtcIPHandling` = `disable_non_proxied_udp` policy ([steps](agent-remediation.md#webrtc-block)); disclose media effects |
| Non-browser app WebRTC/UDP with only the system proxy on (this is the Claude Desktop WebRTC leak case: Electron sends its own STUN/UDP) | The system proxy does not cover UDP or apps that ignore it; turn on TUN with strict route ([steps](agent-remediation.md#webrtc-block)) and retest UDP with `network_check.py run` |
| Policy exists but browser ignores it | Check key/type/version/profile/management precedence and refresh requirements; do not overwrite the entire policy tree |
| HTTPS succeeds, STUN fails | Preserve the HTTPS finding and investigate STUN-specific path/endpoint uncertainty; no automatic account cleanup or node cycling |
| TUN UDP route uses wrong rule/node | Propose a limited rule/node-capability correction; preserve Hysteria2/TUIC outer UDP and other applications |
| Timezone/language differs from egress label | No automatic remedy; ask the actual user setting goal and distinguish clock accuracy from display |

ENV-06 plan families are: keep current configuration with narrow rule repair; explicit proxy plus rules; TUN plus rules; explicitly scoped compatibility fallback. Do not publish an unvalidated universal Clash YAML. Account for GUI/extension merge priority, effective runtime, subscription updates, first-match ordering, internal exceptions, Codex connectivity, and rollback conflicts.

The shipped selected-target IPv4-only contract is evaluated separately from these four legacy semantic plans. Do not inject networking changes into an unrelated rule edit or remove the older compatibility planner's outer-transport protection. A legacy intent to preserve target-leg IPv6 conflicts with that contract and must be disclosed; it is not silently reinterpreted as an instruction to block. These finding/plan entries remain local diagnostic methods, not the current whole-device scope or automatic exceptions. Completing an independent plan does not satisfy either the scoped contract or the current whole-device requirement.

## Detection tools

`network_check.py run` contacts only the neutral endpoints it lists (`network_check.py endpoints`), never Claude or Anthropic, and is run after the user approved the check plan (B tier). Add `--proxy http://127.0.0.1:<port>` to also test the local HTTP/mixed port, `--failure-drill` for the interactive stop-the-core drill, and `--evidence-output` to feed `egress_verifier.py`. WebRTC uses the bundled local page (`serve_webrtc.py`) in the user's actual browser profile; record origin, version, effective policy and candidate classes.

## Report format

For each finding provide: stable module ID; result; target/program/profile/path/family; observation and source/time; unknowns; proposed minimal change; preserved objects; expected future observation; next module; authorization/capability blocker. Avoid risk scores. Deduplicate shared root causes instead of proposing repeated network rewrites.
