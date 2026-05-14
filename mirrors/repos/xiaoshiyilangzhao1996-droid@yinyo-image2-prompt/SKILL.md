---
name: yinyo-image2-prompt
description: GPT-Image-2 万能 Prompt 工程师。覆盖写实摄影、产品Mockup、电影质感、Pixar 3D、UI截图、信息图、Logo/品牌系统、水墨海报、科普海报、收藏玩具、动作分解表等全场景，35个子模板+5-Phase引导流程，输出完整高质量prompt + 参数建议。
version: 1.6.0
last_updated: 2026-05-07
changelog: |
  v1.6.0 (2026-05-07): 苍何横比吸收6个复杂模板+Logo三合一升级+负面约束+A/B策略
  v1.5.0 (2026-05-07): 达尔文审视。盲评表前移+Mockup标注+编辑决策树+Phase 2精简
  v1.4.0 (2026-05-07): 5-Phase引导式流程重构
  v1.0.0 (2026-05-06): 首版发布
---

# yinyo-image2-prompt — GPT-Image-2 万能 Prompt 工程师

## 用途

当用户需要使用 GPT-Image-2 生成**非纯文字海报**的高质量图片时，使用本 skill。

**适用场景**：写实摄影、产品Mockup、App UI截图、电影质感、Pixar 3D角色、信息图、Logo、漫画条、360°全景、等轴微缩场景、动作人偶、复古交易卡、创意概念图等。

**不适用场景**：以字体美学为核心的文字海报 → 使用 `image2-typography-poster` skill。

---

## 一、GPT-Image-2 核心能力速查

| 能力 | 表现 | Prompt 建议 |
|------|------|------------|
| 文字渲染 | 拉丁/中/日/韩/阿拉伯文 ≥95% | 关键文字 1-5 词，英文引号包裹 |
| 多元素构图 | 单图稳定承载 150+ 元素 | 用编号或列表分组 |
| 人脸一致性 | persistent embedding 跨图保持 | 固定描述年龄/种族/特征/服饰 |
| 物理材质 | 金属反射、湿地、玻璃折射正确 | 明确提及材质名和光源 |
| 编辑模式 | 原图 + edit 端点精确局部调整 | "preserve everything else" 锁定 |
| 世界知识 | 内置推理，理解真实事件/场景 | 可隐含上下文 |
| 4K 输出 | 原生 4K + 自定义尺寸 | 超出像素预算自动缩放 |

---

## 二、Prompt 写作 5 大铁律

> ⚠️ 这 5 条是 OpenAI 官方 + 社区共识，**每次写 prompt 都必须遵守**。

### 铁律 1：主题前置
核心主体放 prompt 开头。模型对前 30% 文字赋予最高权重。
→ 主体不会被环境描述淹没。

### 铁律 2：结构化场景
顺序：**场景 → 主体 + 动作 → 视觉风格/介质 → 镜头参数 → 光线 → 构图 → 约束**
→ 复杂构图不会丢失元素。

### 铁律 3：文字用英文引号
所有要出现在图片中的文字用 `"..."` 包裹。
→ 文字渲染成功率从 70% → 95%+。

### 铁律 4：明确镜头与光线
指定具体参数：焦距（24mm/35mm/50mm/85mm/100mm macro）、光圈（f/1.4/f/2/f/4）、角度（eye-level/low-angle/bird's-eye）、色温（3200K warm/5600K daylight）。
→ gpt-image-2 集成物理引擎，镜头参数有实际效果。

### 铁律 5：编辑时分离"变与不变"
修改图片时，明确分为：`Change: ...` / `Preserve: ...`
→ 每次编辑都要重复不变量清单，防止漂移。

---

## 三、gpt-image-2 vs 旧版本关键差异

| 维度 | 1.5 时代做法 | 2.0 正确做法 |
|------|------------|------------|
| 关键词堆砌 | "8K, ultra detailed, masterpiece" 必须 | ❌ 完全无效，浪费语义空间 |
| 负面提示词 | "no text, no watermark" | ✅ 改用正面约束句 |
| 文字渲染 | 限 1-2 词，易出错 | 支持 3-5 词，多行短句 |
| 镜头描述 | 可选装饰 | **强烈推荐**，有物理效果 |
| 编辑模式 | 重新生成 | 优先 edit 端点 |

> 💡 迁移经验：旧 prompt 约 70% 只需删除冗余形容词就能获得更好效果。

---

## 四、Prompt 结构公式

### 通用结构（每次生成必用）
```
[场景描述，1-2句]
[主体描述 + 动作/状态，2-3句]
[视觉风格 / 介质，1句]
[镜头参数：焦距 + 光圈 + 角度，1句]
[光线描述：方向 + 色温 + 质感，1-2句]
[构图：框架 + 前景/中景/背景，1句]
[约束：排除项 / 不变量，1-2句]
Style: [风格标签]
```

### Style 标签速查
| 标签 | 风格 | 最佳适用 |
|------|------|----------|
| `editorial-magazine` | 杂志排版 | 海报、UI |
| `studio-product` | 棚拍产品 | 产品包装 |
| `cinematic-anamorphic` | 变形宽银幕 | 电影质感 |
| `pixar-3d` | 皮克斯 3D | 角色、吉祥物 |
| `kodak-portra-400` | 柯达胶片 | 写实人像 |
| `raw-documentary` | 原始纪实 | 街拍、生活 |

---

## 五、场景识别与模板选择

收到用户需求后，先判断属于以下哪个场景类别，再套用对应模板。

### 场景分类表

| 场景类别 | 关键词信号 | 对应模板 |
|----------|-----------|----------|
| 🎯 写实摄影 | 人像、街拍、胶片、照片感、真实 | → 模板 A |
| 📦 产品 Mockup | 产品照、电商、包装、广告图 | → 模板 B |
| 🎬 电影质感 | 电影、剧照、宽银幕、氛围 | → 模板 C |
| 🧸 Pixar 3D | 3D、卡通角色、吉祥物、皮克斯 | → 模板 D |
| 📱 App UI | App界面、手机截图、UI设计 | → 模板 E |
| 📊 信息图 | 信息图、图解、数据可视化、infographic | → 模板 F |
| 🎨 Logo与品牌系统 | Logo、标志、品牌VI、品牌手册、品牌触点 | → 模板 G |
| 🏙️ 等轴微缩 | 等轴、3D微缩、isometric、SaaS头图 | → 模板 H |
| 🃏 创意概念 | 交易卡、人偶包装、漫画条、360全景、拆解板、水墨海报、科普海报、品牌视觉板、动作表、收藏玩具 | → 模板 I |
| 🖼️ 编辑工作流 | 修改现有图、风格迁移、局部调整 | → 模板 J |
| 🎭 概念插画/场景卡片 | 节日卡、故事场景、情感插画、概念艺术 | → 模板 K |

### 模板有效性速查（33组盲评硬数据）

> **核心原则**：知道什么时候不用模板，比模板本身更重要。查完这张表再决定是否套模板。

