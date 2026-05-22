# Director Style Library — 31 World-Class Filmmakers

**Source attribution：** Distilled from [`xjpp22/awesome--sora-prompts`](https://github.com/xjpp22/awesome--sora-prompts) (open source, 102⭐). Each director entry maps to a **Visual Style Prompt** + **Editing Style Prompt** based on their signature masterpiece.

**用法：** 寫 prompt 時，**用導演姓名 + 「style」**（適用 MJ / Sora 2 / Veo 3.1 / Kling — 見 [community-prompt-patterns.md](community-prompt-patterns.md) 的「導演名分裂」META rule）。或直接挑 director 對應的 Visual / Editing prompt tokens 嵌入你的 prompt。

**⚠️ 平台分流（再次強調）：**
- ✅ MJ v7 / Sora 2 / Veo 3.1 / SDXL：直接用 `in the style of {Director Name}` 有效
- ❌ Flux / Nano Banana Pro：訓練時被 scrub，改用具體 Visual Style Prompt 描述
- ⚠️ Seedance / Wan / Hailuo（中文影片模型）：個別 DP 名弱證據，**改用 Visual Style 具體 token**

---

## 🎬 大師索引（31 位）

| # | 導演 | 代表作 | 風格速覽 |
|---|---|---|---|
| 1 | Wes Anderson | The Grand Budapest Hotel | 對稱 + 粉彩 + 玩偶屋感 |
| 2 | Stanley Kubrick | The Shining | 技術精準 + 反差不安 |
| 3 | Wong Kar-wai 王家衛 | In the Mood for Love | 霓虹色調 + 慢動作 + 跟拍長鏡 |
| 4 | David Lynch | Mulholland Drive | 超現實 + 變形視角 |
| 5 | Quentin Tarantino | Pulp Fiction | 致敬經典 + 暴力長鏡 + 分割畫面 |
| 6 | Darren Aronofsky | Requiem for a Dream | 變形鏡 + 手持 + 幽閉框 |
| 7 | Park Chan-wook 朴贊郁 | Oldboy | 唯美暴力 + 單鏡動作 + 新黑色 |
| 8 | Christopher Nolan | Interstellar | 實拍 + IMAX + 真實太空 |
| 9 | Hayao Miyazaki 宮崎駿 | Spirited Away | 手繪動畫 + 鮮豔色彩 + 夢幻 |
| 10 | Alfonso Cuarón | Gravity | 長鏡頭 + 單鏡頭 sequence |
| 11 | Terrence Malick | The Tree of Life | 自然光 + 慢鏡 + 詩意 |
| 12 | Paul Thomas Anderson | There Will Be Blood | 長鏡 + 質感 + 時代感 |
| 13 | Lynne Ramsay | You Were Never Really Here | 主觀鏡 + 手持 + 變形 |
| 14 | Bong Joon-ho 奉俊昊 | Parasite | 階級對比 + 動態跟拍 |
| 15 | Denis Villeneuve | Blade Runner 2049 | 史詩景觀 + 氛圍光 + CGI |
| 16 | Andrei Tarkovsky | Stalker | 長鏡 + 慢節奏 + 夢幻 |
| 17 | Pedro Almodóvar | Pain and Glory | 大膽色 + 鮮豔場景 + 情緒特寫 |
| 18 | Jane Campion | The Piano | 寬全景 + 自然景 + 女性凝視 |
| 19 | Guillermo del Toro | Pan's Labyrinth | 暗黑奇幻 + 怪物 + 魔幻寫實 |
| 20 | Agnès Varda | Vagabond | 手持 + 紀錄寫實 + 自然光 |
| 21 | Spike Lee | Do the Right Thing | 大膽色 + Dutch angle + 跟拍 |
| 22 | Kelly Reichardt | First Cow | 極簡 + 自然景 + 慢節奏 |
| 23 | Hirokazu Kore-eda 是枝裕和 | Still Walking | 長鏡 + 靜止 + 家庭 + 自然光 |
| 24 | Sofia Coppola | Lost in Translation | 粉彩 + 對稱 + 憂鬱 |
| 25 | Lars von Trier | Dancer in the Dark | 手持 + 晃動 + 主觀 + 實驗 |
| 26 | Kathryn Bigelow | The Hurt Locker | 手持 + 戰爭真實 + 幽閉 |
| 27 | Jia Zhangke 賈樟柯 | A Touch of Sin | 長鏡 + 靜止 + 當代中國 |
| 28 | Barry Jenkins | Moonlight | 蔥鬱攝影 + 親密特寫 + 鮮色 |
| 29 | Apichatpong Weerasethakul 阿比查邦 | Uncle Boonmee | 長鏡 + 夢境 + 魔幻寫實 |
| 30 | Michel Gondry | Eternal Sunshine | 創意特效 + 玩心 + 夢境 |
| 31 | Panos Cosmatos | Mandy | 霓虹迷幻 + 對稱 + 反烏托邦 |

---

## 🎨 完整風格描述（Visual + Editing Style Prompts）

### 1. Wes Anderson — *The Grand Budapest Hotel*
- **Visual：** Meticulously symmetrical compositions, pastel color palettes, dollhouse-like miniatures, quirky camera angles, tracking shots
- **Editing：** Fast-paced with jump cuts, witty dialogue, synchronized montages

### 2. Stanley Kubrick — *The Shining*
- **Visual：** Technically masterful with sweeping landscapes, innovative effects, and stark contrasts creating unease
- **Editing：** Precise and calculated with long takes and montage sequences building suspense and realism

### 3. Wong Kar-wai 王家衛 — *In the Mood for Love*
- **Visual：** Lush color palettes, neon lights, slow-motion, tracking shots, long takes, unique camerawork
- **Editing：** Dreamlike sequences, melancholic atmosphere, juxtaposition of past and present

### 4. David Lynch — *Mulholland Drive*
- **Visual：** Surreal imagery, distorted perspectives, unsettling close-ups, dreamlike sequences, industrial landscapes
- **Editing：** Non-linear narrative, jump cuts, disorienting sound design

### 5. Quentin Tarantino — *Pulp Fiction*
- **Visual：** Homages to classic cinema, pop culture references, close-ups on violence, long takes, split-screen sequences
- **Editing：** Non-linear storytelling, dynamic dialogue, punctuating violence, iconic soundtrack

### 6. Darren Aronofsky — *Requiem for a Dream*
- **Visual：** Disturbing imagery, distorted lenses, handheld camerawork, claustrophobic framing, tracking shots
- **Editing：** Fast-paced cuts, subjective point-of-view, unsettling imagery, layered sound design

### 7. Park Chan-wook 朴贊郁 — *Oldboy*
- **Visual：** Visually striking violence, long takes, single-shot action sequences, neo-noir atmosphere, dramatic color palettes
- **Editing：** Stylized transitions, impactful slow-motion, suspenseful sequences, dynamic sound design

### 8. Christopher Nolan — *Interstellar*
- **Visual：** Practical effects, IMAX cinematography, awe-inspiring landscapes, realistic space visuals, handheld camerawork
- **Editing：** Tight cuts, complex timelines, intricate time travel sequences, impactful sound design

### 9. Hayao Miyazaki 宮崎駿 — *Spirited Away*
- **Visual：** Hand-drawn animation, vibrant colors, whimsical creatures, detailed landscapes, dreamlike sequences
- **Editing：** Emotionally driven pacing, seamless transitions, focus on character expressions and movement

### 10. Alfonso Cuarón — *Gravity*
- **Visual：** Long takes, single-shot sequences, realistic space visuals, immersive camerawork, minimal dialogue
- **Editing：** Seamless cuts, subjective point-of-view, use of silence and sound design to build tension

### 11. Terrence Malick — *The Tree of Life*
- **Visual：** Natural light, breathtaking landscapes, slow-motion shots, poetic imagery, philosophical themes
- **Editing：** Impressionistic, non-linear, voiceover narration, long takes, contemplative pacing

### 12. Paul Thomas Anderson — *There Will Be Blood*
- **Visual：** Long takes, meticulous cinematography, focus on textures and details, period-specific atmosphere, oil landscapes
- **Editing：** Rhythmic cuts, complex character studies, use of silence and sound design to create tension

### 13. Lynne Ramsay — *You Were Never Really Here*
- **Visual：** Subjective camerawork, handheld shots, close-ups, distorted perspectives, use of color to reflect emotions
- **Editing：** Non-linear narrative, jump cuts, disorienting imagery, sound design as storytelling tool

### 14. Bong Joon-ho 奉俊昊 — *Parasite*
- **Visual：** Contrasting visuals (rich vs. poor), dynamic tracking shots, meticulous set design, claustrophobic framing
- **Editing：** Fast-paced cuts, unexpected shifts in tone, dark humor, suspenseful build-up

### 15. Denis Villeneuve — *Blade Runner 2049*
- **Visual：** Visually stunning landscapes, atmospheric lighting, realistic CGI, epic scale, slow-motion sequences
- **Editing：** Precise cuts, building tension, use of silence and sound design, immersive experience

### 16. Andrei Tarkovsky — *Stalker*
- **Visual：** Long takes, slow pacing, dreamlike sequences, philosophical themes, emphasis on nature
- **Editing：** Contemplative, minimalist, metaphorical, use of long shots to build atmosphere

### 17. Pedro Almodóvar — *Pain and Glory*
- **Visual：** Bold colors, vibrant sets, expressive costumes, melodrama, stylized framing, close-ups on emotions
- **Editing：** Fast-paced, playful, dramatic shifts, voiceover narration, use of pop music

### 18. Jane Campion — *The Piano*
- **Visual：** Wide panoramic shots, natural landscapes, focus on female gaze, raw emotions, evocative use of silence
- **Editing：** Rhythmic cuts, subtle storytelling, character-driven moments, exploration of unspoken tension

### 19. Guillermo del Toro — *Pan's Labyrinth*
- **Visual：** Dark fantasy aesthetic, grotesque creatures, magical realism, intricate production design, dreamlike sequences
- **Editing：** Dynamic cuts, suspenseful build-up, juxtaposition of beauty and horror, impactful sound design

### 20. Agnès Varda — *Vagabond*
- **Visual：** Handheld camerawork, documentary realism, social commentary, focus on marginalized characters, use of natural light
- **Editing：** Non-linear narrative, jump cuts, blending fiction and documentary, observational approach

### 21. Spike Lee — *Do the Right Thing*
- **Visual：** Bold color palettes, dynamic camerawork, Dutch angles, tracking shots, use of music videos as inspiration
- **Editing：** Rhythmic cuts, energetic sequences, juxtaposing humor and social commentary, impactful soundtrack

### 22. Kelly Reichardt — *First Cow*
- **Visual：** Minimalism, natural landscapes, muted colors, slow pacing, long takes, focus on character interactions
- **Editing：** Contemplative pacing, subtle drama, use of silence and sound design to build atmosphere

### 23. Hirokazu Kore-eda 是枝裕和 — *Still Walking*
- **Visual：** Long takes, static camerawork, intimate compositions, focus on family dynamics, natural light
- **Editing：** Subtle cuts, observational approach, naturalistic acting, quiet emotional moments

### 24. Sofia Coppola — *Lost in Translation*
- **Visual：** Pastel color palettes, elegant costumes, symmetrical compositions, use of wide shots, melancholic atmosphere
- **Editing：** Slow pacing, minimalist dialogue, focus on atmosphere and character emotions, subtle soundtrack

### 25. Lars von Trier — *Dancer in the Dark*
- **Visual：** Handheld camerawork, shaky frames, close-ups, subjective point-of-view, distorted imagery, experimental techniques
- **Editing：** Jump cuts, non-linear narrative, unsettling sequences, use of sound design to create tension

### 26. Kathryn Bigelow — *The Hurt Locker*
- **Visual：** Handheld camerawork, realistic portrayals of war, shaky close-ups, claustrophobic framing, long takes
- **Editing：** Fast-paced cuts, intense sequences, use of sound design to create immersion and tension

### 27. Jia Zhangke 賈樟柯 — *A Touch of Sin*
- **Visual：** Long takes, static camerawork, realistic portrayal of contemporary China, wide shots of landscapes, handheld sequences
- **Editing：** Slow pacing, observational approach, focus on social commentary, minimalist dialogue

### 28. Barry Jenkins — *Moonlight*
- **Visual：** Lush cinematography, intimate close-ups, vibrant colors, handheld camerawork, focus on characters' expressions
- **Editing：** Subtle cuts, lyrical pacing, evocative soundtrack, use of music to convey emotions

### 29. Apichatpong Weerasethakul 阿比查邦 — *Uncle Boonmee Who Can Recall His Past Lives*
- **Visual：** Long takes, dreamlike sequences, magical realism, surreal imagery, blending documentary and fiction
- **Editing：** Slow pacing, contemplative atmosphere, minimalist dialogue, focus on sound design

### 30. Michel Gondry — *Eternal Sunshine of the Spotless Mind*
- **Visual：** Creative use of special effects, innovative camerawork, playful visuals, dreamlike sequences, surreal imagery
- **Editing：** Fast-paced cuts, non-linear narrative, dynamic sequences, use of music and sound design to enhance storytelling

### 31. Panos Cosmatos — *Mandy*
- **Visual：** Dreamlike surrealism with meticulous symmetry, blending retro-futurism and religious iconography
- **Editing：** Slow-paced and jarring, juxtaposing reality and dreams for a disorienting atmosphere

---

## 🎯 用法範例

### Pattern A：直接用導演名（MJ / Sora 2 / Veo 3.1）

```
Cinematic portrait in the style of Wong Kar-wai — neon lights, slow-motion,
long takes, melancholic atmosphere. {SUBJECT} smoking by a phone booth at
night, rain-soaked street.
```

### Pattern B：抽 Visual Style token 嵌入（任何平台）

對 Flux / Nano Banana Pro / Seedance 用 token：

```
Lush color palettes, neon lights, slow-motion tracking shot, long take,
melancholic atmosphere. {SUBJECT} smoking by a phone booth at night, rain-
soaked street, dreamlike sequence with juxtaposition of past and present.
```

→ 沒提王家衛三個字，但每個 token 來自他的 visual signature。

### Pattern C：組合多個導演風格

```
The hyper-realistic CGI of Denis Villeneuve combined with the dark fantasy
aesthetic of Guillermo del Toro. {SUBJECT} stands at the edge of a colossal
ruined cathedral, atmospheric lighting, grotesque creatures lurking in
shadows, magical realism.
```

### Pattern D：類型對應導演速查

| 你要拍 | 用哪位導演的 style |
|---|---|
| 對稱 + 粉彩 + 童趣 | Wes Anderson |
| 史詩科幻 + 氛圍光 | Denis Villeneuve / Christopher Nolan |
| 神秘東方 + 慢動作 + 霓虹 | Wong Kar-wai |
| 戰爭手持寫實 | Kathryn Bigelow |
| 暗黑奇幻 + 魔幻寫實 | Guillermo del Toro |
| 動畫 + 夢幻 | Hayao Miyazaki / Michel Gondry |
| 詩意自然 + 慢長鏡 | Terrence Malick / Tarkovsky |
| 唯美暴力 + 神黑色 | Park Chan-wook |
| 階級對比 + 動態 | Bong Joon-ho |
| 紀錄寫實 + 手持 | Agnès Varda / Lars von Trier |
| 室內家庭 + 自然光 | Hirokazu Kore-eda |
| 大膽色彩 + 情緒 | Pedro Almodóvar / Spike Lee |
| 霓虹迷幻 + 反烏托邦 | Panos Cosmatos |
| 變形主觀 + 心理 | Darren Aronofsky / Lynne Ramsay |
| 玩心特效 + 夢境 | Michel Gondry |

---

## 📚 延伸學習

- 完整 source：[`xjpp22/awesome--sora-prompts`](https://github.com/xjpp22/awesome--sora-prompts)（每位導演附參考圖）
- 跨平台分流：[community-prompt-patterns.md §導演名分裂](community-prompt-patterns.md)
- 進階電影語彙：[cinematic-direction.md](cinematic-direction.md)
- 鏡頭語言基礎：[camera-language.md](camera-language.md)
