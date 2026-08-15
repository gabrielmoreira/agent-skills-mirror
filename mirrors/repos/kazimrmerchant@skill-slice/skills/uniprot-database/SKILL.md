---
name: uniprot-database
description: "Queries rest.uniprot.org for UniProtKB search, FASTA/JSON/TSV retrieval, async ID mapping jobs, and Swiss-Prot versus TrEMBL filters. Use for accession lookup, gene or organism search, sequence pull, or Ensembl/RefSeq/PDB mapping. Do not use for SPARQL at sparql.uniprot.org or a multi-service bioservices client."
version: 1.0.1
license: Unknown
metadata:
  skill-author: K-Dense Inc.
risk: safe
source: community
scope: L
---

# UniProt Database

## Overview

UniProt is the world's leading comprehensive protein sequence and functional information resource. This skill provides direct HTTP/REST access to the UniProt REST API (`https://rest.uniprot.org`) for protein searches, sequence retrieval, ID mapping, and annotation access. For Python workflows that span multiple biological databases, consider `bioservices` (unified interface to 40+ services) instead — use this skill when you need direct HTTP/REST control or UniProt-specific features.

## When to Use

Use this skill when any of the following apply:

- Searching for protein entries by name, gene symbol, accession, or organism
- Retrieving protein sequences in FASTA, JSON, TSV, or other supported formats
- Mapping identifiers between UniProt and external databases (Ensembl, RefSeq, PDB, AlphaFoldDB, KEGG, GO, etc.)
- Accessing protein annotations including GO terms, domains, and functional descriptions
- Batch retrieving multiple protein entries efficiently
- Querying reviewed (Swiss-Prot) vs. unreviewed (TrEMBL) protein data
- Streaming large protein datasets that exceed pagination limits
- Building custom queries with field-specific search syntax

**Trigger keywords:** UniProt, protein search, FASTA retrieval, accession lookup, Swiss-Prot, TrEMBL, ID mapping, protein annotation, GO term, protein sequence, UniProtKB.

## Prerequisites

- **Network access** to `https://rest.uniprot.org` (no API key required for standard public queries)
- **Python 3.8+** if using the helper script (`scripts/uniprot_client.py`)
- **PowerShell** on Windows is the primary host shell. Use `curl.exe` (Windows built-in) or `Invoke-RestMethod` for HTTP calls from the command line
- Optional Python packages for advanced workflows: `unipressed` (modern typed client), `bioservices` (multi-service unified client)

## Procedure

### 1. Search for Proteins

Use the search endpoint with a structured query and desired format.

**Endpoint:**
```
https://rest.uniprot.org/uniprotkb/search?query={query}&format={format}
```

**Supported formats:** `json`, `tsv`, `xlsx`, `xml`, `fasta`, `rdf`, `txt`

**Common query patterns:**

```python
# Search by protein name
query = 'insulin AND organism_name:"Homo sapiens"'

# Search by gene name (reviewed only = Swiss-Prot)
query = "gene:BRCA1 AND reviewed:true"

# Search by accession
query = "accession:P12345"

# Search by sequence length range
query = "length:[100 TO 500]"

# Search by taxonomy ID (9606 = Human)
query = "taxonomy_id:9606"

# Search by GO term
query = "go:0005515"  # Protein binding
```

**PowerShell example (TSV output with selected fields):**

```powershell
$query = [uri]::EscapeDataString('insulin AND organism_name:"Homo sapiens"')
curl.exe -s "https://rest.uniprot.org/uniprotkb/search?query=$query&fields=accession,gene_names,organism_name,length,sequence&format=tsv"
```

**Boolean and field syntax:**

```
kinase AND organism_name:human
(diabetes OR insulin) AND reviewed:true
cancer NOT lung
gene:BRCA*
protein_name:kinase*
length:[100 TO 500]
mass:[50000 TO 100000]
annotation:(type:signal)
```

> **Load `references/query_syntax.md`** when you need comprehensive syntax documentation, advanced boolean/nested queries, or wildcard rules before constructing complex queries.

### 2. Retrieve a Single Protein Entry

Retrieve a specific protein by accession number.

