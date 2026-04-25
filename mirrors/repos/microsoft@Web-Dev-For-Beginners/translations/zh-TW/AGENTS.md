# AGENTS.md

## 專案概覽

這是一個用於教授初學者網頁開發基礎的教育課程儲存庫。該課程是由 Microsoft Cloud Advocates 開發的完整 12 週課程，包含 24 個涵蓋 JavaScript、CSS 和 HTML 的實作課程。

### 主要組成部分

- <strong>教育內容</strong>：24 個結構化課程，組成以專案為基礎的模組
- <strong>實作專案</strong>：生態瓶、打字遊戲、瀏覽器擴充功能、太空遊戲、銀行應用、程式碼編輯器和 AI 聊天助理
- <strong>互動測驗</strong>：48 個測驗，每個測驗包含 3 題（課前/課後評量）
- <strong>多語言支援</strong>：透過 GitHub Actions 自動翻譯超過 50 種語言
- <strong>技術堆疊</strong>：HTML、CSS、JavaScript、Vue.js 3、Vite、Node.js、Express、Python（用於 AI 專案）

### 架構

- 教育儲存庫，採用以課程為基礎的結構
- 每個課程資料夾包含 README、程式碼範例及解答
- 獨立專案置於不同目錄（quiz-app、各種課程專案）
- 透過 GitHub Actions (co-op-translator) 進行翻譯系統
- 文件以 Docsify 提供，並可匯出為 PDF

## 安裝指令

此儲存庫主要用於教育內容的學習。若要操作特定專案：

### 主要儲存庫安裝

```bash
git clone https://github.com/microsoft/Web-Dev-For-Beginners.git
cd Web-Dev-For-Beginners
```

### 測驗應用安裝 (Vue 3 + Vite)

```bash
cd quiz-app
npm install
npm run dev        # 啟動開發伺服器
npm run build      # 為生產環境建置
npm run lint       # 執行 ESLint
```

### 銀行專案 API (Node.js + Express)

```bash
cd 7-bank-project/api
npm install
npm start          # 啟動 API 伺服器
npm run lint       # 執行 ESLint
npm run format     # 使用 Prettier 格式化
```

### 瀏覽器擴充專案

```bash
cd 5-browser-extension/solution
npm install
# 遵循瀏覽器特定的擴充功能載入說明
```

### 太空遊戲專案

```bash
cd 6-space-game/solution
npm install
# 在瀏覽器中開啟 index.html 或使用 Live Server
```

### 聊天專案 (Python 後端)

```bash
cd 9-chat-project/solution/backend/python
pip install openai
# 設定 GITHUB_TOKEN 環境變數
python api.py
```

## 開發工作流程

### 內容貢獻者

1. **將儲存庫分支 (fork)** 至你的 GitHub 帳號
2. **在本機複製 (clone) 你的分支**
3. <strong>建立新分支</strong> 來進行修改
4. 修改課程內容或程式碼範例
5. 在相關專案目錄中測試程式碼變更
6. 按照貢獻指南提交 Pull Request

### 學習者

1. 分支或複製儲存庫
2. 按順序瀏覽課程目錄
3. 閱讀各課程的 README 文件
4. 在 https://ff-quizzes.netlify.app/web/ 完成課前測驗
5. 在課程資料夾中練習程式碼範例
6. 完成作業與挑戰
7. 參加課後測驗

### 實時開發

- <strong>文件</strong>：於根目錄執行 `docsify serve`（預設端口 3000）
- <strong>測驗應用</strong>：於 quiz-app 資料夾執行 `npm run dev`
- <strong>專案</strong>：使用 VS Code Live Server 擴充功能提供 HTML 專案服務
- **API 專案**：於相應 API 目錄執行 `npm start`

## 測試指令

### 測驗應用測試

```bash
cd quiz-app
npm run lint       # 檢查程式碼風格問題
npm run build      # 確認建置成功
```

### 銀行 API 測試

```bash
cd 7-bank-project/api
npm run lint       # 檢查程式碼風格問題
node server.js     # 驗證伺服器是否無錯誤啟動
```

### 一般測試方式

- 此為教育用儲存庫，不包含全面自動化測試
- 以手動測試為主，重點為：
  - 程式碼範例能正常執行無錯誤
  - 文件中的連結有效
  - 專案能成功編譯
  - 範例遵循最佳實踐

### 提交前檢查

