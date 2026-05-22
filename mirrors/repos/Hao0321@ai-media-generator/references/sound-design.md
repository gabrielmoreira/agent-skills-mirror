# 音效設計 (Sound Design) — 對白 / SFX / 配樂 / Foley

**定位：** Veo 3.1 與 Sora 2 起，AI 影片原生支援同步音訊。音效設計不再是後期事，而是 prompt 層級的決策。本檔教你寫出「有聲如見」的 prompt。

**適用平台：**
- ✅ **Veo 3.1** — 目前原生音訊最強 (對白 + SFX + 配樂同步)
- ✅ **Sora 2** — 近年加入原生音訊，畫面一致性最好
- ✅ **Vidu Q3** — 16 秒原生音視訊
- ⚠️ **Kling / Seedance / Runway** — 尚無原生音訊 (要後期補)

---

## Part 1 — 音訊層級分類

電影音訊有 4 個基本層，每層 prompt 寫法不同：

| 層級 | 英文 | 說明 | Prompt 語法 |
|---|---|---|---|
| **對白** | Dialogue | 人物講話 | `A character says, "..."` (引號內是講的字) |
| **環境音** | Ambience / Room tone | 背景持續性聲音 | 描述性，放在視覺後 |
| **特效音** | SFX (Sound Effects) | 特定物件/動作的聲音 | `SFX: ...` 前綴 |
| **配樂** | Soundtrack / Score / BGM | 襯底音樂 | `Soundtrack: [風格]` 或 `Score: ...` |

---

## Part 2 — 對白 Prompt 寫法

### 基本語法 (Veo 3 官方推薦)

```
[畫面描述]
A woman in a beige trench coat leans forward and says, "I already told you
everything I know." She pauses, eyes narrowing.
```

**規則：**
- 講話內容 **必用雙引號** `"..."`
- 引號外寫 **誰講的 + 怎麼講** (情緒、音量、節奏)
- 引號內 **只寫字面講的字**，不要舞台指示

### 情緒修飾詞

在 "says" 前加：

| 情緒 | 寫法 | 效果 |
|---|---|---|
| 低聲 | `whispers` / `says softly` | 音量降、氣音 |
| 大聲 | `shouts` / `yells` | 音量拉、可能破音 |
| 顫抖 | `says tremulously` / `voice shaking` | 聲音抖 |
| 冷漠 | `says flatly` / `deadpan` | 無情緒、機械感 |
| 憤怒 | `growls` / `says through gritted teeth` | 低沉、咬牙 |
| 笑 | `says with a laugh` / `chuckles` | 帶笑聲 |
| 哭 | `says through tears` / `sobs` | 帶哭聲 |
| 嘆 | `sighs heavily before saying` | 嘆後再講 |
| 喘 | `pants, then gasps out` | 運動後或急促 |
| 內心 OS | `voiceover narration:` 或 `internal monologue:` | 非現場、旁白感 |

### 語言與口音

| 需求 | 寫法 |
|---|---|
| 中文普通話 | `speaks in Mandarin Chinese`, `"你確定嗎？"` |
| 粵語 | `speaks in Cantonese`, `"你肯定？"` |
| 英式英語 | `in a London accent, says, "..."` |
| 南方口音 | `with a Texas drawl, says, "..."` |
| 日語 | `in Japanese, says, "..."` |
| 韓語 | `in Korean, says, "..."` |

**實測：** Veo 3.1 對英文口音辨識度高；中文對白穩定度仍略低於英文 (2026-04)。關鍵場景可先用英文配中文字幕。

### 多人對話

```
Two detectives sit across a booth in a diner.

Detective A leans forward, voice low: "You already know where the body is,
don't you?"

Detective B stares silently for three beats, then slowly nods. He whispers,
"I never wanted any of this."
```

**關鍵：**
- 每個角色的行動 + 說話分段寫
- 中間可加 `pauses for X beats` 控制節奏
- 雙人鏡頭自然會對應 medium two-shot (見 [camera-language.md](camera-language.md))

### 內心獨白 / 旁白

```
Voiceover (internal monologue): "She had warned him that night, but he
thought he knew better."

[畫面：男子獨自走過雨中街道]
```

Veo / Sora 會自動生成內心敘述式口吻 (通常較平靜、貼近耳朵)。

---

## Part 3 — SFX (特效音) 寫法

### 基本語法

用 `SFX:` 前綴，描述聲源 + 音質：

```
SFX: thunder cracks in the distance, then rolls for several seconds.
SFX: a coffee cup clinks against a saucer.
SFX: muffled footsteps approaching on wet pavement.
```

