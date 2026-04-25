# AGENTS.md

## 專案概覽

這是一個用於教導初學者網頁開發基礎的教育課程資源庫。該課程為 Microsoft 雲端倡導者開發的全面 12 週課程，包含 24 個實作課程，涵蓋 JavaScript、CSS 及 HTML。

### 主要組成部分

- <strong>教育內容</strong>：24 個結構化課程，按計劃式模組組織
- <strong>實作專案</strong>：玻璃箱生態缸、打字遊戲、瀏覽器擴充功能、太空遊戲、銀行應用、程式碼編輯器及 AI 聊天助理
- <strong>互動測驗</strong>：48 次測驗，每次含 3 題（課前/課後評量）
- <strong>多語言支援</strong>：透過 GitHub Actions 自動翻譯超過 50 種語言
- <strong>技術棧</strong>：HTML、CSS、JavaScript、Vue.js 3、Vite、Node.js、Express、Python（用於 AI 專案）

### 架構

- 以課程為基礎的教育資源庫結構
- 每個課程資料夾包含 README、程式碼範例與解答
- 獨立專案分別放在不同目錄（quiz-app、各種課程專案）
- 採用 GitHub Actions 實現的翻譯系統（co-op-translator）
- 以 Docsify 提供文件服務並可匯出為 PDF

## 安裝指令

本資源庫主要用於教育內容瀏覽。若欲操作特定專案：

### 主資源庫安裝

```bash
git clone https://github.com/microsoft/Web-Dev-For-Beginners.git
cd Web-Dev-For-Beginners
```

### 測驗應用安裝（Vue 3 + Vite）

```bash
cd quiz-app
npm install
npm run dev        # 啟動開發伺服器
npm run build      # 建置生產版本
npm run lint       # 執行 ESLint
```

### 銀行專案 API（Node.js + Express）

```bash
cd 7-bank-project/api
npm install
npm start          # 啟動 API 伺服器
npm run lint       # 執行 ESLint
npm run format     # 用 Prettier 格式化
```

### 瀏覽器擴充功能專案

```bash
cd 5-browser-extension/solution
npm install
# 遵循瀏覽器特定的擴充功能載入說明
```

### 太空遊戲專案

```bash
cd 6-space-game/solution
npm install
# 在瀏覽器中打開 index.html 或使用 Live Server
```

### 聊天專案（Python 後端）

```bash
cd 9-chat-project/solution/backend/python
pip install openai
# 設定 GITHUB_TOKEN 環境變量
python api.py
```

## 開發工作流程

### 內容貢獻者指南

1. <strong>將本資源庫分叉</strong>至您的 GitHub 帳戶
2. <strong>克隆您的分叉庫</strong>到本地
3. <strong>建立新分支</strong>用於您的修改
4. 修改課程內容或程式碼範例
5. 在相關專案目錄測試程式碼變動
6. 按照貢獻指南提交拉取請求

### 學習者指南

1. 分叉或克隆本資源庫
2. 依序瀏覽課程目錄
3. 閱讀每課的 README 文件
4. 完成課前測驗，網址：https://ff-quizzes.netlify.app/web/
5. 練習課程資料夾內的程式碼範例
6. 完成作業與挑戰
7. 參加課後測驗

### 即時開發

- <strong>文件</strong>：於根目錄執行 `docsify serve`（預設埠號 3000）
- <strong>測驗應用</strong>：於 quiz-app 目錄執行 `npm run dev`
- <strong>專案</strong>：使用 VS Code Live Server 擴充套件服務 HTML 專案
- **API 專案**：於各 API 目錄執行 `npm start`

## 測試說明

### 測驗應用測試

```bash
cd quiz-app
npm run lint       # 檢查程式碼風格問題
npm run build      # 確認構建成功
```

### 銀行 API 測試

```bash
cd 7-bank-project/api
npm run lint       # 檢查代碼風格問題
node server.js     # 驗證伺服器啟動時無錯誤
```

### 一般測試方法

- 本教育資源庫無全面自動化測試
- 手動測試重點包括：
  - 程式碼範例能夠無錯誤執行
  - 文件中所有連結均正常
  - 專案能成功建置
  - 範例維持最佳實務

### 提交前檢查

- 在含有 package.json 的目錄執行 `npm run lint`
- 確認 markdown 連結有效
- 在瀏覽器或 Node.js 測試程式碼範例
- 確認翻譯維持良好結構

