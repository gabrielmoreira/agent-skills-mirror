# Suno — AI 音樂生成

官網 `https://suno.com/`。2026 時點主力 **Suno v5.5**（2026-03-26 釋出）。文字描述 + 結構化歌詞 → 完整歌曲（人聲 + 編曲 + 混音 + 母帶）。Suno 的核心差異化：**Style / Lyrics 兩個獨立欄位**、**方括號 meta tags 結構標記**、**Voices（聲線一致性）** 與 **Studio 生成式 DAW**（12 軌 stem 分軌）。

---

## 0. 版本能力矩陣（2026-06 時點）

| 版本 | 釋出 | 標誌能力 | tier |
|---|---|---|---|
| **v4** | 2024-11 | Remaster（舊曲升音質）、**ReMi** 歌詞模型、音質躍升 | — |
| **v4.5** | 2025-05 | **Personas**、Covers、Extend、Prompt Enhancement Helper、分類 meta tag `[Genre: X]`、genre mashup 理解強 | 免費 `v4.5-all` |
| **v5** | 2025-09 | **Suno Studio**（瀏覽器 DAW）、**12 軌 stem 分離**、Persona Voices、studio-grade 母帶音質 | Pro / Premier |
| **v5.5** | 2026-03-26 | **Voices**（Persona 改名 + 可捕捉「你自己的聲音」）、**Custom Models**（Pro/Premier 訓自己風格模型 ×3）、**My Taste**（學你口味，全 tier） | Pro / Premier（Studio 限 Premier） |

**重點變化（務必理解）：**
- **Personas 已改名為 Voices**（v5.5）。舊 Personas 全部保留在新的 **Voices 分頁**，不會遺失。
- **v5 的所有 prompt / meta tags / negative prompts / style tags 在 v5.5 完全相容**，沒有任何移除或改變 — 不需要重寫既有 prompt 範本。
- **免費帳號實際拿到 `v4.5-all`**（每日 50 credits ≈ 10 首，非商用）。送出後 Suno 常**額外附贈 2 首 v5.x Preview 試聽片段**（~1:08，要升 Pro 才能下載完整版）— 這是 upsell 機制。
- **Studio DAW 綁 Premier**（$24/月 起）；Pro 可用 v5 model 但**不含 Studio**。（Studio↔Pro 細節見 §8.5，部分來源說法不一，標 (待驗證)）

---

## 1. 兩個欄位 — 分清楚（Suno 最重要的概念）

Suno Custom Mode 有兩個獨立欄位，**功能完全不同**：

| 欄位 | 放什麼 | 不要放什麼 |
|---|---|---|
| **Style** | 曲風、情緒、樂器、BPM、年代、製作/混音風格 | 歌詞 / 結構標籤 |
| **Lyrics** | 歌詞、結構 metatags `[Verse]`、段內人聲 tag | 整段曲風描述 |

把 `[Verse]` 放到 Style 欄會沒反應；把 `dark synthwave` 放到 Lyrics 欄會被當成歌詞唱出來。

官方定位（v5.5）：**Style 寫「整體聲音世界」**（genre / vocal lane / 速度感 / 編制 / 氛圍）；**Lyrics 寫「段落流程 + 局部提示 + 結構行為」**。

---

## 2. Style 欄 — 五段公式

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
- **4–8 個 tag 最穩**；太少模型自由發揮，太多互相打架。**樂器超過 3-4 個易混音擠爆**。
- **一類一個 tag** — genre 一個、mood 一個、vocal 一個 …
- **最重要的 style 詞放在前 20-30 字**（影響力最大）。
- **v5/v5.5 懂製作品質詞彙**：`modern pop production, radio-ready mix, punchy drums, wide stereo field, crisp high-end, warm bass`
- **Negative 放在最後面，用明確排除句**：`no drums`, `no auto-tune`, `exclude rap`，或進階模式用 **Exclude styles** 欄。
- **v4.5+ 寫法 ≠ 堆關鍵字**：官方說 v4.5「更接近編劇而非節拍標籤」，吃 metaphor / 地點 / 場景 / 情緒的敘事式描述。但別過頭 — 仍要保留明確 genre / BPM / 樂器 anchor。

