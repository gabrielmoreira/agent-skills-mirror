# 剪接與轉場 (Editing & Transitions) — 節奏的語言

**定位：** 單鏡再好，剪點沒對，整片垮。這份檔是把「資深剪接師」的思維整合進 prompt 與工作流。

**什麼時候讀這檔：**
- 做 multi-shot 敘事 (Seedance `Cut to`、storyboard 多鏡)
- 把多個單鏡 AI 片段剪接成完整影片
- 寫 MV / 廣告的 shot list (節奏比單鏡美感更重要)
- Sora 2 的 storyboard 模式 (秒級編排)

---

## Part 1 — 剪接理論速覽

### Eisenstein 蒙太奇五類

俄國 1920s 大師 Sergei Eisenstein 定義的五種剪接邏輯，**AI 模型 prompt 能懂**：

| 類型 | 英文 | 說明 | Prompt 寫法 |
|---|---|---|---|
| **節拍** | Metric | 按固定秒數切，機械律動 | `cuts on every 2 seconds, machine-precise rhythm` |
| **節奏** | Rhythmic | 跟著音樂拍點切 | `cuts on every downbeat, 120 BPM groove` |
| **旋律** | Tonal | 跟情緒調性切 | `cuts timed to mood shifts, contemplative slow dissolves` |
| **倍音** | Overtonal | 多重節奏層疊 | `layered cutting rhythms, fast cuts within long sustained takes` |
| **智性** | Intellectual | 並置兩個不相關 shot 創造意義 | `juxtapose shot A with shot B to imply [meaning]` |

### 經典連接性 vs 不連接性剪接

| 派別 | 原則 | 用途 |
|---|---|---|
| **Continuity (好萊塢經典)** | 觀眾不察覺剪接、空間時間連貫 | 敘事片、電視劇 |
| **Jump Cut (法國新浪潮)** | 刻意跳接、破壞連貫 | MV、獨立片、時尚片 |
| **Match Cut** | 下一鏡形狀/動作接續 | 詩意過渡、史詩 |
| **Smash Cut** | 極端對比切入 | 喜劇、反差、驚悚 |
| **Cross Cutting** | 兩條線交錯剪 | 懸疑、動作、追逐 |

---

## Part 2 — 具體剪接手法 × Prompt 寫法

### Match Cut (匹配剪接)

**定義：** 前後兩鏡的視覺/動作/意義連接起來。經典：《2001 太空漫遊》骨頭→太空船。

**類型：**

| 子類 | 說明 | Prompt 示例 |
|---|---|---|
| **Match on action** | 動作連續性 | `Cut on the character throwing the ball; next shot catches it mid-air in a different location` |
| **Match on shape** | 形狀相似 | `Cut from a circular window to a circular moon in the next scene` |
| **Match on graphic** | 構圖相似 | `Cut between two symmetrical compositions with subject centered` |
| **Match on sound** | 聲音延續 | `Cut with dialogue continuing seamlessly across two different locations` |

### Whip Pan / Snap Zoom

**定義：** 快速搖鏡 (whip pan) 或快速變焦 (snap zoom)，常用於 Wes Anderson、Edgar Wright、動作片。

```
Shot A ends with a rapid whip pan to the right, motion blur fills the frame,
which cuts to Shot B (the whip continues in Shot B at the start, landing
on the new subject).
```

**速度提示：** Wes Anderson 的 whip pan 是**乾脆停住**，Edgar Wright 的是**往復反彈**。

### Speed Ramp (速度坡道)

**定義：** 同一個 shot 內速度變化。實拍/後期都能做，AI prompt 表達需要明確分段。

```
[Veo / Sora / Kling]:
The shot starts at 60fps (1.5x slow), then speed ramps up to 24fps
(real-time) at the 3-second mark, then ramps down to 120fps (5x slow) for
the final 2 seconds as the subject jumps.
```

**情境：**
- 動作爆發前慢→快 (醞釀+釋放)
- 高潮瞬間快→慢 (時間凝固)
- 情緒轉換 (現實慢→夢境快)

### Freeze Frame

