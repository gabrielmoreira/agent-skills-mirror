# Theming & Color — Material 3 Token System, 29 Roles, Custom Extensions

The most common theming failure in Android apps is not using the wrong blue — it is using only four of Material 3's twenty-nine color roles and leaving the other twenty-five at their grey-and-purple defaults. The result is an app that looks like every other uncustomised Material app: correct, but anonymous. This guide builds a theming system with the full depth the platform offers.

---

## The Three-Layer Token Architecture

Every color value in a production design system passes through three layers before reaching a composable. Collapsing these layers — writing hex codes directly in composables, or mapping primitive tokens straight to components — is the root cause of weak, inflexible theming.

```
Layer 1: Primitive Tokens   — raw color values (hex codes). Internal only.
Layer 2: Semantic Tokens    — role-named mappings (what the color means).
Layer 3: Component Tokens   — per-component overrides (where needed).
```

### Layer 1 — Primitive Tokens

Define every hex value in one place. These are `internal` — nothing outside the theme module touches them directly. Name them by hue and tone, not by purpose.

```kotlin
// core/ui/src/main/kotlin/com/example/core/ui/theme/primitives/ColorPrimitives.kt
internal object ColorPrimitives {

    // Indigo palette (10 = darkest, 99 = lightest)
    val Indigo10  = Color(0xFF0A0030)
    val Indigo20  = Color(0xFF1A0060)
    val Indigo30  = Color(0xFF2A008F)
    val Indigo40  = Color(0xFF3D00C7)   // primary in light mode
    val Indigo80  = Color(0xFFBBA3FF)   // primary in dark mode
    val Indigo90  = Color(0xFFE2D9FF)
    val Indigo95  = Color(0xFFF1ECFF)
    val Indigo99  = Color(0xFFFFFBFF)

    // Coral palette
    val Coral10   = Color(0xFF2B0000)
    val Coral20   = Color(0xFF4E1A00)
    val Coral30   = Color(0xFF7A2E00)
    val Coral40   = Color(0xFFAA4800)
    val Coral80   = Color(0xFFFFB685)
    val Coral90   = Color(0xFFFFDCBE)

    // Teal palette (secondary)
    val Teal30    = Color(0xFF004D48)
    val Teal40    = Color(0xFF006B63)
    val Teal80    = Color(0xFF50D8CD)
    val Teal90    = Color(0xFF74F5EA)

    // Neutral (surface/background tones)
    val Grey10    = Color(0xFF1C1B1F)
    val Grey12    = Color(0xFF201F23)
    val Grey17    = Color(0xFF2A2930)
    val Grey22    = Color(0xFF36343B)
    val Grey87    = Color(0xFFDEDDE2)
    val Grey90    = Color(0xFFE7E0EC)
    val Grey95    = Color(0xFFF4EFF4)
    val Grey99    = Color(0xFFFFFBFE)

    // Neutral variant (surfaceVariant tones)
    val NeutralVariant30 = Color(0xFF4A4458)
    val NeutralVariant50 = Color(0xFF7A7289)
    val NeutralVariant60 = Color(0xFF958DA5)
    val NeutralVariant80 = Color(0xFFCAC4D0)
    val NeutralVariant90 = Color(0xFFE7DFF6)

    // Error (fixed — same in all brands)
    val Red10  = Color(0xFF410002)
    val Red40  = Color(0xFFBA1A1A)
    val Red80  = Color(0xFFFFB4AB)
    val Red90  = Color(0xFFFFDAD6)
}
```

### Layer 2 — Semantic Tokens (Material 3 ColorScheme)

Map primitives to the 29 Material 3 color roles. Define both light and dark schemes completely — no role should be left at the Material baseline default.

