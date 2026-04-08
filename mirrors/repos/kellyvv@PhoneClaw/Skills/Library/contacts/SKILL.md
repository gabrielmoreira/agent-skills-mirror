---
name: Contacts
name-zh: 通讯录
description: '查询、创建、更新或删除联系人。当用户要查电话、看联系方式、存号码、补充联系人信息或删除联系人时使用。'
version: "1.1.0"
icon: person.crop.circle
disabled: false
type: device

triggers:
  - 联系人
  - 通讯录
  - 查电话
  - 联系电话
  - 存号码
  - 联系方式
  - 删除联系人

allowed-tools:
  - contacts-search
  - contacts-upsert
  - contacts-delete

examples:
  - query: "把王总电话 13812345678 添加到联系人"
    scenario: "新建或更新联系人"
  - query: "检查下联系人张晓霞的电话多少"
    scenario: "查询联系人电话"
  - query: "把王总从联系人中删除"
    scenario: "删除联系人"
---

# 联系人查询与维护

你负责帮助用户查询、创建、更新或删除通讯录联系人。

## 可用工具

- **contacts-search**: 查询联系人
  - `query`: 关键词，可用于模糊搜索
  - `name`: 联系人姓名
  - `phone`: 手机号
  - `email`: 邮箱
  - `identifier`: 联系人标识
- **contacts-upsert**: 创建或更新联系人
  - `name`: 必填，联系人姓名
  - `phone`: 可选，手机号；如果提供，会优先按手机号查重
  - `company`: 可选，公司
  - `email`: 可选，邮箱
  - `notes`: 可选，备注
- **contacts-delete**: 删除联系人
  - `query`: 关键词，可用于模糊搜索
  - `name`: 联系人姓名
  - `phone`: 手机号
  - `email`: 邮箱
  - `identifier`: 联系人标识

## 执行流程

1. 如果用户在查询电话、邮箱、联系方式，优先调用 `contacts-search`
2. 如果用户在删除、移除、删掉联系人，调用 `contacts-delete`
3. 如果用户在保存、添加或更新联系人，调用 `contacts-upsert`
4. 查询或删除时优先提取 `name`，提取不到再用 `query`
5. 保存或更新时提取姓名、手机号、公司、邮箱、备注
6. 如果缺少保存联系人所需的 `name`，先简短追问
7. 工具成功后，直接用中文给出简洁结果

## 多轮澄清处理

### 找到多个匹配时

调用 `contacts-search` 或 `contacts-delete` 后，如果工具结果显示有多个候选（matches > 1），不要直接报错或乱选一个。按以下格式问用户：

> 找到多个 [name]：
> (1) [phone1] · [extra info]
> (2) [phone2] · [extra info]
>
> 要操作哪一个？回复编号、电话号码后几位，或"全部"。

把这些候选信息**保留**在你的回答里，下一轮用户回应时你需要参考。

### 用户回答澄清后（关键）

如果上一轮你刚问过用户"要操作哪一个"，**当前用户消息就是答案**。不要再问一次，按答案语义解析后**重新调用同一个工具**：

| 用户说什么 | 含义 | 怎么调 |
|---|---|---|
| 完整电话 `15212345678` | 精确指定 | 用 `phone` 参数加完整号码 |
| 尾号 `5678` / "尾号 5678" | 模糊定位 | 用 `query` 参数加尾号 |
| 编号 `1` / `(1)` / "第一个" | 选候选列表第 N 个 | 取上一轮列出的第 N 个的电话作为 `phone` |
| "全部" / "都删" / "两个都" | 操作所有候选 | 对每个候选**依次**调用工具，每次用 `phone` 精确定位一个 |
| 名字 + 公司 / 备注 | 用区分性信息 | 加 `name` + `notes` 等参数 |

调用例（用户回答 "152123458"）：
<tool_call>
{"name": "contacts-delete", "arguments": {"name": "张总", "phone": "152123458"}}
</tool_call>

### 用户取消时

如果用户在多轮澄清过程中表达了**放弃意图**——例如说"算了"、"不删了"、"取消"、"停"、"nevermind"，或任何自然语言里表示不想继续的意思——**直接给一句简短确认**（如"好的，已取消"），**不要 emit 任何 tool_call**。

判断"是否在表达放弃"由你自己理解上下文，不要依赖任何固定关键词列表。模型有自然语言理解能力，请用它。

### 不要捏造执行结果

如果你**没有真正调用 tool**，**绝对不要**说"已经删除"、"已添加"、"已更新"。
- 要么 emit 一个真实的 `<tool_call>`
- 要么如实告诉用户你需要更多信息或操作已取消
- **不允许**只输出"已完成"这种文本而不调工具

## 调用格式

<tool_call>
{"name": "contacts-search", "arguments": {"name": "张晓霞"}}
</tool_call>

<tool_call>
{"name": "contacts-upsert", "arguments": {"name": "王总", "phone": "13812345678", "company": "字节"}}
</tool_call>

<tool_call>
{"name": "contacts-delete", "arguments": {"name": "王总"}}
</tool_call>
