---
name: "co2-estimation"
description: "Calculate carbon footprint of construction projects. Estimate CO2 emissions from materials, transportation, and construction processes using emission factors databases."
homepage: "https://datadrivenconstruction.io"
metadata: {"openclaw": {"emoji": "🎬", "os": ["darwin", "linux", "win32"], "homepage": "https://datadrivenconstruction.io", "requires": {"bins": ["python3"]}}}
---
# CO2 Estimation for Construction

## Overview

Based on DDC methodology (Chapter 3.3), this skill provides comprehensive CO2 and carbon footprint calculations for construction projects. Sustainability is no longer optional - clients and regulations demand accurate environmental impact assessments.

**Book Reference:** "4D, 6D-8D и расчет CO2" / "4D-8D BIM and CO2 Calculation"

> "Расчет углеродного следа становится обязательным требованием для многих проектов. BIM-модель содержит все необходимые данные для автоматизации этого процесса."
> — DDC Book, Chapter 3.3

## Quick Start

```python
import pandas as pd

# Load BIM elements with materials
df = pd.read_excel("bim_elements.xlsx")

# CO2 emission factors (kg CO2 per unit)
emission_factors = {
    'Concrete': 0.13,      # kg CO2 per kg
    'Steel': 1.85,         # kg CO2 per kg
    'Brick': 0.24,         # kg CO2 per kg
    'Timber': -1.6,        # negative = carbon sink
    'Glass': 0.85,         # kg CO2 per kg
    'Aluminum': 8.14       # kg CO2 per kg
}

# Calculate emissions
df['CO2_kg'] = df.apply(
    lambda row: row['Weight_kg'] * emission_factors.get(row['Material'], 0),
    axis=1
)

total_co2 = df['CO2_kg'].sum()
print(f"Total Carbon Footprint: {total_co2:,.0f} kg CO2")
print(f"Equivalent: {total_co2/1000:,.1f} tonnes CO2")
```

## Emission Factors Database

### Material Emission Factors (Embodied Carbon)

```python
# Comprehensive emission factors database (kg CO2e per kg material)
EMISSION_FACTORS_KG = {
    # Concrete and cement
    'Concrete_C20': 0.10,
    'Concrete_C30': 0.13,
    'Concrete_C40': 0.16,
    'Concrete_C50': 0.19,
    'Cement_Portland': 0.83,
    'Mortar': 0.20,

    # Metals
    'Steel_Reinforcing': 1.85,
    'Steel_Structural': 1.55,
    'Steel_Recycled': 0.47,
    'Aluminum_Primary': 8.14,
    'Aluminum_Recycled': 0.52,
    'Copper': 2.71,

    # Masonry
    'Brick_Clay': 0.24,
    'Brick_Concrete': 0.12,
    'Stone_Natural': 0.06,
    'Block_Concrete': 0.10,

    # Wood (negative = carbon sequestration)
    'Timber_Softwood': -1.60,
    'Timber_Hardwood': -1.40,
    'Plywood': 0.45,
    'CLT': -1.20,          # Cross-Laminated Timber
    'Glulam': -1.10,

    # Insulation
    'Insulation_Mineral': 1.20,
    'Insulation_EPS': 3.29,
    'Insulation_XPS': 3.45,
    'Insulation_Cellulose': 0.10,

    # Glass
    'Glass_Float': 0.85,
    'Glass_Double': 1.30,
    'Glass_Triple': 1.80,

    # Plastics
    'PVC': 2.61,
    'HDPE': 1.93,
    'Polycarbonate': 5.00,

    # Other
    'Gypsum_Board': 0.39,
    'Ceramic_Tile': 0.78,
    'Asphalt': 0.05
}

# Emission factors per volume (kg CO2e per m³)
EMISSION_FACTORS_M3 = {
    'Concrete_C30': 312,    # ~2400 kg/m³ * 0.13
    'Steel': 14430,         # ~7800 kg/m³ * 1.85
    'Timber': -800,         # ~500 kg/m³ * -1.6
    'Brick': 432,           # ~1800 kg/m³ * 0.24
    'Glass': 2125           # ~2500 kg/m³ * 0.85
}
```

## Carbon Footprint Calculator

### Basic Calculator

