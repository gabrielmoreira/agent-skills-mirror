# 工作流 B: 组织 Cookbook (Interactive Case Collection & Setup)

本工作流规范了如何通过与项目负责人交互式沟通，收集特定主题下的用例（cases/benches）和章节，并物理初始化对应的 Cookbook 交付项目。

---

## 1. 执行步骤

### 步骤 1: 交互式收集需求与用例
- **行动**:
  1. **明确主题与模型**: 主动询问负责人拟产出的 Cookbook 针对什么模型（如 `ring-2.6-1t`）以及什么主题（如 `tool-calling`、`structured-outputs`、`agent-orchestration` 等）。
  2. **盘点可用资产**: 扫描当前仓库的 `cookbook-chapters/`、`benches/` 和 `bench-results/`，列出与该主题相关的所有已有章节、评测任务和已跑出数据的评测结果。
  3. **确认包含用例**: 通过交互式提问（或提出推荐的用例列表），让负责人确认本次 Cookbook 编译中拟包含的 Chapters、Benches 和 Results。

### 步骤 2: 物理创建交付项目目录
- **行动**:
  1. **确定命名与路径**: 在 `cookbooks/` 目录下创建平铺的项目文件夹。命名规范为：`YYYY-MM-DD_{model-name}_{cookbook-name}`。
     *   *若该 Cookbook 包含未完工的内容/评测，则命名中必须加入 `_🟥_`，例如：`YYYY-MM-DD_🟥_{model-name}_{cookbook-name}`。*
  2. **初始化核心文件**:
     - 创建 `readme.md`：记录此 Cookbook 的主题、适用模型、受众、以及所基于的最佳实践来源。
     - 创建 `toc.md`：核心驱动大纲（参见步骤 3 的 TOC 规范）。
     - 创建 `contents.md`：空文件，或仅包含基本大标题。该文件后续由编译脚本自动填充，严禁手动在此处写入正文。

### 步骤 3: 编写 TOC 驱动大纲 (toc.md)
- **行动**:
  1. 在 `toc.md` 中以无序列表形式定义整个 Cookbook 的树状结构。
  2. 每一级节点代表一个章节，非叶子节点和叶子节点必须使用 WikiLinks 或相对路径关联到 `cookbook-chapters/` 下的具体目录或文件。
  3. 对于需要挂载评测或跑分结果的叶子章节，必须在其下方以缩进的无序列表挂载指向 `benches/` 和 `bench-results/` 物理目录的链接。
  4. **TOC 结构规范示例**:
     ```markdown
     # TOC 大纲
     
     - [[cookbook-chapters/EXAMPLE-tool-calling/content.md|第一章：工具调用基础]]
     - [[cookbook-chapters/EXAMPLE-tool-calling/file-delimiters/content.md|第二章：文件分隔符调优技巧]]
       - [评测源码](file:///benches/2026-01-01_EXAMPLE-different-delimeter-for-files/)
       - [跑分数据与推理日志](file:///bench-results/2026-01-01_model-name_EXAMPLE-different-delimeter-for-files/)
     ```

### 步骤 4: 任务流追加与状态标记
- **行动**:
  1. 交叉检查 TOC 挂载的内容。如果引用的 Chapters、Benches 或 Results 中包含 `🟥` 占位，则在此 Cookbook 的 `toc.md` 对应节点旁，以及整个项目的根目录 `TODO.md` 中，追加相应的 `🟥` 任务条目。
  2. 使用统一的任务追踪格式追加在 `TODO.md` 的 Task Stream 中，例如：
     ```markdown
     - YYYY-MM-DD HH:mm 🟥 补充 {cookbook-name} 引用的 {bench-name} 评测用例与 runner 代码
     ```
  3. 向负责人汇报项目已成功初始化，列出生成的 `readme.md` 和 `toc.md` 的路径，并展示当前待办任务，等待下一步开发指派。

---

## 2. 约束规范

- **TOC 唯一驱动**: 任何 Cookbook 的生成必须通过 `toc.md` 引导。不得在 `contents.md` 中直接进行手动拼装或硬编码。
- **状态一致性**: 若 Cookbook 包含未完成的评测（`benches/` 带有 `🟥`），整个 Cookbook 目录名和 `toc.md` 中必须包含 `🟥` 标志，直至评测数据完全跑出并合入 `bench-results/`。
