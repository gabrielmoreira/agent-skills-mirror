# Asset Library — 可重用角色卡 / 風格卡 / 場景卡

**定位：** 做過一次的角色、場景、風格組合，存成卡片。下次 auto-pilot 呼叫 `@角色名` 直接帶入，不用重寫視覺錨。

**使用方式：**
1. 使用者講「做個 Aya 咖啡師的早晨影片」→ auto-pilot 查本檔找 `@Aya-咖啡師` → 自動帶 3+ 視覺錨到 prompt
2. 使用者講「那個深夜鳥女孩換成海邊」→ `@深夜鳥-少女` + 新場景
3. 每次 demo 完的成功角色自動追加到本檔 (或由使用者指令明存)

---

## 🎭 角色卡 (Character Cards)

### @深夜鳥-少女 (Aya-夜貓版)
**首次出現：** 2026-04-18 OiiOii + Flow 深夜鳥系列
**視覺錨：**
- 16 歲少女
- 長黑髮，齊瀏海 (或兩邊分)
- 米色寬鬆開襟毛衣 (cream oversized cardigan)
- 內搭深色 T 恤
- 靦腆溫柔微笑
**配角：** 橘貓 (原 brief 為黑底白爪白胸斑，agent 解讀為橘貓)
**最佳平台：** Flow Veo 3.1 (生過兩版) / Kling I2V / Runway Gen-4 Refs
**English tokens：**
```
a 16-year-old girl with long black hair and bangs, wearing a cream oversized 
cardigan over a dark t-shirt, shy gentle smile
```

---

### @異世界-紅斗篷少女 (Liana)
**首次出現：** 2026-04-19 Flow Veo 3.1 + 2026-04-20 Kling 3.0 異世界
**視覺錨：**
- 14 歲少女
- 長黑髮
- **紅色斗篷 hooded cloak** (crimson-red)
- 米色皮製旅行裝 (cream leather traveling clothes)
- 背腰小皮袋
- 驚奇 + 溫柔不安表情
**經典場景：** 古老石雕拱門 + 發光 emerald runes + 魔法森林入口
**最佳平台：** Kling 3.0 Native Audio / Flow Veo 3.1 / Seedance multi-shot
**English tokens：**
```
a 14-year-old girl with long black hair, wearing a crimson-red hooded cloak 
over cream leather traveling clothes, small leather pouch at waist, wonder 
and quiet unease on her face
```

---

### @Aya-咖啡師
**首次出現：** 2026-04 storyboard.md 範例 (尚未實際生成)
**視覺錨：**
- 20 代後半女性
- 短黑髮俐落馬尾
- 白色立領襯衫 + 棕色圍裙
- 左手細銀戒
**經典場景：** 獨立咖啡店吧檯 + 黃銅咖啡機 + 晨霧窗
**最佳平台：** Seedance 1.0 Pro (multi-shot 故事)
**English tokens：**
```
a woman in her late 20s with short black hair in a low ponytail, wearing a 
crisp white collared shirt and brown apron, thin silver ring on left hand
```

---

### @Chef-Lin (Neon Dumpling Shop IP)
**首次出現：** 2026-04 oiioii.md 範例 (尚未實際生成)
**視覺錨：**
- 40 代男性
- 白色廚師服
- 左眉疤
- 嘴裡常叼電子菸
**經典場景：** Cyberpunk Taipei 夜市、蒸籠、紅燈籠
**最佳平台：** OiiOii Story Video / Kling 武俠感 / Seedance
**English tokens：**
```
Chef Lin, middle-aged man, white chef coat, scar on left brow, 
digital cigarette in mouth
```

---

### @神秘客 (Mysterious Customer)
**首次出現：** 2026-04 oiioii.md 範例
**視覺錨：**
- 高個子、黑色 trench coat
- 大簷帽遮住臉
- 琥珀色發光雙眼
**English tokens：**
```
tall figure in a black trench coat, face hidden under a wide-brim hat, 
glowing amber eyes
```

---

