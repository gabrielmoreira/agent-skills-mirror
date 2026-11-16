# Guardian Switch：统一防直连开关

这是已部署防护的日常开关。Windows 使用两个桌面快捷方式直接启动 PowerShell，无浏览器或 Python 开关服务；Mac/Linux 保留 Python 命令行、本机网页与桌面入口。首次由目标机 Agent 配置并验收，以后用户直接使用桌面入口。没有新增常驻服务。

## 支持范围与操作含义

| 操作 | 行为 |
| --- | --- |
| `on` | 开启保护，确认网络正常后保留，并启用开机保持。临时开启后有 180 秒确认窗口 |
| `off` | 停用当前保护及开机加载，保留配置，重启后保持关闭 |
| `status` | 读回当前系统规则与开机状态；失败、混合状态或权限不足报待核实 |
| `uninstall` | 先 OFF，再移除 Mac/Linux 已部署防护组件；Windows 恢复基线并删除开关快照，原有防火墙规则保留 |
| `audit` | Windows 按需审计：核对防火墙配置、白名单条件、程序、服务和接口，只读 |
| `preview` | Windows 首次配置：只读检查拟保存的快照及计划，不落盘 |
| `snapshot` | Windows 首次配置：保存关闭保护时的恢复基线，不覆盖已有快照 |
| `gui` / `desktop` | 仅 Mac/Linux：打开本机界面／生成桌面入口，不执行防火墙改动 |

- **macOS**：复用 `guardian-pf-killswitch.sh`。ON 为 `apply → confirm → persist`，OFF 为 `unpersist → rollback`，卸载使用已有 `uninstall`。
- **Linux + FlClash TUN**：复用已部署的 `flclash-killswitch.service`、刷新任务及 nftables 规则。ON 在 systemd 单次保险丝保护下启动服务，确认后启用开机加载及 timer；OFF 停用服务和刷新任务并移除专用规则表。规则更新仍用原部署脚本。已有刷新脚本路径、用户和参数必须先验证可用。
- **Windows**：复用已配置、审查过的防火墙规则，通过精确规则 `Name` 切换启用状态，并切换 Domain/Private/Public 默认出站。OFF 恢复快照中的默认策略与指定规则状态，不导入整机防火墙备份、不关闭整个防火墙。
- **VPS 仅入站防火墙**：`vps-guard.sh` 不提供出站 Kill Switch，不纳入此开关。VPS 上实际部署了 FlClash TUN 防护时才采用 Linux 后端。

Windows 的 `status` 只读回生效策略、规则启停和出站放行名单。需要核对规则条件、程序、服务和接口时运行 `audit`。整机模式的 ON／KEEP 仍核对出站名单、默认策略与已审核的白名单条件。实际出口、DNS、UDP、IPv6、WebRTC 另行验收。Windows 只提供 `whole_machine` 开启路径；旧 `application_paths` 或未填写模式的配置只允许 Off／Recover／Uninstall 恢复，不提供第二条部署路线。

配置只绑定当前设备。新设备需重新配置，不能复制旧验收结论。已开启且开机保持开启时，ON 不重复加载；状态不完整时先排查或按恢复方案 OFF。当前规则读回与真实出口、DNS、UDP、IPv6、WebRTC 验收分别记录；Mac 现有新接口覆盖及开机加载时序限制仍适用。

## 首次配置：交给目标机 Agent