**定義：** 鏡頭凍結成靜幀。

```
The shot freezes on the character's face at the exact moment of realization,
held for 3 seconds as the soundtrack cuts to silence.
```

常搭配：旁白回憶、死亡瞬間、喜劇反差。

### J-Cut / L-Cut (聲畫錯位)

**J-Cut (下鏡聲先行)：** 下一鏡的聲音在本鏡最後 1-2 秒就先進來。

```
At second 8 of Shot A (a silent city street), dialogue from Shot B begins
to fade in. Cut to Shot B at second 10 with the dialogue already in mid-
sentence.
```

**L-Cut (本鏡聲延續)：** 本鏡的聲音延續到下一鏡。

```
Shot A shows a character speaking. Cut to Shot B (a different character's
reaction face) while Shot A's dialogue continues for another 3 seconds.
```

**用途：** 自然、生動、真實感。劇情片 80% 的剪點會用 J 或 L cut。

### Cross Cut / Parallel Editing (交叉剪接)

**定義：** 兩個 (或更多) 不同地點的動作交錯剪。

```
Parallel editing between three locations:
- Location A: Bomb technician defusing, tight close-ups, 2-3 second cuts
- Location B: Investigator racing through traffic, medium shots, 2 second cuts
- Location C: Family at dinner, wide shots, slower 5 second cuts

Cut frequency accelerates as they converge, ending in synchronized moment.
```

**經典：** 《沉默的羔羊》、《頂尖對決》、Scorsese 《The Departed》。

### Dissolve / Fade

| 類型 | 寫法 | 時長 |
|---|---|---|
| Cross dissolve | `cross dissolve between shots, 1 second overlap` | 0.5-2s |
| Fade to black | `fade to black, 2 seconds` | 結尾 |
| Fade from black | `fade in from black` | 開場 |
| Fade to white | `fade to white` | 回憶/夢境 |
| Long dissolve (time passage) | `slow 5-second dissolve suggesting days passing` | 5-10s |

### Wipe / Transition

多用於喜劇、90s 片：
- `horizontal wipe left-to-right`
- `iris wipe closing to center` (經典無聲片感)
- `star wipe` (喜劇復古)

大多現代劇情片避免用 wipe，因為太「工藝」感。**Star Wars** 例外 (招牌)。

### Smash Cut

**定義：** 極端聲音/視覺對比的硬切。

```
Smash cut from the character's loud scream to absolute silence and a static
wide shot of an empty field.
```

常用：醒夢、死亡、情緒崩潰。

---

## Part 3 — 剪接節奏設計

### 單鏡平均長度 (ASL - Average Shot Length) 參考

| 類型 | ASL | 特徵 |
|---|---|---|
| 快節奏動作 | 1-3s | Michael Bay, Jason Bourne |
| 標準好萊塢 | 3-5s | 一般商業片 |
| 歐陸藝術片 | 8-15s | Bergman, Kieslowski |
| 慢電影 | 30s+ | Tarkovsky, Béla Tarr |
| MV | 1-2s (副歌) / 4-6s (主歌) | 跟音樂節拍 |
| 廣告 30s | 1-3s | 快節奏品牌訊息 |

### 節奏加速曲線 (Build-up)

廣告/動作片常見：

```
Shot list cadence:
Shots 1-3: each 5 seconds (establish)
Shots 4-6: each 3 seconds (build)
Shots 7-10: each 1.5 seconds (intensify)
Shot 11: 4 seconds (climax hero shot)
Shot 12: 5 seconds slow resolution
```

### 節奏減速曲線 (Wind-down)

```
Shots 1-5: each 1 second (chaos)
Shots 6-8: each 3 seconds (settle)
Shots 9-10: each 8 seconds (still, reflective)
```

---

## Part 4 — 不同媒體的剪接範式

### 電影長片

- **開場 3 分鐘** 內要有情緒鉤子 (劇變或謎)
- **平均節奏** 3-7 秒一鏡
- **高潮前 5-10 分鐘** 會加快剪接
- **結尾** 通常有「呼吸點」(長靜鏡)

