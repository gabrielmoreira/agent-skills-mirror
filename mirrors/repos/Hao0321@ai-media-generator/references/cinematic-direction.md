# 電影導演 / 攝影指導級別的 Prompt 設計

**定位：** 當使用者要的是「電影感」、「好萊塢級」、「奢侈品級」的畫面時，這份檔案是 prompt 的頂級語彙庫。核心觀念：**AI 模型對電影工業術語有極高的敏感度**，因為訓練資料含大量影人訪談、IMDB、Letterboxd、電影拉片、DP 幕後花絮。

## 核心方法：Meta Token Stack 四層結構

要超越「AI 感」、讓畫面像真正的電影，用這個四層：

```
[導演/風格簽名] + [攝影指導 (DP) 簽名] + [底片/感光元件] + [鏡頭/焦段/光圈]
+ [燈光設計] + [色彩分級] + [構圖規則] + [動作/景別]
```

**範例 (Blade Runner 2049 致敬)：**
```
Shot by Roger Deakins, cinematic 2.39:1 anamorphic, shot on Alexa LF with
Panavision anamorphic lenses, Kodak Vision3 250D emulation, high contrast
teal-and-orange grade with saturated magenta practicals, volumetric neon
haze, low-angle hero shot of a man in a trench coat walking through a rain-
soaked alley, practical neon signs bokeh, shallow depth of field, slow
dolly-in tracking.
```

**反例 (AI 感重)：**
```
a cool cinematic scene, beautiful, high detail, 8k, masterpiece, realistic
```

AI 模型看前者會觸發成千上萬個「Deakins + Alexa + anamorphic」訓練樣本；看後者只會觸發「generic beauty」。

---

## Part 1 — 導演簽名 (Director Signatures)

把導演名當成「風格套件」。每個導演是一個打包好的美感權重。

### 英美/國際敘事片

| 導演 | 簽名風格 | 高訊號 prompt token |
|---|---|---|
| **Wes Anderson** | 對稱、粉彩、中景定格、whip pan、snap zoom、書籍式構圖 | `Wes Anderson style, symmetrical composition, pastel palette, centered subject, flat tableau, whimsical diorama, Futura font signage` |
| **Christopher Nolan** | IMAX 寬幅、70mm、低視角英雄鏡、陡峭建築感 | `Nolan-inspired IMAX wide field of view, 70mm anamorphic, practical explosions, desaturated cool palette, low-angle architectural hero shot` |
| **Denis Villeneuve** | 紀念碑式建築、極簡色塊、沙漠/外星感、靜物感 | `Villeneuve monumental scale, brutalist architecture, desaturated ochre and steel palette, lone figure in vast landscape, cathedral-like space` |
| **David Fincher** | 冷調精確、水銀質感、恐怖的靜止、打磨感 | `Fincher cold precision, desaturated greens and amber lows, 85mm close-up, surgical framing, locked-off camera, mercurial skin tones` |
| **Stanley Kubrick** | 單點透視、對稱、tracking 穩定、怪誕建築 | `Kubrick one-point perspective, wide-angle 18mm symmetrical hallway, Steadicam tracking, stark institutional architecture, uncanny stillness` |
| **Paul Thomas Anderson** | 70mm 人物史詩、自然風長鏡頭、溫暖黃調 | `PTA 70mm cinematography, humanist mid-shot, warm amber grade, steadicam tracking shot following a character, long unbroken take` |
| **Terrence Malick** | 自然光詩意、仰拍天空、低機位麥田、Lubezki 長鏡 | `Malick ethereal naturalism, golden hour low angle with sun flare, Steadicam drifting through tall grass, whispered narration feel` |
| **Coen Brothers** | 平衡構圖、冷峻黑色幽默、復古美國中西部 | `Coens deadpan framing, medium locked shot, period Americana, desaturated ochre and grey, dry humor stillness` |
| **Quentin Tarantino** | 高飽和、trunk shot、低角度、footage-stock 混搭 | `Tarantino stylized saturation, trunk shot low angle from a car interior, grindhouse grain, stylized gore, retro 70s title cards` |
| **Martin Scorsese** | 手持運鏡、freeze frame、古典 oneshot、宗教感 | `Scorsese dynamic handheld, steadicam tracking through a crowd, long oner, warm tungsten practicals, period New York` |
| **Alfonso Cuarón** | Lubezki 自然光 + 長鏡頭、手持沉浸 | `Cuarón Lubezki-photographed, handheld single take, Steadicam immersion, natural daylight through clouds` |
| **Steven Spielberg** | 鏡頭運動揭示、超廣角反應鏡、中心構圖 | `Spielberg dolly-in reveal, wide-angle reaction close-up on face looking up in awe, warm amber light from off-screen source` |
| **Alejandro González Iñárritu** | Lubezki 長鏡、自然光、原生感 | `Iñárritu long unbroken take, handheld Steadicam, available light only, 360° rotation around subject` |

