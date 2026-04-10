# readme-from-docx 技能参考文档

> 本文档是技能的辅助参考资料。每次使用技能时，**必须**从 docx 文档中重新分析章节结构和图片映射，不要依赖历史记录。

---

## 三个核心原则（必须遵守）

1. **图片按文档 rId 顺序提取**：遍历 `word/document.xml` 中 `<w:body>` 的每个段落，从 `<wp:inline>` / `<wp:anchor>` → `<a:blip>` 取出 `r:embed` 值，按正文出现顺序编号。
2. **章节-图片映射每次从文档提取**：不同版本的 docx 章节顺序和图片数量可能不同，每次使用技能都要重新分析。
3. **其他语言使用英文格式和英文图片**：章节数量/顺序与英文版对齐，图片固定 `../../images/previews/en/`。
4. **文档换行必须对应保留**：docx 中 `<w:br/>` → Markdown `  \n`（两个空格+换行），不要合并为单行。

---

## 图片提取输出

### 英文 docx（以 readme-英文V3.docx 为例）

输出目录：`images/previews/en/`

| 编号 | ZIP 内路径 | 输出文件名 |
|------|------------|------------|
| 1 | word/media/image7.png | image1.png |
| 2 | word/media/image6.png | image2.png |
| 3 | word/media/image1.png | image3.png |
| 4 | word/media/image5.png | image4.png |
| 5 | word/media/image8.png | image5.png |
| 6 | word/media/image4.png | image6.png |
| 7 | word/media/image9.png | image7.png |
| 8 | word/media/image11.png | image8.png |
| 9 | word/media/image12.png | image9.png |
| 10 | word/media/image3.png | image10.png |
| 11 | word/media/image13.png | image11.png |
| 12 | word/media/image14.png | image12.png |
| 13 | word/media/image2.png | image13.png |
| 14 | word/media/image10.png | image14.png |

> 注意：ZIP 内的 `imageN.png` 文件名顺序**不等同于**文档中的出现顺序，必须按 rId 遍历 body 顺序提取。上表为 V3 版的实际映射。

### 中文 docx（以 readme-中文-V3.docx 为例）

输出目录：`images/previews/zh-CN/`

| 编号 | ZIP 内路径 | 输出文件名 |
|------|------------|------------|
| 1 | word/media/image7.png | image1.png |
| 2 | word/media/image6.png | image2.png |
| 3 | word/media/image1.png | image3.png |
| 4 | word/media/image5.png | image4.png |
| 5 | word/media/image8.png | image5.png |
| 6 | word/media/image4.png | image6.png |
| 7 | word/media/image9.png | image7.png |
| 8 | word/media/image11.png | image8.png |
| 9 | word/media/image12.png | image9.png |
| 10 | word/media/image3.png | image10.png |
| 11 | word/media/image13.png | image11.png |
| 12 | word/media/image14.png | image12.png |
| 13 | word/media/image2.png | image13.png |
| 14 | word/media/image10.png | image14.png |
| 15 | word/media/image15.png | image15.png |

> 注意：中文 docx 比英文版多一张图（image15.png），是"社区交流&联系我们"的二维码图。

---

## 章节-图片映射参考（V3 版）

> ⚠️ 此映射基于 V3 版文档。每次使用技能时，需从当前文档重新分析。

### 英文版（14 张图）

| 序号 | 图片 | 英文标题 | 英文描述 |
|------|------|----------|----------|
| 1 | image1.png | AI Chatbot Assistant | Ask your AI assistant any question... |
| 2 | image2.png | （同上段落续图） |  |
| 3 | image3.png | Multi-Agent Mode | Multiple specialized AI agents collaborate... |
| 4 | image4.png | （同上段落续图） |  |
| 5 | image5.png | Local Knowledge Base Q&A | Build your private knowledge base... |
| 6 | image6.png | （同上段落续图） |  |
| 7 | image7.png | Global Shortcut Key | Press global shortcut to activate... |
| 8 | image8.png | （同上段落续图） |  |
| 9 | image9.png | File Watch Mode | Automatically processes files in folder... |
| 10 | image10.png | （同上段落续图） |  |
| 11 | image11.png | Multi-Account Management | Supports multiple accounts and role switching... |
| 12 | image12.png | （同上段落续图） |  |
| 13 | image13.png | AI Model Switching | Switch between different AI models... |
| 14 | image14.png | One-Click Launcher Ball | Click the floating ball to instantly wake up... |

### 中文版（15 张图）

