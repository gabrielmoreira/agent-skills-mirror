# Adaptive Layouts — Large Screens, Foldables, WindowSizeClass

An app that only runs well on a phone in portrait mode is half-built. Tablets, foldables, Chromebooks, and landscape phones are not edge cases — they are a growing segment of Android users. Google requires large-screen quality tiers for Play Store featuring. Building adaptive from the start costs far less than retrofitting it later.

---

## WindowSizeClass — the foundation

`WindowSizeClass` classifies the current window into width and height buckets:

| Class | Width | Typical device |
|-------|-------|---------------|
| `Compact` | < 600dp | Phone portrait |
| `Medium` | 600dp – 840dp | Phone landscape, small tablet, foldable unfolded inner |
| `Expanded` | > 840dp | Tablet, desktop |

```kotlin
// In Activity
class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContent {
            val windowSizeClass = calculateWindowSizeClass(this)
            AppTheme {
                AppRoot(windowSizeClass = windowSizeClass)
            }
        }
    }
}

// Dependency
// implementation("androidx.window:window:1.3.0")
// implementation("androidx.window:window-core:1.3.0")
```

### Using WindowSizeClass in composables

```kotlin
@Composable
fun AppRoot(
    windowSizeClass: WindowSizeClass,
    navController: NavHostController = rememberNavController()
) {
    val isCompact = windowSizeClass.widthSizeClass == WindowWidthSizeClass.Compact

    Scaffold(
        bottomBar = {
            // Bottom nav only on compact; rail/drawer on medium/expanded
            if (isCompact) {
                AppBottomNavBar(navController)
            }
        }
    ) { padding ->
        Row(modifier = Modifier.padding(padding)) {
            if (!isCompact) {
                AppNavigationRail(navController)
            }
            AppNavigation(
                navController = navController,
                windowSizeClass = windowSizeClass,
                modifier = Modifier.weight(1f)
            )
        }
    }
}
```

---

## NavigationSuiteScaffold — automatic adaptive navigation

`NavigationSuiteScaffold` automatically selects bottom bar (compact), navigation rail (medium), or navigation drawer (expanded) based on the current window size:

```kotlin
// implementation("androidx.compose.material3.adaptive:adaptive-navigation-suite:1.3.1")

@Composable
fun AdaptiveAppShell(
    currentDestination: NavDestination?,
    onNavigate: (TopLevelRoute) -> Unit,
    content: @Composable () -> Unit
) {
    NavigationSuiteScaffold(
        navigationSuiteItems = {
            topLevelRoutes.forEach { route ->
                item(
                    icon = { Icon(route.icon, contentDescription = route.label) },
                    label = { Text(route.label) },
                    selected = currentDestination?.hierarchy?.any {
                        it.hasRoute(route.route::class)
                    } == true,
                    onClick = { onNavigate(route) }
                )
            }
        }
    ) {
        content()
    }
}
```

---

## ListDetailPaneScaffold — two-pane layouts

On phones, show list then detail (standard navigation). On tablets, show both side by side.

```kotlin
// implementation("androidx.compose.material3.adaptive:adaptive-layout:1.0.0")
// implementation("androidx.compose.material3.adaptive:adaptive-navigation:1.0.0")

@Composable
fun ArticleListDetailScreen(
    articles: List<Article>,
    onArticleSelected: (Article) -> Unit
) {
    val navigator = rememberListDetailPaneScaffoldNavigator<Article>()

    BackHandler(navigator.canNavigateBack()) {
        navigator.navigateBack()
    }

    ListDetailPaneScaffold(
        directive = navigator.scaffoldDirective,
        value = navigator.scaffoldValue,
        listPane = {
            AnimatedPane {
                ArticleListPane(
                    articles = articles,
                    onArticleClick = { article ->
                        navigator.navigateTo(ListDetailPaneScaffoldRole.Detail, article)
                    }
                )
            }
        },
        detailPane = {
            AnimatedPane {
                val article = navigator.currentDestination?.contentKey
                if (article != null) {
                    ArticleDetailPane(article = article)
                } else {
                    PlaceholderDetailPane()
                }
            }
        }
    )
}

@Composable
private fun ArticleListPane(
    articles: List<Article>,
    onArticleClick: (Article) -> Unit
) {
    LazyColumn {
        items(articles, key = { it.id }) { article ->
            ArticleRow(
                article = article,
                onClick = { onArticleClick(article) }
            )
        }
    }
}
```

---

## Foldable Support

### Detect fold state

```kotlin
// implementation("androidx.window:window:1.3.0")

@Composable
fun rememberFoldingFeature(): FoldingFeature? {
    val activity = LocalContext.current as Activity
    var foldingFeature by remember { mutableStateOf<FoldingFeature?>(null) }

    LaunchedEffect(activity) {
        WindowInfoTracker.getOrCreate(activity)
            .windowLayoutInfo(activity)
            .collect { layoutInfo ->
                foldingFeature = layoutInfo.displayFeatures
                    .filterIsInstance<FoldingFeature>()
                    .firstOrNull()
            }
    }
    return foldingFeature
}

@Composable
fun FoldAwareLayout(content: @Composable (isTableTop: Boolean, isSeparating: Boolean) -> Unit) {
    val foldingFeature = rememberFoldingFeature()
    val isTableTop = foldingFeature?.orientation == FoldingFeature.Orientation.HORIZONTAL
    val isSeparating = foldingFeature?.isSeparating == true

    content(isTableTop, isSeparating)
}
```

