---
description: "Python 安全规范，扩展通用安全规则 (Python security extending common rules)"
globs: ["**/*.py", "**/*.pyi"]
alwaysApply: false
---
# Python 安全规范 (Python Security)

> 本文件在通用安全规则的基础上，增加了针对 Python 的特定安全内容。

## 密钥管理 (Secret Management)

```python
import os
from dotenv import load_dotenv

load_dotenv()

# 如果缺失则抛出 KeyError
api_key = os.environ["OPENAI_API_KEY"]
```

## 安全扫描 (Security Scanning)

- 使用 **bandit** 进行静态安全分析：
  ```bash
  bandit -r src/
  ```

## 参考 (Reference)

如果适用，请参阅技能（Skill）：`django-security` 以获取 Django 特定的安全指南。
