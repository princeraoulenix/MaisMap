# MaïsMap

**Agricultural decision-support application for maize farmers in Northern Cameroon**
NASA Space Apps Challenge 2026 | Team GeoWorks

---

## What is MaïsMap?

MaïsMap is an interactive geospatial application that helps maize farmers and agricultural
stakeholders in Northern Cameroon identify the risk of false starts of the rainy season and
make better-informed sowing decisions.

It analyzes historical rainfall and temperature data (NASA POWER, 1984–present) to compute:

- Rainy-season onset (Sivakumar 1988 / AGRHYMET method)
- False starts of the rainy season
- Consecutive dry spells during the growing season
- Heat-stress days (Tmax > 35°C, CIMMYT threshold)
- A composite agricultural risk score (LOW / MEDIUM / HIGH)
- Sowing recommendations in plain French

**Core question: When should farmers sow maize in Northern Cameroon?**

> This tool is a decision-support prototype. Its recommendations must be interpreted
> alongside local agronomic guidance. It does not guarantee a sowing date.

---

## Quick Start (Windows)

```powershell
# 1. Clone or open the project
cd MaisMap

# 2. Create virtual environment (if not already created)
python -m venv .venv

# 3. Activate
.\.venv\Scripts\Activate.ps1

# 4. Install dependencies
python -m pip install -r requirements.txt

# 5. Generate demo data (first time only)
python src\data\generate_demo.py

# 6. Run the application
python -m streamlit run app.py
```

The application opens at **http://localhost:8501**

---

## Run Tests

```powershell
python -m pytest tests\ -v
```

37 tests covering onset detection, false-start detection, dry-spell analysis,
heat-stress counting, risk model, trends, data loading, GeoJSON validation,
and geospatial grid coverage.

---

## Fetch Real NASA Data (optional, requires internet)

```powershell
python src\data\nasa_pipeline.py --year 2022
python src\data\nasa_pipeline.py --year 2022 --year 2021 --year 2020
```

Results are saved to `data/processed/grid_{year}.geojson` and cached in `data/raw/cache/`.
Set `use_demo = False` in `app.py` to switch to real data.

---

## Project Structure

```
MaisMap/
├── app.py                        # Main Streamlit application
├── requirements.txt
├── CHANGELOG.md
├── config/
│   ├── settings.py               # Paths, map defaults, study area
│   └── thresholds.py             # Agronomic thresholds (documented)
├── data/
│   ├── demo/demo_grid.geojson    # Synthetic demonstration dataset
│   ├── processed/                # Real NASA data (grid_{year}.geojson)
│   └── raw/cache/                # NASA POWER API cache
├── src/
│   ├── analysis/
│   │   ├── onset.py              # Sivakumar onset detection
│   │   ├── false_start.py        # False-start detection
│   │   ├── dry_spell.py          # Dry-spell analysis
│   │   ├── heat_stress.py        # Heat-day counting
│   │   ├── risk_model.py         # Risk score + sowing advice
│   │   └── trends.py             # Historical trend aggregation
│   ├── data/
│   │   ├── nasa_power.py         # NASA POWER API connector
│   │   ├── nasa_pipeline.py      # Full real-data pipeline
│   │   ├── data_loader.py        # GeoJSON loader (demo + real)
│   │   ├── validator.py          # GeoJSON schema validation
│   │   └── generate_demo.py      # Synthetic dataset generator
│   ├── geospatial/
│   │   └── grid.py               # Grid generation + coverage validation
│   └── visualization/
│       ├── map.py                # Folium map + NASA GIBS overlay
│       └── charts.py             # Plotly historical charts
├── tests/
│   └── test_analysis.py          # 37 automated tests
└── docs/
    ├── methodology.md            # Scientific methodology
    ├── data_sources.md           # NASA data source documentation
    ├── limitations.md            # Known limitations
    └── jury_presentation.md      # Demo script + jury guide
```

---

## Application Features

| Feature | Status |
|---|---|
| Interactive risk map (Folium) | Done |
| Color-coded grid cells | Done |
| Cell popups with all indicators | Done |
| Year selector | Done |
| Region filter | Done |
| Risk-class filter | Done |
| NASA GIBS satellite overlay | Done |
| Historical trend charts (5 charts) | Done |
| Scenario sensitivity simulator | Done |
| GeoJSON validation report | Done |
| Methodology tab | Done |
| CSV export | Done |
| Demo data banner | Done |
| Real NASA POWER pipeline | Done |
| 37 automated tests | Done |

---

## Data Sources

| Source | Variable | Resolution | Period | Role |
|---|---|---|---|---|
| NASA POWER | Precipitation, Tmax | 0.5° (~55 km) | 1984–present | Primary analysis |
| NASA GPM IMERG | Precipitation | 0.1° (~11 km) | 2000–present | Validation (connector ready) |
| NASA SMAP | Surface soil moisture | 36 km | 2015–present | Supplementary (documented) |
| NASA GIBS | MODIS True Color | Variable | Daily | Visualization overlay |

The current demo dataset is **synthetic** and clearly labeled as such.

---

## Agronomic Methodology

**Onset detection:** Sivakumar (1988) / AGRHYMET method
- Trigger: >= 20 mm over 3 consecutive days after April 1
- Validation: no dry spell >= 7 days in the following 30 days

**False start:** Trigger followed by >= 10 consecutive dry days within 30 days

**Heat stress threshold:** Tmax > 35°C (pollen viability threshold, CIMMYT)

**Risk weights:** False start 40% · Dry spell 35% · Heat stress 25%
(documented in `config/thresholds.py`, provisional pending agronomic validation)

See `docs/methodology.md` for full details.

---

## Limitations

- Demo dataset is synthetic — no operational value
- 0.5° resolution (~55 km) cannot capture local microclimatic variation
- Risk weights are provisional and not validated against yield data
- No seasonal forecast capability — historical analysis only
- Recommendations must be confirmed with local agricultural extension services

See `docs/limitations.md` for the complete list.

---

## Team

**GeoWorks** — NASA Space Apps Challenge 2026
Challenge: *Field Shift: Adapting Farms with NASA Data*
