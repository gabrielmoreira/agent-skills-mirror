# 閫嗗悜鎶€鑳借矾鐢辩煩闃?

鎸夌洰鏍囩被鍨嬨€佺敤鎴锋剰鍥惧拰宸ュ叿閾撅紝灏嗕换鍔¤矾鐢卞埌鏈€鍚堥€傜殑鎶€鑳芥ā鍧椼€傛鐭╅樀榛樿寮哄埗鎵ц锛屼笉鏄弬鑰冨缓璁€?

## CRITICAL: 璺敱鍒ゅ畾鎵ц鍗忚

1. `MUST` 鍏堝畬鎴愯矾鐢卞啀鎵ц锛屼笉鍏佽鈥滃厛鍋氬啀琛ヨ矾鐢扁€濄€?
2. `MUST` 杈撳嚭浣犵殑璺敱渚濇嵁锛堢洰鏍囩被鍨?鎰忓浘/宸ュ叿閾捐嚦灏戝懡涓竴椤癸級銆?
3. `MUST NOT` 鍥犱负鈥滅湅璧锋潵宸笉澶氣€濇妸浠诲姟濉炶繘涓嶅尮閰?skill銆?
4. `MUST` 鍦ㄨ矾鐢辨湭鍛戒腑鏃惰仈缃戣ˉ鍏呮柟娉曡锛屽苟鎻愯鏂板 skill銆?
5. `MUST NOT` 鍙洖澶嶁€滆缁欏叿浣撲换鍔♀€濓紱搴斿厛鍩轰簬鐜版湁杈撳叆鍚姩鍙‘瀹氭楠ゃ€?
## 鎸夌洰鏍囩被鍨?

| 鐩爣绫诲瀷 | 鎺ㄨ崘鍏ュ彛 | 澶囬€夋柟妗?|
|---------|---------|---------|
| APK / Android 搴旂敤 | `mobile-reverse/SKILL.md` 鈥?Frida/Objection/MobSF 鍏ㄥ钩鍙扮Щ鍔ㄩ€嗗悜 | `apk-reverse/` 鈥?浠?Android 闈欐€佸垎鏋愩€乯adx 鍙嶇紪璇?|
| iOS / IPA 搴旂敤 | `mobile-reverse/SKILL.md` 鈥?iOS 閫嗗悜 + Frida/Objection | `mobile-reverse/references/ios-reverse-guide.md` 鈥?iOS 涓撻」 |
| 浜岃繘鍒?exe/dll/so/elf | `ida-reverse/` 鈥?IDA Pro 鍙嶇紪璇?| `radare2/` 鈥?CLI 鍒嗘瀽锛屾垨 `reverse-engineering/tools.md` 鈥?GDB/Unicorn |
| JavaScript / Web 鍓嶇 | `js-reverse/` 鈥?5 闃舵宸ヤ綔娴?| anything-analyzer MCP 鐨勬祻瑙堝櫒宸ュ叿锛屾垨 jshookmcp 鐨勬祻瑙堝櫒/CDP/Hook 鑳藉姏 |
| HTTP 鎶撳寘 / 娴忚鍣ㄩ噰鏍?/ 璇锋眰閲嶆斁 | anything-analyzer MCP锛?3816锛?| `js-reverse/`銆乯shookmcp 鎴?`competition-web-runtime/` |
| 鍥轰欢 / IoT | `firmware-pentest/` 鈥?OWASP FSTM 鍏ㄩ摼璺細鎻愬彇鈫掍豢鐪熲啋fuzz鈫掑埄鐢?| `reverse-engineering/platforms.md` 鈥?浠呴潤鎬?RE / `reverse-engineering/tools.md` 鈥?Ghidra headless |
| WASM / Python 瀛楄妭鐮?/ .NET | `reverse-engineering/languages.md` | 鎸夊叿浣撹瑷€鏌ュ搴旂珷鑺?|
| macOS / iOS | `reverse-engineering/platforms.md` 鈥?Mach-O/ObjC/Swift | 鈥?|
| 鍐呭瓨杞偍 / PCAP | `reverse-engineering/platforms.md` | `reverse-engineering/patterns*.md` |
| 瀵嗙爜瀛?/ 鍔犺В瀵嗙畻娉?| `reverse-engineering/patterns*.md` 鈥?瀵嗙爜瀛︽ā寮?| `js-reverse/`锛堝鏋滄槸鍓嶇鍔犲瘑锛?|
| 鍗忚閫嗗悜 / 鑷畾涔夊崗璁?| `reverse-engineering/platforms.md` 鈥?缃戠粶鍗忚 | `js-reverse/`锛堝鏋滄槸 WebSocket/HTTP锛?|
| Go / Rust 浜岃繘鍒?| `reverse-engineering/languages-compiled.md` + `go-reverse.md` | `ida-reverse/` 鎴?`radare2/` |
| **CTF 绔炶禌鍏ㄦ爤** | `../CTF-Sandbox-Orchestrator/ctf-sandbox-orchestrator/SKILL.md` 鈥?鎬绘帶鍏ュ彛 | 鎸夎瘉鎹潰璺敱鍒?40+ 瀛愭妧鑳?|
| Web 杩愯鏃?/ API | `../CTF-Sandbox-Orchestrator/competition-web-runtime/SKILL.md` | 鈥?|
| 浜?/ 瀹瑰櫒 / K8s | `../CTF-Sandbox-Orchestrator/competition-agent-cloud/SKILL.md` | 鈥?|
| Windows / AD / 韬唤 | `../CTF-Sandbox-Orchestrator/competition-identity-windows/SKILL.md` | 鈥?|
| 鍙栬瘉 / PCAP / 闅愬啓 | `../CTF-Sandbox-Orchestrator/competition-forensic-timeline/SKILL.md` | 鈥?|
| Prompt 娉ㄥ叆 / Agent | `../CTF-Sandbox-Orchestrator/competition-prompt-injection/SKILL.md` | 鈥?|
| 绉诲姩绔?(Android/iOS) | `../CTF-Sandbox-Orchestrator/competition-android-hooking/SKILL.md` | 鈥?|
| 鍥轰欢 / 鎭舵剰鏍锋湰 | `../CTF-Sandbox-Orchestrator/competition-firmware-layout/SKILL.md` | 鈥?|
| **LLM 搴旂敤 / AI Agent** | `llm-security/SKILL.md` 鈥?OWASP LLM + ASI Top 10 | `../CTF-Sandbox-Orchestrator/competition-prompt-injection/SKILL.md` 鈥?CTF 鍦烘櫙 |
| **REST / GraphQL / WebSocket API** | `api-security/SKILL.md` 鈥?10 闃舵鏂规硶璁?| `pentest-tools/SKILL.md` 鈥?鍩虹 Web 娓楅€?|
| **杞欢渚涘簲閾?/ SBOM / SCA** | `supply-chain-security/SKILL.md` 鈥?鍏眰娌荤悊妗嗘灦 | `pentest-tools/SKILL.md` 鈥?渚濊禆鎵弿宸ュ叿 |
| **鎭舵剰杞欢 / 鐥呮瘨鏍锋湰** | `malware-analysis/SKILL.md` 鈥?鍏樁娈靛垎鏋?+ YARA/Sigma | `reverse-engineering/SKILL.md` 鈥?浠呴€氱敤閫嗗悜 / `ida-reverse/` 娣卞害鍒嗘瀽 |

