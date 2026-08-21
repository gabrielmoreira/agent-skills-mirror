---
name: seaborn
description: "Draws dataset-oriented statistical graphics with seaborn: relplot, displot, catplot, lmplot, hue/size/style encodings, and seaborn.objects Plot layers on tidy pandas frames. Use for grouped estimates, KDE/ECDF, regression bands, or faceted publication figures. Never send Matplotlib Axes/GridSpec/rcParams construction or Altair/Vega chart specs here."
version: 1.0.1
license: BSD-3-Clause license
metadata:
    skill-author: K-Dense Inc.
risk: unknown
source: community
---

## When to Use
- You need publication-quality statistical graphics directly from tabular datasets.
- You are exploring multivariate relationships, distributions, or grouped comparisons with minimal plotting code.
- You want seaborn's dataset-oriented API and statistical defaults on top of matplotlib.

## Prerequisites
- Python environment with `seaborn`, `pandas`, and `matplotlib` installed.
- Windows host (PowerShell) is primary. Ensure your Python environment is activated before running scripts.

## Procedure

1. **Import Libraries and Load Data**
   Always use well-structured DataFrames with meaningful column names.
   ```python
   import seaborn as sns
   import matplotlib.pyplot as plt
   import pandas as pd

   df = sns.load_dataset('tips')
   ```

2. **Choose Plotting Interface**
   - **Function Interface (Traditional):** Use for quick exploratory analysis and single-purpose visualizations.
     ```python
     sns.scatterplot(data=df, x='total_bill', y='tip', hue='day')
     plt.show()
     ```
   - **Objects Interface (Modern):** Use for complex layered visualizations and fine-grained control over transformations.
     ```python
     from seaborn import objects as so
     (
         so.Plot(data=df, x='total_bill', y='tip')
         .add(so.Dot(), color='day')
         .add(so.Line(), so.PolyFit())
     )
     ```

3. **Select Plot Type by Category**
   - **Relational:** `scatterplot()`, `lineplot()`, `relplot()` (figure-level).
   - **Distribution:** `histplot()`, `kdeplot()`, `ecdfplot()`, `rugplot()`, `displot()`, `jointplot()`, `pairplot()`.
   - **Categorical:** `stripplot()`, `swarmplot()`, `boxplot()`, `violinplot()`, `boxenplot()`, `barplot()`, `pointplot()`, `countplot()`, `catplot()`.
   - **Regression:** `regplot()`, `lmplot()`, `residplot()`.
   - **Matrix:** `heatmap()`, `clustermap()`.

4. **Apply Semantic Mappings**
   Use `hue`, `size`, and `style` to encode additional dimensions.
   ```python
   sns.scatterplot(data=df, x='total_bill', y='tip', hue='time', size='size', style='sex')
   ```

5. **Configure Theming and Aesthetics**
   ```python
   sns.set_theme(style='whitegrid', palette='pastel', font='sans-serif')
   sns.set_context("talk", font_scale=1.2)
   ```

6. **Combine with Matplotlib for Custom Layouts**
   Use axes-level functions with `ax=` parameter for complex multi-panel figures. Figure-level functions cannot be placed in existing figures.
   ```python
   fig, axes = plt.subplots(2, 2, figsize=(10, 10))
   sns.scatterplot(data=df, x='x', y='y', ax=axes[0, 0])
   sns.histplot(data=df, x='x', ax=axes[0, 1])
   plt.tight_layout()
   ```

7. **Save High-Quality Figures**
   ```python
   fig = sns.relplot(data=df, x='x', y='y', col='group')
   fig.savefig('figure.png', dpi=300, bbox_inches='tight')
   fig.savefig('figure.pdf')  # Vector format for publications
   ```

## Pitfalls
- **Figure-Level vs Axes-Level:** Figure-level functions (`relplot`, `displot`, `catplot`, `lmplot`, `jointplot`, `pairplot`) manage the entire figure and cannot be placed in existing matplotlib subplots using `ax=`. Use axes-level functions (`scatterplot`, `histplot`, etc.) for custom layouts.
- **Data Format:** Seaborn prefers long-form (tidy) data where each variable is a column. Wide-form data works for simple cases but limits flexibility. Convert using `df.melt(var_name='condition', value_name='measurement')`.
- **Overlapping Labels:** Rotate x-ticks and use tight layout: `plt.xticks(rotation=45, ha='right'); plt.tight_layout()`.
- **KDE Smoothness:** If KDE is too smooth or jagged, adjust bandwidth: `sns.kdeplot(data=df, x='x', bw_adjust=0.5)`.
- **Legend Position:** Figure-level functions place legends outside. Move using `g._legend.set_bbox_to_anchor((0.9, 0.5))`.
- **Colors Not Distinct:** Use `sns.set_palette("bright")` or specify `n_colors` in `sns.color_palette("husl", n_colors=len(df['category'].unique()))`.

## Verification
1. **Check Library Installation:**
   ```powershell
   python -c "import seaborn; print(seaborn.__version__)"
   ```
   Expected output: A version number (e.g., `0.12.2`).

2. **Run Test Plot:**
   ```python
   import seaborn as sns
   import matplotlib.pyplot as plt
   df = sns.load_dataset('tips')
   sns.scatterplot(data=df, x='total_bill', y='tip', hue='day')
   plt.show()
   ```
   Expected output: A scatter plot window displaying total bill vs tip, colored by day.

## Official docs

Function names, parameters, and gallery patterns live in seaborn's docs (v0.13), not in this folder:

- Function API: https://seaborn.pydata.org/api.html
- Objects interface (`seaborn.objects.Plot`): https://seaborn.pydata.org/tutorial/objects_interface.html
- Example gallery: https://seaborn.pydata.org/examples/index.html