| 序号 | 图片 | 中文标题 | 中文描述 |
|------|------|----------|----------|
| 1 | image1.png | AI 聊天助手 | 向 AI 助手提出任何问题... |
| 2 | image2.png | （同上段落续图） |  |
| 3 | image3.png | 多Agent模式 | 多个专业 AI 代理协同工作... |
| 4 | image4.png | （同上段落续图） |  |
| 5 | image5.png | 本地知识库问答 | 构建专属私有知识库... |
| 6 | image6.png | （同上段落续图） |  |
| 7 | image7.png | 全局快捷键 | 通过快捷键快速唤醒... |
| 8 | image8.png | （同上段落续图） |  |
| 9 | image9.png | 文件监控模式 | 自动处理文件夹中的文件... |
| 10 | image10.png | （同上段落续图） |  |
| 11 | image11.png | 多账号管理 | 支持多账号切换... |
| 12 | image12.png | （同上段落续图） |  |
| 13 | image13.png | AI 模型切换 | 在不同 AI 模型之间切换... |
| 14 | image14.png | 一键启动 | 点击悬浮球唤醒主应用窗口... |
| 15 | image15.png | 社区交流&联系我们 | 欢迎联系我们获取帮助... |

---

## 文件与图片路径对应表

| 文件路径 | 内容语言 | 图片路径前缀 | 图片数量 |
|----------|----------|--------------|----------|
| `README.md`（根目录） | 中文 | `./images/previews/zh-CN/` | 15（或以实际提取为准） |
| `docs/readmes/README_en.md` | 英文 | `../../images/previews/en/` | 14 |
| `docs/readmes/README_zh-CN.md` | 中文 | `../../images/previews/zh-CN/` | 15（或以实际提取为准） |
| `docs/readmes/README_*.md`（其他 14 种） | 各语言 | `../../images/previews/en/` | 14 |

---

## 各语言标题对照表

### 章节大标题

| 语言 | 代码 | 功能预览标题 | 服务器部署标题 |
|------|------|-------------|---------------|
| 简体中文 | zh-CN | `## 功能预览` | `## 服务器模式部署` |
| 繁体中文 | zh-TW | `## 功能預覽` | `## 伺服器模式部署` |
| 英语 | en | `## Previews` | `## Server Mode Deployment` |
| 日语 | ja-JP | `## プレビュー` | `## サーバーモードデプロイ` |
| 韩语 | ko-KR | `## 미리보기` | `## 서버 모드 배포` |
| 阿拉伯语 | ar-SA | `## معاينة` | `## نشر وضع الخادم` |
| 孟加拉语 | bn-BD | `## প্রিভিউ` | `## সার্ভার মোড ডিপ্লয়মেন্ট` |
| 德语 | de-DE | `## Vorschau` | `## Server-Modus-Bereitstellung` |
| 西班牙语 | es-ES | `## Previsualizaciones` | `## Despliegue en Modo Servidor` |
| 法语 | fr-FR | `## Aperçus` | `## Déploiement en Mode Serveur` |
| 印地语 | hi-IN | `## पूर्वावलोकन` | `## सर्वर मोड परिनियोजन` |
| 意大利语 | it-IT | `## Anteprime` | `## Distribuzione Modalità Server` |
| 葡萄牙语 | pt-BR | `## Visualizações` | `## Implantação em Modo Servidor` |
| 斯洛文尼亚语 | sl-SI | `## Predogledi` | `## Namestitev v načinu strežnika` |
| 土耳其语 | tr-TR | `## Önizlemeler` | `## Sunucu Modu Dağıtımı` |
| 越南语 | vi-VN | `## Xem trước` | `## Triển khai Chế độ Máy chủ` |

### 功能小标题（V3 版参考）

| 序号 | 英文 | 中文 |
|------|------|------|
| 1 | AI Chatbot Assistant | AI 聊天助手 |
| 2 | Multi-Agent Mode | 多Agent模式 |
| 3 | Local Knowledge Base Q&A | 本地知识库问答 |
| 4 | Global Shortcut Key | 全局快捷键 |
| 5 | File Watch Mode | 文件监控模式 |
| 6 | Multi-Account Management | 多账号管理 |
| 7 | AI Model Switching | AI 模型切换 |
| 8 | One-Click Launcher Ball | 一键启动 |
| 9 | Community & Contact Us | 社区交流&联系我们 |

> ⚠️ 以上小标题翻译基于 V3 版文档。不同版本的 docx 章节顺序和数量可能不同，使用技能时请从当前文档重新提取。

### 其他语言小标题（按序号对应英文）

