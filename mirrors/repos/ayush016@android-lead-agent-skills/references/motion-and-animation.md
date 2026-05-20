# Motion & Animation — Complete Reference

> Shared element transitions have their own dedicated file: `shared-element-transitions.md`

Animation is not decoration. Every motion should communicate something: that a new element has arrived, that a process is in progress, that content is loading, that an action succeeded. Motion that communicates nothing costs the user attention for no return.

---

## AnimatedVisibility

The workhorse for showing and hiding composables with animated enter/exit.

### Basic Usage

```kotlin
AnimatedVisibility(
    visible = isExpanded,
    enter = fadeIn(tween(300)) + expandVertically(expandFrom = Alignment.Top),
    exit = fadeOut(tween(200)) + shrinkVertically(shrinkTowards = Alignment.Top)
) {
    ExpandedContent()
}
```

### Stagger Pattern for Lists

Staggering list item entry creates a sense of the list flowing in, rather than slamming into place all at once. The formula: `delay = index * 30ms`, capped at `min(index * 30, 300)` to prevent late-arriving items from feeling disconnected.

```kotlin
@Composable
fun StaggeredList(items: List<FeedItem>) {
    var isVisible by remember { mutableStateOf(false) }

    LaunchedEffect(Unit) { isVisible = true }

    Column {
        items.forEachIndexed { index, item ->
            val delay = (index * 40).coerceAtMost(300)
            AnimatedVisibility(
                visible = isVisible,
                enter = fadeIn(tween(durationMillis = 300, delayMillis = delay)) +
                        slideInVertically(
                            animationSpec = tween(durationMillis = 300, delayMillis = delay),
                            initialOffsetY = { it / 3 }
                        )
            ) {
                FeedItemRow(item = item)
            }
        }
    }
}
```

### animateEnterExit — Element-Level Choreography

When the parent `AnimatedVisibility` controls the overall visibility but a child element needs its own timing within that animation:

```kotlin
AnimatedVisibility(
    visible = showPanel,
    enter = fadeIn(),
    exit = fadeOut()
) {
    Box {
        PanelBackground()  // fades with parent

        ActionButton(
            modifier = Modifier.animateEnterExit(
                enter = slideInVertically(
                    animationSpec = tween(300, delayMillis = 100),
                    initialOffsetY = { it / 2 }
                ),
                exit = slideOutVertically(tween(150))
            )
        )
    }
}
```

---

## animate*AsState Family

### Choosing Spring vs Tween

**Spring**: Use for direct manipulation, state changes the user caused (toggling a switch, pressing a button). The physics-based overshoot feels like the UI is responding, not executing.

```kotlin
val elevation by animateDpAsState(
    targetValue = if (isPressed) 8.dp else 2.dp,
    animationSpec = spring(
        stiffness = Spring.StiffnessHigh,
        dampingRatio = Spring.DampingRatioNoBouncy
    ),
    label = "card_elevation"
)
```

**Tween**: Use for programmatic state changes (loading → content, pagination, tab switching) where precise timing matters and bounce would feel incorrect.

```kotlin
val alpha by animateFloatAsState(
    targetValue = if (isLoaded) 1f else 0f,
    animationSpec = tween(durationMillis = 400, easing = FastOutSlowInEasing),
    label = "content_alpha"
)
```

**Snap**: Use when you need instant state change with no animation — useful inside complex animation sequences where you're managing each piece yourself.

```kotlin
val position by animateOffsetAsState(
    targetValue = targetOffset,
    animationSpec = snap(),
    label = "instant_position"
)
```

### Custom Easing

```kotlin
val OvershootEasing = Easing { fraction ->
    val tension = 2.5f
    val adjusted = fraction - 1f
    adjusted * adjusted * ((tension + 1) * adjusted + tension) + 1f
}

val smoothExpand by animateFloatAsState(
    targetValue = if (expanded) 1f else 0f,
    animationSpec = tween(500, easing = OvershootEasing),
    label = "smooth_expand"
)
```

---

## Animatable — Gesture-Coupled Animation

Use `Animatable` when animation targets change continuously (drag, swipe) rather than discretely.

### Drag-to-Dismiss

