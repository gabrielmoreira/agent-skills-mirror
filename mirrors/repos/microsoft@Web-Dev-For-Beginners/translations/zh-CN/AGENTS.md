# AGENTS.md

## 项目概述

这是一个面向初学者教授网页开发基础知识的教育课程仓库。该课程是一门由微软云宣传人员开发的为期12周的综合课程，包含24个涵盖JavaScript、CSS和HTML的实践课程。

### 关键组成部分

- <strong>教学内容</strong>：24个结构化课程，按项目模块组织
- <strong>实用项目</strong>：生态瓶、打字游戏、浏览器扩展、太空游戏、银行应用、代码编辑器和AI聊天助手
- <strong>互动测验</strong>：48个测验，每个包含3个问题（课前/课后评估）
- <strong>多语言支持</strong>：通过GitHub Actions自动翻译50多种语言
- <strong>技术栈</strong>：HTML、CSS、JavaScript、Vue.js 3、Vite、Node.js、Express、Python（用于AI项目）

### 架构

- 教育仓库，基于课程结构
- 每课文件夹包含README、代码示例和解决方案
- 独立项目位于单独目录（quiz-app、各种课程项目）
- 使用GitHub Actions（co-op-translator）实现翻译系统
- 文档通过Docsify提供，并可导出为PDF

## 设置命令

此仓库主要用于教学内容的使用。若需使用具体项目：

### 主仓库设置

```bash
git clone https://github.com/microsoft/Web-Dev-For-Beginners.git
cd Web-Dev-For-Beginners
```

### 测验应用设置（Vue 3 + Vite）

```bash
cd quiz-app
npm install
npm run dev        # 启动开发服务器
npm run build      # 构建生产版本
npm run lint       # 运行 ESLint
```

### 银行项目 API（Node.js + Express）

```bash
cd 7-bank-project/api
npm install
npm start          # 启动 API 服务器
npm run lint       # 运行 ESLint
npm run format     # 使用 Prettier 格式化
```

### 浏览器扩展项目

```bash
cd 5-browser-extension/solution
npm install
# 遵循浏览器特定的扩展加载说明
```

### 太空游戏项目

```bash
cd 6-space-game/solution
npm install
# 在浏览器中打开 index.html 或使用实时服务器
```

### 聊天项目（Python 后端）

```bash
cd 9-chat-project/solution/backend/python
pip install openai
# 设置 GITHUB_TOKEN 环境变量
python api.py
```

## 开发工作流

### 内容贡献者

1. <strong>Fork 仓库</strong>到你的GitHub账号
2. **克隆你的 Fork** 到本地
3. <strong>创建新的分支</strong> 用于改动
4. 修改课程内容或代码示例
5. 在相关项目目录中测试代码改动
6. 按贡献指南提交拉取请求

### 学习者

1. Fork 或克隆仓库
2. 按顺序进入课程目录
3. 阅读每课的README文件
4. 在 https://ff-quizzes.netlify.app/web/ 完成课前测验
5. 按课程学习代码示例
6. 完成作业和挑战
7. 参加课后测验

### 实时开发

- <strong>文档</strong>：在根目录运行 `docsify serve` （端口3000）
- <strong>测验应用</strong>：在quiz-app目录运行 `npm run dev`
- <strong>项目</strong>：使用VS Code Live Server扩展打开HTML项目
- **API项目**：分别在对应API目录运行 `npm start`

## 测试指南

### 测验应用测试

```bash
cd quiz-app
npm run lint       # 检查代码风格问题
npm run build      # 验证构建是否成功
```

### 银行API测试

```bash
cd 7-bank-project/api
npm run lint       # 检查代码风格问题
node server.js     # 验证服务器启动无错误
```

### 测试总体方法

- 这是一个没有完整自动测试的教学仓库
- 手动测试关注点：
  - 代码示例无错误运行
  - 文档中的链接正常
  - 项目构建成功完成
  - 示例符合最佳实践

### 提交前检查

