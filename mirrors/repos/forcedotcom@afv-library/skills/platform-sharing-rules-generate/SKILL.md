---
name: platform-sharing-rules-generate
description: "Use this skill when users need to create, generate, or modify Salesforce Sharing Rules metadata. TRIGGER when: users mention sharing rules, record sharing, criteria-based sharing, role-based sharing, guest user sharing, portal user sharing, sharingRules, sharingCriteriaRules, sharingGuestRules, sharingOwnerRules, .sharingRules-meta.xml files, or ask to share records with specific roles or groups. Also trigger when users want to configure record-level access beyond org-wide defaults (OWD), share object records with roles, groups, or guest users, or set up Experience Site guest user record visibility. SKIP when: user needs permission sets or profiles (use platform-permission-set-generate), or needs object-level security rather than record-level sharing (use platform-permission-set-generate)."
metadata:
  version: "1.0"
---

# Sharing Rules Generator

Generate Salesforce Sharing Rules metadata to control record-level access beyond org-wide defaults. Supports criteria-based rules, role/group-based owner rules, and guest user rules for Experience Sites.

## Scope

- **In scope**: Generating `sharingCriteriaRules`, `sharingOwnerRules`, and `sharingGuestRules` metadata; retrieving existing sharing rules from an org; appending new rules to existing files; configuring rules for Guest and Portal profiles.
- **Out of scope**: Changing org-wide defaults (OWD/sharing model), creating Experience Sites, configuring permission sets or profiles (use `platform-permission-set-generate`), territory-based sharing rules.

---

## Clarifying Questions

Before generating, confirm with the user if not already clear:

- Which object should the sharing rule apply to? (standard or custom object API name)
- What type of rule? (criteria-based, role/group-based owner rule, or guest user rule)
- Who should records be shared with? (role name, group, portal role, or guest user nickname)
- What access level? (Read or Read/Write)
- For criteria-based rules: what field conditions should match?

---

## Required Inputs

Gather or infer before proceeding:

- **Object API name**: The sObject the rule targets (e.g., `Account`, `Property__c`)
- **Rule type**: One of `sharingCriteriaRules`, `sharingOwnerRules`, or `sharingGuestRules`
- **Shared-to target**: Role, group, portal role, or guest user community nickname
- **Access level**: `Read` or `Edit` (maps to Read-Only or Read/Write)
- **Criteria** (for criteria/guest rules): Field name, operation, and value for each filter item

Defaults unless specified:
- Access level: `Read`
- `includeRecordsOwnedByAll`: `true` for criteria rules
- `includeHVUOwnedRecords`: `false` for guest rules
- Account sharing rules include `accountSettings` with all sub-access levels set to `None`

---

## Workflow

All steps are sequential. Do not skip or reorder.

### Phase 1 — Discover

1. **Resolve the SFDX project path** — find the project's `sfdx-project.json` and identify the package directory for `sharingRules/`.

2. **Check for existing sharing rules** — look for `<packageDir>/sharingRules/<ObjectName>.sharingRules-meta.xml`. If found, read it to understand existing rules and avoid duplicates.

3. **If no local file exists**, retrieve from the org:
   ```sh
   sf project retrieve start --metadata "SharingRules:<ObjectName>" --target-org <org>
   ```

### Phase 2 — Determine Rule Type

4. **Select the rule type** based on user intent. Read `references/rule-types.md` for the complete schema of each type and its required elements.

5. **For Account sharing rules**: the `accountSettings` element is required. Default sub-access levels to `None` unless the user specifies otherwise.

6. **For Guest rules**: the `sharedTo` must use `<guestUser>` with the site guest user's community nickname. Never use `<role>` or `<group>` for guest rules.

### Phase 3 — Generate

7. **Construct the XML** following the schema in `references/rule-types.md`. Key structure:
   - One `.sharingRules-meta.xml` file per object
   - All rules for the same object go in the same file
   - If appending to an existing file, add the new rule element inside the existing `<SharingRules>` root

