# Accessibility — Semantics, TalkBack, Focus, Contrast

Accessibility is not a compliance checkbox. It is the difference between an app that works for everyone and one that works for some. Screen readers, switch access, keyboard navigation, large text, and high contrast are not edge cases — they are the daily reality for hundreds of millions of people. An inaccessible screen is an unfinished screen.

---

## Semantic Properties — the foundation

Compose exposes a semantic tree that accessibility services (TalkBack, Switch Access, Voice Access) use to understand your UI. Every meaningful composable must have correct semantics.

### contentDescription

```kotlin
// Image — always provide a description or mark explicitly as decorative
AsyncImage(
    model = article.imageUrl,
    contentDescription = "${article.title} cover image" // meaningful
)

AsyncImage(
    model = decorativeBannerUrl,
    contentDescription = null // explicitly decorative — TalkBack skips it
)

// Icon alone — needs description
Icon(
    imageVector = Icons.Default.Favorite,
    contentDescription = "Add to favorites" // describes the action, not the icon name
)

// Icon + Label — description on the icon is redundant, provide null
Row {
    Icon(Icons.Default.Star, contentDescription = null) // label provides context
    Text("5 stars")
}
```

### Role declaration for custom components

```kotlin
// Custom card that acts as a button
Card(
    onClick = onClick,
    modifier = Modifier.semantics {
        role = Role.Button
        contentDescription = "Article: ${article.title}. Double-tap to open."
    }
) { ... }

// Custom toggle
Box(
    modifier = Modifier
        .toggleable(
            value = isChecked,
            onValueChange = onCheckedChange,
            role = Role.Checkbox
        )
        .semantics {
            stateDescription = if (isChecked) "Checked" else "Unchecked"
        }
) { ... }

// Custom tab
Row(
    modifier = Modifier.selectable(
        selected = isSelected,
        onClick = onClick,
        role = Role.Tab
    )
) { ... }
```

### stateDescription — describe dynamic state

```kotlin
// Expandable section
Column(
    modifier = Modifier.semantics {
        contentDescription = "Details section"
        stateDescription = if (isExpanded) "Expanded" else "Collapsed"
    }
) {
    Row(
        modifier = Modifier.clickable(onClick = { isExpanded = !isExpanded })
    ) {
        Text("Details")
        Icon(
            if (isExpanded) Icons.Default.ExpandLess else Icons.Default.ExpandMore,
            contentDescription = null // state described by parent stateDescription
        )
    }
    if (isExpanded) { ExpandedContent() }
}

// Loading state
Box(
    modifier = Modifier.semantics {
        contentDescription = "Article list"
        stateDescription = when (uiState) {
            is ArticleUiState.Loading -> "Loading articles"
            is ArticleUiState.Ready -> "${uiState.articles.size} articles loaded"
            is ArticleUiState.Error -> "Error loading articles"
        }
    }
) { ... }
```

---

## Custom Accessibility Actions

Provide shortcuts for complex interactions that would be difficult with linear navigation:

```kotlin
// Swipeable list item — provide semantic action for the swipe gesture
@Composable
fun DismissibleRow(
    item: Article,
    onDismiss: () -> Unit,
    content: @Composable () -> Unit
) {
    val swipeState = rememberSwipeToDismissBoxState(
        confirmValueChange = { it == SwipeToDismissBoxValue.EndToStart }
    )

    Box(
        modifier = Modifier.semantics {
            customActions = listOf(
                CustomAccessibilityAction(
                    label = "Dismiss article",
                    action = {
                        onDismiss()
                        true
                    }
                )
            )
        }
    ) {
        SwipeToDismissBox(state = swipeState, ...) { content() }
    }
}

// Long list item with multiple actions
@Composable
fun ArticleCard(
    article: Article,
    onOpen: () -> Unit,
    onShare: () -> Unit,
    onSave: () -> Unit
) {
    Card(
        modifier = Modifier.semantics {
            contentDescription = article.title
            customActions = listOf(
                CustomAccessibilityAction("Open article") { onOpen(); true },
                CustomAccessibilityAction("Share article") { onShare(); true },
                CustomAccessibilityAction("Save article") { onSave(); true }
            )
        }
    ) {
        // card content
    }
}
```

---

## Focus Management

### focusRequester — move focus programmatically

```kotlin
@Composable
fun SearchBar(onClose: () -> Unit) {
    val focusRequester = remember { FocusRequester() }

    LaunchedEffect(Unit) {
        // Focus the search field immediately when the bar appears
        focusRequester.requestFocus()
    }

    OutlinedTextField(
        value = query,
        onValueChange = { query = it },
        placeholder = { Text("Search articles") },
        modifier = Modifier
            .fillMaxWidth()
            .focusRequester(focusRequester)
    )
}
```

### focusProperties — control focus traversal

```kotlin
// Skip a non-interactive overlay element from focus traversal
Box(
    modifier = Modifier.focusProperties { canFocus = false }
) {
    DecorativeOverlay()
}

// Define custom focus order
val (first, second, third) = remember { FocusRequester.createRefs() }

Column {
    Button(
        onClick = {},
        modifier = Modifier
            .focusRequester(first)
            .focusProperties { next = second }
    ) { Text("First") }

    Button(
        onClick = {},
        modifier = Modifier
            .focusRequester(second)
            .focusProperties { previous = first; next = third }
    ) { Text("Second") }
}
```

