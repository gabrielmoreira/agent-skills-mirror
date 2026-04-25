# AGENTS.md

## Project Overview

這是一個教育課程資源庫，旨在教導初學者網頁開發基礎。該課程由 Microsoft Cloud Advocates 開發，為期12週，包含24個實作課程，涵蓋 JavaScript、CSS 及 HTML。

### Key Components

- <strong>教育內容</strong>：24個結構化課程，組成專案式模組
- <strong>實作專案</strong>：溫室效應、打字遊戲、瀏覽器擴充功能、太空遊戲、銀行應用程式、程式碼編輯器及 AI 聊天助理
- <strong>互動測驗</strong>：48個測驗，每個包含3題（課前/課後評量）
- <strong>多語言支援</strong>：透過 GitHub Actions 自動翻譯50多種語言
- <strong>技術</strong>：HTML、CSS、JavaScript、Vue.js 3、Vite、Node.js、Express、Python（用於 AI 專案）

### Architecture

- 教育資源庫，採課程結構
- 每個課程資料夾包含 README、範例程式碼及解答
- 獨立專案存於不同目錄（quiz-app、多個課程專案）
- 使用 GitHub Actions (co-op-translator) 的翻譯系統
- 文件由 Docsify 提供，並以 PDF 形式可用

## Setup Commands

本資源庫主要用於教育內容瀏覽。若要操作特定專案：

### Main Repository Setup

```bash
git clone https://github.com/microsoft/Web-Dev-For-Beginners.git
cd Web-Dev-For-Beginners
```

### Quiz App Setup (Vue 3 + Vite)

```bash
cd quiz-app
npm install
npm run dev        # 啟動開發伺服器
npm run build      # 為生產環境編譯
npm run lint       # 執行 ESLint
```

### Bank Project API (Node.js + Express)

```bash
cd 7-bank-project/api
npm install
npm start          # 啟動 API 伺服器
npm run lint       # 執行 ESLint
npm run format     # 使用 Prettier 格式化
```

### Browser Extension Projects

```bash
cd 5-browser-extension/solution
npm install
# 遵循瀏覽器特定的擴充功能載入指示
```

### Space Game Projects

```bash
cd 6-space-game/solution
npm install
# 在瀏覽器中打開 index.html 或使用 Live Server
```

### Chat Project (Python Backend)

```bash
cd 9-chat-project/solution/backend/python
pip install openai
# 設定 GITHUB_TOKEN 環境變量
python api.py
```

## Development Workflow

### For Content Contributors

1. <strong>派生資源庫</strong>至您的 GitHub 帳號
2. <strong>將派生版本複製（clone）</strong>到本機
3. <strong>為變更建立新分支</strong>
4. 修改課程內容或程式碼範例
5. 在相關專案資料夾測試程式碼變更
6. 依照貢獻指引提交 pull request

### For Learners

1. 派生或複製資源庫
2. 依序瀏覽課程資料夾
3. 閱讀每個課程的 README 文件
4. 完成課前測驗 https://ff-quizzes.netlify.app/web/
5. 練習課堂範例程式碼
6. 完成作業與挑戰
7. 參加課後測驗

### Live Development

- <strong>文件</strong>：於根目錄執行 `docsify serve`（預設連接埠3000）
- <strong>測驗應用</strong>：在 quiz-app 目錄執行 `npm run dev`
- <strong>專案</strong>：使用 VS Code Live Server 擴充功能開發 HTML 專案
- **API 專案**：在相應 API 目錄執行 `npm start`

## Testing Instructions

### Quiz App Testing

```bash
cd quiz-app
npm run lint       # 檢查代碼風格問題
npm run build      # 驗證構建成功
```

### Bank API Testing

```bash
cd 7-bank-project/api
npm run lint       # 檢查程式碼風格問題
node server.js     # 驗證伺服器能否無錯誤啟動
```

### General Testing Approach

- 本教育資源庫未包含全面的自動測試
- 手動測試重點：
  - 範例程式碼無錯誤執行
  - 文件中的連結均正常
  - 專案能成功編譯與建置
  - 範例符合最佳實踐

### Pre-submission Checks

- 在有 package.json 的目錄執行 `npm run lint`
- 驗證 Markdown 連結有效
- 瀏覽器或 Node.js 測試範例程式碼
- 確認翻譯結構維持正確

## Code Style Guidelines

### JavaScript

