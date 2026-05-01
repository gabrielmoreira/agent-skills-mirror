---
name: odoo-code-review
description: Review Odoo code for correctness, security, performance, and Odoo 18 standards. Use when reviewing Odoo modules, diffs, or pull requests; produce a scored report with weighted criteria.
---

# Odoo Code Review

## Objective

Review Odoo code changes against clear criteria, identify risks, and score using a weighted scale from an Odoo 18 expert perspective.

## Pre-review Requirements

- Read `skills/odoo-18.0/SKILL.md` as the master index for all Odoo 18 guides.
- Read relevant guides from `skills/odoo-18.0/references/` based on change scope:
  - **Models/ORM**: `odoo-18-model-guide.md`
  - **Fields**: `odoo-18-field-guide.md`
  - **Decorators**: `odoo-18-decorator-guide.md`
  - **Performance**: `odoo-18-performance-guide.md`
  - **Views/XML**: `odoo-18-view-guide.md`
  - **Security**: `odoo-18-security-guide.md`
  - **Controllers**: `odoo-18-controller-guide.md`
  - **Transactions**: `odoo-18-transaction-guide.md`
  - **Mixins**: `odoo-18-mixins-guide.md` (mail.thread, activities)
  - **Testing**: `odoo-18-testing-guide.md`
  - **Migration**: `odoo-18-migration-guide.md`
  - **Actions**: `odoo-18-actions-guide.md`
  - **Data Files**: `odoo-18-data-guide.md`
  - **Manifest**: `odoo-18-manifest-guide.md`
- Identify scope: module, file, and change context.
- Master Odoo 18 API changes: `<list>` instead of `<tree>`, `@api.ondelete`, etc.

## Expert Review Process

1. **Scope**: Identify change scope, objectives, and key risks
2. **ORM & Model Methods**: Search patterns, CRUD operations, recordset operations
3. **Field Definitions**: Field types, computed fields, relational field parameters
4. **API Decorators**: @api.depends, @api.constrains, @api.ondelete (Odoo 18!)
5. **Performance**: N+1 detection, batch operations, field selection
6. **Transaction Management**: Savepoints, UniqueViolation, serialization
7. **Views & XML**: Odoo 18 tags (`<list>`), inheritance, structure
8. **Security**: ACL, record rules, exceptions, sudo usage
9. **Controllers**: Auth types, CSRF protection, routing
10. **Mixins**: mail.thread, mail.activity.mixin, mail.alias.mixin usage
11. **Testing**: Test coverage, proper test cases, @tagged decorators
12. **Migration**: Migration scripts, data migration patterns
13. **Actions**: Window actions, server actions, cron jobs
14. **Data Files**: XML/CSV data structure, noupdate, shortcuts
15. **Manifest**: Dependencies, external deps, hooks, assets

## Odoo 18 Complete Checklist

### ORM & Model Methods (30%)
- ❌ **DO NOT** use `search()` inside loop (N+1 anti-pattern)
- ✅ Use `search_read()` when dict output needed
- ✅ Use `read_group()` for aggregate queries
- ✅ Use `IN` domain instead of search in loop: `[('order_id', 'in', orders.ids)]`
- ✅ Batch `create([{...}, {...}])` for multiple records
- ✅ Use `recordset.write()` instead of loop
- ✅ Use `recordset.unlink()` instead of loop
- ✅ Use `mapped()` instead of list comprehension
- ✅ Use `filtered()` before operations
- ✅ Use `exists()` to filter non-existing records

### Field Definitions (15%)
- ✅ `Many2one` has `ondelete` parameter (`cascade`, `restrict`, `set null`)
- ✅ `Monetary` has `currency_field` parameter
- ✅ `One2many` has `inverse_name` parameter
- ❌ **DO NOT** use `Float` for currency (use `Monetary`)
- ❌ **DO NOT** use `<tree>` in Odoo 18 (use `<list>`)
- ✅ Computed fields have `store=True` if searchable/groupable needed
- ✅ `@api.depends` includes ALL dependencies with dotted paths

### API Decorators (15%)
- ✅ `@api.depends` uses dotted paths for related fields: `@api.depends('partner_id.email')`
- ❌ **DO NOT** use dotted paths in `@api.constrains` (only simple field names)
- ✅ `@api.ondelete(at_uninstall=False)` instead of overriding `unlink()` for validation (Odoo 18!)
- ✅ `@api.constrains` raises `ValidationError`
- ✅ `@api.model_create_multi` for batch create (Odoo 18)

### Performance (20%)
- ❌ **DO NOT** `search()` in loop
- ❌ **DO NOT** `browse()` in loop
- ❌ **DO NOT** `create()` in loop
- ❌ **DO NOT** `write()` in loop
- ❌ **DO NOT** `unlink()` in loop
- ✅ Use prefetch (automatic) for related field access
- ✅ Use `search_read()` to fetch specific fields
- ✅ Use `bin_size=True` for binary fields
- ✅ Use advisory locks for concurrent operations

