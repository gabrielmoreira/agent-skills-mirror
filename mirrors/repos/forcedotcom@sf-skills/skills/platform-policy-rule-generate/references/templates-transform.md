# TRANSFORM Templates

Each template is a verified shape from a passing test fixture. Copy, then change names/values.

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
                <valueString>{&quot;t&quot;:&quot;Text&quot;,&quot;v&quot;:&quot;FIELD&quot;}</valueString>
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

For parameterized masking (e.g. mask all but first 4 chars):
```xml
<resourceTransform>ALL_BUT_FIRST_N_CHARS_RESOURCE_TRANSFORM</resourceTransform>
<resourceExpression>
    <type>ARGLIST</type>
    <version>1</version>
    <transformExpression>
        <argument>
            <type>NUMBER</type>
            <value>4</value>
        </argument>
    </transformExpression>
</resourceExpression>
```