```kotlin
// core/ui/src/main/kotlin/com/example/core/ui/theme/ColorSchemes.kt
internal val AppLightColorScheme = lightColorScheme(
    // — Primary group —
    primary             = ColorPrimitives.Indigo40,
    onPrimary           = Color.White,
    primaryContainer    = ColorPrimitives.Indigo90,
    onPrimaryContainer  = ColorPrimitives.Indigo10,
    inversePrimary      = ColorPrimitives.Indigo80,

    // — Secondary group —
    secondary           = ColorPrimitives.Teal40,
    onSecondary         = Color.White,
    secondaryContainer  = ColorPrimitives.Teal90,
    onSecondaryContainer = ColorPrimitives.Teal30,

    // — Tertiary group (warm accent for visual balance) —
    tertiary            = ColorPrimitives.Coral40,
    onTertiary          = Color.White,
    tertiaryContainer   = ColorPrimitives.Coral90,
    onTertiaryContainer = ColorPrimitives.Coral10,

    // — Error group —
    error               = ColorPrimitives.Red40,
    onError             = Color.White,
    errorContainer      = ColorPrimitives.Red90,
    onErrorContainer    = ColorPrimitives.Red10,

    // — Surface group (the majority of your app's backgrounds) —
    background          = ColorPrimitives.Grey99,
    onBackground        = ColorPrimitives.Grey10,
    surface             = ColorPrimitives.Grey99,
    onSurface           = ColorPrimitives.Grey10,
    surfaceVariant      = ColorPrimitives.NeutralVariant90,
    onSurfaceVariant    = ColorPrimitives.NeutralVariant30,
    surfaceTint         = ColorPrimitives.Indigo40,
    inverseSurface      = ColorPrimitives.Grey22,
    inverseOnSurface    = ColorPrimitives.Grey95,

    // — Outline group —
    outline             = ColorPrimitives.NeutralVariant50,
    outlineVariant      = ColorPrimitives.NeutralVariant80,
    scrim               = Color.Black,
)

internal val AppDarkColorScheme = darkColorScheme(
    primary             = ColorPrimitives.Indigo80,
    onPrimary           = ColorPrimitives.Indigo20,
    primaryContainer    = ColorPrimitives.Indigo30,
    onPrimaryContainer  = ColorPrimitives.Indigo90,
    inversePrimary      = ColorPrimitives.Indigo40,

    secondary           = ColorPrimitives.Teal80,
    onSecondary         = ColorPrimitives.Teal30,
    secondaryContainer  = ColorPrimitives.Teal30,
    onSecondaryContainer = ColorPrimitives.Teal90,

    tertiary            = ColorPrimitives.Coral80,
    onTertiary          = ColorPrimitives.Coral20,
    tertiaryContainer   = ColorPrimitives.Coral30,
    onTertiaryContainer = ColorPrimitives.Coral90,

    error               = ColorPrimitives.Red80,
    onError             = ColorPrimitives.Red10,
    errorContainer      = ColorPrimitives.Red40,
    onErrorContainer    = ColorPrimitives.Red90,

    background          = ColorPrimitives.Grey10,
    onBackground        = ColorPrimitives.Grey90,
    surface             = ColorPrimitives.Grey10,
    onSurface           = ColorPrimitives.Grey90,
    surfaceVariant      = ColorPrimitives.NeutralVariant30,
    onSurfaceVariant    = ColorPrimitives.NeutralVariant80,
    surfaceTint         = ColorPrimitives.Indigo80,
    inverseSurface      = ColorPrimitives.Grey87,
    inverseOnSurface    = ColorPrimitives.Grey22,

    outline             = ColorPrimitives.NeutralVariant60,
    outlineVariant      = ColorPrimitives.NeutralVariant30,
    scrim               = Color.Black,
)
```

---

## All 29 Color Roles — When to Use Each

This is the section most developers skip and the reason most apps look flat.

### Primary Group (most prominent actions)

| Role | Use |
|------|-----|
| `primary` | Filled buttons, active state indicators, FABs, navigation active icons |
| `onPrimary` | Text and icons placed directly on `primary` surfaces |
| `primaryContainer` | Tinted backgrounds for selected chips, highlighted cards, active tab backgrounds |
| `onPrimaryContainer` | Text and icons on `primaryContainer` backgrounds |
| `inversePrimary` | Primary-equivalent color for use on `inverseSurface` (e.g. snackbar action text) |

### Secondary Group (supporting, less dominant)

| Role | Use |
|------|-----|
| `secondary` | Secondary buttons, filter chips, less prominent interactive elements |
| `onSecondary` | Content on `secondary` |
| `secondaryContainer` | Tag backgrounds, secondary selection states, grouped content areas |
| `onSecondaryContainer` | Content on `secondaryContainer` |

### Tertiary Group (complementary accent)

| Role | Use |
|------|-----|
| `tertiary` | Accents that contrast with both primary and secondary — use sparingly for visual interest |
| `onTertiary` | Content on `tertiary` |
| `tertiaryContainer` | Calendar event backgrounds, mood indicators, illustrative tinted areas |
| `onTertiaryContainer` | Content on `tertiaryContainer` |