| 场景 | 模板效果 | 结论 |
|------|---------|------|
| Pixar 3D | 0:3 大败 | ❌ **不套模板**，保持简洁 |
| 概念插画 | 0:3 大败 | ❌ **不套模板**，保持叙事性 |
| 写实摄影 | 3:3 平手 | ⚠️ 模板无加成，简洁模式即可 |
| 创意概念 | 2:2 平手 | ⚠️ 视情况，简单场景不套 |
| 等轴微缩 | 1:1 平手 | ⚠️ 模板无加成 |
| App UI | 2:0 大胜 | ✅ **必须用模板E** |
| Logo/品牌 | 2:0 大胜 | ✅ **必须用模板G** |
| 编辑工作流 | 3:0 大胜 | ✅ **必须用模板J** |
| 电影质感 | 2:1 胜 | ✅ **推荐模板C** |
| 信息图 | 1:1 平手 | ⚠️ 模板F有帮助但非必须 |
| 产品Mockup | 1:2 败 | ⚠️ 原版prompt可能更好，见模板B |

---

## 六、场景模板库

### 模板 A：写实摄影（Photorealism）

**核心原则**：像描述一张正在被拍下的真实照片。用摄影语言，要求真实质感（毛孔、皱纹、织物磨损、瑕疵）。避免暗示影棚修饰的词。

> ⚠️ **关键区分**：写实摄影分两种——**场景人像**（有故事、有动作、有环境）和**棚拍人像**（静态、可控光线、纯背景）。选错模板会丢失叙事性。

#### A1：场景人像 / 叙事肖像（Story Portrait）
> 适用：有故事感的人像——人物在做某件事、在某个真实环境中、有互动元素
> 特点：需要叙事、动作、环境细节、情绪引导

```
Create a photorealistic candid photograph of a [AGE]-year-old
[ETHNICITY] [GENDER] with [HAIR DESCRIPTION] and [DISTINCTIVE FEATURE].
[人物正在做什么动作] while [伴随状态/互动元素].
[LOCATION] — [环境细节1], [环境细节2], [环境细节3].
Shot like a 35mm film photograph, [SHOT TYPE] at [ANGLE],
using a [FOCAL LENGTH] lens.
[LIGHTING: direction, quality, color temperature].
The image should feel [情绪词: honest/unposed/intimate/contemplative],
with real skin texture, worn materials, and everyday detail.
[约束: No glamorization, no heavy retouching, no studio polish.]
```

**情绪词速查**：
| 情绪 | 适用场景 |
|------|----------|
| honest, unposed | 纪实、生活 |
| intimate, warm | 私密、家庭 |
| contemplative, powerful | 沉思、孤独 |
| raw, gritty | 街头、底层 |
| dreamy, ethereal | 梦幻、浪漫 |

#### A2：棚拍人像（Studio Portrait）
> 适用：标准人像照——可控光线、简洁背景、突出五官

```
Photorealistic medium close-up portrait of a [AGE]-year-old
[ETHNICITY] [GENDER] with [HAIR DESCRIPTION] and [DISTINCTIVE FEATURE].
Wearing [CLOTHING DESCRIPTION], seated in [LOCATION].
Shot on a 35mm full-frame camera with a 50mm f/1.4 lens,
shallow depth of field, golden hour window light from camera left,
3200K warm color temperature.
Natural skin texture with visible pores, sharp focus on eyes,
slight film grain, no smoothing or beauty filter.
Vertical 4:5 framing.
```

> 跨图一致性：保持 [ETHNICITY] [HAIR] [DISTINCTIVE FEATURE] 一致，embedding 持久化会维持面部一致。

#### A3：iPhone 街拍 / 生活快照
> 适用：iPhone随拍、生活记录、社交媒体真实感
> 特点：**简洁为王**，不要过度结构化

```
Amateur iPhone photo of [SCENE + 主体 + 动作].
Shot from [ANGLE], natural [TIME OF DAY] light, no flash.
Environment: [2-3 个真实环境细节].
The image should look like a very authentic life slice.
```

> ⚠️ 如果用户输入已经足够简洁有力（如 "Amateur iPhone photo at Apple Park, Tim Cook presenting on stage. Shot from the crowd at a distance"），**不要膨胀它**。只补全缺失要素。

#### A4：35mm 胶片风格
```
35mm film photography, [AESTHETIC ADJECTIVE] aesthetic,
soft ambient [LIGHTING TYPE] lighting mixed with gentle natural window light,
subtle film grain, gentle color shift, high atmosphere editorial style,
intimate medium shot, [SUBJECT DESCRIPTION].
[PHYSICAL DETAILS — 皮肤质感、发型、服装]
[LIGHTING: direction, color temperature, quality]
[POSE & LOCATION]
```

#### A5：RAW 纪实 / 瞬间抓拍
> 适用：地铁站、便利店、街头——追求"未经修饰的真实"
> 特点：**诗意简洁**，保留原版的画面感和节奏

```
Create a completely RAW quality, unprocessed, unedited image
with full iPhone camera quality.
[SCENE — 用短句描述场景，保留诗意]
[人物 + 动作 — 简洁，不清单化]
[1-2 个关键环境细节，不要堆砌]
```

> ⚠️ 这类prompt的好在于"a momentary blur"式的诗意，不要改成"dynamic motion blur with slight optical distortion"。

> **负面约束写法**（苍何经验）：在写实纪实场景，明确的负面排除比正面约束更精准。示例：
> `负面约束：不要插画、动漫、CGI、棚拍光、过度干净、过度构图、假液体、漂浮物、品牌文字、水印、海报设计感。`
> 和正面约束并用效果最佳。

---

### 模板 B：产品 Mockup（Product Photography）

**核心原则**：像描述一张已经在卖的产品广告图。聚焦材质、光线、标签完整性。

> ⚠️ **盲评提示**：产品Mockup在盲评中模板1:2败给简洁prompt。如果用户描述已经具体（有产品名、材质、场景），优先用简洁模式直接优化，不套模板。

#### B1：标准产品棚拍
```
A close-up product photograph of a [PRODUCT TYPE] standing upright
on a [SURFACE] with a clean [BACKGROUND] backdrop.
The packaging is [MATERIAL] with [TEXTURE], featuring:
- A bold logo "[BRAND]" in [LOGO STYLE]
- A descriptive line "[DESCRIPTION]" below the logo
- A small badge in the upper-right reading "[BADGE TEXT]"
Lighting: large softbox at 45° from camera left,
small fill light from camera right, subtle reflection on the surface.
Shot at f/4, ISO 100, 1/125s, on a 100mm macro lens,
3:4 vertical crop, ultra-sharp focus on the label.
```

**包装类型速查**：
| 产品 | 材质 | 表面 |
|------|------|------|
| 咖啡豆 | 牛皮纸袋 + 金属箔封口 | 木桌 |
| 护肤品 | 磨砂玻璃瓶 + 浮雕瓶盖 | 大理石 |
| 食品罐 | 哑光铁罐 + 纸质标签 | 浅灰水泥 |
| 数码配件 | 高级触感黑盒 | 深色皮革 |

