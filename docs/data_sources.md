# MaïsMap — Data Sources

## NASA POWER (Primary source)

| Attribute | Value |
|---|---|
| Full name | NASA Prediction Of Worldwide Energy Resources |
| URL | https://power.larc.nasa.gov |
| API endpoint | https://power.larc.nasa.gov/api/temporal/daily/point |
| Community | AG (Agroclimatology) |
| Variables used | PRECTOTCORR (precipitation), T2M_MAX (max temperature) |
| Spatial resolution | 0.5° × 0.5° (~55 km) |
| Temporal resolution | Daily |
| Period available | 1984–present |
| Role in MaïsMap | Primary source for onset, false start, dry spell, heat stress |
| Caching | Results cached in `data/raw/cache/` as JSON |

**PRECTOTCORR:** Bias-corrected precipitation (mm/day). Derived from MERRA-2 reanalysis, corrected against GPCP climatology.

**T2M_MAX:** Maximum temperature at 2 m height (°C). From MERRA-2 reanalysis.

> NASA POWER data is a reanalysis product, not direct station measurements. It represents gridded estimates that may differ from local observations.

---

## NASA GPM IMERG (Secondary — connector ready)

| Attribute | Value |
|---|---|
| Full name | Global Precipitation Measurement — Integrated Multi-satellitE Retrievals |
| Product | GPM IMERG Final Run v07 |
| Spatial resolution | 0.1° × 0.1° (~11 km) |
| Temporal resolution | Daily (aggregated from 30-min) |
| Period available | June 2000–present |
| Role in MaïsMap | Higher-resolution precipitation validation |
| Status | Connector prepared in `src/data/nasa_power.py` — requires Earthdata login |

> GPM IMERG requires NASA Earthdata authentication. The connector is implemented but not activated in the demo version.

---

## NASA SMAP (Supplementary — documented)

| Attribute | Value |
|---|---|
| Full name | Soil Moisture Active Passive |
| Product | SPL3SMP (Level-3 daily composite) |
| Spatial resolution | 36 km |
| Temporal resolution | Daily (ascending/descending passes) |
| Period available | April 2015–present |
| Variable | Surface soil moisture (0–5 cm) |
| Role in MaïsMap | Supplementary soil moisture indicator |
| Status | Not yet integrated — documented for future development |

> ⚠️ SMAP measures **surface** soil moisture (0–5 cm). This is not equivalent to root-zone soil moisture, which is more relevant for crop stress assessment.

---

## NASA GIBS (Visualization overlay)

| Attribute | Value |
|---|---|
| Full name | Global Imagery Browse Services |
| URL | https://gibs.earthdata.nasa.gov |
| Layer used | MODIS Terra Corrected Reflectance (True Color) |
| Tile format | WMTS / GoogleMapsCompatible |
| Role in MaïsMap | Optional satellite imagery background overlay |
| Status | Implemented in `src/visualization/map.py` |

> GIBS imagery is for **visualization only**. It is not used in any numerical calculation.

---

## Demonstration Dataset

| Attribute | Value |
|---|---|
| File | `data/demo/demo_grid.geojson` |
| Type | **SYNTHETIC** — not real measurements |
| Generator | `src/data/generate_demo.py` |
| Years | 2010–2023 (14 years) |
| Cells | 60 per year (840 total) |
| Purpose | Application testing and demonstration only |

> All synthetic records are labeled `data_source: "SYNTHETIC — DEMONSTRATION ONLY"` and `confidence: "demo"`. They must never be presented as NASA observations.
