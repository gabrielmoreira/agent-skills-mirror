# Kling 3.0 · 提示词索引（72 条）

> **Kling 3.0**（可灵 3.0，快手出品）是 2026 年支持原生音画同步、智能分镜、最长 2 分钟视频的电影级生成模型。中文理解能力业界领先，对镜头语言响应精准。

按场景分类。每条含完整可复制的 prompt、推荐参数、来源。也可以用 [Web 浏览器](../../tools/prompt-browser/index.html) 搜索/筛选。

## 三套核心写法

Kling 提示词有三种主流写法，按复杂度递进：

| 写法 | 公式 | 适用 | 代表条目 |
|---|---|---|---|
| **4 部分基础** | Subject + Action + Context + Style | 单一场景、短视频 | kl-006/014/021 |
| **5 层进阶** | Scene → Characters → Action → Camera → Audio & Style | 带剧情、带音频、复杂叙事 | kl-001/009/010/011/019 |
| **图生视频** | 只描述运动，不重描述视觉 | 已有参考图 | kl-002/003/013/018/020/035/036 |

详见 [methodology/09-kling-公式.md](../../methodology/09-kling-公式.md)。

## 目录

- [🛍️ 产品与商业广告](#-产品与商业广告) (5)
- [🎬 电影叙事与戏剧场景](#-电影叙事与戏剧场景) (8)
- [⚡ 动作、格斗与追逐](#-动作格斗与追逐) (5)
- [🌀 病毒变身与转场](#-病毒变身与转场) (4)
- [🎵 音乐 MV 与表演](#-音乐-mv-与表演) (3)
- [🔮 实验与超现实](#-实验与超现实) (4)
- [🎮 游戏与 IP 风](#-游戏与-ip-风) (3)
- [🖼️ 图生视频专项](#-图生视频专项) (4)

---

## 🛍️ 产品与商业广告

### kl-001 · 香水广告（带角色配音 CTA）
`product` `perfume` `audio` `narrative` `5-layer` · 9:16 / 10s · [Atlabs AI](https://www.atlabs.ai/blog/kling-3-0-prompting-guide-master-ai-video-generation)

```
Scene: Interior studio with smooth gradient lighting and a polished marble pedestal. Characters: A confident host (mid-30s, sleek black blazer) stands beside the bottle. Action: Close-up rotating perfume bottle, then the host introduces it enthusiastically, describing the scent notes with hand gestures. Extreme close-up of mist erupting in slow motion. Camera: Smooth orbit then push-in to extreme macro, ending on host's direct address. Audio & Style: Warm voiceover with subtle jazz bed, crisp atomizer hiss; luxury commercial polish.
```
> 💡 5 层公式样板，Kling 原生音画同步的"看家场景"

### kl-002 · 雨夜跑车启动（图生视频）
`car` `rain` `image-to-video` `audio` · 16:9 / 5s · [vicsee.com](https://vicsee.com/blog/kling-3-prompts)

```
The headlights blaze on and the engine roars to life. The rear tires spin, spraying water across the wet asphalt, and the car launches forward. The camera tracks alongside at speed as neon reflections streak past on the wet ground.
```
> 💡 图生视频典范：只描述运动，不重描述图中已有的车型/环境。湿地面提供丰富运动数据。

### kl-003 · 球鞋悬浮旋转（图生视频）
`product` `sneaker` `image-to-video` `orbit` · 1:1 / 5s · [vicsee.com](https://vicsee.com/blog/kling-3-prompts)

```
The sneaker rotates in midair, the side lighting catching different textures as it turns. Gold dust particles drift across the frame. The shoe tilts slightly, hovering, as if weightless. The camera orbits around it in a half circle.
```

### kl-004 · 奢华手表 360 度旋转（图生视频）
`product` `watch` `image-to-video` · 1:1 / 5s · [VEED](https://www.veed.io/learn/kling-ai-prompting-guide)

```
Watch rotates smoothly 360 degrees clockwise, maintaining position on surface, subtle reflections shifting on metal surfaces.
```
> 💡 图生视频「只写运动」最纯净示范

### kl-005 · 夜市炒锅火球（图生视频）
`food` `fire` `image-to-video` `audio` · 16:9 / 8s · [vicsee.com](https://vicsee.com/blog/kling-3-prompts)

```
The chef flips the wok hard, launching noodles into the air as a fireball erupts upward. He catches them clean, tilts the wok and slides the dish onto a plate with his spatula, then pushes the plate across the worn counter toward the camera with a grin. Steam billows upward through the lantern light.
```
> 💡 明火创造动态光照，明确指定工具（wok/spatula）增强物理真实感

---

## 🎬 电影叙事与戏剧场景

### kl-006 · 赛博朋克侦探
`noir` `cyberpunk` `rain` `tracking` · 21:9 / 8s · [Elser AI](https://www.elser.ai/blog/kling-ai-prompts-guide-25-cinematic-prompts-that-actually-work-in-2026)

```
A cyberpunk detective walking through a neon-lit alley, camera tracking behind him, rain falling, reflections on wet ground, cinematic lighting, noir atmosphere.
```

### kl-007 · 末日废墟探索
`post-apocalyptic` `wide` · 16:9 / 8s · [Elser AI](https://www.elser.ai/blog/kling-ai-prompts-guide-25-cinematic-prompts-that-actually-work-in-2026)

```
A post-apocalyptic survivor exploring abandoned city ruins, wide angle shot, dusty air, cinematic color grading.
```

### kl-008 · 太空探索者落地（戏剧揭幕）
`sci-fi` `reveal` `volumetric-light` · 16:9 / 8s · [Elser AI](https://www.elser.ai/blog/kling-ai-prompts-guide-25-cinematic-prompts-that-actually-work-in-2026)

```
A space explorer stepping onto an unknown planet, dramatic reveal shot, volumetric lighting, epic sci-fi tone.
```

### kl-009 · 黄金时刻重逢（情感对话）
`reunion` `golden-hour` `audio` `dialog` `5-layer` · 16:9 / 12s · [Atlabs AI](https://www.atlabs.ai/blog/kling-3-0-prompting-guide-master-ai-video-generation)

```
Scene: A park bench at golden hour, fall leaves drifting. Characters: Two reunited friends with a 10-year gap, both early 30s. Action: Alternating over-the-shoulder shots between both characters with nostalgic dialogue about missing each other, culminating in a moment of shared emotional recognition. Camera: Slow push-in on each speaker, ending on a held wide two-shot. Audio & Style: Soft piano underscore, ambient park sounds, warm cinematic color grade.
```

### kl-010 · 雨夜车内对话
`dialog` `rain` `tension` `audio` `5-layer` · 16:9 / 10s · [Atlabs AI](https://www.atlabs.ai/blog/kling-3-0-prompting-guide-master-ai-video-generation)

```
Scene: Interior of a parked car at night with rain drumming on the roof. Characters: Driver (40s, weathered face) and passenger (20s, anxious). Action: Driver expresses hesitation while passenger avoids eye contact, exploration of misunderstanding through tense back-and-forth dialogue with rain intensifying throughout. Camera: Tight two-shots alternating with isolating singles, slight handheld drift. Audio & Style: Heavy rain ambience, no music, naturalistic dialogue.
```

### kl-011 · 教练训斥鼓手（高强度训练）
`tension` `audio` `drama` `5-layer` · 16:9 / 12s · [Atlabs AI](https://www.atlabs.ai/blog/kling-3-0-prompting-guide-master-ai-video-generation)

```
Scene: A dimly lit jazz rehearsal room with cymbals catching key light. Characters: A drumming instructor (60s, intense) and a young drummer (20s, sweating). Action: Instructor critiques drummer's tempo with escalating fury through multiple close-ups on sweating hands, facial expressions, and cymbal crashes. Character stammers nervously while instructor demands precision through shouted corrections. Camera: Punchy quick cuts, snap zooms to drummer's face. Audio & Style: Loud cymbal hits, raw vocal performance, no music.
```

### kl-012 · 电梯邂逅（克制情感）
`romance` `subtle` `minimal-dialog` `5-layer` · 9:16 / 10s · [Atlabs AI](https://www.atlabs.ai/blog/kling-3-0-prompting-guide-master-ai-video-generation)

```
Scene: An elevator at night, soft fluorescent ambient. Characters: Two strangers (late 20s) who discover shared music taste during an elevator encounter. Action: Subtle smiles and whispered recognition develop connection through minimal dialogue before doors open, suggesting possibility. Camera: Static two-shot with rack focus between faces. Audio & Style: Faint elevator hum, almost imperceptible music leak from one stranger's headphones.
```

### kl-013 · 雨中咖啡馆肖像（图生视频）
`portrait` `rain` `image-to-video` `cinematic` · 16:9 / 8s · [vicsee.com](https://vicsee.com/blog/kling-3-prompts)

```
She lowers her cup to the saucer, gazing out at the rain. Lightning cracks outside, illuminating the wet street for an instant — she turns toward the camera with a faint smile. Rain intensifies on the glass, streaks racing down, neon reflections rippling on the cobblestones. Slow dolly in toward her face.
```
> 💡 Kling 优先处理人物动作而非环境事件 — 雷电只作为氛围触发

---

## ⚡ 动作、格斗与追逐

### kl-014 · 剑士对决慢镜
`sword` `slow-motion` `rotation` · 16:9 / 5s · [Elser AI](https://www.elser.ai/blog/kling-ai-prompts-guide-25-cinematic-prompts-that-actually-work-in-2026)

```
Two warriors clashing swords in slow motion, sparks flying, dynamic camera rotation, high contrast lighting.
```

### kl-015 · 动漫街头格斗
`anime` `handheld` `motion-blur` · 16:9 / 5s · [Elser AI](https://www.elser.ai/blog/kling-ai-prompts-guide-25-cinematic-prompts-that-actually-work-in-2026)

```
Anime-style street fight, handheld camera feel, fast motion blur, intense expressions.
```

### kl-016 · 超级英雄落地冲击
`superhero` `impact` `cinematic` · 16:9 / 5s · [Elser AI](https://www.elser.ai/blog/kling-ai-prompts-guide-25-cinematic-prompts-that-actually-work-in-2026)

```
A superhero landing impact shot, ground cracking, cinematic zoom, dramatic lighting.
```

### kl-017 · 雨中武术
`martial-arts` `rain` `slow-motion` · 16:9 / 5s · [Elser AI](https://www.elser.ai/blog/kling-ai-prompts-guide-25-cinematic-prompts-that-actually-work-in-2026)

```
Martial arts fight in a rainy alley, water splashes, slow-motion kicks, ultra-detailed.
```

### kl-019 · 体育场冲场（队长鼓舞）
`sports` `stadium` `audio` `epic` `5-layer` · 16:9 / 12s · [Atlabs AI](https://www.atlabs.ai/blog/kling-3-0-prompting-guide-master-ai-video-generation)

```
Scene: A stadium tunnel transitioning to a bright field. Characters: Players in team colors with the quarterback (captain) at the front. Action: Players depicted with backlit low angles gaining momentum, quarterback rallies team with commanding voice, then wide stadium shots with crowd and pyrotechnics. Camera: Tunnel POV → backlit low-angle hero shot → crane wide reveal. Audio & Style: Orchestral music building tension, crowd roar, captain's shouted voice line.
```

---

## 🌀 病毒变身与转场

### kl-021 · 真人变动漫角色（短视频爆款）
`transformation` `anime` `tiktok` · 9:16 / 5s · [Elser AI](https://www.elser.ai/blog/kling-ai-prompts-guide-25-cinematic-prompts-that-actually-work-in-2026)

```
A girl transforming into an anime character, smooth transition, glowing effects, TikTok style.
```

### kl-022 · 前后对比变身（分屏）
`before-after` `split-screen` `anime` · 9:16 / 5s · [Elser AI](https://www.elser.ai/blog/kling-ai-prompts-guide-25-cinematic-prompts-that-actually-work-in-2026)

```
Before vs after anime transformation, split screen, high contrast visuals.
```

### kl-023 · 赛博朋克化身（毛刺效果）
`cyberpunk` `transformation` `glitch` `neon` · 9:16 / 5s · [Elser AI](https://www.elser.ai/blog/kling-ai-prompts-guide-25-cinematic-prompts-that-actually-work-in-2026)

```
A realistic human turning into cyberpunk avatar, glitch effects, neon lighting.
```

### kl-024 · 未来城 POV 醒来
`pov` `futuristic` `immersive` · 9:16 / 5s · [Elser AI](https://www.elser.ai/blog/kling-ai-prompts-guide-25-cinematic-prompts-that-actually-work-in-2026)

```
POV: waking up in a futuristic city, first-person camera, immersive motion.
```

---

## 🎵 音乐 MV 与表演

### kl-025 · 霓虹舞台演唱
`music` `stage` `neon` · 16:9 / 8s · [Elser AI](https://www.elser.ai/blog/kling-ai-prompts-guide-25-cinematic-prompts-that-actually-work-in-2026)

```
A singer performing on a neon stage, dynamic lighting, cinematic camera movement.
```

### kl-026 · 超现实梦境序列
`surreal` `dreamlike` `slow-motion` · 16:9 / 8s · [Elser AI](https://www.elser.ai/blog/kling-ai-prompts-guide-25-cinematic-prompts-that-actually-work-in-2026)

```
Abstract dream sequence with floating objects, slow motion, surreal visuals.
```

### kl-027 · 舞者穿越多场景
`dance` `transition` `music-video` · 16:9 / 8s · [Elser AI](https://www.elser.ai/blog/kling-ai-prompts-guide-25-cinematic-prompts-that-actually-work-in-2026)

```
A dancer moving through shifting environments, seamless transitions.
```

---

## 🔮 实验与超现实

### kl-028 · 时间冻结的街道
`time-freeze` `surreal` `camera-move` · 16:9 / 8s · [Elser AI](https://www.elser.ai/blog/kling-ai-prompts-guide-25-cinematic-prompts-that-actually-work-in-2026)

```
Time freezing in a busy city street, camera moving through frozen people.
```

### kl-029 · 跨世界行走
`multi-world` `surreal` `transformation` · 16:9 / 8s · [Elser AI](https://www.elser.ai/blog/kling-ai-prompts-guide-25-cinematic-prompts-that-actually-work-in-2026)

```
A character walking through different worlds with each step.
```

### kl-030 · 现实故障破碎
`glitch` `distortion` `surreal` · 16:9 / 5s · [Elser AI](https://www.elser.ai/blog/kling-ai-prompts-guide-25-cinematic-prompts-that-actually-work-in-2026)

```
Reality glitching and breaking apart, surreal distortion.
```

### kl-031 · 镜中世界
`mirror` `alternate` `surreal` · 16:9 / 8s · [Elser AI](https://www.elser.ai/blog/kling-ai-prompts-guide-25-cinematic-prompts-that-actually-work-in-2026)

```
A mirror world reflecting an alternate version of the character.
```

---

## 🎮 游戏与 IP 风

### kl-032 · RPG 地牢入口
`rpg` `fantasy` `torch` · 16:9 / 5s · [Elser AI](https://www.elser.ai/blog/kling-ai-prompts-guide-25-cinematic-prompts-that-actually-work-in-2026)

```
A fantasy RPG hero entering a dungeon, torch lighting, cinematic angle.
```

### kl-033 · 数字黑客世界
`hacker` `cyberpunk` `neon` · 16:9 / 5s · [Elser AI](https://www.elser.ai/blog/kling-ai-prompts-guide-25-cinematic-prompts-that-actually-work-in-2026)

```
Cyberpunk hacker inside a digital world, floating code, neon grids.
```

### kl-034 · 动漫 Boss 战开场
`boss-battle` `anime` `vfx` · 16:9 / 5s · [Elser AI](https://www.elser.ai/blog/kling-ai-prompts-guide-25-cinematic-prompts-that-actually-work-in-2026)

```
Anime-style boss battle intro, dramatic zoom, energy effects.
```

---

## 🖼️ 图生视频专项

### kl-018 · 武士拔刀斩竹（图生视频）
`samurai` `image-to-video` `katana` `physical` · 16:9 / 5s · [vicsee.com](https://vicsee.com/blog/kling-3-prompts)

```
The samurai raises the katana and slashes in one explosive arc, the blade catching golden light as it cuts through the air. Mist swirls violently around the slash. Two bamboo stalks behind him slide and topple, cut clean. The camera pushes in slowly on his face, eyes locked forward.
```
> 💡 明确指定工具（katana/bamboo）+ 因果链（slash→bamboo topples）= 强物理感

### kl-020 · 拉力赛车出弯（图生视频）
`rally` `image-to-video` `motorsport` · 16:9 / 6s · [vicsee.com](https://vicsee.com/blog/kling-3-prompts)

```
The car powers out of the corner, rear end sliding wide, gravel and dirt erupting from the tires in a rooster tail. It straightens, accelerates hard down the mountain road, kicking up a dust cloud that hangs in the golden afternoon light. The camera pans to follow as it disappears around the next bend.
```
> 💡 用显式速度动词（powers/accelerates hard）覆盖 Kling 默认的慢动作倾向

### kl-035 · 雄鹰击水捕鱼（图生视频）
`wildlife` `image-to-video` `eagle` `nature` · 16:9 / 6s · [vicsee.com](https://vicsee.com/blog/kling-3-prompts)

```
The eagle's talons slam into the river with an explosive splash, water erupting around its legs. Wings beat down hard and it launches back into the air, climbing fast, water streaming off its talons in silver trails. The camera tilts up to follow as it rises against the mountain backdrop, morning light catching the spray.
```
> 💡 Kling 自带的电影感慢镜会自动渲染戏剧瞬间

### kl-036 · 龙塔起飞（图生视频）
`dragon` `image-to-video` `fantasy` `epic` · 21:9 / 8s · [vicsee.com](https://vicsee.com/blog/kling-3-prompts)

```
The dragon beats its wings with thunderous force and launches off the tower, stone crumbling from the edge. It rockets upward, the downdraft scattering torchlight in the streets below. It banks hard left at speed, jaws opening, a stream of fire ripping across the storm sky. Lightning illuminates its silhouette.
```
> 💡 幻想场景用真实物理交互锚定（stone crumbles / torches flicker）= 可信度大增

---

## 下一步

- 想看 Seedance / HappyHorse 提示词 → [../seedance/](../seedance/README.md) · [../happyhorse/](../happyhorse/README.md)
- 想理解 Kling 的写法差异 → [methodology/09-kling-公式.md](../../methodology/09-kling-公式.md)
- 想让 Claude 帮你写 Kling 提示词 → [skills/kling-prompter/](../../skills/kling-prompter/SKILL.md)
- 想用 Web 工具搜索筛选 → [tools/prompt-browser/index.html](../../tools/prompt-browser/index.html)
