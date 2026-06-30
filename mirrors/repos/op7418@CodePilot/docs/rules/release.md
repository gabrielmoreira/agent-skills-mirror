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

macOS 产出 DMG（arm64 + x64），Windows 产出 NSIS 安装包。`scripts/after-pack.js` 重编译 better-sqlite3 为 Electron ABI。构建前清理 `rm -rf release/ .next/`。

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

## 安装说明

**macOS**: 下载 DMG → 拖入 Applications → 首次启动如遇安全提示，在系统设置 > 隐私与安全中点击"仍要打开"
**Windows**: 下载 exe 安装包 → 双击安装

## 系统要求

- macOS 12.0+ / Windows 10+ / Linux (glibc 2.31+)
- 需要配置 API 服务商（Anthropic / OpenRouter 等）
- 推荐安装 Claude Code CLI 以获得完整功能
```

## Release Notes 写作规则

- 更新内容必须用用户能理解的语言，不要出现 commit hash、函数名、文件路径
- 每个条目说清楚"用户能感知到什么变化"
- 下载链接必须是完整的 GitHub release download URL，用户点击即可下载
- 如果某个分类没有内容（如没有修复），跳过该分类不要留空标题
- `git log --oneline` 的输出只用于自己梳理，不要原样复制到 Release Notes
