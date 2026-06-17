---
name: code-cleanup-helper
description: 兩模式工具 — Mode A 掃 codebase / SKILL.md / prompt 找重複/命名/模組/過長 4 類技術債；Mode B 跑 repo audit 檢查私公版 sync / release 一致性 / cross-link / 版本標記漂移 + 開源交接健檢 5 維度。觸發詞：「清理 code」「找重複」「重構」「模組化」「review codebase」「掃 prompt」「我這 skill 寫好亂」「prompt 太長拆一下」「跑大專案怕亂」「audit 我的 repo」「check release 一致性」「私公版 diff」「版本對齊」「release ship 前盤點」時觸發。
---

<!--
  code-cleanup-helper skill — Created by 駱君昊 (Hao)
  Repo: https://github.com/Hao0321/claude-skill-code-cleanup
  Companion skill to: https://github.com/Hao0321/claude-skill-social-post
  License: MIT — 保留此標註即可修改、使用、商用
-->

# code-cleanup-helper

幫你掃 codebase / SKILL.md / prompt template，或跑 release ship 前 audit，找 9 類技術債：

**Mode A — Codebase Cleanup**（v0.1 base）：
1. 重複邏輯（DRY 違反）
2. 命名不一致（同 concept 多個稱呼）
3. 可抽 reusable 模組區塊
4. 過長檔案 / 函數

**Mode B — Repo Audit**（v0.2 新增 / v0.3 加 Dim 9）：
5. 私公版 sync GAP（適用 dual-repo skill）
6. Release 一致性（git tag / gh release / CHANGELOG / README）
7. Cross-link 完整性（broken markdown link / repo cross-ref）
8. 版本標記漂移（多檔案 version mention drift）
9. 開源/交接文件健檢（主力定位顛倒 / 隱性依賴沒標需求 / onboarding 無 minimum-viable，源自 M89）

**永遠先報告 + 等使用者確認，絕不自動修改檔案**。

## 三階段工作流（適用 both modes）

### Phase 1：掃描（scan，< 30 sec）

讀取目標資料夾，建立索引：
- 每檔案行數
- 跨檔案 substring matching（≥ 30 字一字不差）
- 高頻 keyword 統計（≥ 4 字、出現 ≥ 5 次）
- 規則 / heading / function 命名 pattern
- (Mode B) git tag / gh release / version mention 集合

工具：`Bash` (wc, grep, sort, uniq, diff, git, gh) + `Glob` + `Grep`

### Phase 2：報告（report，< 1 KB 給人讀）

輸出結構化發現（依模式 4 + 5 dimension）。

### Phase 3：建議（suggest）

不直接改 code，輸出 refactor proposal。使用者確認後才用 `Edit` / `Write` 工具改檔案。

## 觸發場景

**Mode A 觸發**：
- 寫到專案 1000+ 行覺得開始亂
- skill prompt 越寫越長覺得有重複
- 想 fork 別人的 skill 但先看 codebase 狀態
- 兩個禮拜沒 review codebase 想盤點

**Mode B 觸發**：
- ship release 前 final audit
- 私公版 skill repo 想確認同步狀態
- 多檔案版本標記抓不出哪個漏更新
- 多 repo ecosystem 想確認 cross-link 完整

## 不要做

- 自動修改檔案（必須使用者確認）
- 刪除任何內容（只報告，不刪）
- 推到 GitHub（使用者自己 commit）
- 修改測試 / CI 設定 / package.json
- 改 license / readme 等 meta files
- 改 `.git/` 內任何東西
- 跑 `git push --force` 或 `git reset --hard`
- 自動 publish GitHub release

---

# Mode A：Codebase Cleanup（4 dimensions）

### Dimension 1: 重複內容（DRY 違反）

**掃描方式**：

```bash
# 跨檔案 ≥ 30 字一字不差重複
cat <files> | grep -o '.\{30,\}' | sort | uniq -c | sort -rn | awk '$1 >= 3'

# 高頻 keyword 散落
for kw in <key concepts>; do
  count=$(grep -r "$kw" <files> | wc -l)
  echo "「$kw」出現 $count 次"
done
```

**警告線**：
- 同字串散落 **≥ 5 個檔案** = 嚴重 DRY 違反
- 同 keyword 出現 **≥ 50 次** = 過度重複，應抽變數
- 同邏輯重複 **≥ 3 次** = 應抽函數 / module

### Dimension 2: 命名不一致

