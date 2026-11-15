# MaïsMap — Project Audit
## Status as of final branch | NASA Space Apps Challenge 2026

---

## Already Implemented and Working

| Component | Status | Notes |
|---|---|---|
| Streamlit application | Done | Runs on localhost:8501 |
| Folium interactive map | Done | Color-coded risk cells, popups, legend, MiniMap |
| NASA GIBS satellite overlay | Done | MODIS Terra True Color via WMTS |
| Year selector | Done | Auto-detects real vs demo data |
| Region filter | Done | Nord, Extreme-Nord, Adamaoua |
| Risk-class filter | Done | LOW/MEDIUM/HIGH multiselect |
| Cell popups | Done | All indicators, data-source badge |
| Dashboard metrics | Done | 6 KPIs including mean rainfall |
| Onset detection | Done | Sivakumar 1988 / AGRHYMET method |
| False-start detection | Done | 10-day post-trigger dry spell |
| Dry-spell analysis | Done | Max consecutive dry days in season |
| Heat-stress counting | Done | Tmax > 35°C, CIMMYT threshold |
| Risk model | Done | Weighted composite, documented |
| Sowing advice | Done | Cautious French-language text |
| Historical trend charts | Done | 5 Plotly charts with reference lines |
| Scenario simulator | Done | Rain/temp sensitivity, not forecast |
| GeoJSON validation | Done | Schema, duplicates, provenance |
| CSV export | Done | Filtered data download |
| Methodology tab | Done | In-app scientific documentation |
| **Real NASA POWER data** | **Done** | 60 cells × 4 years (2020–2023) |
| **Crop rotation engine** | **Done** | 3 strategies, priority scoring |
| **Crop calendar reference** | **Done** | MINADER-sourced |
| NASA POWER pipeline | Done | Cached, retry, rate-limited |
| SoilGrids connector | Done | Fetched — null values for region |
| Data loader (real+demo) | Done | Auto-detects, enriches with soil |
| Geospatial grid module | Done | 60-cell coverage validation |
| 46 automated tests | Done | All passing |
| docs/methodology.md | Done | Full scientific documentation |
| docs/data_sources.md | Done | All sources documented |
| docs/limitations.md | Done | 13 documented limitations |
| docs/jury_presentation.md | Done | 7-minute demo script |

---

## Partially Implemented

| Component | Status | Gap |
|---|---|---|
| SoilGrids soil data | Partial | API returned null values for Northern Cameroon — documented limitation |
| Historical trend (real data) | Partial | Only 4 years of real data (2020–2023); demo extends to 2010 |
| GPM IMERG connector | Partial | Documented, connector architecture ready, requires Earthdata auth |
| SMAP connector | Partial | Documented, not integrated |

---

## Not Implemented

| Component | Reason |
|---|---|
| Landsat/Sentinel-2 NDVI | Requires large raster downloads and cloud masking — beyond current scope |
| SRTM terrain analysis | Requires raster processing library (rasterio) — not installed |
| Administrative boundaries | No authoritative open-license boundary file retrieved |
| FAO GAEZ integration | Web service only — no bulk download available |
| Seasonal forecast | Out of scope — historical analysis only |

---

## Broken

None — all 46 tests pass, app syntax clean.

---

## Awaiting External Data

| Item | Status |
|---|---|
| SoilGrids data for Northern Cameroon | API available but returns null — known model gap |
| GPM IMERG historical data | Requires NASA Earthdata account |
| MINADER official yield data | Not publicly available online |

---

## Synthetic Data

- `data/demo/demo_grid.geojson` — 840 features, 14 years, clearly labeled SYNTHETIC
- All synthetic records carry `confidence: "demo"` and `data_source: "SYNTHETIC — DEMONSTRATION ONLY"`

---

## Real Data

- `data/processed/grid_2020.geojson` — 60 cells, NASA POWER v9
- `data/processed/grid_2021.geojson` — 60 cells, NASA POWER v9
- `data/processed/grid_2022.geojson` — 60 cells, NASA POWER v9
- `data/processed/grid_2023.geojson` — 59 cells, NASA POWER v9 (1 cell had DNS failure)
- `data/raw/cache/` — 239 NASA POWER JSON cache files
- `data/derived/soil_grid.json` — 60 cells, SoilGrids v2.0 (null values — documented)

---

## Scientifically Unvalidated

- Risk model weights (40/35/25) — provisional, not calibrated against yield data
- Crop rotation benefit scores — qualitative assessments from literature, not field measurements
- Sivakumar onset thresholds — validated for West Africa generally, not specifically for this grid
