---
description: "扩展自通用规则的 Python 编码风格"
globs: ["**/*.py", "**/*.pyi"]
alwaysApply: false
---
# Python 编码风格

> 本文件在通用编码风格规则的基础上扩展了 Python 特有的内容。

## 标准 (Standards)

- 遵循 **PEP 8** 规范
- 在所有函数签名中使用**类型注解 (type annotations)**

## 不变性 (Immutability)

优先使用不可变数据结构：

```python
from dataclasses import dataclass

@dataclass(frozen=True)
class User:
    name: str
    email: str

from typing import NamedTuple

class Point(NamedTuple):
    x: float
    y: float
```

## 格式化 (Formatting)

- 使用 **black** 进行代码格式化
- 使用 **isort** 进行导入 (import) 排序
- 使用 **ruff** 进行代码检查 (linting)

## 参考 (Reference)

有关完整的 Python 惯用法 (idioms) 和模式 (patterns)，请参阅技能 (Skill)：`python-patterns`。
