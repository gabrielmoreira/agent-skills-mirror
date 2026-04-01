## memory tools
use when durable recall or storage is useful
- `memory_load`: args `query`, optional `threshold`, `limit`, `filter`
- `memory_save`: args `text`, optional `area` and metadata kwargs
- `memory_delete`: arg `ids` comma-separated ids
- `memory_forget`: args `query`, optional `threshold`, `filter`
notes:
- `threshold` is similarity from `0` to `1`
- `filter` is a python expression over metadata
- verify destructive memory changes if accuracy matters
