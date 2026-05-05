---
name: "trailsnap-cli"
description: "TrailSnap CLI 命令行工具，用于查询照片、相册、标签、位置和人物等信息。当用户需要查看照片、相册数据时调用此技能。"
---

# TrailSnap CLI 技能

此技能允许使用 `trailsnap`工具 与 TrailSnap 后端 API 进行交互。

## 功能
1. 根据指定条件（可选过滤参数）查询照片列表。
2. 查询分类标签、相册、位置和人物（面部）信息。
3. 查询某张照片的详细信息。

## 安装

使用以下命令检查是否安装了 `trailsnap` 工具，如果没有安装则可以参考[install.md](install.md)文档进行安装。

```bash
trailsnap -v
```

## 初始配置

首次使用该工具时，需要配置 API 地址和 Token。你可以使用以下命令来判断是否需要配置 API 地址和 Token：

```bash
trailsnap photos list --limit 1
```

如果你收到错误信息，说明你需要配置 API 地址和 Token。可以询问用户这两个信息，然后通过以下命令进行配置：
```bash
trailsnap config set --url <API_BASE_URL> --token <YOUR_API_TOKEN>
```

## 使用方法

使用前可以通过 `trailsnap <command> -h` 或 `trailsnap <command> <subcommand> -h` 查看每个命令的详细帮助信息。通常情况下，你需要先根据用户的问题逐步筛选出检索条件（一个简单的[示例](examples/simple.md)），然后查询符合条件的照片列表。

- `locations timeline` 命令能够查到时间和空间上的信息，是一个很好的工具，返回一个足迹时间轴（某一段时间去了那个地方）。
- 除非用户不需要显示照片，否则都要以合适的格式展示照片，如果需要显示某张照片，你可以使用 `medias` 命令获取其URL地址或者照片文件。
- 在使用之前你需要阅读 [reference.md](reference.md) 文件，了解每个命令的详细参数和选项。
- 如果需要的话，可以参考 [examples/simple.md](examples/simple.md) 文件，了解如何使用该工具。

使用 Python 运行脚本：

```bash
trailsnap <command> <subcommand> [options]
```

## 生成的 HTML 页面规范

- 整体风格：极简轻复古治愈手账风，低饱和莫兰迪配色，奶白米杏主色调，柔和浅阴影、统一大圆角；
- 布局：响应式卡片布局，时间倒序展示；
- 单卡片结构：日期头部→相册图片区→日记正文→轻量化标签；
- 视觉：无高饱和颜色、无复杂动效、无冗余组件，字体舒适留白充足；
- 功能：支持单图/多图相册展示、标签分类、图片点击放大；
- 产出要求：纯轻量化HTML，结构整洁，适配本地静态浏览，对接相册图片url地址直接预览，文案温柔生活化。
