# Reorder Point Examples

## Example 1: Same Time Unit

Inputs:

- Item: corrugated case SKU A
- Average demand: 25 cases per day
- Lead time: 8 days
- Safety stock: 60 cases
- Rounding: whole cases

Calculation:

```text
demand during lead time = 25 cases/day * 8 days = 200 cases
ROP = 200 cases + 60 cases = 260 cases
```

Expected output:

```text
Reorder point: 260 cases
```

## Example 2: Time Unit Conversion

Inputs:

- Item: replacement part SKU B
- Average demand: 140 units per week
- Lead time: 10 days
- Safety stock: 90 units
- Rounding: whole units

Calculation:

```text
lead time in weeks = 10 / 7 = 1.428571 weeks
demand during lead time = 140 units/week * 1.428571 weeks = 200 units
ROP = 200 units + 90 units = 290 units
```

Expected output:

```text
Reorder point: 290 units
```

## Example 3: Missing Safety Stock

Inputs:

- Item: component SKU C
- Average demand: 12 units per day
- Lead time: 5 days
- Safety stock: missing

Calculation:

```text
demand during lead time = 12 units/day * 5 days = 60 units
```

Expected behavior:

```text
Lead-time demand is 60 units. A final reorder point needs safety stock or an
approved assumption that safety stock is zero.
```

## Example 4: Inventory Position Comparison

Inputs:

- Item: label roll SKU D
- Average demand: 18 rolls per day
- Lead time: 6 days
- Safety stock: 40 rolls
- On hand: 120 rolls
- On order: 20 rolls
- Allocated/backordered: 10 rolls

Calculation:

```text
demand during lead time = 18 rolls/day * 6 days = 108 rolls
ROP = 108 rolls + 40 rolls = 148 rolls
inventory position = 120 rolls + 20 rolls - 10 rolls = 130 rolls
```

Expected output:

```text
Reorder point: 148 rolls
Inventory position: 130 rolls
Reorder signal: yes
```

## Example 5: Negative Input

Inputs:

- Average demand: -5 units per day
- Lead time: 4 days
- Safety stock: 20 units

Expected behavior:

```text
Cannot calculate a reorder point because average demand cannot be negative.
Ask for corrected demand input.
```