### 歐陸 / 藝術片

| 導演 | 簽名風格 | 高訊號 token |
|---|---|---|
| **Andrei Tarkovsky** | 超慢運鏡、水與鏡面、沉思感、4:3 | `Tarkovsky contemplative slowness, long static take, 4:3 academy ratio, rain on windowsill, mossy texture, weathered interior` |
| **Béla Tarr** | 黑白 + 無盡長鏡、雨與泥濘 | `Béla Tarr black and white, 10-minute unbroken take, rain and mud, eastern European gloom, handheld tracking` |
| **Lars von Trier** | Dogme 手持、自然光、粗糙質感 | `von Trier Dogme 95 handheld, available light, handheld shake, raw unprocessed skin, jump cut feel` |
| **Yorgos Lanthimos** | 魚眼廣角、對稱、怪異疏離、淺綠金調 | `Lanthimos fisheye 4mm wide, symmetrical composition, cold awkward distance, pale green and gold palette, expressionless performers` |
| **Michael Haneke** | 靜止長鏡、中景、冷酷中產階級 | `Haneke locked-off medium static shot, unflinching duration, sterile bourgeois interior, no score` |
| **Luca Guadagnino** | 肉感自然光、夏日皮膚、35mm、義大利感 | `Guadagnino sensual naturalism, 35mm film, sun-drenched Italian villa, warm skin tones, intimate proximity` |
| **Jane Campion** | 女性凝視、自然潮濕、質地、直視 | `Campion tactile naturalism, mist and wet earth, 35mm, intimate close-up, ambient diffused daylight` |

### 亞洲

| 導演 | 簽名風格 | 高訊號 token |
|---|---|---|
| **Wong Kar-wai (王家衛)** | 霓虹、慢動作、步態、紅綠對撞、Christopher Doyle 攝影 | `Wong Kar-wai style, Christopher Doyle cinematography, stepped-frame slow motion, neon-drenched alley, red and green palette collision, longing close-ups` |
| **Akira Kurosawa (黑澤明)** | 多機位、雨中武士、仰拍旗幟、Toshiro Mifune 特寫 | `Kurosawa wuxia / samurai epic, low-angle wide, telephoto compression, rain and wind-blown banners, multi-camera coverage feel` |
| **Yasujirō Ozu (小津安二郎)** | Tatami 低機位、90° 直視、四季日本 | `Ozu tatami-mat low angle shot, direct-to-camera 90°, balanced domestic tableau, seasonal Japan` |
| **Zhang Yimou (張藝謀)** | 強烈色塊、千人陣列、紅燈籠、武俠美術 | `Zhang Yimou saturated color block, mass choreography, red lanterns, wuxia bamboo forest, silk and symmetry` |
| **Hou Hsiao-hsien (侯孝賢)** | 靜止遠景、台語鄉土、光斑穿過 | `Hou Hsiao-hsien static long shot, distant observation, 1960s Taiwan nostalgia, sunlight through wooden shutters` |
| **Bong Joon-ho (奉俊昊)** | 類型混搭、社會縱深、垂直空間 | `Bong Joon-ho vertical class contrast, genre hybrid, cold rain on glass, dark and warm palette split` |
| **Park Chan-wook (朴贊郁)** | 華麗對稱、維多利亞美學、報復敘事 | `Park Chan-wook ornate symmetry, Victorian maximalism, baroque color, slow reveal camera` |
| **Hayao Miyazaki (宮崎駿)** | Studio Ghibli、自然奇幻、水彩背景 | `Studio Ghibli hand-painted watercolor backgrounds, soft pastoral fantasy, lush wind through tall grass, cel-shaded character` |
| **Makoto Shinkai (新海誠)** | 現代日系、光暈、城市 + 星空、感傷 | `Makoto Shinkai anime, volumetric god rays, hyper-detailed urban landscape, lens flare, bittersweet dusk sky` |
| **Satoshi Kon (今敏)** | 夢境蒙太奇、現實崩塌、精神病美學 | `Satoshi Kon fractured reality edit, match cut between realities, paranoid urban Tokyo` |

