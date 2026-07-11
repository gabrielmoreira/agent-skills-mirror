# ACCESS / GOVERNANCE Templates

Each template is a verified shape from a passing test fixture. Copy, then change names/values.

---

## ACCESS — Simple Permit (no conditions)

Source: `baseSteelthread`

```xml
<?xml version="1.0" encoding="UTF-8"?>
<PolicyRuleDefinition xmlns="http://soap.sforce.com/2006/04/metadata">
    <action>Read</action>
    <category>ACCESS_POLICY_RULE_DEFINITION</category>
    <effect>Permit</effect>
    <label>Rule0</label>
    <policyRuleDefinitionSetName>Set1</policyRuleDefinitionSetName>
    <principalAuthenticationLevel>INTERNAL</principalAuthenticationLevel>
    <principalScopeType>ANY</principalScopeType>
    <resourceScopeType>ANY</resourceScopeType>
    <ruleConsumer>DATACLOUD</ruleConsumer>
    <transformPrecedence>0</transformPrecedence>
</PolicyRuleDefinition>
```

---

## ACCESS / GOVERNANCE — "Objects AND all their fields" via TupleRead (UI-compatible)

Source: see §8.2.1 of policy.md

Three required pieces:
1. `<action>TupleRead</action>` — cascades object-level condition to fields
2. **OR-of-ENTITYTYPE clause** — required for UI editability (without it the builder crashes)
3. The actual semantic gate (tag / classification / permission)

```xml
<?xml version="1.0" encoding="UTF-8"?>
<PolicyRuleDefinition xmlns="http://soap.sforce.com/2006/04/metadata">
    <action>TupleRead</action>
    <category>GOVERNANCE_POLICY_RULE_DEFINITION</category>
    <effect>Permit</effect>
    <label>GrantPublicAccess</label>
    <policyRuleDefinitionSetName>PublicAccessSet</policyRuleDefinitionSetName>
    <principalAuthenticationLevel>INTERNAL</principalAuthenticationLevel>
    <principalScopeType>ANY</principalScopeType>
    <resourceScopeType>ANY</resourceScopeType>
    <ruleConsumer>DATACLOUD</ruleConsumer>
    <transformPrecedence>0</transformPrecedence>
    <whenPolicyRuleDefinitionClauseConjunction>
        <!-- (1) and (2): OR-of-ENTITYTYPE clause — required for UI rendering -->
        <conditions>
            <clause>WHEN</clause>
            <operator>IS</operator>
            <policyRuleValueSet>
                <valueString>{&quot;t&quot;:&quot;Text&quot;,&quot;v&quot;:&quot;OBJECT&quot;}</valueString>
            </policyRuleValueSet>
            <resourcePath>ENTITYTYPE</resourcePath>
        </conditions>
        <conditions>
            <clause>WHEN</clause>
            <operator>IS</operator>
            <policyRuleValueSet>
                <valueString>{&quot;t&quot;:&quot;Text&quot;,&quot;v&quot;:&quot;FIELD&quot;}</valueString>
            </policyRuleValueSet>
            <resourcePath>ENTITYTYPE</resourcePath>
        </conditions>
        <!-- (3): actual semantic gate -->
        <conditions>
            <clause>WHEN</clause>
            <operator>CONTAINS_ANY</operator>
            <resourcePath>TAG</resourcePath>
            <policyRuleValueSet>
                <valueReference>DataGovernanceTags.ExternalData.Visibility.Public</valueReference>
                <valueReferenceType>STANDARD_TAG</valueReferenceType>
            </policyRuleValueSet>
        </conditions>
        <!-- MUST use (AND N) not bare N for every top-level param — bare index crashes UI -->
        <conjunctionExpression>(AND (OR 1 2) (AND 3))</conjunctionExpression>
    </whenPolicyRuleDefinitionClauseConjunction>
</PolicyRuleDefinition>
```

For **deny semantics**: `<effect>Forbid</effect>`. To add "deny unless permission Y", insert a 4th condition with `ASSIGNED_PERMISSIONS_PATH CONTAINS_NONE Y` and use `(AND (OR 1 2) (AND 3) (AND 4))`.

---

## ACCESS — Gated by Tag / Classification / Permission

Source: `conditionTagValidSteelthread`, `conditionClassificationValidClauseSteelthread`, `conditionAssignedPermPathValidSteelthread`

```xml
<?xml version="1.0" encoding="UTF-8"?>
<PolicyRuleDefinition xmlns="http://soap.sforce.com/2006/04/metadata">
    <action>Read</action>
    <category>ACCESS_POLICY_RULE_DEFINITION</category>
    <effect>Permit</effect>
    <label>Rule0</label>
    <policyRuleDefinitionSetName>TagSet1</policyRuleDefinitionSetName>
    <principalAuthenticationLevel>INTERNAL</principalAuthenticationLevel>
    <principalScopeType>ANY</principalScopeType>
    <resourceScopeType>ANY</resourceScopeType>
    <ruleConsumer>DATACLOUD</ruleConsumer>
    <transformPrecedence>0</transformPrecedence>
    <whenPolicyRuleDefinitionClauseConjunction>
        <conditions>
            <clause>WHEN</clause>
            <operator>CONTAINS_ANY</operator>
            <resourcePath>TAG</resourcePath>
            <policyRuleValueSet>
                <valueReference>CustomTagRef</valueReference>
                <valueReferenceType>CUSTOM_TAG</valueReferenceType>
            </policyRuleValueSet>
        </conditions>
        <conjunctionExpression>1</conjunctionExpression>
    </whenPolicyRuleDefinitionClauseConjunction>
</PolicyRuleDefinition>
```

Swap the inner condition for permission gating:
```xml
<conditions>
    <clause>WHEN</clause>
    <operator>CONTAINS_ANY</operator>
    <principalPath>ASSIGNED_PERMISSIONS_PATH</principalPath>
    <policyRuleValueSet>
        <valueReference>testCustomPermission1</valueReference>
        <valueReferenceType>CUSTOM_PERMISSION</valueReferenceType>
    </policyRuleValueSet>
</conditions>
```
