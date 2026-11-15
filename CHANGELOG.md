# CHANGELOG

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
- Plotly historical charts (onset, false starts, dry spells, risk distribution)
- Scenario simulator (rainfall/temperature sensitivity)
- Streamlit application with sidebar controls, 4 tabs, demo banner
- 25 automated tests (all passing)
- README, CHANGELOG, .gitignore, requirements.txt
