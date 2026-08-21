---
name: matplotlib
description: "Builds Matplotlib figures with the OO Axes API: subplots, mosaic, GridSpec, rcParams, and savefig to PNG/PDF/SVG. Use for pyplot line, scatter, bar, hist, heatmap, contour, or 3D work in Python. Never route Seaborn estimators or Plotly Dash apps through this chair."
version: 1.0.1
license: https://github.com/matplotlib/matplotlib/tree/main/LICENSE
metadata:
  skill-author: K-Dense Inc.
risk: unknown
source: community
---

## When to Use

Use this skill when:

- Creating any type of plot or chart (line, scatter, bar, histogram, heatmap, contour, box, violin, 3D surface, etc.)
- Generating scientific or statistical visualizations
- Customizing plot appearance (colors, styles, labels, legends, annotations)
- Creating multi-panel figures with subplots, mosaic layouts, or GridSpec
- Exporting visualizations to PNG, PDF, SVG, or other formats
- Building interactive plots or animations
- Working with 3D visualizations
- Integrating plots into Jupyter notebooks or GUI applications

**Trigger keywords:** plot, chart, figure, axes, subplot, matplotlib, pyplot, visualization, heatmap, contour, histogram, scatter, bar chart, savefig, rcParams, colormap.

## Prerequisites

- Python 3.8+ installed and available on `PATH`
- Matplotlib installed: `pip install matplotlib` (NumPy is a required dependency and installs automatically)
- For Jupyter integration: `pip install jupyter` and run `%matplotlib inline` or `%matplotlib widget` in a notebook cell
- Windows host is primary (PowerShell). Use `python` (not `python3`) in PowerShell commands.

## Procedure

### 1. Choose the Interface

**Object-Oriented (RECOMMENDED for all production code):**

```python
import matplotlib.pyplot as plt

fig, ax = plt.subplots()
ax.plot([1, 2, 3, 4])
ax.set_ylabel('some numbers')
plt.show()
```

- Explicit control over Figure and Axes objects
- Better for complex figures with multiple subplots
- Easier to maintain and debug

**pyplot (MATLAB-style — quick exploration only):**

```python
import matplotlib.pyplot as plt

plt.plot([1, 2, 3, 4])
plt.ylabel('some numbers')
plt.show()
```

- Stateful; convenient for simple scripts
- Avoid in production code due to implicit state confusion

### 2. Create a Basic Plot (OO Interface)

```python
import matplotlib.pyplot as plt
import numpy as np

# Create figure and axes with explicit size
fig, ax = plt.subplots(figsize=(10, 6), constrained_layout=True)

# Generate and plot data
x = np.linspace(0, 2*np.pi, 100)
ax.plot(x, np.sin(x), label='sin(x)')
ax.plot(x, np.cos(x), label='cos(x)')

# Customize
ax.set_xlabel('x')
ax.set_ylabel('y')
ax.set_title('Trigonometric Functions')
ax.legend()
ax.grid(True, alpha=0.3)

# Save and/or display
plt.savefig('plot.png', dpi=300, bbox_inches='tight')
plt.show()
```

### 3. Create Multi-Panel Figures

**Regular grid:**

```python
fig, axes = plt.subplots(2, 2, figsize=(12, 10), constrained_layout=True)
axes[0, 0].plot(x, y1)
axes[0, 1].scatter(x, y2)
axes[1, 0].bar(categories, values)
axes[1, 1].hist(data, bins=30)
```

**Mosaic layout (flexible, label-based):**

```python
fig, axes = plt.subplot_mosaic([['left', 'right_top'],
                                 ['left', 'right_bottom']],
                                figsize=(10, 8))
axes['left'].plot(x, y)
axes['right_top'].scatter(x, y)
axes['right_bottom'].hist(data)
```

**GridSpec (maximum control):**

```python
from matplotlib.gridspec import GridSpec

fig = plt.figure(figsize=(12, 8))
gs = GridSpec(3, 3, figure=fig)
ax1 = fig.add_subplot(gs[0, :])    # Top row, all columns
ax2 = fig.add_subplot(gs[1:, 0])   # Bottom two rows, first column
ax3 = fig.add_subplot(gs[1:, 1:])  # Bottom two rows, last two columns
```

