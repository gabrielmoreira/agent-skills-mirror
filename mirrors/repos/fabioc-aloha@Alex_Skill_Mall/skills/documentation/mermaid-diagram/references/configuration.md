# Mermaid Configuration and Theming Reference

Complete guide to configuring and customizing Mermaid diagrams.

**Source**: mermaid-js/mermaid repository (packages/mermaid/src/docs/config/)

---

## Table of Contents

1. [Theme Options](#theme-options)
2. [Theme Customization](#theme-customization)
3. [Configuration Methods](#configuration-methods)
4. [Configuration Parameters](#configuration-parameters)
5. [Diagram-Specific Configuration](#diagram-specific-configuration)
6. [Layout Algorithms](#layout-algorithms)
7. [Accessibility Features](#accessibility-features)
8. [Security Configuration](#security-configuration)

---

## Theme Options

Mermaid provides **5 built-in themes**:

### default
The default theme for all diagrams. General-purpose with balanced colors.

### neutral
Great for black and white documents that will be printed. Minimal color usage.

### dark
Works well with dark-colored elements or dark-mode interfaces. Light text on dark backgrounds.

### forest
Contains shades of green. Nature-inspired color palette.

### base
**The only theme that can be modified via `themeVariables`**. Start with this for customization.

### Setting Theme

**Site-wide** (JavaScript):
```javascript
mermaid.initialize({
  theme: 'dark'
});
```

**Per-diagram** (frontmatter, v10.5.0+):
```markdown
---
config:
  theme: 'forest'
---
flowchart TD
    A --> B
```

**Per-diagram** (directive, deprecated):
```
%%{init: {'theme':'neutral'}}%%
flowchart TD
    A --> B
```

---

## Theme Customization

Only the **base** theme supports customization via `themeVariables`.

### Core Theme Variables

```markdown
---
config:
  theme: 'base'
  themeVariables:
    primaryColor: '#BB2528'
    primaryTextColor: '#fff'
    primaryBorderColor: '#7C0000'
    lineColor: '#F8B229'
    secondaryColor: '#006100'
    tertiaryColor: '#fff'
---
flowchart TD
    A --> B
```

### Available Theme Variables

**Colors**:
- `primaryColor` - Background color in nodes
- `primaryTextColor` - Text color in nodes
- `primaryBorderColor` - Border color
- `secondaryColor` - Secondary background color
- `tertiaryColor` - Tertiary background color
- `lineColor` - Line/edge colors
- `background` - Diagram background

**Typography**:
- `fontFamily` - Font family for diagram text
- `fontSize` - Font size (default: 16px)

**Dark Mode**:
- `darkMode` - Boolean affecting color calculations

### Color Derivation

Many colors are automatically calculated from primary colors:
- Setting `primaryColor` affects multiple derived colors
- The theme engine ensures visual harmony
- Secondary and tertiary colors cascade to related elements

### Example: Custom Corporate Theme

```markdown
---
config:
  theme: 'base'
  themeVariables:
    primaryColor: '#0066cc'
    primaryTextColor: '#ffffff'
    primaryBorderColor: '#004499'
    lineColor: '#0066cc'
    secondaryColor: '#99ccff'
    tertiaryColor: '#f0f8ff'
    background: '#ffffff'
    fontFamily: 'Arial, sans-serif'
    fontSize: '14px'
    darkMode: false
---
flowchart LR
    A --> B --> C
```

---

## Configuration Methods

Three ways to configure Mermaid diagrams:

### 1. Site-wide Initialization (JavaScript)

Applied once, affects all diagrams on the page.

```javascript
mermaid.initialize({
  theme: 'dark',
  logLevel: 'error',
  securityLevel: 'loose',
  startOnLoad: true,
  fontFamily: 'Arial',
  flowchart: {
    useMaxWidth: true,
    curve: 'basis'
  }
});
```

### 2. Frontmatter Config (YAML, v10.5.0+)

**RECOMMENDED** - Per-diagram configuration using YAML frontmatter.

```markdown
---
title: My Diagram Title
config:
  theme: base
  themeVariables:
    primaryColor: "#00ff00"
  flowchart:
    curve: linear
---
flowchart TD
    A --> B
```

### 3. Directives (Deprecated v10.5.0+)

Legacy method, replaced by frontmatter.

```
%%{init: {'theme':'forest', 'themeVariables': {'primaryColor':'#ff0000'}}}%%
flowchart TD
    A --> B
```

**Recommendation**: Use frontmatter for new diagrams.

---

## Configuration Parameters

### Top-Level Configuration

**Theme and Appearance**:
```yaml
theme: default | neutral | dark | forest | base
look: classic | handDrawn
fontFamily: "trebuchet ms, verdana, arial, sans-serif"
```

**Logging and Debug**:
```yaml
logLevel: trace | debug | info | warn | error | fatal
logLevel: 0 | 1 | 2 | 3 | 4 | 5  # Numeric equivalent
```

**Security**:
```yaml
securityLevel: strict | loose | sandbox
```

**Rendering**:
```yaml
startOnLoad: true | false
maxTextSize: 50000
maxEdges: 500
htmlLabels: true | false
layout: dagre | elk
```

### Configuration Hierarchy

Configuration is applied in order:

1. **Default values** (built into Mermaid)
2. **Site-level** (`mermaid.initialize()`)
3. **Frontmatter** (YAML config block)
4. **Directives** (deprecated, but highest priority)

Later configurations override earlier ones.

---

## Diagram-Specific Configuration

Each diagram type has its own configuration namespace.

### Flowchart

```yaml
config:
  flowchart:
    curve: basis | linear | monotoneX | monotoneY | natural | step | stepAfter | stepBefore
    diagramPadding: 8
    useMaxWidth: true
    rankSpacing: 50
    nodeSpacing: 50
    htmlLabels: true
```

### Sequence Diagram

```yaml
config:
  sequence:
    width: 150
    height: 65
    messageAlign: left | center | right
    mirrorActors: true | false
    wrap: false
    showSequenceNumbers: false
    actorMargin: 50
    boxMargin: 10
    noteMargin: 10
```

### Class Diagram

```yaml
config:
  class:
    useMaxWidth: true
    htmlLabels: false
    defaultRenderer: dagre | elk
```

### State Diagram

```yaml
config:
  state:
    dividerMargin: 10
    sizeUnit: 5
    padding: 8
    textHeight: 10
    titleShift: -15
    noteMargin: 10
    forkWidth: 70
    forkHeight: 7
```

### Gantt Chart

```yaml
config:
  gantt:
    titleTopMargin: 25
    barHeight: 20
    barGap: 4
    topPadding: 50
    leftPadding: 75
    gridLineStartPadding: 35
    fontSize: 11
    sectionFontSize: 11
    numberSectionStyles: 4
    displayMode: compact | classic
```

### ER Diagram

```yaml
config:
  er:
    diagramPadding: 20
    layoutDirection: TB | BT | LR | RL
    minEntityWidth: 100
    minEntityHeight: 75
    entityPadding: 15
    stroke: gray
    fill: honeydew
    fontSize: 12
```

### Pie Chart

```yaml
config:
  pie:
    useWidth: 960
    useMaxWidth: true
    textPosition: 0.75
```

### Git Graph

```yaml
config:
  gitGraph:
    mainBranchName: main
    orientation: LR | TB | BT
    showBranches: true
    showCommitLabel: true
    rotateCommitLabel: true
    parallelCommits: false
```

---

## Layout Algorithms

Mermaid supports multiple layout algorithms for different use cases.

### dagre (Default)

**Best for**: General-purpose layouts, flowcharts, class diagrams

```yaml
config:
  layout: dagre
```

Balanced, predictable layouts with good performance.

### elk

**Best for**: Complex diagrams, advanced customization

```yaml
config:
  layout: elk
  elk:
    nodePlacementStrategy: SIMPLE | LINEAR_SEGMENTS | BRANDES_KOEPF | NETWORK_SIMPLEX
    mergeEdges: true | false
```

More sophisticated algorithm with additional options:
- **SIMPLE**: Quick, basic placement
- **LINEAR_SEGMENTS**: Balanced node placement
- **BRANDES_KOEPF**: Minimizes edge crossings
- **NETWORK_SIMPLEX**: Optimizes edge lengths

### Examples

**ELK with edge merging**:
```markdown
---
config:
  layout: elk
  elk:
    mergeEdges: true
---
flowchart TD
    A --> B
    A --> C
    A --> D
```

---

## Accessibility Features

Mermaid automatically supports accessibility with proper configuration.

### Accessible Title

```
accTitle: User Login Flow
```

Generates `<title>` element in SVG for screen readers.

### Accessible Description

**Single-line**:
```
accDescr: This diagram shows the user authentication process
```

**Multi-line**:
```
accDescr {
    This is a comprehensive diagram showing
    the complete user authentication flow
    including error handling and session management
}
```

Generates `<desc>` element in SVG.

### aria-roledescription

Automatically set by Mermaid based on diagram type:
- `flowchart` → "flowchart-v2"
- `sequenceDiagram` → "sequence"
- etc.

### Complete Accessibility Example

```markdown
---
title: User Authentication Flow
---
flowchart TD
    accTitle: User Login Process
    accDescr {
        Diagram illustrating the user login workflow
        including credential validation and error handling
    }

    Start[User enters credentials] --> Valid{Credentials valid?}
    Valid -->|Yes| Success[Login successful]
    Valid -->|No| Error[Show error message]
```

### SVG Output

Generates:
```xml
<svg aria-roledescription="flowchart-v2" aria-labelledby="title-id" aria-describedby="desc-id">
    <title id="title-id">User Login Process</title>
    <desc id="desc-id">Diagram illustrating the user login workflow...</desc>
    ...
</svg>
```

---

## Security Configuration

### securityLevel

Controls trust level for diagram content.

**strict** (default):
- Most restrictive
- Disables click events
- Disables script tags
- Safe for untrusted content

**loose**:
- Enables click events
- Allows more interactivity
- Use only for trusted content

**sandbox**:
- Renders in sandboxed iframe
- Isolates diagram from page
- Prevents malicious scripts
- Some interactive features blocked

### Configuration

```javascript
mermaid.initialize({
  securityLevel: 'strict'
});
```

Or per-diagram:
```yaml
config:
  securityLevel: loose
```

### DOMPurify Integration

Mermaid uses DOMPurify by default to sanitize HTML.

**Custom DOMPurify config** (use with caution):
```javascript
mermaid.initialize({
  dompurifyConfig: {
    ALLOWED_TAGS: ['b', 'i', 'em', 'strong']
  }
});
```

### Best Practices

- Keep Mermaid updated to latest version
- Use `strict` for user-provided diagrams
- Regularly review security advisories
- Report vulnerabilities to security@mermaid.live
- Keep dependencies current

---

## Additional Features

### Handdrawn Look

Sketch-style rendering for informal diagrams.

```yaml
config:
  look: handDrawn
```

### Multiple Diagrams

Render multiple diagrams on the same page with different configs.

```html
<pre class="mermaid">
%%{init: {'theme':'forest'}}%%
flowchart TD
    A --> B
</pre>

<pre class="mermaid">
%%{init: {'theme':'dark'}}%%
sequenceDiagram
    A->>B: Message
</pre>
```

### CDN Delivery

Load Mermaid from CDN:

```html
<script type="module">
  import mermaid from 'https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.esm.min.mjs';
  mermaid.initialize({ startOnLoad: true });
</script>
```

---

## Configuration Examples

### Dark Mode Diagram

```markdown
---
config:
  theme: dark
  themeVariables:
    darkMode: true
  flowchart:
    curve: basis
---
flowchart LR
    A[Start] --> B{Check}
    B -->|Yes| C[Process]
    B -->|No| D[End]
```

### Handdrawn Sketch Style

```markdown
---
config:
  theme: neutral
  look: handDrawn
---
flowchart TD
    A --> B --> C
```

### Custom Corporate Theme

```markdown
---
config:
  theme: base
  themeVariables:
    primaryColor: '#0052cc'
    primaryTextColor: '#ffffff'
    lineColor: '#0052cc'
    background: '#f4f5f7'
    fontFamily: 'Inter, sans-serif'
---
sequenceDiagram
    User->>System: Request
    System-->>User: Response
```

### ELK Layout with Sequence

```markdown
---
config:
  layout: elk
  elk:
    nodePlacementStrategy: BRANDES_KOEPF
    mergeEdges: true
---
flowchart TD
    A --> B
    A --> C
    B --> D
    C --> D
```

---

## Configuration Schema

Complete configuration schema available at:
`mermaid-js/mermaid/packages/mermaid/src/schemas/config.schema.yaml`

Key documentation files:
- `/docs/config/theming.md`
- `/docs/config/configuration.md`
- `/docs/config/usage.md`
- `/docs/config/accessibility.md`

---

## Summary

**Themes**: 5 built-in (default, neutral, dark, forest, base)
**Customization**: Only `base` theme via themeVariables
**Methods**: Frontmatter (recommended), Initialize, Directives (deprecated)
**Security**: strict (default), loose, sandbox
**Layout**: dagre (default), elk, tidy tree
**Looks**: classic (default), handDrawn
**Accessibility**: accTitle, accDescr, automatic aria attributes

For syntax fundamentals, see **syntax.md**.
For best practices, see **best-practices.md**.
For diagram types, see **diagram-types.md**.