| 语言 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 |
|------|---|---|---|---|---|---|---|---|---|
| zh-TW | AI 聊天助理 | 多Agent模式 | 本地知識庫問答 | 全域快捷鍵 | 檔案監控模式 | 多帳號管理 | AI 模型切換 | 一鍵啟動 | 社群交流&聯繫我們 |
| ja-JP | AIチャットアシスタント | マルチAgentモード | ローカルナレッジベースQ&A | グローバルショートカットキー | ファイル監視モード | マルチアカウント管理 | AIモデル切り替え | ワンクリックランチャー | コミュニティ&お問い合わせ |
| ko-KR | AI 채팅 어시스턴트 | 멀티 Agent 모드 | 로컬 지식 베이스 Q&A | 글로벌 단축키 | 파일 감시 모드 | 멀티 계정 관리 | AI 모델 전환 | 원클릭 런처 | 커뮤니티&문의 |
| de-DE | KI-Chatbot-Assistent | Multi-Agent-Modus | Lokale Wissensbasis Q&A | Globale Tastenkombination | Dateiüberwachungsmodus | Multi-Account-Verwaltung | KI-Modellwechsel | Ein-Klick-Starter | Community & Kontakt |
| es-ES | Asistente de chatbot IA | Modo multiagente | Q&A de base de conocimiento local | Atajo de teclado global | Modo de vigilancia de archivos | Gestión de múltiples cuentas | Cambio de modelo IA | Bola de inicio con un clic | Comunidad y contacto |
| fr-FR | Assistant chatbot IA | Mode multi-agent | Q&R de base de connaissances locale | Raccourci global | Mode surveillance de fichiers | Gestion multi-comptes | Changement de modèle IA | Lanceur en un clic | Communauté & contact |
| ar-SA | مساعد روبوت المحادثة الذكي | وضع الوكيل المتعدد |问答本地知识库 | الاختصار العام | وضع مراقبة الملفات | إدارة الحسابات المتعددة | تبديل نموذج الذكاء الاصطناعي | كرة التشغيل بنقرة واحدة | المجتمع والتواصل |
| bn-BD | AI চ্যাটবট অ্যাসিস্ট্যান্ট | মাল্টি-এজেন্ট মোড | স্থানীয় নলেজ বেস Q&A | গ্লোবাল শর্টকাট কী | ফাইল ওয়াচ মোড | মাল্টি-অ্যাকাউন্ট ম্যানেজমেন্ট | AI মডেল স্যুইচিং | ওয়ান-ক্লিক লঞ্চার বল | কমিউনিটি ও যোগাযোগ |
| hi-IN | AI चैटबॉट सहायक | मल्टी-एजेंट मोड | स्थानीय ज्ञान आधार Q&A | वैश्विक शॉर्टकट कुंजी | फ़ाइल वॉच मोड | मल्टी-अकाउंट प्रबंधन | AI मॉडल स्विचिंग | वन-क्लिक लॉन्चर बॉल | समुदाय और संपर्क करें |
| it-IT | Assistente chatbot AI | Modalità multi-agente | Q&A della knowledge base locale | Tasto di scelta rapida globale | Modalità sorveglianza file | Gestione account multipli | Cambio modello AI | Pulsante di avvio con un clic | Community e contattaci |
| pt-BR | Assistente de chatbot IA | Modo multiagente | Q&A da base de conhecimento local | Atalho global | Modo de vigilância de arquivos | Gerenciamento de múltiplas contas | Troca de modelo IA | Bola de inicialização com um clique | Comunidade e contato |
| sl-SI | AI pomočnik za klepet | Večagentni način | Q&A lokalne baze znanja | Globalna bližnjica | Način spremljanja datotek | Upravljanje več računov | Preklapljanje AI modela | Enoklik滨江ni zaganjalnik | Skupnost in kontakt |
| tr-TR | AI sohbet botu asistanı | Çoklu Aracı Modu | Yerel bilgi tabanı SSS | Global kısayol tuşu | Dosya izleme modu | Çoklu hesap yönetimi | AI modeli değiştirme | Tek tıklamayla başlatıcı | Topluluk ve iletişim |
| vi-VN | Trợ lý chatbot AI | Chế độ đa tác nhân | Hỏi đáp cơ sở kiến thức cục bộ | Phím tắt toàn cầu | Chế độ theo dõi tệp | Quản lý đa tài khoản | Chuyển đổi mô hình AI | Quả cầu khởi chạy một lần | Cộng đồng và liên hệ |

---

## 路径注意事项

- 根目录 `README.md` 中图片路径用 `./images/previews/zh-CN/`（从项目根目录出发）。
- `docs/readmes/` 下所有文件的图片路径统一用 `../../images/previews/en/`（英文图片）或 `../../images/previews/zh-CN/`（中文图片）。
- **不要**使用 `../../../images/...` 或 `../../../../images/...`，那代表文件引用路径错误。
