---
name: chengfeng-check-updates
description: 剪辑环境的唯一管理者：就绪检查（skills 是否最新 → Runtime 是否配套）、Skills 更新激活、Runtime 安装与体检。用户说检查更新、安装剪辑环境、装播放器、检查剪辑环境、剪辑环境就绪了吗、配置转录凭证时使用；业务 Skill（剪口播/字幕/画面/导出）第 0 步也引用本 Skill 的就绪检查。不用于剪辑、字幕、画面、导出本身或项目数据迁移。
user-invocable: true
---

# 检查更新（环境总管）

环境的一切逻辑只写在本 Skill：skills 版本、Runtime 安装与体检。业务 Skill 第 0 步
一行引用下面的「就绪检查」，自己不带任何环境逻辑——环境策略要变，只改这一个文件。
本 Skill 不建项目、不打开 Studio、不转录任何媒体。

## 就绪检查（业务 Skill 的第 0 步从这里执行）

三步走完，输出三态之一：**就绪 / 需新会话 / 停**。

### 一、定位插件根（两步，不经过 shell 变量）

命令块不用 shell 变量与命令替换——bash 和 PowerShell 的赋值语法互不兼容，
胶水逻辑一律由 Agent 自己完成：

```bash
codex plugin list --json
```

从输出的 `installed` 列表里找 **`enabled` 为 true 且 `name` 为 `chengfeng-videocut`
的唯一一行**，取它的 `source.path`——这就是**插件根**；再用你的文件工具确认
`<插件根>/.codex-plugin/plugin.json` 存在。命中不是恰好一行、或该文件不存在，
停止并报告插件未正确安装。

**此后所有命令里的 `<插件根>` 都代入这个字面路径**（含空格时整段引号包住）。
禁止依赖未保证存在的 `SKILL_DIR`、硬编码开发机路径或用目录搜索猜测安装位置。

### 二、skills 最新吗

```bash
node "<插件根>/scripts/check-plugin-update.cjs" --marketplace chengfeng-videocut --json
```

（Marketplace 名默认 `chengfeng-videocut`；用户自己配过别的名字就用他配的。）

- `current` → 继续第三步
- `update_available_confirmation_required` → 展示 installed、available、40-hex
  immutable commit、publisher SHA-256，停下等用户确认；确认后走下面「激活」节。
  激活成功 = **需新会话**：会话开始时 skill 文本已载入，中途更新对本会话不生效，
  请用户新开会话再继续任务
- `marketplace_not_refreshable`（本地开发源）→ 继续第三步，不伪造 remote check
- 网络不可达、`update_metadata_untrusted` 或其他检查错误 → 向用户说明一句，
  带当前版本继续第三步——**更新检查失败不阻塞干活**

### 三、Runtime 配套吗

```bash
node "<插件根>/scripts/ensure-runtime.cjs" --install-if-missing --json
```

- `ready` → **就绪**，业务 Skill 继续
- missing：脚本只提示一次「正在从 GitHub Release 安装」，SHA-256 校验完成后自动续跑
- `runtime_unhealthy`、安装失败或安装后 doctor 失败 → **停**，报告结构化诊断。
  **停止就是停止：禁止用自制的审核页、播放器、时间线或任何替代界面继续流程。**
  产品不可用时做出的任何产出都不可信（真实案例：Runtime 缺失时 Agent 手搓了一个
  「审片台」网页，其审核决定与产品的账本格式完全不兼容，用户白做一遍）。
  正确动作只有一个：把结构化诊断给用户，指引安装或上报 Issue
- `runtime_capability_missing` → **停**：Runtime 健康但低于合同要求。报告两个版本号
  与差异，指引用户确认后升级（升级替换 `~/.chengfeng-videocut/app`，项目数据不动）；
  用户未确认前不动现有安装，禁止回退旧剪辑链
- 就绪检查阶段禁止启动服务、打开 Studio 或创建项目

### 机器前置依赖

