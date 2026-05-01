---
name: "labor-allocation"
description: "Allocate and track labor resources across project activities. Balance workload, track attendance, and optimize crew assignments."
homepage: "https://datadrivenconstruction.io"
metadata: {"openclaw": {"emoji": "👷", "os": ["darwin", "linux", "win32"], "homepage": "https://datadrivenconstruction.io", "requires": {"bins": ["python3"]}}}
---
# Labor Allocation Manager

## Business Case

### Problem Statement
Labor management challenges:
- Assigning workers to activities
- Balancing workload
- Tracking attendance
- Optimizing productivity

### Solution
Systematic labor allocation and tracking to optimize resource utilization and maintain project schedule.

## Technical Implementation

```python
import pandas as pd
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from datetime import date, timedelta
from enum import Enum
from collections import defaultdict


class Trade(Enum):
    CARPENTER = "carpenter"
    ELECTRICIAN = "electrician"
    PLUMBER = "plumber"
    CONCRETE = "concrete"
    MASON = "mason"
    IRONWORKER = "ironworker"
    HVAC = "hvac"
    PAINTER = "painter"
    LABORER = "laborer"
    OPERATOR = "operator"
    FOREMAN = "foreman"


class WorkerStatus(Enum):
    AVAILABLE = "available"
    ASSIGNED = "assigned"
    ON_LEAVE = "on_leave"
    SICK = "sick"
    TERMINATED = "terminated"


class SkillLevel(Enum):
    APPRENTICE = "apprentice"
    JOURNEYMAN = "journeyman"
    MASTER = "master"


@dataclass
class Worker:
    worker_id: str
    name: str
    trade: Trade
    skill_level: SkillLevel
    hourly_rate: float
    company: str
    status: WorkerStatus = WorkerStatus.AVAILABLE
    certifications: List[str] = field(default_factory=list)


@dataclass
class Assignment:
    assignment_id: str
    worker_id: str
    activity_id: str
    activity_name: str
    start_date: date
    end_date: date
    hours_per_day: float
    location: str


@dataclass
class AttendanceRecord:
    date: date
    worker_id: str
    activity_id: str
    hours_worked: float
    overtime_hours: float
    status: str  # present, absent, late


class LaborAllocation:
    """Manage labor allocation and tracking."""

    def __init__(self, project_name: str):
        self.project_name = project_name
        self.workers: Dict[str, Worker] = {}
        self.assignments: List[Assignment] = []
        self.attendance: List[AttendanceRecord] = []

    def add_worker(self,
                   worker_id: str,
                   name: str,
                   trade: Trade,
                   skill_level: SkillLevel,
                   hourly_rate: float,
                   company: str,
                   certifications: List[str] = None) -> Worker:
        """Add worker to pool."""

        worker = Worker(
            worker_id=worker_id,
            name=name,
            trade=trade,
            skill_level=skill_level,
            hourly_rate=hourly_rate,
            company=company,
            certifications=certifications or []
        )

        self.workers[worker_id] = worker
        return worker

    def assign_worker(self,
                      worker_id: str,
                      activity_id: str,
                      activity_name: str,
                      start_date: date,
                      end_date: date,
                      hours_per_day: float = 8,
                      location: str = "") -> Optional[Assignment]:
        """Assign worker to activity."""

        if worker_id not in self.workers:
            return None

        worker = self.workers[worker_id]

        # Check for conflicts
        conflicts = self.check_conflicts(worker_id, start_date, end_date)
        if conflicts:
            print(f"Warning: Worker has {len(conflicts)} conflicting assignments")

        assignment = Assignment(
            assignment_id=f"ASN-{len(self.assignments)+1:04d}",
            worker_id=worker_id,
            activity_id=activity_id,
            activity_name=activity_name,
            start_date=start_date,
            end_date=end_date,
            hours_per_day=hours_per_day,
            location=location
        )

        self.assignments.append(assignment)
        worker.status = WorkerStatus.ASSIGNED

        return assignment

    def check_conflicts(self,
                        worker_id: str,
                        start_date: date,
                        end_date: date) -> List[Assignment]:
        """Check for scheduling conflicts."""

        conflicts = []

        for assignment in self.assignments:
            if assignment.worker_id != worker_id:
                continue

            # Check overlap
            if not (end_date < assignment.start_date or start_date > assignment.end_date):
                conflicts.append(assignment)

        return conflicts

    def record_attendance(self,
                          date: date,
                          worker_id: str,
                          activity_id: str,
                          hours_worked: float,
                          overtime_hours: float = 0,
                          status: str = "present"):
        """Record worker attendance."""

        self.attendance.append(AttendanceRecord(
            date=date,
            worker_id=worker_id,
            activity_id=activity_id,
            hours_worked=hours_worked,
            overtime_hours=overtime_hours,
            status=status
        ))

    def get_workers_by_trade(self, trade: Trade) -> List[Worker]:
        """Get available workers by trade."""
        return [
            w for w in self.workers.values()
            if w.trade == trade and w.status in [WorkerStatus.AVAILABLE, WorkerStatus.ASSIGNED]
        ]

    def get_daily_roster(self, target_date: date) -> pd.DataFrame:
        """Get roster for specific date."""

        roster = []

        for assignment in self.assignments:
            if assignment.start_date <= target_date <= assignment.end_date:
                worker = self.workers.get(assignment.worker_id)
                if worker:
                    roster.append({
                        'Worker ID': worker.worker_id,
                        'Name': worker.name,
                        'Trade': worker.trade.value,
                        'Company': worker.company,
                        'Activity': assignment.activity_name,
                        'Location': assignment.location,
                        'Hours': assignment.hours_per_day
                    })

        return pd.DataFrame(roster)

    def get_activity_crew(self, activity_id: str) -> List[Dict[str, Any]]:
        """Get crew assigned to activity."""

        crew = []

        for assignment in self.assignments:
            if assignment.activity_id == activity_id:
                worker = self.workers.get(assignment.worker_id)
                if worker:
                    crew.append({
                        'worker_id': worker.worker_id,
                        'name': worker.name,
                        'trade': worker.trade.value,
                        'skill_level': worker.skill_level.value,
                        'hourly_rate': worker.hourly_rate,
                        'start_date': assignment.start_date,
                        'end_date': assignment.end_date
                    })

        return crew

    def calculate_labor_cost(self,
                              activity_id: str = None,
                              start_date: date = None,
                              end_date: date = None) -> Dict[str, Any]:
        """Calculate labor costs."""

        total_hours = 0
        total_overtime = 0
        total_cost = 0
        by_trade = defaultdict(float)

        for record in self.attendance:
            # Filter by activity
            if activity_id and record.activity_id != activity_id:
                continue

            # Filter by date
            if start_date and record.date < start_date:
                continue
            if end_date and record.date > end_date:
                continue

            worker = self.workers.get(record.worker_id)
            if not worker:
                continue

            regular_cost = record.hours_worked * worker.hourly_rate
            overtime_cost = record.overtime_hours * worker.hourly_rate * 1.5

            total_hours += record.hours_worked
            total_overtime += record.overtime_hours
            total_cost += regular_cost + overtime_cost
            by_trade[worker.trade.value] += regular_cost + overtime_cost

        return {
            'total_hours': round(total_hours, 1),
            'total_overtime': round(total_overtime, 1),
            'total_cost': round(total_cost, 2),
            'by_trade': dict(by_trade)
        }

    def get_utilization_report(self,
                                start_date: date,
                                end_date: date) -> pd.DataFrame:
        """Get worker utilization report."""

        data = []
        work_days = (end_date - start_date).days + 1
        available_hours = work_days * 8

        for worker in self.workers.values():
            # Get attendance records
            records = [
                r for r in self.attendance
                if r.worker_id == worker.worker_id
                and start_date <= r.date <= end_date
            ]

            worked_hours = sum(r.hours_worked + r.overtime_hours for r in records)
            utilization = (worked_hours / available_hours * 100) if available_hours > 0 else 0

            data.append({
                'Worker ID': worker.worker_id,
                'Name': worker.name,
                'Trade': worker.trade.value,
                'Available Hours': available_hours,
                'Worked Hours': round(worked_hours, 1),
                'Utilization %': round(utilization, 1)
            })

        return pd.DataFrame(data).sort_values('Utilization %', ascending=False)

    def forecast_labor_needs(self,
                              activities: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Forecast labor needs for activities."""

        needs = defaultdict(lambda: {'hours': 0, 'workers': 0})

        for activity in activities:
            trade = activity.get('trade', 'laborer')
            hours = activity.get('manhours', 0)
            duration = activity.get('duration_days', 1)

            workers_needed = hours / (duration * 8) if duration > 0 else 0

            needs[trade]['hours'] += hours
            needs[trade]['workers'] = max(needs[trade]['workers'], int(workers_needed) + 1)

        # Check availability
        for trade_name, requirement in needs.items():
            try:
                trade = Trade(trade_name)
                available = len(self.get_workers_by_trade(trade))
                requirement['available'] = available
                requirement['shortage'] = max(0, requirement['workers'] - available)
            except ValueError:
                requirement['available'] = 0
                requirement['shortage'] = requirement['workers']

        return dict(needs)

    def export_to_excel(self, output_path: str) -> str:
        """Export labor data to Excel."""

        with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
            # Workers
            workers_df = pd.DataFrame([
                {
                    'ID': w.worker_id,
                    'Name': w.name,
                    'Trade': w.trade.value,
                    'Skill': w.skill_level.value,
                    'Rate': w.hourly_rate,
                    'Company': w.company,
                    'Status': w.status.value
                }
                for w in self.workers.values()
            ])
            workers_df.to_excel(writer, sheet_name='Workers', index=False)

            # Assignments
            assignments_df = pd.DataFrame([
                {
                    'ID': a.assignment_id,
                    'Worker': a.worker_id,
                    'Activity': a.activity_name,
                    'Start': a.start_date,
                    'End': a.end_date,
                    'Hours/Day': a.hours_per_day,
                    'Location': a.location
                }
                for a in self.assignments
            ])
            assignments_df.to_excel(writer, sheet_name='Assignments', index=False)

            # Roster for today
            roster = self.get_daily_roster(date.today())
            roster.to_excel(writer, sheet_name='Today Roster', index=False)

        return output_path
```

