---
name: "cwicr-report-generator"
description: "Generate professional cost estimation reports from CWICR calculations. HTML, PDF, Excel outputs with charts and breakdowns."
homepage: "https://datadrivenconstruction.io"
metadata: {"openclaw": {"emoji": "🗄️", "os": ["darwin", "linux", "win32"], "homepage": "https://datadrivenconstruction.io", "requires": {"bins": ["python3"]}}}
---
# CWICR Report Generator

## Overview
Generate professional cost reports from CWICR calculations - executive summaries, detailed breakdowns, charts, and export to multiple formats.

## Python Implementation

```python
import pandas as pd
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
import json


@dataclass
class ReportSection:
    """Report section content."""
    title: str
    content: str
    chart_type: Optional[str] = None
    chart_data: Optional[Dict] = None


@dataclass
class CostReport:
    """Complete cost report."""
    project_name: str
    generated_date: datetime
    total_cost: float
    currency: str
    sections: List[ReportSection]
    line_items: List[Dict]
    summary: Dict[str, Any]


class CWICRReportGenerator:
    """Generate cost estimation reports."""

    def __init__(self, project_name: str = "Project",
                 currency: str = "USD"):
        self.project_name = project_name
        self.currency = currency
        self.sections: List[ReportSection] = []
        self.line_items: List[Dict] = []

    def add_summary(self, summary_data: Dict[str, float]):
        """Add executive summary section."""

        content = f"""
        <div class="summary-box">
            <h3>Cost Summary</h3>
            <table class="summary-table">
                <tr><td>Labor</td><td class="amount">${summary_data.get('labor', 0):,.2f}</td></tr>
                <tr><td>Materials</td><td class="amount">${summary_data.get('material', 0):,.2f}</td></tr>
                <tr><td>Equipment</td><td class="amount">${summary_data.get('equipment', 0):,.2f}</td></tr>
                <tr><td>Overhead</td><td class="amount">${summary_data.get('overhead', 0):,.2f}</td></tr>
                <tr><td>Profit</td><td class="amount">${summary_data.get('profit', 0):,.2f}</td></tr>
                <tr class="total"><td>TOTAL</td><td class="amount">${summary_data.get('total', 0):,.2f}</td></tr>
            </table>
        </div>
        """

        self.sections.append(ReportSection(
            title="Executive Summary",
            content=content,
            chart_type="pie",
            chart_data={
                'labels': ['Labor', 'Materials', 'Equipment', 'Overhead', 'Profit'],
                'values': [
                    summary_data.get('labor', 0),
                    summary_data.get('material', 0),
                    summary_data.get('equipment', 0),
                    summary_data.get('overhead', 0),
                    summary_data.get('profit', 0)
                ]
            }
        ))

    def add_breakdown_by_category(self, breakdown: Dict[str, float]):
        """Add breakdown by category section."""

        rows = ""
        for category, cost in sorted(breakdown.items(), key=lambda x: -x[1]):
            rows += f"<tr><td>{category}</td><td class='amount'>${cost:,.2f}</td></tr>"

        content = f"""
        <table class="detail-table">
            <thead><tr><th>Category</th><th>Cost</th></tr></thead>
            <tbody>{rows}</tbody>
        </table>
        """

        self.sections.append(ReportSection(
            title="Cost by Category",
            content=content,
            chart_type="bar",
            chart_data={
                'labels': list(breakdown.keys()),
                'values': list(breakdown.values())
            }
        ))

    def add_line_items(self, items: List[Dict]):
        """Add detailed line items."""
        self.line_items = items

        rows = ""
        for item in items[:50]:  # Limit for report
            rows += f"""
            <tr>
                <td>{item.get('code', '')}</td>
                <td>{item.get('description', '')[:50]}</td>
                <td>{item.get('quantity', 0):,.2f}</td>
                <td>{item.get('unit', '')}</td>
                <td class="amount">${item.get('unit_price', 0):,.2f}</td>
                <td class="amount">${item.get('total', 0):,.2f}</td>
            </tr>
            """

        content = f"""
        <table class="line-items">
            <thead>
                <tr>
                    <th>Code</th>
                    <th>Description</th>
                    <th>Qty</th>
                    <th>Unit</th>
                    <th>Unit Price</th>
                    <th>Total</th>
                </tr>
            </thead>
            <tbody>{rows}</tbody>
        </table>
        """

        self.sections.append(ReportSection(
            title="Line Items",
            content=content
        ))

    def generate_html(self) -> str:
        """Generate HTML report."""

        sections_html = ""
        for section in self.sections:
            sections_html += f"""
            <section class="report-section">
                <h2>{section.title}</h2>
                {section.content}
            </section>
            """

        html = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Cost Report - {self.project_name}</title>
    <style>
        body {{ font-family: 'Segoe UI', Arial, sans-serif; margin: 40px; background: #f5f5f5; }}
        .report-container {{ max-width: 1200px; margin: 0 auto; background: white; padding: 40px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
        h1 {{ color: #2c3e50; border-bottom: 3px solid #3498db; padding-bottom: 10px; }}
        h2 {{ color: #34495e; margin-top: 30px; }}
        .summary-box {{ background: #ecf0f1; padding: 20px; border-radius: 8px; }}
        table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
        th, td {{ padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }}
        th {{ background: #3498db; color: white; }}
        .amount {{ text-align: right; font-family: monospace; }}
        .total {{ font-weight: bold; background: #f8f9fa; }}
        .line-items td {{ font-size: 0.9em; }}
        .meta {{ color: #7f8c8d; font-size: 0.9em; margin-bottom: 20px; }}
    </style>
</head>
<body>
    <div class="report-container">
        <h1>Cost Estimation Report</h1>
        <div class="meta">
            <p>Project: {self.project_name}</p>
            <p>Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}</p>
            <p>Currency: {self.currency}</p>
        </div>
        {sections_html}
        <footer style="margin-top: 40px; color: #95a5a6; text-align: center;">
            Generated by DDC CWICR | DataDrivenConstruction.io
        </footer>
    </div>
</body>
</html>
        """

        return html

    def save_html(self, output_path: str) -> str:
        """Save HTML report to file."""
        html = self.generate_html()
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html)
        return output_path

    def generate_excel(self, output_path: str) -> str:
        """Generate Excel report."""

        with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
            # Summary sheet
            if self.sections:
                summary_data = []
                for section in self.sections:
                    if section.chart_data:
                        for i, label in enumerate(section.chart_data.get('labels', [])):
                            summary_data.append({
                                'Category': label,
                                'Amount': section.chart_data.get('values', [])[i]
                            })
                if summary_data:
                    pd.DataFrame(summary_data).to_excel(
                        writer, sheet_name='Summary', index=False)

            # Line items sheet
            if self.line_items:
                pd.DataFrame(self.line_items).to_excel(
                    writer, sheet_name='Line Items', index=False)

        return output_path

    def generate_json(self) -> str:
        """Generate JSON report."""

        report = {
            'project_name': self.project_name,
            'generated_date': datetime.now().isoformat(),
            'currency': self.currency,
            'sections': [
                {
                    'title': s.title,
                    'chart_data': s.chart_data
                } for s in self.sections
            ],
            'line_items': self.line_items
        }

        return json.dumps(report, indent=2)


class QuickReport:
    """Quick report generation from cost data."""

    @staticmethod
    def from_dataframe(df: pd.DataFrame,
                       project_name: str = "Project") -> CWICRReportGenerator:
        """Generate report from cost DataFrame."""

        gen = CWICRReportGenerator(project_name)

        # Calculate summary
        summary = {
            'labor': df['labor_cost'].sum() if 'labor_cost' in df.columns else 0,
            'material': df['material_cost'].sum() if 'material_cost' in df.columns else 0,
            'equipment': df['equipment_cost'].sum() if 'equipment_cost' in df.columns else 0,
            'overhead': df['overhead_cost'].sum() if 'overhead_cost' in df.columns else 0,
            'profit': df['profit_cost'].sum() if 'profit_cost' in df.columns else 0,
            'total': df['total_cost'].sum() if 'total_cost' in df.columns else 0
        }
        gen.add_summary(summary)

        # Category breakdown
        if 'category' in df.columns and 'total_cost' in df.columns:
            breakdown = df.groupby('category')['total_cost'].sum().to_dict()
            gen.add_breakdown_by_category(breakdown)

        # Line items
        items = df.to_dict('records')
        gen.add_line_items(items)

        return gen
```

## Quick Start

```python
# Create report generator
gen = CWICRReportGenerator("Office Building", currency="EUR")

# Add sections
gen.add_summary({
    'labor': 125000,
    'material': 350000,
    'equipment': 75000,
    'overhead': 82500,
    'profit': 63250,
    'total': 695750
})

# Save reports
gen.save_html("cost_report.html")
gen.generate_excel("cost_report.xlsx")
```

## From DataFrame

```python
# Quick report from cost DataFrame
report = QuickReport.from_dataframe(cost_df, "My Project")
report.save_html("quick_report.html")
```

## Resources
- **DDC Book**: Chapter 4.2 - ETL Load Reports
