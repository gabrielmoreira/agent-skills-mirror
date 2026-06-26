---
name: liquid-glass-design
description: iOS 26 灵动玻璃（Liquid Glass）设计系统 — 适用于 SwiftUI、UIKit 和 WidgetKit 的具有模糊、反射和交互式变形效果的动态玻璃材质。
---

# 灵动玻璃（Liquid Glass）设计系统 (iOS 26)

实现 Apple 灵动玻璃（Liquid Glass）的设计模式 — 这是一种动态材质，可以模糊背后的内容，反射周围内容的颜色和光影，并对触摸和指针交互做出反应。涵盖了 SwiftUI、UIKit 和 WidgetKit 的集成。

## 何时激活

- 为 iOS 26+ 构建或更新采用新设计语言的应用
- 实现玻璃风格的按钮、卡片、工具栏或容器
- 在玻璃元素之间创建变形（Morphing）过渡
- 为小组件（Widgets）应用灵动玻璃效果
- 将现有的模糊/材质效果迁移到新的灵动玻璃 API

## 核心模式 — SwiftUI

### 基础玻璃效果

为任何视图添加灵动玻璃效果的最简单方法：

```swift
Text("Hello, World!")
    .font(.title)
    .padding()
    .glassEffect()  // 默认：常规变体，胶囊形状
```

### 自定义形状和色调（Tint）

```swift
Text("Hello, World!")
    .font(.title)
    .padding()
    .glassEffect(.regular.tint(.orange).interactive(), in: .rect(cornerRadius: 16.0))
```

关键自定义选项：
- `.regular` — 标准玻璃效果
- `.tint(Color)` — 添加颜色提亮以突出显示
- `.interactive()` — 响应触摸和指针交互
- 形状：`.capsule`（默认）、`.rect(cornerRadius:)`、`.circle`

### 玻璃按钮样式

```swift
Button("Click Me") { /* 操作 */ }
    .buttonStyle(.glass)

Button("Important") { /* 操作 */ }
    .buttonStyle(.glassProminent)
```

### 适用于多元素的 GlassEffectContainer

始终将多个玻璃视图包裹在容器中，以优化性能和实现变形效果：

```swift
GlassEffectContainer(spacing: 40.0) {
    HStack(spacing: 40.0) {
        Image(systemName: "scribble.variable")
            .frame(width: 80.0, height: 80.0)
            .font(.system(size: 36))
            .glassEffect()

        Image(systemName: "eraser.fill")
            .frame(width: 80.0, height: 80.0)
            .font(.system(size: 36))
            .glassEffect()
    }
}
```

`spacing` 参数控制合并距离 — 越近的元素其玻璃形状会融合在一起。

### 联合玻璃效果

使用 `glassEffectUnion` 将多个视图合并为一个玻璃形状：

```swift
@Namespace private var namespace

GlassEffectContainer(spacing: 20.0) {
    HStack(spacing: 20.0) {
        ForEach(symbolSet.indices, id: \.self) { item in
            Image(systemName: symbolSet[item])
                .frame(width: 80.0, height: 80.0)
                .glassEffect()
                .glassEffectUnion(id: item < 2 ? "group1" : "group2", namespace: namespace)
        }
    }
}
```

### 变形（Morphing）过渡

在玻璃元素出现/消失时创建平滑的变形：

```swift
@State private var isExpanded = false
@Namespace private var namespace

GlassEffectContainer(spacing: 40.0) {
    HStack(spacing: 40.0) {
        Image(systemName: "scribble.variable")
            .frame(width: 80.0, height: 80.0)
            .glassEffect()
            .glassEffectID("pencil", in: namespace)

        if isExpanded {
            Image(systemName: "eraser.fill")
                .frame(width: 80.0, height: 80.0)
                .glassEffect()
                .glassEffectID("eraser", in: namespace)
        }
    }
}

Button("Toggle") {
    withAnimation { isExpanded.toggle() }
}
.buttonStyle(.glass)
```

### 在侧边栏下方延伸水平滚动

要允许水平滚动内容延伸到侧边栏或检查器（Inspector）下方，请确保 `ScrollView` 内容触及容器的领先/尾随（leading/trailing）边缘。当布局延伸到边缘时，系统会自动处理侧边栏下方的滚动行为 — 无需额外的修饰符。

## 核心模式 — UIKit

### 基础 UIGlassEffect

