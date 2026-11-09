# macOS Claude 清理教程

> 公开脱敏阅读版：保留操作说明，移除了个人机器路径和历史执行记录。原始输入与此分发版本的哈希分别登记在 manifest.json。

适用于卸载 Claude Desktop、清理旧登录状态，同时保留独立安装的 Claude Code CLI。本文按 2026 年 10 月本机实际检查整理。其他版本、安装方式和账户的路径可能不同，操作前应先检查。

**清理本地数据不等于解除封禁，也不能保证新账号不会被关联或再次封禁。不要为此修改 Mac 硬件 UUID、序列号或整个系统钥匙串。**

## 一 先选择清理范围

| 目的 | 处理内容 | 保留内容 |
| --- | --- | --- |
| 仅重置登录 | 已确认的登录凭据、OAuth 缓存 | CLI、项目、历史、skills、hooks、插件 |
| 卸载官方桌面端 | Claude.app 和对应桌面端数据 | 独立 CLI 及其配置 |
| 卸载额外客户端 | 对应应用、确认归属的支持目录 | 不属于该客户端的共享目录 |
| 完全重置 CLI | 程序、配置和历史均可能涉及 | 必须另行确认；本文默认不执行 |

**不要按名称包含 Claude 就全部删除。** 桌面端数据、终端程序、历史和自定义配置是不同对象。

## 二 区分桌面端和独立 CLI

本机确认的布局：

```text
/Applications/Claude.app                         官方桌面端
~/Library/Application Support/Claude/            官方桌面端数据
~/.local/bin/claude                              独立 CLI 入口
~/.local/share/claude/                            独立 CLI 程序及版本
~/.claude/                                       CLI 历史与自定义数据等
~/.claude.json                                   CLI 全局配置
```

若要保留终端，以下四项不要在卸载软件中勾选：

```text
~/.local/bin/claude
~/.local/share/claude/
~/.claude/
~/.claude.json
```

注意：桌面端支持目录中也可能有 `claude-code` 子目录。判断归属要看完整路径，不要只看末级文件夹名称。

本机卸载前，桌面端支持目录占用约 15 GB，大部分来自 `vm_bundles`，还包含本地会话、虚拟机及待上传文件。它不是纯缓存。删除整个目录意味着放弃其中的本地桌面数据；有重要任务时先导出或备份。

## 三 清理前准备

1. 保存 Claude、终端及浏览器中的工作和未提交内容。
2. 正常退出 Claude Desktop 和额外客户端，结束正在执行的 CLI 任务。
3. 清理浏览器数据库前，退出对应浏览器；不能只关闭窗口后就认为进程已退出。
4. 需要回滚时，把待删项目备份到应用目录之外，并限制访问权限。
5. 只清理当前用户的相关文件，不使用 `sudo` 批量扫删所有用户目录。

检查相关进程，仅查看，不杀进程：

```sh
ps -axo pid=,comm= | grep -i '[c]laude'
```

如发现多个会话，先辨认 PID 和所属任务。不要使用 `pkill -9 -f claude` 这类宽泛强杀命令。

## 四 使用 App Cleaner 卸载桌面端

1. 搜索 Claude，启用能显示关联文件的详细视图。
2. 仅勾选要卸载的应用。官方 `Claude` 与 `Claude Code Haha` 是不同应用。
3. 展开可执行文件、应用程序支持、缓存和偏好设置，逐项看完整路径。
4. 确认没有勾选第二节列出的四个 CLI 路径。
5. 确认桌面端本地数据不再需要后，再点击移除。
6. 若只卸载官方桌面端，取消 `Claude Code Haha`；独立的小写 `claude` 项也应保持不勾选。

本次实际出现过的桌面端项目：

```text
/Applications/Claude.app
~/Library/Application Support/Claude/
~/Library/Application Support/Claude-3p/
~/Library/HTTPStorages/com.anthropic.claudefordesktop/
~/Library/Preferences/com.anthropic.claudefordesktop.plist
~/Library/Preferences/ByHost/com.anthropic.claudefordesktop.*.plist
~/Library/Caches/com.anthropic.claudefordesktop*
~/Library/Logs/Claude/
```

