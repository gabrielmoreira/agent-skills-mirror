# Preflight + seed queries (Phases 1–3b)

Load-bearing SOQL and shell recipes that `SKILL.md` Phases 1–3b hand off to.
`PREFIX_DOT` / `PREFIX_UNDER` / `URL_NS` come from `SKILL.md` "Find the
namespace first". Every query is **sales-org-scoped** where the underlying
object is partitioned.

## Phase 1 — Preflight queries

### Step 4: TPM entitlement (Permission Set License)

TPM is licensed via the `CGCRetailAndTPMMgmtPsl` PSL (no `TPM App`
UserLicense):

```sql
SELECT Id FROM PermissionSetLicenseAssign
 WHERE Assignee.Username = '<running-user-name>'
   AND PermissionSetLicense.DeveloperName = 'CGCRetailAndTPMMgmtPsl'
```

Empty + `OrganizationType = 'Developer Edition'` or `IsSandbox = true` →
**warn** (the permset gate below is the real check); any other org shape +
empty → **stop**.

### Step 5: Running-user permission set (TPM Admin persona)

Need a permset granting the *TPM Master Data Admin* persona. The shipped name
is `TPM_Master_Data_Admin` (bare, non-namespaced), but customers frequently
clone it; treat a miss as "ask", not "fail":

```sql
SELECT PermissionSet.Name, PermissionSet.Label FROM PermissionSetAssignment
 WHERE Assignee.Username = '<running-user-name>'
   AND (PermissionSet.Name = 'TPM_Master_Data_Admin'
        OR PermissionSet.Label LIKE '%TPM%Master Data Admin%')
```

Match → proceed. No match → offer
`sf org assign permset --name TPM_Master_Data_Admin --target-org <alias>` AND
ask if the user holds an equivalent (cloned/renamed) permset; wait for
confirmation or assignment, then re-query. Proceed only once admin access is
confirmed.

### Step 7: Running user's `Sales_Org__c` matches `<salesOrg>`

```sql
SELECT Id, Username, ${PREFIX_UNDER}Sales_Org__c FROM User WHERE Username = '<running-user-name>'
```

Blank or `!= '<salesOrg>'` → stop; fix on the user record (confirm before
mutating). This gate is R6 of `conventions-and-payload-rules.md` — blank
throws `SOU0003`, mismatch surfaces as "not found" (create/update) or
`TransformationError` (copy). Category access is preflighted in Phase 6 per
R9.

## Phase 2 — Verify BO API framework state

Read-only. All three counts MUST be scoped to `<salesOrg>` — the framework
rows are sales-org-partitioned.

```bash
# 1. Workflow rows for this sales org (expect 4: create/update/copy/derive)
sf data query --target-org <alias> --json --query "
  SELECT Name FROM ${PREFIX_UNDER}BO_API_Workflow__c
   WHERE ${PREFIX_UNDER}BO_API__r.Name = 'Promotion'
     AND ${PREFIX_UNDER}BO_API__r.${PREFIX_UNDER}Sales_Org__c = '<salesOrg>'"

# 2. Step rows for this sales org
sf data query --target-org <alias> --json --query "
  SELECT COUNT(Id) FROM ${PREFIX_UNDER}BO_API_Workflow_Step__c
   WHERE ${PREFIX_UNDER}Sales_Org__c = '<salesOrg>'"

# 3. Junction rows whose parent workflow belongs to a Promotion BO API for this sales org
sf data query --target-org <alias> --json --query "
  SELECT COUNT(Id) FROM ${PREFIX_UNDER}BO_API_Workflow_Workflow_Step__c
   WHERE ${PREFIX_UNDER}BO_API_Workflow__r.${PREFIX_UNDER}BO_API__r.Name = 'Promotion'
     AND ${PREFIX_UNDER}BO_API_Workflow__r.${PREFIX_UNDER}BO_API__r.${PREFIX_UNDER}Sales_Org__c = '<salesOrg>'"
```

Outcome routing:
- Zero workflow rows → fresh for this sales org, Phase 3 will seed.
- Full state (4 workflow rows `create/update/copy/derive`; >0 step + junction
  rows) → Phase 3 is a no-op for this sales org (still run for idempotency;
  3a shows zero net-new).
- Partial state → **error**; stop, report which rows are missing. A human
  inspects first.

## Phase 3a — Retrieve the packaged seed

Fetch the `TPMSetupData` static resource into a dedicated `setup-data/`
subproject (keeps the read-only managed resource out of the Phase-5a deploy
tree at `./.promotion-bo-api-deploy/force-app`).

1. Locate the resource:
   ```bash
   sf data query --target-org <alias> --json --query "
     SELECT Id, Name, NamespacePrefix, SystemModStamp, BodyLength
       FROM StaticResource WHERE Name = 'TPMSetupData'"
   ```
   Zero rows → stop ("TPMSetupData static resource not found — is the CGCloud
   package installed?"). Multiple rows → prefer the one whose
   `NamespacePrefix` matches Phase 1; if prefixes disagree, stop and ask.
2. Retrieve into the dedicated subproject:
   ```bash
   mkdir -p ./.promotion-bo-api-deploy/setup-data/force-app/main/default
   printf '{ "packageDirectories": [{ "path": "force-app", "default": true }], "sourceApiVersion": "60.0" }' \
     > ./.promotion-bo-api-deploy/setup-data/sfdx-project.json
   ( cd ./.promotion-bo-api-deploy/setup-data && sf project retrieve start \
       --metadata "StaticResource:${PREFIX_UNDER}TPMSetupData" --target-org <alias> --json )
   ```
   Non-success → stop, print `result` errors. (`sf project retrieve` works
   cross-platform; no `unzip` needed.)
3. SFDX expands the zip to
   `./.promotion-bo-api-deploy/setup-data/force-app/main/default/staticresources/${PREFIX_UNDER}TPMSetupData/BOApi/`.
   Expected 8 CSVs — `0_BO_API__c.csv`, `0_BO_API_Entity__c.csv`,
   `0_BO_API_Output_Entity__c.csv`, `0_BO_API_Workflow__c.csv`,
   `0_BO_API_Workflow_Entity__c.csv`, `0_BO_API_Workflow_Step__c.csv`,
   `0_BO_API_Workflow_Workflow_Step__c.csv`,
   `0_BO_API_Step_Input_Structure__c.csv` — plus `import.json`. Any missing →
   stop, print the delta.
4. Confirm each target sObject exists:
   `sf sobject describe --sobject '${PREFIX_UNDER}BO_API_Workflow__c' --target-org <alias> > /dev/null`
   (etc.). Any describe failure → stop (package partially installed).

## Phase 3b — Poll the batch chain

`GenericDemoSetupDataBatch` self-chains via `finish()`, so poll by class (not
by a single job id):

```bash
sf data query --target-org <alias> --json --query "
  SELECT COUNT() FROM AsyncApexJob
   WHERE ApexClass.Name = 'GenericDemoSetupDataBatch'
     AND CreatedDate >= ${PHASE3_START}
     AND Status NOT IN ('Completed','Failed','Aborted')"
```

Sleep 5s between polls; break when count is zero for **two consecutive** polls
(covers the gap between a parent's `finish()` and a child's `AsyncApexJob` row
appearing).

Final check — every child succeeded:

```sql
SELECT Id, Status, NumberOfErrors, ExtendedStatus FROM AsyncApexJob
 WHERE ApexClass.Name = 'GenericDemoSetupDataBatch' AND CreatedDate >= ${PHASE3_START}
```

Any `Failed`/`Aborted`/`NumberOfErrors > 0` → stop, print `ExtendedStatus`.