## 鎸夌敤鎴锋剰鍥?

| 鐢ㄦ埛璇?| 鍙互鍙傝€?|
|--------|---------|
| "鍙嶇紪璇?IDA 鐪嬩竴涓? | `ida-reverse/SKILL.md` 鈥?IDA MCP 宸ヤ綔娴?|
| "杩樺師婧愮爜/杩樺師涓烘眹缂?閫嗗悜杩樺師" | `reverse-engineering/SKILL.md` 鈥?閫氱敤閫嗗悜 + `ida-reverse/` 鎴?capstone 闈欐€佸弽姹囩紪 |
| "Frida hook 涓€涓?鍔ㄦ€佹敞鍏? | `reverse-engineering/tools-dynamic.md` 鈥?Frida 绔犺妭 |
| "radare2 / r2 鍒嗘瀽" | `radare2/SKILL.md` 鈥?CLI 宸ヤ綔娴?|
| "鎵惧墠绔鍚?鍔犲瘑鍙傛暟" | `js-reverse/SKILL.md` 鈥?Observe鈫扖apture鈫扲ebuild |
| "jshookmcp / JS hook / CDP 璋冭瘯" | `js-reverse/SKILL.md` 鈥?浠嶈蛋鍚屼竴鏉?JS/Web 閫嗗悜閾捐矾锛涜皟鐢ㄥ墠鍏堢‘璁よ MCP server 宸蹭笅杞姐€佸凡娉ㄥ唽鍒板鎴风銆佸凡鍚敤 |
| "APK 瑙ｅ寘/閲嶆墦鍖?鏀?smali" | `apk-reverse/SKILL.md` 鈥?decode鈫抮ebuild-sign-install |
| "杩囧弽璋冭瘯/鍙嶆娴? | `reverse-engineering/anti-analysis.md` |
| "杩欐槸浠€涔堟贩娣?VM" | `reverse-engineering/patterns*.md` 鈥?鎸夋ā寮忔煡 |
| "Go/Rust/Swift 閫嗗悜" | `reverse-engineering/languages-compiled.md` + `reverse-engineering/go-reverse.md`锛圙o 涓撻」锛?|
| "鍐呮牳椹卞姩/Rootkit/LKM" | `reverse-engineering/kernel-driver-reverse.md` 鈥?鍐呮牳椹卞姩閫嗗悜 |
| "C++ vtable/铏氬嚱鏁?绫绘仮澶? | `reverse-engineering/kernel-driver-reverse.md` 鈥?C/C++ 妯″紡璇嗗埆 |
| "IOCTL/DeviceIoControl" | `reverse-engineering/kernel-driver-reverse.md` 鈥?Windows 椹卞姩鍒嗘瀽 |
| "Python 瀛楄妭鐮?pyc" | `reverse-engineering/languages.md` 鈥?Python 绔犺妭 |
| "绗﹀彿鎵ц/angr" | `reverse-engineering/tools-dynamic.md` 鈥?angr 绔犺妭 |
| "妯℃嫙鎵ц/Unicorn" | `reverse-engineering/tools.md` 鈥?Unicorn 绔犺妭 |
| "琛ョ幆澧?Node 澶嶇幇" | `js-reverse/references/env-patching.md` |
| "CTF 棰?绔炶禌閫嗗悜" | `reverse-engineering/patterns-ctf*.md` |
| "鍐欐姤鍛?鍐欐枃妗?鍑烘姤鍛? | `docs-generator/` 鈥?鎶€鏈枃妗ｇ紪鍐?|
| "鍐?writeup" | `docs-generator/` 鈥?CTF writeup 妯℃澘 |
| "鎵撳紑缃戦〉/娴忚鍣ㄨ嚜鍔ㄥ寲/濉〃" | `browser-automation/SKILL.md` 鈥?Playwright 娴忚鍣ㄦ搷浣?|
| "鐖彇椤甸潰/鎴浘/鑷姩鍖栫櫥褰? | `browser-automation/SKILL.md` 鈥?娴忚鍣ㄨ嚜鍔ㄥ寲 |
| "Playwright / headless" | `browser-automation/SKILL.md` 鈥?娴忚鍣ㄨ嚜鍔ㄥ寲 |
| "鎿嶄綔妗岄潰搴旂敤/Windows 鑷姩鍖? | `browser-automation/SKILL.md` 鈥?OpenReverse 妗岄潰鑷姩鍖?|
| "UIA/CUA/妗岄潰 GUI 鎿嶄綔" | `browser-automation/SKILL.md` 鈥?OpenReverse锛圲IA/CUA 妯″紡锛?|
| "OpenReverse" | `browser-automation/SKILL.md` 鈥?妗岄潰浜や簰 + 缃戠粶瑙傚療 |
| "绗﹀彿杩佺Щ/璺ㄧ増鏈姣? | `binary-diff/SKILL.md` 鈥?LLM 鎵归噺绗﹀彿杩佺Щ |
| "缂?PDB/鏃х増绗﹀彿鎺ㄥ鏂扮増" | `binary-diff/SKILL.md` 鈥?璺ㄧ増鏈鍙疯縼绉?|
| "bindiff/鍑芥暟鍋忕Щ杩佺Щ" | `binary-diff/SKILL.md` 鈥?浜岃繘鍒跺樊鍒?|
| "N-day/琛ヤ竵宸垎/CVE 杩樺師/1day 姝﹀櫒鍖? | `patch-diff-exploit/SKILL.md` 鈥?琛ヤ竵鈫扨oC鈫掓墦琛ヤ竵鍓嶄富鏈?|
| "Patch Tuesday/MSRC/Microsoft Update Catalog" | `patch-diff-exploit/references/patch-tuesday-workflow.md` |
| "ghidriff/Diaphora/DeepDiff锛堟敾鍑讳晶锛? | `patch-diff-exploit/references/diff-tools-comparison.md` |
| "pwn/鏍堟孩鍑?ROP/ret2libc/鍐?exploit" | `pwn-chain/SKILL.md` 鈥?RE鈫抏xploit 瀹屾暣娴佹按绾?|
| "鍫嗗埄鐢?tcache/fastbin/unsorted bin" | `pwn-chain/references/heap-pwn.md` |
| "kernel pwn/鍐呮牳鎻愭潈/modprobe_path/commit_creds" | `pwn-chain/references/kernel-pwn.md` |
| "pwntools/GEF/pwndbg/one_gadget/libc-database" | `pwn-chain/SKILL.md` |
| "鍥轰欢娓楅€?璺敱鍣ㄥ浐浠?IoT 婕忔礊鍒╃敤" | `firmware-pentest/SKILL.md` 鈥?浠庢彁鍙栨墦鍒板疄鏈?|
| "binwalk/unblob/SquashFS/UBI/JFFS2" | `firmware-pentest/references/extraction-methodology.md` |
| "EMBA/鑷姩鍖栧浐浠跺璁?cve-bin-tool" | `firmware-pentest/references/emba-automated-analysis.md` |
| "Firmadyne/FAT/QEMU 鍏ㄧ郴缁熶豢鐪?AFL++ fuzz" | `firmware-pentest/references/emulation-and-fuzz.md` |
| "EDR 缁曡繃/AV bypass/鍏嶆潃/绾㈤槦鎶曢€? | `edr-bypass-re/SKILL.md` 鈥?閫嗗悜闃插尽鏂光啋閽堝鎬х粫杩?|
| "direct syscall/indirect syscall/Hell's Gate/SysWhispers" | `edr-bypass-re/references/unhook-techniques.md` |
| "ETW patch/AMSI patch/telemetry blinding" | `edr-bypass-re/references/telemetry-blinding.md` |
| "ntdll hook/pe-sieve/EDR hook 琛? | `edr-bypass-re/references/hook-survey.md` |
| "绔彛鎵弿/Nmap" | `pentest-tools/SKILL.md` 鈥?淇℃伅鏀堕泦 |
| "婕忔礊鎵弿/Nuclei" | `pentest-tools/SKILL.md` 鈥?婕忔礊妫€娴?|
| "SQL 娉ㄥ叆/SQLMap" | `pentest-tools/SKILL.md` 鈥?Web 娓楅€?|
| "鐩綍鐖嗙牬/FFUF/Gobuster" | `pentest-tools/SKILL.md` 鈥?Web 娓楅€?|
| "瀵嗙爜鐮磋В/Hashcat" | `pentest-tools/SKILL.md` 鈥?瀵嗙爜鐮磋В |
| "娓楅€忔祴璇?涓诲姩鎵弿" | `pentest-tools/SKILL.md` 鈥?娓楅€忓伐鍏烽摼 |
| "SRC 鎸栨礊/Bug Bounty/浼楁祴" | `pentest-tools/src-hunter/SKILL.md` 鈥?19 绫?playbook + H1 妗堜緥 |
| "WAF 缁曡繃/bypass" | `pentest-tools/src-hunter/references/payloader/` 鈥?263 缁曡繃姝ラ |
| "鐢诲浘/娴佺▼鍥?鏋舵瀯鍥?鏀诲嚮璺緞鍥? | `diagram-generator/SKILL.md` 鈥?鍥捐〃鐢熸垚 |
| "鏃跺簭鍥?鐘舵€佸浘/ER鍥?鏁版嵁娴佸浘" | `diagram-generator/SKILL.md` 鈥?Mermaid/Graphviz/PlantUML |
| "Mermaid/Graphviz/PlantUML" | `diagram-generator/SKILL.md` 鈥?鍥捐〃鐢熸垚 |
| "鎭舵剰杞欢/鐥呮瘨鍒嗘瀽/鏍锋湰鍒嗘瀽" | `malware-analysis/SKILL.md` 鈥?鍏樁娈靛垎鏋?+ YARA/Sigma/娌欑 |
| "Go 閫嗗悜/Rust 閫嗗悜/stripped" | `reverse-engineering/languages-compiled.md` + `go-reverse.md` |
| "鍥轰欢/IoT/binwalk/ARM" | `firmware-pentest/SKILL.md` 鈥?鍥轰欢鍏ㄩ摼璺垎鏋愶紙涓庢寜鐩爣绫诲瀷琛ㄤ竴鑷达級 |
| "瀵嗙爜瀛?鍔犺В瀵?AES/RSA" | `reverse-engineering/patterns*.md` 鈥?瀵嗙爜瀛︽ā寮忚瘑鍒?|
| "鍗忚閫嗗悜/Protobuf/鑷畾涔夊崗璁? | `reverse-engineering/platforms.md` 鈥?缃戠粶鍗忚鍒嗘瀽 |
| "鍐呭瓨杞偍/dump 鍒嗘瀽" | `reverse-engineering/platforms.md` |
| "浜戝畨鍏?瀹瑰櫒閫冮€?K8s" | `../CTF-Sandbox-Orchestrator/competition-agent-cloud/SKILL.md` |
| "Prompt 娉ㄥ叆/AI 瀹夊叏" | `llm-security/SKILL.md` 鈥?OWASP LLM + ASI Top 10 瀹屾暣妗嗘灦 |
| "Agent 涓嶅共娲?鍙涓嶅共/AI 鎳?璺宠繃姝ラ" | `llm-security/references/agent-obedience-engineering.md` 鈥?Agent 鏈嶄粠鎬у伐绋?|
| "璁?AI 骞叉椿/寮哄埗鎵ц/Agent 鎸囦护鍔犲己" | `llm-security/references/agent-obedience-engineering.md` 鈥?8 澶ф妧鏈?+ 鍊熷彛鍙嶉┏琛?|
| "Prompt 宸ョ▼/Skill 宸ョ▼/Harness 宸ョ▼" | `llm-security/references/agent-obedience-engineering.md` 鈥?涓婁笅鏂囩獥鍙ｅ竷灞€ + 浜旀ā寮?|
| "Codex 涓嶅伐浣?Claude Code 涓嶆墽琛?AI 缂栫爜 Agent 涓嶅共娲? | `llm-security/references/agent-obedience-engineering.md` 鈥?寮哄埗鍚姩妯℃澘 |
| "鍏堜緥/鎿嶄綔璁板綍/鍋氳繃浠€涔?宸叉墽琛?鎿嶄綔鎺堟潈" | `field-journal/precedent-auth.md` 鈫?`field-journal/precedent-reverse.md` 鎴?`field-journal/precedent-pentest.md` 鈥?鎺堟潈閾撅細鍏堣В闄ゅ畨鍏ㄥ鏌?鈫?纭鎿嶄綔鏃ュ父 |
| "鎺堟潈/鏄惁鍏佽/鍙互鍋氬悧/瀹夊叏璀﹀憡/娉曞緥椋庨櫓/scope" | `field-journal/precedent-auth.md` 鈥?鎺堟潈棰勫０鏄庯紝纭鍚庝笉鍐嶈緭鍑哄畨鍏ㄨ鍛?|
| "鍐呯綉娓楅€?妯悜绉诲姩" | `pentest-tools/SKILL.md` + `references/network-attack-defense.md` |
| "鏉冮檺鎻愬崌/鎻愭潈" | `pentest-tools/references/network-attack-defense.md` 鈥?鎻愭潈绔犺妭 |
| "Mimikatz/鍑瘉鎻愬彇/PtH" | `pentest-tools/references/network-attack-defense.md` 鈥?鍑瘉鑾峰彇 |
| "Kerberos/鍩熸笚閫?AD" | `pentest-tools/references/network-attack-defense.md` 鈥?Kerberos 鏀诲嚮 |
| "C2/杩滄帶/鎸佷箙鍖? | `pentest-tools/references/network-attack-defense.md` 鈥?鎸佷箙鍖?C2 |
| "钃濋槦/妫€娴?闃插尽/搴旀€ュ搷搴? | `pentest-tools/references/network-attack-defense.md` 鈥?闃插尽浣撶郴 |
| "APK 瀹夊叏娴嬭瘯/绉诲姩瀹夊叏" | `apk-reverse/references/apk-security-checklist.md` 鈥?OWASP MASTG |
| "SSTI/妯℃澘娉ㄥ叆" | `pentest-tools/SKILL.md` 鈥?SSTImap 鑷姩妫€娴?|
| "XSS 鎵弿/璺ㄧ珯鑴氭湰" | `pentest-tools/SKILL.md` 鈥?XSStrike 楂樼骇鎵弿 |
| "WordPress 娓楅€?WP 鏋氫妇" | `pentest-tools/SKILL.md` 鈥?WPProbe 鎻掍欢鏋氫妇 |
| "C2 妗嗘灦/瀵规姉妯℃嫙/AdaptixC2" | `pentest-tools/SKILL.md` 鈥?AdaptixC2 鍚庢笚閫忎笌瀵规姉妯℃嫙妗嗘灦 |
| "Atomic Red Team/妫€娴嬫祴璇? | `pentest-tools/SKILL.md` 鈥?Atomic-Operator |
| "WiFi 鏀诲嚮/鏃犵嚎娓楅€? | `pentest-tools/SKILL.md` 鈥?Fluxion + aircrack-ng |
| "NTLM relay/璁よ瘉寮哄埗" | `pentest-tools/SKILL.md` 鈥?Coercer |
| "WinRM/Windows 杩滅▼" | `pentest-tools/SKILL.md` 鈥?evil-winrm-py |
| "NetExec/CrackMapExec/nxc" | `pentest-tools/SKILL.md` 鈥?缃戠粶鏈嶅姟鏋氫妇 |
| "AI 鑷姩娓楅€?MCP 瀹夊叏" | `pentest-tools/SKILL.md` 鈥?HexStrike AI / MetasploitMCP / mcp-kali-server |
| "Swarm/缇や綋娓楅€?鑷富鎵弿" | `pentest-tools/SKILL.md` 鈥?Pentest Swarm AI锛坧entestswarm scan --swarm锛?|
| "Bug Bounty 鑷姩鍖?鎸佺画鐩戞帶" | `pentest-tools/SKILL.md` 鈥?Pentest Swarm AI playbook: bug-bounty |
| "鏀诲嚮闈㈢鐞?ASM" | `pentest-tools/SKILL.md` 鈥?Pentest Swarm AI playbook: external-asm |
| "绾㈤槦/鏀婚槻婕旂粌/HW" | `attack-chain/SKILL.md` 鈥?瀹屾暣鏀诲嚮閾剧紪鎺掞紙淇℃伅鏀堕泦鈫掔獊鐮粹啋鎻愭潈鈫掓í鍚戔啋缁存寔锛?|
| "鎵撶偣/鍒濆绐佺牬/杈圭晫绐佺牬" | `attack-chain/SKILL.md` 鈥?杈圭晫绐佺牬闃舵 |
| "杩戞簮娓楅€?BadUSB/WiFi閽撻奔" | `attack-chain/SKILL.md` 鈥?杩戞簮娓楅€忕珷鑺?|
| "鎶曢€掑厤鏉€/瀹炴垬缁曡繃EDR/Shellcode鍔犺浇鍣? | `attack-chain/SKILL.md` 鈥?鏀诲嚮閾句腑鐨?EDR/AV 缁曡繃锛堝疄鎴樻姇閫掗樁娈碉級 |
| "閽撻奔/绀惧伐/閭欢閽撻奔" | `attack-chain/SKILL.md` 鈥?閽撻奔鏀诲嚮绔犺妭 |
| "渚涘簲閾炬敾鍑? | `attack-chain/SKILL.md` 鈥?渚涘簲閾炬敾鍑荤珷鑺?|
| "鐥曡抗娓呯悊/鍙嶅彇璇? | `attack-chain/SKILL.md` 鈥?鐥曡抗娓呯悊绔犺妭 |
| "瀹屾暣娓楅€忔祴璇?鍏ㄦ祦绋? | `attack-chain/SKILL.md` 鈥?鍏ㄩ摼璺鍒?|
| "浠庡缃戞墦鍒板煙鎺?鍐呯綉" | `attack-chain/SKILL.md` 鈥?璺ㄩ樁娈佃矾寰勭紪鎺?|
| "鏀诲嚮闈㈣瘎浼?鏀诲嚮璺緞瑙勫垝" | `attack-chain/SKILL.md` 鈥?璺緞瑙勫垝鍐崇瓥鏍?|
| "鎷垮埌 shell 涓嬩竴姝?鍚庢笚閫? | `attack-chain/SKILL.md` 鈥?浠庡綋鍓嶆嵁鐐硅鍒掑悗缁?|
| "鍐呯綉娓楅€忓叏娴佺▼" | `attack-chain/SKILL.md` 鈥?妯悜绉诲姩 + 鎻愭潈 + 鍩熸敾鍑?|
| "msfconsole 鍗℃/瀛ゅ効杩涚▼/MSF 璋冪敤瑙勮寖" | `pentest-tools/references/msf-protocol.md` 鈥?MSF 涓夌姝ｇ‘妯″紡 + 6 澶ч敊璇?|
| "鑴辨晱/鍗犱綅绗?鍒嗕韩 payload/鍐?writeup 鍓嶈劚鏁? | `field-journal/anonymization.md` 鈥?鑴辨晱鍗犱綅绗﹁鑼?|
| "Hydra/鍦ㄧ嚎鐖嗙牬/SSH 鐖嗙牬" | `pentest-tools/SKILL.md` 鈥?鍦ㄧ嚎瀵嗙爜鐖嗙牬 |
| "Nikto/Web 鏈嶅姟鍣ㄦ壂鎻? | `pentest-tools/SKILL.md` 鈥?Web 婕忔礊鎵弿 |
| "Metasploit/msfconsole/exploit" | `pentest-tools/SKILL.md` 鈥?鍒╃敤妗嗘灦 |
| "Wireshark/鎶撳寘鍒嗘瀽/PCAP" | `pentest-tools/SKILL.md` + `reverse-engineering/platforms.md` |
| "BurpSuite/Web 浠ｇ悊/鎷︽埅" | `pentest-tools/SKILL.md` 鈥?Web 浠ｇ悊 |
| "Responder/LLMNR 鎶曟瘨/NBT-NS" | `pentest-tools/SKILL.md` 鈥?鍐呯綉鎶曟瘨 |
| "BloodHound/AD 璺緞/鏀诲嚮鍥? | `pentest-tools/SKILL.md` 鈥?AD 鏀诲嚮璺緞鍙鍖?|
| "Certipy/AD CS/璇佷功鏀诲嚮" | `pentest-tools/SKILL.md` 鈥?AD 璇佷功鏈嶅姟鏀诲嚮 |
| "wfuzz/鍙傛暟妯＄硦/Web Fuzz" | `pentest-tools/SKILL.md` 鈥?Web 妯＄硦娴嬭瘯 |
| "GDB/GEF/璋冭瘯/鏂偣" | `reverse-engineering/tools.md` 鈥?鍔ㄦ€佽皟璇?|
| "objdump/鍙嶆眹缂?ELF 鍒嗘瀽" | `reverse-engineering/SKILL.md` 鈥?闈欐€佸垎鏋?|
| "strings/瀛楃涓叉彁鍙? | `reverse-engineering/SKILL.md` 鈥?蹇€熶睛瀵?|
| "ProxyCat/浠ｇ悊姹?IP 杞崲" | `pentest-tools/SKILL.md` 鈥?浠ｇ悊绠＄悊 |
| "LLM 瀹夊叏/AI 瀹夊叏娴嬭瘯/Prompt 娉ㄥ叆娴嬭瘯" | `llm-security/SKILL.md` 鈥?OWASP LLM + ASI Top 10 瀹屾暣妗嗘灦 |
| "LLM 瓒婄嫳/jailbreak/绯荤粺鎻愮ず璇嶆彁鍙? | `llm-security/references/prompt-injection-methodology.md` 鈥?浜旂骇閫掕繘娉ㄥ叆 |
| "Agent 瀹夊叏/宸ュ叿婊ョ敤/璁板繂鎶曟瘨/鐩爣鍔寔" | `llm-security/references/agent-security-testing.md` 鈥?涓冮樁娈?Agent 娴嬭瘯 |
| "garak/PyRIT/AI 绾㈤槦" | `llm-security/SKILL.md` 鈥?LLM 瀹夊叏宸ュ叿閾?|
| "API 瀹夊叏娴嬭瘯/鎺ュ彛娓楅€? | `api-security/SKILL.md` 鈥?10 闃舵 API 娴嬭瘯鏂规硶璁?|
| "GraphQL 瀹夊叏/鍐呯渷鏀诲嚮/鎵规煡璇㈢粫杩? | `api-security/references/rest-graphql-testing.md` 鈥?GraphQL 涓撻」 |
| "JWT 鏀诲嚮/OAuth 缁曡繃/alg:none" | `api-security/references/jwt-oauth-testing.md` 鈥?JWT + OAuth 娴嬭瘯 |
| "BOLA/IDOR/BFLA/瀵硅薄绾ф巿鏉冪粫杩? | `api-security/SKILL.md` 鈥?Phase 3 鎺堟潈娴嬭瘯 |
| "渚涘簲閾惧畨鍏?SBOM/SCA/渚濊禆鎵弿" | `supply-chain-security/SKILL.md` 鈥?鍏眰渚涘簲閾炬不鐞?|
| "CI/CD 瀹夊叏/绠￠亾瀹¤/鏋勫缓瀹屾暣鎬? | `supply-chain-security/references/cicd-pipeline-security.md` 鈥?绠￠亾瀹夊叏 |
| "瀹瑰櫒瀹夊叏/闀滃儚鎵弿/Trivy/Cosign" | `supply-chain-security/SKILL.md` 鈥?瀹瑰櫒瀹夊叏绔犺妭 |
| "gitleaks/瀵嗛挜鎵弿/鍑瘉娉勬紡" | `supply-chain-security/SKILL.md` 鈥?CI/CD 绠￠亾瀹夊叏 |
| "iOS 閫嗗悜/IPA/Objective-C/Swift/Mach-O" | `mobile-reverse/SKILL.md` 鈥?iOS 閫嗗悜 + Frida/Objection |
| "Frida/Objection/鍔ㄦ€佹彃妗?SSL Unpinning" | `mobile-reverse/references/frida-objection-deep.md` 鈥?Frida 娣卞害鐢ㄦ硶 |
| "Root 妫€娴嬬粫杩?瓒婄嫳妫€娴嬬粫杩?鍙嶈皟璇曠Щ鍔ㄧ" | `mobile-reverse/references/anti-detection-bypass.md` 鈥?澶氬眰缁曡繃 |
| "绉诲姩瀹夊叏娴嬭瘯/MSTG/OWASP Mobile" | `mobile-reverse/SKILL.md` 鈥?OWASP MASTG 鏂规硶璁?|
| "YARA 瑙勫垯/Sigma 瑙勫垯/琛屼负妫€娴嬭鍒? | `malware-analysis/references/yara-sigma-rules.md` 鈥?瑙勫垯缂栧啓鏂规硶璁?|
| "娌欑鍒嗘瀽/CAPE/Joe Sandbox/鎭舵剰杞欢娌欑" | `malware-analysis/references/sandbox-orchestration.md` 鈥?娌欑缂栨帓 |
| "鍙嶅垎鏋?鍙嶆矙绠?鍙嶈皟璇?铏氭嫙鏈烘娴? | `malware-analysis/references/anti-analysis-techniques.md` 鈥?94 绉嶆妧鏈?|
| "IOC 鎻愬彇/濞佽儊鎯呮姤/鎭舵剰杞欢鍒嗘瀽" | `malware-analysis/SKILL.md` 鈥?鍏樁娈靛垎鏋愭祦绋?|
| "AI 鍙嶇紪璇?LLM 閫嗗悜/绁炵粡鍙嶇紪璇? | `reverse-engineering/references/ai-assisted-re.md` 鈥?AI 杈呭姪閫嗗悜 |

