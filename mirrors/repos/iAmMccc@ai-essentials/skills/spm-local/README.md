# SPM Local — SPM 本地依赖管理

解决 Xcode SPM 的网络痛点：Xcode 不走系统代理、全局代理影响内网、Reset Package 重复下载。

通过终端脚本将三方库 clone 到本地，Xcode 以 Add Local 方式引用，彻底绕开网络问题。

## 设计原理

Xcode 自身不使用系统代理设置，导致 Resolve Package 经常卡死。常见的解决办法是开全局代理，但又会影响内网服务访问。而且每次 Reset Package Caches 都会重新下载所有依赖。

本方案参考 CocoaPods 的思路：

1. **终端可走代理** — 用 shell 脚本在终端 clone 三方库，终端天然支持代理
2. **本地缓存** — 三方库下载到项目的 `Packages/Caches/` 目录，下载一次后续不再重复
3. **Add Local 引用** — Xcode 直接引用本地路径，不再依赖网络 Resolve

## 安装

在项目根目录执行：

```bash
curl -sL https://raw.githubusercontent.com/iAmMccc/ai-essentials/main/install-skill.sh | bash -s spm-local
```

安装后会在项目根目录生成 `Packages/` 目录结构及下载脚本。

## 使用

### 1. 配置依赖清单

编辑 `Packages/packages.json`：

```json
[
  { "url": "https://github.com/SnapKit/SnapKit" },
  { "url": "https://github.com/onevcat/Kingfisher" },
  { "url": "https://github.com/ccgus/fmdb.git", "version": "2.7.12" }
]
```

- `url`：仓库地址（必填）
- `version`：tag 版本号（可选，不填则拉取默认分支最新代码）

### 2. 执行下载

```bash
./Packages/scripts/fetch-packages.sh
```

脚本自动继承终端的代理设置（`http_proxy` / `https_proxy`），如果访问 GitHub 不稳定，请先在终端配置好代理再执行。

### 3. Xcode 添加本地包

File → Add Package Dependencies → Add Local → 选择 `Packages/Caches/` 下对应文件夹。

每个库只需添加一次，后续更新只跑脚本即可。

### 4. 更新依赖版本

修改 `packages.json` 中的 `version` → 跑脚本 → Xcode 中 Resolve Package Versions。

## 注意事项

- `Packages/Caches/` 应加入 `.gitignore`，不提交三方库源码
- 新同事 clone 项目后，跑一次脚本即可恢复所有依赖
- 如果某个库是其他库的 SPM 依赖（如 fmdb 是 MementoKV 的依赖），也需要一并本地化
- 每个库只需在 Xcode 中 Add Local 一次，后续更新只需跑脚本
