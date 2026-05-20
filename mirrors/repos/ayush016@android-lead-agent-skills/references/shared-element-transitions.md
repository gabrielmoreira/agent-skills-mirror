# Shared Element Transitions — Production Reference

> Official API reference: https://developer.android.com/develop/ui/compose/animation/shared-elements

Shared element transitions are the single most powerful technique for communicating spatial relationships during navigation. When a user taps an image and it flows from a list thumbnail into a full-screen hero, the brain understands immediately where it came from and that it can go back. No amount of fade or slide achieves that. Use them by default for any content navigation.

---

## Mental Model — Three Layers

Understanding how the three layers interact makes every other concept obvious.

### Layer 1: SharedTransitionLayout (the coordinator)

`SharedTransitionLayout` is a layout composable that creates a `SharedTransitionScope`. It must **wrap the entire region** where shared elements will transition — which means it wraps the `NavHost` (or `NavDisplay`), not just individual screens. It maintains a registry of active shared content states and drives the interpolation between source and destination geometry.

```kotlin
SharedTransitionLayout {
    // this: SharedTransitionScope
    NavHost(navController, startDestination = HomeRoute) {
        composable<HomeRoute> { ... }
        composable<DetailRoute> { ... }
    }
}
```

### Layer 2: SharedTransitionScope (the receiver)

`SharedTransitionLayout` gives you a `SharedTransitionScope` receiver. Composables must be **inside this receiver** to access the `sharedElement()` and `sharedBounds()` modifiers. Thread it down via `with(sharedTransitionScope) { }` or through CompositionLocals.

### Layer 3: AnimatedVisibilityScope (the per-composable handle)

Each composable destination inside a `NavHost` is itself an `AnimatedContentScope` (which implements `AnimatedVisibilityScope`). This scope tells the shared element system whether this composable is currently entering or exiting. It must be passed to every `sharedElement()` or `sharedBounds()` call.

In Navigation 2, access it as `this@composable` inside a `composable { }` block.  
In Navigation 3, access it as `LocalNavAnimatedContentScope.current`.

### The Key Contract

Source and destination nodes with **identical keys** have their geometry interpolated by the system. The key is compared by equality — use a stable, identity-based value (like a database ID), never a list position index, which can shift.

---

## sharedElement() vs sharedBounds()

This is the most important choice you make for each transition.

### sharedElement() — same content, different geometry

Use when the **same content** appears in both source and destination: an image going from a 120dp thumbnail to a full-width hero; a text label that becomes a heading. The system renders only the destination composable during the transition and interpolates position and size.

**No `enter`/`exit` parameters** — the content itself doesn't change visibility, only geometry.

```kotlin
// The image is the same asset in both places — sharedElement is correct
Modifier.sharedElement(
    state = rememberSharedContentState(key = "product-image-${product.id}"),
    animatedVisibilityScope = animatedVisibilityScope
)
```

### sharedBounds() — different content, shared spatial region

Use when **different composables** share the same conceptual region on screen: a compact card expanding into a full-screen detail view; a FAB morphing into a modal surface. The source and destination are visually distinct but spatially continuous. The system keeps both composables alive and clips them within the shared region during the transition.

**Has `enter`/`exit` parameters** — controls how the destination content appears within the shared region.

```kotlin
// The card and the detail screen are different composables sharing a region
Modifier.sharedBounds(
    sharedContentState = rememberSharedContentState(key = "card-region-${item.id}"),
    animatedVisibilityScope = animatedVisibilityScope,
    enter = fadeIn(tween(durationMillis = 300)),
    exit = fadeOut(tween(durationMillis = 150)),
    resizeMode = SharedTransitionScope.ResizeMode.ScaleToBounds()
)
```

**Quick reference:**

| Question | sharedElement() | sharedBounds() |
|---|---|---|
| Same content? | Yes | No |
| Same image/icon? | ✓ | — |
| Card → screen? | — | ✓ |
| FAB → dialog? | — | ✓ |
| Text (same string)? | ✓ | — |
| Enter/exit control? | Not available | Available |

---

## Threading the Scopes

### Option A: Explicit Parameters (preferred for shallow trees)

Pass both scopes as parameters. Explicit, zero-magic, easy to trace in an IDE. Use this when the composable tree is 1–2 levels deep from the NavHost.

