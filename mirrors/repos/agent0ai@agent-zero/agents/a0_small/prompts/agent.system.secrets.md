{{if secrets}}
## secret aliases
use exact alias form `§§secret(name)`; real values are injected automatically
{{secrets}}
{{endif}}
{{if vars}}
## variables
these are plain non-sensitive values; use them directly without `§§secret(...)`
{{vars}}
{{endif}}
