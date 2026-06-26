# 样式预设参考 (Style Presets Reference)

为 `frontend-slides` 精心设计的视觉样式。

本文件用于：
- 强制性的视口适配（Viewport-fitting）CSS 基础
- 预设选择与氛围映射
- CSS 注意事项与验证规则

仅限抽象形状。除非用户明确要求，否则避免使用插图。

## 视口适配是不可逾越的底线 (Viewport Fit Is Non-Negotiable)

每一张幻灯片必须完全填满一个视口。

### 金科玉律 (Golden Rule)

```text
每一张幻灯片 = 正好一个视口高度。
内容过多 = 拆分为更多幻灯片。
严禁在幻灯片内部滚动。
```

### 密度限制 (Density Limits)

| 幻灯片类型 | 最大内容量 |
|------------|-----------------|
| 标题页 (Title slide) | 1 个标题 + 1 个副标题 + 可选标语 |
| 内容页 (Content slide) | 1 个标题 + 4-6 个项目符号或 2 个段落 |
| 功能网格 (Feature grid) | 最多 6 个卡片 |
| 代码页 (Code slide) | 最多 8-10 行 |
| 引用页 (Quote slide) | 1 条引用 + 署名 |
| 图片页 (Image slide) | 1 张图片，建议高度低于 60vh |

## 强制性基础 CSS (Mandatory Base CSS)

将此代码块复制到生成的每个演示文稿中，然后在此基础上进行主题化。

```css
/* ===========================================
   VIEWPORT FITTING: MANDATORY BASE STYLES
   =========================================== */

html, body {
    height: 100%;
    overflow-x: hidden;
}

html {
    scroll-snap-type: y mandatory;
    scroll-behavior: smooth;
}

.slide {
    width: 100vw;
    height: 100vh;
    height: 100dvh;
    overflow: hidden;
    scroll-snap-align: start;
    display: flex;
    flex-direction: column;
    position: relative;
}

.slide-content {
    flex: 1;
    display: flex;
    flex-direction: column;
    justify-content: center;
    max-height: 100%;
    overflow: hidden;
    padding: var(--slide-padding);
}

:root {
    --title-size: clamp(1.5rem, 5vw, 4rem);
    --h2-size: clamp(1.25rem, 3.5vw, 2.5rem);
    --h3-size: clamp(1rem, 2.5vw, 1.75rem);
    --body-size: clamp(0.75rem, 1.5vw, 1.125rem);
    --small-size: clamp(0.65rem, 1vw, 0.875rem);

    --slide-padding: clamp(1rem, 4vw, 4rem);
    --content-gap: clamp(0.5rem, 2vw, 2rem);
    --element-gap: clamp(0.25rem, 1vw, 1rem);
}

.card, .container, .content-box {
    max-width: min(90vw, 1000px);
    max-height: min(80vh, 700px);
}

.feature-list, .bullet-list {
    gap: clamp(0.4rem, 1vh, 1rem);
}

.feature-list li, .bullet-list li {
    font-size: var(--body-size);
    line-height: 1.4;
}

.grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(min(100%, 250px), 1fr));
    gap: clamp(0.5rem, 1.5vw, 1rem);
}

img, .image-container {
    max-width: 100%;
    max-height: min(50vh, 400px);
    object-fit: contain;
}

@media (max-height: 700px) {
    :root {
        --slide-padding: clamp(0.75rem, 3vw, 2rem);
        --content-gap: clamp(0.4rem, 1.5vw, 1rem);
        --title-size: clamp(1.25rem, 4.5vw, 2.5rem);
        --h2-size: clamp(1rem, 3vw, 1.75rem);
    }
}

@media (max-height: 600px) {
    :root {
        --slide-padding: clamp(0.5rem, 2.5vw, 1.5rem);
        --content-gap: clamp(0.3rem, 1vw, 0.75rem);
        --title-size: clamp(1.1rem, 4vw, 2rem);
        --body-size: clamp(0.7rem, 1.2vw, 0.95rem);
    }

    .nav-dots, .keyboard-hint, .decorative {
        display: none;
    }
}

@media (max-height: 500px) {
    :root {
        --slide-padding: clamp(0.4rem, 2vw, 1rem);
        --title-size: clamp(1rem, 3.5vw, 1.5rem);
        --h2-size: clamp(0.9rem, 2.5vw, 1.25rem);
        --body-size: clamp(0.65rem, 1vw, 0.85rem);
    }
}

@media (max-width: 600px) {
    :root {
        --title-size: clamp(1.25rem, 7vw, 2.5rem);
    }

    .grid {
        grid-template-columns: 1fr;
    }
}

@media (prefers-reduced-motion: reduce) {
    *, *::before, *::after {
        animation-duration: 0.01ms !important;
        transition-duration: 0.2s !important;
    }

    html {
        scroll-behavior: auto;
    }
}
```

