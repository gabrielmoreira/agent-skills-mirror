# Data Model Reference — X Bug Triage Plugin

## Tables (8)

| Table | Primary Key | Purpose |
|-------|------------|---------|
| triage_runs | run_id | Metadata for each triage execution |
| candidates | post_id | Normalized bug candidates (33 fields) |
| clusters | cluster_id | Grouped bug reports with severity and lifecycle |
| cluster_posts | (cluster_id, post_id) | Junction: candidates ↔ clusters |
| overrides | override_id | Human corrections (8 types) persisted across runs |
| suppression_rules | rule_id | Known noise patterns for auto-dismissal |
| issue_links | link_id | Bidirectional cluster ↔ GitHub issue mapping |
| audit_log | event_id | Complete audit trail (12 event types) |

## Key Enums

- **Classification** (12): bug_report, sarcastic_bug_report, feature_request, account_problem, billing_problem, policy_or_expectation_mismatch, ux_friction, model_quality_issue, user_error_or_confusion, praise, noise, needs_review
- **ClusterFamily** (4): product_defect, model_quality_defect, policy_mismatch, ux_friction
- **ClusterState** (7): open, filed, monitoring, fix_deployed, resolved, closed, suppressed
- **Severity** (4): low, medium, high, critical
- **EvidenceTier** (4): 1 (Exact), 2 (Strong), 3 (Moderate), 4 (Weak)
- **OverrideType** (8): cluster_merge, cluster_split, noise_suppression, routing_override, issue_family_link, severity_override, label_correction, snooze
- **AuditEventType** (12): ingest_run_started/completed, source_fetched, candidate_classified, pii_redaction, cluster_created/updated/state_changed, routing_recommendation, escalation_triggered, human_action, override_created

## Candidate Fields (33)

post_id, author_handle, author_id, timestamp, source_type, product_surface, feature_area, symptoms, error_strings, repro_hints, urls, has_media, media_keys, language, conversation_id, thread_root_id, reply_to_id, referenced_post_ids, public_metrics, classification, classification_confidence, classification_rationale, report_quality_score, independence_score, account_authenticity_score, historical_accuracy_score, reporter_reliability_score, reporter_category, pii_flags, raw_text_redacted, raw_text_storage_policy, triage_run_id

## Source: `lib/types.ts`, `db/schema.sql`