### SFX 分類詞庫

#### 🌧️ 天氣 / 自然
| 聲音 | 寫法 |
|---|---|
| 雷 | `distant thunder`, `sudden thunderclap`, `rolling thunder` |
| 雨 | `gentle rain pattering on a tin roof`, `heavy rain drumming`, `rain hissing on hot pavement` |
| 風 | `wind whistling through gaps`, `howling wind`, `gentle breeze rustling leaves` |
| 浪 | `waves crashing on rocks`, `gentle lapping water`, `distant surf` |
| 火 | `crackling fire`, `roaring flames`, `ember popping` |
| 雪 | `muffled silence of snow`, `crunching footsteps on fresh snow` |

#### 🏙️ 城市
| 聲音 | 寫法 |
|---|---|
| 車流 | `distant traffic hum`, `passing car whoosh`, `honking horn in distance` |
| 捷運 | `subway train rumble approaching then passing`, `train doors chime` |
| 人群 | `crowd murmur`, `indistinct chatter of a busy market`, `cheering crowd` |
| 腳步 | `footsteps on wet pavement`, `hard shoe clicks on marble`, `sneakers on concrete` |
| 施工 | `jackhammer in distance`, `construction banging` |
| 廣播 | `indistinct PA announcement echoes` |

#### 🏠 室內 / 日常
| 聲音 | 寫法 |
|---|---|
| 門 | `heavy wooden door creaking open`, `modern door click shut`, `glass door swish` |
| 鐘 | `grandfather clock ticking`, `alarm clock buzzing` |
| 電器 | `refrigerator hum`, `microwave beep`, `washing machine tumble` |
| 打字 | `mechanical keyboard clacking`, `old typewriter ding and return` |
| 紙 | `paper rustling`, `page turn`, `paper being torn` |
| 杯碗 | `glass clinking`, `ceramic cup set on wood`, `liquid pouring into a glass` |

#### 🔫 武器 / 戰鬥
| 聲音 | 寫法 |
|---|---|
| 槍 | `single gunshot echo`, `rapid gunfire`, `bullet whizzing past` |
| 劍 | `sword being drawn from sheath`, `blade clashing with blade`, `metal ring of a weapon` |
| 爆炸 | `distant explosion rumble`, `close-up detonation boom` |
| 拳腳 | `solid punch impact with breath out`, `sneaker squeak on mat` |

#### 🐾 動物
| 聲音 | 寫法 |
|---|---|
| 狗 | `distant dog bark`, `puppy whimpering`, `large dog growling` |
| 貓 | `soft mew`, `cat purring close to mic`, `hissing cat` |
| 鳥 | `dawn chorus`, `single crow call`, `owl hoot` |
| 蟲 | `crickets chirping at night`, `cicadas buzzing`, `buzzing fly` |

#### 🎬 電影感 SFX
| 聲音 | 寫法 |
|---|---|
| Whoosh 轉場 | `sudden whoosh pass` |
| Riser 漸強 | `synth riser building tension` |
| Impact 重擊 | `deep sub-bass impact` |
| Stinger 收尾 | `orchestral stinger hit` |
| Sub-bass drone | `low sub-bass drone under entire scene` |
| Heart beat | `amplified slow heart beat thud` |

### SFX 層疊寫法

多個 SFX 同時發生，用 `+` 或逗號分開：

```
SFX: heavy rain on rooftop, rolling thunder in distance, water dripping
into a metal bucket inside, plus a single flickering neon sign buzzing.
```

---

## Part 4 — 配樂 (Soundtrack) 寫法

### 基本語法

```
Soundtrack: [風格] + [情緒] + [樂器] + [BPM] + [動態曲線]
```

或用 `Score:`：

```
Score: tense orchestral strings building to a crescendo, then sudden silence.
```

### 配樂風格詞庫