```kotlin
@Composable
fun DismissibleCard(
    onDismiss: () -> Unit,
    content: @Composable () -> Unit
) {
    val offsetX = remember { Animatable(0f) }
    val coroutineScope = rememberCoroutineScope()
    val dismissThreshold = 200.dp.dpToPx()

    Box(
        modifier = Modifier
            .graphicsLayer { translationX = offsetX.value }
            .pointerInput(Unit) {
                detectHorizontalDragGestures(
                    onHorizontalDrag = { _, dragAmount ->
                        coroutineScope.launch {
                            offsetX.snapTo(offsetX.value + dragAmount)
                        }
                    },
                    onDragEnd = {
                        coroutineScope.launch {
                            if (abs(offsetX.value) > dismissThreshold) {
                                // Fling off screen
                                offsetX.animateTo(
                                    targetValue = if (offsetX.value > 0) 2000f else -2000f,
                                    animationSpec = tween(300, easing = FastOutLinearInEasing)
                                )
                                onDismiss()
                            } else {
                                // Spring back
                                offsetX.animateTo(
                                    targetValue = 0f,
                                    animationSpec = spring(stiffness = Spring.StiffnessMedium)
                                )
                            }
                        }
                    }
                )
            }
    ) {
        content()
    }
}
```

### Swipe-to-Reveal Action

```kotlin
@Composable
fun SwipeRevealRow(
    actions: @Composable RowScope.() -> Unit,
    content: @Composable () -> Unit
) {
    val actionsWidth = 96.dp.dpToPx()
    val offsetX = remember { Animatable(0f) }
    val scope = rememberCoroutineScope()

    Box {
        Row(
            modifier = Modifier.matchParentSize(),
            horizontalArrangement = Arrangement.End
        ) { actions() }

        Box(
            modifier = Modifier
                .graphicsLayer { translationX = offsetX.value }
                .pointerInput(Unit) {
                    detectHorizontalDragGestures(
                        onHorizontalDrag = { _, drag ->
                            scope.launch {
                                val clamped = (offsetX.value + drag).coerceIn(-actionsWidth, 0f)
                                offsetX.snapTo(clamped)
                            }
                        },
                        onDragEnd = {
                            scope.launch {
                                val snap = if (offsetX.value < -actionsWidth / 2) -actionsWidth else 0f
                                offsetX.animateTo(snap, spring(stiffness = Spring.StiffnessMedium))
                            }
                        }
                    )
                }
        ) { content() }
    }
}
```

---

## updateTransition — Multi-Property State Machines

Use `updateTransition` when multiple properties must animate together in sync when state changes — for example, a button that morphs from one visual state to another.

```kotlin
enum class ButtonState { Idle, Loading, Success, Error }

@Composable
fun MorphingButton(
    state: ButtonState,
    onClick: () -> Unit
) {
    val transition = updateTransition(targetState = state, label = "button_state")

    val containerColor by transition.animateColor(
        label = "button_color",
        transitionSpec = { tween(400) }
    ) { buttonState ->
        when (buttonState) {
            ButtonState.Idle    -> MaterialTheme.colorScheme.primary
            ButtonState.Loading -> MaterialTheme.colorScheme.surfaceVariant
            ButtonState.Success -> Color(0xFF2E7D32)
            ButtonState.Error   -> MaterialTheme.colorScheme.error
        }
    }

    val cornerRadius by transition.animateDp(
        label = "button_radius",
        transitionSpec = { spring(stiffness = Spring.StiffnessMediumLow) }
    ) { buttonState ->
        when (buttonState) {
            ButtonState.Loading -> AppRadius.Full
            else -> AppRadius.Small
        }
    }

    val iconAlpha by transition.animateFloat(
        label = "icon_alpha",
        transitionSpec = { tween(300) }
    ) { buttonState ->
        if (buttonState == ButtonState.Loading) 0f else 1f
    }

    Button(
        onClick = { if (state == ButtonState.Idle) onClick() },
        colors = ButtonDefaults.buttonColors(containerColor = containerColor),
        shape = RoundedCornerShape(cornerRadius)
    ) {
        AnimatedContent(state, label = "button_icon") { currentState ->
            when (currentState) {
                ButtonState.Loading -> CircularProgressIndicator(
                    modifier = Modifier.size(20.dp),
                    color = MaterialTheme.colorScheme.primary,
                    strokeWidth = 2.dp
                )
                ButtonState.Success -> Icon(Icons.Default.Check, contentDescription = "Success")
                ButtonState.Error   -> Icon(Icons.Default.Close, contentDescription = "Error")
                ButtonState.Idle    -> Text("Submit")
            }
        }
    }
}
```

---

## InfiniteTransition — Shimmer, Pulse, Breathing

**Warning**: `InfiniteTransition` always runs, even when the composable is not visible. If used inside a `LazyColumn`, prefer composables that only compose when visible and cancel the infinite animation on exit. Never use `InfiniteTransition` for more than 2–3 concurrent properties — each animator costs composition time every frame.

