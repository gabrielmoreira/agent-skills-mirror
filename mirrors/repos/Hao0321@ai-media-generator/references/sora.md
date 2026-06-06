# OpenAI Sora 2 / Sora 2 Pro

官方 `https://openai.com/sora/`。OpenAI 的文生影片旗艦，2026 時點主力 **Sora 2 / Sora 2 Pro**，首創與 **原生同步音訊** + **社群 App (類 TikTok feed)** 整合，標誌功能是 **Cameo（客串）**。

---

## ⚠️ 平台狀態警告（2026-06，最高優先）

**OpenAI 已宣布全面停運 Sora。先看這段再決定要不要用。**

| 里程碑 | 日期 | 內容 |
|---|---|---|
| 停運公告 | **2026-03-24** | OpenAI 經 X 宣布 Sora 退役 |
| Web / App 關閉 | **2026-04-26** | `sora.com` + iOS/Android App 全部停止 |
| API 關閉 | **2026-09-24** | `sora-2` / `sora-2-pro` 端點下線，第三方代理一併失效 |
| 資料刪除 | 上述日期後 | 帳號與生成影片**永久刪除，無保證救援窗** |

**對本 skill 的意涵：**
- ❌ **官方 `sora.com` Web / App 自 2026-04-26 起無法操作** → site-profile 自動化流程已失效，不要嘗試導航/登入。
- ⚠️ **唯一殘存路徑**：第三方代理（fal.ai / Replicate / Azure AI Foundry / 各家 reseller API）在 **API sunset (2026-09-24) 前**仍可能跑 `sora-2` / `sora-2-pro`。要用 Sora **只剩這條**，且時效有限。
- ✅ **本檔的 prompt 工程仍有價值**：Sora 的「分鏡卡」思維、shot list、物理擬真語彙是**通用技能**，可平移到 Veo / Kling / Seedance，也適用上述代理 API。
- 👉 **新專案的預設建議**：改用本 skill 其他現役模型（Veo 3.1 / Kling 2.6 / Seedance）。把 Sora 當「歷史最佳實踐參考」+「代理 API 限時可用」看待。

> 後續章節保留完整 Sora 2 能力與技巧，供 (a) 代理 API 限時使用 (b) prompt craft 平移其他模型。涉及官方 App 專屬功能（feed / leaderboard / cameo 建立 UI）已隨 App 關閉失效，會標註。

---

## 版本能力矩陣（Sora 2 vs 2 Pro）

| 維度 | Sora 2 | Sora 2 Pro |
|---|---|---|
| 取得 | ChatGPT Plus ($20/月) | ChatGPT Pro ($200/月) |
| 解析度 | 720p (1280×720 / 720×1280) | 720p / 1024p / **1080p (1920×1080)** |
| 時長（Web/App） | 4 / 8 / 12s | 4 / 8 / 12s（UI 端） |
| 時長（API） | 4 / 8 / 12s | 10 / 15 / **25s**（25s **不支援** 1080p，會降階）(待驗證 UI 是否同步到 25s) |
| 原生音訊 | ✅ 對白 + SFX + ambient + 配樂 | ✅ 同左，品質更穩 |
| T2V / I2V | ✅ 文生 + 圖生（首幀鎖定） | ✅ 同左 |
| 物理擬真 | 強（Sora 2 主打賣點） | 最強，動作/材質更穩 |
| Cameo / Remix / Storyboard | ✅ | ✅ |
| 浮水印 | 強制可見浮水印 + C2PA metadata | **可移除可見浮水印**（Pro 專屬，C2PA 仍保留） |
| 月配額 | 有限（**日 rolling cap ~30 credits** 後限速）| 高/近無限，但仍有日節流 |

**API 定價（Standard，停運前）**：Sora 2 Pro `$0.30/s (720p)` / `$0.50/s (1024p)` / `$0.70/s (1080p)`；Batch tier 約半價（latency 最長 24h）。一支失敗的 25s 1080p batch 仍計費（~$8.75）。Sora 2（非 Pro）更便宜。(數字來自第三方彙整，**待官方驗證**)