#### B2：透明背景产品提取
```
A [PRODUCT] photographed on a transparent/white background.
Clean edges, no color fringing, no light spill.
Studio product photography, soft even lighting,
subtle shadow directly beneath the object.
Sharp focus on the entire product, f/8, 100mm macro lens.
```

#### B3：产品应用场景
```
A [PRODUCT] in use in a [CONTEXT/ENVIRONMENT].
[USER/ACTION DESCRIPTION]
Natural [TIME OF DAY] lighting, lifestyle photography style.
Shot at f/2.8, 35mm lens, eye-level angle.
Focus on the product with the environment softly blurred.
```

---

### 模板 C：电影质感（Cinematic）

**核心原则**：像描述一帧电影截图。指定胶片、调色、构图、导演参考。

```
A cinematic still from an imaginary [GENRE] film,
shot on Kodak Vision3 500T 35mm film stock.
The frame shows [SUBJECT + ACTION] in a [LOCATION]
during [TIME OF DAY].
Color palette: teal shadows and orange highlights,
slight halation around bright areas, organic film grain,
anamorphic 2.39:1 widescreen aspect ratio.
Camera: 40mm lens at f/2, slight motion blur on the foreground,
deep focus on the subject's face.
Mood: [MOOD ADJECTIVES], inspired by the visual language of
[DIRECTOR REFERENCE].
```

**风格速查**：
| 子风格 | 调色 | 光线 | 典型场景 |
|--------|------|------|----------|
| Film Noir | 高对比黑白 | 百叶窗阴影 | 侦探、悬疑 |
| Coming-of-Age | 暖色调 | 自然光 + 16mm颗粒 | 青春、成长 |
| Cyberpunk | 霓虹蓝/紫 | 雨夜湿地反射 | 科幻、赛博 |
| Wabi-sabi | 低饱和 | 柔和窗光 + 16:9 | 安静、日常 |
| Denis Villeneuve | 橙红渐变 + 剪影 | 强背光 + 反光地板 | 史诗、孤独 |
| Wes Anderson | 对称 + 粉彩色 | 均匀平面光 | 趣味、对称 |

---

### 模板 D：Pixar 3D 角色

> **核心**：描述"角色是谁在做什么"，加上关键视觉锚点（表情、材质），不要列渲染参数。
> v1.2精简过头导致PK输给对手——需要在"太详细"和"太极简"之间找到平衡。

#### D1：标准模式（推荐）
```
A 3D Pixar-style [SUBJECT], [KEY ACTION/POSE].
[表情+体态描述, 如 large expressive eyes, rosy cheeks, gentle smile].
[1-2 KEY VISUAL DETAILS, e.g. outfit texture, prop, fur/hair detail].
Clean [BACKGROUND TYPE], soft warm lighting, shallow depth of field.
```

**原则**：4行。第1行角色+动作，第2行表情锚点，第3行视觉细节，第4行背景+光线。
**为什么比极简好**：PK赛证明，加上表情锚点和视觉细节能提升0.5-1.0分。

#### D2：极简模式
```
A cute 3D animated [SUBJECT] doing [ACTION].
[Pixar/Disney/Illumination] style, [warm/bright/soft] lighting.
```

**什么时候用极简**：用户只说 "画个可爱XX" 或 "Pixar风格XX"，没有复杂要求时。

**反面教材（不要这样写）**：
```
❌ A 3D Pixar-style character of a cat, 3/4 front view, soft cinematic key light from above,
❌ warm rim light from behind. Smooth subsurface scattering on skin,
❌ fluffy hair with stray strands, subtle fabric folds on clothing.
❌ Background: clean pastel gradient, shallow depth of field with creamy bokeh.
❌ Render quality: feature-film polish, soft global illumination, no harsh shadows.
```
→ v1.1盲评：比简洁prompt差 1.12 分。模型被过度约束，丧失了创造力。

---

### 模板 E：App UI Mockup

```
A high-fidelity mobile app screenshot, iPhone 15 Pro frame,
vertical 9:19.5 aspect ratio.
The screen shows a [APP CATEGORY] app with the following layout:
- Top: status bar (9:41, 100% battery, full signal)
- Header: app name "[APP NAME]" in bold, profile icon on the right
- Main: a [HERO COMPONENT] taking 60% of the screen
- Below: [LIST/CARDS/CONTENT BLOCKS]
- Bottom: tab bar with 4 icons (home / explore / notifications / profile)
Design language: [COLOR PALETTE], rounded corners (16px),
subtle drop shadows, system font (SF Pro), [light/dark] mode.
Render the screen pixel-perfect, all text fully legible.
```

---

### 模板 F：信息图（Infographic）

```
Create a detailed infographic about [TOPIC].
Target audience: [AUDIENCE].
Layout: [vertical/vertical scroll/single panel].

Sections (top to bottom):
1. Title: "[TITLE]" — large bold sans-serif, [COLOR]
2. Section 1: [TOPIC] — [ICON] + [STAT/DATA POINT]
3. Section 2: [TOPIC] — [VISUAL ELEMENT] + brief explanation
4. Section 3: [TOPIC] — [CHART/DIAGRAM TYPE]
5. Footer: "[SOURCE/CALL TO ACTION]"

Color palette: [PRIMARY], [SECONDARY], [ACCENT].
Typography: clean sans-serif for body, bold geometric for headers.
Visual style: flat vector illustrations with subtle shadows,
no 3D effects, generous whitespace between sections.
All text must be legible at 100% zoom.
quality="high" recommended for dense text layouts.
```

---

### 模板 G：Logo 设计与品牌系统

> **核心**：Logo生成需要**硬约束**（色值、对称性、无渐变）+ **品牌个性描述**。
> PK赛教训：缺少具体色值和技术约束会输给对手的精准描述。
> v1.6升级：从单Logo扩展为Logo + 品牌身份包 + 品牌触点板 + 品牌包络广告四位一体。

#### G1：单 Logo 设计

```
Design a [STYLE: minimalist / geometric / organic / vintage] logo for "[BRAND NAME]",
a [BUSINESS TYPE / INDUSTRY].

Concept: [CORE VISUAL IDEA, e.g. "a leaf shape integrated with the letter E"].
Brand personality: [ADJECTIVE 1], [ADJECTIVE 2], [ADJECTIVE 3].

Visual specs:
- Color: [PRIMARY COLOR] ([HEX CODE]) on pure white background
- Shape: [SYMMETRICAL / ASYMMETRICAL], [GEOMETRIC / ORGANIC] lines
- Weight: [SINGLE STROKE / VARIED THICKNESS], [THIN / MEDIUM / BOLD]
- Layout: centered logo mark with brand name below in [SERIF / SANS-SERIF / CUSTOM] font

Constraints: no gradients, no shadows, no 3D effects, no watermarks,
scalable from favicon to billboard, original and non-infringing.
```

