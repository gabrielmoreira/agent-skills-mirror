# UniProtKB `fields=` names

Pass a comma-separated list as `fields=` on `/uniprotkb/search`, `/uniprotkb/stream`, and `/uniprotkb/accessions`. Unknown names are **silently ignored**. Live catalog:

```
GET https://rest.uniprot.org/configure/uniprotkb/result-fields
```

## High-use columns

| Token | Label | Group |
|---|---|---|
| `accession` | Entry | Names & Taxonomy |
| `id` | Entry Name | Names & Taxonomy |
| `gene_names` | Gene Names | Names & Taxonomy |
| `gene_primary` | Gene Names (primary) | Names & Taxonomy |
| `organism_name` | Organism | Names & Taxonomy |
| `organism_id` | Organism (ID) | Names & Taxonomy |
| `protein_name` | Protein names | Names & Taxonomy |
| `reviewed` | Reviewed | Miscellaneous |
| `length` | Length | Sequences |
| `mass` | Mass | Sequences |
| `sequence` | Sequence | Sequences |
| `cc_function` | Function [CC] | Function |
| `ec` | EC number | Function |
| `go` | Gene Ontology (GO) | Gene Ontology |
| `go_id` | Gene Ontology IDs | Gene Ontology |
| `go_p` / `go_f` / `go_c` | GO process / function / component | Gene Ontology |
| `ft_domain` | Domain [FT] | Family & Domains |
| `xref_pdb` | PDB | 3D structure |
| `xref_alphafolddb` | AlphaFoldDB | 3D structure |

Comment blocks use `cc_*`. Sequence features use `ft_*`. Cross-references use `xref_*`.

## Example

```
https://rest.uniprot.org/uniprotkb/search?query=insulin&fields=accession,gene_names,organism_name,length,sequence&format=tsv
```

FASTA responses ignore `fields=` — the sequence is the body. Use TSV or JSON when selecting columns.

## Pitfalls

- Typos do not 400; count returned columns against the request list.
- `reviewed` is a search query field *and* a result column. Filtering still requires `reviewed:true` in `query=`.
- Prefer the configure endpoint over memorizing every `cc_*` / `ft_*` name; the set grows with UniProt releases.
