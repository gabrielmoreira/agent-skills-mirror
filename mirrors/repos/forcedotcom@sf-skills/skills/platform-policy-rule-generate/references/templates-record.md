# RECORD Templates

These examples are distilled from retrieved policies. Use them to understand persisted structure, but generate only values published by the target release's MDAPI contract.

---

## RECORD — Basic RLS (record field = user attribute)

Source: `references/examples/PrincipalFieldMatchRLS/`

> **RLS MDAPI round-trip is fragile in real orgs.** Deploy/retrieve can fail with opaque gacks if a DMO field in `<valueDomain>` is not mapped in the org's data streams. Use read-only metadata inspection to verify the field mapping before generating XML; do not create or edit the rule in Policy Builder from this skill.

> `SCALAR_ATTRIBUTE` is a confirmed, deployable, Policy Builder-compatible principal path for record-field-to-principal-attribute comparisons, per DG UI source (this is how the builder itself authors the condition, not established by a per-shape round-trip). Use this template directly in normal author mode.

```xml
<?xml version="1.0" encoding="UTF-8"?>
<PolicyRuleDefinition xmlns="http://soap.sforce.com/2006/04/metadata">
    <action>Read</action>
    <category>RECORD_POLICY_RULE_DEFINITION</category>
    <effect>Permit</effect>
    <label>Rule 1</label>
    <policyRuleDefinitionSetName>EXACT_SET_NAME</policyRuleDefinitionSetName>
    <policyRuleResourceDomains>
        <resourceDomain>EXACT_DMO</resourceDomain>
    </policyRuleResourceDomains>
    <principalAuthenticationLevel>INTERNAL</principalAuthenticationLevel>
    <principalScopeType>ANY</principalScopeType>
    <resourceScopeType>RECORD</resourceScopeType>
    <ruleConsumer>DATACLOUD</ruleConsumer>
    <transformPrecedence>0</transformPrecedence>
    <whenPolicyRuleDefinitionClauseConjunction>
        <conditions>
            <clause>WHEN</clause>
            <operator>EQUALS</operator>
            <principalExpression>
                <soqlTarget>
                    <select>EXACT_USER_FIELD</select>
                </soqlTarget>
                <type>SOQLTARGETLISTEXPR</type>
                <version>1</version>
            </principalExpression>
            <resourcePath>RECORDFIELD</resourcePath>
            <valueDomain>EXACT_DMO:EXACT_FIELD</valueDomain>
            <valuePrincipalPath>SCALAR_ATTRIBUTE</valuePrincipalPath>
        </conditions>
        <conjunctionExpression>(AND 1)</conjunctionExpression>
    </whenPolicyRuleDefinitionClauseConjunction>
</PolicyRuleDefinition>
```

## RECORD — RLS via PROJECTION Join

Source: `references/examples/ExistsJoinRLS/`

```xml
<conditions>
    <clause>WHEN</clause>
    <operator>EXISTS</operator>
    <policyRuleDefinitionCondition>
        <clause>WHEN</clause>
        <operator>EQUALS</operator>
        <policyRuleValueSet>
            <valueText>${User.Email}</valueText>
        </policyRuleValueSet>
        <resourcePath>RECORDFIELD</resourcePath>
        <valueDomain>RESOURCE_DMO:RESOURCE_FIELD</valueDomain>
    </policyRuleDefinitionCondition>
    <resourceExpression>
        <projection>
            <join>
                <alias>JOIN_ALIAS</alias>
                <predicate>
                    <attribute>JOIN_DMO:JOIN_FIELD</attribute>
                    <comparator>EQUALS</comparator>
                    <on>
                        <field>RESOURCE_FIELD</field>
                        <resourceAlias>resource</resourceAlias>
                        <schema>RESOURCE_DMO</schema>
                    </on>
                </predicate>
                <schema>JOIN_DMO</schema>
            </join>
        </projection>
        <type>PROJECTION</type>
        <version>1</version>
    </resourceExpression>
    <resourcePath>EXPRESSION</resourcePath>
    <whereClauseConjunction>1</whereClauseConjunction>
</conditions>
```