- 使用現代 ES6+ 語法
- 遵循專案中提供的標準 ESLint 設定
- 使用明確的變數與函式命名，利於教學理解
- 添加解說概念的註解
- 於配置的情況下使用 Prettier 格式化

### HTML/CSS

- 使用語意化 HTML5 元素
- 響應式設計原則
- 清晰的類別命名規則
- 為教學目的解釋 CSS 技巧的註解

### Python

- 遵守 PEP 8 編碼風格指南
- 清晰且具教育意義的範例程式碼
- 於有助於學習處使用型別提示

### Markdown Documentation

- 清晰的標題層級
- 語言指定的程式碼區塊
- 連結至額外資源
- `images/` 目錄內的截圖與圖片
- 圖片需有替代文字以利無障礙

### File Organization

- 課程依序編號（1-getting-started-lessons、2-js-basics 等）
- 每個專案含 `solution/`，通常也有 `start/` 或 `your-work/` 目錄
- 圖片存放於各課程專屬的 `images/` 資料夾
- 翻譯存於 `translations/{language-code}/` 結構下

## Build and Deployment

### Quiz App Deployment (Azure Static Web Apps)

quiz-app 已設定用於 Azure Static Web Apps 部署：

```bash
cd quiz-app
npm run build      # 建立 dist/ 資料夾
# 在推送至 main 時通過 GitHub Actions 工作流程部署
```

Azure Static Web Apps 配置：
- <strong>應用程式位置</strong>：`/quiz-app`
- <strong>輸出位置</strong>：`dist`
- <strong>工作流程</strong>：`.github/workflows/azure-static-web-apps-ashy-river-0debb7803.yml`

### Documentation PDF Generation

```bash
npm install                    # 安裝 docsify-to-pdf
npm run convert               # 從 docs 生成 PDF
```

### Docsify Documentation

```bash
npm install -g docsify-cli    # 全域安裝 Docsify
docsify serve                 # 在 localhost:3000 提供服務
```

### Project-specific Builds

每個專案目錄可能有自己的建置流程：
- Vue 專案：`npm run build` 產生生產用套件
- 靜態專案：無建置步驟，直接提供檔案服務

## Pull Request Guidelines

### Title Format

使用清晰、有描述性的標題以指明變更範圍：
- `[Quiz-app] 新增第X課測驗`
- `[Lesson-3] 修正溫室專案錯字`
- `[Translation] 新增第5課的西班牙文翻譯`
- `[Docs] 更新設定指引`

### Required Checks

提交 PR 前：

1. <strong>程式碼品質</strong>：
   - 在受影響的專案資料夾執行 `npm run lint`
   - 修正所有 lint 錯誤及警告

2. <strong>建置驗證</strong>：
   - 執行 `npm run build`（如適用）
   - 確認無建置錯誤

3. <strong>連結驗證</strong>：
   - 測試所有 Markdown 連結
   - 確認圖片參照正常

4. <strong>內容審核</strong>：
   - 校對拼字與文法
   - 確保程式碼範例正確且具教育意義
   - 驗證翻譯保持原意

### Contribution Requirements