---

## Part 2 — 攝影指導 (DP) 簽名

**DP 比導演更技術化，寫進 prompt 通常拉高「工業等級」訊號**。

| DP | 簽名手法 | Prompt token |
|---|---|---|
| **Roger Deakins** (Blade Runner 2049, 1917, No Country) | 主體光溢出 1-2 檔、背景反向打光、anamorphic bokeh、練習光 (practicals) | `Roger Deakins cinematography, overexposed key on subject's lit side, backlit separation, Panavision anamorphic, practical lamps, 2.39:1` |
| **Emmanuel Lubezki** (Birdman, Revenant, Tree of Life) | 自然光大師、Steadicam 長鏡、廣角沉浸 | `Lubezki natural light only, handheld Steadicam long take, 14mm Zeiss Master wide, available light, 360° rotation` |
| **Hoyte van Hoytema** (Oppenheimer, Dunkirk, Her) | IMAX 寬幅、淺景深隔離主體、最少背光 | `Hoyte van Hoytema IMAX 70mm, wide shot with shallow depth of field isolating subject, minimal backlight, Kodak Vision3 500T` |
| **Greig Fraser** (Dune, Batman, Rogue One) | 低對比、沙與塵的顆粒、暖金打底 | `Greig Fraser atmospheric grain, low contrast warm amber base, dust motes, practical fire glow, Alexa 65 large format` |
| **James Friend** (All Quiet on the Western Front) | 泥濘戰場、陰鬱天空、無英雄感 | `James Friend war realism, muddy trenches, overcast diffused sky, desaturated mud and grey, handheld unflinching` |
| **Rachel Morrison** (Mudbound) | 自然感女性凝視、質地優先 | `Rachel Morrison humanist naturalism, tactile skin texture, sunlight through dust, soft golden hour` |
| **Christopher Doyle** (Wong Kar-wai films) | 手持顫動、霓虹、stepped frame、過飽和 | `Christopher Doyle handheld energy, oversaturated reds and greens, stepped-frame slow motion, neon reflection in rain` |
| **Darius Khondji** (Seven, Amour, Midnight in Paris) | 低鑰照明、暖膠片、歐陸暗房感 | `Darius Khondji low-key darkroom warmth, ENR bleach bypass, Kodak Vision3 250D, practical tungsten` |
| **Bradford Young** (Arrival, Selma) | 低曝光黑膚色細節、氛圍灰藍 | `Bradford Young low-light Black skin tone rendering, misty blue-grey, underexposed cinematic` |
| **Robbie Ryan** (The Favourite, Poor Things) | 魚眼 + 復古鏡、自然光、戲謔 | `Robbie Ryan vintage Zeiss lenses, fisheye wide, candlelit interiors, Lanthimos collaboration` |
| **Matthew Libatique** (Requiem, Black Swan) | Dutch angle、鏡面分身、手持癲狂 | `Libatique Dutch angle, mirror doubling, handheld frenetic, saturated split lighting` |

---

## Part 3 — 鏡頭焦段與情緒對應

每個焦段是一種「敘事語氣」。

| 焦段 | 字面效果 | 情緒/用途 | Prompt token |
|---|---|---|---|
| **14mm / 18mm** (超廣角) | 極度變形、吞沒空間 | 不安、迷失、恐懼、奇幻尺度 | `shot on 14mm ultra-wide, slight barrel distortion, immersive space` |
| **24mm** (廣角) | 寬闊、輕微變形 | 環境建立、空間感 | `24mm environmental wide, subtle wide-angle energy` |
| **35mm** (人文標準) | 像人眼稍寬、穩 | 人物 + 環境並重、紀實感 | `35mm classic humanist lens, Seven Samurai feel` |
| **50mm** (標準) | 最接近人眼 | 寫實、對話戲、自然 | `50mm normal lens, natural perspective, eye-level` |
| **85mm** (肖像) | 空間壓縮、柔散景 | 人物情感、肖像感、浪漫 | `85mm portrait lens, shallow depth of field, creamy bokeh` |
| **135mm / 200mm** (望遠) | 極度壓縮、分離主體 | 偷窺感、孤立、巨大尺度 | `200mm telephoto compression, subject isolated against background` |
| **Anamorphic 40-50mm** | 寬銀幕、橢圓散景、水平條光斑 | 電影感招牌 | `Panavision anamorphic 50mm, oval bokeh, horizontal lens flares, 2.39:1` |
| **Macro (100mm macro)** | 極近、景深極淺 | 細節、蟲、手、水滴 | `100mm macro, 1:1 reproduction, extreme shallow DoF` |
| **Fisheye (8-15mm)** | 魚眼曲變 | 極端主觀、怪誕 | `8mm fisheye, extreme barrel distortion` |
| **Tilt-shift** | 選擇性模糊 | 小人國感、微縮 | `tilt-shift miniature effect, selective focus` |

