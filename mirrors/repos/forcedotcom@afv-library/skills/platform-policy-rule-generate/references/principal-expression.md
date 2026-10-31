# Principal Expressions

Retrieved server evidence can contain a principal attribute selected from the principal record using `SOQLTARGETLISTEXPR`:

```xml
<conditions>
    <clause>WHEN</clause>
    <operator>EQUALS</operator>
    <policyRuleValueSet>
        <valueText>EXPECTED_VALUE</valueText>
    </policyRuleValueSet>
    <principalExpression>
        <soqlTarget>
            <select>PrincipalField</select>
        </soqlTarget>
        <type>SOQLTARGETLISTEXPR</type>
        <version>1</version>
    </principalExpression>
    <principalPath>SCALAR_ATTRIBUTE</principalPath>
</conditions>
```

Construction:

1. Resolve the principal field name from the target org.
2. Put that field in `<soqlTarget><select>`.
3. Use `SOQLTARGETLISTEXPR`, version `1`.
4. Put the comparison value in the right-side `policyRuleValueSet`.
5. Use the operator appropriate to the value.

`SCALAR_ATTRIBUTE` paired with `SOQLTARGETLISTEXPR` is the normal-author-mode mechanism for a principal scalar-attribute comparison (for example, `Department`, `Title`, `Division`). It is not in the shorter enum table published for other principal paths, but it is a confirmed, deployable, Policy Builder-compatible construct per DG UI source: it is how the Data Governance UI itself creates user-attribute conditions (not established by a per-shape round-trip), which is why it appears throughout retrieved API 69.0 evidence for OLS, FLS, masking, and RLS. Generate it directly in normal author mode — resolve the requested attribute against the target org's supported-attribute table in `consumer-datacloud-ui.md` and use the exact field name in `<soqlTarget><select>`. Do not replace it with `ASSIGNED_PERMISSIONS_PATH`; permission membership and scalar principal attributes are different operands.
