# drawio viewer (vendored)

用于在工作区文件浏览里预览 `.drawio` 文件的官方 viewer 脚本,直接 vendor 进仓库以避免运行时从外网拉取。

- **来源**: https://github.com/jgraph/drawio (发布产物 `viewer-static.min.js`)
- **版本**: `30.0.4`(以 min.js 内嵌的 `VERSION` 字符串为准,`pnpm licenses:generate` 会自动解析)
- **License**: Apache-2.0(见同目录 `LICENSE`,Copyright (c) JGraph Ltd)
- **附加限制说明**: 上游对其 icon set / stencil / 模板**素材**另有"未经书面许可不得用于 Atlassian 产品"的附加条款;本目录只 vendor viewer **代码本体**,不包含也不分发那些素材,该限制对本产品不适用。

## 更新方式

从上游仓库或 diagrams.net 发布产物取新版 `viewer-static.min.js` 覆盖本目录同名文件,然后运行 `pnpm licenses:generate` 刷新第三方声明(版本号自动从 min.js 解析,无需手改)。

## 使用入口

`apps/desktop/src/renderer/features/cc-agent/workdir-browse/DrawioPreview.tsx` —— 首次打开 `.drawio` 文件时动态注入 `<script>` 加载(约 3.6MB,不进 main bundle),后续复用。业务方不要直接 import 本目录。
