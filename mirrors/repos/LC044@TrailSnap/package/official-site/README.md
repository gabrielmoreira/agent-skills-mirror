# TrailSnap 官网 (Official Site)

这是 TrailSnap 项目的官方文档与落地页网站，基于 [VitePress](https://vitepress.dev/) 构建。

## 目录结构

```
package/official-site/
├── .vitepress/          # VitePress 配置与主题
│   ├── config.mts       # 核心配置文件
│   └── theme/           # 自定义主题 (暂无)
├── docs/                # 文档内容
│   ├── guide/           # 用户指南
│   └── dev/             # 开发者文档
├── index.md             # 首页 (Landing Page)
└── package.json         # 项目依赖
```

## 快速开始

### 1. 安装依赖

```bash
pnpm install
```

### 2. 本地开发

启动本地开发服务器，实时预览修改效果：

```bash
pnpm run docs:dev
```

访问地址通常为：`http://localhost:5173`

### 3. 构建打包

生成静态文件（默认输出到 `.vitepress/dist`）：

```bash
pnpm run docs:build
```

### 4. 本地预览构建产物

在构建完成后，可以预览生成的静态网站：

```bash
pnpm run docs:preview
```

## 部署

本项目已配置 GitHub Actions 自动部署。
每当代码推送到 `main` 分支且涉及 `package/official-site` 目录变更时，会自动构建并将 `dist` 目录推送到 `gh-pages` 分支。

详情请参考项目根目录下的 `.github/workflows/deploy-docs.yml`。