**Logo 多触点验证**（建议补充到 prompt 中）：
```
Also show the logo applied across touchpoints:
- Business card (90×55mm)
- App icon (rounded square)
- Website header
- Signage / billboard
This helps verify readability at different sizes.
```
> 来源：苍何 awesome-gpt-image-2。Logo不能只看单图，缩小到App图标是否可读、横竖比例是否适配，只有多触点展示才能暴露问题。

**为什么需要Constraints**：OpenAI官方Cookbook + fal.ai指南都强调——Logo生成的关键是用约束
防止模型"自由发挥到你不想要的方向"。色值、对称性、无渐变不是过度结构化，是Logo必需的硬参数。

**PK赛数据**：v1.2的Logo模板因为缺少色值和技术约束，输给了指定 #2D5016 + no gradients 的对手。

#### G2：完整品牌身份包
> 来源：苍何 awesome-gpt-image-2。适用于品牌从0到1的完整VI交付。

```
为[业务名]交付一套完整品牌身份系统。

输入信息：
业务描述：[一句话说明]
行业：[行业]，目标受众：[描述]
品牌个性：[5个关键词]
希望触发的感受：[信任/兴奋/奢华/亲近/力量]

请输出：
1. Logo概念：3-5个完全不同的方向，每个说明视觉理念、形状语言、象征意义、字体方向
2. 配色系统：主色+辅助色+强调色+中性色，附HEX代码和使用规则
3. 字体系统：标题+正文+强调字体，字号层级和免费替代方案
4. 应用触点：名片、App图标、网站首页、社媒模板、广告牌上的应用效果
5. 品牌规则：3条永远不要打破的核心规则
6. 禁用规则："不要怎么用"的明确清单

设计语言：[现代极简/科技品牌/奢华编辑]，主色[颜色+HEX]，大量留白。
输出：结构化品牌手册，任何设计师或AI工具都能在10分钟内理解并复用。
```

#### G3：品牌包络产品广告
> 来源：苍何 awesome-gpt-image-2。同一品牌下替换不同产品时，视觉世界保持一致。

```
PHASE 1 / ANCHOR：用 2 行描述[品牌身份]，包括调色板、材质、光影和情绪。
PHASE 2 / INJECT：把[产品]放入这个品牌世界中，产品要服从品牌气质和环境语言。
PHASE 3 / FORMAT：指定[输出格式]，例如 hero 图、方形广告、竖版 story 或电商头图。
PHASE 4 / SIGNATURE：加入[品牌元素]，例如颗粒、阴影、叠加纹理、包装符号或图形边框。

目标：同一品牌下替换不同产品时，视觉世界保持一致，广告图仍有明确主角和商业质感。
```

---

### 模板 H：等轴微缩场景（Isometric Miniature）

```
A 45° top-down isometric miniature 3D scene of a [SCENE THEME]
diorama on a wooden display base.
Soft refined PBR textures, realistic materials,
clean unified composition, minimalistic aesthetics.
Tiny props integrated into the architecture: [3 SPECIFIC ELEMENTS].
Studio softbox lighting, subtle ambient occlusion,
pastel color palette dominated by [COLOR1] and [COLOR2].
Square 1:1 frame, centered subject, plenty of negative space.
```

---

### 模板 I：创意概念（Creative Concepts）

#### I1：复古交易卡
```
A premium holographic trading card, vertical 3:4 layout.
Center: a [SUBJECT] in dynamic pose, vibrant cinematic lighting.
Border: ornate gold filigree with rune-like icons in four corners.
Top banner reads "[RARITY]" in bold serif caps.
Bottom panel: name plate "[CHARACTER NAME]", three small stat icons
(power / speed / magic) with numeric values.
Holographic foil effect, slight grain, studio backdrop.
```

#### I2：动作人偶吸塑包装
```
A stylized action figure of [SUBJECT] sealed inside a premium
plastic blister pack, photographed straight-on.
The cardboard backing is glossy with a bold header reading
"[BRAND / NAME]" in oversized sans-serif caps and a smaller
tagline "[TAGLINE]".
The figure is posed upright with [ACCESSORY 1] and [ACCESSORY 2]
slotted into molded compartments next to it.
Studio product photography, soft top lighting,
clean off-white background, subtle reflection on the floor.
```

#### I3：360° 全景
```
A 360° equirectangular panoramic photograph of [LOCATION],
aspect ratio 2:1.
The horizon is perfectly level across the middle of the frame.
Foreground (bottom 1/3): [具体前景元素].
Mid-ground (middle 1/3): [建筑/人物/场景].
Background (top 1/3): [天空/远景].
Lighting: natural [TIME OF DAY] sun, soft atmospheric haze.
No fish-eye distortion at the poles, ready for VR projection.
```

#### I4：漫画条（Comic Strip）
```
Create a short vertical comic-style reel with [N] equal-sized panels.
Panel 1: [场景 + 动作]
Panel 2: [场景 + 动作]
Panel 3: [场景 + 动作]
Panel 4: [场景 + 动作]
Style: clean line art, flat colors, consistent character design
across all panels. Each panel should read as a clear narrative beat.
```

#### I5：概念产品研发拆解板
> 来源：苍何 awesome-gpt-image-2。这是一种**多阶段叙事性构图**——不是单张成品渲染，而是从灵感→分析→迭代→验证→规格的完整研发故事。

```
为[产品/家具/装置]生成一张完整的概念产品研发拆解板，而不是单张成品渲染图。

核心概念：
把[灵感来源，如揉皱纸团/贝壳/折纸/机械结构]转译成[产品类型]。
设计哲学：[一句话说明功能与情绪，例如"把受控混乱转化为高舒适度座椅"]。

画面结构：
中心：高质量 hero render，展示最终产品的主要形态、材质和比例。
左侧：观察与形态分析，包含灵感图、轮廓提取、结构线、折痕/纹理/受力方向标注。
中部：形态迭代过程，展示从原始形态到产品外壳的 3-5 个演化步骤。
下方：人体工学或使用场景验证，包含尺寸、角度、使用姿态和关键功能说明。
右侧：结构集成与材料方案，展示内部骨架、外壳、软垫/面料/连接件等分层拆解。
底部：最终材质、表面纹理、颜色方案和关键规格表。

视觉风格：
工业设计提案板，干净白底或浅灰背景，技术图纸 + 产品摄影混合风格，
细线标注，清晰标题，真实阴影，材质细节可见。

约束：
不要只画一个漂亮产品；必须展示分析、迭代、人体工学、结构、材料和规格。
不要让文字挤满画面；每个阶段只保留短标题和关键标签。
产品外形应保留[灵感来源]的识别特征，但必须看起来可制造、可使用。
```

#### I6：水墨双重曝光人物海报
> 来源：苍何 awesome-gpt-image-2。适合个人IP、品牌主理人、运动员的高级人物海报。

