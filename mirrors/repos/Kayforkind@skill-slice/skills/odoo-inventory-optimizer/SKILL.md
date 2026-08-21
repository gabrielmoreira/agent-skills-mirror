---
name: odoo-inventory-optimizer
description: "Configures Odoo 16+ Inventory: per-category FIFO or AVCO automated valuation, min/max replenishment, putaway locations, 2- and 3-step warehouse routes, and lot/serial tracking. Use when negative stock, broken cost layers, or Pick-Pack-Ship is the work. Do not use for QWeb report XML or purchase-pricelist setup."
version: 1.0.1
risk: safe
source: self
---

# Odoo Inventory Optimizer

## Overview

Production-grade guide for configuring and optimizing Odoo Inventory across valuation, replenishment, putaway, routing, and multi-step warehouse operations. Covers exact menu paths, hard rules to avoid data corruption, and verification steps for each configuration.

## When to Use

- Choosing or switching between FIFO and AVCO stock valuation per product category.
- Setting up minimum/maximum stock reordering rules to prevent stockouts.
- Designing multi-step warehouse flows (2-step receipt, 3-step delivery).
- Configuring putaway rules to route products to specific storage locations automatically.
- Troubleshooting negative stock, incorrect valuation, or missing stock moves.
- Enabling Lots/Serial Numbers for high-value or regulated items.

## Prerequisites

- Odoo 16+ with **Inventory** module installed.
- **Accounting** module required for automated inventory valuation (posts stock journal entries). Community Edition without Accounting cannot post stock journal entries.
- **Storage Locations** and **Multi-Step Routes** enabled in Inventory settings for putaway and multi-step flows.
- Manager-level access to Inventory → Configuration menus.
- Windows host (PowerShell) for any shell-based verification or XML-RPC scripting.

## Procedure

### 1. Enable Required Inventory Settings

```text
Menu: Inventory → Configuration → Settings

Enable: Storage Locations
Enable: Multi-Step Routes
```

Costing method is **not** set globally — it is set per Product Category (see step 2).

### 2. Configure FIFO or AVCO Stock Valuation

```text
Menu: Inventory → Configuration → Product Categories → Edit

  Category: All / Physical Goods
  Costing Method: First In First Out (FIFO)
  Inventory Valuation: Automated
  Account Stock Valuation: [Balance Sheet inventory account]
  Account Stock Input:   [Stock Received Not Billed]
  Account Stock Output:  [Stock Delivered Not Invoiced]
```

> **HARD RULE:** Do **not** switch costing method (FIFO ↔ AVCO) after transactions have been recorded. It produces incorrect historical cost data. Only change costing method on a fresh database or before any stock moves exist for that category.

### 3. Set Up a Min/Max Reordering Rule

```text
Menu: Inventory → Operations → Replenishment → New

Product: Office Paper A4
Location: WH/Stock
Min Qty: 100        (trigger reorder when stock falls below this)
Max Qty: 500        (purchase up to this quantity)
Multiple Qty: 50    (always order in multiples of 50)
Route: Buy          (triggers a Purchase Order automatically)
       or Manufacture (triggers a Manufacturing Order)
```

Set reordering rules on fast-moving items so purchase orders generate automatically. Review the Replenishment report periodically for stale rules.

### 4. Configure Putaway Rules

```text
Menu: Inventory → Configuration → Putaway Rules → New

  Product Category: Refrigerated Goods
    → Location: WH/Stock/Cold Storage

  Product: Laptop Model X
    → Location: WH/Stock/Electronics/Shelf A
```

Leave the Product field blank to apply the rule to an entire category. When a receipt is validated, Odoo automatically suggests the correct destination location per product or category.

### 5. Configure Multi-Step Warehouse Delivery

```text
Menu: Inventory → Configuration → Warehouses → [Your Warehouse]

Outgoing Shipments: Pick + Pack + Ship (3 steps)
```

Operations created automatically:

| Operation | Purpose |
|-----------|---------|
| PICK | Move goods from storage shelf to packing area |
| PACK | Package items and print shipping label |
| OUT | Hand off to carrier / mark as shipped |

For 2-step receipt (Receive → Quality → Store), set **Incoming Shipments** to the appropriate multi-step option on the same warehouse form.

### 6. Enable Lots/Serial Numbers

Use Lots/Serial Numbers for high-value or regulated items (medical devices, electronics). Enable per Product via the **Tracking** field (By Lot or By Serial Number).

> **Caution:** Serial number tracking at the individual unit level (SN per line) adds significant UI overhead. Test performance with large volumes before enabling broadly.

### 7. Run a Physical Inventory Adjustment

```text
Menu: Inventory → Operations → Physical Inventory
```

Run at least quarterly to correct stock drift.

> **HARD RULE:** Do **not** use "Update Quantity" to fix stock errors. Always use Inventory Adjustments to maintain a proper audit trail with stock move history.

## Pitfalls

- **Switching costing method post-transaction** — corrupts historical cost data. Never do this on a live category with existing stock moves.
- **Using "Update Quantity" instead of Inventory Adjustments** — bypasses the audit trail and hides the reason for the correction.
- **Mixing product categories with different costing methods in the same storage location** — creates valuation ambiguity; understand the impact before doing this.
- **Automated valuation without Accounting module** — stock journal entries will not post; ensure Accounting is installed.
- **Landed costs not covered here** — import duties and freight allocation require the `stock_landed_costs` module, which is out of scope for this skill.
- **Cross-warehouse transfers** — involve transit locations and intercompany invoicing complexities not fully covered here.
- **Serial number performance** — SN-per-line tracking can degrade UI responsiveness with high move volumes.

## Verification

### Verify Costing Method per Category

```text
Menu: Inventory → Configuration → Product Categories

Select category → confirm Costing Method and Inventory Valuation fields.
```

Expected: Costing Method = FIFO (or AVCO), Inventory Valuation = Automated, with all three stock accounts populated.

### Verify Reordering Rule Triggers

```text
Menu: Inventory → Operations → Replenishment

Reduce on-hand stock below Min Qty for a test product.
Confirm a replenishment request or draft PO appears.
```

Expected: A Purchase Order (Buy route) or Manufacturing Order (Manufacture route) is generated automatically.

### Verify Putaway Rule Application

```text
Menu: Inventory → Operations → Receipts

Create a receipt for a product with a putaway rule.
Validate the receipt and confirm the destination location matches the rule.
```

Expected: Destination location auto-populates to the configured bin (e.g., `WH/Stock/Cold Storage`).

### Verify Multi-Step Delivery Flow

```text
Menu: Inventory → Operations → Transfers

Create a delivery order for a warehouse with 3-step delivery enabled.
Confirm PICK, PACK, and OUT transfers are created in sequence.
```

Expected: Three linked transfers appear — PICK → PACK → OUT — each requiring validation before the next proceeds.

### Verify Stock Valuation Journal Entries

```text
Menu: Accounting → Journal Entries

Filter by Stock Valuation journal.
Confirm entries are posted on receipt and delivery validation.
```

Expected: Debit to Stock Valuation account on receipt, credit on delivery, with matching Stock Input/Output balancing entries.

## Related Skills

- **odoo-purchase-optimizer** — for vendor pricelists and PO automation tied to reordering rules.
- **odoo-manufacturing-mrp** — for Manufacturing Order generation from reordering rules with the Manufacture route.
