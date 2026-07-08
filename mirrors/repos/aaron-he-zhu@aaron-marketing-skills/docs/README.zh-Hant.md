<div align="center">

# Aaron 行銷技能庫

**120 個行銷技能 —— 品牌敘事、SEO/GEO、紅人、付費廣告、郵件、產品發布、社媒 —— 共享一套契約。**

<p align="center">
  <a href="https://github.com/aaron-he-zhu/aaron-marketing-skills"><img src="https://img.shields.io/github/stars/aaron-he-zhu/aaron-marketing-skills?style=flat" alt="GitHub Stars"></a>
  <a href="https://github.com/aaron-he-zhu/aaron-marketing-skills/blob/main/VERSIONS.md"><img src="https://img.shields.io/badge/version-16.0.3-orange" alt="Version"></a>
  <a href="https://github.com/aaron-he-zhu/aaron-marketing-skills/blob/main/LICENSE"><img src="https://img.shields.io/badge/license-Apache%202.0-green" alt="License"></a>
  <a href="https://github.com/aaron-he-zhu/aaron-marketing-skills/commits/main"><img src="https://img.shields.io/github/last-commit/aaron-he-zhu/aaron-marketing-skills" alt="Last Commit"></a>
</p>
<p align="center">
  <a href="https://www.skills.sh/aaron-he-zhu"><img src="https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/aaron-he-zhu/aaron-marketing-skills/main/badges/skillssh.json" alt="skills.sh"></a>
  <a href="https://clawhub.ai/aaron-he-zhu"><img src="https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/aaron-he-zhu/aaron-marketing-skills/main/badges/clawhub.json" alt="ClawHub"></a>
  <a href="https://skillhub.cn/user/user_2c0f1e77"><img src="https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/aaron-he-zhu/aaron-marketing-skills/main/badges/skillhub.json" alt="SkillHub"></a>
</p>

[English](../README.md) | [Deutsch](README.de.md) | [Español](README.es.md) | [Français](README.fr.md) | [Italiano](README.it.md) | [日本語](README.ja.md) | [한국어](README.ko.md) | [Português](README.pt.md) | [简体中文](README.zh.md) | **繁體中文**

</div>

一套 Claude 技能與斜線命令，讓聊天 Agent 成為行銷操作員。七個學科 + 一個共享協議層，一圖總覽：

| 層 | 技能 | 生命週期（階段目錄） | 框架 → 門 | 入口命令 |
|----|------|----------------------|-----------|----------|
| **Narrative** | 16 | trace → architect → land → evaluate | [TALE](../references/tale-benchmark.md) → `narrative-quality-auditor`（NQS） | `/aaron-marketing:narrative` |
| **SEO/GEO** | 16 | research → build → optimize → monitor | [CORE-EEAT](../references/core-eeat-benchmark.md) → `content-quality-auditor` · [CITE](../references/cite-domain-rating.md) → `domain-authority-auditor` | `/aaron-marketing:seo-geo` |
| **紅人** | 16 | discover → plan → activate → measure | [C³](../references/c3-benchmark.md) → `content-reviewer`（ART）；`fit-scorer` 打 ACE 分 | `/aaron-marketing:influencer` |
| **付費廣告** | 16 | research → orchestrate → activate → scale | [ROAS](../references/roas-benchmark.md) → `ad-account-auditor`（RQS） | `/aaron-marketing:ad` |
| **郵件** | 16 | setup → engage → nurture → deliver | [SEND](../references/send-benchmark.md) → `email-quality-auditor`（EQS） | `/aaron-marketing:email` |
| **產品發布** | 16 | research → assemble → mobilize → prove | [RAMP](../references/ramp-benchmark.md) → `launch-readiness-auditor`（LQS） | `/aaron-marketing:launch` |
| **社媒** | 16 | explore → craft → host → observe | [ECHO](../references/echo-benchmark.md) → `social-quality-auditor`（SQS） | `/aaron-marketing:social` |
| **協議層** | 8 | ——（階段流程之外的共享機件） | 7 個真相註冊表（entity · creator · offer/claims · consent · launch · channel · narrative）+ HOT/WARM/COLD 記憶 | —— |

`/aaron-marketing:auto` 把任意自然語言目標路由到全庫。全部為**純 Markdown** —— 唯一的程式碼是一個 Bash hook runner、一個 Bash 校驗器、以及零依賴的 Python 標準庫資料助手（無 `pip`、無建置步驟）。**每個技能都能在 Tier 1 僅憑你貼上的資料執行**；連接器只是自動化取數。

