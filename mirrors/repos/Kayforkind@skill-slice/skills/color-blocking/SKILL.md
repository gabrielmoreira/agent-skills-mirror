---
name: color-blocking
description: Implements Mondrian-style color-blocking layouts with large flat geometric panels, a 3-4 color high-contrast palette, and thick black grid lines via CSS Grid or native stacks. Use when the user wants color blocking, Mondrian grids, or bold geometric color sections on web or mobile. Not for glassmorphism, VisionOS spatial glass, or gradient/shadow UI. Do not use as a general design-system or theming skill.
version: 1.0.1
date_added: "2026-06-17"
risk: safe
source: self
source_type: self
---

# Color Blocking

> "The grid made visible. Large, solid swaths of contrasting color defining the layout."

## Overview

Color Blocking is a visual sub-style that divides the viewport into large geometric rectangles, each filled with a solid, bold color. Blocks touch directly or are separated by stark black grid lines reminiscent of Mondrian paintings. Typography is placed precisely within blocks to balance visual weight. This skill is a child reference of the `design-it` skill.

## When to Use

Use this sub-style when the user's request matches the Color Blocking aesthetic:

- Large, solid swaths of contrasting color defining the layout
- Mondrian-style grids with thick black dividing lines
- Striking, flat layout divisions with no shadows or gradients
- Bold sans-serif typography placed inside color blocks
- Geometric division of the viewport into rectangles or squares

**Trigger keywords**: color blocking, Mondrian layout, bold color blocks, geometric color grid, flat color sections, striking layout divisions, high-contrast color panels.

## Prerequisites

- Basic familiarity with CSS Grid (web) or the target mobile framework's layout system (SwiftUI, Flutter, React Native, or Jetpack Compose).
- A bold sans-serif font available or loaded (e.g., Space Grotesk, Inter, Helvetica Neue Bold).
- A defined color palette of 3–4 strong, high-contrast colors.

## Procedure

### 1. Define the Color Palette

Choose 3 to 4 highly contrasting, bold colors. Recommended palettes:

- **Industrial Chic**: Red `#EF4444`, Black `#000000`, Grey `#6B7280`, White `#FFFFFF`
- **Custom Bold**: Yellow `#FACC15`, Navy `#2563EB`, Pink `#EC4899`, White `#FFFFFF`

Rules:
- Text on light blocks (yellow, white) should be black.
- Text on dark blocks (blue, red, black) should be white.
- Ensure WCAG contrast ratios are met for any text-bearing block.

### 2. Choose the Grid Structure

Plan the geometric division before coding:

- Decide the number of rows and columns (e.g., 3 columns × 2 rows).
- Assign `flex` or `fr` weights to create unequal block sizes (e.g., `1fr 2fr 1fr`).
- Decide grid line thickness: typically `2px` to `4px` solid black.

### 3. Web Implementation (CSS Grid)

CSS Grid is the only effective way to build this layout on the web.

```css
body {
  margin: 0;
  font-family: 'Space Grotesk', sans-serif;
  color: #000;
}

.color-block-grid {
  display: grid;
  grid-template-columns: 1fr 2fr 1fr;
  grid-template-rows: 60vh 40vh;
  /* Thick black lines between blocks */
  gap: 4px;
  background-color: #000;
  border: 4px solid #000;
  min-height: 100vh;
}

.block {
  padding: 40px;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
}

.block-yellow { background-color: #FACC15; }
.block-white  { background-color: #FFFFFF; }
.block-blue   { background-color: #2563EB; color: #FFF; }
.block-red    { background-color: #EF4444; }

.block-title {
  font-size: 3rem;
  font-weight: 900;
  text-transform: uppercase;
  margin: 0;
}
```

Key technique: Set `background-color: #000` on the grid container and use `gap: 4px`. The black background peeks through the gaps, creating Mondrian-style grid lines without extra elements.

### 4. SwiftUI Implementation

