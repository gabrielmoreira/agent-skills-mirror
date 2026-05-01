---
name: "schedule-cost-link"
description: "Link schedule activities to cost items. Create cost-loaded schedules, generate cash flow curves, and track earned value."
homepage: "https://datadrivenconstruction.io"
metadata: {"openclaw": {"emoji": "📅", "os": ["darwin", "linux", "win32"], "homepage": "https://datadrivenconstruction.io", "requires": {"bins": ["python3"]}}}
---
# Schedule-Cost Linker

## Business Case

### Problem Statement
Integrating schedule and cost requires:
- Linking activities to budget items
- Creating cost-loaded schedules
- Generating cash flow forecasts
- Tracking earned value metrics

### Solution
Systematic linkage between schedule activities and cost data to enable integrated project control.

## Technical Implementation

```python
import pandas as pd
import numpy as np
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field
from datetime import date, timedelta
from enum import Enum
from collections import defaultdict


class LoadingMethod(Enum):
    UNIFORM = "uniform"          # Even distribution
    FRONT_LOADED = "front_loaded"
    BACK_LOADED = "back_loaded"
    BELL_CURVE = "bell_curve"


@dataclass
class ScheduleActivity:
    activity_id: str
    name: str
    start_date: date
    finish_date: date
    duration: int
    percent_complete: float = 0


@dataclass
class CostItem:
    cost_code: str
    description: str
    budgeted_cost: float
    labor_cost: float
    material_cost: float
    equipment_cost: float


@dataclass
class ActivityCostLink:
    activity_id: str
    cost_code: str
    budgeted_cost: float
    loading_method: LoadingMethod


@dataclass
class EarnedValueMetrics:
    data_date: date
    bcws: float  # Budgeted Cost of Work Scheduled (PV)
    bcwp: float  # Budgeted Cost of Work Performed (EV)
    acwp: float  # Actual Cost of Work Performed (AC)
    sv: float    # Schedule Variance
    cv: float    # Cost Variance
    spi: float   # Schedule Performance Index
    cpi: float   # Cost Performance Index
    eac: float   # Estimate at Completion
    etc: float   # Estimate to Complete
    vac: float   # Variance at Completion


class ScheduleCostLinker:
    """Link schedule activities to cost items."""

    def __init__(self, project_name: str, budget_at_completion: float):
        self.project_name = project_name
        self.bac = budget_at_completion
        self.activities: Dict[str, ScheduleActivity] = {}
        self.cost_items: Dict[str, CostItem] = {}
        self.links: List[ActivityCostLink] = []
        self.actual_costs: Dict[str, float] = {}  # activity_id -> actual cost

    def add_activity(self,
                     activity_id: str,
                     name: str,
                     start_date: date,
                     finish_date: date,
                     percent_complete: float = 0):
        """Add schedule activity."""

        duration = (finish_date - start_date).days + 1

        self.activities[activity_id] = ScheduleActivity(
            activity_id=activity_id,
            name=name,
            start_date=start_date,
            finish_date=finish_date,
            duration=duration,
            percent_complete=percent_complete
        )

    def add_cost_item(self,
                      cost_code: str,
                      description: str,
                      budgeted_cost: float,
                      labor_pct: float = 0.4,
                      material_pct: float = 0.5,
                      equipment_pct: float = 0.1):
        """Add cost item."""

        self.cost_items[cost_code] = CostItem(
            cost_code=cost_code,
            description=description,
            budgeted_cost=budgeted_cost,
            labor_cost=budgeted_cost * labor_pct,
            material_cost=budgeted_cost * material_pct,
            equipment_cost=budgeted_cost * equipment_pct
        )

    def link_activity_cost(self,
                           activity_id: str,
                           cost_code: str,
                           loading_method: LoadingMethod = LoadingMethod.UNIFORM):
        """Link activity to cost item."""

        if activity_id not in self.activities:
            return

        cost_item = self.cost_items.get(cost_code)
        budgeted = cost_item.budgeted_cost if cost_item else 0

        self.links.append(ActivityCostLink(
            activity_id=activity_id,
            cost_code=cost_code,
            budgeted_cost=budgeted,
            loading_method=loading_method
        ))

    def record_actual_cost(self, activity_id: str, actual_cost: float):
        """Record actual cost for activity."""
        self.actual_costs[activity_id] = actual_cost

    def _distribute_cost(self,
                          cost: float,
                          start_date: date,
                          duration: int,
                          method: LoadingMethod) -> Dict[date, float]:
        """Distribute cost over activity duration."""

        daily_costs = {}

        if duration <= 0:
            return {start_date: cost}

        if method == LoadingMethod.UNIFORM:
            daily = cost / duration
            for i in range(duration):
                daily_costs[start_date + timedelta(days=i)] = daily

        elif method == LoadingMethod.FRONT_LOADED:
            total_weight = sum(range(duration, 0, -1))
            for i in range(duration):
                weight = (duration - i) / total_weight
                daily_costs[start_date + timedelta(days=i)] = cost * weight

        elif method == LoadingMethod.BACK_LOADED:
            total_weight = sum(range(1, duration + 1))
            for i in range(duration):
                weight = (i + 1) / total_weight
                daily_costs[start_date + timedelta(days=i)] = cost * weight

        elif method == LoadingMethod.BELL_CURVE:
            # Simplified bell curve
            mid = duration / 2
            for i in range(duration):
                distance = abs(i - mid)
                weight = 1 - (distance / mid) * 0.5
                daily_costs[start_date + timedelta(days=i)] = cost * weight / duration

        return daily_costs

    def generate_cost_loaded_schedule(self) -> pd.DataFrame:
        """Generate cost-loaded schedule."""

        data = []

        for link in self.links:
            activity = self.activities.get(link.activity_id)
            cost_item = self.cost_items.get(link.cost_code)

            if activity and cost_item:
                data.append({
                    'Activity ID': activity.activity_id,
                    'Activity Name': activity.name,
                    'Cost Code': link.cost_code,
                    'Description': cost_item.description,
                    'Start': activity.start_date,
                    'Finish': activity.finish_date,
                    'Duration': activity.duration,
                    'Budget': link.budgeted_cost,
                    '% Complete': activity.percent_complete,
                    'Earned Value': link.budgeted_cost * activity.percent_complete / 100,
                    'Loading': link.loading_method.value
                })

        return pd.DataFrame(data)

    def generate_cash_flow(self,
                           project_start: date = None,
                           project_end: date = None) -> pd.DataFrame:
        """Generate cash flow curve."""

        if not self.links:
            return pd.DataFrame()

        # Get date range
        if project_start is None:
            project_start = min(self.activities[l.activity_id].start_date for l in self.links)
        if project_end is None:
            project_end = max(self.activities[l.activity_id].finish_date for l in self.links)

        # Aggregate daily costs
        daily_totals = defaultdict(float)

        for link in self.links:
            activity = self.activities.get(link.activity_id)
            if not activity:
                continue

            daily_costs = self._distribute_cost(
                link.budgeted_cost,
                activity.start_date,
                activity.duration,
                link.loading_method
            )

            for day, cost in daily_costs.items():
                daily_totals[day] += cost

        # Build cash flow data
        data = []
        cumulative = 0
        current = project_start

        while current <= project_end:
            daily = daily_totals.get(current, 0)
            cumulative += daily

            data.append({
                'Date': current,
                'Daily': round(daily, 2),
                'Cumulative': round(cumulative, 2),
                'Cumulative %': round(cumulative / self.bac * 100, 1) if self.bac > 0 else 0
            })

            current += timedelta(days=1)

        return pd.DataFrame(data)

    def calculate_earned_value(self, data_date: date) -> EarnedValueMetrics:
        """Calculate earned value metrics at data date."""

        # BCWS - Planned Value through data date
        bcws = 0
        for link in self.links:
            activity = self.activities.get(link.activity_id)
            if not activity:
                continue

            daily_costs = self._distribute_cost(
                link.budgeted_cost,
                activity.start_date,
                activity.duration,
                link.loading_method
            )

            for day, cost in daily_costs.items():
                if day <= data_date:
                    bcws += cost

        # BCWP - Earned Value (budget * % complete)
        bcwp = 0
        for link in self.links:
            activity = self.activities.get(link.activity_id)
            if activity:
                bcwp += link.budgeted_cost * activity.percent_complete / 100

        # ACWP - Actual Cost
        acwp = sum(self.actual_costs.values())

        # Variances
        sv = bcwp - bcws
        cv = bcwp - acwp

        # Indices
        spi = bcwp / bcws if bcws > 0 else 0
        cpi = bcwp / acwp if acwp > 0 else 0

        # Forecasts
        eac = self.bac / cpi if cpi > 0 else self.bac
        etc = eac - acwp
        vac = self.bac - eac

        return EarnedValueMetrics(
            data_date=data_date,
            bcws=round(bcws, 2),
            bcwp=round(bcwp, 2),
            acwp=round(acwp, 2),
            sv=round(sv, 2),
            cv=round(cv, 2),
            spi=round(spi, 2),
            cpi=round(cpi, 2),
            eac=round(eac, 2),
            etc=round(etc, 2),
            vac=round(vac, 2)
        )

    def get_monthly_cash_flow(self) -> pd.DataFrame:
        """Aggregate cash flow by month."""

        daily = self.generate_cash_flow()
        if daily.empty:
            return pd.DataFrame()

        daily['Month'] = pd.to_datetime(daily['Date']).dt.to_period('M')
        monthly = daily.groupby('Month').agg({
            'Daily': 'sum',
            'Cumulative': 'last'
        }).reset_index()

        monthly.columns = ['Month', 'Monthly Cost', 'Cumulative']
        return monthly

    def export_to_excel(self, output_path: str) -> str:
        """Export integrated data to Excel."""

        with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
            # Cost-loaded schedule
            schedule = self.generate_cost_loaded_schedule()
            schedule.to_excel(writer, sheet_name='Cost-Loaded Schedule', index=False)

            # Cash flow
            cash_flow = self.generate_cash_flow()
            if not cash_flow.empty:
                cash_flow.to_excel(writer, sheet_name='Cash Flow', index=False)

            # Monthly
            monthly = self.get_monthly_cash_flow()
            if not monthly.empty:
                monthly.to_excel(writer, sheet_name='Monthly', index=False)

            # Earned Value
            evm = self.calculate_earned_value(date.today())
            evm_df = pd.DataFrame([{
                'Data Date': evm.data_date,
                'BCWS (PV)': evm.bcws,
                'BCWP (EV)': evm.bcwp,
                'ACWP (AC)': evm.acwp,
                'SV': evm.sv,
                'CV': evm.cv,
                'SPI': evm.spi,
                'CPI': evm.cpi,
                'EAC': evm.eac,
                'ETC': evm.etc,
                'VAC': evm.vac
            }])
            evm_df.to_excel(writer, sheet_name='Earned Value', index=False)

        return output_path
```

