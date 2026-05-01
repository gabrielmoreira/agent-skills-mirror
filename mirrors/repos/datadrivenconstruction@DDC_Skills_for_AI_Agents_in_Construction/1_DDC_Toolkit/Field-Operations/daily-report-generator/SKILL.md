---
name: "daily-report-generator"
description: "Automatically generate daily construction reports from field data, worker inputs, weather, and progress photos. Creates professional PDF reports."
homepage: "https://datadrivenconstruction.io"
metadata: {"openclaw": {"emoji": "🏗️", "os": ["darwin", "linux", "win32"], "homepage": "https://datadrivenconstruction.io", "requires": {"bins": ["python3"]}}}
---
# Daily Report Generator for Construction Sites

Automate the creation of comprehensive daily construction reports by aggregating data from multiple sources into professional documentation.

## Business Case

**Problem**: Site managers spend 45-60 minutes daily on:
- Collecting information from foremen
- Checking weather conditions
- Compiling worker counts and hours
- Writing narrative summaries
- Formatting and distributing reports

**Solution**: Automated system that:
- Pulls data from Google Sheets/project database
- Integrates weather API data
- Aggregates worker timesheets
- Generates professional PDF reports
- Distributes to stakeholders automatically

**ROI**: 80% reduction in daily reporting time (45 min → 9 min for review)

## Report Structure

```
┌──────────────────────────────────────────────────────────────────────┐
│                    DAILY CONSTRUCTION REPORT                          │
│                                                                       │
│  Project: ЖК Солнечный, Корпус 2          Date: 24.01.2026           │
│  Report #: DCR-2026-024                   Weather: ☁️ -5°C           │
├──────────────────────────────────────────────────────────────────────┤
│                                                                       │
│  1. WEATHER CONDITIONS                                                │
│  ┌────────────┬────────────┬────────────┬────────────┐               │
│  │ Morning    │ Afternoon  │ Evening    │ Impact     │               │
│  │ -8°C ☀️    │ -5°C ☁️    │ -7°C 🌙    │ Normal     │               │
│  └────────────┴────────────┴────────────┴────────────┘               │
│                                                                       │
│  2. WORKFORCE                                                         │
│  ┌────────────────────────────────────────────────────┐              │
│  │ Category          │ Planned │ Actual │ Hours      │              │
│  ├────────────────────────────────────────────────────┤              │
│  │ GC Supervision    │    3    │   3    │    27      │              │
│  │ Electrical        │   12    │  11    │    88      │              │
│  │ Plumbing          │    8    │   8    │    64      │              │
│  │ HVAC              │    6    │   6    │    48      │              │
│  │ TOTAL             │   29    │  28    │   227      │              │
│  └────────────────────────────────────────────────────┘              │
│                                                                       │
│  3. WORK COMPLETED TODAY                                              │
│  • Electrical: Completed rough-in floors 5-6                         │
│  • Plumbing: Installed risers section A                              │
│  • HVAC: Ductwork installation 60% complete                          │
│                                                                       │
│  4. WORK PLANNED FOR TOMORROW                                         │
│  • Electrical: Begin rough-in floor 7                                │
│  • Plumbing: Continue risers section B                               │
│  • HVAC: Complete ductwork, begin testing                            │
│                                                                       │
│  5. ISSUES / DELAYS                                                   │
│  • Material delay: Electrical panels (ETA: 26.01)                    │
│  • Weather: Expected snow may delay exterior work                    │
│                                                                       │
│  6. SAFETY                                                            │
│  ✅ No incidents                                                      │
│  ✅ Toolbox talk completed: Fall protection                          │
│                                                                       │
│  7. PHOTOS                                                            │
│  [Photo 1: Floor 5 electrical]  [Photo 2: Riser installation]        │
│                                                                       │
│  ─────────────────────────────────────────────────────────────────   │
│  Prepared by: Иван Петров, Site Manager                              │
│  Approved by: ___________________                                     │
│  Distribution: Owner, Architect, PM                                   │
└──────────────────────────────────────────────────────────────────────┘
```

## Python Implementation