## 视口检查清单 (Viewport Checklist)

- 每个 `.slide` 都有 `height: 100vh`、`height: 100dvh` 和 `overflow: hidden`
- 所有排版使用 `clamp()`
- 所有间距使用 `clamp()` 或视口单位 (Viewport units)
- 图片具有 `max-height` 约束
- 网格通过 `auto-fit` + `minmax()` 进行适配
- 在 `700px`、`600px` 和 `500px` 处存在针对矮屏幕的断点 (breakpoints)
- 如果任何内容感到局促，请拆分幻灯片

## 氛围与预设映射 (Mood to Preset Mapping)

| 氛围 | 推荐预设 |
|------|--------------|
| 令人印象深刻 / 自信 (Impressed / Confident) | Bold Signal, Electric Studio, Dark Botanical |
| 兴奋 / 充满活力 (Excited / Energized) | Creative Voltage, Neon Cyber, Split Pastel |
| 冷静 / 专注 (Calm / Focused) | Notebook Tabs, Paper & Ink, Swiss Modern |
| 启发 / 感动 (Inspired / Moved) | Dark Botanical, Vintage Editorial, Pastel Geometry |

## 预设目录 (Preset Catalog)

### 1. Bold Signal (醒目信号)

- 风格：自信、高冲击力、发布会级别 (keynote-ready)
- 适用场景：商业计划书 (pitch decks)、发布会、重要声明
- 字体：Archivo Black + Space Grotesk
- 色板：木炭色底，鲜橙色焦点卡片，清晰的白色文字
- 特色：超大章节编号，深色背景上的高对比度卡片

### 2. Electric Studio (电力工作室)

- 风格：干净、大胆、机构打磨感 (agency-polished)
- 适用场景：客户演示、策略审查
- 字体：仅限 Manrope
- 色板：黑、白、饱和的钴蓝点缀
- 特色：双面板拆分和锋利的社论排版对齐

### 3. Creative Voltage (创意电压)

- 风格：活力十足、复古现代、调皮的自信
- 适用场景：创意工作室、品牌工作、产品叙事
- 字体：Syne + Space Mono
- 色板：电蓝、霓虹黄、深海军蓝
- 特色：半色调纹理、徽章、有冲击力的对比

### 4. Dark Botanical (深色植萃)

- 风格：优雅、高端、有氛围感
- 适用场景：奢侈品牌、深度叙述、高端产品演示
- 字体：Cormorant + IBM Plex Sans
- 色板：近乎黑色、暖象牙白、粉红、金、陶土色
- 特色：模糊的抽象圆圈、纤细的线条、克制的动效

### 5. Notebook Tabs (笔记本标签)

- 风格：编辑感、组织严密、有触感
- 适用场景：报告、审查、结构化叙事
- 字体：Bodoni Moda + DM Sans
- 色板：木炭色背景上的奶油色纸张，搭配粉彩标签
- 特色：纸页效果、彩色侧边标签、活页夹细节

### 6. Pastel Geometry (粉彩几何)

- 风格：亲和力、现代、友好
- 适用场景：产品概览、入职引导、轻快品牌演示
- 字体：仅限 Plus Jakarta Sans
- 色板：淡蓝色背景，奶油色卡片，柔和的粉/薄荷/薰衣草点缀
- 特色：垂直胶囊形、圆角卡片、柔和阴影

