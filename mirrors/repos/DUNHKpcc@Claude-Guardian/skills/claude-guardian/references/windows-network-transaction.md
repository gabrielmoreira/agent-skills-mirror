# Windows 网络修改与恢复

把已审核的网络修改交给本机任务执行，Agent 断网或终端退出后仍可到期恢复。DNS、代理、TUN、路由、网卡等步骤脚本须按目标机准备；仅覆盖计划内的修改。

## 使用前

- 明确目标、精确修改范围、原值、影响、执行顺序和恢复办法，按 [C 档授权](authorization-tiers.md) 当场确认，Agent 不代输确认。没有已启动的独立恢复就不写入网络配置。
- 按[安全退出](routes-and-platforms.md#safe-shutdown)核实受保护应用及后台进程已退出。恢复原配置可能恢复直连，须确认恢复目标及局域网、VPN、远程管理的影响。
- SYSTEM 的 `HKCU` 不是登录用户的注册表，用户代理设置须绑定具体 SID。Kill Switch 只恢复自己的防火墙范围；与本事务组合使用须先验证。

执行期间创建临时 SYSTEM 计划任务，每分钟及开机时检查。提交、完整恢复或准备失败后移除任务，恢复失败则保留。备份与日志位于 `%ProgramData%\ClaudeGuardian\NetworkTransaction`，仅管理员和 SYSTEM 可访问；旧批次归档，不自动删除。关机或休眠期间无法恢复。

## 运行

在 Skill 目录下打开管理员 PowerShell：

```powershell
$tx = '.\assets\killswitch\windows-network-transaction.ps1'
powershell.exe -NoProfile -File $tx -Action Start -Plan C:\private\network-plan.json
powershell.exe -NoProfile -File $tx -Action Status
powershell.exe -NoProfile -File $tx -Action Commit
powershell.exe -NoProfile -File $tx -Action Recover
```

计划示例：步骤脚本与 JSON 放在同一目录，下面的脚本须先实现并审核。

```json
{
  "version": 1,
  "target": "EXACT-MACHINE-NAME",
  "timeout_seconds": 600,
  "restore_goal": "恢复修改前的指定配置，受保护业务保持退出",
  "steps": [
    {"id": "proxy", "script": "reviewed-proxy.ps1", "scope": "指定代理配置和服务"},
    {"id": "dns", "script": "reviewed-dns.ps1", "scope": "指定网卡的 DNS 模式和值"}
  ]
}
```

`Start` 输入 `START <设备名>`。进入 `awaiting_commit` 后，先验证实际网络、Agent 连接和出口，再用 `Commit` 输入 `KEEP <事务编号>`；需立即恢复则用 `Recover`。两者均为请求，**再次查询 Status，确认最终状态**。

## 步骤脚本

每步接收 `-Operation` 和 `-Snapshot`，实现以下操作：

| Operation | 要求 |
| --- | --- |
| `Prepare` | 只读原状态，保存 JSON 快照，不改网络 |
| `CheckRestore` | 读回并核对快照原值 |
| `Apply` | 修改该步审核范围 |
| `Check` | 读回并核对拟改值 |
| `Restore` | 恢复该步范围，包括部分生效的修改；遇到无关变更报错，不覆盖 |

脚本须离线、无交互、可重复恢复；检查外部程序退出码，失败或读回不符以非零退出。不得启动脱离执行树的后台写入。每次操作最多 30 秒，整批修改与等待确认共用 60–1800 秒期限；超时先终止步骤进程树，再恢复。

全部快照及原状态检查通过后才开始修改。步骤复制到私有目录并核对 SHA256；快照只写入指定路径，脚本、配置和日志不上传。

## 恢复与结果

中途失败、到期或请求恢复时，从可能部分生效的当前步骤开始逆序恢复并读回。失败项保留重试；任务中断后先终止残留步骤再恢复，不继续修改。未完成批次会阻止新批次。

| 状态 | 含义 |
| --- | --- |
| `committed` | 提交前再次读回通过，修改已保留 |
| `restored` | 已恢复并读回通过 |
| `prepare_failed` | 准备失败，未开始修改 |
| `recovery_failed` | 恢复不完整，检查私有日志并保留快照与任务 |

已验证真实 PowerShell 的临时文件回归。真实网络、SYSTEM 任务调度、睡眠和重启仍需在目标机验收。
