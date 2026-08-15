---
name: godot-inventory-system
version: 1.1.1
description: "Implements Godot 4.4+ bag systems with Resource ItemData, typed slots and stacking, leftover-aware add, equipment stat aggregation, signal-driven drag-and-drop UI, and id+quantity JSON saves. Use for backpack, paperdoll, or loot-grid work with editor-authored items. Not a one-item pickup helper and not Godot before 4.4; never assume this folder ships inventory helper scripts."
risk: safe
source: openrouter-deepsearch
date_added: 2026-06-16
---

# Inventory Systems in Godot 4.4+

All examples target **Godot 4.4+** (the current LTS as of 2026) and use the latest stable APIs. GDScript is shown first, then C#. Windows host with PowerShell is the primary development environment.

> **Related skills:** **resource-pattern** for custom Resource data containers, **save-load** for inventory serialization, **event-bus** for inventory change notifications, **hud-system** for inventory UI display.

---

## When to Use

Use this skill when building any inventory system in Godot 4.4+ that requires:
- Resource-based item definitions with editor integration
- Slot-based storage with stacking logic
- Equipment slots with stat aggregation
- UI binding with drag-and-drop support
- Serialization for save/load functionality
- Compatibility with Godot's new **TypedArray** and **TypedDictionary** generics (no need for legacy `Array` casts)

### Do Not Use

- Simple single-item pickup systems without slot management
- Non-Godot engines or Godot versions prior to 4.4
- Cases where items don't need to be Resources (e.g., purely procedural items with no editor authoring)
- Inventory systems requiring server-authoritative multiplayer synchronization without additional networking layers
- **Deprecated:** Using `Object.set_meta` for item data storage — switch to typed Resources as shown below
- **Security warning:** Never trust client-side inventory data in multiplayer; always validate on the server side

---

## Prerequisites

- Godot 4.4+ installed and accessible from PowerShell:
  ```powershell
  godot --version   # Expected output: 4.4.x-stable or higher
  ```
- Project initialized at `res://` with a standard directory structure:
  ```powershell
  # Recommended folders under the Godot project (res://): items/ for ItemData .tres, inventory/ for gameplay scripts
  ```
- Basic familiarity with Godot Resource system and `@tool`/`[Tool]` annotations
- For C#: .NET SDK installed and Godot with .NET support enabled

---

## Procedure

### Architecture Overview

```
┌─────────────────────────────────────────────────────────┐
│                        UI Layer                         │
│   InventoryUI (Control)                                 │
│     └─ GridContainer                                    │
│           └─ SlotUI × N (Button)                        │
│                 └─ TextureRect (icon) + Label (qty)     │
│                                                         │
│   Connects to: inventory_changed signal                 │
│   Drag-and-drop via _get_drag_data / _drop_data         │
└───────────────────────┬─────────────────────────────────┘
                        │ reads / mutates
┌───────────────────────▼─────────────────────────────────┐
│                    Inventory (Node)                      │
│   slots: TypedArray[InventorySlot]                      │
│   add_item(item, qty) → leftover: int                   │
│   remove_item(item, qty)                                │
│   has_item(item, qty) → bool                            │
│   get_item_count(item) → int                            │
│                                                         │
│   signals: inventory_changed                            │
│             item_added(item, quantity)                  │
│             item_removed(item, quantity)                │
└───────────────────────┬─────────────────────────────────┘
                        │ references
┌───────────────────────▼─────────────────────────────────┐
│                   Data Layer (Resources)                 │
│   ItemData (Resource)                                   │
│     id, name, description, icon, max_stack_size,        │
│     item_type enum                                      │
│                                                         │
│   InventorySlot (RefCounted)                            │
│     item: ItemData, quantity: int                       │
└─────────────────────────────────────────────────────────┘
```

### Step 1: Define ItemData Resource

Define items as Resources so they live in `.tres` files, are shareable across scenes, and benefit from full editor integration.

#### GDScript (Godot 4.4)

```gdscript
# res://inventory/item_data.gd
@tool
class_name ItemData
extends Resource

# Group exported properties for cleaner inspector
@export_group("Identification")
@export var id: String = ""
@export var name: String = ""

@export_group("Presentation")
@export var description: String = ""
@export var icon: Texture2D

@export_group("Gameplay")
@export var max_stack_size: int = 99
enum ItemType { CONSUMABLE, EQUIPMENT, MATERIAL, KEY_ITEM }
@export var item_type: ItemType = ItemType.MATERIAL
```

Create item assets: **res://items/potion_health.tres**, set `id = "potion_health"` etc. The `@tool` annotation enables live preview of changes in the editor.

#### C# (Godot 4.4)

