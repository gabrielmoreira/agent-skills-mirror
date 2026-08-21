---
name: monochromatic-ui
description: "Implements a strict single-hue UI: HSL tints/shades, tinted mono900 shadows, texture and weight instead of a second hue, including error and success states. Use when the user wants monochromatic, one-color palette, or tint/shade discipline on web or mobile. Not for duotone or multi-hue brand systems, glassmorphism as the look, or treating this as a WCAG auditor."
version: 1.0.1
---

# Monochromatic UI

> "Elegance through constraint. A single hue, explored through all its tints, tones, and shades."

## When to Use

Use this skill when the user requests a monochromatic design system, single-color palette, or strict color-discipline aesthetic for web or mobile apps. This is a child reference of the `design-it` skill.

**Trigger keywords:** monochromatic, single hue, one color palette, tints and shades, color discipline, elegant constraint, duotone avoidance.

## Core Principles

1. **Single Hue**: Choose one base color (e.g., deep blue at HSL hue 210). The entire UI is built using lighter (tints) and darker (shades) of that exact hue. Never introduce a second hue.
2. **High Contrast for Legibility**: The darkest shade and the lightest tint must pass WCAG accessibility standards when placed together as text-on-background.
3. **Texture over Color**: Because color is restricted, differentiate sections using subtle textures, patterns, varying opacities, font weights, and spacing.
4. **Tinted Shadows**: All drop shadows must be tinted with the base hue's darkest shade (`mono900`). Pure black shadows look dirty and break the aesthetic.
5. **No Accent Colors**: Errors, warnings, and success states must be communicated through bold text, dark shades, borders, or icons — never a second hue.

## Visual DNA

| Attribute | Guidance |
|---|---|
| **Colors** | One dominant hue extrapolated into 5+ steps (900 → 100). Default suggestion: Monochromatic Brown or a hue from Earth-Grounded Elegance. |
| **Typography** | Clean and unobtrusive. Hierarchy is established through font weight and size, not color. |
| **Shadows** | Always tinted with `mono900` at low opacity. Never pure `#000`. |
| **Borders** | Use mid-tone (`mono300`) for subtle separation. |

## Prerequisites

- Target platform identified: Web (CSS), SwiftUI, Flutter, React Native, or Jetpack Compose.
- Base hue selected (0–360 HSL/HSV value).
- Accessibility contrast checker available (browser DevTools or external tool).

## Procedure

### 1. Define the Palette

Pick a base hue and generate five steps using HSL. Keep the hue constant; vary saturation and lightness.

```
Hue: 210 (Deep Blue example)
mono-900: hsl(210, 80%, 10%)   — very dark (text, shadows)
mono-700: hsl(210, 70%, 30%)   — dark (hover states)
mono-500: hsl(210, 60%, 50%)   — base (buttons, accents)
mono-300: hsl(210, 50%, 80%)   — light (borders)
mono-100: hsl(210, 40%, 95%)   — very light (backgrounds)
```

### 2. Web Implementation (CSS)

```css
:root {
  --mono-900: hsl(210, 80%, 10%);
  --mono-700: hsl(210, 70%, 30%);
  --mono-500: hsl(210, 60%, 50%);
  --mono-300: hsl(210, 50%, 80%);
  --mono-100: hsl(210, 40%, 95%);
}

body {
  background-color: var(--mono-100);
  color: var(--mono-900);
  font-family: 'Inter', sans-serif;
}

.mono-card {
  background-color: #ffffff;
  border: 1px solid var(--mono-300);
  border-radius: 8px;
  padding: 32px;
  box-shadow: 0 10px 25px hsla(210, 80%, 10%, 0.05); /* Tinted shadow */
}

.mono-btn {
  background-color: var(--mono-500);
  color: #ffffff;
  border: none;
  border-radius: 4px;
  padding: 12px 24px;
  transition: background-color 0.2s;
}

.mono-btn:hover {
  background-color: var(--mono-700);
}

.mono-subtext {
  color: var(--mono-500);
  font-weight: 500;
}
```

**Key rule:** Use HSL variables so the entire palette can be re-hued by changing one number.

### 3. SwiftUI Implementation