- 於含有 package.json 的目錄執行 `npm run lint`
- 確認 markdown 連結正確
- 在瀏覽器或 Node.js 中測試程式碼範例
- 確保翻譯內容結構完整

## 程式碼風格指導

### JavaScript

- 使用現代 ES6+ 語法
- 遵循專案內標準 ESLint 配置
- 使用有意義的變數和函數名稱以利教學理解
- 添加說明註解解釋概念給學習者
- 配置 Prettier 的地方使用其格式化

### HTML/CSS

- 採用語意化的 HTML5 元素
- 遵循響應式設計原則
- 清晰的類別命名規範
- 用註解解釋 CSS 技巧給學習者

### Python

- 遵循 PEP 8 風格規範
- 清晰且具教育意義的程式碼範例
- 適當使用型別註記方便學習

### Markdown 文件

- 清楚的標題層級
- 含有語言指示的程式區塊
- 附加資源連結
- 在 `images/` 資料夾中的截圖與圖片
- 針對圖片附加替代文字以利無障礙

### 檔案組織

- 課程依序編號（1-getting-started-lessons、2-js-basics 等）
- 每個專案有 `solution/` 且通常有 `start/` 或 `your-work/` 目錄
- 圖片儲存在課程專屬的 `images/` 資料夾中
- 翻譯存放於 `translations/{language-code}/` 結構中

## 建置與部署

### 測驗應用部署 (Azure 靜態網站)

quiz-app 配置為 Azure 靜態網站部署：

```bash
cd quiz-app
npm run build      # 建立 dist/ 資料夾
# 在推送至 main 分支時，透過 GitHub Actions 工作流程進行部署
```

Azure 靜態網站配置：
- <strong>應用位置</strong>：`/quiz-app`
- <strong>輸出位置</strong>：`dist`
- <strong>工作流程</strong>：`.github/workflows/azure-static-web-apps-ashy-river-0debb7803.yml`

### 文件 PDF 產生

```bash
npm install                    # 安裝 docsify-to-pdf
npm run convert               # 從 docs 產生 PDF
```

### Docsify 文件

```bash
npm install -g docsify-cli    # 全域安裝 Docsify
docsify serve                 # 在 localhost:3000 提供服務
```

### 專案建置

各專案目錄可能有獨立建置流程：
- Vue 專案：使用 `npm run build` 產生生產包
- 靜態專案：不需建置，直接提供檔案服務

## Pull Request 指南

### 標題格式

使用清晰且描述性標題指示修改範圍：
- `[Quiz-app] 新增課程 X 測驗`
- `[Lesson-3] 修正生態瓶專案錯字`
- `[Translation] 新增課程 5 之西班牙文翻譯`
- `[Docs] 更新安裝說明`

### 必要檢查

提交 PR 前：

1. <strong>程式碼品質</strong>：
   - 在相關專案目錄執行 `npm run lint`
   - 修正所有 lint 錯誤與警告

2. <strong>建置驗證</strong>：
   - 如適用，執行 `npm run build`
   - 確保無建置錯誤

3. <strong>連結校驗</strong>：
   - 測試所有 markdown 連結
   - 確認圖片引用有效

4. <strong>內容審核</strong>：
   - 校對拼字與語法
   - 確保程式碼範例正確且具教育意義
   - 確認翻譯準確且保持原意

### 貢獻條件

