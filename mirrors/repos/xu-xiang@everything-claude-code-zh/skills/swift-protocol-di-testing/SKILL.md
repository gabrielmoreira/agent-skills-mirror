---
name: swift-protocol-di-testing
description: 基于协议的依赖注入（Protocol-based Dependency Injection），通过精简的协议和 Swift 测试框架（Swift Testing）来模拟文件系统、网络和外部 API，编写可测试的 Swift 代码。
origin: ECC
---

# 基于 Swift 协议的依赖注入（Testing）

通过将外部依赖（文件系统、网络、iCloud）抽象到精简且功能集中的协议（Protocols）后面，使 Swift 代码变得可测试。这种模式支持无需实际 I/O 即可进行确定性测试（Deterministic Tests）。

## 何时激活

- 编写访问文件系统、网络或外部 API 的 Swift 代码时
- 需要在不触发实际故障的情况下测试错误处理路径时
- 构建需要在不同环境（App、测试、SwiftUI 预览）下运行的模块时
- 使用 Swift 并发（Concurrency，如 Actor、Sendable）设计可测试架构时

## 核心模式

### 1. 定义精简且功能集中的协议

每个协议应仅处理一个特定的外部关注点。

```swift
// 文件系统访问
public protocol FileSystemProviding: Sendable {
    func containerURL(for purpose: Purpose) -> URL?
}

// 文件读写操作
public protocol FileAccessorProviding: Sendable {
    func read(from url: URL) throws -> Data
    func write(_ data: Data, to url: URL) throws
    func fileExists(at url: URL) -> Bool
}

// 书签存储（例如：用于沙盒应用）
public protocol BookmarkStorageProviding: Sendable {
    func saveBookmark(_ data: Data, for key: String) throws
    func loadBookmark(for key: String) throws -> Data?
}
```

### 2. 创建默认（生产环境）实现

```swift
public struct DefaultFileSystemProvider: FileSystemProviding {
    public init() {}

    public func containerURL(for purpose: Purpose) -> URL? {
        FileManager.default.url(forUbiquityContainerIdentifier: nil)
    }
}

public struct DefaultFileAccessor: FileAccessorProviding {
    public init() {}

    public func read(from url: URL) throws -> Data {
        try Data(contentsOf: url)
    }

    public func write(_ data: Data, to url: URL) throws {
        try data.write(to: url, options: .atomic)
    }

    public func fileExists(at url: URL) -> Bool {
        FileManager.default.fileExists(atPath: url.path)
    }
}
```

### 3. 创建用于测试的模拟实现（Mock）

```swift
public final class MockFileAccessor: FileAccessorProviding, @unchecked Sendable {
    public var files: [URL: Data] = [:]
    public var readError: Error?
    public var writeError: Error?

    public init() {}

    public func read(from url: URL) throws -> Data {
        if let error = readError { throw error }
        guard let data = files[url] else {
            throw CocoaError(.fileReadNoSuchFile)
        }
        return data
    }

    public func write(_ data: Data, to url: URL) throws {
        if let error = writeError { throw error }
        files[url] = data
    }

    public func fileExists(at url: URL) -> Bool {
        files[url] != nil
    }
}
```

### 4. 使用默认参数注入依赖

生产代码使用默认值；测试则注入模拟对象（Mocks）。

```swift
public actor SyncManager {
    private let fileSystem: FileSystemProviding
    private let fileAccessor: FileAccessorProviding

    public init(
        fileSystem: FileSystemProviding = DefaultFileSystemProvider(),
        fileAccessor: FileAccessorProviding = DefaultFileAccessor()
    ) {
        self.fileSystem = fileSystem
        self.fileAccessor = fileAccessor
    }

    public func sync() async throws {
        guard let containerURL = fileSystem.containerURL(for: .sync) else {
            throw SyncError.containerNotAvailable
        }
        let data = try fileAccessor.read(
            from: containerURL.appendingPathComponent("data.json")
        )
        // 处理数据...
    }
}
```

### 5. 使用 Swift 测试框架编写测试

```swift
import Testing

@Test("Sync manager handles missing container")
func testMissingContainer() async {
    let mockFileSystem = MockFileSystemProvider(containerURL: nil)
    let manager = SyncManager(fileSystem: mockFileSystem)

    await #expect(throws: SyncError.containerNotAvailable) {
        try await manager.sync()
    }
}

@Test("Sync manager reads data correctly")
func testReadData() async throws {
    let mockFileAccessor = MockFileAccessor()
    mockFileAccessor.files[testURL] = testData

    let manager = SyncManager(fileAccessor: mockFileAccessor)
    let result = try await manager.loadData()

    #expect(result == expectedData)
}

@Test("Sync manager handles read errors gracefully")
func testReadError() async {
    let mockFileAccessor = MockFileAccessor()
    mockFileAccessor.readError = CocoaError(.fileReadCorruptFile)

    let manager = SyncManager(fileAccessor: mockFileAccessor)

    await #expect(throws: SyncError.self) {
        try await manager.sync()
    }
}
```

## 最佳实践

- **单一职责（Single Responsibility）**：每个协议应仅处理一个关注点 —— 不要创建拥有过多方法的“万能协议（God Protocols）”。
- **符合 Sendable 协议**：当协议在 Actor 边界之间使用时，此项为必须。
- **默认参数（Default Parameters）**：允许生产环境代码默认使用真实实现；仅在测试中才需要指定模拟对象（Mocks）。
- **错误模拟（Error Simulation）**：为模拟对象设计可配置的错误属性，以便测试失败路径。
- **仅对边界进行模拟**：模拟外部依赖（文件系统、网络、API），不要对内部类型进行模拟。

## 需避免的反模式（Anti-Patterns）

- 创建一个涵盖所有外部访问的大而全的协议。
- 对没有外部依赖的内部类型进行模拟。
- 使用 `#if DEBUG` 条件编译块而不是正确的依赖注入。
- 在与 Actor 配合使用时忘记让协议符合 `Sendable`。
- 过度工程（Over-engineering）：如果一个类型没有外部依赖，则不需要为其定义协议。

## 何时使用

- 任何涉及文件系统、网络或外部 API 的 Swift 代码。
- 测试在真实环境下难以触发的错误处理路径。
- 构建需要同时在 App、测试和 SwiftUI 预览上下文中运行的模块。
- 使用 Swift 并发（Actor、结构化并发）并需要可测试架构的应用。