### 30 秒廣告

```
0-3s Hook (吸睛、反差)
3-10s Build (情境建立)
10-20s Peak (產品/情感高潮)
20-28s Product reveal
28-30s Logo + tagline
```

### MV

```
Intro (filter sweep): slow establishing, 1 shot
Verse 1: medium pace, 2-4 seconds per shot
Pre-chorus: cuts accelerate to 1-2 seconds
Chorus (drop): rapid cuts on beat, 0.5-1 second
Verse 2: return to medium
Bridge: slow/abstract visual break
Chorus × 2: fastest cutting
Outro: single long shot fade
```

### TikTok / Reel (9-15s)

```
0-0.5s: Visual hook (strong contrast)
0.5-3s: Reveal / setup
3-12s: Main content
12-15s: Punch line / CTA
```

**幾乎全部都是 1-1.5s/鏡，每 0.5s 就有新資訊。**

### 社群短影音 (30-60s)

保留 3 秒 intro hook 原則，後面每 3-5s 一個視覺變化。

---

## Part 5 — 音畫同步策略

### 配樂驅動剪接 (BPM matching)

```
Music: 120 BPM (beat every 0.5 seconds)
Cuts on every 4 beats = cuts every 2 seconds
Cuts on downbeat (1 of every 4) = cuts every 2 seconds but landing on strong beats
Cuts on every beat = cuts every 0.5 seconds (very rapid)
```

### 對白驅動剪接 (Dialogue)

**基本律：** 講話的人講話時，鏡頭多在講話的人臉上；聽話的人反應時，切到反應。

```
Shot A: Character A speaks first line (medium close-up)
Shot B: Cut to Character B's reaction, then Character B speaks second line
Shot C: Cut to Character A's reaction to B's response
```

**進階：** J-cut 讓聲音先行，視覺延遲一拍，更自然。

### SFX 驅動剪接

```
SFX: approaching train roar builds in Shot A (establishing exterior)
Smash cut to Shot B (interior) exactly on the moment the train passes
visible through window
```

---

## Part 6 — AI 工具與剪接工作流

### Seedance 1.0 Pro 原生多鏡 (`Cut to`)

Seedance 是目前唯一在單一 prompt 內能寫多鏡的 AI 影片平台：

```
Wide static shot of a fisherman mending nets on a dock at dawn.
Cut to: close-up of his weathered hands working the rope.
Cut to: wide shot of his small boat bobbing in the harbor.
Cut to: low-angle shot as he pushes the boat out at sunrise.
```

**限制：** 10 秒內最多 5 鏡；每鏡獨立描述；角色/場景描述要重複以保一致。

### Sora 2 Storyboard

逐秒編排 prompt：

```
0s: Establishing wide shot of the alley.
2s: Camera begins slow push-in.
4s: Cut to medium close-up of detective's face.
6s: He exhales smoke, turns toward sound off-screen.
8s: Whip pan to reveal approaching figure.
10s: Freeze on his reaction.
```

### Kling / Runway / Vidu 手動剪接

這些平台一次生單鏡，需要下載後去 CapCut / DaVinci / Premiere 剪。工作流：

1. 逐鏡生成 (用 storyboard.md 的 template)
2. 匯入剪輯軟體
3. 依本檔 Part 2 的手法切接

---

## Part 7 — 剪接中的「不剪」智慧

### 長鏡頭 (Oner / Long Take)

**定義：** 一鏡到底，不切。經典：Cuaron《Gravity》《Roma》、Iñárritu《Birdman》(看似一鏡)。

**Prompt 寫法：**
```
One continuous unbroken take, no cuts. Handheld Steadicam following the
subject through multiple rooms, maintaining single perspective for 60
seconds.
```

**AI 限制：** 當前 AI 影片平台最長單鏡 10-16s (Vidu Q3 16s 是最長)，要更長得 stitch 多鏡用 match cut 偽裝連續。

### 反剪接 (靜止)

不剪不是懶，是刻意。Michael Haneke 一鏡 8 分鐘、Béla Tarr 10 分鐘長鏡都有意義。