### Table-top mode (horizontal fold, half-open)

```kotlin
@Composable
fun VideoPlayerScreen() {
    FoldAwareLayout { isTableTop, _ ->
        if (isTableTop) {
            // Fold at bottom: video on top half, controls on bottom half
            Column {
                VideoSurface(modifier = Modifier.weight(1f))
                HingeGuide()  // visual separator at fold
                VideoControls(modifier = Modifier.weight(1f))
            }
        } else {
            // Standard layout
            Box(modifier = Modifier.fillMaxSize()) {
                VideoSurface(modifier = Modifier.fillMaxSize())
                VideoControls(modifier = Modifier.align(Alignment.BottomCenter))
            }
        }
    }
}
```

---

## Adaptive Content Composables

### Respond to available width within composables

```kotlin
@Composable
fun AdaptiveArticleCard(article: Article, modifier: Modifier = Modifier) {
    BoxWithConstraints(modifier = modifier) {
        if (maxWidth > 600.dp) {
            // Wide: horizontal layout with large image
            Row {
                AsyncImage(
                    model = article.imageUrl,
                    contentDescription = null,
                    modifier = Modifier.width(200.dp).fillMaxHeight()
                )
                ArticleTextContent(article, modifier = Modifier.weight(1f))
            }
        } else {
            // Narrow: vertical layout with smaller image
            Column {
                AsyncImage(
                    model = article.imageUrl,
                    contentDescription = null,
                    modifier = Modifier.fillMaxWidth().height(160.dp)
                )
                ArticleTextContent(article)
            }
        }
    }
}
```

### Adaptive grid columns

```kotlin
@Composable
fun AdaptiveGrid(
    items: List<Article>,
    windowSizeClass: WindowSizeClass,
    modifier: Modifier = Modifier
) {
    val columns = when (windowSizeClass.widthSizeClass) {
        WindowWidthSizeClass.Compact  -> 1
        WindowWidthSizeClass.Medium   -> 2
        WindowWidthSizeClass.Expanded -> 3
        else -> 1
    }

    LazyVerticalGrid(
        columns = GridCells.Fixed(columns),
        contentPadding = PaddingValues(AppSpacing.M),
        horizontalArrangement = Arrangement.spacedBy(AppSpacing.M),
        verticalArrangement = Arrangement.spacedBy(AppSpacing.M),
        modifier = modifier
    ) {
        items(items, key = { it.id }) { article ->
            ArticleCard(article = article)
        }
    }
}
```

---

## Window Insets — Comprehensive Guide

Always handle insets explicitly. Never rely on the system to handle them for you.

```kotlin
// Enable edge-to-edge in Activity (required from Android 15)
class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        enableEdgeToEdge()
        setContent { AppTheme { AppRoot() } }
    }
}
```

### Inset types and when to use each

```kotlin
// safeDrawingPadding: status bar + nav bar + display cutout — use for full-screen content
Modifier.fillMaxSize().safeDrawingPadding()

// statusBarsPadding: only top bar height — use for app bars / top content
Modifier.statusBarsPadding()

// navigationBarsPadding: only bottom nav height — use for bottom sheets, FABs
Modifier.navigationBarsPadding()

// imePadding: keyboard height — use on scroll containers with text fields
Modifier.imePadding()

// systemGesturesPadding: areas reserved for back gesture — use for edge content
Modifier.systemGesturesPadding()

// windowInsetsPadding: targeted inset type — maximum control
Modifier.windowInsetsPadding(WindowInsets.statusBars)
```

### Correct Scaffold + insets pattern

```kotlin
Scaffold(
    topBar = { AppTopBar() },  // TopAppBar handles status bar internally
    bottomBar = { AppBottomBar() },  // NavigationBar handles nav bar internally
    floatingActionButton = {
        FloatingActionButton(
            onClick = { },
            modifier = Modifier.navigationBarsPadding() // FAB must clear nav bar
        ) { Icon(Icons.Default.Add, null) }
    },
    contentWindowInsets = WindowInsets(0) // let content manage its own insets
) { paddingValues ->
    LazyColumn(
        contentPadding = paddingValues + PaddingValues(horizontal = AppSpacing.M),
        modifier = Modifier.fillMaxSize()
    ) {
        // content
    }
}
```

### Display cutouts (notch/hole-punch)

```kotlin
// Allow content to draw behind cutout area on landscape phones
WindowCompat.getInsetsController(window, window.decorView)
    .isAppearanceLightStatusBars = false

// In composable — read cutout bounds if you need to avoid them
val cutout = WindowInsets.displayCutout.asPaddingValues()
val cutoutLeft = cutout.calculateLeftPadding(LocalLayoutDirection.current)
```

---

## Large Screen Quality Requirements

Google Play features apps meeting these large-screen requirements:

- [ ] App does not crash or show blank screen on large screen
- [ ] App is usable in all orientations (no orientation lock unless camera/game)
- [ ] No fixed-size windows requiring scroll to use the app
- [ ] Multi-window (split-screen) works correctly
- [ ] Layout adapts meaningfully on 600dp+ width — not just stretched phone UI
- [ ] Keyboard and mouse input handled correctly (no touch-only gestures as the only option)
- [ ] `android:resizeableActivity="true"` in manifest (default true from API 24)
