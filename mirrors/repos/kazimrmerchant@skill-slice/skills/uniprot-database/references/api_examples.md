# UniProt REST examples

Base URL: `https://rest.uniprot.org`. No API key for public UniProtKB reads. Send a `User-Agent`. Prefer `scripts/uniprot_client.py` for repeated calls.

## Search (TSV)

PowerShell:

```powershell
$query = [uri]::EscapeDataString('gene:BRCA1 AND reviewed:true')
curl.exe -s "https://rest.uniprot.org/uniprotkb/search?query=$query&format=tsv&fields=accession,id,gene_names&size=5"
```

Python (this skill's helper):

```python
from uniprot_client import search_proteins

rows = search_proteins(
    "gene:BRCA1 AND reviewed:true",
    format="tsv",
    fields="accession,id,gene_names",
    size=5,
)
print(rows.decode("utf-8"))
```

## Single FASTA

```powershell
curl.exe -s "https://rest.uniprot.org/uniprotkb/P12345.fasta"
```

```python
from uniprot_client import get_protein
print(get_protein("P12345", "fasta").decode("utf-8"))
```

## Batch accessions

```powershell
curl.exe -s "https://rest.uniprot.org/uniprotkb/accessions?accessions=P12345,P04637&format=fasta"
```

```python
from uniprot_client import batch_retrieve
print(batch_retrieve(["P12345", "P04637"], "fasta").decode("utf-8"))
```

## Stream

```powershell
$query = [uri]::EscapeDataString('accession:P12345')
curl.exe -s "https://rest.uniprot.org/uniprotkb/stream?query=$query&format=fasta"
```

```python
from uniprot_client import stream_results
print(stream_results("accession:P12345", "fasta").decode("utf-8"))
```

## ID mapping

```powershell
curl.exe -s -X POST "https://rest.uniprot.org/idmapping/run" -d "ids=P12345&from=UniProtKB_AC-ID&to=Ensembl"
# then GET /idmapping/status/{jobId} and GET /idmapping/results/{jobId}
```

```python
from uniprot_client import map_ids
print(map_ids(["P12345"], "UniProtKB_AC-ID", "Ensembl"))
```

## R (httr)

```r
library(httr)
url <- "https://rest.uniprot.org/uniprotkb/P12345.fasta"
resp <- GET(url, user_agent("uniprot-database-skill/1.0"))
stop_for_status(resp)
cat(content(resp, "text", encoding = "UTF-8"))
```

## CLI helper

From this skill folder (Python 3.8+ , stdlib only):

```powershell
python .\scripts\uniprot_client.py get P12345 --format fasta
python .\scripts\uniprot_client.py search "gene:BRCA1 AND reviewed:true" --format tsv --size 5
python .\scripts\uniprot_client.py map P12345 --from-db UniProtKB_AC-ID --to-db Ensembl
```
