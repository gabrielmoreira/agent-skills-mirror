---
name: "data-visualization"
description: "Create visualizations for construction data. Generate charts, graphs, heatmaps, and interactive dashboards using Matplotlib, Seaborn, and Plotly for project analysis and reporting."
homepage: "https://datadrivenconstruction.io"
metadata: {"openclaw": {"emoji": "📈", "os": ["darwin", "linux", "win32"], "homepage": "https://datadrivenconstruction.io", "requires": {"bins": ["python3"]}}}
---
# Data Visualization for Construction

## Overview

Based on DDC methodology (Chapter 4.1), this skill provides comprehensive data visualization techniques for construction analytics. Visual insights drive better decisions - from cost breakdowns to schedule analysis.

**Book Reference:** "Аналитика данных и принятие решений" / "Data Analytics and Decision Making"

> "Визуализация данных превращает сложные наборы данных в понятные графики, которые могут использоваться для принятия решений на всех уровнях проекта."
> — DDC Book, Chapter 4.1

## Quick Start

```python
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Load construction data
df = pd.read_excel("project_data.xlsx")

# Quick bar chart - volumes by category
fig, ax = plt.subplots(figsize=(10, 6))
df.groupby('Category')['Volume_m3'].sum().plot(kind='bar', ax=ax)
ax.set_title('Volume by Category')
ax.set_ylabel('Volume (m³)')
plt.tight_layout()
plt.savefig('volume_by_category.png', dpi=150)
plt.show()
```

## Matplotlib Fundamentals

### Basic Charts for Construction

```python
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

def create_cost_breakdown_pie(df, cost_col='Cost', category_col='Category'):
    """Create pie chart for cost breakdown"""
    costs = df.groupby(category_col)[cost_col].sum()

    fig, ax = plt.subplots(figsize=(10, 8))

    # Create pie with percentage labels
    wedges, texts, autotexts = ax.pie(
        costs.values,
        labels=costs.index,
        autopct='%1.1f%%',
        startangle=90,
        colors=plt.cm.Set3.colors
    )

    ax.set_title('Cost Breakdown by Category', fontsize=14, fontweight='bold')

    # Add total in center
    ax.text(0, 0, f'Total:\n${costs.sum():,.0f}',
            ha='center', va='center', fontsize=12)

    plt.tight_layout()
    return fig

def create_volume_bar_chart(df, volume_col='Volume_m3', category_col='Category'):
    """Create horizontal bar chart for volumes"""
    volumes = df.groupby(category_col)[volume_col].sum().sort_values()

    fig, ax = plt.subplots(figsize=(10, 6))

    bars = ax.barh(volumes.index, volumes.values, color='steelblue')

    # Add value labels
    for bar, value in zip(bars, volumes.values):
        ax.text(value + volumes.max() * 0.01, bar.get_y() + bar.get_height()/2,
                f'{value:,.0f} m³', va='center', fontsize=10)

    ax.set_xlabel('Volume (m³)')
    ax.set_title('Material Volumes by Category', fontsize=14, fontweight='bold')
    ax.set_xlim(0, volumes.max() * 1.15)

    plt.tight_layout()
    return fig

def create_level_comparison(df, value_col='Volume_m3', level_col='Level'):
    """Create grouped bar chart comparing levels"""
    pivot = df.pivot_table(
        values=value_col,
        index=level_col,
        columns='Category',
        aggfunc='sum',
        fill_value=0
    )

    fig, ax = plt.subplots(figsize=(12, 6))
    pivot.plot(kind='bar', ax=ax, width=0.8)

    ax.set_xlabel('Building Level')
    ax.set_ylabel('Volume (m³)')
    ax.set_title('Volume Distribution by Level and Category', fontsize=14, fontweight='bold')
    ax.legend(title='Category', bbox_to_anchor=(1.02, 1), loc='upper left')

    plt.xticks(rotation=45)
    plt.tight_layout()
    return fig
```

### Time Series Visualization

