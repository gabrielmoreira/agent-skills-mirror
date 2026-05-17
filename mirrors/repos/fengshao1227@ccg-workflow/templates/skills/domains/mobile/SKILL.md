---
name: mobile
description: 移动开发。iOS、Android、SwiftUI、Jetpack Compose、React Native、Flutter、跨平台。当用户提到移动开发、iOS、Android、跨平台时路由到此。
license: MIT
user-invocable: false
disable-model-invocation: false
---

# 移动开发域 · Mobile Development

## 域概览

```
原生开发                    跨平台开发
├── iOS (SwiftUI/UIKit)     ├── React Native (JS/TS)
├── Android (Compose/Kotlin) └── Flutter (Dart)
└── 共通：MVVM / 网络层 / 持久化 / 测试
```

---

## iOS 开发

### SwiftUI 核心模式

- View 组件：`struct MyView: View { var body: some View { ... } }`
- State 管理：
  - `@State` — 本地状态
  - `@Binding` — 父子双向绑定
  - `@StateObject` — 拥有 ObservableObject
  - `@ObservedObject` — 引用 ObservableObject
  - `@EnvironmentObject` / `@Environment` — 全局注入
- ObservableObject：`@Published` 属性自动触发 UI 更新
- Custom ViewModifier：`struct CardModifier: ViewModifier` + `extension View { func cardStyle() }`
- 生命周期：`.task { await ... }` / `.onAppear` / `.onDisappear`

### UIKit 集成

- UIViewControllerRepresentable：包装 UIViewController 到 SwiftUI
- UIViewRepresentable：包装 UIView 到 SwiftUI
- Coordinator 模式：处理 delegate 回调
- Auto Layout：`NSLayoutConstraint.activate([...])` + `translatesAutoresizingMaskIntoConstraints = false`

### Combine 响应式

- Publisher：`URLSession.shared.dataTaskPublisher` → `map` → `decode` → `eraseToAnyPublisher`
- 订阅：`.sink(receiveCompletion:receiveValue:)` + `.store(in: &cancellables)`
- 常用 Operators：`debounce` / `removeDuplicates` / `combineLatest` / `flatMap`
- Subject：`PassthroughSubject`（无初始值）/ `CurrentValueSubject`（有初始值）

### iOS 架构

MVVM（推荐）：
- Model：`Codable` 数据结构
- Repository：`protocol` + `async throws` 方法
- ViewModel：`@MainActor class VM: ObservableObject` + `@Published` 属性
- View：`@StateObject private var viewModel = VM()`

VIPER（复杂场景）：
- View ←→ Presenter ←→ Interactor → Entity
- Router 处理导航

### 网络层

- APIClient：泛型 `func get<T: Decodable>(_ path:) async throws -> T`
- Token 管理：`request.setValue("Bearer \(token)", forHTTPHeaderField: "Authorization")`
- 错误处理：`enum APIError: Error { case invalidURL, invalidResponse, httpError(Int) }`

### 数据持久化

- UserDefaults：`@propertyWrapper struct UserDefault<T>` 简化访问
- Keychain：`SecItemAdd` / `SecItemCopyMatching` 存储敏感数据
- Core Data：`NSPersistentContainer` + `NSManagedObjectContext`
- SwiftData（iOS 17+）：`@Model` 宏简化持久化

### iOS Checklist

- [ ] SwiftUI 优先，UIKit 按需集成
- [ ] `@MainActor` 确保 UI 线程安全
- [ ] async/await 替代回调
- [ ] 依赖注入提升可测试性
- [ ] LazyVStack/LazyHStack 优化大列表
- [ ] 图片缓存（NSCache）减少内存压力
- [ ] Keychain 存储敏感数据（非 UserDefaults）
- [ ] 单元测试覆盖 ViewModel + Mock Repository

---

## Android 开发

### Jetpack Compose 核心模式

- Composable：`@Composable fun MyScreen() { ... }`
- State 管理：
  - `remember { mutableStateOf(value) }` — 本地状态
  - `rememberSaveable` — 跨配置变更保存
  - `derivedStateOf` — 派生状态避免重组
- LazyColumn：`items(list, key = { it.id })` 提供稳定 key
- Side Effects：
  - `LaunchedEffect(key)` — 启动协程
  - `DisposableEffect(key)` — 清理资源（onDispose）
  - `SideEffect` — 同步状态到外部
  - `snapshotFlow { state }` — 监听状态变化转 Flow
- Navigation：`NavHost` + `composable(route)` + `navController.navigate()`
- Custom Modifier：`fun Modifier.myModifier(): Modifier = composed { ... }`

### ViewModel + StateFlow

- StateFlow（推荐替代 LiveData）：
  - `MutableStateFlow(UiState())` + `.asStateFlow()`
  - `_uiState.update { it.copy(isLoading = true) }`
  - Compose 中：`val uiState by viewModel.uiState.collectAsState()`
- UiState data class：封装 loading / error / data

### Kotlin Coroutines & Flow

