[English](README.md) · **简体中文** · [OpenMotion](../docs/README.zh-CN.md)

# OpenMotion 资源库

**分享视频背后的方法、动效和品牌。** 从第一天就用这个目录收纳可复用的 Skills、模板、Motion 组件、动效设计体系和 Brandkit。可以贡献完整作品，也可以贡献一个讲清楚用途的小方法。

| 分类 | 从这里开始 | 收录内容 |
| --- | --- | --- |
| **🧠 Skills** | [Growth Teardown](skills/openmotion-growth-teardown/SKILL.md) · [Design Styles](skills/openmotion-design-styles/SKILL.md) · [Presenter Story](skills/openmotion-presenter-story/SKILL.md) · [Motion Design Remix](skills/openmotion-design-remix/SKILL.md) · [风格配方](#style-recipes) · [Brandkit 整理](skills/openmotion-brandkit/SKILL.md) | 用 `SKILL.md` 描述可重复使用的方法，按需附示例与参考。 |
| **🎞️ 模板** | [Studio 可编辑起点](templates/README.md) · [Presenter Tech](templates/presenter-tech/README.md) | 完整工程、预览、替换与改编说明。 |
| **🧩 Motion 组件** | [标题揭示配方](components/title-reveal/README.md) | 标题、转场、图表或场景，说明时序、可修改项与接入方式。 |
| **🎨 动效设计体系** | [Ink & Water](design-systems/ink-water/MOTION_DESIGN.md) | 用 `MOTION_DESIGN.md` 记录字体、构图、节奏、运动和声音规则。 |
| **便携创作包** | [规范](../docs/motion-package-spec.md) · [工具与 Product Story 示例](../packages/motion-package/README.md) | 通过动效文档引用独立设计文档，携带素材、精确依赖与可选 Agent 使用方法。 |
| **💼 Brandkits** | [OpenMotion](brandkits/openmotion/BRANDKIT.md) | 品牌事实、可用文案、配色、字体、素材入口与使用规则。 |

```text
library/
├── skills/openmotion-growth-teardown/          → 公司增长调研 → 带出处的增长地图视频
├── skills/openmotion-design-styles/            → 21 种设计风格 + 2 种布局 → 按风格规则做成的视频
├── skills/openmotion-presenter-story/          → three presenter / motion recipes
├── skills/openmotion-design-remix/             → six source / remix profiles
├── skills/openmotion-highlighter-notes/ …       → 96 个单风格配方（见下文）
├── skills/openmotion-brandkit/SKILL.md
├── templates/presenter-tech/                   → local presenter / motion package
├── templates/README.md                         → 现有可编辑工程源码
├── components/title-reveal/README.md           → 动效配方
├── design-systems/ink-water/MOTION_DESIGN.md
├── brandkits/openmotion/BRANDKIT.md
└── ENTRY_TEMPLATE.md                    → 贡献清单
```

## 🎞️ 把参考变成可传播的 Skill 包

[真人口播案例](../docs/motion-design-examples.zh-CN.md#presenter-motion)用三份设计配方连接真实语音、字幕、屏幕录制与动效；配套对比为上游演示，新的 OpenMotion 改编仍需制作与审片。

[六组动态对比](../docs/motion-design-examples.zh-CN.md)展示同一套动效实现怎样换成不同内容。每种 profile 都有 `MOTION_DESIGN.md`、保持/替换约定、固定版本源码、preset 与真实渲染证据。把可复用方法连同工程一起贡献，让下一位创作者可以继续改编。

<a id="style-recipes"></a>

### 风格配方

每个配方都是独立的 Library Skill，也是 Studio Skills 页上的一张卡片：一种画面风格，写清动效规则、所需输入、不能做什么和交付前检查。全部是配方/草稿，尚无成片对比。

| 用途 | Skills |
| --- | --- |
| 口播叠加 (10) | [荧光笔笔记](skills/openmotion-highlighter-notes/SKILL.md) · [白板马克笔](skills/openmotion-whiteboard-marker/SKILL.md) · [参数表](skills/openmotion-spec-sheet/SKILL.md) · [红笔档案](skills/openmotion-red-pen-archive/SKILL.md) · [新闻讲解杂志页](skills/openmotion-editorial-explainer/SKILL.md) · [电光大数字](skills/openmotion-electric-impact-type/SKILL.md) · [橙色大字直出](skills/openmotion-orange-unfiltered/SKILL.md) · [粗细对比字](skills/openmotion-runway-rebel/SKILL.md) · [线框物件](skills/openmotion-wireframe-style/SKILL.md) · [黑白杂志版式](skills/openmotion-monochrome-magazine/SKILL.md) |
| 无人出镜讲解 (15) | [纸片拼贴讲解](skills/openmotion-paper-collage-explainer/SKILL.md) · [白板手绘讲解](skills/openmotion-whiteboard-doodle/SKILL.md) · [纸地图旅程](skills/openmotion-paper-map-journey/SKILL.md) · [档案人物志](skills/openmotion-archive-collage/SKILL.md) · [手绘插画讲解](skills/openmotion-hand-drawn-explainer/SKILL.md) · [马卡龙扁平动画](skills/openmotion-pastel-flat-2d/SKILL.md) · [纸艺立体场景](skills/openmotion-paper-diorama/SKILL.md) · [像素风讲解](skills/openmotion-pixel-art-explainer/SKILL.md) · [课程纸感图解](skills/openmotion-editorial-webinar/SKILL.md) · [黏土动画](skills/openmotion-clay-explainer/SKILL.md) · [童话神话](skills/openmotion-storybook-myth/SKILL.md) · [毛毡定格](skills/openmotion-felt-stop-motion/SKILL.md) · [纸片定格](skills/openmotion-paper-stop-motion/SKILL.md) · [文章配图卡片](skills/openmotion-article-illustrations/SKILL.md) · [实拍转手绘](skills/openmotion-footage-to-handpainted/SKILL.md) |
| 产品宣传 (35) | [官网发布片](skills/openmotion-website-launch/SKILL.md) · [回声叠字](skills/openmotion-echo-stack-type/SKILL.md) · [劈字滚字](skills/openmotion-split-slot-type/SKILL.md) · [巨字翻牌](skills/openmotion-giant-flip-type/SKILL.md) · [等距卡片飞行](skills/openmotion-isometric-card-flight/SKILL.md) · [卡片轮播](skills/openmotion-card-carousel/SKILL.md) · [粉笔蓝图](skills/openmotion-chalk-blueprint/SKILL.md) · [一比特点阵](skills/openmotion-one-bit-dither/SKILL.md) · [霓虹描边字](skills/openmotion-neon-outline-type/SKILL.md) · [圆环遮罩转场](skills/openmotion-ring-mask-reveal/SKILL.md) · [速度线](skills/openmotion-velocity-lines/SKILL.md) · [复古扁平插画](skills/openmotion-retro-flat-scene/SKILL.md) · [极光渐变](skills/openmotion-aurora-gradient/SKILL.md) · [墨线丝带](skills/openmotion-ink-ribbon/SKILL.md) · [贴纸弹跳](skills/openmotion-sticker-bounce/SKILL.md) · [文件夹弹出](skills/openmotion-folder-pop/SKILL.md) · [角标线框](skills/openmotion-corner-frames/SKILL.md) · [百叶色带](skills/openmotion-shutter-bands/SKILL.md) · [液态色块](skills/openmotion-liquid-blob/SKILL.md) · [宣言波普](skills/openmotion-manifesto-pop/SKILL.md) · [扁平卡片讲解](skills/openmotion-flat-card-explainer/SKILL.md) · [AI 助手功能导览](skills/openmotion-ai-assistant-tour/SKILL.md) · [珊瑚标题卡](skills/openmotion-coral-title-cards/SKILL.md) · [半透明玻璃](skills/openmotion-translucent-glass/SKILL.md) · [自适应排版](skills/openmotion-adaptive-layout/SKILL.md) · [彩色泡泡](skills/openmotion-bubble-field/SKILL.md) · [卡片配文](skills/openmotion-cards-and-text/SKILL.md) · [纯色节拍](skills/openmotion-flat-beat/SKILL.md) · [磁吸粒子](skills/openmotion-magnet-particles/SKILL.md) · [星云开场](skills/openmotion-nova-intro/SKILL.md) · [高级光环](skills/openmotion-premium-halo/SKILL.md) · [镜头推近](skills/openmotion-push-in-type/SKILL.md) · [重新打光](skills/openmotion-relight-reveal/SKILL.md) · [柔滑擦除](skills/openmotion-smooth-wipes/SKILL.md) · [量子粒子](skills/openmotion-quantum-particles/SKILL.md) |
| 商品与带货 (12) | [光影商品](skills/openmotion-light-shadow-product/SKILL.md) · [飞溅漂浮](skills/openmotion-splash-float-product/SKILL.md) · [平铺陈列](skills/openmotion-flat-lay-product/SKILL.md) · [手持展示](skills/openmotion-in-hand-product/SKILL.md) · [深色高级海报](skills/openmotion-dark-premium-poster/SKILL.md) · [3D 超现实海报](skills/openmotion-surreal-3d-poster/SKILL.md) · [撞色海报](skills/openmotion-color-pop-poster/SKILL.md) · [多汁飞溅海报](skills/openmotion-juicy-splash-poster/SKILL.md) · [前后对比](skills/openmotion-before-after/SKILL.md) · [隐藏功能演示](skills/openmotion-hidden-feature-demo/SKILL.md) · [分步教程](skills/openmotion-step-by-step-tutorial/SKILL.md) · [盲盒揭晓](skills/openmotion-mystery-box-reveal/SKILL.md) |
| 品牌与封面 (10) | [故障风 Logo](skills/openmotion-glitch-logo-sting/SKILL.md) · [大字海报](skills/openmotion-bold-type-poster/SKILL.md) · [液态玻璃 Logo](skills/openmotion-liquid-glass-logo/SKILL.md) · [液体 Logo](skills/openmotion-liquid-logo/SKILL.md) · [电影感 Logo](skills/openmotion-cinematic-logo/SKILL.md) · [杂志留白海报](skills/openmotion-editorial-poster/SKILL.md) · [复古印刷海报](skills/openmotion-retro-print-poster/SKILL.md) · [纪录片感品牌片](skills/openmotion-doc-promo/SKILL.md) · [波普风短片](skills/openmotion-pop-style/SKILL.md) · [内容封面设计](skills/openmotion-content-cover/SKILL.md) |
| 特效 (2) | [贴纸撕开](skills/openmotion-sticker-peel/SKILL.md) · [时间定格](skills/openmotion-time-freeze/SKILL.md) |
| 剪辑方法 (12) | [先列候选再切短视频](skills/openmotion-shortlist-shorts/SKILL.md) · [按稿剪辑](skills/openmotion-edit-to-script/SKILL.md) · [多素材混剪](skills/openmotion-multi-clips-to-reels/SKILL.md) · [花字字幕](skills/openmotion-caption-styling/SKILL.md) · [双语字幕](skills/openmotion-bilingual-captions/SKILL.md) · [分镜转动效](skills/openmotion-storyboard-to-motion/SKILL.md) · [分镜拆解](skills/openmotion-shot-breakdown/SKILL.md) · [广告脚本](skills/openmotion-ad-script/SKILL.md) · [口播动效点位](skills/openmotion-motion-graphic-placement/SKILL.md) · [参考口播复刻](skills/openmotion-talking-head-recreation/SKILL.md) · [直播带货切片](skills/openmotion-livestream-clips/SKILL.md) · [多机位剪辑](skills/openmotion-multicam-edit/SKILL.md) |

<a id="使用资源"></a>

## 🚀 使用资源

1. 根据任务选择方法、设计体系或模板，先看状态和来源说明。
2. 将文件、自己的素材和修改目标明确交给 Agent。Brandkit 定义品牌身份，动效设计体系定义表现方式，模板提供可编辑实现。
3. 制作视频时继续使用[对应的制作 Skill](../docs/skills.md)，在同一工程里预览、修改和导出。

可选 Library Skills 可以从本地仓库分别安装：

```sh
npx skills add ./library/skills --skill openmotion-brandkit
npx skills add ./library/skills --skill openmotion-design-remix
npx skills add ./library/skills --skill openmotion-presenter-story
npx skills add ./library/skills --skill openmotion-growth-teardown
npx skills add ./library/skills --skill openmotion-design-styles
npx skills add ./library/skills --skill openmotion-spec-sheet
```

从源码或完整插件 ZIP 安装、升级到明确的宿主 Skill 目录：

```sh
node scripts/install-library-skill.mjs openmotion-design-remix /absolute/path/to/host/skills
```

安装器只接受本页列出的 101 个 `openmotion-*` 正式名称。相同内容可复用，自定义内容不会被覆盖。升级时仅清除完整文件哈希与官方原版一致的旧跳转目录；自定义、含额外文件或符号链接的旧目录会保留，并在 `preservedLegacy` 中列出，供人工检查。分别为已安装的 Library Skill 重跑此命令，再刷新宿主 Skill 列表。旧名调用已移除，请更新已有提示词和路径。

资源库当前是可浏览的源码目录，不会自动导入 Studio 或注册为 MCP 资源。五个核心制作入口仍在 [`skills/`](../skills/)；可选 Library Skills 提供品牌上下文、真人叙事设计配方、从调研到成片的增长拆解方法、96 个单风格配方或特定源码改编方法，不增加核心制作路线。[Studio 目录](../docs/template-catalog.md)与[可观看参考](../docs/collections/README.zh-CN.md)继续使用原有来源和行为。

<a id="贡献一个有用的起点"></a>

## 🤝 贡献一个有用的起点

在对应分类下新建文件夹，按[条目清单](ENTRY_TEMPLATE.md)写清用途、可编辑输入、示例、署名、许可和实际检查结果。已有模板通过链接复用，不维护第二份副本。

- **参考：** 附原作、作者与来源，供学习。
- **配方 / 草案：** 可阅读的指导，仍需在具体工程里验证。
- **可编辑示例：** 提供源码，并注明已检查的修改与导出。

记录工程版本、实际改编、导出与审片证据后，才称为已验证模板；封面、安装成功均不替代成片验证。PR 流程见[贡献指南](../CONTRIBUTING.zh-CN.md)。原创文字与示例遵循 [Apache-2.0](../LICENSE)，外部媒体和上游项目保留原许可与署名。
