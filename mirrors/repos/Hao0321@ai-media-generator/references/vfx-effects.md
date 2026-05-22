# VFX 總監級別的特效 Prompt 設計

**定位：** 電影/廣告裡「看起來很貴的那一層」來自 VFX 與物理特效。AI 生圖/影片對「特效語彙」格外敏感 — 正確的詞能把普通場景拉升到 IMAX 等級。

見 [cinematic-direction.md](cinematic-direction.md) Part 9 是精簡版；本檔是**完整版**，給真的要設計複雜視效的 prompt 時用。

---

## Part 1 — 大氣效果 (Atmospheric)

大氣是空間的靈魂。加對了，畫面就有「呼吸」。

### 霧 / 霾 / 塵

| 類型 | 物理感 | Prompt token |
|---|---|---|
| **Fog (濃霧)** | 能見度 < 50m | `thick ground fog, low visibility, moisture-laden air` |
| **Mist (薄霧)** | 半透、詩意 | `light morning mist, diaphanous veil, soft atmospheric haze` |
| **Haze (霾)** | 城市污染/霧霾 | `urban haze, compressed distance, soft sun through smog` |
| **Dust particles** | 光束裡浮塵 | `dust motes floating in shaft of light, Brownian motion particles` |
| **Smoke (戲劇煙)** | 明顯氣態 | `theatrical smoke machine haze, volumetric fog for light beams` |
| **Steam** | 熱氣 | `steam rising from hot surface, vertical wispy columns` |
| **Fog banks** | 分層霧 | `stratified fog layers, knee-height ground fog with clear air above` |

### 光束穿越大氣

```
volumetric god rays piercing through canopy, visible atmospheric light
beams, Tyndall effect, crepuscular rays from behind clouds
```

**技術細節：**
- `Tyndall effect` (光散射) — 高階訊號詞
- `crepuscular rays` (晨昏光線) — 科學精確
- `aerial perspective` (空氣透視) — 讓遠景變藍灰

---

## Part 2 — 水與液體

### 水的各種形態

| 類型 | Prompt token |
|---|---|
| **雨絲 (背光)** | `backlit rain streaks, silver needles against dark background` |
| **雨點 (特寫)** | `raindrops hitting surface in extreme close-up, macro water crown splash` |
| **暴雨** | `torrential downpour, reduced visibility, sheet rain pouring` |
| **小雨** | `gentle drizzle, barely visible, wet glistening surfaces` |
| **水坑反射** | `reflected neon in rain puddles, wet pavement mirror` |
| **瀑布** | `cascading waterfall, slow motion water ribbons, mist cloud at base` |
| **海浪** | `crashing ocean waves, white foam explosion, green-blue tube wave` |
| **水花 (超慢速)** | `high-speed water splash at 1000fps, suspended droplets frozen mid-air` |
| **波紋** | `ripples expanding across still water surface, concentric circles` |
| **水下光** | `underwater caustics, dappled light patterns on pool floor` |
| **水氣凝結** | `condensation beading on cold glass, individual water droplets` |

---

## Part 3 — 火 / 煙 / 熱

| 類型 | Prompt token |
|---|---|
| **篝火** | `crackling campfire, warm orange flicker on faces, dancing shadows` |
| **蠟燭** | `flickering candlelight, small warm point source, subtle flicker` |
| **煙** | `slow rising smoke, volumetric, lit from side, wisps curling` |
| **大火 (實拍)** | `practical fire, real flames, no CGI, pyrotechnic, warm chaotic light` |
| **爆炸 (Nolan 式)** | `practical explosion, Christopher Nolan style real pyrotechnics, ground-level blast, debris and fireball` |
| **爆炸 (大片感)** | `cinematic large-scale explosion, orange fireball with black smoke plume, Michael Bay style` |
| **熱浪** | `heat shimmer distortion, air rippling above hot surface` |
| **灰燼** | `floating embers, glowing orange specks rising, ash particles` |
| **蒸汽/水汽** | `hot steam cloud, billowing vertically, backlit` |

---

## Part 4 — 雪 / 冰 / 冷

| 類型 | Prompt token |
|---|---|
| **飄雪 (輕)** | `gentle falling snowflakes, sparse, individual flakes visible` |
| **暴風雪** | `blizzard, horizontal driving snow, whiteout conditions` |
| **積雪** | `fresh snow accumulation on surfaces, crystalline texture` |
| **冰面** | `frozen lake surface, cracked ice, reflective glaze` |
| **冰錐** | `icicles hanging from eaves, translucent ice with light refraction` |
| **哈氣** | `visible breath in cold air, vapor clouds from mouth` |
| **結霜** | `frost crystals on window glass, delicate ice ferns` |