**Prompt 寫法：**
```
Locked-off static shot, no camera movement, no cuts. Subject stands in
frame for extended duration. Time and stillness as the primary drama.
```

---

## Part 8 — 剪接錯誤清單

| 錯誤 | 症狀 | 對策 |
|---|---|---|
| **30 度規則違反** | 同一主體連續兩鏡角度差 < 30°，像跳接 | 切兩鏡時角度相差 ≥ 30° 或徹底變 |
| **180 度規則違反** | 視線方向穿軸線 | 雙人戲兩人視線要相對，不要同向 |
| **音樂 BPM 對不上** | 剪點落在弱拍，節奏怪 | 找 downbeat (每小節第 1 拍) 切 |
| **單一節奏** | 整片相同 ASL，疲勞 | 三階段律動 (慢-中-快-慢) |
| **無呼吸點** | 滿滿對白 + 滿滿配樂 | 每 60-90 秒留 1 個 silent beat |
| **過度使用 dissolve** | 文青病 | 多數剪點用 hard cut，dissolve 留給情緒轉折 |
| **忘記 J-cut / L-cut** | 對話戲機械、不生動 | 80% 對話剪點該用 J/L cut |

---

## Part 9 — 剪接風格速配

| 作品風格 | 剪接特徵 | Prompt 關鍵詞 |
|---|---|---|
| Christopher Nolan | 快切 + 交叉剪 + 音響連續 | `parallel editing, cross-cut, sound bridge, rapid 2-3 second cuts` |
| Wes Anderson | 對稱 + whip pan + snap zoom | `Wes Anderson symmetrical cut, deadpan snap zoom, whimsical whip pan` |
| Edgar Wright | 音效驅動 + 快速 cut-ins | `Edgar Wright sound-driven editing, quick insert cuts, musical timing` |
| Tarantino | 長對話 + 不預期切換 | `long dialogue scenes, sudden jarring cut to violent action` |
| Scorsese | 長 oner + freeze + 旁白 | `long unbroken take, freeze frame with VO narration` |
| A24 indie | 慢長鏡 + 自然聲優先 | `long static takes, natural sound, sparse dialogue, no soundtrack` |
| Hiro Murai (MV) | 一鏡到底 + slow pace | `one continuous handheld take, slow deliberate pace` |
| Cole Bennett (MV) | 每拍一剪 + VFX 轉場 | `beat-matched cuts, animated VFX transitions, hyper-saturated` |
| TikTok UGC | 前 1 秒 hook + 每 0.5s 新資訊 | `rapid information density, jump cuts every beat, punchy` |

---

## Part 10 — 速查卡：為你的案子選對剪接策略

**決策樹：**

```
Q1. 媒材 / 片長？
├── 電影 90 min+ → ASL 3-7s, continuity 主, 高潮加速
├── 廣告 30s → ASL 1-3s, arc-driven (hook/build/peak/reveal)
├── MV 2-4 min → BPM matching, 副歌快切, 主歌中速
├── 短影音 <60s → ASL 0.5-2s, hook in 3s
└── 藝術片 → ASL 15s+, 靜為主

Q2. 節奏類型？
├── 動作 → metric + rhythmic
├── 敘事 → tonal (情緒切)
├── 詩意 → overtonal (層疊) + long takes
└── 概念 → intellectual (意義切)

Q3. 觀眾專注度?
├── 劇院 (高) → 可用慢鏡、長 takes
├── 串流平板 (中) → 標準 ASL
└── 手機直播/TikTok (低) → 前 1 秒必 hook, ASL < 2s
```

---

## 連結

- [StudioBinder — Shot Composition Rules](https://www.studiobinder.com/blog/rules-of-shot-composition-in-film/)
- [Awesome AI Video Prompts (GitHub)](https://github.com/geekjourneyx/awesome-ai-video-prompts)
- [Sora 2 Prompting Guide](https://cookbook.openai.com/examples/sora/sora2_prompting_guide)
- [Veo 3 Prompting Guide](https://deepmind.google/models/veo/prompt-guide/)
