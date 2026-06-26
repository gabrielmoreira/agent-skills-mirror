---
name: swift-actor-persistence
description: Swift 中使用 actor 实现的线程安全数据持久化 —— 结合内存缓存与文件存储，从设计上消除数据竞争。
origin: ECC
---

# 使用 Swift Actors 实现线程安全持久化 (Swift Actors for Thread-Safe Persistence)

使用 Swift actor 构建线程安全数据持久化层的模式。该模式结合了内存缓存（In-memory caching）与基于文件的存储，利用 actor 模型（Actor model）在编译时消除数据竞争（Data races）。

## 何时启用

- 在 Swift 5.5+ 中构建数据持久化层
- 需要对共享可变状态（Shared mutable state）进行线程安全访问
- 希望消除手动同步操作（如 locks、DispatchQueues）
- 构建具有本地存储的离线优先（Offline-first）应用

## 核心模式 (Core Pattern)

### 基于 Actor 的仓库模式 (Actor-Based Repository)

Actor 模型保证了序列化访问（Serialized access）—— 由编译器强制执行，确保不会出现数据竞争。

```swift
public actor LocalRepository<T: Codable & Identifiable> where T.ID == String {
    private var cache: [String: T] = [:]
    private let fileURL: URL

    public init(directory: URL = .documentsDirectory, filename: String = "data.json") {
        self.fileURL = directory.appendingPathComponent(filename)
        // 在 init 期间同步加载（此时 actor 隔离尚未生效）
        self.cache = Self.loadSynchronously(from: fileURL)
    }

    // MARK: - 公共 API

    public func save(_ item: T) throws {
        cache[item.id] = item
        try persistToFile()
    }

    public func delete(_ id: String) throws {
        cache[id] = nil
        try persistToFile()
    }

    public func find(by id: String) -> T? {
        cache[id]
    }

    public func loadAll() -> [T] {
        Array(cache.values)
    }

    // MARK: - 私有方法

    private func persistToFile() throws {
        let data = try JSONEncoder().encode(Array(cache.values))
        try data.write(to: fileURL, options: .atomic)
    }

    private static func loadSynchronously(from url: URL) -> [String: T] {
        guard let data = try? Data(contentsOf: url),
              let items = try? JSONDecoder().decode([T].self, from: data) else {
            return [:]
        }
        return Dictionary(uniqueKeysWithValues: items.map { ($0.id, $0) })
    }
}
```

### 使用方法 (Usage)

由于 actor 隔离（Actor isolation），所有调用都会自动变为异步：

```swift
let repository = LocalRepository<Question>()

// 读取 —— 从内存缓存中进行快速 O(1) 查找
let question = await repository.find(by: "q-001")
let allQuestions = await repository.loadAll()

// 写入 —— 原子化地更新缓存并持久化到文件
try await repository.save(newQuestion)
try await repository.delete("q-001")
```

### 结合 @Observable ViewModel

```swift
@Observable
final class QuestionListViewModel {
    private(set) var questions: [Question] = []
    private let repository: LocalRepository<Question>

    init(repository: LocalRepository<Question> = LocalRepository()) {
        self.repository = repository
    }

    func load() async {
        questions = await repository.loadAll()
    }

    func add(_ question: Question) async throws {
        try await repository.save(question)
        questions = await repository.loadAll()
    }
}
```

## 关键设计决策 (Key Design Decisions)

| 决策 | 理由 |
|----------|-----------|
| 使用 Actor (而非 class + lock) | 编译器强制执行线程安全，无需手动同步 |
| 内存缓存 + 文件持久化 | 缓存提供快速读取，磁盘提供持久化写入 |
| 在 init 中同步加载 | 避免异步初始化的复杂性，且对本地文件影响较小 |
| 以 ID 为键的字典 (Dictionary) | 通过标识符进行 O(1) 查找 |
| 泛型支持 `Codable & Identifiable` | 可在任何模型类型中复用 |
| 原子化文件写入 (`.atomic`) | 防止崩溃时出现部分写入导致的数据损坏 |

## 最佳实践 (Best Practices)

- **对所有跨 actor 边界的数据使用 `Sendable` 类型**
- **保持 actor 的公共 API 最小化** —— 仅暴露业务领域操作，不暴露持久化细节
- **使用 `.atomic` 写入** 以防止应用在写入过程中崩溃导致数据损坏
- **在 `init` 中同步加载** —— 异步初始化会增加复杂性，而对本地文件的同步读取收益更高
- **结合 `@Observable`** ViewModel 实现响应式 UI 更新

## 避免的反模式 (Anti-Patterns to Avoid)

- 在新的 Swift 并发代码中使用 `DispatchQueue` 或 `NSLock` 而非 actor
- 将内部缓存字典直接暴露给外部调用者
- 在没有验证的情况下让文件 URL 变为可配置
- 遗忘所有 actor 方法调用都是 `await` 的 —— 调用者必须处理异步上下文
- 使用 `nonisolated` 绕过 actor 隔离（这违背了使用 actor 的初衷）

## 适用场景 (When to Use)

- iOS/macOS 应用中的本地数据存储（用户数据、设置、缓存内容）
- 稍后与服务器同步的离线优先（Offline-first）架构
- 任何被应用多个部分并发访问的共享可变状态
- 使用现代 Swift 并发（Swift Concurrency）替换旧有的基于 `DispatchQueue` 的线程安全方案
