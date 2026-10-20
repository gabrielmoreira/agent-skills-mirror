---
name: implement
description: "基于 spec 或 ticket 集合实现一段工作。"
disable-model-invocation: true
---

实现用户在 spec 或 tickets 中描述的工作。

尽可能在预先约定好的 seams 上使用 `/tdd`。

定期运行 typechecking，定期运行单个测试文件，并在最后运行完整测试套件。

完成后，使用 `/code-review` 审查这次工作。

把工作提交到当前 branch。