### Transaction Management (10%)
- ✅ Use `with self.env.cr.savepoint():` for error isolation
- ❌ **DO NOT** continue after UniqueViolation without savepoint
- ✅ Use advisory locks to prevent serialization errors
- ✅ Group identical updates to minimize conflicts

### Views & XML (5%)
- ✅ Use `<list>` instead of `<tree>` (Odoo 18!)
- ✅ Use `decoration-*` for row styling
- ✅ Use `xpath` or shorthand with `position` for inheritance
- ✅ Proper `inherit_id` reference

### Security (5%)
- ✅ Has `ir.model.access.csv` file with proper permissions
- ✅ Use `UserError` for business logic errors
- ✅ Use `ValidationError` for constraint violations
- ✅ Use `AccessError` for permission issues
- ❌ **DO NOT** raise generic `Exception`
- ✅ Record rules defined with proper domain_force

### Controllers (5%)
- ✅ Use correct `auth` type (`user`, `public`, `none`)
- ✅ Use `auth='none'` for truly public endpoints (webhooks)
- ✅ CSRF enabled for POST (default)
- ✅ `csrf=False` only for external webhooks

### Mixins (Additional Check)
- ✅ `mail.thread` properly configured with `tracking=True` on tracked fields
- ✅ `mail.activity.mixin` used for activity-enabled models
- ✅ `mail.alias.mixin` properly configured with alias fields
- ✅ `utm.mixin` for campaign tracking when applicable
- ✅ Proper message_post usage, not direct chatter manipulation

### Testing (Additional Check)
- ✅ Tests cover new functionality
- ✅ Proper use of `@tagged` decorators (standard, post_install, etc.)
- ✅ TransactionCase for model tests, HttpCase for web tests
- ✅ Test data properly isolated
- ✅ Query count assertions for performance-critical code

### Migration (Additional Check)
- ✅ Migration scripts in `migrations/{version}/` directory
- ✅ Pre-migration scripts for data cleanup
- ✅ Post-migration scripts for data migration
- ✅ Uses hooks (pre_init, post_init, uninstall) appropriately
- ✅ Idempotent migration scripts

## Anti-Patterns to Detect

| Anti-Pattern | Consequence | Fix |
|--------------|-------------|-----|
| `search()` in loop | N+1 queries | Use `search_read()` with `IN` domain |
| `create()` in loop | N INSERT statements | Batch: `create([{...}, {...}])` |
| `write()` in loop | N UPDATE statements | `records.write({...})` |
| `unlink()` in loop | N DELETE statements | `records.unlink()` |
| Override `unlink()` for validation | Breaks module uninstall | Use `@api.ondelete(at_uninstall=False)` |
| `@api.depends('a')` then access `a.b` | N queries | Add `@api.depends('a.b')` |
| `@api.constrains('a.b')` | Not supported | Use only `@api.constrains('a')` |
| `<tree>` in Odoo 18 | Deprecated | Use `<list>` |
| `Float` for currency | Precision issues | Use `Monetary` |
| Missing `ondelete` on Many2one | Orphan records | Add `ondelete='cascade/restrict'` |
| Generic `Exception` | Poor UX | Use `UserError`, `ValidationError` |
| Continue after UniqueViolation without savepoint | Transaction aborted | Use `with self.env.cr.savepoint():` |
| Direct chatter manipulation instead of message_post | Breaks mail.thread features | Use `message_post()` with proper subtype |
| Missing `tracking=True` on tracked fields | No field tracking in chatter | Add `tracking=True` to field definition |
| Tests without `@tagged` decorators | Wrong test environment | Add `@tagged('standard')`, `@tagged('post_install')` |
| Non-idempotent migration script | Fails on re-run | Use `if not field_exists:` checks |
| Missing `noupdate="1"` on reference data | Data overwritten on update | Add `noupdate="1"` to reference records |
| Cron without `interval_number` and `interval_type` | Never runs | Add proper interval configuration |

## Scoring Scale (Weighted)

**Criteria** (score 1-10):

- **ORM & Model Methods** (28%)
- **Field Definitions** (14%)
- **API Decorators** (14%)
- **Performance** (18%)
- **Transaction Management** (10%)
- **Views & XML** (4%)
- **Security** (6%)
- **Controllers** (6%)

**Total calculation**:

```
total = 0.28*orm + 0.14*fields + 0.14*decorators + 0.18*performance + 0.10*transaction + 0.04*views + 0.06*security + 0.06*controllers
```

**Score anchors**:

- **9-10**: Excellent, no significant risks, follows all best practices
- **7-8**: Good, minor issues or improvements possible
- **5-6**: Average, clear risks to address, has anti-patterns
- **3-4**: Poor, serious errors or regression-prone
- **1-2**: Very poor, cannot merge, violates critical patterns

## Report Format (Required)

