# Condition Model

Each `<conditions>` element is a comparison:

```text
condition = left operand + operator + right operand
```

The XML does not contain literal `<left>` or `<right>` elements. The operand type determines which elements represent each side.

| Logical part | XML representation |
|---|---|
| Resource left operand | `resourcePath`, optionally `resourceExpression` |
| Principal left operand | `principalPath`, optionally `principalExpression` |
| Context left operand | `contextPath` |
| Comparison | `operator` |
| Right reference or literal | `policyRuleValueSet` |
| Right record/domain value | `valueDomain` |
| Right principal-derived value | `valuePrincipalPath` |
| Clause polarity | `clause` inside the matching WHEN/UNLESS wrapper |

Every condition must be constructed in this order:

1. Select the wrapper: `whenPolicyRuleDefinitionClauseConjunction` or `unlessPolicyRuleDefinitionClauseConjunction`.
2. Set `<clause>` to `WHEN` or `UNLESS` to match the wrapper.
3. Select the left path. Most conditions use one of `resourcePath`, `principalPath`, or `contextPath`; a record-field-to-principal comparison uses both `resourcePath=RECORDFIELD` and a principal expression.
4. Add a `resourceExpression` or `principalExpression` if the selected left operand requires an expression.
5. Select the operator valid for that operand.
6. Add the right-side representation required by the shape. Most conditions use one of `policyRuleValueSet`, `valueDomain`, or `valuePrincipalPath`; a record-field-to-principal comparison uses `valueDomain` and `valuePrincipalPath` together.

Example: principal has a permission.

```xml
<conditions>
    <clause>WHEN</clause>
    <operator>CONTAINS_ANY</operator>
    <policyRuleValueSet>
        <valueReference>cust_perm1</valueReference>
        <valueReferenceType>CUSTOM_PERMISSION</valueReferenceType>
    </policyRuleValueSet>
    <principalPath>ASSIGNED_PERMISSIONS_PATH</principalPath>
</conditions>
```

This means: left operand `principal.assignedPermissions`, operator `CONTAINS_ANY`, right operand custom permission `cust_perm1`.

For FLS and masking, condition 1 must be `resourcePath=ENTITYTYPE`, `operator=IS`, and `valueText=FIELD`. OLS instead begins with two entity-type conditions for `OBJECT` and `FIELD`, grouped with `OR`.
