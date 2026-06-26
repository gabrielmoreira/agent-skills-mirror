---
name: foundation-models-on-device
description: Apple FoundationModels 框架，用于设备端大语言模型（LLM）—— iOS 26+ 中的文本生成、配合 @Generable 的引导式生成、工具调用以及快照流式传输。
---

# FoundationModels：设备端大语言模型 (iOS 26)

使用 FoundationModels 框架将 Apple 的设备端语言模型集成到应用中的模式。涵盖文本生成、使用 `@Generable` 的结构化输出、自定义工具调用以及快照流式传输 —— 全部在设备端运行，以支持隐私保护和离线使用。

## 何时激活

- 使用 Apple Intelligence 在设备端构建 AI 驱动的功能
- 在不依赖云端的情况下生成或总结文本
- 从自然语言输入中提取结构化数据
- 为特定领域的 AI 操作实现自定义工具调用
- 流式传输结构化响应以实现实时 UI 更新
- 需要隐私保护的 AI（数据不离开设备）

## 核心模式 —— 可用性检查

在创建会话（Session）之前，请务必检查模型的可用性：

```swift
struct GenerativeView: View {
    private var model = SystemLanguageModel.default

    var body: some View {
        switch model.availability {
        case .available:
            ContentView()
        case .unavailable(.deviceNotEligible):
            Text("设备不符合 Apple Intelligence 的使用条件")
        case .unavailable(.appleIntelligenceNotEnabled):
            Text("请在设置中启用 Apple Intelligence")
        case .unavailable(.modelNotReady):
            Text("模型正在下载或尚未就绪")
        case .unavailable(let other):
            Text("模型不可用：\(other)")
        }
    }
}
```

## 核心模式 —— 基础会话

```swift
// 单轮：每次创建一个新会话
let session = LanguageModelSession()
let response = try await session.respond(to: "去巴黎旅游哪个月份比较好？")
print(response.content)

// 多轮：复用会话以保留对话上下文
let session = LanguageModelSession(instructions: """
    你是一个烹饪助手。
    请根据食材提供食谱建议。
    建议要保持简短且实用。
    """)

let first = try await session.respond(to: "我有鸡肉和米饭")
let followUp = try await session.respond(to: "那素食选择呢？")
```

提示词指令（Instructions）的关键点：
- 定义模型的角色（“你是一个导师”）
- 指定要做什么（“帮助提取日历事件”）
- 设置风格偏好（“尽可能简短地回答”）
- 添加安全措施（“对于危险请求，请回答‘我无法提供帮助’”）

## 核心模式 —— 使用 @Generable 的引导式生成

生成结构化的 Swift 类型，而不是原始字符串：

### 1. 定义一个 Generable 类型

```swift
@Generable(description: "关于猫的基本个人资料信息")
struct CatProfile {
    var name: String

    @Guide(description: "猫的年龄", .range(0...20))
    var age: Int

    @Guide(description: "关于猫性格的一句话简介")
    var profile: String
}
```

### 2. 请求结构化输出

```swift
let response = try await session.respond(
    to: "生成一只可爱的待领养小猫",
    generating: CatProfile.self
)

// 直接访问结构化字段
print("名字: \(response.content.name)")
print("年龄: \(response.content.age)")
print("简介: \(response.content.profile)")
```

### 支持的 @Guide 约束

- `.range(0...20)` —— 数字范围
- `.count(3)` —— 数组元素计数
- `description:` —— 生成的语义引导

## 核心模式 —— 工具调用

允许模型调用自定义代码以执行特定领域任务：

### 1. 定义一个工具（Tool）

```swift
struct RecipeSearchTool: Tool {
    let name = "recipe_search"
    let description = "搜索匹配给定术语的食谱并返回结果列表。"

    @Generable
    struct Arguments {
        var searchTerm: String
        var numberOfResults: Int
    }

    func call(arguments: Arguments) async throws -> ToolOutput {
        let recipes = await searchRecipes(
            term: arguments.searchTerm,
            limit: arguments.numberOfResults
        )
        return .string(recipes.map { "- \($0.name): \($0.description)" }.joined(separator: "\n"))
    }
}
```