---

## Part 5 — 光效 (Light Effects)

### Lens Flare 與光斑

| 類型 | Prompt token |
|---|---|
| **Anamorphic flare** | `horizontal anamorphic lens flare, blue streak across frame, classic Panavision` |
| **J.J. Abrams flare** | `J.J. Abrams-style excessive lens flare, multiple streaks, saturated blue` |
| **Subtle lens flare** | `controlled subtle lens flare, single gentle streak, not overbearing` |
| **Bokeh** | `creamy out-of-focus bokeh, circular highlights, 85mm f/1.4` |
| **Swirly bokeh** | `swirly Helios 44-2 bokeh, vintage lens character, spinning background` |
| **Soap bubble bokeh** | `soap bubble bokeh from Trioplan 100mm, distinct edge highlights` |
| **Chromatic aberration** | `chromatic aberration on edges, purple and green fringing, vintage lens` |
| **Vignetting** | `dark corners vignetting, vintage lens fall-off` |
| **Halation** | `red halation bloom around bright lights, Cinestill 800T emulation` |
| **Bloom / Glow** | `soft bloom around highlights, dreamy halo effect` |

### 實體光源 (Practical Sources)

| 光源 | Prompt token |
|---|---|
| **霓虹招牌** | `buzzing neon signs, magenta and cyan tube lights, visible flicker` |
| **鎢絲燈 (黃)** | `warm tungsten practicals at 3200K, golden incandescent bulbs` |
| **螢光燈 (綠)** | `fluorescent tube lighting, green cast, flickering overhead fixture` |
| **鈉蒸氣 (橘街燈)** | `sodium vapor street lamps, monochromatic orange, highway lighting` |
| **LED 彩光** | `RGB LED strips, saturated color wash, gamer setup aesthetic` |
| **蠟燭群** | `rows of candles, baroque cathedral, flickering warm points` |
| **手電筒** | `directional flashlight beam, harsh edge light, investigator mood` |
| **閃電** | `lightning strike illumination, brief stark white cold key` |
| **煙火** | `fireworks exploding overhead, colored bursts, ambient glow` |
| **投影光** | `projected light patterns, window shadow on floor, venetian blinds` |

---

## Part 6 — 動作與物理 (Physics)

AI 模型對「物理語彙」非常敏感 — 正確的詞觸發真實的動態。

### 衣物 / 頭髮 / 布料

```
cloth simulation with natural drape, silk fabric flowing in wind with
individual fold dynamics, hair flowing with per-strand physics, cape
trailing behind running subject, scarf caught in breeze
```

### 碎裂 / 破壞

```
shattering glass in slow motion, each shard catching light, debris
particles falling with realistic gravity, wall crumbling with dust plume,
paper scattering in wind
```

### 衝擊 / 爆發

```
shockwave radial blast, ground impact dust plume, muzzle flash point
source, recoil on body, bullet time 360° pan around frozen moment
```

### 自然元素

```
wind blowing through tall grass creating wave patterns, leaves swirling
in gust, sand dunes shifting, water surface rippling to wind, fire reacting
to air movement
```

---

## Part 7 — 科幻 / 奇幻 / 超自然

| 類型 | Prompt token |
|---|---|
| **全息投影** | `holographic projection, semi-transparent blue, scan lines, glitch artifacts` |
| **能量場** | `glowing energy aura around figure, volumetric force field, particle emission` |
| **魔法符文** | `glowing magic runes in mid-air, orbiting golden glyphs, ancient inscription light` |
| **傳送光** | `teleportation light column, vertical beam with particle dispersal` |
| **時間凍結** | `time freeze effect, debris frozen in midair, single subject moving through still world` |
| **電漿/電弧** | `electric arcs crawling across metal, plasma discharge, Tesla coil effect` |
| **外星大氣** | `alien atmosphere, toxic green haze, twin suns, unusual sky color` |
| **賽博龐克 UI** | `holographic UI overlay, floating data panels, translucent interface` |
| **液態金屬** | `liquid metal T-1000 effect, mercurial surface rippling, silver chrome` |
| **時空扭曲** | `spacetime distortion lens warp, gravitational fisheye, event horizon` |

---

## Part 8 — 合成與後期 (Compositing)

