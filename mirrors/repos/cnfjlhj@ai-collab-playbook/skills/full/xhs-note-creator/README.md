# xhs-note-creator

生成小红书笔记文案、多主题卡片和可选发布流程。
---

## ✨ 功能

- **🎨 8 套主题皮肤**：默认简约灰 + Playful Geometric / Neo-Brutalism / Botanical / Professional / Retro / Terminal / Sketch
- **📐 4 种分页模式**：
  - `separator`：按 `---` 分隔手动分页
  - `auto-fit`：固定尺寸，自动整体缩放内容，避免溢出/大面积留白
  - `auto-split`：根据渲染后高度自动拆分为多张卡片
  - `dynamic`：根据内容动态调整图片高度
- **🧱 统一卡片结构**：外层浅灰背景（`card-container`）+ 内层主题背景（`card-inner`）+ 纯排版层（`card-content`）
- **🧠 封面与正文一体化**：封面背景、标题渐变和正文卡片背景都按主题自动匹配

---

## 🖼 主题预览

仓库提供 8 套主题。使用 `assets/example.md` 可直接生成封面和正文卡片进行比较：

```bash
python scripts/render_xhs.py assets/example.md -t professional -m auto-split
```
---

## 🚀 使用方式总览

### 1. 克隆项目

```bash
git clone https://github.com/cnfjlhj/ai-collab-playbook.git
cd ai-collab-playbook/skills/full/xhs-note-creator
```

可以将本项目放到支持 Skills 的客户端目录，例如：

- Claude：`~/.claude/skills/`
- Alma：`~/.config/Alma/skills/`
- TRAE：`/your-path/.trae/skills/`

### 2. 安装依赖

**Python：**

```bash
pip install -r requirements.txt
playwright install chromium
```

> 若系统已安装 Chrome，可跳过浏览器下载，并在渲染时设置 `PLAYWRIGHT_CHROMIUM_EXECUTABLE=/path/to/google-chrome`。

**Node.js：**

```bash
npm install
npx playwright install chromium
```

---

## 🎨 渲染图片（Python）

核心脚本：`scripts/render_xhs.py`

```bash
# 最简单用法（默认主题 + 手动分页）
python scripts/render_xhs.py assets/example.md

# 使用自动分页（推荐：内容长短难控）
python scripts/render_xhs.py assets/example.md -m auto-split

# 使用固定尺寸自动缩放（auto-fit）
python scripts/render_xhs.py assets/example.md -m auto-fit

# 切换主题（例如 Playful Geometric）
python scripts/render_xhs.py assets/example.md -t playful-geometric -m auto-split

# 自定义尺寸和像素比
python scripts/render_xhs.py assets/example.md -t retro -m dynamic --width 1080 --height 1440 --max-height 2160 --dpr 2
```

**主要参数：**

| 参数 | 简写 | 说明 |
|------|------|------|
| `--theme` | `-t` | 主题：`default`、`playful-geometric`、`neo-brutalism`、`botanical`、`professional`、`retro`、`terminal`、`sketch` |
| `--mode` | `-m` | 分页模式：`separator` / `auto-fit` / `auto-split` / `dynamic` |
| `--width` | `-w` | 图片宽度（默认 1080） |
| `--height` |  | 图片高度（默认 1440，`dynamic` 为最小高度） |
| `--max-height` |  | `dynamic` 模式最大高度（默认 4320） |
| `--dpr` |  | 设备像素比，控制清晰度（默认 2） |

> 生成结果会包含：封面 `cover.png` + 正文卡片 `card_1.png`、`card_2.png`...

---

## 🎨 渲染图片（Node.js）

脚本：`scripts/render_xhs.js`，参数与 Python 基本一致：

```bash
# 默认主题 + 手动分页
node scripts/render_xhs.js assets/example.md

# 指定主题 + 自动分页
node scripts/render_xhs.js assets/example.md -t terminal -m auto-split
```

---

## 📤 发布到小红书

### 1. 配置 Cookie

```bash
cp env.example.txt .env
```

编辑 `.env`：

```env
XHS_COOKIE=your_cookie_string_here
```

> 获取方式：浏览器登录小红书 → F12 → Network → 任意请求的 Cookie 头，复制整串。

### 2. 手动发布（可选）

```bash
python scripts/publish_xhs.py \
  --title "笔记标题" \
  --desc "笔记描述内容" \
  --images cover.png card_1.png card_2.png
```

> 默认发布为仅自己可见。确认内容无误后，显式添加 `--public` 才会公开。

**可选参数：**

| 参数 | 说明 |
|------|------|
| `--public` | 公开发布（默认仅自己可见） |
| `--post-time "2024-01-01 12:00:00"` | 定时发布 |
| `--api-mode` | 通过 xhs-api 服务发布 |
| `--dry-run` | 仅验证，不实际发布 |

---

## 📁 项目结构

```text
xhs-note-creator/
├── SKILL.md
├── README.md
├── STYLES.md
├── requirements.txt
├── package.json
├── package-lock.json
├── env.example.txt
├── references/
│   └── params.md
├── assets/
│   ├── cover.html
│   ├── card.html
│   ├── styles.css
│   ├── example.md
│   └── themes/
│       ├── default.css
│       ├── playful-geometric.css
│       ├── neo-brutalism.css
│       ├── botanical.css
│       ├── professional.css
│       ├── retro.css
│       ├── terminal.css
│       └── sketch.css
└── scripts/
    ├── render_xhs.py
    ├── render_xhs_v2.py
    ├── render_xhs.js
    ├── render_xhs_v2.js
    └── publish_xhs.py
```

---

## ⚠️ 注意事项

1. **Cookie 安全**：不要把 `.env` 提交到 Git 或共享出去。
2. **Cookie 有效期**：过期后发布失败是正常现象，重新抓一次 Cookie 即可。
3. **发布频率**：避免短时间内高频发布，以免触发平台风控。
4. **图片尺寸**：默认 1080×1440px，符合小红书推荐比例。

---

## 🙏 致谢

- [Playwright](https://playwright.dev/) - 浏览器自动化渲染
- [Marked](https://marked.js.org/) - Markdown 解析
- [xhs](https://github.com/ReaJason/xhs) - 小红书 API 客户端

---

## 📄 License

MIT License © 2026