```csharp
// res://inventory/ItemData.cs
using Godot;

[GlobalClass, Tool]
public partial class ItemData : Resource
{
    public enum ItemType
    {
        Consumable,
        Equipment,
        Material,
        KeyItem,
    }

    [ExportGroup("Identification")]
    [Export] public string Id { get; set; } = "";

    [ExportGroup("Identification")]
    [Export] public string Name { get; set; } = "";

    [ExportGroup("Presentation")]
    [Export] public string Description { get; set; } = "";

    [ExportGroup("Presentation")]
    [Export] public Texture2D Icon { get; set; }

    [ExportGroup("Gameplay")]
    [Export] public int MaxStackSize { get; set; } = 99;

    [ExportGroup("Gameplay")]
    [Export] public ItemType Type { get; set; } = ItemType.Material;
}
```

> Use `[GlobalClass]` so the Inspector dropdown shows `ItemData` as a resource type when creating `.tres` files. The `[Tool]` attribute mirrors the GDScript `@tool` flag.

### Step 2: Define InventorySlot

`InventorySlot` is a lightweight object tracking an item reference and its quantity. Define it as a `RefCounted` subclass (recommended for both GDScript and C#).

#### GDScript

```gdscript
# res://inventory/inventory_slot.gd
@tool
class_name InventorySlot
extends RefCounted

var item: ItemData = null
var quantity: int = 0

func is_empty() -> bool:
    return item == null or quantity <= 0

func can_stack(new_item: ItemData) -> bool:
    return not is_empty() and item == new_item and quantity < item.max_stack_size

# Adds amount to this slot, capped at max_stack_size.
# Returns the leftover that did not fit.
func add_to_stack(amount: int) -> int:
    if item == null:
        push_error("%s.add_to_stack called on empty slot".format(self))
        return amount
    var space := item.max_stack_size - quantity
    var to_add := min(amount, space)
    quantity += to_add
    return amount - to_add

# Removes amount from this slot. Clears the slot when quantity reaches zero.
func remove_from_stack(amount: int) -> void:
    quantity -= amount
    if quantity <= 0:
        quantity = 0
        item = null
```

#### C#

```csharp
// res://inventory/InventorySlot.cs
using Godot;

[Tool]
public partial class InventorySlot : RefCounted
{
    public ItemData Item { get; set; }
    public int Quantity { get; set; }

    public bool IsEmpty() => Item == null || Quantity <= 0;

    public bool CanStack(ItemData newItem) =>
        !IsEmpty() && Item == newItem && Quantity < Item.MaxStackSize;

    /// <summary>Adds amount to this slot. Returns leftover that did not fit.</summary>
    public int AddToStack(int amount)
    {
        if (Item == null)
        {
            GD.PushError($"{nameof(InventorySlot)}.{nameof(AddToStack)} called on empty slot");
            return amount;
        }
        int space = Item.MaxStackSize - Quantity;
        int toAdd = Mathf.Min(amount, space);
        Quantity += toAdd;
        return amount - toAdd;
    }

    /// <summary>Removes amount from this slot. Clears when quantity reaches zero.</summary>
    public void RemoveFromStack(int amount)
    {
        Quantity -= amount;
        if (Quantity <= 0)
        {
            Quantity = 0;
            Item = null;
        }
    }
}
```

### Step 3: Implement the Inventory Class

#### GDScript (TypedArray)

```gdscript
# res://inventory/inventory.gd
@tool
class_name Inventory
extends Node

signal inventory_changed
signal item_added(item: ItemData, quantity: int)
signal item_removed(item: ItemData, quantity: int)

@export var capacity: int = 20

# TypedArray provides compile-time type safety in Godot 4.4
var slots: TypedArray[InventorySlot] = TypedArray.new()

func _ready() -> void:
    slots.resize(capacity)
    for i in capacity:
        slots[i] = InventorySlot.new()

# Returns the number of items that could NOT be added (leftover).
func add_item(item: ItemData, quantity: int = 1) -> int:
    var remaining := quantity

    # Fill existing stacks first
    for slot in slots:
        if remaining <= 0:
            break
        if not slot.is_empty() and slot.item == item:
            remaining = slot.add_to_stack(remaining)

    # Open empty slots next
    for slot in slots:
        if remaining <= 0:
            break
        if slot.is_empty():
            slot.item = item
            remaining = slot.add_to_stack(remaining)

    var added := quantity - remaining
    if added > 0:
        item_added.emit(item, added)
        inventory_changed.emit()

    return remaining

func remove_item(item: ItemData, quantity: int = 1) -> void:
    var remaining := quantity

    for slot in slots:
        if remaining <= 0:
            break
        if not slot.is_empty() and slot.item == item:
            var removed := min(slot.quantity, remaining)
            slot.remove_from_stack(removed)
            remaining -= removed

    var actually_removed := quantity - remaining
    if actually_removed > 0:
        item_removed.emit(item, actually_removed)
        inventory_changed.emit()

func has_item(item: ItemData, quantity: int = 1) -> bool:
    return get_item_count(item) >= quantity

func get_item_count(item: ItemData) -> int:
    var total := 0
    for slot in slots:
        if not slot.is_empty() and slot.item == item:
            total += slot.quantity
    return total
```

#### C# (TypedArray)

```csharp
// res://inventory/Inventory.cs
using Godot;
using Godot.Collections;

[Tool]
public partial class Inventory : Node
{
    [Signal] public delegate void InventoryChangedEventHandler();
    [Signal] public delegate void ItemAddedEventHandler(ItemData item, int quantity);
    [Signal] public delegate void ItemRemovedEventHandler(ItemData item, int quantity);

    [Export] public int Capacity { get; set; } = 20;

    // TypedArray gives compile-time safety and better editor support
    public TypedArray<InventorySlot> Slots { get; private set; } = new();

    public override void _Ready()
    {
        for (int i = 0; i < Capacity; i++)
            Slots.Add(new InventorySlot());
    }

    /// <summary>Returns the number of items that could NOT be added (leftover).</summary>
    public int AddItem(ItemData item, int quantity = 1)
    {
        int remaining = quantity;

        // Fill existing stacks first
        foreach (var slot in Slots)
        {
            if (remaining <= 0) break;
            if (!slot.IsEmpty() && slot.Item == item)
                remaining = slot.AddToStack(remaining);
        }

        // Open empty slots next
        foreach (var slot in Slots)
        {
            if (remaining <= 0) break;
            if (slot.IsEmpty())
            {
                slot.Item = item;
                remaining = slot.AddToStack(remaining);
            }
        }

        int added = quantity - remaining;
        if (added > 0)
        {
            EmitSignal(SignalName.ItemAdded, item, added);
            EmitSignal(SignalName.InventoryChanged);
        }

        return remaining;
    }

    public void RemoveItem(ItemData item, int quantity = 1)
    {
        int remaining = quantity;

        foreach (var slot in Slots)
        {
            if (remaining <= 0) break;
            if (!slot.IsEmpty() && slot.Item == item)
            {
                int removed = Mathf.Min(slot.Quantity, remaining);
                slot.RemoveFromStack(removed);
                remaining -= removed;
            }
        }

        int actuallyRemoved = quantity - remaining;
        if (actuallyRemoved > 0)
        {
            EmitSignal(SignalName.ItemRemoved, item, actuallyRemoved);
            EmitSignal(SignalName.InventoryChanged);
        }
    }

    public bool HasItem(ItemData item, int quantity = 1) => GetItemCount(item) >= quantity;

    public int GetItemCount(ItemData item)
    {
        int total = 0;
        foreach (var slot in Slots)
            if (!slot.IsEmpty() && slot.Item == item)
                total += slot.Quantity;
        return total;
    }
}
```

### Step 4: Equipment Extension

Add equipment slots (`HEAD`, `CHEST`, `WEAPON`, etc.) by extending the `Inventory` class with a typed slot map. Stat aggregation runs by summing `ItemData.stats` across equipped items; signal `equipment_changed` is emitted when slots change.

> **Load `references/equipment.md`** when implementing equipment slots. It contains the full GDScript and C# `Equipment` class with `EquipmentSlotType` enum, equip/unequip API, and stat aggregation. The implementation uses `TypedDictionary[EquipmentSlotType, InventorySlot]` for compile-time safety.

### Step 5: UI Binding

Slot-grid UI: a `GridContainer` of `Panel` slot widgets, each rendering one `InventorySlot`. Drag-and-drop uses `_get_drag_data`, `_can_drop_data`, and `_drop_data` on the slot widget. The Inventory emits `inventory_changed`; the UI re-renders only the affected slots (no per-frame polling).

> **Load `references/ui-binding.md`** when building the inventory UI. It contains the full GDScript and C# slot widget (drag/drop, hover preview), inventory grid layout, and tooltip wiring. Updated to use Godot 4.4's `Control.mouse_entered`/`mouse_exited` signals for hover handling.

### Step 6: Serialization

Persist Inventory + Equipment as a `TypedDictionary` keyed by the **resource path** of each `ItemData`. Versioning is handled via a top-level `version` field to allow future migrations.

```gdscript
# res://inventory/serialization.gd (GDScript)
func save_inventory(path: String) -> void:
    var data := {
        "version": 2,
        "slots": []
    }
    for slot in slots:
        if slot.is_empty():
            continue
        data["slots"].append({
            "id": slot.item.id,
            "quantity": slot.quantity
        })
    var file = FileAccess.open(path, FileAccess.WRITE)
    file.store_string(JSON.stringify(data))
    file.close()
```

```csharp
// res://inventory/Serialization.cs (C#)
using Godot;
using Godot.Collections;

public partial class InventorySerializer : RefCounted
{
    public void SaveInventory(string path, TypedArray<InventorySlot> slots)
    {
        var dict = new Dictionary
        {
            ["version"] = 2,
            ["slots"] = new Array()
        };
        foreach (var slot in slots)
        {
            if (slot.IsEmpty()) continue;
            dict["slots"].As<Array>().Add(new Dictionary
            {
                ["id"] = slot.Item.Id,
                ["quantity"] = slot.Quantity
            });
        }
        var file = FileAccess.Open(path, FileAccess.ModeFlags.Write);
        file.StoreString(JSON.Print(dict));
        file.Close();
    }
}
```

> **Load `references/serialization.md`** when implementing save/load. It contains a detailed migration guide for versioned JSON payloads and the `ItemRegistry` pattern for loading items at startup.

---

## Pitfalls

1. **Never use `Object.set_meta` for item data storage** — this is deprecated. Use typed `Resource` subclasses as shown above.
2. **Never trust client-side inventory data in multiplayer** — always validate on the server side before applying changes.
3. **`Inventory.add_item()` returns leftover count** — callers must handle a full inventory (leftover > 0 means items didn't fit).
4. **UI must never poll per-frame** — all updates are driven by the `inventory_changed` signal.
5. **`InventorySlot.remove_from_stack()` must clear `item` to `null`** when quantity reaches 0, otherwise stale references persist.
6. **Equipment slots must be keyed by `EquipmentSlotType` enum, not by string** — string keys allow typos that fail silently at runtime.
7. **`max_stack_size = 1` on `EQUIPMENT` and `KEY_ITEM` types** to prevent stacking.
8. **Serialization stores `id + quantity` only** — never serialize full `ItemData` objects or resource paths, as paths break when files move.
9. **All `push_error()` / `GD.PushError` messages must include the class name and method** for easy tracing.
10. **Do not use deprecated `Array` without generics** — Godot 4.4+ provides `TypedArray` and `TypedDictionary` for compile-time safety.
11. **`Equipment.get_total_stat()` should be called when stats are needed**, not cached unless profiling demands it.
12. **Drag-and-drop must swap slot contents directly then emit `inventory_changed` once** — avoid multiple signal emissions per swap.

---

## Verification

Run through this checklist to verify a correct implementation:

- [ ] `ItemData` extends `Resource` with a stable `id` string set in the Inspector
- [ ] `ItemData` files live under `res://items/` and are committed to version control
- [ ] `Inventory.add_item()` returns leftover count; callers handle a full inventory
- [ ] `inventory_changed` signal drives all UI updates — UI never polls per-frame
- [ ] `InventorySlot.remove_from_stack()` clears `item` to `null` when quantity reaches 0
- [ ] Equipment slots keyed by `EquipmentSlotType` enum, not by string, to catch typos at compile time
- [ ] `Equipment.get_total_stat()` is called when stats are needed, not cached unless profiling demands it
- [ ] Serialization stores `id + quantity` only — never full `ItemData` objects or resource paths
- [ ] `ItemRegistry` loads items at startup; all deserialization goes through it
- [ ] Drag-and-drop swaps slot contents directly then emits `inventory_changed` once
- [ ] `max_stack_size = 1` on `EQUIPMENT` and `KEY_ITEM` types to prevent stacking
- [ ] All `push_error()` / `GD.PushError` messages include the class name and method for easy tracing
- [ ] Run the test suite to verify add/remove/stacking logic
- [ ] Verify UI updates correctly on `inventory_changed` signal
- [ ] Test serialization round-trip with version migration
- [ ] Ensure no deprecated APIs (e.g., `Array` without generics) are used
- [ ] Security check: inventory data received from network is validated against server-side state before applying changes

### Quick Smoke Test (PowerShell)

```powershell
# Verify Godot version
godot --version

# Open project to check for script errors
godot --editor --quit

# Run all tests (if using GUT or similar)
godot --headless --script res://tests/run_tests.gd
```

Expected: no script errors in the Output panel; all tests pass with exit code 0.

---

## Related Skills

- **resource-pattern** — for custom Resource data containers
- **save-load** — for inventory serialization
- **event-bus** — for inventory change notifications
- **hud-system** — for inventory UI display
