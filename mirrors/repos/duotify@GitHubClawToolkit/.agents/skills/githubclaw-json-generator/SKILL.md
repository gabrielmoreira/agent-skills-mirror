---
name: githubclaw-json-generator
description: 為 GitHubClawToolkit 的 skill 或 template 目錄生成 githubclaw.json metadata 檔案。當使用者新增、更新 skill/template 並需要建立或更新 githubclaw.json 時觸發。也適用於批次為多個 skill/template 產生 githubclaw.json 的情境。不適用於與 GitHubClawToolkit 無關的一般 JSON 生成需求。
---

# GitHubClaw JSON Generator

為 GitHubClawToolkit repo 中的 skill 或 template 目錄產生標準化的 `githubclaw.json` metadata 檔案，供 GitHubClawCore 統一解析使用。

## 執行流程

### 步驟 1：確認目標目錄

確認使用者指定的目標路徑。目標必須是 `skills/` 或 `templates/` 下的某個子目錄。

- 若使用者未指定，詢問要為哪個 skill 或 template 產生 `githubclaw.json`。
- 若使用者要求批次處理，逐一對每個目錄執行步驟 2–5。

### 步驟 2：掃描目標目錄

讀取目標目錄中的關鍵檔案以提取資訊：

**Skill 目錄優先讀取：**
- `SKILL.md`（提取 name、description、required_env）
- `README.md`（提取描述、用途說明）
- `package.json`（提取 version）
- `scripts/` 目錄內容（判斷功能性質）

**Template 目錄優先讀取：**
- `AGENTS.md`（提取描述、架構說明）
- `README.md`（提取描述、用途說明）
- `.copilot/config.json`（Copilot 框架設定）
- `.codex/config.toml`（Codex 框架設定）
- `.agents/skills/` 目錄內容（判斷內含技能）

### 步驟 3：決定各欄位值

參閱 `references/schema.md` 取得完整欄位規格。核心規則：

1. **name**：使用英文，對應目錄名稱但可加空格（如 `gemini-summary` → `Gemini Summary`）
2. **tagline**：一句繁體中文簡介，不超過 50 字
3. **description**：繁體中文詳細描述，2-4 句話說明功能與適用情境
4. **category**：根據功能選擇合適分類（見 schema.md 中的合法值清單）
5. **tags**：3-6 個相關標籤，使用小寫英文
6. **version**：優先從 `package.json` 取得，無則預設 `1.0.0`
7. **support_url**：固定為 `https://github.com/duotify/GitHubClawToolkit/issues`
8. **homepage**：固定為 `https://learn.duotify.com/courses/githubclaw`
9. **requireEnv**：從 SKILL.md 的 `required_env` 欄位、README 中的環境變數說明、或 scripts 中的 `process.env` 提取

### 步驟 4：生成 JSON

讀取 `assets/githubclaw.template.json` 作為結構範本，填入步驟 3 決定的值，將結果寫入目標目錄的 `githubclaw.json`。

確保 JSON 格式正確：
- 使用 2 空格縮排
- 檔案結尾換行
- 無多餘逗號

### 步驟 5：驗證

執行以下驗證：
- JSON 語法正確（可用 `python3 -m json.tool` 驗證）
- 所有必填欄位皆存在且非空
- `category` 值在合法清單內
- `tags` 為非空陣列
- `requireEnv` 為陣列（可為空）

若驗證失敗，修正後重新寫入。

## 輸出格式範例

```json
{
  "name": "Gemini Summary",
  "tagline": "多格式內容摘要工具，自動辨識輸入類型並輸出繁體中文摘要",
  "description": "Gemini Summary 可自動偵測輸入來源類型（網頁、PDF、影片、音訊），透過 Google Gemini API 產生繁體中文摘要。支援多種格式，一鍵取得精簡重點整理。",
  "category": "content",
  "tags": ["summarization", "gemini", "content-analysis", "multilingual"],
  "version": "1.0.0",
  "support_url": "https://github.com/duotify/GitHubClawToolkit/issues",
  "homepage": "https://learn.duotify.com/courses/githubclaw",
  "requireEnv": ["GEMINI_API_KEY"]
}
```

## 錯誤處理

| 狀況 | 處理方式 |
|------|---------|
| 目標目錄不存在 | 提示使用者確認路徑 |
| 目標目錄無任何描述檔案 | 請使用者提供 name、tagline、description |
| 已存在 `githubclaw.json` | 詢問使用者是否要覆蓋更新 |
| 無法判斷 category | 預設使用 `data`，並提示使用者確認 |
| 無法判斷 requireEnv | 預設為空陣列 `[]`，並提示使用者確認 |