```python
class CarbonCalculator:
    """Calculate carbon footprint for construction projects"""

    def __init__(self, emission_factors=None):
        self.factors = emission_factors or EMISSION_FACTORS_KG
        self.results = {}

    def calculate_embodied_carbon(self, df, material_col='Material',
                                   weight_col='Weight_kg'):
        """Calculate embodied carbon from materials"""
        df = df.copy()

        # Map materials to emission factors
        df['Emission_Factor'] = df[material_col].map(self.factors).fillna(0)
        df['CO2_kg'] = df[weight_col] * df['Emission_Factor']

        # Summary by material
        summary = df.groupby(material_col).agg({
            weight_col: 'sum',
            'CO2_kg': 'sum'
        }).round(2)

        self.results['embodied'] = {
            'total_kg': df['CO2_kg'].sum(),
            'by_material': summary,
            'details': df
        }

        return df

    def calculate_transport_carbon(self, df, distance_col='Distance_km',
                                    weight_col='Weight_kg',
                                    transport_type='truck'):
        """Calculate transport emissions"""
        # Transport emission factors (kg CO2 per tonne-km)
        transport_factors = {
            'truck': 0.062,
            'rail': 0.022,
            'ship': 0.016,
            'air': 0.602
        }

        factor = transport_factors.get(transport_type, 0.062)

        df = df.copy()
        df['Transport_CO2_kg'] = (df[weight_col] / 1000) * df[distance_col] * factor

        self.results['transport'] = {
            'total_kg': df['Transport_CO2_kg'].sum(),
            'factor_used': factor,
            'transport_type': transport_type
        }

        return df

    def calculate_construction_carbon(self, df,
                                       equipment_hours=None,
                                       fuel_consumption=None):
        """Calculate construction phase emissions"""
        # Equipment emission factors (kg CO2 per hour)
        equipment_factors = {
            'excavator': 25.0,
            'crane': 18.5,
            'concrete_pump': 22.0,
            'loader': 15.0,
            'compactor': 8.0,
            'generator': 12.0
        }

        if equipment_hours:
            construction_co2 = sum(
                hours * equipment_factors.get(equip, 15.0)
                for equip, hours in equipment_hours.items()
            )
        elif fuel_consumption:
            # Diesel: 2.68 kg CO2 per liter
            construction_co2 = fuel_consumption * 2.68
        else:
            construction_co2 = 0

        self.results['construction'] = {
            'total_kg': construction_co2
        }

        return construction_co2

    def get_total_footprint(self):
        """Get total carbon footprint"""
        total = sum(
            r.get('total_kg', 0)
            for r in self.results.values()
        )
        return {
            'total_kg': total,
            'total_tonnes': total / 1000,
            'breakdown': {k: v.get('total_kg', 0) for k, v in self.results.items()}
        }

    def generate_report(self):
        """Generate carbon footprint report"""
        footprint = self.get_total_footprint()

        report = []
        report.append("=" * 50)
        report.append("CARBON FOOTPRINT REPORT")
        report.append("=" * 50)
        report.append("")
        report.append(f"Total Carbon Footprint: {footprint['total_tonnes']:,.2f} tonnes CO2e")
        report.append("")
        report.append("Breakdown:")

        for category, value in footprint['breakdown'].items():
            pct = (value / footprint['total_kg'] * 100) if footprint['total_kg'] > 0 else 0
            report.append(f"  {category.capitalize():15s}: {value:>12,.0f} kg ({pct:>5.1f}%)")

        report.append("")
        report.append("=" * 50)

        return "\n".join(report)
```

### Usage Example

```python
# Load project data
elements = pd.read_excel("bim_export.xlsx")

# Initialize calculator
calc = CarbonCalculator()

# Calculate embodied carbon
elements = calc.calculate_embodied_carbon(
    elements,
    material_col='Material',
    weight_col='Weight_kg'
)

# Add transport emissions
elements['Distance_km'] = 50  # Average transport distance
elements = calc.calculate_transport_carbon(
    elements,
    distance_col='Distance_km',
    weight_col='Weight_kg',
    transport_type='truck'
)

# Construction phase
equipment_usage = {
    'excavator': 120,
    'crane': 500,
    'concrete_pump': 80,
    'loader': 200
}
calc.calculate_construction_carbon(equipment_hours=equipment_usage)

# Generate report
print(calc.generate_report())

# Get detailed breakdown
footprint = calc.get_total_footprint()
```

## Life Cycle Assessment (LCA)

### Full LCA Calculation