```python
def create_progress_chart(df, date_col='Date', value_col='Cumulative_Progress'):
    """Create S-curve progress chart"""
    df = df.sort_values(date_col)

    fig, ax = plt.subplots(figsize=(12, 6))

    # Actual progress
    ax.plot(df[date_col], df[value_col],
            'b-', linewidth=2, label='Actual Progress')

    # Planned progress (if available)
    if 'Planned_Progress' in df.columns:
        ax.plot(df[date_col], df['Planned_Progress'],
                'g--', linewidth=2, label='Planned Progress')

    ax.fill_between(df[date_col], 0, df[value_col], alpha=0.3)

    ax.set_xlabel('Date')
    ax.set_ylabel('Progress (%)')
    ax.set_title('Project S-Curve', fontsize=14, fontweight='bold')
    ax.legend()
    ax.grid(True, alpha=0.3)

    # Format dates
    fig.autofmt_xdate()

    plt.tight_layout()
    return fig

def create_gantt_chart(df, start_col='Start', end_col='End', task_col='Task'):
    """Create simple Gantt chart"""
    df = df.sort_values(start_col)

    fig, ax = plt.subplots(figsize=(14, len(df) * 0.5 + 2))

    # Plot each task as horizontal bar
    for i, (_, row) in enumerate(df.iterrows()):
        start = pd.to_datetime(row[start_col])
        end = pd.to_datetime(row[end_col])
        duration = (end - start).days

        ax.barh(i, duration, left=start, height=0.6,
                align='center', color='steelblue', alpha=0.8)

    ax.set_yticks(range(len(df)))
    ax.set_yticklabels(df[task_col])
    ax.set_xlabel('Date')
    ax.set_title('Project Schedule - Gantt Chart', fontsize=14, fontweight='bold')
    ax.grid(axis='x', alpha=0.3)

    fig.autofmt_xdate()
    plt.tight_layout()
    return fig
```

## Seaborn for Statistical Visualization

### Distribution Analysis

```python
import seaborn as sns

def create_distribution_analysis(df, value_col='Volume_m3', category_col='Category'):
    """Create distribution plots for construction data"""
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))

    # 1. Histogram with KDE
    sns.histplot(data=df, x=value_col, kde=True, ax=axes[0, 0])
    axes[0, 0].set_title('Volume Distribution')

    # 2. Box plot by category
    sns.boxplot(data=df, x=category_col, y=value_col, ax=axes[0, 1])
    axes[0, 1].set_xticklabels(axes[0, 1].get_xticklabels(), rotation=45)
    axes[0, 1].set_title('Volume by Category')

    # 3. Violin plot
    sns.violinplot(data=df, x=category_col, y=value_col, ax=axes[1, 0])
    axes[1, 0].set_xticklabels(axes[1, 0].get_xticklabels(), rotation=45)
    axes[1, 0].set_title('Volume Distribution by Category')

    # 4. Strip plot with jitter
    sns.stripplot(data=df, x=category_col, y=value_col,
                  ax=axes[1, 1], alpha=0.5, jitter=True)
    axes[1, 1].set_xticklabels(axes[1, 1].get_xticklabels(), rotation=45)
    axes[1, 1].set_title('Individual Elements')

    plt.tight_layout()
    return fig

def create_correlation_heatmap(df, numeric_cols=None):
    """Create correlation heatmap for numeric columns"""
    if numeric_cols is None:
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()

    corr_matrix = df[numeric_cols].corr()

    fig, ax = plt.subplots(figsize=(10, 8))

    sns.heatmap(corr_matrix,
                annot=True,
                cmap='RdYlBu_r',
                center=0,
                fmt='.2f',
                square=True,
                ax=ax)

    ax.set_title('Correlation Matrix', fontsize=14, fontweight='bold')

    plt.tight_layout()
    return fig
```

### Category Analysis