## 程式碼風格指南

### JavaScript

- 使用現代 ES6+ 語法
- 遵循專案中提供的 ESLint 標準設定
- 變數與函式名稱具意義，方便教學理解
- 添加說明性註解幫助學習者理解
- 使用配置好的 Prettier 格式化

### HTML/CSS

- 採用語意化 HTML5 元素
- 採用響應式設計原則
- 使用清晰的類別命名規則
- 註解說明 CSS 技巧助學習

### Python

- 遵守 PEP 8 風格指南
- 提供清楚且具教育意義的範例程式碼
- 適時使用類型提示促進學習

### Markdown 文件

- 清晰的標題層級
- 所有程式碼區塊指定語言
- 提供連結至更多資源
- `images/` 目錄內包含截圖與圖片
- 圖片提供可及性說明的替代文字

### 檔案組織

- 課程依序編號（如 1-getting-started-lessons、2-js-basics 等）
- 每個專案有 `solution/` 資料夾，常見也有 `start/` 或 `your-work/`
- 課程專屬的 `images/` 資料夾存放圖片
- 翻譯內容存放在 `translations/{language-code}/` 結構

## 建置與部署

### 測驗應用部署（Azure Static Web Apps）

quiz-app 已配置為 Azure Static Web Apps 部署：

```bash
cd quiz-app
npm run build      # 建立 dist/ 資料夾
# 當推送到 main 分支時，透過 GitHub Actions 工作流程進行部署
```

Azure Static Web Apps 配置：
- <strong>應用程式位置</strong>：`/quiz-app`
- <strong>輸出位置</strong>：`dist`
- <strong>工作流程</strong>：`.github/workflows/azure-static-web-apps-ashy-river-0debb7803.yml`

### 文件 PDF 生成

```bash
npm install                    # 安裝 docsify-to-pdf
npm run convert               # 從 docs 生成 PDF
```

### Docsify 文件

```bash
npm install -g docsify-cli    # 全域安裝 Docsify
docsify serve                 # 在 localhost:3000 提供服務
```

### 專案特定建置

各專案目錄可能有獨立建置流程：
- Vue 專案：執行 `npm run build` 產生生產包
- 靜態專案：無建置步驟，直接提供檔案服務

## 拉取請求指引

### 標題格式

使用清楚、具描述性的標題表明更改範圍：
- `[Quiz-app] 新增課程 X 測驗`
- `[Lesson-3] 修正玻璃箱專案錯字`
- `[Translation] 新增第 5 課西班牙語翻譯`
- `[Docs] 更新安裝說明`

### 必須檢查項目

提交 PR 前：

1. <strong>程式碼品質</strong>：
   - 於受影響專案目錄執行 `npm run lint`
   - 修正所有 lint 警告與錯誤

2. <strong>建置驗證</strong>：
   - 若適用，執行 `npm run build`
   - 確保無建置錯誤

3. <strong>連結驗證</strong>：
   - 測試所有 markdown 連結
   - 確認圖片引用有效

4. <strong>內容檢視</strong>：
   - 校對拼寫與語法
   - 確保程式碼範例正確且具教育意義
   - 核對翻譯保持原意

### 貢獻要求

