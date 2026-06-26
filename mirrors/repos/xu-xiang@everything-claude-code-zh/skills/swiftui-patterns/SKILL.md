---
name: swiftui-patterns
description: SwiftUI 架构模式，使用 @Observable 进行状态管理，视图组合、导航、性能优化以及现代 iOS/macOS UI 最佳实践。
---

# SwiftUI 模式 (SwiftUI Patterns)

在 Apple 平台上构建声明式、高性能用户界面的现代 SwiftUI 模式。涵盖 Observation 框架、视图组合、类型安全导航以及性能优化。

## 何时激活

- 构建 SwiftUI 视图并管理状态（`@State`, `@Observable`, `@Binding`）
- 使用 `NavigationStack` 设计导航流
- 构建视图模型（View Model）和数据流
- 针对列表和复杂布局优化渲染性能
- 在 SwiftUI 中使用环境值（Environment Values）和依赖注入

## 状态管理 (State Management)

### 属性包装器选择 (Property Wrapper Selection)

选择最适合的简单包装器：

| 包装器 (Wrapper) | 使用场景 |
|---------|----------|
| `@State` | 视图局部值类型（开关、表单字段、Sheet 弹出状态） |
| `@Binding` | 对父视图 `@State` 的双向引用 |
| `@Observable` 类 + `@State` | 拥有多个属性的自有模型 |
| `@Observable` 类 (无包装器) | 从父视图传递的只读引用 |
| `@Bindable` | 对 `@Observable` 属性的双向绑定 |
| `@Environment` | 通过 `.environment()` 注入的共享依赖 |

### @Observable 视图模型 (ViewModel)

使用 `@Observable`（而非 `ObservableObject`）——它能追踪属性级别的变化，因此 SwiftUI 仅重新渲染读取了已更改属性的视图：

```swift
@Observable
final class ItemListViewModel {
    private(set) var items: [Item] = []
    private(set) var isLoading = false
    var searchText = ""

    private let repository: any ItemRepository

    init(repository: any ItemRepository = DefaultItemRepository()) {
        self.repository = repository
    }

    func load() async {
        isLoading = true
        defer { isLoading = false }
        items = (try? await repository.fetchAll()) ?? []
    }
}
```

### 使用视图模型（ViewModel）的视图

```swift
struct ItemListView: View {
    @State private var viewModel: ItemListViewModel

    init(viewModel: ItemListViewModel = ItemListViewModel()) {
        _viewModel = State(initialValue: viewModel)
    }

    var body: some View {
        List(viewModel.items) { item in
            ItemRow(item: item)
        }
        .searchable(text: $viewModel.searchText)
        .overlay { if viewModel.isLoading { ProgressView() } }
        .task { await viewModel.load() }
    }
}
```

### 环境注入 (Environment Injection)

使用 `@Environment` 替换 `@EnvironmentObject`：

```swift
// 注入 (Inject)
ContentView()
    .environment(authManager)

// 使用 (Consume)
struct ProfileView: View {
    @Environment(AuthManager.self) private var auth

    var body: some View {
        Text(auth.currentUser?.name ?? "Guest")
    }
}
```

## 视图组合 (View Composition)

### 提取子视图以限制失效范围

将视图拆分为小型、专注的结构体。当状态改变时，只有读取该状态的子视图会重新渲染：

```swift
struct OrderView: View {
    @State private var viewModel = OrderViewModel()

    var body: some View {
        VStack {
            OrderHeader(title: viewModel.title)
            OrderItemList(items: viewModel.items)
            OrderTotal(total: viewModel.total)
        }
    }
}
```

### 用于可复用样式的 ViewModifier

```swift
struct CardModifier: ViewModifier {
    func body(content: Content) -> some View {
        content
            .padding()
            .background(.regularMaterial)
            .clipShape(RoundedRectangle(cornerRadius: 12))
    }
}

extension View {
    func cardStyle() -> some View {
        modifier(CardModifier())
    }
}
```

## 导航 (Navigation)

### 类型安全的 NavigationStack

配合 `NavigationPath` 使用 `NavigationStack` 实现编程式、类型安全的路由：

```swift
@Observable
final class Router {
    var path = NavigationPath()

    func navigate(to destination: Destination) {
        path.append(destination)
    }

    func popToRoot() {
        path = NavigationPath()
    }
}

enum Destination: Hashable {
    case detail(Item.ID)
    case settings
    case profile(User.ID)
}

struct RootView: View {
    @State private var router = Router()

    var body: some View {
        NavigationStack(path: $router.path) {
            HomeView()
                .navigationDestination(for: Destination.self) { dest in
                    switch dest {
                    case .detail(let id): ItemDetailView(itemID: id)
                    case .settings: SettingsView()
                    case .profile(let id): ProfileView(userID: id)
                    }
                }
        }
        .environment(router)
    }
}
```

## 性能 (Performance)

### 对大型集合使用延迟容器 (Lazy Containers)

`LazyVStack` 和 `LazyHStack` 仅在视图可见时才创建它们：

```swift
ScrollView {
    LazyVStack(spacing: 8) {
        ForEach(items) { item in
            ItemRow(item: item)
        }
    }
}
```

### 稳定的标识符 (Stable Identifiers)

在 `ForEach` 中始终使用稳定、唯一的 ID —— 避免使用数组索引：

```swift
// 使用 Identifiable 协议实现或显式指定 id
ForEach(items, id: \.stableID) { item in
    ItemRow(item: item)
}
```

### 避免在 body 中执行昂贵的操作

- 绝不要在 `body` 内部执行 I/O、网络请求或重度计算
- 使用 `.task {}` 执行异步工作 —— 它会在视图消失时自动取消
- 在滚动视图中谨慎使用 `.sensoryFeedback()` 和 `.geometryGroup()`
- 尽量减少在列表（List）中使用 `.shadow()`、`.blur()` 和 `.mask()` —— 它们会触发离屏渲染（offscreen rendering）

### Equatable 协议实现

对于 body 渲染代价高昂的视图，实现 `Equatable` 协议以跳过不必要的重新渲染：

```swift
struct ExpensiveChartView: View, Equatable {
    let dataPoints: [DataPoint] // DataPoint 必须符合 Equatable

    static func == (lhs: Self, rhs: Self) -> Bool {
        lhs.dataPoints == rhs.dataPoints
    }

    var body: some View {
        // 复杂的图表渲染逻辑
    }
}
```

## 预览 (Previews)

使用 `#Preview` 宏配合内联 Mock 数据进行快速迭代：

```swift
#Preview("空状态") {
    ItemListView(viewModel: ItemListViewModel(repository: EmptyMockRepository()))
}

#Preview("已加载") {
    ItemListView(viewModel: ItemListViewModel(repository: PopulatedMockRepository()))
}
```

## 需避免的反模式 (Anti-Patterns)

- 在新代码中使用 `ObservableObject` / `@Published` / `@StateObject` / `@EnvironmentObject` —— 请迁移至 `@Observable`
- 直接在 `body` 或 `init` 中放入异步工作 —— 请使用 `.task {}` 或显式的加载方法
- 在不拥有数据的子视图内部将视图模型创建为 `@State` —— 应从父视图传递
- 使用 `AnyView` 类型擦除 —— 推荐对条件视图使用 `@ViewBuilder` 或 `Group`
- 在向 Actor 传递数据或从 Actor 接收数据时忽略 `Sendable` 要求

## 参考资料 (References)

参见技能：`swift-actor-persistence` 了解基于 Actor 的持久化模式。
参见技能：`swift-protocol-di-testing` 了解基于协议的依赖注入（DI）以及使用 Swift Testing 进行测试。