**Rule**: If your design has a warm/cool tension (blue primary + orange accent), tertiary is where the accent lives. Don't leave it at the Material default — it appears as a random purple on most devices.

### Surface Group (the backbone of most screens)

| Role | Use |
|------|-----|
| `surface` | Default card and sheet backgrounds |
| `onSurface` | Primary text and icons on surface backgrounds |
| `surfaceVariant` | Alternative card backgrounds, input field fills, differentiated list item rows |
| `onSurfaceVariant` | Secondary text and secondary icons — captions, metadata, subtitles |
| `surfaceTint` | The primary-color tint applied to elevated surfaces (handled automatically by `Surface(tonalElevation)`) |
| `background` | App-level screen background — in most apps matches `surface` |
| `onBackground` | Content on the background — typically identical to `onSurface` |

**Critical distinction**: `onSurface` vs `onSurfaceVariant`:
- Use `onSurface` for the most important text on any card (article title, product name)
- Use `onSurfaceVariant` for supporting text (timestamp, author name, subtitle)
- Never use `onBackground` for text inside cards — it's only for direct-on-background content

### Inverse Group (high contrast, rare use)

| Role | Use |
|------|-----|
| `inverseSurface` | Tooltip and snackbar container backgrounds (inverts the surface for high contrast) |
| `inverseOnSurface` | Text inside tooltips/snackbars |
| `inversePrimary` | Links or action text inside snackbars |

### Error Group

| Role | Use |
|------|-----|
| `error` | Error text, destructive action buttons, validation error underlines |
| `onError` | Content on error backgrounds |
| `errorContainer` | Error banner backgrounds, error chip fills |
| `onErrorContainer` | Text inside error containers |

**Rule**: `error` is for text and icon fills. `errorContainer` is for backgrounds. Never place `onError` text on `errorContainer` — the contrast will fail.

### Outline Group

| Role | Use |
|------|-----|
| `outline` | Borders on text fields, card outlines, dividers between sections |
| `outlineVariant` | Lighter dividers, decorative borders, subtle separators |
| `scrim` | Overlay behind modal dialogs and bottom sheets |

---

## Material Theme Builder — Generate Your Brand Palette

Never hand-pick all 29 colors manually. Material Theme Builder generates a complete, contrast-compliant palette from a single brand color. Use it once per project.

**Workflow:**
1. Go to https://m3.material.io/theme-builder#/custom
2. Set your brand's primary color (e.g. `#3D00C7`)
3. Optionally set secondary and tertiary key colors
4. Click **Export → Jetpack Compose** — generates complete `Color.kt` with all 29 roles for both light and dark
5. Paste the generated values into your `ColorPrimitives.kt` and map them in `AppLightColorScheme`/`AppDarkColorScheme`

The tool guarantees WCAG AA contrast compliance between every role and its `on-` counterpart. Hand-picked palettes almost never achieve this without testing.

---

## Complete Theme Assembly

```kotlin
// core/ui/src/main/kotlin/com/example/core/ui/theme/AppTheme.kt

@Composable
fun AppTheme(
    darkTheme: Boolean = isSystemInDarkTheme(),
    dynamicColor: Boolean = true,
    content: @Composable () -> Unit
) {
    val colorScheme = when {
        // Dynamic color: wallpaper-derived palette on Android 12+
        dynamicColor && Build.VERSION.SDK_INT >= Build.VERSION_CODES.S -> {
            val context = LocalContext.current
            if (darkTheme) dynamicDarkColorScheme(context)
            else dynamicLightColorScheme(context)
        }
        // Static brand palette
        darkTheme -> AppDarkColorScheme
        else      -> AppLightColorScheme
    }

    // Provide custom extension tokens alongside MaterialTheme
    val gradientColors = if (dynamicColor && Build.VERSION.SDK_INT >= Build.VERSION_CODES.S) {
        AppGradientColors() // empty — dynamic color generates its own tones
    } else {
        if (darkTheme) DarkGradientColors else LightGradientColors
    }

    CompositionLocalProvider(
        LocalAppGradientColors  provides gradientColors,
        LocalAppDimensions      provides AppDimensions(),
        LocalAppElevation       provides AppElevation(),
    ) {
        MaterialTheme(
            colorScheme = colorScheme,
            typography  = AppTypography,
            shapes      = AppShapes,
            content     = content
        )
    }
}
```

