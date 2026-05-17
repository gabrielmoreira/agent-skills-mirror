---
name: ai
description: AI/LLM 能力索引。Agent 开发、LLM 安全、RAG 系统。当用户提到 AI、LLM、Agent、RAG、Prompt 时路由到此。
license: MIT
user-invocable: false
disable-model-invocation: false
---

# 丹鼎秘典 · AI/LLM 能力中枢

## 能力矩阵

| Skill | 定位 | 核心能力 |
|-------|------|----------|
| [agent-dev](agent-dev.md) | Agent 开发 | 多 Agent 编排、工具调用、RAG |
| [llm-security](llm-security.md) | LLM 安全 | Prompt 注入、越狱防护、输出安全 |
| [rag-system](rag-system.md) | RAG 系统 | 向量数据库、检索策略、重排算法 |
| [prompt-and-eval](prompt-and-eval.md) | Prompt 工程与模型评估 | Few-shot、CoT、ReAct、RAGAS、LLM-as-Judge |

## AI 工程原则

```yaml
设计原则:
  - 人机协作，AI 增强而非替代
  - 可解释性优先
  - 安全边界明确
  - 渐进式自主

开发原则:
  - Prompt 即代码，需版本控制
  - 输入输出都需验证
  - 成本与效果平衡
  - 持续评估与迭代
```
