---
name: pubchem-database
version: 1.1.1
description: "Queries PubChem via PUG-REST or PubChemPy: name/CID/SMILES/InChI search, properties, similarity/substructure, bioactivity. Use for public compound lookups. Not for proprietary chemistry (use local RDKit), biomacromolecules (PDB), quantum jobs (Gaussian/ORCA), or UniProt proteins (uniprot-database). Honor NCBI ≤5 req/s and X-Throttling-Control."
risk: safe
source: openrouter-deepsearch
date_added: 2026-06-16
---

## Overview

PubChem is the world's largest freely available chemical database (110M+ compounds, 270M+ bioactivities), maintained by NCBI. It requires no license or API key and is reachable programmatically. Use it to search chemical structures by name, CID, SMILES, or InChI; retrieve precomputed molecular properties; run similarity and substructure searches; pull bioactivity data; and convert between identifier formats.

Two access layers exist:
- **PubChemPy (high-level):** Python wrapper that builds URLs, handles asynchronous polling for structure searches, and parses responses into `Compound` objects. Prefer for everyday lookups.
- **PUG-REST via `requests` (low-level):** Direct HTTP calls. Use when you need an endpoint PubChemPy does not wrap (e.g. `assaysummary`, PUG-View annotations) or precise control over timeouts/retries.

## When to Use

Use this skill when you need **public, authoritative chemical data without a licensing barrier** and want it from code rather than a web UI. Concretely:

- Searching compounds by name, structure (SMILES/InChI), or molecular formula — PubChem resolves all to a single canonical CID.
- Retrieving molecular properties (MW, LogP, TPSA, hydrogen-bonding descriptors) — precomputed, no local cheminformatics toolkit needed.
- Performing similarity searches for scaffold hopping and lead expansion.
- Conducting substructure searches for specific chemical motifs / pharmacophore screening.
- Accessing bioactivity data from screening assays.
- Converting between identifier formats (CID, SMILES, InChI, InChIKey) — one fetch yields every format.
- Batch processing multiple compounds for drug-likeness screening or property analysis.

**Do NOT use when:**
- **Proprietary/sensitive chemistry:** Every query travels to NCBI's public servers and can be logged. Use an in-house database or local RDKit instead.
- **Real-time or very high-throughput pipelines:** The public API is rate-limited (5 req/s, 400 req/min, 300 s/min running time). Mirror locally or license a bulk download.
- **Very large molecules (biomacromolecules):** Size ceilings cause failures or partial data. Use the PDB instead.
- **Quantum-mechanical calculations or specialized simulations:** PubChem stores precomputed descriptors, not a compute engine. Use Gaussian, ORCA, or Schrödinger.

## Prerequisites

Install the required Python packages:

```powershell
pip install pubchempy requests pandas
```

Verify imports:

```powershell
python -c "import pubchempy, requests, pandas"
```