```
生成一张[人物/角色/品牌主理人/运动员]的水墨双重曝光人物海报。
画幅：9:16 竖版，高级电影海报构图。
主体结构：
- 上半区：放大的人物头部、面部轮廓或半身剪影，形成最强识别锚点。
- 中下区：同一人物的全身或半身主体，姿态为[站姿/动作姿态/凝视镜头]。
- 剪影内部：融合[关键场景]、[象征物]、[叙事片段]、[环境纹理]，形成双重曝光叙事。
视觉连接：用云雾、水墨扩散、飞白边缘、负空间和柔和明暗过渡，把上方剪影、内部拼贴和下方主体连成一条从上到下的视觉动线。
风格：东方水墨美学 + 写实电影感，克制、高级、留白充足，层次丰富但不杂乱。
文字：可加入[标题/姓名/短句]，必须少量、可读、像海报题签而不是信息图说明。
约束：不要硬拼贴，不要把背景塞满，不要廉价武侠特效，不要复制真实海报版式，不要让剪影和主体互相抢焦点。
输出：海报级完成图，主体清晰，水墨边缘自然，叙事元素与人物身份强相关。
```

#### I7：自然科普海报（Apple 风格）
> 来源：苍何 awesome-gpt-image-2。适合科普内容、自然博物馆、教育类视觉。

```
生成一张 9:16 竖版高级科普海报，Apple Keynote 产品发布风格。

画面结构：
顶部左侧：中文大标题 [{物种名}]，副标题 [{一句定位}]，细短横线，英文名 [{英文物种名}]，分布信息。
中部：超高清、真实、强烈立体感的 {物种名}，占画面 50%-70%。白色背景，可保留少量承托物（树枝/岩石/雪地），真实阴影。
底部：四个极简信息栏目，细线 icon + 彩色小标题 + 1-3行短说明，栏目间极细浅灰竖线分隔。
最底部：一句灰色小字总结。

设计原则：
- 主体极度放大，最强视觉中心
- 纯白/极浅灰白渐变背景，大量留白
- 不使用圆角卡片、厚边框、大面积装饰图形
- 文字像高端发布会视觉，标题巨大，副标题克制

禁止项：不要淡黄色旧纸背景、复杂信息图网格、圆角卡片、儿童科普风、卡通风。
```

#### I8：品牌触点系统视觉板
> 来源：苍何 awesome-gpt-image-2。不是单张海报，而是一套完整品牌应用展示——适合品牌提案、VI汇报。

```
为[品牌名]生成一张高端品牌触点系统视觉板。

品牌定位：[行业/生活方式/产品品类]
核心气质：[关键词1]、[关键词2]、[关键词3]
主视觉场景：[核心产品/服务/体验]，放在[材质表面/空间场景]中。

触点系统必须包含：
- 主产品 hero shot
- 包装盒 / 手提袋 / 杯子 / 标签 / 贴纸 / 封签等品牌物料
- 菜单卡 / 价目表 / 小型排版样张
- 生活方式场景或用户使用片段
- 配色、字体、图形语言在不同触点上的统一应用

设计语言：[现代极简/日式留白/奢华编辑/科技品牌]，主色[颜色]，辅助色[颜色]，大量留白，细腻材质，真实阴影。
构图：像顶级设计机构提案页，主视觉最突出，辅助物料层级清楚，整体有品牌系统感。

约束：不要只生成一个 logo；不要把所有物料挤成杂乱拼贴；不要使用随机乱码文字；不要让各触点风格割裂。
```

#### I9：角色动作分解参考表
> 来源：苍何 awesome-gpt-image-2。适合动画/舞蹈/游戏动作参考，4×4网格结构化动作序列。

```
生成一张[角色/人物]动作分解参考表。
风格：[黑白线稿/3D 灰阶/漫画分镜/教学图]，背景纯净。
版式：4×4 网格，共 16 个等尺寸面板，细线分隔，每格左上角编号 1-16。

角色一致性：所有面板使用同一角色，保持脸型、服装、比例和发型一致。
每格结构：
- 顶部：动作标题
- 中央：完整身体动作姿态
- 底部：3-4 行动作说明
- 叠加：方向箭头、旋转箭头或运动轨迹线

动作序列：[从基础站姿到结束动作的完整步骤]
约束：不要复杂背景，不要新增角色，不要彩色干扰，不要改变角色身份。
输出：清晰可读、可用于动画/舞蹈/游戏动作参考的角色动作表。
```

#### I10：参考图转 3D 收藏玩具
> 来源：苍何 awesome-gpt-image-2。适合将人物照片转为高端潮玩/收藏品形象。

```
将输入照片转换为高端 3D 收藏玩具形象。

身份保持：保留原始人物/角色的脸部身份、主要发型、表情气质和服装识别点。
造型比例：大头设计，五官轻微夸张，身体比例玩具化，但整体仍保持高级设计感。
材质：哑光 vinyl / resin / collectible figure finish，皮肤和服饰材质要有细节。
灯光与背景：柔和棚拍光，干净背景，[黑色/白色/品牌色]，主体居中，轮廓清晰。
质感：超清锐度，真实材质反射，premium designer toy aesthetic。

约束：不要改变身份，不要廉价塑料感，不要多角色，不要复杂背景，不要文字水印。
输出：一张完整的高端收藏玩具渲染图。
```

---

### 模板 J：编辑工作流（Edit）

**核心原则**：明确分为 Change（什么改变）和 Preserve（什么保持不变）。每次编辑都要重复不变量清单，防止漂移。

#### J1：风格迁移
```
Use the same style from the input image and generate [NEW SUBJECT].
Preserve: palette, texture, brushwork, film grain, composition framing.
Change: only the subject/content.
```

#### J2：局部修改
```
Change: replace [SPECIFIC ELEMENT] with [NEW ELEMENT].
Preserve: keep the subject's face, pose, clothing, and lighting
exactly the same as the input.
```

#### J3：光线/天气变换
```
Change: transform the lighting to [NEW LIGHTING CONDITION].
Preserve: identity, geometry, camera angle, object positions,
all physical elements unchanged.
```

#### J4：多图合成
```
Place the [ELEMENT] from the second image into the setting of image 1,
[POSITION DESCRIPTION].
Use the same style of lighting, composition and background.
Do not change anything else in image 1.
```

#### J5：虚拟试穿
```
Edit the image to dress the person using the provided clothing images.
Do not change face, facial features, skin tone, body shape, pose,
or identity in any way.
Preserve exact likeness, expression, hairstyle, and proportions.
Replace only the clothing, fitting the garments naturally to
the existing pose and body geometry with realistic fabric behavior.
Match lighting, shadows, and color temperature to the original photo
so the outfit integrates photorealistically.
Do not change the background, camera angle, framing, or image quality.
```

#### J6：室内设计替换
```
In this room photo, replace ONLY [SPECIFIC ELEMENT] with [NEW ELEMENT].
Preserve camera angle, room lighting, floor shadows, and surrounding objects.
Keep all other aspects of the image unchanged.
Photorealistic contact shadows and [MATERIAL] texture.
```

#### J7：产品提取（透明背景）
```
Extract the [PRODUCT] from this image and place it on a clean,
transparent background.
Preserve the exact shape, color, texture, and details of the product.
Clean edges, no color fringing, no background remnants.
Studio-quality lighting with subtle shadow beneath.
```