### 進階：分類 meta tag（v4.5+ 可放 Style 欄，精度更高）

v4.5 起支援**帶分類前綴**的方括號 tag，比裸關鍵字更精準：

```
[Genre: dark synthwave] [Mood: tense] [Energy: building]
[Vocalist: breathy female] [Instrument: analog Moog bass]
[Texture: warm tape saturation]
```

常見分類：`[Genre: ]` `[Style: ]` `[Mood: ]` `[Energy: ]` `[Texture: ]` `[Instrument: X (qualifier)]` `[Vocalist: ]`。**(部分為社群整理，非全部官方明列，效果以實測為準)**

### Style tag 實用字典（節錄）

**Genre / Subgenre：**
dark synthwave / retrowave / city pop / J-pop / K-ballad / nu-disco /
post-punk / shoegaze / dream pop / bedroom pop / lo-fi hip hop / trap
soul / afrobeats / amapiano / reggaeton / EDM big room / dubstep / drum &
bass / UK garage / chillwave / ambient / neoclassical / cinematic
orchestral / epic trailer / chiptune / math rock / midwest emo / neosoul

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

**Production（混音語彙，v5 強項）：**
lo-fi tape saturation / gated reverb / side-chained pads / filter sweeps /
analog warmth / pristine digital / vintage 1980s / modern punchy / wall of
sound / minimalist sparse / tube compression / mono bass / ghost snares /
wide stereo field / dual-tracked vocal

---

## 3. Lyrics 欄 — 結構 metatags

**必須用方括號**。寫 `Verse:` 會被當成歌詞唱出來。**Meta tag 在每段「段落切換處」與開頭最有效**。

### 必備結構 tag
- `[Intro]`（可加樂器：`[Intro: acoustic guitar]`）
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

### 人聲/情緒 tag（v5 起很敏感）
- `[Male Vocal]` / `[Female Vocal]`
- `[Whisper]` / `[Shout]` / `[Falsetto]` / `[Spoken]`
- `[Harmony]` / `[Ad-libs]` / `[Backing Vocals]`
- `[Instrumental]`
- `[Beat Drop]`

### 語言 tag（混語必備）
- `[Chinese Verse]`, `[English Chorus]`, `[Japanese]`, `[Korean]`

### 用量上限（避免 AI 混亂）
- Genre **1-2 個**、Instrument **2-3 個**、Mood/Energy **1-2 個**、結構 tag 每段切換各一個。
- 樂器 tag **超過 3-4 個**會讓模型輸出不穩。

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

---

## 4. 進階 prompt 技巧（Suno 專屬）

### 4.1 Top-anchor 技巧（鎖住整首風格）

**把最重要的 1-2 句風格/人聲指示放在 Lyrics 最前面**，Suno 會用它鎖住整首：

```
[A dreamy female vocal with subtle reverb, intimate bedroom pop, 68 BPM]

[Verse 1]
...
```

實測有效的 anchor 範例：`[C minor ballad, 68 BPM, dual-tracked breathy female lead, lo-fi bedroom pop intimate]`

### 4.2 段內局部提示（per-section direction）

每段開頭用括號給「演出指示」，控制動態起伏：
```
[Verse 1]
(female vocal, whispered, sparse)
...
[Chorus]
(full band enters, harmony on "夜", soaring)
...
[Bridge]
(female vocal, spoken half-whispered)
...
```

### 4.3 結構決定長度（重要）

Suno **不限定固定長度**，依歌詞 metatag 結構自動延長。
- 完整 5-part 結構（Intro / V1 / PC / C / V2 / PC / C / Bridge / Final C / Outro / End）→ 實測可跑到 **4-5 分鐘**。
- 只寫 Verse + Chorus → 可能只有 1-2 分鐘。
- **想要完整歌 = 把所有 metatags 寫齊。**

