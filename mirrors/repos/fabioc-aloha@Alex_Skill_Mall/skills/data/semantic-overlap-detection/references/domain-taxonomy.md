# Domain Taxonomy

A framework for classifying semantic model columns into domains that may overlap. The taxonomy is **structural, not domain-specific** — adapt the domain names and examples to the actual model being analyzed.

## How to Use This Taxonomy

1. Read the model's table and column names
2. For each non-hidden string/categorical column, identify which **structural domain category** it belongs to
3. Give it a domain ID using the pattern `CATEGORY-SPECIFICITY` (e.g., `GEO-REGION`, `ORG-REGIONAL`, `PRODUCT-CATEGORY`)
4. Assign a **concept question** — the short user question this column answers (see each category below)
5. Columns sharing a domain category are candidates for overlap analysis
6. Columns sharing the **same concept question but different root concepts** are Class A (Competing Classifications) candidates — this catches overlaps that word-stem matching misses

## Concept Questions

Each domain category defines one or more **concept questions** — the questions a user would ask that could route to columns in this category. Concept questions are the key input to Pass 5f (Competing Classifications) in Phase 1.

| Concept Question | Domain Category | Competing Roots (examples) |
|---|---|---|
| Where geographically? | Geographic / Location | Country, Region, Area, Territory, Market, Sales Region, Customer Region |
| What org unit? | Organizational / Structural | Region, District, Division, Store Group, Market |
| What kind of org? | Organizational / Structural | Sales Channel, Distribution Channel, Store Type |
| What type/category? | Classification / Type | Product Category, Product Line, Store Department, Product Family |
| What sales channel? | Classification / Type | Channel, Sales Channel, Distribution Channel, Order Type |
| What customer segment? | Classification / Type | Customer Tier, Customer Segment, Account Type, Customer Class |
| What level/grade? | Measurement / Level | Discount Band, Discount Tier, Price Level, Discount Level |
| Which person/entity? | Identity / Naming | Customer Name, Account Label, Store Name, Product Display Name |
| Which identifier? | Identity / Naming | Customer ID, Product SKU, Order Number, Account Code |
| What demographic? | Demographic / Protected | Customer Age Group, Customer Gender, Loyalty Tier |
| What time period? | Time / Temporal | Calendar Year, Fiscal Quarter, Order Month |

## Structural Domain Categories

### Geographic / Location

Columns that classify entities by physical location, territory, or jurisdiction.

**Concept question**: "Where geographically?"

**Common hierarchy pattern**: Region → Sub-region → Country → State → Metro → City → Building

**Overlap risk**: High. Most models have 2+ independent geo classification systems (e.g., entity location vs sales territory vs legal entity).

| Domain ID pattern | What it captures | Overlap signal |
|---|---|---|
| `GEO-REGION` | Broadest geo grouping | Multiple tables may have different regional groupings |
| `GEO-COUNTRY` | Country-level | Legal entity country vs physical location country |
| `GEO-STATE` | State/province | State names collide with city names |
| `GEO-CITY` | City hierarchy (detail → summary → group) | Values can appear at multiple hierarchy levels |
| `GEO-CAMPUS` | Physical facility / site / building | Overlaps with city-level columns |
| `GEO-TERRITORY` | Sales / commercial territory | Independent from entity-location geo |

**Key overlap pattern**: The same geographic value appears in an entity-level system and an organizational-unit-level system that classify geography differently.

**Physical vs Legal/Jurisdictional distinction**: Many models have two independent geo systems on the same entity — physical location (where goods are shipped) and legal entity location (which legal entity is invoiced). These can diverge: a customer with `Ship-To City` = "Dublin" may have `Bill-To Country` = "United States" if their billing entity is US-based. Watch for modifier pairs like `Ship-To X` vs `Bill-To X`, `Warehouse X` vs `Store X`, or `Physical X` vs `Entity X` — these are Class A (Competing Classifications), not duplicates.

### Organizational / Structural

Columns that classify entities by organizational structure, hierarchy, or grouping.

**Concept questions**: "What org unit?" / "What kind of org?"

**Common hierarchy pattern**: Division → Region → District → Store, often with parallel Regional and Channel cuts

**Overlap risk**: High. Star schemas frequently have 2+ org hierarchies on the same dimension table.

| Domain ID pattern | What it captures | Overlap signal |
|---|---|---|
| `ORG-REGIONAL` | Regional sales hierarchy | Parallel to ORG-CHANNEL, values may overlap |
| `ORG-CHANNEL` | Channel-based org hierarchy | Parallel to ORG-REGIONAL |
| `ORG-EXTERNAL` | Separate org dimension table (e.g., distributor hierarchy) | Third independent system |
| `ORG-FUNCTION` | Functional classification of org units (e.g., store department) | Overlaps with product-level classification |

**Key overlap pattern**: A region or district name exists at different levels across parallel hierarchies (sales region vs distribution region), and the user doesn't know which hierarchy to query.

### Classification / Type

Columns that classify the primary entity (person, product, account, etc.) into categories.

**Concept questions**: "What type/category?" / "What sales channel?" / "What customer segment?"

**Common hierarchy pattern**: Family → Category → Subcategory → Detail

**Overlap risk**: Very high when classification exists at both the entity level and the organizational-unit level.