| 場景 | Prompt 寫法 |
|---|---|
| 緊張懸疑 | `Soundtrack: low pulsing synth bass, dissonant string swells, building tension` |
| 溫柔感傷 | `Soundtrack: solo piano melancholy, sparse notes, warm reverb, no drums` |
| 史詩壯闊 | `Soundtrack: orchestral brass and taiko drums, Hans Zimmer inspired, rising heroic crescendo` |
| 懷舊爵士 | `Soundtrack: smooth 1940s jazz, muted trumpet, brushed drums, warm vinyl` |
| 賽博龐克 | `Soundtrack: dark synthwave, analog Moog bass, gated reverb snare, 95 BPM` |
| 東方古韻 | `Soundtrack: traditional Chinese erhu and guzheng, pentatonic melody, ambient drone` |
| 電子節奏 | `Soundtrack: techno four-on-the-floor, 128 BPM, side-chained synths` |
| Lo-fi 寧靜 | `Soundtrack: lo-fi hip-hop, warm vinyl crackle, muted piano, 75 BPM` |
| 民謠溫暖 | `Soundtrack: acoustic folk, fingerpicked guitar, soft harmonica` |
| 無音樂 | `No soundtrack. Only diegetic ambience.` |

### 配樂動態 (Dynamic Arc)

寫 prompt 時可明講音樂 **怎麼發展**：

```
Soundtrack: starts with solo piano (0-3s), gentle strings enter (3-6s),
full orchestral swell on the reveal (6-9s), then sudden drop to silence
(10s).
```

這樣 Veo 3.1 / Sora 2 的配樂會配合視覺節拍。

### 配樂版權注意

**⚠️ 不要寫具體曲名或藝人名：**
- ❌ `Soundtrack: Radiohead's "Creep"` (侵權風險)
- ✅ `Soundtrack: melancholic alternative rock in the spirit of 1990s Radiohead`

AI 模型理解「風格」而不需要「真歌」。寫風格安全又有效。

---

## Part 5 — Foley (擬音)

Foley 是**人工重現**的貼身聲音：腳步、衣物摩擦、物件操作。AI 模型在「描述性 Foley」表現越來越好。

### 常見 Foley Prompt

| 動作 | 寫法 |
|---|---|
| 腳步 (皮鞋) | `Foley: leather shoes on wooden floor, heel-toe rhythm` |
| 腳步 (運動) | `Foley: sneakers on wet concrete, slight squeak` |
| 衣物 | `Foley: trench coat rustling as character turns` |
| 倒飲料 | `Foley: liquid pouring into a ceramic cup, bubble glug` |
| 點火 | `Foley: Zippo lighter flick and flame whoosh` |
| 抽菸 | `Foley: cigarette paper crackle on inhale, slow exhale` |
| 寫字 | `Foley: ballpoint pen scratching on paper` |
| 翻書 | `Foley: hard cover book being opened, page turn` |
| 拉拉鍊 | `Foley: zipper opening on leather jacket` |
| 金屬 | `Foley: metal key ring jingling in hand` |

---

## Part 6 — 完整案例：音訊 × 視覺對齊

### 案例 A — 偵探獨白戲 (Veo 3.1)

```
Interior, a dimly lit diner booth, rain streaming down the window behind.
Medium close-up of a weary detective, his face half in shadow from the
overhead practical lamp.

Dialogue (internal monologue, Voice-over): "She had called me three times
that night. I didn't answer. I should have answered."

Action: He slowly lifts a ceramic coffee cup to his lips, takes a long sip.

SFX: distant thunder rolling, rain drumming on the diner roof, ceramic cup
setting down on the formica table, refrigerator hum.

Foley: coffee cup clinks gently, detective exhales slowly through his nose.

Soundtrack: sparse low piano with a single held string note, melancholic
and unresolved, very quiet under the dialogue.

Visual: cinematic noir, shot on Alexa 35, Kodak Vision3 500T emulation,
2.39:1 anamorphic, warm tungsten practical overhead, cool teal shadows.
```

### 案例 B — 快節奏運動廣告 (Veo 3.1)

```
30-second sports commercial. Four beats synchronized to a driving 128 BPM
track.

Beat 1 (0-5s): Extreme close-up of sprinter's eye. SFX: single deep
heartbeat thud. Soundtrack: subtle rising synth drone.

Beat 2 (5-15s): Low-angle tracking of feet pounding track. SFX: pounding
footsteps, breathing rhythmic. Soundtrack: 4/4 kick enters, 128 BPM techno
groove builds.

Beat 3 (15-25s): Hero silhouette mid-stride. SFX: stadium crowd roar fades
in and up. Soundtrack: full drop, synthesizer lead soaring, crowd cheer
blending into music.

Beat 4 (25-30s): Athlete crosses finish line. SFX: sudden silence of music,
then breath, then single explosive cheer. Soundtrack: cuts out for 2 seconds
of pure breath and ambient stadium, then brand stinger hit on tagline.

Visual: 200fps Phantom slow motion, bleach bypass, brand red accent light.
```

### 案例 C — 中文情感戲 (Sora 2 / Veo 3.1 + 中文)