> 合併前的兩個獨立倉庫現均為**純路標倉庫**——[seo-geo-claude-skills](https://github.com/aaron-he-zhu/seo-geo-claude-skills)（最終 20 技能版本線保留於 tag `v9.9.12`）與 [influencer-marketing-agent-skills](https://github.com/aaron-he-zhu/influencer-marketing-agent-skills)（最終 IMPACT 版本線保留於 tag `standalone-final`），安裝一律指向本倉庫。兄弟倉庫策略見 [docs/repo-family.md](repo-family.md)。

---

## 目錄

- [為什麼選它](#為什麼選它)
- [安裝](#安裝)
- [初次使用](#初次使用)
- [架構](#架構)
  - [共享技能契約](#共享技能契約)
  - [系統：四層行銷作業系統](#系統四層行銷作業系統)
  - [品質體系：八框架、八門](#品質體系八框架八門)
  - [協議層](#協議層)
  - [記憶與自動化](#記憶與自動化)
- [技能目錄](#技能目錄)
  - [Narrative — TALE（16）](#narrative--tale16)
  - [SEO/GEO（16）](#seogeo16)
  - [紅人（16）](#紅人16)
  - [付費廣告 — ROAS（16）](#付費廣告--roas16)
  - [郵件行銷 — SEND（16）](#郵件行銷--send16)
  - [產品發布 — RAMP（16）](#產品發布--ramp16)
  - [社媒 — ECHO（16）](#社媒--echo16)
  - [協議層（8）](#協議層8)
- [命令](#命令)
- [連接器與層級](#連接器與層級)
- [推薦工作流](#推薦工作流)
- [倉庫結構](#倉庫結構)
- [設計哲學](#設計哲學)
- [品質守衛](#品質守衛)
- [貢獻與文檔](#貢獻與文檔)
- [免責聲明](#免責聲明)
- [授權條款](#授權條款)

---

## 為什麼選它

| 原則 | 落到實處 |
|------|----------|
| **預設 keyless** | 每個技能都能在 **Tier 1** 僅憑貼上的資料、或從免費/第一方來源拉取的資料執行。付費工具與 MCP 伺服器是選配，絕非前提。付費廣告技能基於**自有帳戶手動匯出**評分——帶金鑰的廣告 API 永不必需。 |
| **是 Markdown，不是框架** | 技能即內容。唯一可執行程式碼是 `hooks/claude-hook.sh`（Bash）、`scripts/validate-skill.sh`（Bash）、`scripts/connectors/*.py`（**僅 Python 標準庫**）。無需安裝、稽核或維護。 |
| **一套共享契約** | 120 個技能暴露同樣的七段結構，並自帶 `discipline` + `phase` 中繼資料，整個庫像一套作業系統：每個技能都知道自己的輸入、輸出，以及下一個該交棒的技能。 |
| **帶門的品質** | 八套基準驅動八個 auditor-class 門，產出結構化、可機器校驗的判定——不是憑感覺。每個帶門產物落盤前都經 PostToolUse hook 校驗。 |
| **真相住在註冊表裡** | 規範事實（品牌實體、創作者檔案、offer/聲明實證、逐主體同意）住在協議層專職註冊表中，唯一寫入者規則——門對照註冊表評判，而非各自重新推導。 |
| **跨輪記憶** | HOT/WARM/COLD 記憶模型在技能與工作階段之間攜帶發現、分數與未決事項，並在寫入時淨化。 |
| **人話** | 技能內建 AI 腔偵測器與禁用詞表，讓輸出讀起來像人寫的。 |

---

## 安裝

可搭配 Claude Code、任意 Agent Skills 相容宿主，或直接 `git clone`：

| 宿主 | 安裝 |
|------|------|
| **Claude Code** | `/plugin marketplace add aaron-he-zhu/aaron-marketing-skills` 然後 `/plugin install aaron-marketing@aaron` |
| **Codex · Cursor · OpenCode · Antigravity · Gemini CLI · Copilot CLI · OpenClaw · Hermes · [70+ 宿主](https://github.com/vercel-labs/skills#supported-agents)** | `npx skills add aaron-he-zhu/aaron-marketing-skills` |
| **[SkillHub.cn](https://skillhub.cn)（中文社群）** | `skillhub install <frontmatter-slug>`（如 `keyword-research`） |
| **任意宿主** | `git clone https://github.com/aaron-he-zhu/aaron-marketing-skills` |

在 Claude Code 中，`marketplace add` 只是註冊目錄——還需執行 `/plugin install aaron-marketing@aaron`（或在 `/plugin` 中選擇）才能真正啟用技能與命令。通用宿主單技能安裝：`npx skills add aaron-he-zhu/aaron-marketing-skills -s keyword-research`。可在 [skills.sh 註冊表](https://skills.sh/aaron-he-zhu/aaron-marketing-skills)瀏覽本技能庫。各宿主的技能目錄、frontmatter 相容細節、以及脫離外掛安裝時的降級行為見 [docs/agent-compatibility.md](agent-compatibility.md)（2026-07 實測 120/120 可安裝）。

安裝外掛**不會**往你的 `/mcp` 清單新增任何東西——MCP 目錄位於 [`docs/mcp-catalog.json`](mcp-catalog.json)，刻意放在 Claude Code 會自動註冊的外掛根 `.mcp.json` 路徑之外，僅作複製貼上參考（見[連接器與層級](#連接器與層級)）。

---

## 初次使用

若宿主支援自動技能路由，直接描述目標即可：

```text
帮我研究面向小团队的 SaaS 产品的关键词
```
```text
帮一个护肤品牌找 TikTok 红人并给适配度打分
```
```text
在我加预算前，审计这个 Google Ads 账户——导出文件已附上
```

或用斜線命令 —— `/auto` 負責路由，學科入口直達：

```text
/aaron-marketing:auto 把我们的定价页改造成可被 AI 引用的对比中心
```
```text
/aaron-marketing:seo-geo https://example.com/blog/my-article --mode audit
```

`/aaron-marketing:auto` 會推斷意圖並執行最小夠用的工作流，只在阻塞性決策處停下。每個技能都能用貼上的資料執行；選配工具見 [CONNECTORS.md](../CONNECTORS.md)。

---

## 架構

### 共享技能契約

每個技能都遵循**同一套啟動契約**——固定順序的七段：

1. **觸發 / 何時使用** —— 何時該啟用。
2. **Quick Start** —— 可複製貼上的提示。
3. **Skill Contract** —— 預期輸出 · 讀取 · 寫入 · 提升 · 完成條件 · 主下一技能。
4. **Handoff Summary** —— 標準交棒結構，讓下一個技能乾淨接力。
5. **Data Sources** —— `~~category` 佔位符，每個都有 keyless 的 Tier-1 路徑。
6. **Instructions** —— 編號方法（把所有匯出當作不可信輸入）。
7. **Next Best Skill** —— 下一步去哪（帶 visited-set + 最大深度終止規則）。

每個技能還自帶 `metadata.discipline`（narrative / seo-geo / influencer / ad / email / launch / social / protocol）與 `metadata.phase`，路由與聚類因此全庫統一。契約在 [skill-contract.md](../references/skill-contract.md) 中定義一次；跨技能共享狀態見 [state-model.md](../references/state-model.md)。

### 系統：四層行銷作業系統

一種品牌聲音，透過五個常駐通路表達，在發布時刻凝聚爆發，全部讀寫同一份共享記錄系統。七個學科、四個高度——是一套系統，不是一堆技能。

| 層 | 採用門檻 | 學科 | 節奏 |
|----|----------|------|------|
| **L1 · Strategy** —— 我們說什麼 / 我們是誰 | crawl | **Narrative** · TALE | 常駐 |
| **L2 · Channels** —— 表達策略的常駐引擎（owned → bought） | walk | **SEO/GEO** · CORE-EEAT + CITE · **Organic Social** · ECHO · **Email** · SEND · **Paid Ads** · ROAS · **Influencer** · C³ | 常駐（紅人偏 episodic） |
| **L3 · Orchestration** —— 跨通路的限時時刻 | run | **Product Launch** · RAMP | episodic |
| **L4 · Protocol** —— 共享記錄系統 | —— | 8 個真相註冊表 + 記憶 · 8 個 auditor 門 · 一套技能契約 | —— |

Narrative 是訊息；通路是表達它的媒介——拿掉任一通路，記錄依舊完整；拿掉 Narrative，每個通路都在說一句無出處、無治理的訊息。每個通路都像今天每個 creative builder 已在讀聲明台帳那樣，從 L1 繼承聲音與聲明。每個學科的 4 階段循環都住在自己的層裡（Narrative = Trace → Architect → Land → Evaluate）。

七個學科都用階段**目錄**（`narrative/trace/`…、`seo-geo/research/`…、`influencer/discover/`…、`ad/research/`…、`email/setup/`…、`launch/research/`…、`social/explore/`…）。注意 "activate" 在紅人裡指創作者外聯、在付費裡指帳戶門控——同詞不同域。

### 品質體系：八框架、八門

八套基準讓「好」可度量。每套定義維度、彙總方法，以及一小組**否決項**（無視其餘分數直接封頂或阻斷的硬性失敗）：

| 框架 | 評分對象 | 項數 / 維度 | 彙總 | 否決項 |
|------|----------|-------------|------|--------|
| **[TALE](../references/tale-benchmark.md)** | 品牌敘事 Truth / Architecture / Landing / Evidence | T / A / L / E | **NQS = floor（目標加權均值）**（算術） | `T1`/`A1`/`L1`/`E1` |
| **[CORE-EEAT](../references/core-eeat-benchmark.md)** | 內容品質（GEO = CORE 均值，SEO = EEAT 均值） | 80 項 / 8 維 | 各維度均值 | `T04`、`C01`、`R10` |
| **[CITE](../references/cite-domain-rating.md)** | 網域權威與引用信任 | 40 項 / 4 維 | 算術加權平均 | `T03`、`T05`、`T09` |
| **[C³](../references/c3-benchmark.md)** | 紅人 創作者/內容/活動 | ACE / ART / ROI · 9 維 | **CVI =（ACE × ART × ROI）^⅓**（幾何） | ACE `A2`/`C1`/`E2`、ART `T1`/`T2` |
| **[ROAS](../references/roas-benchmark.md)** | 付費廣告 回報/報價/受眾/花費效率 | R / O / A / S | **RQS = floor（目標加權均值）**（算術） | `R1`/`R2`/`O1`/`O2`/`A1` |
| **[SEND](../references/send-benchmark.md)** | 郵件行銷 寄件完整/送達 · 互動 · 培育/生命週期 · 直接回應/轉換 | S / E / N / D | **EQS = floor（目標加權均值）**（算術） | `S1`/`S2`/`N1`/`D1` |
| **[RAMP](../references/ramp-benchmark.md)** | 產品發布 就緒 · 資產 · 勢能 · 證明 | R / A / M / P · 40 項 | **LQS = floor（目標加權均值）**（算術） | `R1`/`A1`/`M1`/`P1`（帶框架名限定——與 ROAS `R1`/`A1` 相區別） |
| **[ECHO](../references/echo-benchmark.md)** | 自然社媒 Embeddedness / Craft / Hosting / Observability | E / C / H / O | **SQS = floor（目標加權均值）**（算術） | `E1`/`C1`/`C2`/`H1`/`H2`/`O1`（帶框架名限定——與 ROAS `O1`/`O2` 相區別） |

每套框架由一個 **auditor-class 門**執行——寫出受 PostToolUse hook 校驗的帶門產物（`class: auditor-output`）。門是工作流步驟，所以駐留並計入各自學科：

| 門 | 框架 | 所在 | 判定 |
|----|------|------|------|
| [narrative-quality-auditor](../narrative/evaluate/narrative-quality-auditor/SKILL.md) | TALE NQS | `narrative/evaluate/`（narrative） | 敘事採用前 SHIP / FIX / BLOCK |
| [content-quality-auditor](../seo-geo/optimize/content-quality-auditor/SKILL.md) | CORE-EEAT | `seo-geo/optimize/`（SEO/GEO） | 發布前 SHIP / FIX / BLOCK |
| [domain-authority-auditor](../seo-geo/monitor/domain-authority-auditor/SKILL.md) | CITE | `seo-geo/monitor/`（SEO/GEO） | TRUSTED / CAUTIOUS / UNTRUSTED |
| [content-reviewer](../influencer/activate/content-reviewer/SKILL.md) | C³ ART | `influencer/activate/`（紅人） | 創作者內容上線前 APPROVED / REVISIONS / REJECTED |
| [ad-account-auditor](../ad/activate/ad-account-auditor/SKILL.md) | ROAS RQS | `ad/activate/`（付費） | 加預算前 SHIP / FIX / BLOCK |
| [email-quality-auditor](../email/deliver/email-quality-auditor/SKILL.md) | SEND EQS | `email/deliver/`（郵件） | 發送前 SHIP / FIX / BLOCK |
| [launch-readiness-auditor](../launch/mobilize/launch-readiness-auditor/SKILL.md) | RAMP LQS | `launch/mobilize/`（產品發布） | 發布時刻確定前 SHIP / FIX / BLOCK |
| [social-quality-auditor](../social/host/social-quality-auditor/SKILL.md) | ECHO SQS | `social/host/`（社媒） | 發布前 SHIP / FIX / BLOCK |

**共享封頂法：** 單個否決項把受影響維度與總分封頂到 `min(raw, 60)`；**兩個及以上否決項 → `BLOCKED`**（無最終分）。判定對使用者翻譯成人話（報告裡不出現項目 ID）。門的機制——handoff schema、封頂算術、產物門清單——在 [auditor-runbook.md](../references/auditor-runbook.md) 統一規定，八套框架的算術由確定性 golden 測試鎖定（見[品質守衛](#品質守衛)）。

### 協議層

`protocol/` 目錄承載學科階段流程之外的**共享真相與記憶機件** —— 8 個技能，單獨計數：

| 技能 | 職責 | 錨定 | 規範儲存 |
|------|------|------|----------|
| [entity-optimizer](../protocol/entity-optimizer/SKILL.md) | 規範品牌/實體檔案（知識圖譜、Wikidata、AI 消歧） | SEO/GEO | `memory/entities/` |
| [creator-registry](../protocol/creator-registry/SKILL.md) | 規範創作者名冊/檔案——去重 handle、帶溯源標籤的受眾資料、費率、合規歷史 | 紅人 | `memory/creators/` |
| [offer-claims-registry](../protocol/offer-claims-registry/SKILL.md) | offer 與聲明實證台帳——O1/T2 聲明檢查所對照評判的那份記錄 | 付費 | `memory/claims/` |
| [consent-registry](../protocol/consent-registry/SKILL.md) | 規範的逐主體同意/抑制記錄——S2/N1 否決項對照評判的那份記錄 | 郵件 | `memory/consent/` |
| [launch-registry](../protocol/launch-registry/SKILL.md) | 規範的逐次發布檔案/發布行事曆——分級、單向生命週期階段、權威日期/禁運期、通路提交台帳；R1 階段真相否決所對照評判的 launch 真相 SSOT | 產品發布 | `memory/launch-registry/` |
| [channel-registry](../protocol/channel-registry/SKILL.md) | 規範的逐通路記錄——handle、所有權/授權、平台規範、揭露預設值；ECHO E1 通路真相否決所對照評判的通路真相 SSOT | 社媒 | `memory/channels/` |
| [narrative-registry](../protocol/narrative-registry/SKILL.md) | 規範的品牌敘事正典——核准的策略敘事、訊息體系、語言/詞彙、證明點；TALE T1 真相否決所對照評判的品牌正典 SSOT | 敘事 | `memory/narrative-registry/` |
| [memory-management](../protocol/memory-management/SKILL.md) | HOT/WARM/COLD 記憶生命週期（擷取 · 提升 · 降級 · 封存 · 查詢） | 全部學科 | `memory/` |

註冊表遵循**唯一寫入者規則**（其他技能經 `candidates.md` 投遞），且註冊表只*存證*——評判歸門。最底層真正橫向的是 `references/` 協議（[auditor-runbook](../references/auditor-runbook.md)、[state-model](../references/state-model.md)、[skill-contract](../references/skill-contract.md)、[humanizer-slop](../references/humanizer-slop.md)、[measurement-protocol](../references/measurement-protocol.md)）——按設計以文件而非技能的形式共享。

### 記憶與自動化

**記憶**按溫度分層，讓上下文跨技能與工作階段留存而不撐爆提示：

| 層 | 位置 | 行為 |
|----|------|------|
| **HOT** | `memory/hot-cache.md` | 每次工作階段自動載入；封頂 **80 行 且 25 KB**（先觸發者為準）。 |
| **WARM** | `memory/<subdir>/` | 各技能工作狀態、帶門稽核產物（`memory/audits/`）、註冊表規範儲存（`memory/entities\|creators\|claims/`）。 |
| **COLD** | `memory/archive/` | 降級/較舊記錄，留作召回。 |

**Hooks**（`hooks/hooks.json`，runner `hooks/claude-hook.sh`）接入四個 Claude Code 事件：

| 事件 | 比對 | 作用 |
|------|------|------|
| `SessionStart` | `startup\|resume\|clear\|compact` | 注入**淨化後**的 hot-cache + 未決事項指標（提示注入行被塗掉；符號連結快取被拒）。 |
| `UserPromptSubmit` | （全部） | 輕量逐提示上下文 hook。 |
| `PostToolUse` | `Write\|Edit` | hot-cache 體積告警 **+ Artifact Gate**：寫到 `memory/audits/` 下、宣告了 `class: auditor-output` 的檔案都會被校驗 handoff schema 與封頂欄位，不合規則攔截寫入。八個 auditor-class 門按契約必須宣告該標記；未標記的檔案不是稽核產物，直接放行。 |
| `Stop` | （全部） | 空操作（靜默退出）。 |

Artifact Gate 是**框架無關**的——同一個 hook 校驗 TALE、CORE-EEAT、CITE、C³、ROAS、SEND、RAMP、ECHO 產物，無任何針對單框架的程式碼。

---

## 技能目錄

技能連結開啟各自的 `SKILL.md`。展開每個學科下的 **詳情** 可看每個技能的一句話用途。目錄順序遵循[四層系統](#系統四層行銷作業系統)——先 Narrative（L1 · Strategy），接著五個常駐通路，再 Launch（L3 · Orchestration），最後協議層。

### Narrative — TALE（16）

`narrative/` 下四個階段目錄（各 4 技能）按 TALE 循環排布（Trace → Architect → Land → Evaluate）；門（⛩ narrative-quality-auditor）位於 Evaluate。只有門計算目標加權 NQS——其餘技能各管一個槓桿並交棒。Narrative 是 L1 · Strategy 層：五個常駐通路繼承的同一種品牌聲音。它吸收定位——`positioning-mapper` 實體仍在 `launch/`，邏輯上讀作 TALE Trace 的最前端。

| 階段 | 技能 |
|------|------|
| **Trace** | [narrative-baseline-mapper](../narrative/trace/narrative-baseline-mapper/SKILL.md), [category-narrative-mapper](../narrative/trace/category-narrative-mapper/SKILL.md), [audience-belief-mapper](../narrative/trace/audience-belief-mapper/SKILL.md), [positioning-truth-tracer](../narrative/trace/positioning-truth-tracer/SKILL.md) |
| **Architect** | [strategic-narrative-designer](../narrative/architect/strategic-narrative-designer/SKILL.md), [message-system-architect](../narrative/architect/message-system-architect/SKILL.md), [brand-language-codifier](../narrative/architect/brand-language-codifier/SKILL.md), [story-bank-builder](../narrative/architect/story-bank-builder/SKILL.md) |
| **Land** | [narrative-cascade-planner](../narrative/land/narrative-cascade-planner/SKILL.md), [pitch-narrative-builder](../narrative/land/pitch-narrative-builder/SKILL.md), [narrative-enablement-kit](../narrative/land/narrative-enablement-kit/SKILL.md), [proof-point-packager](../narrative/land/proof-point-packager/SKILL.md) |
| **Evaluate** | ⛩ [narrative-quality-auditor](../narrative/evaluate/narrative-quality-auditor/SKILL.md), [message-test-designer](../narrative/evaluate/message-test-designer/SKILL.md), [narrative-resonance-monitor](../narrative/evaluate/narrative-resonance-monitor/SKILL.md), [narrative-drift-monitor](../narrative/evaluate/narrative-drift-monitor/SKILL.md) |

<details><summary><b>逐技能用途（Narrative）</b></summary>

| 技能 | TALE 槓桿 | 用途 |
|------|-----------|------|
| narrative-baseline-mapper | T | 擷取當前散落於自有陣地的真實品牌故事——任何重設計之前那個誠實的起點。 |
| category-narrative-mapper | T | 梳理品類的主導敘事與具名替代品，讓品牌能主張一個可防守、有差異的位置。 |
| audience-belief-mapper | T | 揭示目標受眾已經相信、懷疑與在意什麼——敘事必須撼動的那些信念。 |
| positioning-truth-tracer | T | 把每一條定位主張追溯回實證，淘汰任何無支撐者（T1 真相否決的上游）。 |
| strategic-narrative-designer | A | 設計核心策略敘事——品牌所領銜的「改變世界」故事弧、賭注與收束。 |
| message-system-architect | A | 架構訊息體系——slogan、支柱、證明點與逐受眾角度，構成一套連貫結構。 |
| brand-language-codifier | A | 編纂聲音、語氣、詞彙、do/don't 用語，讓每個通路聽起來都是同一個品牌。 |
| story-bank-builder | A | 建立可複用的證明故事、客戶敘事與類比庫，供各通路取用。 |
| narrative-cascade-planner | L | 規劃敘事如何無稀釋、無漂移地級聯進每個通路與時刻。 |
| pitch-narrative-builder | L | 把敘事塑成 pitch 形態——deck 骨架、demo 故事、投資人/媒體框架。 |
| narrative-enablement-kit | L | 讓每個團隊都能一致講故事的賦能包——talk track、FAQ、訊息地圖。 |
| proof-point-packager | L | 把證明點打包成通路就緒、感知聲明台帳的資產。 |
| ⛩ narrative-quality-auditor | T+A+L+E（NQS） | auditor-class TALE 門：算 NQS、跑 T1/A1/L1/E1、產出 SHIP/FIX/BLOCK；含**敘事採用 go/no-go**模式。 |
| message-test-designer | E | 設計訊息測試——變體矩陣、受眾分組、對策略敘事的共鳴判讀。 |
| narrative-resonance-monitor | E | 用 keyless 來源追蹤敘事在各通路的落地情況（proxy 資料已標註）。 |
| narrative-drift-monitor | E | 監視敘事漂移——各通路偏離核准正典之處——並標記校正。 |

**跨學科複用**（計入原階段，不重複造輪子）：[positioning-mapper](../launch/research/positioning-mapper/SKILL.md)（邏輯上是 Trace 的最前端，實體在 `launch/`）、[message-house-builder](../launch/assemble/message-house-builder/SKILL.md)、`audience-mapper`、`share-of-voice-tracker`（共鳴分母）。**無新連接器**——敘事共鳴複用 `bluesky.py` / `gdelt.py` / `tavily.py` / `wayback.py`——見 [tale-benchmark.md](../references/tale-benchmark.md)。

</details>

### SEO/GEO（16）

四個階段目錄（各 4 技能），外加本學科的兩個品質門（標 ⛩）。

| 階段 | 技能 |
|------|------|
| **Research** | [keyword-research](../seo-geo/research/keyword-research/SKILL.md), [competitor-analysis](../seo-geo/research/competitor-analysis/SKILL.md), [serp-analysis](../seo-geo/research/serp-analysis/SKILL.md), [content-gap-analysis](../seo-geo/research/content-gap-analysis/SKILL.md) |
| **Build** | [content-writer](../seo-geo/build/content-writer/SKILL.md), [geo-content-optimizer](../seo-geo/build/geo-content-optimizer/SKILL.md), [serp-markup-builder](../seo-geo/build/serp-markup-builder/SKILL.md), [page-play-builder](../seo-geo/build/page-play-builder/SKILL.md) |
| **Optimize** | ⛩ [content-quality-auditor](../seo-geo/optimize/content-quality-auditor/SKILL.md), [technical-seo-checker](../seo-geo/optimize/technical-seo-checker/SKILL.md), [on-page-seo-auditor](../seo-geo/optimize/on-page-seo-auditor/SKILL.md), [site-structure-optimizer](../seo-geo/optimize/site-structure-optimizer/SKILL.md) |
| **Monitor** | ⛩ [domain-authority-auditor](../seo-geo/monitor/domain-authority-auditor/SKILL.md), [rank-tracker](../seo-geo/monitor/rank-tracker/SKILL.md), [performance-monitor](../seo-geo/monitor/performance-monitor/SKILL.md), [offsite-signal-analyzer](../seo-geo/monitor/offsite-signal-analyzer/SKILL.md) |

<details><summary><b>逐技能用途（SEO/GEO）</b></summary>

| 技能 | 用途 |
|------|------|
| keyword-research | 為頁面/主題/活動開啟關鍵字工作——意圖、需求、臨門一腳機會。 |
| competitor-analysis | 分析競品 SEO 策略，對比網域，挖出其關鍵字與缺口。 |
| serp-analysis | 讀懂 SERP——特性、摘要、People Also Ask、某查詢的排名規律。 |
| content-gap-analysis | 找出相對競品缺失的主題與覆蓋空洞。 |
| content-writer | *（合併 seo-content-writer + content-refresher）* 撰寫並刷新 SEO 最佳化的文章、著陸頁、產品文案。 |
| geo-content-optimizer | 為 AI 引擎（ChatGPT、Perplexity、AI Overviews、Gemini、Claude、Copilot）最佳化內容。 |
| serp-markup-builder | *（合併 meta-tags-optimizer + schema-markup-generator）* 標題/meta/OG/Twitter 標籤 + JSON-LD / Schema.org 結構化資料。 |
| page-play-builder | *（合併 programmatic + parasite + comparison + local，4 模式）* 範本驅動頁面打法——批量頁、第三方平台發布、對比頁、本地/GBP。 |
| ⛩ content-quality-auditor | 80 項 CORE-EEAT 發布就緒門（SHIP/FIX/BLOCK）。 |
| technical-seo-checker | 網站速度、Core Web Vitals、索引、可抓取性、robots。 |
| on-page-seo-auditor | 稽核頁面級 on-page 健康度——標題層級、關鍵字佈局、圖片、品質訊號。 |
| site-structure-optimizer | *（合併 internal-linking-optimizer + site-architecture）* 內部連結、錨文字、孤立頁、頁面層級、URL 分類、hub/spoke 主題叢集。 |
| ⛩ domain-authority-auditor | 40 項 CITE 網域信任門（TRUSTED/CAUTIOUS/UNTRUSTED）。 |
| rank-tracker | 追蹤關鍵字排名、位次變化與跌幅。 |
| performance-monitor | *（合併 performance-reporter + alert-manager）* 多指標 SEO/GEO 報告、看板與閾值告警。 |
| offsite-signal-analyzer | *（合併 backlink-analyzer + ai-traffic）* 外連檔案 + 連結品質，加上在你自己的 GA4/GSC/日誌中度量 AI 助手引薦流量。 |

</details>

### 紅人（16）

四個階段目錄（各 4 技能）；本學科的門（⛩ content-reviewer）位於 Activate。

| 階段 | 技能 |
|------|------|
| **Discover** | [audience-mapper](../influencer/discover/audience-mapper/SKILL.md), [trend-spotter](../influencer/discover/trend-spotter/SKILL.md), [influencer-discovery](../influencer/discover/influencer-discovery/SKILL.md), [fit-scorer](../influencer/discover/fit-scorer/SKILL.md) |
| **Plan** | [competitor-tracker](../influencer/plan/competitor-tracker/SKILL.md), [campaign-planner](../influencer/plan/campaign-planner/SKILL.md), [brief-generator](../influencer/plan/brief-generator/SKILL.md), [budget-optimizer](../influencer/plan/budget-optimizer/SKILL.md) |
| **Activate** | [outreach-manager](../influencer/activate/outreach-manager/SKILL.md), ⛩ [content-reviewer](../influencer/activate/content-reviewer/SKILL.md), [contract-helper](../influencer/activate/contract-helper/SKILL.md), [content-amplifier](../influencer/activate/content-amplifier/SKILL.md) |
| **Measure** | [landing-optimizer](../influencer/measure/landing-optimizer/SKILL.md), [performance-analyzer](../influencer/measure/performance-analyzer/SKILL.md), [roi-calculator](../influencer/measure/roi-calculator/SKILL.md), [report-generator](../influencer/measure/report-generator/SKILL.md) |

<details><summary><b>逐技能用途（紅人）</b></summary>

| 技能 | 用途 |
|------|------|
| audience-mapper | *（合併 audience-analyzer + niche-researcher）* 在與創作者合作前做受眾畫像，並摸清其亞文化 / 微社群。 |
| trend-spotter | 活動節奏與主題——趨勢話題、聲音、內容格式、文化時刻。 |
| influencer-discovery | 從零搭建紅人名單、拓展新平台、規模化找 nano/micro。 |
| fit-scorer | 對候選名單做客觀加權適配打分（基於 C³ ACE）。 |
| competitor-tracker | 競品的合作紅人、活動、格式、估算觸及/花費與缺口。 |
| campaign-planner | 規劃活動、產品發布、tentpole 或常態化創作者專案。 |
| brief-generator | 標準化紅人 brief 與可複用團隊範本。 |
| budget-optimizer | 跨層級/平台分配預算、預測 ROI、建模情境（同時服務付費廣告的花費 + 出價節奏）。 |
| outreach-manager | pitch、跟進節奏、再啟用、費率談判、狀態追蹤。 |
| ⛩ content-reviewer | 對紅人提交內容做發布前門決策（C³ ART：FTC 揭露 T1、聲明真實性 T2）。 |
| contract-helper | 起草/審閱創作者協議——使用權、獨家、標準條款。 |
| content-amplifier | *（合併 content-amplifier + ugc-repurposer）* 用付費投放放大自然創作者內容，並把 UGC 二次利用到付費、網站、郵件、自然社媒。 |
| landing-optimizer | 面向創作者/付費流量的著陸頁——訊息一致、行動裝置、A/B（同時服務付費點擊後）。 |
| performance-analyzer | 評估創作者結果、橫比創作者、情感、轉換（同時是付費跨通路記分卡）。 |
| roi-calculator | 度量/預測 ROI、為預算辯護、評估創作者/層級價值（共享回報計算引擎，含付費）。 |
| report-generator | 週期結束後面向利害關係人的書面報告（同時出付費廣告報告）。 |

</details>

### 付費廣告 — ROAS（16）

`ad/` 下四個階段目錄（各 4 技能）按 ROAS 循環排布；門（⛩ ad-account-auditor）位於 Activate。只有門計算目標加權 RQS——其餘技能各管一個槓桿並交棒。

| 階段 | 技能 |
|------|------|
| **Research** | [campaign-architect](../ad/research/campaign-architect/SKILL.md), [audience-segment-builder](../ad/research/audience-segment-builder/SKILL.md), [search-term-miner](../ad/research/search-term-miner/SKILL.md), [product-feed-optimizer](../ad/research/product-feed-optimizer/SKILL.md) |
| **Orchestrate** | [ad-creative-builder](../ad/orchestrate/ad-creative-builder/SKILL.md), [ad-test-designer](../ad/orchestrate/ad-test-designer/SKILL.md), [bid-strategy-planner](../ad/orchestrate/bid-strategy-planner/SKILL.md), [landing-experience-checker](../ad/orchestrate/landing-experience-checker/SKILL.md) |
| **Activate** | ⛩ [ad-account-auditor](../ad/activate/ad-account-auditor/SKILL.md), [conversion-signal-qa](../ad/activate/conversion-signal-qa/SKILL.md), [placement-exclusion-manager](../ad/activate/placement-exclusion-manager/SKILL.md), [conversion-value-mapper](../ad/activate/conversion-value-mapper/SKILL.md) |
| **Scale** | [paid-measurement-loop](../ad/scale/paid-measurement-loop/SKILL.md), [attribution-reconciler](../ad/scale/attribution-reconciler/SKILL.md), [budget-pacing-monitor](../ad/scale/budget-pacing-monitor/SKILL.md), [fatigue-frequency-manager](../ad/scale/fatigue-frequency-manager/SKILL.md) |

<details><summary><b>逐技能用途（付費廣告）</b></summary>

| 技能 | ROAS 槓桿 | 用途 |
|------|-----------|------|
| campaign-architect | A + 結構 | 帳戶/活動結構、campaign 類型選型、比對類型、否定詞/排除、付費↔自然蠶食；含常態化**搜尋詞挖掘**模式。 |
| audience-segment-builder | A | 把自有客戶/CRM/GA4 匯出轉為種子受眾、相似種子、排除人群、漏斗分層鎖定地圖。 |
| search-term-miner | A | *（NEW）* 從搜尋詞報告挖掘否定詞、新增關鍵字候選與比對類型收斂。 |
| product-feed-optimizer | O | *（NEW）* Shopping/PMax feed 品質——標題、屬性、GTIN、品類對應與拒登修復。 |
| ad-creative-builder | O | RSA 標題/描述、hook、角度矩陣，並與目標頁訊息一致。 |
| ad-test-designer | O（+S） | 設計 A/B/n 與增量實驗（假設、變體矩陣、樣本量/檢定力），判讀顯著性 → promote/kill。 |
| bid-strategy-planner | S | *（NEW）* 選型並配置出價策略（tCPA/tROAS/max-conversions）、設定目標種子、規劃學習期過渡。 |
| landing-experience-checker | O | *（NEW）* 點擊後頁面 QA——廣告相關性、載入速度、行動裝置、政策——即廣告↔頁面訊息一致檢查。 |
| ⛩ ad-account-auditor | R+O+A+S（RQS） | auditor-class ROAS 門：算 RQS、跑 R1/R2/O1/O2/A1、產出 SHIP/FIX/BLOCK；含**上線 go/no-go**模式。 |
| conversion-signal-qa | R | 上線前追蹤 QA（事件觸發、UTM 規範、去重門控、視窗對齊、iOS-ATT 標記）——R1/R2 的前置（建訊號，門打分）。 |
| placement-exclusion-manager | A | *（NEW）* 版位/受眾排除名單——品牌安全封鎖、垃圾版位剪除、浪費花費抑制。 |
| conversion-value-mapper | R | *（NEW）* 把轉換動作對應到價值/權重與價值規則，讓 tROAS 依真實毛利而非原始次數出價。 |
| paid-measurement-loop | R（+S） | 把一次上線的改動相對對照在視窗內回讀 → Promote / Keep-testing / Rollback / Unproven。 |
| attribution-reconciler | R | 針對 GA4/ecommerce 訂單 ID 真值集做常態去重、視窗/幣別歸一、模型對比、增量。 |
| budget-pacing-monitor | S | *（NEW）* 在投放期追蹤消耗節奏對比預算，標記欠投/超投，並建議配速校正。 |
| fatigue-frequency-manager | O | *（NEW）* 監視頻次與創意衰減訊號，標記疲勞廣告，並排程刷新/輪換。 |

**跨學科複用**（計入原階段，不重複造輪子）：[budget-optimizer](../influencer/plan/budget-optimizer/SKILL.md)（花費 + 出價節奏/學習期模式）、[landing-optimizer](../influencer/measure/landing-optimizer/SKILL.md)（點擊後）、[roi-calculator](../influencer/measure/roi-calculator/SKILL.md)（回報計算）、[report-generator](../influencer/measure/report-generator/SKILL.md)、[performance-analyzer](../influencer/measure/performance-analyzer/SKILL.md)。

</details>

### 郵件行銷 — SEND（16）

`email/` 下四個階段目錄（各 4 技能）按 SEND 循環排布；門（⛩ email-quality-auditor）位於 Deliver。只有門計算目標加權 EQS——其餘技能各管一個槓桿並交棒。用例無關（B2C 生命週期 / B2B 冷觸達 / newsletter-creator），由目標權重欄決定側重。

| 階段 | 技能 |
|------|------|
| **Setup** | [deliverability-qa](../email/setup/deliverability-qa/SKILL.md), [list-segment-builder](../email/setup/list-segment-builder/SKILL.md), [list-growth-designer](../email/setup/list-growth-designer/SKILL.md), [list-hygiene-monitor](../email/setup/list-hygiene-monitor/SKILL.md) |
| **Engage** | [email-creative-builder](../email/engage/email-creative-builder/SKILL.md), [subject-line-lab](../email/engage/subject-line-lab/SKILL.md), [email-render-builder](../email/engage/email-render-builder/SKILL.md), [dynamic-content-personalizer](../email/engage/dynamic-content-personalizer/SKILL.md) |
| **Nurture** | [email-sequence-designer](../email/nurture/email-sequence-designer/SKILL.md), [newsletter-monetization-planner](../email/nurture/newsletter-monetization-planner/SKILL.md), [preference-frequency-manager](../email/nurture/preference-frequency-manager/SKILL.md), [reactivation-specialist](../email/nurture/reactivation-specialist/SKILL.md) |
| **Deliver** | ⛩ [email-quality-auditor](../email/deliver/email-quality-auditor/SKILL.md), [send-experiment-designer](../email/deliver/send-experiment-designer/SKILL.md), [inbox-placement-monitor](../email/deliver/inbox-placement-monitor/SKILL.md), [cold-outbound-sequencer](../email/deliver/cold-outbound-sequencer/SKILL.md) |

<details><summary><b>逐技能用途（郵件行銷）</b></summary>

| 技能 | SEND 槓桿 | 用途 |
|------|-----------|------|
| deliverability-qa | S | 發送前 SPF/DKIM/DMARC/BIMI 認證、聲譽、收件匣落位、垃圾內容、清單衛生（S1 檢查）。 |
| list-segment-builder | E | 從自有清單/CRM/GA4 匯出建構行為 + 生命週期階段分群與抑制規則。 |
| list-growth-designer | S（+N） | 清單成長策略——獲取通路、lead magnet 構思、合規的雙重確認擷取流程 spec、推薦環機制；在獲取點餵入 S 同意品質。 |
| list-hygiene-monitor | S | *（NEW）* 持續的清單健康度——退信/投訴清理、sunset 政策、再確認、非活躍分群抑制。 |
| email-creative-builder | E（+D） | 主旨/預覽文字/內文/CTA，與著陸頁訊息一致，感知聲明台帳。 |
| subject-line-lab | S | *（NEW）* 主旨/預覽文字構思與評分——長度、垃圾觸發詞、好奇/清晰平衡、測試用變體集。 |
| email-render-builder | E | *（NEW）* HTML 郵件建置/QA——用戶端相容、暗色模式、可存取性、純文字替代、渲染測試清單。 |
| dynamic-content-personalizer | E | *（NEW）* 合併標籤/liquid 個人化塊、條件內容規則、回退值安全。 |
| email-sequence-designer | N | 生命週期/自動化流程（歡迎、棄購、購後、召回）+ 頻次治理。 |
| newsletter-monetization-planner | D | 付費訂閱、贊助位庫存 + 刊例、推薦成長循環經濟。 |
| preference-frequency-manager | N | *（NEW）* 偏好中心設計與發送頻次治理，以削減疲勞與退訂。 |
| reactivation-specialist | N | *（NEW）* 沉睡訂閱者的 win-back / 再互動流程，含 sunset-or-recover 決策規則。 |
| ⛩ email-quality-auditor | S+E+N+D（EQS） | auditor-class SEND 門：算 EQS、跑 S1/S2/N1/D1、產出 SHIP/FIX/BLOCK；含**發送前 go/no-go**模式。 |
| send-experiment-designer | E | A/B / 發送時間 / hold-out 設計，含樣本量 + 顯著性判讀（promote/kill）。 |
| inbox-placement-monitor | S | *（NEW）* 透過 seed 清單與供應商訊號持續追蹤收件匣 vs 垃圾落位，並帶聲譽漂移告警。 |
| cold-outbound-sequencer | D | *（NEW）* 合規 B2B 冷觸達節奏——送達安全的爬坡、個人化 token、回覆處理步驟。 |

**跨學科複用**（計入原階段，不重複造輪子）：[audience-mapper](../influencer/discover/audience-mapper/SKILL.md)、[landing-optimizer](../influencer/measure/landing-optimizer/SKILL.md)、[roi-calculator](../influencer/measure/roi-calculator/SKILL.md)、[report-generator](../influencer/measure/report-generator/SKILL.md)、[performance-analyzer](../influencer/measure/performance-analyzer/SKILL.md)、[offer-claims-registry](../protocol/offer-claims-registry/SKILL.md)。

</details>

### 產品發布 — RAMP（16）

`launch/` 下四個階段目錄（各 4 技能）按 RAMP 循環排布；門（⛩ launch-readiness-auditor）位於 Mobilize。只有門計算目標加權 LQS——其餘技能各管一個槓桿並交棒。用例無關（B2B SaaS 銷售主導 / dev-tool 社群發布 / 行動 app 商店發布），由目標權重欄決定側重。

| 階段 | 技能 |
|------|------|
| **Research** | [positioning-mapper](../launch/research/positioning-mapper/SKILL.md), [launch-tier-planner](../launch/research/launch-tier-planner/SKILL.md), [launch-window-planner](../launch/research/launch-window-planner/SKILL.md), [early-access-designer](../launch/research/early-access-designer/SKILL.md) |
| **Assemble** | [message-house-builder](../launch/assemble/message-house-builder/SKILL.md), [launch-asset-packager](../launch/assemble/launch-asset-packager/SKILL.md), [pricing-packaging-planner](../launch/assemble/pricing-packaging-planner/SKILL.md), [sales-enablement-kit](../launch/assemble/sales-enablement-kit/SKILL.md) |
| **Mobilize** | ⛩ [launch-readiness-auditor](../launch/mobilize/launch-readiness-auditor/SKILL.md), [launch-day-conductor](../launch/mobilize/launch-day-conductor/SKILL.md), [community-launch-runner](../launch/mobilize/community-launch-runner/SKILL.md), [press-media-relations](../launch/mobilize/press-media-relations/SKILL.md) |
| **Prove** | [launch-monitor](../launch/prove/launch-monitor/SKILL.md), [launch-feedback-synthesizer](../launch/prove/launch-feedback-synthesizer/SKILL.md), [launch-retro-analyzer](../launch/prove/launch-retro-analyzer/SKILL.md), [momentum-planner](../launch/prove/momentum-planner/SKILL.md) |

<details><summary><b>逐技能用途（產品發布）</b></summary>

| 技能 | RAMP 槓桿 | 用途 |
|------|-----------|------|
| positioning-mapper | R | Dunford 式定位畫布——具名競爭替代品、獨特屬性、價值主題、灘頭細分、onlyness 陳述。 |
| launch-tier-planner | R | 分級決策（Tier 1 旗艦 / Tier 2 定向 / Tier 3 changelog 級）、發布類型宣告、KPI 目標、帶 kill criteria 的風險登記冊。 |
| launch-window-planner | R | 候選視窗對比（衝突 / 順風 / 風險）、launch-week vs 滾動發布裁決、商店審核緩衝、禁運期視窗定義。 |
| early-access-designer | R | waitlist→concept→alpha→beta→GA 階段階梯，含畢業標準、cohort 門控、回饋閉環、推薦機制（R1 階段真相否決的上游）。 |
| message-house-builder | A | 訊息屋（tagline、one-liner、價值支柱、證明點）+ working-backwards PR-FAQ 骨架 + 逐通路角度包（A1 的上游）。 |
| launch-asset-packager | A | 分級化發布資產清單——press kit 規格、demo/截圖規格、發布 FAQ、商店 listing 中繼資料、技術上線檢查表。 |
| pricing-packaging-planner | A | 發布定價與打包——層級結構、價值到定價地圖、launch-offer 階梯、帶畢業路徑的 beta 定價、保證條款。 |
| sales-enablement-kit | A | 內部賦能——battle card、銷售 talk track、異議處理表、內部 FAQ + CS macros、遵守禁運紀律的內部公告。 |
| ⛩ launch-readiness-auditor | R+A+M+P（LQS） | auditor-class RAMP 門：算 LQS、跑 R1/A1/M1/P1、產出 SHIP/FIX/BLOCK；含**T-1 go/no-go**模式。 |
| launch-day-conductor | M | 逐小時分塊的發布日 runbook——前置條件門檢查、不可逆推送後的觀察窗裁決、P0–P3 事件階梯 + 回滾 playbook。 |
| community-launch-runner | M | 逐平台提交包（Product Hunt、Show HN、subreddit、目錄波次、區域/中文通路），置於平台紅線檢查之下。 |
| press-media-relations | M | 三層媒體/分析師名單、禁運 pitch 擇時、標準結構新聞稿草稿、分析師簡報大綱。 |
| launch-monitor | P | T-0→T+30 視窗監控——儀表化驗證（P1 的上游）、排名/評論/新聞輪詢、D0/W1/M1 KPI 快照、spike-vs-sustain 判讀。 |
| launch-feedback-synthesizer | P | 回饋主題摘要、open→shipped 狀態環（「you asked, we shipped」）、合規社證收割。 |
| launch-retro-analyzer | P | D1/W1/M1 複盤——逐通路實際 vs 目標、對最大偏差做 5-Whys、keep/kill/change 決策、成果快照寫回註冊表。 |
| momentum-planner | P | T+1→T+30 勢能計畫——發布時刻行事曆、公告分級路由、relaunch 正當性裁決、下一個 Tier-1 時刻。 |

**跨學科複用**（計入原階段，不重複造輪子）：`audience-mapper`、`trend-spotter`、`budget-optimizer`、`landing-optimizer`、`campaign-planner`、`outreach-manager`、`content-amplifier`、`email-creative-builder` / `email-sequence-designer` / `cold-outbound-sequencer`、`campaign-architect` / `ad-creative-builder`、`page-play-builder` / `content-writer`、`technical-seo-checker` / `serp-markup-builder`、`performance-monitor`、`keyword-research`、`entity-optimizer`、`offer-claims-registry`、`consent-registry`、`list-growth-designer`、`roi-calculator` / `performance-analyzer` / `report-generator`——見 [ramp-benchmark.md](../references/ramp-benchmark.md)。

</details>

### 社媒 — ECHO（16）

`social/` 下四個階段目錄（各 4 技能）按 ECHO 循環排布；門（⛩ social-quality-auditor）位於 Host。只有門計算目標加權 SQS——其餘技能各管一個槓桿並交棒。用例無關（社群/dev-tool / B2C 品牌 / B2B 創辦人主導），由目標權重欄決定側重。本學科**不**提供任何發文、互動或私訊自動化。

| 階段 | 技能 |
|------|------|
| **Explore** | [channel-portfolio-planner](../social/explore/channel-portfolio-planner/SKILL.md), [voice-dossier-builder](../social/explore/voice-dossier-builder/SKILL.md), [platform-norm-profiler](../social/explore/platform-norm-profiler/SKILL.md), [participation-warmup-planner](../social/explore/participation-warmup-planner/SKILL.md) |
| **Craft** | [social-calendar-builder](../social/craft/social-calendar-builder/SKILL.md), [social-creative-builder](../social/craft/social-creative-builder/SKILL.md), [short-video-scripter](../social/craft/short-video-scripter/SKILL.md), [advocacy-program-designer](../social/craft/advocacy-program-designer/SKILL.md) |
| **Host** | ⛩ [social-quality-auditor](../social/host/social-quality-auditor/SKILL.md), [engagement-inbox-manager](../social/host/engagement-inbox-manager/SKILL.md), [social-selling-planner](../social/host/social-selling-planner/SKILL.md), [crisis-response-planner](../social/host/crisis-response-planner/SKILL.md) |
| **Observe** | [social-pulse-monitor](../social/observe/social-pulse-monitor/SKILL.md), [share-of-voice-tracker](../social/observe/share-of-voice-tracker/SKILL.md), [dark-social-attributor](../social/observe/dark-social-attributor/SKILL.md), [social-measurement-loop](../social/observe/social-measurement-loop/SKILL.md) |

<details><summary><b>逐技能用途（社媒）</b></summary>

| 技能 | ECHO 槓桿 | 用途 |
|------|-----------|------|
| channel-portfolio-planner | E | 從受眾真正所在之處挑選平台組合與逐通路角色/節奏（把通路記錄進註冊表）。 |
| voice-dossier-builder | E | 品牌聲音、語氣、人設、do/don't 詞彙，以維持一致的、像人的存在感。 |
| platform-norm-profiler | E | 發文前的逐平台規範、格式、排名訊號與紅線規則。 |
| participation-warmup-planner | E | 非推廣的社群暖場計畫——在推銷之前，在哪裡現身並創造價值。 |
| social-calendar-builder | C | 內容行事曆——主題、系列、與真實產能平衡的節奏（不過度發文）。 |
| social-creative-builder | C | 平台原生貼文（hook/內文/CTA），訊息一致且感知聲明台帳。 |
| short-video-scripter | C | 短影音腳本——hook、節拍、螢幕文字、留存結構。 |
| advocacy-program-designer | C | 員工/社群倡導計畫——opt-in、揭露預設值、可分享資產包。 |
| ⛩ social-quality-auditor | E+C+H+O（SQS） | auditor-class ECHO 門：算 SQS、跑 E1/C1/C2/H1/H2/O1、產出 SHIP/FIX/BLOCK；含**發布前 go/no-go**模式。 |
| engagement-inbox-manager | H | 回覆/留言/私訊分診 playbook——回應分層、升級、真誠互動紀律（不製造/誘餌式互動）。 |
| social-selling-planner | H | 創辦人/團隊社交銷售動作——關係優先外聯，不做自動化私訊。 |
| crisis-response-planner | H | 預先草擬的危機分層、緩衝聲明、升級階梯、暫停排程觸發條件。 |
| social-pulse-monitor | O | 從 keyless 來源獲取提及/情感/主題脈動、spike-vs-sustain 判讀（proxy 資料已標註）。 |
| share-of-voice-tracker | O | 在週期穩定的分母上，對比具名競品的聲量占比。 |
| dark-social-attributor | O | 歸因 dark-social/無連結流量——UTM 紀律、自報歸因擷取、引薦解析。 |
| social-measurement-loop | O | 把一次上線的改動相對基線在視窗內回讀 → Promote / Keep-testing / Rollback。 |

**跨學科複用**（計入原階段，不重複造輪子）：`trend-spotter`、`audience-mapper`、`content-amplifier`、`outreach-manager`、`competitor-tracker`、`landing-optimizer`、`performance-analyzer`、`roi-calculator`、`report-generator`、`offer-claims-registry`、`community-launch-runner`、`creator-registry`、`page-play-builder`、`memory-management`——見 [echo-benchmark.md](../references/echo-benchmark.md)。

</details>

### 協議層（8）

共享真相與記憶機件——角色與唯一寫入者規則見上文[架構 § 協議層](#協議層)。

| 組 | 技能 |
|----|------|
| **協議層** | [entity-optimizer](../protocol/entity-optimizer/SKILL.md), [creator-registry](../protocol/creator-registry/SKILL.md), [offer-claims-registry](../protocol/offer-claims-registry/SKILL.md), [consent-registry](../protocol/consent-registry/SKILL.md), [launch-registry](../protocol/launch-registry/SKILL.md), [channel-registry](../protocol/channel-registry/SKILL.md), [narrative-registry](../protocol/narrative-registry/SKILL.md), [memory-management](../protocol/memory-management/SKILL.md) |

<details><summary><b>逐技能用途（協議層）</b></summary>

| 技能 | 用途 |
|------|------|
| entity-optimizer | 面向知識圖譜、Wikidata、AI 消歧的規範實體檔案。 |
| creator-registry | 規範創作者名冊/檔案——去重 handle、帶溯源標籤的受眾資料、費率、合規歷史。 |
| offer-claims-registry | 規範 offer 與聲明實證台帳——O1/T2 聲明檢查所對照評判的那份記錄。 |
| consent-registry | 規範的逐主體同意/抑制記錄——opt-in 時間戳 + 合法依據、雙重確認證明、僅追加的退訂/退信/投訴歷史；S2/N1 否決項對照評判的那份記錄。 |
| launch-registry | 規範的逐次發布檔案 + 發布行事曆——分級、發布類型、單向生命週期階段（draft→…→GA）、權威日期 + 禁運期承諾、通路提交台帳、成果快照；launch 真相 SSOT。 |
| channel-registry | 規範的逐通路記錄——handle、所有權/授權、平台規範、揭露預設值；ECHO E1 通路真相否決所對照評判的通路真相 SSOT。 |
| narrative-registry | 規範的品牌敘事正典——核准的策略敘事、訊息體系、語言/詞彙、證明點；TALE T1 真相否決所對照評判的品牌正典 SSOT。 |
| memory-management | 審閱、提升、降級、封存 HOT/WARM/COLD 專案記憶。 |

</details>

---

## 命令

8 個命令：`/aaron-marketing:auto` 跨全部七學科路由任意目標；每個學科恰有一個顯式入口。原始檔：[commands/](../commands)。

| 命令 | 用途 | 收窄 |
|------|------|------|
| `/aaron-marketing:auto` | 描述任意目標——推斷意圖並執行最小夠用的工作流 | `--deep`（窮盡/壓測） |
| `/aaron-marketing:narrative` | 品牌敘事（TALE 循環）：追溯當前故事與品類、架構策略敘事與訊息體系、落地到各通路、品質門、共鳴與漂移 | `--phase trace\|architect\|land\|evaluate` |
| `/aaron-marketing:seo-geo` | SEO/GEO 端到端：研究需求/競品、創作內容、稽核品質/技術/可見性/權威、追蹤排名/報告/記憶 | `--mode research\|create\|audit\|track` + 各模式子參數（`--competitors` `--map` · `--brief` `--series` `--refresh` `--publish` `--meta` `--schema` `--type` · `--full` `--tech` `--visibility` `--authority` · `--alert` `--report` `--remember` `--period`） |
| `/aaron-marketing:influencer` | 紅人：受眾洞察、發現與適配、規劃、外聯、放大、ROI | `--phase discover\|plan\|activate\|measure` |
| `/aaron-marketing:ad` | 付費廣告（ROAS 循環）：分群、結構、創意、實驗設計、稽核門、衡量 | `--phase research\|orchestrate\|activate\|scale` |
| `/aaron-marketing:email` | 郵件行銷（SEND 循環）：送達/同意、分群、創意、生命週期流程、變現、發送測試、稽核門 | `--phase setup\|engage\|nurture\|deliver` |
| `/aaron-marketing:launch` | 產品發布（RAMP 循環）：定位、分級與擇時、訊息屋與資產、就緒門、發布日執行、監控與複盤 | `--phase research\|assemble\|mobilize\|prove` |
| `/aaron-marketing:social` | 自然社媒（ECHO 循環）：通路組合與聲音、行事曆與創意、品質門、互動/危機主持、脈動與衡量 | `--phase explore\|craft\|host\|observe` |

日常工作通常從 `/aaron-marketing:auto` 開始；其餘七個是顯式的學科入口，用 `--mode` / `--phase` 收窄階段。

**改名說明：** 命令使用 `/aaron-marketing:` 前綴。原 `research` / `create` / `audit` / `track` 四個命令現為 `/aaron-marketing:seo-geo` 的 `--mode`（子參數不變）。舊 `/seo:*` 與 `/aaron-seo-geo:*` 可經 `auto` 恢復——例如 `/aaron-marketing:auto /aaron-seo-geo:audit https://example.com/blog/post` 返回 `/aaron-marketing:seo-geo https://example.com/blog/post --mode audit`。

---

## 連接器與層級

技能用 `~~category` 佔位符（`~~SEO tool`、`~~web analytics`、`~~ad platform`、`~~email platform` 等）而非具體廠商命名，且每個類別都有 **keyless 的 Tier-1 路徑**。完整配方（含每個類別的免費/第一方端點）見 [CONNECTORS.md](../CONNECTORS.md)。

### 連接器層本身就是一件產品

**100+ 條記錄在案的整合路徑**，分三個精心設計的層——每一條都名副其實：

| 層 | 你得到什麼 |
|----|------------|
| **21 個內建零依賴連接器** | 純 Python 標準庫——無 `pip`、無建置。keyless 即時 SERP + JS 渲染抓取（Firecrawl、Tavily）、AI 答案引用探針、DNS-over-HTTPS 郵件認證拉取、維基百科關注度序列、GDELT 新聞提及、真實 YouTube 創作者指標、IndexNow + 百度收錄推送、Resend ESP 自動化，以及能把上述任一變成前後對比時間序列的 git 可差分測量台帳。 |
| **60+ 個記錄在案的官方/免費 API** | 每一行都連結廠商**官方文件**、帶核驗日期，且每條連結入庫前都經過 HTTP 實測。包含多數工具清單遺漏的路徑：GSC URL Inspection、CrUX History（40 週真實使用者 CWV）、Gmail Postmaster Tools API、Meta 廣告庫、微軟 Clarity 資料匯出 API。 |
| **廠商 MCP 伺服器** | 18 個遠端端點入目錄（絕不自動註冊——你的 `/mcp` 清單保持乾淨），外加 Google Analytics、Search Console、**Google Ads**、**微軟 Clarity** 的官方自架伺服器。其中兩個遠端 MCP 完全免鑑權（Firecrawl、Tavily）。 |

讓它們可信而不只是數量多的四個理由：

- **三類安全等級、工程化門控**（[SECURITY.md](../SECURITY.md)）：託管抓取器在每次委託抓取前**本地預檢 robots.txt**、遇 Disallow 拒絕執行；一切改變外部狀態的操作（發郵件、推送收錄）**預設 dry-run**，必須顯式 `--live` 才執行，廠商支援冪等鍵就用、不支援就絕不自動重試。
- **核驗，然後再核驗**：端點對照廠商一手文件帶日期核實、keyless 路徑經過真實呼叫測試、CI 守衛強制版本/追蹤同步、發版前的 live 冒煙專抓端點漂移（它已經兩次抓到真實的 API 變更）。
- **只報事實、不下判定**：連接器輸出記錄存在性、解析標籤和原始序列；裁決交給 auditor 門，技能給每個數字標註 **Measured / User-provided / Estimated**。
- **成文的 playbook**（[docs/connector-playbook.md](connector-playbook.md)）管轄每一次新增——定性、驗證、實作、測試、接線、文件、追蹤、回歸、歸檔——目錄再成長，品質不滑坡。

| 層級 | 需要 | 你獲得 |
|------|------|--------|
| **Tier 1**（預設） | 無 | 貼上資料，或從免費/公開來源拉取。分析框架照常執行。 |
| **Tier 2** | 一個免費第一方 API 或 MCP | 自動取你自己的 GSC / GA4 / Core Web Vitals 資料。 |
| **Tier 3** | 更完整的 MCP 集 | 全自動多源工作流。 |

- **內建零依賴助手** 位於 `scripts/connectors/`（僅 Python 標準庫），在本地拉取公開/自有資料——如 PageSpeed/CrUX、Open PageRank、頁面抓取、Wayback CDX、Wikidata SPARQL、Common Crawl、advertools 配方——外加 **`resend.py`**：郵件技能直連 Resend ESP 的自動化（免費檔 key：寄件網域認證狀態、種子測試投遞、抑制名單同步、廣播定時發送；變更類子命令預設 dry-run，需 `--live` 才執行）；以及 **`firecrawl.py`** + **`tavily.py`**：研究類技能直連託管抓取器的 keyless 自動化（Firecrawl：即時搜尋結果 + JS 渲染頁 markdown + 站點 URL 清單；Tavily：帶評分的搜尋 + AI 答案引擎引用來源探針（GEO 用）+ URL 擷取——兩者完全無需 key，均內建本地 robots.txt 預檢）。
- **免費/keyless 來源** 按類別記錄：Google Search Console 與 GA4（自有資料）、PageSpeed/CrUX、Wikidata、Common Crawl、Open PageRank、Firecrawl keyless SERP/抓取、Tavily keyless AI 搜尋、DNS-over-HTTPS 郵件認證記錄（`doh.py`）、維基百科關注度序列（`pageviews.py`）、GDELT 新聞提及（`gdelt.py`）、免費 key 的 YouTube 創作者指標（`youtube.py`）、IndexNow + 百度收錄推送（`indexpush.py`，dry-run 門控）、廣告透明庫（Meta/Google/TikTok），以及 crt.sh、W3C 校驗器、oEmbed、HN Algolia 的配方行。
- **選配 MCP 伺服器**（Ahrefs、Semrush、SE Ranking、SISTRIX、SimilarWeb、自架免費的 **OpenSEO** 套件、Cloudflare、Vercel、HubSpot、Amplitude、Notion、Webflow、Sanity、Contentful、Slack、Resend、keyless 的 Firecrawl 與 Tavily）在 [`docs/mcp-catalog.json`](mcp-catalog.json) 中作為**僅複製貼上參考**——目錄位於會被自動註冊的外掛根 `.mcp.json` 路徑之外，不會為你註冊任何東西。把你想要的條目複製進自己的 MCP 設定即可。

付費廣告技能基於你的**自有帳戶手動匯出**（原生廣告管理後台 CSV、GA4、電商）評分。帶金鑰的廣告 API（Google Ads SDK、Meta Marketing API）僅是 opt-in Tier-2/3，**絕不**作為 Tier-1 要求。郵件技能同理——基於你**自己的 ESP 匯出**評分，所有送達率訊號均 keyless（DNS 查詢、DMARC RUA 報告、種子收件測試），帶金鑰的 ESP API 也絕不是 Tier-1 要求；若你的 ESP 是 Resend，內建的 `resend.py` 可在免費檔上自動化同一閉環。

---

## 推薦工作流

**SEO/GEO**
1. **Research** — `keyword-research` → `competitor-analysis` → `content-gap-analysis`
2. **Build** — `content-writer` → `geo-content-optimizer` → `serp-markup-builder` / `page-play-builder`
3. **Optimize** — `content-quality-auditor`（⛩ 發布門） → `on-page-seo-auditor` → `technical-seo-checker` → `site-structure-optimizer`
4. **Monitor** — `rank-tracker` → `performance-monitor` → `offsite-signal-analyzer`；信任評審用 `domain-authority-auditor`（⛩）

**紅人**
1. **Discover** — `audience-mapper` → `trend-spotter` → `influencer-discovery` → `fit-scorer`（C³ ACE）
2. **Plan** — `competitor-tracker` → `campaign-planner` → `brief-generator` → `budget-optimizer`
3. **Activate** — `outreach-manager` → `content-reviewer`（⛩ ART 門） → `contract-helper` → `content-amplifier`
4. **Measure** — `landing-optimizer` → `performance-analyzer` → `roi-calculator` → `report-generator`

**付費廣告（ROAS 循環）**
1. **Research** — `audience-segment-builder` → `campaign-architect`
2. **Orchestrate** — `ad-creative-builder` → `ad-test-designer`（著陸頁配 `landing-optimizer`）
3. **Activate** — `conversion-signal-qa` → `ad-account-auditor`（⛩ RQS 門），在任何預算上線前
4. **Scale** — `paid-measurement-loop` → `attribution-reconciler` → `roi-calculator` → `report-generator`

**郵件行銷（SEND 循環）**
1. **Setup** — `deliverability-qa` → `list-segment-builder`
2. **Engage** — `email-creative-builder`
3. **Nurture** — `email-sequence-designer` → `newsletter-monetization-planner`
4. **Deliver** — `send-experiment-designer` → `email-quality-auditor`（⛩ EQS 門），在任何發送前

要做完整信任評審，把 `content-quality-auditor` 與 `domain-authority-auditor` 搭配，得到合計 120 項的評估。開啟 `memory-management` 後，交棒與未決事項自動留存在 HOT/WARM/COLD 記憶中。

---

## 倉庫結構

```
narrative/{trace,architect,land,evaluate}/                  # Narrative — TALE(16，含其門)
seo-geo/{research,build,optimize,monitor}/                  # SEO/GEO(16，含其 2 個門)
influencer/{discover,plan,activate,measure}/                   # 紅人(16，含其門)
ad/research|orchestrate|activate|scale/            # 付費廣告 — ROAS(16，含其門)
email/setup|engage|nurture|deliver/                  # 郵件行銷 — SEND(16，含其門)
launch/research|assemble|mobilize|prove/             # 產品發布 — RAMP(16，含其門)
social/explore|craft|host|observe/                   # 社媒 — ECHO(16，含其門)
protocol/                                            # 協議層(8) — 真相註冊表 + 記憶
commands/        # 8 個斜線命令(auto、narrative、seo-geo、influencer、ad、email、launch、social)
references/      # 共享契約、狀態模型、八套基準、auditor runbook、平台資料包
evals/           # 各技能結構化 eval 用例 + structure-manifest.json
hooks/           # hooks.json + claude-hook.sh(唯一執行邏輯)
scripts/         # validate-skill.sh + connectors/(標準庫) + CI 守衛
memory/          # HOT/WARM/COLD 鷹架 + 註冊表儲存(entities/creators/claims/consent/launch/channels/narrative-registry)
docs/            # 在地化 README（zh）
.claude-plugin/  # plugin.json + marketplace.json 鏡像
```

---

## 設計哲學

- **技能即內容。** 唯一的程式碼是 Bash 校驗器、Bash hook runner、零依賴的 Python 標準庫連接器/檢查助手。永不引入第三方 / `pip` 依賴——由依賴蔓延守衛強制。
- **keyless 優先。** 每個 `~~category` 都有免費/自有資料配方；MCP 與付費工具純屬便利。
- **外科手術式 & MECE。** 每個技能只擔一項職責，邊界清晰；重疊的工作做成現有技能的*模式*，而非新堆一個薄技能。註冊表存證、門評判、分析器餵門。
- **不編數字。** 技能為每個資料標註 Measured / User-provided / Estimated，並內建 AI 腔 / 禁用詞偵測。
- **合規是指引，不是法律。** FTC 揭露與聲明真實性檢查標註風險，但不構成法律意見。

---

## 品質守衛

每次變更都跑一組 fail-closed 守衛（均在 `scripts/` 與 `tests/`）：

| 守衛 | 檢查 |
|------|------|
| `validate-skill.sh` | 全部 120 個技能的 frontmatter、必備章節、版本一致性、外掛相對連結。 |
| `golden-auditor-math.py` | **八套**框架的權重和 + 工作範例算術的確定性校驗。 |
| `check-evals.py` | eval 結構 lint + `structure-manifest.json`（120/120 技能均帶 eval 用例）。 |
| `check-pii.py` | 攔截提交的金鑰 / PII（token 級允許名單，fail-closed）。 |
| `check-stdlib-only.sh` | 依賴蔓延守衛 + 付費廣告帶金鑰 API 紅線。 |
| `check-versions.sh` | 版本同步守衛：束版本在 plugin.json / 兩個 marketplace 鏡像 / 兩個 README 徽章 / CLAUDE.md / VERSIONS.md 發布行 + changelog 條目間完全一致，且每個 SKILL.md 版本與其 VERSIONS.md 行相符。 |
| `tests/test_connectors_local.py` | 全部連接器純請求建構函式的離線單測（CI 不連網）。 |
| `tests/test_hook_artifact_gate.sh` | hook 的 Artifact Gate + SessionStart 淨化的行為測試。 |

線上端點漂移由**手動**的 [`scripts/connectors/smoke-live.sh`](../scripts/connectors/smoke-live.sh) 單獨覆蓋——每個託管連接器一次最小真實呼叫 + 回應形狀斷言（限速應答記 SKIP）；發版前手動跑，絕不進 CI。

---

## 貢獻與文檔

- **[CONTRIBUTING.md](../CONTRIBUTING.md)** —— 撰寫規則、貢獻清單、權威的 8 檔案追蹤列表。
- **[VERSIONS.md](../VERSIONS.md)** —— 各技能版本 + 變更日誌（目前套件：`16.0.0`）。
- **[SECURITY.md](../SECURITY.md)** · **[PRIVACY.md](../PRIVACY.md)** · **[CODE_OF_CONDUCT.md](../CODE_OF_CONDUCT.md)** —— 安全、隱私、社群政策。
- **[CLAUDE.md](../CLAUDE.md)** / **[AGENTS.md](../AGENTS.md)** —— 面向 Agent 的本倉庫上下文。

---

## 免責聲明

這些技能用於輔助品牌敘事、SEO/GEO、紅人行銷、付費廣告、郵件行銷、產品發布與自然社媒工作流，但**不**保證排名、AI 引用、流量、互動、轉換、ROAS、送達率或任何業務結果。紅人、廣告、郵件與社媒合規檢查（FTC 揭露、聲明真實性、平台政策、同意/opt-in、實質關聯揭露）為指引，非法律意見。在用於重大策略、財務或法律決策之前，請與具備資格的專業人士核實建議。

## 授權條款

Apache License 2.0 —— 見 [LICENSE](../LICENSE)。

*最後同步英文 README：v16.0.3*

## Star History

<a href="https://www.star-history.com/?repos=aaron-he-zhu%2Faaron-marketing-skills&type=date&legend=top-left">
 <picture>
   <source media="(prefers-color-scheme: dark)" srcset="https://api.star-history.com/chart?repos=aaron-he-zhu/aaron-marketing-skills&type=date&theme=dark&legend=top-left" />
   <source media="(prefers-color-scheme: light)" srcset="https://api.star-history.com/chart?repos=aaron-he-zhu/aaron-marketing-skills&type=date&legend=top-left" />
   <img alt="Star History Chart" src="https://api.star-history.com/chart?repos=aaron-he-zhu/aaron-marketing-skills&type=date&legend=top-left" />
 </picture>
</a>
