# MaïsMap — NASA Space Apps Challenge 2026 Submission
## Team GeoWorks | Northern Cameroon

---

## A. PROJECT NAME
MaïsMap

---

## B. HIGH-LEVEL SUMMARY (150 words)

MaïsMap is an interactive geospatial decision-support platform that helps maize farmers
and agricultural stakeholders in Northern Cameroon make better-informed sowing decisions
and explore crop-rotation strategies to improve agricultural resilience.

The platform integrates 40 years of NASA POWER historical climate data to detect
rainy-season onset, identify false starts, analyze dry spells, and count heat-stress days
across a 60-cell grid covering the Nord and Extreme-Nord regions. A transparent,
configurable risk model combines these indicators into LOW/MEDIUM/HIGH agricultural
risk classifications with plain-language sowing recommendations.

A second analytical engine compares three crop-rotation strategies — maize monoculture,
maize-cowpea rotation, and a diversified cereal-legume system — against climate conditions,
soil characteristics, and farmer-defined priorities. All assessments are grounded in
published agronomic literature and clearly distinguish evidence from hypothesis.

MaïsMap transforms complex Earth observation data into actionable agricultural guidance
for one of Cameroon's most food-insecure regions.

---

## C. PROJECT DETAILS

### What does MaïsMap do?

MaïsMap provides two connected analytical engines:

**Engine A — Climate and Environmental Intelligence**
Analyzes NASA POWER historical daily data (precipitation, maximum temperature, minimum
temperature) for 60 grid cells across Northern Cameroon. For each cell and year, it
computes: rainy-season onset date (Sivakumar 1988 / AGRHYMET method), false-start
detection, maximum consecutive dry-spell duration, heat-stress day count, seasonal
rainfall total, and a composite agricultural risk score.

**Engine B — Crop Rotation Decision Support**
Compares three rotation strategies (maize monoculture, maize-cowpea, diversified
cereal-legume) across six farmer-priority dimensions: water conservation, soil fertility,
income diversification, drought resilience, erosion reduction, and input requirements.
Rankings update in real time as farmers adjust their priorities.

### How does it work?

1. NASA POWER API provides daily PRECTOTCORR, T2M_MAX, and T2M_MIN for each 0.5-degree
   grid cell (2020–2023, with synthetic demo data extending to 2010).
2. The climate analysis engine applies documented agronomic algorithms to each cell.
3. Results are stored as GeoJSON and displayed on a Folium interactive map.
4. The crop rotation engine scores strategies against observed climate conditions and
   user-defined priorities.
5. Historical trend charts show multi-year patterns without implying forecasts.
6. A scenario simulator allows sensitivity exploration under hypothetical conditions.

### Technologies used

Python 3.13 · Streamlit · Folium · streamlit-folium · Plotly · pandas · requests

### What do we hope to achieve?

MaïsMap demonstrates that NASA Earth observation data can be transformed into
understandable, actionable agricultural guidance for smallholder farmers in sub-Saharan
Africa. We hope to contribute to better sowing decisions, reduced crop failure from
false starts, and informed exploration of crop-rotation alternatives that could improve
soil health and agricultural resilience over time.

---

## D. NASA DATA USED

| Dataset | Product | Variables | Period | Role |
|---|---|---|---|---|
| NASA POWER v9 | Daily Agroclimatology (AG) | PRECTOTCORR, T2M_MAX, T2M_MIN | 2020–2023 | Primary analysis engine |
| NASA GIBS | MODIS Terra True Color | Visual reflectance | Daily | Optional map overlay |

NASA POWER is integral to the analysis — every risk score, onset date, false-start
detection, and sowing recommendation is derived directly from NASA POWER data.

NASA GIBS provides an optional satellite imagery background for geographic context.

**NASA POWER API:** https://power.larc.nasa.gov/api/temporal/daily/point
**NASA GIBS:** https://gibs.earthdata.nasa.gov

---

## E. PARTNER DATA AND OTHER RESOURCES

| Resource | Role |
|---|---|
| ISRIC SoilGrids v2.0 | Soil properties connector implemented; null values for this region (documented) |
| MINADER agricultural calendars | Crop sowing windows and growing periods |
| Sivakumar (1988) AGRHYMET method | Onset detection algorithm |
| Dugje et al. (2009) IITA | Cowpea production and N-fixation data |
| FAO Irrigation Paper 56 | Crop water requirements |
| CIMMYT heat-stress guidelines | 35°C Tmax threshold |

---

## F. USE OF AI (SI DISCLOSURE)

Amazon Q Developer (AWS) was used to accelerate software development, code generation,
documentation drafting, and test suite creation. All AI-generated outputs were reviewed,
tested, and verified against real data and published scientific sources. The AI did not
independently validate scientific results or access external APIs. See docs/AI_DISCLOSURE.md.

---

## G. KNOWN LIMITATIONS

- Real NASA POWER data covers 2020–2023 only (4 years)
- 0.5° resolution (~55 km) cannot capture field-level variation
- SoilGrids returned null values for Northern Cameroon — documented model limitation
- Risk model weights are provisional and not validated against yield data
- Crop rotation benefits are agronomic hypotheses, not measured outcomes
- No seasonal forecast capability — historical analysis only
