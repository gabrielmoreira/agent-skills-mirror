---
name: gru
description: 使用 GRU 对足量时间序列进行预测
icon: 🧠
allowedTools: [get_schema, query_data, run_analysis, generate_chart]
---
# GRU 预测

仅在样本量和序列长度足够时使用。确认窗口、特征和预测期，严格按时间划分训练验证，避免泄漏，报告基线对比、误差和不确定性；小数据优先建议传统时序模型。