```python
def create_category_summary(df, category_col='Category',
                            value_col='Volume_m3', cost_col='Cost'):
    """Create comprehensive category summary visualization"""
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))

    # 1. Count by category
    category_counts = df[category_col].value_counts()
    sns.barplot(x=category_counts.index, y=category_counts.values, ax=axes[0, 0])
    axes[0, 0].set_title('Element Count by Category')
    axes[0, 0].set_xticklabels(axes[0, 0].get_xticklabels(), rotation=45)

    # 2. Total volume by category
    volumes = df.groupby(category_col)[value_col].sum().sort_values(ascending=False)
    sns.barplot(x=volumes.index, y=volumes.values, ax=axes[0, 1])
    axes[0, 1].set_title('Total Volume by Category')
    axes[0, 1].set_xticklabels(axes[0, 1].get_xticklabels(), rotation=45)

    # 3. Average cost by category
    if cost_col in df.columns:
        avg_cost = df.groupby(category_col)[cost_col].mean().sort_values(ascending=False)
        sns.barplot(x=avg_cost.index, y=avg_cost.values, ax=axes[1, 0])
        axes[1, 0].set_title('Average Cost by Category')
        axes[1, 0].set_xticklabels(axes[1, 0].get_xticklabels(), rotation=45)

    # 4. Volume vs Cost scatter
    if cost_col in df.columns:
        sns.scatterplot(data=df, x=value_col, y=cost_col,
                        hue=category_col, alpha=0.7, ax=axes[1, 1])
        axes[1, 1].set_title('Volume vs Cost')
        axes[1, 1].legend(bbox_to_anchor=(1.02, 1), loc='upper left')

    plt.tight_layout()
    return fig
```

## Plotly for Interactive Dashboards

### Interactive Charts

```python
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

def create_interactive_cost_breakdown(df, category_col='Category', cost_col='Cost'):
    """Create interactive sunburst chart"""
    # Aggregate by category and material
    agg_df = df.groupby([category_col, 'Material'])[cost_col].sum().reset_index()

    fig = px.sunburst(
        agg_df,
        path=[category_col, 'Material'],
        values=cost_col,
        title='Cost Breakdown by Category and Material'
    )

    fig.update_layout(height=600)
    return fig

def create_interactive_3d_scatter(df, x_col='Volume_m3', y_col='Cost',
                                   z_col='Weight_kg', color_col='Category'):
    """Create 3D scatter plot for multi-dimensional analysis"""
    fig = px.scatter_3d(
        df,
        x=x_col,
        y=y_col,
        z=z_col,
        color=color_col,
        hover_data=['ElementId'],
        title='3D Analysis: Volume vs Cost vs Weight'
    )

    fig.update_layout(height=700)
    return fig

def create_interactive_timeline(df, date_col='Date', value_col='Progress',
                                 category_col='Phase'):
    """Create interactive timeline with range slider"""
    fig = px.line(
        df,
        x=date_col,
        y=value_col,
        color=category_col,
        title='Project Progress Timeline'
    )

    fig.update_layout(
        xaxis=dict(
            rangeselector=dict(
                buttons=list([
                    dict(count=1, label="1m", step="month", stepmode="backward"),
                    dict(count=3, label="3m", step="month", stepmode="backward"),
                    dict(count=6, label="6m", step="month", stepmode="backward"),
                    dict(step="all", label="All")
                ])
            ),
            rangeslider=dict(visible=True),
            type="date"
        ),
        height=500
    )

    return fig
```

### Dashboard Layout

