# MaïsMap — NASA Space Apps Challenge 2026 Submission

**Team:** GeoWorks
**Event:** Yaoundé Local Event, Cameroon
**Challenge:** Field Shift — Adapting Farms with NASA Data

---

## 1. Project Name

MaïsMap

---

## 2. High-Level Project Summary (50–200 words)

MaïsMap is an interactive climate and soil intelligence platform that helps maize farmers
and agricultural stakeholders in Northern Cameroon make better-informed sowing and
crop-rotation decisions. It combines real NASA POWER meteorological data (2020–2023) with
ISRIC SoilGrids soil estimates to compute climate risk indicators across a 60-cell
geospatial grid covering the Nord and Extreme-Nord regions.

The platform provides two analytical engines: Engine A detects rainy-season onset using
the Sivakumar (1988) / AGRHYMET method, identifies false starts, dry spells, and heat-stress
days, and produces a composite agricultural risk score (LOW / MEDIUM / HIGH). Engine B
compares three crop-rotation strategies — maize monoculture, maize–cowpea, and a
diversified cereal–legume system — using six farmer priority dimensions and climate-fit
scoring derived from observed conditions.

The application is built with Python, Streamlit, and Folium, includes 46 automated tests,
and is openly available on GitHub. All data sources, assumptions, and limitations are
transparently documented.

---

## 3. Link to Project Demo

https://github.com/princeraoulenix/MaisMap/blob/main/docs/demo/MaisMap_NASA_Space_Apps_2026.pptx

*(7-slide presentation — copy path above or download from the repository)*

---

## 4. Link to Final Project

https://github.com/princeraoulenix/MaisMap

---

## 5. Detailed Project Description

### Problem

Smallholder maize farmers in Northern Cameroon face three compounding challenges:

1. **Rainfall variability** — The unimodal rainy season (May–October) shows high
   inter-annual variability. False starts — early rainfall triggers followed by extended
   dry spells — cause crop failure when farmers sow too early.

2. **Heat stress** — Maximum temperatures regularly exceed 35°C during the growing season,
   reducing maize pollen viability at a critical growth stage.

3. **Soil and climate information gaps** — Farmers lack accessible tools to interpret
   historical climate patterns or compare crop-rotation strategies based on local conditions.

### Solution

MaïsMap addresses these challenges through two analytical engines:

**Engine A — Climate Intelligence**

Using daily NASA POWER data (PRECTOTCORR, T2M_MAX, T2M_MIN) for 60 grid cells at 0.5°
resolution, the platform computes:

- Rainy-season onset using the Sivakumar (1988) / AGRHYMET method: first day after
  April 1 with ≥ 20 mm over 3 consecutive days, not followed by a 7-day dry spell
  within 30 days.
- False-start detection: onset trigger followed by ≥ 10 consecutive dry days within
  30 days.
- Maximum consecutive dry-spell days within the 120-day growing season.
- Heat-stress days (Tmax > 35°C, CIMMYT pollen-viability threshold).
- A composite risk score (false start 40%, dry spell 35%, heat stress 25%) producing
  LOW / MEDIUM / HIGH classifications.
- Sowing advice in plain French.

**Engine B — Crop Rotation Lab**

Three rotation strategies are compared using published agronomic literature:

- Strategy A: Maize monoculture (documented baseline — MINADER)
- Strategy B: Maize–Cowpea rotation (nitrogen fixation potential — Dugje et al. 2009)
- Strategy C: Diversified cereal–legume (maize → cowpea → sorghum)

Users adjust six farmer priority dimensions (water conservation, soil fertility, income
diversification, drought resilience, erosion reduction, lower inputs) via interactive
sliders. The engine computes weighted priority scores and climate-fit assessments based
on observed conditions for the selected year and region.

All rotation benefits are clearly labeled as agronomic hypotheses from published
literature, not field-validated measurements at this location.

### Technical Implementation

- **Data pipeline:** `src/acquisition/fetch_nasa_power.py` fetches daily NASA POWER data
  for all 60 grid cells and runs the full analysis pipeline, saving results to
  `data/processed/grid_{year}.geojson`.
- **Analysis modules:** Modular Python functions for onset, false start, dry spell,
  heat stress, risk model, and trends — each independently tested.
- **Application:** Streamlit app with 6 tabs (Map, Climate Analysis, Crop Rotation Lab,
  Scenario, Data, Methodology).
- **Visualization:** Folium interactive map with NASA GIBS MODIS overlay option;
  5 Plotly historical trend charts.
- **Testing:** 46 automated tests covering all analysis modules, data loading, validation,
  geospatial grid, and crop rotation engine.

### Data Availability

