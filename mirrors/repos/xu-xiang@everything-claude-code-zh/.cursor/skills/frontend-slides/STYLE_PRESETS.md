# 样式预设参考 (Style Presets Reference)

为 `frontend-slides` 精选的视觉样式。

使用此文件用于：
- 必须的视口适配（Viewport-fitting）CSS 基础
- 预设选择与氛围映射
- CSS 注意事项与验证规则

仅限抽象形状。除非用户明确要求，否则避免使用插图。

## 视口适配是不可逾越的底线 (Viewport Fit Is Non-Negotiable)

每张幻灯片必须完全填满一个视口。

### 金科玉律 (Golden Rule)

```text
每张幻灯片 = 恰好一个视口高度。
内容过多 = 拆分为更多幻灯片。
严禁在幻灯片内滚动。
```

### 密度限制 (Density Limits)

| 幻灯片类型 | 最大内容量 |
|------------|-----------------|
| 标题页 (Title slide) | 1 个标题 + 1 个副标题 + 可选标语 |
| 内容页 (Content slide) | 1 个标题 + 4-6 个项目符号或 2 个段落 |
| 特性网格 (Feature grid) | 最多 6 个卡片 |
| 代码页 (Code slide) | 最多 8-10 行 |
| 引用页 (Quote slide) | 1 个引用 + 署名 |
| 图片页 (Image slide) | 1 张图片，理想情况下在 60vh 以下 |

## 强制性基础 CSS (Mandatory Base CSS)

将此代码块复制到每个生成的演示文稿中，然后在此基础上进行主题化。

