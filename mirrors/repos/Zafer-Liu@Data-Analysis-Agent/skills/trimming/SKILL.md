---
name: trimming
description: 对异常样本执行截尾处理并评估偏差
icon: 🔪
allowedTools: [get_schema, profile_data, clean_data, query_data]
---
# 截尾处理

先定义异常判据和业务合理范围，量化拟删除样本及其特征。仅在用户意图明确时执行，保留原始数据和可追溯输出；处理后报告样本损失及潜在选择偏差。
