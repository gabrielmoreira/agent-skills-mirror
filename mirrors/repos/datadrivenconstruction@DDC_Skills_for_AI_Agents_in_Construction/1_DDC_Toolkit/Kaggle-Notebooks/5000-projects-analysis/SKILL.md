---
name: "5000-projects-analysis"
description: "Analyze 5000+ IFC and Revit projects at scale for patterns, benchmarks, and insights. Big data analysis for construction."
homepage: "https://datadrivenconstruction.io"
metadata: {"openclaw": {"emoji": "📓", "os": ["win32"], "homepage": "https://datadrivenconstruction.io", "requires": {"bins": ["python3"]}}}
---
# Large-Scale BIM Project Analysis

## Business Case

### Problem Statement
Construction companies lack industry benchmarks because:
- Individual project data is insufficient for statistical analysis
- Comparable project data is not available
- Manual analysis doesn't scale to thousands of projects

### Solution
Analyze 5000+ IFC and Revit projects to extract patterns, create benchmarks, and train ML models for prediction.

### Business Value
- **Industry benchmarks** - Compare your project to 5000+ others
- **Pattern detection** - Identify common designs and issues
- **ML training data** - Build predictive models with real data
- **Research foundation** - Academic and industry research dataset

## Technical Implementation

### Dataset Overview
| Metric | Value |
|--------|-------|
| Total Projects | 5000+ |
| File Formats | IFC, RVT |
| Elements | Millions |
| Categories | 200+ |

### Analysis Pipeline

```python
import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, List
import matplotlib.pyplot as plt
import seaborn as sns

class BIMProjectAnalyzer:
    def __init__(self, data_path: str):
        self.data_path = Path(data_path)
        self.projects = []
        self.elements = None

    def load_projects(self) -> int:
        """Load all project data."""
        project_files = list(self.data_path.glob("*.xlsx"))

        for f in project_files:
            try:
                df = pd.read_excel(f, sheet_name="Elements")
                df['ProjectId'] = f.stem
                self.projects.append(df)
            except Exception as e:
                print(f"Error loading {f}: {e}")

        self.elements = pd.concat(self.projects, ignore_index=True)
        return len(self.projects)

    def project_statistics(self) -> pd.DataFrame:
        """Calculate statistics per project."""
        stats = self.elements.groupby('ProjectId').agg({
            'ElementId': 'count',
            'Category': 'nunique',
            'Volume': ['sum', 'mean'],
            'Area': ['sum', 'mean']
        }).reset_index()

        stats.columns = [
            'ProjectId', 'ElementCount', 'CategoryCount',
            'TotalVolume', 'AvgVolume', 'TotalArea', 'AvgArea'
        ]
        return stats

    def category_distribution(self) -> pd.DataFrame:
        """Analyze element distribution across categories."""
        dist = self.elements.groupby('Category').agg({
            'ElementId': 'count',
            'ProjectId': 'nunique',
            'Volume': 'sum',
            'Area': 'sum'
        }).reset_index()

        dist.columns = ['Category', 'ElementCount', 'ProjectCount',
                        'TotalVolume', 'TotalArea']
        dist['AvgPerProject'] = dist['ElementCount'] / dist['ProjectCount']

        return dist.sort_values('ElementCount', ascending=False)

    def find_outliers(self, column: str, threshold: float = 3.0) -> pd.DataFrame:
        """Find projects with outlier values."""
        stats = self.project_statistics()
        mean = stats[column].mean()
        std = stats[column].std()

        z_scores = np.abs((stats[column] - mean) / std)
        outliers = stats[z_scores > threshold]

        return outliers

    def benchmark_project(self, project_id: str) -> Dict:
        """Compare project against dataset benchmarks."""
        stats = self.project_statistics()
        project = stats[stats['ProjectId'] == project_id].iloc[0]

        percentiles = {}
        for col in ['ElementCount', 'TotalVolume', 'TotalArea']:
            percentile = (stats[col] < project[col]).mean() * 100
            percentiles[col] = round(percentile, 1)

        return {
            'project_id': project_id,
            'percentiles': percentiles,
            'above_average': {
                col: project[col] > stats[col].mean()
                for col in ['ElementCount', 'TotalVolume', 'TotalArea']
            }
        }

    def generate_report(self, output_path: str) -> str:
        """Generate comprehensive analysis report."""
        stats = self.project_statistics()
        cat_dist = self.category_distribution()

        # Create visualizations
        fig, axes = plt.subplots(2, 2, figsize=(14, 10))

        # Element count distribution
        axes[0, 0].hist(stats['ElementCount'], bins=50, edgecolor='black')
        axes[0, 0].set_title('Element Count Distribution')
        axes[0, 0].set_xlabel('Elements per Project')

        # Top categories
        top_cats = cat_dist.head(15)
        axes[0, 1].barh(top_cats['Category'], top_cats['ElementCount'])
        axes[0, 1].set_title('Top 15 Categories')

        # Volume distribution
        axes[1, 0].hist(stats['TotalVolume'], bins=50, edgecolor='black')
        axes[1, 0].set_title('Total Volume Distribution')

        # Category count vs Element count
        axes[1, 1].scatter(stats['CategoryCount'], stats['ElementCount'], alpha=0.5)
        axes[1, 1].set_xlabel('Category Count')
        axes[1, 1].set_ylabel('Element Count')
        axes[1, 1].set_title('Complexity Analysis')

        plt.tight_layout()
        plt.savefig(output_path, dpi=150)

        return output_path
```

