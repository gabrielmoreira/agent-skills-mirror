### scheduler
manage saved tasks and schedules
rules:
- before `scheduler:create_*` or `scheduler:run_task`, inspect existing tasks with `scheduler:find_task_by_name` or `scheduler:list_tasks`
- do not manually run a task just because it is scheduled or planned unless user asks to run now
- do not create recursive task prompts that schedule more tasks
methods:
- `scheduler:list_tasks`: optional `state[]`, `type[]`, `next_run_within`, `next_run_after`
- `scheduler:find_task_by_name`: `name`
- `scheduler:show_task`: `uuid`
- `scheduler:run_task`: `uuid`, optional `context`
- `scheduler:delete_task`: `uuid`
- `scheduler:create_scheduled_task`: `name`, `system_prompt`, `prompt`, optional `attachments[]`, `schedule{minute,hour,day,month,weekday}`, optional `dedicated_context`
- `scheduler:create_adhoc_task`: `name`, `system_prompt`, `prompt`, optional `attachments[]`, optional `dedicated_context`
- `scheduler:create_planned_task`: `name`, `system_prompt`, `prompt`, optional `attachments[]`, `plan[]` iso datetimes like `2025-04-29T18:25:00`, optional `dedicated_context`
- `scheduler:wait_for_task`: `uuid`; works for dedicated-context tasks
