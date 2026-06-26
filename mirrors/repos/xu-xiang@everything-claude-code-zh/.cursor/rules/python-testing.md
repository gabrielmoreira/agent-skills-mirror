---
description: "扩展通用规则的 Python 测试 (Python testing extending common rules)"
globs: ["**/*.py", "**/*.pyi"]
alwaysApply: false
---
# Python 测试 (Python Testing)

> 本文件通过 Python 特定内容扩展了通用测试规则（Common testing rule）。

## 框架 (Framework)

使用 **pytest** 作为测试框架。

## 覆盖率 (Coverage)

```bash
pytest --cov=src --cov-report=term-missing
```

## 测试组织 (Test Organization)

使用 `pytest.mark` 进行测试分类：

```python
import pytest

@pytest.mark.unit
def test_calculate_total():
    ...

@pytest.mark.integration
def test_database_connection():
    ...
```

## 参考 (Reference)

详见技能（Skill）：`python-testing` 以获取详细的 pytest 模式和固件（Fixtures）。
