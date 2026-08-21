---
name: bento-ui
description: "Lays out Apple-style bento grids: mixed-span rounded compartments (1x1, 2x1, 1x2, 2x2) with CSS Grid, Flutter staggered tiles, SwiftUI LazyVGrid, or RN/Compose row stacks. Use when the request is a bento grid, bento-box dashboard, or modular compartment cards. Not for plain card lists, Flexbox-only galleries, or magazine masonry that skips equal-gap compartments."
version: 1.0.1
date_added: "2026-06-17"
risk: safe
source: self
source_type: self
parent: design-it
---

# Bento UI

> "Everything in its right place. A highly structured, modular grid of distinct compartments."

## Overview

Bento UI arranges content into a responsive grid of rounded, equally-spaced cards ("compartments") inspired by Japanese bento boxes. The aesthetic is Apple-esque: clean, premium, and highly structured. Cells vary in size (1×1, 2×1, 1×2, 2×2) to create visual rhythm while maintaining strict geometric consistency.

**Visual DNA**
- **Colors**: Highly adaptable; pairs premium with Minimalist Slate or Yacht Club palettes. Background is slightly off-white or light gray so white compartments pop.
- **Typography**: Apple-esque (`SF Pro`, `Inter`). Headlines bold, placed top-left or bottom-left of each compartment.
- **Visuals**: High-quality edge-to-edge images or single large 3D icons inside specific grid cells to break up text-heavy cards.

**Core Principles**
1. **Strict Grid Structure** — Entire UI built on a responsive multi-column grid (3×3, 4×4, or irregular masonry).
2. **Rounded Compartments** — Every content piece lives in a card with consistent, large border-radius (24–32px web / 24–32pt mobile).
3. **Equal Spacing** — Gap between compartments is perfectly consistent everywhere (16px/16pt mobile, 24px web).

## When to Use

Trigger this skill when the user requests any of the following:
- "Bento grid" or "bento box" layout
- Modular dashboard with distinct rounded cards
- Apple-style compartment UI
- Grid of mixed-size content tiles
- A child reference of the `design-it` skill for structured card-based dashboards

Do **not** trigger for standard card lists, simple flex grids, or magazine-style masonry without the compartment aesthetic.

## Prerequisites

- **Web**: CSS Grid support (all modern browsers). Flexbox alone is insufficient for strict 2D bento structure.
- **Flutter**: `flutter_staggered_grid_view` package — practically mandatory for complex bento grids.
  ```powershell
  flutter pub add flutter_staggered_grid_view
  ```
- **SwiftUI**: iOS 14+ (LazyVGrid). Xcode 12+.
- **React Native**: RN 0.71+ (for `gap` support in flexbox). Older versions require margin-based spacing.
- **Jetpack Compose**: Compose 1.0+. `LazyVerticalGrid` available but manual Row/Column with `weight(1f)` is more reliable for irregular layouts.

## Procedure

### 1. Web — CSS Grid Implementation

CSS Grid is **mandatory**. Flexbox is too difficult to maintain the strict 2D structure.

```css
.bento-container {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  grid-auto-rows: 200px;
  gap: 24px;
  padding: 24px;
  background-color: var(--bg-primary); /* Slightly darker than cards */
}

.bento-card {
  background-color: #fff;
  border-radius: 32px; /* Very large border radius */
  padding: 32px;
  box-shadow: 0 4px 24px rgba(0,0,0,0.04);
  /* Optional: subtle 1px border for crispness */
  border: 1px solid rgba(0,0,0,0.05);

  display: flex;
  flex-direction: column;
  justify-content: space-between;
}

/* Creating spans for different bento sizes */
.bento-span-2 { grid-column: span 2; }
.bento-span-2-row { grid-row: span 2; }
.bento-large { grid-column: span 2; grid-row: span 2; }
```

**Steps:**
1. Define a `.bento-container` with `display: grid`, fixed column count, `grid-auto-rows`, and consistent `gap`.
2. Set the container background slightly darker than card backgrounds.
3. Create `.bento-card` with large `border-radius` (32px), generous `padding` (32px), and a very soft shadow.
4. Add span utility classes for 2×1, 1×2, and 2×2 cells.
5. Mix cell sizes deliberately — a grid of only 1×1 cells defeats the bento purpose.

