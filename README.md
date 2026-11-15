# MaïsMap

**Agricultural decision-support application for maize farmers in Northern Cameroon**  
NASA Space Apps Challenge 2026 | Team GeoWorks

---

## What is MaïsMap?

MaïsMap is an interactive geospatial application that helps maize farmers and agricultural
stakeholders in Northern Cameroon identify the risk of false starts of the rainy season and
make better-informed sowing decisions.

It analyzes historical rainfall and temperature data to compute:
- Rainy-season onset (Sivakumar/AGRHYMET method)
- False starts of the rainy season
- Consecutive dry spells during the growing season
- Heat-stress days (Tmax > 35°C)
- A composite agricultural risk score (LOW / MEDIUM / HIGH)
- Sowing recommendations in plain language

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

The application opens at http://localhost:8501

---

## Run Tests

```powershell
python -m pytest tests\ -v
```

25 tests covering onset detection, false-start detection, dry-spell analysis,
heat-stress counting, risk model, and data loading.

---

## Project Structure

```
MaisMap/
├── app.py                    # Main Streamlit application
├── requirements.txt
├── config/
│   ├── settings.py           # Paths, map defaults
│   └── thresholds.py         # Agronomic thresholds (documented)
├── data/
│   ├── demo/                 # Synthetic demonstration dataset
│   ├── processed/            # Real processed data (when available)
│   └── raw/                  # Raw NASA downloads + cache
├── src/
│   ├── analysis/
│   │   ├── onset.py          # Sivakumar onset detection
│   │   ├── false_start.py    # False-start detection
│   │   ├── dry_spell.py      # Dry-spell analysis
│   │   ├── heat_stress.py    # Heat-day counting
│   │   ├── risk_model.py     # Risk score + sowing advice
│   │   └── trends.py         # Historical trend aggregation
│   ├── data/
│   │   ├── nasa_power.py     # NASA POWER API connector
│   │   ├── data_loader.py    # GeoJSON loader (demo + real)
│   │   └── generate_demo.py  # Synthetic dataset generator
│   └── visualization/
│       ├── map.py            # Folium map builder
│       └── charts.py         # Plotly historical charts
├── tests/
│   └── test_analysis.py      # 25 automated tests
└── docs/
    ├── methodology.md
    ├── data_sources.md
    └── limitations.md
```

---

## Data Sources

| Source | Variable | Resolution | Period |
|--------|----------|------------|--------|
| NASA POWER | Precipitation, Tmax, Tmin | 0.5° (~55 km) | 1984–present |
| NASA GPM IMERG | Precipitation | 0.1° (~11 km) | 2000–present |
| NASA SMAP | Surface soil moisture | 36 km | 2015–present |

The current demo dataset is **synthetic** and clearly labeled as such.
Real NASA data can be fetched using `src/data/nasa_power.py`.

---

## Agronomic Methodology

**Onset detection:** Sivakumar (1988) / AGRHYMET method  
- Trigger: ≥ 20 mm over 3 consecutive days after April 1  
- Validation: no dry spell ≥ 7 days in the following 30 days

**False start:** Trigger followed by ≥ 10 consecutive dry days within 30 days

**Heat stress threshold:** Tmax > 35°C (pollen viability threshold, CIMMYT)

**Risk weights:** False start 40% · Dry spell 35% · Heat stress 25%  
(documented in `config/thresholds.py`)

---

## Limitations

- The demo dataset is synthetic. Results do not represent real conditions.
- The 0.5° grid (~55 km) cannot capture local microclimatic variation.
- The risk model uses provisional weights pending agronomic validation.
- This tool does not replace local agricultural extension services.

---

## Team

**GeoWorks** — NASA Space Apps Challenge 2026  
Challenge: *Field Shift: Adapting Farms with NASA Data*