**版本決策：**
```
要 1080p / 最穩物理 / 去浮水印 → Sora 2 Pro（需 Pro 訂閱或代理 Pro API）
只要看 demo、預算敏感、720p 可接受 → Sora 2
要 >12s 長片段 → 只有 Pro API（10/15/25s），且 25s 犧牲解析度
官方 UI 已關 → 一律走代理 API（時效到 2026-09-24）
```

---

## 核心哲學

OpenAI 官方指南的核心類比：**把自己當成在對沒看過腳本的攝影指導 (DP) 簡報**。不講清楚，他會自己補 — 結果可能不是你要的。

> **Prompt = 一張分鏡卡：鏡頭景別、景深、動作節拍、燈光、調色。**

兩種極端，刻意選邊：
- **長 prompt（細節滿）= 高控制、低隨機** → 客戶交付、要可重現時用。
- **短 prompt = 低控制、高創意自由** → 探索、想要意外美感時用。

官方金句：**「把 prompt 當許願清單，不是合約」** — 留白讓模型發揮，鎖死讓模型聽話，看你要哪個。

---

## Prompt 公式（官方 Universal Template）

Sora 官方推「**散文 + 分區塊**」結構，比單行更可控：

```
[散文場景描述：角色、服裝、場景、天氣、氛圍，平鋪直敘。]

Cinematography:
  Camera shot: [景別 + 角度]
  Depth of field: [shallow / deep]
  Lens / style cues: [anamorphic / handheld / 32mm spherical...]
  Mood: [整體基調]

Actions:
  - [Beat 1：清楚、單一的動作]
  - [Beat 2：另一個明確節拍]
  - [Beat 3：動作或對白]

Dialogue:
  [簡短自然、配合片長的台詞]
```

**單行緊湊版（短片段也夠用）：**
```
[Framing + Lens] + [Subject + Beats] + [Lighting] + [Palette / Style] + (可選)[Audio / Dialogue]
```

**範例（單行）：**
```
Medium close-up, 50mm, shallow depth of field. A woman in a red raincoat
stands on a wooden pier, slowly raising her hood as the first drops of rain
fall. She looks out over the gray ocean. Overcast soft light, cool
desaturated palette except for her red coat. Melancholic, cinematic, 35mm
film grain. SFX: light rain on wood, distant seagulls.
```

---

## Sora 專屬進階 Prompt 技巧

### A. 物理擬真是 Sora 2 的主場 → 餵「可被物理模擬的動作」

Sora 2 賣點是 world-physics（重量、慣性、流體、布料、彈跳）。**要讓它發揮，動作要寫成有物理後果的**，而不是抽象形容。

- ✅ `the basketball hits the rim, bounces twice, and rolls off the backboard`（有碰撞、衰減）
- ✅ `she sets the glass down too hard; coffee sloshes over the rim`（液體慣性）
- ✅ `the cape catches the wind and snaps taut behind him`（布料受力）
- ❌ `cool dynamic action`（無物理可模擬 → 模型亂猜）

**但避開已知脆弱物理**（見失敗章）：精細手指互動（拉拉鍊、扣鈕扣）、咬痕等「因果型」細節、鏡面反射、極快 whip-pan。

### B. 「One Shot, One Thing」— 一鏡一事

官方鐵律：**一個鏡頭 = 一個運鏡 + 一個主體動作**。塞太多會 motion unreadable。

- 弱：`Actor walks across the room.`（含糊）
- 強：`Actor takes four steps to the window, pauses, and pulls the curtain in the final second.`（有節拍、有計數、落在時間軸上）

把動作寫成 **beats / counts（小步、手勢、停頓）**，模型才知道怎麼分配到秒數。

### C. Shot List / 多鏡寫法

多鏡序列要 **每個 shot block 互相獨立**（各自一個 camera setup + 一個動作 + 一套燈光），這樣可單獨生成也可串接：

```
Beat 1 — Wide establishing, eye level: rooftop at night, city lights below.
Beat 2 — Medium tracking, slight angle from behind: the runner leaps between
         buildings, cape flowing.
Beat 3 — Low-angle close-up: landing, dust rising in the final second.
```

敘事節拍語法 Sora 也吃：`starts wide, then cuts to medium, ends on close-up`。

### D. 進階電影攝影語彙（Sora 對這些特別敏銳）

