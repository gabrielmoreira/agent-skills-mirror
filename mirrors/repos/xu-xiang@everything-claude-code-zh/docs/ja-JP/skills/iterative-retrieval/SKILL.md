---
name: iterative-retrieval
description: 为了解决子智能体（Sub-agent）的上下文问题，逐步优化上下文获取的模式
---

# 反复检索模式 (Iterative Retrieval Pattern)

解决多智能体工作流（Multi-agent Workflow）中的“上下文问题”。子智能体在开始工作之前，通常不知道需要哪些上下文。

## 问题

子智能体（Sub-agent）在启动时上下文有限。它们通常不知道：
- 哪些文件包含相关的代码
- 代码库中存在哪些模式（Patterns）
- 项目使用什么术语

标准方法往往会失败：
- **发送全部**：超出上下文限制（Context Limit）
- **什么都不发**：智能体缺乏关键信息
- **猜测所需内容**：经常出错

## 解决方案：反复检索

分为 4 个阶段的循环，逐步优化上下文：

```
┌─────────────────────────────────────────────┐
│                                             │
│   ┌──────────┐      ┌──────────┐            │
│   │ DISPATCH │─────▶│ EVALUATE │            │
│   └──────────┘      └──────────┘            │
│        ▲                  │                 │
│        │                  ▼                 │
│   ┌──────────┐      ┌──────────┐            │
│   │   LOOP   │◀─────│  REFINE  │            │
│   └──────────┘      └──────────┘            │
│                                             │
│        最大 3 个循环，之后继续执行             │
└─────────────────────────────────────────────┘
```

### 阶段 1: 派发 (DISPATCH)

收集候选文件的初始宽泛查询：

```javascript
// 从高层意图开始
const initialQuery = {
  patterns: ['src/**/*.ts', 'lib/**/*.ts'],
  keywords: ['authentication', 'user', 'session'],
  excludes: ['*.test.ts', '*.spec.ts']
};

// 派发给检索智能体
const candidates = await retrieveFiles(initialQuery);
```

### 阶段 2: 评估 (EVALUATE)

评估获取内容的关联性（Relevance）：

```javascript
function evaluateRelevance(files, task) {
  return files.map(file => ({
    path: file.path,
    relevance: scoreRelevance(file.content, task),
    reason: explainRelevance(file.content, task),
    missingContext: identifyGaps(file.content, task)
  }));
}
```

评分标准：
- **高 (0.8-1.0)**：直接实现目标功能
- **中 (0.5-0.7)**：包含相关的模式或类型
- **低 (0.2-0.4)**：间接相关
- **无 (0-0.2)**：不相关，排除

### 阶段 3: 优化 (REFINE)

根据评估更新检索标准：

```javascript
function refineQuery(evaluation, previousQuery) {
  return {
    // 添加在高关联性文件中发现的新模式
    patterns: [...previousQuery.patterns, ...extractPatterns(evaluation)],

    // 添加在代码库中发现的术语
    keywords: [...previousQuery.keywords, ...extractKeywords(evaluation)],

    // 排除已确认的无关路径
    excludes: [...previousQuery.excludes, ...evaluation
      .filter(e => e.relevance < 0.2)
      .map(e => e.path)
    ],

    // 针对特定的缺口 (Gaps)
    focusAreas: evaluation
      .flatMap(e => e.missingContext)
      .filter(unique)
  };
}
```

### 阶段 4: 循环 (LOOP)

使用优化后的标准重复执行（最多 3 个循环）：

```javascript
async function iterativeRetrieve(task, maxCycles = 3) {
  let query = createInitialQuery(task);
  let bestContext = [];

  for (let cycle = 0; cycle < maxCycles; cycle++) {
    const candidates = await retrieveFiles(query);
    const evaluation = evaluateRelevance(candidates, task);

    // 检查是否有足够的上下文
    const highRelevance = evaluation.filter(e => e.relevance >= 0.7);
    if (highRelevance.length >= 3 && !hasCriticalGaps(evaluation)) {
      return highRelevance;
    }

    // 优化并继续
    query = refineQuery(evaluation, query);
    bestContext = mergeContext(bestContext, highRelevance);
  }

  return bestContext;
}
```

## 实践案例

### 案例 1：Bug 修复上下文

```
任务："修复认证令牌过期 Bug"

循环 1:
  DISPATCH: 在 src/** 中搜索 "token"、"auth"、"expiry"
  EVALUATE: 发现 auth.ts(0.9)、tokens.ts(0.8)、user.ts(0.3)
  REFINE: 添加 "refresh"、"jwt" 关键词；排除 user.ts

循环 2:
  DISPATCH: 使用优化后的术语搜索
  EVALUATE: 发现 session-manager.ts(0.95)、jwt-utils.ts(0.85)
  REFINE: 已获得足够上下文（2 个极高关联性文件）

结果: auth.ts, tokens.ts, session-manager.ts, jwt-utils.ts
```

### 案例 2：功能实现

```
任务："在 API 端点添加速率限制"

循环 1:
  DISPATCH: 在 routes/** 中搜索 "rate"、"limit"、"api"
  EVALUATE: 未匹配 - 代码库使用的是 "throttle" 术语
  REFINE: 添加 "throttle"、"middleware" 关键词

循环 2:
  DISPATCH: 使用优化后的术语搜索
  EVALUATE: 发现 throttle.ts(0.9)、middleware/index.ts(0.7)
  REFINE: 需要路由器模式（Router Pattern）

循环 3:
  DISPATCH: 搜索 "router"、"express" 模式
  EVALUATE: 发现 router-setup.ts(0.8)
  REFINE: 已获得足够上下文

结果: throttle.ts, middleware/index.ts, router-setup.ts
```

## 与智能体集成

在智能体提示词（Prompt）中使用：

```markdown
在获取此任务的上下文时：
1. 从宽泛的关键词搜索开始
2. 评估每个文件的关联性（0-1 刻度）
3. 识别仍缺失的上下文
4. 优化检索标准并重复（最多 3 个循环）
5. 返回关联性在 0.7 以上的文件
```

## 最佳实践

1. **宽进严出** - 初始查询不要过于具体。
2. **学习代码库术语** - 第一个循环通常能揭示项目的命名规范。
3. **追踪缺失内容** - 明确的缺口（Gaps）识别能有效驱动检索优化。
4. **“足够好”即可停止** - 3 个高关联性文件通常优于 10 个平庸文件。
5. **果断排除** - 低关联性文件通常不会在后续循环中变得相关。

## 相关项目

- [The Longform Guide](https://x.com/affaanmustafa/status/2014040193557471352) - 子智能体编排（Sub-agent Orchestration）章节
- `continuous-learning` 技能 - 用于随时间改进的模式
- `~/.claude/agents/` 中的智能体定义
