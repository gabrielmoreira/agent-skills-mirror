# Widget Bundle Validation Checks

Report each check individually as `pass` or `fail (<reason>)`.

- **`schema-parses`** — `<pkgDir>/uiWidgets/<widgetName>/schema.json` parses as JSON.
- **`schema-root-keys`** — root has `title` (string), `type: "object"`, and `properties.attributes` (object) — where `properties.attributes` carries `lightning:type: "lightning__objectType"` and a nested `properties` map. No `unevaluatedProperties: false`.
- **`schema-leaf-types`** — every leaf under `properties.attributes.properties` carries a `lightning:type`. Singular nested inner-class fields carry `lightning:type` set to the inner Apex class reference (`@apexClassType/<namespace>__<OuterClass>$<InnerClass>`); the nested shape is not redeclared. `List<InnerClass>` fields carry `lightning:type: "lightning__listType"` with `items.lightning:type` set to the inner Apex class reference (`@apexClassType/<namespace>__<OuterClass>$<InnerClass>`), not a redeclared field map — see `references/schema-from-lightning-type.md`. **When the list has no Apex-backed type** (schema inferred from the prompt), `items.lightning:type: "lightning__objectType"` MUST carry an inline nested `properties` map for every item field the body binds via `{!$item.X}`.
- **`bindings-resolve`** — every `{!$attrs.X}` (or `{!$attrs.<outerField>.<innerField>}` for nested objects) in `<widgetName>.json` resolves to a property under `schema.json` `properties.attributes.properties`, and every `{!$item.X}` resolves to a `forItem` loop variable defined upstream. This applies to `$attrs`/`$item` references **inside formula expressions** too.
- **`formulas-supported`** — every function name used inside a `{!...}` expression appears in the *Supported functions* list in `references/widget-formulas.md`.
- **`body-envelope`** — `<widgetName>.json` root has `type: "lightning__agentforceWidget"` and a `contentBody` object whose `widgetBody` carries the UEM tree rooted at `tile/widget`. No node in the tree — root or non-root — carries a `type` key.
- **`metaxml-wellformed`** — `<widgetName>.uiwidget-meta.xml` parses as well-formed XML.
- **`metaxml-elements`** — `<widgetName>.uiwidget-meta.xml` has root `<UiWidgetBundle>` and contains `<masterLabel>` (non-empty), `<description>` (non-empty), and `<widgetType>JSON</widgetType>`.
- **`files-present`** — all three files exist at the resolved `<pkgDir>/uiWidgets/<widgetName>/` path.
- **`button-actions-present`** — every `tile/button` in `<widgetName>.json` has an `actions.click` action node whose `definition` is `action/openLink` or `action/sendMessage`.
- **`labels-valid`** — if the user did not ask for localization, `<widgetName>.json` contains no `$Label` (report `pass (not requested)`). Otherwise every `$Label` follows the rules in `references/widget-labels.md` and appears in the step 10 report.
