---
name: git-commit
description: |
  当用户要求提交代码、写 commit message、或提到 git commit 时使用。
  自动分析 git diff，生成规范的中文 commit message。
---

# Git Commit

## 执行流程

### 第一步：查看变更

```bash
git status
git diff --cached   # 已暂存的变更
git diff            # 未暂存的变更
```

如果没有已暂存的变更，提示用户先 `git add`。

### 第二步：分析变更，生成 commit message

根据变更内容，判断类型并生成 message。

**格式**：

```
[类型] 简洁描述（不超过 50 字）
```

**类型标签**：

| 标签 | 含义 | 示例 |
|------|------|------|
| `[新功能]` | 新增功能 | `[新功能] 图片缓存模块` |
| `[修复]` | Bug 修复 | `[修复] 登录页崩溃问题` |
| `[优化]` | 迭代优化、重构、性能提升 | `[优化] 网络请求超时处理逻辑` |
| `[文档]` | 文档变更 | `[文档] 补充 Token 篇的图片说明` |
| `[配置]` | 构建、依赖、配置变更 | `[配置] 更新 SPM 依赖版本` |

**描述要求**：

- 用中文
- 说清楚「改了什么」，而不是「做了什么操作」
- 不超过 50 字
- 不要以句号结尾

**正反示例**：

```
✅ [新功能] 用户登录页，支持账号密码和验证码两种方式
✅ [修复] 列表页下拉刷新后数据重复
✅ [优化] 将网络请求回调改为 async/await

❌ [新功能] 添加了一些代码        ← 太模糊
❌ [修复] fix bug                 ← 不是中文，且无具体信息
❌ [优化] 修改了 NetworkService   ← 只说了改了哪个文件，没说改了什么
```

**多个变更时**：如果本次提交包含多项不同类型的变更，取最主要的那个作为类型。如果确实涉及多个独立改动，建议拆分成多次提交。

### 第三步：展示并等待确认

将生成的 commit message 展示给用户，格式如下：

```
建议的 commit message：

[类型] 描述

涉及的文件：
- path/to/file1
- path/to/file2

确认提交？
```

等用户确认后再执行 `git commit`。

## 禁止行为

- 不要未经确认直接执行 git commit
- 不要生成英文的 commit message
- 不要把所有改动的文件名罗列到 message 里
- 不要写超过 50 字的描述

## 安装

在你的项目根目录下执行：

```bash
curl -sL https://raw.githubusercontent.com/iAmMccc/ai-essentials/main/install-skill.sh | bash -s git-commit
```

安装后在对话中说「帮我提交」即可触发。