### @Noir-Detective (賽博龐克偵探)
**首次出現：** 2026-04 iteration-2 benchmark 範例
**視覺錨：**
- 30 代疲憊男
- 米色/灰風衣 (trench coat)
- 鬍渣
- 叼菸
**經典場景：** 雨夜便利店、霓虹街巷、鈉蒸氣街燈
**最佳平台：** Kling 2.6 Pro / 3.0 Noir prompts / Runway Gen-4
**English tokens：**
```
a weary male detective in his 30s, damp charcoal-grey trench coat, 
stubble, tired eyes lit by a dying cigarette ember
```

---

## 🎨 風格卡 (Style Cards)

### @Shinkai-Ghibli-Blend
**場景適用：** 動漫異世界 / 校園青春 / 療癒日常
**Style token：**
```
Makoto Shinkai cinematic anime blended with Studio Ghibli hand-painted 
backgrounds, Hoyte van Hoytema warm-cool contrast, Kodak Vision3 500T 
emulation, volumetric god rays piercing the canopy, 16:9 widescreen
```
**配套 SFX：** 風吹樹葉、鳥鳴、遠處環境、少女的呼吸
**配套 Soundtrack：** Joe Hisaishi-inspired Ghibli orchestral, gentle solo piano

### @BladeRunner-2049-Noir
**場景適用：** 賽博龐克偵探 / 未來城市夜景
**Style token：**
```
shot by Roger Deakins, Panavision C-Series anamorphic 50mm at T2.0, 
Arri Alexa LF, Cinestill 800T emulation with heavy red halation around 
every light source, teal shadows crushed deep, sodium-amber highlights, 
magenta-cyan neon rim, 2.39:1 anamorphic horizontal flares, volumetric 
atmospheric haze
```

### @WongKarWai-HK-Noir
**場景適用：** HK 90s 懷舊 / 慢動作步態 / 紅綠色彩碰撞
**Style token：**
```
Wong Kar-wai style, Christopher Doyle handheld cinematography, 
stepped-frame slow motion at 48fps printed to 24fps, Fuji 8mm film grain, 
saturated red and emerald color collision, In the Mood for Love palette
```

### @Apple-Product-Hero
**場景適用：** 科技產品廣告 / 靜物極簡
**Style token：**
```
Apple product commercial aesthetic, pure white cyclorama infinity background, 
100mm macro at f/8 focus stacked, Phase One IQ4 150MP, cool 5600K lighting, 
seamless gradient, zero grain, zero imperfection
```

### @Nike-Heroic-Sport
**場景適用：** 運動廣告 / 英雄鏡 / 汗珠慢動作
**Style token：**
```
Nike commercial heroic aesthetic, 200fps Phantom Flex 4K slow motion, 
low-angle hero shot, sweat droplets frozen mid-air, bleach bypass crushed 
blacks, stadium arc lamp rim light, saturated brand red gel
```

### @A24-Indie-Naturalism
**場景適用：** 文青獨立 / 冷靜敘事 / 真實不美化
**Style token：**
```
A24 indie film aesthetic, naturalistic unglamorous cinematography, handheld 
subtle shake, 35mm film grain, Kodak Vision3 500T, available natural light 
only, slight green color cast, real skin texture no beauty retouching
```

---

## 🎵 Suno 聲線/風格卡 (Persona / Style Cards)

> 把每首生成過的歌存成可重用 Persona — 下次只換 lyrics，style 自動繼承，省 5 倍 type 量。
> 完整 SOP 見 [site-profiles/suno.md §6 Speed Optimization](../automation/site-profiles/suno.md)

### @Suno-雨夜便利店燈 (Lo-Fi Mandarin Sentimental)
**首次生成：** 2026-04-20 Suno v4.5-all (4:11 + 3:48)
**Style token：**
```
Lo-fi Mandarin sentimental ballad in C major, 72 BPM, Rhodes MK II electric piano
through tape saturation, fingerpicked nylon-string guitar, brushed kit ghost snares,
side-chained warm pads, female vocal close-mic intimate breath, vinyl crackle 
ambience, late-night convenience store atmosphere, 70s soft city pop production
```
**配套主題：** 雨夜、便利店、孤單溫柔、城市寂寞
**重用方式：** Suno → Persona → 換 lyrics 即可