Real NASA POWER data is included in the repository for 2020–2023 (60 cells × 4 years =
239 features, one cell missing in 2023 due to API response). A synthetic demo dataset
covers 2010–2023 as a fallback.

ISRIC SoilGrids v2.0 was queried for all 60 cell centroids. The API returned null property
values for Northern Cameroon — a known gap in the global model. The connector is
implemented and documented; the limitation is clearly disclosed in the application.

### Limitations

- Real data covers 2020–2023 only (4 years).
- 0.5° resolution cannot capture field-level variation.
- SoilGrids returned null values for this region.
- Risk weights are provisional and not validated against yield data.
- No seasonal forecast capability.

---

## 6. Use of Super Intelligence (SI)

**Tool used:** Amazon Q Developer (AWS AI coding assistant)

**Actual uses:**
- Code generation and architecture design for Python modules and the Streamlit application
- Documentation drafting (methodology, data sources, limitations, submission text)
- Debugging and error resolution (forward-reference bugs, path issues)
- Test suite generation
- Data pipeline implementation

**Not used for:**
- Scientific validation of results against field data
- Fabricating data, measurements, or statistics
- Generating NASA logos or official branding
- Producing the underlying agronomic knowledge (all thresholds and methods are cited
  from peer-reviewed literature)

All AI-generated code was reviewed, tested against the 46-test suite, and verified
against actual API responses. All AI-generated documentation was cross-checked against
official NASA and agronomic sources.

See [`docs/AI_DISCLOSURE.md`](docs/AI_DISCLOSURE.md) for the complete disclosure.

---

## 7. NASA Data

**Primary NASA data source:**

**NASA POWER (Prediction Of Worldwide Energy Resources) v9**
- URL: https://power.larc.nasa.gov/
- API documentation: https://power.larc.nasa.gov/docs/services/api/temporal/daily/
- Variables used: PRECTOTCORR (precipitation, mm/day), T2M_MAX (maximum temperature
  at 2 m, °C), T2M_MIN (minimum temperature at 2 m, °C)
- Temporal coverage: 2020–2023 (daily)
- Spatial coverage: 60 cells, 13°–16°E, 7.5°–12.5°N, 0.5° resolution
- Underlying model: MERRA-2 reanalysis

**Secondary NASA data source:**

**NASA GIBS (Global Imagery Browse Services)**
- URL: https://earthdata.nasa.gov/eosdis/science-system-description/eosdis-components/gibs
- Used for: MODIS Terra True Color satellite imagery overlay in the interactive map
- Tile service: https://gibs.earthdata.nasa.gov/wmts/

---

## 8. Space Agency Partner Data and Other References

**ISRIC SoilGrids v2.0** (ISRIC — World Soil Information, not NASA)
- URL: https://www.isric.org/explore/soilgrids
- Documentation: https://docs.isric.org/globaldata/soilgrids/
- Variables queried: pH (phh2o), soil organic carbon (soc), clay, sand, silt (0–5 cm)
- Status: API returned null values for Northern Cameroon — documented limitation

**Agronomic references:**
- Sivakumar, M.V.K. (1988). Predicting rainy season potential from the onset of rains
  in Southern Sahelian and Sudanian climatic zones of West Africa. *Agricultural and
  Forest Meteorology*, 42(4), 295–305.
  https://doi.org/10.1016/0168-1923(88)90039-1
- AGRHYMET (1996). Caractéristiques agroclimatiques des saisons des pluies récentes
  en Afrique soudano-sahélienne. AGRHYMET, Niamey.
- MINADER (2023). Guide technique de production du maïs au Cameroun. Ministère de
  l'Agriculture et du Développement Rural, Yaoundé.
- Dugje, I.Y. et al. (2009). Farmers' Guide to Cowpea Production in West Africa.
  IITA, Ibadan. https://www.iita.org/
- Bationo, A. et al. (2012). Soil Organic Carbon Dynamics, Functions and Management
  in West African Agro-ecosystems. Springer.
- FAO (2018). Crop Water Requirements. FAO Irrigation and Drainage Paper 56.
  https://www.fao.org/3/x0490e/x0490e00.htm
- CIMMYT heat-stress guidelines for maize (35°C pollen-viability threshold).
  https://www.cimmyt.org/

**Software and libraries:**
- Python 3.13: https://www.python.org/
- Streamlit: https://streamlit.io/
- Folium: https://python-visualization.github.io/folium/
- Plotly: https://plotly.com/python/
- pandas: https://pandas.pydata.org/
- python-pptx: https://python-pptx.readthedocs.io/
- pytest: https://pytest.org/
- QGIS: https://qgis.org/ (cartographic validation)
