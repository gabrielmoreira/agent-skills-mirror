# Reverse Engineering Skill Routing Matrix

Route tasks to the most appropriate skill module by target type, user intent, and toolchain.

## CRITICAL: Routing Execution Protocol

1. **MUST** complete routing BEFORE executing. Do NOT "do first, route later".
2. **MUST** match ALL three dimensions (target type + user intent + toolchain) before entering a skill.
3. If route not matched 鈫?propose new skill, do NOT force-fit.
4. Cross-module tasks 鈫?combine skills per "Path Crossing" section.
5. After routing, read the target skill's SKILL.md BEFORE taking action.

## By Target Type

| Target Type | Recommended Entry | Alternative |
|-------------|------------------|-------------|
| APK / Android app | `apk-reverse/` 鈥?jadx decompile + apktool unpack | If core is in .so 鈫?`ida-reverse/` or `radare2/` |
| Binary exe/dll/so/elf | `ida-reverse/` 鈥?IDA Pro decompile | `radare2/` 鈥?CLI analysis, or `reverse-engineering/tools.md` 鈥?GDB/Unicorn |
| JavaScript / Web frontend | `js-reverse/` 鈥?5-stage workflow | anything-analyzer MCP browser tools, or jshookmcp CDP/Hook |
| HTTP capture / browser sampling / request replay | anything-analyzer MCP (23816) | `js-reverse/`, jshookmcp, or `competition-web-runtime/` |
| Firmware / IoT | `reverse-engineering/platforms.md` 鈥?binwalk/ARM/MIPS | `reverse-engineering/tools.md` 鈥?Ghidra headless |
| WASM / Python bytecode | `reverse-engineering/languages.md` | Check specific language section |
| .NET / C# 鎵樼绋嬪簭 (exe/dll) / ConfuserEx/SmartAssembly 娣锋穯 / Sharp* 绾㈤槦宸ュ叿 | `dotnet-reverse/SKILL.md` 鈥?dnSpyEx + de4dot锛孖L 浼樺厛 | IL2CPP/NativeAOT (native) 鈫?`reverse-engineering/` |
| macOS / iOS | `reverse-engineering/platforms.md` 鈥?Mach-O/ObjC/Swift | `mobile-reverse/` for iOS-specific |
| Game (Unity) | `reverse-engineering/` 鈥?engine reverse, anti-cheat, IL2CPP/Mono (see seed-014) | `ida-reverse/` deep analysis |
| Memory dump / PCAP | `reverse-engineering/platforms.md` | `reverse-engineering/patterns*.md` |
| Malware / virus sample | `reverse-engineering/` 鈥?YARA/sandbox/behavior analysis | `ida-reverse/` deep analysis |
| OLLVM-obfuscated binary (鎺у埗娴佸钩鍧﹀寲/铏氬亣鎺у埗娴?MBA) | `reverse-engineering/references/ollvm-deobfuscation.md` 鈥?瀹屾暣鑴卞瘑宸ヤ綔娴?| obpo-plugin / d810-ng (IDA) / ollvm-unflattener (Miasm) / ollvm-breaker (Binary Ninja) / angr / deollvm (ARM64)
| Cryptography / encryption algorithms | `reverse-engineering/patterns*.md` 鈥?crypto patterns | `js-reverse/` (if frontend crypto) |
| Protocol reverse / custom protocol | `reverse-engineering/platforms.md` 鈥?network protocols | `js-reverse/` (if WebSocket/HTTP) |
| Go / Rust binary | `reverse-engineering/languages-compiled.md` + `go-reverse.md` | `ida-reverse/` or `radare2/` |
| LLM / AI application | `llm-security/` 鈥?OWASP LLM Top 10 + ASI Top 10 | Prompt injection, Agent security |
| API / REST / GraphQL | `api-security/` 鈥?BOLA/BFLA/JWT/OAuth | `pentest-tools/` for scanning |
| Supply chain / SBOM / CI-CD | `supply-chain-security/` 鈥?Trivy/Syft/Gitleaks | 鈥?|
| iOS app (IPA) | `mobile-reverse/` 鈥?class-dump/Hopper/Frida iOS | `reverse-engineering/platforms.md` |
| **CTF competition (full stack)** | `../CTF-Sandbox-Orchestrator/ctf-sandbox-orchestrator/SKILL.md` 鈥?master entry | Route to 40+ sub-skills by evidence |
| Web runtime / API | `../CTF-Sandbox-Orchestrator/competition-web-runtime/SKILL.md` | 鈥?|
| Cloud / Container / K8s | `../CTF-Sandbox-Orchestrator/competition-agent-cloud/SKILL.md` | 鈥?|
| Windows / AD / Identity | `../CTF-Sandbox-Orchestrator/competition-identity-windows/SKILL.md` | 鈥?|
| Forensics / PCAP / Steganography | `../CTF-Sandbox-Orchestrator/competition-forensic-timeline/SKILL.md` | 鈥?|
| Prompt injection / Agent | `../CTF-Sandbox-Orchestrator/competition-prompt-injection/SKILL.md` | 鈥?|
| Mobile (Android/iOS) | `../CTF-Sandbox-Orchestrator/competition-android-hooking/SKILL.md` | 鈥?|
| Firmware / Malware sample | `../CTF-Sandbox-Orchestrator/competition-firmware-layout/SKILL.md` | 鈥?|