#### J8：草图→渲染
```
Turn this drawing into a photorealistic image.
Preserve the exact layout, proportions, and perspective.
Choose realistic materials and lighting consistent with the sketch intent.
Do not add new elements or text.
```

#### J9：图片翻译（本地化）
```
Translate the text in this image to [TARGET LANGUAGE].
Do not change any other aspect of the image.
Preserve typography style, placement, spacing, and hierarchy.
Translate verbatim and accurately, with no extra words.
```

#### J10：服装/产品替换
```
Edit the image to replace the [ORIGINAL PRODUCT] with [NEW PRODUCT].
Do not change the person's face, facial features, skin tone,
body shape, pose, or identity.
Preserve exact likeness, expression, hairstyle, and proportions.
Fit the new product naturally to the existing pose with realistic behavior.
Match lighting, shadows, and color temperature to the original.
```

---

### 模板 K：概念插画 / 场景卡片

> ⚠️ **重要**：概念插画场景**核心是创意叙事，不是参数堆砌**。
> 盲评结果：过度结构化的插画prompt比简洁原版差 0.6-1.0 分。
> 保持画面感和叙事性，不要列出构图/色彩/质感参数。

#### K1：场景卡片（带文字）
```
[插画类型] illustration: [核心场景描述，1-2句话].
[Mood/氛围，一个短句].
Style: [视觉风格关键词，2-3个].

Include ONLY this text: "[要出现的文字]"
```

**原则**：让模型自己决定构图、配色、光线。你只描述"画什么"和"什么感觉"。

#### K2：故事场景（无文字）
```
A [风格] illustration of [SCENE].
[主体 + 动作].
Mood: [情绪].
```

**极致简洁**。2-3句话足够。模型会自动补全所有视觉细节。

**反面教材（不要这样写）**：
```
❌ Create a holiday card illustration.
❌ Scene: [详细场景描述，包括主体、动作、环境、细节].
❌ The scene suggests [情感/叙事暗示].
❌ Mood: [情绪形容词1], [情绪形容词2], [情绪形容词3].
❌ Style: [视觉风格描述], [光线], [质感], [构图], [品质].
❌ Constraints: Original artwork only. No trademarks. No watermarks. No logos.
```
→ 盲评结果：这种写法比简洁prompt差 0.6-1.0 分。模板化描述杀死了插画需要的灵动性。

---

## 七、4 大进阶技巧

### 技巧 1：用约束控制元素数量
多元素场景可能过度渲染，末尾加：
```
Constraints: exactly [N] elements, no extra props,
no additional text beyond what's specified above.
```
→ 正面约束比负面提示词在 gpt-image-2 上稳定得多。

### 技巧 2：用 Seed 复现构图
```python
img = client.images.generate(
    model="gpt-image-2",
    prompt=PROMPT,
    size="1024x1536",
    quality="high",
    extra_body={"seed": 20260421},
)
```
→ 固定 seed + 固定 prompt = 跨次生成保持构图、光线、角色特征一致。

### 技巧 3：生产级分辨率工作流
| 阶段 | 目标 | 分辨率 | n | 预算 |
|------|------|--------|---|------|
| 概念探索 | 找方向 | 1024×1024 | 4 | 10% |
| 构图迭代 | 锁定主体布局 | 1024×1536 | 2 | 25% |
| 风格收敛 | 确定光线色彩 | 1024×1536 | 1 | 20% |
| 文字精修 | edit 微调 | 1024×1536 | 1 | 15% |
| 最终输出 | 4K 放大 | 2048×3072 | 1 | 30% |

→ 成本降 60%，质量通过率从 40% → 85%+。

### 技巧 4：迭代而非过载
从干净基础 prompt 开始，用小的单次修改跟进：
- `"make lighting warmer"`
- `"remove the extra tree"`
- `"shift the subject to the left third"`
- `"same style as before, but change the background to..."`

---

## 八、6 大常见陷阱（每次生成前扫一遍）

| 陷阱 | 错误做法 | 正确做法 |
|------|----------|----------|
| 1. 塞进一个长句 | 一段话糊成一团 | 分段：场景→主体→细节→光线→约束 |
| 2. 冲突风格 | "photorealistic" + "cartoon" | 只选一个主风格 |
| 3. 负面提示词 | "no watermark, no text" | 改用正面约束 |
| 4. 忽略镜头参数 | 不写焦距和光圈 | 明确指定，有物理效果 |
| 5. 文字不用引号 | 直接写文字 | `"..."` 包裹 |
| 6. 编辑不说清变与不变 | 只说"改背景" | `Change: ...` / `Preserve: ...` |

---

## 九、尺寸与比例速查

| 比例 | 像素 | 适用场景 |
|------|------|----------|
| 1:1 | 1024×1024 | Logo、头像、社交媒体 |
| 4:5 | 1024×1280 | Instagram 竖图、人像 |
| 3:4 | 1024×1365 | 交易卡、竖版海报 |
| 16:9 | 1536×864 | 公众号封面、横版主图 |
| 9:16 | 864×1536 | 手机全屏、Stories |
| 2:3 | 1024×1536 | 杂志页、竖版海报 |
| 2:1 | 1536×768 | 360°全景、Banner |
| 2.39:1 | 1536×642 | 电影宽银幕 |

---

## 十、执行流程与引导（Phase 0-5）

### Phase 0：复杂度判断（关键！）

在套模板之前，先判断用户输入的复杂度。同时参考 **§五 模板有效性速查** 确认该场景是否需要模板。

| 用户输入特征 | 模式 | 处理方式 |
|-------------|------|----------|
| 已经是结构化prompt / 只需微调 | 🟢 简洁模式 | 只做优化和补全，不强行套模板 |
| 一句话需求，无细节 | 🔵 扩展模式 | 套模板，填充占位符 |
| 多个场景元素 + 特定要求 | 🟡 定制模式 | 参考模板，混合组装 |
| 编辑现有图片 | 🟠 编辑模式 | 使用模板J |
| **创意驱动需求**（3D卡通/插画/艺术） | 🔴 **跳过模板** | 直接优化用户描述，不套任何模板 |

**判断标准**：
- 如果用户输入已经包含 ≥3 个以下要素（场景、主体、动作、镜头、光线、风格）→ 用简洁模式
- **如果场景属于 Pixar 3D / 概念插画 / 艺术创作类** → 跳过模板，只做最小优化（加quality/size）
- §五的盲评表会告诉你该场景模板是否有效 → **先查再套**

**简洁模式原则**（当用户输入已经很好时）：
- 不要把2句话膨胀成5句
- 不要给已经简洁有力的prompt强加结构
- 只在缺失关键要素时补全（缺镜头参数？缺光线？）
- 保留原版的诗意、节奏感和画面感
- "a momentary blur" 不要改成 "dynamic motion blur"

---

### Phase 1：场景+主题确认（一次性问完，5-6个问题）

收到用户需求后，**一次性**抛出以下问题（用户已说清楚的跳过）：