```kotlin
SharedTransitionLayout {
    val navController = rememberNavController()

    NavHost(
        navController = navController,
        startDestination = HomeRoute,
        modifier = Modifier.fillMaxSize()
    ) {
        composable<HomeRoute> {
            // this@composable is AnimatedContentScope / AnimatedVisibilityScope
            CatalogScreen(
                sharedTransitionScope = this@SharedTransitionLayout,
                animatedVisibilityScope = this@composable,
                onItemClick = { item ->
                    navController.navigate(DetailRoute(itemId = item.id))
                }
            )
        }
        composable<DetailRoute> { backStack ->
            val route: DetailRoute = backStack.toRoute()
            ItemDetailScreen(
                itemId = route.itemId,
                sharedTransitionScope = this@SharedTransitionLayout,
                animatedVisibilityScope = this@composable,
                onBack = { navController.popBackStack() }
            )
        }
    }
}
```

Receive them in the screen composable:

```kotlin
@Composable
fun CatalogScreen(
    sharedTransitionScope: SharedTransitionScope,
    animatedVisibilityScope: AnimatedVisibilityScope,
    onItemClick: (CatalogItem) -> Unit,
    // ...
) {
    with(sharedTransitionScope) {
        LazyVerticalGrid(columns = GridCells.Fixed(2)) {
            items(items, key = { it.id }) { item ->
                CatalogCard(
                    item = item,
                    onClick = { onItemClick(item) },
                    animatedVisibilityScope = animatedVisibilityScope
                )
            }
        }
    }
}
```

### Option B: CompositionLocal (preferred for deep trees)

When shared element modifiers live 4+ composable levels below the NavHost, threading explicit parameters through every layer becomes noisy. Use CompositionLocals instead.

```kotlin
val LocalSharedTransitionScope = compositionLocalOf<SharedTransitionScope?> { null }
val LocalAnimatedVisibilityScope = compositionLocalOf<AnimatedVisibilityScope?> { null }

// At the NavHost level:
SharedTransitionLayout {
    CompositionLocalProvider(LocalSharedTransitionScope provides this) {
        NavHost(navController, startDestination = HomeRoute) {
            composable<HomeRoute> {
                CompositionLocalProvider(LocalAnimatedVisibilityScope provides this@composable) {
                    CatalogScreen(onItemClick = { ... })
                }
            }
            composable<DetailRoute> {
                CompositionLocalProvider(LocalAnimatedVisibilityScope provides this@composable) {
                    ItemDetailScreen(onBack = { ... })
                }
            }
        }
    }
}

// In any deeply nested composable:
@Composable
fun ProductHeroImage(imageUrl: String, productId: Long) {
    val sharedTransitionScope = LocalSharedTransitionScope.current
        ?: error("SharedTransitionScope not provided")
    val animatedVisibilityScope = LocalAnimatedVisibilityScope.current
        ?: error("AnimatedVisibilityScope not provided")

    with(sharedTransitionScope) {
        AsyncImage(
            model = imageUrl,
            contentDescription = null,
            modifier = Modifier
                .sharedElement(
                    rememberSharedContentState(key = "product-image-$productId"),
                    animatedVisibilityScope = animatedVisibilityScope
                )
                .fillMaxWidth()
                .aspectRatio(1f)
        )
    }
}
```

**Rule of thumb**: Use explicit params for screens; switch to CompositionLocal when you find yourself adding `sharedTransitionScope` and `animatedVisibilityScope` to 3+ intermediate composables that don't use them directly.

---

## Transition Specs

### Default Behaviour

Out of the box, shared elements use a spring animation for geometry and a crossfade for content visibility. This is already good. Customise only when the default feels wrong for a specific transition.

### Customising with boundsTransform

```kotlin
Modifier.sharedElement(
    state = rememberSharedContentState(key = "hero-image-${item.id}"),
    animatedVisibilityScope = animatedVisibilityScope,
    boundsTransform = { initialBounds, targetBounds ->
        spring(
            dampingRatio = Spring.DampingRatioLowBouncy,
            stiffness = Spring.StiffnessMedium
        )
    }
)
```

### Spring vs Tween

**Spring**: Feels physical. The element overshoots slightly and settles. Use for imagery, cards, and surface transitions where a tactile quality is desirable. Tune `stiffness` to control speed; tune `dampingRatio` to control bounce.

