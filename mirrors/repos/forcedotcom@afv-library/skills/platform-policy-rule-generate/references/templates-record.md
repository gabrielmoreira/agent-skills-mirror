# RECORD Templates

Each template is a verified shape from a passing test fixture. Copy, then change names/values.

---

## RECORD — Basic RLS (record field = user attribute)

Source: `conditionRLSValidSteelthread` (first condition), `conditionStandardIdRLSValidSteelthread`

> **RLS MDAPI round-trip is fragile in real orgs.** Deploy/retrieve can fail with opaque gacks if a DMO field in `<valueDomain>` is not mapped in the org's data streams. Build the rule in the UI first; use MDAPI templates as verification shapes, not first-try authoring. See §8.3 of policy.md.

```xml
<?xml version="1.0" encoding="UTF-8"?>
<PolicyRuleDefinition xmlns="http://soap.sforce.com/2006/04/metadata">
    <action>Read</action>
    <category>RECORD_POLICY_RULE_DEFINITION</category>
    <effect>Permit</effect>
    <label>Rule1</label>
    <policyRuleDefinitionSetName>StandardFieldSet3</policyRuleDefinitionSetName>
    <policyRuleResourceDomains>
        <resourceDomain>testDMO__dlm</resourceDomain>
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
            <resourcePath>RECORDFIELD</resourcePath>
            <valueDomain>testDMO__dlm:name__c</valueDomain>
            <valuePrincipalPath>USER_ID</valuePrincipalPath>
        </conditions>
        <conjunctionExpression>1</conjunctionExpression>
    </whenPolicyRuleDefinitionClauseConjunction>
</PolicyRuleDefinition>
```

For literal-value RLS (e.g. `record.field == 'X'`), use `<policyRuleValueSet><valueString>X</valueString></policyRuleValueSet>` instead of `<valuePrincipalPath>`.

---

## RECORD — RLS via PROJECTION Join

Source: `conditionRLSValidSteelthread` (second condition)

```xml
<conditions>
    <clause>WHEN</clause>
    <operator>EXISTS</operator>
    <resourcePath>EXPRESSION</resourcePath>
    <resourceExpression>
        <type>PROJECTION</type>
        <version>1</version>
        <projection>
            <join>
                <schema>testDMO__dlm</schema>
                <alias>test 1</alias>
                <predicate>
                    <comparator>EQUALS</comparator>
                    <attribute>testDMO__dlm:name__c</attribute>
                    <on>
                        <resourceAlias>resource</resourceAlias>
                        <schema>testDMO__dlm</schema>
                        <field>age__c</field>
                    </on>
                </predicate>
            </join>
        </projection>
    </resourceExpression>
</conditions>
```
