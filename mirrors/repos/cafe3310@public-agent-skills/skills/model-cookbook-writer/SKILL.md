---
name: model-cookbook-writer
description: 编写、丰富与编译 model cookbook 的专用人机协作开发工作流。包含 Prompting Guide 大纲扩展、交付物大纲拆解与初始化、TOC 驱动编译为 HTML/Jupyter Notebook 预览及两库联动沉淀。
license: Apache-2.0
author: github/cafe3310
depends_on_skill: [cafe3310-obsidian-writer, memories-off]
depends_on_binary: [python3]
---

# Skill: model-cookbook-writer

本 Skill 定义了一套大模型应用 Cookbook 在工程与文档开发中的全生命周期开发规范和人机协作工作流。它为将策略调优、评测跑分、代码用例与最终发布版拼装预览建立了完整的规范契约。

---

## 1. 仓库结构规范 (Repository Architecture)

大模型 Cookbook 仓库必须严格遵守以下目录结构和文件格式定义，以确保编译脚本能够自动解析、拼接，并支持与知识图谱的联动。

```
ling-model-cookbook/
├── AGENTS.md                  # 项目章程与规范文件 (明确规则与协作流程)
├── TODO.md                    # 动态的任务积压与指派清单 (Log-driven Task Stream)
├── cookbook-chapters/         # 章节内容树 (存放理论、最佳实践及代码示例)
│   └── {chapter-name}/
│       ├── content.md         # 章节正文文本说明 (非叶子节点通常只包含此文件)
│       ├── benchmarks.md      # 评估该章节提示词机制的 micro-benchmarks 建议 (叶子节点专有)
│       └── examples.md        # 该章节的具体任务代码样例 (叶子节点专有)
├── benches/                   # 所有的微评测任务物理源码 (平铺命名)
│   └── YYYY-MM-DD_{bench-name}/
│       ├── README.md          # 评测目的、方式、对比分支及 Rubrics 四要素说明
│       ├── cases/             # 结构化的测试用例数据集 (如 test_cases.json)
│       └── test_runner.py     # 可独立运行的 Python 评测脚本
├── bench-results/             # 跑分数据客观归档 (平铺命名，与 benches 对应)
│   └── YYYY-MM-DD_{model-name}_{bench-name}/
│       ├── README.md          # 记录测试环境、简要结论与复现命令
│       ├── results.json       # 汇总跑出的评测指标结果 (包含 metrics、config 等字段)
│       └── detail.json        # 记录每个 case 的具体推理日志与判定详情
└── cookbooks/                 # 具体的 Cookbook 交付发布项目 (平铺命名)
    └── YYYY-MM-DD_{model-name}_{cookbook-name}/
        ├── readme.md          # 项目说明，介绍本次交付的背景、模型及受众
        ├── toc.md             # 编译主驱动大纲，通过树形列表挂载 Chapters、Benches 与 Results
        └── contents.md        # 编译产物：拼接合并后的正文大合集 (严禁手动在此处编辑内容)
```

### 核心目录详解
1.  **章节分类树 (`cookbook-chapters/`)**:
    *   **非叶子章节**: 仅用于大类框架，包含 `content.md`，用于对本大类机制做宏观概述。
    *   **叶子章节**: 真正的落地实现节点，必须同时包含 `content.md`、`benchmarks.md` 与 `examples.md`。
    *   *未开始编写的章节，其 Markdown 首行必须以 `🟥` 起头做待办标记。*
2.  **微评测任务 (`benches/`)**:
    *   平铺命名。未完工的评测任务在日期后缀加上 `_🟥_`。
    *   `README.md` 中**必须**包含四要素：**评测目的、评测方式、对比方案、判定标准 (Rubrics)**。
3.  **跑分数据 (`bench-results/`)**:
    *   若评测尚未执行或正在执行，其 `README.md` 的状态需配置为 `Pending`，且 results.json 的 state 置为 `pending`。
    *   测试完成后，合入最终的 metrics 数据与 inputs/outputs 推理明细。
4.  **交付项目 (`cookbooks/`)**:
    *   大纲和正文彻底解耦。`toc.md` 扮演大纲路由，挂载物理文件的链接；`contents.md` 是编译生成的最终产物。

---

## 2. 核心工作流分支 (Decoupled Workflows)

本技能解耦为四个独立的工作流分支文件，指导开发助理（Agent）与负责人的不同阶段协作：

