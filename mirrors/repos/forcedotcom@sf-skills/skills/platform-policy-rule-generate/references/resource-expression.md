# Resource Expressions

Use `resourceExpression` when the resource-side operand is computed from a projection instead of a direct path. The condition must use `<resourcePath>EXPRESSION</resourcePath>`.

A transform argument list is different: it is a top-level `resourceExpression` on the rule, not inside a condition. Use `ARGLIST` exactly as documented in `policy-shapes.md` and the retrieved masking example.

The validated RLS join shape is:

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

For a join, define an `<alias>`, a `<schema>`, and a `<predicate>`. `<attribute>` belongs to the joined schema; `<on>` identifies the evaluated resource schema and field. Verify that join keys have compatible types. `whereClauseConjunction` numbers the nested `policyRuleDefinitionCondition` elements from `1`; it does not refer to top-level rule conditions.

Do not invent projection structure or substitute a different operator. Start from a retrieved, deployed example for the same relationship shape and change only resolved schema, field, and alias values while preserving which side is joined and which side is the evaluated resource.