```kotlin
spring(
    stiffness = Spring.StiffnessMedium,       // balanced feel
    dampingRatio = Spring.DampingRatioNoBouncy // no overshoot for professional UIs
)
```

**Tween**: Feels designed. Precise timing, explicit easing. Use when you need exact coordination with other timed animations (Lottie, audio, etc.).

```kotlin
tween(durationMillis = 400, easing = FastOutSlowInEasing)
```

### Z-ordering

When two shared elements overlap during a transition (e.g. an image beneath a card surface), control which renders on top with `zIndexInOverlay`:

```kotlin
Modifier.sharedBounds(
    sharedContentState = rememberSharedContentState(key = "card-surface-${item.id}"),
    animatedVisibilityScope = animatedVisibilityScope,
    zIndexInOverlay = 1f  // renders above elements with lower zIndex
)
```

---

## renderInSharedTransitionScope

Some elements should remain visually present during a transition even though they only exist on one screen — for example, a floating action button or a toolbar that appears on the detail screen but not the list. Without special handling, these elements flash into existence at their final position as the transition completes, which looks broken.

Apply `renderInSharedTransitionScope` to make them render in the shared overlay layer, participating in the transition's visual stack:

```kotlin
@Composable
fun DetailScreen(
    sharedTransitionScope: SharedTransitionScope,
    animatedVisibilityScope: AnimatedVisibilityScope
) {
    with(sharedTransitionScope) {
        Box(modifier = Modifier.fillMaxSize()) {
            // Main content with shared elements...

            // The back button only exists on detail — without renderInSharedTransitionScope
            // it would pop into view abruptly when the transition completes.
            IconButton(
                onClick = onBack,
                modifier = Modifier
                    .align(Alignment.TopStart)
                    .renderInSharedTransitionScope(this@SharedTransitionLayout)
                    .animateEnterExit(
                        enter = fadeIn(tween(300, delayMillis = 150)),
                        exit = fadeOut(tween(150))
                    )
            ) {
                Icon(Icons.AutoMirrored.Filled.ArrowBack, contentDescription = "Back")
            }
        }
    }
}
```

**What happens if you forget it**: The element either disappears behind the transitioning content (z-order issue) or blinks into existence at the end of the transition. Neither is acceptable in a polished UI.

---

## Pattern 1: List → Detail Image Transition

The canonical shared element pattern: a grid thumbnail flows into a full-width detail hero. Use `sharedElement()` because the same image appears in both places.

