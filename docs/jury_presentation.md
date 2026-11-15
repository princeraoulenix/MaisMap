# MaïsMap — NASA Space Apps Challenge 2026
## Jury Presentation Guide | Team GeoWorks

---

## Problem Statement

Maize farmers in Northern Cameroon face a critical annual decision: **when to sow**.
Sowing too early risks crop failure from false starts — early rains followed by prolonged
dry spells that kill germinating seeds. Sowing too late shortens the growing season.

The region has sparse meteorological infrastructure. Farmers rely on experience and
observation, without access to systematic historical climate analysis.

**Core question: When should farmers sow maize in Northern Cameroon?**

---

## Target Users

1. **Maize farmers** — need simple, actionable sowing guidance
2. **Agricultural extension officers** — need regional risk maps for field advisory
3. **NGOs and development agencies** — need evidence for agricultural planning
4. **Researchers** — need reproducible historical climate analysis

---

## Solution: MaïsMap

An interactive geospatial decision-support application that:
- Analyzes 40 years of NASA climate data
- Detects rainy-season onset using the validated Sivakumar/AGRHYMET method
- Identifies false starts and dry spells
- Computes a transparent, configurable agricultural risk score
- Displays results on an interactive map with cell-level popups
- Provides plain-language sowing recommendations in French

---

## NASA Datasets Used

| Dataset | Role |
|---|---|
| NASA POWER (PRECTOTCORR, T2M_MAX) | Primary — onset, false start, dry spell, heat stress |
| NASA GPM IMERG | Secondary — higher-resolution precipitation validation |
| NASA SMAP | Supplementary — surface soil moisture indicator |
| NASA GIBS (MODIS Terra) | Visualization — satellite imagery overlay |

---

## Technical Architecture

```
NASA POWER API
      ↓
src/data/nasa_pipeline.py   ← fetch + cache
      ↓
src/analysis/
  onset.py          ← Sivakumar onset detection
  false_start.py    ← false-start identification
  dry_spell.py      ← consecutive dry-day analysis
  heat_stress.py    ← Tmax > 35°C counting
  risk_model.py     ← weighted composite score
      ↓
data/processed/grid_{year}.geojson
      ↓
src/visualization/
  map.py            ← Folium interactive map
  charts.py         ← Plotly historical charts
      ↓
app.py              ← Streamlit application
```

**Stack:** Python 3.13 · Streamlit · Folium · Plotly · NASA POWER API

---

## Live Demonstration Script (7 minutes)

### Step 1 — Open MaïsMap (30 sec)
- Launch: `.venv\Scripts\python.exe -m streamlit run app.py`
- Point out: demo banner, NASA logo, year selector
- Say: "This is MaïsMap — a decision-support tool for maize farmers in Northern Cameroon,
  built on 40 years of NASA climate data."

### Step 2 — Select a year (30 sec)
- Select year **2017** (a historically difficult year in the demo)
- Point out: dashboard metrics — number of cells, risk distribution
- Say: "2017 shows elevated risk across the region — more false starts than average."

### Step 3 — Display the risk map (1 min)
- Show the color-coded map: green (low), orange (medium), red (high)
- Point out the north-south gradient (drier in the far north)
- Say: "The map shows agricultural risk at 0.5-degree resolution — about 55 km per cell.
  This matches the resolution of NASA POWER data."

### Step 4 — Select a cell (1 min)
- Click on a HIGH-risk cell in the Extrême-Nord region
- Read the popup: onset date, false start, dry spell, heat days, risk score, advice
- Say: "This cell had a false start — early rains followed by 14 dry days.
  The risk score is 78/100. The recommendation is to wait for more stable rainfall."

### Step 5 — Explain the indicators (1 min)
- Switch to the Méthodologie tab
- Show the onset definition table
- Say: "We use the Sivakumar 1988 method — the standard for West African onset detection.
  A trigger requires 20mm over 3 days, validated by no 7-day dry spell in 30 days."

### Step 6 — Historical analysis (1 min)
- Switch to Analyse historique tab
- Show onset-by-year chart and false-start frequency
- Say: "Over 14 years of demo data, we can see the variability in onset dates
  and the frequency of false starts. This is historical analysis — not a forecast."

### Step 7 — Scenario simulator (30 sec)
- Enable the simulator in the sidebar
- Set rain -10%, temperature +1°C
- Show the metric change
- Say: "The scenario simulator shows sensitivity — not a climate projection.
  It helps stakeholders understand how risk indicators respond to changing conditions."

### Step 8 — NASA data connection (30 sec)
- Show the Data Sources tab in the methodology section
- Say: "When internet is available, the pipeline fetches real NASA POWER data.
  The demo runs offline with synthetic data so the presentation never depends on connectivity."

---

## Innovation

1. **Transparent methodology** — every threshold, weight and assumption is documented and configurable
2. **Offline-ready** — works without internet using cached/demo data
3. **Validation layer** — automatic GeoJSON schema validation with provenance tracking
4. **Scenario sensitivity** — interactive exploration of hypothetical conditions
5. **Bilingual design** — French-language interface for local users, English documentation

---

## Known Limitations (be honest with the jury)

- Demo data is synthetic — real NASA POWER integration is implemented but requires internet
- 0.5° resolution cannot capture field-level variation
- Risk weights are provisional — not yet validated against observed yield data
- No seasonal forecast capability — historical analysis only
- SMAP and GPM IMERG connectors are documented but not yet fully integrated

---

## Future Improvements

1. Integrate real NASA POWER data for 1984–2024 (pipeline ready)
2. Add GPM IMERG for higher-resolution precipitation
3. Validate risk weights against MINADER crop yield records
4. Add SMS/offline export for field extension officers
5. Integrate CHIRPS or ERA5 as alternative precipitation sources
6. Add departmental administrative boundaries from official sources
7. Translate interface to local languages (Fulfulde, Arabic)

---

## Launch Command

```powershell
cd MaisMap
.\.venv\Scripts\Activate.ps1
python -m streamlit run app.py
```

Opens at: http://localhost:8501