```
帮你做一张好图！几个问题确认方向：

1️⃣ 场景类型：
   🎯写实照片 | 📦产品Mockup | 🧸3D卡通 | 🎬电影质感 | 📱App UI
   🎨Logo/品牌系统 | 📊信息图 | 🎃创意概念 | 🖼️编辑图片 | 🎭插画 | 🏙️等轴微缩

   💡 创意概念包含：交易卡/人偶/漫画条/拆解板/水墨海报/科普海报/品牌视觉板/动作表/收藏玩具
   💡 Logo/品牌系统包含：单Logo / 完整品牌身份包 / 品牌包络广告

2️⃣ 核心主体：画面的主角是谁/什么？

3️⃣ 用途：公众号封面 / 产品展示 / 品牌VI / 社交媒体 / PPT / 其他

4️⃣ 情绪氛围：温暖治愈 / 科技未来 / 奢华高端 / 可爱萌 / 神秘幽暗 / 清新自然

5️⃣ 有参考图或参考风格吗？可以发给我

不确定的跳过就行，我来推荐 👍
```

**智能跳过规则**：
- 用户已经说清楚的参数 → 不重复问
- 用户给参考图 → 跳过风格/色调问题，从图中提取
- 用户说"你来定" → 用该场景最佳默认值

### Phase 2：场景深度引导（按场景问6-8个参数）

根据Phase 1确定的场景，**一次性**问该场景的核心参数：

#### 🧸 Pixar 3D
> ⚠️ 盲评结论：模板0:3大败。不套模板D，只收集关键信息构建简洁描述。

```
3个核心参数决定画面质量：

- 角色是谁？在做什么？（一只小狐狸抱着猫咪 / 机器人举着气球）
- 表情和性格？（大眼睛好奇歪头 / 开心大笑 / 害羞低头）⚡ 最影响质量
- 参考哪个动画风格？（默认Pixar | Disney/Illumination/DreamWorks/吉卜力）
```

#### 📱 App UI
> ✅ 盲评结论：模板2:0大胜。推荐使用模板E（见§六）。

```
- App类型？（冥想/外卖/健身/金融/社交/音乐）
- App名称？（出现在Header中）
- 深色还是浅色模式？
- 主色调？（蓝色系/绿色系/紫色系；可给HEX色值）
- 首页主要展示什么？（呼吸圆圈+课程卡片 / 信息流 / 地图 / 仪表盘）
- 底部Tab几个？分别是什么？（默认4个: home/explore/stats/profile）
- iOS还是Android？（默认iPhone 15 Pro | Android Material）
- 想参考哪个App的风格？
```

#### 🎨 Logo与品牌系统
> ✅ 盲评结论：模板2:0大胜。推荐使用模板G（见§六）。

**先确定你需要哪个层级**：
- 只要一个Logo → G1 单Logo设计
- 品牌从0到1的完整VI → G2 完整品牌身份包
- 同品牌多产品广告一致性 → G3 品牌包络产品广告

**G1 单Logo — 引导问题**：
```
- 品牌名？
- 行业/领域？
- 品牌个性？选3个形容词（如clean, trustworthy, earth-conscious）
- 核心视觉概念？（如叶子+E字母融合 / 山峰轮廓 / 无限符号）
- Logo风格？极简几何 / 有机圆润 / 复古经典 / 手绘质感 / 字母标
- 主色调？（给HEX色值最好，如 #2D5016）
- 需要带文字吗？（纯图标 / 图标+品牌名 / 只要字体设计）
- 对称性？（默认对称 | 不对称）
```

**G2 完整品牌身份包 — 引导问题**：
```
- 业务名和一句话描述？
- 行业和目标受众？
- 品牌个性？5个关键词
- 希望触发的感受？（信任/兴奋/奢华/亲近/力量）
- 喜欢的视觉身份参考？3个
- 讨厌的视觉身份参考？3个
- 设计语言偏好？（现代极简/科技品牌/奢华编辑）
```

**G3 品牌包络产品广告 — 引导问题**：
```
- 品牌身份描述？（调色板、材质、光影、情绪）
- 要放进去的产品？
- 输出格式？（hero图/方形广告/竖版story/电商头图）
- 品牌签名元素？（颗粒/阴影/叠加纹理/包装符号/图形边框）
```

#### 🎯 写实摄影
> ⚠️ 盲评结论：模板3:3平手。模板无加成，简洁模式即可。以下参数用于补全缺失要素。

```
- 主体是谁？（年龄/性别/种族/发型/穿着/特征）
- 在做什么？（坐在咖啡馆看书 / 走东京街头 / 抱着孩子微笑）
- 场景环境？（咖啡馆 / 地铁站 / 海边日落 / 雨中街道）
- 整体氛围？温暖治愈 / 冷酷都市 / 胶片复古 / 奢华时尚 / 纪实新闻
- 镜头感？（默认35mm candid | 50mm人像 / 85mm浅景深 / iPhone业余感）
- 光线？（默认natural | golden hour / 霓虹灯 / 影棚 / 逆光剪影）
- 拍摄角度？（默认eye-level | 微俯 / 仰拍 / 俯拍）
- 构图？（默认居中 | 三分法 / 对称 / 引导线 / 留白）
```

#### 🎬 电影质感
> ✅ 盲评结论：模板2:1胜。推荐使用模板C（见§六）。

```
- 场景描述？（雨夜城市天台 / 废弃工厂 / 太空舱）
- 画面主体？（穿风衣的背影 / 情侣拥吻 / 复古跑车）
- 电影风格？Noir / Villeneuve科幻 / Wes Anderson对称 / Warm Romance / Thriller
- 色调？（默认teal&orange | 低饱和 / 黑白 / 暖琥珀）
- 光线类型？（侧光rim light / 顶光god ray / 霓虹背光 / 烛光）
- 宽高比？（默认2.39:1电影宽银幕 | 16:9 / 4:3 / 1:1）
- 画面中需要文字吗？
```

#### 📦 产品 Mockup
> ⚠️ 盲评结论：模板1:2败。模板无加成，简洁模式优先。只在用户需求很空时才参考模板B。

```
- 产品是什么？（咖啡豆/护肤品/食品罐/数码配件/其他）
- 拍摄场景？（纯色棚拍 / 透明背景提取 / 生活场景应用）
- 核心卖点？材质/颜色/标签上的文字
```

#### 📊 信息图
> ⚠️ 盲评结论：模板1:1平手。模板有帮助但非必须。

```
- 主题？
- 面向谁？
- 要展示哪些数据/信息点？（列3-5个）
- 布局？（默认竖版滚动 | 单版面）
- 视觉风格？（默认flat vector | 手绘 / 3D / 等轴）
- 配色方案？
- 图表/可视化类型？（柱状图 / 饼图 / 流程图 / 时间线）
```

#### 🖼️ 编辑工作流
> ✅ 盲评结论：模板3:0大胜。必须使用模板J（见§六）。

**J1-J10 子模板选择决策树**：