### 4. Select Plot Types

| Plot Type | Use Case | Example Call |
|-----------|----------|--------------|
| Line | Time series, trends | `ax.plot(x, y, linewidth=2, linestyle='--', marker='o', color='blue')` |
| Scatter | Correlations | `ax.scatter(x, y, s=sizes, c=colors, alpha=0.6, cmap='viridis')` |
| Bar | Categorical comparisons | `ax.bar(categories, values, color='steelblue', edgecolor='black')` |
| Horizontal bar | Long labels | `ax.barh(categories, values)` |
| Histogram | Distributions | `ax.hist(data, bins=30, edgecolor='black', alpha=0.7)` |
| Heatmap | Matrix data | `im = ax.imshow(matrix, cmap='coolwarm', aspect='auto')` then `plt.colorbar(im, ax=ax)` |
| Contour | 3D data on 2D | `contour = ax.contour(X, Y, Z, levels=10)` then `ax.clabel(contour, inline=True, fontsize=8)` |
| Box | Statistical distributions | `ax.boxplot([data1, data2, data3], labels=['A', 'B', 'C'])` |
| Violin | Distribution densities | `ax.violinplot([data1, data2, data3], positions=[1, 2, 3])` |

For specialized plot types beyond the table, use the official gallery: https://matplotlib.org/stable/gallery/index.html

### 5. Apply Styling and Customization

**Color specification methods:**

- Named colors: `'red'`, `'blue'`, `'steelblue'`
- Hex codes: `'#FF5733'`
- RGB tuples: `(0.1, 0.2, 0.3)`
- Colormaps: `cmap='viridis'`, `cmap='plasma'`, `cmap='coolwarm'`

**Style sheets:**

```python
plt.style.use('seaborn-v0_8-darkgrid')
print(plt.style.available)  # List all available styles
# Common: 'ggplot', 'bmh', 'fivethirtyeight', 'seaborn-v0_8-darkgrid'
```

**rcParams for global defaults:**

```python
plt.rcParams['font.size'] = 12
plt.rcParams['axes.labelsize'] = 14
plt.rcParams['axes.titlesize'] = 16
plt.rcParams['xtick.labelsize'] = 10
plt.rcParams['ytick.labelsize'] = 10
plt.rcParams['legend.fontsize'] = 12
plt.rcParams['figure.titlesize'] = 18
```

**Text and annotations:**

```python
ax.text(x, y, 'annotation', fontsize=12, ha='center')
ax.annotate('important point', xy=(x, y), xytext=(x+1, y+1),
            arrowprops=dict(arrowstyle='->', color='red'))
```

For colormap and style-sheet options, prefer perceptually uniform maps (`viridis`, `plasma`, `cividis`) and the official cheatsheets: https://matplotlib.org/cheatsheets/

### 6. Save and Export Figures

```python
# High-resolution PNG for presentations/papers
plt.savefig('figure.png', dpi=300, bbox_inches='tight', facecolor='white')

# Vector format for publications (scalable)
plt.savefig('figure.pdf', bbox_inches='tight')
plt.savefig('figure.svg', bbox_inches='tight')

# Transparent background
plt.savefig('figure.png', dpi=300, bbox_inches='tight', transparent=True)
```

**Key parameters:**

| Parameter | Purpose | Recommended Value |
|-----------|---------|-------------------|
| `dpi` | Resolution | 300 for publications, 150 for web, 72 for screen |
| `bbox_inches='tight'` | Remove excess whitespace | Always use |
| `facecolor='white'` | Ensure white background | Use with dark themes |
| `transparent=True` | Transparent background | For overlays |

### 7. Create 3D Plots

```python
from mpl_toolkits.mplot3d import Axes3D

fig = plt.figure(figsize=(10, 8))
ax = fig.add_subplot(111, projection='3d')

# Surface plot
ax.plot_surface(X, Y, Z, cmap='viridis')

# 3D scatter
ax.scatter(x, y, z, c=colors, marker='o')

# 3D line plot
ax.plot(x, y, z, linewidth=2)

ax.set_xlabel('X Label')
ax.set_ylabel('Y Label')
ax.set_zlabel('Z Label')
```