**Accession formats:**
- Classic: `P12345`, `Q1AAA9`, `O15530` (6 chars: 1 letter + 5 alphanumeric)
- Extended: `A0A022YWF9` (10 chars for newer entries)

**Endpoint:**
```
https://rest.uniprot.org/uniprotkb/{accession}.{format}
```

**PowerShell example (FASTA):**

```powershell
curl.exe -s "https://rest.uniprot.org/uniprotkb/P12345.fasta"
```

### 3. Batch Retrieval and ID Mapping

Map protein identifiers between database systems in three steps.

**Step 1 — Submit mapping job:**

```powershell
$body = "ids=P12345,Q8N6T3,A0A022YWF9&from=UniProtKB_AC-ID&to=Ensembl"
curl.exe -s -X POST "https://rest.uniprot.org/idmapping/run" -d $body
```

Returns a JSON object with a `jobId`.

**Step 2 — Check job status:**

```powershell
curl.exe -s "https://rest.uniprot.org/idmapping/status/{jobId}"
```

**Step 3 — Retrieve results:**

```powershell
curl.exe -s "https://rest.uniprot.org/idmapping/results/{jobId}"
```

**Supported mapping databases include:** UniProtKB AC/ID, Gene names, Ensembl, RefSeq, EMBL, PDB, AlphaFoldDB, KEGG, GO terms, and many more.

> **Load `references/id_mapping_databases.md`** before constructing an ID mapping job to confirm the exact `from` and `to` database identifiers supported by the API.

**Limitations:**
- Maximum **100,000 IDs** per mapping job
- Results stored for **7 days** after job completion

### 4. Stream Large Result Sets

For queries that exceed pagination limits, use the stream endpoint to retrieve all matching results in a single response.

**Endpoint:**
```
https://rest.uniprot.org/uniprotkb/stream?query={query}&format={format}
```

**PowerShell example:**

```powershell
$query = [uri]::EscapeDataString('taxonomy_id:9606 AND reviewed:true')
curl.exe -s "https://rest.uniprot.org/uniprotkb/stream?query=$query&format=fasta" -o swissprot_human.fasta
```

### 5. Customize Retrieved Fields

Specify only the fields you need to reduce bandwidth and processing time.

**Common fields:**

| Field | Description |
|---|---|
| `accession` | UniProt accession number |
| `id` | Entry name |
| `gene_names` | Gene name(s) |
| `organism_name` | Organism |
| `protein_name` | Protein names |
| `sequence` | Amino acid sequence |
| `length` | Sequence length |
| `go_*` | Gene Ontology annotations |
| `cc_*` | Comment fields (function, interaction, etc.) |
| `ft_*` | Feature annotations (domains, sites, etc.) |

**Example with field selection:**
```
https://rest.uniprot.org/uniprotkb/search?query=insulin&fields=accession,gene_names,organism_name,length,sequence&format=tsv
```

> **Load `references/api_fields.md`** when you need the complete field list or are constructing a TSV/JSON query with non-standard fields.

### 6. Use the Python Helper Script

For programmatic access, use `scripts/uniprot_client.py` which implements:

- `search_proteins(query, format)` — Search UniProt with any query
- `get_protein(accession, format)` — Retrieve a single protein entry
- `map_ids(ids, from_db, to_db)` — Map between identifier types
- `batch_retrieve(accessions, format)` — Retrieve multiple entries
- `stream_results(query, format)` — Stream large result sets

> **Load `scripts/uniprot_client.py`** when the task requires repeated API calls, pagination handling, or integration into a Python pipeline. For one-off queries, use `curl.exe` or `Invoke-RestMethod` directly.

**Alternative Python packages:**
- **Unipressed** — Modern, typed Python client for the UniProt REST API
- **bioservices** — Comprehensive bioinformatics web services client (40+ services)

> **Load `references/api_examples.md`** when you need code examples in multiple languages (Python, curl, R) beyond the patterns shown here.

## Best Practices

1. **Prefer reviewed entries** — Filter with `reviewed:true` for Swiss-Prot (manually curated) entries when data quality matters
2. **Specify format explicitly** — FASTA for sequences, TSV for tabular data, JSON for programmatic parsing
3. **Use field selection** — Only request fields you need to reduce bandwidth and processing time
4. **Handle pagination or stream** — For large result sets, implement proper pagination or use the stream endpoint
5. **Cache results locally** — Store frequently accessed data to minimize repeated API calls
6. **Rate-limit your requests** — Be respectful of API resources; implement delays for large batch operations
7. **Check data quality** — TrEMBL entries are computational predictions; Swiss-Prot entries are manually reviewed

