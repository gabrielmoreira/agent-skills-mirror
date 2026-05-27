# HappyHorse 1.0 · 提示词索引（90 条）

> HappyHorse 1.0 是阿里巴巴 Kling 团队的视频生成模型，**原生音视频联合生成**，时长 3-15s（千问 App 5/10/15s 三档，默认 5s），提示词**严格按 30-55 词**最佳（超过 60 词会被忽略后半段）。

按场景分类。每条含完整可复制的 prompt、推荐参数、来源。也可以用 [Web 浏览器](../../tools/prompt-browser/index.html) 搜索/筛选。

## 三个核心规则

1. **主体先行，动作其后**：`A woman walking...` ✅ / `Walking, a woman...` ❌
2. **明确指定镜头技术**：HappyHorse 对"特写""广角"理解非常精确，别留给模型猜
3. **音频激活路径**：主动写 `with X audible`（如 `with rain on leaves audible`、`with engine roar audible`、`speaking English at a natural pace`），激活音频合成通道

## 目录

- [🎯 时序节拍电影感](#-时序节拍电影感) (7) — CrePal 独创写法
- [🛍️ 产品与商业广告](#-产品与商业广告) (10)
- [👤 人物与肖像](#-人物与肖像) (10)
- [⚡ 动作与运动](#-动作与运动) (10)
- [🎬 电影风格](#-电影风格) (10)
- [🌿 自然与风景](#-自然与风景) (10)

---

## 🎯 时序节拍电影感

> **来源**：[CrePal](https://crepal.ai/blog/aivideo/aivideo-happyhorse-1-0-prompts/)。独创"8s 时序节拍"写法，开头加 `Xs duration. First Ys: ... Final Zs: ...`，效果提升显著。

### hh-001 · 雨中面部特写（带时序）
`close-up` `rain` `static` `timed` · 9:16 / 8s

```
8s duration. Extreme close-up of a woman in her 30s, dark wet hair, rain running down her face, eyes focused ahead, subtle jaw tension. Camera holds still. Shallow depth of field. Overcast grey light from directly in front. Slow-motion feel, realistic skin texture, cinematic realism.
```

### hh-002 · 广角建立镜头（带时序）
`wide` `establishing` `dawn` `fade-in` · 16:9 / 8s

```
8s duration, first 2s: black. Slow fade reveals: wide shot, mountain valley at dawn, low mist between pine trees, single dirt road leading into the scene, no people. Camera very slowly pushes forward on a dolly. Soft blue-gold light on the horizon. Quiet, cinematic, high production value.
```

### hh-003 · 动作序列（带时序）
`action` `skateboard` `night` `low-angle` · 16:9 / 6s

```
6s duration. A skateboarder lands a kick-flip on wet asphalt in an empty parking lot at night. Yellow sodium lights above. Low-angle side tracking shot moving with the board. Slow motion on impact, then returns to normal speed. Realistic motion blur. Urban, gritty, authentic.
```

### hh-004 · 角色叙事（情绪驱动）
`character` `narrative` `melancholic` `diner` · 16:9 / 8s

```
8s duration. A young man, early 20s, dark curly hair, wearing a faded denim jacket, sits alone at a diner table at night. Empty coffee cup in front of him. He looks out the window, then slowly back at the table. Close-medium shot. Warm tungsten interior light against cold dark exterior. Quiet, slightly melancholic, naturalistic.
```

### hh-005 · 情绪场景（行为表达）
`emotion` `subtle` `static` `doorway` · 16:9 / 7s

```
7s duration. A woman in her 40s stands in a doorway, one hand on the frame. She looks down the hallway, pauses, then slowly closes the door. Medium shot, static camera. Soft warm interior light. No dialogue. The scene communicates loss without showing it directly.
```

### hh-006 · 产品英雄镜头（轨道运动）
`product` `skincare` `orbit` `studio` · 1:1 / 8s

```
8s duration. A luxury skincare serum bottle on a black marble surface, soft studio key light from upper left, subtle specular highlight along the glass edge. Camera slowly orbits the bottle in a 60-degree arc. Clean minimal aesthetic. Product stays sharp throughout. Commercial quality.
```

### hh-007 · 生活方式场景（活力女性）
`lifestyle` `fitness` `rooftop` `golden-hour` · 9:16 / 7s

```
7s duration. A woman in activewear stands on a rooftop at sunrise, facing the city, holding a water bottle. She takes a sip, looks out. Light tracking shot moving from side to behind. Golden hour warm light. Aspirational, clean, athletic lifestyle feel. No text. No logo.
```

---

## 🛍️ 产品与商业广告

> 全部来自 [Try Happy Horse AI](https://tryhappyhorseai.com/blog/happy-horse-ai-prompts) — 经数百次实测验证。

### hh-008 · 咖啡倒入特写（带音频）
`food` `coffee` `macro` `audio` · 1:1 / 6s

```
Extreme close-up of hot coffee being poured into a white ceramic mug, slow motion, steam rising, rich dark liquid swirling, warm studio lighting, marble surface, with pour sound audible.
```

### hh-009 · 香水瓶旋转
`product` `perfume` `rotate` `studio` · 1:1 / 6s

```
A crystal perfume bottle rotating slowly on a reflective black surface, studio lighting with soft specular highlights, mist spraying from the nozzle in slow motion, dark elegant background.
```

### hh-010 · 运动鞋产品展示
`product` `sneaker` `rotate` `minimal` · 1:1 / 8s

```
A white sneaker on a clean white surface, slow 360-degree rotation, dramatic side lighting with sharp shadows, extreme detail on texture and stitching, minimal aesthetic.
```

### hh-011 · 新鲜水果·慢动作
`food` `fruit` `macro` `slow-motion` · 1:1 / 6s

```
Slow-motion water droplets falling onto a sliced orange, extreme close-up, studio backlight, water spraying off the surface, vivid citrus color, high-speed slow motion.
```

### hh-012 · 威士忌酒杯（带音频）
`beverage` `whisky` `low-angle` `audio` · 1:1 / 6s

```
A crystal whisky glass being filled with amber liquid in slow motion, low camera angle looking upward, warm amber backlighting, ice cubes with condensation, with the pour sound audible.
```

### hh-013 · 笔记本电脑英雄镜头
`tech` `laptop` `minimal` `studio` · 16:9 / 6s

```
A slim silver laptop opens on a clean white desk, slow motion from closed to open, screen illuminates with a soft gradient, minimal tech aesthetic, cool studio lighting.
```

### hh-014 · 餐厅摆盘
`food` `plating` `overhead` `macro` · 1:1 / 6s

```
A chef's hand places a garnish on an elegantly plated restaurant dish, extreme close-up, overhead camera, soft diffused natural light from a nearby window, steam rising from the dish.
```

### hh-015 · 奢华手表产品镜头
`product` `watch` `luxury` `macro` · 1:1 / 8s

```
A luxury watch rotating slowly on a dark brushed metal surface, macro close-up, specular highlights catching the dial and bezel, dramatic directional studio lighting.
```

### hh-016 · 化妆品开箱
`product` `cosmetics` `unboxing` `minimal` · 9:16 / 8s

```
Elegant hands open a black matte cosmetics box in slow motion, tissue paper unfolding, a lipstick revealed on white cushioning, soft diffused studio lighting, premium minimalist aesthetic.
```

### hh-017 · 蜡烛燃烧（带音频）
`macro` `candle` `audio` `warm` · 1:1 / 6s

```
A thick cream-colored pillar candle burning in slow motion, extreme close-up on the flame, wax pooling and melting at the edges, warm golden light, dark background, with faint crackling sound audible.
```

---

## 👤 人物与肖像

### hh-018 · 电影感访谈（自然光）
`portrait` `interview` `natural-light` `dialog` · 16:9 / 8s

```
A mid-30s woman with short dark hair speaks directly to camera, medium close-up, natural window light from the left, shallow depth of field, soft bokeh background, calm confident expression, speaking English at a natural pace.
```

### hh-019 · 街头肖像·黄金时刻
`portrait` `street` `golden-hour` `tracking` · 16:9 / 8s

```
A young man in a navy jacket walks slowly through a busy urban street at golden hour, tracking shot from slightly ahead, warm orange light catching his face, shallow depth of field, candid documentary style.
```

### hh-020 · 老工匠制陶
`portrait` `craft` `elderly` `film-grain` · 16:9 / 8s

```
Close-up of weathered hands shaping clay on a pottery wheel, slow pan upward to reveal an elderly Japanese man's focused expression, warm workshop lighting, 16mm film grain effect.
```

### hh-021 · 舞者·工作室
`dance` `studio` `slow-motion` `motion-blur` · 9:16 / 6s

```
A female contemporary dancer mid-movement against a white studio background, high-speed slow motion, harsh directional studio lighting from stage left, motion blur on extended limbs, full body frame.
```

### hh-022 · 多语言对话镜头（韩语）
`portrait` `dialog` `korean` `studio` · 16:9 / 8s

```
A professional Korean woman in business attire speaks to camera, clean white background, three-point studio lighting, medium shot, speaking Korean at a measured pace.
```

### hh-023 · 户外玩耍的孩子
`child` `outdoor` `handheld` `joy` · 16:9 / 6s

```
A 6-year-old girl with curly red hair runs through a sunlit backyard, wide shot, handheld camera feel, natural afternoon light, motion blur on running legs, joyful expression.
```

### hh-024 · 时尚模特·编辑风
`fashion` `editorial` `runway` `slow-motion` · 9:16 / 8s

```
A tall model in an emerald green silk dress walks toward camera on a minimalist white runway, slow motion, dramatic side lighting, fabric rippling with movement, editorial magazine aesthetic.
```

### hh-025 · 厨师·餐厅厨房（带音频）
`chef` `cooking` `audio` `overhead` · 1:1 / 6s

```
A chef in white uniform flips vegetables in a wok over high flame, close-up on hands and pan, kitchen steam rising, motion blur on the toss, dramatic overhead lighting, with the sizzle sound audible.
```

### hh-026 · 科学家·实验室
`portrait` `scientist` `lab` `macro` · 16:9 / 6s

```
A female scientist in safety goggles examines a glowing blue liquid in a glass vial, extreme close-up, dark lab background with ambient equipment lights, subtle lens flare.
```

### hh-027 · 街头音乐人（带音频）
`music` `street` `rain` `audio` · 16:9 / 8s

```
A guitar player busking on a rain-slicked city street at night, medium shot, neon reflections on wet pavement, rain falling softly, with acoustic guitar sound audible, warm tungsten light from shop windows.
```

---

## ⚡ 动作与运动

### hh-028 · 山路摩托车（带音频）
`motorcycle` `mountain` `tracking` `audio` · 16:9 / 8s

```
A matte black motorcycle rides through a mountain switchback road, low tracking shot from road level, motion blur on background trees, golden late afternoon light, with engine sound audible.
```

### hh-029 · 跑酷运动员
`parkour` `urban` `dusk` `slow-motion` · 16:9 / 6s

```
A parkour athlete leaps between rooftops in an urban environment at dusk, wide shot tracking the jump, city lights beginning to appear, slow motion at the peak of the jump.
```

### hh-030 · 跑车揭幕（带音频）
`car` `tunnel` `audio` `low-angle` · 16:9 / 8s

```
A red sports car accelerates from 0 through a dark tunnel, camera at bumper level, motion blur intensifying, tunnel lights streaking overhead, with engine roar audible.
```

### hh-031 · 武术套路
`martial-arts` `kata` `wide` `silence` · 16:9 / 8s

```
A martial artist performs a slow, deliberate kata sequence on a wooden floor, wide shot, single overhead light source creating dramatic shadows, slow motion, complete silence.
```

### hh-032 · 游泳运动员水下
`sports` `swimming` `underwater` `high-speed` · 16:9 / 6s

```
An Olympic swimmer mid-stroke underwater, high-speed camera from the side, bubbles trailing from hands, light filtering in from above, motion blur on limbs, pale chlorine-blue water.
```

### hh-033 · 篮球慢动作
`sports` `basketball` `macro` `slow-motion` · 1:1 / 6s

```
A basketball spinning slowly in mid-air against a gym background, extreme slow motion close-up, detailed leather texture, stadium lights in soft bokeh below, suspended in perfect stillness.
```

### hh-034 · 骏马奔腾（带音频）
`animal` `horse` `tracking` `audio` · 16:9 / 8s

```
A chestnut horse gallops across an open field at full speed, wide tracking shot from the side, golden afternoon light, dust rising from hooves, mane and tail streaming, with hoofbeats audible.
```

### hh-035 · 无人机竞速（带音频）
`drone` `pov` `racing` `audio` · 16:9 / 8s

```
First-person drone POV racing through a forest course at high speed, motion blur on passing trees, dappled light flickering, tight turn with tilt, with drone motor whine audible.
```

### hh-036 · 雨滴玻璃特写
`macro` `rain` `window` `slow-motion` · 9:16 / 6s

```
Extreme close-up of raindrops racing down a window pane, tracking one drop, water surface refracting a blurred city street behind, slow motion.
```

### hh-037 · 落叶·慢动作（带音频）
`nature` `autumn` `macro` `audio` · 9:16 / 6s

```
A single autumn maple leaf falls from a tree branch in extreme slow motion, macro lens, late afternoon backlight, rotating slowly, with ambient forest sounds audible.
```

---

## 🎬 电影风格

### hh-038 · 35mm 黑色电影（带音频）
`noir` `b&w` `35mm` `audio` · 16:9 / 8s

```
A detective in a trench coat walks under a streetlamp in heavy rain, low angle, high contrast black and white, 35mm film grain, shadows cutting across his face, with rain and footsteps audible.
```

### hh-039 · 吉卜力风格
`ghibli` `anime` `wide` `warm` · 16:9 / 6s

```
A young girl sits in a field of tall grass watching storm clouds build on the horizon, wide shot, warm afternoon light, painted sky aesthetic, grass blowing in wind, gentle orchestral mood.
```

### hh-040 · 韦斯·安德森对称构图
`wes-anderson` `symmetry` `pastel` `vintage` · 16:9 / 6s

```
A hotel concierge stands perfectly centered in a pastel-colored lobby, symmetrical composition, flat lighting, medium shot, slight zoom-out, deadpan expression, vintage costume.
```

### hh-041 · 航拍史诗风景
`aerial` `epic` `sunrise` `coast` · 16:9 / 8s

```
Aerial drone shot pulling back to reveal a coastal cliff at sunrise, camera starting from sea level and rising, warm pink horizon, white water below the cliff, Hans Zimmer-style ambient score.
```

### hh-042 · 恐怖·走廊
`horror` `static` `audio` `atmospheric` · 16:9 / 8s

```
A long dark hospital corridor, single flickering fluorescent light ahead, static wide shot, a shadow crosses the far end, oppressive silence with faint electrical hum audible.
```

### hh-043 · 8mm 家庭录像
`vintage` `8mm` `family` `warm` · 4:3 / 8s

```
A family barbecue in a backyard in summer, handheld 8mm film aesthetic, color shift to warm orange, film grain, spontaneous framing, children running in background, muffled ambient sound.
```

### hh-044 · 赛博朋克城市景观（带音频）
`cyberpunk` `neon` `rain` `audio` · 16:9 / 8s

```
A neon-lit street in a futuristic Asian megacity at night, rain-slicked road, holographic ads flickering overhead, pedestrians with umbrellas, tracking shot from a low vehicle, with electronic ambient music audible.
```

### hh-045 · 慢速电视·风景
`slow-tv` `static` `nature` `ambient` · 16:9 / 8s

```
A real-time shot of a river at dusk, static wide angle, water flowing slowly over smooth rocks, light fading gradually, ambient river sounds, no music, no cuts.
```

### hh-046 · 新闻播报风格
`broadcast` `news` `studio` `dialog` · 16:9 / 8s

```
A news anchor at a desk with a broadcast studio background, three-point lighting, medium shot, speaking directly to camera, neutral expression, speaking English in a measured tone.
```

### hh-047 · 抽象动态图形
`abstract` `fluid` `macro` `silence` · 1:1 / 6s

```
Flowing liquid metal morphs into geometric shapes, extreme close-up, dark background, iridescent color shift from silver to gold, slow rotation, high specular highlights, complete silence.
```

---

## 🌿 自然与风景

### hh-048 · 日出海浪（带音频）
`nature` `ocean` `sunrise` `audio` · 16:9 / 8s

```
Slow motion ocean waves breaking on a rocky coastline at sunrise, wide shot, warm pink and orange light, seafoam detail, shallow depth of field on foreground rocks, with ocean sound audible.
```

### hh-049 · 雨中森林（带音频）
`nature` `forest` `rain` `audio` · 16:9 / 8s

```
A dense Pacific Northwest forest during light rain, static wide shot, drops falling through shafts of pale morning light, puddle surface rings, fog in the mid-distance, with rain on leaves audible.
```

### hh-050 · 沙漠延时
`timelapse` `desert` `wide` `warm` · 16:9 / 8s

```
An accelerated timelapse of clouds moving over red rock desert formations, wide establishing shot, harsh afternoon shadows shifting rapidly, deep blue sky, warm ochre rock tones.
```

### hh-051 · 城市降雪
`snow` `city` `static` `night` · 16:9 / 8s

```
Heavy snowfall over a quiet European city square at night, wide static shot, streetlights creating halos in the falling snow, snow accumulating on stone surfaces, empty cobblestone streets.
```

### hh-052 · 水下海带森林
`underwater` `kelp` `ethereal` `silence` · 16:9 / 8s

```
Sunlight filtering through a kelp forest underwater, slow drifting camera movement upward, bioluminescent particles, wide shot, deep blue-green color grade, complete silence.
```

### hh-053 · 火山喷发·航拍
`aerial` `volcano` `night` `tracking` · 16:9 / 8s

```
Aerial drone view of active lava flowing down a dark volcanic mountainside at night, slow tracking shot from above, glowing red-orange lava against black rock, steam rising from cooling edges.
```

### hh-054 · 樱花飘落
`sakura` `japan` `slow-motion` `spring` · 16:9 / 8s

```
Cherry blossom petals falling from a full-bloom tree in a Japanese garden, slow motion, pale pink petals against a soft grey sky, wooden bench and stone path below, gentle spring light.
```

### hh-055 · 闪电风暴延时
`timelapse` `storm` `lightning` `wide` · 16:9 / 8s

```
Time-lapse of a lightning storm over flat prairie land, dark dramatic sky, multiple lightning strikes illuminating storm clouds, distant rain curtains visible, wide landscape shot.
```

### hh-056 · 秋日森林漫步·第一视角（带音频）
`pov` `autumn` `forest` `audio` · 16:9 / 8s

```
A first-person POV walk through a dense autumn forest, leaves in orange and red, dappled afternoon light through the canopy, slight camera sway, dry leaves crunching underfoot with sound.
```

### hh-057 · 北极冰洞
`arctic` `ice-cave` `ethereal` `audio` · 16:9 / 8s

```
Inside a translucent blue Arctic ice cave, slow panning shot, shafts of pale light through the ice ceiling, ice crystal formations on walls, near silence with faint wind audible.
```

---

## 下一步

- 想看 Seedance 提示词 → [seedance/README.md](../seedance/README.md)
- 想理解 HappyHorse 公式 → [methodology/02-进阶公式.md](../../methodology/02-进阶公式.md)
- 想让 Claude 用 happyhorse 公式写 → [skills/happyhorse-prompter](../../skills/happyhorse-prompter/)
