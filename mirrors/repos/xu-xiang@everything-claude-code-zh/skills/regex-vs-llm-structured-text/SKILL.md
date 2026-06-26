---
name: regex-vs-llm-structured-text
description: 在解析结构化文本时，用于在正则表达式（Regex）和大型语言模型（LLM）之间进行选择的决策框架——优先使用正则表达式，仅针对低置信度的边界情况引入 LLM。
origin: ECC
---

# 结构化文本解析：正则表达式（Regex）与大语言模型（LLM）的抉择

这是一个用于解析结构化文本（测验、表单、发票、文档）的实用决策框架。核心见解是：正则表达式（Regex）能以极低的成本确定性地处理 95-98% 的情况。应将昂贵的 LLM 调用保留给剩余的边界情况（Edge Cases）。

## 何时激活（When to Activate）

- 解析具有重复模式的结构化文本（问题、表单、表格等）
- 在文本提取任务中权衡使用正则表达式还是 LLM
- 构建结合这两种方法的混合流水线（Hybrid Pipelines）
- 在文本处理中优化成本与准确性的平衡

## 决策框架（Decision Framework）

```
文本格式是否一致且重复？
├── 是 (>90% 遵循某种模式) → 从正则表达式（Regex）开始
│   ├── 正则表达式处理了 95%+ → 完成，无需 LLM
│   └── 正则表达式处理率 <95% → 仅针对边界情况添加 LLM
└── 否 (非格式化，高度多变) → 直接使用 LLM
```

## 架构模式（Architecture Pattern）

```
源文本（Source Text）
    │
    ▼
[正则解析器 (Regex Parser)] ─── 提取结构 (95-98% 准确率)
    │
    ▼
[文本清洗器 (Text Cleaner)] ─── 去除噪声 (标记、页码、人工痕迹)
    │
    ▼
[置信度评分器 (Confidence Scorer)] ─── 标记低置信度提取结果
    │
    ├── 高置信度 (≥0.95) → 直接输出
    │
    └── 低置信度 (<0.95) → [LLM 验证器 (LLM Validator)] → 输出
```

## 实现参考（Implementation）

### 1. 正则解析器 (处理绝大多数情况)

```python
import re
from dataclasses import dataclass

@dataclass(frozen=True)
class ParsedItem:
    id: str
    text: str
    choices: tuple[str, ...]
    answer: str
    confidence: float = 1.0

def parse_structured_text(content: str) -> list[ParsedItem]:
    """使用正则表达式模式解析结构化文本。"""
    pattern = re.compile(
        r"(?P<id>\d+)\.\s*(?P<text>.+?)\n"
        r"(?P<choices>(?:[A-D]\..+?\n)+)"
        r"Answer:\s*(?P<answer>[A-D])",
        re.MULTILINE | re.DOTALL,
    )
    items = []
    for match in pattern.finditer(content):
        choices = tuple(
            c.strip() for c in re.findall(r"[A-D]\.\s*(.+)", match.group("choices"))
        )
        items.append(ParsedItem(
            id=match.group("id"),
            text=match.group("text").strip(),
            choices=choices,
            answer=match.group("answer"),
        ))
    return items
```

### 2. 置信度评分 (Confidence Scoring)

标记可能需要 LLM 审查的项目：

```python
@dataclass(frozen=True)
class ConfidenceFlag:
    item_id: str
    score: float
    reasons: tuple[str, ...]

def score_confidence(item: ParsedItem) -> ConfidenceFlag:
    """对提取置信度进行评分并标记问题。"""
    reasons = []
    score = 1.0

    if len(item.choices) < 3:
        reasons.append("few_choices") # 选项过少
        score -= 0.3

    if not item.answer:
        reasons.append("missing_answer") # 缺失答案
        score -= 0.5

    if len(item.text) < 10:
        reasons.append("short_text") # 文本过短
        score -= 0.2

    return ConfidenceFlag(
        item_id=item.id,
        score=max(0.0, score),
        reasons=tuple(reasons),
    )

def identify_low_confidence(
    items: list[ParsedItem],
    threshold: float = 0.95,
) -> list[ConfidenceFlag]:
    """返回低于置信度阈值的项目。"""
    flags = [score_confidence(item) for item in items]
    return [f for f in flags if f.score < threshold]
```

