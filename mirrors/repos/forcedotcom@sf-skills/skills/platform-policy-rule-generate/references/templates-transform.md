# TRANSFORM Templates

The `LAST_N_CHARS_RESOURCE_TRANSFORM` shape is MDAPI persistence-validated in `references/examples/LastCharactersFieldMasking/`. Other transforms in this file are older fixture-only references.

---

## TRANSFORM — Field Masking with Permission + Classification Gates

Source: `conditionClassificationValidDataMaskingSteelthread`

```xml
<?xml version="1.0" encoding="UTF-8"?>
<PolicyRuleDefinition xmlns="http://soap.sforce.com/2006/04/metadata">
    <action>Read</action>
    <category>TRANSFORM_POLICY_RULE_DEFINITION</category>
    <effect>Transform</effect>
    <label>Rule0</label>
    <policyRuleDefinitionSetName>DataMasking1</policyRuleDefinitionSetName>
    <principalAuthenticationLevel>INTERNAL</principalAuthenticationLevel>
    <principalScopeType>ANY</principalScopeType>
    <resourceScopeType>FIELD</resourceScopeType>
    <resourceTransform>NULL_RESOURCE_TRANSFORM</resourceTransform>
    <ruleConsumer>DATACLOUD</ruleConsumer>
    <transformPrecedence>0</transformPrecedence>
    <whenPolicyRuleDefinitionClauseConjunction>
        <conditions>
            <clause>WHEN</clause>
            <operator>IS</operator>
            <resourcePath>ENTITYTYPE</resourcePath>
            <policyRuleValueSet>
                <valueText>FIELD</valueText>
            </policyRuleValueSet>
        </conditions>
        <conditions>
            <clause>WHEN</clause>
            <operator>CONTAINS_NONE</operator>
            <principalPath>ASSIGNED_PERMISSIONS_PATH</principalPath>
            <policyRuleValueSet>
                <valueReference>testCustomPermissionMasking</valueReference>
                <valueReferenceType>CUSTOM_PERMISSION</valueReferenceType>
            </policyRuleValueSet>
        </conditions>
        <conditions>
            <clause>WHEN</clause>
            <operator>CONTAINS_ANY</operator>
            <resourcePath>CLASSIFICATION</resourcePath>
            <policyRuleValueSet>
                <valueReference>DataGovernanceClassifications.DataCategorization.FieldUsage.Active</valueReference>
                <valueReferenceType>STANDARD_CLASSIFICATION</valueReferenceType>
            </policyRuleValueSet>
        </conditions>
        <conjunctionExpression>(AND 1 2 3)</conjunctionExpression>
    </whenPolicyRuleDefinitionClauseConjunction>
</PolicyRuleDefinition>
```

Validated `LAST_N_CHARS_RESOURCE_TRANSFORM` argument shape:
```xml
<resourceExpression>
    <transformExpression>
        <argument>
            <type>STRING</type>
            <value>12</value>
        </argument>
    </transformExpression>
    <type>ARGLIST</type>
    <version>1</version>
</resourceExpression>
<resourceTransform>LAST_N_CHARS_RESOURCE_TRANSFORM</resourceTransform>
```

Do not infer argument type or count for another transform.
