# Guardian Switch：统一防直连开关

这是已部署防护的日常开关：命令行、轻量本机网页、桌面入口共用同一控制器。首次由目标机 Agent 配置并验收，以后用户直接打开桌面入口，不必重复运行 Skill。Python 3.10+ 与系统原生工具即可；没有 Electron、第三方 GUI 库或新增常驻服务。

## 支持范围与操作含义

| 操作 | 行为 |
| --- | --- |
| `on` | 开启保护；180 秒保险丝内确认网络正常后保留，并启用开机保持 |
| `off` | 停用当前保护及开机加载，保留配置，重启后保持关闭 |
| `status` | 读回当前系统规则与开机状态；失败、混合状态或权限不足报待核实 |
| `uninstall` | 先 OFF，再移除 Mac/Linux 已部署防护组件；Windows 恢复基线并删除开关快照，原有防火墙规则保留 |
| `snapshot` | Windows 首次配置：保存关闭保护时的恢复基线，不覆盖已有快照 |
| `gui` / `desktop` | 打开本机界面／生成桌面入口，不执行防火墙改动 |

- **macOS**：复用 `guardian-pf-killswitch.sh`。ON 为 `apply → confirm → persist`，OFF 为 `unpersist → rollback`，卸载使用已有 `uninstall`。
- **Linux + FlClash TUN**：复用已部署的 `flclash-killswitch.service`、刷新任务及 nftables 规则。ON 在 systemd 单次保险丝保护下启动服务，确认后启用开机加载及 timer；OFF 停用服务和刷新任务并移除专用规则表。规则更新仍用原部署脚本。已有刷新脚本路径、用户和参数必须先验证可用。
- **Windows**：复用已配置、审查过的防火墙规则，通过精确规则 `Name` 切换启用状态，并切换 Domain/Private/Public 默认出站。OFF 恢复快照中的默认策略与指定规则状态，不导入整机防火墙备份、不关闭整个防火墙。
- **VPS 仅入站防火墙**：`vps-guard.sh` 不提供出站 Kill Switch，不纳入此开关。VPS 上实际部署了 FlClash TUN 防护时才采用 Linux 后端。

配置只绑定当前设备。新设备需重新配置，不能复制旧验收结论。已开启且开机保持开启时，ON 不重复加载；状态不完整时先排查或按恢复方案 OFF。当前规则读回与真实出口、DNS、UDP、IPv6、WebRTC 验收分别记录；Mac 现有新接口覆盖及开机加载时序限制仍适用。

## 首次配置：交给目标机 Agent