| Domain ID pattern | What it captures | Overlap signal |
|---|---|---|
| `CLASS-BROAD` | Broadest entity classification | e.g., product line, customer segment |
| `CLASS-SPECIFIC` | Specific entity classification | e.g., product subcategory, customer tier |
| `CLASS-UNIT` | Classification of the org unit, not the entity | e.g., store department, warehouse zone |
| `CLASS-CHANNEL` | Sales or distribution channel | e.g., channel, order type, distribution type |
| `CLASS-TITLE` | Display name / label | e.g., product display name, account label |
| `CLASS-ROLE` | System-internal classification | e.g., internal SKU, account code |

**Key overlap pattern**: A value could be a product's own classification (CLASS-BROAD/SPECIFIC) OR the classification of the store/department the product is sold in (CLASS-UNIT). The user's intent determines which is correct.

**Cross-cutting subfamily — Product Identity / Classification**: In retail and sales models, several columns across different tables answer "what is this product?" at different levels or from different perspectives: product display name (customer-facing), product SKU (internal identifier), product category (functional grouping), product line (broader portfolio track), and derived mappings (e.g., `Product Category Mapping`). These span multiple tables and classification systems but form a single overlap family. Classify each as CLASS-BROAD, CLASS-SPECIFIC, or CLASS-ROLE depending on its granularity, and ensure they cross-reference each other in descriptions.

### Measurement / Level

Columns that represent a graded attribute at multiple granularities.

**Concept question**: "What level/grade?"

**Common hierarchy pattern**: Exact value → Grouped band → Named summary → Numeric representation

**Overlap risk**: Medium. Within-hierarchy only — rarely cross-table.

| Domain ID pattern | What it captures | Overlap signal |
|---|---|---|
| `LEVEL-EXACT` | Individual value | "10%", "Premium", "$50" |
| `LEVEL-GROUP` | Grouped band | "10-20%", "$50-$100" |
| `LEVEL-SUMMARY` | Named band | "High Discount", "Premium Tier", "Enterprise" |
| `LEVEL-NUMERIC` | Sortable numeric representation | Redundant with LEVEL-EXACT |
| `LEVEL-STAGE` | Lifecycle stage | Order stage, fulfillment status |

**Key overlap pattern**: User says a value that exists in both LEVEL-EXACT and LEVEL-NUMERIC, or a name that could be LEVEL-SUMMARY or LEVEL-STAGE.

### Identity / Naming

Columns that identify specific entity instances by name, code, or identifier.

**Concept questions**: "Which person/entity?" / "Which identifier?"

**Common pattern**: Code → Display Name → Full Name, with role variants (ship-to vs bill-to)

**Overlap risk**: Low for disambiguation (entity context resolves most cases), but high for column count.

| Domain ID pattern | What it captures | Overlap signal |
|---|---|---|
| `ID-CODE` | System identifier | Customer ID, Product SKU, Order Number |
| `ID-NAME` | Display name | Customer Name, Product Name, Store Name |
| `ID-VARIANT` | Role-based variant | Ship-To Name, Bill-To Name, Sold-To Name |

**Key overlap pattern**: Usually resolvable from entity context. Exclude from disambiguation analysis per Phase 1 step 5b.

### Demographic / Protected Attribute

Columns containing protected-class or demographic attributes.

**Concept question**: "What demographic?"

| Domain ID pattern | What it captures | Overlap signal |
|---|---|---|
| `DEMO-ATTR` | Demographic attribute | Customer Age Group, Customer Gender |
| `DEMO-GROUP` | Group membership | Loyalty tier, customer segment |
| `DEMO-REGIONAL` | Region-specific variant | e.g., US-specific vs global classification |

**Key overlap pattern**: Same attribute on multiple tables via different security bridges (Class D).

### Time / Temporal

Columns representing time periods, fiscal periods, or temporal classifications.

**Concept question**: "What time period?"

| Domain ID pattern | What it captures | Overlap signal |
|---|---|---|
| `TIME-CALENDAR` | Calendar period | Calendar Year Month, Order Month |
| `TIME-FISCAL` | Fiscal period | Fiscal Year, Fiscal Quarter |
| `TIME-CLASS` | Period classification | "Most Recent", "Current Year", "YTD" |

**Key overlap pattern**: Time columns rarely cause disambiguation problems — agent context (trending vs snapshot) usually resolves them.

---

## Cross-Category Collision Matrix

The hardest disambiguation problems occur when a single user value maps to columns in **different domain categories**:

| Category A | Category B | Why it collides |
|---|---|---|
| **GEO-REGION** (entity table) | **GEO-TERRITORY** (org-unit table) | Same geographic name, different classification system |
| **GEO-COUNTRY** | **GEO-REGION** | Country name is also a sub-region value |
| **GEO-STATE** | **GEO-CITY** | A state name is also a city name |
| **CLASS-BROAD** | **ORG-FUNCTION** | A product classification is also a store department name |
| **CLASS-SPECIFIC** | **CLASS-TITLE** | A product subcategory is also a product display name pattern |
| **CLASS-BROAD** | **CLASS-CHANNEL** | A product line is also a sales channel category |
| **LEVEL-EXACT** | **LEVEL-NUMERIC** | Same values in two columns |
| **DEMO-ATTR** (table A) | **DEMO-ATTR** (table B) | Same column via different security paths |
| **ORG-REGIONAL** | **ORG-CHANNEL** | Same org name at different hierarchy cut points |

When you find a collision pair, classify it into one of the [5 ambiguity classes](./ambiguity-classes.md) and generate the appropriate artifacts. Use the concept questions to systematically identify Class A competitors — columns from different categories that answer the same user question.