### 4.4 Voices（前 Personas）一致性

- 在某首歌上選 **Create Persona / Voice** → 存成可重用的「聲線指紋」。
- 新歌呼叫同一 Voice → **跨歌保持人聲一致**（建「品牌 vocalist」用）。
- v5.5 起 Voices 還能**捕捉你自己上傳/錄的聲音**。
- 全部 Voices 在 **Voices 分頁**。

### 4.5 Custom Models（v5.5，Pro/Premier）

- 上傳**你在 Suno 外做的曲子** → 微調出「更像你」的 v5.5 變體模型（每人最多 3 個）。
- 與 Voices 差異：Voices 控**人聲**，Custom Model 控**整體曲風/聲音 DNA**。

### 4.6 Prompt Enhancement Helper（不熟術語救星）

Style 欄輸入簡單 genre → 按 **Enhance** → Suno 自動擴寫成詳細專業語彙再生成。適合不熟音樂術語的使用者。

### 4.7 進階模式 sliders（More Options）

- **Vocal Gender:** Male / Female
- **Lyrics Mode:** Manual（自己寫）/ Auto（Suno 生）/ ReMi（AI 歌詞模型）
- **Weirdness**（0-100%）：低=貼 prompt，高=自由發揮
- **Style Influence**（0-100%）：低=模型自由，高=嚴格照 style prompt
- **Exclude styles**：放 negative（比句尾 `no xxx` 更乾淨）

---

## 5. 進階功能地圖（Personas/Voices · Stems · Covers · Extend · Remaster · Studio）

| 功能 | 用途 | 重點 / tier |
|---|---|---|
| **Voices**（前 Personas）| 存人聲指紋 → 套到新歌，跨歌一致 | v4.5+；Voices 分頁 |
| **Covers** | 上傳**你自己的音檔** → 給 prompt 改成新曲風，**保留旋律** | v4.5+ |
| **Extend** | 從既有片段往後續作（intelligent extend 保結構）| v4.5+；Covers 也可被 Extend 超過 4 分鐘 |
| **Remaster** | 舊版（v3/v4）曲子升到新音質；或同結構做**細微變體** refine 音色 | v4+ |
| **ReMi** | AI **歌詞**生成模型（pronounced「ray-me」），Custom mode Beta | v4+ |
| **Stems（分軌）** | 把任一曲拆成 **最多 12 軌**（vocals/drums/bass/其他），輸出**時間對齊 WAV** 進 DAW | v5；30-60 秒處理 |
| **Studio（生成式 DAW）** | 瀏覽器多軌 timeline：分軌、6-band 參數 EQ、Warp Markers 改時序、Remove FX、Alternates 換段、Loops（直接生 4-bar loop / impact swell）、stem multitrack 匯出 | **Premier**（v5）；2026-02 加 Warp/RemoveFX/Alternates/Time Signature |
| **Hooks** | 專生 **~30 秒 hook**（品牌主題曲 / 廣告短片），高密度記憶點 | sidebar `+Create` |
| **Genre Mashup** | 直接寫混搭，如 `midwest emo + neosoul`、`trap soul + jazz fusion` | v4.5 理解細緻 |
| **Add Vocals / Add Instrumentals** | 純樂曲加人聲 / acapella 加伴奏 | v4.5+ co-creation |

### Studio 補充（Premier）

- **Loops 生成**取代「切 3 分鐘整曲找 4-bar」：直接 prompt `90bpm Lo-Fi Drum Loop` / `Cinematic Impact Swell`。
- 開任一生成曲進編輯 → Studio 自動啟用多軌環境。
- **Stem → Timeline**：點每軌旁的箭頭 icon 加進 timeline。
- **匯出**：Multitrack 可把所有軌當 stems 在你的 Studio mix context 下匯出，最大彈性給外部 DAW（Ableton / Logic / FL）。

---

## 6. 進階 Recipe

### 6.1 廣告配樂 30 秒（instrumental bed）

目標：可墊在 voiceover 下、結構乾淨、loop 友善。