1. 按[本机防火墙](local-firewall-prompts.md)、[VM](vm-guidance.md)或[进阶 Linux](advanced-route.md)完成已有部署。核实实际目标。Mac/Linux 开关需 Python 3.10+；Mac 需 PF；Linux 需 systemd、nft、sudo 和图形终端；Windows 需 Windows PowerShell 5.1、NetSecurity 与任务计划程序。Linux 无桌面时用 CLI。
2. 把整个解压后的 Skill 放在稳定位置；不要只复制入口脚本。复制 [config.example.json](../assets/killswitch/config.example.json) 到本机私有目录。填写 `target`：Windows 使用 `[Environment]::MachineName`，Mac/Linux 使用 `python -c "import platform; print(platform.node())"` 的精确输出，`backend` 选择 `mac_pf`、`linux_flclash` 或 `windows_firewall`。
3. `protected_processes` 填实际需要退出的应用与后台进程名，包括 Claude、CLI、实际使用的浏览器和相关 Helper。首次核实对应监听、自动启动及共享进程，沿用[安全退出](routes-and-platforms.md#safe-shutdown)。OFF/卸载会检查这份清单，发现仍运行则停止，不代用户杀进程。仅关闭窗口通常不够；清单不能覆盖的共享进程需先按退出流程处理。
4. Mac 的 `mac` 字段填写代理配置**绝对路径** `CONFIG`，或 `NODE_IPS` 与 `NODE_PORTS`；可选 `NICS`、`BOOTSTRAP_DNS`、`LAN_NET` 沿用原脚本语义。Linux 不用这些字段，但保留模板结构。配置中不填写密码或订阅链接。
5. Windows 填 `windows.enable_rules` 的精确 `Name`。整机模式的 `disable_rules` 可留空，开关会在保存基线时从本机发现。三档防火墙启用、默认出站明确为 Allow 后执行 `snapshot`。已有 Block 部署须由 Agent 从部署前备份核实恢复状态，不能把 Block 当 OFF 基线。快照路径放在 `%ProgramData%\ClaudeGuardian\Switch\baseline.json`（通常为模板中的 C 盘路径）。该专用目录限制为 SYSTEM/管理员访问，用于快照和保险丝私有副本；不要放其他文件。ON 不新增规则，不替代节点/TUN/DNS 规则部署。
6. 告知目标、影响、保险丝与离线恢复方案，按现有 A/B/C 授权执行。首次 ON/网络中断仍须当场确认；不得让 Agent 代输终端确认或用管道确认。系统改动权限与仓库开发权限分开。
7. 按[突发场景验收](local-firewall-prompts.md#incident-acceptance)和下面的开关验收交付。配置、基线快照、真实路径与私人证据仅保存在目标机。

Windows 原生桌面入口的后端等待上限为 On 800 秒、Confirm 300 秒、Off 600 秒；超时不会伪报成功。首次配置的原生 Preview／Snapshot／Status 由 Agent 单独计时。应用及读回由本机保险丝保护，最多 240 秒。应用核实完成后进入 180 秒 KEEP 窗口。按时 KEEP 后，本机任务继续保护最终读回，最多 240 秒。未按时确认、验证失败或中断均走恢复，确认成功才撤销任务。

开关保险丝只覆盖自身后端。Windows 同时修改 DNS、代理、TUN、路由或网卡时，先读 [网络事务与独立恢复](windows-network-transaction.md)，不能把 OFF 当成这些设置的完整回滚。

## Windows 整机出口模式：代价与首次交付

**选择前必须讲清楚：这套模式影响整台电脑。**代理停止或不可用时，浏览器、下载、游戏等其他软件也可能断网；国内网站未配置直连例外时同样走代理，可能增加流量、延迟或费用。局域网共享／打印、虚拟机／Cowork、其他 VPN 和远程管理必须先核对，不能承诺全部保持原状。加入直连例外意味着这些流量不再受到“只能走代理”的约束；宽泛放行会破坏防护。OFF 恢复原出站策略，可能恢复直连，不是保留保护的网络修复按钮。

**执行边界：**先说明目标机、规则差异、影响、备份、分阶段保险丝与独立恢复入口，再由用户当场确认首次 ON（C 档）。远程机器必须有不依赖当前连接的救援方式；不能用开关配置字段代替用户确认。仓库开发授权不授权修改真实设备。

首次配置由目标机 Agent 完成：

1. 按[Windows 防火墙](local-firewall-prompts.md#windows-的防火墙系统自带)先验证 TUN、节点和代理核心，并保存当前策略备份。整理用户需要的国内直连、局域网、虚拟机、Cowork、VPN 和远程访问，列明保留／受影响／不支持；组织管理设备仍按既有规则停止。
2. 将 `windows.mode` 设为 `whole_machine`，只填入 `enable_rules`。它是已审核的代理节点、TUN 和必要例外规则的精确 `Name`。每项例外核对程序、接口、地址、协议和端口。避免用 Claude 主程序的版本路径承担整机防护。
3. 将 `disable_rules` 留空，执行一次 `snapshot`。开关从本机持久和生效策略发现需要停用的出站 Allow，保存实际规则的启停原值、三档默认策略及白名单条件。基线落盘前完成审计，输出计划停用数量。想先看计划时可用 `preview`；已有基线继续使用。
4. 告知计划停用数量和网络影响，确认本机恢复入口后由用户开启。ON 会检查是否有新增放行和白名单变化；Windows 无法通过本地策略停用的放行会阻止部署。已部署后有新规则需复核，再更新基线。旧配置手填的停用规则仍按精确名称执行。
5. 确认前验证代理可用、独立程序不能绕过代理、停止代理后无非批准直连。恢复后核对网络正常。沿用 `network_check.py run --failure-drill` 与 `egress_verifier.py`，分别记录 TCP／UDP、DNS、IPv6、WebRTC。
6. 交付时保存首次真实验收结论和例外清单，说明保险丝未确认会恢复原策略，恢复后不再保证防直连。开关与文档不会自动启动 Claude 或做真实业务测试。

**日常行为：**普通 Claude 更新仅改变程序目录或增加组件、未改网络策略时，默认阻止及出口允许规则仍适用，不需要每次找 Agent 重绑 Claude 路径。新安装程序若新增出站 Allow、代理核心路径／节点地址／端口、TUN 或网卡、例外、安全条件发生变化，则需复核。开关在查询和操作时读回规则，运行期间没有常驻监控。

ON／KEEP 要求已审核的白名单条件一致、两种存储的出站 Allow 集合匹配，开启后还要求三档默认出站均为 Block。检查失败时恢复原策略。在代理路径、接口或服务变更后运行 `audit` 检查依赖。网络故障先检查精确差异，不扩大白名单碰运气。快照记录的是经审查的配置，不自动证明所选例外合理或真实网络阻断有效。

**旧配置迁移：**不自动升级。保留旧配置／快照和恢复入口，先按安全退出与旧配置 OFF 恢复，再由 Agent 出完整整机计划。旧快照移至本机私有备份后，按新模式重新 snapshot；不能只改 mode、删除快照或复制他人快照就宣称已迁移。切换计划可能恢复直连，期间不启动受保护业务。

## 命令行与桌面入口

以下路径由 Agent 按实际环境替换。Windows 首次配置先展示整机影响、必要例外、计划停用数量与恢复方案，取得具体授权；不能因模板使用 whole_machine 就跳过说明。网络验收脚本仍需要 Python，日常 Windows 开关不需要。

Windows（首次部署的 Snapshot 等系统操作在管理员终端执行）：

```powershell
# 普通用户生成两个桌面入口，不修改防火墙；拒绝覆盖同名快捷方式
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\assets\killswitch\windows-shortcuts.ps1 -Config C:\private\switch.json
# 先预览，授权后保存基线；已有有效整机基线不重建
.\assets\killswitch\windows-switch.ps1 -Action Preview -Config C:\private\switch.json
.\assets\killswitch\windows-switch.ps1 -Action Snapshot -Config C:\private\switch.json
.\assets\killswitch\windows-switch.ps1 -Action Status -Config C:\private\switch.json
.\assets\killswitch\windows-switch.ps1 -Action Audit -Config C:\private\switch.json
```

桌面生成“开启保护（限制直连）.lnk”和“关闭保护（恢复联网）.lnk”，两者引用随包现有 `icon.ico`，图标表示操作而非实时状态。双击后按需 UAC 提权，显示目标和影响并确认；ON 读回临时状态后输入 KEEP，OFF 检查受保护进程后恢复。失败保留可见错误，按回车关闭窗口。取消 KEEP 会恢复，关闭窗口仍由原有独立保险丝处理。

旧 Windows 页面入口不再可用。迁移时由 Agent 核对旧 Guardian Switch.lnk 确实指向 killswitch.py gui 后移除该快捷方式；先正常退出旧页面服务，不能按进程名批量终止 Python。保留私有配置、快照和后端，生成新入口。旧模式须先用原配置 Off 恢复，再备份旧基线并部署整机白名单。

Mac/Linux（GUI、桌面生成使用普通用户，防火墙命令使用 sudo）：

```sh
python scripts/killswitch.py gui --config /absolute/path/switch.json
python scripts/killswitch.py desktop --config /absolute/path/switch.json --output /absolute/path/Guardian-Switch
# 管理员终端（macOS/Linux 加 sudo，Python 使用实际绝对路径）
python scripts/killswitch.py status --config /absolute/path/switch.json
python scripts/killswitch.py on --config /absolute/path/switch.json
python scripts/killswitch.py off --config /absolute/path/switch.json
python scripts/killswitch.py uninstall --config /absolute/path/switch.json
```

生成目录必须不存在，避免覆盖已有入口；可以选桌面下的新目录。Mac 生成 `.app`、Linux 生成 `.desktop`，均带应用图标。Linux 桌面若要求“允许启动”，由用户确认；这些是可检查的本机启动器，不是签名安装包。移动 Skill、Python 或配置文件后重新生成入口。卸载防护后，桌面入口与私有配置保留，可按明确范围自行删除。

Mac/Linux GUI 是仅监听 `127.0.0.1` 随机端口的临时网页，带随机会话地址、同源校验和固定操作集合；不加载远程字体、脚本或图片。点击操作后打开本机终端提权，确认界面中的目标与动作，再在终端输入相应确认文本。ON 后另输入 `KEEP` 才保留；超时或取消走恢复流程。不要把 GUI 本身以管理员运行。

Mac/Linux GUI 显示实际操作后的读回结果，超过 90 秒标“需要刷新”；刷新也需本机读取权限，不把旧结果当实时监控。按“退出”立即结束本机界面服务；直接关闭标签页后服务最多保留 15 分钟。正在执行的操作须先在终端完成或取消。关闭界面不关闭防护，不自动运行出口探测或接触 Claude。

## 恢复与开关验收

- 首次交付走真实桌面路径：Windows 双击 → PowerShell/UAC → 确认 → 真实状态读回；Mac/Linux 双击 → GUI → 本机终端/sudo → 确认 → 真实状态读回；不能仅以 SSH 或管理员命令行通过代替桌面入口验收。
- ON：验证代理正常、非批准直连被阻断，在保险丝内保留；Mac/Linux 开机项、Windows 三档实际策略分别核实。关闭代理造成的断网不是开关损坏。
- OFF：先按安全退出流程清理相关进程，再关闭；确认保护与开机保持均关闭，重启后仍关闭；再次 ON 可恢复。
- 取消、拒绝提权、缺依赖、无权限、规则与配置不一致时不得显示成功。意外中断保持“待核实”，在本机终端运行 `status`；不要重复点击掩盖失败。
- 开启失败时，保险丝恢复未保护状态以恢复访问，不作为持续 fail-closed。确认前不要启动受保护业务；独立恢复入口须不依赖被切断的 SSH/代理链路。
- Mac 原生离线恢复：`guardian-pf-killswitch.sh unpersist` 后 `rollback`。Linux 关闭启动单元与刷新任务，再核实专用表已移除。Windows 使用随包 `windows-switch.ps1 -Action Off -Config <私有配置>` 在管理员终端恢复快照；不要删除快照后再尝试恢复。紧急回滚沿用原授权和独立救援方案。
- 目前验证分为控制器/HTTP/启动器离线测试、PowerShell 原生解析与夹具状态读回、浏览器演示交互和目标机真实防火墙验收。演示与 CI 不代填目标机验收。

## 界面与随包文件

[Mac/Linux 入口](../scripts/killswitch.py)、[Mac/Linux GUI 与桌面生成](../scripts/killswitch_ui.py)、[Windows 桌面入口](../assets/killswitch/windows-desktop.ps1)、[Windows 快捷方式生成](../assets/killswitch/windows-shortcuts.ps1)、[Windows 后端](../assets/killswitch/windows-switch.ps1)、[配置模板](../assets/killswitch/config.example.json)。页面来自 [HTML](../assets/killswitch/switch.html)、[CSS](../assets/killswitch/switch.css)、[JavaScript](../assets/killswitch/switch.js)。

图标源文件为 `tools/assets/claude-color.png`，修改后运行 `tools/generate_switch_icon.py` 重新生成 SVG／PNG／ICO／ICNS，不手改产物。生成依赖 macOS `sips`，运行开关无需此依赖。

Mac/Linux 无系统操作的预览：`python scripts/killswitch_ui.py --preview`。界面明确显示演示标记，所有按钮只改变演示状态。