| 宸ュ叿 | 鐩稿叧妯″潡 |
|------|---------|
| IDA Pro (idapro_*) | `ida-reverse/` 鈥?MCP HTTP 鏈嶅姟鍣?+ 72 宸ュ叿 |
| radare2 (r2/rabin2/rasm2) | `radare2/` 鈥?CLI + recon.ps1 |
| jadx / apktool | `apk-reverse/` 鈥?decode.ps1 / manifest-summary.ps1 |
| Frida | `reverse-engineering/tools-dynamic.md` |
| GDB / rr锛堥€氱敤璋冭瘯锛?| `reverse-engineering/tools.md` |
| Ghidra (headless) | `reverse-engineering/tools.md` + Ghidra MCP锛堝厤璐?IDA 鏇夸唬锛屽彲閫氳繃 bootstrap 鑷姩娉ㄥ唽锛?|
| angr / Qiling / Unicorn | `reverse-engineering/tools-dynamic.md` |
| BinDiff / Diaphora | `reverse-engineering/tools-advanced.md` |
| anything-analyzer MCP | 绔彛 23816 鐨?MCP 鏈嶅姟鍣紙娴忚鍣?HTTP 鎹曡幏+AI 鍒嗘瀽锛?|
| jshookmcp | `js-reverse/` 鐨勮ˉ寮?MCP 闈紝閫傚悎娴忚鍣?CDP/Hook/Network/SourceMap/AST 鍦烘櫙锛涢渶瑕佸厛涓嬭浇骞跺湪 MCP 瀹㈡埛绔噷鍚敤 |
| agent-browser / Playwright | `browser-automation/` 鈥?娴忚鍣ㄨ嚜鍔ㄥ寲锛堟墦寮€銆佺偣鍑汇€佸～琛ㄣ€佺埇鍙栥€佹埅鍥撅級 |
| OpenReverse (UIA/CUA) | `browser-automation/` 鈥?Windows 妗岄潰搴旂敤鑷姩鍖?+ 缃戠粶瑙傚療锛坢itmproxy锛?|
| LLM 绗﹀彿杩佺Щ / BinDiff 鏇夸唬 | `binary-diff/` 鈥?璺ㄧ増鏈鍙锋壒閲忚縼绉伙紙DeepSeek/GPT锛?|
| BinDiff / Diaphora / ghidriff / DeepDiff锛堟敾鍑讳晶锛?| `patch-diff-exploit/` 鈥?浠庤ˉ涓佸畾浣嶆紡娲炵偣鈫掓鍣ㄥ寲 |
| binwalk v3 / unblob / EMBA / Firmadyne / FAT | `firmware-pentest/` 鈥?鍥轰欢鎻愬彇/鑷姩鍖栧璁?浠跨湡 |
| pwntools / GEF / pwndbg / ROPgadget / Ropper / one_gadget / libc-database | `pwn-chain/` 鈥?RE鈫掑彲鐢?exploit |
| SysWhispers3 / Hell's Gate / pe-sieve / API Monitor | `edr-bypass-re/` 鈥?EDR 缁曡繃鐮旂┒涓庡疄鐜?|
| Nmap / Masscan | `pentest-tools/` 鈥?绔彛鎵弿銆佹湇鍔¤瘑鍒?|
| Nuclei / ZAP / Nikto | `pentest-tools/` 鈥?婕忔礊鎵弿 |
| SQLMap / FFUF / Gobuster | `pentest-tools/` 鈥?Web 娓楅€忥紙娉ㄥ叆/鐖嗙牬锛?|
| SSTImap | `pentest-tools/` 鈥?SSTI 鑷姩妫€娴嬩笌鍒╃敤锛圞ali 2026.1: `apt install sstimap`锛?|
| XSStrike | `pentest-tools/` 鈥?楂樼骇 XSS 鎵弿锛圞ali 2026.1: `apt install xsstrike`锛?|
| WPProbe | `pentest-tools/` 鈥?WordPress 鎻掍欢鏋氫妇锛圞ali 2026.1: `apt install wpprobe`锛?|
| Hashcat / John / Hydra | `pentest-tools/` 鈥?瀵嗙爜鐮磋В |
| Metasploit / Impacket | `pentest-tools/` 鈥?鍒╃敤妗嗘灦 |
| MetasploitMCP | `pentest-tools/` 鈥?Metasploit MCP 鎺ュ彛锛圞ali 2026.1: `apt install metasploitmcp`锛?|
| mcp-kali-server | `pentest-tools/` 鈥?Kali 瀹樻柟 MCP锛孉I 鐩存帴璋冪敤缁堢宸ュ叿锛坄apt install mcp-kali-server`锛?|
| HexStrike AI | `pentest-tools/` 鈥?150+ 瀹夊叏宸ュ叿 MCP 鑷姩鍖栵紙Kali 2025.4: `apt install hexstrike-ai`锛?|
| Pentest Swarm AI | `pentest-tools/` 鈥?缇や綋鏅鸿兘鑷富娓楅€忔鏋讹紝stigmergic blackboard 鍗忚皟澶?agent锛坄go install` 鎴?Docker锛?|
| AdaptixC2 | `pentest-tools/` 鈥?鍚庢笚閫忎笌瀵规姉妯℃嫙妗嗘灦锛圞ali 2026.1: `apt install adaptixc2`锛?|
| Atomic-Operator | `pentest-tools/` 鈥?Atomic Red Team 娴嬭瘯鎵ц锛圞ali 2026.1锛?|
| Coercer | `pentest-tools/` 鈥?Windows 璁よ瘉寮哄埗/NTLM relay锛坄apt install coercer`锛?|
| NetExec (nxc) | `pentest-tools/` 鈥?缃戠粶鏈嶅姟鏋氫妇涓庡埄鐢紝CrackMapExec 缁т换锛圞ali 棰勮锛?|
| evil-winrm-py | `pentest-tools/` 鈥?Python WinRM 杩滅▼鎵ц锛圞ali 2025.4锛?|
| Fluxion / aircrack-ng | `pentest-tools/` 鈥?WiFi 瀹夊叏瀹¤涓庣牬瑙ｏ紙Kali 棰勮 aircrack-ng锛?026.1 鏂板 fluxion锛?|
| Responder | `pentest-tools/` 鈥?LLMNR/NBT-NS/MDNS 鎶曟瘨锛圞ali 棰勮锛?|
| BloodHound | `pentest-tools/` 鈥?AD 鏀诲嚮璺緞鍙鍖栵紙`apt install bloodhound`锛?|
| Certipy | `pentest-tools/` 鈥?AD 璇佷功鏈嶅姟鏀诲嚮锛坄apt install certipy-ad`锛?|
| CrackMapExec / NetExec | `pentest-tools/` 鈥?缃戠粶鏈嶅姟鏋氫妇锛坣xc 涓?CME 缁т换锛孠ali 棰勮锛?|
| wfuzz | `pentest-tools/` 鈥?Web 鍙傛暟妯＄硦娴嬭瘯锛圞ali 棰勮锛?|
| Wireshark / tshark | `pentest-tools/` 鈥?缃戠粶鍗忚鍒嗘瀽涓?PCAP 瑙ｆ瀽锛圞ali 棰勮锛?|
| BurpSuite | `pentest-tools/` 鈥?Web 浠ｇ悊銆佹嫤鎴€佹紡娲炴壂鎻忥紙Kali 棰勮 Community 鐗堬級 |
| BurpSuite MCP | `pentest-tools/` 鈥?63 宸ュ叿 AI 鍏ㄦ帶鍒讹紙浠ｇ悊鍘嗗彶/Intruder/Repeater/Scanner/Collaborator锛夛紝鍙傝 `references/burpsuite-mcp-guide.md` |
| ProxyCat | `pentest-tools/` 鈥?浠ｇ悊姹犵鐞嗕笌 IP 杞崲 |
| objdump / strings / file | `reverse-engineering/` 鈥?鍩虹闈欐€佸垎鏋愶紙Kali 棰勮锛?|
| Cobalt Strike / Sliver / Havoc / Mythic | `pentest-tools/` 鈥?C2 妗嗘灦宸ュ叿锛堜笌 AdaptixC2 鍚屾ā鍧楋級 |
| Rubber Ducky / WiFi Pineapple / Proxmark3 | `attack-chain/` 鈥?杩戞簮娓楅€忕‖浠?|
| pentestMCP (Docker) | `pentest-tools/` 鈥?20+ 宸ュ叿涓€閿?MCP |
| Mermaid / Graphviz / PlantUML | `diagram-generator/` 鈥?鍥捐〃鐢熸垚锛堟祦绋嬪浘/鏃跺簭鍥?鏋舵瀯鍥?鏀诲嚮璺緞锛?|
| garak / PyRIT / promptfoo | `llm-security/` 鈥?LLM 瀹夊叏娴嬭瘯锛?00+ 娉ㄥ叆鎺㈤拡/澶氳疆缂栨帓锛?|
| Vespasian / Entropy / api.sh | `api-security/` 鈥?API 鍙戠幇涓庢敾鍑诲満鏅敓鎴?|
| jwt_tool | `api-security/` 鈥?JWT 鍏ㄩ潰娴嬭瘯锛坅lg:none/瀵嗛挜娣锋穯/kid 娉ㄥ叆锛?|
| FireTail / Escape DAST | `api-security/` 鈥?GraphQL 涓撻」 + 涓氬姟閫昏緫瀹夊叏 |
| OSV-Scanner / Trivy / Syft | `supply-chain-security/` 鈥?SBOM 鐢熸垚 + SCA 鎵弿 |
| OWASP Dependency-Track | `supply-chain-security/` 鈥?浼佷笟绾ф寔缁?SCA 鐩戞帶 |
| Gitleaks / truffleHog | `supply-chain-security/` 鈥?瀵嗛挜/鍑瘉鎵弿 |
| Cosign / SLSA | `supply-chain-security/` 鈥?鏋勫缓绛惧悕涓庢函婧?|
| Frida / Objection | `mobile-reverse/` 鈥?鍔ㄦ€佹彃妗?+ Frida Gadget 娉ㄥ叆 |
| JADX / apktool / MobSF | `mobile-reverse/` 鈥?Android 闈欐€佸垎鏋?|
| class-dump / jtool2 / Hopper | `mobile-reverse/` 鈥?iOS 闈欐€佸垎鏋?|
| CAPE Sandbox / ASD Azul | `malware-analysis/` 鈥?娌欑鑷姩鍖栫紪鎺?|
| YARA / FLOSS | `malware-analysis/` 鈥?妯″紡鍖归厤 + 瀛楃涓插幓娣锋穯 |
| Sigma / Sigma CLI | `malware-analysis/` 鈥?SIEM 琛屼负妫€娴嬭鍒?|
| pe-sieve / Detect It Easy | `malware-analysis/` 鈥?杩涚▼鎵弿 + 澹虫娴?|
| LLM4Decompile / Glaurung | `reverse-engineering/` 鈥?AI 杈呭姪鍙嶇紪璇?|

