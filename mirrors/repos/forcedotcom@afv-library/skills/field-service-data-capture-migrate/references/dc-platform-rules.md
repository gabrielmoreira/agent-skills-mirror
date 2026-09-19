# DC platform rules reference

These rules govern any valid DataCaptureFlow. The transformer enforces them automatically. This section is the authoritative reference for debugging deploy errors or validating migrated flows manually.

## Required flow headers

```xml
<processType>DataCaptureFlow</processType>
<areMetricsLoggedToDataCloud>false</areMetricsLoggedToDataCloud>
<environments>Offline</environments>
<!-- NO <apiVersion> tag — causes: "You can't specify the field API Version" -->
```

## Required input variables (platform launch contract)

SFS Mobile passes these on launch — every DataCaptureFlow must declare them:
```xml
<variables><name>recordId</name><dataType>String</dataType><isInput>true</isInput>...</variables>
<variables><name>parentRecordId</name><dataType>String</dataType><isInput>true</isInput>...</variables>
<variables><name>parentObjectType</name><dataType>String</dataType><isInput>true</isInput>...</variables>
```

## Flow structure rules

| Rule | Detail |
|---|---|
| First element after `<start>` | **Must be a `<screens>` element** — connecting `<start>` directly to recordLookups or decisions causes mobile offline rendering failure |
| DML placement | Create, Update, Delete MUST be at the END of the flow |
| Screens after DML | NOT allowed |
| Decision between sequential CUD nodes | A Decision CAN route to which CUD chain starts; once a CUD chain begins, no Decision may appear between sequential CUD nodes |
| Subflows (CUD) | Subflows CANNOT contain Create, Update, or Delete operations |
| Subflows (type) | Can only call another DataCaptureFlow — calling an AutoLaunched subflow is blocked |
| `<actionCalls>` | Not allowed in DataCaptureFlow |
| Fault connectors | Not supported — must be stripped |
| XML element grouping | All elements of the same type must appear in a contiguous block — mixing them causes "Element X is duplicated" deploy error |

## Visibility rule accessor suffixes

```xml
<leftValueReference>componentName.SUFFIX</leftValueReference>
```

| Component type | Suffix |
|---|---|
| Input components (`dcTextInput`, `dcNumeric`, `dcCheckbox`, `dcDate`, etc.) | `.value` |
| Choice components (`dcPicklist`, `dcRbGroup`, `dcCbGroup`) | `.selectedChoiceValues` |
| Toggle (`dcToggle`) | `.isActive` |
| Name component (`dcName`) | `.firstName` / `.lastName` |
| Lookup single select (`dcLookup`) | `.recordId` |
| Lookup multi-select (`dcLookup` with `isMultiSelection=true`) | `.recordIds` |

## Decision IsNull canonical pattern

`IsNull` uses a `booleanValue` on the right — NOT a null literal:
```xml
<conditions>
    <leftValueReference>v_ParentId</leftValueReference>
    <operator>IsNull</operator>
    <rightValue><booleanValue>false</booleanValue></rightValue>
    <!-- false = "is not null"; true = "is null" -->
</conditions>
```

## Calculation timing (critical)

Calculated values **cannot display on the same screen that collects the inputs** — calculations run only after the user taps Next.

Required pattern:
```text
Screen N (collect inputs) → Assignment / recordLookups / decisions → Screen N+1 (display results)
```

Screen N's connector must point to the calculation element, NOT directly to Screen N+1.

## DisplayText formula limitations

`DisplayText` has severely limited formula support at mobile runtime. Complex formulas deploy and preview in Flow Builder but **fail at runtime** with `Error while resolving default value reference`.

| Pattern | Works in DC DisplayText? |
|---|---|
| Simple variable reference: `{!var_RiskScore}` | Yes |
| Component ref: `{!MyPicklist.selectedChoiceValues}` | Yes |
| Global vars: `{!$Flow.CurrentDate}`, `{!$User.FirstName}` | Yes |
| `IF(Toggle.isActive, "YES", "NO")` | No — fails at mobile runtime |
| `TEXT(CASE(...))`, `ADDMONTHS(...)`, nested date math | No — fails at mobile runtime |
| Mixing multiple component refs + formulas in one `fieldText` | No — fails at mobile runtime |

**Pattern**: pre-calculate in an `<assignments>` element → store in a variable → reference that variable in DisplayText.

## `isRequired=true` behind a `visibilityRule`

**Never** mark a field `isRequired=true` if it is behind a `visibilityRule`. The required check fires even while the field is hidden — the mobile worker cannot proceed.

Set `isRequired=false` and add a `validationRule` instead:
```text
IF(TriggerField.isActive, AND(NOT(ISBLANK(value)), value >= 0), TRUE)
```

## Lookup component specifics

| Property | Behaviour |
|---|---|
| Display label in results | Driven by the object's **Primary Compact Layout** — first field in that layout. To change: Setup → Compact Layouts → reorder → assign as Primary. No `displayField` inputParameter exists. |
| Multi-select | Set `isMultiSelection=true`; output is `{!Lookup.recordIds}` (collection) |
| Scoping filter | Use `recordIdCollection` (not `recordIds`) — only effective when `isMultiSelection=true`; silently ignored in single-select |
| Attribute names | `isDisabled` and `isReadonly` (lowercase `o`) — `disabled`/`readOnly` cause deploy errors |

## Repeater specifics

- Output collection: **`.AllItems` only** (confirmed API v66) — `AddedItems`, `PrepopulatedItems`, `RemovedItems` all cause deploy errors
- Loop body references: use `Loop_Name.fieldName.value` (the loop variable's name), NOT `Repeater_Name.fieldName.value`
- Prepopulate: bind an existing SObject collection via the `collection` inputParameter
- Inside nested fields: reference source rows via `SourceCollection[$EachItem].FieldApiName` — `$EachItem` only resolves inside Repeater-nested fields; downstream loops still iterate `Repeater_Name.AllItems` normally
- The Repeater itself must NOT have `storeOutputAutomatically` — causes deploy error; only nested fields inside the Repeater get it

## Global variable allowlist

Only these global variables are supported in DataCaptureFlow (all others blocked):

- `$Api`, `$Label`, `$Organization`, `$Profile`, `$System`, `$User`, `$UserRole`
- `$Flow.CurrentDate`, `$Flow.CurrentDateTime`, `$Flow.InterviewStartTime`, `$Flow.InterviewGuid`

Input default binding behavior:

| Default binding | Component | Works? |
|---|---|---|
| `$User.Username` | `dcTextInput` | Yes |
| `$User.Name` | `dcTextInput` | No — type mismatch, use `$User.Username` |
| `$Flow.InterviewStartTime` | `dcDateTime` | Yes |
| `$Flow.CurrentDate` | `dcDate` | Yes |
