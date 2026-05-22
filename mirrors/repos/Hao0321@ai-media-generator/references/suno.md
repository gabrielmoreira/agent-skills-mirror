# Suno v5 — AI 音樂生成

官網 `https://suno.com/`。2026 時點主力 **Suno v5** (Studio Mode、stem separation、up to 4 分鐘、negative prompts)。

## 兩個欄位 — 分清楚

Suno UI 有兩個獨立欄位，**功能完全不同**：

| 欄位 | 放什麼 | 不要放什麼 |
|---|---|---|
| **Style** | 曲風、情緒、樂器、BPM、年代、製作風格 | 歌詞 / 結構標籤 |
| **Lyrics** | 歌詞、結構標籤 `[Verse]`、人聲 tag | 曲風描述 |

把 `[Verse]` 放到 Style 欄會沒反應；把 "dark synthwave" 放到 Lyrics 欄會被當成歌詞唱。

## Style 欄 — 五段公式

```
(1) 曲風 + 次曲風 + (2) 情緒/能量 + (3) 人聲風格 + (4) 關鍵樂器與製作 + (5) 節奏/BPM
```

**範例：**
```
Dark synthwave with retro funk elements, moody and tense, female vocal with
sultry whispered delivery, analog synth bass, gated reverb snare, side-chained
pads, warm tape saturation, 98 BPM
```

### 規則
- **4–8 個 tag 最穩**；太少模型自由發揮，太多互相打架
- **一類一個 tag** — genre 一個、mood 一個、vocal 一個 …
- **v5 懂製作品質詞彙**：`modern pop production, radio-ready mix, punchy drums, wide
stereo field, crisp high-end, warm bass`
- **Negative 放在最後面，用明確排除句**：`no drums`, `no auto-tune`, `exclude rap`

### Style tag 實用字典 (節錄)

**Genre / Subgenre：**
dark synthwave / retrowave / city pop / J-pop / K-ballad / nu-disco /
post-punk / shoegaze / dream pop / bedroom pop / lo-fi hip hop / trap
soul / afrobeats / amapiano / reggaeton / EDM big room / dubstep / drum &
bass / UK garage / chillwave / ambient / neoclassical / cinematic
orchestral / epic trailer / chiptune / math rock

**Mood：**
melancholic / euphoric / tense / triumphant / nostalgic / haunting / playful /
cathartic / dreamy / ominous / uplifting / bittersweet

**Vocal style：**
`female vocal` / `male vocal` / `gender-neutral vocal` / `falsetto` /
`whispered` / `breathy` / `raspy` / `operatic` / `soulful` / `spoken word` /
`duet` / `choir`

**Instruments：**
analog synth / Moog bass / Rhodes electric piano / 808 kick / trap hi-hats /
orchestral strings / pedal steel guitar / saxophone / ukulele / erhu / koto /
shakuhachi / taiko drums

**Production：**
lo-fi tape saturation / gated reverb / side-chained pads / filter sweeps /
analog warmth / pristine digital / vintage 1980s / modern punchy / wall of
sound / minimalist sparse

## Lyrics 欄 — 結構 metatags

**必須用方括號**。寫 "Verse:" 會被當成歌詞唱出來。

### 必備結構 tag
- `[Intro]`
- `[Verse 1]` / `[Verse 2]` / ...
- `[Pre-Chorus]`
- `[Chorus]`
- `[Post-Chorus]`
- `[Bridge]`
- `[Breakdown]` / `[Drop]`
- `[Solo]` / `[Guitar Solo]` / `[Synth Solo]`
- `[Interlude]`
- `[Outro]`
- `[End]` / `[Fade Out]`

### 人聲/情緒 tag (v5 起很敏感)
- `[Male Vocal]` / `[Female Vocal]`
- `[Whisper]` / `[Shout]` / `[Falsetto]` / `[Spoken]`
- `[Harmony]` / `[Ad-libs]` / `[Backing Vocals]`
- `[Instrumental]`
- `[Beat Drop]`

### 語言 tag (混語必備)
- `[Chinese Verse]`, `[English Chorus]`, `[Japanese]`, `[Korean]`

### 範例 Lyrics 結構

```
[Intro]
(soft piano arpeggio)

[Verse 1]
(female vocal, whispered)
The city sleeps in amber light
Your shadow fades from sight

[Pre-Chorus]
(rising intensity)
And I keep waiting for the sound
Of you coming back around

[Chorus]
(full band, soaring)
Don't let me go tonight
Don't let me go
Hold on to the fading light
Don't let me go

[Verse 2]
...

[Bridge]
(instrumental break, synth solo)

[Chorus × 2, with ad-libs]
...

[Outro]
(fade out, single piano note)
```

## 進階：Top-anchor 技巧

**把最重要的 1-2 句風格/人聲指示放在 Lyrics 最前面**，Suno 會用它鎖住整首：

```
[A dreamy female vocal with subtle reverb, intimate bedroom pop]

[Verse 1]
...
```