```python
def create_project_dashboard(df):
    """Create comprehensive project dashboard"""
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=(
            'Cost by Category',
            'Volume Distribution',
            'Elements by Level',
            'Progress Over Time'
        ),
        specs=[
            [{"type": "pie"}, {"type": "bar"}],
            [{"type": "bar"}, {"type": "scatter"}]
        ]
    )

    # 1. Cost pie chart
    costs = df.groupby('Category')['Cost'].sum()
    fig.add_trace(
        go.Pie(labels=costs.index, values=costs.values, name='Cost'),
        row=1, col=1
    )

    # 2. Volume bar chart
    volumes = df.groupby('Category')['Volume_m3'].sum().sort_values(ascending=True)
    fig.add_trace(
        go.Bar(x=volumes.values, y=volumes.index, orientation='h', name='Volume'),
        row=1, col=2
    )

    # 3. Elements by level
    level_counts = df.groupby('Level').size()
    fig.add_trace(
        go.Bar(x=level_counts.index, y=level_counts.values, name='Count'),
        row=2, col=1
    )

    # 4. Progress scatter (if available)
    if 'Date' in df.columns and 'Progress' in df.columns:
        fig.add_trace(
            go.Scatter(x=df['Date'], y=df['Progress'], mode='lines+markers', name='Progress'),
            row=2, col=2
        )

    fig.update_layout(
        height=800,
        title_text='Project Analytics Dashboard',
        showlegend=False
    )

    return fig
```

## Construction-Specific Visualizations

### Heatmaps for Level Analysis

```python
def create_level_heatmap(df, level_col='Level', category_col='Category',
                          value_col='Volume_m3'):
    """Create heatmap for level-by-category analysis"""
    pivot = df.pivot_table(
        values=value_col,
        index=level_col,
        columns=category_col,
        aggfunc='sum',
        fill_value=0
    )

    fig, ax = plt.subplots(figsize=(12, 8))

    sns.heatmap(
        pivot,
        annot=True,
        fmt=',.0f',
        cmap='YlOrRd',
        ax=ax,
        cbar_kws={'label': 'Volume (m³)'}
    )

    ax.set_title('Volume Distribution: Level × Category', fontsize=14, fontweight='bold')

    plt.tight_layout()
    return fig

def create_material_treemap(df, category_col='Category', material_col='Material',
                             value_col='Volume_m3'):
    """Create treemap for hierarchical material analysis"""
    agg_df = df.groupby([category_col, material_col])[value_col].sum().reset_index()

    fig = px.treemap(
        agg_df,
        path=[category_col, material_col],
        values=value_col,
        title='Material Distribution Treemap',
        color=value_col,
        color_continuous_scale='Blues'
    )

    fig.update_layout(height=600)
    return fig
```

### Cost Analysis Charts

```python
def create_cost_analysis_dashboard(df):
    """Create comprehensive cost analysis visualization"""
    fig, axes = plt.subplots(2, 3, figsize=(18, 10))

    # 1. Cost distribution histogram
    sns.histplot(data=df, x='Cost', bins=30, ax=axes[0, 0])
    axes[0, 0].set_title('Cost Distribution')
    axes[0, 0].axvline(df['Cost'].mean(), color='r', linestyle='--', label='Mean')
    axes[0, 0].axvline(df['Cost'].median(), color='g', linestyle='--', label='Median')
    axes[0, 0].legend()

    # 2. Cost by category (box plot)
    sns.boxplot(data=df, x='Category', y='Cost', ax=axes[0, 1])
    axes[0, 1].set_xticklabels(axes[0, 1].get_xticklabels(), rotation=45)
    axes[0, 1].set_title('Cost Range by Category')

    # 3. Cumulative cost
    sorted_costs = df.sort_values('Cost', ascending=False)
    sorted_costs['Cumulative_Cost'] = sorted_costs['Cost'].cumsum()
    sorted_costs['Cumulative_Pct'] = sorted_costs['Cumulative_Cost'] / sorted_costs['Cost'].sum() * 100
    axes[0, 2].plot(range(len(sorted_costs)), sorted_costs['Cumulative_Pct'])
    axes[0, 2].axhline(80, color='r', linestyle='--', alpha=0.5)
    axes[0, 2].set_xlabel('Number of Elements')
    axes[0, 2].set_ylabel('Cumulative Cost %')
    axes[0, 2].set_title('Pareto Analysis (80/20)')

    # 4. Cost per unit volume
    df['Cost_per_m3'] = df['Cost'] / df['Volume_m3'].replace(0, np.nan)
    by_cat = df.groupby('Category')['Cost_per_m3'].mean().sort_values(ascending=True)
    axes[1, 0].barh(by_cat.index, by_cat.values)
    axes[1, 0].set_title('Average Cost per m³ by Category')

    # 5. Top 10 elements by cost
    top10 = df.nlargest(10, 'Cost')
    axes[1, 1].barh(top10['ElementId'], top10['Cost'])
    axes[1, 1].set_title('Top 10 Elements by Cost')

    # 6. Cost vs Volume scatter with regression
    sns.regplot(data=df, x='Volume_m3', y='Cost', ax=axes[1, 2],
                scatter_kws={'alpha': 0.5})
    axes[1, 2].set_title('Cost vs Volume (with Trend)')

    plt.tight_layout()
    return fig
```