*   **[工作流 A: 摄取参考与扩展大纲 (Read & Extend Outline)](file://./workflows/workflow_a_ingest_references.md)**
    *   *场景*: 阅读官方最新提示词工程文献后，提炼核心策略与微评测任务并合入交付大纲。
*   **[工作流 B: 组织 Cookbook (Interactive Case Collection & Setup)](file://./workflows/workflow_b_organize_cookbook.md)**
    *   *场景*: 交互式盘点可用资产，定制 `toc.md` 物理引用关系并初始化新交付项目。
*   **[工作流 C: TOC 驱动编译与多格式预览 (TOC-Driven Compilation & Previews)](file://./workflows/workflow_c_toc_compile_preview.md)**
    *   *场景*: 运行脚本将大纲编译拼装为 `contents.md`、ScrollSpy 滚动高亮 `preview.html` 网页及状态机拆分的 `preview.ipynb` 笔记本。
*   **[工作流 D: 知识图谱与文档同步 (Knowledge Base & Vault Synchronization)](file://./workflows/workflow_d_sync_knowledge_base.md)**
    *   *场景*: 开发完结后，通过 `memocli` 非破坏性追加图谱并生成 Obsidian 📅 状态报告，执行 iCloud Git 同步优化。

---

## 3. 微型范例仓库 (Example Assets)

为了直观地展示符合本 Skill 结构定义的仓库设计，在 [assets/example-cookbook-repo/](file://./assets/example-cookbook-repo/) 中建立了一个微型模拟仓库作为参考：

*   **项目章程与清单**:
    - [AGENTS.md (模拟项目章程契约)](file://./assets/example-cookbook-repo/AGENTS.md)
    - [TODO.md (模拟任务日志)](file://./assets/example-cookbook-repo/TODO.md)
*   **章节设计**:
    - [EXAMPLE-tool-calling/content.md (大类父章节)](file://./assets/example-cookbook-repo/cookbook-chapters/EXAMPLE-tool-calling/content.md)
    - [file-delimiters/content.md (叶子章节正文)](file://./assets/example-cookbook-repo/cookbook-chapters/EXAMPLE-tool-calling/file-delimiters/content.md)
    - [file-delimiters/benchmarks.md (叶子章节评估说明)](file://./assets/example-cookbook-repo/cookbook-chapters/EXAMPLE-tool-calling/file-delimiters/benchmarks.md)
    - [file-delimiters/examples.md (叶子章节代码用例)](file://./assets/example-cookbook-repo/cookbook-chapters/EXAMPLE-tool-calling/file-delimiters/examples.md)
*   **评测源码与结果**:
    - [benches/.../README.md (包含评测四要素说明)](file://./assets/example-cookbook-repo/benches/2026-01-01_EXAMPLE-different-delimeter-for-files/README.md)
    - [bench-results/.../results.json (客观指标跑分数据)](file://./assets/example-cookbook-repo/bench-results/2026-01-01_model-name_EXAMPLE-different-delimeter-for-files/results.json)
*   **发布交付物**:
    - [cookbooks/.../toc.md (TOC 树形驱动大纲)](file://./assets/example-cookbook-repo/cookbooks/2026-01-01_model-name_EXAMPLE-different-delimeter-for-files/toc.md)
    - [cookbooks/.../contents.md (拼接合成的最终正文)](file://./assets/example-cookbook-repo/cookbooks/2026-01-01_model-name_EXAMPLE-different-delimeter-for-files/contents.md)

---

## 4. 自动化编译工具说明 (Compiler CLI)

本 Skill 在 `scripts/` 目录下搭载了自动化编译预览工具：
*   **脚本物理路径**: `scripts/compile_cookbook.py`
*   **执行方式**:
    ```bash
    python3 scripts/compile_cookbook.py <cookbook_directory_path>
    ```
*   **产出位置**: `build/<cookbook_folder_name>/` (已由项目根目录的 `.gitignore` 排除，保持 Git 环境整洁)。

---

## 5. 技能包待办事项 (TODO & Roadmap)

本 Skill 目前专注于 Cookbook 的大纲提炼、用例组织、TOC 驱动编译和两库联动记录，**尚未包含**以下核心开发环节的工作流与规范：
*   🟥 **开发评测 Framework**：即 `bench-framework/` 基座项目（包括与模型 API 交互的 client 封装、判定逻辑 judge 以及执行度量 runner 引擎）的开发与维护规范。
*   🟥 **开发评测任务**：即 `benches/` 目录下具体测试用例集设计、`test_runner.py` 逻辑实现及本地联调的开发工作流。