| 效果 | Prompt token |
|---|---|
| **Matte painting 背景** | `digital matte painting background, 2.5D parallax depth, epic landscape vista` |
| **Green screen 合成感** | `clean composite with sharp edge preservation, no green spill, natural shadow match` |
| **Multi-plate** | `multiple elements composited, foreground subject + mid-ground environment + matte sky` |
| **Sky replacement** | `replaced sky with dramatic cloudscape, color temperature matched to scene` |
| **Day-for-night** | `day-for-night grade, underexposed blue-shifted, Hollywood night illusion` |
| **Rotoscope** | `rotoscoped animation feel, traced live-action, hand-drawn edges` |
| **Stop motion** | `stop-motion puppet animation feel, slight jitter, visible craft` |
| **Frame interpolation** | `smooth 60fps interpolated motion, hyper-smooth modern feel` |
| **Datamosh / Glitch** | `datamosh glitch artifact, pixel drift, corrupted frame` |
| **Film burn transition** | `film burn transition, orange flash frame, splice` |

---

## Part 9 — 特定工具的特效支援度

### Kling (2026 最強角色 + 物理之一)

**強項：**
- 手持晃動、衣物、頭髮自然
- 水、煙、火的物理
- 相機運鏡配合物理

**Prompt 技巧：**
```
hair blowing in the wind, cloth flowing naturally with physics, water
splashing realistically on impact, dust particles catching light, fog
drifting with air current
```

### Runway Aleph (影片編輯)

**強項：**
- 加入/刪除既有影片裡的元素
- 換天空、換地面
- 局部重打光

**Prompt 示例：**
```
add gently falling snow throughout the scene with realistic accumulation
add dramatic storm clouds to the sky, maintain foreground lighting
remove the telephone pole in the background
restyle the entire shot as a Studio Ghibli animation
```

### Veo 3.1 (原生音訊 + 物理最真)

**強項：**
- 物理模擬 (跌落、碰撞、液體流動)
- 原生環境音 + 物件音效

**Prompt 技巧：**
```
glass shatters on impact with realistic physics and accompanying sound.
SFX: high-pitched crystalline shatter, shard patter on floor.
```

### Sora 2 (storyboard + remix)

**強項：**
- 長鏡頭連續性
- 跨場景風格一致

**Prompt 技巧：** 分 beats 描述特效
```
Three beats:
Beat 1: Establishing the fire from a distance.
Beat 2: Cut to practical flame lapping at a wooden beam.
Beat 3: Ember showers rising into night sky.
```

### Seedance (多鏡頭敘事)

**強項：** `Cut to` 分段，每鏡獨立特效

```
Wide shot of a forest in heavy fog, silhouette figure approaches.
Cut to: close-up of a hand reaching into volumetric beam of light.
Cut to: particles disperse as hand passes through.
```

---

## Part 10 — 超難 VFX 情境的 Prompt Recipes

### 💧 水下世界
```
Underwater scene, dappled sunlight caustics on sandy floor, visible
suspended particles, slight blue-green color shift, gentle current
movement, bubble streams rising, long focal length with shallow DoF
isolating fish subject, natural reef coral in background
```

### 🌋 火山爆發
```
Volcanic eruption at dusk, lava fountain spewing orange molten rock, black
smoke plume reaching stratosphere, volcanic ash fall foreground, lightning
within the ash cloud, hero shot from low angle with silhouetted figure
witnessing, Hoyte van Hoytema IMAX 70mm
```

### 🌆 賽博龐克雨夜
```
Cyberpunk megacity rain-soaked street at night, neon magenta and cyan
signage reflected in puddles, Cinestill 800T halation bloom around every
light source, volumetric haze from food stalls, dense atmospheric depth,
Roger Deakins Blade Runner 2049 cinematography, anamorphic 2.39:1
```

### 🚀 宇宙飛船內部
```
Interior of spacecraft, mixed lighting: warm practical panel lights vs
cool cold-blue emergency strip lights, weightless dust particles floating,
thin layer of condensation on viewport, distant earth curvature visible
through window, cables and tubes lit by practical panel illumination, Greig
Fraser Alexa 65 cinematography
```

### 🌲 魔幻森林
```
Enchanted forest at twilight, dense volumetric god rays piercing through
ancient canopy, floating magical particles drifting upward (fireflies plus
dust), moss-covered gigantic tree trunks, subtle glowing mushrooms as
practical accent light, cool blue-green base with warm accent from magical
sources, Terrence Malick Lubezki-style Steadicam drift
```

### ⚔️ 武俠決鬥
```
Two wuxia swordsmasters mid-duel in a bamboo forest at dawn, slow motion
240fps, falling bamboo leaves drift around them, misty morning air with
visible god rays, practical wind machine effect on robes, slight wire-work
weightlessness, Zhang Yimou saturated emerald and amber, Panavision
anamorphic horizontal flares on the blades as they catch light
```

