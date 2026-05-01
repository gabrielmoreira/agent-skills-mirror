---
type: skill
lifecycle: stable
inheritance: inheritable
name: temp-file-python-analysis
description: Inline Python in shell scripts has quoting issues:
tier: standard
applyTo: '**/*temp*,**/*file*,**/*python*'
currency: 2026-04-30
lastReviewed: 2026-04-30
---

# Temp File Python Analysis

## The Problem

Inline Python in shell scripts has quoting issues:

```bash
# Fails with quote escaping problems
python -c "import pandas as pd; df = pd.read_csv('data.csv'); print(df[df['name'] == 'John'])"

# Even worse with complex logic
python -c "
import json
with open('config.json') as f:
    data = json.load(f)
    for item in data['items']:
        if item['status'] == 'active':
            print(item['name'])
"
```

## The Solution

Write to `_tmp.py`, execute, delete:

```bash
# Write script
cat > _tmp.py << 'EOF'
import pandas as pd
df = pd.read_csv('data.csv')
result = df[df['name'] == 'John']
print(result.to_json(orient='records'))
EOF

# Execute
python _tmp.py

# Clean up
rm _tmp.py
```

## PowerShell Equivalent

```powershell
$script = @'
import pandas as pd
df = pd.read_csv('data.csv')
print(df.describe().to_string())
'@

$script | Out-File -FilePath "_tmp.py" -Encoding utf8
python _tmp.py
Remove-Item "_tmp.py"
```

## Benefits

| Approach | Quoting Issues | Debugging | Editor Support |
|----------|---------------|-----------|----------------|
| Inline `-c` | Many | Hard | None |
| Heredoc | Some | Medium | Limited |
| Temp file | None | Easy | Full |

## Patterns

### Quick Data Analysis

```bash
cat > _tmp.py << 'EOF'
import pandas as pd
import sys
df = pd.read_csv(sys.argv[1])
print(f"Rows: {len(df)}")
print(f"Columns: {list(df.columns)}")
print(df.dtypes)
EOF
python _tmp.py data.csv
rm _tmp.py
```

### JSON Transformation

```bash
cat > _tmp.py << 'EOF'
import json
with open('input.json') as f:
    data = json.load(f)
# Transform
result = [item for item in data if item.get('active')]
with open('output.json', 'w') as f:
    json.dump(result, f, indent=2)
EOF
python _tmp.py
rm _tmp.py
```

## When to Apply

- Any multi-line Python in shell context
- Complex string handling
- Data analysis one-offs
- JSON/CSV processing

## Tags

`data` `python` `shell` `analysis`