Sora 解析真實器材/濾鏡描述，越「劇組」越穩：
- 鏡頭：`32mm / 50mm spherical primes`、`anamorphic 2.0x lens`、`anamorphic 2.39:1, lens flares`
- 景深：`shallow focus (sharp on subject, blurred background)`
- 快門/感光：`180° shutter; digital capture emulating 65mm`
- 濾鏡：`Black Pro-Mist 1/4`
- 運鏡：`slow push-in toward the subject's eyes`、`handheld eng camera`、`aerial wide shot, slight downward angle`、`bird's-eye view, slowly rotating`

### E. Cameo 在 prompt 裡的用法

Cameo（見功能地圖）建好後，在 prompt 引用該角色，**只描述場景與動作，不重述長相**（長相由 cameo 鎖定）：
```
[@MyCameo] sits at a ramen counter in a neon-lit Tokyo alley, steam rising
from the bowl. Medium close-up, 50mm, shallow DoF. He blows on the noodles,
then looks up as the door chimes. Warm practical lighting, teal night exterior.
```
保持 **identity 描述一致**（同一套措辭）可降低跨鏡 identity drift。

### F. Remix 改寫策略（核心：nudge，不是 gamble）

Remix = 對滿意結果**微調一個變數**，其餘不動。官方原則「一次改一件」：

```
"same shot, switch to 85mm"                       # 只改鏡頭
"same lighting, new palette: teal, sand, rust"    # 只改調色
"same composition, change wardrobe to white suit" # 只改服裝
```
**句型 = `same X, new/switch Y`**，明講你改什麼。先把滿意結果 pin 起來再 Remix。

**問題鏡頭的 Remix 救援法（官方）**：
1. **Strip back** — 凍結運鏡、簡化動作、清空背景。
2. **Verify** — 確認基底對了。
3. **Iterate** — 一層一層加回複雜度，每加一層就驗。

---

## 進階功能地圖（用途 + 何時用 + 現狀）

> ⚠️ 標 🔴 = 官方 App/Web 專屬，2026-04-26 後已隨平台關閉失效；標 🟡 = 在代理 API/SDK 上可能仍可用至 2026-09-24。

### 1. Cameo — 客串（殺手級功能）🟡🔴

把「特定身分」鎖進任何場景，跨鏡保持一致。**Sora 最大差異化**。分兩種：

| 類型 | 對象 | 建立方式 | 同意機制 |
|---|---|---|---|
| **Personal Cameo** | **真人本人**（你/經同意的朋友）| App 內錄一段 video+audio 驗證身分與長相 | opt-in，需本人；可設誰能用、**可撤銷**、可移除含你的影片 |
| **Character Cameo** | **寵物 / 物件 / 塗鴉 / 原創角色**（**非真人**）| Profile → Create cameo → 上傳幾秒影片（可用舊 Sora 影片當素材）| 權限：Only me / People I approve / Mutuals / Everyone / Everyone（排除特定人）|

- **何時用**：同一角色/吉祥物/寵物要出現在多支影片、做品牌人物、系列短劇。建一次永久重用 → 省掉每支重描長相。
- **真人 ≠ Character Cameo**：描繪真人只能走 Personal Cameo 同意流程，不能用 Character Cameo 繞過。
- 🔴 **建立 UI 已隨 App 關閉**；既有 cameo 能否在代理 API 引用 **待驗證**。

### 2. Remix — 改寫變奏 🟡

已有滿意結果，改**一個**變數，其餘不變。用途見上節 F。**最常用、最安全的迭代工具**。

### 3. Storyboard — 分鏡編排 🟡🔴

逐格（scene card）精確指定每段的輸入：可從一句概念自動生草稿，再逐格編輯運鏡/角色/光線。
- **每格寫法 = 短**：只描述**那一格的變化**，不要每格寫完整 prompt（會互相打架）。
- 每格可帶自己的 audio（dialogue / SFX / ambient / music）。
- **何時用**：多鏡敘事、要精準控制節奏與連續性、要跨鏡沿用 cameo 角色。
- 實測回報：跨 3 鏡能保住同一髮型/服裝/可辨識的同一張臉。
- 🔴 互動式 storyboard 介面屬 App 功能。

### 4. Blend — 融合兩影片 🟡