## By User Intent

| User Says | Route To |
|-----------|----------|
| "decompile / IDA analyze" | `ida-reverse/SKILL.md` 鈥?IDA MCP workflow |
| "recover source / disassemble" | `reverse-engineering/SKILL.md` + `ida-reverse/` |
| "Frida hook / dynamic inject" | `reverse-engineering/tools-dynamic.md` 鈥?Frida section |
| "radare2 / r2 analyze" | `radare2/SKILL.md` 鈥?CLI workflow |
| "find frontend signature / encrypted params" | `js-reverse/SKILL.md` 鈥?Observe鈫扖apture鈫扲ebuild |
| "jshookmcp / JS hook / CDP debug" | `js-reverse/SKILL.md` 鈥?same JS/Web chain |
| "APK unpack / repack / modify smali" | `apk-reverse/SKILL.md` 鈥?decode鈫抮ebuild-sign-install |
| "bypass anti-debug / anti-detection" | `reverse-engineering/anti-analysis.md` |
| "OLLVM deobfuscate / 鎺у埗娴佸钩鍧﹀寲鍘婚櫎 / deflat / 鑴辨贩娣? | `reverse-engineering/references/ollvm-deobfuscation.md` 鈥?瀹屾暣宸ヤ綔娴?|
| "obpo / obpo-plugin / d810-ng / d810" | `reverse-engineering/references/ollvm-deobfuscation.md` 鈥?鐜颁唬鍙嶆贩娣嗗伐鍏?|
| "Hikari / Polaris / Pluto / O-MVLL / Arkari / goron 娣锋穯" | `reverse-engineering/references/ollvm-deobfuscation.md` 鈥?鐜颁唬 OLLVM 鍙樼澶勭悊 |
| "Tigress / Hodur / Approov 娣锋穯" | `reverse-engineering/references/ollvm-deobfuscation.md` 鈥?d810-ng 涓撶敤 unflattener |
| "Trap Angr / angr 璺緞鐖嗙偢" | `reverse-engineering/references/ollvm-deobfuscation.md` 鈥?Pluto/Polaris 闄烽槺澶勭悊 |
| "BR 娣锋穯 / 闂存帴鍒嗘敮娣锋穯鍘婚櫎" | `reverse-engineering/references/ollvm-deobfuscation.md` 鈥?DeObfBR + 鏁版嵁娈靛彧璇?|
| "what obfuscation / VM is this" | `reverse-engineering/patterns*.md` 鈥?match by pattern |
| "Go/Rust/Swift reverse" | `reverse-engineering/languages-compiled.md` + `go-reverse.md` |
| ".NET / C# 閫嗗悜 / dnSpy / dnSpyEx 鍒嗘瀽" | `dotnet-reverse/SKILL.md` 鈥?鎵樼 PE 閫嗗悜 |
| "ConfuserEx / SmartAssembly / Babel 鑴辨贩娣?/ 鑴卞３" | `dotnet-reverse/references/obfuscators.md` 鈥?de4dot + anti-tamper 缁曡繃 |
| "Sharp* 宸ュ叿鍒嗘瀽 / Rubeus / SharpHound 閫嗗悜" | `dotnet-reverse/references/sharp-tools.md` 鈥?绾㈤槦宸ュ叿鍒嗘瀽 |
| ".NET malware / loader / info-stealer 閫嗗悜" | `dotnet-reverse/SKILL.md` 鈥?閰嶇疆/C2/key 鎻愬彇 |
| "C# 绋嬪簭 patch / keygen / 鏀瑰垽鏂? | `dotnet-reverse/references/common-workflow.md` 鈥?IL patch 浼樺厛 |
| "kernel driver / Rootkit / LKM" | `reverse-engineering/kernel-driver-reverse.md` |
| "Python bytecode / pyc" | `reverse-engineering/languages.md` 鈥?Python section |
| "symbol execution / angr" | `reverse-engineering/tools-dynamic.md` 鈥?angr section |
| "patch environment / Node reproduce" | `js-reverse/references/env-patching.md` |
| "CTF challenge / competition reverse" | `reverse-engineering/patterns-ctf*.md` |
| "write report / documentation" | `docs-generator/` 鈥?technical documentation |
| "write writeup" | `docs-generator/` 鈥?CTF writeup template |
| "open webpage / browser automation / fill form" | `browser-automation/SKILL.md` 鈥?Playwright |
| "crawl page / screenshot / auto login" | `browser-automation/SKILL.md` |
| "desktop automation / Windows automation" | `browser-automation/SKILL.md` 鈥?OpenReverse |
| "game reverse / anti-cheat / hack analysis" | `reverse-engineering/SKILL.md` 鈥?game reverse (IL2CPP/Unity/Cheat Engine) |
| "Unity / IL2CPP / Mono" | `reverse-engineering/SKILL.md` 鈥?Unity + `seed-014_unity-il2cpp-reverse.md` |
| "Cheat Engine / memory scan" | `reverse-engineering/SKILL.md` 鈥?Cheat Engine memory analysis |
| "symbol migration / cross-version compare" | `binary-diff/SKILL.md` 鈥?LLM batch migration |
| "missing PDB / old version symbols" | `binary-diff/SKILL.md` 鈥?cross-version symbol migration |
| "bindiff / function offset migration" | `binary-diff/SKILL.md` 鈥?binary diff |
| "port scan / Nmap" | `pentest-tools/SKILL.md` 鈥?information gathering |
| "vulnerability scan / Nuclei" | `pentest-tools/SKILL.md` 鈥?vulnerability detection |
| "SQL injection / SQLMap" | `pentest-tools/SKILL.md` 鈥?web pentest |
| "directory brute force / FFUF / Gobuster" | `pentest-tools/SKILL.md` 鈥?web pentest |
| "password cracking / Hashcat" | `pentest-tools/SKILL.md` 鈥?password cracking |
| "penetration testing / active scan" | `pentest-tools/SKILL.md` 鈥?pentest toolchain |
| "SRC hunting / Bug Bounty" | `pentest-tools/src-hunter/SKILL.md` 鈥?19 playbooks + H1 cases |
| "WAF bypass" | `pentest-tools/src-hunter/references/payloader/` 鈥?263 bypass steps |
| "draw diagram / flowchart / architecture" | `diagram-generator/SKILL.md` |
| "attack path diagram / sequence diagram" | `diagram-generator/SKILL.md` 鈥?Mermaid/Graphviz/PlantUML |
| "malware / virus analysis / sample analysis" | `reverse-engineering/SKILL.md` + YARA/sandbox |
| "firmware / IoT / binwalk / ARM" | `reverse-engineering/platforms-hardware.md` |
| "cryptography / AES / RSA" | `reverse-engineering/patterns*.md` 鈥?crypto pattern recognition |
| "protocol reverse / Protobuf / custom protocol" | `reverse-engineering/platforms.md` |
| "cloud security / container escape / K8s" | `../CTF-Sandbox-Orchestrator/competition-agent-cloud/SKILL.md` |
| "Prompt injection / AI security" | `llm-security/SKILL.md` 鈥?OWASP LLM + ASI Top 10 |
| "internal network / lateral movement" | `pentest-tools/SKILL.md` + `references/network-attack-defense.md` |
| "privilege escalation" | `pentest-tools/references/network-attack-defense.md` 鈥?escalation section |
| "Mimikatz / credential extraction / PtH" | `pentest-tools/references/network-attack-defense.md` |
| "Kerberos / domain pentest / AD" | `pentest-tools/references/network-attack-defense.md` |
| "C2 / persistence / remote control" | `pentest-tools/references/network-attack-defense.md` |
| "blue team / detection / defense / IR" | `pentest-tools/references/network-attack-defense.md` |
| "APK security testing / mobile security" | `apk-reverse/references/apk-security-checklist.md` 鈥?OWASP MASTG |
| "SSTI / template injection" | `pentest-tools/SKILL.md` 鈥?SSTImap |
| "XSS scan / cross-site scripting" | `pentest-tools/SKILL.md` 鈥?XSStrike |
| "WordPress pentest / WP enumeration" | `pentest-tools/SKILL.md` 鈥?WPProbe |
| "C2 framework / adversary simulation" | `pentest-tools/SKILL.md` 鈥?AdaptixC2 |
| "WiFi attack / wireless pentest" | `pentest-tools/SKILL.md` 鈥?Fluxion + aircrack-ng |
| "NTLM relay / auth coercion" | `pentest-tools/SKILL.md` 鈥?Coercer |
| "NetExec / CrackMapExec / nxc" | `pentest-tools/SKILL.md` 鈥?network service enumeration |
| "AI auto pentest / MCP security" | `pentest-tools/SKILL.md` 鈥?HexStrike AI / MetasploitMCP |
| "Swarm / swarm pentest / autonomous scan" | `pentest-tools/SKILL.md` 鈥?Pentest Swarm AI |
| "red team / HW / attack exercise" | `attack-chain/SKILL.md` 鈥?full attack chain orchestration |
| "initial breach / boundary breach" | `attack-chain/SKILL.md` 鈥?boundary breach phase |
| "close-range pentest / BadUSB / WiFi phishing" | `attack-chain/SKILL.md` 鈥?close-range section |
| "EDR bypass / evasion / AV bypass" | `attack-chain/SKILL.md` 鈥?EDR/AV evasion section |
| "phishing / social engineering" | `attack-chain/SKILL.md` 鈥?phishing section |
| "supply chain attack" | `attack-chain/SKILL.md` 鈥?supply chain section |
| "trace cleanup / anti-forensics" | `attack-chain/SKILL.md` 鈥?cleanup section |
| "full pentest / end-to-end" | `attack-chain/SKILL.md` 鈥?full chain planning |
| "from external to domain controller" | `attack-chain/SKILL.md` 鈥?cross-phase path orchestration |
| "attack surface assessment / path planning" | `attack-chain/SKILL.md` 鈥?path planning decision tree |
| "got shell, what next / post-exploitation" | `attack-chain/SKILL.md` 鈥?plan from current foothold |
| "BurpSuite / Burp proxy / intercept" | `pentest-tools/SKILL.md` + `references/burpsuite-mcp-guide.md` |
| "Burp MCP / proxy history analysis" | `pentest-tools/references/burpsuite-mcp-guide.md` 鈥?83 tools |
| "Intruder brute force / Repeater replay" | `pentest-tools/references/burpsuite-mcp-guide.md` |
| "Collaborator / OOB testing" | `pentest-tools/references/burpsuite-mcp-guide.md` |
| "API security / GraphQL / JWT attack" | `api-security/SKILL.md` 鈥?REST/GraphQL/JWT/OAuth |
| "supply chain security / SBOM / SCA" | `supply-chain-security/SKILL.md` 鈥?Trivy/Syft/Gitleaks |
| "iOS reverse / IPA / Mach-O" | `mobile-reverse/SKILL.md` 鈥?class-dump/Hopper/Frida iOS |
| "Objection / SSL Pinning bypass" | `mobile-reverse/SKILL.md` 鈥?dynamic instrumentation |
| "YARA / malware detection rules" | `malware-analysis/SKILL.md` 鈥?YARA/Sigma/IOC |
| "N-day / patch diff / CVE reproduction" | `binary-diff/SKILL.md` 鈥?ghidriff/Diaphora/DeepDiff |
| "MBA simplification / mixed boolean-arithmetic / 琛ㄨ揪寮忓寲绠€" | `reverse-engineering/references/ollvm-deobfuscation.md` 鈥?SiMBA/D-810 |
| "opaque predicate / 涓嶉€忔槑璋撹瘝鍘婚櫎" | `reverse-engineering/references/ollvm-deobfuscation.md` 鈥?绗﹀彿鎵ц鍘婚櫎 |
| "Hikari deobfuscate / 瀛楃涓插姞瀵嗘仮澶? | `reverse-engineering/references/ollvm-deobfuscation.md` 鈥?Hikari 鍙樼澶勭悊 |
| "pwn / stack overflow / ROP / ret2libc" | `reverse-engineering/patterns-ctf*.md` + pwntools |
| "Agent not working / AI lazy / skip steps" | `llm-security/references/agent-obedience-engineering.md` |
| "MSF stuck / orphan process / MSF protocol" | `pentest-tools/references/msf-protocol.md` |
| "anonymize / placeholder / writeup desensitize" | `field-journal/anonymization.md` |
| "Hydra / online brute force" | `pentest-tools/SKILL.md` 鈥?online password attack |
| "Metasploit / msfconsole / exploit" | `pentest-tools/SKILL.md` 鈥?exploitation framework |
| "Wireshark / packet analysis / PCAP" | `pentest-tools/SKILL.md` + `reverse-engineering/platforms.md` |
| "BurpSuite / web proxy / intercept" | `pentest-tools/SKILL.md` 鈥?web proxy |
| "ProxyCat / proxy pool / IP rotation" | `pentest-tools/SKILL.md` 鈥?proxy management |