### 2. SwiftUI Implementation

```swift
struct BentoGrid: View {
    let columns = [
        GridItem(.flexible(), spacing: 16),
        GridItem(.flexible(), spacing: 16)
    ]

    var body: some View {
        ScrollView {
            LazyVGrid(columns: columns, spacing: 16) {
                // 2x1 Span (Full width)
                BentoCard(title: "Hero", color: .blue)
                    .frame(height: 180)

                // 1x1 Spans
                BentoCard(title: "Stats", color: .green)
                    .frame(height: 180)
                BentoCard(title: "Graph", color: .purple)
                    .frame(height: 180)

                // 1x2 Span (Tall)
                BentoCard(title: "Activity", color: .orange)
                    .frame(height: 376) // (180 * 2) + 16 spacing

                // 1x1 Spans next to the tall one
                VStack(spacing: 16) {
                    BentoCard(title: "A", color: .pink).frame(height: 180)
                    BentoCard(title: "B", color: .cyan).frame(height: 180)
                }
            }
            .padding(16)
        }
        .background(Color(.systemGroupedBackground))
    }
}

struct BentoCard: View {
    let title: String
    let color: Color
    var body: some View {
        RoundedRectangle(cornerRadius: 24)
            .fill(Color(.secondarySystemGroupedBackground))
            .overlay(
                Text(title).font(.headline).foregroundColor(color),
                alignment: .topLeading
            )
            .padding(16)
            // Soft bento shadow
            .shadow(color: .black.opacity(0.04), radius: 12, x: 0, y: 4)
    }
}
```

**Steps:**
1. Use `LazyVGrid` for uniform grids with `GridItem(.flexible(), spacing: 16)`.
2. For complex irregular bento layouts (1×2 spans), mix `VStack` and `HStack` inside grid cells to fake spans.
3. Maintain absolute consistency: `cornerRadius` 24–32pt, `spacing` 16pt.
4. Use `Color(.systemGroupedBackground)` for the container and `Color(.secondarySystemGroupedBackground)` for cards.

### 3. Flutter Implementation

```dart
import 'package:flutter_staggered_grid_view/flutter_staggered_grid_view.dart';

class BentoScreen extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.grey[100],
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16),
        child: StaggeredGrid.count(
          crossAxisCount: 4, // 4 columns total
          mainAxisSpacing: 16,
          crossAxisSpacing: 16,
          children: const [
            // 2x1 (Full width in a 2-col layout, spans 4)
            StaggeredGridTile.count(
              crossAxisCellCount: 4,
              mainAxisCellCount: 2,
              child: BentoCard(title: 'Hero'),
            ),
            // 1x1
            StaggeredGridTile.count(
              crossAxisCellCount: 2,
              mainAxisCellCount: 2,
              child: BentoCard(title: 'Stats'),
            ),
            // 1x1
            StaggeredGridTile.count(
              crossAxisCellCount: 2,
              mainAxisCellCount: 2,
              child: BentoCard(title: 'Graph'),
            ),
            // 1x2 (Tall)
            StaggeredGridTile.count(
              crossAxisCellCount: 2,
              mainAxisCellCount: 4,
              child: BentoCard(title: 'Activity'),
            ),
          ],
        ),
      ),
    );
  }
}

class BentoCard extends StatelessWidget {
  final String title;
  const BentoCard({required this.title});

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(24),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(24),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.04),
            blurRadius: 12,
            offset: const Offset(0, 4),
          ),
        ],
      ),
      alignment: Alignment.topLeft,
      child: Text(title, style: const TextStyle(fontWeight: FontWeight.bold)),
    );
  }
}
```

**Steps:**
1. Add `flutter_staggered_grid_view` as a dependency.
2. Use `StaggeredGrid.count` with `crossAxisCount: 4` for a 4-column base grid.
3. Declare each tile with `StaggeredGridTile.count(crossAxisCellCount:, mainAxisCellCount:)` to explicitly set spans.
4. Set `mainAxisSpacing` and `crossAxisSpacing` to 16 for consistent gutters.
5. Card `borderRadius` 24, soft shadow with 0.04 opacity.

### 4. React Native Implementation

