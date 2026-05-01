---
name: "schedule-delay-analyzer"
description: "Analyze schedule delays, identify causes, and calculate time impacts using delay analysis methods."
homepage: "https://datadrivenconstruction.io"
metadata: {"openclaw": {"emoji": "📅", "os": ["darwin", "linux", "win32"], "homepage": "https://datadrivenconstruction.io", "requires": {"bins": ["python3"]}}}
---
# Schedule Delay Analyzer

## Technical Implementation

```python
import pandas as pd
from datetime import date, timedelta
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from enum import Enum


class DelayType(Enum):
    EXCUSABLE_COMPENSABLE = "excusable_compensable"
    EXCUSABLE_NON_COMPENSABLE = "excusable_non_compensable"
    NON_EXCUSABLE = "non_excusable"
    CONCURRENT = "concurrent"


class DelayCause(Enum):
    OWNER_CHANGE = "owner_change"
    DESIGN_ERROR = "design_error"
    WEATHER = "weather"
    DIFFERING_CONDITIONS = "differing_conditions"
    CONTRACTOR_ISSUE = "contractor_issue"
    MATERIAL_DELAY = "material_delay"
    LABOR_SHORTAGE = "labor_shortage"
    PERMIT_DELAY = "permit_delay"
    OTHER = "other"


@dataclass
class DelayEvent:
    delay_id: str
    activity_id: str
    activity_name: str
    delay_type: DelayType
    cause: DelayCause
    start_date: date
    end_date: date
    delay_days: int
    on_critical_path: bool
    description: str
    documentation: List[str] = field(default_factory=list)
    cost_impact: float = 0.0


@dataclass
class ScheduleBaseline:
    baseline_date: date
    planned_completion: date
    activities: Dict[str, Dict[str, date]]  # activity_id: {start, end}


class ScheduleDelayAnalyzer:
    def __init__(self, project_name: str, contract_completion: date):
        self.project_name = project_name
        self.contract_completion = contract_completion
        self.baselines: List[ScheduleBaseline] = []
        self.delays: Dict[str, DelayEvent] = {}
        self._counter = 0

    def add_baseline(self, baseline_date: date, planned_completion: date,
                    activities: Dict[str, Dict[str, date]]):
        baseline = ScheduleBaseline(baseline_date, planned_completion, activities)
        self.baselines.append(baseline)

    def record_delay(self, activity_id: str, activity_name: str,
                    delay_type: DelayType, cause: DelayCause,
                    start_date: date, end_date: date,
                    on_critical_path: bool, description: str,
                    cost_impact: float = 0) -> DelayEvent:
        self._counter += 1
        delay_id = f"DLY-{self._counter:04d}"

        delay = DelayEvent(
            delay_id=delay_id,
            activity_id=activity_id,
            activity_name=activity_name,
            delay_type=delay_type,
            cause=cause,
            start_date=start_date,
            end_date=end_date,
            delay_days=(end_date - start_date).days,
            on_critical_path=on_critical_path,
            description=description,
            cost_impact=cost_impact
        )
        self.delays[delay_id] = delay
        return delay

    def calculate_project_delay(self) -> int:
        """Calculate total critical path delay."""
        critical_delays = [d for d in self.delays.values() if d.on_critical_path]
        return sum(d.delay_days for d in critical_delays)

    def analyze_by_type(self) -> Dict[str, Dict[str, Any]]:
        analysis = {}
        for delay in self.delays.values():
            dtype = delay.delay_type.value
            if dtype not in analysis:
                analysis[dtype] = {'count': 0, 'days': 0, 'cost': 0}
            analysis[dtype]['count'] += 1
            analysis[dtype]['days'] += delay.delay_days
            analysis[dtype]['cost'] += delay.cost_impact
        return analysis

    def analyze_by_cause(self) -> Dict[str, int]:
        by_cause = {}
        for delay in self.delays.values():
            cause = delay.cause.value
            by_cause[cause] = by_cause.get(cause, 0) + delay.delay_days
        return by_cause

    def calculate_time_extension_claim(self) -> Dict[str, Any]:
        """Calculate basis for time extension claim."""
        excusable = [d for d in self.delays.values()
                    if d.delay_type in [DelayType.EXCUSABLE_COMPENSABLE,
                                        DelayType.EXCUSABLE_NON_COMPENSABLE]
                    and d.on_critical_path]

        compensable = [d for d in excusable
                      if d.delay_type == DelayType.EXCUSABLE_COMPENSABLE]

        return {
            'excusable_delays': len(excusable),
            'excusable_days': sum(d.delay_days for d in excusable),
            'compensable_delays': len(compensable),
            'compensable_days': sum(d.delay_days for d in compensable),
            'total_cost_impact': sum(d.cost_impact for d in compensable),
            'recommended_extension': sum(d.delay_days for d in excusable)
        }

    def get_summary(self) -> Dict[str, Any]:
        critical_delay = self.calculate_project_delay()
        projected_completion = self.contract_completion + timedelta(days=critical_delay)

        return {
            'project': self.project_name,
            'contract_completion': self.contract_completion,
            'projected_completion': projected_completion,
            'total_delays': len(self.delays),
            'critical_path_delays': sum(1 for d in self.delays.values() if d.on_critical_path),
            'total_delay_days': critical_delay,
            'by_type': self.analyze_by_type(),
            'by_cause': self.analyze_by_cause()
        }

    def export_analysis(self, output_path: str):
        data = [{
            'ID': d.delay_id,
            'Activity': d.activity_name,
            'Type': d.delay_type.value,
            'Cause': d.cause.value,
            'Start': d.start_date,
            'End': d.end_date,
            'Days': d.delay_days,
            'Critical': d.on_critical_path,
            'Cost Impact': d.cost_impact,
            'Description': d.description
        } for d in self.delays.values()]
        pd.DataFrame(data).to_excel(output_path, index=False)
```

## Quick Start

```python
analyzer = ScheduleDelayAnalyzer("Office Tower", date(2024, 12, 31))

delay = analyzer.record_delay(
    activity_id="A-300",
    activity_name="Foundation Work",
    delay_type=DelayType.EXCUSABLE_COMPENSABLE,
    cause=DelayCause.OWNER_CHANGE,
    start_date=date(2024, 3, 1),
    end_date=date(2024, 3, 15),
    on_critical_path=True,
    description="Owner requested additional scope",
    cost_impact=50000
)

summary = analyzer.get_summary()
print(f"Project delayed by {summary['total_delay_days']} days")

claim = analyzer.calculate_time_extension_claim()
print(f"Recommended extension: {claim['recommended_extension']} days")
```

## Resources
- **DDC Book**: Chapter 3.3 - Schedule Management