---

## Part 4 — 燈光設計進階

燈光是電影畫面的 **90% 氛圍**。Prompt 寫清楚燈光，成品品質直接跳一個等級。

### 經典肖像光

| 類型 | 說明 | Prompt token |
|---|---|---|
| **Rembrandt** | 主光 45°，鼻下三角形光 | `Rembrandt lighting, triangle of light on shadowed cheek, 45° key light, dramatic classical portrait` |
| **Split (分光)** | 主光 90°，臉一半亮一半暗 | `split lighting, half-face in shadow, film noir drama` |
| **Loop (環光)** | 主光稍偏，鼻下小陰影 | `loop lighting, slight nose shadow on cheek, natural portrait` |
| **Butterfly (蝴蝶光)** | 主光正上方，下巴蝴蝶陰影 | `butterfly lighting, nose shadow centered below, glamour portrait` |
| **Clamshell** | 上下兩盞柔光，無陰影 | `clamshell beauty lighting, top and bottom soft box, beauty campaign` |
| **Broad** | 對相機近的那面亮 | `broad lighting, key on camera-side face, welcoming feel` |
| **Short** | 對相機近的那面暗 | `short lighting, key on away-side face, slimming, introspective` |

### 風格化燈光

| 類型 | 說明 | Prompt token |
|---|---|---|
| **Chiaroscuro** | 極端明暗對比、油畫感 | `chiaroscuro, extreme light-dark contrast, deep black shadows, luminous highlights, Caravaggio painting lighting` |
| **Low-key** | 主要是暗，僅少許亮部 | `low-key lighting, dominant shadows, single source accent` |
| **High-key** | 主要是亮，極少陰影 | `high-key lighting, bright even fill, fashion editorial` |
| **Volumetric** | 可見光束、霧中光、耶穌光 | `volumetric lighting, visible god rays, atmospheric haze, light beams through fog` |
| **Neon / Practical only** | 場景內實光 | `practical lights only, neon signs, tungsten bulbs, no studio lighting` |
| **Hard light / 硬光** | 銳利陰影、直射 | `hard direct sunlight, sharp shadows, high contrast` |
| **Soft light / 柔光** | 擴散、羽化陰影 | `soft diffused light, feathered shadows, overcast sky` |
| **Mixed color temperature** | 冷暖對撞 | `mixed color temperature, warm tungsten practicals vs cool blue daylight through window` |

### 時段光

| 時段 | Prompt token |
|---|---|
| Golden hour | `golden hour low-angle sun, warm amber backlight, rim light on subject` |
| Blue hour | `blue hour twilight, deep indigo sky, practical amber lamps lit` |
| Magic hour | `magic hour transition, purple and orange gradient sky, silhouette` |
| Pre-dawn | `pre-dawn diffused grey light, misty, no direct sun yet` |
| Harsh noon | `harsh noon overhead sun, hard shadows under brow and chin` |
| Overcast | `overcast diffused daylight, even soft shadows, cool cloudy mood` |
| Night (practical) | `night scene lit only by practicals, sodium vapor street lamps` |
| Night (moonlight) | `moonlit night, cool blue fill, soft top light` |

### 光比 / Contrast Ratio

Prompt 寫 `2:1 ratio` (柔) 到 `8:1` (戲劇) — 高階模型懂這個：

- `low contrast 2:1 key-to-fill` — 柔和
- `moderate 4:1 contrast` — 標準戲劇片
- `high 8:1 contrast` — noir
- `extreme 16:1 contrast` — chiaroscuro

---

## Part 5 — 底片模擬與色彩分級

**勝過一切「cinematic, 8k」的法寶**。AI 模型對底片 stock 極敏感。

### 電影底片 (Motion Picture Stocks)

