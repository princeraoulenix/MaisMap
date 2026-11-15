# CHANGELOG

## [0.2.0] — 2026-11-15 (develop branch)

### Fixed
- **Critical:** Forward-reference bug in `app.py` — `_load_all_years` called before its definition (crashed history tab at runtime)
- **Critical:** Dead code in `_render_scenario` — `mod_geojson` built then immediately overwritten
- **Bug:** `rain_delta`/`temp_delta` NameError when scenario tab opened without sidebar checkbox active
- **Bug:** `chart_risk_distribution` imported but `chart_heat_days` missing from import

### Added
- `src/data/validator.py` — full GeoJSON schema validation (required fields, risk class, coordinate bounds, duplicates, provenance)
- `src/data/nasa_pipeline.py` — complete NASA POWER real-data pipeline with caching and rate limiting
- `src/geospatial/grid.py` — grid generation and coverage validation utilities
- `src/visualization/charts.py` — new `chart_heat_days` with agronomic threshold reference lines; all charts now have reference lines and consistent styling
- `src/visualization/map.py` — NASA GIBS MODIS satellite overlay; MiniMap widget; improved popup with data-source badge; better legend
- `app.py` — satellite overlay toggle in sidebar; validation report in Data tab; Méthodologie tab with full methodology; 6-column dashboard metrics; `show_satellite` wired to `build_map`; `_load_all_years_cached` now defined before use
- `docs/methodology.md` — complete scientific methodology documentation
- `docs/data_sources.md` — all NASA data sources documented with product details
- `docs/limitations.md` — 13 documented limitations
- `docs/jury_presentation.md` — 7-minute demo script and jury presentation guide
- `tests/test_analysis.py` — expanded from 25 to 37 tests; added TestTrends, TestValidator, TestGeospatialGrid

### Changed
- `app.py` — history tab now shows 5 charts (added heat days); summary statistics row added
- `app.py` — scenario tab sliders always rendered (disabled when inactive) to prevent NameError
- `config/settings.py` — no changes required
- `config/thresholds.py` — no changes required

## [0.1.0] — 2026-11-15

### Added
- Full project structure (config, src, data, tests, docs)
- Synthetic demo GeoJSON dataset: 840 features, 14 years, 60 cells/year
- Onset detection (Sivakumar/AGRHYMET method)
- False-start detection
- Dry-spell analysis
- Heat-stress day counting
- Composite risk model (LOW/MEDIUM/HIGH) with documented weights
- Sowing advice generator
- Historical trend aggregation
- NASA POWER API connector with local caching
- Folium interactive map with color-coded risk cells and popups
- Plotly historical charts
- Scenario simulator
- Streamlit application with sidebar controls, 4 tabs, demo banner
- 25 automated tests (all passing)
- README, CHANGELOG, .gitignore, requirements.txt