---

## Dynamic Color — The Right Pattern

Dynamic color reads wallpaper tones from the Android system on API 31+ and builds a complete 29-role scheme. Your static brand palette is the fallback — it must be defined and good-looking, not a placeholder.

```kotlin
val colorScheme = when {
    // Priority 1: dynamic (Android 12+, if the user hasn't disabled it)
    dynamicColor && Build.VERSION.SDK_INT >= Build.VERSION_CODES.S -> {
        if (darkTheme) dynamicDarkColorScheme(LocalContext.current)
        else           dynamicLightColorScheme(LocalContext.current)
    }
    // Priority 2: brand dark palette
    darkTheme -> AppDarkColorScheme
    // Priority 3: brand light palette
    else      -> AppLightColorScheme
}
```

**When to disable dynamic color**: If your app has strong brand identity that must be maintained regardless of the user's wallpaper (banking apps, brand-critical utilities), pass `dynamicColor = false` and document the reason.

---

## Tonal Elevation — Depth Without Shadows

Material 3 does not use shadow elevation for depth on surfaces. It uses a tonal color overlay: the higher the elevation, the more the `surfaceTint` colour (which equals `primary`) bleeds into the surface. This is why cards on dark mode feel slightly purple/tinted — that is correct behaviour, not a bug.

```kotlin
// Low elevation: content card — subtle separation from background
Surface(tonalElevation = 1.dp) { CardContent() }

// Medium elevation: modal sheet, elevated navigation rail
Surface(tonalElevation = 3.dp) { SheetContent() }

// High elevation: navigation drawer, menus
Surface(tonalElevation = 8.dp) { DrawerContent() }
```

**Elevation levels and their tonal tint percentages:**

| tonalElevation | Primary tint % | Use |
|---|---|---|
| 0dp | 0% | App background, non-elevated surfaces |
| 1dp | 5% | Cards, list items |
| 3dp | 8% | FAB, elevated chips |
| 6dp | 11% | Navigation drawers |
| 8dp | 12% | Menus, dialogs |
| 12dp | 14% | Modal bottom sheets |

Do not replicate this manually with `color.copy(alpha = X)` — the `tonalElevation` parameter on `Surface` and `Card` handles it automatically.

---

## Custom Extension Tokens — Beyond MaterialTheme

Material 3 does not cover everything. Gradients, branded dimensions, extra color roles (warning, success, info), and custom elevation systems all need `CompositionLocal`. Use `staticCompositionLocalOf` for values that rarely change and `compositionLocalOf` for values that change frequently (e.g. runtime theme switching).

### Gradient Colors

```kotlin
// Gradient token data class
@Immutable
data class AppGradientColors(
    val topColor: Color = Color.Unspecified,
    val bottomColor: Color = Color.Unspecified,
    val container: Color = Color.Unspecified,
)

val LocalAppGradientColors = staticCompositionLocalOf { AppGradientColors() }

// Brand gradient definitions
internal val LightGradientColors = AppGradientColors(
    topColor    = ColorPrimitives.Indigo95,
    bottomColor = ColorPrimitives.Teal90,
    container   = ColorPrimitives.Indigo90,
)

internal val DarkGradientColors = AppGradientColors(
    topColor    = ColorPrimitives.Indigo10,
    bottomColor = ColorPrimitives.Teal30,
    container   = ColorPrimitives.Indigo20,
)

// Usage in composables:
val gradientColors = LocalAppGradientColors.current

Box(
    modifier = Modifier.background(
        Brush.verticalGradient(
            colors = listOf(gradientColors.topColor, gradientColors.bottomColor)
        )
    )
)
```

### Extra Semantic Color Roles (Warning, Success, Info)

Material 3 only defines `error`. For warning and success states, add them as extensions.