```python
class ConstructionLCA:
    """Life Cycle Assessment for construction projects"""

    def __init__(self, building_lifespan=50):
        self.lifespan = building_lifespan
        self.phases = {}

    def calculate_a1_a3(self, materials_df):
        """Product stage: Raw material supply, transport, manufacturing"""
        materials_df['A1_A3'] = materials_df.apply(
            lambda row: row['Weight_kg'] * EMISSION_FACTORS_KG.get(row['Material'], 0),
            axis=1
        )
        self.phases['A1-A3'] = materials_df['A1_A3'].sum()
        return self.phases['A1-A3']

    def calculate_a4(self, materials_df, avg_distance_km=100):
        """Transport to site"""
        # 0.062 kg CO2 per tonne-km for truck
        self.phases['A4'] = (materials_df['Weight_kg'].sum() / 1000) * avg_distance_km * 0.062
        return self.phases['A4']

    def calculate_a5(self, construction_energy_kwh, waste_factor=0.05):
        """Construction/installation process"""
        # Electricity emission factor varies by region (0.4 kg CO2/kWh average)
        energy_emissions = construction_energy_kwh * 0.4
        # Waste emissions (estimate 5% material waste)
        self.phases['A5'] = energy_emissions
        return self.phases['A5']

    def calculate_b1_b7(self, annual_energy_kwh, maintenance_co2_annual=0):
        """Use stage: Operation, maintenance, repair, replacement"""
        annual_operation = annual_energy_kwh * 0.4
        total_operational = (annual_operation + maintenance_co2_annual) * self.lifespan
        self.phases['B1-B7'] = total_operational
        return self.phases['B1-B7']

    def calculate_c1_c4(self, materials_df, demolition_energy_kwh=0):
        """End of life: Deconstruction, transport, processing, disposal"""
        # Demolition energy
        demolition = demolition_energy_kwh * 0.4
        # Transport to disposal (50 km average)
        transport = (materials_df['Weight_kg'].sum() / 1000) * 50 * 0.062
        # Landfill emissions (rough estimate)
        disposal = materials_df['Weight_kg'].sum() * 0.01

        self.phases['C1-C4'] = demolition + transport + disposal
        return self.phases['C1-C4']

    def calculate_d(self, recycled_materials_df):
        """Module D: Benefits beyond system boundary (recycling credits)"""
        # Recycling credits (negative emissions)
        credits = recycled_materials_df.apply(
            lambda row: -row['Weight_kg'] * EMISSION_FACTORS_KG.get(row['Material'], 0) * 0.5,
            axis=1
        ).sum() if len(recycled_materials_df) > 0 else 0

        self.phases['D'] = credits
        return self.phases['D']

    def get_total_lca(self):
        """Calculate total life cycle emissions"""
        embodied = self.phases.get('A1-A3', 0) + self.phases.get('A4', 0) + self.phases.get('A5', 0)
        operational = self.phases.get('B1-B7', 0)
        end_of_life = self.phases.get('C1-C4', 0)
        credits = self.phases.get('D', 0)

        return {
            'embodied_carbon': embodied,
            'operational_carbon': operational,
            'end_of_life_carbon': end_of_life,
            'recycling_credits': credits,
            'total_lifecycle': embodied + operational + end_of_life + credits,
            'phases': self.phases
        }

    def get_carbon_intensity(self, floor_area_m2):
        """Calculate carbon intensity per m²"""
        lca = self.get_total_lca()
        return {
            'embodied_per_m2': lca['embodied_carbon'] / floor_area_m2,
            'operational_per_m2_year': lca['operational_carbon'] / (floor_area_m2 * self.lifespan),
            'total_per_m2': lca['total_lifecycle'] / floor_area_m2
        }
```

## Reporting and Visualization

### Carbon Report Generation