```swift
struct MonochromaticView: View {
    // Hue 210° → 210/360 = 0.58 in SwiftUI's 0.0–1.0 scale
    let mono900 = Color(hue: 0.58, saturation: 0.80, brightness: 0.10)
    let mono700 = Color(hue: 0.58, saturation: 0.70, brightness: 0.30)
    let mono500 = Color(hue: 0.58, saturation: 0.60, brightness: 0.50)
    let mono300 = Color(hue: 0.58, saturation: 0.50, brightness: 0.80)
    let mono100 = Color(hue: 0.58, saturation: 0.40, brightness: 0.95)

    var body: some View {
        VStack(spacing: 24) {
            VStack(alignment: .leading, spacing: 12) {
                Text("Monochromatic Elegance")
                    .font(.title2).fontWeight(.semibold)
                    .foregroundColor(mono900)
                Text("Using only variations in saturation and brightness of a single hue.")
                    .foregroundColor(mono500)
            }
            .padding(32)
            .background(Color.white)
            .border(mono300, width: 1)
            .shadow(color: mono900.opacity(0.1), radius: 15, y: 5) // Tinted shadow

            Button(action: {}) {
                Text("Primary Action")
                    .fontWeight(.bold)
                    .foregroundColor(.white)
                    .frame(maxWidth: .infinity)
                    .padding()
                    .background(mono500)
                    .cornerRadius(8)
            }
        }
        .padding()
        .frame(maxWidth: .infinity, maxHeight: .infinity)
        .background(mono100)
    }
}
```

**Key rule:** Always use `Color(hue:saturation:brightness:)` — never hex codes — to guarantee math-perfect monochromatic harmony.

### 4. Flutter Implementation

```dart
class MonochromaticScreen extends StatelessWidget {
  // Flutter HSVColor: Hue 0–360, Saturation 0.0–1.0, Value 0.0–1.0
  final Color mono900 = const HSVColor.fromAHSV(1.0, 210, 0.80, 0.10).toColor();
  final Color mono500 = const HSVColor.fromAHSV(1.0, 210, 0.60, 0.50).toColor();
  final Color mono300 = const HSVColor.fromAHSV(1.0, 210, 0.50, 0.80).toColor();
  final Color mono100 = const HSVColor.fromAHSV(1.0, 210, 0.40, 0.95).toColor();

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: mono100,
      body: Center(
        child: Padding(
          padding: const EdgeInsets.all(24.0),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Container(
                width: double.infinity,
                padding: const EdgeInsets.all(32),
                decoration: BoxDecoration(
                  color: Colors.white,
                  border: Border.all(color: mono300),
                  borderRadius: BorderRadius.circular(8),
                  boxShadow: [
                    BoxShadow(
                      color: mono900.withOpacity(0.1),
                      blurRadius: 15,
                      offset: const Offset(0, 5),
                    )
                  ],
                ),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text('Monochromatic',
                      style: TextStyle(fontSize: 24, fontWeight: FontWeight.w600, color: mono900)),
                    const SizedBox(height: 12),
                    Text('Variations of a single hue.',
                      style: TextStyle(fontSize: 16, color: mono500)),
                  ],
                ),
              ),
              const SizedBox(height: 24),
              ElevatedButton(
                onPressed: () {},
                style: ElevatedButton.styleFrom(
                  backgroundColor: mono500,
                  foregroundColor: Colors.white,
                  minimumSize: const Size(double.infinity, 56),
                  shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(8)),
                  elevation: 0,
                ),
                child: const Text('Primary Action', style: TextStyle(fontWeight: FontWeight.bold)),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
```

**Key rule:** Use `HSVColor.fromAHSV()` for explicit palette control without guessing hex codes.

### 5. React Native Implementation

```jsx
const theme = {
  mono900: 'hsl(210, 80%, 10%)',
  mono700: 'hsl(210, 70%, 30%)',
  mono500: 'hsl(210, 60%, 50%)',
  mono300: 'hsl(210, 50%, 80%)',
  mono100: 'hsl(210, 40%, 95%)',
};

const MonochromaticScreen = () => (
  <View style={{ flex: 1, backgroundColor: theme.mono100, padding: 24, justifyContent: 'center' }}>
    <View style={{
      backgroundColor: '#FFFFFF',
      borderColor: theme.mono300,
      borderWidth: 1,
      borderRadius: 8,
      padding: 32,
      marginBottom: 24,
      shadowColor: theme.mono900, shadowOffset: { width: 0, height: 5 },
      shadowOpacity: 0.1, shadowRadius: 15,
    }}>
      <Text style={{ fontSize: 24, fontWeight: '600', color: theme.mono900, marginBottom: 12 }}>
        Monochromatic
      </Text>
      <Text style={{ fontSize: 16, color: theme.mono500 }}>
        Using HSL strings in React Native makes palette generation trivial.
      </Text>
    </View>
    <TouchableOpacity style={{
      backgroundColor: theme.mono500,
      padding: 16,
      borderRadius: 8,
      alignItems: 'center',
    }}>
      <Text style={{ fontWeight: 'bold', color: '#FFFFFF', fontSize: 16 }}>
        Primary Action
      </Text>
    </TouchableOpacity>
  </View>
);
```

