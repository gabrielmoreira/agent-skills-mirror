---
description: "扩展自通用规则的 Python 模式"
globs: ["**/*.py", "**/*.pyi"]
alwaysApply: false
---
# Python 模式（Python Patterns）

> 本文件以 Python 特定内容扩展了通用模式（common patterns）规则。

## 协议 / 鸭子类型（Protocol / Duck Typing）

```python
from typing import Protocol

class Repository(Protocol):
    def find_by_id(self, id: str) -> dict | None: ...
    def save(self, entity: dict) -> dict: ...
```

## 将数据类（Dataclasses）作为数据传输对象（DTOs）

```python
from dataclasses import dataclass

@dataclass
class CreateUserRequest:
    name: str
    email: str
    age: int | None = None
```

## 上下文管理器（Context Managers）与生成器（Generators）

- 使用上下文管理器（`with` 语句）进行资源管理
- 使用生成器（Generators）进行延迟求值和内存高效的迭代

## 参考（Reference）

请参阅技能：`python-patterns` 以获取包括装饰器（decorators）、并发（concurrency）和包组织（package organization）在内的全面模式。