```python
import pandas as pd
from datetime import datetime, date
from typing import Optional, List, Dict
import requests
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
import os

class DailyReportGenerator:
    """Generate professional daily construction reports"""

    def __init__(self, config: dict):
        self.config = config
        self.weather_api_key = config.get('weather_api_key')
        self.project_name = config.get('project_name')
        self.report_date = config.get('report_date', date.today())

    def get_weather_data(self, location: str) -> dict:
        """Fetch weather data from API"""
        if not self.weather_api_key:
            return self._mock_weather()

        url = f"https://api.openweathermap.org/data/2.5/weather"
        params = {
            'q': location,
            'appid': self.weather_api_key,
            'units': 'metric',
            'lang': 'ru'
        }

        response = requests.get(url, params=params)
        if response.status_code == 200:
            data = response.json()
            return {
                'temp': round(data['main']['temp']),
                'description': data['weather'][0]['description'],
                'humidity': data['main']['humidity'],
                'wind_speed': round(data['wind']['speed']),
                'icon': self._get_weather_icon(data['weather'][0]['main'])
            }
        return self._mock_weather()

    def _get_weather_icon(self, condition: str) -> str:
        icons = {
            'Clear': '☀️',
            'Clouds': '☁️',
            'Rain': '🌧️',
            'Snow': '❄️',
            'Thunderstorm': '⛈️',
            'Mist': '🌫️'
        }
        return icons.get(condition, '🌤️')

    def _mock_weather(self) -> dict:
        return {
            'temp': -5,
            'description': 'облачно',
            'humidity': 65,
            'wind_speed': 3,
            'icon': '☁️'
        }

    def get_workforce_data(self, source: pd.DataFrame) -> dict:
        """Aggregate workforce data from timesheet"""
        # Expected columns: trade, worker_name, hours_worked, planned_hours

        summary = source.groupby('trade').agg({
            'worker_name': 'count',
            'hours_worked': 'sum',
            'planned_hours': 'sum'
        }).reset_index()

        summary.columns = ['trade', 'actual_count', 'actual_hours', 'planned_hours']

        # Calculate planned count (assuming 8-hour shifts)
        summary['planned_count'] = (summary['planned_hours'] / 8).astype(int)

        return {
            'trades': summary.to_dict('records'),
            'total_workers': summary['actual_count'].sum(),
            'total_hours': summary['actual_hours'].sum(),
            'total_planned': summary['planned_count'].sum()
        }

    def get_work_completed(self, tasks: pd.DataFrame) -> List[dict]:
        """Extract completed work from task system"""
        # Filter completed tasks for today
        completed = tasks[
            (tasks['date'] == self.report_date.strftime('%d.%m.%Y')) &
            (tasks['status'].isin(['Completed', 'Partial']))
        ]

        work_items = []
        for _, row in completed.iterrows():
            work_items.append({
                'trade': row['trade'],
                'description': row['description'],
                'status': row['status'],
                'notes': row.get('notes', '')
            })

        return work_items

    def get_work_planned(self, tasks: pd.DataFrame) -> List[dict]:
        """Get planned work for tomorrow"""
        tomorrow = self.report_date + pd.Timedelta(days=1)

        planned = tasks[
            tasks['date'] == tomorrow.strftime('%d.%m.%Y')
        ]

        work_items = []
        for _, row in planned.iterrows():
            work_items.append({
                'trade': row['trade'],
                'description': row['description'],
                'priority': row.get('priority', 'Medium')
            })

        return work_items

    def get_issues(self, issues_log: pd.DataFrame) -> List[dict]:
        """Get active issues and delays"""
        active = issues_log[
            (issues_log['status'] == 'Open') |
            (issues_log['date_reported'] == self.report_date.strftime('%d.%m.%Y'))
        ]

        return active[['category', 'description', 'impact', 'resolution_date']].to_dict('records')

    def get_safety_data(self, safety_log: pd.DataFrame) -> dict:
        """Get safety information for the day"""
        today_incidents = safety_log[
            safety_log['date'] == self.report_date.strftime('%d.%m.%Y')
        ]

        return {
            'incidents': len(today_incidents[today_incidents['type'] == 'Incident']),
            'near_misses': len(today_incidents[today_incidents['type'] == 'Near Miss']),
            'toolbox_talk': today_incidents[
                today_incidents['type'] == 'Toolbox Talk'
            ]['topic'].tolist(),
            'observations': today_incidents[
                today_incidents['type'] == 'Observation'
            ]['description'].tolist()
        }

    def generate_report(self, data: dict, output_path: str) -> str:
        """Generate PDF report"""

        doc = SimpleDocTemplate(
            output_path,
            pagesize=A4,
            rightMargin=2*cm,
            leftMargin=2*cm,
            topMargin=2*cm,
            bottomMargin=2*cm
        )

        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'Title',
            parent=styles['Heading1'],
            fontSize=16,
            alignment=1,
            spaceAfter=12
        )
        heading_style = ParagraphStyle(
            'Heading',
            parent=styles['Heading2'],
            fontSize=12,
            spaceBefore=12,
            spaceAfter=6
        )

        elements = []

        # Title
        elements.append(Paragraph(
            f"DAILY CONSTRUCTION REPORT",
            title_style
        ))

        # Header info
        header_data = [
            ['Project:', self.project_name, 'Date:', self.report_date.strftime('%d.%m.%Y')],
            ['Report #:', data.get('report_number', 'DCR-001'), 'Weather:', f"{data['weather']['icon']} {data['weather']['temp']}°C"]
        ]
        header_table = Table(header_data, colWidths=[3*cm, 6*cm, 3*cm, 4*cm])
        header_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (2, 0), (2, -1), 'Helvetica-Bold'),
        ]))
        elements.append(header_table)
        elements.append(Spacer(1, 12))

        # Weather section
        elements.append(Paragraph("1. WEATHER CONDITIONS", heading_style))
        weather = data['weather']
        weather_text = f"""
        Temperature: {weather['temp']}°C | Humidity: {weather['humidity']}% |
        Wind: {weather['wind_speed']} m/s | Conditions: {weather['description']}
        """
        elements.append(Paragraph(weather_text, styles['Normal']))

        # Workforce section
        elements.append(Paragraph("2. WORKFORCE", heading_style))
        workforce = data['workforce']
        workforce_data = [['Trade', 'Planned', 'Actual', 'Hours']]
        for trade in workforce['trades']:
            workforce_data.append([
                trade['trade'],
                str(trade['planned_count']),
                str(trade['actual_count']),
                str(int(trade['actual_hours']))
            ])
        workforce_data.append([
            'TOTAL',
            str(workforce['total_planned']),
            str(workforce['total_workers']),
            str(int(workforce['total_hours']))
        ])

        workforce_table = Table(workforce_data, colWidths=[6*cm, 3*cm, 3*cm, 3*cm])
        workforce_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
        ]))
        elements.append(workforce_table)

        # Work completed
        elements.append(Paragraph("3. WORK COMPLETED TODAY", heading_style))
        for item in data.get('work_completed', []):
            bullet = f"• {item['trade']}: {item['description']}"
            if item.get('notes'):
                bullet += f" ({item['notes']})"
            elements.append(Paragraph(bullet, styles['Normal']))

        # Work planned
        elements.append(Paragraph("4. WORK PLANNED FOR TOMORROW", heading_style))
        for item in data.get('work_planned', []):
            bullet = f"• {item['trade']}: {item['description']}"
            elements.append(Paragraph(bullet, styles['Normal']))

        # Issues
        elements.append(Paragraph("5. ISSUES / DELAYS", heading_style))
        issues = data.get('issues', [])
        if issues:
            for issue in issues:
                bullet = f"• {issue['category']}: {issue['description']}"
                if issue.get('resolution_date'):
                    bullet += f" (ETA: {issue['resolution_date']})"
                elements.append(Paragraph(bullet, styles['Normal']))
        else:
            elements.append(Paragraph("No significant issues reported.", styles['Normal']))

        # Safety
        elements.append(Paragraph("6. SAFETY", heading_style))
        safety = data.get('safety', {})
        if safety.get('incidents', 0) == 0:
            elements.append(Paragraph("✅ No incidents reported", styles['Normal']))
        else:
            elements.append(Paragraph(f"⚠️ {safety['incidents']} incident(s) reported", styles['Normal']))

        if safety.get('toolbox_talk'):
            elements.append(Paragraph(f"✅ Toolbox talk: {', '.join(safety['toolbox_talk'])}", styles['Normal']))

        # Signature block
        elements.append(Spacer(1, 24))
        elements.append(Paragraph("─" * 60, styles['Normal']))
        elements.append(Paragraph(f"Prepared by: {data.get('prepared_by', '_________________')}", styles['Normal']))
        elements.append(Paragraph(f"Date: {datetime.now().strftime('%d.%m.%Y %H:%M')}", styles['Normal']))

        # Build PDF
        doc.build(elements)
        return output_path


# Usage Example
def generate_daily_report(
    project_name: str,
    location: str,
    timesheet_path: str,
    tasks_path: str,
    output_dir: str
) -> str:
    """Generate daily report from source files"""

    # Initialize generator
    generator = DailyReportGenerator({
        'project_name': project_name,
        'weather_api_key': os.environ.get('WEATHER_API_KEY'),
        'report_date': date.today()
    })

    # Load data
    timesheet = pd.read_excel(timesheet_path)
    tasks = pd.read_excel(tasks_path)

    # Compile report data
    report_data = {
        'report_number': f"DCR-{date.today().strftime('%Y-%j')}",
        'weather': generator.get_weather_data(location),
        'workforce': generator.get_workforce_data(timesheet),
        'work_completed': generator.get_work_completed(tasks),
        'work_planned': generator.get_work_planned(tasks),
        'issues': [],  # Load from issues log if available
        'safety': {
            'incidents': 0,
            'toolbox_talk': ['Fall Protection'],
            'near_misses': 0
        },
        'prepared_by': 'Site Manager'
    }

    # Generate PDF
    output_path = os.path.join(
        output_dir,
        f"Daily_Report_{date.today().strftime('%Y%m%d')}.pdf"
    )

    return generator.generate_report(report_data, output_path)


if __name__ == "__main__":
    report_path = generate_daily_report(
        project_name="ЖК Солнечный, Корпус 2",
        location="Moscow,RU",
        timesheet_path="timesheet.xlsx",
        tasks_path="tasks.xlsx",
        output_dir="./reports"
    )
    print(f"Report generated: {report_path}")
```

