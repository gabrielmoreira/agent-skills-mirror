// Anonymous Apex template — schedules a Salesforce Schedulable class.
//
// Placeholders (single-quote-escaped by scripts/build-scheduled-apex.mjs):
//   {{JOB_NAME}}         — value of CronTrigger.CronJobDetail.Name after scheduling.
//   {{CRON_EXPRESSION}}  — 6- or 7-field Salesforce cron expression.
//   {{APEX_CLASS_NAME}}  — bare identifier of a class that implements Schedulable.
//
// Prerequisites (enforced upstream — see references/scheduled_apex_path.md):
//   1. Step F-1 has already asserted no CronTrigger with CronJobDetail.Name = '{{JOB_NAME}}'
//      exists on the target org — otherwise System.schedule throws.
//   2. The {{APEX_CLASS_NAME}} class exists on the target org — sandbox refresh
//      copies class metadata, so this is normally satisfied post-refresh.
System.schedule('{{JOB_NAME}}', '{{CRON_EXPRESSION}}', new {{APEX_CLASS_NAME}}());
