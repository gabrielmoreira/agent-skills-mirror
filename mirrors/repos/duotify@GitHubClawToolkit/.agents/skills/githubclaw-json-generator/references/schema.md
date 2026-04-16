# githubclaw.json Schema 規格

本文件定義 `githubclaw.json` 的完整欄位規格，供 agent 在產生檔案時參照。

---

## 完整結構

```json
{
  "name": "string",
  "tagline": "string",
  "description": "string",
  "category": "string",
  "tags": ["string"],
  "version": "string",
  "support_url": "string",
  "homepage": "string",
  "requireEnv": ["string"]
}
```

---

## 欄位詳細規格

### name（必填）

- **類型**：string
- **說明**：顯示名稱，使用英文，與目錄名對應但可加空格與大寫
- **規則**：
  - 將目錄名的 `-` 轉為空格，每個單字首字母大寫
  - 例：`gemini-summary` → `Gemini Summary`
  - 例：`felo-x-search` → `Felo X Search`
  - 例：`copilot-gemini-api` → `Copilot Gemini API`

### tagline（必填）

- **類型**：string
- **語言**：繁體中文
- **說明**：一句話簡介，不超過 50 字
- **範例**：`"多格式內容摘要工具，自動辨識輸入類型並輸出繁體中文摘要"`

### description（必填）

- **類型**：string
- **語言**：繁體中文
- **說明**：詳細描述，2-4 句話，說明功能、技術、適用情境
- **範例**：`"Gemini Summary 可自動偵測輸入來源類型（網頁、PDF、影片、音訊），透過 Google Gemini API 產生繁體中文摘要。支援多種格式，一鍵取得精簡重點整理。"`

### category（必填）

- **類型**：string
- **說明**：分類標籤，必須為以下合法值之一

| 值 | 說明 | 適用情境 |
|----|------|---------|
| `data` | 資料搜尋與擷取 | 搜尋引擎、爬蟲、資料提取 |
| `content` | 內容生成與分析 | 摘要、翻譯、圖片生成、簡報 |
| `integration` | 第三方服務整合 | Telegram、LINE、Slack 通知 |
| `automation` | 自動化與工作流程 | 瀏覽器自動化、CI/CD |
| `meta` | 技能管理與輔助 | 技能搜尋、技能建立工具 |
| `starter` | 入門/空白範本 | 最小設定的起步範本 |
| `framework` | 框架整合範本 | 預設整合多項技能的完整範本 |

### tags（必填）

- **類型**：string[]
- **說明**：3-6 個相關標籤
- **規則**：
  - 使用小寫英文
  - 使用 `-` 連接多詞標籤（如 `content-analysis`）
  - 包含核心技術（如 `gemini`、`felo`）
  - 包含功能類型（如 `search`、`summarization`）

### version（必填）

- **類型**：string
- **說明**：語意化版本號（SemVer）
- **規則**：
  - 優先從 `package.json` 的 `version` 欄位取得
  - 無 `package.json` 時預設為 `1.0.0`
  - 格式：`MAJOR.MINOR.PATCH`

### support_url（必填）

- **類型**：string
- **固定值**：`https://github.com/duotify/GitHubClawToolkit/issues`

### homepage（必填）

- **類型**：string
- **固定值**：`https://learn.duotify.com/courses/githubclaw`

### requireEnv（必填）

- **類型**：string[]
- **說明**：該 skill/template 所需的環境變數名稱
- **規則**：
  - 無需環境變數時使用空陣列 `[]`
  - 環境變數名稱使用全大寫、底線分隔（如 `GEMINI_API_KEY`）
  - 提取來源優先順序：
    1. SKILL.md 的 `required_env` frontmatter 欄位
    2. README.md 中明確提及的環境變數
    3. scripts 中 `process.env.XXX` 或 `$XXX` 的用法
    4. .codex/config.toml 或 .copilot/config.json 中的環境變數設定

---

## 常見 requireEnv 對照表

| 環境變數 | 用途 | 常見於 |
|---------|------|--------|
| `GEMINI_API_KEY` | Google Gemini API 金鑰 | gemini-* 系列 skill/template |
| `FELO_API_KEY` | Felo Open API 金鑰 | felo-* 系列 skill/template |
| `TELEGRAM_BOT_TOKEN` | Telegram Bot 令牌 | telegram-notify |
| `TELEGRAM_CHAT_ID` | Telegram 聊天室 ID | telegram-notify |
| `LINE_CHANNEL_ACCESS_TOKEN` | LINE Channel 存取令牌 | line-bot template |
| `LINE_CHANNEL_SECRET` | LINE Channel 密鑰 | line-bot template |

---

## 驗證規則

產生 `githubclaw.json` 後，確認以下條件：

1. JSON 語法正確（無多餘逗號、括號配對正確）
2. 所有 9 個欄位皆存在
3. 無額外欄位（嚴格遵循 schema）
4. `category` 值在合法值清單內
5. `tags` 為非空字串陣列（至少 3 個）
6. `requireEnv` 為字串陣列（可為空）
7. `version` 符合 SemVer 格式
8. `support_url` 與 `homepage` 為固定值
9. `tagline` 與 `description` 為繁體中文
10. 使用 2 空格縮排，檔案結尾有換行
