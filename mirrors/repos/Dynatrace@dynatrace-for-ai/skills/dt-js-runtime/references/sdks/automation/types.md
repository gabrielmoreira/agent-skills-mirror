# Automation — Types & Enums

Full field definitions: https://developer.dynatrace.com/develop/sdks/client-automation/#types

## Workflow types

`Workflow`, `WorkflowCreate`, `WorkflowUpdate`, `WorkflowInput`, `WorkflowList`, `WorkflowExport`, `WorkflowTemplate`, `WorkflowDefinitionTemplate`, `WorkflowTaskDefaults`, `WorkflowLimit`, `WorkflowThrottlesResetStatus`, `Task`, `Tasks`, `TaskInput`, `TaskPosition`, `TaskTransition`, `TaskTransitions`, `TaskRetryOption`, `TaskConditionOption`, `Throttle`, `ThrottleRequest`, `ThrottleLimitEvent(s)`.

## Execution types

`Execution`, `ExecutionInput`, `ExecutionParams`, `ExecutionLimits`, `ExecutionInputsRequest`, `ExecutionProvidedInput`, `PaginatedExecutionList`, `ActionExecution`, `ActionExecutionInput`, `ActionExecutionLoopItem`, `TaskExecution(s)`, `TaskExecutionInput`, `TaskExecutionConditions`, `EventLog(s)`, `EventLogContext`.

## Trigger types

`Trigger`, `TriggerRequest`, `TriggerExport`, `EventTrigger`, `EventTriggerRequest`, `EventTriggerExport`, `EventTriggerPreviewRequest`, `EventTriggerPreviewResponse`, `EventQuery`, `EventQueryTriggerConfig`, `EventTriggerConfig`, `CronTrigger`, `IntervalTrigger`, `OnceTrigger`, `TimeTrigger`, `ScheduleTrigger`, `TriggerManualDetail`, plus Davis configs (`DavisEventConfig`, `DavisEventTriggerConfig`, `DavisProblemConfig`, `DavisProblemTriggerConfig`, `EntityTags`).

## Schedule / rule / calendar types

`Schedule`, `ScheduleExport`, `ScheduleInput(s)`, `ScheduleRequest`, `SchedulePreviewRequest`, `SchedulePreviewResponse`, `ScheduleFilterParameters`, `Rule`, `RuleCreate`, `RuleUpdate`, `RulePreviewResponse`, `RRule`, `FixedOffsetRule`, `RelativeOffsetRule`, `GroupingRule`, `BusinessCalendarCreate/Response/Update`, `Country(List)`, `Holiday(s)`, `HolidayCalendarList`, `Weekdays(Names/Values)`.

## Settings / webhook / misc

`GetSettingsResponse`, `UserSettings`, `GetServiceUsersResponse`, `WebhookHandler`, `WebhookHandlerList`, `VersionResponse`, `ChangeHistory`, `PaginatedChangeHistory`, `ModificationInfo`, `Source`, `EnvironmentObject`, `DuplicationRequest`.

## Error types

`Error`, `ErrorDetails`, `ErrorEnvelope`.

## Enums

`ExecutionState`, `ActionExecutionState`, `TaskExecutionState`, `EventLogState`, `WorkflowType`, `OwnerType`, `GetWorkflowsQueryOwnerType`, `TriggerType`, `TriggerSubType`, `RuleType`, `Freq`, `Byday`, `Byworkday`, `Wkst`, `Direction`, `Timezone`, `ValidationMethod`, `HmacSignatureEncoding`, `MaintenanceWindowTriggerBehaviorType`, `EventType`, and the preview/trigger config enums.