- 在含package.json的目录运行 `npm run lint`
- 验证Markdown链接有效
- 在浏览器或Node.js中测试代码示例
- 检查翻译结构是否正确保持

## 代码风格指南

### JavaScript

- 使用现代ES6+语法
- 遵循项目中的标准ESLint配置
- 使用有意义的变量和函数名，便于教学理解
- 添加注释解释概念
- 配置Prettier进行代码格式化

### HTML/CSS

- 语义化的HTML5元素
- 响应式设计原则
- 清晰的类命名规范
- 注释说明CSS技术点

### Python

- 遵循PEP 8规范
- 清晰的教学示例代码
- 适当添加类型提示，便于学习

### Markdown文档

- 明确的标题层级结构
- 代码块标明语言
- 资源链接
- 在`images/`目录下存放截图和图片
- 图片含有Alt文本，方便无障碍访问

### 文件组织

- 课程按顺序编号（1-getting-started-lessons、2-js-basics等）
- 每个项目包含`solution/`，通常还有`start/`或`your-work/`目录
- 图片存放在对应课程的`images/`文件夹
- 翻译文件在`translations/{language-code}/`结构下

## 构建与部署

### 测验应用部署（Azure Static Web Apps）

quiz-app配置为Azure静态网页应用部署：

```bash
cd quiz-app
npm run build      # 创建 dist/ 文件夹
# 在 push 到 main 时通过 GitHub Actions 工作流部署
```

Azure静态网页应用配置：
- <strong>应用位置</strong>：`/quiz-app`
- <strong>输出位置</strong>：`dist`
- <strong>工作流</strong>：`.github/workflows/azure-static-web-apps-ashy-river-0debb7803.yml`

### 文档PDF生成

```bash
npm install                    # 安装 docsify-to-pdf
npm run convert               # 从 docs 生成 PDF
```

### Docsify文档

```bash
npm install -g docsify-cli    # 全局安装 Docsify
docsify serve                 # 在 localhost:3000 上启动服务
```

### 项目专属构建

各项目目录可能有自己的构建流程：
- Vue项目：运行`npm run build`生成生产包
- 静态项目：无构建步骤，直接提供文件

## 拉取请求指南

### 标题格式

使用清晰、描述性的标题，说明改动内容：
- `[Quiz-app] 新增第X课测验`
- `[Lesson-3] 修复生态瓶项目拼写错误`
- `[Translation] 为第5课添加西班牙语翻译`
- `[Docs] 更新设置说明`

### 必需检查

提交PR前：

1. <strong>代码质量</strong>：
   - 在相关项目目录运行 `npm run lint`
   - 修复所有lint错误和警告

2. <strong>构建验证</strong>：
   - 如适用，运行`npm run build`
   - 确保无构建错误

3. <strong>链接验证</strong>：
   - 测试所有Markdown链接
   - 确认图片引用正常

4. <strong>内容校对</strong>：
   - 拼写和语法检查
   - 确保代码示例正确且有教学价值
   - 翻译准确保持原意

### 贡献要求