```jsx
const BentoScreen = () => {
  return (
    <ScrollView
      style={{ flex: 1, backgroundColor: '#F2F2F7' }}
      contentContainerStyle={{ padding: 16 }}
    >
      {/* 2x1 Span */}
      <View style={[styles.bentoCard, { height: 180, marginBottom: 16 }]}>
        <Text style={styles.title}>Hero</Text>
      </View>

      <View style={{ flexDirection: 'row', gap: 16, marginBottom: 16 }}>
        {/* 1x1 Spans */}
        <View style={[styles.bentoCard, { flex: 1, height: 180 }]}>
          <Text style={styles.title}>Stats</Text>
        </View>
        <View style={[styles.bentoCard, { flex: 1, height: 180 }]}>
          <Text style={styles.title}>Graph</Text>
        </View>
      </View>

      <View style={{ flexDirection: 'row', gap: 16 }}>
        {/* 1x2 Span (Tall) */}
        <View style={[styles.bentoCard, { flex: 1, height: 376 }]}>
          <Text style={styles.title}>Activity</Text>
        </View>

        <View style={{ flex: 1, gap: 16 }}>
          {/* Stacked 1x1s */}
          <View style={[styles.bentoCard, { height: 180 }]}>
            <Text style={styles.title}>A</Text>
          </View>
          <View style={[styles.bentoCard, { height: 180 }]}>
            <Text style={styles.title}>B</Text>
          </View>
        </View>
      </View>
    </ScrollView>
  );
};

const styles = StyleSheet.create({
  bentoCard: {
    backgroundColor: '#FFFFFF',
    borderRadius: 24,
    padding: 24,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.04,
    shadowRadius: 12,
    elevation: 2,
  },
  title: {
    fontWeight: '700',
    fontSize: 18,
  }
});
```

**Steps:**
1. React Native lacks CSS Grid — manually compose using `flexDirection: 'row'` and vertical stacks.
2. Use the `gap` property (RN 0.71+) for consistent gutters; fall back to margins on older versions.
3. Calculate tall card heights as `(cellHeight * 2) + gap` (e.g., `180*2 + 16 = 376`).
4. Card `borderRadius` 24, `shadowOpacity` 0.04, `elevation` 2 for Android.

### 5. Jetpack Compose Implementation

```kotlin
@Composable
fun BentoGrid() {
    Column(
        modifier = Modifier
            .fillMaxSize()
            .background(Color(0xFFF2F2F7))
            .verticalScroll(rememberScrollState())
            .padding(16.dp),
        verticalArrangement = Arrangement.spacedBy(16.dp)
    ) {
        // Full width
        BentoCard(title = "Hero", modifier = Modifier.fillMaxWidth().height(180.dp))

        // Two columns
        Row(horizontalArrangement = Arrangement.spacedBy(16.dp)) {
            BentoCard(title = "Stats", modifier = Modifier.weight(1f).height(180.dp))
            BentoCard(title = "Graph", modifier = Modifier.weight(1f).height(180.dp))
        }

        // Complex span: 1x2 left, two 1x1s right
        Row(horizontalArrangement = Arrangement.spacedBy(16.dp)) {
            BentoCard(title = "Activity", modifier = Modifier.weight(1f).height(376.dp))

            Column(
                modifier = Modifier.weight(1f),
                verticalArrangement = Arrangement.spacedBy(16.dp)
            ) {
                BentoCard(title = "A", modifier = Modifier.fillMaxWidth().height(180.dp))
                BentoCard(title = "B", modifier = Modifier.fillMaxWidth().height(180.dp))
            }
        }
    }
}

@Composable
fun BentoCard(title: String, modifier: Modifier = Modifier) {
    Card(
        modifier = modifier,
        shape = RoundedCornerShape(24.dp),
        colors = CardDefaults.cardColors(containerColor = Color.White),
        elevation = CardDefaults.cardElevation(defaultElevation = 2.dp)
    ) {
        Text(title, fontWeight = FontWeight.Bold, modifier = Modifier.padding(24.dp))
    }
}
```

**Steps:**
1. While `LazyVerticalGrid` exists, for irregular bento layouts, manually build Rows and Columns with `weight(1f)` — more reliable.
2. Use `Arrangement.spacedBy(16.dp)` on both Columns and Rows for mathematically perfect gutters.
3. Card `shape = RoundedCornerShape(24.dp)`, `defaultElevation = 2.dp`.
4. Container background `Color(0xFFF2F2F7)` (iOS systemGroupedBackground equivalent).

