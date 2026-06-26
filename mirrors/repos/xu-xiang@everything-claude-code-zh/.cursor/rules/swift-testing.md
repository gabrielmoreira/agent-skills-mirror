---
description: "Swift 测试（Swift Testing）扩展了通用规则"
globs: ["**/*.swift", "**/Package.swift"]
alwaysApply: false
---
# Swift 测试 (Swift Testing)

> 本文件通过 Swift 特定的内容扩展了通用测试规则。

## 框架 (Framework)

对新测试使用 **Swift Testing** (`import Testing`)。使用 `@Test` 和 `#expect`：

```swift
@Test("User creation validates email")
func userCreationValidatesEmail() throws {
    #expect(throws: ValidationError.invalidEmail) {
        try User(email: "not-an-email")
    }
}
```

## 测试隔离 (Test Isolation)

每个测试都会获得一个新实例 —— 在 `init` 中进行设置（set up），在 `deinit` 中进行销毁（tear down）。测试之间不得共享可变状态（mutable state）。

## 参数化测试 (Parameterized Tests)

```swift
@Test("Validates formats", arguments: ["json", "xml", "csv"])
func validatesFormat(format: String) throws {
    let parser = try Parser(format: format)
    #expect(parser.isValid)
}
```

## 覆盖率 (Coverage)

```bash
swift test --enable-code-coverage
```

## 参考 (Reference)

有关基于协议的依赖注入（protocol-based dependency injection）和 Swift Testing 的模拟模式（mock patterns），请参阅技能（skill）：`swift-protocol-di-testing`。