```css
/* ===========================================
   视口适配：强制性基础样式
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

## 视口自查表 (Viewport Checklist)

- 每个 `.slide` 都有 `height: 100vh`、`height: 100dvh` 和 `overflow: hidden`
- 所有排版（Typography）都使用 `clamp()`
- 所有间距都使用 `clamp()` 或视口单位（Viewport units）
- 图片有 `max-height` 约束
- 网格使用 `auto-fit` + `minmax()` 进行自适应
- 在 `700px`、`600px` 和 `500px` 处存在针对短屏幕的断点
- 如果感觉拥挤，请拆分幻灯片

## 氛围与预设映射 (Mood to Preset Mapping)

| 氛围 (Mood) | 推荐预设 (Good Presets) |
|------|--------------|
| 印象深刻 / 自信 (Impressed / Confident) | Bold Signal, Electric Studio, Dark Botanical |
| 兴奋 / 充满活力 (Excited / Energized) | Creative Voltage, Neon Cyber, Split Pastel |
| 冷静 / 专注 (Calm / Focused) | Notebook Tabs, Paper & Ink, Swiss Modern |
| 启发 / 感动 (Inspired / Moved) | Dark Botanical, Vintage Editorial, Pastel Geometry |

## 预设目录 (Preset Catalog)

### 1. Bold Signal

- 氛围：自信、高影响力、主题演讲级别
- 适用场景：融资路演（Pitch decks）、发布会、声明
- 字体：Archivo Black + Space Grotesk
- 色板：深炭色底色、亮橙色焦点卡片、锐利白文本
- 标志性设计：超大章节数字、暗色背景上的高对比度卡片

### 2. Electric Studio

- 氛围：简洁、大胆、专业机构质感
- 适用场景：客户演示、战略回顾
- 字体：仅 Manrope
- 色板：黑、白、高饱和度钴蓝装饰色
- 标志性设计：双面板分割和锐利的编辑风格对齐

### 3. Creative Voltage

- 氛围：充满活力、复古现代、俏皮的自信
- 适用场景：创意工作室、品牌工作、产品故事讲述
- 字体：Syne + Space Mono
- 色板：电蓝、霓虹黄、深海军蓝
- 标志性设计：半调（Halftone）纹理、徽章、有张力的对比

### 4. Dark Botanical

- 氛围：优雅、高端、有氛围感
- 适用场景：奢侈品牌、深度叙事、高端产品演示
- 字体：Cormorant + IBM Plex Sans
- 色板：近黑色、暖象牙白、腮红粉、金色、赤陶土色
- 标志性设计：模糊的抽象圆圈、细腻的细线装饰、克制的动画

### 5. Notebook Tabs

- 氛围：社论风格、条理分明、有触感
- 适用场景：报告、评审、结构化故事讲述
- 字体：Bodoni Moda + DM Sans
- 色板：炭色背景上的奶油纸张色，搭配马卡龙色标签
- 标志性设计：纸张床、彩色侧边标签、活页夹细节

### 6. Pastel Geometry

- 氛围：平易近人、现代、友好
- 适用场景：产品概览、入职引导、轻量化品牌演示
- 字体：仅 Plus Jakarta Sans
- 色板：淡蓝色背景、奶油色卡片、柔和的粉/薄荷绿/薰衣草紫装饰色
- 标志性设计：垂直胶囊形状、圆角卡片、柔和阴影

### 7. Split Pastel

- 氛围：俏皮、现代、创意
- 适用场景：机构介绍、研讨会、作品集
- 字体：仅 Outfit
- 色板：桃红色 + 薰衣草紫分割，搭配薄荷绿徽章
- 标志性设计：分割背景、圆角标签、轻量化网格叠加

### 8. Vintage Editorial

- 氛围：诙谐、个性驱动、杂志风格
- 适用场景：个人品牌、有见地的演讲、故事讲述
- 字体：Fraunces + Work Sans
- 色板：奶油色、炭色、灰调暖色装饰色
- 标志性设计：几何装饰、带边框的标注块、有张力的衬线标题

### 9. Neon Cyber

- 氛围：未来感、科技感、动力十足
- 适用场景：AI、基础设施、开发者工具、“未来的 X” 主题演讲
- 字体：Clash Display + Satoshi
- 色板：午夜蓝、青色、品红
- 标志性设计：发光效果、粒子、网格、数据雷达能量感

### 10. Terminal Green

- 氛围：开发者导向、极客简洁
- 适用场景：API、CLI 工具、工程演示
- 字体：仅 JetBrains Mono
- 色板：GitHub 暗色 + 终端绿
- 标志性设计：扫描线、命令行框架、精准的等宽节奏

### 11. Swiss Modern

- 氛围：极简、精准、数据优先
- 适用场景：企业、产品战略、分析报告
- 字体：Archivo + Nunito
- 色板：白、黑、信号红
- 标志性设计：可见网格、不对称设计、几何纪律感

### 12. Paper & Ink

- 氛围：文学感、有深度、故事驱动
- 适用场景：文章、主题演讲叙事、宣言演示
- 字体：Cormorant Garamond + Source Serif 4
- 色板：暖奶油色、炭色、深红色装饰色
- 标志性设计：侧边引用、首字下沉、优雅的细线

## 直接选择提示词 (Direct Selection Prompts)

如果用户已经知道他们想要的样式，让他们直接从上面的预设名称中选择，而不是强制生成预览。

## 动画感觉映射 (Animation Feel Mapping)

| 感觉 (Feeling) | 运动方向 (Motion Direction) |
|---------|------------------|
| 戏剧性 / 电影感 (Dramatic / Cinematic) | 缓慢淡入、视差、大比例缩放进入 |
| 科技感 / 未来感 (Techy / Futuristic) | 发光、粒子、网格运动、乱码文本（Scramble text） |
| 俏皮 / 友好 (Playful / Friendly) | 弹性缓动（Springy easing）、圆润形状、漂浮感运动 |
| 专业 / 企业 (Professional / Corporate) | 微妙的 200-300ms 过渡、简洁的滑动 |
| 冷静 / 极简 (Calm / Minimal) | 非常克制的动作、空白优先 |
| 社论 / 杂志 (Editorial / Magazine) | 强等级感、交错的文本与图片互动 |

## CSS 注意事项：负值函数 (CSS Gotcha: Negating Functions)

千万不要这样写：

```css
right: -clamp(28px, 3.5vw, 44px);
margin-left: -min(10vw, 100px);
```

浏览器会静默忽略它们。

请务必改为这样写：

```css
right: calc(-1 * clamp(28px, 3.5vw, 44px));
margin-left: calc(-1 * min(10vw, 100px));
```

## 验证尺寸 (Validation Sizes)

至少测试以下尺寸：
- 桌面端 (Desktop): `1920x1080`, `1440x900`, `1280x720`
- 平板端 (Tablet): `1024x768`, `768x1024`
- 移动端 (Mobile): `375x667`, `414x896`
- 横屏手机 (Landscape phone): `667x375`, `896x414`

## 反模式 (Anti-Patterns)

不要使用：
- 白底紫色的初创公司模板
- Inter / Roboto / Arial 作为视觉核心，除非用户明确要求功利性的中立感
- 满屏的项目符号、微小的字号或需要滚动的代码块
- 当抽象几何图形能做得更好时，使用装饰性插图
