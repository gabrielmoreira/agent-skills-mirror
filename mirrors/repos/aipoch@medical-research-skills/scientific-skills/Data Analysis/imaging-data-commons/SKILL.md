---
name: imaging-data-commons
description: Use idc-index to query and download public cancer imaging data from NCI Imaging Data Commons. Used to access large-scale radiology (CT, MR, PET) and pathology datasets for AI training or research. No authentication required. Supports metadata querying, in-browser visualization, and license checking.
license: MIT
author: aipoch
---
> **Source**: [https://github.com/aipoch/medical-research-skills](https://github.com/aipoch/medical-research-skills)
# Imaging Data Commons

## When to Use

- Use this skill when you need use idc-index to query and download public cancer imaging data from nci imaging data commons. used to access large-scale radiology (ct, mr, pet) and pathology datasets for ai training or research. no authentication required. supports metadata querying, in-browser visualization, and license checking in a reproducible workflow.
- Use this skill when a data analytics task needs a packaged method instead of ad-hoc freeform output.
- Use this skill when the user expects a concrete deliverable, validation step, or file-based result.
- Use this skill when `the documented workflow in this package` is the most direct path to complete the request.
- Use this skill when you need the `imaging-data-commons` package behavior rather than a generic answer.

## Key Features

- Scope-focused workflow aligned to: Use idc-index to query and download public cancer imaging data from NCI Imaging Data Commons. Used to access large-scale radiology (CT, MR, PET) and pathology datasets for AI training or research. No authentication required. Supports metadata querying, in-browser visualization, and license checking.
- Documentation-first workflow with no packaged script requirement.
- Reference material available in `references/` for task-specific guidance.
- Structured execution path designed to keep outputs consistent and reviewable.

## Dependencies

- `Python`: `3.10+`. Repository baseline for current packaged skills.
- `Third-party packages`: `not explicitly version-pinned in this skill package`. Add pinned versions if this skill needs stricter environment control.

## Example Usage

```text
Skill directory: 20260316/scientific-skills/Data Analytics/imaging-data-commons
No packaged executable script was detected.
Use the documented workflow in SKILL.md together with the references/assets in this folder.
```

Example run plan:
1. Read the skill instructions and collect the required inputs.
2. Follow the documented workflow exactly.
3. Use packaged references/assets from this folder when the task needs templates or rules.
4. Return a structured result tied to the requested deliverable.

## Implementation Details

See `## Overview` above for related details.

- Execution model: validate the request, choose the packaged workflow, and produce a bounded deliverable.
- Input controls: confirm the source files, scope limits, output format, and acceptance criteria before running any script.
- Primary implementation surface: instruction-only workflow in `SKILL.md`.
- Reference guidance: `references/` contains supporting rules, prompts, or checklists.
- Parameters to clarify first: input path, output path, scope filters, thresholds, and any domain-specific constraints.
- Output discipline: keep results reproducible, identify assumptions explicitly, and avoid undocumented side effects.

## Overview

Use the `idc-index` Python package to query and download public cancer imaging data from the National Cancer Institute (NCI) Imaging Data Commons (IDC). No authentication required to access data.

**Core Tool:** `idc-index` ([GitHub](https://github.com/imagingdatacommons/idc-index))

**View latest data scale:**

```python
from idc_index import IDCClient
client = IDCClient()

# Get IDC data version
print(client.get_idc_version())

# Get collection count and total series count
stats = client.sql_query("""
    SELECT   
        COUNT(DISTINCT collection_id) as collections,
        COUNT(DISTINCT analysis_result_id) as analysis_results,
        COUNT(DISTINCT PatientID) as patients,
        COUNT(DISTINCT StudyInstanceUID) as studies,
        COUNT(DISTINCT SeriesInstanceUID) as series,
        SUM(instanceCount) as instances,
        SUM(series_size_MB)/1000000 as size_TB
    FROM index
""")
print(stats)
```

**Core Workflow:**
1. Query metadata → `client.sql_query()`
2. Download DICOM files → `client.download_from_selection()`
3. Visualize in browser → `client.get_viewer_URL(seriesInstanceUID=...)`

## When to Use This Skill

- Finding publicly available radiology (CT, MR, PET) or pathology (slide microscopy) images
- Filtering image subsets by cancer type, imaging modality, anatomical site, or other metadata
- Downloading DICOM data from IDC
- Checking data licenses before research or commercial use
- Visualizing medical images in the browser without needing local DICOM viewer software

## IDC Data Model

IDC adds two grouping levels above the standard DICOM hierarchy (Patient → Study → Series → Instance):

- **collection_id**: Groups patients by disease, modality, or research focus (e.g., `tcga_luad`, `nlst`). A patient belongs to only one collection.
- **analysis_result_id**: Identifies derived objects (segmentations, annotations, radiomics features) across one or more original collections.

Use `collection_id` to find original imaging data (may include annotations stored with images); use `analysis_result_id` to find AI-generated or expert-annotated annotations.

**Key Identifiers for Querying:**

| Identifier | Scope | Purpose |
|------------|-------|---------|
| `collection_id` | Dataset grouping | Filter by project/study |
| `PatientID` | Patient | Group images by patient |
| `StudyInstanceUID` | DICOM study | Group related series, visualization |
| `SeriesInstanceUID` | DICOM series | Group related series, visualization |

## Index Tables

The `idc-index` package provides multiple metadata index tables accessible via SQL or pandas DataFrame.

**Important:** Use `client.indices_overview` to get current table descriptions and column schemas. This is the authoritative source for available columns and their types—always consult this when writing SQL or exploring data structures.

### Available Tables

| Table Name | Row Granularity | Loading Method | Description |
|-------|-----------------|--------|-------------|
| `index` | 1 row = 1 DICOM series | Auto | Core metadata for all current IDC data |
| `prior_versions_index` | 1 row = 1 DICOM series | Auto | Series from previous IDC versions; for downloading deprecated data |
| `collections_index` | 1 row = 1 collection | fetch_index() | Collection-level metadata and descriptions |
| `analysis_results_index` | 1 row = 1 analysis result set | fetch_index() | Metadata about derived datasets (annotations, segmentations) |
| `clinical_index` | 1 row = 1 clinical data column | fetch_index() | Mapping of clinical table columns to collections |
| `sm_index` | 1 row = 1 slide microscopy series | fetch_index() | Slide microscopy (pathology) series metadata |
| `sm_instance_index` | 1 row = 1 slide microscopy instance | fetch_index() | Instance-level metadata for slide microscopy (SOPInstanceUID) |
| `seg_index` | 1 row = 1 DICOM segmentation series | fetch_index() | Segmentation metadata: algorithm, number of segments, reference to source image series |

**Auto** = Automatically loaded when `IDCClient()` is instantiated
**fetch_index()** = Requires executing `client.fetch_index("table_name")` to load

### Joining Tables

**Key columns are not explicitly marked; here is a subset that can be used for joins.**

| Join Column | Tables | Use Case |
|-------------|--------|----------|
| `collection_id` | index, prior_versions_index, collections_index, clinical_index | Link series to collection metadata or clinical data |
| `SeriesInstanceUID` | index, prior_versions_index, sm_index, sm_instance_index | Cross-table linking of series; connect to slide microscopy details |
| `StudyInstanceUID` | index, prior_versions_index | Link studies across current and historical data |
| `PatientID` | index, prior_versions_index | Link patients across current and historical data |
| `analysis_result_id` | index, analysis_results_index | Link series to analysis result metadata (annotations, segmentations) |
| `source_DOI` | index, analysis_results_index | Link via publication DOI |
| `crdc_series_uuid` | index, prior_versions_index | Link via CRDC unique identifier |
| `Modality` | index, prior_versions_index | Filter by imaging modality |
| `SeriesInstanceUID` | index, seg_index | Link segmentation series to its index metadata |
| `segmented_SeriesInstanceUID` | seg_index → index | Link segmentation to its source image series (join seg_index.segmented_SeriesInstanceUID = index.SeriesInstanceUID) |

**Note:** `Subjects`, `Updated`, and `Description` appear in multiple tables but with different meanings (counts vs. identifiers, different update contexts).

**Join Examples:**
```python
from idc_index import IDCClient
client = IDCClient()

# Join index with collections_index to get cancer types
client.fetch_index("collections_index")
result = client.sql_query("""
    SELECT i.SeriesInstanceUID, i.Modality, c.CancerTypes, c.TumorLocations
    FROM index i
    JOIN collections_index c ON i.collection_id = c.collection_id
    WHERE i.Modality = 'MR'
    LIMIT 10
""")

# Join index with sm_index to get slide microscopy details
client.fetch_index("sm_index")
result = client.sql_query("""
    SELECT i.collection_id, i.PatientID, s.ObjectiveLensPower, s.min_PixelSpacing_2sf
    FROM index i
    JOIN sm_index s ON i.SeriesInstanceUID = s.SeriesInstanceUID
    LIMIT 10
""")

# Join seg_index with index to find segmentations and their source images
client.fetch_index("seg_index")
result = client.sql_query("""
    SELECT
        s.SeriesInstanceUID as seg_series,
        s.AlgorithmName,
        s.total_segments,
        src.collection_id,
        src.Modality as source_modality,
        src.BodyPartExamined
    FROM seg_index s
    JOIN index src ON s.segmented_SeriesInstanceUID = src.SeriesInstanceUID
    WHERE s.AlgorithmType = 'AUTOMATIC'
    LIMIT 10
""")
```

### Accessing Index Tables

**Via SQL (recommended for filtering/aggregation):**
```python
from idc_index import IDCClient
client = IDCClient()

# Query main index (always available)
results = client.sql_query("SELECT * FROM index WHERE Modality = 'CT' LIMIT 10")

# Fetch and query additional indexes
client.fetch_index("collections_index")
collections = client.sql_query("SELECT collection_id, CancerTypes, TumorLocations FROM collections_index")

client.fetch_index("analysis_results_index")
analysis = client.sql_query("SELECT * FROM analysis_results_index LIMIT 5")
```

**As pandas DataFrame (direct access):**
```python

# Main index (always available after client initialization)
df = client.index

# Fetch and access on-demand indexes
client.fetch_index("sm_index")
sm_df = client.sm_index
```

### Discovering Table Schemas (Key to Writing Queries)

The `indices_overview` dictionary contains complete schema information for all tables. **Always refer to this information when writing queries or exploring data structures.**

**DICOM Attribute Mapping:** Many columns are populated directly from DICOM attributes in source files. Column descriptions in the schema indicate whether a column corresponds to a DICOM attribute (e.g., "DICOM Modality attribute" or reference to a DICOM tag). This allows leveraging DICOM knowledge at query time—standard DICOM attribute names like `PatientID`, `StudyInstanceUID`, `Modality`, `BodyPartExamined` all work as expected.

```python
from idc_index import IDCClient
client = IDCClient()

# List all available indexes with their descriptions
for name, info in client.indices_overview.items():
    print(f"\n{name}:")
    print(f"  Installed: {info['installed']}")
    print(f"  Description: {info['description']}")

# Get full schema for a specific index (columns, types, descriptions)
schema = client.indices_overview["index"]["schema"]
print(f"\nTable: {schema['table_description']}")
print("\nColumns:")
for col in schema['columns']:
    desc = col.get('description', 'No description')
    # Description indicates whether column comes from DICOM attribute
    print(f"  {col['name']} ({col['type']}): {desc}")

# Find columns that belong to DICOM attributes (check if description contains "DICOM")
dicom_cols = [c['name'] for c in schema['columns'] if 'DICOM' in c.get('description', '').upper()]
print(f"\nDICOM-sourced columns: {dicom_cols}")
```

**Alternative: Use `get_index_schema()` method:**
```python
schema = client.get_index_schema("index")

# Returns the same schema dictionary: {'table_description': ..., 'columns': [...]}
```

### Key Columns in Primary `index` Table

Most commonly used columns in queries (full list and descriptions available in `indices_overview`):

| Column Name | Type | DICOM | Description |
|--------|------|-------|-------------|
| `collection_id` | STRING | No | IDC collection identifier |
| `analysis_result_id` | STRING | No | If applicable, indicates the analysis result set this series belongs to |
| `source_DOI` | STRING | No | DOI linking to dataset details; for further content info and attribution (see citation section below) |
| `PatientID` | STRING | Yes | Patient identifier |
| `StudyInstanceUID` | STRING | Yes | DICOM study UID |
| `SeriesInstanceUID` | STRING | Yes | DICOM series UID — for download/viewing |
| `Modality` | STRING | Yes | Imaging modality (CT, MR, PT, SM, etc.) |
| `BodyPartExamined` | STRING | Yes | Anatomical site |
| `SeriesDescription` | STRING | Yes | Series description |
| `Manufacturer` | STRING | Yes | Device manufacturer |
| `StudyDate` | STRING | Yes | Study execution date |
| `PatientSex` | STRING | Yes | Patient sex |
| `PatientAge` | STRING | Yes | Patient age at time of study |
| `license_short_name` | STRING | No | License type (CC BY 4.0, CC BY-NC 4.0, etc.) |
| `series_size_MB` | FLOAT | No | Series size in MB |
| `instanceCount` | INTEGER | No | Number of DICOM instances in the series |

**DICOM = Yes**: Column values extracted from DICOM attributes of the same name. For numeric tag mappings, refer to the [DICOM Standard](https://dicom.nema.org/medical/dicom/current/output/chtml/part06/chapter_6.html). Use standard DICOM knowledge to anticipate values and formats.

### Clinical Data Access

```python

# Fetch clinical index (also downloads clinical data tables)
client.fetch_index("clinical_index")

# Query clinical index to find available tables and their columns
tables = client.sql_query("SELECT DISTINCT table_name, column_label FROM clinical_index")

# Load specific clinical table as DataFrame
clinical_df = client.get_clinical_table("table_name")
```

For detailed workflows including value mapping schemas and joining clinical data with imaging data, see `references/clinical_data_guide.md`.

## Data Access Options

| Method | Authentication Required | Best For |
|--------|---------------|----------|
| `idc-index` | No | Key queries and downloads (recommended) |
| IDC Portal | No | Interactive exploration, manual selection, browser-based download |
| BigQuery | Yes (GCP account) | Complex queries, complete DICOM metadata |
| DICOMweb proxy | No | Tool integration via DICOMweb API |
| Cloud storage (S3/GCS) | No | Direct file access, batch downloads, custom pipelines |

**Cloud Storage Organization**

All DICOM files mirrored between AWS S3 and Google Cloud Storage are stored in public cloud storage buckets. Files are organized by CRDC UUID (not DICOM UID) to support versioning.

| Bucket (AWS / GCS) | License | Content |
|--------------------|---------|---------|
| `idc-open-data` / `idc-open-data` | No commercial restrictions | >90% of IDC data |
| `idc-open-data-two` / `idc-open-idc1` | No commercial restrictions | Collections that may contain head scans |
| `idc-open-data-cr` / `idc-open-cr` | Commercial use restricted (CC BY-NC) | ~4% of data |

File storage format is `<crdc_series_uuid>/<crdc_instance_uuid>.dcm`. Freely accessible via AWS CLI, gsutil, or s5cmd with anonymous access (no bandwidth fees). Use the `series_aws_url` column in the index to get S3 URL; GCS uses the same path structure.

For bucket details, access commands, UUID mapping, and versioning, see `references/cloud_storage_guide.md`.

**DICOMweb Access**

IDC data is available via DICOMweb interface (implemented on Google Cloud Healthcare API) for integrating PACS systems and DICOMweb-compatible tools.

| Endpoint | Authentication | Use Case |
|----------|------|----------|
| Public proxy | No | Testing, moderate queries, daily quota |
| Google Healthcare | Yes (GCP) | Production use, higher quotas |

For endpoint URLs, code examples, supported operations, and implementation details, see `references/dicomweb_guide.md`.

## Installation and Setup

**Required (basic access):**
```bash
pip install --upgrade idc-index
```

**Important:** Each IDC data release triggers a new version of `idc-index`. Unless you need an older version for reproducibility, always use the `--upgrade` flag when installing.

**Tested version:** idc-index 0.11.7 (IDC data version v23)

**Optional (data analysis):**
```bash
pip install pandas numpy pydicom
```

## Core Capabilities

### 1. Data Discovery and Exploration

Discover available imaging collections and data in IDC:

```python
from idc_index import IDCClient

client = IDCClient()

# Get summary statistics from main index
query = """
SELECT
  collection_id,
  COUNT(DISTINCT PatientID) as patients,
  COUNT(DISTINCT SeriesInstanceUID) as series,
  SUM(series_size_MB) as size_mb
FROM index
GROUP BY collection_id
ORDER BY patients DESC
"""
collections_summary = client.sql_query(query)

# For richer collection metadata, use collections_index
client.fetch_index("collections_index")
collections_info = client.sql_query("""
    SELECT collection_id, CancerTypes, TumorLocations, Species, Subjects, SupportingData
    FROM collections_index
""")

# For analysis results (annotations, segmentations), use analysis_results_index
client.fetch_index("analysis_results_index")
analysis_info = client.sql_query("""
    SELECT analysis_result_id, analysis_result_title, Subjects, Collections, Modalities
    FROM analysis_results_index
""")
```

**`collections_index`** provides curated metadata for each collection: cancer types, tumor locations, species, subject counts, and supported data types, without needing aggregation from the main index.

**`analysis_results_index`** lists derived datasets (AI segmentations, expert annotations, radiomics features) with their source collections and modalities.

### 2. Querying Metadata with SQL

Use SQL to query the IDC mini-index to find specific datasets.

**First, explore optional filter values:**
```python
from idc_index import IDCClient

client = IDCClient()

# Check what Modality values exist
modalities = client.sql_query("""
    SELECT DISTINCT Modality, COUNT(*) as series_count
    FROM index
    GROUP BY Modality
    ORDER BY series_count DESC
""")
print(modalities)

# Check what BodyPartExamined values exist for MR modality
body_parts = client.sql_query("""
    SELECT DISTINCT BodyPartExamined, COUNT(*) as series_count
    FROM index
    WHERE Modality = 'MR' AND BodyPartExamined IS NOT NULL
    GROUP BY BodyPartExamined
    ORDER BY series_count DESC
    LIMIT 20
""")
print(body_parts)
```

**Then query using validated filter values:**
```python

# Find breast MRI scans (using actual values from exploration above)
results = client.sql_query("""
    SELECT
      collection_id,
      PatientID,
      SeriesInstanceUID,
      Modality,
      SeriesDescription,
      license_short_name
    FROM index
    WHERE Modality = 'MR'
      AND BodyPartExamined = 'BREAST'
    LIMIT 20
""")

# Access results as pandas DataFrame
for idx, row in results.iterrows():
    print(f"Patient: {row['PatientID']}, Series: {row['SeriesInstanceUID']}")
```

**Filter by cancer type, requires joining with `collections_index`:**
```python
client.fetch_index("collections_index")
results = client.sql_query("""
    SELECT i.collection_id, i.PatientID, i.SeriesInstanceUID, i.Modality
    FROM index i
    JOIN collections_index c ON i.collection_id = c.collection_id
    WHERE c.CancerTypes LIKE '%Breast%'
      AND i.Modality = 'MR'
    LIMIT 20
""")
```

**Available metadata fields** (full list use `client.indices_overview`):
- Identifiers: collection_id, PatientID, StudyInstanceUID, SeriesInstanceUID
- Imaging: Modality, BodyPartExamined, Manufacturer, ManufacturerModelName
- Clinical: PatientAge, PatientSex, StudyDate
- Descriptions: StudyDescription, SeriesDescription
- License: license_short_name

**Note:** Cancer types are in `collections_index.CancerTypes`, not in the main `index` table.

### 3. Downloading DICOM Files

Efficiently download imaging data from IDC cloud storage:

**Download entire collection:**
```python
from idc_index import IDCClient

client = IDCClient()

# Download small collection (RIDER Pilot ~1GB)
client.download_from_selection(
    collection_id="rider_pilot",
    downloadDir="./data/rider"
)
```

**Download specific series:**
```python

# First, query for series UIDs
series_df = client.sql_query("""
    SELECT SeriesInstanceUID
    FROM index
    WHERE Modality = 'CT'
      AND BodyPartExamined = 'CHEST'
      AND collection_id = 'nlst'
    LIMIT 5
""")

# Download only these series
client.download_from_selection(
    seriesInstanceUID=list(series_df['SeriesInstanceUID'].values),
    downloadDir="./data/lung_ct"
)
```

**Custom directory structure:**

Default `dirTemplate` is: `%collection_id/%PatientID/%StudyInstanceUID/%Modality_%SeriesInstanceUID`

```python

# Simplified hierarchy (omit StudyInstanceUID level)
client.download_from_selection(
    collection_id="tcga_luad",
    downloadDir="./data",
    dirTemplate="%collection_id/%PatientID/%Modality"
)

# Result path: ./data/tcga_luad/TCGA-05-4244/CT/

# Flat structure (all files in same directory)
client.download_from_selection(
    seriesInstanceUID=list(series_df['SeriesInstanceUID'].values),
    downloadDir="./data/flat",
    dirTemplate=""
)

# Result path: ./data/flat/*.dcm
```

### Command-Line Download

The `idc download` command provides command-line access to download functionality without writing Python code. Available after installing `idc-index`.

**Auto-detect input type:** Manifest file path, or identifier (collection_id, PatientID, StudyInstanceUID, SeriesInstanceUID, crdc_series_uuid).

```bash

# Download entire collection
idc download rider_pilot --download-dir ./data

# Download specific series by UID
idc download "1.3.6.1.4.1.9328.50.1.69736" --download-dir ./data

# Download multiple items (comma-separated)
idc download "tcga_luad,tcga_lusc" --download-dir ./data

# Download from manifest file (auto-detect)
idc download manifest.txt --download-dir ./data
```

**Options:**

| Option | Description |
|--------|-------------|
| `--download-dir` | Output directory (default: current directory) |
| `--dir-template` | Directory hierarchy template (default: `%collection_id/%PatientID/%StudyInstanceUID/%Modality_%SeriesInstanceUID`) |
| `--log-level` | Logging verbosity: debug, info, warning, error, critical |

**Manifest files:**

Manifest files contain S3 URLs (one per line), which can be:
- Exported from IDC Portal after queue selection
- Shared by collaborators for reproducible data access
- Programmatically generated from query results

Format (one S3 URL per line):
```
s3://idc-open-data/cb09464a-c5cc-4428-9339-d7fa87cfe837/*
s3://idc-open-data/88f3990d-bdef-49cd-9b2b-4787767240f2/*
```

**Example: Generate manifest from Python query:**

```python
from idc_index import IDCClient

client = IDCClient()

# Query series URLs
results = client.sql_query("""
    SELECT series_aws_url
    FROM index
    WHERE collection_id = 'rider_pilot' AND Modality = 'CT'
""")

# Save as manifest file
with open('ct_manifest.txt', 'w') as f:
    for url in results['series_aws_url']:
        f.write(url + '\n')
```

Then download:
```bash
idc download ct_manifest.txt --download-dir ./ct_data
```

### 4. Visualizing IDC Images

View DICOM data in the browser without downloading:

```python
from idc_index import IDCClient
import webbrowser

client = IDCClient()

# First query to get valid UIDs
results = client.sql_query("""
    SELECT SeriesInstanceUID, StudyInstanceUID
    FROM index
    WHERE collection_id = 'rider_pilot' AND Modality = 'CT'
    LIMIT 1
""")

# View single series
viewer_url = client.get_viewer_URL(seriesInstanceUID=results.iloc[0]['SeriesInstanceUID'])
webbrowser.open(viewer_url)

# View all series in a study (useful for multi-series exams like MRI protocols)
viewer_url = client.get_viewer_URL(studyInstanceUID=results.iloc[0]['StudyInstanceUID'])
webbrowser.open(viewer_url)
```

This method automatically selects OHIF v3 for radiology or SLIM for slide microscopy. Viewing by study is very useful when a DICOM study contains multiple series (e.g., T1, T2, DWI sequences in a single MRI session).

### 5. Understanding and Checking Licenses

Check data licenses before use (critical for commercial applications):

```python
from idc_index import IDCClient

client = IDCClient()

# Check licenses for all collections
query = """
SELECT DISTINCT
  collection_id,
  license_short_name,
  COUNT(DISTINCT SeriesInstanceUID) as series_count
FROM index
GROUP BY collection_id, license_short_name
ORDER BY collection_id
"""

licenses = client.sql_query(query)
print(licenses)
```

**License types in IDC:**
- **CC BY 4.0** / **CC BY 3.0** (~97% of data) - Allows commercial use with attribution
- **CC BY-NC 4.0** / **CC BY-NC 3.0** (~3% of data) - Non-commercial use only
- **Custom license** (rare) - Some collections have specific terms (e.g., NLM terms)

**Important:** Always check the license before using IDC data in publications or commercial applications. Each DICOM file's metadata tags its specific license.

### Generating Citations for Attribution

The `source_DOI` column contains DOIs pointing to publications describing the data generation process. To meet attribution requirements, use `citations_from_selection()` to generate properly formatted citations:

```python
from idc_index import IDCClient

client = IDCClient()

# Get citations for collection (APA format by default)
citations = client.citations_from_selection(collection_id="rider_pilot")
for citation in citations:
    print(citation)

# Get citations for specific series
results = client.sql_query("""
    SELECT SeriesInstanceUID FROM index
    WHERE collection_id = 'tcga_luad' LIMIT 5
""")
citations = client.citations_from_selection(
    seriesInstanceUID=list(results['SeriesInstanceUID'].values)
)

# Alternative format: BibTeX (for LaTeX documents)
bibtex_citations = client.citations_from_selection(
    collection_id="tcga_luad",
    citation_format=IDCClient.CITATION_FORMAT_BIBTEX
)
```

**Parameters:**
- `collection_id`: Filter by collection
- `patientId`: Filter by patient ID
- `studyInstanceUID`: Filter by study UID
- `seriesInstanceUID`: Filter by series UID
- `citation_format`: Use `IDCClient.CITATION_FORMAT_*` constants:
  - `CITATION_FORMAT_APA` (default) - APA style
  - `CITATION_FORMAT_BIBTEX` - BibTeX for LaTeX
  - `CITATION_FORMAT_JSON` - CSL JSON
  - `CITATION_FORMAT_TURTLE` - RDF Turtle

**Best Practice:** When publishing results obtained using IDC data, include generated citations to properly attribute data sources and meet license requirements.

### 6. Batch Processing and Filtering

Efficiently process large-scale datasets through filtering:

```python
from idc_index import IDCClient
import pandas as pd

client = IDCClient()

# Find chest CT scans from GE scanners
query = """
SELECT
  SeriesInstanceUID,
  PatientID,
  collection_id,
  ManufacturerModelName
FROM index
WHERE Modality = 'CT'
  AND BodyPartExamined = 'CHEST'
  AND Manufacturer = 'GE MEDICAL SYSTEMS'
  AND license_short_name = 'CC BY 4.0'
LIMIT 100
"""

results = client.sql_query(query)

# Save manifest for later use
results.to_csv('lung_ct_manifest.csv', index=False)

# Download in batches to avoid timeouts
batch_size = 10
for i in range(0, len(results), batch_size):
    batch = results.iloc[i:i+batch_size]
    client.download_from_selection(
        seriesInstanceUID=list(batch['SeriesInstanceUID'].values),
        downloadDir=f"./data/batch_{i//batch_size}"
    )
```

### 7. Advanced Queries with BigQuery

For queries requiring complete DICOM metadata, complex JOINs, clinical data tables, or private DICOM elements, use Google BigQuery. Requires a GCP project with billing enabled.

**Quick Reference:**
- Dataset: `bigquery-public-data.idc_current.*`
- Main table: `dicom_all` (merged metadata)
- Complete metadata: `dicom_metadata` (all DICOM tags)
- Private elements: `OtherElements` column (vendor-specific tags like diffusion b-values)

For setup, table schemas, query patterns, private element access, and cost optimization, see `references/bigquery_guide.md`.

### 8. Tool Selection Guide

| Task | Tool | Reference |
|------|------|-----------|
| Programmatic query and download | `idc-index` | This document |
| Interactive exploration | IDC Portal | https://portal.imaging.datacommons.cancer.gov/ |
| Complex metadata queries | BigQuery | `references/bigquery_guide.md` |
| 3D visualization and analysis | SlicerIDCBrowser | https://github.com/ImagingDataCommons/SlicerIDCBrowser |

**Default Choice:** `idc-index` is recommended for the vast majority of tasks (no authentication, simple API, supports batch downloads).

### 9. Integration with Analysis Pipelines

Integrate IDC data into imaging analysis workflows:

**Read downloaded DICOM files:**
```python
import pydicom
import os

# Read DICOM files from downloaded series
series_dir = "./data/rider/rider_pilot/RIDER-1007893286/CT_1.3.6.1..."

dicom_files = [os.path.join(series_dir, f) for f in os.listdir(series_dir)
               if f.endswith('.dcm')]

# Load first image
ds = pydicom.dcmread(dicom_files[0])
print(f"Patient ID: {ds.PatientID}")
print(f"Modality: {ds.Modality}")
print(f"Image shape: {ds.pixel_array.shape}")
```

**Build 3D volume from CT series:**
```python
import pydicom
import numpy as np
from pathlib import Path

def load_ct_series(series_path):
    """Load CT series as 3D numpy array"""
    files = sorted(Path(series_path).glob('*.dcm'))
    slices = [pydicom.dcmread(str(f)) for f in files]

    # Sort by slice position
    slices.sort(key=lambda x: float(x.ImagePositionPatient[2]))

    # Stack into 3D array
    volume = np.stack([s.pixel_array for s in slices])

    return volume, slices[0]  # Return volume and first slice for metadata

volume, metadata = load_ct_series("./data/lung_ct/series_dir")
print(f"Volume shape: {volume.shape}")  # (z, y, x)
```

**Integration with SimpleITK:**
```python
import SimpleITK as sitk
from pathlib import Path

# Read DICOM series
series_path = "./data/ct_series"
reader = sitk.ImageSeriesReader()
dicom_names = reader.GetGDCMSeriesFileNames(series_path)
reader.SetFileNames(dicom_names)
image = reader.Execute()

# Apply processing (smoothing filter)
smoothed = sitk.CurvatureFlow(image1=image, timeStep=0.125, numberOfIterations=5)

# Save as NIfTI format
sitk.WriteImage(smoothed, "processed_volume.nii.gz")
```

## Common Use Cases

### Use Case 1: Find and Download Lung CT Scans for Deep Learning

**Goal:** Build training dataset of lung CT scans from NLST collection

**Steps:**
```python
from idc_index import IDCClient

client = IDCClient()

# 1. Query lung CT scans with specific criteria
query = """
SELECT
  PatientID,
  SeriesInstanceUID,
  SeriesDescription
FROM index
WHERE collection_id = 'nlst'
  AND Modality = 'CT'
  AND BodyPartExamined = 'CHEST'
  AND license_short_name = 'CC BY 4.0'
ORDER BY PatientID
LIMIT 100
"""

results = client.sql_query(query)
print(f"Found {len(results)} series from {results['PatientID'].nunique()} patients")

# 2. Download data organized by patient
client.download_from_selection(
    seriesInstanceUID=list(results['SeriesInstanceUID'].values),
    downloadDir="./training_data",
    dirTemplate="%collection_id/%PatientID/%SeriesInstanceUID"
)

# 3. Save manifest for reproducibility
results.to_csv('training_manifest.csv', index=False)
```

### Use Case 2: Query Brain MRI by Manufacturer for Quality Research

**Goal:** Compare image quality across different MRI scanner manufacturers

**Steps:**
```python
from idc_index import IDCClient
import pandas as pd

client = IDCClient()

# Query brain MRI grouped by manufacturer
query = """
SELECT
  Manufacturer,
  ManufacturerModelName,
  COUNT(DISTINCT SeriesInstanceUID) as num_series,
  COUNT(DISTINCT PatientID) as num_patients
FROM index
WHERE Modality = 'MR'
  AND BodyPartExamined LIKE '%BRAIN%'
GROUP BY Manufacturer, ManufacturerModelName
HAVING num_series >= 10
ORDER BY num_series DESC
"""

manufacturers = client.sql_query(query)
print(manufacturers)

# Download samples from each manufacturer for comparison
for _, row in manufacturers.head(3).iterrows():
    mfr = row['Manufacturer']
    model = row['ManufacturerModelName']

    query = f"""
    SELECT SeriesInstanceUID
    FROM index
    WHERE Manufacturer = '{mfr}'
      AND ManufacturerModelName = '{model}'
      AND Modality = 'MR'
      AND BodyPartExamined LIKE '%BRAIN%'
    LIMIT 5
    """

    series = client.sql_query(query)
    client.download_from_selection(
        seriesInstanceUID=list(series['SeriesInstanceUID'].values),
        downloadDir=f"./quality_study/{mfr.replace(' ', '_')}"
    )
```

### Use Case 3: Preview Series Without Downloading

**Goal:** Preview imaging data before deciding to download

```python
from idc_index import IDCClient
import webbrowser

client = IDCClient()

series_list = client.sql_query("""
    SELECT SeriesInstanceUID, PatientID, SeriesDescription
    FROM index
    WHERE collection_id = 'acrin_nsclc_fdg_pet' AND Modality = 'PT'
    LIMIT 10
""")

# Preview each series in browser
for _, row in series_list.iterrows():
    viewer_url = client.get_viewer_URL(seriesInstanceUID=row['SeriesInstanceUID'])
    print(f"Patient {row['PatientID']}: {row['SeriesDescription']}")
    print(f"  View at: {viewer_url}")
    # webbrowser.open(viewer_url)  # Uncomment to auto-open
```

For more visualization options, see [IDC Portal Getting Started Guide](https://learn.canceridc.dev/portal/getting-started) or [SlicerIDCBrowser](https://github.com/ImagingDataCommons/SlicerIDCBrowser) for 3D Slicer integration.

### Use Case 4: License-Sensitive Batch Download for Commercial Use

**Goal:** Only download CC-BY licensed data suitable for commercial use

**Steps:**
```python
from idc_index import IDCClient

client = IDCClient()

# Query only CC BY licensed data (allows commercial use with attribution)
query = """
SELECT
  SeriesInstanceUID,
  collection_id,
  PatientID,
  Modality
FROM index
WHERE license_short_name LIKE 'CC BY%'
  AND license_short_name NOT LIKE '%NC%'
  AND Modality IN ('CT', 'MR')
  AND BodyPartExamined IN ('CHEST', 'BRAIN', 'ABDOMEN')
LIMIT 200
"""

cc_by_data = client.sql_query(query)

print(f"Found {len(cc_by_data)} CC BY licensed series")
print(f"Collections: {cc_by_data['collection_id'].unique()}")

# Download after license verification
client.download_from_selection(
    seriesInstanceUID=list(cc_by_data['SeriesInstanceUID'].values),
    downloadDir="./commercial_dataset",
    dirTemplate="%collection_id/%Modality/%PatientID/%SeriesInstanceUID"
)

# Save license information
cc_by_data.to_csv('commercial_dataset_manifest_CC-BY_ONLY.csv', index=False)
```

## Best Practices

- **Check license before use** - Always query `license_short_name` field and comply with license terms (CC BY vs CC BY-NC).
- **Generate citations for attribution** - Use `citations_from_selection()` to get properly formatted citations from `source_DOI` values and include them in publications.
- **Start with small queries** - Use `LIMIT` clause when exploring to avoid long downloads and help understand data structure.
- **Use mini-index for simple queries** - Only use BigQuery when you need comprehensive metadata or complex JOINs.
- **Organize downloads with dirTemplate** - Use meaningful directory structures like `%collection_id/%PatientID/%Modality`.
- **Cache query results** - Save DataFrames as CSV files to avoid repeated queries and ensure reproducibility.
- **Estimate size before downloading** - Check collection sizes before downloading—some collections are TB in size!
- **Save manifests** - Always save query results with series UIDs for reproducibility and data provenance tracking.
- **Read documentation** - IDC data structure and metadata fields are documented at https://learn.canceridc.dev/.
- **Use IDC forum** - Search for answers at https://discourse.canceridc.dev/, or ask questions to IDC maintainers and users.

## Troubleshooting

**Problem: `ModuleNotFoundError: No module named 'idc_index'`**
- **Cause:** idc-index package not installed.
- **Solution:** Install with `pip install --upgrade idc-index`.

**Problem: Download fails with connection timeout**
- **Cause:** Unstable network or too large download.
- **Solution:**
  - Download in small batches (e.g., 10-20 series at a time).
  - Check network connection.
  - Use `dirTemplate` to organize downloads by batch.
  - Implement retry logic with delays.

**Problem: `BigQuery quota exceeded` or billing error**
- **Cause:** BigQuery requires a GCP project with billing enabled.
- **Solution:** For simple queries, use idc-index mini-index (no cost), or see `references/bigquery_guide.md` for cost optimization tips.

**Problem: Cannot find series UID or no data returned**
- **Cause:** UID typo, data not in current IDC version, or wrong field name.
- **Solution:**
  - Check if data is in current IDC version (some older data may be deprecated).
  - Test query with `LIMIT 5` first.
  - Verify field names against metadata schema documentation.

**Problem: Downloaded DICOM files won't open**
- **Cause:** Download corrupted or viewer incompatible.
- **Solution:**
  - Check DICOM object type (Modality and SOPClassUID attributes) — some object types require specialized tools.
  - Verify file integrity (check file sizes).
  - Validate with pydicom: `pydicom.dcmread(file, force=True)`.
  - Try different DICOM viewers (3D Slicer, Horos, RadiAnt, QuPath).
  - Re-download the series.

## Common SQL Query Patterns

Quick reference for common queries. Detailed contextual examples are in the "Core Capabilities" section above.

### Discover Available Filter Values
```python

# What modalities exist?
client.sql_query("SELECT DISTINCT Modality FROM index")

# What body parts for a specific modality?
client.sql_query("""
    SELECT DISTINCT BodyPartExamined, COUNT(*) as n
    FROM index WHERE Modality = 'CT' AND BodyPartExamined IS NOT NULL
    GROUP BY BodyPartExamined ORDER BY n DESC
""")

# What manufacturers for MR?
client.sql_query("""
    SELECT DISTINCT Manufacturer, COUNT(*) as n
    FROM index WHERE Modality = 'MR'
    GROUP BY Manufacturer ORDER BY n DESC
""")
```

### Find Annotations and Segmentations

**Note:** Not all image-derived objects belong to analysis result collections. Some annotations are stored with the original images. Use DICOM Modality or SOPClassUID to find all derived objects regardless of their collection type.

```python

# Find all segmentations and structure sets via DICOM Modality

# SEG = DICOM Segmentation, RTSTRUCT = Radiotherapy structure set
client.sql_query("""
    SELECT collection_id, Modality, COUNT(*) as series_count
    FROM index
    WHERE Modality IN ('SEG', 'RTSTRUCT')
    GROUP BY collection_id, Modality
    ORDER BY series_count DESC
""")

# Find segmentations for specific collection (including non-analysis result items)
client.sql_query("""
    SELECT SeriesInstanceUID, SeriesDescription, analysis_result_id
    FROM index
    WHERE collection_id = 'tcga_luad' AND Modality = 'SEG'
""")

# List analysis result collections (curated derived datasets)
client.fetch_index("analysis_results_index")
client.sql_query("""
    SELECT analysis_result_id, analysis_result_title, Collections, Modalities
    FROM analysis_results_index
""")

# Find analysis results for a specific source collection
client.sql_query("""
    SELECT analysis_result_id, analysis_result_title
    FROM analysis_results_index
    WHERE Collections LIKE '%tcga_luad%'
""")

# Use seg_index for detailed DICOM segmentation metadata
client.fetch_index("seg_index")

# Get segmentation statistics by algorithm
client.sql_query("""
    SELECT AlgorithmName, AlgorithmType, COUNT(*) as seg_count
    FROM seg_index
    WHERE AlgorithmName IS NOT NULL
    GROUP BY AlgorithmName, AlgorithmType
    ORDER BY seg_count DESC
    LIMIT 10
""")

# Find segmentations for specific source images (e.g., chest CT)
client.sql_query("""
    SELECT
        s.SeriesInstanceUID as seg_series,
        s.AlgorithmName,
        s.total_segments,
        s.segmented_SeriesInstanceUID as source_series
    FROM seg_index s
    JOIN index src ON s.segmented_SeriesInstanceUID = src.SeriesInstanceUID
    WHERE src.Modality = 'CT' AND src.BodyPartExamined = 'CHEST'
    LIMIT 10
""")

# Find TotalSegmentator results in source image context
client.sql_query("""
    SELECT
        seg_info.collection_id,
        COUNT(DISTINCT s.SeriesInstanceUID) as seg_count,
        SUM(s.total_segments) as total_segments
    FROM seg_index s
    JOIN index seg_info ON s.SeriesInstanceUID = seg_info.SeriesInstanceUID
    WHERE s.AlgorithmName LIKE '%TotalSegmentator%'
    GROUP BY seg_info.collection_id
    ORDER BY seg_count DESC
""")
```

### Query Slide Microscopy Data
```python

# sm_index contains detailed metadata; join with index to get collection_id
client.fetch_index("sm_index")
client.sql_query("""
    SELECT i.collection_id, COUNT(*) as slides,
           MIN(s.min_PixelSpacing_2sf) as min_resolution
    FROM sm_index s
    JOIN index i ON s.SeriesInstanceUID = i.SeriesInstanceUID
    GROUP BY i.collection_id
    ORDER BY slides DESC
""")
```

### Estimate Download Size
```python

# Total size for specific criteria
client.sql_query("""
    SELECT SUM(series_size_MB) as total_mb, COUNT(*) as series_count
    FROM index
    WHERE collection_id = 'nlst' AND Modality = 'CT'
""")
```

### Link to Clinical Data
```python
client.fetch_index("clinical_index")

# Find collections with clinical data and their corresponding tables
client.sql_query("""
    SELECT collection_id, table_name, COUNT(DISTINCT column_label) as columns
    FROM clinical_index
    GROUP BY collection_id, table_name
    ORDER BY collection_id
""")
```

For complete schemas including value mappings and patient cohort selection, see `references/clinical_data_guide.md`.

## Related Skills

The following skills complement the IDC workflow for downstream analysis and visualization:

### DICOM Processing
- **pydicom** - Read, write, and manipulate downloaded DICOM files. Used to extract pixel data, read metadata, anonymize, and convert formats. Fundamental for processing IDC radiology data (CT, MR, PET).

### Pathology and Slide Microscopy
- **histolab** - Lightweight slide extraction and preprocessing for Whole Slide Images (WSI). Used for basic slide processing, tissue detection, and dataset preparation of IDC slide microscopy data.
- **pathml** - Full-featured computational pathology toolbox. Used for advanced WSI analysis, including multiplexed imaging, nucleus segmentation, and training machine learning models on pathology data downloaded from IDC.

### Metadata Visualization
- **matplotlib** - Low-level plotting library with full customization. Used to create static charts summarizing IDC query results (modality bar charts, series count histograms, etc.).
- **seaborn** - Statistical visualization library with pandas integration. Used for quick exploration of IDC metadata distributions, variable relationships, and categorical comparisons with beautiful default styles.
- **plotly** - Interactive visualization library. Used when you need hover info, zoom and pan capabilities to explore IDC metadata, or to create embeddable web dashboards for collection statistics.

### Data Exploration
- **exploratory-data-analysis** - Comprehensive EDA for scientific data files. Used after downloading IDC data to understand file structure, quality, and characteristics before analysis.

## Resources

### Schema Reference (Primary Source)

**Always use `client.indices_overview` to get current column schemas.** This ensures consistency with your installed idc-index version:

```python

# Get column names and types for any table
schema = client.indices_overview["index"]["schema"]
columns = [(c['name'], c['type'], c.get('description', '')) for c in schema['columns']]
```

### Reference Documentation

- **clinical_data_guide.md** - Clinical/tabular data navigation, value mappings, and linking with imaging data.
- **cloud_storage_guide.md** - Direct access to cloud storage buckets (S3/GCS), file organization, CRDC UUID, versioning, and reproducibility.
- **cli_guide.md** - Complete idc-index command-line interface reference (`idc download`, `idc download-from-manifest`, `idc download-from-selection`).
- **bigquery_guide.md** - Advanced BigQuery usage guide for complex metadata queries.
- **dicomweb_guide.md** - DICOMweb endpoint URLs, code examples, and Google Healthcare API implementation details.
- **[indices_reference](https://idc-index.readthedocs.io/en/latest/indices_reference.html)** - External documentation for index tables (may be ahead of installed version).

### External Links

- **IDC Portal**: https://portal.imaging.datacommons.cancer.gov/explore/
- **Official Documentation**: https://learn.canceridc.dev/
- **Tutorials**: https://github.com/ImagingDataCommons/IDC-Tutorials
- **User Forum**: https://discourse.canceridc.dev/
- **idc-index GitHub**: https://github.com/ImagingDataCommons/idc-index
- **Citation**: Fedorov, A., et al. "National Cancer Institute Imaging Data Commons: Toward Transparency, Reproducibility, and Scalability in Imaging Artificial Intelligence." RadioGraphics 43.12 (2023). https://doi.org/10.1148/rg.230180

### Skill Updates

This skill version can be found in the skill metadata. To check for updates:
- Visit [Releases page](https://github.com/ImagingDataCommons/idc-claude-skill/releases)
- Watch the repository on GitHub (Watch → Custom → Releases)