### 7. Split Pastel (拆分粉彩)

- 风格：调皮、现代、创意
- 适用场景：机构介绍、工作坊、作品集
- 字体：仅限 Outfit
- 色板：桃色 + 薰衣草色拆分，搭配薄荷色徽章
- 特色：拆分背景、圆角标签、轻质网格叠加层

### 8. Vintage Editorial (复古社论)

- 风格：诙谐、个性十足、杂志启发
- 适用场景：个人品牌、有观点的演讲、叙事
- 字体：Fraunces + Work Sans
- 色板：奶油色、木炭色、尘土色调的暖色点缀
- 特色：几何点缀、带边框的标注块、有冲击力的衬线标题

### 9. Neon Cyber (霓虹赛博)

- 风格：未来感、科技感、律动
- 适用场景：AI、基础设施、开发者工具、关于未来的演讲
- 字体：Clash Display + Satoshi
- 色板：午夜蓝、青色、洋红色
- 特色：发光效果、粒子、网格、数据雷达动能

### 10. Terminal Green (终端绿)

- 风格：开发者导向、黑客极简
- 适用场景：API、CLI 工具、工程演示
- 字体：仅限 JetBrains Mono
- 色板：GitHub 深色 + 终端绿
- 特色：扫描线、命令行框架、精确的等宽节奏

### 11. Swiss Modern (瑞士现代)

- 风格：极简、精确、数据优先
- 适用场景：企业、产品策略、分析报告
- 字体：Archivo + Nunito
- 色板：白、黑、信号红
- 特色：可见网格、不对称、几何规范

### 12. Paper & Ink (纸墨)

- 风格：文学感、有深度、故事驱动
- 适用场景：论文、主题演讲叙事、宣言演示
- 字体：Cormorant Garamond + Source Serif 4
- 色板：暖奶油色、木炭色、绯红点缀
- 特色：引句块 (pull quotes)、首字下沉 (drop caps)、优雅的线条

## 直接选择提示词 (Direct Selection Prompts)

如果用户已经知道他们想要的样式，请让他们直接从上述预设名称中挑选，而不是强行生成预览。

## 动画效果映射 (Animation Feel Mapping)

| 感觉 | 运动方向 |
|---------|------------------|
| 戏剧化 / 电影感 (Dramatic / Cinematic) | 缓慢淡入淡出、视差、大幅缩入 (scale-ins) |
| 科技感 / 未来感 (Techy / Futuristic) | 发光、粒子、网格运动、乱码文本 (scramble text) |
| 调皮 / 友好 (Playful / Friendly) | 弹性缓动 (springy easing)、圆角形状、浮动运动 |
| 专业 / 企业 (Professional / Corporate) | 微妙的 200-300ms 过渡、干净的切页 |
| 冷静 / 极简 (Calm / Minimal) | 非常克制的动作、留白优先 |
| 社论 / 杂志感 (Editorial / Magazine) | 强等级感、文本与图片的交错互动 |

## CSS 注意事项：负函数 (CSS Gotcha: Negating Functions)

严禁这样写：

```css
right: -clamp(28px, 3.5vw, 44px);
margin-left: -min(10vw, 100px);
```

浏览器会默默忽略它们。

请务必改写为：

```css
right: calc(-1 * clamp(28px, 3.5vw, 44px));
margin-left: calc(-1 * min(10vw, 100px));
```

## 验证尺寸 (Validation Sizes)

最低限度测试：
- 桌面端：`1920x1080`, `1440x900`, `1280x720`
- 平板端：`1024x768`, `768x1024`
- 移动端：`375x667`, `414x896`
- 横屏手机：`667x375`, `896x414`

## 反模式 (Anti-Patterns)

不要使用：
- 白底紫色的初创公司模板
- 将 Inter / Roboto / Arial 作为视觉声音，除非用户明确想要实用的中性风格
- 项目符号墙 (bullet walls)、微小的字体或需要滚动的代码块
- 抽象几何图形能做得更好的地方却使用装饰性插图
