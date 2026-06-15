---
name: unit-conversion-get-units
api: Unit Conversion
method: GET
path: /v1/technology/convert/units
base_url: https://api.requiems.xyz
description: Returns all available unit conversion types grouped by measurement category
---

## Endpoint

**GET https://api.requiems.xyz/v1/technology/convert/units**

## List Available Units

Returns all available unit conversion types grouped by measurement category

## Response Example

```json
{
  "data": {
    "length": ["cm", "ft", "in", "km", "m", "miles", "mm", "nmi", "yd"],
    "weight": ["g", "kg", "lb", "mg", "oz", "stone", "t"],
    "volume": ["cup", "fl_oz", "gal", "l", "ml", "pt", "qt", "tbsp", "tsp"],
    "temperature": ["c", "f", "k"],
    "area": ["acre", "cm2", "ft2", "ha", "in2", "km2", "m2", "mm2", "yd2"],
    "speed": ["km_h", "knots", "m_s", "mph"]
  },
  "metadata": {
    "timestamp": "2026-01-01T00:00:00Z"
  }
}
```

## Response Fields

| Field | Type | Description |
| ----- | ---- | ----------- |
| `length` | array | Available length units: millimeter (mm), centimeter (cm), meter (m), kilometer (km), inch (in), foot (ft), yard (yd), mile (miles), nautical mile (nmi) |
| `weight` | array | Available weight units: milligram (mg), gram (g), kilogram (kg), metric ton (t), ounce (oz), pound (lb), stone (stone) |
| `volume` | array | Available volume units: milliliter (ml), liter (l), teaspoon (tsp), tablespoon (tbsp), fluid ounce (fl_oz), cup (cup), pint (pt), quart (qt), gallon (gal) |
| `temperature` | array | Available temperature units: celsius (c), fahrenheit (f), kelvin (k) |
| `area` | array | Available area units: square millimeter (mm2), square centimeter (cm2), square meter (m2), square kilometer (km2), square inch (in2), square foot (ft2), square yard (yd2), acre (acre), hectare (ha) |
| `speed` | array | Available speed units: meters per second (m_s), kilometers per hour (km_h), miles per hour (mph), knots (knots) |