### Analysis Examples

```python
# Initialize analyzer
analyzer = BIMProjectAnalyzer("C:/Data/5000_Projects")

# Load all projects
num_projects = analyzer.load_projects()
print(f"Loaded {num_projects} projects")

# Get statistics
stats = analyzer.project_statistics()
print("\nDataset Summary:")
print(f"  Total elements: {analyzer.elements.shape[0]:,}")
print(f"  Avg elements/project: {stats['ElementCount'].mean():,.0f}")
print(f"  Avg volume/project: {stats['TotalVolume'].mean():,.2f} m³")

# Category analysis
categories = analyzer.category_distribution()
print("\nTop 10 Categories:")
print(categories.head(10)[['Category', 'ElementCount', 'AvgPerProject']])

# Benchmark a specific project
benchmark = analyzer.benchmark_project("MyProject_001")
print(f"\nProject Benchmark:")
print(f"  Element count: {benchmark['percentiles']['ElementCount']}th percentile")
print(f"  Total volume: {benchmark['percentiles']['TotalVolume']}th percentile")

# Generate report
report_path = analyzer.generate_report("analysis_report.png")
```

## Insights You Can Extract

### Structural Patterns
- Average wall-to-floor ratio
- Typical door/window counts per area
- MEP element density benchmarks

### Quality Indicators
- Category completeness
- Parameter fill rates
- Geometric consistency

### Complexity Metrics
- Elements per m² of floor area
- Category diversity index
- Level count vs building height

## Integration with ML

```python
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split

# Prepare features for cost prediction
features = stats[[
    'ElementCount', 'CategoryCount',
    'TotalVolume', 'TotalArea'
]].values

# Assuming you have cost data
# costs = [project_cost_data]

# Train model
X_train, X_test, y_train, y_test = train_test_split(
    features, costs, test_size=0.2
)

model = RandomForestRegressor(n_estimators=100)
model.fit(X_train, y_train)

# Predict for new project
new_project = [[5000, 50, 15000, 8000]]  # elements, categories, volume, area
predicted_cost = model.predict(new_project)
```

## Resources

- **Kaggle Notebook**: [5000 Projects Analysis](https://www.kaggle.com/code/artemboiko/5000-projects-ifc-rvt-datadrivenconstruction-io)
- **Dataset**: Available via DataDrivenConstruction.io
