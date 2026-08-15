# ID mapping databases

Names below are the **exact** `from` / `to` tokens for `POST https://rest.uniprot.org/idmapping/run`. They are case-sensitive. Refresh the live catalog before an unusual mapping:

```
GET https://rest.uniprot.org/configure/idmapping/fields
```

`UniProtKB_AC-ID` is a **from** database only. `UniProtKB` and `UniProtKB-Swiss-Prot` are **to** databases only. Mapping gene names (`Gene_Name`) to UniProtKB requires a taxon when the API asks for one.

## UniProt group

| Token | From | To |
|---|---|---|
| `UniProtKB_AC-ID` | yes | no |
| `UniProtKB` | no | yes |
| `UniProtKB-Swiss-Prot` | no | yes |
| `UniParc` | yes | yes |
| `UniRef50` / `UniRef90` / `UniRef100` | yes | yes |
| `Gene_Name` | yes | yes |
| `CRC64` | yes | yes |

## Sequence and structure

| Token | Typical use |
|---|---|
| `RefSeq_Protein` | NCBI protein accessions |
| `RefSeq_Nucleotide` | NCBI nucleotide |
| `EMBL-GenBank-DDBJ` | nucleotide entries |
| `EMBL-GenBank-DDBJ_CDS` | CDS |
| `PDB` | 3D structures |
| `CCDS` | consensus CDS |
| `PIR` | PIR identifiers |

## Genome annotation and pathways

| Token | Typical use |
|---|---|
| `Ensembl` | gene |
| `Ensembl_Protein` / `Ensembl_Transcript` | protein / transcript |
| `Ensembl_Genomes` | non-vertebrate Ensembl |
| `GeneID` | NCBI Gene |
| `KEGG` | KEGG gene |
| `HGNC` | human gene names |
| `MGI` / `RGD` / `SGD` / `FlyBase` / `WormBase` / `ZFIN` | model organisms |
| `Reactome` / `BioCyc` | pathways |
| `ChEMBL` / `DrugBank` | chemistry |

AlphaFold and GO are UniProtKB **result fields** (`xref_alphafolddb`, `go`), not ID-mapping `to` tokens. Pull those via search/retrieve with `fields=`, not via `/idmapping`.

## Job contract

1. `POST /idmapping/run` with `from`, `to`, `ids` (comma-separated, max **100,000**).
2. Poll `GET /idmapping/status/{jobId}` until `jobStatus` is no longer `RUNNING`.
3. `GET /idmapping/results/{jobId}` — results expire after **7 days**.

One source ID may map to many targets; check `failedIds` for misses. Split oversized lists into multiple jobs.

## Confirm tokens before submit

```powershell
curl.exe -s "https://rest.uniprot.org/configure/idmapping/fields"
```
