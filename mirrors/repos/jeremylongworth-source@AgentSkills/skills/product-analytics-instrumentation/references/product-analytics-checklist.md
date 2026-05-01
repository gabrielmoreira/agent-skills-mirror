# Product Analytics Instrumentation Checklist

## Measurement Design

- Product decision and metric question are explicit.
- Journey stages and key user actions are mapped.
- North-star, activation, funnel, retention, and guardrail metrics are defined.
- Events are tied to analysis use cases.

## Taxonomy

- Event names are consistent and readable.
- Required and optional properties are documented.
- Identity rules distinguish anonymous, user, account, device, session, and group identifiers.
- Environment, source, version, and timestamp handling are clear.
- Deprecated events have replacement or removal guidance.

## Privacy And Governance

- PII and sensitive data are excluded or reviewed.
- Consent and regional privacy requirements are considered.
- Ownership and approval process for new events are defined.
- Data retention and deletion needs are considered.

## QA

- Events fire once, at the correct moment, with expected properties.
- Test users and production users are distinguishable.
- Client and server events do not double-count unless designed to.
- Dashboards are reconciled against source systems where possible.
- Data quality checks catch missing properties, schema drift, and unexpected volume changes.