## Export and Reporting

### Save Visualizations

```python
def save_all_visualizations(df, output_dir='reports/charts'):
    """Generate and save all standard visualizations"""
    import os
    os.makedirs(output_dir, exist_ok=True)

    # Generate charts
    charts = {
        'cost_breakdown': create_cost_breakdown_pie(df),
        'volume_bars': create_volume_bar_chart(df),
        'distribution': create_distribution_analysis(df),
        'level_heatmap': create_level_heatmap(df)
    }

    # Save each chart
    saved_files = []
    for name, fig in charts.items():
        filepath = f"{output_dir}/{name}.png"
        fig.savefig(filepath, dpi=150, bbox_inches='tight')
        plt.close(fig)
        saved_files.append(filepath)

    return saved_files

def create_pdf_report(df, output_path='project_report.pdf'):
    """Create PDF report with multiple visualizations"""
    from matplotlib.backends.backend_pdf import PdfPages

    with PdfPages(output_path) as pdf:
        # Page 1: Overview
        fig1 = create_cost_breakdown_pie(df)
        pdf.savefig(fig1)
        plt.close(fig1)

        # Page 2: Volume analysis
        fig2 = create_volume_bar_chart(df)
        pdf.savefig(fig2)
        plt.close(fig2)

        # Page 3: Distribution
        fig3 = create_distribution_analysis(df)
        pdf.savefig(fig3)
        plt.close(fig3)

        # Page 4: Heatmap
        fig4 = create_level_heatmap(df)
        pdf.savefig(fig4)
        plt.close(fig4)

    return output_path
```

## Quick Reference

| Chart Type | Best For | Library |
|------------|----------|---------|
| Bar Chart | Category comparisons | Matplotlib/Seaborn |
| Pie Chart | Cost breakdown | Matplotlib |
| Heatmap | Level × Category matrix | Seaborn |
| Box Plot | Distribution by group | Seaborn |
| Scatter | Relationship analysis | Matplotlib/Plotly |
| Treemap | Hierarchical data | Plotly |
| Sunburst | Multi-level breakdown | Plotly |
| Gantt | Schedule visualization | Matplotlib |
| S-Curve | Progress tracking | Matplotlib |

## Color Palettes for Construction

```python
# Professional color palettes
CONSTRUCTION_COLORS = {
    'primary': ['#2C3E50', '#3498DB', '#1ABC9C', '#F39C12', '#E74C3C'],
    'materials': {
        'Concrete': '#95A5A6',
        'Steel': '#34495E',
        'Timber': '#D35400',
        'Brick': '#C0392B',
        'Glass': '#3498DB'
    },
    'categories': {
        'Structural': '#2C3E50',
        'Architectural': '#3498DB',
        'MEP': '#27AE60',
        'Finishes': '#F39C12'
    }
}
```

## Resources

- **Book**: "Data-Driven Construction" by Artem Boiko, Chapter 4.1
- **Website**: https://datadrivenconstruction.io
- **Matplotlib**: https://matplotlib.org
- **Seaborn**: https://seaborn.pydata.org
- **Plotly**: https://plotly.com/python

## Next Steps

- See `pandas-construction-analysis` for data preparation
- See `cost-prediction` for predictive analytics
- See `qto-report` for quantity extraction