- 同意微软CLA（首次PR自动检查）
- 遵守[微软开源行为准则](https://opensource.microsoft.com/codeofconduct/)
- 请参阅[CONTRIBUTING.md](./CONTRIBUTING.md)了解详细指南
- 若相关，请在PR描述中注明issue编号

### 审核流程

- PR由维护者和社区审核
- 优先保证教育清晰度
- 代码示例应遵循当前最佳实践
- 翻译要求准确且文化适应

## 翻译系统

### 自动翻译

- 使用GitHub Actions的co-op-translator工作流
- 自动翻译50多种语言
- 源文件位于主目录
- 翻译文件存放于`translations/{language-code}/`目录

### 手动改进翻译

1. 在`translations/{language-code}/`找到文件
2. 保持结构下做改进
3. 确保代码示例依然可用
4. 测试本地化测验内容

### 翻译元数据

翻译文件包含元数据头：
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

## 调试与排错

### 常见问题

<strong>测验应用启动失败</strong>：
- 检查Node.js版本（建议v14+）
- 删除`node_modules`和`package-lock.json`，重新运行`npm install`
- 检查端口冲突（默认Vite使用5173端口）

**API服务器无法启动**：
- 验证Node.js版本（node >=10）
- 检查端口是否被占用
- 确认所有依赖已安装`npm install`

<strong>浏览器扩展无法加载</strong>：
- 确认manifest.json格式正确
- 检查浏览器控制台错误
- 按浏览器扩展安装说明操作

**Python聊天项目问题**：
- 确认已安装OpenAI包：`pip install openai`
- 确认GITHUB_TOKEN环境变量已设置
- 检查GitHub模型访问权限

**Docsify未提供文档**：
- 全局安装docsify-cli：`npm install -g docsify-cli`
- 在仓库根目录运行
- 检查`docs/_sidebar.md`是否存在

### 开发环境提示

- HTML项目推荐使用VS Code Live Server扩展
- 安装ESLint和Prettier扩展保持格式一致
- 利用浏览器开发者工具调试JavaScript
- Vue项目安装Vue DevTools浏览器扩展

### 性能考虑

- 多语言翻译文件众多（50+语言）导致完整克隆体积大
- 仅工作内容时可使用浅克隆：`git clone --depth 1`
- 编辑英文内容时排除翻译文件搜索
- 初次运行构建过程较慢（npm install，Vite构建）

## 安全考虑

### 环境变量

- API密钥绝不可提交到仓库
- 使用`.env`文件（已包含在`.gitignore`中）
- 在项目README中注明所需环境变量

### Python项目

- 使用虚拟环境：`python -m venv venv`
- 保持依赖更新
- GitHub令牌应仅授予必要权限

### GitHub模型访问权限

- 访问GitHub模型需要个人访问令牌（PAT）
- 令牌应存为环境变量
- 严禁提交令牌或凭据

## 其他说明

### 目标受众

- 完全的网页开发初学者
- 学生和自学者
- 教室中使用该课程的教师
- 内容设计注重无障碍和渐进技能培养

### 教学理念

- 基于项目的学习方法
- 频繁的知识检测（测验）
- 实操编码练习
- 真实应用示例
- 先掌握基础再学框架

### 仓库维护

- 活跃的学习者和贡献者社区
- 定期更新依赖和内容
- 维护者监控问题和讨论
- 翻译更新自动化通过GitHub Actions

### 相关资源

- [Microsoft Learn模块](https://docs.microsoft.com/learn/)
- [学生中心资源](https://docs.microsoft.com/learn/student-hub/)
- 推荐学习者使用[GitHub Copilot](https://marketplace.visualstudio.com/items?itemName=GitHub.copilot)
- 额外课程：生成式AI、数据科学、机器学习、物联网课程等

### 使用具体项目

详见各项目README文件：
- `quiz-app/README.md` - Vue 3测验应用
- `7-bank-project/README.md` - 带认证的银行应用
- `5-browser-extension/README.md` - 浏览器扩展开发
- `6-space-game/README.md` - 基于Canvas的游戏开发
- `9-chat-project/README.md` - AI聊天助手项目

### Monorepo结构

虽非传统monorepo，但此仓库包含多个独立项目：
- 每课内容自成体系
- 项目不共享依赖
- 可单独开发项目互不影响
- 克隆整个仓库获得完整课程体验

---

<!-- CO-OP TRANSLATOR DISCLAIMER START -->
**免责声明**：  
本文件由 AI 翻译服务 [Co-op Translator](https://github.com/Azure/co-op-translator) 进行翻译。虽然我们力求准确，但请注意自动翻译可能包含错误或不准确之处。原文的母语版本应被视为权威来源。对于重要信息，建议使用专业人工翻译。我们不对因使用本翻译而产生的任何误解或误释承担责任。
<!-- CO-OP TRANSLATOR DISCLAIMER END -->