把兩段素材合成，prompt 講清楚兩邊各提供什麼：
```
Blend A with B. A is the location and lighting. B is the subject and motion.
```
- **何時用**：A 場景/氛圍 + B 主體/表演，要合成一鏡。

### 5. Stitch / Re-cut — 拼接 / 重剪 🟡🔴

- **Stitch**：把多段 clip 串接成更長連續影片。
- **Re-cut**：重排既有片段順序，或切出特定段落 loop。
- **何時用**：超過單次時長上限、要組長片、要調剪輯節奏。

### 6. Loop — 無縫循環 🟡🔴

自動把片段變首尾無縫的 loopable。**何時用**：背景動畫、社群貼文循環、ambient 視覺。

### 7. Style Presets 🟡🔴

官方風格預設（animation / realistic / cinematic / retro / anime…），Pro 有更多。快速定調，不必每次手寫風格 token。

### 8. Social / Feed / Leaderboard（Sora App）🔴

類 TikTok 演算法 feed、follow 好友、remix 別人作品（需授權）、**leaderboard**（最多 remix 的 clip、最多人用的 cameo）。**已隨 App 關閉，純歷史記錄。**

### 9. Image-to-Video（首幀鎖定）🟡

上傳參考圖（jpeg/png/webp），鎖定角色設計/服裝/場景陳設/美學當**首幀錨點**，文字 prompt 定義「接下來發生什麼」。**圖的解析度需對齊目標影片解析度**。

---

## 音訊（Sora 2 原生）

用法類 Veo：
- **對白**：引號 `"..."`；Storyboard/API 用獨立 Dialogue 區塊 + 角色標籤。台詞**簡短、配合片長**（4s 約一兩句來回）。
- **SFX**：`SFX: ...`
- **Ambient**：直接與畫面並列描述（`The hum of espresso machines forms the background.`）
- **音樂**：`Soundtrack: [風格]`（寫風格，**勿寫具體曲名/作曲家**會侵權降級）
- **Diegetic 優先**：官方範例偏好「畫面內真實聲源」勝過外加配樂/foley。

市場共識（2026）：**對白/口型 Veo 3.1 仍略領先**，**視覺一致性與物理 Sora 更好**。

---

## 進階 Recipe

### Recipe 1 — 電影感 noir 獨白（單鏡、滿細節、高控制）
```
Interior of a parked car at night, rain streaming down the windshield. A weary
detective stares at a photograph in his hand, neon-pink signage reflecting on
his face.

Cinematography:
  Camera shot: medium close-up, slight angle from the passenger side
  Depth of field: shallow (sharp on his eyes, blurred rain behind)
  Lens / style: 85mm spherical prime, Black Pro-Mist 1/4, 35mm film grain
  Mood: melancholic noir, teal-and-magenta grade

Actions:
  - He exhales slowly, breath fogging slightly
  - He turns the photo over in the final two seconds

Dialogue:
  - Detective: "I should have known."

Audio: SFX rain on windshield, distant thunder. Soundtrack: sparse piano with
low synth drone, -18LUFS, no added foley.
```

### Recipe 2 — 物理動作三節拍（測 Sora 2 物理強項）
```
Rooftop at night, city lights far below, a runner in a flowing cape.

Cinematography:
  Anamorphic 2.0x lens, handheld eng energy, cool blue palette with orange
  city accents, cinematic.

Actions:
  - Beat 1 (wide establishing, eye level): runner sprints toward the ledge
  - Beat 2 (medium tracking from behind): he leaps; the cape snaps taut and
    catches the wind mid-air
  - Beat 3 (low-angle close-up): he lands hard, knees absorbing the impact,
    dust kicking up in the final second

Audio: SFX wind rush, fabric flap, a heavy landing thud. Soundtrack: pulsing
low synth.
```

### Recipe 3 — Cameo 角色 + Remix 迭代（系列短劇工作流）
```
# Step 1：建 Character Cameo（寵物柯基，一次性，上傳幾秒影片）
# Step 2：基準鏡頭
[@CorgiCameo] in a tiny detective trench coat sits behind a desk in a dim
office, a single desk lamp glowing. Medium close-up, 50mm, shallow DoF, warm
practical key + cool window spill, film-noir mood. He tilts his head as the
phone rings.

# Step 3：Remix 變奏（每次只改一件）
"same shot, switch to 35mm wider framing"
"same composition, new palette: amber and deep green"
"same setup, change time to early morning, soft cool light"
```