### onFocusChanged — visual feedback for focus

```kotlin
@Composable
fun AccessibleCard(onClick: () -> Unit, content: @Composable () -> Unit) {
    var isFocused by remember { mutableStateOf(false) }

    Card(
        onClick = onClick,
        modifier = Modifier
            .onFocusChanged { isFocused = it.isFocused }
            .then(
                if (isFocused) Modifier.border(
                    width = 2.dp,
                    color = MaterialTheme.colorScheme.primary,
                    shape = MaterialTheme.shapes.medium
                ) else Modifier
            )
    ) { content() }
}
```

---

## Touch Targets — Minimum 48dp × 48dp

```kotlin
// Icon button that's visually smaller than 48dp — wrap to ensure 48dp touch target
IconButton(
    onClick = onClick,
    modifier = Modifier.size(48.dp) // explicit 48dp even if icon is 24dp
) {
    Icon(
        imageVector = Icons.Default.Close,
        contentDescription = "Close",
        modifier = Modifier.size(24.dp) // visual size separate from touch target
    )
}

// For custom clickable areas, ensure minimum size
Box(
    modifier = Modifier
        .defaultMinSize(minWidth = 48.dp, minHeight = 48.dp)
        .clickable(onClick = onClick)
)
```

---

## Live Regions — announce dynamic changes

```kotlin
// Announce count changes to screen readers without moving focus
Text(
    text = "Showing ${filteredCount} of ${totalCount} items",
    modifier = Modifier.semantics {
        liveRegion = LiveRegionMode.Polite // announce on change without interrupting
    }
)

// For urgent announcements (error states)
Text(
    text = errorMessage,
    color = MaterialTheme.colorScheme.error,
    modifier = Modifier.semantics {
        liveRegion = LiveRegionMode.Assertive // interrupt current announcement
    }
)
```

---

## Merged vs Unmerged Semantics

By default, clickable containers merge child semantics into a single accessibility node — which is usually what you want for cards. Control explicitly when needed:

```kotlin
// Merge all child content descriptions into one tappable node (default for clickable)
Card(
    onClick = onClick,
    modifier = Modifier.semantics(mergeDescendants = true) {
        // All child Text/Image descriptions merged here
    }
) {
    Text(article.title) // merged into card's semantic node
    Text(article.summary) // merged into card's semantic node
}

// Prevent merging — each child is its own accessibility node
Row(
    modifier = Modifier.semantics(mergeDescendants = false) {}
) {
    Text(article.title) // separate node
    IconButton(onClick = onShare) { // separate node with its own action
        Icon(Icons.Default.Share, contentDescription = "Share")
    }
}
```

---

## Colour Contrast

WCAG AA requirements (minimum):
- Normal text (< 18sp or < 14sp bold): **4.5:1** contrast ratio
- Large text (≥ 18sp or ≥ 14sp bold): **3:1** contrast ratio
- UI components and graphical objects: **3:1** contrast ratio

```kotlin
// Verify your token pairs meet contrast requirements:
// MaterialTheme.colorScheme.onPrimary on Primary → typically 7:1+ (WCAG AAA)
// MaterialTheme.colorScheme.onSurface on Surface → verify in your specific palette
// MaterialTheme.colorScheme.onSurfaceVariant on SurfaceVariant → often marginal — check

// Use Material Theme Builder or contrast checker tools to verify all pairs:
// https://m3.material.io/theme-builder#/custom
// https://webaim.org/resources/contrastchecker/
```

---

## Accessibility Testing

### Automated — Espresso Accessibility Checks

```kotlin
@RunWith(AndroidJUnit4::class)
class AccessibilityTest {
    @get:Rule
    val accessibilityRule = AccessibilityChecksRule()

    @Test
    fun article_card_passes_accessibility_checks() {
        onView(withId(R.id.article_card))
            .check(ViewAssertions.matches(isDisplayed()))
        // AccessibilityChecksRule automatically runs checks on every interaction
    }
}
```

### Manual — TalkBack testing checklist

1. Enable TalkBack (Settings → Accessibility → TalkBack)
2. Navigate the entire screen using only swipe gestures
3. Verify every interactive element is reachable and announced correctly
4. Verify state changes are announced (loading → loaded, error messages)
5. Verify focus order is logical (top-left to bottom-right in LTR)
6. Disable TalkBack and test with Switch Access (single switch, two-switch)

### Compose semantics debugging

```kotlin
// Print semantic tree in tests
composeTestRule.onRoot().printToLog("Semantics")

// Find nodes by semantics
composeTestRule
    .onNode(
        hasContentDescription("Add to favorites") and hasClickAction()
    )
    .assertIsDisplayed()
    .performClick()

// Verify no element is missing a content description
composeTestRule
    .onAllNodes(hasTestTag("article_image"))
    .onEach {
        it.assertContentDescriptionIsNotEmpty()
    }
```