### 2. 创建带有工具的会话

```swift
let session = LanguageModelSession(tools: [RecipeSearchTool()])
let response = try await session.respond(to: "帮我找一些意面食谱")
```

### 3. 处理工具错误

```swift
do {
    let answer = try await session.respond(to: "寻找番茄汤的食谱。")
} catch let error as LanguageModelSession.ToolCallError {
    print(error.tool.name)
    if case .databaseIsEmpty = error.underlyingError as? RecipeSearchToolError {
        // 处理特定的工具错误
    }
}
```

## 核心模式 —— 快照流式传输

使用 `PartiallyGenerated` 类型为实时 UI 流式传输结构化响应：

```swift
@Generable
struct TripIdeas {
    @Guide(description: "未来旅行的想法")
    var ideas: [String]
}

let stream = session.streamResponse(
    to: "有哪些令人兴奋的旅行点子？",
    generating: TripIdeas.self
)

for try await partial in stream {
    // partial: TripIdeas.PartiallyGenerated (所有属性均为 Optional)
    print(partial)
}
```

### SwiftUI 集成

```swift
@State private var partialResult: TripIdeas.PartiallyGenerated?
@State private var errorMessage: String?

var body: some View {
    List {
        ForEach(partialResult?.ideas ?? [], id: \.self) { idea in
            Text(idea)
        }
    }
    .overlay {
        if let errorMessage { Text(errorMessage).foregroundStyle(.red) }
    }
    .task {
        do {
            let stream = session.streamResponse(to: prompt, generating: TripIdeas.self)
            for try await partial in stream {
                partialResult = partial
            }
        } catch {
            errorMessage = error.localizedDescription
        }
    }
}
```

## 关键设计决策

| 决策 | 原理 |
|----------|-----------|
| 设备端执行 | 隐私性 —— 数据不离开设备；支持离线工作 |
| 4,096 Token 限制 | 设备端模型约束；跨会话分块处理大数据 |
| 快照流式传输（而非增量） | 对结构化输出友好；每个快照都是一个完整的局部状态 |
| `@Generable` 宏 | 结构化生成的编译时安全性；自动生成 `PartiallyGenerated` 类型 |
| 每个会话单次请求 | `isResponding` 防止并发请求；如果需要，创建多个会话 |
| `response.content`（而非 `.output`） | 正确的 API —— 始终通过 `.content` 属性访问结果 |

## 最佳实践

- **始终在创建会话前检查 `model.availability`** —— 处理所有不可用的情况
- **使用 `instructions`** 来引导模型行为 —— 它们的优先级高于提示词（Prompts）
- **在发送新请求前检查 `isResponding`** —— 会话每次处理一个请求
- **访问 `response.content`** 获取结果 —— 而非 `.output`
- **将大型输入分成块** —— 4,096 Token 限制适用于指令 + 提示词 + 输出的总和
- **使用 `@Generable`** 进行结构化输出 —— 比解析原始字符串具有更强的保证
- **使用 `GenerationOptions(temperature:)`** 来调整创意程度（越高越有创意）
- **使用 Instruments 进行监控** —— 使用 Xcode Instruments 分析请求性能

## 应避免的反模式

- 在未先检查 `model.availability` 的情况下创建会话
- 发送超过 4,096 Token 上下文窗口的输入
- 尝试在单个会话上进行并发请求
- 使用 `.output` 而非 `.content` 来访问响应数据
- 在 `@Generable` 结构化输出可行时解析原始字符串响应
- 在单个提示词中构建复杂的、多步骤的逻辑 —— 请拆分为多个针对性强的提示词
- 假设模型始终可用 —— 设备资格和设置各不相同

## 何时使用

- 针对隐私敏感型应用的设备端文本生成
- 从用户输入中提取结构化数据（表单、自然语言命令）
- 必须离线工作的 AI 辅助功能
- 逐步显示生成内容的流式 UI
- 通过工具调用（搜索、计算、查找）执行特定领域的 AI 操作
