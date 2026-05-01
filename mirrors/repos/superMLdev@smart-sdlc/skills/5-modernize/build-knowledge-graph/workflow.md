# build-knowledge-graph — Workflow

> 🏛️ "A knowledge graph is the bridge between legacy code and the new system. It captures what the business NEEDS, stripped of how the legacy system happened to implement it."

## Why This Matters

Legacy code mixes two things that should never be mixed:
1. **Business logic** — what the business needs to be true (NEEDS to be preserved)
2. **Implementation artifacts** — how COBOL/JCL/DB2 happened to store it (CAN be discarded)

A COBOL program called `ORDVALD` that validates orders in 500 lines is not the thing to preserve. The business rules it enforces — "orders over $10,000 need manager approval", "customers on credit hold cannot place orders" — are what survive modernization.

The knowledge graph captures only the business rules. The COBOL is discarded.

## Supported Input Sources

| Source | Step |
|--------|------|
| Legacy code inventory (`_superml/legacy-inventory/`) | All steps |
| Functional specification documents (text/markdown) | Step 01 |
| Data dictionaries from business | Step 01 |
| Domain expert conversation | Steps 01–03 |
| Process diagrams (described in text) | Step 03 |

## Activation Questions

Before starting, confirm:

> "I'm ready to build the knowledge graph from the legacy code analysis.
> 
> A few questions before I start:
> 1. What is the **name of this business domain**? (e.g., 'Order Management', 'Policy Administration', 'Trade Settlement')
> 2. Do you have any **additional documents** to include beyond the code analysis?
> 3. Are there **domain terms** in this system that have specific meanings I should know about?
> 4. Should I stop after each entity group for your review, or build the complete graph in one pass?"

## Step Sequence

| Step | File | What happens |
|------|------|-------------|
| 1 | `steps/step-01-extract-entities.md` | Find domain entities from data structures + program analysis |
| 2 | `steps/step-02-map-business-rules.md` | Extract and categorize all business rules |
| 3 | `steps/step-03-map-processes.md` | Trace end-to-end business processes |
| 4 | `steps/step-04-generate-graph.md` | Assemble complete knowledge graph |

⏸️ **STOP after activation questions.** Wait for user confirmation before starting Step 1.

Load and follow `./steps/step-01-extract-entities.md`.
