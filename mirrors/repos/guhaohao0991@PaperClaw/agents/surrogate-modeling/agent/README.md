# Surrogate-Modeling Expert Agent

## 📋 系统概述

这是一个专门用于三维几何代理模型领域论文检索、总结和评估的智能代理系统。

### 核心功能

1. **论文自动检索** - 每天21:00自动从 arXiv 检索最新论文
2. **深度总结评估** - 对筛选的论文进行专业级总结和评分
3. **周报自动生成** - 每周日10:00生成精选周报并发送如流消息

---

## 📁 目录结构

```
~/.openclaw/agents/surrogate-modeling-expert/
├── AGENT.md                    # Agent 核心定义和任务说明
├── README.md                   # 本文件
├── models.json                 # 模型配置
└── skills/                     # 技能模块
    ├── arxiv-search/           # arXiv 论文检索技能
    │   └── SKILL.md
    ├── paper-review/           # 论文总结评估技能
    │   └── SKILL.md
    ├── weekly-report/          # 周报生成技能
    │   ├── SKILL.md
    │   └── scripts/
    │       └── generate_weekly_report_v2.py
    └── semantic-scholar/      # Semantic Scholar API
        ├── SKILL.md
        └── semantic_scholar_api.py

workspace/3d_surrogate_proj/
├── papers/                     # 论文存储目录
│   └── <paper_title>/
│       ├── *.pdf              # 论文原文
│       ├── summary.md         # 论文总结
│       ├── scores.md          # 论文评分
│       └── metadata.json      # 元数据
├── weekly_reports/            # 周报存储目录
│   └── YYYY-MM-DD_weekly_report.md
├── search_logs/               # 检索日志目录
│   └── YYYY-MM-DD_search_log.json
└── evaluated_papers.json      # 论文索引
```

---

## ⚙️ 定时任务配置

### 1. 每日论文检索
- **触发时间**: 每天 21:00 (UTC+8)
- **任务内容**: 
  - 使用8个核心关键词检索 arXiv
  - 每个关键词检索30篇论文
  - 筛选质量最好的3篇进行深度分析

### 2. 每周报告生成
- **触发时间**: 每周日 10:00 (UTC+8)
- **任务内容**:
  - 回顾本周所有论文
  - 筛选 Top 3 精选论文
  - 生成 Markdown 周报
  - 发送如流消息

---

## 🔍 检索关键词

### 核心关键词
1. `geometry-aware neural operator` - 几何感知神经算子
2. `operator learning on arbitrary domains` - 任意域上的算子学习
3. `transformer for PDE` - PDE 求解的 Transformer 方法
4. `Latent Manifold Operator Learning` - 潜在流形算子学习
5. `Scientific Machine Learning` - 科学机器学习
6. `PhysicsML` - 物理机器学习
7. `Physics-Informed Neural Network` - 物理信息神经网络
8. `Neural PDE` - 神经 PDE 求解器

---

## 📊 论文评估体系

### 评分维度

#### 1. 工程应用价值 (Engineering Application) - 1-10分
- 解决实际工程问题的能力
- 工业级验证程度
- 部署可行性与效率优势

#### 2. 网络架构创新 (Architecture Innovation) - 1-10分
- 架构设计的新颖性
- 模块和机制的创新
- 与现有架构的对比优势

#### 3. 理论贡献 (Theoretical Contribution) - 1-10分
- 是否提出新的数学框架
- 是否证明重要定理
- 是否建立新的理论连接
- 理论深度与严谨性

#### 4. 结果可靠性 (Reliability) - 1-10分
- 实验设计严谨性
- 开源代码与数据
- 结果可复现性

#### 5. 影响力评分 (Impact Score) - 1-10分
- 科研与应用价值
- 与业界前沿对比
- Date-Citation权衡调整

**最终评分公式**：
```
四维基础评分 = (工程应用 + 架构创新 + 理论贡献 + 可靠性) / 4
最终综合评分 = 四维基础评分 × 0.9 + 影响力评分 × 0.1
```

---

## 🚀 使用方法

### 手动触发检索
```bash
# 用户可以通过对话触发
"帮我检索 geometry-aware neural operator 相关的最新论文"

# 或者指定关键词
"帮我搜索 transformer for PDE 的最新研究"
```

### 查看检索结果
```bash
# 查看论文目录
ls workspace/3d_surrogate_proj/papers/

# 查看某篇论文的总结
cat workspace/3d_surrogate_proj/papers/<paper_title>/summary.md

# 查看某篇论文的评分
cat workspace/3d_surrogate_proj/papers/<paper_title>/scores.md
```

### 查看周报
```bash
# 查看周报目录
ls workspace/3d_surrogate_proj/weekly_reports/

# 查看最新周报
cat workspace/3d_surrogate_proj/weekly_reports/*.md
```

### 管理定时任务
```bash
# 查看所有定时任务
openclaw cron list

# 临时禁用任务
openclaw cron update <job-id> --patch '{"enabled": false}'

# 立即执行任务
openclaw cron run <job-id>
```

---

## 📝 论文总结规范

每篇论文的 `summary.md` 必须回答以下10个问题：

1. 论文试图解决什么问题？
2. 这是一个新问题吗？以前的研究工作有没有解决相同或类似的问题？
3. 这篇文章要验证一个什么科学假设？
4. 有哪些相关研究？如何归类？谁是这一课题在领域内值得关注的研究员？
5. 论文中提到的解决方案之关键是什么？
6. 论文中的实验是如何设计的？
7. 用于定量评估的数据集是什么？代码有没有开源？
8. 论文中的实验及结果有没有很好地支持需要验证的科学假设？
9. 这篇论文到底有什么贡献？
10. 下一步怎么做？有什么工作可以继续深入？

---

## 🎯 专业领域

### 数学深度
- 算子学习理论（Operator Learning）
- 泛函分析
- 偏微分方程（PDEs）的神经数值求解
- 几何深度学习
- 最优传输（Optimal Transport）几何嵌入
- 微分流形参数化
- 非结构化网格的算子学习

### 架构前沿
- 稀疏注意力（Sparse Attention）
- Multi-Latent-Attention
- 降阶模型（Reduced Order Modeling）
- 等变神经网络（Equivariant NNs）
- 图神经网络（Graph Neural Network）

### 工程经验
- 超大规模 3D 几何处理
- 分布式 HPC 训练
- 显存优化技术（FlashAttention, Kernel Fusion）
- 线性复杂度算子 O(N) 在大规模工业级 3D 仿真中的落地

---

## 🔄 更新日志

### v1.0 (2026-03-02)
- ✅ 创建 Agent 核心配置
- ✅ 创建 arXiv 检索技能
- ✅ 创建论文总结评估技能
- ✅ 创建周报生成技能
- ✅ 配置每日检索定时任务 (21:00)
- ✅ 配置每周报告定时任务 (周日 10:00)
- ✅ 创建项目目录结构
- ✅ 实现四维评分系统
- ✅ 实现 Date-Citation 权衡机制
- ✅ 集成知识库文档创建
- ✅ 集成如流消息推送

---

*Surrogate-Modeling Expert Agent v1.0*  
*创建时间: 2026-03-02*
