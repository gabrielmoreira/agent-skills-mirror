---
name: data-format-conversion-post-format
api: Data Format Conversion
method: POST
path: /v1/technology/format
base_url: https://api.requiems.xyz
description: Convert content from one structured data format to another. Supported formats: json, yaml, csv, xml, toml.
---

## Endpoint

**POST https://api.requiems.xyz/v1/technology/format**

## Convert Format

Convert content from one structured data format to another. Supported formats:
json, yaml, csv, xml, toml.

## Parameters

| Name      | Type   | Required | Location | Description                                                          |
| --------- | ------ | -------- | -------- | -------------------------------------------------------------------- |
| `from`    | string | yes      | body     | Source format. One of: json, yaml, csv, xml, toml                    |
| `to`      | string | yes      | body     | Target format. One of: json, yaml, csv, xml, toml                    |
| `content` | string | yes      | body     | The content to convert, serialized as a string in the source format. |

## Request Example

```json
{
  "from": "json",
  "to": "yaml",
  "content": "{\"name\": \"Alice\", \"age\": 30}"
}
```

## Response Example

```json
{
  "data": {
    "result": "age: 30\nname: Alice\n"
  },
  "metadata": {
    "timestamp": "2026-01-01T00:00:00Z"
  }
}
```

## Response Fields

| Field    | Type   | Description                                            |
| -------- | ------ | ------------------------------------------------------ |
| `result` | string | The converted content serialized in the target format. |

## Errors

- `422` **validation_failed** — One of from, to, or content is missing, or
  from/to is not one of the supported format values.
- `422` **invalid_json** — The content field is not valid JSON (when from is
  json).
- `422` **invalid_yaml** — The content field is not valid YAML (when from is
  yaml).
- `422` **invalid_csv** — The content field is not valid CSV, or a row has more
  columns than the header (when from is csv).
- `422` **invalid_xml** — The content field is not valid XML (when from is xml).
- `422` **invalid_toml** — The content field is not valid TOML (when from is
  toml).
- `422` **conversion_error** — The data structure is incompatible with the
  target format (e.g. converting a JSON array to TOML, which requires a
  top-level object).
- `413` **content_too_large** — The content field exceeds the 512 KB limit.
