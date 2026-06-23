---
name: sql
description: 使用 SQL 安全查询当前已选择的数据表
icon: 🗄️
allowedTools: [get_schema, get_table_detail, query_data]
---
# SQL 查询

先读取已授权分析表的 schema，确认真实表名与字段名，再编写只读 SQL。优先聚合并限制返回行数，不猜测字段；SQL 数据源只能查询用户已选择的分析表。解释查询口径并总结结果。