支持 **macOS** 与 **Windows 10/11**。缺任何一个依赖，安装会在对应环节明确停下
（不静默跳过）：Bun ≥ 1.2、Node.js、ffmpeg ≥ 6、Google Chrome（导出用）。

```text
macOS     brew install bun ffmpeg          Chrome 从官网装
Windows   winget install Oven-sh.Bun       winget install Gyan.FFmpeg
          winget install OpenJS.NodeJS.LTS Google.Chrome
          装完新开一个终端/会话，PATH 才生效
```

云端转录另需火山引擎凭证：`node "<插件根>/scripts/videocut-cli.cjs" config set transcription.apiKey <key>`。

详细协议见 [Runtime 与产品契约](../../references/runtime-and-product-contract.md)。

## Skills 更新：inspect 与激活

只允许 Codex 官方 Marketplace 命令处理快照和激活。纯查看（不 refresh、不打网络）：

```bash
node "<插件根>/scripts/check-plugin-update.cjs" --marketplace "<市场名>" --inspect --json
```

带 refresh 的检查（用户明确说「检查更新」，或就绪检查第二步）：

```bash
node "<插件根>/scripts/check-plugin-update.cjs" --marketplace "<市场名>" --json
```

- `current`：报告 current/latest、Marketplace 与已刷新事实。
- `update_available_confirmation_required`：展示 installed、available、40-hex immutable commit、publisher SHA-256；停止等用户确认。
- `marketplace_not_refreshable`：本地 marketplace 不是远程更新源；不伪造 remote check。
- `update_metadata_untrusted`：缺 40-hex immutable commit、发布者包校验和，或 Codex snapshot 中可重算的包清单哈希不一致；裸 semver/tag 不能替代 commit，不下载、不调用 `plugin add`。官方 CLI 没有独立 stage 命令，因此不声称已 stage。
- 任何 refresh/parse/version 错误：保留结构化 JSON；不复制目录、不删除 cache。

### 用户明确确认后才激活

确认必须发生在用户已看见 exact available version、ref 与 checksum 之后：

```bash
node "<插件根>/scripts/check-plugin-update.cjs" --marketplace "<市场名>" --activate --confirmed --expected-version "<展示过的版本>" --expected-ref "<展示过的40位commit>" --expected-sha256 "<展示过的包SHA256>" --json
```

脚本通过官方 `codex plugin marketplace upgrade` 刷新 Git snapshot，重算 snapshot 内候选包的文件清单 SHA-256，并比对三个 `--expected-*` 值；随后才使用官方 `codex plugin add`。没有独立 stage：官方 refresh 的 snapshot 是唯一可检查来源。它必须从 `plugin add` 返回的 installed cache 路径复读 version、immutable ref、publisher SHA-256，并重算同一 inventory digest；Codex list 不含 ref/checksum 时只接受 installed `.codex-plugin/update-provenance.json` 的可验证来源，缺失即失败。只有四项都等于候选才报告 `activated`。激活成功后告知用户重启 Codex 或新开会话。

`plugin_activation_unsupported` 表示官方 CLI 没有原子选择该版本：停止，不删除 cache、复制 sources 或重装 Runtime 模拟升级。

## 用户说「安装剪辑环境 / 装播放器 / 检查环境」

直接跑完整就绪检查；拿到「就绪」后再跑完整自检并原样报告：

```bash
node "<插件根>/scripts/videocut-cli.cjs" doctor --json
```

报告：Runtime 版本与位置、doctor 每项检查结果、缺失项的修法（机器依赖指引安装；
转录凭证指引 `node "<插件根>/scripts/videocut-cli.cjs" config set transcription.apiKey <key>`）。
装好后告诉用户：直接说「剪口播」就能开始。

## 边界

- Plugin 版本与 Runtime 版本相互独立；Runtime 的最低兼容与 Release 目标由
  `runtime-requirements.json` 合同控制，不在本文硬编码任何版本号
- 不把本地 staging、legacy cache 或 local marketplace 说成 remotely updatable
- 不发布、不改项目数据或媒体；用户确认后的官方 Codex activation 与 Runtime
  安装是仅有的写入例外