```
## Quick Summary
- [1-2 sentences summarizing key points]

## Overall Score
- Total: X.X/10
- Formula: 0.28*ORM + 0.14*Fields + 0.14*Decorators + 0.18*Perf + 0.10*Trans + 0.04*Views + 0.06*Sec + 0.06*Controllers

## Score by Criteria
- ORM & Model Methods: X/10 — [brief reason, any anti-patterns?]
- Field Definitions: X/10 — [brief reason]
- API Decorators: X/10 — [brief reason, check @api.ondelete, dotted paths]
- Performance: X/10 — [brief reason, any N+1?]
- Transaction Management: X/10 — [brief reason, savepoints correct?]
- Views & XML: X/10 — [brief reason, using <list>?]
- Security: X/10 — [brief reason]
- Controllers: X/10 — [brief reason]

## Key Findings (high → low priority)

### 🔴 Critical (Must Fix)
- [Severity] Brief description + consequence + fix suggestion
- Code reference: `path/file.py:XX`

### 🟡 Major (Should Fix)
- [Severity] Brief description + consequence + fix suggestion
- Code reference: `path/file.py:XX`

### 🔵 Minor (Nice to Have)
- [Severity] Brief description + improvement suggestion

## Positive Patterns Found
- ✅ [Good pattern found] - Line XX

## Recommendations
- [Specific, clear improvements, in priority order]

## Testing
- Ran: [if any, state commands]
- Missing: [tests missing or not run, N+1 scenarios]
```

## Response Rules

- Prioritize error and risk detection first, then suggestions
- If no significant issues, clearly state "No findings"
- Cite correct file and code when needed: `path/to/file.py:XX`
- State assumptions when information is missing (don't guess)
- Focus on Odoo-specific patterns, not generic Python advice
- Provide code examples for complex issues
- Reference Odoo documentation when applicable

## Deep Dive Checks

When reviewing, thoroughly check:

1. **Does @api.depends have complete dependencies?**
   - Check dotted paths: `partner_id.email` instead of just `partner_id`
   - Missing dependencies cause N queries
   - Reference: `skills/odoo-18.0/references/odoo-18-decorator-guide.md`

2. **Are there N+1 queries?**
   - Loop with `search()`, `browse()`, `read()` inside
   - Solution: `search_read()` with `IN` domain or `read_group()`
   - Reference: `skills/odoo-18.0/references/odoo-18-performance-guide.md`

3. **Are there batch operations?**
   - `create()`, `write()`, `unlink()` in loop
   - Solution: Batch operations on recordset
   - Reference: `skills/odoo-18.0/references/odoo-18-performance-guide.md`

4. **Is transaction safe?**
   - UniqueViolation handling without savepoint
   - Concurrent updates without advisory lock
   - Reference: `skills/odoo-18.0/references/odoo-18-transaction-guide.md`

5. **Are Odoo 18 patterns correct?**
   - Use `<list>` instead of `<tree>`
   - Use `@api.ondelete()` instead of overriding `unlink()`
   - Use `@api.model_create_multi` for batch create
   - Reference: `skills/odoo-18.0/references/odoo-18-view-guide.md`

6. **Are field definitions correct?**
   - `Monetary` with `currency_field`
   - `Many2one` with `ondelete`
   - Computed field with `store=True` if needed
   - Reference: `skills/odoo-18.0/references/odoo-18-field-guide.md`

7. **Is exception handling correct?**
   - `UserError`, `ValidationError`, `AccessError`
   - No generic `Exception`
   - Reference: `skills/odoo-18.0/references/odoo-18-security-guide.md`

8. **Are mixins properly configured?**
   - `mail.thread` with proper tracking fields
   - `mail.activity.mixin` for activities
   - `mail.alias.mixin` with alias fields
   - Reference: `skills/odoo-18.0/references/odoo-18-mixins-guide.md`

9. **Is testing adequate?**
   - Tests for new functionality
   - Proper use of `@tagged` decorators
   - Query count assertions for performance
   - Reference: `skills/odoo-18.0/references/odoo-18-testing-guide.md`

10. **Are migrations handled correctly?**
    - Proper migration script location
    - Pre/post migration scripts
    - Idempotent operations
    - Reference: `skills/odoo-18.0/references/odoo-18-migration-guide.md`

11. **Are actions properly defined?**
    - Window actions with correct context
    - Server actions for automation
    - Cron jobs with proper intervals
    - Reference: `skills/odoo-18.0/references/odoo-18-actions-guide.md`

12. **Are data files correct?**
    - Proper XML record structure
    - `noupdate="1"` for reference data
    - CSV data properly formatted
    - Reference: `skills/odoo-18.0/references/odoo-18-data-guide.md`

13. **Is manifest correct?**
    - All dependencies declared
    - External dependencies listed
    - Hooks properly configured
    - Reference: `skills/odoo-18.0/references/odoo-18-manifest-guide.md`
