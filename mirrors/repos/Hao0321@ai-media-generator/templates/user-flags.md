# User Flags — 使用者可自然語言指定的選項

**定位：** 使用者要「超傻瓜」也要能細控。本檔列出 **自然語言 flag 辨識表** — 使用者說一句話時混入這些關鍵字，auto-pilot 就 override 預設。

**用法：** auto-pilot 的 Stage 1 (Intent Parser) 除了拆 9 slot，還掃這份清單找 flag。找到就 override Stage 2 預設。

---

## 平台指定

| 使用者說 | Auto-Pilot 執行 |
|---|---|
| 「用 Flow」「用 Veo」 | Flow / Veo 3.1 |
| 「用 Kling」「Kling 3.0」 | Kling 3.0 (免費) 或 2.6 Pro (若 3.0 鎖) |
| 「用 Seedance」 | Seedance 1.0 Pro |
| 「用 Runway」 | Runway Gen-4 |
| 「用 OiiOii」 | OiiOii Story Video |
| 「Suno」「做音樂」 | Suno v5 |
| 「Midjourney」「MJ」 | Midjourney v7 |
| 「Flux」 | Flux 1.1 Pro |
| 「Nano Banana」「Gemini 圖」 | Nano Banana Pro |
| 「Seedream」「即夢」 | Seedream 4.5 |
| 「Sora」 | Sora 2 |
| 「最便宜」「免費」 | 找免費 tier (Kling 免費、Vidu 免費) |
| 「最好質量」「最頂」 | Kling 2.6 Pro / Veo 3.1 Quality / Midjourney v7 |

---

## 模型子版本

| 使用者說 | 對應 |
|---|---|
| 「Fast」「快」 | 該平台的 Fast 版 (Veo 3.1 Fast / Kling Fast 等) |
| 「Quality」「質量」「高質」 | Quality / Master / Pro 頂級版 |
| 「Lite」「輕量」 | Lite 版 (最便宜) |
| 「2.1 Master」「2.6 Pro」「3.0」 | Kling 特定版本 |
| 「v7 --raw」「原始」 | Midjourney raw mode |
| 「Kontext」 | Flux Kontext (編輯版) |

---

## 時長

| 使用者說 | 對應秒數 |
|---|---|
| 「短片」「short」 | 5-10s |
| 「5 秒 / 5s」 | 5s |
| 「8 秒」 | 8s (Veo 原生) |
| 「10 秒 / 10s」 | 10s (Kling 原生) |
| 「15 秒」 | 15s (Kling 3.0) |
| 「16 秒」 | 16s (Vidu Q3) |
| 「30 秒 / 廣告長度」 | 30s (需 extend 或多鏡剪接) |
| 「1 分鐘 / MV 長度」 | 60s+ (多鏡拼) |
| 「長片」「長一點」 | 平台最大 |

---

## 版本數量

| 使用者說 | 對應 |
|---|---|
| 「一個 / 1 個 / 單版」 | x1 (最省) |
| 「兩個 / x2 / 對比」 | x2 (預設) |
| 「三個 / x3」 | x3 |
| 「四個 / x4 / 多版比較」 | x4 (貴) |

---

## 畫面比

| 使用者說 | 對應 |
|---|---|
| 「直的 / 豎屏 / 手機 / TikTok / Reel / Shorts」 | 9:16 |
| 「橫的 / 16:9 / YouTube / 電視」 | 16:9 (預設) |
| 「方的 / 1:1 / Instagram」 | 1:1 |
| 「電影比 / 寬銀幕 / 2.39」 | 2.39:1 |
| 「直幅海報」 | 2:3 / 3:4 |

---

## 解析度 / 品質

| 使用者說 | 對應 |
|---|---|
| 「低解析 / 720p / 省」 | 720p (Kling 免費預設) |
| 「1080p / HD / 標準」 | 1080p (多數平台預設) |
| 「4K / 超高」 | 4K (Kling 3.0 Omni / Veo 3.1 Quality) |
| 「HDR / 色深」 | 支援的平台才開 |

