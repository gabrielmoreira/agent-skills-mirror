---
description: "扩展通用规则的 Swift 安全规范"
globs: ["**/*.swift", "**/Package.swift"]
alwaysApply: false
---
# Swift 安全规范 (Swift Security)

> 本文件在通用安全规则的基础上，增加了 Swift 特有的安全内容。

## 密钥管理 (Secret Management)

- 对敏感数据（令牌、密码、密钥）使用 **Keychain 服务 (Keychain Services)** —— 绝不要使用 `UserDefaults`
- 对构建时密钥使用环境变量或 `.xcconfig` 文件
- 绝不要在源码中硬编码密钥 —— 反编译工具可以轻而易举地提取它们

```swift
let apiKey = ProcessInfo.processInfo.environment["API_KEY"]
guard let apiKey, !apiKey.isEmpty else {
    fatalError("API_KEY not configured")
}
```

## 传输安全 (Transport Security)

- 应用传输安全 (App Transport Security, ATS) 默认强制执行 —— 不要禁用它
- 对关键端点使用证书固定 (Certificate Pinning)
- 验证所有服务器证书

## 输入验证 (Input Validation)

- 在显示之前清理所有用户输入，以防止注入攻击
- 使用 `URL(string:)` 并进行验证，而不是强制解包 (force-unwrapping)
- 在处理来自外部源（API、深层链接、剪贴板）的数据之前进行验证