```
Style:
Uplifting modern corporate pop, optimistic and clean, no lead vocals,
bright plucked synth, four-on-the-floor kick, claps, warm sub bass,
shimmering bell arps, subtle string pad swells, 120 BPM, radio-ready mix,
wide stereo, leaves headroom for voiceover

Lyrics:
[Intro]
(soft pluck + pad, 4 bars)
[Build]
(add claps + bass, rising filter)
[Drop / Main Theme]
(full arrangement, memorable hook, 8 bars)
[Outro]
(strip to pad, clean ending)
[End]
```

要點：`no lead vocals` + `leaves headroom for voiceover`；結構只留 Intro/Build/Drop/Outro 控在 30s 上下（短結構=短歌）；做完用 **Stems** 拆掉不要的軌。

### 6.2 品牌 Jingle（5-10 秒記憶點）

目標：極短、唱出品牌名/標語、一聽就記得。用 **Hooks** 功能最佳。

```
Style:
Catchy retro pop jingle, warm and friendly, single bright female vocal,
ukulele, hand claps, glockenspiel, whistle hook, 110 BPM, vintage radio jingle

Lyrics:
[Hook]
(female vocal, cheerful, single line)
<品牌標語，6-8 字，押韻>
[End]
(final chord + whistle)
```

要點：只寫 `[Hook]` + `[End]`；歌詞**一句**就好；用 Voices 鎖定同一聲線讓系列 jingle 一致。**禁止寫真實品牌名以外的版權 IP / 藝人名**（侵權降級）。

### 6.3 中文情歌（Mandopop ballad，完整製作）

歌詞中文、**風格描述用英文**（Style 欄對英文最準）。

```
Style:
Mandopop ballad with modern R&B production, male vocal with gentle falsetto,
muted Rhodes MK II electric piano, fingerpicked nylon guitar, subtle strings,
brushed kit, upright bass, warm tube compression, 80 BPM, melancholic yet
hopeful, no auto-tune, no 808

Lyrics:
[C minor ballad, 80 BPM, gentle male falsetto, intimate]

[Intro]
(soft piano)

[Verse 1]
[Male Vocal, gentle]
那年夏天的蟬鳴
還在耳邊迴響
你說過的晚安
成為最後的光

[Pre-Chorus]
(strings enter)
時間走得太快
我還沒學會說再見

[Chorus]
[Full band, emotional]
如果時間能倒流
我願意再等一次
哪怕只是一眼
也是一輩子

[Verse 2]
...

[Bridge]
[Male Vocal, spoken half-whispered]
...

[Chorus]
(with harmonies + ad-libs)
...

[Outro]
(fade out, single piano note)
[End]
```

要點：中文每行 **6-8 字** 斷句最穩；情感濃烈的字（離別/星光/夜雨）表現好；雙語混唱用 `[Chinese Verse]` + `[English Chorus]`。

### 6.4 完整專輯工作流（Voices + Covers + Extend + Stems）

```
Step 1：用完整專業 prompt 做 1 首歌（10 credits / 2 版）
Step 2：挑最好 version → Create Voice（存聲線）
Step 3：同 Voice + 新歌詞 → 跑 3-5 首，整張專輯一致聲線
Step 4：每首 Extend 到 3-4 分鐘
Step 5：Premier 用 Stems 拆 12 軌 → Studio / 外部 DAW 自己混音母帶
```

---

## 7. 5 風格速查範例

**1. Dark Synthwave**
```
Style: Dark synthwave with retro funk, moody, female vocal sultry and whispered,
analog Moog bass, gated reverb snare, side-chained pads, 98 BPM, cinematic
Lyrics:
[Intro] (synth swell)
[Verse 1] [Female Vocal, whispered]
Neon bleeding through the rain / You left your jacket on the chair ...
```

**2. Lo-fi Hip Hop**
```
Style: Lo-fi hip hop instrumental with jazz samples, warm vinyl crackle,
dusty boom bap drums, upright bass, muted trumpet, 75 BPM, nostalgic study vibes, no vocals
Lyrics:
[Instrumental]
```

