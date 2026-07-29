## Distinct exception conditions

Emit one `<exception>` element for each distinct failure condition, even when
multiple conditions raise the same exception type:

```xml
<exception cref="ArgumentException">
When <paramref name="x"/> and <paramref name="y"/> are negative.
</exception>
<exception cref="ArgumentException">
When <paramref name="z"/> is <see langword="null"/> or empty.
</exception>
```

Do not merge these entries merely because their `cref` values match. Keep each
condition independently discoverable in generated reference documentation.
