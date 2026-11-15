# MaïsMap — Changelog

All notable changes to this project are documented here.

---

## [Final] — 2026 NASA Space Apps Submission

### Added
- Engine B: Crop Rotation Lab with 3 strategies (A/B/C), 6 priority dimensions,
  interactive sliders, climate-fit scoring, crop calendar reference table
- Real NASA POWER data pipeline (`src/acquisition/fetch_nasa_power.py`)
  fetching PRECTOTCORR, T2M_MAX, T2M_MIN for 60 cells × 4 years (2020–2023)
- ISRIC SoilGrids connector (`src/acquisition/fetch_soilgrids.py`) — null values
  returned for Northern Cameroon, documented as known limitation
- GeoJSON schema validator (`src/data/validator.py`)
- NASA GIBS MODIS satellite overlay option
- Scenario sensitivity simulator (rain ±30%, temperature ±4°C)
- 5 Plotly historical trend charts with agronomic threshold reference lines
- CSV export from Data tab
- 7-slide NASA Space Apps presentation (`docs/demo/MaisMap_NASA_Space_Apps_2026.pptx`)
- `docs/NASA_SUBMISSION.md` — complete NASA submission form text
- `docs/AI_DISCLOSURE.md` — honest Amazon Q Developer disclosure
- `docs/DATA_REFERENCES.md` — full data and literature references
- `docs/PROJECT_AUDIT.md` — development audit log

### Fixed
- Forward-reference bug: `_load_all_years` called before definition in app.py
- Dead code in `_render_scenario` (undefined variables)
- Region filter mapping inconsistency ("All" vs "Toutes")
- Coordinate order validation in tests

### Changed
- README completely rewritten for NASA submission
- Test count updated from 37 to 46
- Data loader auto-detects real vs demo data by year
- App uses real NASA POWER data by default when available

### Data
- `data/processed/grid_2020.geojson` — 60 cells, real NASA POWER
- `data/processed/grid_2021.geojson` — 60 cells, real NASA POWER
- `data/processed/grid_2022.geojson` — 60 cells, real NASA POWER
- `data/processed/grid_2023.geojson` — 59 cells, real NASA POWER (1 cell missing)
- `data/demo/demo_grid.geojson` — 840 features, synthetic, 2010–2023
- `data/derived/soil_grid.json` — SoilGrids fetch result (null values, documented)

---

## [Phase 2] — Bug Fixes & Scientific Validation

### Added
- GeoJSON validator with schema, coordinate bounds, duplicate detection
- NASA GIBS satellite overlay
- Improved map popups with data-source badges (DEMO / NASA)
- Test suite expanded from 25 to 37 tests

### Fixed
- Critical forward-reference bug in app.py
- NameError on scenario variables

---

## [Phase 1] — Initial Build

### Added
- Full project structure
- Streamlit application with Folium map
- Sivakumar (1988) onset detection
- False-start detection
- Dry-spell analysis
- Heat-stress counting
- Composite risk model (LOW / MEDIUM / HIGH)
- Sowing advice in French
- Synthetic demo dataset (840 features, 2010–2023)
- 25 automated tests
- `config/settings.py` and `config/thresholds.py`
- `docs/methodology.md`, `docs/limitations.md`, `docs/data_sources.md`