1. 按[本机防火墙](local-firewall-prompts.md)、[VM](vm-guidance.md)或[进阶 Linux](advanced-route.md)完成已有部署。核实实际目标与 Python 3.10+。Mac 需 PF；Linux 需 systemd、nft、sudo 和图形终端；Windows 需 Windows PowerShell 5.1、NetSecurity 与任务计划程序。Linux 无桌面时用 CLI。
2. 把整个解压后的 Skill 放在稳定位置；不要只复制入口脚本。复制 [config.example.json](../assets/killswitch/config.example.json) 到本机私有目录。填写 `target` 为 `python -c "import platform; print(platform.node())"` 的精确输出，`backend` 选择 `mac_pf`、`linux_flclash` 或 `windows_firewall`。
3. `protected_processes` 填实际需要退出的应用与后台进程名，包括 Claude、CLI、实际使用的浏览器和相关 Helper。首次核实对应监听、自动启动及共享进程，沿用[安全退出](routes-and-platforms.md#safe-shutdown)。OFF/卸载会检查这份清单，发现仍运行则停止，不代用户杀进程。仅关闭窗口通常不够；清单不能覆盖的共享进程需先按退出流程处理。
4. Mac 的 `mac` 字段填写代理配置**绝对路径** `CONFIG`，或 `NODE_IPS` 与 `NODE_PORTS`；可选 `NICS`、`BOOTSTRAP_DNS`、`LAN_NET` 沿用原脚本语义。Linux 不用这些字段，但保留模板结构。配置中不填写密码或订阅链接。
5. Windows 填 `windows.enable_rules` 与 `disable_rules` 的精确 `Name`，不填 `DisplayName` 或通配符。先审查其他宽泛 Allow 规则，并在三档防火墙启用、默认出站明确为 Allow 的恢复基线下执行 `snapshot`。已有 Block 部署须由 Agent 从部署前备份核实恢复状态，不能把 Block 当 OFF 基线。快照路径放在 `%ProgramData%\ClaudeGuardian\Switch\baseline.json`（通常为模板中的 C 盘路径）。该专用目录限制为 SYSTEM/管理员访问，用于快照和保险丝私有副本；不要放其他文件。ON 不新增规则，不替代节点/TUN/DNS 规则部署。
6. 告知目标、影响、保险丝与离线恢复方案，按现有 A/B/C 授权执行。首次 ON/网络中断仍须当场确认；不得让 Agent 代输终端确认或用管道确认。系统改动权限与仓库开发权限分开。
7. 按[突发场景验收](local-firewall-prompts.md#incident-acceptance)和下面的开关验收交付。配置、基线快照、真实路径与私人证据仅保存在目标机。

## 命令行与桌面入口

以下命令中的路径由 Agent 按实际环境替换。GUI、桌面生成使用普通用户；防火墙命令在 sudo／管理员终端运行。

```sh
python scripts/killswitch.py gui --config /absolute/path/switch.json
python scripts/killswitch.py desktop --config /absolute/path/switch.json --output /absolute/path/Guardian-Switch
# 管理员终端（macOS/Linux 加 sudo，Python 使用实际绝对路径）
python scripts/killswitch.py status --config /absolute/path/switch.json
python scripts/killswitch.py on --config /absolute/path/switch.json
python scripts/killswitch.py off --config /absolute/path/switch.json
python scripts/killswitch.py uninstall --config /absolute/path/switch.json
# Windows 首次保存恢复基线
python scripts/killswitch.py snapshot --config C:\private\switch.json
```

生成目录必须不存在，避免覆盖已有入口；可以选桌面下的新目录。Mac 生成 `.app`、Windows 生成 `.lnk`、Linux 生成 `.desktop`，均带应用图标。Linux 桌面若要求“允许启动”，由用户确认；这些是可检查的本机启动器，不是签名安装包。移动 Skill、Python 或配置文件后重新生成入口。卸载防护后，桌面入口与私有配置保留，可按明确范围自行删除。

GUI 是仅监听 `127.0.0.1` 随机端口的临时网页，带随机会话地址、同源校验和固定操作集合；不加载远程字体、脚本或图片。点击操作后打开本机终端提权，确认界面中的目标与动作，再在终端输入相应确认文本。ON 后另输入 `KEEP` 才保留；超时或取消走恢复流程。不要把 GUI 本身以管理员运行。

GUI 显示实际操作后的读回结果，超过 90 秒标“需要刷新”；刷新也需本机读取权限，不把旧结果当实时监控。按“退出”立即结束本机界面服务；直接关闭标签页后服务最多保留 15 分钟。正在执行的操作须先在终端完成或取消。关闭界面不关闭防护，不自动运行出口探测或接触 Claude。

## 恢复与开关验收

- 首次交付走真实桌面路径：双击 → GUI → 本机终端/UAC/sudo → 确认 → 真实状态读回；不能仅以 SSH 或管理员命令行通过代替桌面入口验收。
- ON：验证代理正常、非批准直连被阻断，在保险丝内保留；Mac/Linux 开机项、Windows 三档实际策略分别核实。关闭代理造成的断网不是开关损坏。
- OFF：先按安全退出流程清理相关进程，再关闭；确认保护与开机保持均关闭，重启后仍关闭；再次 ON 可恢复。
- 取消、拒绝提权、缺依赖、无权限、规则与配置不一致时不得显示成功。意外中断保持“待核实”，在本机终端运行 `status`；不要重复点击掩盖失败。
- 开启失败时，保险丝恢复未保护状态以恢复访问，不作为持续 fail-closed。确认前不要启动受保护业务；独立恢复入口须不依赖被切断的 SSH/代理链路。
- Mac 原生离线恢复：`guardian-pf-killswitch.sh unpersist` 后 `rollback`。Linux 关闭启动单元与刷新任务，再核实专用表已移除。Windows 使用随包 `windows-switch.ps1 -Action Off -Config <私有配置>` 在管理员终端恢复快照；不要删除快照后再尝试恢复。紧急回滚沿用原授权和独立救援方案。
- 目前验证分为控制器/HTTP/启动器离线测试、PowerShell 原生解析与夹具状态读回、浏览器演示交互和目标机真实防火墙验收。演示与 CI 不代填目标机验收。

## 界面与随包文件

[入口脚本](../scripts/killswitch.py)、[GUI 与桌面生成](../scripts/killswitch_ui.py)、[Windows 后端](../assets/killswitch/windows-switch.ps1)、[配置模板](../assets/killswitch/config.example.json)。页面来自 [HTML](../assets/killswitch/switch.html)、[CSS](../assets/killswitch/switch.css)、[JavaScript](../assets/killswitch/switch.js)。

图标由仓库 `tools/generate_switch_icon.py` 生成：[SVG](../assets/killswitch/icon.svg)、[PNG](../assets/killswitch/icon.png)、[ICO](../assets/killswitch/icon.ico)、[ICNS](../assets/killswitch/icon.icns)。修改生成器后重新生成，不手改产物。

无系统操作的预览：`python scripts/killswitch_ui.py --preview`。界面明确显示演示标记，所有按钮只改变演示状态。