```swift
let glassEffect = UIGlassEffect()
glassEffect.tintColor = UIColor.systemBlue.withAlphaComponent(0.3)
glassEffect.isInteractive = true

let visualEffectView = UIVisualEffectView(effect: glassEffect)
visualEffectView.translatesAutoresizingMaskIntoConstraints = false
visualEffectView.layer.cornerRadius = 20
visualEffectView.clipsToBounds = true

view.addSubview(visualEffectView)
NSLayoutConstraint.activate([
    visualEffectView.centerXAnchor.constraint(equalTo: view.centerXAnchor),
    visualEffectView.centerYAnchor.constraint(equalTo: view.centerYAnchor),
    visualEffectView.widthAnchor.constraint(equalToConstant: 200),
    visualEffectView.heightAnchor.constraint(equalToConstant: 120)
])

// 向 contentView 添加内容
let label = UILabel()
label.text = "Liquid Glass"
label.translatesAutoresizingMaskIntoConstraints = false
visualEffectView.contentView.addSubview(label)
NSLayoutConstraint.activate([
    label.centerXAnchor.constraint(equalTo: visualEffectView.contentView.centerXAnchor),
    label.centerYAnchor.constraint(equalTo: visualEffectView.contentView.centerYAnchor)
])
```

### 适用于多元素的 UIGlassContainerEffect

```swift
let containerEffect = UIGlassContainerEffect()
containerEffect.spacing = 40.0

let containerView = UIVisualEffectView(effect: containerEffect)

let firstGlass = UIVisualEffectView(effect: UIGlassEffect())
let secondGlass = UIVisualEffectView(effect: UIGlassEffect())

containerView.contentView.addSubview(firstGlass)
containerView.contentView.addSubview(secondGlass)
```

### 滚动边缘效果（Scroll Edge Effects）

```swift
scrollView.topEdgeEffect.style = .automatic
scrollView.bottomEdgeEffect.style = .hard
scrollView.leftEdgeEffect.isHidden = true
```

### 工具栏玻璃集成

```swift
let favoriteButton = UIBarButtonItem(image: UIImage(systemName: "heart"), style: .plain, target: self, action: #selector(favoriteAction))
favoriteButton.hidesSharedBackground = true  // 选择不使用共享玻璃背景
```

## 核心模式 — WidgetKit

### 渲染模式检测

```swift
struct MyWidgetView: View {
    @Environment(\.widgetRenderingMode) var renderingMode

    var body: some View {
        if renderingMode == .accented {
            // 强调色模式：白色色调、主题化的玻璃背景
        } else {
            // 全色模式：标准外观
        }
    }
}
```

### 用于视觉层级的强调组（Accent Groups）

```swift
HStack {
    VStack(alignment: .leading) {
        Text("Title")
            .widgetAccentable()  // 强调组
        Text("Subtitle")
            // 主要组（默认）
    }
    Image(systemName: "star.fill")
        .widgetAccentable()  // 强调组
}
```

### 强调色模式下的图像渲染

```swift
Image("myImage")
    .widgetAccentedRenderingMode(.monochrome)
```

### 容器背景

```swift
VStack { /* 内容 */ }
    .containerBackground(for: .widget) {
        Color.blue.opacity(0.2)
    }
```

## 关键设计决策

| 决策 | 理由 |
|----------|-----------|
| 使用 GlassEffectContainer 包裹 | 性能优化，支持玻璃元素之间的变形过渡 |
| `spacing` 参数 | 控制合并距离 — 微调元素融合所需的接近程度 |
| `@Namespace` + `glassEffectID` | 支持在视图层级变化时实现平滑的变形过渡 |
| `interactive()` 修饰符 | 显式开启触摸/指针反应 — 并非所有玻璃都应有响应 |
| UIKit 中的 UIGlassContainerEffect | 与 SwiftUI 保持一致的容器模式 |
| 小组件中的强调渲染模式 | 当用户选择强调色主屏幕时，系统会应用色调玻璃 |

## 最佳实践

- **始终使用 GlassEffectContainer**：当对多个兄弟视图应用玻璃效果时，它可以启用变形效果并提高渲染性能。
- **在其他外观修饰符（frame, font, padding）之后应用** `.glassEffect()`。
- **仅在响应用户交互的元素上使用** `.interactive()`（如按钮、可切换项目）。
- **仔细选择容器间距**：以控制玻璃效果何时合并。
- **使用 `withAnimation`**：在更改视图层级时使用，以启用平滑的变形过渡。
- **在不同外观下进行测试**：包括浅色模式、深色模式以及强调色/色调模式。
- **确保无障碍对比度**：玻璃上的文字必须保持清晰可读。

## 应避免的反模式

- 在没有 GlassEffectContainer 的情况下使用多个独立的 `.glassEffect()` 视图。
- 嵌套过多的玻璃效果：会降低性能和视觉清晰度。
- 为每个视图都应用玻璃效果：应保留给交互元素、工具栏和卡片。
- 在 UIKit 中使用圆角时忘记设置 `clipsToBounds = true`。
- 忽略小组件中的强调渲染模式：这会破坏强调色主屏幕的外观。
- 在玻璃背后使用不透明背景：这会破坏半透明效果。

## 何时使用

- 采用新 iOS 26 设计的导航栏、工具栏和标签栏。
- 悬浮操作按钮和卡片式容器。
- 需要视觉深度和触摸反馈的交互式控件。
- 应该与系统灵动玻璃外观集成的小组件。
- 相关 UI 状态之间的变形过渡。