```kotlin
@Immutable
data class AppExtendedColors(
    val warning:         Color = Color.Unspecified,
    val onWarning:       Color = Color.Unspecified,
    val warningContainer:    Color = Color.Unspecified,
    val onWarningContainer:  Color = Color.Unspecified,
    val success:         Color = Color.Unspecified,
    val onSuccess:       Color = Color.Unspecified,
    val successContainer:    Color = Color.Unspecified,
    val onSuccessContainer:  Color = Color.Unspecified,
)

val LocalAppExtendedColors = staticCompositionLocalOf { AppExtendedColors() }

internal val LightExtendedColors = AppExtendedColors(
    warning              = Color(0xFF795900),
    onWarning            = Color.White,
    warningContainer     = Color(0xFFFFDFA0),
    onWarningContainer   = Color(0xFF251A00),
    success              = Color(0xFF1A6B2F),
    onSuccess            = Color.White,
    successContainer     = Color(0xFFB7F4C8),
    onSuccessContainer   = Color(0xFF00210B),
)

internal val DarkExtendedColors = AppExtendedColors(
    warning              = Color(0xFFEDB900),
    onWarning            = Color(0xFF3F2E00),
    warningContainer     = Color(0xFF594200),
    onWarningContainer   = Color(0xFFFFDFA0),
    success              = Color(0xFF9CD7AE),
    onSuccess            = Color(0xFF003917),
    successContainer     = Color(0xFF005223),
    onSuccessContainer   = Color(0xFFB7F4C8),
)

// Accessor object — mirrors MaterialTheme pattern
object AppTheme {
    val extendedColors: AppExtendedColors
        @Composable get() = LocalAppExtendedColors.current
    val gradientColors: AppGradientColors
        @Composable get() = LocalAppGradientColors.current
    val dimensions: AppDimensions
        @Composable get() = LocalAppDimensions.current
}

// Usage:
val successColor = AppTheme.extendedColors.success
```

### Dimension Tokens (spacing and sizing beyond the 4dp grid)

```kotlin
@Immutable
data class AppDimensions(
    val cardPadding:         Dp = 16.dp,
    val screenHorizontal:    Dp = 16.dp,
    val sectionGap:          Dp = 24.dp,
    val iconSizeMedium:      Dp = 24.dp,
    val iconSizeLarge:       Dp = 32.dp,
    val avatarSizeSmall:     Dp = 32.dp,
    val avatarSizeMedium:    Dp = 48.dp,
    val minTouchTarget:      Dp = 48.dp,
    val bottomBarHeight:     Dp = 80.dp,
)

val LocalAppDimensions = staticCompositionLocalOf { AppDimensions() }
```

---

## Extending MaterialTheme with Kotlin Extension Properties

For single values that logically belong to an existing Material system, use extension properties. No extra CompositionLocal needed.

```kotlin
// Extra color role on ColorScheme — accessible as MaterialTheme.colorScheme.snackbarAction
val ColorScheme.snackbarAction: Color
    @Composable
    get() = if (isSystemInDarkTheme()) ColorPrimitives.Coral80 else ColorPrimitives.Coral40

// Extra text style on Typography
val Typography.overline: TextStyle
    get() = TextStyle(
        fontWeight = FontWeight.Medium,
        fontSize   = 10.sp,
        lineHeight = 16.sp,
        letterSpacing = 1.5.sp,
    )

// Extra shape on Shapes
val Shapes.pill: Shape
    get() = RoundedCornerShape(percent = 50)
```

---

## Color for Component States

Material components apply alpha overlays for pressed, focused, hovered, and disabled states automatically via the `Indication` system. When building custom components, replicate this:

```kotlin
// Disabled states: 38% alpha on content, 12% alpha on container
val disabledContentAlpha    = 0.38f
val disabledContainerAlpha  = 0.12f

// Pressed overlay: 10% of onContainer color
val pressedOverlayAlpha = 0.10f

// Focused overlay: 12% of onContainer color
val focusedOverlayAlpha = 0.12f

// Hovered overlay: 8% of onContainer color
val hoveredOverlayAlpha = 0.08f

// Custom button applying these correctly:
@Composable
fun BrandButton(
    onClick: () -> Unit,
    enabled: Boolean = true,
    text: String
) {
    val containerColor = if (enabled)
        MaterialTheme.colorScheme.primary
    else
        MaterialTheme.colorScheme.onSurface.copy(alpha = disabledContainerAlpha)

    val contentColor = if (enabled)
        MaterialTheme.colorScheme.onPrimary
    else
        MaterialTheme.colorScheme.onSurface.copy(alpha = disabledContentAlpha)

    Button(
        onClick = onClick,
        enabled = enabled,
        colors = ButtonDefaults.buttonColors(
            containerColor         = containerColor,
            contentColor           = contentColor,
            disabledContainerColor = containerColor,
            disabledContentColor   = contentColor
        )
    ) { Text(text) }
}
```