- 同意 Microsoft CLA（首次 PR 時自動檢查）
- 遵守 [Microsoft 開源行為守則](https://opensource.microsoft.com/codeofconduct/)
- 詳細指南見 [CONTRIBUTING.md](./CONTRIBUTING.md)
- 若有，於 PR 描述內提及相關議題編號

### 審查流程

- PR 由維護者與社群審核
- 優先確保教育清晰度
- 程式碼範例應符合當前最佳實務
- 翻譯需審核準確性與文化適切性

## 翻譯系統

### 自動翻譯

- 利用 GitHub Actions 配合 co-op-translator 工作流程
- 自動翻譯超過 50 種語言
- 原始檔案放在主目錄
- 翻譯檔案存放於 `translations/{language-code}/`

### 手動翻譯改進

1. 找到對應的 `translations/{language-code}/` 檔案
2. 在保持檔案結構的情況下進行優化
3. 確保程式碼範例能正確執行
4. 測試本地化測驗內容

### 翻譯元資料

翻譯檔含有元資料標頭：
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

## 偵錯與問題排解

### 常見問題

<strong>測驗應用無法啟動</strong>：
- 檢查 Node.js 版本（建議 v14 以上）
- 刪除 `node_modules` 及 `package-lock.json`，重新執行 `npm install`
- 檢查埠號衝突（預設 Vite 使用埠 5173）

**API 伺服器無法啟動**：
- 確認 Node.js 版本達最低要求 (node >=10)
- 確認埠號未被占用
- 確認全部依賴已透過 `npm install` 安裝

<strong>瀏覽器擴充功能無法載入</strong>：
- 確認 manifest.json 格式正確
- 查看瀏覽器控制台錯誤訊息
- 遵循瀏覽器擴充程式安裝指引

**Python 聊天專案問題**：
- 確認已安裝 OpenAI 套件：`pip install openai`
- 確認環境變數 GITHUB_TOKEN 已設定
- 檢查 GitHub Models 存取權限

**Docsify 無法提供文件服務**：
- 全局安裝 docsify-cli：`npm install -g docsify-cli`
- 於資源庫根目錄執行
- 確認 `docs/_sidebar.md` 檔案存在

### 開發環境小技巧

- 使用 VS Code 搭配 Live Server 擴充開發 HTML 專案
- 安裝 ESLint 與 Prettier 擴充以維持格式統一
- 使用瀏覽器開發者工具偵錯 JavaScript
- Vue 專案安裝 Vue DevTools 瀏覽器擴充

### 效能考量

- 超過 50 種語言的翻譯檔案量大，完整複製佔用空間多
- 只開發內容可用淺層複製：`git clone --depth 1`
- 進行英文內容工作時建議排除翻譯資料夾搜尋
- 首次建置可能較慢（npm install、Vite 建置）

## 安全事項

### 環境變數

- API 金鑰絕不可提交至資源庫
- 使用 `.env` 檔（已加入 `.gitignore`）
- 專案 README 中記錄所需環境變數

### Python 專案

- 使用虛擬環境：`python -m venv venv`
- 維護相依套件更新
- GitHub 令牌設定最低必要權限

### GitHub Models 存取

- 需使用個人訪問令牌 (PAT)
- 令牌應儲存在環境變數
- 禁止提交令牌或認證資訊

## 附加說明

### 目標對象

- 完全沒有網頁開發經驗的初學者
- 學生及自學者
- 在課堂中使用本課程的教師
- 內容設計強調易懂性與循序漸進技能建立

### 教育理念

- 採用專案導向學習方式
- 定期知識檢核（測驗）
- 實作程式練習
- 真實世界應用範例
- 強調基礎概念後再著重框架

### 資源庫維護

- 積極活躍的學習者與貢獻者社群
- 定期更新依賴與內容
- 維護者監控問題與討論
- 翻譯更新自動化使用 GitHub Actions

### 相關資源

- [Microsoft Learn 模組](https://docs.microsoft.com/learn/)
- [學生中心資源](https://docs.microsoft.com/learn/student-hub/)
- 建議學習者使用 [GitHub Copilot](https://marketplace.visualstudio.com/items?itemName=GitHub.copilot)
- 另有生成式 AI、資料科學、機器學習、物聯網課程可供學習

### 操作特定專案

有關各專案詳細說明，請參閱對應 README：
- `quiz-app/README.md` - Vue 3 測驗應用
- `7-bank-project/README.md` - 含認證的銀行應用
- `5-browser-extension/README.md` - 瀏覽器擴充開發
- `6-space-game/README.md` - Canvas 遊戲開發
- `9-chat-project/README.md` - AI 聊天助理專案

### Monorepo 結構說明

儘管非傳統 monorepo，本資源庫含多個獨立專案：
- 每課程獨立自成一體
- 專案間無相依套件共用
- 可個別專案工作不影響其他專案
- 若需完整課程體驗，請完整複製此資源庫

---

<!-- CO-OP TRANSLATOR DISCLAIMER START -->
**免責聲明**：  
本文件係使用 AI 翻譯服務 [Co-op Translator](https://github.com/Azure/co-op-translator) 進行翻譯。雖然我們致力於保持準確性，但請注意自動翻譯可能包含錯誤或不準確之處。原始語言版本的文件應被視為權威來源。對於重要資訊，建議採用專業人工翻譯。我們不對使用本翻譯文件所產生之任何誤解或誤釋負責。
<!-- CO-OP TRANSLATOR DISCLAIMER END -->