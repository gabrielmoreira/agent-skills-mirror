# Chart Types Reference

Charts can only be added to Summary or Matrix reports. A Tabular report with a `<chart>` element will fail deployment.

## Available Chart Types

| Chart Type | Category | Notes |
|-----------|----------|-------|
| `HorizontalBar` | Bar | Single-series horizontal bar |
| `HorizontalBarGrouped` | Bar | Grouped horizontal bars (requires secondaryGroupingColumn) |
| `HorizontalBarStacked` | Bar | Stacked horizontal bars |
| `HorizontalBarStackedTo100` | Bar | Stacked to 100% |
| `VerticalColumn` | Column | Single-series vertical column |
| `VerticalColumnGrouped` | Column | Grouped vertical columns |
| `VerticalColumnStacked` | Column | Stacked vertical columns |
| `VerticalColumnStackedTo100` | Column | Stacked to 100% |
| `Line` | Line | Single-series line |
| `LineGrouped` | Line | Grouped line chart |
| `LineCumulative` | Line | Cumulative line chart |
| `LineCumulativeGrouped` | Line | Grouped cumulative line |
| `Pie` | Circular | Pie chart |
| `Donut` | Circular | Donut chart |
| `Funnel` | Other | Funnel chart |
| `Scatter` | Other | Scatter chart |
| `ScatterGrouped` | Other | Grouped scatter chart |

## legendPosition

`legendPosition` is only accepted on some chart types. On the others, ANY value fails with `chart-legendPosition: Invalid value specified: Right` — omit the element.

| Chart types | Accepted `legendPosition` |
|-------------|---------------------------|
| Single-series `HorizontalBar`, `VerticalColumn`, `Line`, `LineCumulative` | None — omit it |
| Grouped/stacked (`VerticalColumnGrouped`, `HorizontalBarStacked`, …) | `Right`, `Bottom` (`OnChart` fails) |
| `Pie`, `Donut`, `Funnel`, `Scatter` | `Right`, `Bottom`, `OnChart` |

## Allowed `<chart>` Child Elements

Use only these elements inside `<chart>`. Anything else (e.g. `<summaryAxisManualRangeEnabled>`, `<showInlineChart>`) fails with `Element ... invalid at this location in type ReportChart`.

`backgroundColor1`, `backgroundColor2`, `backgroundFadeDir`, `chartSummaries` (`aggregate`, `axisBinding`, `column`), `chartType`, `enableHoverLabels`, `expandOthers`, `groupingColumn`, `legendPosition`, `location`, `secondaryGroupingColumn`, `showAxisLabels`, `showPercentage`, `showTotal`, `showValues`, `size`, `summaryAxisRange` (`Auto` or `Manual`), `textColor`, `textSize`, `title`, `titleColor`, `titleSize`.

A minimal chart needs only `chartType`, `groupingColumn`, `chartSummaries`, and `location`.

## Record Count Charts

To chart a record count, `<chartSummaries>` holds ONLY `<column>RowCount</column>` — no `<aggregate>`. `Sum` with `RowCount` fails with `aggregate type cannot be specified with RowCount summary`, and `Count` is not a valid aggregate at all.

```xml
<chartSummaries>
    <column>RowCount</column>
</chartSummaries>
```

For any other column, `<aggregate>` is required and must be `Sum`, `Average`, `Maximum`, or `Minimum`.
