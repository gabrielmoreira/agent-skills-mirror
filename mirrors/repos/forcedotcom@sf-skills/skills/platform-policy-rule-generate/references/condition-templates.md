# Condition Templates

Use these templates only after resolving the reference values in the target org.

## Entity Type

```xml
<conditions>
    <clause>WHEN</clause>
    <operator>IS</operator>
    <policyRuleValueSet>
        <valueText>OBJECT</valueText>
    </policyRuleValueSet>
    <resourcePath>ENTITYTYPE</resourcePath>
</conditions>
```

For a UI-renderable object-level (OLS/GOVERNANCE `TupleRead`) policy, both `OBJECT` and `FIELD` entity-type conditions are required and must be OR'd together — see the OLS section in `policy-shapes.md` and the entity-type discriminator rule in `ui-compatibility.md`. Omitting the pair still deploys and works at runtime, but crashes the Policy Builder on open (UI-only failure, not a persistence failure). FLS/masking policies use `FIELD` only — do not add an `OBJECT` condition for those.

## Standard Tag

```xml
<conditions>
    <clause>WHEN</clause>
    <operator>CONTAINS_ANY</operator>
    <policyRuleValueSet>
        <valueReference>EXACT.STANDARD.TAG.NAME</valueReference>
        <valueReferenceType>STANDARD_TAG</valueReferenceType>
    </policyRuleValueSet>
    <resourcePath>TAG</resourcePath>
</conditions>
```

## Standard Classification

```xml
<conditions>
    <clause>WHEN</clause>
    <operator>CONTAINS_ANY</operator>
    <policyRuleValueSet>
        <valueReference>EXACT.STANDARD.CLASSIFICATION.NAME</valueReference>
        <valueReferenceType>STANDARD_CLASSIFICATION</valueReferenceType>
    </policyRuleValueSet>
    <resourcePath>CLASSIFICATION</resourcePath>
</conditions>
```

## Custom Permission

```xml
<conditions>
    <clause>WHEN</clause>
    <operator>CONTAINS_ANY</operator>
    <policyRuleValueSet>
        <valueReference>EXACT_CUSTOM_PERMISSION_DEVELOPER_NAME</valueReference>
        <valueReferenceType>CUSTOM_PERMISSION</valueReferenceType>
    </policyRuleValueSet>
    <principalPath>ASSIGNED_PERMISSIONS_PATH</principalPath>
</conditions>
```

## Principal Scalar Attribute

Use the complete `principalExpression` template in `principal-expression.md`. Its right-side comparison is normally `<valueText>...</valueText>`.

For FLS or masking, instantiate the Entity Type template once with `FIELD`. For OLS, instantiate it twice, first with `OBJECT` and then with `FIELD`.

## RLS Record Field Equals Principal Attribute

Use this template in normal author mode whenever the request compares a resource field to the requesting principal's own attribute (for example, "records where `OwnerDepartment` matches the user's `Department`"). `SCALAR_ATTRIBUTE` is a confirmed, deployable, Policy Builder-compatible principal path for this comparison, per DG UI source (this is how the builder itself authors the condition, not established by a per-shape round-trip).

```xml
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
```

This shape has a resource path, a principal expression, a value domain, and a value principal path. Resolve all three API names in the target org before generating XML.