## Suno v5 新功能

### Studio Mode
- **Stem separation**：產生後可分離人聲 / 鼓 / 貝斯 / 其他
- **Section-by-section editing**：單獨重生成某段 (Verse、Chorus)
- **Negative prompting**：Style 欄末尾可加排除

### 長度
- 最長約 4 分鐘 (Pro 以上)

### 音質
- v5 明顯比 v4.5 乾淨，人聲清晰度與混音平衡↑

## Persona / Cover / Extend / Remix

| 功能 | 用途 | Prompt 重點 |
|---|---|---|
| **Persona** | 把某首歌的人聲風格記錄，套用到新歌 | 先做 Persona → 呼叫 |
| **Cover** | 原歌詞用不同風格重做 | Style 寫新風格 |
| **Extend** | 從既有片段往後接 | 描述接下來的段落 |
| **Remix (v5)** | 改單一變數 | 如 "same song, new mood: uplifting" |
| **Stems 下載** | 分軌 | 無 prompt |

## 中文歌技巧

- **歌詞用中文**、**風格描述仍用英文**
- 情感濃烈的字 (「離別」、「星光」、「夜雨」) 在 Suno 表現不錯
- 雙語混唱：`[Chinese Verse]` + `[English Chorus]`
- 避免太長每行 (>12 字)，模型斷句會歪

**範例：**
```
Style: Mandopop ballad with modern R&B production, male vocal with gentle
falsetto, Rhodes piano, subtle strings, 80 BPM, melancholic and hopeful

Lyrics:
[Intro]
(soft piano)

[Verse 1]
[Male Vocal, gentle]
那年夏天的蟬鳴
還在耳邊迴響
你說過的晚安
成為最後的光

[Chorus]
[Full band, emotional]
如果時間能倒流
我願意再等一次
哪怕只是一眼
也是一輩子
```

## 範例彙整 (5 風格)

**1. Dark Synthwave**
```
Style: Dark synthwave with retro funk, moody, female vocal sultry and whispered,
analog Moog bass, gated reverb snare, side-chained pads, 98 BPM, cinematic

Lyrics:
[Intro]
(synth swell)

[Verse 1]
[Female Vocal, whispered]
Neon bleeding through the rain
You left your jacket on the chair
...
```

**2. Lo-fi Hip Hop**
```
Style: Lo-fi hip hop instrumental with jazz samples, warm vinyl crackle,
dusty boom bap drums, upright bass, muted trumpet, 75 BPM, nostalgic study
vibes, no vocals

Lyrics:
[Instrumental]
```

**3. Epic Trailer**
```
Style: Cinematic epic orchestral trailer, massive choir swells, taiko drums,
brass stabs, rising tension into heroic climax, 120 BPM, Hans Zimmer inspired

Lyrics:
[Instrumental, rising tension]
```

**4. Shibuya-kei / J-pop**
```
Style: Shibuya-kei meets modern J-pop, bright and playful, female vocal
clean and cute, bossa nova guitar, retro samples, vibraphone, 108 BPM

Lyrics:
[Intro]
(handclaps, bossa guitar)

[Verse 1]
[Female Vocal]
(Japanese lyrics here)
...
```

**5. Indie Folk**
```
Style: Intimate indie folk, male vocal raspy and heartfelt, fingerpicked
acoustic guitar, subtle harmonium, gentle brushed drums, 72 BPM, bittersweet

Lyrics:
[Intro]
(single acoustic guitar)

[Verse 1]
[Male Vocal, soft]
Morning light through the broken blind
Coffee cold on the windowsill
...
[Chorus]
[Harmonies enter]
...
```

## 常見錯誤

- **Style 欄塞歌詞** → 會當 tag 處理，出來一團糟
- **Lyrics 欄用 "Verse:" 沒括號** → 被唱出來
- **忘記 `[End]` 或 `[Outro]`** → 突然截斷或無限 loop
- **一首歌塞 10+ instruments** → 混音擠爆。挑 4–6 個
- **Negative 放在 Style 中間** → 要放最後
- **中文歌用純中文 Style 描述** → Style 欄對英文最準；要用英文描述曲風
- **同時指定衝突 mood** (`happy and melancholic`) → 選一個 dominant

## 連結

- 官方：https://suno.com/
- v5 完整指南 (HookGenius)：https://hookgenius.app/learn/suno-v5-complete-guide/
- 2026 Prompt 完整指南：https://hookgenius.app/learn/suno-prompt-guide-2026/
- 300+ Style Tags 分類庫：https://hookgenius.app/learn/suno-style-tags-guide/
- Metatags 完整列表：https://hookgenius.app/learn/suno-metatags-complete-list/
- Meta Tags & Song Structure (Jack Righteous)：https://jackrighteous.com/en-us/pages/suno-ai-meta-tags-guide
- Voice / Vocal Tags (howtopromptsuno)：https://howtopromptsuno.com/making-music/voice-tags
- Style + Lyrics 整合：https://howtopromptsuno.com/style-lyrics
- v5 Lyrics 專業指南 (CometAPI)：https://www.cometapi.com/how-to-instruct-suno-v5-with-lyrics/
- Prompt 位置指南 (Jack Righteous)：https://jackrighteous.com/en-us/blogs/guides-using-suno-ai-music-creation/where-to-put-your-suno-prompt-guide
- Complete Prompts & Styles (Travis Nicholson)：https://travisnicholson.medium.com/complete-list-of-prompts-styles-for-suno-ai-music-2024-33ecee85f180