```kotlin
// Data
data class MediaItem(val id: Long, val title: String, val imageUrl: String)

// Navigation routes
@Serializable data object MediaGridRoute
@Serializable data class MediaDetailRoute(val itemId: Long)

// NavHost setup
SharedTransitionLayout(modifier = Modifier.fillMaxSize()) {
    val navController = rememberNavController()

    NavHost(navController, startDestination = MediaGridRoute) {
        composable<MediaGridRoute> {
            MediaGridScreen(
                sharedTransitionScope = this@SharedTransitionLayout,
                animatedVisibilityScope = this@composable,
                onItemClick = { item ->
                    navController.navigate(MediaDetailRoute(itemId = item.id))
                }
            )
        }
        composable<MediaDetailRoute> { backStack ->
            val route: MediaDetailRoute = backStack.toRoute()
            MediaDetailScreen(
                itemId = route.itemId,
                sharedTransitionScope = this@SharedTransitionLayout,
                animatedVisibilityScope = this@composable,
                onBack = { navController.popBackStack() }
            )
        }
    }
}

// Grid screen
@Composable
fun MediaGridScreen(
    items: List<MediaItem>,
    sharedTransitionScope: SharedTransitionScope,
    animatedVisibilityScope: AnimatedVisibilityScope,
    onItemClick: (MediaItem) -> Unit
) {
    LazyVerticalGrid(
        columns = GridCells.Adaptive(minSize = 160.dp),
        contentPadding = PaddingValues(SpaceM),
        horizontalArrangement = Arrangement.spacedBy(SpaceS),
        verticalArrangement = Arrangement.spacedBy(SpaceS)
    ) {
        items(items, key = { it.id }) { item ->
            with(sharedTransitionScope) {
                Box(
                    modifier = Modifier
                        .clip(MaterialTheme.shapes.medium)
                        .clickable { onItemClick(item) }
                ) {
                    AsyncImage(
                        model = item.imageUrl,
                        contentDescription = item.title,
                        contentScale = ContentScale.Crop,
                        modifier = Modifier
                            .sharedElement(
                                state = rememberSharedContentState(
                                    key = "media-image-${item.id}"
                                ),
                                animatedVisibilityScope = animatedVisibilityScope,
                                boundsTransform = { _, _ ->
                                    spring(
                                        stiffness = Spring.StiffnessMedium,
                                        dampingRatio = Spring.DampingRatioNoBouncy
                                    )
                                }
                            )
                            .fillMaxWidth()
                            .aspectRatio(1f)
                    )
                }
            }
        }
    }
}

// Detail screen
@Composable
fun MediaDetailScreen(
    item: MediaItem,
    sharedTransitionScope: SharedTransitionScope,
    animatedVisibilityScope: AnimatedVisibilityScope,
    onBack: () -> Unit
) {
    with(sharedTransitionScope) {
        Column(modifier = Modifier.fillMaxSize().verticalScroll(rememberScrollState())) {
            AsyncImage(
                model = item.imageUrl,
                contentDescription = item.title,
                contentScale = ContentScale.Crop,
                modifier = Modifier
                    .sharedElement(
                        state = rememberSharedContentState(
                            key = "media-image-${item.id}"  // identical key
                        ),
                        animatedVisibilityScope = animatedVisibilityScope,
                        boundsTransform = { _, _ ->
                            spring(
                                stiffness = Spring.StiffnessMedium,
                                dampingRatio = Spring.DampingRatioNoBouncy
                            )
                        }
                    )
                    .fillMaxWidth()
                    .height(320.dp)
            )

            Column(modifier = Modifier.padding(SpaceM)) {
                Text(text = item.title, style = MaterialTheme.typography.headlineMedium)
                // remaining detail content...
            }
        }

        // Back button — only on detail, needs renderInSharedTransitionScope
        IconButton(
            onClick = onBack,
            modifier = Modifier
                .statusBarsPadding()
                .padding(SpaceS)
                .renderInSharedTransitionScope(this@MediaDetailScreen)
                .animateEnterExit(
                    enter = fadeIn(tween(250, delayMillis = 200)),
                    exit = fadeOut(tween(150))
                )
        ) {
            Icon(Icons.AutoMirrored.Filled.ArrowBack, contentDescription = "Back")
        }
    }
}
```

---

## Pattern 2: Card Expansion (Container Transform)

A compact card expands to fill the screen. Source and destination are visually different composables sharing a region — use `sharedBounds()`.

```kotlin
// Compact card state (source)
@Composable
fun ExpandableCard(
    content: ContentItem,
    sharedTransitionScope: SharedTransitionScope,
    animatedVisibilityScope: AnimatedVisibilityScope,
    onClick: () -> Unit
) {
    val cardShape = RoundedCornerShape(16.dp)

    with(sharedTransitionScope) {
        Card(
            onClick = onClick,
            shape = cardShape,
            modifier = Modifier
                .sharedBounds(
                    sharedContentState = rememberSharedContentState(
                        key = "content-card-${content.id}"
                    ),
                    animatedVisibilityScope = animatedVisibilityScope,
                    clipInOverlayDuringTransition = OverlayClip(cardShape),
                    enter = fadeIn(tween(300)),
                    exit = fadeOut(tween(150)),
                    boundsTransform = { _, _ ->
                        spring(
                            stiffness = Spring.StiffnessMediumLow,
                            dampingRatio = Spring.DampingRatioNoBouncy
                        )
                    }
                )
                .fillMaxWidth()
                .height(180.dp)
        ) {
            // Card preview content: thumbnail + title
            Row(modifier = Modifier.fillMaxSize()) {
                AsyncImage(
                    model = content.thumbnailUrl,
                    contentDescription = null,
                    contentScale = ContentScale.Crop,
                    modifier = Modifier.width(120.dp).fillMaxHeight()
                )
                Column(modifier = Modifier.padding(SpaceM)) {
                    Text(content.title, style = MaterialTheme.typography.titleMedium)
                    Text(content.subtitle, style = MaterialTheme.typography.bodySmall)
                }
            }
        }
    }
}

// Expanded detail (destination)
@Composable
fun ContentDetailScreen(
    content: ContentItem,
    sharedTransitionScope: SharedTransitionScope,
    animatedVisibilityScope: AnimatedVisibilityScope,
    onBack: () -> Unit
) {
    with(sharedTransitionScope) {
        Box(
            modifier = Modifier
                .sharedBounds(
                    sharedContentState = rememberSharedContentState(
                        key = "content-card-${content.id}"  // same key
                    ),
                    animatedVisibilityScope = animatedVisibilityScope,
                    enter = fadeIn(tween(300, delayMillis = 50)),
                    exit = fadeOut(tween(200)),
                    boundsTransform = { _, _ ->
                        spring(
                            stiffness = Spring.StiffnessMediumLow,
                            dampingRatio = Spring.DampingRatioNoBouncy
                        )
                    }
                )
                .fillMaxSize()
                .background(MaterialTheme.colorScheme.surface)
        ) {
            Column(modifier = Modifier.verticalScroll(rememberScrollState())) {
                AsyncImage(
                    model = content.heroImageUrl,
                    contentDescription = content.title,
                    contentScale = ContentScale.Crop,
                    modifier = Modifier.fillMaxWidth().height(260.dp)
                )
                Column(modifier = Modifier.padding(SpaceM)) {
                    Text(content.title, style = MaterialTheme.typography.headlineMedium)
                    Spacer(modifier = Modifier.height(SpaceS))
                    Text(content.body, style = MaterialTheme.typography.bodyLarge)
                }
            }
        }
    }
}
```