### 8. Confirm Unfamiliar APIs

Look up method signatures on the Matplotlib API index (https://matplotlib.org/stable/api/index.html) rather than guessing `Axes`/`Figure` parameters. Gallery examples at https://matplotlib.org/stable/gallery/index.html cover specialized plot types.

### 9. Organize Reusable Plot Code

```python
def create_analysis_plot(data, title):
    """Create standardized analysis plot."""
    fig, ax = plt.subplots(figsize=(10, 6), constrained_layout=True)

    ax.plot(data['x'], data['y'], linewidth=2)

    ax.set_xlabel('X Axis Label', fontsize=12)
    ax.set_ylabel('Y Axis Label', fontsize=12)
    ax.set_title(title, fontsize=14, fontweight='bold')
    ax.grid(True, alpha=0.3)

    return fig, ax

fig, ax = create_analysis_plot(my_data, 'My Analysis')
plt.savefig('analysis.png', dpi=300, bbox_inches='tight')
```

## Pitfalls

1. **Overlapping elements** — Use `constrained_layout=True` at figure creation or call `fig.tight_layout()` before saving. Do not use both together.
2. **State confusion with pyplot interface** — The pyplot state machine tracks the "current" figure/axes implicitly. Use the OO interface (`fig, ax = plt.subplots()`) to avoid ambiguity in production code.
3. **Memory leaks with many figures** — Always close figures explicitly with `plt.close(fig)` when generating many plots in a loop. Unclosed figures accumulate in memory.
4. **Font warnings** — If fonts are missing, suppress warnings by setting `plt.rcParams['font.sans-serif'] = ['DejaVu Sans']` or install the required font package.
5. **DPI confusion** — `figsize` is in inches, not pixels. Final pixel dimensions: `pixels = dpi * inches`. A `(10, 6)` figure at 300 dpi produces a 3000×1800 image.
6. **Rainbow colormaps (jet)** — Not perceptually uniform; can misrepresent data. Use `viridis`, `plasma`, `inferno`, or `cividis` instead.
7. **Large dataset file size** — For scatter/line plots with many points, pass `rasterized=True` to reduce PDF/SVG file size. Downsample dense time series before plotting.
8. **`show()` blocks in scripts** — `plt.show()` blocks execution in non-interactive scripts. Call `savefig()` before `show()` to ensure the file is written.
9. **Style name changes** — Seaborn styles were renamed in matplotlib 3.6+ (e.g., `'seaborn-darkgrid'` → `'seaborn-v0_8-darkgrid'`). Use `plt.style.available` to check valid names.

## Verification

### Check Installation

```powershell
python -c "import matplotlib; print(matplotlib.__version__)"
```

Expected output (version may differ):

```
3.9.0
```

### Verify a Plot Renders and Saves

```powershell
python -c "import matplotlib.pyplot as plt; fig, ax = plt.subplots(); ax.plot([1,2,3,4]); plt.savefig('test_plot.png', dpi=150, bbox_inches='tight'); print('OK')"
```

Expected output:

```
OK
```

Verify the file exists:

```powershell
Test-Path .\test_plot.png
```

Expected output:

```
True
```

### Verify Available Styles

```powershell
python -c "import matplotlib.pyplot as plt; print(plt.style.available)"
```

### Verify Backend (Non-Interactive / Headless)

```powershell
python -c "import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt; print(matplotlib.get_backend())"
```

Expected output:

```
Agg
```

## Related Skills

- **numpy** — Array generation and numerical data feeding into plots
- **pandas** — DataFrame-based plotting and data manipulation
- **seaborn** — High-level statistical visualizations built on matplotlib

## Additional Resources

- Official documentation: https://matplotlib.org/
- Gallery: https://matplotlib.org/stable/gallery/index.html
- Cheatsheets: https://matplotlib.org/cheatsheets/
- Tutorials: https://matplotlib.org/stable/tutorials/index.html

## Limitations

- Use this skill only when the task clearly matches the scope described above.
- Do not treat the output as a substitute for environment-specific validation, testing, or expert review.
- Stop and ask for clarification if required inputs, permissions, safety boundaries, or success criteria are missing.