---

## 🆕 Suno v4.5 + v5 進階功能完整地圖

### 1. Personas (聲線存檔)

- 選某首歌的人聲 → "Create Persona"
- Persona 存成可重用的 character voice
- 新歌可套這個 persona，保持跨歌聲線一致
- **用例：** 建立「品牌 vocalist」，所有行銷曲都用同一聲線

### 2. Covers (同歌詞重做)

- 原歌詞 + 新 style → 重生不同曲風版本
- 同一首歌的 rock 版 / 爵士版 / lo-fi 版
- v4.5 起 **Cover 可 Extend 更長** (不只 4 分鐘)

### 3. Extend (延長現有歌)

- 完成的歌再跑 extend → 自動續作 2-4 分鐘
- v4.5+ 支援 intelligent extend (保持結構一致)

### 4. Remix (一次改一變數)

- `same song, new mood: uplifting`
- `same lyrics, change to 95 BPM`
- `same melody, remove drums`

### 5. Remaster (微調變體)

- 微變體 (同一 prompt 不同 seed)
- 快速生多版本挑最好

### 6. Genre Mashups (v4.5 強項)

直接寫混搭 genre，Suno v4.5 理解細緻：
```
midwest emo + neosoul
EDM + folk
trap soul + jazz fusion
```

### 7. Prompt Enhancement Helper

Style 欄輸入簡單 genre → 按 Enhance → Suno 自動擴寫詳細專業語彙。**不熟音樂術語的使用者救星**。

### 8. Co-Creation (v4.5+)

- **Add Vocals** (純樂曲加人聲)
- **Add Instrumentals** (純 acapella 加伴奏)
- **Inspire** (AI 建議 prompt 改善方向)

### 9. Hooks (副歌片段)

- 專門生成 **30 秒 hook** (品牌主題曲 / 廣告短片)
- 左側 sidebar `+Create` next to Hooks
- 優化為極短高密度記憶點

### 10. Studio Mode (v5 Pro only)

- **Stem separation** (vocal / drums / bass / other 分軌)
- Section-by-section editing
- 專業音訊 cleanup + 微調
- Stems 下載 (WAV)

### 11. v5 vs v4.5 差異

| 項目 | v4.5 (免費 tier `v4.5-all`) | v5 (Pro only) |
|---|---|---|
| 速度 | 標準 | **10x faster** |
| 長度 | 4 分鐘 | **30s hook 到 8 分鐘 epic** |
| 音質 | 好 | **更高 fidelity**，clearer separation |
| Voice consistency | 一般 | **跨 project 保持一致** |
| Stem export | 無 | **有** |
| 結構連貫 | 還 OK | **Professional transitions** |

### 12. 進階 Style 控制 (Advanced 模式下 More Options)

- **Vocal Gender:** Male / Female
- **Lyrics Mode:** Manual (自己寫) / Auto (Suno 自動生歌詞)
- **Weirdness** slider (0-100%)：低=貼 prompt，高=自由發揮
- **Style Influence** slider (0-100%)：低=模型自由，高=嚴格 style prompt

### 13. Persona + Covers + Extend 組合工作流 (專業製作)

```
Step 1: 用完整專業 prompt 做 1 首歌 (10 credits, 2 版)
Step 2: 挑最好 version → Create Persona (存聲線)
Step 3: 同 Persona + 新歌詞 → 3-5 首專輯 (4-5 首歌的一致聲線)
Step 4: 每首 Extend 到 3-4 分鐘
Step 5: v5 Pro 用 Stems 下載分軌 → 自己混音
```

這個 workflow 能產出**完整專輯**。

### 新連結

- [Introducing v4.5 (Suno blog)](https://suno.com/blog/introducing-v4-5)
- [Introducing v5](https://help.suno.com/en/articles/8105153)
- [Suno v5 vs v4.5 Upgrade Guide](https://jackrighteous.com/en-us/blogs/guides-using-suno-ai-music-creation/suno-v5-vs-v4-5-upgrade-guide)
- [Suno v5 + Studio Complete Guide (Medium)](https://medium.com/@creativeaininja/suno-v5-and-studio-the-complete-guide-to-professional-ai-music-production-d55c0747a48e)
- [Suno Remix Guide 2026](https://jackrighteous.com/en-us/pages/suno-remix-v45-guide)
