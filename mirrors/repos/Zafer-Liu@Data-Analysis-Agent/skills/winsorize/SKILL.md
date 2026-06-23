---
name: winsorize
description: 对极端值执行缩尾处理并验证影响
icon: ✂️
allowedTools: [get_schema, profile_data, clean_data, query_data]
---
# 缩尾处理

识别目标数值字段和异常分布，说明上下界规则后再缩尾。不得默认覆盖原始数据；比较处理前后的分布、均值和关键指标，并记录边界与受影响行数。