---

## Pattern 3: FAB → Full-Screen Compose Surface

A FAB morphs into a full-screen compose/creation surface. Classic Material container transform, implemented with `sharedBounds()` because a FAB and a full-screen sheet are completely different composables sharing a spatial relationship.

```kotlin
// Shared key constant to avoid typos
private const val COMPOSE_SURFACE_KEY = "compose-surface-shared"

// Parent screen that toggles FAB / compose surface
@Composable
fun FeedScreen(
    sharedTransitionScope: SharedTransitionScope,
    animatedVisibilityScope: AnimatedVisibilityScope
) {
    var showCompose by rememberSaveable { mutableStateOf(false) }

    Box(modifier = Modifier.fillMaxSize()) {
        // Main feed content...
        FeedList(modifier = Modifier.fillMaxSize())

        // Use AnimatedContent to toggle between FAB and compose surface
        AnimatedContent(
            targetState = showCompose,
            transitionSpec = {
                fadeIn(tween(1)) togetherWith fadeOut(tween(1)) // visibility handled by sharedBounds
            },
            label = "fab_compose_toggle",
            modifier = Modifier.fillMaxSize()
        ) { composing ->
            if (!composing) {
                with(sharedTransitionScope) {
                    FloatingActionButton(
                        onClick = { showCompose = true },
                        shape = CircleShape,
                        containerColor = MaterialTheme.colorScheme.primaryContainer,
                        modifier = Modifier
                            .align(Alignment.BottomEnd)
                            .padding(SpaceL)
                            .sharedBounds(
                                sharedContentState = rememberSharedContentState(
                                    key = COMPOSE_SURFACE_KEY
                                ),
                                animatedVisibilityScope = this@AnimatedContent,
                                clipInOverlayDuringTransition = OverlayClip(CircleShape),
                                boundsTransform = { _, _ ->
                                    spring(stiffness = Spring.StiffnessMediumLow)
                                }
                            )
                    ) {
                        Icon(Icons.Default.Edit, contentDescription = "Compose")
                    }
                }
            } else {
                with(sharedTransitionScope) {
                    Surface(
                        modifier = Modifier
                            .fillMaxSize()
                            .sharedBounds(
                                sharedContentState = rememberSharedContentState(
                                    key = COMPOSE_SURFACE_KEY
                                ),
                                animatedVisibilityScope = this@AnimatedContent,
                                enter = fadeIn(tween(300, delayMillis = 100)),
                                exit = fadeOut(tween(200)),
                                resizeMode = SharedTransitionScope.ResizeMode.ScaleToBounds(),
                                boundsTransform = { _, _ ->
                                    spring(stiffness = Spring.StiffnessMediumLow)
                                }
                            ),
                        color = MaterialTheme.colorScheme.surface,
                        tonalElevation = 3.dp
                    ) {
                        ComposeContent(onDismiss = { showCompose = false })
                    }
                }
            }
        }
    }
}
```

---

## Pattern 4: Text Continuation