### Pulse Indicator

```kotlin
@Composable
fun PulseIndicator(
    color: Color = MaterialTheme.colorScheme.primary,
    modifier: Modifier = Modifier
) {
    val transition = rememberInfiniteTransition(label = "pulse")

    val scale by transition.animateFloat(
        initialValue = 1f,
        targetValue = 1.2f,
        animationSpec = infiniteRepeatable(
            animation = tween(700, easing = FastOutSlowInEasing),
            repeatMode = RepeatMode.Reverse
        ),
        label = "pulse_scale"
    )

    val alpha by transition.animateFloat(
        initialValue = 0.8f,
        targetValue = 0.3f,
        animationSpec = infiniteRepeatable(
            animation = tween(700, easing = FastOutSlowInEasing),
            repeatMode = RepeatMode.Reverse
        ),
        label = "pulse_alpha"
    )

    Box(
        modifier = modifier
            .scale(scale)
            .size(12.dp)
            .background(color.copy(alpha = alpha), CircleShape)
    )
}
```

### Breathing Background (subtle premium effect)

```kotlin
@Composable
fun BreathingGradientBackground(modifier: Modifier = Modifier) {
    val transition = rememberInfiniteTransition(label = "breathing")
    val offset by transition.animateFloat(
        initialValue = 0f,
        targetValue = 1f,
        animationSpec = infiniteRepeatable(
            animation = tween(4000, easing = LinearEasing),
            repeatMode = RepeatMode.Reverse
        ),
        label = "gradient_offset"
    )

    val primary = MaterialTheme.colorScheme.primaryContainer
    val secondary = MaterialTheme.colorScheme.secondaryContainer

    Box(
        modifier = modifier
            .fillMaxSize()
            .drawBehind {
                drawRect(
                    brush = Brush.linearGradient(
                        colors = listOf(primary, secondary, primary),
                        start = Offset(size.width * offset, 0f),
                        end = Offset(size.width * (offset + 1f), size.height)
                    )
                )
            }
    )
}
```

---

## AnimatedContent — Content Transitions

### Tab Switching with Slide Direction

```kotlin
@Composable
fun TabContent(
    selectedTab: Int,
    content: @Composable (Int) -> Unit
) {
    var previousTab by remember { mutableIntStateOf(selectedTab) }

    AnimatedContent(
        targetState = selectedTab,
        transitionSpec = {
            val direction = if (targetState > previousTab) 1 else -1
            slideInHorizontally { it * direction } + fadeIn(tween(200)) togetherWith
            slideOutHorizontally { -it * direction } + fadeOut(tween(150))
        },
        label = "tab_content"
    ) { tab ->
        SideEffect { previousTab = tab }
        content(tab)
    }
}
```

### Size-Animating Counter

```kotlin
@Composable
fun AnimatedCounter(count: Int, modifier: Modifier = Modifier) {
    AnimatedContent(
        targetState = count,
        transitionSpec = {
            if (targetState > initialState) {
                slideInVertically { -it } + fadeIn() togetherWith
                slideOutVertically { it } + fadeOut()
            } else {
                slideInVertically { it } + fadeIn() togetherWith
                slideOutVertically { -it } + fadeOut()
            }
        },
        label = "counter"
    ) { value ->
        Text(
            text = value.toString(),
            style = MaterialTheme.typography.titleLarge,
            modifier = modifier
        )
    }
}
```

---

## Canvas Animation

### Custom Arc Progress Ring

```kotlin
@Composable
fun ArcProgressRing(
    progress: Float, // 0f to 1f
    strokeWidth: Dp = 8.dp,
    color: Color = MaterialTheme.colorScheme.primary,
    trackColor: Color = MaterialTheme.colorScheme.surfaceVariant,
    modifier: Modifier = Modifier
) {
    val animatedProgress by animateFloatAsState(
        targetValue = progress,
        animationSpec = tween(1000, easing = FastOutSlowInEasing),
        label = "arc_progress"
    )

    Canvas(modifier = modifier.size(80.dp)) {
        val strokePx = strokeWidth.toPx()
        val diameter = size.minDimension - strokePx
        val topLeft = Offset(strokePx / 2, strokePx / 2)
        val arcSize = Size(diameter, diameter)
        val startAngle = -90f
        val sweepAngle = 360f * animatedProgress

        // Track
        drawArc(
            color = trackColor,
            startAngle = startAngle,
            sweepAngle = 360f,
            useCenter = false,
            topLeft = topLeft,
            size = arcSize,
            style = Stroke(width = strokePx, cap = StrokeCap.Round)
        )

        // Progress
        drawArc(
            brush = Brush.sweepGradient(
                colors = listOf(color.copy(alpha = 0.6f), color)
            ),
            startAngle = startAngle,
            sweepAngle = sweepAngle,
            useCenter = false,
            topLeft = topLeft,
            size = arcSize,
            style = Stroke(width = strokePx, cap = StrokeCap.Round)
        )
    }
}
```

