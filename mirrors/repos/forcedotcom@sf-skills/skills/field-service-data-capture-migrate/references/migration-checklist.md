# Data Capture Migration Checklist

Step-by-step manual validation checklist for migrated flows.

## Pre-Migration

- [ ] **Identify candidate flows** — `SELECT Id, ApiName, Label, ProcessType FROM FlowDefinition WHERE ProcessType = 'FieldServiceMobile'` (Tooling API)
- [ ] **Retrieve legacy flow XML** — `sf project retrieve start --metadata Flow:<FlowApiName> --target-org <alias>`
- [ ] **Run analysis script** — `python3 "$SCR/analyze_flow.py" /tmp/<FlowApiName>.flow-meta.xml /tmp/<FlowApiName>_analysis.json`
- [ ] **Review risk score and manual steps** (from analysis output)
- [ ] **Decision: GREEN → automate, YELLOW → review spec, RED → manual redesign**

## Migration Phase

- [ ] **Run converter** — `python3 "$SCR/convert_to_dc_spec.py" /tmp/<FlowApiName>.flow-meta.xml /tmp/<FlowApiName>_dc_spec.json`
- [ ] **Review generated spec**
  - Field types are correct; choice mappings for picklists/radios are valid
  - No `_migrationNote` fields requiring manual config; check `_automationNote` for postScreen automation
- [ ] **Adjust spec as needed** — add `lookupObject` for Lookup fields, `fileName` for FileView fields, simplify flagged visibility rules, convert Apex-dependent logic to record lookups
- [ ] **Build Data Capture flow** — `python3 "$SCR/vendor/build_flow.py" /tmp/<FlowApiName>_dc_spec.json <FlowApiName>_v2 /tmp/<FlowApiName>_v2.flow-meta.xml`
- [ ] **Deploy to org** — `"$SCR/deploy_flow.sh" <alias> /tmp/<FlowApiName>_v2.flow-meta.xml`
- [ ] **Verify deploy success** — `SELECT ApiName, ProcessType FROM FlowDefinition WHERE ApiName = '<FlowApiName>_v2'` (Tooling API)

## Post-Deploy Validation

### Desktop Testing

- [ ] **Open Flow Builder** for the deployed flow — verify screens render, field properties (type, label, required, visibility) are correct, and automation elements (decisions, loops, record operations) behave as expected
- [ ] **Direct flow launch test** at `<instanceUrl>/flow/<FlowApiName>_v2` — complete the form end-to-end, verify all screens display, required validation and conditional visibility work, and submit succeeds
- [ ] **Verify record creation/update** — query the target object for records created `WHERE CreatedDate = TODAY`, confirm structure matches expectations

### Briefcase & Offline Priming

- [ ] **Add objects/fields to Briefcase** — Setup → Briefcase Builder; add every object/field the flow reads or writes, assign to the test user
- [ ] **Verify priming** — run as the test user in the User simulator; confirm the primed record count is reasonable

### Mobile Testing

- [ ] **Attach to test parent record** — this skill does not script this step (it would be a data-record write, out of the deploy-metadata-only scope). Attach the migrated form to a test parent record (ServiceAppointment/WorkOrder/etc.) manually via Setup's Data Capture assignment UI before continuing.
- [ ] **Verify Forms tab prerequisites** — all three must pass before the form appears on FSL Mobile:
  - `DynamicDataCapture` and `WorkPlan` internal sharing model (`EntityDefinition.InternalSharingModel`) must be `ReadWrite`, not `Private`
  - `FieldServiceSettings.DoesShareSaWithAr__c` and `DoesShareSaParentWoWithAr__c` must both be `true`
  - If any setting changed, re-save affected `AssignedResource` records so the new sharing rules apply
- [ ] **Device: sign out + back in** (required after any OWD/sharing change above)
- [ ] **Device: open parent record → Forms tab** — verify the migrated form appears and opens with all screens rendering
- [ ] **Device: complete form online** — fill all fields, exercise required validation and visibility rules, submit, verify the success message
- [ ] **Device: verify data persisted** — query the target object for today's records
- [ ] **Device: enable airplane mode → complete form offline** — fill and submit; verify it queues as a draft with a "queued" indicator
- [ ] **Device: disable airplane mode, wait ~30s for sync, then verify the queued record synced** — query the target object again

