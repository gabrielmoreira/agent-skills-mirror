---
name: cost-aware-llm-pipeline
description: LLM API 使用成本优化模式——基于任务复杂度的模型路由、预算跟踪、重试逻辑和提示词缓存。
origin: ECC
---

# 成本感知型 LLM 流水线 (Cost-Aware LLM Pipeline)

在保持质量的同时控制 LLM API 成本的模式。将模型路由 (Model Routing)、预算跟踪 (Budget Tracking)、重试逻辑 (Retry Logic) 和提示词缓存 (Prompt Caching) 组合成一个可复用的流水线。

## 何时启用

- 构建调用 LLM API（Claude、GPT 等）的应用
- 处理具有不同复杂度的批量项目
- 需要将 API 支出控制在预算范围内
- 在不牺牲复杂任务质量的前提下优化成本

## 核心概念

### 1. 基于任务复杂度的模型路由 (Model Routing)

为简单任务自动选择更便宜的模型，将昂贵的模型留给复杂任务。

```python
MODEL_SONNET = "claude-sonnet-4-6"
MODEL_HAIKU = "claude-haiku-4-5-20251001"

_SONNET_TEXT_THRESHOLD = 10_000  # 字符数阈值
_SONNET_ITEM_THRESHOLD = 30     # 项目数阈值

def select_model(
    text_length: int,
    item_count: int,
    force_model: str | None = None,
) -> str:
    """根据任务复杂度选择模型。"""
    if force_model is not None:
        return force_model
    if text_length >= _SONNET_TEXT_THRESHOLD or item_count >= _SONNET_ITEM_THRESHOLD:
        return MODEL_SONNET  # 复杂任务
    return MODEL_HAIKU  # 简单任务 (便宜 3-4 倍)
```

### 2. 不可变成本跟踪 (Immutable Cost Tracking)

使用冻结的数据类 (Frozen Dataclasses) 跟踪累计支出。每次 API 调用都会返回一个新的跟踪器——绝不修改原始状态。

```python
from dataclasses import dataclass

@dataclass(frozen=True, slots=True)
class CostRecord:
    model: str
    input_tokens: int
    output_tokens: int
    cost_usd: float

@dataclass(frozen=True, slots=True)
class CostTracker:
    budget_limit: float = 1.00
    records: tuple[CostRecord, ...] = ()

    def add(self, record: CostRecord) -> "CostTracker":
        """返回添加了新记录的新跟踪器 (绝不修改自身状态)。"""
        return CostTracker(
            budget_limit=self.budget_limit,
            records=(*self.records, record),
        )

    @property
    def total_cost(self) -> float:
        return sum(r.cost_usd for r in self.records)

    @property
    def over_budget(self) -> bool:
        return self.total_cost > self.budget_limit
```

### 3. 精细化重试逻辑 (Narrow Retry Logic)

仅在瞬时错误 (Transient Errors) 时重试。对身份验证或错误请求执行快速失败 (Fail Fast)。

```python
from anthropic import (
    APIConnectionError,
    InternalServerError,
    RateLimitError,
)

_RETRYABLE_ERRORS = (APIConnectionError, RateLimitError, InternalServerError)
_MAX_RETRIES = 3

def call_with_retry(func, *, max_retries: int = _MAX_RETRIES):
    """仅在瞬时错误时重试，其他错误立即报错。"""
    for attempt in range(max_retries):
        try:
            return func()
        except _RETRYABLE_ERRORS:
            if attempt == max_retries - 1:
                raise
            time.sleep(2 ** attempt)  # 指数退避 (Exponential backoff)
    # AuthenticationError, BadRequestError 等 -> 立即抛出异常
```

### 4. 提示词缓存 (Prompt Caching)

缓存较长的系统提示词 (System Prompts)，避免在每次请求时重复发送。

```python
messages = [
    {
        "role": "user",
        "content": [
            {
                "type": "text",
                "text": system_prompt,
                "cache_control": {"type": "ephemeral"},  # 缓存此内容
            },
            {
                "type": "text",
                "text": user_input,  # 变量部分
            },
        ],
    }
]
```

## 组合使用

在单个流水线函数中组合所有四项技术：

```python
def process(text: str, config: Config, tracker: CostTracker) -> tuple[Result, CostTracker]:
    # 1. 路由模型
    model = select_model(len(text), estimated_items, config.force_model)

    # 2. 检查预算
    if tracker.over_budget:
        raise BudgetExceededError(tracker.total_cost, tracker.budget_limit)

    # 3. 带重试与缓存的调用
    response = call_with_retry(lambda: client.messages.create(
        model=model,
        messages=build_cached_messages(system_prompt, text),
    ))

    # 4. 跟踪成本 (不可变模式)
    record = CostRecord(model=model, input_tokens=..., output_tokens=..., cost_usd=...)
    tracker = tracker.add(record)

    return parse_result(response), tracker
```

## 价格参考 (2025-2026)

| 模型 | 输入 ($/1M tokens) | 输出 ($/1M tokens) | 相对成本 |
|-------|---------------------|----------------------|---------------|
| Haiku 4.5 | $0.80 | $4.00 | 1x |
| Sonnet 4.6 | $3.00 | $15.00 | ~4x |
| Opus 4.5 | $15.00 | $75.00 | ~19x |

## 最佳实践

- **从最便宜的模型开始**，仅在达到复杂度阈值时路由到昂贵模型。
- **在批量处理前设置明确的预算限制**——宁愿提前失败也不要超支。
- **记录模型选择决策**，以便根据真实数据调整阈值。
- **为超过 1024 tokens 的系统提示词使用提示词缓存**——既能节省成本又能降低延迟。
- **绝不在身份验证或校验错误时重试**——仅重试瞬时故障（网络、频率限制、服务器错误）。

## 应避免的反模式 (Anti-Patterns)

- 不分复杂度，对所有请求都使用最昂贵的模型。
- 对所有错误进行重试（在永久性失败上浪费预算）。
- 修改成本跟踪状态（增加调试和审计难度）。
- 在整个代码库中硬编码模型名称（应使用常量或配置）。
- 忽视对重复系统提示词的提示词缓存。

## 使用场景

- 任何调用 Claude、OpenAI 或类似 LLM API 的应用。
- 成本累积迅速的批量处理流水线。
- 需要智能路由的多模型架构。
- 需要预算安全护栏 (Guardrails) 的生产系统。