上面的星号表示名称模式，**不是让你直接执行通配符删除命令**。临时缓存还可能位于 `/private/var/folders/.../C/`，只处理归属已确认的 Claude 项，不能删除整个 `C` 或 `var/folders`。

## 五 保留配置时重置登录

### 钥匙串

本机曾发现的两个服务名：

```text
Claude Code-credentials
Claude Safe Storage
```

先检查，不输出密码：

```sh
security find-generic-password -s "Claude Code-credentials" >/dev/null 2>&1
printf 'Claude Code credential lookup exit=%s\n' "$?"
security find-generic-password -s "Claude Safe Storage" >/dev/null 2>&1
printf 'Claude Safe Storage lookup exit=%s\n' "$?"
```

本次系统上，退出码 0 表示找到；44 表示未找到指定条目。其他错误不能自动当作已清理。

**仅在已决定退出登录，且不再需要对应桌面数据解密凭据时，执行：**

```sh
security delete-generic-password -s "Claude Code-credentials"
security delete-generic-password -s "Claude Safe Storage"
```

钥匙串删除后通常需要重新登录。`Claude Safe Storage` 可能用于桌面端加密存储；不要在仍需要保留桌面登录数据时随意删除。其他版本或自定义配置目录可能使用不同名称，两个条目未找到不等于所有凭据都不存在。

### 配置中的登录字段

本次在下列文件中发现过登录数据：

- `~/.claude.json` 及自动备份中的 `oauthAccount`。
- `~/.claude/config.json` 中的 `primaryApiKey`。仅凭字段名称不能确定它是有效的 Anthropic 密钥。
- `~/Library/Application Support/Claude/config.json` 中的 `oauth:tokenCache`、`oauth:tokenCacheV2`、`lastKnownAccountUuid`。

需要保留设置时：先备份，用 JSON 工具删除已确认的字段，再验证文件能正常解析。不要用文本替换破坏 JSON，不要直接清空整个配置文件。

如已卸载整个桌面端，原路径不存在就跳过，不要为了清理而重新创建它。

`machineID`、`userID` 是本次在应用配置中发现的本地字段，**不是 Mac 硬件 UUID 或序列号**。本次清理删除过这些字段，但不能据此宣称能够防封；普通退出登录不必随机伪造它们。

另外检查 `~/.claude/.credentials.json` 是否存在，以及自己是否设置了 `CLAUDE_CONFIG_DIR`。不要把凭据内容复制到聊天或公开日志中。

## 六 桌面端网页存储与浏览器集成

下列桌面端子目录可用于重置本地网页状态，但可能同时丢失偏好、草稿及离线数据，应先退出应用并备份：

```text
Local Storage
Session Storage
IndexedDB
WebStorage
Cookies
Cookies-journal
```

本机还出现过 `ant-did`、`ant-device-registry.json`、`config.json.journal`。它们按桌面端残留处理，不应视为已经证实的封号开关。

不再使用 Claude 浏览器集成时，可以删除对应浏览器 `NativeMessagingHosts` 目录下归属已确认的 `com.anthropic.*.json` 文件。此举会影响扩展与本机的通信；它不等于卸载浏览器扩展，也不等于清除网站 Cookie。

**保留 CLI、历史或桌面本地任务时，不要直接整删 `~/.claude`、`Partitions`、会话目录或项目文件。**

## 七 浏览器中的 Claude 站点数据

优先使用浏览器自己的站点数据管理界面：

1. 分别检查实际使用过的浏览器和配置档案。
2. 搜索 `claude.ai`、`anthropic.com` 及确实使用过的相关域名。
3. 仅移除这些站点的数据；这会使相关登录失效，未提交草稿也可能丢失。
4. 不要选择清空全部网站 Cookie、整个浏览器 Profile、书签或浏览历史。

不要手工编辑仍被浏览器使用的 Cookies SQLite 数据库、LevelDB 或 IndexedDB。直接改库还需要正确处理 WAL、日志文件、权限和完整性；普通清理不建议采用。

