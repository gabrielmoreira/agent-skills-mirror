# Ontology Workflows (Detailed)

## Table of Contents

- [From OneLake](#from-onelake)
- [From Semantic Model](#from-semantic-model)
- [Data Agent Integration](#data-agent)
- [Time Series Data Binding](#time-series-binding)
- [Preview Experience and Graph Queries](#preview-experience)
- [REST API Operations](#rest-api-operations)

---

## From OneLake

Complete workflow for creating an ontology manually from OneLake data.

### Step 1: Create the Ontology Item

1. In your Fabric workspace, select **+ New item**
2. Search for and select **Ontology (preview)**
3. Enter a name (letters, numbers, underscores only — no spaces or dashes)
4. Select **Create**

> If you see an error, verify all [required tenant settings](./tenant-settings.md#required-tenant-settings).

### Step 2: Create Entity Types

1. Select **Add entity type** from the ribbon or center canvas
2. Enter an entity type name (1-26 chars, alphanumeric + hyphens + underscores)
3. The **Entity type configuration** pane opens

> **Tip**: Avoid GQL reserved words. For example, use `Products` (plural) instead of `Product`.

### Step 3: Bind Static Data

1. In the Entity type configuration pane, switch to the **Bindings** tab
2. Select **Add data to entity type**
3. Choose a OneLake data source (lakehouse or eventhouse) and select **Connect**
4. Select a table and select **Next**
5. For **Binding type**, select **Static**
6. Under **Bind your properties**, map source columns to property names
7. Select **Save**

### Step 4: Set Entity Type Key

1. Back in the Entity type configuration pane, select **Add entity type key**
2. Choose one or more properties that uniquely identify each record
3. Select **Save**

> Only string and integer columns are available as entity type keys.

### Step 5: Create Relationship Types

1. Select **Add relationship** from the ribbon
2. Enter the **Relationship type name** (e.g., "has", "drives", "soldIn")
3. Select **Source entity type** and **Target entity type** (must be different)
4. Select **Add relationship type**
5. In the **Relationship configuration** pane:
   - Select the **Source data** (workspace, lakehouse, and linking table)
   - For each entity type, map the **Source column** that identifies instances
   - The source columns must match the entity type keys
6. Select **Create**

### Step 6: Repeat for All Entity Types

Create all required entity types, bindings, and relationships following the same pattern.

---

## From Semantic Model

Complete workflow for generating an ontology from a Power BI semantic model.

### Step 1: Generate the Ontology

1. Navigate to your semantic model in Fabric
2. From the ribbon, select **Generate Ontology**
3. Select your **Workspace** and enter a **Name**
4. Select **Create**

> The semantic model must not be in "My workspace". Tables must be visible (not hidden) with relationships defined.

### Step 2: Verify Entity Types

1. In the **Entity Types** pane, check that each expected entity type was created
2. Verify properties match your semantic model columns

### Step 3: Verify Data Bindings

1. Select each entity type and switch to the **Bindings** tab
2. Confirm source tables are correctly mapped
3. Verify entity type keys are set

### Step 4: Configure Relationship Types

Relationships imported from the semantic model may be defined but not fully configured:

1. Select each relationship type on the canvas
2. Update the relationship details:
   - **Source data** table
   - **Source column** for source entity type
   - **Source column** for target entity type
3. Select **Update**

### Semantic Model Mode Support

| Feature | Direct Lake | DirectQuery | Import |
|---------|:-----------:|:-----------:|:------:|
| Generate ontology | Yes | Yes | Yes |
| Auto data binding | Yes | Yes | No |
| Manual data binding | Yes | No | No |

---

## Data Agent

Complete workflow for connecting an ontology to a Fabric data agent.

### Prerequisites

- Data agent item types (preview) tenant setting enabled
- Copilot and Azure OpenAI tenant settings enabled (3 settings)
- A fully configured ontology with entity types, data bindings, and relationships

### Step 1: Create a Data Agent

1. In your Fabric workspace, select **+ New item**
2. Search for and select **Data agent**
3. Name the agent and select **Create**

### Step 2: Add Ontology as Source

1. In the data agent configuration, add a **knowledge source**
2. Select your ontology item

### Step 3: Provide Agent Instructions

Add instructions to improve agent behavior:

```text
Support group by in GQL
```

This instruction enables better aggregation in ontology queries.

### Step 4: Test the Agent

1. Open the agent chat
2. Ask questions using your business vocabulary (entity type names, relationships)
3. Verify the agent uses ontology terminology consistently

### remediate Agent Queries

| Issue | Solution |
|-------|----------|
| First queries fail | Wait a few minutes for agent initialization, then retry |
| Results don't aggregate | Add `Support group by in GQL` instruction |
| Vague or generic results | Ensure ontology is added as knowledge source; verify entity/relationship names |

---

## Time Series Binding

Workflow for binding time series data (e.g., sensor telemetry) to entity types.

### Step 1: Prepare Time Series Data

- Data must be in **columnar format**: one row per timestamped observation
- Columns include: timestamp, property values (e.g., temperature, pressure)
- Data can be in OneLake or an eventhouse

### Step 2: Add Time Series Binding

1. Select the entity type and go to the **Bindings** tab
2. Select **Add data to entity type**
3. Choose your data source and table
4. For **Binding type**, select **Time series**
5. Select the **Timestamp column**
6. Map source columns to properties
7. Select **Save**

---

## Preview Experience

Using the ontology preview experience to explore data and graphs.

### Access the Preview

1. In the **Entity Types** pane, select an entity type
2. Select **Entity type overview** from the menu ribbon
3. The preview experience opens with data tiles and graphs

### Explore Data

- **View tiles**: Line charts and configurable tiles with time slices
- **Graph view**: Select **Expand** on a graph tile to see entity instances in Graph
- **Entity instances**: Browse specific instances for detailed information

### Query Across Instances

1. In the graph view, use the **Query builder** ribbon
2. The default query shows entities one hop away
3. Select **Run query** to execute
4. **Add filters** for property values or change **Components** in the graph
5. Switch view types: **Diagram**, **Card**, or **Table**

### Open in Fabric Graph

For more complex queries, select **Open in Fabric Graph** to access the full Graph in Microsoft Fabric interface.

### Refresh Data

Updates in upstream data sources require manual refresh before they appear in the ontology. Use the **Refresh** option in the preview experience to pull latest data.

---

## REST API Operations

### Create an Ontology Item via REST API

```powershell
# Authenticate
$token = (Get-AzAccessToken -ResourceUrl "https://api.fabric.microsoft.com").Token
$headers = @{ "Authorization" = "Bearer $token"; "Content-Type" = "application/json" }

# Create ontology
$body = @{
    displayName = "MyOntology"
    type        = "Ontology"
} | ConvertTo-Json

$workspaceId = "your-workspace-id"
$uri = "https://api.fabric.microsoft.com/v1/workspaces/$workspaceId/items"

Invoke-RestMethod -Uri $uri -Method Post -Headers $headers -Body $body
```

### List Ontology Items

```powershell
$uri = "https://api.fabric.microsoft.com/v1/workspaces/$workspaceId/items?type=Ontology"
$items = Invoke-RestMethod -Uri $uri -Method Get -Headers $headers
$items.value | Format-Table displayName, id, type
```

### Delete an Ontology Item

```powershell
$itemId = "your-ontology-item-id"
$uri = "https://api.fabric.microsoft.com/v1/workspaces/$workspaceId/items/$itemId"
Invoke-RestMethod -Uri $uri -Method Delete -Headers $headers
```

### Using Fabric CLI

```bash
fab auth login
fab item list --workspace "YourWorkspace" --type Ontology
fab item create --workspace "YourWorkspace" --type Ontology --name "MyOntology"
```