- 同意 Microsoft CLA（首次 PR 自動檢查）
- 遵循 [Microsoft 開源行為準則](https://opensource.microsoft.com/codeofconduct/)
- 詳細指南見 [CONTRIBUTING.md](./CONTRIBUTING.md)
- 如適用於 PR 描述中註明 issue 編號

### 審核程序

- PR 由維護者與社群審核
- 優先考量教育清晰度
- 程式碼範例應符合最佳實務
- 翻譯審核確保準確且符合文化背景

## 翻譯系統

### 自動翻譯

- 透過 GitHub Actions 配合 co-op-translator 工作流程
- 自動翻譯超過 50 種語言
- 來源檔置於主要目錄中
- 翻譯檔存於 `translations/{language-code}/` 目錄

### 手動翻譯改進

1. 定位於 `translations/{language-code}/` 中的檔案
2. 進行改進並保留結構
3. 確保程式碼範例依然可運作
4. 測試任何本地化測驗內容

### 翻譯元資料

翻譯檔包含元資料標頭：
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

## 除錯與疑難排解

### 常見問題

<strong>測驗應用無法啟動</strong>：
- 確認 Node.js 版本（建議 v14 以上）
- 刪除 `node_modules` 和 `package-lock.json`，重新執行 `npm install`
- 檢查端口是否衝突（預設 Vite 使用 5173 端口）

**API 伺服器無法啟動**：
- 確認 Node.js 版本符合最低要求（node >=10）
- 檢查該端口是否已被占用
- 確保已執行 `npm install` 以安裝所有相依套件

<strong>瀏覽器擴充無法載入</strong>：
- 確認 manifest.json 格式正確
- 查看瀏覽器主控台有無錯誤訊息
- 參考瀏覽器專屬擴充安裝說明

**Python 聊天專案問題**：
- 確保安裝了 OpenAI 套件：`pip install openai`
- 確認 GITHUB_TOKEN 環境變數已設定
- 檢查 GitHub Models 訪問權限

**Docsify 無法提供文件服務**：
- 全域安裝 docsify-cli：`npm install -g docsify-cli`
- 從儲存庫根目錄執行
- 確認存在 `docs/_sidebar.md`

### 開發環境建議

- 使用 VS Code 搭配 Live Server 擴充執行 HTML 專案
- 安裝 ESLint 和 Prettier 擴充以維持格式一致
- 利用瀏覽器開發者工具除錯 JavaScript
- Vue 專案建議安裝 Vue DevTools 瀏覽器擴充

### 性能考量

- 多達 50 種語言之翻譯使完整克隆資料龐大
- 僅編輯內容可使用淺層克隆：`git clone --depth 1`
- 編輯英文內容時可排除翻譯搜尋
- 第一次執行建置流程可能較慢（npm install、Vite build）

## 安全性考量

### 環境變數

- API 金鑰不可提交至儲存庫
- 使用 `.env` 檔案（已列入 `.gitignore`）
- 文件中說明所需環境變數

### Python 專案

- 使用虛擬環境：`python -m venv venv`
- 持續更新相依套件
- GitHub Token 需具最小必要權限

### GitHub Models 存取權限

- 使用個人存取權杖（PAT）
- 將 Token 設為環境變數
- 絕不提交 Token 或帳密

## 附加說明

### 目標對象

- 完全初學者的網頁開發學習者
- 學生與自我學習者
- 在教室使用課程的老師
- 內容設計強調無障礙性及技能逐步建立

### 教育理念

- 以專案為基礎的學習方式
- 頻繁的知識檢核（測驗）
- 實作程式練習
- 真實世界應用範例
- 注重基礎概念，先於框架學習

### 儲存庫維護

- 積極的學習及貢獻社群
- 定期更新相依套件與內容
- 維護者監控議題與討論
- 透過 GitHub Actions 自動化翻譯更新

### 相關資源

- [Microsoft Learn 模組](https://docs.microsoft.com/learn/)
- [學生中心資源](https://docs.microsoft.com/learn/student-hub/)
- 推薦學習者使用 [GitHub Copilot](https://marketplace.visualstudio.com/items?itemName=GitHub.copilot)
- 其他課程：生成式 AI、資料科學、機器學習、物聯網課程

### 使用特定專案說明

個別專案詳細說明請參考：

- `quiz-app/README.md` - Vue 3 測驗應用
- `7-bank-project/README.md` - 帶身份驗證的銀行應用
- `5-browser-extension/README.md` - 瀏覽器擴充功能開發
- `6-space-game/README.md` - Canvas 遊戲開發
- `9-chat-project/README.md` - AI 聊天助理專案

### Monorepo 結構

雖非傳統 monorepo，此儲存庫包含多個獨立專案：

- 各課程自成一體
- 專案間不共用相依套件
- 可單獨工作不影響其他專案
- 克隆整個儲存庫可獲得完整課程體驗

---

<!-- CO-OP TRANSLATOR DISCLAIMER START -->
**免責聲明**：  
本文件使用 AI 翻譯服務 [Co-op Translator](https://github.com/Azure/co-op-translator) 進行翻譯。雖然我們努力追求準確性，但請注意，自動翻譯可能包含錯誤或不準確之處。原始文件的母語版本應被視為權威來源。對於關鍵資訊，建議採用專業人工翻譯。我們對因使用此翻譯而產生的任何誤解或誤釋概不負責。
<!-- CO-OP TRANSLATOR DISCLAIMER END -->