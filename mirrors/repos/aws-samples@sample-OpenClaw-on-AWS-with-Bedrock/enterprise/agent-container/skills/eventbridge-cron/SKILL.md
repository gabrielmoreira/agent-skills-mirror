# EventBridge Cron — Scheduled Tasks

Schedule recurring tasks via Amazon EventBridge Scheduler. Tasks execute at the specified time and deliver results to the user's chat channel.

## Usage

```bash
node /skills/eventbridge-cron/tool.js '<JSON>'
```

## Actions

### Create a schedule
```json
{"action":"create", "cron_expression":"cron(0 9 * * ? *)", "timezone":"Asia/Shanghai", "message":"Check email and summarize unread messages", "schedule_name":"Daily email check"}
```

### List all schedules
```json
{"action":"list"}
```

### Update a schedule
```json
{"action":"update", "schedule_id":"a1b2c3d4", "expression":"cron(0 10 * * ? *)", "message":"New task message", "enable":true}
```

### Delete a schedule
```json
{"action":"delete", "schedule_id":"a1b2c3d4"}
```

## Expression Formats

| Format | Example | Description |
|--------|---------|-------------|
| `cron()` | `cron(0 9 * * ? *)` | 6 fields: Min Hour Day Month DayOfWeek Year |
| `rate()` | `rate(1 hour)` | Fixed interval, minimum 5 minutes |
| `at()` | `at(2026-12-31T23:59:00)` | One-time execution |

## Examples

| User says | Expression |
|-----------|------------|
| Every day at 9am | `cron(0 9 * * ? *)` |
| Weekdays at 5pm | `cron(0 17 ? * MON-FRI *)` |
| Every 30 minutes | `rate(30 minutes)` |
| First of each month at 10am | `cron(0 10 1 * ? *)` |