## Data Sources Integration

### From n8n Project Management System
```python
# Connect to Google Sheets used by n8n bot
def get_data_from_project_management(spreadsheet_id: str) -> dict:
    """Pull data from n8n project management system"""
    import gspread

    gc = gspread.service_account()
    sh = gc.open_by_key(spreadsheet_id)

    # Get completed tasks
    tasks_sheet = sh.worksheet('Tasks')
    tasks = pd.DataFrame(tasks_sheet.get_all_records())

    # Get workforce from worker responses
    workers_sheet = sh.worksheet('Workers')
    workers = pd.DataFrame(workers_sheet.get_all_records())

    return {
        'tasks': tasks,
        'workers': workers
    }
```

### From Timesheet System
```python
# Integrate with common timesheet formats
def import_timesheet(source: str, format: str = 'excel') -> pd.DataFrame:
    """Import timesheet data from various sources"""

    if format == 'excel':
        df = pd.read_excel(source)
    elif format == 'csv':
        df = pd.read_csv(source)
    elif format == 'procore':
        df = fetch_procore_timesheet(source)

    # Standardize columns
    df = df.rename(columns={
        'Trade': 'trade',
        'Worker': 'worker_name',
        'Hours': 'hours_worked',
        'Planned Hours': 'planned_hours'
    })

    return df
```

