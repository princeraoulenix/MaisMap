# MaïsMap — Data References
## NASA Space Apps Challenge 2026 | Team GeoWorks

---

## ACTUALLY DOWNLOADED AND PROCESSED

### NASA POWER v9
- **Institution:** NASA Langley Research Center
- **Product:** POWER Daily Agroclimatology (AG community)
- **Variables:** PRECTOTCORR (precipitation mm/day), T2M_MAX (max temp °C), T2M_MIN (min temp °C)
- **URL:** https://power.larc.nasa.gov/api/temporal/daily/point
- **Temporal coverage:** 2020–2023 (4 years × 60 cells = 239 successful fetches)
- **Spatial resolution:** 0.5° × 0.5° (~55 km)
- **Temporal resolution:** Daily
- **Processing:** Onset detection, false-start detection, dry-spell analysis, heat-stress counting, risk scoring
- **Cache:** data/raw/cache/power_*.json
- **Output:** data/processed/grid_{year}.geojson
- **License:** NASA Open Data — free for research and educational use
- **Date accessed:** 2026-11-15
- **Citation:** Stackhouse, P.W. et al. (2018). POWER Release 8 (with GIS Applications). American Meteorological Society Annual Meeting.

---

## DATA ACCESSED THROUGH A SERVICE (partial results)

### ISRIC SoilGrids v2.0
- **Institution:** ISRIC — World Soil Information
- **Product:** SoilGrids v2.0 REST API
- **Variables attempted:** phh2o, soc, clay, sand, silt, bdod, cec, nitrogen (0–5 cm depth)
- **URL:** https://rest.isric.org/soilgrids/v2.0/properties/query
- **Result:** API returned null values for all queried cells in Northern Cameroon
- **Known limitation:** SoilGrids v2.0 has reduced coverage in parts of sub-Saharan Africa where training data is sparse
- **Status:** Connector implemented, data unavailable for this region
- **Cache:** data/raw/cache/soil_*.json (25 files, all with null property values)
- **License:** CC BY 4.0
- **Date accessed:** 2026-11-15
- **Citation:** Poggio, L. et al. (2021). SoilGrids 2.0: producing soil information for the globe with quantified spatial uncertainty. SOIL, 7, 217–240.

---

## VISUAL-ONLY LAYERS

### NASA GIBS — MODIS Terra True Color
- **Institution:** NASA Earthdata / GIBS
- **Product:** MODIS_Terra_CorrectedReflectance_TrueColor
- **URL:** https://gibs.earthdata.nasa.gov/wmts/epsg3857/best/
- **Role:** Optional satellite imagery background overlay in Folium map
- **Note:** Visual only — not used in any numerical calculation
- **License:** NASA Open Data
- **Date accessed:** 2026-11-15

---

## REFERENCES CONSULTED (not integrated as data)

### NASA GPM IMERG
- **URL:** https://gpm.nasa.gov/data/imerg
- **Product:** GPM IMERG Final Run v07
- **Status:** Connector architecture documented; requires NASA Earthdata authentication
- **Reason not integrated:** Requires user account; beyond current scope

### NASA SMAP
- **URL:** https://nsidc.org/data/smap
- **Products investigated:** SPL3SMP, SPL4SMGP
- **Status:** Documented; not integrated
- **Reason:** Requires NSIDC Earthdata account and specialized HDF5 processing

### NASA SRTM / NASADEM
- **URL:** https://www.earthdata.nasa.gov/data/catalog/lpcloud-nasadem-hgt-001
- **Status:** Documented; not integrated
- **Reason:** Requires rasterio for raster processing — not installed

### ESA Copernicus Sentinel-2
- **URL:** https://dataspace.copernicus.eu/
- **Status:** Documented; not integrated
- **Reason:** Large raster downloads and cloud masking beyond current scope
- **Note:** ESA partner data — not a NASA mission

### FAO GAEZ v5
- **URL:** https://www.fao.org/land-water/resources/tools/databases/gaez/en
- **Status:** Referenced for crop suitability context; not integrated as data
- **Reason:** No bulk download API available

---

## AGRONOMIC REFERENCES USED IN CROP ROTATION ENGINE

| Reference | Role |
|---|---|
| MINADER (2023). Guide technique de production du maïs au Cameroun | Crop calendars, sowing windows |
| Dugje, I.Y. et al. (2009). Farmers' Guide to Cowpea Production in West Africa. IITA | Cowpea N-fixation, water requirements |
| Bationo, A. et al. (2012). Soil Organic Carbon Dynamics in West African Agro-ecosystems. Springer | Soil organic matter, N cycling |
| Kamara, A.Y. et al. (2014). Maize-cowpea intercropping in Sudan Savanna. Experimental Agriculture | Rotation benefits |
| FAO (2018). Crop Water Requirements. FAO Irrigation Paper 56 | Water demand estimates |
| Sivakumar, M.V.K. (1988). Predicting rainy season potential. Agricultural and Forest Meteorology 42(4) | Onset detection method |
| Schlenker, W. & Roberts, M.J. (2009). Nonlinear temperature effects on US crop yields. PNAS | Heat stress threshold |
| CIMMYT Heat Stress Guidelines | 35°C Tmax threshold for maize |

---

## OPEN-SOURCE LIBRARIES

| Library | Version | Role |
|---|---|---|
| streamlit | 1.67.0 | Web application framework |
| folium | 1.0.0 | Interactive maps |
| streamlit-folium | 0.27.4 | Folium-Streamlit integration |
| plotly | 7.1.0 | Interactive charts |
| pandas | 3.1.1 | Data manipulation |
| requests | 2.34.2 | HTTP API calls |
| numpy | 2.5.4 | Numerical operations |
| pytest | 9.2.0 | Automated testing |