### Recipe 4 —（簡短，讓 Sora 自由發揮）
```
A paper crane unfolds itself in reverse on a white desk. Soft natural light.
```

---

## 常見失敗 + 修法

| 失敗 | 原因 | 修法 |
|---|---|---|
| **文字/招牌/Logo 全糊** | Sora **架構性弱點**，非 prompt 問題 | 不要靠 Sora 出可讀文字；文字/logo **後製疊上**。`a sign that says "X"` 也救不了 |
| **手指/拉鍊/倒液體變形** | 精細手部與「因果型」互動脆弱 | 避開特寫精細手部動作；鏡頭拉遠、簡化互動 |
| **跨鏡 identity drift（同人變臉）** | 尤其戲劇性燈光下 | 用 **Cameo** 鎖身分；identity 描述用**完全相同措辭** |
| **鏡面反射/倒影出錯** | 空間推理弱點 | 避開鏡子/水面為主體的構圖，或弱化反射 |
| **快速 whip-pan / 急 zoom 扭曲** | 快速運鏡觸發 warping | 改慢速 push-in / dolly；一鏡一運鏡 |
| **Remix 一次改太多 → 整個變掉** | 違反「一次一變數」 | 嚴守 `same X, new Y`，一次一件 |
| **Storyboard 每格寫完整 prompt → 互打架** | 各格資訊衝突 | 每格只寫「**這格的變化**」 |
| **細節太少卻期待高品質** | Sora 不讀心 | 補 framing + DoF + lighting 錨點；細節進、細節出 |
| **動作含糊 motion unreadable** | 一鏡塞太多事 | 收斂成「一運鏡 + 一動作」，寫成 beats |
| **自相矛盾指令**（`handheld` + `locked camera`）| 衝突 | 二選一 |
| **對白寫成敘述**（`she says she has to leave`）| 不會唸出來 | 用引號 `She says, "I have to leave."` |
| **25s 卻要 1080p** | 官方限制 25s 不支援 HD | 要 1080p 選 10s/15s；要 25s 接受降階 |
| **音訊層疊太多**（對白+SFX+樂+ambient+旁白）| 混亂 | 挑 2–3 層，diegetic 優先 |

---

## 連結

**官方**
- OpenAI Sora 2 發表：https://openai.com/index/sora-2/
- **Sora 停運說明（必讀）**：https://help.openai.com/en/articles/20001152-what-to-know-about-the-sora-discontinuation
- Sora Release Notes：https://help.openai.com/en/articles/12593142-sora-release-notes
- Cameo 使用（generating content with cameos）：https://help.openai.com/en/articles/12435986-generating-content-with-cameos
- 官方 Sora 2 Prompting Guide (cookbook)：https://cookbook.openai.com/examples/sora/sora2_prompting_guide
- 開發者版 cookbook：https://developers.openai.com/cookbook/examples/sora/sora2_prompting_guide
- Creating videos with Sora：https://help.openai.com/en/articles/12460853-creating-videos-with-sora
- Generating videos on Sora：https://help.openai.com/en/articles/9957612-generating-videos-on-sora

**第三方 / 教學**
- Sora 2 Prompting Guide 中文鏡像：https://soratoai.com/en/docs/guides/sora-2-prompting-guide/
- fal.ai — How to write prompts for Sora 2：https://fal.ai/learn/devs/how-to-write-prompts-sora-2
- Azure AI Foundry — Sora 2 video generation：https://learn.microsoft.com/en-us/azure/foundry/openai/concepts/video-generation
- Sora 2 vs 2 Pro（MindStudio）：https://www.mindstudio.ai/blog/sora-2-vs-sora-2-pro-upgrade-worth-it
- Tips for 2026 (WaveSpeedAI)：https://wavespeed.ai/blog/posts/sora-2-prompting-tips-better-videos-2026/
- Tutorial (DataCamp)：https://www.datacamp.com/tutorial/sora-ai

> 注：官方 cookbook / help 連結在 sunset 後可能失效。中文鏡像與第三方教學保留 prompt craft 參考價值。
