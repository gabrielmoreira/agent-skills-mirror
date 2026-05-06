---
name: spm-local
description: |
  当用户要求管理 SPM 本地依赖、添加新的三方库、更新依赖版本、
  或遇到 Xcode SPM 网络问题时使用。
  通过终端下载三方库到本地，绕过 Xcode 的网络限制。
---

# SPM 本地依赖管理

通过终端将三方库下载到本地 `Packages/Caches/` 目录，Xcode 以 Add Local 方式引入。

## 目录结构

```
Packages/
├── packages.json              # 依赖清单（URL + 版本）
├── scripts/
│   └── fetch-packages.sh      # 下载/更新脚本
└── Caches/                    # 下载的三方库（gitignore）
```

## 依赖清单格式

```json
[
  { "url": "https://github.com/SnapKit/SnapKit" },
  { "url": "https://github.com/ccgus/fmdb.git", "version": "2.7.12" }
]
```

- `url`：仓库地址（必填）
- `version`：tag 版本号（可选，不填则拉取默认分支最新）
- 库名自动从 URL 解析

## 执行流程

### 新增依赖

1. 编辑 `Packages/packages.json`，添加一条记录
2. 执行 `./Packages/scripts/fetch-packages.sh`
3. Xcode → File → Add Package Dependencies → Add Local → 选择 `Packages/Caches/` 下对应文件夹

### 更新版本

1. 修改 `Packages/packages.json` 中对应条目的 `version`
2. 执行 `./Packages/scripts/fetch-packages.sh`
3. Xcode → File → Packages → Resolve Package Versions

## 脚本逻辑

1. 读取 `packages.json`，逐条处理
2. 从 URL 解析库名
3. 判断 `Caches/` 下是否已存在该库：
   - **不存在** → clone（指定版本则完整 clone + checkout，否则浅克隆）
   - **存在但为空目录** → 删除后重新 clone
   - **存在且有内容** → 指定了版本则 fetch + checkout，否则 skip
4. 完成后输出汇总