## Quick Start

```python
from datetime import date, timedelta

# Initialize manager
labor = LaborAllocation("Office Building A")

# Add workers
labor.add_worker("W001", "John Smith", Trade.CONCRETE, SkillLevel.JOURNEYMAN, 45, "ABC Concrete")
labor.add_worker("W002", "Mike Jones", Trade.CONCRETE, SkillLevel.APPRENTICE, 30, "ABC Concrete")
labor.add_worker("W003", "Tom Brown", Trade.CARPENTER, SkillLevel.MASTER, 55, "XYZ Carpentry")

# Assign to activity
labor.assign_worker(
    worker_id="W001",
    activity_id="A-101",
    activity_name="Pour Slab Level 3",
    start_date=date.today(),
    end_date=date.today() + timedelta(days=5),
    hours_per_day=10,
    location="Level 3"
)

# Record attendance
labor.record_attendance(date.today(), "W001", "A-101", hours_worked=10, overtime_hours=2)
```

## Common Use Cases

### 1. Daily Roster
```python
roster = labor.get_daily_roster(date.today())
print(roster)
```

### 2. Labor Cost
```python
cost = labor.calculate_labor_cost(activity_id="A-101")
print(f"Total Cost: ${cost['total_cost']:,.2f}")
```

### 3. Forecast Needs
```python
activities = [
    {'trade': 'concrete', 'manhours': 400, 'duration_days': 5},
    {'trade': 'carpenter', 'manhours': 200, 'duration_days': 10}
]
needs = labor.forecast_labor_needs(activities)
print(needs)
```

## Resources
- **DDC Book**: Chapter 3.1 - Labor Management