## Examples

### Sizing Patterns

| Pattern | CSS Grid | Flutter StaggeredGrid | Purpose |
|---------|----------|----------------------|---------|
| 1×1 | default | `count(2, 2)` | Standard content tile |
| 2×1 | `grid-column: span 2` | `count(4, 2)` | Hero / wide stat |
| 1×2 | `grid-row: span 2` | `count(2, 4)` | Tall activity feed |
| 2×2 | `grid-column: span 2; grid-row: span 2` | `count(4, 4)` | Featured content |

### Do's and Don'ts

- **DO**: Mix sizes — 2×1, 1×2, and 2×2 cells create visual interest. A grid of only 1×1 cells is not bento.
- **DO**: Keep card interiors minimal. If a card needs many elements, split into multiple cards.
- **DO**: Use a slightly darker container background so white cards pop.
- **DON'T**: Clutter the inside of a bento card with too many elements.
- **DON'T**: Use Flexbox for web bento grids — CSS Grid is mandatory for 2D structure.
- **DON'T**: Vary border-radius or spacing between cards — consistency is the entire aesthetic.

## Pitfalls

1. **Flexbox for web grids** — Flexbox cannot maintain strict 2D row/column alignment when cells span multiple rows. Always use CSS Grid.
2. **Inconsistent spacing** — Even 1px difference in gaps breaks the bento illusion. Use a single `gap` value everywhere.
3. **All 1×1 cells** — A uniform grid of identical tiles is a standard card grid, not bento. Deliberately mix at least 2 cell sizes.
4. **Overcrowded cards** — Bento cards should be glanceable. If content overflows, split into adjacent compartments.
5. **Flutter without staggered grid** — Standard `GridView` cannot produce irregular spans. The `flutter_staggered_grid_view` package is required.
6. **React Native `gap` on old versions** — `gap` in flexbox requires RN 0.71+. On older versions, use margins and calculate totals manually.
7. **SwiftUI span complexity** — `LazyVGrid` doesn't natively support row spans. You must nest `VStack`/`HStack` inside cells to fake tall spans.
8. **Shadow too strong** — Bento shadows should be barely visible (`opacity: 0.04`). Heavy shadows make it look like Material Design, not bento.
9. **Accessibility** — Visual grid structure does not guarantee logical screen-reader order. Verify reading order separately.

## Verification

### Web
1. Open browser DevTools → confirm `display: grid` is applied to container.
2. Check that all gaps are equal: inspect computed `gap` value — should be identical everywhere.
3. Resize viewport to mobile width — grid should reflow (use `auto-fit` or media queries).
4. Verify contrast ratios between card background and text meet WCAG AA.

### SwiftUI
1. Build in Xcode (Cmd+B) — no errors.
2. Run in Simulator — visually confirm equal spacing and consistent cornerRadius.
3. Test VoiceOver navigation order matches visual top-to-bottom, left-to-right flow.

### Flutter
1. Run `flutter analyze` — no errors.
2. Run on device/emulator — confirm staggered tiles render at correct spans.
3. Verify `flutter_staggered_grid_view` is in `pubspec.yaml`.

### React Native
1. Run `npx react-native run-android` and `run-ios` — confirm layout matches.
2. Check `gap` support: if RN < 0.71, verify margin-based fallback renders identically.
3. Inspect shadow on iOS (shadow props) and Android (elevation) — both should be subtle.

### Jetpack Compose
1. Build in Android Studio — no errors.
2. Run on emulator — confirm `Arrangement.spacedBy` produces identical gutters.
3. Verify tall card height equals `(cellHeight * 2) + spacing`.

## Related Skills

- **design-it** — Parent skill; trigger bento-ui as a child reference when the overall design system calls for compartment-style layouts.
- **Minimalist Slate** / **Yacht Club** — Recommended color palettes that pair premium with bento aesthetics.

## Limitations

- This is a styling reference and does not replace environment-specific validation, accessibility testing, or expert review.
- Ensure appropriate contrast ratios and responsive behaviors are verified separately.
- Code examples are starting templates — adapt spacing, radius, and column counts to the specific project's design tokens.