### @Suno-公車站牌 (Smooth Acoustic Mandarin)
**首次生成：** 2026-04-20 Suno v4.5-all (4:07)
**Style token：**
```
Smooth acoustic Mandarin folk-pop in D major, 78 BPM, fingerpicked steel-string 
guitar, Wurlitzer 200A electric piano, brushed jazz kit, walking upright bass,
warm female vocal with subtle vibrato, autumn afternoon golden hour atmosphere,
70s Taiwanese folk revival production
```
**配套主題：** 等待、午後、淡淡感傷、回憶
**重用方式：** 換 lyrics 寫不同等待主題

### @Suno-札幌白線 (Indie Mandarin Winter Ballad)
**首次生成：** 2026-04-20 Suno v4.5-all (4:23 + 4:19)
**Style token：**
```
Indie Mandarin winter ballad in A minor, 68 BPM, glassy felted piano, 
ambient pad textures, gentle brushed kit, sub-bass low end, female vocal 
ethereal close-mic, snow-covered Hokkaido aesthetic, Sigur Rós-inspired 
post-rock build, cinematic crescendo
```
**配套主題：** 冬天、雪、思念、距離
**重用方式：** 適合所有冬季 / 北方 / 距離主題

### @Suno-第三杯咖啡 (Smooth Jazz Mandarin Ballad)
**首次生成：** 2026-04-20 Suno v4.5-all (4:24 + 3:29)
**Style token：**
```
Smooth jazz Mandarin pop ballad in G major, 84 BPM, intimate Hammond B3 organ,
brushed jazz kit, walking upright bass, muted trumpet solos, female vocal 
sultry close-mic, late-night jazz cafe atmosphere, Diana Krall-inspired 
production, smoky room ambience
```
**配套主題：** 咖啡、深夜、爵士、成熟思考
**重用方式：** 適合所有 jazz / cafe / 沉思主題

### @Suno-廚房的歌 (Warm Mandarin Folk-Pop)
**首次生成：** 2026-04-20 Suno v4.5-all
**Style token：**
```
Warm Mandarin folk-pop in F major, 96 BPM, fingerpicked acoustic guitar,
ukulele, soft handclaps, glockenspiel sparkles, accordion warmth, female 
vocal bright cheerful, kitchen warmth atmosphere, 70s Taiwanese sunshine 
pop production
```
**配套主題：** 家、廚房、日常、溫暖
**重用方式：** 適合所有 home / family / 日常溫馨主題

---

## 🌍 場景卡 (Scene Cards)

### @Taipei-夜市-Cyberpunk
**核心元素：**
- 霓虹招牌 (magenta / cyan)
- 蒸籠冒出水蒸氣
- 濕漉街面反射
- 掛滿紅燈籠
- 繁體中文 / 台語招牌
- 電動機車

### @魔法森林-石門入口
**核心元素：**
- 古老石雕拱門
- 發光 emerald 符文
- 體積光 god rays 穿透樹冠
- 漂浮魔法粒子 (fireflies / dust motes)
- 深綠苔蘚 + 暖金陽光

### @深夜街角-自動販賣機
**核心元素：**
- 空無一人街道
- 暖橘色路燈
- 藍綠色螢光販賣機
- 濕漉地面落葉
- 晨霧 / 輕雨

### @停車場-便利店-雨夜
**核心元素：**
- 24 小時便利店
- 鈉蒸氣街燈 (橘色)
- 霓虹招牌 (pink/cyan)
- 鋪滿水的柏油地
- 孤單單人

### @竹林-晨霧
**核心元素：**
- 密集竹林
- 晨霧流動
- 穿過竹葉的金光
- 落葉飄動

---

## 如何追加到本檔

使用者示意：「把剛剛那個角色存起來」「存這個風格」`→` 我把當次用的 prompt + 視覺錨 + 經典場景整理成新卡片加進對應 section。

Auto-Pilot 在 Stage 1 Intent Parser 時，若使用者提到 `@角色名` 或「那個 X 角色」，立刻來本檔查，**直接帶 English tokens 進 prompt**，不用重組。