**Key rule:** React Native's `StyleSheet` accepts `hsl()` strings natively — use them instead of hex for easier debugging.

### 6. Jetpack Compose Implementation

```kotlin
@Composable
fun MonochromaticScreen() {
    // Compose Color.hsv: Hue 0–360f, Saturation 0–1f, Value 0–1f
    val mono900 = Color.hsv(210f, 0.80f, 0.10f)
    val mono500 = Color.hsv(210f, 0.60f, 0.50f)
    val mono300 = Color.hsv(210f, 0.50f, 0.80f)
    val mono100 = Color.hsv(210f, 0.40f, 0.95f)

    Column(
        modifier = Modifier.fillMaxSize().background(mono100).padding(24.dp),
        verticalArrangement = Arrangement.Center
    ) {
        Box(
            modifier = Modifier
                .fillMaxWidth()
                .shadow(15.dp, RoundedCornerShape(8.dp), spotColor = mono900.copy(alpha = 0.2f))
                .background(Color.White, RoundedCornerShape(8.dp))
                .border(1.dp, mono300, RoundedCornerShape(8.dp))
                .padding(32.dp)
        ) {
            Column {
                Text("Monochromatic", fontSize = 24.sp, fontWeight = FontWeight.SemiBold, color = mono900)
                Spacer(Modifier.height(12.dp))
                Text("Strictly enforced hue discipline.", color = mono500)
            }
        }
        Spacer(Modifier.height(24.dp))
        Button(
            onClick = { },
            colors = ButtonDefaults.buttonColors(containerColor = mono500, contentColor = Color.White),
            shape = RoundedCornerShape(8.dp),
            modifier = Modifier.fillMaxWidth().height(56.dp)
        ) {
            Text("Primary Action", fontWeight = FontWeight.Bold)
        }
    }
}
```

**Key rule:** Set `spotColor` in `Modifier.shadow` to `mono900` to prevent muddy, disjointed shadows.

## Do's and Don'ts

| ✅ Do | ❌ Don't |
|---|---|
| Use pure white or pure black as absolute extremes for text legibility | Sneak in an accent color (e.g., red error button in a blue UI) |
| Tint all shadows with `mono900` | Use pure `#000` black shadows |
| Establish hierarchy via font weight and size | Rely on color variation alone for hierarchy |
| Signify errors with bold text, dark shades, borders, or icons | Add a second hue for semantic states — this breaks the aesthetic |
| Use HSL/HSV color functions for palette generation | Hardcode unrelated hex values |

## Pitfalls

- **Accent color creep**: Adding a red error state or green success indicator instantly converts the design to "duotone" or standard UI. Resist this. Use bold text, icons, or the darkest shade for errors.
- **Pure black shadows**: `box-shadow: ... rgba(0,0,0,0.1)` looks muddy against a tinted palette. Always use `hsla(hue, sat%, light%, alpha)`.
- **Insufficient contrast**: Mid-tones (`mono500`) on `mono100` backgrounds may fail WCAG AA. Always verify text/background pairs.
- **Flat appearance**: Without color variety, the UI can feel lifeless. Compensate with texture, elevation, spacing, and weight contrast.
- **Hex code drift**: Manually picking hex values for each shade leads to hue inconsistency. Always derive from a single HSL/HSV hue value.

## Verification

1. **Hue consistency check**: Inspect every color in the palette and confirm the hue value is identical across all steps.
   - Web: Open DevTools → Computed → filter for `hsl(`. All hue values should match.
2. **Contrast check**: Verify text-on-background pairs meet WCAG AA (4.5:1 for normal text, 3:1 for large text).
   - Use browser DevTools accessibility inspector or a contrast checker tool.
3. **Shadow tint check**: Confirm no shadow uses pure black (`rgb(0,0,0)` or `#000`).
   - Web: Search CSS for `rgba(0, 0, 0` or `#000` in shadow properties.
4. **No second hue**: Scan the entire codebase for any color whose hue differs from the base.
   - Web: Check all `hsl()`, `hsla()`, and hex values against the base hue.
5. **Visual review**: Render the UI and confirm sections are differentiated by weight, spacing, and texture — not by color.

## Limitations

- This is a styling reference and does not replace environment-specific validation, accessibility testing, or expert review.
- Ensure appropriate contrast ratios and responsive behaviors are verified separately on real devices.
- Pure white (`#FFFFFF`) and pure black (`#000000`) are permitted only as absolute extremes for text legibility, not as palette members.

## Related Skills

- `design-it` — Parent skill; consult for overall design system strategy and when multiple sub-styles are being evaluated.
