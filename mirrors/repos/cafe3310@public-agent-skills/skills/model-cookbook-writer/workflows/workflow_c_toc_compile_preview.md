# 工作流 C: TOC 驱动编译与多格式预览 (TOC-Driven Compilation & Previews)

本工作流规范了如何通过 `scripts/compile_cookbook.py` 脚本，将散落的 Markdown 章节及微评测指针，一键拼装并转换为适合不同环境阅读与实操的交付物格式。

---

## 1. 执行步骤

### 步骤 1: 运行编译指令
- **命令**:
  ```bash
  python3 scripts/compile_cookbook.py cookbooks/YYYY-MM-DD_{model-name}_{cookbook-name}
  ```
  *注：若未提供路径且 `cookbooks/` 下仅有一个项目，脚本会自动定位；但为保证准确性，推荐显式指定绝对或相对路径。*

### 步骤 2: 正文物理拼装 (contents.md)
- **机制**:
  1. 脚本深度解析 `toc.md`，提取所有被引用的物理文件。
  2. 剥离每个 Markdown 文件头部的 YAML Frontmatter，并在章节交界处动态插入带有唯一 HTML ID 的锚点标签（如 `<a id="sec-1-1"></a>`）。
  3. 按大纲顺序无损拼接，并将整合后的 Markdown 正文写入 `build/YYYY-MM-DD_{model-name}_{cookbook-name}/contents.md`。

### 步骤 3: 磨砂玻璃 ScrollSpy HTML 编译 (preview.html)
- **机制**:
  1. 编译输出单文件 HTML `preview.html`。
  2. **页面结构**:
     - 左侧：双栏/单栏磨砂玻璃质感的树形大纲导航，自带模糊实时过滤搜索框。
     - 右侧：marked.js 实时渲染的阅读区域。
     - 滚动监听 (ScrollSpy)：当用户在右侧滚动阅读时，左侧目录高亮根据当前的 DOM 锚点 ID 平滑跟随。
  3. **Unicode 安全防崩机制 (CRITICAL)**:
     - 脚本将拼接好的 Markdown 做 Base64 编码嵌入 HTML。
     - 在前端还原 Base64 时，**严禁使用** `decodeURIComponent(escape(atob(...)))`，这遇到复杂中文、特定 Emoji 或生僻 Unicode 字符时会发生 `URIError: URI malformed` 导致页面彻底白屏。
     - **必须**使用 `TextDecoder("utf-8")` 进行安全的字节数组转换：
       ```javascript
       const binaryString = atob(base64Content);
       const len = binaryString.length;
       const bytes = new Uint8Array(len);
       for (let i = 0; i < len; i++) {
           bytes[i] = binaryString.charCodeAt(i);
       }
       const markdownText = new TextDecoder("utf-8").decode(bytes);
       ```

### 步骤 4: 行级状态机 IPYNB 编译 (preview.ipynb)
- **机制**:
  1. 脚本对 `contents.md` 执行**行级状态机**遍历，进行 Markdown 块和 Python 代码块的物理剥离。
  2. **状态转移规则**:
     - *状态 0 (Markdown)*: 逐行收集文本。当遇到 ````python` 时，将收集到的文本打包成一个 `markdown` cell，切换为 *状态 1*。
     - *状态 1 (Python Code)*: 逐行收集代码。当遇到 ```` ` 时，将收集到的代码打包成一个 `code` cell，清空 outputs 与 execution_count，切换回 *状态 0*。
  3. 最终输出符合 Jupyter Notebook v4 JSON 规范的 `preview.ipynb`，供 VS Code 或 Colab 打开一键运行，使 Cookbook 具有动态调试能力。

### 步骤 5: 构建物隔离与 Git 忽略
- **行动**:
  1. 脚本的生成物（`contents.md`, `preview.html`, `preview.ipynb`）必须统一放置于根目录下的 `build/` 子目录中，严禁写回 `cookbooks/` 源目录。
  2. 在项目根目录的 `.gitignore` 中必须添加一行 `build/`。

---

## 2. 约束规范

- **零硬编码 HTML**: 严禁在 `cookbook-chapters/` 和 `cookbooks/` 的源 Markdown 中硬编码大纲结构及搜索逻辑，这些都属于编译阶段的视图渲染，必须由脚本动态生成。
- **Notebook 代码闭环**: 凡编译为 `code` cell 的代码段，原则上应能独立或在上下文依赖下运行，严禁保留大量未闭环的占位伪代码。