## Quick Start

```python
from datetime import date, timedelta

# Initialize linker
linker = ScheduleCostLinker("Office Building", budget_at_completion=5000000)

# Add activities
linker.add_activity("A-001", "Foundation", date(2024, 6, 1), date(2024, 6, 30), percent_complete=100)
linker.add_activity("A-002", "Structure", date(2024, 7, 1), date(2024, 9, 30), percent_complete=60)
linker.add_activity("A-003", "MEP", date(2024, 8, 1), date(2024, 11, 30), percent_complete=30)

# Add cost items
linker.add_cost_item("01-FOUND", "Foundation Work", 500000)
linker.add_cost_item("02-STRUCT", "Structural Work", 2000000)
linker.add_cost_item("03-MEP", "MEP Systems", 1500000)

# Link
linker.link_activity_cost("A-001", "01-FOUND")
linker.link_activity_cost("A-002", "02-STRUCT", LoadingMethod.BELL_CURVE)
linker.link_activity_cost("A-003", "03-MEP", LoadingMethod.BACK_LOADED)

# Record actuals
linker.record_actual_cost("A-001", 520000)
linker.record_actual_cost("A-002", 1300000)
```

## Common Use Cases

### 1. Earned Value Analysis
```python
evm = linker.calculate_earned_value(date.today())
print(f"CPI: {evm.cpi}")
print(f"SPI: {evm.spi}")
print(f"EAC: ${evm.eac:,.2f}")
```

### 2. Cash Flow Forecast
```python
cash_flow = linker.generate_cash_flow()
print(cash_flow.tail(10))
```

### 3. Monthly Breakdown
```python
monthly = linker.get_monthly_cash_flow()
print(monthly)
```

## Resources
- **DDC Book**: Chapter 4.2 - Schedule-Cost Integration
