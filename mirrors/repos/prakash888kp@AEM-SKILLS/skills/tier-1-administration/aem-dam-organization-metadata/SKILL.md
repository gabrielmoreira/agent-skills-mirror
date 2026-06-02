# AEM DAM Organization & Metadata

## Purpose
Architect and implement Digital Asset Management strategies including folder structures, metadata schemas, smart tags, asset processing profiles, and search optimization in AEM Assets.

## When to Use (Triggers)
- User mentions "DAM," "assets," "metadata schema," or "asset management"
- References to `/content/dam/`, metadata profiles, or processing profiles
- Questions about asset search, tagging, or rendition generation
- Requests involving Dynamic Media, asset workflows, or folder metadata
- File paths containing `/dam/` or references to `dam:Asset` node type

## Core Capabilities
- Design scalable DAM folder structures with metadata inheritance
- Create custom metadata schemas with field validation and cascading rules
- Configure asset processing profiles for renditions and transformations
- Implement tag taxonomies and smart tagging strategies
- Optimize asset search with custom search facets and predicates

## Domain Knowledge Required
### Technical Foundation
- JCR node structure for dam:Asset (original, renditions, metadata, subassets)
- Metadata schema editor and form field types
- Asset microservices architecture (Cloud Service) vs. workflow-based processing (6.5)
- Oak index configuration for DAM search queries

### AEM-Specific Context
- Processing profiles vs. metadata profiles vs. image profiles
- Dynamic Media integration (Scene7 mode, Hybrid mode)
- Connected Assets and cross-instance DAM sharing
- Asset Link sharing and Brand Portal distribution
- Folder metadata schemas vs. asset-level metadata schemas

## Implementation Approach
### Step 1: Taxonomy & Structure Design
Plan folder hierarchy and classification strategy.
- Define top-level folder organization (by brand, campaign, asset type, region)
- Design tag taxonomy aligned with business vocabulary
- Plan metadata inheritance rules (folder → subfolder → asset)
- Determine access control requirements per folder

### Step 2: Metadata Schema Configuration
Build metadata entry forms for authors.
- Create schema forms under `/conf/<project>/settings/dam/adminui-extension/metadataschema/`
- Define required, optional, and computed fields
- Configure cascading dropdowns and conditional field visibility
- Set up validation rules and default values

### Step 3: Processing Profile Setup
Configure automated asset transformation.
- Define rendition profiles (web, thumbnail, print, social)
- Configure video transcoding profiles if applicable
- Set up PDF rasterization and document extraction
- Configure smart crop profiles for Dynamic Media

### Step 4: Search & Discovery Optimization
Ensure assets are findable by all stakeholders.
- Configure custom search facets (by metadata, tags, file type)
- Set up Omnisearch predicates for advanced filtering
- Create saved searches and smart collections
- Implement asset reporting for usage analytics

### Step 5: Governance & Lifecycle
Establish asset lifecycle management.
- Configure asset expiration and archival policies
- Set up version management and version purging
- Define asset usage tracking and reference detection
- Implement rights management metadata fields

## Quality Checklist
- [ ] Folder structure supports growth without reorganization
- [ ] Metadata schema covers all business-required fields
- [ ] Processing profiles generate all needed renditions efficiently
- [ ] Search returns relevant results within 3 seconds for common queries
- [ ] Tag taxonomy is consistent and governed
- [ ] Asset permissions follow principle of least privilege
- [ ] Expired assets are properly flagged or hidden from search
- [ ] Bulk import/export workflows function correctly

## Related Skills
- aem-workflows-process-steps (DAM processing workflows)
- aem-security-access-control (DAM permissions)
- aem-content-strategy-architecture (asset usage in content)

## Example Use Cases
1. **Global Brand Asset Library:** Design a DAM structure for 50,000+ assets across 12 brands with region-specific licensing metadata, automated rendition generation, and brand-specific access controls.
2. **Product Photography Pipeline:** Configure automated processing for product images including background removal, smart crop profiles for multiple aspect ratios, and metadata extraction from EXIF/IPTC data.
3. **Video Content Hub:** Implement video asset management with transcoding profiles, chapter marker extraction, thumbnail generation, and integration with a streaming CDN.

## Notes
- AEM Cloud Service uses asset microservices — no custom workflow runners for processing
- Folder metadata schemas apply to all assets in the folder but don't override asset-level metadata
- Smart Tags require Adobe Sensei configuration and training for custom taxonomies
- Dynamic Media renditions are generated on-demand, not stored as traditional renditions
