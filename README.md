# Metropiness

Classify any US coordinate as metro, suburban, or rural using Census tract boundaries and USDA RUCA codes.

## The Problem

There's no single tool that takes a lat/lon coordinate and tells you how "metro" a location is. The data exists, but it's scattered:

- **USDA RUCA codes** have granular density classifications (1–10 scale), but they're just a spreadsheet keyed to census tracts. No coordinate lookup, no API.
- **Census TIGER/Line files** can resolve coordinates to census tracts, but tell you nothing about density or urbanity.
- **Other tools** (like EPI's `metstat`) only give a binary metro yes/no — no granularity.

Metropiness ties it all together into one local lookup.

## Install

clone this git repo

## Usage

```python
from metropiness import Metropiness

m = Metropiness()

# Get the RUCA classification description
m.classify(40.7128, -74.0060)
# → (1, 'Metropolitan core')

m.classify(35.2, -89.1)
# → (9, 'Small town low commuting')

# Get just the RUCA code (1-10)
m.ruca_code(40.7128, -74.0060)
# → 1
```

## RUCA Scale from the USDA 

| Code | Description |
|------|-------------|
| 1 | Metropolitan core |
| 2 | Metropolitan high commuting |
| 3 | Metropolitan low commuting |
| 4 | Micropolitan core |
| 5 | Micropolitan high commuting |
| 6 | Micropolitan low commuting |
| 7 | Small town core |
| 8 | Small town high commuting |
| 9 | Small town low commuting |
| 10 | Rural |

## How It Works

1. A compressed national Census tract boundary map (derived from TIGER/Line shapefiles) is bundled with the package
2. Your coordinate is matched to a tract using a spatial lookup — which of the ~85,000 tract polygons contains this point?
3. The tract ID is looked up against USDA RUCA codes to get the density classification

Everything runs locally. No API calls, no internet needed, no rate limits.

## Building the Data Yourself

If you want to regenerate the tract boundary data from source (or build an uncompressed version):

```
cd scripts
python build_data.py
```

This downloads all state-level TIGER/Line shapefiles from the Census Bureau, combines them into a single national file, and optionally simplifies the geometries for compression.

## Data Sources

- **Tract Boundaries:** [US Census Bureau TIGER/Line Shapefiles (2025)](https://www.census.gov/geographies/mapping-files/time-series/geo/tiger-line-file.html)
- **Density Classification:** [USDA Economic Research Service RUCA Codes (2020)](https://www.ers.usda.gov/data-products/rural-urban-commuting-area-codes/)

## Accuracy

The bundled tract boundaries are simplified to reduce file size (~35MB vs ~628MB uncompressed). This means points very close to tract borders may occasionally be assigned to a neighboring tract. In validation testing against the Census Bureau's geocoder API, the vast majority of lookups match exactly. When mismatches occur, the neighboring tract almost always has the same RUCA classification.

For maximum accuracy, use `build_data.py` to generate an uncompressed version.

## Contact
srahim457@gmail.com