---

## Runtime Theme Switching

When the app must support switching themes at runtime (branded variants, per-user customisation):

```kotlin
// Define multiple brand palettes
enum class AppBrandTheme { Default, HighContrast, Warm, Cool }

@Immutable
data class BrandColorTokens(
    val light: ColorScheme,
    val dark: ColorScheme,
    val lightGradients: AppGradientColors,
    val darkGradients: AppGradientColors,
)

val BrandThemeCatalog = mapOf(
    AppBrandTheme.Default       to BrandColorTokens(AppLightColorScheme, AppDarkColorScheme, LightGradientColors, DarkGradientColors),
    AppBrandTheme.HighContrast  to BrandColorTokens(HighContrastLightScheme, HighContrastDarkScheme, ...),
    AppBrandTheme.Warm          to BrandColorTokens(WarmLightScheme, WarmDarkScheme, ...),
)

// In ViewModel or DataStore:
val selectedBrand: StateFlow<AppBrandTheme> = ...

// In AppTheme composable:
@Composable
fun AppTheme(
    brand: AppBrandTheme = AppBrandTheme.Default,
    darkTheme: Boolean = isSystemInDarkTheme(),
    content: @Composable () -> Unit
) {
    val tokens = BrandThemeCatalog[brand] ?: BrandThemeCatalog[AppBrandTheme.Default]!!
    val colorScheme = if (darkTheme) tokens.dark else tokens.light
    val gradients   = if (darkTheme) tokens.darkGradients else tokens.lightGradients

    CompositionLocalProvider(LocalAppGradientColors provides gradients) {
        MaterialTheme(
            colorScheme = colorScheme,
            typography  = AppTypography,
            shapes      = AppShapes,
            content     = content
        )
    }
}
```

---

## Surface Color Hierarchy — Practical Guide

Understanding when to use which surface role eliminates the "everything looks flat" problem.

```
App background (background)
  └─ Screen content area
       ├─ Cards at rest (surface / tonalElevation = 1dp)
       │    ├─ Selected card (primaryContainer)
       │    ├─ Secondary info card (surfaceVariant)
       │    └─ Error card (errorContainer)
       └─ Navigation components
            ├─ Bottom bar (surface / tonalElevation = 3dp)
            ├─ FAB (primaryContainer / tonalElevation = 6dp)  
            └─ Modal sheet (surface / tonalElevation = 1dp)
```

### Text colour on each surface

```kotlin
// On surface — primary text
Text(text = title, color = MaterialTheme.colorScheme.onSurface)

// On surface — secondary/supporting text  
Text(text = subtitle, color = MaterialTheme.colorScheme.onSurfaceVariant)

// On surfaceVariant — body text
Text(text = body, color = MaterialTheme.colorScheme.onSurfaceVariant)

// On primaryContainer — text inside a selected chip or highlighted card
Text(text = label, color = MaterialTheme.colorScheme.onPrimaryContainer)

// Hint/placeholder text — manually apply opacity
Text(text = placeholder, color = MaterialTheme.colorScheme.onSurface.copy(alpha = 0.6f))
```

---

## Brand Brush System — Gradients as First-Class Tokens

Define brand gradients as `Brush` objects in the theme, not inline in composables.

```kotlin
// core/ui/src/main/kotlin/com/example/core/ui/theme/AppBrushes.kt

object AppBrushes {

    @Composable
    fun verticalHero(): Brush {
        val colors = LocalAppGradientColors.current
        return Brush.verticalGradient(
            colors = listOf(colors.topColor, colors.bottomColor)
        )
    }

    @Composable
    fun primaryRadial(): Brush = Brush.radialGradient(
        colors = listOf(
            MaterialTheme.colorScheme.primaryContainer,
            MaterialTheme.colorScheme.primary.copy(alpha = 0.0f)
        ),
        radius = 600f
    )

    @Composable
    fun scrimGradient(): Brush = Brush.verticalGradient(
        colors = listOf(
            Color.Transparent,
            MaterialTheme.colorScheme.surface.copy(alpha = 0.6f),
            MaterialTheme.colorScheme.surface,
        )
    )

    // Animated gradient text
    @Composable
    fun brandTextGradient(): Brush = Brush.linearGradient(
        colors = listOf(
            MaterialTheme.colorScheme.primary,
            MaterialTheme.colorScheme.tertiary
        )
    )
}

// Usage — gradient text:
Text(
    text = "Brand Headline",
    style = MaterialTheme.typography.headlineLarge,
    modifier = Modifier.drawWithCache {
        val brush = AppBrushes.brandTextGradient()
        onDrawWithContent {
            drawWithLayer {
                drawContent()
                drawRect(brush = brush, blendMode = BlendMode.SrcAtop)
            }
        }
    }
)
```