```python
def generate_carbon_report(df, project_name, floor_area_m2):
    """Generate comprehensive carbon footprint report"""

    # Calculate totals
    total_co2 = df['CO2_kg'].sum()
    co2_per_m2 = total_co2 / floor_area_m2

    # By category
    by_category = df.groupby('Category')['CO2_kg'].sum().sort_values(ascending=False)

    # By material
    by_material = df.groupby('Material')['CO2_kg'].sum().sort_values(ascending=False)

    report = {
        'project': project_name,
        'floor_area_m2': floor_area_m2,
        'total_co2_kg': total_co2,
        'total_co2_tonnes': total_co2 / 1000,
        'co2_per_m2': co2_per_m2,
        'by_category': by_category.to_dict(),
        'by_material': by_material.to_dict(),
        'benchmark_comparison': classify_carbon_intensity(co2_per_m2)
    }

    return report

def classify_carbon_intensity(co2_per_m2):
    """Classify building carbon intensity against benchmarks"""
    # Typical benchmarks for embodied carbon (kg CO2e/m²)
    if co2_per_m2 < 300:
        return {'rating': 'A+', 'description': 'Ultra-low carbon'}
    elif co2_per_m2 < 500:
        return {'rating': 'A', 'description': 'Low carbon'}
    elif co2_per_m2 < 750:
        return {'rating': 'B', 'description': 'Below average'}
    elif co2_per_m2 < 1000:
        return {'rating': 'C', 'description': 'Average'}
    elif co2_per_m2 < 1250:
        return {'rating': 'D', 'description': 'Above average'}
    else:
        return {'rating': 'E', 'description': 'High carbon'}

def export_carbon_report(report, filepath):
    """Export carbon report to Excel"""
    with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
        # Summary sheet
        summary_df = pd.DataFrame({
            'Metric': ['Total CO2 (tonnes)', 'CO2 per m²', 'Rating', 'Floor Area'],
            'Value': [
                f"{report['total_co2_tonnes']:,.1f}",
                f"{report['co2_per_m2']:,.0f} kg/m²",
                report['benchmark_comparison']['rating'],
                f"{report['floor_area_m2']:,.0f} m²"
            ]
        })
        summary_df.to_excel(writer, sheet_name='Summary', index=False)

        # By category
        cat_df = pd.DataFrame.from_dict(report['by_category'], orient='index', columns=['CO2_kg'])
        cat_df.to_excel(writer, sheet_name='By Category')

        # By material
        mat_df = pd.DataFrame.from_dict(report['by_material'], orient='index', columns=['CO2_kg'])
        mat_df.to_excel(writer, sheet_name='By Material')
```

## Carbon Reduction Strategies

### Material Optimization

```python
def suggest_carbon_reduction(df, material_col='Material'):
    """Suggest material substitutions to reduce carbon"""

    # Low-carbon alternatives
    alternatives = {
        'Concrete_C40': ('Concrete_C30', 0.19, 0.13),  # (alt, current_factor, alt_factor)
        'Steel_Structural': ('Steel_Recycled', 1.55, 0.47),
        'Aluminum_Primary': ('Aluminum_Recycled', 8.14, 0.52),
        'Insulation_EPS': ('Insulation_Cellulose', 3.29, 0.10),
        'Brick_Clay': ('Timber_CLT', 0.24, -1.20)
    }

    suggestions = []

    for material, (alt, current, alt_factor) in alternatives.items():
        subset = df[df[material_col] == material]
        if len(subset) > 0:
            current_co2 = subset['Weight_kg'].sum() * current
            alt_co2 = subset['Weight_kg'].sum() * alt_factor
            saving = current_co2 - alt_co2

            suggestions.append({
                'current_material': material,
                'alternative': alt,
                'current_co2_kg': current_co2,
                'alternative_co2_kg': alt_co2,
                'potential_saving_kg': saving,
                'saving_percent': (saving / current_co2 * 100) if current_co2 > 0 else 0
            })

    return pd.DataFrame(suggestions).sort_values('potential_saving_kg', ascending=False)
```

## Quick Reference

| Metric | Formula |
|--------|---------|
| Embodied Carbon | `Weight_kg × Emission_Factor` |
| Transport Carbon | `(Weight_tonnes) × Distance_km × 0.062` |
| Carbon Intensity | `Total_CO2 / Floor_Area_m2` |
| LCA Total | `A1-A3 + A4 + A5 + B1-B7 + C1-C4 + D` |

## Common Emission Factors

| Material | kg CO2e/kg | kg CO2e/m³ |
|----------|------------|------------|
| Concrete C30 | 0.13 | 312 |
| Steel (new) | 1.85 | 14,430 |
| Steel (recycled) | 0.47 | 3,666 |
| Timber | -1.60 | -800 |
| Brick | 0.24 | 432 |
| Aluminum | 8.14 | 21,978 |

## Resources

- **Book**: "Data-Driven Construction" by Artem Boiko, Chapter 3.3
- **Website**: https://datadrivenconstruction.io
- **ICE Database**: Inventory of Carbon and Energy
- **EN 15978**: Sustainability of construction works standard

## Next Steps

- See `cost-prediction` for cost-carbon optimization
- See `qto-report` for extracting quantities for CO2 calculation
- See `data-visualization` for carbon dashboards