**3. Epic Trailer**
```
Style: Cinematic epic orchestral trailer, massive choir swells, taiko drums,
brass stabs, rising tension into heroic climax, 120 BPM, dramatic and heroic
Lyrics:
[Instrumental, rising tension]
```
（⚠️ 寫風格詞，**不要寫作曲家本名**如 Hans Zimmer — 侵權降級）

**4. Shibuya-kei / J-pop**
```
Style: Shibuya-kei meets modern J-pop, bright and playful, female vocal
clean and cute, bossa nova guitar, retro samples, vibraphone, 108 BPM
Lyrics:
[Intro] (handclaps, bossa guitar)
[Verse 1] [Female Vocal] (Japanese lyrics here) ...
```

**5. Indie Folk**
```
Style: Intimate indie folk, male vocal raspy and heartfelt, fingerpicked
acoustic guitar, subtle harmonium, gentle brushed drums, 72 BPM, bittersweet
Lyrics:
[Intro] (single acoustic guitar)
[Verse 1] [Male Vocal, soft]
Morning light through the broken blind / Coffee cold on the windowsill ...
[Chorus] [Harmonies enter] ...
```

---

## 8. 常見失敗 + 修法

| 失敗症狀 | 根因 | 修法 |
|---|---|---|
| 出來一團糟、tag 亂套 | **Style 欄塞了歌詞** | 歌詞只進 Lyrics 欄 |
| 「Verse」「Chorus」被唱出來 | Lyrics 用 `Verse:` **沒方括號** | 一律 `[Verse 1]` 方括號 |
| 突然截斷 / 無限 loop | 漏 `[Outro]` / `[End]` | 結尾補 `[Outro]` + `[End]` |
| 混音擠爆、糊 | 一首塞 **10+ 樂器** | 砍到 3-6 個；多餘的事後用 Stems 拆 |
| Negative 沒生效 | `no xxx` 放在 **Style 中間** | 放句尾，或用 Exclude styles 欄 |
| 中文歌曲風跑歪 | Style 用**純中文**描述 | 曲風用**英文**，只有歌詞用中文 |
| 情緒模糊不定 | 同時給**衝突 mood**（`happy and melancholic`）| 選一個 dominant |
| 中文斷句歪掉 | 每行 **>12 字** | 中文每行 6-8 字 |
| 只生出 1-2 分鐘 | 歌詞**結構太少** | 補齊 Intro/Verse/PC/Chorus/Bridge/Outro |
| 想要 WAV / stems 卻沒有 | **免費 tier** 限 MP3 | WAV / 12 軌 stems / Video 需 Pro/Premier |
| 換 model 後 prompt 失效？ | 誤以為 v5.5 改了語法 | **v5 tags 在 v5.5 完全相容**，不用改 |
| 整首被降級 / 模糊 | prompt 含**版權 IP / 藝人 / 作曲家本名** | 只寫曲風（`dramatic orchestral` 不寫人名）|

---

## 9. 中文歌技巧（彙整）

- **歌詞用中文、風格描述用英文**（Style 欄對英文最準）。
- 中文每行 **6-8 字** 最穩，>12 字斷句會歪。
- 情感濃烈字（離別 / 星光 / 夜雨）Suno 表現不錯。
- 雙語混唱：`[Chinese Verse]` + `[English Chorus]`。
- 視覺/在地意象（蟬鳴 / 晚安 / 窗台）在中文 ballad 效果好。

---

## 10. 價格與商用權（2026，待官方頁複核）

| 方案 | 月費 | credits | 商用 | 重點 |
|---|---|---|---|---|
| **Basic / Free** | $0 | 50/天（≈10 首）| ❌ 非商用 | model `v4.5-all`，MP3 only |
| **Pro** | $10（年繳 $8）| 2,500/月（≈500 首）| ✅ | v5 model、commercial、WAV/stems/video |
| **Premier** | $30（年繳 $24）| 10,000/月（≈2,000 首）| ✅ | + **Suno Studio DAW**、early access |

