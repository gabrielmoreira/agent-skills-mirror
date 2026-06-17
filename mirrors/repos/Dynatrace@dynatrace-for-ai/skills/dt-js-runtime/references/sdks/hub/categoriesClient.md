# `categoriesClient`

Browse Hub categories. Requires scope `hub:catalog:read`. Import:

```ts
import { categoriesClient } from "@dynatrace-sdk/client-hub";
```

| Method | Returns | Purpose |
|---|---|---|
| `getCategories()` | `Categories` | List Hub categories, including the IDs of associated items and their content blocks (if any). |

## Example

```ts
import { categoriesClient } from "@dynatrace-sdk/client-hub";

const categories = await categoriesClient.getCategories();
```