---

## Common Theming Mistakes — and Their Fixes

### Mistake 1: Using only `primary` and ignoring the container roles

```kotlin
// BAD — every element fights for attention
Button(colors = ButtonDefaults.buttonColors(containerColor = MaterialTheme.colorScheme.primary))
Chip(colors = ChipColors(containerColor = MaterialTheme.colorScheme.primary))
Card(colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.primary))

// GOOD — hierarchy through role differentiation
Button(colors = ButtonDefaults.buttonColors(containerColor = MaterialTheme.colorScheme.primary))         // highest emphasis
Chip(colors = FilterChipDefaults.filterChipColors(selectedContainerColor = MaterialTheme.colorScheme.primaryContainer)) // medium
Card(colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surfaceVariant))        // lowest
```

### Mistake 2: Hardcoding `Color.White` or `Color.Black` for text

```kotlin
// BAD — breaks in dark mode
Text(text = title, color = Color.Black)
Text(text = subtitle, color = Color.Gray)

// GOOD — semantically correct, adapts to dark/light automatically
Text(text = title, color = MaterialTheme.colorScheme.onSurface)
Text(text = subtitle, color = MaterialTheme.colorScheme.onSurfaceVariant)
```

### Mistake 3: Defining dark mode color scheme as a colour-inverted copy of light

Dark mode is not light mode inverted. The tone values shift differently. The primary color in dark mode is typically the `80`-tone (light teal blue), not the inverted `40`-tone (dark teal). Always derive dark mode values from the Material Theme Builder output, not from `Color.Inverse` transformations.

### Mistake 4: Placing `onPrimary` text on `primaryContainer` background

Every `on-` color is designed for exactly one background: its base. Mixing them fails contrast:

```kotlin
// BAD — onPrimary is designed for the dark primary background, 
//        not the light primaryContainer background
Card(colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.primaryContainer)) {
    Text(color = MaterialTheme.colorScheme.onPrimary)  // will likely be white on light pastel — invisible
}

// GOOD
Card(colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.primaryContainer)) {
    Text(color = MaterialTheme.colorScheme.onPrimaryContainer)  // dark tone — correct contrast
}
```

### Mistake 5: Leaving `tertiary` at the Material baseline default

The default tertiary is a generic purple that matches no brand. If you don't set it, your UI will show stray purple accents from components that use tertiary. Always set all three accent families.

### Mistake 6: Using `alpha` on `onSurface` when `onSurfaceVariant` is the correct choice

```kotlin
// BAD — manual alpha is fragile; contrast may fail at some device display settings
Text(color = MaterialTheme.colorScheme.onSurface.copy(alpha = 0.6f))

// GOOD — Material 3 designed onSurfaceVariant for exactly this use case
Text(color = MaterialTheme.colorScheme.onSurfaceVariant)
```

---

## Theming Checklist — Before Shipping Any Screen

- [ ] All 29 color roles defined in both light and dark `ColorScheme` — none left at Material default
- [ ] No hardcoded hex colours outside of `ColorPrimitives` file
- [ ] No `Color.White`, `Color.Black`, `Color.Gray` in any composable
- [ ] `tertiary` and `tertiaryContainer` set to brand-intentional values, not Material default purple
- [ ] `onX` colour used on its matching `X` background only — no cross-mixing
- [ ] `onSurfaceVariant` used for secondary/supporting text, not `onSurface.copy(alpha=0.6f)`
- [ ] Dynamic color tested: does the app look good with wallpaper-derived colours?
- [ ] Static palette tested: does the app look good when dynamic color is unavailable (API < 31)?
- [ ] Dark mode tested on a real device — not just toggling system setting in emulator
- [ ] Custom extension tokens (`AppExtendedColors`, `AppGradientColors`) provided via `CompositionLocalProvider`
- [ ] `Material Theme Builder` export used to generate the palette, not hand-picked hex values
- [ ] Tonal elevation used for depth — no manual `color.copy(alpha)` overlays to simulate shadow