**Rate limits (HARD RULE):** NCBI asks that any user or application stay at or below **5 requests/second** on PUG-REST ([usage policy](https://pubchem.ncbi.nlm.nih.gov/docs/pug-rest)). Dynamic throttling may still return HTTP 503 (`PUGREST.ServerBusy`). Keep ≥0.2s spacing in batch loops, honor `X-Throttling-Control` / `Retry-After` when present, and use bulk download instead of hammering REST.

**Reference files:** Load `references/api_reference.md` when you need the complete property list, full endpoint catalog, or the raw asynchronous request/poll workflow details.

**Scripts:** Use `scripts/compound_search.py` for name/CID/SMILES lookups and `scripts/bioactivity_query.py` for assay data retrieval. These are the verified entry points for the two most common workflows.

## Procedure

### 1. Chemical Structure Search

Use a wrapper that validates inputs and collapses PubChemPy's dual failure modes (raises errors AND returns empty lists) into one predictable function:

```python
from typing import List
import pubchempy as pcp
from pubchempy import Compound, PubChemPyError

def search_compounds(identifier: str, namespace: str) -> List[Compound]:
    valid_namespaces = {"name", "smiles", "inchi", "cid", "formula"}
    if not isinstance(identifier, str) or not identifier.strip():
        raise ValueError("identifier must be a non-empty string")
    if namespace not in valid_namespaces:
        raise ValueError(f"namespace must be one of {sorted(valid_namespaces)}, got {namespace!r}")
    try:
        return pcp.get_compounds(identifier.strip(), namespace)
    except PubChemPyError as exc:
        raise RuntimeError(f"PubChem lookup failed for {identifier!r} ({namespace}): {exc}") from exc
```

**By name** (one name can map to several records — always treat result as a list):

```python
aspirin_hits = search_compounds("aspirin", "name")
aspirin = aspirin_hits[0]
```

**By CID** (most reliable — exact primary key, skips fuzzy resolution):

```python
aspirin_by_cid = pcp.Compound.from_cid(2244)
```

**By SMILES:**

```python
hits = search_compounds("CC(=O)OC1=CC=CC=C1C(=O)O", "smiles")
```

**By InChI** (pass the COMPLETE string — truncated InChI resolves to a different or no structure):

```python
inchi = "InChI=1S/C9H8O4/c1-6(10)13-8-5-3-2-4-7(8)9(11)12/h2-5H,1H3,(H,11,12)"
hits = search_compounds(inchi, "inchi")
```

**By molecular formula** (returns every match — pair with a downstream filter):

```python
formula_hits = search_compounds("C9H8O4", "formula")
print(f"{len(formula_hits)} compounds share the formula C9H8O4")
```

### 2. Property Retrieval

**Whole-record access via `Compound` object** — every accessor is `Optional` because PubChem does not compute every descriptor for every record. Guard for `None` to prevent `TypeError`:

```python
import pubchempy as pcp
from pubchempy import Compound, PubChemPyError
from typing import List, Optional

def get_first_compound(name: str) -> Compound:
    if not isinstance(name, str) or not name.strip():
        raise ValueError("name must be a non-empty string")
    try:
        matches = pcp.get_compounds(name.strip(), "name")
    except PubChemPyError as exc:
        raise RuntimeError(f"PubChem lookup failed for {name!r}: {exc}") from exc
    if not matches:
        raise LookupError(f"No compound found for {name!r}")
    return matches[0]

caffeine = get_first_compound("caffeine")
mw = caffeine.molecular_weight       # Optional[float]
xlogp = caffeine.xlogp                # Optional[float]
tpsa = caffeine.tpsa                  # Optional[float]
smiles = caffeine.canonical_smiles    # Optional[str]
```

**Selected properties via `get_properties`** — request only the fields you need. This transfers a fraction of the bytes and keeps you under the rate limit:

```python
from typing import Dict, List, Union
import pubchempy as pcp
from pubchempy import PubChemPyError

PropertyValue = Union[str, int, float]
PropertyRecord = Dict[str, PropertyValue]

def get_selected_properties(identifier: str, namespace: str, properties: List[str]) -> List[PropertyRecord]:
    if not isinstance(identifier, str) or not identifier.strip():
        raise ValueError("identifier must be a non-empty string")
    if not properties:
        raise ValueError("properties must contain at least one property name")
    try:
        return pcp.get_properties(properties, identifier.strip(), namespace)
    except PubChemPyError as exc:
        raise RuntimeError(f"Property lookup failed for {identifier!r}: {exc}") from exc

records = get_selected_properties("aspirin", "name",
    ["MolecularFormula", "MolecularWeight", "CanonicalSMILES", "XLogP"])
```

**Available properties:** `MolecularFormula`, `MolecularWeight`, `CanonicalSMILES`, `IsomericSMILES`, `InChI`, `InChIKey`, `IUPACName`, `XLogP`, `TPSA`, `HBondDonorCount`, `HBondAcceptorCount`, `RotatableBondCount`, `Complexity`, `Charge`, and more. Load `references/api_reference.md` for the complete list.

**Batch property retrieval** — isolate each lookup so one bad name does not abort the run:

```python
import pandas as pd
import pubchempy as pcp
from pubchempy import PubChemPyError
from typing import Dict, List, Union

PropertyValue = Union[str, int, float]
PropertyRecord = Dict[str, PropertyValue]

def batch_properties(names: List[str], properties: List[str]) -> pd.DataFrame:
    if not names:
        raise ValueError("names must contain at least one compound name")
    if not properties:
        raise ValueError("properties must contain at least one property name")
    rows = []
    failures = []
    for name in names:
        if not name.strip():
            failures.append(repr(name))
            continue
        try:
            rows.extend(pcp.get_properties(properties, name.strip(), "name"))
        except PubChemPyError as exc:
            failures.append(f"{name} ({exc})")
    if failures:
        print(f"Skipped {len(failures)} compound(s): {failures}")
    return pd.DataFrame(rows)

df = batch_properties(["aspirin", "ibuprofen", "paracetamol"],
    ["MolecularFormula", "MolecularWeight", "XLogP"])
```

### 3. Similarity Search

**HARD RULE:** PubChem expresses similarity threshold as an integer percentage in `[0, 100]`. Passing `0.85` (a common mistake) is interpreted as "0% similar" and floods you with the entire database. Always validate up front.

```python
from typing import List
import pubchempy as pcp
from pubchempy import Compound, PubChemPyError

def similarity_search(smiles: str, threshold: int = 90, max_records: int = 50) -> List[Compound]:
    if not isinstance(smiles, str) or not smiles.strip():
        raise ValueError("smiles must be a non-empty string")
    if not isinstance(threshold, int) or not 0 <= threshold <= 100:
        raise ValueError(f"threshold must be an integer in [0, 100], got {threshold!r}")
    if max_records <= 0:
        raise ValueError(f"max_records must be positive, got {max_records}")
    try:
        return pcp.get_compounds(smiles.strip(), "smiles",
            searchtype="similarity", Threshold=threshold, MaxRecords=max_records)
    except PubChemPyError as exc:
        raise RuntimeError(f"Similarity search failed: {exc}") from exc

# Get query SMILES first
query = pcp.get_compounds("gefitinib", "name")
query_smiles = query[0].canonical_smiles or ""
similar = similarity_search(query_smiles, threshold=85, max_records=50)
for c in similar[:10]:
    print(f"CID {c.cid}: {c.iupac_name or 'N/A'} | MW: {c.molecular_weight or 'N/A'}")
```

**Note:** Similarity searches are asynchronous and may take 15–30 seconds. PubChemPy handles the submit/poll/retrieve pattern automatically.

### 4. Substructure Search

**HARD RULE:** Always cap `max_records`. A common fragment like benzene matches millions of records; without a ceiling the call can exceed PubChem's ~30-second asynchronous window and time out.

```python
from typing import List
import pubchempy as pcp
from pubchempy import Compound, PubChemPyError

def substructure_search(smiles: str, max_records: int = 100) -> List[Compound]:
    if not isinstance(smiles, str) or not smiles.strip():
        raise ValueError("smiles must be a non-empty SMILES/SMARTS pattern")
    if max_records <= 0:
        raise ValueError(f"max_records must be positive, got {max_records}")
    try:
        return pcp.get_compounds(smiles.strip(), "smiles",
            searchtype="substructure", MaxRecords=max_records)
    except PubChemPyError as exc:
        raise RuntimeError(f"Substructure search failed: {exc}") from exc

matches = substructure_search("c1ccncc1", max_records=100)
print(f"Found {len(matches)} compounds containing a pyridine ring")
```

**Common substructures:**
- Benzene ring: `c1ccccc1`
- Pyridine: `c1ccncc1`
- Phenol: `c1ccc(O)cc1`
- Carboxylic acid: `C(=O)O`

### 5. Format Conversion

One fetch returns every identifier format — bundle conversions into a single function to spend one API request instead of five:

```python
from typing import Dict, Optional
import pubchempy as pcp
from pubchempy import Compound, PubChemPyError

def identifier_bundle(name: str) -> Dict[str, Optional[str]]:
    if not isinstance(name, str) or not name.strip():
        raise ValueError("name must be a non-empty string")
    try:
        matches = pcp.get_compounds(name.strip(), "name")
    except PubChemPyError as exc:
        raise RuntimeError(f"Lookup failed for {name!r}: {exc}") from exc
    if not matches:
        raise LookupError(f"No compound found for {name!r}")
    c = matches[0]
    return {
        "cid": str(c.cid) if c.cid is not None else None,
        "smiles": c.canonical_smiles,
        "inchi": c.inchi,
        "inchikey": c.inchikey,
        "formula": c.molecular_formula,
    }

def download_structure(identifier: str, namespace: str, output_format: str, path: str) -> None:
    supported = {"SDF", "JSON", "PNG", "XML", "CSV", "ASNT"}
    if output_format.upper() not in supported:
        raise ValueError(f"output_format must be one of {sorted(supported)}")
    try:
        pcp.download(output_format.upper(), identifier, namespace, path, overwrite=True)
    except PubChemPyError as exc:
        raise RuntimeError(f"Download failed for {identifier!r}: {exc}") from exc

ids = identifier_bundle("aspirin")
download_structure("aspirin", "name", "SDF", "aspirin.sdf")
download_structure("2244", "cid", "JSON", "aspirin.json")
```

### 6. Structure Visualization

When calling PUG-REST directly for images, always set a `timeout` and check the response status. PubChem returns a non-PNG error body for a bad CID — without a check you would write a corrupt file to disk:

```python
from pathlib import Path
import requests

def save_structure_png(cid: int, path: str, image_size: str = "large") -> Path:
    if not isinstance(cid, int) or cid <= 0:
        raise ValueError(f"cid must be a positive integer, got {cid!r}")
    if image_size not in {"small", "large"}:
        raise ValueError("image_size must be 'small' or 'large'")
    url = (
        f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/cid/{cid}/PNG?image_size={image_size}"
    )
    resp = requests.get(url, timeout=30)
    resp.raise_for_status()
    out = Path(path)
    out.write_bytes(resp.content)
    return out

save_structure_png(2244, "aspirin.png")
```

### 7. Bioactivity Data

Use PUG-REST directly for assay summaries (PubChemPy does not wrap this endpoint). Load `references/api_reference.md` for the full bioactivity endpoint catalog.

```python
import requests
from typing import Dict, List

def get_bioactivity(cid: int) -> List[Dict]:
    if not isinstance(cid, int) or cid <= 0:
        raise ValueError(f"cid must be a positive integer, got {cid!r}")
    url = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/cid/{cid}/assaysummary/JSON"
    resp = requests.get(url, timeout=30)
    resp.raise_for_status()
    data = resp.json()
    return data.get("Table", {}).get("Columns", {}).get("Row", [])

assays = get_bioactivity(2244)
print(f"Total assays for aspirin: {len(assays)}")
```

### Workflow: Lipinski Rule of Five Check

```python
from typing import Dict, List
import pubchempy as pcp
from pubchempy import PubChemPyError

def check_lipinski(name: str) -> Dict[str, object]:
    try:
        matches = pcp.get_compounds(name.strip(), "name")
    except PubChemPyError as exc:
        raise RuntimeError(f"Lookup failed for {name!r}: {exc}") from exc
    if not matches:
        raise LookupError(f"No compound found for {name!r}")
    c = matches[0]
    checks = {}
    violations = []
    unknown = []
    for label, val, limit in [
        ("MW", c.molecular_weight, 500),
        ("LogP", c.xlogp, 5),
        ("HBD", c.h_bond_donor_count, 5),
        ("HBA", c.h_bond_acceptor_count, 10),
    ]:
        if val is None:
            unknown.append(label)
        else:
            checks[label] = val
            if val > limit:
                violations.append(f"{label}={val} > {limit}")
    return {"checks": checks, "violations": violations, "unknown": unknown}

result = check_lipinski("aspirin")
print(f"Lipinski violations: {result['violations']} (unknown: {result['unknown']})")
```

### Workflow: Drug-Like Analog Finder

PubChem similarity search cannot filter by MW/LogP server-side. Fetch the similar set, then apply the property window locally, skipping records with missing descriptors:

```python
from typing import List
import pubchempy as pcp
from pubchempy import Compound, PubChemPyError

def find_drug_like_analogs(reference_name: str, threshold: int = 85, max_records: int = 50) -> List[Compound]:
    if not isinstance(reference_name, str) or not reference_name.strip():
        raise ValueError("reference_name must be a non-empty string")
    if not isinstance(threshold, int) or not 0 <= threshold <= 100:
        raise ValueError(f"threshold must be an integer in [0, 100], got {threshold!r}")
    if max_records <= 0:
        raise ValueError(f"max_records must be positive, got {max_records}")
    try:
        reference = pcp.get_compounds(reference_name.strip(), "name")
    except PubChemPyError as exc:
        raise RuntimeError(f"Lookup failed for {reference_name!r}: {exc}") from exc
    if not reference:
        raise LookupError(f"No compound found for {reference_name!r}")
    ref_smiles = reference[0].canonical_smiles
    if not ref_smiles:
        raise LookupError(f"{reference_name!r} has no canonical SMILES")
    try:
        similar = pcp.get_compounds(ref_smiles, "smiles",
            searchtype="similarity", Threshold=threshold, MaxRecords=max_records)
    except PubChemPyError as exc:
        raise RuntimeError(f"Similarity search failed: {exc}") from exc
    candidates = []
    for c in similar:
        mw = c.molecular_weight
        logp = c.xlogp
        if mw is None or logp is None:
            continue
        if 200 <= mw <= 600 and -1 <= logp <= 5:
            candidates.append(c)
    return candidates

analogs = find_drug_like_analogs("imatinib", threshold=85, max_records=20)
print(f"Found {len(analogs)} drug-like candidates")
```

## Pitfalls

1. **Similarity threshold as float:** PubChem expects an integer percentage `[0, 100]`. Passing `0.85` silently means "0% similar" and returns the entire database. Always validate and reject floats.

2. **Truncated InChI strings:** A partial InChI resolves to a different or no structure. Always pass the complete InChI string including the `InChI=1S/` prefix.

3. **Missing descriptors:** PubChem does not compute every descriptor for every record. Every `Compound` accessor is `Optional`. Guard for `None` before arithmetic to avoid `TypeError`.

4. **Substructure search without `max_records`:** Common fragments (benzene, pyridine) match millions of records. Without a ceiling, the asynchronous search can exceed PubChem's ~30-second window and time out. Always set `MaxRecords`.

5. **Rate limiting (HARD RULE):** PubChem enforces 5 req/s, 400 req/min, and 300 s/min running time. In batch loops, maintain ≥0.2s spacing between requests. Exceeding limits produces HTTP 503 responses.

6. **Proprietary structures:** Every query travels to NCBI's public servers and can be logged. Never query undisclosed or proprietary structures through PubChem. Use local RDKit instead.

7. **`download` without `overwrite=True`:** PubChemPy raises `IOError` if the target file exists and `overwrite` is False. Always pass `overwrite=True` or handle the error explicitly.

8. **PUG-REST image requests without timeout:** A network call with no timeout can hang a pipeline indefinitely. PubChem returns a non-PNG error body for invalid CIDs. Always set `timeout` and check `raise_for_status()` before writing to disk.

9. **Batch failures aborting the run:** A single unknown name should not discard the rest of a batch. Wrap each lookup in its own `try/except` and accumulate failures rather than raising.

10. **Name ambiguity:** One chemical name can map to several PubChem records. Always treat name-based search results as a list, not a single compound.

## Verification

Run these checks in order — each builds on the previous:

1. **Dependencies import cleanly:**
   ```powershell
   python -c "import pubchempy, requests, pandas"
   ```
   Expected: exits 0 with no output.

2. **Live name lookup:**
   ```powershell
   python scripts/compound_search.py
   ```
   Expected: prints aspirin's CID (2244) and molecular formula (C9H8O4).

3. **Bioactivity path:**
   ```powershell
   python scripts/bioactivity_query.py
   ```
   Expected: returns a non-zero `total_assays` count for aspirin (CID 2244).

4. **Error handling — nonsense name:**
   ```python
   import pubchempy as pcp
   result = pcp.get_compounds("zzqqxx123", "name")
   print(result)  # Expected: [] (empty list, no crash)
   ```

5. **Optional-descriptor handling:**
   ```python
   import pubchempy as pcp
   c = pcp.Compound.from_cid(2244)
   print(f"XLogP: {c.xlogp}")  # Expected: a float or None, never a TypeError
   ```

6. **Rate-limit compliance:** A 20-compound batch with ≥0.2s spacing should produce no HTTP 503 responses. Check programmatically:
   ```python
   import time, pubchempy as pcp
   for name in ["aspirin", "ibuprofen", "paracetamol", "naproxen", "celecoxib"]:
       pcp.get_properties(["MolecularWeight"], name, "name")
       time.sleep(0.2)
   print("Batch complete — no 503 errors")
   ```

7. **PubChem usage policy:** Confirm the workflow stays within 5 req/s, 400 req/min, and 300 s/min running time.

## Related skills

This skill is self-contained with no hard dependency on another skill. For deeper API detail (full endpoint list, every available property, raw asynchronous request/poll workflow), load `references/api_reference.md`. Pair with a local cheminformatics toolkit (e.g. RDKit) when you need offline computation that PubChem's stored descriptors do not cover.