A title in a list item continues as the heading in the detail screen. The string is identical in both locations — `sharedElement()` is correct. The system interpolates position and size; the text renders at the destination style throughout.

```kotlin
// List item
@Composable
fun ArticleListItem(
    article: Article,
    sharedTransitionScope: SharedTransitionScope,
    animatedVisibilityScope: AnimatedVisibilityScope,
    onClick: () -> Unit
) {
    with(sharedTransitionScope) {
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .clickable(onClick = onClick)
                .padding(horizontal = SpaceM, vertical = SpaceS)
        ) {
            AsyncImage(
                model = article.thumbnailUrl,
                contentDescription = null,
                contentScale = ContentScale.Crop,
                modifier = Modifier
                    .sharedElement(
                        rememberSharedContentState(key = "article-image-${article.id}"),
                        animatedVisibilityScope = animatedVisibilityScope
                    )
                    .size(72.dp)
                    .clip(MaterialTheme.shapes.small)
            )
            Spacer(modifier = Modifier.width(SpaceM))
            Column(modifier = Modifier.weight(1f)) {
                Text(
                    text = article.title,
                    style = MaterialTheme.typography.titleMedium,
                    maxLines = 2,
                    overflow = TextOverflow.Ellipsis,
                    modifier = Modifier.sharedElement(
                        rememberSharedContentState(key = "article-title-${article.id}"),
                        animatedVisibilityScope = animatedVisibilityScope
                    )
                )
                Text(
                    text = article.publishedAt,
                    style = MaterialTheme.typography.labelSmall,
                    color = MaterialTheme.colorScheme.onSurfaceVariant
                )
            }
        }
    }
}

// Detail screen
@Composable
fun ArticleDetailScreen(
    article: Article,
    sharedTransitionScope: SharedTransitionScope,
    animatedVisibilityScope: AnimatedVisibilityScope,
    onBack: () -> Unit
) {
    with(sharedTransitionScope) {
        Column(
            modifier = Modifier
                .fillMaxSize()
                .verticalScroll(rememberScrollState())
        ) {
            AsyncImage(
                model = article.heroImageUrl,
                contentDescription = article.title,
                contentScale = ContentScale.Crop,
                modifier = Modifier
                    .sharedElement(
                        rememberSharedContentState(key = "article-image-${article.id}"),
                        animatedVisibilityScope = animatedVisibilityScope
                    )
                    .fillMaxWidth()
                    .height(240.dp)
            )

            Column(modifier = Modifier.padding(SpaceM)) {
                Text(
                    text = article.title,
                    style = MaterialTheme.typography.headlineMedium,
                    modifier = Modifier.sharedElement(
                        rememberSharedContentState(key = "article-title-${article.id}"),
                        animatedVisibilityScope = animatedVisibilityScope
                    )
                )
                Spacer(modifier = Modifier.height(SpaceS))
                Text(
                    text = article.body,
                    style = MaterialTheme.typography.bodyLarge,
                    modifier = Modifier.animateEnterExit(
                        enter = fadeIn(tween(300, delayMillis = 200)),
                        exit = fadeOut(tween(100))
                    )
                )
            }
        }
    }
}
```

**Note on text style**: `sharedElement()` interpolates bounds geometry but not typography style. The text renders at the destination style throughout. If you need the *appearance* of the style interpolating, you can animate `fontSize` separately via `animateFloatAsState` — but in practice the geometry interpolation alone produces a convincing continuation effect.

---

## Navigation Integration

### NavHost (Navigation 2) — complete wiring

```kotlin
@Composable
fun AppNavigation() {
    SharedTransitionLayout(modifier = Modifier.fillMaxSize()) {
        val navController = rememberNavController()

        NavHost(
            navController = navController,
            startDestination = HomeRoute
        ) {
            composable<HomeRoute> {
                HomeScreen(
                    sharedTransitionScope = this@SharedTransitionLayout,
                    animatedVisibilityScope = this@composable,
                    onNavigate = { dest -> navController.navigate(dest) }
                )
            }
            composable<DetailRoute> {
                val route: DetailRoute = it.toRoute()
                DetailScreen(
                    route = route,
                    sharedTransitionScope = this@SharedTransitionLayout,
                    animatedVisibilityScope = this@composable,
                    onBack = { navController.popBackStack() }
                )
            }
        }
    }
}
```