### 🎭 超現實夢境
```
Dreamlike surreal scene, objects floating impossibly without gravity, soft
backlit subject with long shadow, muted pastel palette shifting subtly
across frame, slight chromatic aberration on edges, film grain, Michel
Gondry handmade practical feel, time moving at half-speed, unresolved
reality
```

### 🏛️ 古希臘 / 神話
```
Ancient Greek temple at golden hour, marble columns catching warm sunset
rays, god rays streaming between columns creating cathedral light, dust
motes floating, ambient haze, Ridley Scott Gladiator-style grandeur,
overhead crane shot establishing scale, Arri Alexa 65 with Cooke S7/i
```

### 🕳️ Horror / 恐怖
```
Dimly lit abandoned hospital corridor, flickering fluorescent practical
lights with green color cast, thin layer of haze, muted desaturated
palette with sickly green shift, wide 24mm lens creating deep perspective
with vanishing point, slow forward dolly inviting dread, Hiro Murai surreal
lowlight, locked tripod, no music cue
```

---

## Part 11 — 整合 Workflow：VFX-driven 概念到 Prompt

**案例：廣告「登山家登頂，暴風雪中的頑強」**

### ❌ 無 VFX 語彙
```
mountaineer reaching summit in snowstorm, epic
```

### ✅ VFX-directed
```
A solitary mountaineer in technical orange gear reaches the summit of a
sheer peak during a blizzard. Wide heroic low-angle shot with mountain
ridge silhouetted against raging storm clouds.

Physics & VFX:
- Horizontal driving snow particles (blizzard, whiteout threatens)
- Wind-whipped jacket fabric simulation with natural drape
- Visible breath condensation from mountaineer, dispersing in wind
- Snow accumulation on shoulders and helmet
- Ice crystals forming on beard and eyebrows
- Rope taught in wind, snow frosted along length

Atmosphere & Light:
- Deep blue-grey overcast color grade, minimal warmth
- Diffused no-shadow ambient light, occasional sun break-through piercing
  through clouds creates brief god rays on the peak
- Volumetric snow haze compressing background
- Low contrast in distance to enhance aerial perspective

Technical:
- Shot on Arri Alexa 65, Cooke S7/i 35mm, T2.0
- Kodak Vision3 500T emulation for organic grain under the gray sky
- 2.39:1 anamorphic, horizontal flare when sun breaks through
- 120fps slow motion to render snow particles clearly
- 4:1 low-key grade, deep blues in shadows, no warm highlights
```

### 為什麼這樣寫
| VFX 語彙 | 觸發什麼 |
|---|---|
| `wind-whipped jacket fabric simulation` | 物理布料 |
| `breath condensation dispersing in wind` | 微粒物理 |
| `ice crystals forming` | 材質變化 |
| `god rays piercing through clouds` | 體積光 |
| `aerial perspective` | 遠景藍灰化 |
| `120fps to render snow particles clearly` | 防止顆粒糊掉 |
| `Kodak Vision3 500T emulation` | 有機顆粒 |
| `horizontal flare when sun breaks through` | anamorphic 招牌 |

---

## 使用哲學

- **VFX token 不是越多越好** — 一個 prompt 最多挑 **5-8 個** 真正契合場景的特效詞
- **物理語彙 > 抽象美感詞** — `dust motes in god rays` 勝過 `atmospheric and dreamy`
- **針對平台調整**：
  - Kling → 物理詞彙最吃
  - Veo 3.1 → 加 SFX 音訊描述
  - Seedance → `Cut to` 分段特效
  - Runway Aleph → 動詞開頭 (add / remove / restyle)
  - Midjourney / Flux → VFX 詞用在靜態構圖上
- **Test → Bank → Reuse** — 測試哪些 VFX token 在你常用的平台上真的有效，把有效組合存成自己的「特效 preset」

## 連結

- [Segmind - Professional VFX with AI](https://blog.segmind.com/how-to-create-professional-vfx-with-ai-video-generators/)
- [Human Academy: VFX with AI](https://www.humanacademy.ai/en/blog/vfx-com-ai)
- [Awesome AI Video Prompts (GitHub)](https://github.com/geekjourneyx/awesome-ai-video-prompts)
- [Controlling Next-Gen Video AI (Medium)](https://medium.com/@creativeaininja/how-to-actually-control-next-gen-video-ai-runway-kling-veo-and-sora-prompting-strategies-92ef0055658b)
- [AI VFX with Kling Tutorial](https://www.youtube.com/watch?v=rVxNBgtP_bs)
- [Mootion AI Visual Effects](https://www.mootion.com/use-cases/en/AI-visual-effects-generator)