## By Toolchain

| Tool | Related Module |
|------|---------------|
| IDA Pro (idapro_*) | `ida-reverse/` 鈥?MCP HTTP server + 72 tools |
| radare2 (r2/rabin2/rasm2) | `radare2/` 鈥?CLI + recon.ps1 |
| jadx / apktool | `apk-reverse/` 鈥?decode.ps1 / manifest-summary.ps1 |
| Frida | `reverse-engineering/tools-dynamic.md` |
| GDB / GEF / pwndbg / rr | `reverse-engineering/tools.md` |
| Ghidra (headless) | `reverse-engineering/tools.md` + Ghidra MCP |
| angr / Qiling / Unicorn | `reverse-engineering/tools-dynamic.md` |
| D-810 / d810-ng | `reverse-engineering/references/ollvm-deobfuscation.md` 鈥?IDA Pro 鍙嶆贩娣嗘彃浠讹紝OLLVM/Tigress/Hodur/Approov + Z3 SMT |
| obpo-plugin | `reverse-engineering/references/ollvm-deobfuscation.md` 鈥?Hex-Rays microcode 浜戞彃浠讹紝鏁堟灉鏈€寮?|
| ollvm-unflattener (Miasm) / ollvm-breaker (Binary Ninja) | `reverse-engineering/references/ollvm-deobfuscation.md` 鈥?鏃?IDA 鍦烘櫙 / BN 鍦烘櫙 |
| DeObfBR | `reverse-engineering/references/ollvm-deobfuscation.md` 鈥?BR 闂存帴鍒嗘敮娣锋穯涓撻」 |
| deflat (QuarksLab) / angr symbol | `reverse-engineering/references/ollvm-deobfuscation.md` 鈥?鎺у埗娴佸钩鍧﹀寲鍘婚櫎 |
| GOOMBA (Ghidra) | `reverse-engineering/references/ollvm-deobfuscation.md` 鈥?Ghidra P-Code 鍙嶆贩娣?|
| BinDiff / Diaphora | `reverse-engineering/tools-advanced.md` |
| anything-analyzer MCP | Port 23816 MCP server (browser + HTTP capture + AI analysis) |
| jshookmcp | `js-reverse/` enhancement MCP for browser/CDP/Hook/Network/SourceMap/AST |
| agent-browser / Playwright | `browser-automation/` 鈥?browser automation |
| OpenReverse (UIA/CUA) | `browser-automation/` 鈥?Windows desktop automation |
| Cheat Engine / x64dbg / ReClass | `reverse-engineering/` 鈥?game memory analysis (seed-014) |
| dnSpyEx / ILSpy / de4dot / dnlib | `dotnet-reverse/` 鈥?.NET/C# 鎵樼绋嬪簭閫嗗悜 + 鑴辨贩娣?|
| dnSpy MCP | `dotnet-reverse/references/sharp-tools.md` 鈥?AI 鐩存帴鎿嶄綔 dnSpy锛坉ecompile / IL inspection锛墊
| IL2CPP Dumper / dnSpy | `reverse-engineering/` 鈥?Unity/Mono game reverse (seed-014) |
| LLM symbol migration / BinDiff alternative | `binary-diff/` 鈥?cross-version batch migration |
| Nmap / Masscan | `pentest-tools/` 鈥?port scan, service identification |
| Nuclei / ZAP / Nikto | `pentest-tools/` 鈥?vulnerability scanning |
| SQLMap / FFUF / Gobuster | `pentest-tools/` 鈥?web pentest (injection/brute force) |
| SSTImap | `pentest-tools/` 鈥?SSTI auto-detection |
| XSStrike | `pentest-tools/` 鈥?advanced XSS scanning |
| Hashcat / John / Hydra | `pentest-tools/` 鈥?password cracking |
| Metasploit / Impacket | `pentest-tools/` 鈥?exploitation framework |
| BurpSuite | `pentest-tools/` 鈥?web proxy, interception, vulnerability scanning |
| BurpSuite MCP | `pentest-tools/` 鈥?83-tool AI full control, see `references/burpsuite-mcp-guide.md` |
| ProxyCat | `pentest-tools/` 鈥?proxy pool management & IP rotation |
| Cobalt Strike / Sliver / Havoc | `attack-chain/` 鈥?C2 framework |
| pentestMCP (Docker) | `pentest-tools/` 鈥?20+ tools one-click MCP |
| Mermaid / Graphviz / PlantUML | `diagram-generator/` 鈥?diagram generation |
| garak / PyRIT / promptfoo | `llm-security/` 鈥?LLM red team testing |
| Trivy / Syft / Gitleaks / OSV-Scanner | `supply-chain-security/` 鈥?supply chain scanning |
| Objection / Frida iOS / class-dump | `mobile-reverse/` 鈥?iOS dynamic analysis |