| 底片 | 特性 | 用途 | Prompt token |
|---|---|---|---|
| **Kodak Vision3 500T** | 鎢絲/室內、壓 2 檔還可用、皮膚暖、顆粒優秀 | 夜戲、室內、低光 | `shot on Kodak Vision3 500T, warm skin tones, fine grain holding under push` |
| **Kodak Vision3 250D** | 日光、細顆粒、對比適中 | 日間外景 | `Kodak Vision3 250D daylight negative, clean mid-tones, cinematic daylight` |
| **Kodak Vision3 200T** | 鎢絲、比 500T 更乾淨 | 控光室內 | `Kodak Vision3 200T, clean warm tungsten, fine grain` |
| **Kodak Vision3 50D** | 超高解析 | 廣告 / 陽光下 | `Kodak Vision3 50D ultra-fine grain, sunny exterior` |
| **Fuji Eterna 500T** | 冷調柔和、歐陸感 | 歐洲 indie | `Fuji Eterna 500T, muted pastel skin, cool European indie feel` |
| **Fuji 400H** | 偏綠、柔、明亮 | 婚禮、日系 | `Fuji 400H pastel greens, bright feminine feel` |
| **Ektachrome (100D)** | 正片、鮮、crisp | 國家地理感 | `Ektachrome slide film, crisp saturated colors, National Geographic feel` |
| **Kodachrome 64** | 1970s 懷舊、深紅 | 復古家庭 | `Kodachrome 64, faded warm reds, 1970s nostalgia` |
| **Cinestill 800T** | 紅光溢出 (halation)、夜霓虹招牌 | 夜景賽博龐克 | `Cinestill 800T red halation around light sources, neon night` |
| **Ilford HP5** | 黑白、經典報導 | 紀實黑白 | `shot on Ilford HP5 black and white, gritty documentary grain` |

### 色彩分級 (Color Grade)

| 分級 | Prompt token |
|---|---|
| **Teal and Orange** | `teal and orange grade, cyan shadows, amber highlights, Hollywood blockbuster look` |
| **Bleach Bypass / ENR** | `bleach bypass high contrast desaturated, silver retention, Saving Private Ryan feel` |
| **Muted Earth Tones** | `muted earth tones, desaturated ochre and olive, European indie` |
| **High Key Bright** | `high-key bright, crushed whites, bright fashion editorial` |
| **Film Noir B&W** | `film noir high contrast black and white, venetian blind shadows` |
| **Pastel Wes Anderson** | `pastel Wes Anderson palette, muted pinks and yellows, powder blue` |
| **Neon Cyberpunk** | `neon cyberpunk magenta and cyan, Blade Runner 2049 grade` |
| **Hollywood Contemporary** | `modern Hollywood drama grade, natural skin, deep teal lows, warm highs` |
| **A24 Indie** | `A24 indie film grade, naturalistic, slight green shift, unglamorous` |
| **Giallo** | `Italian giallo vivid red and blue gel lights, Argento-inspired` |

**重要規則 (來自 film stock 實測)：**
1. **用具體 stock 名，不要用 "vintage"** — `Kodak Vision3 500T` > `vintage film look`
2. **不要疊太多 stock** — `Kodak Vision3, Fuji, vintage, cinematic` = 模糊結果。**選一個 stock + 1-2 個配合詞**
3. **配合動作詞防顆粒 smear** — 靜態或 `slow dolly`，避免快速搖晃稀釋顆粒

---

## Part 6 — 構圖進階規則

| 規則 | 用途 | Prompt token |
|---|---|---|
| **Rule of thirds** | 主體放三分線交點 | `rule of thirds composition, subject on right third line` |
| **Golden ratio / Fibonacci** | 自然螺旋構圖 | `golden ratio composition, spiral leading to subject` |
| **Leading lines** | 線條引導視線 | `leading lines converging to subject, railway tracks pulling eye` |
| **Framing within frame** | 門/窗/拱/樹框 | `framed within a doorway, archway framing the subject, layered foreground` |
| **Symmetry** | 中心對稱 | `perfect vertical symmetry, mirror composition, Kubrick central frame` |
| **Negative space** | 大量留白 | `negative space composition, subject offset lower-right, 70% empty sky` |
| **Triangular** | 三角形 | `triangular composition, three subjects forming a stable triangle` |
| **Dutch angle** | 斜線不安 | `Dutch angle canted frame, 15° tilt, unease` |
| **Layered depth** | 前中後景 | `layered depth, foreground out-of-focus leaves, mid-ground subject, blurred background` |
| **OTS** (over-the-shoulder) | 對話戲 | `over-the-shoulder shot, subject 1 blurred in foreground, subject 2 in focus` |