```swift
struct ColorBlockingView: View {
    let gridSpacing: CGFloat = 4 // Thickness of the black lines

    var body: some View {
        // Black background acts as the grid lines between blocks
        VStack(spacing: gridSpacing) {
            // Top Row
            HStack(spacing: gridSpacing) {
                ColorBlock(color: .yellow, text: "CREATE", textColor: .black)
                ColorBlock(color: .blue, text: "VISION", textColor: .white)
            }
            .frame(height: 300)

            // Bottom Row
            HStack(spacing: gridSpacing) {
                ColorBlock(color: .red, text: "BOLD", textColor: .white)
                    .frame(width: 120) // Fixed narrow block
                ColorBlock(color: .white, text: "MINIMAL", textColor: .black)
            }
        }
        .background(Color.black) // The grid lines
        .border(Color.black, width: gridSpacing) // Outer border
        .ignoresSafeArea()
    }
}

struct ColorBlock: View {
    let color: Color
    let text: String
    let textColor: Color
    var body: some View {
        color
            .overlay(
                Text(text)
                    .font(.system(size: 32, weight: .black))
                    .foregroundColor(textColor)
                    .padding(),
                alignment: .bottomLeading
            )
    }
}
```

Key technique: Set `.background(Color.black)` on the parent stack and use `spacing: 4`. The background peeks through the gaps. Use `.ignoresSafeArea()` to let blocks bleed to the physical device edge.

### 5. Flutter Implementation

```dart
class ColorBlockingScreen extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      // Black background creates the grid lines
      backgroundColor: Colors.black,
      body: SafeArea(
        bottom: false,
        child: Column(
          children: [
            // Top Row
            Expanded(
              flex: 3, // 3/5 of vertical space
              child: Row(
                children: [
                  Expanded(flex: 1, child: ColorBlock(color: const Color(0xFFFACC15), text: 'CREATE', textColor: Colors.black)),
                  const SizedBox(width: 4), // Grid line
                  Expanded(flex: 2, child: ColorBlock(color: const Color(0xFF2563EB), text: 'VISION', textColor: Colors.white)),
                ],
              ),
            ),
            const SizedBox(height: 4), // Horizontal grid line
            // Bottom Row
            Expanded(
              flex: 2, // 2/5 of vertical space
              child: Row(
                children: [
                  Expanded(flex: 1, child: ColorBlock(color: const Color(0xFFEF4444), text: 'BOLD', textColor: Colors.white)),
                  const SizedBox(width: 4),
                  Expanded(flex: 2, child: ColorBlock(color: Colors.white, text: 'MINIMAL', textColor: Colors.black)),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }
}

class ColorBlock extends StatelessWidget {
  final Color color;
  final String text;
  final Color textColor;
  const ColorBlock({required this.color, required this.text, required this.textColor});

  @override
  Widget build(BuildContext context) {
    return Container(
      color: color,
      padding: const EdgeInsets.all(24),
      alignment: Alignment.bottomLeft,
      child: Text(text, style: TextStyle(fontSize: 32, fontWeight: FontWeight.w900, color: textColor)),
    );
  }
}
```

Key technique: Use `Expanded` with varying `flex` factors to divide the screen geometrically. Insert `SizedBox(width: 4)` or `height: 4` between rows and columns to expose the black `Scaffold` background as grid lines.

### 6. React Native Implementation

```jsx
const ColorBlockingScreen = () => {
  return (
    <View style={{ flex: 1, backgroundColor: '#000', gap: 4 }}>
      {/* Top Row */}
      <View style={{ flex: 3, flexDirection: 'row', gap: 4 }}>
        <View style={[styles.block, { flex: 1, backgroundColor: '#FACC15' }]}>
          <Text style={[styles.text, { color: '#000' }]}>CREATE</Text>
        </View>
        <View style={[styles.block, { flex: 2, backgroundColor: '#2563EB' }]}>
          <Text style={[styles.text, { color: '#FFF' }]}>VISION</Text>
        </View>
      </View>

      {/* Bottom Row */}
      <View style={{ flex: 2, flexDirection: 'row', gap: 4 }}>
        <View style={[styles.block, { flex: 1, backgroundColor: '#EF4444' }]}>
          <Text style={[styles.text, { color: '#FFF' }]}>BOLD</Text>
        </View>
        <View style={[styles.block, { flex: 2, backgroundColor: '#FFF' }]}>
          <Text style={[styles.text, { color: '#000' }]}>MINIMAL</Text>
        </View>
      </View>
    </View>
  );
};

const styles = StyleSheet.create({
  block: {
    justifyContent: 'flex-end',
    padding: 24,
  },
  text: {
    fontSize: 32,
    fontWeight: '900',
    fontFamily: 'SpaceGrotesk-Bold',
  }
});
```

Key technique: The `gap` property in React Native flexbox makes this trivial. Set a black background on the parent, set `gap: 4`, and children automatically space out revealing thick black lines. Use `flex: 1`, `flex: 2`, etc. for block proportions.