### Predictive Back Support

Enable the predictive back gesture (Android 14+) so the back gesture scrubs the shared element transition in reverse:

**AndroidManifest.xml**:
```xml
<application android:enableOnBackInvokedCallback="true">
```

**Version catalog dependency**:
```toml
[versions]
navigation = "2.8.0"  # or newer

[libraries]
androidx-navigation-compose = { module = "androidx.navigation:navigation-compose", version.ref = "navigation" }
```

No code change required beyond the manifest flag — the Navigation Compose library handles the gesture-driven scrubbing automatically.

---

## Pitfalls & Debugging

### 1. Key mismatch — no animation fires

**Symptom**: Navigation works but elements snap instantly with no transition.  
**Root cause**: The key in the source composable doesn't equal the key in the destination.  
**Fix**: Use a constant or string template derived from the same stable ID. Add a log to verify both keys before filing a bug:
```kotlin
Log.d("SharedElement", "key = 'media-image-${item.id}'")
```
Also check: the key type uses structural equality. Data classes work; mutable lists do not.

---

### 2. Scope not threaded — crash or silent fallback

**Symptom**: `IllegalStateException: No SharedTransitionScope found` or `NullPointerException` when trying to call `sharedElement()`.  
**Root cause**: The composable calling `sharedElement()` is not inside a `with(sharedTransitionScope) { }` block, or `SharedTransitionLayout` doesn't wrap the part of the tree where both screens live.  
**Fix**: Verify `SharedTransitionLayout` wraps the entire NavHost. Use the `with(sharedTransitionScope) { }` receiver idiom or CompositionLocal. Check that `animatedVisibilityScope` is the correct `this@composable` reference, not one from an outer or unrelated scope.

---

### 3. Z-ordering — wrong element renders on top

**Symptom**: During the transition, the destination element appears underneath the source element (or vice versa), creating a visual jump.  
**Root cause**: Default z-ordering puts elements in tree order, which may not match the desired visual layering during the transition.  
**Fix**: Set `zIndexInOverlay` on the element that should render on top:
```kotlin
Modifier.sharedBounds(
    sharedContentState = rememberSharedContentState(key = "hero-${item.id}"),
    animatedVisibilityScope = animatedVisibilityScope,
    zIndexInOverlay = 1f
)
```

---

### 4. Missing renderInSharedTransitionScope — element disappears

**Symptom**: A UI element (FAB, back button, toolbar) that only exists on the destination screen is invisible during the transition and blinks into existence at the end.  
**Root cause**: The element is not participating in the shared overlay layer, so it renders behind the transitioning content.  
**Fix**: Apply `renderInSharedTransitionScope` to elements that should be visible during the transition but don't have a matching shared element key on the source screen. Pair it with `animateEnterExit` to fade it in smoothly.

---

### 5. Non-stable keys — animation fires on every recompose

**Symptom**: Shared element animations trigger unexpectedly during unrelated state updates, causing jitter.  
**Root cause**: The key passed to `rememberSharedContentState()` is computed from an unstable value (e.g., a list index, a random UUID generated on each call, or an object without structural equality).  
**Fix**: Keys must be stable across recompositions. Use entity IDs from your data model. If you need composite keys, use a data class:
```kotlin
data class ContentSharedKey(val contentId: Long, val surface: String)
// "surface" disambiguates the same content appearing in multiple contexts
```

---

### 6. Conflicting clip shapes — visual artifacts during transition

**Symptom**: During the transition, the shared element has incorrect or ugly clipping — visible corners or edge artefacts that don't match either the source or destination shape.  
**Root cause**: `clipInOverlayDuringTransition` is not set, so the system uses a default clip that doesn't match your card's shape. Or different clip shapes are applied via `Modifier.clip()` before `sharedBounds()`.  
**Fix**: Pass an `OverlayClip` with the source shape to `clipInOverlayDuringTransition`, and avoid applying `Modifier.clip()` before the `sharedBounds()` modifier. Let `sharedBounds()` manage the clipping during the transition:
```kotlin
val cardShape = RoundedCornerShape(16.dp)

Modifier.sharedBounds(
    sharedContentState = rememberSharedContentState(key = "card-${item.id}"),
    animatedVisibilityScope = animatedVisibilityScope,
    clipInOverlayDuringTransition = OverlayClip(cardShape)
)
```