- 同意 Microsoft CLA（首個 PR 自動檢查）
- 遵守 [Microsoft 開源行為準則](https://opensource.microsoft.com/codeofconduct/)
- 詳細指引請參閱 [CONTRIBUTING.md](./CONTRIBUTING.md)
- 如適用於 Issue，請於 PR 說明中引用編號

### Review Process

- PR 由維護者與社群審查
- 優先考量教育清晰性
- 程式碼範例需符合現行最佳實踐
- 翻譯確認準確且文化適切

## Translation System

### Automated Translation

- 使用 GitHub Actions 及 co-op-translator 工作流程
- 自動翻譯成50多種語言
- 主要檔案位於主目錄
- 翻譯檔案位於 `translations/{language-code}/` 目錄

### Adding Manual Translation Improvements

1. 在 `translations/{language-code}/` 找到檔案
2. 在維持結構的前提下優化翻譯
3. 確保範例程式碼可運作
4. 測試本地化測驗內容

### Translation Metadata

翻譯檔含有元數據標頭：
```markdown
<!--
CO_OP_TRANSLATOR_METADATA:
{
  "original_hash": "...",
  "translation_date": "...",
  "source_file": "...",
  "language_code": "..."
}
-->
```

## Debugging and Troubleshooting

### Common Issues

<strong>測驗應用無法啟動</strong>：
- 檢查 Node.js 版本（建議 v14+）
- 刪除 `node_modules` 及 `package-lock.json`，重新執行 `npm install`
- 檢查埠號衝突（預設：Vite 使用埠5173）

**API 伺服器無法啟動**：
- 確認 Node.js 版本符合要求（node >=10）
- 確定埠號未被占用
- 確保已執行 `npm install` 安裝所有相依套件

<strong>瀏覽器擴充功能無法載入</strong>：
- 確認 manifest.json 格式正確
- 檢查瀏覽器主控台錯誤訊息
- 遵循瀏覽器特定的擴充功能安裝指示

**Python 聊天專案問題**：
- 確認已安裝 OpenAI 套件：`pip install openai`
- 確保 GITHUB_TOKEN 環境變數設定正確
- 檢查 GitHub Models 存取權限

**Docsify 文件無法啟動**：
- 全域安裝 docsify-cli：`npm install -g docsify-cli`
- 於資源庫根目錄執行
- 檢查 `docs/_sidebar.md` 是否存在

### Development Environment Tips

- 使用 VS Code 的 Live Server 擴充功能開發 HTML 專案
- 安裝 ESLint 和 Prettier 擴充套件以統一格式
- 使用瀏覽器開發者工具除錯 JavaScript
- Vue 專案安裝 Vue DevTools 瀏覽器擴充功能

### Performance Considerations

- 大量翻譯檔案（50多種語言）使完整克隆檔案龐大
- 僅工作於內容時，可使用淺層克隆：`git clone --depth 1`
- 處理英文內容時，建議排除翻譯資料夾搜尋
- 第一次建置流程（npm install、Vite build）可能較慢

## Security Considerations

### Environment Variables

- API 金鑰切勿提交至資源庫
- 使用 `.env` 檔（已加入 `.gitignore`）
- 在專案 README 文件中說明必須的環境變數

### Python Projects

- 使用虛擬環境：`python -m venv venv`
- 維持依賴套件更新
- GitHub Token 需限權限為最小必須

### GitHub Models Access

- 需要個人存取權杖（PAT）
- 令牌應存為環境變數
- 切勿提交令牌或認證資訊

## Additional Notes

### Target Audience

- 完全初學者的網頁開發
- 學生與自學者
- 教師於課堂中使用本課綱
- 內容設計符合無障礙及循序漸進學習

### Educational Philosophy

- 專案導向學習
- 頻繁知識檢測（測驗）
- 動手練習程式碼實作
- 實務應用範例
- 強調基礎而非框架

### Repository Maintenance

- 積極的學習者與貢獻者社群
- 定期更新依賴與內容
- 維護者監控議題與討論
- 翻譯更新自動化由 GitHub Actions 管理

### Related Resources

- [Microsoft Learn 模組](https://docs.microsoft.com/learn/)
- [學生資源中心](https://docs.microsoft.com/learn/student-hub/)
- 推薦使用 [GitHub Copilot](https://marketplace.visualstudio.com/items?itemName=GitHub.copilot)
- 其它課程：生成式 AI、資料科學、機器學習、物聯網課程可用

### Working with Specific Projects

個別專案詳細說明，請參考各目錄下 README：
- `quiz-app/README.md` - Vue 3 測驗應用程式
- `7-bank-project/README.md` - 含驗證的銀行應用程式
- `5-browser-extension/README.md` - 瀏覽器擴充開發
- `6-space-game/README.md` - Canvas 遊戲開發
- `9-chat-project/README.md` - AI 聊天助理專案

### Monorepo Structure

本資源庫非典型 monorepo，但包含多個獨立專案：
- 各課程各自獨立
- 專案間不共用相依
- 可獨立作業不影響其他專案
- 克隆完整資源庫以取得全套課程體驗

---

<!-- CO-OP TRANSLATOR DISCLAIMER START -->
**免責聲明**：  
本文件乃使用 AI 翻譯服務 [Co-op Translator](https://github.com/Azure/co-op-translator) 所翻譯。雖然我們致力於確保準確性，但請注意自動翻譯可能包含錯誤或不準確之處。原始文件之母語版本應被視為權威來源。對於關鍵資訊，建議採用專業人工翻譯。我們不對因使用本翻譯所產生之任何誤解或誤譯承擔責任。
<!-- CO-OP TRANSLATOR DISCLAIMER END -->