### Comparison Testing

- [ ] **Create a test parent record** (e.g. Work Order)
- [ ] **Complete the LEGACY flow on record A** — note fields populated and records created
- [ ] **Complete the MIGRATED flow on record B** — note fields populated and records created
- [ ] **Diff the two outcomes** — field values, record counts, and relationships must match; no data loss

### Edge Cases & Stress Tests

- [ ] **All decision branches** — walk each conditional path, verify correct screen routing
- [ ] **Visibility rules** — toggle controlling fields, verify dependents show/hide correctly
- [ ] **Repeater (if present)** — add, edit, and delete rows; verify the `.AllItems` loop creates the correct records
- [ ] **Lookup (if present)** — search, select, verify downstream references resolve
- [ ] **File/signature/image components (if present)** — capture/upload, verify `ContentDocument` and its `ContentDocumentLink` to the parent are created
- [ ] **Validation rules** — submit with missing required fields and with invalid data; confirm both are blocked with the correct error message

## Production Cutover

- [ ] **Final smoke test** on the migrated flow
- [ ] **Communicate to users** — notify technicians, provide a side-by-side comparison if useful, set a cutover date
- [ ] **Monitor for issues** — failed drafts in the sync queue, support tickets, data quality
- [ ] **Deactivate the legacy flow** (after the soak period)
- [ ] **Remove the `_v2` suffix** (optional) — clone with the production name, repoint DDC attachments, delete the `_v2` version
- [ ] **Clean up test records**

## Rollback Plan

If critical issues are found:

- [ ] **Deactivate the migrated flow** (Flow Builder)
- [ ] **Reactivate the legacy flow**
- [ ] **Repoint DDC attachments** back to the legacy flow — update `DynamicDataCapture.ActionDefinition` to `<LegacyFlowApiName>`
- [ ] **Notify users of the rollback**
- [ ] **Root cause analysis** — review failed drafts, check error logs, identify missing config (Briefcase, FLS, OWD, etc.)
- [ ] **Fix and retry** — adjust the spec, rebuild as `_v3`, repeat this checklist

## Documentation

- [ ] **Update org documentation** — migration date, differences from the legacy version, training materials
- [ ] **Archive the legacy flow** — export XML to source control with a README explaining the migration
- [ ] **Tag the migrated flow** — note in Flow Builder that it's a migrated version, referencing the original flow name

## Success Criteria

Migration is successful when:

1. All screens render correctly on mobile
2. All fields accept input and validate correctly
3. Conditional logic works (visibility, routing)
4. Record operations succeed (creates/updates)
5. Offline mode works (drafts queue and sync)
6. Data integrity matches legacy flow output
7. No user-reported critical issues for 1 week
8. Form appears reliably in FSL Mobile "Forms" tab
9. Performance is acceptable (form loads < 2 sec)
10. Technicians can complete the form without errors

## Common Issues & Fixes

| Issue | Likely Cause | Fix |
|-------|--------------|-----|
| Form doesn't appear in Forms tab | DDC/WorkPlan OWD is Private | Set to ReadWrite, re-save AssignedResources, sign out/in on device |
| Field missing on mobile | Not in Briefcase | Add object/field to Briefcase Builder |
| Lookup returns no results | `lookupObject` not configured | Add to spec and redeploy |
| File upload fails | `parentRecordId` not wired | Converter should auto-wire; verify XML |
| Visibility rule doesn't work | Formula too complex for DC | Simplify or move to Assignment + simple condition |
| Draft never syncs | Validation rule blocks insert | Fix validation rule or adjust form data |
| Form renders blank | Custom component not converted | Replace with native DC component |
| Create fails with "field required" | `isRequired` not set on field | Add to spec or in Flow Builder |
| Multiple rows not created | Repeater `.AllItems` loop incorrect | Verify loop references `RepeaterName.AllItems`, not `RepeaterName` |
| Cross-screen reference broken | Formula in DisplayText not supported | Move to Assignment between screens |
