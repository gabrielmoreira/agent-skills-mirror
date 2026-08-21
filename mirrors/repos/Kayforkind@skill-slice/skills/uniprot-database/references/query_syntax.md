# UniProtKB query syntax

Build the `query=` string for `https://rest.uniprot.org/uniprotkb/search` (and `stream`). Official field list: https://www.uniprot.org/help/query-fields. URL-encode the whole query before appending it (`[uri]::EscapeDataString()` in PowerShell, `urllib.parse.urlencode` in the helper script).

## Boolean operators

| Operator | Meaning | Example |
|---|---|---|
| `AND` | both sides match | `kinase AND reviewed:true` |
| `OR` | either side | `(diabetes OR insulin) AND reviewed:true` |
| `NOT` | exclude | `cancer NOT lung` |
| parentheses | grouping | `(gene:BRCA1 OR gene:BRCA2) AND organism_id:9606` |

Operators are uppercase. Bare words search the default text index.

## Field queries

| Field | Example |
|---|---|
| `accession` | `accession:P12345` |
| `gene` | `gene:BRCA1` |
| `gene` wildcard | `gene:BRCA*` |
| `protein_name` | `protein_name:kinase*` |
| `organism_name` | `organism_name:"Homo sapiens"` |
| `taxonomy_id` / `organism_id` | `taxonomy_id:9606` |
| `reviewed` | `reviewed:true` (Swiss-Prot) or `reviewed:false` (TrEMBL) |
| `length` range | `length:[100 TO 500]` |
| `mass` range | `mass:[50000 TO 100000]` |
| `go` | `go:0005515` |
| `ec` | `ec:1.13.-.-` |
| `annotation` | `annotation:(type:signal)` |

Quote multi-word values. Ranges use `[low TO high]` with `TO` in uppercase.

## Encoding

Queries with spaces, quotes, or brackets must be encoded. Unencoded quotes produce HTTP 400 or a silently wrong parse.

```powershell
$query = [uri]::EscapeDataString('gene:BRCA1 AND reviewed:true')
curl.exe -s "https://rest.uniprot.org/uniprotkb/search?query=$query&format=tsv&fields=accession,id,gene_names&size=5"
```

## Pitfalls

- `reviewed:true` is Swiss-Prot (curated). Omitting it mixes in TrEMBL predictions.
- Invalid field names in `fields=` are dropped with no error — the TSV simply has fewer columns. Cross-check `references/api_fields.md`.
- Default search page size is 25. Use cursor pagination or `uniprotkb/stream` for large result sets.
- This skill talks to REST, not SPARQL. Graph queries belong at `https://sparql.uniprot.org/`.