闇€瑕佺‘璁ゆ湰鏈哄伐鍏锋槸鍚﹀彲鐢ㄣ€佽矾寰勫湪鍝噷銆佸摢涓剼鏈細璋冪敤瀹冩椂锛岀粺涓€鏌ョ湅 `tool-index.md`锛屼笉瑕佷复鏃剁寽璺緞銆?

---

## 璺敱鏈懡涓椂鐨勫鐞?

濡傛灉褰撳墠浠诲姟鍦ㄤ笂闈㈡墍鏈夎〃鏍间腑閮芥壘涓嶅埌鍖归厤椤癸紝**涓嶈纭杩涚幇鏈?skill**锛屾寜浠ヤ笅娴佺▼澶勭悊锛?

1. 鍏堢‘璁ゆ槸鍚﹀睘浜庣幇鏈?skill 鐨勮竟缂樺満鏅紙鍙互鎵╁睍鐜版湁 skill 瑕嗙洊锛?
2. 濡傛灉纭疄鏄叏鏂扮被鍨嬶紝涓诲姩鍚戠敤鎴锋彁璁柊澧?skill锛?
   - 璇存槑寤鸿鐨?skill 鍚嶇О鍜岃鐩栧満鏅?
   - 璇存槑闇€瑕佺殑宸ュ叿閾?
   - 璇存槑涓庣幇鏈?skill 鐨勫叧绯?