---

## Part 7 — Meta Token Stack (高寫實度技巧)

**用檔名 + EXIF + 相機型號堆疊，讓 AI 輸出像真實拍攝**。

### iPhone 日常感
```
IMG_2985.HEIC, iPhone 15 Pro, f/1.78, 24mm equivalent, shot handheld at
dusk, ISO 800, slight motion blur, no filter, unposed
```

### 專業 DSLR/Mirrorless
```
Canon EOS R5 raw, RF 50mm f/1.2L at f/2.0, ISO 400, 1/200s, natural window
light, Kodak Portra 400 emulation, no post processing
```

### 電影機
```
Arri Alexa LF, Panavision Ultra Vista anamorphic 50mm, T2.8, Log C3, Kodak
Vision3 500T emulation, 23.976fps, 180° shutter
```

### 中片幅 (Fashion editorial)
```
Phase One XF IQ4 150MP, Schneider 80mm f/2.8, natural daylight, Capture One
neutral profile, fashion editorial, no retouching
```

### 底片掃描感
```
Mamiya 7 II, 80mm f/4, Kodak Portra 400 120 medium format film, Noritsu
scan, light leak on edge, soft halation
```

### 紀錄片手持
```
Sony FX3, 24-70mm f/2.8 at f/4, ISO 3200, handheld, S-Log3, available light,
documentary run-and-gun
```

---

## Part 8 — 時代與地域風格

| 風格 | 特徵 | Prompt token |
|---|---|---|
| **French New Wave (1960s)** | Godard, 黑白, handheld, jump cuts | `French New Wave black and white, 35mm handheld, Godard jump cut feel` |
| **Italian Neorealism** | 1940-50s 街頭、非職業演員 | `Italian neorealism, street-level 1940s Rome, unglamorous documentary feel` |
| **70s American New Hollywood** | 粗糙膠片、zoom、自然光 | `1970s New Hollywood grit, zoom lens, Kodak 5254 grain, Taxi Driver feel` |
| **80s Synthwave** | 霓虹、magenta + cyan、VHS | `1980s synthwave aesthetic, neon magenta and cyan, VHS fuzz, chrome sunset` |
| **Hong Kong Noir (90s)** | Wong Kar-wai、粵語黑幫、霓虹 | `1990s Hong Kong noir, Christopher Doyle handheld, rainy Kowloon alleys` |
| **Dogme 95** | 手持、自然光、無配樂 | `Dogme 95 stripped-down naturalism, handheld, available light, no score` |
| **K-drama 2020s** | 柔焦、暖調、韓式情感 | `K-drama modern palette, soft warm skin tones, Seoul nightscape bokeh` |
| **Anime cel-shaded** | 賽璐珞、硬線、Ghibli/Shinkai | `cel-shaded anime, hand-painted backgrounds, Studio Ghibli texture` |
| **Grindhouse 70s** | 膠片刮痕、饱和紅、暴力 | `1970s grindhouse print damage, scratches and cigarette burns, blown-out reds` |

---

## Part 9 — VFX 與特效詞彙

| 類型 | Prompt token |
|---|---|
| **Practical effects** | `practical in-camera effects, real fire and smoke, no CGI, analog` |
| **Compositing seam** | `seamless digital compositing, multiple plates, matte painting background` |
| **Matte painting** | `digital matte painting background, 2.5D parallax, epic landscape` |
| **Particles dust** | `atmospheric dust particles catching light, practical haze` |
| **Particles rain** | `heavy practical rain, backlit rain streaks, reflected puddles` |
| **Snow** | `gentle falling snow, practical snow machine, subtle accumulation` |
| **Fog / Mist** | `low-lying mist, knee-height fog, atmospheric depth` |
| **Lens flare** | `anamorphic horizontal lens flare, J.J. Abrams flare, controlled not excessive` |
| **Halation** | `Cinestill 800T red halation around practicals` |
| **Smoke** | `heavy atmospheric smoke, volumetric light interacting with haze` |
| **Fire** | `practical fire, warm orange flicker on subject, dancing shadows` |
| **Water splash** | `high-speed practical water splash, frozen droplets` |
| **Cloth simulation** | `realistic cloth simulation, wind-blown silk with natural drape` |
| **Hair dynamics** | `hair flowing naturally in wind, individual strand physics` |
| **Debris** | `debris particles falling, scale dust and small chunks` |
| **Explosion** | `practical explosion, Nolan-style real pyrotechnics, not CGI` |
| **Motion blur** | `natural motion blur from 180° shutter` |
| **Freeze frame** | `freeze frame moment, crystallized mid-motion` |
| **Time lapse** | `time lapse, star trails, clouds streaking across sky` |
| **Slow motion** | `120fps Phantom slow motion, water droplets suspended` |

