# MaïsMap — 7-Slide Presentation Outline
## NASA Space Apps Challenge 2026 | Team GeoWorks

---

## SLIDE 1 — Title and Problem

**Title:** MaïsMap: NASA Data for Smarter Maize Farming in Northern Cameroon

**Problem statement:**
- Northern Cameroon: 2+ million smallholder farmers depend on maize
- Critical annual decision: WHEN to sow?
- False starts (early rain followed by dry spell) destroy germinating crops
- No systematic access to historical climate analysis
- Sparse meteorological infrastructure

**Visual:** Map of Northern Cameroon with study area highlighted

---

## SLIDE 2 — The Agricultural Challenge

**The false-start problem:**
- Farmer sows after first rains → 12-day dry spell → crop failure
- Happens in 30–60% of years in the Extreme-Nord (based on NASA POWER analysis)
- Costs: lost seed, lost labor, delayed replanting, food insecurity

**The rotation opportunity:**
- Continuous maize depletes soil nitrogen
- Maize-cowpea rotation can reduce Striga pressure and diversify income
- Farmers need evidence to change practices

**Visual:** Timeline showing false-start scenario vs. stable onset

---

## SLIDE 3 — NASA and Partner Datasets

**Primary: NASA POWER v9**
- 40 years of daily precipitation and temperature
- 0.5° resolution (~55 km) — matches our grid
- Used for: onset, false starts, dry spells, heat stress, risk scores

**Visualization: NASA GIBS**
- MODIS Terra True Color overlay
- Geographic context for the interactive map

**Partner data:**
- ISRIC SoilGrids v2.0 (connector implemented)
- MINADER agricultural calendars
- Published agronomic literature (IITA, FAO, CIMMYT)

**Visual:** NASA POWER data flow diagram

---

## SLIDE 4 — Architecture and Workflow

```
NASA POWER API → fetch_nasa_power.py → data/processed/grid_{year}.geojson
                                              ↓
                              Engine A: Climate Analysis
                              (onset, false start, dry spell, heat, risk)
                                              ↓
                              Engine B: Crop Rotation Scoring
                              (3 strategies × 6 priority dimensions)
                                              ↓
                              Streamlit App → Folium Map + Plotly Charts
```

**Stack:** Python 3.13 · Streamlit · Folium · Plotly · NASA POWER API

**Visual:** Architecture diagram

---

## SLIDE 5 — Interactive Map and Climate Analysis

**Map features:**
- 60 grid cells, color-coded by risk (green/orange/red)
- Click any cell → onset date, false-start status, dry spell, heat days, risk score, sowing advice
- Year selector (2020–2023 real data)
- NASA GIBS satellite overlay option

**Historical charts:**
- Onset date by year
- False-start frequency
- Dry-spell evolution
- Heat-stress days
- Risk distribution

**Visual:** Screenshot of the MaïsMap application

---

## SLIDE 6 — Crop Rotation Laboratory

**Three strategies compared:**
- A: Maize monoculture (baseline)
- B: Maize–cowpea rotation
- C: Diversified maize–cowpea–sorghum

**Farmer priority controls:**
- Water conservation · Soil fertility · Income diversification
- Drought resilience · Erosion reduction · Lower inputs

**Climate fit assessment:**
- Each strategy scored against observed conditions for the selected year
- High-risk years favor drought-tolerant strategies (B and C)

**Honest communication:**
- Benefits labeled as hypotheses where not locally measured
- Data gaps explicitly listed

**Visual:** Strategy comparison table with priority sliders

---

## SLIDE 7 — Impact, Limitations, and Future

**Potential impact:**
- Farmers: better-timed sowing decisions, reduced false-start losses
- Extension officers: regional risk maps for field advisory
- Policymakers: evidence for agricultural planning

**Current limitations (honest):**
- 4 years of real data (2020–2023)
- 0.5° resolution — not field-level
- Rotation benefits are hypotheses, not measured outcomes
- No seasonal forecast capability

**Future development:**
- Extend to 40 years of NASA POWER data
- Integrate GPM IMERG for higher-resolution precipitation
- Validate risk weights against MINADER yield records
- Add SMS export for field extension officers
- Translate to Fulfulde and Arabic

**Launch command:**
```
python -m streamlit run app.py
```

---

## DEMO SCRIPT (7 minutes)

1. (0:00) Open app → show real-data banner, year 2022
2. (0:45) Map → click HIGH-risk cell in Extreme-Nord → read popup
3. (1:30) Explain onset + false start from popup data
4. (2:15) Climate tab → show false-start frequency chart
5. (3:00) Crop Rotation tab → adjust priorities → watch ranking change
6. (4:00) Explain Strategy B vs A for this cell's climate
7. (4:45) Scenario tab → set rain -10% → show risk shift
8. (5:30) Methodology tab → show NASA POWER source
9. (6:00) Data tab → download CSV
10. (6:30) Close: "Real NASA data, transparent methods, farmer-centered design"
