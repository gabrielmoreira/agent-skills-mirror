# 音樂影片 (MV) 製作管線

## 兩條路線

### 路線 A — 一站式 (OiiOii Anime Music Video)
- **工時最短**，素材最少
- 犧牲控制力
- 適合快速成品 / 個人專案

見 [../references/oiioii.md](../references/oiioii.md) Anime MV 模式。

### 路線 B — 組合式 (Suno + 影片模型 + 剪接)
- 音樂用 Suno 生成
- 影片用 Kling / Seedance / Runway 分鏡生成
- 剪接軟體對齊音畫
- 控制力最強，品質上限最高

以下聚焦路線 B。

## 路線 B 工作流

### Step 1 — 概念

1 段話描述 MV：
- **情境**：人、地、時
- **情緒走向**：開場 → 高潮 → 收尾
- **視覺概念**：抽象 (色彩、符號) 或敘事 (有劇情)

**範例：**
> 一個穿棕色皮夾克的男子騎著摩托車穿越夜晚的霓虹城市，漸入人潮市集，然後在天橋上停下凝視遠方。電子合成器 + 鼓點，80 年代復古未來感。

### Step 2 — 先做音樂 (Suno)

為什麼先音樂：音樂的 BPM、段落長度、情緒高潮時間點決定影片剪接節奏。

見 [../references/suno.md](../references/suno.md)。

**建議做法：**
1. 寫 Style (4-8 tag) + Lyrics (結構完整)
2. 生成 2-3 版，挑最穩的
3. **記下** 每段的時間：Intro 0:00–0:08 / Verse 1 0:08–0:32 / Chorus 0:32–0:56 …
4. 下載 stems (v5 Studio Mode) 保留選擇

### Step 3 — 拆影片分鏡

**核心原則：** **一個音樂段落 = 1–3 個影片鏡頭**。

| 音樂段落 | 影片建議 |
|---|---|
| Intro (8–15s) | 1 個環境建立鏡 (establishing) |
| Verse (20–40s) | 2–4 個敘事鏡，節奏緩 |
| Pre-Chorus | 1 個「將爆發」的張力鏡 |
| Chorus (20–30s) | 3–5 個高能量鏡，快剪 |
| Bridge / Breakdown | 1–2 個慢鏡、不同時空、靜物 |
| Outro | 1 個收尾鏡，慢慢拉遠或淡出 |

### Step 4 — 逐鏡生成

每個鏡頭：
- 決定平台 (運鏡強度 → Kling；多鏡故事 → Seedance；角色一致 → Runway Gen-4 Refs / Vidu Ref2V)
- 寫 prompt (按該平台的 reference 檔)
- 生成 5–10s 片段
- 保持 **角色描述逐字一致** (複製貼上最安全)

見 [storyboard.md](storyboard.md) 的一致性技巧。

### Step 5 — 剪接對齊

工具：DaVinci Resolve、Premiere、CapCut、Final Cut。

**對齊重點：**
- 音樂的第一拍 = 影片第一個鏡的切入
- Chorus 的第一拍通常是最強視覺鏡
- Drop / Beat Drop → 硬切 (hard cut)
- 過渡段 → dissolve / match cut
- Outro 淡出 → 影片同步 fade to black

### Step 6 — 後期

- **色調統一**：用 LUT 或色輪把所有鏡的色調拉成同一套 (teal-orange / Ektar 100 / Portra 400 模擬)
- **加字幕** (若有歌詞) — 可用 CapCut 自動歌詞或人工 .srt
- **補音效** (腳步、環境音) — Vidu Q3 / Veo 3.1 已生成的可以直接用；否則從 freesound.org 補
- **輸出**：1080p 30fps / 9:16 for TikTok / 16:9 for YouTube

## 完整範例

**概念：** 80s 復古未來，摩托車 + 霓虹城市。

### 音樂 (Suno v5)
```
Style:
Retro synthwave with 80s neon futurism, driving analog synth bass,
gated reverb snare, arpeggiated lead, no vocals, 112 BPM, nocturnal and
yearning, Kavinsky inspired, wide stereo

Lyrics:
[Instrumental, Intro — rising filter sweep]

[Verse 1 — steady kick enters, bass groove]

[Pre-Chorus — risers, tension]

[Chorus — drop to full arp lead, soaring]

[Verse 2 — percussive variation]

[Chorus ×2 — climax]

[Outro — gradual filter down, fade]
```

時間：約 3:00

### 分鏡 (Kling 2.1 Master + Runway Gen-4 Refs)

**角色卡：**
```
CHAR = "a man in his 30s with stubble, dark messy hair, wearing a brown
leather jacket over a white t-shirt, dark jeans, black motorcycle gloves"
BIKE = "a matte black retro cafe racer motorcycle with a small round headlight"
```

**Shot 1 (Intro 0:00-0:10, Kling)**
```
Wide aerial establishing shot, descending toward a 1980s neon-lit metropolis
at night, rain-slick streets reflecting magenta and cyan signs. Cinematic,
Blade Runner 2049 palette, anamorphic lens flares, synthwave aesthetic.
```

**Shot 2 (Verse 0:10-0:25, Kling)**
```
[CHAR] riding [BIKE] through a neon-drenched street at night, medium tracking
shot from the side, camera moves alongside him. Neon reflections on his
leather jacket, cool blue and magenta grade, cinematic.
```

**Shot 3 (Verse 0:25-0:40, Kling)**
```
Close-up of [CHAR]'s face through the motorcycle visor, eyes focused on the
road ahead. Neon colors reflecting on the visor. Shallow depth of field,
cinematic, cool palette.
```

**Shot 4 (Pre-Chorus 0:40-0:50, Seedance)**
```
Low-angle tracking shot from behind the motorcycle, [CHAR] on [BIKE]
accelerating down an empty neon tunnel. Camera pushes forward, motion blur
building. Cinematic synthwave aesthetic.
```

**Shot 5 (Chorus 0:50-1:10, Runway Gen-4 Refs with character ref)**
```
(ref 1: CHAR portrait) The character, standing on a rooftop overlooking the
neon city below, the wind blowing his jacket open. Low-angle hero shot.
Dramatic magenta backlight from the skyline. Cinematic.
```

... (繼續拆剩下的鏡)

### 剪接清單
- 0:00 — Shot 1 (10s) cut to Shot 2
- 0:10 — Shot 2 (15s) match cut on motion to Shot 3
- 0:25 — Shot 3 (15s) cut to Shot 4
- 0:40 — Shot 4 (10s) match cut on forward motion to Shot 5 (drop on 0:50!)
- 0:50 — Shot 5 hard cut on the beat drop
- ...

### 後期
- 整片套 synthwave LUT (magenta shadows + cyan highlights)
- Grain 輕微 (35mm 模擬)
- 輸出 1080p 30fps 16:9

## 快速版 (無 Suno，用現有歌)

如果使用者已有一首歌 (原創或有授權)：
1. 拿歌曲波形貼 timeline
2. 標出 Verse / Chorus / Drop 時間
3. 跳到 Step 3 直接拆分鏡

**版權提醒：** 用別人版權的歌做 MV 上傳社群要考慮版權。Suno 生成的歌一般使用者有商用權 (看方案)，最乾淨。

## 常見錯誤

- **影片比音樂長 / 短** — 先確定音樂定稿再拆鏡
- **高潮視覺沒對到 Chorus 第一拍** — 重剪對齊
- **所有鏡都一樣 pacing** — 要有呼吸：Verse 緩、Chorus 快剪
- **角色描述不一致** — 設角色卡變數，複製貼
- **色調每鏡不一樣** — 後期 LUT 統一