**掃描方式**：

```bash
grep -rho "R[0-9]\+：" <files> | sort -u
grep -rho "規則 [0-9]\+" <files> | sort -u
```

**常見 inconsistency**：
- 中英混用：「Skill」vs「技能」vs「skill」
- 編號格式：「R5」vs「規則 5」vs「Rule 5」
- 變數命名：camelCase vs snake_case 混用
- 同義詞：user / account / profile / member

**處理建議**：選一個 canonical 形式，其他 rename。

### Dimension 3: 可抽模組區塊

**掃描方式**：找重複 ≥ 3 次的 logic block + 邏輯獨立 + 跨檔案 reuse 機會

**候選範例**：
- Header block（每個檔案開頭重複）
- Constant 定義（version / 日期 / 數字常數）
- 同樣「檢查表」格式
- 共用 emoji 鍵 / glyph

### Dimension 4: 過長檔案 / 函數

**警告線**：

| 檔案類型 | 警告 | 嚴重 |
|---|---|---|
| SKILL.md | > 200 行 | > 400 行 |
| references/*.md | > 400 行 | > 800 行 |
| 一般 .py / .ts | > 500 行 | > 1000 行 |
| 單函數 | > 50 行 | > 100 行 |

---

# Mode B：Repo Audit（5 dimensions，v0.2 新增 / v0.3 加 Dim 9）

### Dimension 5: 私公版 sync GAP

適用 dual-repo skill（私人版含個人資料 + 公開開源版）。

**掃描方式**：

```bash
for f in $(cd <private_skill> && find . -name "*.md"); do
  if [ -f <public_skill>/$f ]; then
    if diff -q <private_skill>/$f <public_skill>/$f > /dev/null 2>&1; then
      echo "  ✅ $f synced"
    else
      line_diff=$(diff <private_skill>/$f <public_skill>/$f | wc -l)
      echo "  ⚠️  $f differs ($line_diff diff lines)"
    fi
  fi
done
```

**判讀**：
- diff 行數 ≤ 10 + 都是 author signature comment block = **by-design**（不算 bug）
- diff 行數 > 10 = **真實 sync gap**，私公版 desync
- 公開版有但私人版沒（example.md 類）= 預期分歧

**處理建議**：
- by-design diff → 加進 ignore list
- 真實 sync gap → 重新 sync 一次 + 加 author comment

### Dimension 6: Release 一致性

檢查 git tag / gh release / CHANGELOG.md / README.md 版本對齊。

**掃描方式**：

```bash
cd <repo>
echo "Git tags: $(git tag -l | sort -V)"
echo "GH releases: $(gh release list --limit 20 --json tagName --jq '.[].tagName' | sort -V)"
echo "CHANGELOG 版本：$(grep -oE 'v[0-9]+\.[0-9]+(\.[0-9]+)?' CHANGELOG.md | sort -uV)"
echo "README 提到 version：$(grep -oE 'v[0-9]+\.[0-9]+(\.[0-9]+)?' README.md | sort -uV)"
```

**警告 patterns**：
- 有 git tag 但沒 gh release → **release 沒 publish**
- 有 gh release 但沒對應 commit tag → tag 丟失
- CHANGELOG 缺最新版 entry → **doc 漏更**
- README 缺最新版提及 → 用戶看到的不是最新

### Dimension 7: Cross-link 完整性

檢查 markdown link / repo 互引用是否都還活著。

**掃描方式**：

```bash
# 找所有內部 .md ref，檢查目標檔案存在
grep -rohE '\[([^]]+)\]\(([^)]+\.md)\)' <files> | while read link; do
  target=$(echo "$link" | grep -oE '\([^)]+\.md\)' | tr -d '()')
  [ -f "$target" ] || echo "❌ Broken: $link"
done

# Cross-repo link 檢查（companion repo / sister skill）
grep -rE 'github\.com/[^/]+/[^/) ]+' <files> | sort -u
```

**警告**：
- 內部 .md link 指向不存在檔案 → broken
- Companion repo 提到的功能 / repo 已 archive / rename → stale link

### Dimension 8: 版本標記漂移

多檔案 / 多段落間版本標記不一致。

**掃描方式**：

```bash
echo "README 內：$(grep -oE 'v[0-9]+\.[0-9]+(\.[0-9]+)?' README.md | sort -uV)"
echo "SKILL.md 內：$(grep -oE 'v[0-9]+\.[0-9]+(\.[0-9]+)?' SKILL.md | sort -uV)"
echo "CHANGELOG 最新：$(grep -oE 'v[0-9]+\.[0-9]+(\.[0-9]+)?' CHANGELOG.md | head -1)"
echo "Latest tag：$(git tag -l | sort -V | tail -1)"
```

**警告**：
- README 提的版本 < 實際 latest tag → 推 release 沒更 README
- SKILL.md 內部「v0.x 更新」提的版本 < CHANGELOG 最新 → 多檔案 drift

### Dimension 9: 開源/交接文件健檢（v0.3 新增 — 源自 M89）

把專案交給陌生人（開源 / handoff）前，查「我熟到忘了講」的 3 個隱性洞 + 1 個 broken ref。

**掃描方式**：

```bash
# 9a. 主力工具定位顛倒 — 主力工具被講成「選用/optional」？
#     先確認你的主力工具名（例：CapCut），再查它附近有沒有貶成選用
grep -rniE "(選用|optional|secondary|非必)[^。\n]*(CapCut|主力工具名)" README* SETUP* docs/ 2>/dev/null \
  && echo "⚠️ 主力工具被標成選用 — 定位可能顛倒"
# 反向：次要工具(ffmpeg…)被列「必需/required」？
grep -rniE "(必需|required)[^。\n]*(ffmpeg|次要工具名)" README* 2>/dev/null \
  && echo "⚠️ 次要工具被列必需 — 主次顛倒"

# 9b. 隱性外部依賴沒進需求 — 核心功能背後靠什麼跑？
#     列出已知硬依賴，逐一查有沒有出現在需求/README
for dep in "Computer Use" "API" "API key" "PATH"; do
  grep -riq "$dep" README* SETUP* || echo "⚠️ 依賴「$dep」未在文件出現 — 採用者會卡"
done

# 9c. onboarding 沒 minimum-viable 分層 — 問卷要全填才有價值？
grep -rqiE "必答|★|required|最小啟動|minimum|quick.?start|5 分鐘" SETUP* README* \
  || echo "⚠️ 找不到『必答/選填分層』或『最小啟動』— onboarding 門檻過高"

# 9d. 引用了不存在的資料夾/檔案（broken folder ref，承 Dimension 7 + M84）
grep -rohE '`[a-zA-Z0-9_./-]+/`' README* SETUP* | tr -d '`' | sort -u | while read d; do
  [ -e "$d" ] || echo "❌ 文件引用不存在的路徑：$d"
done

# 9e. 個資/個人脈絡被當「預設」烤進邏輯（源自 M90 — 採用者最隱蔽的雷）
#     作者名/品牌/個人路徑/個人主題詞 出現在 src 程式碼，且是 default（非 example）
AUTHOR_TOKENS="作者名|品牌名|你的英文 handle|你的網域"   # 換成你的：例 Hao0321|自由工坊|hao0321\.com
grep -rnE "$AUTHOR_TOKENS" src/ --include="*.py" 2>/dev/null | grep -viE "example|sample|範例|your[-_ ]" \
  && echo "⚠️ 個資/品牌烤進 src 程式碼 — 採用者會 match 不到或被污染"
# default 參數指向作者個人 keyword/map/dict？（非 example 命名 = 高風險）
grep -rnE "else [A-Z_]*KEYWORD_MAP|else [A-Z_]*_(MAP|DICT|TOPICS)" src/ --include="*.py" 2>/dev/null \
  | grep -viE "EXAMPLE|DEFAULT_EMPTY|\{\}" \
  && echo "⚠️ 函數 default 吃作者個人 map → 陌生採用者全 match 不到 = 輸出對不上"
# 語言鎖死？（純中文 keyword / 只 handle CJK，無語言無關 fallback）
grep -rlE "[一-鿿]{2,}\"" src/ --include="*.py" 2>/dev/null | while read f; do
  grep -qiE "fallback|filename|token.?overlap|語言無關|language.?agnostic" "$f" \
    || echo "⚠️ $f 有 CJK keyword 但無語言無關 fallback → 非中文採用者全 miss"
done
```

**警告 patterns**：
- 主力工具出現在「選用/optional」清單 → **定位顛倒**（別人會拿次要工具當主力）
- 核心自動化的隱性依賴（Computer Use / API key / 特定 app / 系統權限）**沒寫進需求** → 採用者跑不起來還不知為何
- SETUP/問卷**沒有 ★必答 vs ⭕選填 分層**，也沒「丟給 AI 訪談你」低門檻路徑 → 填完才給價值 = 棄坑
- README 引用 `docs/` 等**不存在的資料夾**（broken link）
- 中英雙語文件**只改一邊** → 語言版 drift（併入 Dimension 5 sync）
- ⭐ **個人化設定當 default 烤進邏輯**（作者 keyword map / 個人路徑 / 品牌 / 語言鎖死）→ 採用者 match 不到 → **輸出對不上**（源自 M90：個人化必須 opt-in，預設走零設定通用解 + 語言無關 fallback）

**判斷句（最高層）**：「**拿掉這個依賴，核心功能還能跑嗎？**」不能 → 必標需求。
「**零基礎陌生人能 5 分鐘跑起來嗎？他知道先用哪條路、要開什麼嗎？**」不能 → onboarding 沒過。

---

## 範例：跑 social-post skill v0.7.3 完整 audit（v0.2 真實 demo）

跑 `Hao0321/claude-skill-social-post` repo 的 Mode A + Mode B 全 audit：

```
=== Cleanup + Audit Report — social-post skill v0.7.3 ===

📊 Repo: 11 個檔案 / 2,179 行

────── Mode A: Cleanup ──────

Dimension 1: 重複內容（top）
- 「鐵粉」65 次 ⚠️
- 「Day 1」70 次散落 ⚠️
- 「F6b」56 次跨 4 檔
- 「敘事意圖」34 次

Dimension 2: 命名不一致 ✅ v0.7.3 已修
- 之前「R[N]」vs「規則 N」雙系統 → v0.7.3 改成「歸納 [N]」+ cross-ref table

Dimension 3: 可抽模組候選
- Day 1-7 戰績數字散落 200+ 次 → 抽 references/battle_records.md

Dimension 4: 過長檔案
- case_studies.md 679 行（接近 800 警告）
- formulas.md 505 行

────── Mode B: Audit ──────

Dimension 5: 私公版 sync GAP
- SKILL.md differ 10 行 = ✅ author signature block by-design
- 其他 3 檔（case_studies / formulas / evaluation）全 synced

Dimension 6: Release 一致性 ⚠️ 抓到 3 處
- Git tags: v0.5, v0.6, v0.7.2, v0.7.3（缺 v0.4, v0.7, v0.7.1 local fetch）
- GH releases: v0.5/v0.6/v0.7/v0.7.1/v0.7.2/v0.7.3 全 live
- ⚠️ CHANGELOG 最新版 v0.7.2，**缺 v0.7.3 entry**（剛 release 沒寫進 doc）

Dimension 7: Cross-link 完整性 ✅
- 外部 link 13 個全 live
- 內部 .md ref 0 個（docs heavy 用 absolute URL，OK）

Dimension 8: 版本標記漂移 ⚠️
- README 提 v0.7.2，**缺 v0.7.3**
- SKILL.md 提到 v0.7.2，**缺 v0.7.3**
- CHANGELOG 最新 v0.7.2，**缺 v0.7.3 entry**

📊 整體健康度：⚠️ 中度
- Mode A: 6/10（v0.7.3 修了命名 +1 分）
- Mode B: 7/10（sync ok / release ok 但 doc drift）

🔧 建議優先 fix：
1. 加 v0.7.3 entry 到 CHANGELOG.md（10 min）
2. README + SKILL.md 加 v0.7.3 提及（5 min）
3. case_studies.md 拆檔（60 min，v0.8 規劃）
```

→ 這個 audit 抓到 **v0.7.3 release 了但 CHANGELOG/README 漏更**。是 cleanup-helper v0.2 立刻發揮價值的 self-demo。

## 設計理念

跟 anthropic-skills 的 progressive disclosure 對齊：
- Phase 1 掃描快（< 30 sec）
- Phase 2 報告濃縮（< 1 KB 給人讀）
- Phase 3 建議才展開 detail

跟 social-post skill 的「敘事意圖」對齊：
- 不只看 syntax 重複，看 **semantic** 重複（同 concept 不同字也算）
- Mode B 看 **release ops** 重複（git / doc / version drift）

## License

MIT — 保留此標註即可修改 / 使用 / 商用。

## Author

駱君昊 (Hao) · MetaFantasy Co-Founder

Repo: https://github.com/Hao0321/claude-skill-code-cleanup
Companion: https://github.com/Hao0321/claude-skill-social-post