---

## 預算 / 成本

| 使用者說 | 策略 |
|---|---|
| 「不花錢」「免費」 | 只選免費 tier，避開付費牆 |
| 「省一點」「便宜」 | Fast/Lite + x1 + 720p |
| 「中等」 | 預設組合 |
| 「不在乎錢」「最好」 | Quality + x2 + 最大解析 |
| 「$X 以內」 | 算進 cost matrix，限額內挑最好 |

---

## 風格

| 使用者說 | 自動套 |
|---|---|
| 「Ghibli」「宮崎駿」 | Studio Ghibli + Makoto Shinkai |
| 「新海誠 / Shinkai」 | Makoto Shinkai (single) |
| 「王家衛 / Wong Kar-wai」 | Christopher Doyle handheld + 霓虹 |
| 「Wes Anderson」 | 對稱粉彩 + whip pan |
| 「Nolan」「諾蘭」 | IMAX + 70mm + 冷藍 |
| 「Villeneuve」「Dune 感」 | Greig Fraser monumental |
| 「Blade Runner 感 / 賽博龐克」 | Deakins + Cinestill 800T halation |
| 「武俠」 | Kurosawa / Zhang Yimou + 竹林 |
| 「奢侈 / Chanel 感」 | 中片幅 + 自然窗光 + 莫內 |
| 「運動 / Nike 感」 | 低角 + 240fps + bleach bypass |
| 「Apple 廣告感」 | cyclorama + macro + 5600K |
| 「寫實 / photorealistic」 | Flux 1.1 Pro + Kodak Portra |
| 「動漫 / anime」 | Shinkai + Ghibli blend |
| 「卡通 / cartoon」 | Pixar 或 2D cel-shaded |
| 「lofi / 懷舊」 | Kodak 底片 + vinyl crackle |
| 「MV / 音樂影片」 | Hiro Murai / Cole Bennett 視風格 |

---

## 音訊

| 使用者說 | 啟用 |
|---|---|
| 「有對白」「要講話」 | 平台選 Veo 3.1 / Sora 2；prompt 加引號對白 |
| 「配樂 / BGM」 | prompt 加 `Soundtrack:` 或用 Suno 後製 |
| 「音效 / SFX」 | prompt 加 `SFX:` 層級 (Veo/Sora/Kling 3.0 支援) |
| 「靜音 / 無聲 / 純視覺」 | 關 Native Audio (省 credits)，prompt 不加音訊 |
| 「Hisaishi 感」「久石讓風」 | `Joe Hisaishi-inspired Ghibli orchestral` |
| 「lo-fi」「爵士」 | 對應 Suno style tag |

---

## 對白語言

| 使用者說 | 設 |
|---|---|
| 「英文對白」 | 預設 (口型最穩) |
| 「中文對白」 | Sora 2 / Veo 3.1 + 引號中文 (口型略降) |
| 「日文」「韓文」 | Veo 3.1 多語支援 |
| 「台語 / 粵語」 | Veo 多 dialects 支援 (Kling 3.0 也強) |

---

## 主題關鍵字增強 (自動補 token)

| 主題 | 自動補充 |
|---|---|
| 「異世界 / 穿越」 | Shinkai + Ghibli + volumetric god rays + magical particles |
| 「末日 / 廢土」 | Villeneuve + muted ochre + dust atmosphere |
| 「校園 / 青春」 | K-drama soft warm + 85mm shallow DoF |
| 「鬼怪 / 恐怖」 | Hiro Murai low-light + green fluorescent + static locked |
| 「武俠 / 古風」 | Kurosawa + Zhang Yimou + 竹林 + anamorphic |
| 「賽博 / 未來」 | Blade Runner 2049 + Cinestill 800T + magenta/cyan |
| 「廣告 / 產品」 | Apple cyclorama 或 Nike low-angle (看品牌語氣) |
| 「MV」 | Hiro Murai 或 Cole Bennett + 節拍剪接 |
| 「時尚」 | Vogue Italia + 中片幅 + 單硬光 |
| 「紀錄片 / 訪談」 | A24 indie + 35mm + 手持 |