- **credits 每日/每月不結轉**；加購 top-up credits 不過期但需有效訂閱才能用。
- 商用權**只涵蓋訂閱期間做的歌**（退訂前產出的歌之權利請複查官方條款）。
- **Studio↔Pro/Premier**：多數來源說 Studio 綁 Premier；少數說 Pro 也能開編輯。送出實際操作前以官方 Pricing 頁為準 **(待驗證)**。

---

## 11. Auto-Pilot 進 Suno 時

**Intent Parser 特化：**
- 偵測「歌 / 音樂 / BGM / 配樂 / jingle」→ 強制平台 Suno。
- 解析「中文 / 英文 / 日文」→ 歌詞語言（曲風描述固定英文）。
- 解析「幾秒/幾分鐘」→ 用**結構長度**控制（短結構=短歌，非設時長 slider）。
- 解析風格（lo-fi / pop / rock / ballad / ambient / hip-hop / cinematic）。
- 偵測「品牌 / 廣告 / 標語」→ 考慮 **Hooks**（30s）或極短 `[Hook]` 結構。

**硬規則：**
- **Prompt 自動拆成 Style + Lyrics 兩欄**，絕不混。
- **禁寫版權 IP / 藝人 / 作曲家本名**（侵權降級），只寫曲風語彙。
- 站點操作 SOP / 座標 / 清空欄位手法見 `../automation/site-profiles/suno.md`。

---

## 連結

**官方：**
- 官網：https://suno.com/
- Pricing：https://suno.com/pricing
- v5.5 公告（Voices / Custom Models / My Taste）：https://suno.com/blog/v5-5
- v5.5 更新說明（Help）：https://help.suno.com/en/articles/11362305
- Introducing v4.5（blog）：https://suno.com/blog/introducing-v4-5
- Introducing v4（Remaster + ReMi）：https://suno.com/blog/v4
- Remaster（Help）：https://help.suno.com/en/articles/8105281
- Studio 介紹（Help）：https://help.suno.com/en/articles/7940161
- Studio 匯出（Help）：https://help.suno.com/en/articles/8128193

**進階指南（第三方）：**
- v5.5 Reference: Meta Tags / Style-of-Music（Blake Crosley）：https://blakecrosley.com/guides/suno
- v5.5 Guide: Voices / Custom Models / My Taste（HookGenius）：https://hookgenius.app/learn/suno-v5-5-guide/
- v5.5 Prompts: what works now（Song AI Farm）：https://www.songaifarm.com/blog/suno-prompts-v5-5
- Suno Studio Tutorial 2026（HookGenius）：https://hookgenius.app/learn/suno-studio-tutorial/
- Suno Studio Guide 2026（Undetectr）：https://undetectr.com/blog/suno-studio-guide
- Stems → DAW（Ableton/Logic/FL，Undetectr）：https://undetectr.com/blog/suno-stems-daw-workflow
- Ultimate v4.5 How-To: Personas/Extend/Cover（Civitai）：https://civitai.com/articles/14849
- Covers Guide 2026（Jack Righteous）：https://jackrighteous.com/en-us/blogs/guides-using-suno-ai-music-creation/suno-ai-covers-guide-v4-transform-your-songs-by-style
- Meta Tags & Song Structure（Jack Righteous）：https://jackrighteous.com/en-us/pages/suno-ai-meta-tags-guide
- 500+ Metatags（OpenMusicPrompt）：https://openmusicprompt.com/blog/suno-ai-metatags-guide
- 300+ Style Tags 分類庫（HookGenius）：https://hookgenius.app/learn/suno-style-tags-guide/
- Free vs Pro vs Premier 2026（HookGenius）：https://hookgenius.app/learn/suno-free-vs-pro-comparison/
- v5 Review（Undetectr）：https://undetectr.com/blog/suno-v5-review

**站內操作 SOP：** `../automation/site-profiles/suno.md`