- 协程：`viewModelScope.launch { withContext(Dispatchers.IO) { ... } }`
- 并发：`coroutineScope { val a = async { ... }; val b = async { ... } }`
- Flow：`flow { emit(value) }` + `.flowOn(Dispatchers.IO)`
- StateFlow：`.stateIn(scope, SharingStarted.WhileSubscribed(5000), initial)`
- 搜索防抖：`searchQuery.debounce(300).filter { it.isNotEmpty() }.flatMapLatest { ... }`
- Channel：`Channel<Event>(BUFFERED)` + `.receiveAsFlow()` 一次性事件

### 依赖注入 (Hilt)

- `@HiltAndroidApp` Application + `@AndroidEntryPoint` Activity
- `@Module @InstallIn(SingletonComponent::class)` 提供依赖
- `@Provides @Singleton` 提供实例 / `@Binds` 绑定接口
- ViewModel：`@HiltViewModel class VM @Inject constructor(repo)` + `hiltViewModel()`

### Room 数据库

- Entity：`@Entity(tableName)` + `@PrimaryKey` + `@ColumnInfo`
- DAO：`@Query` / `@Insert(onConflict = REPLACE)` / `@Delete` + 返回 `Flow<List<T>>`
- Database：`@Database(entities, version)` + `Room.databaseBuilder`

### 网络层 (Retrofit)

- ApiService：`@GET` / `@POST` / `@Path` / `@Query` / `@Body` / `@Multipart`
- Interceptor：AuthInterceptor 注入 Bearer Token
- OkHttpClient：`addInterceptor` + `connectTimeout`

### Android Checklist

- [ ] Compose 优先，View 系统按需使用
- [ ] StateFlow 替代 LiveData
- [ ] Hilt 依赖注入
- [ ] Room 本地持久化
- [ ] `key` 参数优化 LazyColumn
- [ ] `remember` / `derivedStateOf` 避免过度重组
- [ ] Coil 图片加载 + 缓存策略
- [ ] 单元测试覆盖 ViewModel（runTest + advanceUntilIdle）

---

## 跨平台开发

### React Native vs Flutter

| 维度 | React Native | Flutter |
|------|--------------|---------|
| 语言 | TypeScript | Dart |
| 渲染 | 原生组件(桥接) | 自绘引擎(Skia) |
| 性能 | 接近原生 | 接近原生 |
| 热重载 | Fast Refresh | Hot Reload |
| 生态 | npm（成熟） | pub.dev（快速增长） |
| UI 一致性 | 跟随系统 | 完全一致 |
| 包体积 | ~7MB | ~15MB |

### React Native 核心模式

- 组件：函数组件 + Hooks（useState / useEffect / useCallback / useMemo）
- 列表：`FlatList` + `keyExtractor` + `initialNumToRender` + `windowSize`
- Navigation：`@react-navigation/native` + `createNativeStackNavigator`
- 状态管理：Redux Toolkit（`createSlice` + `createAsyncThunk`）/ Zustand
- 原生桥接：`NativeModules` 调用 iOS(Swift) / Android(Kotlin) 原生代码
- 性能：`React.memo` / Hermes 引擎 / 新架构 JSI（无桥接序列化）

### Flutter 核心模式

- Widget：StatelessWidget / StatefulWidget + `setState`
- 状态管理：
  - Provider：`ChangeNotifier` + `Consumer` / `context.watch`
  - Riverpod（推荐）：`FutureProvider` / `StateNotifierProvider` + `ref.watch`
- Navigation：go_router（`GoRoute` + `context.go/push/pop`）
- 原生桥接：`MethodChannel` + Platform Channels（iOS Swift / Android Kotlin）
- 性能：`const` 构造函数 / `ListView.builder` / `RepaintBoundary` / `ValueKey`

### 选型建议

| 场景 | 推荐 | 理由 |
|------|------|------|
| 团队有 Web 背景 | React Native | 学习成本低 |
| 追求极致性能/动画 | Flutter | 自绘引擎 60fps |
| UI 高度定制 | Flutter | 完全控制渲染 |
| 大量原生交互 | React Native | 桥接生态成熟 |
| 需要原生极致体验 | 原生开发 | 无桥接开销 |

### 跨平台 Checklist

- [ ] 选型匹配团队技术栈和业务需求
- [ ] 列表优化：FlatList(RN) / ListView.builder(Flutter) + key
- [ ] 状态管理：Redux Toolkit(RN) / Riverpod(Flutter)
- [ ] 原生模块桥接方案验证
- [ ] 包体积优化：ProGuard(Android) / tree-shake-icons(Flutter)
- [ ] 性能基线：冷启动 < 1.5s / 渲染 > 55fps

---

## 通用最佳实践

| 实践 | 说明 |
|------|------|
| MVVM 架构 | 分离 UI / 业务逻辑 / 数据层 |
| 依赖注入 | Hilt(Android) / Protocol(iOS) / Context(RN) |
| 响应式状态 | StateFlow / Combine / Hooks / Riverpod |
| 网络层封装 | 统一错误处理 + Token 管理 + 重试 |
| 本地持久化 | Room / Core Data / AsyncStorage / Hive |
| 列表优化 | 懒加载 + 稳定 key + 缓存 |
| 测试覆盖 | ViewModel 单元测试 + UI 测试关键流程 |

## 触发词

iOS、SwiftUI、UIKit、Combine、Android、Jetpack Compose、Kotlin、React Native、Flutter、跨平台、移动开发、MVVM