### 7. Jetpack Compose Implementation

```kotlin
@Composable
fun ColorBlockingScreen() {
    val gridSpacing = 4.dp

    Column(
        modifier = Modifier
            .fillMaxSize()
            .background(Color.Black) // Grid lines
    ) {
        // Top Row
        Row(
            modifier = Modifier.weight(3f),
            horizontalArrangement = Arrangement.spacedBy(gridSpacing)
        ) {
            ColorBlock(Color(0xFFFACC15), "CREATE", Color.Black, Modifier.weight(1f))
            ColorBlock(Color(0xFF2563EB), "VISION", Color.White, Modifier.weight(2f))
        }

        Spacer(Modifier.height(gridSpacing))

        // Bottom Row
        Row(
            modifier = Modifier.weight(2f),
            horizontalArrangement = Arrangement.spacedBy(gridSpacing)
        ) {
            ColorBlock(Color(0xFFEF4444), "BOLD", Color.White, Modifier.weight(1f))
            ColorBlock(Color.White, "MINIMAL", Color.Black, Modifier.weight(2f))
        }
    }
}

@Composable
fun ColorBlock(color: Color, text: String, textColor: Color, modifier: Modifier = Modifier) {
    Box(
        modifier = modifier
            .fillMaxHeight()
            .background(color)
            .padding(24.dp),
        contentAlignment = Alignment.BottomStart
    ) {
        Text(text, fontSize = 32.sp, fontWeight = FontWeight.Black, color = textColor)
    }
}
```

Key technique: `Modifier.background(Color.Black)` combined with `Arrangement.spacedBy(4.dp)` creates the Mondrian grid. Use `Modifier.weight(Xf)` to mathematically divide screen real estate.

## Pitfalls

- **DO** ensure extreme contrast. Text on a yellow block should be black; text on a dark blue block should be white.
- **DON'T** use drop shadows, rounded corners, or gradients. Keep everything completely flat and sharp.
- **DON'T** add margins between blocks. Blocks must touch directly or be separated only by the black grid line.
- **DON'T** use more than 4 colors. Color Blocking relies on bold, limited palettes.
- **DON'T** use thin grid lines. The Mondrian effect requires `2px`–`4px` thick black borders.
- **DON'T** forget `.ignoresSafeArea()` (SwiftUI) or `SafeArea(bottom: false)` (Flutter) if you want blocks to bleed to the device edge.
- **DON'T** use `border-radius` or `clip-path` on blocks. All corners must be sharp 90-degree angles.
- **Accessibility**: Bold colors alone do not guarantee readable text. Always verify WCAG contrast ratios for text-bearing blocks.

## Verification

1. **Visual check**: Open the implemented screen in a browser or simulator. Confirm that:
   - Blocks are large, solid, and fill their grid cells completely.
   - Grid lines are uniformly thick black (`2px`–`4px`).
   - No shadows, gradients, or rounded corners are present.
   - Text is fully legible against its background color.

2. **Contrast verification**: For each text-on-color pairing, verify WCAG AA (4.5:1 for normal text, 3:1 for large text):
   - Yellow `#FACC15` + Black text `#000` → contrast ratio ~14:1 ✅
   - Blue `#2563EB` + White text `#FFF` → contrast ratio ~5:1 ✅
   - Red `#EF4444` + White text `#FFF` → contrast ratio ~3.8:1 (large text only) ⚠️
   - White `#FFFFFF` + Black text `#000` → contrast ratio 21:1 ✅

3. **Responsive check** (web): Resize the browser window. Confirm blocks reflow proportionally and the grid remains intact at common breakpoints (375px, 768px, 1280px).

4. **Framework-specific build check**:
   - **Web**: `npx serve .` and open in browser — no console errors.
   - **SwiftUI**: Build in Xcode (`Cmd+B`) — no errors.
   - **Flutter**: `flutter analyze` — no issues; `flutter run` — renders correctly.
   - **React Native**: `npx react-native run-ios` or `run-android` — renders correctly.
   - **Jetpack Compose**: Build in Android Studio — no errors; preview renders.

## Limitations

- This is a styling reference and does not replace environment-specific validation, accessibility testing, or expert review.
- Ensure appropriate contrast ratios and responsive behaviors are verified separately.
- Color values may need adjustment for dark mode or brand-specific palettes.

## Related Skills

- `design-it` — Parent skill; this is a child reference and is not meant to be triggered directly.