---

## Part 10 — 從概念到 Prompt 的案例工作流

**案例：「雨夜、一個偵探在便利商店外抽菸等人」**

### ❌ 弱 Prompt
```
a detective smoking outside a convenience store at night, cinematic, 8k
```
→ AI 感重、一般。

### ⚠️ 中等 Prompt
```
A detective in a trench coat smoking a cigarette outside a convenience
store at night, rain, neon signs, cinematic lighting, shallow depth of
field, moody atmosphere
```
→ OK 但沒特色。

### ✅ 頂級 Prompt (用本檔的語彙庫)
```
Medium close-up on a weary male detective in a damp trench coat smoking a
cigarette outside a 24-hour convenience store at 3 AM. Shot by Roger Deakins,
Panavision anamorphic 50mm at T2.0, Kodak Vision3 500T, slight halation
around the store's magenta and cyan neon signage. Low-key 4:1 contrast,
practical fluorescent fill from the storefront, backlit by distant street
lamps through light rain, visible volumetric haze. Teal shadows and sodium-
amber highlights. 2.39:1 aspect. Rain streaks on the trench coat, his
breath visible. Cigarette ember as only warm point source on face.
```

### 完整 token 解構
| 層 | 選項 | 用意 |
|---|---|---|
| DP | Roger Deakins | 招牌偵探片美學 |
| 相機/鏡頭 | Alexa LF + Panavision 50mm T2.0 | 電影工業級 |
| 底片 | Kodak Vision3 500T + halation | 夜戲經典 |
| 比例 | 2.39:1 anamorphic | 寬銀幕電影感 |
| 光比 | 4:1 low-key | Noir 戲劇 |
| 光源 | practical fluorescent + backlit street + 煙頭 | 多層次照明 |
| 色彩 | teal shadows + sodium amber | 2026 經典配色 |
| 氛圍 | volumetric haze + rain streaks + breath | 物理細節 |
| 景別 | medium close-up | 情緒優先 |

---

## 使用哲學

- **不要疊太多** — 上述是「語彙庫」，每次 prompt 挑 **5-8 個高質量 token** 即可。過度疊加反而稀釋。
- **對齊故事** — Wes Anderson 語彙不該放在武俠片裡。選符合故事調性的 bundle。
- **實驗 → 固定** — 生成 3-5 版對比，找出哪些 token 真的影響輸出，把有效的記錄成自己的「風格 preset」。
- **跨平台有效** — Kling / Sora / Veo 對電影 token 都敏感；Seedream / Midjourney 對導演/DP 名尤其敏感。

## 連結

- [Metricsmule AI Filmmaking Prompts](https://metricsmule.com/ai/ai-filmmaking-prompts/)
- [Director's Guide to AI Video (GitHub)](https://gist.github.com/Dowwie/b1015e1c3b4bffedd1cfc76e45c7da96)
- [Wes Anderson Midjourney Library](https://midlibrary.io/styles/wes-anderson)
- [Hailuo: Film Stock Emulation Guide](https://hailuoai.video/pages/knowledge/film-stock-emulation-ai-video-kodak-fuji-guide)
- [Cinematographers with Recognizable Look](https://www.premiumbeat.com/blog/cinematographers-with-recognizable-look/)
- [Cinematic Lighting Prompts (Atlabs)](https://www.atlabs.ai/blog/improve-your-ai-filmmaking-using-cinematic-lighting-prompts)
- [42 Cinematic AI Composition Prompts](https://www.atlabs.ai/blog/42-cinematic-ai-composition-prompts-guide)
- [No Film School AI Prompts](https://nofilmschool.com/ai-prompts-for-filmmakers)
- [Director Rip-off research](https://nofilmschool.com/which-directors-people-using-ai-rip-off)