```
Interior, a Taiwan night market dumpling shop, steam rising from bamboo
baskets. Medium close-up of a middle-aged chef (Chef Lin) and a young
apprentice at the counter.

Dialogue:
Chef Lin, slowly wiping a bowl, speaks in Mandarin with Taiwanese lilt:
"你知道為什麼我堅持用老麵嗎？"

Apprentice, without looking up from the dough: "因為奶奶教你的。"

Chef Lin pauses, then quietly: "不是。是因為它記得我奶奶。"

SFX: bamboo steamer lid clattering softly, oil bubbling in a wok, distant
scooter passing on the street, light rain beginning outside.

Foley: porcelain bowl being wiped with cloth, hands kneading dough with
soft slap.

Soundtrack: single erhu melody, melancholic and warm, very sparse, 60 BPM.

Visual: shot on Alexa Mini LF, Cooke S7/i 50mm T2.0, warm tungsten
practical from hanging red lanterns overhead, Kodak Vision3 500T emulation,
shallow depth of field isolating Chef Lin's hands.
```

---

## Part 7 — 音訊層的優先順序

做 prompt 時，若篇幅有限，**音訊 4 層的重要性排序**：

1. **對白** (必有對白的戲) — 最影響觀眾理解
2. **環境音 + 關鍵 SFX** — 讓畫面可信 (雨、車流、腳步)
3. **Foley** — 貼身細節，提升沉浸感
4. **配樂** — 最後加，避免蓋掉前三層

**常見錯誤：** prompt 寫一堆配樂描述，卻忽略環境音。結果 Veo 生出像 MV 不像電影。

---

## Part 8 — 與視覺對齊的節奏原則

- **配樂的重拍 = 視覺的剪點** — prompt 明寫 `cut on the downbeat`
- **對白的停頓 = 鏡頭切換** — `pause for 2 beats before next shot`
- **SFX 引導視覺** — 先聲後影 (如雷聲 → 閃電畫面)，或反之
- **靜音是武器** — `sudden drop to silence` 比任何聲響都有戲

---

## Part 9 — 平台限制與變通

| 平台 | 音訊支援 | Prompt 做法 |
|---|---|---|
| Veo 3.1 | ✅ 完整 (對白/SFX/BGM) | 全寫在 prompt，模型自動合成 |
| Sora 2 | ✅ 完整，對白稍弱於 Veo | 同上，對白關鍵場景多跑幾次 |
| Vidu Q3 | ✅ 環境音 + 物件音效 (對白弱) | SFX 寫詳細，對白去 Veo |
| Kling 2.6 Pro | ⚠️ 部分 (lipsync 要上傳音訊) | 視覺 prompt only，後期補音 |
| Seedance 1.0 Pro | ❌ 無原生音訊 | 後期用 Suno 配樂 + freesound 補 SFX |
| Runway Gen-4 | ❌ 無原生音訊 | 同上 |

### 後期補音訊的替代路徑

若平台不支援原生音訊：
1. **Suno v5** — BGM / 整首歌
2. **ElevenLabs / Resemble AI** — TTS 對白
3. **Freesound.org / Epidemic Sound** — SFX / Foley
4. **Descript / Adobe Premiere** — 合成對齊

---

## Part 10 — 速查表

### 對白快速寫法

```
[Character] says, "[Line]."                           # 基本
[Character], voice [emotion], says, "[Line]."         # 加情緒
[Character] pauses, then whispers, "[Line]."          # 加停頓
[Character], in [accent/language], says, "[Line]."    # 加口音
Voice-over: "[Line]."                                 # 旁白
```

### SFX 快速寫法

```
SFX: [source] [action] [quality adjective].
SFX: [layer 1], [layer 2], [layer 3].
```

### 配樂快速寫法

```
Soundtrack: [genre/mood] [instrument] [BPM] [arc].
Score: [emotional function, e.g., "building tension" / "quiet resolution"].
```

---

## 連結

- [Veo 3 DeepMind Prompt Guide](https://deepmind.google/models/veo/prompt-guide/)
- [Veo 3.1 Google Cloud Ultimate Guide](https://cloud.google.com/blog/products/ai-machine-learning/ultimate-prompting-guide-for-veo-3-1)
- [Sora 2 OpenAI Cookbook](https://cookbook.openai.com/examples/sora/sora2_prompting_guide)
- [100+ Veo 3 Examples (GVN)](https://geekvibesnation.com/google-veo-3-prompts-100-tested-examples-that-actually-work-2026/)