## Pitfalls

- **TrEMBL vs. Swiss-Prot confusion**: TrEMBL entries are computationally predicted and unreviewed. Always use `reviewed:true` when you need manually curated Swiss-Prot data. Do not assume all UniProtKB entries are experimentally validated.
- **URL encoding**: Queries containing spaces, quotes, or special characters must be URL-encoded. In PowerShell, use `[uri]::EscapeDataString()` before appending to the URL. Failure to encode will produce 400 errors or unexpected results.
- **ID mapping job limits**: Each mapping job accepts a maximum of **100,000 IDs**. Exceeding this silently truncates or rejects the job. Split large ID lists into batches.
- **ID mapping result expiry**: Results are stored for only **7 days**. Retrieve and persist results before they expire.
- **Pagination vs. stream**: The search endpoint paginates results (default 25 per page). If you expect more than a few hundred results and do not implement cursor-based pagination, use the `stream` endpoint instead.
- **Field name typos**: Invalid field names in the `fields` parameter are silently ignored by the API — you will get a response with fewer columns than expected and no error. Cross-check against `references/api_fields.md`.
- **Accession format ambiguity**: Classic accessions (6 chars) and extended accessions (10 chars) are both valid. Do not validate accession length strictly; use the API to confirm existence.
- **Rate limiting**: UniProt may throttle or block IPs making excessive rapid requests. Add delays (e.g., 0.5–1 second) between batch calls.

## Verification

Verify that the API is reachable and returning expected data:

```powershell
# 1. Check API connectivity — retrieve a known accession in FASTA
curl.exe -s "https://rest.uniprot.org/uniprotkb/P12345.fasta"
# Expected: FASTA header line starting with ">sp|P12345|..." followed by sequence lines

# 2. Verify search returns results
$query = [uri]::EscapeDataString('gene:BRCA1 AND reviewed:true')
curl.exe -s "https://rest.uniprot.org/uniprotkb/search?query=$query&format=tsv&fields=accession,id,gene_names&size=5"
# Expected: TSV with header row and at least one data row

# 3. Verify stream endpoint works
$query = [uri]::EscapeDataString('accession:P12345')
curl.exe -s "https://rest.uniprot.org/uniprotkb/stream?query=$query&format=fasta"
# Expected: Single FASTA entry for P12345

# 4. Verify ID mapping submission
curl.exe -s -X POST "https://rest.uniprot.org/idmapping/run" -d "ids=P12345&from=UniProtKB_AC-ID&to=Ensembl"
# Expected: JSON containing a "jobId" field
```

If any of the above returns an HTTP 4xx/5xx error or empty body, check network connectivity, URL encoding, and query syntax before proceeding.

## Resources

### scripts/
- `uniprot_client.py` — Python client with helper functions for search, retrieval, ID mapping, batch retrieval, and streaming

### references/
- `api_fields.md` — Complete list of available fields for customizing queries (load before constructing non-standard field selections)
- `id_mapping_databases.md` — Supported databases for ID mapping operations (load before submitting any ID mapping job)
- `query_syntax.md` — Comprehensive query syntax with advanced examples (load before constructing complex boolean/nested queries)
- `api_examples.md` — Code examples in multiple languages: Python, curl, R (load when you need language-specific patterns beyond this skill)

### External links
- **API Documentation**: https://www.uniprot.org/help/api
- **Interactive API Explorer**: https://www.uniprot.org/api-documentation
- **REST Tutorial**: https://www.uniprot.org/help/uniprot_rest_tutorial
- **Query Syntax Help**: https://www.uniprot.org/help/query-fields
- **SPARQL Endpoint**: https://sparql.uniprot.org/ (for advanced graph queries)

## Limitations

- Use this skill only when the task clearly matches the scope described above.
- Do not treat the output as a substitute for environment-specific validation, testing, or expert review.
- Stop and ask for clarification if required inputs, permissions, safety boundaries, or success criteria are missing.