Check `tool-index.md` for actual tool availability, paths, and versions. NEVER guess paths.

---

## Route Not Matched 鈥?Handling

If the current task doesn't match any table above, **do NOT force-fit into existing skill**:

1. Check if it's an edge case of an existing skill (can extend coverage)
2. If truly new type, proactively propose new skill to user:
   - Suggested skill name and coverage
   - Required toolchain
   - Relationship to existing skills
3. User confirms 鈫?execute per `CONTRIBUTING.md`
4. After creation, update this routing matrix

**AI does NOT need to wait for user to discover the gap. Route failure IS the signal to propose a new skill.**

## Path Crossing (Cross-Module Scenarios)

Some tasks span multiple modules. Common crossings:

```
APK Reverse Path:
  apk-reverse/decode.ps1 鈫?Java layer analysis
  鈫?If core is in .so
  ida-reverse/ or radare2/ 鈫?.so analysis
  鈫?If dynamic verification needed
  apk-reverse/frida-run.ps1 鈫?Frida Hook

Frontend JS Reverse Path:
  js-reverse/Observe 鈫?locate target request
  鈫?Need stronger browser/CDP/Hook/Network capability
  jshookmcp 鈫?runtime sampling, breakpoints, interception, SourceMap/AST
  鈫?After confirming entry function
  js-reverse/Rebuild 鈫?Node local reproduction
  鈫?Need environment patching
  js-reverse/references/env-patching.md

Binary Reverse Path:
  radare2/recon.ps1 鈫?quick reconnaissance
  鈫?Deep analysis
  ida-reverse/ 鈫?IDA decompile
  鈫?Dynamic verification
  reverse-engineering/tools-dynamic.md 鈫?Frida/GDB

CTF Competition Path (via CTF-Sandbox-Orchestrator):
  ctf-sandbox-orchestrator/SKILL.md 鈫?build sandbox model
  鈫?Route by dominant evidence
  competition-web-runtime/ or competition-reverse-pwn/ or competition-identity-windows/
  鈫?Blocked 鈫?return to master
  ctf-sandbox-orchestrator 鈫?re-route

Web Pentest + BurpSuite MCP Path:
  browser-automation/ 鈫?auto-browse target with Burp proxy
  鈫?Traffic captured
  burpsuite MCP proxy_history 鈫?AI analyzes all requests
  鈫?Suspicious endpoints found
  burpsuite MCP intruder_attack 鈫?automated enumeration
  鈫?Vulnerability confirmed
  docs-generator/ 鈫?generate pentest report
```