### 3. LLM 验证器 (仅处理边界情况)

```python
def validate_with_llm(
    item: ParsedItem,
    original_text: str,
    client,
) -> ParsedItem:
    """使用 LLM 修复低置信度的提取结果。"""
    response = client.messages.create(
        model="claude-haiku-4-5-20251001",  # 使用最便宜的模型进行验证
        max_tokens=500,
        messages=[{
            "role": "user",
            "content": (
                f"Extract the question, choices, and answer from this text.\n\n"
                f"Text: {original_text}\n\n"
                f"Current extraction: {item}\n\n"
                f"Return corrected JSON if needed, or 'CORRECT' if accurate."
            ),
        }],
    )
    # 解析 LLM 响应并返回修正后的项目...
    return corrected_item
```

### 4. 混合流水线 (Hybrid Pipeline)

```python
def process_document(
    content: str,
    *,
    llm_client=None,
    confidence_threshold: float = 0.95,
) -> list[ParsedItem]:
    """完整流水线：正则提取 -> 置信度检查 -> 针对边界情况调用 LLM。"""
    # 步骤 1: 正则提取 (处理 95-98% 的情况)
    items = parse_structured_text(content)

    # 步骤 2: 置信度评分
    low_confidence = identify_low_confidence(items, confidence_threshold)

    if not low_confidence or llm_client is None:
        return items

    # 步骤 3: LLM 验证 (仅针对被标记的项目)
    low_conf_ids = {f.item_id for f in low_confidence}
    result = []
    for item in items:
        if item.id in low_conf_ids:
            result.append(validate_with_llm(item, content, llm_client))
        else:
            result.append(item)

    return result
```

## 真实世界指标 (Real-World Metrics)

来自一个生产环境的测验解析流水线（410 个项目）：

| 指标 (Metric) | 数值 (Value) |
|--------|-------|
| 正则表达式成功率 | 98.0% |
| 低置信度项目数 | 8 (2.0%) |
| 需要的 LLM 调用次数 | ~5 |
| 相比全 LLM 方案节省的成本 | ~95% |
| 测试覆盖率 | 93% |

## 最佳实践 (Best Practices)

- **从正则表达式开始** —— 即使是不完美的正则也能为你提供改进的基准。
- **使用置信度评分** —— 以编程方式识别哪些内容需要 LLM 协助。
- **使用最便宜的 LLM 进行验证** —— Haiku 级别的模型通常已经足够。
- **切勿修改（Mutate）原始解析项** —— 在清洗/验证步骤中应返回新的实例。
- **测试驱动开发（TDD）非常适用** —— 先为已知模式编写测试，然后再处理边界情况。
- **记录指标** —— 记录正则表达式成功率、LLM 调用次数等，以跟踪流水线的健康状况。

## 应避免的反模式 (Anti-Patterns to Avoid)

- 当正则表达式能处理 95% 以上情况时，仍将所有文本发送给 LLM（既昂贵又缓慢）。
- 对非格式化、高度多变的文本使用正则表达式（在这种情况下 LLM 表现更好）。
- 跳过置信度评分并寄希望于正则表达式“刚好能用”。
- 在清洗/验证步骤中直接修改已解析的对象。
- 不测试边界情况（格式错误的输入、缺失字段、编码问题等）。

## 适用场景 (When to Use)

- 测验/考试题目解析
- 表单数据提取
- 发票/收据处理
- 文档结构解析（标题、章节、表格）
- 任何具有重复模式且对成本敏感的结构化文本处理
