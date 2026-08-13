# 发版 / Release

> 从 `CLAUDE.md` 顶层拆出的完整发版细则。顶层只留：发版流程一句话摘要 + **发版纪律**（硬规则）+ 指到这里。
> 发版时读这份。

## 发版纪律（硬规则，顶层也保留）

- **禁止自动发版**：`git push` + `git tag` 必须等用户明确指示后才执行。commit 可以正常进行。
- 不要手动创建 GitHub Release（CI 会自动创建并上传构建产物）。
- 不要删除 / 重建已发布的 release tag（会把已发布 Release 打回 Draft）。

## 发版流程

更新 `RELEASE_NOTES.md` → 更新 `package.json` version → `npm install` 同步 lock → 提交推送 → `git tag v{版本号} && git push origin v{版本号}` → CI 自动构建发布并使用 `RELEASE_NOTES.md` 作为 Release 正文。

## 构建

macOS 产出 DMG（arm64 + x64），Windows 产出 NSIS 安装包（x64），Linux 在原生 Ubuntu 22.04 x64 / arm64 runner 产出 AppImage、deb、rpm。`scripts/after-pack.js` 重编译 better-sqlite3 为 Electron ABI。任一平台/架构的安装包、原生 ABI、packaged server 或 source-map 卫生门禁失败，都会阻断正式 Release。

macOS stable 与 preview 都必须把仓库 `MAC_CERT_P12_BASE64` / `MAC_CERT_PASSWORD` secrets 映射为 electron-builder 的 `CSC_LINK` / `CSC_KEY_PASSWORD`，并用 `APPLE_TEAM_ID` → `CODEPILOT_APPLE_TEAM_ID` 校验精确 `TeamIdentifier`。`CSC_LINK` 只负责导入证书；若未另行配置显式 identity，证书打包步骤不得设置 `CSC_IDENTITY_AUTO_DISCOVERY=false`，否则 electron-builder 会导入证书却跳过身份选择。缺 secrets、ad-hoc、Team ID 不匹配、afterSign 或最终产物 `codesign --verify --deep --strict` 失败都必须阻断；禁止上传 ad-hoc 包。无证书的本地目录包只有显式 `CODEPILOT_ALLOW_ADHOC_SIGNING=1` 才允许生成，且只能作隔离开发 smoke，不能标记 `Release ready`。

涉及 packaged Next utility 生命周期、Codex transport/model discovery 或 server recovery 的版本，除启动期 `/api/health` 外还必须在对应平台产物执行：一次运行期强制退出并验证 offline recovery page → bounded safe-mode restart → 原 stable port/route 恢复；三次自动重启分别消费 1s/2s/4s 预算后，第 4 次退出验证停止自动重试；有不可验证 descendant 时验证 fail-closed。Codex 相关改动另需至少 15 分钟 warmup soak。未完成这些真实产物 smoke 时只能报 `Tests pass`，不得报 `Release ready`。

> Windows 构建机器钉在 `windows-2022`（见 tech-debt #44：`windows-latest` 滚到 VS18 后 node-gyp 编译 native 模块失败）。

## Release Notes 格式（必须严格遵循）

标题：`CodePilot v{版本号}`

正文结构：

```markdown
## CodePilot v{版本号}

> 一句话版本摘要，说明这个版本的核心主题或推荐升级理由。

### 新增功能
- 功能描述（面向用户的语言，不要写 commit hash）

### 修复问题
- 修复了 xxx 的问题

### 优化改进
- 优化了 xxx

## 下载地址

### macOS
- [Apple Silicon (M1/M2/M3/M4)](https://github.com/op7418/CodePilot/releases/download/v{版本号}/CodePilot-{版本号}-arm64.dmg)
- [Intel](https://github.com/op7418/CodePilot/releases/download/v{版本号}/CodePilot-{版本号}-x64.dmg)

### Windows
- [Windows 安装包](https://github.com/op7418/CodePilot/releases/download/v{版本号}/CodePilot.Setup.{版本号}.exe)

### Linux x64
- [AppImage](https://github.com/op7418/CodePilot/releases/download/v{版本号}/CodePilot-{版本号}-x86_64.AppImage)
- [deb](https://github.com/op7418/CodePilot/releases/download/v{版本号}/CodePilot-{版本号}-amd64.deb)
- [rpm](https://github.com/op7418/CodePilot/releases/download/v{版本号}/CodePilot-{版本号}-x86_64.rpm)

### Linux arm64
- [AppImage](https://github.com/op7418/CodePilot/releases/download/v{版本号}/CodePilot-{版本号}-arm64.AppImage)
- [deb](https://github.com/op7418/CodePilot/releases/download/v{版本号}/CodePilot-{版本号}-arm64.deb)
- [rpm](https://github.com/op7418/CodePilot/releases/download/v{版本号}/CodePilot-{版本号}-aarch64.rpm)

## 安装说明

**macOS**: 下载 DMG → 拖入 Applications → 首次启动如遇安全提示，在系统设置 > 隐私与安全中点击"仍要打开"
**Windows**: 下载 exe 安装包 → 双击安装
**Linux**: AppImage 添加可执行权限后直接运行；Debian/Ubuntu 安装 deb；Fedora/RHEL 系安装 rpm

## 系统要求

- macOS 12.0+ / Windows 10+ / Linux (glibc 2.35+)
- 需要配置 API 服务商（Anthropic / OpenRouter 等）
- 推荐安装 Claude Code CLI 以获得完整功能
```

## Release Notes 写作规则

- 更新内容必须用用户能理解的语言，不要出现 commit hash、函数名、文件路径
- 每个条目说清楚"用户能感知到什么变化"
- 下载链接必须是完整的 GitHub release download URL，用户点击即可下载
- 如果某个分类没有内容（如没有修复），跳过该分类不要留空标题
- `git log --oneline` 的输出只用于自己梳理，不要原样复制到 Release Notes