本次操作曾清除 Edge Default 档案中 12 条相关 Cookie，验证其他 Cookie 行不变，数据库完整性正常。Chrome 当时仍在运行，其相关站点数据没有清除。不要把 Edge 的结果理解为所有浏览器已清空。

## 八 卸载后检查遗漏

本机通过卸载软件移除应用后，还发现：

```text
~/Library/Application Support/claude-code-desktop/
~/Applications/Claude Code URL Handler.app
```

前者是额外桌面支持目录；后者为 URL 处理辅助应用。确认不再需要相应功能后才删除。URL 处理器移除可能影响相应深链跳转，不会因为删除该辅助应用就自动删除独立 CLI。

本次这两项已从原位置移除，随后按用户要求永久删除了对应回滚备份。

## 九 验收

### 确认独立 CLI 仍在

以下检查不启动 Claude，也不会发起模型请求：

```sh
ls -l "$HOME/.local/bin/claude"
ls -ld "$HOME/.local/share/claude" "$HOME/.claude"
```

本机是原生安装，可解析程序路径并检查签名：

```sh
python3 - <<'CHECK'
from pathlib import Path
import subprocess
p = Path.home() / '.local/bin/claude'
if not p.exists():
    raise SystemExit('CLI 不存在或链接失效，需要检查安装路径')
actual = p.resolve()
print('CLI 路径:', actual)
r = subprocess.run(['codesign', '--verify', '--strict', str(actual)])
print('签名检查退出码:', r.returncode)
CHECK
```

若通过 npm 等方式安装，入口和校验方式可能不同，不要直接套用本机原生二进制的判断。

### 确认清理目标已不存在

```sh
python3 - <<'CHECK'
from pathlib import Path
h = Path.home()
for p in [
    Path('/Applications/Claude.app'),
    h / 'Library/Application Support/Claude',
    h / 'Library/Application Support/claude-code-desktop',
    h / 'Applications/Claude Code URL Handler.app',
]:
    print('仍存在' if p.exists() or p.is_symlink() else '不存在', p)
CHECK
```

继续检查两项钥匙串、相关进程，以及要保留的 `projects`、`history.jsonl`、`skills`、`hooks`、`plugins`、`settings.json`。

## 十 备份 回滚与永久删除

- 移到应用目录之外：应用原位置已清理，但数据仍在磁盘上。
- 移到废纸篓：仍可恢复，不算永久删除。
- 删除私有备份：丢失对应回滚能力，必须再次确认具体范围。
- 文件系统删除：不等于经过认证的 SSD 安全擦除；Time Machine、APFS 快照等也不在本教程删除范围内。

公开阅读版已移除个人用户名、私有备份目录、执行产物位置以及原作者机器的清理结果。不要据此推断你的设备已经完成清理，也不要尝试访问作者的备份。

私有备份及差异文件可能含旧账号信息和敏感配置，不应上传或提交仓库。执行回滚前，应检查备份是否仍可用、确认恢复范围，并退出相关浏览器；回滚可能恢复旧登录字段、Cookie 和已清理数据。

## 十一 验收记录应如何填写

请依据当前设备的实际检查记录应用是否卸载、CLI 是否保留、配置与项目是否完整、哪些浏览器数据仍存在，以及备份与回滚是否可用。未执行的步骤标记为“未执行”；没有证据的结果标记为“未验证”。不要把本教程当作执行报告。

## 十二 不要把清理当成防封保证

论坛确有换号后连续封禁的自述，也有同设备换号正常的反例；它们不能证明修改某一个本地字段就能避免关联。本机此前发现的 `region_unavailable` 只证明当时有地区访问限制，不能直接证明硬件黑名单或账号连坐。

遇到问题时先保存错误原文、时间、客户端版本和认证方式，区分地区限制、凭据失效、限流与账号停用。不要通过反复注册、充值或登录新号来做破坏性测试，也不要为了未经证实的推断继续删项目和改系统身份。
