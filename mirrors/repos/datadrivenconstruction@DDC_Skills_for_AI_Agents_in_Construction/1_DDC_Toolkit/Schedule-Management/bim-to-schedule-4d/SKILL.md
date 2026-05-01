---
name: "bim-to-schedule-4d"
description: "Create 4D construction simulations by linking BIM models with project schedules."
homepage: "https://datadrivenconstruction.io"
metadata: {"openclaw": {"emoji": "📅", "os": ["darwin", "linux", "win32"], "homepage": "https://datadrivenconstruction.io", "requires": {"bins": ["python3"]}}}
---
# BIM to Schedule 4D Simulation

## Technical Implementation

```python
import pandas as pd
from datetime import date, datetime
from typing import Dict, Any, List
from dataclasses import dataclass, field
from enum import Enum


class SimulationStatus(Enum):
    SETUP = "setup"
    READY = "ready"
    RUNNING = "running"
    COMPLETE = "complete"


@dataclass
class TimeSlice:
    slice_date: date
    visible_elements: List[str]
    active_activities: List[str]
    completed_activities: List[str]


@dataclass
class Simulation4D:
    simulation_id: str
    name: str
    start_date: date
    end_date: date
    interval_days: int
    status: SimulationStatus
    time_slices: List[TimeSlice] = field(default_factory=list)


class BIMSchedule4DSimulation:
    def __init__(self, project_name: str):
        self.project_name = project_name
        self.elements: Dict[str, Dict[str, Any]] = {}
        self.activities: Dict[str, Dict[str, Any]] = {}
        self.links: Dict[str, List[str]] = {}  # activity_id: [element_ids]
        self.simulations: Dict[str, Simulation4D] = {}

    def add_element(self, element_id: str, name: str, category: str, level: str):
        self.elements[element_id] = {
            'id': element_id, 'name': name, 'category': category, 'level': level
        }

    def add_activity(self, activity_id: str, name: str, start: date, end: date):
        self.activities[activity_id] = {
            'id': activity_id, 'name': name, 'start': start, 'end': end
        }

    def link_elements(self, activity_id: str, element_ids: List[str]):
        self.links[activity_id] = element_ids

    def create_simulation(self, name: str, start: date, end: date,
                         interval_days: int = 7) -> Simulation4D:
        sim_id = f"SIM-{len(self.simulations) + 1:03d}"
        simulation = Simulation4D(
            simulation_id=sim_id,
            name=name,
            start_date=start,
            end_date=end,
            interval_days=interval_days,
            status=SimulationStatus.SETUP
        )
        self.simulations[sim_id] = simulation
        return simulation

    def generate_time_slices(self, sim_id: str):
        if sim_id not in self.simulations:
            return

        sim = self.simulations[sim_id]
        sim.time_slices = []
        current = sim.start_date

        while current <= sim.end_date:
            visible = []
            active = []
            completed = []

            for act_id, act in self.activities.items():
                if act['end'] < current:
                    completed.append(act_id)
                    if act_id in self.links:
                        visible.extend(self.links[act_id])
                elif act['start'] <= current <= act['end']:
                    active.append(act_id)
                    if act_id in self.links:
                        visible.extend(self.links[act_id])

            slice = TimeSlice(
                slice_date=current,
                visible_elements=list(set(visible)),
                active_activities=active,
                completed_activities=completed
            )
            sim.time_slices.append(slice)

            from datetime import timedelta
            current += timedelta(days=sim.interval_days)

        sim.status = SimulationStatus.READY

    def get_slice_at_date(self, sim_id: str, target_date: date) -> TimeSlice:
        if sim_id not in self.simulations:
            return None
        sim = self.simulations[sim_id]
        for slice in sim.time_slices:
            if slice.slice_date == target_date:
                return slice
        return None

    def export_simulation(self, sim_id: str, output_path: str):
        if sim_id not in self.simulations:
            return
        sim = self.simulations[sim_id]
        data = [{
            'Date': s.slice_date,
            'Visible Elements': len(s.visible_elements),
            'Active Activities': len(s.active_activities),
            'Completed': len(s.completed_activities)
        } for s in sim.time_slices]
        pd.DataFrame(data).to_excel(output_path, index=False)
```

## Quick Start

```python
sim = BIMSchedule4DSimulation("Office Tower")

sim.add_element("E001", "Footing", "Foundation", "B1")
sim.add_activity("A100", "Foundation", date(2024, 1, 1), date(2024, 2, 28))
sim.link_elements("A100", ["E001"])

simulation = sim.create_simulation("Construction Sequence", date(2024, 1, 1), date(2024, 12, 31))
sim.generate_time_slices(simulation.simulation_id)
```

## Resources
- **DDC Book**: Chapter 3.3 - 4D BIM