## n8n Workflow for Automation

```yaml
name: Daily Report Automation
trigger:
  type: cron
  expression: "0 18 * * 1-6"  # 6 PM daily

steps:
  - collect_task_data:
      node: Google Sheets
      operation: readRows
      sheet: Tasks
      filter: Date = TODAY()

  - collect_timesheet:
      node: Google Sheets
      operation: readRows
      sheet: Timesheet
      filter: Date = TODAY()

  - get_weather:
      node: HTTP Request
      url: "https://api.openweathermap.org/data/2.5/weather"
      params:
        q: "Moscow,RU"
        appid: "{{$env.WEATHER_API_KEY}}"

  - generate_report:
      node: Code (Python)
      code: |
        from daily_report import generate_report
        return generate_report(items)

  - upload_to_drive:
      node: Google Drive
      operation: upload
      file: "={{$json.report_path}}"
      folder: "Daily Reports"

  - send_notification:
      node: Telegram
      operation: sendDocument
      chatId: "MANAGERS_GROUP_ID"
      document: "={{$json.drive_url}}"
      caption: |
        📋 Daily Report - {{$now.format('DD.MM.YYYY')}}

        Workforce: {{$json.total_workers}} workers
        Tasks completed: {{$json.completed_tasks}}
        Issues: {{$json.open_issues}}
```

## Report Distribution

```python
def distribute_report(report_path: str, recipients: dict):
    """Distribute report to stakeholders"""

    # Email distribution
    for email in recipients.get('email', []):
        send_email(
            to=email,
            subject=f"Daily Report - {date.today().strftime('%d.%m.%Y')}",
            body="Please find attached the daily construction report.",
            attachment=report_path
        )

    # Telegram distribution
    for chat_id in recipients.get('telegram', []):
        send_telegram_document(
            chat_id=chat_id,
            document_path=report_path,
            caption=f"📋 Daily Report - {date.today().strftime('%d.%m.%Y')}"
        )

    # Upload to project portal
    if portal_url := recipients.get('portal'):
        upload_to_portal(portal_url, report_path)
```

## Best Practices

1. **Data Collection**: Set up automated data collection to minimize manual input
2. **Review Time**: Allow 5-10 minutes for manager review before distribution
3. **Photos**: Include 3-5 key photos showing progress
4. **Issues**: Be specific about impacts and resolution dates
5. **Distribution**: Send by 6-7 PM to allow stakeholder review

---

*"A good daily report tells the story of the day in 2 minutes or less."*