8. **Name the rule** — derive `<fullName>` from the intent (PascalCase, no spaces, descriptive). Generate a matching `<label>` in Title Case with spaces.

9. **Write the file** to `<packageDir>/sharingRules/<ObjectName>.sharingRules-meta.xml`.

### Phase 4 — Verify

10. **Run the verification checklist** below before presenting output.

---

## Verification Checklist

### Universal Checks
- [ ] Does the file have the XML declaration and `<SharingRules xmlns="http://soap.sforce.com/2006/04/metadata">` root?
- [ ] Is there exactly one file per object with all rules inside it?
- [ ] Does `<fullName>` use PascalCase with no spaces?
- [ ] Is `<label>` present and human-readable?
- [ ] Is `<accessLevel>` one of `Read` or `Edit`?

### Criteria Rule Checks
- [ ] Is `<includeRecordsOwnedByAll>` present (required boolean)?
- [ ] Does each `<criteriaItems>` have `<field>`, `<operation>`, and `<value>`?
- [ ] Are picklist values valid for the target org?

### Guest Rule Checks   CRITICAL
- [ ] Does `<sharedTo>` use `<guestUser>` (NOT `<role>` or `<group>`)?
- [ ] Is `<includeHVUOwnedRecords>` present (required boolean)?
- [ ] Is `<includeRecordsOwnedByAll>` ABSENT (only for criteria rules, not guest rules)?

### Owner Rule Checks
- [ ] Does the rule have both `<sharedFrom>` and `<sharedTo>` elements?
- [ ] Do both use valid `<role>`, `<roleAndSubordinates>`, or `<group>` targets?

### Account-Specific Checks   CRITICAL
- [ ] If object is Account, is `<accountSettings>` present with all three sub-elements?
- [ ] Are `<caseAccessLevel>`, `<contactAccessLevel>`, `<opportunityAccessLevel>` all set?

---

## Rules / Constraints

| Constraint | Rationale |
|-----------|-----------|
| One `.sharingRules-meta.xml` file per object | Platform requirement — multiple files cause deployment errors |
| Guest rules must use `<guestUser>` in `sharedTo` | Using `<role>` or `<group>` causes: "Specify a guest user's nickname for the guestUser field" |
| Account rules require `<accountSettings>` | Without it: "AccountSettings is required for account sharing rules" |
| `includeRecordsOwnedByAll` is required on criteria rules | Missing it causes: "Required field is missing: sharingCriteriaRules" |
| `includeHVUOwnedRecords` is required on guest rules | Missing it causes deployment failure |
| Criteria field values must exist as picklist values on the org | Invalid values cause: "Picklist value does not exist" |
| Never hardcode file paths — resolve from `sfdx-project.json` | Customer projects use custom package directories |

---

## Gotchas

| Issue | Resolution |
|-------|------------|
| Guest rule uses `<role>` instead of `<guestUser>` | Replace with `<guestUser>CommunityNickname</guestUser>` |
| Account rule missing `accountSettings` | Add `<accountSettings>` with all three access level sub-elements set to `None` |
| Criteria rule missing `includeRecordsOwnedByAll` | Add `<includeRecordsOwnedByAll>true</includeRecordsOwnedByAll>` |
| Picklist value mismatch | Query the org for valid values before generating criteria |
| Appending duplicates existing rule name | Check existing `<fullName>` values before writing |
| Guest user nickname not found | Query: `SELECT CommunityNickname FROM User WHERE UserType='Guest' AND IsActive=true` |

---

## Output Expectations

Deliverables:
- `<packageDir>/sharingRules/<ObjectName>.sharingRules-meta.xml` — complete sharing rules file for the target object

---

## Cross-Skill Integration

| Need | Delegate to |
|------|-------------|
| Permission set configuration | `platform-permission-set-generate` skill |
| Custom object creation (if target object doesn't exist) | `platform-custom-object-generate` skill |

---

## Reference File Index

| File | When to read |
|------|-------------|
| `references/rule-types.md` | Phase 2 — before generating any rule, to get the complete XML schema for each rule type |