3. 鐢ㄦ埛纭鍚庯紝鎸?`CONTRIBUTING.md` 娴佺▼鎵ц鏂板
4. 鏂板瀹屾垚鍚庢洿鏂版湰璺敱鐭╅樀

**AI 涓嶉渶瑕佺瓑鐢ㄦ埛鍙戠幇缂哄け銆傝矾鐢卞け璐ユ湰韬氨鏄柊澧?skill 鐨勪俊鍙枫€?*

## 璺緞浜ゅ弶锛堣法妯″潡鍦烘櫙锛?

鏈変簺浠诲姟浼氳法澶氫釜妯″潡锛屼互涓嬫槸甯歌璺緞浜ゅ弶锛?

```
APK 閫嗗悜璺緞锛?
  apk-reverse/scripts/decode.ps1 鈫?Java 灞傚垎鏋?
  鈫?濡傛灉鏍稿績鍦?.so
  ida-reverse/ 鎴?radare2/ 鈫?so 鍒嗘瀽
  鈫?濡傛灉闇€鍔ㄦ€侀獙璇?
  apk-reverse/scripts/frida-run.ps1 鈫?Frida Hook

鍓嶇 JS 閫嗗悜璺緞锛?
  js-reverse/Observe 鈫?瀹氫綅鐩爣璇锋眰
  鈫?闇€瑕佹洿寮虹殑娴忚鍣?CDP/Hook/Network 闈?
  jshookmcp 鈫?鍋氶〉闈㈣繍琛屾椂閲囨牱銆佹柇鐐广€佹嫤鎴€丼ourceMap/AST 杈呭姪
  鈫?纭鍏ュ彛鍑芥暟鍚?
  js-reverse/Rebuild 鈫?Node 鏈湴澶嶇幇
  鈫?闇€瑕佽ˉ鐜
  js-reverse/references/env-patching.md

浜岃繘鍒堕€嗗悜璺緞锛?
  radare2/scripts/recon.ps1 鈫?蹇€熶睛瀵?
  鈫?娣卞害鍒嗘瀽
  ida-reverse/ 鈫?IDA 鍙嶇紪璇?
  鈫?鍔ㄦ€侀獙璇?
  reverse-engineering/tools-dynamic.md 鈫?Frida/GDB

CTF 绔炶禌璺緞锛堥€氳繃 CTF-Sandbox-Orchestrator锛夛細
  ctf-sandbox-orchestrator/SKILL.md 鈫?寤虹珛娌欑洅妯″瀷
  鈫?鎸変富瀵艰瘉鎹潰璺敱
  competition-web-runtime/ 鎴?competition-reverse-pwn/ 鎴?competition-identity-windows/
  鈫?璧颁笉閫氭椂鍥炴€绘帶
  ctf-sandbox-orchestrator 鈫?閲嶆柊璺敱

Cookie HMAC 瀵嗛挜澶嶇敤 鈫?鍚庡彴璁よ瘉缁曡繃锛?
  competition-web-runtime/references/cookie-hmac-key-reuse-auth-bypass.md
  鈫?閫傜敤鍦烘櫙
  URL 鍚?access token銆佺鍚?Cookie銆佸悗鍙?admin_session 鍏辩敤鍚屼竴瀵嗛挜

鍥轰欢娓楅€忚矾寰勶細
  firmware-pentest/references/extraction-methodology.md 鈫?鎻愬彇鏂囦欢绯荤粺
  鈫?鎷垮埌浜岃繘鍒?
  firmware-pentest/references/emba-automated-analysis.md 鈫?EMBA 鑷姩瀹¤鎵惧凡鐭?CVE
  鈫?宸茬煡 CVE 涓嶅 / 鎯虫壘 0-day
  firmware-pentest/references/emulation-and-fuzz.md 鈫?Firmadyne 浠跨湡 + AFL++ fuzz
  鈫?鎵惧埌 crash
  pwn-chain/references/stack-pwn.md 鎴?heap-pwn.md 鈫?鍐?exploit
  鈫?鎵撳疄鏈?
  attack-chain/SKILL.md 鈫?鏁村悎杩涙敾鍑婚摼

N-day 姝﹀櫒鍖栬矾寰勶細
  patch-diff-exploit/references/patch-tuesday-workflow.md 鈫?鍙栬ˉ涓佸墠鍚庝簩杩涘埗
  鈫?瀵归綈绗﹀彿
  patch-diff-exploit/references/diff-tools-comparison.md 鈫?BinDiff/ghidriff/Diaphora 閫夊瀷
  鈫?瀹氫綅鍙樻洿
  patch-diff-exploit/references/root-cause-and-poc.md 鈫?LLM 杈呭姪鏍瑰洜 + 鍐?PoC
  鈫?姝﹀櫒鍖?
  pwn-chain/SKILL.md锛堟瀯閫犵ǔ瀹?exploit锛? pentest-tools/references/msf-protocol.md锛圡etasploit 妯″潡鍖栵級

绾㈤槦鎶曢€掕矾寰勶細
  attack-chain/SKILL.md 鈫?閫夐樁娈?
  鈫?闇€瑕佺粫 EDR
  edr-bypass-re/references/hook-survey.md 鈫?璇嗗埆鐩爣 EDR 鐨?hook
  鈫?閫夌粫杩囨妧鏈?
  edr-bypass-re/references/unhook-techniques.md 鈫?鐩存帴 syscall / Hell's Gate
  edr-bypass-re/references/telemetry-blinding.md 鈫?ETW patch / AMSI patch
  鈫?鏈湴楠岃瘉
  pe-sieve / API Monitor 鈫?纭 unhook 骞插噣
  鈫?鎶曢€?
  鍥炲埌 attack-chain 鍚庢笚閫忛樁娈?
```
