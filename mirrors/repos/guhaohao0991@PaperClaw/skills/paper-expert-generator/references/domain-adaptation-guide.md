# Domain Adaptation Guide

## Table of Contents
1. [Keyword Library Examples (8 Domains)](#1-keyword-library-examples)
2. [Evaluation Rubric Examples (8 Domains)](#2-evaluation-rubric-examples)
3. [Summary Question Adaptation](#3-summary-question-adaptation)
4. [Role Definition Persona Guide](#4-role-definition-persona-guide)

---

## 1. Keyword Library Examples

### Template Format
```
CORE KEYWORDS (ti: arXiv title search):
  - "ti:<topic> <method>"
  - "ti:<method> <application>"

METHOD KEYWORDS:
  - "ti:<technique> <domain>"

APPLICATION KEYWORDS:
  - "ti:<use-case> <domain>"

EXCLUSION KEYWORDS (for --exclude filter):
  - <unrelated_term1>, <unrelated_term2>
```

---

### 1.1 Bioinformatics / Computational Biology

**Core queries:**
- `ti:protein structure prediction transformer`
- `ti:single cell RNA sequencing deep learning`
- `ti:drug discovery graph neural network`
- `ti:genomics foundation model`
- `ti:protein language model`

**Method queries:**
- `ti:diffusion model protein design`
- `ti:graph neural network molecular property`
- `ti:attention mechanism genomics`
- `ti:contrastive learning biological sequence`

**Application queries:**
- `ti:drug target interaction neural network`
- `ti:gene expression prediction`
- `ti:variant effect prediction`

**Exclusion keywords:**
- `epidemiology`, `clinical trial`, `social network`, `NLP`, `finance`, `image classification`

---

### 1.2 Computer Vision

**Core queries:**
- `ti:vision transformer image recognition`
- `ti:3D object detection neural network`
- `ti:video understanding temporal`
- `ti:image generation diffusion model`
- `ti:scene understanding segmentation`

**Method queries:**
- `ti:self-supervised learning visual representation`
- `ti:neural radiance field 3D reconstruction`
- `ti:contrastive learning vision`
- `ti:efficient transformer vision`

**Application queries:**
- `ti:autonomous driving perception`
- `ti:medical image segmentation`
- `ti:video object detection`

**Exclusion keywords:**
- `NLP`, `finance`, `genomics`, `protein`, `drug discovery`, `social media`

---

### 1.3 Reinforcement Learning / Decision Making

**Core queries:**
- `ti:reinforcement learning offline policy`
- `ti:multi-agent reinforcement learning cooperative`
- `ti:model-based reinforcement learning world model`
- `ti:large language model planning reasoning`
- `ti:reward learning human feedback`

**Method queries:**
- `ti:transformer reinforcement learning`
- `ti:diffusion policy robot learning`
- `ti:hierarchical reinforcement learning`

**Application queries:**
- `ti:reinforcement learning robotics manipulation`
- `ti:game playing neural network`

**Exclusion keywords:**
- `finance portfolio`, `epidemiology`, `social network analysis`, `drug discovery`

---

### 1.4 Natural Language Processing (NLP)

**Core queries:**
- `ti:large language model reasoning`
- `ti:instruction tuning alignment`
- `ti:retrieval augmented generation`
- `ti:code generation LLM`
- `ti:multilingual language model`

**Method queries:**
- `ti:parameter efficient fine-tuning`
- `ti:chain of thought prompting`
- `ti:knowledge graph language model`

**Application queries:**
- `ti:question answering language model`
- `ti:text summarization neural`

**Exclusion keywords:**
- `finance`, `genomics`, `protein`, `image classification`, `drug discovery`

---

### 1.5 Quantum Computing / Quantum ML

**Core queries:**
- `ti:quantum machine learning variational`
- `ti:quantum neural network circuit`
- `ti:quantum error correction`
- `ti:variational quantum algorithm optimization`
- `ti:quantum advantage classical simulation`

**Method queries:**
- `ti:quantum circuit optimization`
- `ti:quantum kernel method classification`

**Application queries:**
- `ti:quantum chemistry simulation`
- `ti:quantum cryptography`

**Exclusion keywords:**
- `classical machine learning`, `NLP`, `finance`, `epidemiology`

---

### 1.6 Robotics / Embodied AI

**Core queries:**
- `ti:robot manipulation dexterous`
- `ti:embodied agent navigation`
- `ti:sim-to-real transfer robot`
- `ti:imitation learning robot`
- `ti:robot foundation model`

**Method queries:**
- `ti:transformer robot planning`
- `ti:diffusion policy imitation`
- `ti:3D perception robot grasping`

**Application queries:**
- `ti:household robot task planning`
- `ti:legged locomotion learning`

**Exclusion keywords:**
- `NLP`, `finance`, `genomics`, `2D image classification`

---

### 1.7 Scientific ML / Physics-Informed ML (PaperClaw default)

**Core queries:**
- `ti:geometry-aware neural operator`
- `ti:neural operator unstructured mesh`
- `ti:transformer PDE solver 3D`
- `ti:physics-informed neural network 3D`
- `ti:discretization-invariant operator`

**Method queries:**
- `ti:operator learning arbitrary geometry`
- `ti:deep learning CFD surrogate`
- `ti:neural surrogate structural mechanics`

**Application queries:**
- `ti:surrogate model 3D geometry`
- `ti:mesh-based neural operator`

**Exclusion keywords:**
- `epidemic`, `finance`, `NLP`, `language model`

---

### 1.8 Graph Learning / Network Science

**Core queries:**
- `ti:graph neural network scalable`
- `ti:graph transformer heterogeneous`
- `ti:graph foundation model`
- `ti:dynamic graph temporal`
- `ti:knowledge graph embedding`

**Method queries:**
- `ti:message passing neural network`
- `ti:graph contrastive learning`
- `ti:graph generative model`

**Application queries:**
- `ti:molecular graph property prediction`
- `ti:social network graph learning`

**Exclusion keywords:**
- `NLP text`, `image classification`, `finance`, `epidemiology`

---

## 2. Evaluation Rubric Examples

### Template
```
Dimension 1 (<name>, JSON key: <key>): <definition>
Dimension 2 (<name>, JSON key: <key>): <definition>
Dimension 3 (<name>, JSON key: <key>): <definition>
Dimension 4 (<name>, JSON key: <key>): <definition>
```

---

### 2.1 Bioinformatics

| Dimension | JSON key | Measures |
|-----------|----------|---------|
| Biological Validity | `biological_validity` | Are biological assumptions correct? Does the model respect known molecular constraints? |
| Computational Scalability | `computational_scalability` | Can the method handle genome-scale data? Memory/compute efficiency? |
| Benchmark Quality | `benchmark_quality` | Standard dataset usage, comparison with SOTA, statistical rigor |
| Translational Potential | `translational_potential` | Real-world applicability: clinical, drug discovery, wet-lab validation |

---

### 2.2 Computer Vision

| Dimension | JSON key | Measures |
|-----------|----------|---------|
| Architecture Innovation | `architecture_innovation` | Novel model design, efficiency improvements, parameter reduction |
| Benchmark Performance | `benchmark_performance` | SOTA comparisons on standard benchmarks (ImageNet, COCO, etc.) |
| Generalization | `generalization` | Cross-dataset transfer, domain shift robustness, few-shot ability |
| Practical Utility | `practical_utility` | Real-world deployment feasibility, inference speed, model size |

---

### 2.3 Reinforcement Learning

| Dimension | JSON key | Measures |
|-----------|----------|---------|
| Algorithm Contribution | `algorithm_contribution` | Novelty of RL algorithm, theoretical guarantees, sample efficiency |
| Task Complexity | `task_complexity` | Difficulty and diversity of evaluated environments |
| Generalization | `generalization` | Zero-shot transfer, multi-task capability, sim-to-real |
| Reproducibility | `reproducibility` | Code availability, hyperparameter sensitivity, variance reporting |

---

### 2.4 NLP / LLM

| Dimension | JSON key | Measures |
|-----------|----------|---------|
| Capability Advance | `capability_advance` | New abilities enabled, reasoning improvement, task coverage |
| Efficiency | `efficiency` | Parameter efficiency, inference cost, fine-tuning cost |
| Safety & Alignment | `safety_alignment` | RLHF quality, refusal behavior, bias reduction |
| Evaluation Rigor | `evaluation_rigor` | Benchmark breadth, human evaluation, ablation studies |

---

### 2.5 Scientific ML / Physics (PaperClaw default)

| Dimension | JSON key | Measures |
|-----------|----------|---------|
| Engineering Value | `engineering_value` | Production deployment feasibility, industrial applicability |
| Architecture Innovation | `architecture_innovation` | Novel operator/network design, discretization invariance |
| Theoretical Contribution | `theoretical_contribution` | Mathematical rigor, approximation theory, convergence proofs |
| Result Reliability | `result_reliability` | Benchmark coverage, error metrics, ablation thoroughness |

---

## 3. Summary Question Adaptation

The 10 summary questions in `paper-review/SKILL.md` should be adapted per domain. The first 5 are universal; adapt questions 6–10 for domain specifics.

### Universal Questions (Q1–Q5) – Same Across All Domains
1. 论文试图解决什么问题？
2. 这是一个新问题吗？已有工作的局限是什么？
3. 验证的科学假设/核心主张是什么？
4. 有哪些相关研究？关键研究者和代表工作是什么？
5. 解决方案的核心技术贡献是什么？

### Domain-Specific Questions (Q6–Q10)

**Bioinformatics:**
6. 使用了哪些生物学数据集？有无湿实验验证？
7. 方法在基因组规模数据上的计算复杂度和可扩展性如何？
8. 模型是否考虑了已知的生物学约束（如序列保守性、结构先验）？
9. 与 AlphaFold / ESM / scBERT 等 SOTA 基线的对比结果如何？
10. 该工作对临床转化或药物发现有何意义？

**Computer Vision:**
6. 使用了哪些基准数据集？与 SOTA 方法的对比结果？
7. 模型的计算效率（参数量、FLOPs、推理速度）如何？
8. 是否进行了跨数据集泛化实验或域迁移测试？
9. 实验设计是否包含充分的消融研究？
10. 该工作对实际部署（边缘设备、实时系统）有何影响？

**Scientific ML (PaperClaw default):**
6. 实验是如何设计的？使用了哪些 PDE/仿真基准？
7. 数据集是否公开？代码是否开源？
8. 实验结果是否支持所提假设？误差指标如何？
9. 该论文的核心贡献（理论/架构/工程）是什么？
10. 未来工作方向？在 3D 几何代理建模中的潜在应用？

---

## 4. Role Definition Persona Guide

The AGENT.md role definition should establish the agent as a world-class expert in the target domain. Use this template:

```
你是一位专注于 <DOMAIN> 领域的首席研究科学家，在以下方向具有深度专业积累：

**核心研究方向**：
- <sub-area 1>（<2–3 key methods/concepts>）
- <sub-area 2>（<2–3 key methods/concepts>）
- <sub-area 3>（<2–3 key methods/concepts>）

**方法论专长**：
- 深度掌握 <technique 1>、<technique 2>、<technique 3>
- 熟悉 <benchmark 1>、<benchmark 2> 等标准评测体系
- 了解 <top venue 1>（如 <journal/conference>）的收录标准

**评估视角**：
- 能从 <perspective 1>（如工程可行性）维度评判论文价值
- 能从 <perspective 2>（如理论严谨性）维度评判论文价值
- 重点关注：<what matters most in this field>
```

### Example – Bioinformatics Persona
```
你是一位专注于计算生物学与生物信息学的首席研究科学家，在以下方向具有深度专业积累：

**核心研究方向**：
- 蛋白质结构预测与设计（AlphaFold、ESMFold、RFdiffusion）
- 单细胞多组学分析（scRNA-seq、ATAC-seq、空间转录组）
- 药物-靶点相互作用预测（图神经网络、分子对接）

**方法论专长**：
- 深度掌握蛋白质语言模型（ESM-2、ProtTrans）、图神经网络（GNN）、扩散模型
- 熟悉 CASP、CATH、DrugBank、ChEMBL 等标准基准数据集
- 了解 Nature Methods、Cell Systems、Bioinformatics 的收录标准

**评估视角**：
- 能从生物学合理性和计算可扩展性两个维度评判论文价值
- 重点关注：湿实验验证程度、基因组规模适用性、临床转化潜力
```