### Path Morph Animation (star ↔ circle)

```kotlin
@Composable
fun MorphingShape(isCircle: Boolean, modifier: Modifier = Modifier) {
    val progress by animateFloatAsState(
        targetValue = if (isCircle) 1f else 0f,
        animationSpec = spring(stiffness = Spring.StiffnessLow),
        label = "morph_progress"
    )

    Canvas(modifier = modifier.size(60.dp)) {
        val path = Path()
        val cx = size.width / 2f
        val cy = size.height / 2f
        val outerRadius = size.minDimension / 2f
        val innerRadius = outerRadius * lerp(0.4f, 1f, progress)
        val points = 5
        val rotation = -Math.PI / 2.0

        path.moveTo(
            cx + outerRadius * cos(rotation).toFloat(),
            cy + outerRadius * sin(rotation).toFloat()
        )

        for (i in 1 until points * 2) {
            val angle = rotation + i * Math.PI / points
            val r = if (i % 2 == 0) outerRadius else innerRadius
            path.lineTo(
                cx + r * cos(angle).toFloat(),
                cy + r * sin(angle).toFloat()
            )
        }
        path.close()

        drawPath(path, color = MaterialTheme.colorScheme.primary)
    }
}
```

---

## Spring Physics — Tuning Guide

The feel of your app lives in these numbers. Choose deliberately.

| Stiffness Preset | Feel | Use For |
|---|---|---|
| `Spring.StiffnessVeryHigh` | Snappy, instant-feeling | Toggle switches, checkboxes |
| `Spring.StiffnessHigh` | Fast, crisp | Press feedback, button scale |
| `Spring.StiffnessMedium` | Balanced, responsive | Cards, panels, shared elements |
| `Spring.StiffnessMediumLow` | Relaxed, flowing | Container transforms, FAB morphs |
| `Spring.StiffnessLow` | Slow, gentle | Background effects, ambient motion |

| Damping Preset | Feel | Use For |
|---|---|---|
| `DampingRatioHighBouncy` | Very springy overshoot | Playful, gamified UIs |
| `DampingRatioMediumBouncy` | Noticeable bounce | List item arrival, success state |
| `DampingRatioLowBouncy` | Subtle settle | Headers, navigation |
| `DampingRatioNoBouncy` | Clean, no overshoot | Professional, content-heavy apps |

```kotlin
// The "feels right" spring for most UI — balanced, no bounce, medium speed
val defaultSpring = spring<Float>(
    stiffness = Spring.StiffnessMedium,
    dampingRatio = Spring.DampingRatioNoBouncy
)

// For container transforms (card expansions, FAB morphs)
val containerTransformSpring = spring<Float>(
    stiffness = Spring.StiffnessMediumLow,
    dampingRatio = Spring.DampingRatioNoBouncy
)
```

---

## Motion Choreography Principles

These rules produce motion that feels intentional, not random:

1. **Enter with ease-out, exit with ease-in.** Content arriving slows to a stop (eases out), signalling it has reached its destination. Content leaving accelerates away (eases in), signalling it's departing. `FastOutSlowInEasing` for enter; `FastOutLinearInEasing` for exit.

2. **Stagger arrivals by ~30–40ms per item.** Never stagger more than 300ms total, or the last item feels forgotten. Formula: `delay = min(index * 35, 300)` milliseconds.

3. **Enter before exit.** When replacing content (tab switching, navigation), the new content should begin its enter animation at or slightly before the old content begins exiting. Crossing animations communicate "something new is here." Sequential animations (first out, then in) communicate "something is loading."

4. **Coordinate opacity with geometry.** A card expanding that also fades in opacity during expansion looks richer than geometry alone. `fadeIn()` synchronized with `expandVertically()` is a one-line addition that doubles perceived quality.

5. **Reserve bounce for celebration.** `DampingRatioMediumBouncy` feels playful. Use it for success states, first-time experiences, and achievement moments. Never use it on everyday navigational actions — it reads as immature.

6. **Duration budget**: Navigation transitions 300–500ms. UI feedback (button press) 100–200ms. Loading completion 400–600ms. Never exceed 600ms for any single motion that isn't an illustrative animation.
