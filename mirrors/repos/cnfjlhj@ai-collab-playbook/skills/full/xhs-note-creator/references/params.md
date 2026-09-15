# 参数参考文档

## 渲染脚本（render_xhs.py）

```bash
python scripts/render_xhs.py <markdown_file> [options]
```

### 参数

| 参数 | 简写 | 说明 | 默认值 |
|---|---|---|---|
| `--output-dir` | `-o` | 输出目录 | 当前工作目录 |
| `--theme` | `-t` | 排版主题 | `default` |
| `--mode` | `-m` | 分页模式 | `separator` |
| `--width` | `-w` | 图片宽度（px） | `1080` |
| `--height` | | 图片高度（`dynamic` 下为最小高度） | `1440` |
| `--max-height` | | `dynamic` 模式下的最大高度 | `4320` |
| `--dpr` | | 设备像素比 | `2` |

### 主题

`default`、`playful-geometric`、`neo-brutalism`、`botanical`、`professional`、`retro`、`terminal`、`sketch`

### 分页模式

| 值 | 说明 |
|---|---|
| `separator` | 按 `---` 分隔符分页 |
| `auto-fit` | 固定尺寸，自动整体缩放内容 |
| `auto-split` | 根据渲染后高度自动切分 |
| `dynamic` | 根据内容动态调整图片高度 |

### 示例

```bash
python scripts/render_xhs.py assets/example.md
python scripts/render_xhs.py assets/example.md -m auto-split
python scripts/render_xhs.py assets/example.md -m auto-fit
python scripts/render_xhs.py assets/example.md -t professional -m dynamic --width 1080 --height 1440 --dpr 2
```

## 发布脚本（publish_xhs.py）

```bash
python scripts/publish_xhs.py --title "标题" --desc "描述" --images cover.png card_1.png
```

### 参数

| 参数 | 简写 | 说明 | 默认值 |
|---|---|---|---|
| `--title` | `-t` | 笔记标题（超过 20 字会截断） | 必填 |
| `--desc` | `-d` | 笔记描述/正文 | `""` |
| `--desc-file` | | 从 UTF-8 文件读取描述，保留换行 | 无 |
| `--images` | `-i` | 图片路径，可传多个 | `[]` |
| `--images-glob` | | 用 glob 收集图片并自然排序 | 无 |
| `--require-image-count` | | 要求最终图片数严格匹配 | 无 |
| `--private` | | 明确设为仅自己可见 | 默认行为 |
| `--public` | | 明确设为公开 | `False` |
| `--post-time` | | 定时发布，格式 `2024-01-01 12:00:00` | 立即发布 |
| `--api-mode` | | 通过 xhs-api 服务发布 | 本地模式 |
| `--api-url` | | API 服务地址 | `http://localhost:5005` |
| `--dry-run` | | 仅验证，不实际发布 | `False` |
| `--verbose` | | 显示底层库输出 | `False` |
| `--debug-json` | | 将结果写入 JSON；可能含敏感信息 | 无 |

默认发布为仅自己可见。确认结果无误后，显式使用 `--public` 才会公开。

```bash
# 私密预览
python scripts/publish_xhs.py -t "标题" --desc-file desc.txt --images-glob "out/*.png" --dry-run

# 验证图片数量
python scripts/publish_xhs.py -t "标题" -d "描述" -i cover.png card_1.png --require-image-count 2 --dry-run

# 明确公开发布
python scripts/publish_xhs.py -t "标题" -d "描述" -i cover.png card_1.png --public
```

## 环境变量

```bash
cp env.example.txt .env
```

`.env` 至少需要 `XHS_COOKIE`。Cookie、`.env`、浏览器 profile 和 `--debug-json` 结果都不得提交或共享。

## Markdown 格式

```yaml
---
emoji: "🚀"
title: "封面标题"
subtitle: "封面副标题"
---
```

在正文中使用 `---` 手动分卡；这与文件开头的 YAML frontmatter 分隔符是两种不同用途。