---

## 社群多平台自動同步 (Social Pack)

使用者一句話要同時出多個畫面比例的版本 (社群發佈需求)：

| 使用者說 | Auto-Pilot 執行 |
|---|---|
| 「社群三版」「三平台版」「同時出 YouTube + TikTok + IG」 | 自動出 16:9 + 9:16 + 1:1 三版 |
| 「YouTube + TikTok」「橫版+豎版」 | 16:9 + 9:16 兩版 |
| 「IG feed 全尺寸」 | 1:1 + 4:5 + 9:16 (IG 貼文三格式) |
| 「短影音全平台」 | 9:16 三版 (不同 seed 供挑選) |

**實作方式：**
- 同一個 prompt，依 flag 跑 N 次 (平台支援時也可單次 x2 不同 aspect)
- Flow 可依序切換 aspect 重送 (每次扣點)
- Kling 要分 N 次生成 (aspect selector)
- **預估成本自動計算並告知**：如「三版共 120 credits，確定？」
- 結果產出後自動命名：`{主題}_16x9.mp4` / `_9x16.mp4` / `_1x1.mp4`

**核心場景：**
- 品牌一次發布多平台 (Nike 的 30s 橫版 + 15s 豎版 + 9s IG reel)
- 個人創作者要覆蓋 YouTube + TikTok + IG + Threads
- 廣告主需要 A/B test 不同比例

## 複合 flag 範例

使用者一句話包多個 flag，auto-pilot 自動全部解析：

**「做一個王家衛風的 30 秒中文對白短片，用最好質量，豎屏手機」**
→ 平台：Sora 2 或 Veo 3.1 Quality (對白 + 最好)
→ 風格：王家衛 + Doyle + Cinestill 800T + 霓虹
→ 時長：30s (= Veo 8s x 4 extend 或多鏡拼)
→ 畫面比：9:16
→ 對白：中文
→ 成本：Quality + 30s = 預算高 (告知使用者)

**「免費幫我做一個宮崎駿風的 5 秒異世界短片，一版就好」**
→ 平台：Kling 3.0 (免費) 或 Seedance Lite
→ 風格：Ghibli + Shinkai + 魔法粒子
→ 時長：5s
→ 畫面比：16:9 (預設)
→ 數量：x1
→ 預算：免費 tier 內

**「Apple 廣告感的產品 hero 30 秒，白底極簡」**
→ 平台：Flux 1.1 Pro 首幀 + Runway Gen-4 Video extend
→ 風格：Apple cyclorama + 100mm macro + 5600K
→ 時長：30s
→ 畫面比：16:9 或 4:5
→ 預算：中 (Flux macro + Runway video)

---

## Auto-Pilot 遇到 flag 衝突時

- 「最便宜 + 最好質量」→ **衝突，問使用者取捨**
- 「Kling + 中文對白」→ Kling 3.0 支援，繼續
- 「Midjourney + 影片」→ Midjourney 不做影片，改建議「MJ 出 key frame → Runway i2v」
- 「4K + 免費」→ 多數平台 4K 要付費，降到最高免費 (通常 720p/1080p)

---

## 使用者不熟術語時的容忍

小朋友可能說：
- 「做個抖音」 = 9:16 短影音，TikTok aesthetic
- 「卡通動畫」 = anime / cel-shaded
- 「夢幻一點」 = pastel + soft bokeh + dreamy bloom
- 「酷一點」 = cyberpunk 或 high contrast
- 「溫馨」 = warm + golden hour + 家庭氛圍
- 「可愛」 = Studio Ghibli / Sanrio / pastel
- 「帥」 = low-angle + rim light + silhouette

Auto-Pilot 要自然語言理解這些**模糊表達**，對應到 skill 語彙庫。

---

## 備忘

- Flag 用自然語言指定優先於預設
- Flag 間衝突 → auto-pilot 選「使用者最可能要的」並在 Preview 告知
- 使用者在 Preview 階段可再補 flag 改設定
