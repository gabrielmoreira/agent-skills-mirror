{{if secrets}}
## secret aliases
use exact alias form `§§secret(name)`; real values are injected automatically
only use provided aliases; do not expose or invent secret values
values may contain special characters, so quote or escape them correctly in shell or code
comments help explain each secret's purpose
{{secrets}}
{{endif}}
{{if vars}}
## variables
these are plain non-sensitive values; use them directly without `§§secret(...)`
{{vars}}
{{endif}}
