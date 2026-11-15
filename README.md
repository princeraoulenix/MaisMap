# 🌽 MaïsMap

**Climate & Soil Intelligence for Smarter Agriculture in Northern Cameroon**

NASA Space Apps Challenge 2026 · Team GeoWorks · Yaoundé, Cameroon
Challenge: *Field Shift — Adapting Farms with NASA Data*

[![Tests](https://img.shields.io/badge/tests-46%2F46%20passing-brightgreen)](tests/test_analysis.py)
[![Python](https://img.shields.io/badge/python-3.13-blue)](requirements.txt)
[![Data](https://img.shields.io/badge/data-NASA%20POWER%20real-green)](data/processed/)

---

## What is MaïsMap?

MaïsMap is an interactive geospatial decision-support platform that helps maize farmers
and agricultural stakeholders in Northern Cameroon make better-informed sowing and
crop-rotation decisions.

It combines **real NASA POWER meteorological data** (2020–2023) with **ISRIC SoilGrids**
soil estimates to compute climate risk indicators and compare three crop-rotation strategies
across a 60-cell grid covering the Nord and Extreme-Nord regions.

> **This is a decision-support prototype.** Recommendations must be interpreted alongside
> local agronomic guidance. The tool does not guarantee a sowing date.

---

## Two Analytical Engines

### Engine A — Climate Intelligence
- Rainy-season onset detection (Sivakumar 1988 / AGRHYMET method)
- False-start detection (early rains followed by dry spells)
- Dry-spell analysis (maximum consecutive dry days)
- Heat-stress days (Tmax > 35°C, CIMMYT pollen-viability threshold)
- Composite agricultural risk score: **LOW / MEDIUM / HIGH**
- Sowing advice in plain French

### Engine B — Crop Rotation Lab
- Three rotation strategies compared side-by-side:
  - **Strategy A:** Maize monoculture (documented baseline)
  - **Strategy B:** Maize–Cowpea rotation (nitrogen fixation potential)
  - **Strategy C:** Diversified cereal–legume (maize → cowpea → sorghum)
- Six farmer priority dimensions with interactive sliders
- Climate-fit scoring per strategy based on observed conditions
- Crop calendar reference (MINADER)
- Transparent assumptions and documented data gaps

---

## Quick Start (Windows)

```powershell
# 1. Clone the repository
git clone https://github.com/princeraoulenix/MaisMap.git
cd MaisMap

# 2. Create and activate virtual environment
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run the application (real NASA data included for 2020–2023)
python -m streamlit run app.py
```

The application opens at **http://localhost:8501**

To generate the synthetic demo dataset (optional fallback):
```powershell
python src\data\generate_demo.py
```

---

## Run Tests

```powershell
python -m pytest tests\ -v
```

**46 tests** covering: onset detection, false-start detection, dry-spell analysis,
heat-stress counting, risk model, trends, data loading (real + demo), GeoJSON validation,
geospatial grid coverage, and crop rotation engine.

---

## Fetch Additional NASA POWER Data (optional)

```powershell
python src\acquisition\fetch_nasa_power.py --year 2019
```

Results are saved to `data/processed/grid_{year}.geojson` and cached in `data/raw/cache/`.

---

## Application Features

| Feature | Status |
|---|---|
| Interactive Folium risk map | ✅ Done |
| Color-coded 60-cell grid | ✅ Done |
| Cell popups with all indicators | ✅ Done |
| Year selector (2020–2023 real + demo) | ✅ Done |
| Region filter (Nord / Extreme-Nord) | ✅ Done |
| Risk-class filter | ✅ Done |
| NASA GIBS satellite overlay | ✅ Done |
| Historical trend charts (5 charts) | ✅ Done |
| Scenario sensitivity simulator | ✅ Done |
| GeoJSON validation report | ✅ Done |
| CSV export | ✅ Done |
| Crop Rotation Lab (Engine B) | ✅ Done |
| Real NASA POWER data (2020–2023) | ✅ Done |
| Demo data fallback (2010–2023) | ✅ Done |
| 46 automated tests | ✅ Done |

---

## Data Sources

| Source | Variables | Resolution | Period | Role |
|---|---|---|---|---|
| **NASA POWER v9** | PRECTOTCORR, T2M_MAX, T2M_MIN | 0.5° (~55 km) | 2020–2023 | Primary analysis |
| **NASA GIBS** | MODIS Terra True Color | Variable | Daily | Satellite overlay |
| **ISRIC SoilGrids v2.0** | pH, SOC, clay, sand, silt | 250 m | 2023 | Attempted — null values returned for this region (documented limitation) |

**Important:** NASA POWER is the NASA data source. ISRIC SoilGrids is an ISRIC resource,
not NASA data. SoilGrids returned null property values for Northern Cameroon — this is a
known gap in the global model and is clearly documented in the application.

Real data is stored in `data/processed/grid_{year}.geojson` (60 features per year).
The synthetic demo dataset (`data/demo/demo_grid.geojson`) covers 2010–2023 and is
clearly labeled as synthetic in the application.

---

## Agronomic Methodology

**Onset detection:** Sivakumar (1988) / AGRHYMET method
- Trigger: ≥ 20 mm over 3 consecutive days after April 1 (DOY 91)
- Validation: no dry spell ≥ 7 days in the following 30 days

**False start:** Trigger followed by ≥ 10 consecutive dry days within 30 days

**Heat stress threshold:** Tmax > 35°C (pollen viability threshold, CIMMYT)

**Risk weights:** False start 40% · Dry spell 35% · Heat stress 25%
(provisional — documented in `config/thresholds.py`, not validated against yield data)

See [`docs/methodology.md`](docs/methodology.md) for full details.

---

## Architecture & Data Flow

```
NASA POWER API
      │
      ▼
src/acquisition/fetch_nasa_power.py
      │  (PRECTOTCORR, T2M_MAX, T2M_MIN — daily, per cell)
      ▼
src/analysis/  (onset · false_start · dry_spell · heat_stress · risk_model)
      │
      ▼
data/processed/grid_{year}.geojson  (60 features, real data)
      │
      ▼
src/data/data_loader.py  (auto-detects real vs demo)
      │
      ▼
app.py  (Streamlit + Folium + Plotly)
      │
      ├── Tab: Map          (Folium interactive map)
      ├── Tab: Climate      (5 Plotly trend charts)
      ├── Tab: Crop Rotation (Engine B — 3 strategies)
      ├── Tab: Scenario     (sensitivity simulator)
      ├── Tab: Data         (table + CSV export)
      └── Tab: Methodology  (scientific documentation)
```

---

## Repository Structure

```
MaisMap/
├── app.py                          # Main Streamlit application
├── requirements.txt
├── CHANGELOG.md
├── config/
│   ├── settings.py                 # Paths, map defaults, study area
│   └── thresholds.py               # Agronomic thresholds (documented)
├── data/
│   ├── demo/demo_grid.geojson      # Synthetic demo (2010–2023, 840 features)
│   ├── processed/                  # Real NASA POWER data (grid_{year}.geojson)
│   ├── derived/soil_grid.json      # SoilGrids fetch result (null values — documented)
│   └── raw/cache/                  # NASA POWER API cache (gitignored)
├── src/
│   ├── acquisition/
│   │   ├── fetch_nasa_power.py     # Real data pipeline
│   │   └── fetch_soilgrids.py      # SoilGrids connector
│   ├── analysis/
│   │   ├── onset.py                # Sivakumar onset detection
│   │   ├── false_start.py          # False-start detection
│   │   ├── dry_spell.py            # Dry-spell analysis
│   │   ├── heat_stress.py          # Heat-day counting
│   │   ├── risk_model.py           # Risk score + sowing advice
│   │   └── trends.py               # Historical trend aggregation
│   ├── crop_rotation/
│   │   └── engine.py               # 3 strategies, priority scoring, climate fit
│   ├── data/
│   │   ├── data_loader.py          # GeoJSON loader (real + demo)
│   │   ├── validator.py            # GeoJSON schema validation
│   │   ├── generate_demo.py        # Synthetic dataset generator
│   │   ├── nasa_power.py           # NASA POWER API connector
│   │   └── nasa_pipeline.py        # Legacy pipeline
│   ├── geospatial/
│   │   └── grid.py                 # Grid generation + coverage validation
│   └── visualization/
│       ├── map.py                  # Folium map + NASA GIBS overlay
│       └── charts.py               # Plotly historical charts
├── tests/
│   └── test_analysis.py            # 46 automated tests
└── docs/
    ├── demo/
    │   ├── MaisMap_NASA_Space_Apps_2026.pptx   # 7-slide presentation
    │   └── build_presentation.py               # Presentation generator
    ├── methodology.md              # Scientific methodology
    ├── data_sources.md             # Data source documentation
    ├── limitations.md              # Known limitations
    ├── AI_DISCLOSURE.md            # AI tool disclosure
    ├── DATA_REFERENCES.md          # Full references
    ├── PROJECT_AUDIT.md            # Development audit log
    └── NASA_SUBMISSION.md          # NASA submission form text
```

---

## Limitations

- Real data covers 2020–2023 only (4 years). Demo data extends to 2010–2023.
- 0.5° resolution (~55 km) cannot capture field-level or village-level variation.
- SoilGrids returned null values for Northern Cameroon — a documented model gap.
- Risk weights are provisional and not validated against crop yield data.
- Crop rotation benefits are agronomic hypotheses from published literature, not measured outcomes at this location.
- No seasonal forecast capability — historical analysis only.

See [`docs/limitations.md`](docs/limitations.md) for the complete list.

---

## Team GeoWorks

| Name | Role |
|---|---|
| KAM FOTSO Gislain | Team Lead / Project Coordinator |
| Souleymanou Daouda | GIS & Cartographic Validation |
| JATSA GUÉDIA Amaël | Agronomic Methodology |
| KWENYUI NDEIH JOSEPH | Agricultural Research & Data Support |
| Djouda Douanla Anaël | Communication & Presentation |
| NDINGA PRINCE RAOUL | Technical Lead & Software Engineer |

---

## Presentation

7-slide NASA Space Apps presentation:
`docs/demo/MaisMap_NASA_Space_Apps_2026.pptx`

To regenerate:
```powershell
python docs\demo\build_presentation.py
```

---

## AI Disclosure

This project used **Amazon Q Developer** (AWS AI coding assistant) to accelerate
software development, documentation, and code quality. All AI-generated code was
reviewed, tested, and verified. See [`docs/AI_DISCLOSURE.md`](docs/AI_DISCLOSURE.md).

---

## References

- Sivakumar, M.V.K. (1988). *Agricultural and Forest Meteorology*, 42(4), 295–305.
- MINADER (2023). Guide technique de production du maïs au Cameroun.
- Dugje et al. (2009). Farmers' Guide to Cowpea Production in West Africa. IITA.
- NASA POWER: https://power.larc.nasa.gov/
- ISRIC SoilGrids: https://www.isric.org/explore/soilgrids
- FAO Irrigation Paper 56 (crop water requirements).