```
用户想做什么？
├── 换风格/把A变成B风格 → J1 风格迁移
├── 只改局部元素 → J2 局部修改
├── 换光线/天气/时段 → J3 光线变换
├── 两张图合成 → J4 多图合成
├── 换衣服/试穿 → J5 虚拟试穿
├── 换房间/家具/装饰 → J6 室内设计替换
├── 抠图/透明背景 → J7 产品提取
├── 草图变渲染 → J8 草图→渲染
├── 换文字语言 → J9 图片翻译
├── 换产品/服装 → J10 服装/产品替换
└── 不确定 → 先问用户“你想改哪方面？”
```

```
- 编辑类型？风格迁移 / 局部修改 / 添加元素 / 删除元素
- 变成什么风格/改成什么？（发参考图或描述）
- 必须保留什么？（人脸 / 构图 / 色调 / 文字）
- 变化程度？（微调 / 适中 / 彻底改变）
- 发原图给我看看
```

#### 🎭 概念插画
> ⚠️ 盲评结论：模板0:3大败。不套模板K，只收集用户脑海中的画面感。

```
3个问题抓住灵魂：

- 核心场景？描述你脑海中的画面
- 情绪/氛围？
- 视觉风格？（水彩 / 油画 / flat design / 手绘线稿 / 绘本风）
```

#### 🏙️ 等轴微缩
> ⚠️ 盲评结论：模板1:1平手。模板无加成。

```
- 微缩场景主题？（云计算数据中心 / 东京路口 / 咖啡馆 / SaaS界面）
- 想包含的小道具/细节？（列3-5个）
- 主色调？
- 风格？（默认写实PBR | low-poly / 像素 / 萌系）
- 基座样式？（默认木质展台 | 白色展台 / 无基座漂浮）
- 有参考图吗？
```

#### 🎃 创意概念
> ⚠️ 盲评结论：模板2:2平手。视情况使用模板I。

**先确定子类型（现在是10选一，用决策树）**：
```
你要做什么类型的创意图？
├── 复古交易卡 / 收藏卡 → I1
├── 动作人偶包装 → I2
├── 360°全景 → I3
├── 漫画条/四格 → I4
├── 产品研发拆解板（工业设计） → I5
├── 水墨双重曝光人物海报 → I6
├── 自然科普海报（Apple风） → I7
├── 品牌触点系统视觉板 → I8
├── 角色动作分解参考表 → I9
├── 照片转3D收藏玩具 → I10
└── 都不是 → 描述你想做什么，我来匹配
```

选定子类型后，根据对应模板的占位符收集关键参数：
- I1-I4：参考§六模板中的占位符（主体/品牌名/动作/场景）
- I5：灵感来源+产品类型+设计哲学
- I6：人物身份+核心场景+象征物+姿态
- I7：物种名+定位句+四个科普栏目
- I8：品牌定位+核心气质+触点清单
- I9：角色描述+完整动作序列
- I10：发参考图+确认身份保持要素

### Phase 3：输出+技术设置

```
最后确认几个技术参数（都有默认值，可以直接跳过）：

📐 尺寸/比例？
   1:1正方形(默认) | 16:9横版 | 9:16竖版 | 4:5 Instagram | 2.39:1电影

⚙️ 质量？
   medium快速预览(省50%成本) | high正式输出(默认)

🔢 生成几张？
   默认1张 | 可选2-4张对比

🔄 A/B双方案？（可选）
   在prompt中加“请输出一版主方案+一版备选方案”，一次生成两个方向直接挑选。
   适合不确定具体风格时快速探索。
```

### Phase 4：输出prompt + 用户确认

**这一步是关键——先生成prompt给用户看，不要直接调API。**

```
根据你的需求，这是为你定制的prompt：

---
[完整prompt文本]
---

参数：size=1024x1024, quality=high, model=gpt-image-2

你想怎么处理？
1. ✅ 看着不错，帮我直接调用生成吧
2. ✏️ 我想调整一下（告诉我改哪里）
3. 🔄 换个方向重新来
```

用户选1 → 帮他调用API生成图片
用户选2 → 调整prompt后重新展示
用户选3 → 回到Phase 1

### Phase 5：生成后反馈循环

```
生成完毕！[展示图片]

满意吗？
- 😍 完美！
- 🔄 微调一下（告诉我改什么，我用edit模式调整）
- 🔁 重新生成（换个随机种子）
- 📐 换个尺寸/比例再出一张
```

### 质量检查（Phase 4展示prompt前内部自检）
- [ ] 主体在 prompt 开头？
- [ ] 结构分段清晰？
- [ ] 文字用引号包裹？
- [ ] 镜头参数明确？
- [ ] 光线描述具体？
- [ ] 没有堆砌 "8K ultra detailed"？
- [ ] 没有冲突风格？
- [ ] 约束用正面句式？（写实纪实场景可加负面约束列表辅助）
- [ ] 不是把简单需求过度工程化？
- [ ] 如果是品牌类需求，是否选择了正确的模板层级？（G1单Logo / G2身份包 / G3包络广告）
- [ ] 如果是创意概念，是否通过决策树选了正确的子模板？

### 默认值策略

每个参数都有安全默认值——即使用户全部跳过也能生成合格图片：
- 色调 → warm暖色调
- 光线 → natural soft light
- 背景 → clean gradient / neutral
- 构图 → centered with padding
- 质量 → high
- 尺寸 → 1:1

默认值来自33组盲评+6组PK赛中得分最高的参数组合。

---

## 十一、混合场景处理

当用户需求不明确或跨多个场景时：

1. **优先识别主场景**：写实 vs 设计 vs 创意
2. **主模板 + 子元素**：例如"写实人像 + 电影质感" → 以模板 A 为主体，融入模板 C 的调色和胶片描述
3. **不要硬套多个模板**：选一个为主，另一个只取关键元素
4. **如果完全不确定**：使用通用结构公式 + 最接近的 Style 标签
5. **简洁优先**：如果用户输入已经很好，不要为了套模板而膨胀它

---

## 十二、与 image2-typography-poster 的边界

| 判断条件 | 使用哪个 skill |
|----------|---------------|
| 画面核心是"某个字/词"的字体设计 | → image2-typography-poster |
| 画面核心是场景、人物、产品、概念 | → yinyo-image2-prompt |
| 公众号封面 + 文字是主角 | → image2-typography-poster |
| 公众号封面 + 场景/概念是主角 | → yinyo-image2-prompt |
| 不确定 | → 先问用户"这张图的核心是文字还是画面？" |

---

## 参考来源
1. OpenAI 官方 Cookbook — GPT Image Generation Models Prompting Guide
2. apiyi.com — GPT-Image-2 prompt collection: 10 most popular templates (April 2026)
3. GitHub ZeroLu/awesome-gpt-image — 社区精选 prompt 集合
4. gptimageai.org — GPT-Image 1.5 Prompt Guide
5. PixVerse — GPT Image 2 Review: Prompt Guide and Use Cases
6. befreed.ai — GPT Image 2: Complete Guide 2026
7. Civitai's Guide to GPT Image 1
8. OpenAI Developer Community — DALL-E 3 & gpt-image-1 tips thread
