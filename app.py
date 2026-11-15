"""
MaïsMap — Agricultural Decision-Support Platform
NASA Space Apps Challenge 2026 | Team GeoWorks | Northern Cameroon
Engine A: Climate Intelligence  |  Engine B: Crop Rotation Lab
"""
import sys, os, json, copy, glob
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import streamlit as st
from streamlit_folium import st_folium
import pandas as pd

from config.settings import (
    APP_TITLE, APP_SUBTITLE, DEMO_YEARS, DATA_DEMO_PATH,
    USE_REAL_DATA_DEFAULT, REAL_DATA_YEARS, DATA_PROCESSED_PATH,
)
from src.data.data_loader import load_dataset, get_available_years
from src.data.validator import validate_geojson
from src.visualization.map import build_map
from src.visualization.charts import (
    chart_onset_by_year, chart_false_start_frequency,
    chart_dry_spell, chart_heat_days, chart_risk_distribution,
)
from src.analysis.risk_model import compute_risk
from src.crop_rotation.engine import (
    ROTATION_STRATEGIES, PRIORITY_DIMENSIONS,
    score_strategies, climate_suitability_score, CROP_CALENDARS,
)

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="MaïsMap — Agricultural Intelligence",
    page_icon="🌽",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Professional CSS ──────────────────────────────────────────────────────────
st.markdown("""
<style>
  /* Base */
  .stApp { background: #f7f6f2; }
  section[data-testid="stSidebar"] { background: #1a2e1a; }
  section[data-testid="stSidebar"] * { color: #e8f0e8 !important; }
  section[data-testid="stSidebar"] .stSelectbox label,
  section[data-testid="stSidebar"] .stMultiSelect label,
  section[data-testid="stSidebar"] .stSlider label,
  section[data-testid="stSidebar"] .stCheckbox label { color: #b8d4b8 !important; font-size:12px; }
  section[data-testid="stSidebar"] hr { border-color: #2d4a2d; }

  /* Header */
  .maismap-header {
    background: #1a2e1a;
    color: white;
    padding: 16px 24px 12px 24px;
    border-radius: 4px;
    margin-bottom: 16px;
    border-left: 4px solid #27ae60;
  }
  .maismap-header h1 {
    margin: 0; font-size: 26px; font-weight: 700;
    color: #27ae60; letter-spacing: 0.5px;
  }
  .maismap-header p {
    margin: 4px 0 0 0; font-size: 13px; color: #a8c4a8;
  }

  /* Banners */
  .banner-real {
    background: #eaf7ee; border: 1px solid #27ae60;
    border-left: 4px solid #27ae60; border-radius: 3px;
    padding: 8px 14px; font-size: 13px; color: #1a5c2a;
    margin-bottom: 12px;
  }
  .banner-demo {
    background: #fef9e7; border: 1px solid #f39c12;
    border-left: 4px solid #f39c12; border-radius: 3px;
    padding: 8px 14px; font-size: 13px; color: #7d5a00;
    margin-bottom: 12px;
  }
  .banner-warn {
    background: #fdf2f2; border: 1px solid #c0392b;
    border-left: 4px solid #c0392b; border-radius: 3px;
    padding: 8px 14px; font-size: 13px; color: #7b1a1a;
    margin-bottom: 8px;
  }
  .banner-info {
    background: #eaf4fb; border: 1px solid #2980b9;
    border-left: 4px solid #2980b9; border-radius: 3px;
    padding: 8px 14px; font-size: 13px; color: #1a4a6b;
    margin-bottom: 8px;
  }

  /* Metric cards */
  .metric-row { display: flex; gap: 10px; margin-bottom: 14px; flex-wrap: wrap; }
  .metric-card {
    background: white; border: 1px solid #dde; border-radius: 4px;
    padding: 10px 16px; min-width: 110px; flex: 1;
    border-top: 3px solid #27ae60;
  }
  .metric-card.orange { border-top-color: #e67e22; }
  .metric-card.red    { border-top-color: #c0392b; }
  .metric-card.blue   { border-top-color: #2980b9; }
  .metric-card.grey   { border-top-color: #7f8c8d; }
  .metric-label { font-size: 11px; color: #666; text-transform: uppercase;
                  letter-spacing: 0.5px; margin-bottom: 2px; }
  .metric-value { font-size: 22px; font-weight: 700; color: #1a2e1a; }
  .metric-sub   { font-size: 11px; color: #888; margin-top: 1px; }

  /* Section headers */
  .section-hdr {
    font-size: 14px; font-weight: 600; color: #1a2e1a;
    border-bottom: 2px solid #27ae60; padding-bottom: 4px;
    margin: 16px 0 10px 0; text-transform: uppercase; letter-spacing: 0.5px;
  }

  /* Strategy cards */
  .strat-card {
    background: white; border: 1px solid #dde; border-radius: 4px;
    padding: 14px 16px; margin-bottom: 8px;
  }
  .strat-card.top { border-left: 4px solid #27ae60; }

  /* Tab styling */
  .stTabs [data-baseweb="tab-list"] { gap: 4px; }
  .stTabs [data-baseweb="tab"] {
    background: #e8ede8; border-radius: 3px 3px 0 0;
    padding: 6px 16px; font-size: 13px; font-weight: 500;
    color: #2d4a2d;
  }
  .stTabs [aria-selected="true"] {
    background: #1a2e1a !important; color: white !important;
  }

  /* Data table */
  .stDataFrame { border: 1px solid #dde; border-radius: 4px; }

  /* Sidebar brand */
  .sidebar-brand {
    font-size: 20px; font-weight: 700; color: #27ae60 !important;
    letter-spacing: 0.5px; margin-bottom: 2px;
  }
  .sidebar-sub { font-size: 11px; color: #7a9a7a !important; }
  .sidebar-section { font-size: 11px; font-weight: 600;
    color: #7a9a7a !important; text-transform: uppercase;
    letter-spacing: 0.5px; margin: 12px 0 4px 0; }
  .sidebar-attr { font-size: 10px; color: #5a7a5a !important; line-height: 1.6; }
</style>
""", unsafe_allow_html=True)


# ── Cached data helpers ───────────────────────────────────────────────────────
@st.cache_data(ttl=600, show_spinner=False)
def _load_all_years_cached(use_demo: bool, region: str, years: tuple) -> list[dict]:
    if use_demo:
        if not os.path.exists(DATA_DEMO_PATH):
            return []
        with open(DATA_DEMO_PATH, encoding="utf-8") as f:
            full = json.load(f)
        all_feats = full.get("features", [])
    else:
        all_feats = []
        for fp in sorted(glob.glob(os.path.join(DATA_PROCESSED_PATH, "grid_*.geojson"))):
            with open(fp, encoding="utf-8") as f:
                gj = json.load(f)
            all_feats.extend(gj.get("features", []))

    result = []
    for year in years:
        feats = [
            f["properties"] for f in all_feats
            if f["properties"].get("year") == year
            and (region == "All" or f["properties"].get("region") == region)
        ]
        if not feats:
            continue
        onsets = [p["season_onset_date"] for p in feats if p.get("season_onset_date")]
        dry    = [p["dry_spell_days"] for p in feats if p.get("dry_spell_days") is not None]
        heat   = [p["heat_days"] for p in feats if p.get("heat_days") is not None]
        scores = [p["risk_score"] for p in feats if p.get("risk_score") is not None]
        rain   = [p["seasonal_rain_mm"] for p in feats if p.get("seasonal_rain_mm") is not None]
        fs_count = sum(1 for p in feats if p.get("false_start"))
        classes  = [p.get("risk_class") for p in feats if p.get("risk_class")]
        dominant = max(set(classes), key=classes.count) if classes else "MEDIUM"
        result.append({
            "year": year,
            "season_onset_date": round(sum(onsets)/len(onsets)) if onsets else None,
            "false_start": fs_count > len(feats) * 0.5,
            "false_start_pct": round(fs_count / len(feats) * 100),
            "dry_spell_days": round(sum(dry)/len(dry), 1) if dry else None,
            "heat_days": round(sum(heat)/len(heat), 1) if heat else None,
            "risk_score": round(sum(scores)/len(scores), 1) if scores else None,
            "risk_class": dominant,
            "seasonal_rain_mm": round(sum(rain)/len(rain), 1) if rain else None,
        })
    return result


def _render_scenario(features, rain_delta, temp_delta):
    modified = []
    for f in features:
        p = copy.deepcopy(f["properties"])
        if p.get("dry_spell_days") is not None:
            p["dry_spell_days"] = max(0, round(p["dry_spell_days"] * (1 - rain_delta / 100)))
        if p.get("heat_days") is not None:
            p["heat_days"] = max(0, p["heat_days"] + round(temp_delta * 2))
        risk = compute_risk(
            p.get("false_start", False),
            p.get("dry_spell_days", 0),
            p.get("heat_days", 0),
        )
        p["risk_class"] = risk["class"]
        p["risk_score"]  = risk["score"]
        modified.append(p)

    n_low  = sum(1 for p in modified if p["risk_class"] == "LOW")
    n_med  = sum(1 for p in modified if p["risk_class"] == "MEDIUM")
    n_high = sum(1 for p in modified if p["risk_class"] == "HIGH")

    st.markdown(
        f'<div class="banner-info">Scenario: rainfall <b>{rain_delta:+d}%</b> · '
        f'temperature <b>{temp_delta:+.1f} °C</b></div>',
        unsafe_allow_html=True,
    )
    c1, c2, c3 = st.columns(3)
    c1.metric("Low risk cells", n_low)
    c2.metric("Moderate risk cells", n_med)
    c3.metric("High risk cells", n_high)

    mod_gj = {
        "type": "FeatureCollection",
        "features": [
            {"type": "Feature", "geometry": features[i]["geometry"], "properties": modified[i]}
            for i in range(len(features))
        ],
    }
    st_folium(build_map(mod_gj), width="100%", height=420,
              returned_objects=[], key="scenario_map")


# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown('<div class="sidebar-brand">🌽 MaïsMap</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="sidebar-sub">Climate & Soil Intelligence<br>'
        'Northern Cameroon · GeoWorks · Space Apps 2026</div>',
        unsafe_allow_html=True,
    )
    st.divider()

    real_years = get_available_years(use_demo=False)
    demo_years = get_available_years(use_demo=True)
    all_years  = sorted(set(real_years + demo_years), reverse=True)
    if not all_years:
        all_years = sorted(DEMO_YEARS, reverse=True)

    st.markdown('<div class="sidebar-section">Year</div>', unsafe_allow_html=True)
    selected_year = st.selectbox("Select year", options=all_years, label_visibility="collapsed")
    use_demo_for_year = selected_year not in real_years

    st.markdown('<div class="sidebar-section">Filters</div>', unsafe_allow_html=True)
    risk_filter = st.multiselect(
        "Risk class", ["LOW", "MEDIUM", "HIGH"],
        default=["LOW", "MEDIUM", "HIGH"],
    )
    region_options = ["All", "Nord", "Extreme-Nord", "Adamaoua"]
    selected_region = st.selectbox("Region", region_options)

    st.divider()
    st.markdown('<div class="sidebar-section">Map Options</div>', unsafe_allow_html=True)
    show_satellite = st.checkbox("NASA GIBS satellite overlay", value=False)

    st.divider()
    st.markdown('<div class="sidebar-section">Scenario Simulator</div>', unsafe_allow_html=True)
    show_scenario = st.checkbox("Enable sensitivity simulator", value=False)
    rain_delta = st.slider("Rainfall change (%)", -30, 30, 0, step=5,
                           disabled=not show_scenario)
    temp_delta = st.slider("Temperature change (°C)", -2, 4, 0, step=1,
                           disabled=not show_scenario)

    st.divider()
    st.markdown('<div class="sidebar-section">Data Sources</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="sidebar-attr">'
        '<b>NASA POWER v9</b> — PRECTOTCORR, T2M_MAX, T2M_MIN<br>'
        '<b>NASA GIBS</b> — MODIS overlay (optional)<br>'
        '<b>ISRIC SoilGrids v2.0</b> — queried; null values for this region<br>'
        '<b>Basemap</b> — © OpenStreetMap contributors'
        '</div>',
        unsafe_allow_html=True,
    )


# ── Load data ─────────────────────────────────────────────────────────────────
geojson, is_demo = load_dataset(selected_year, use_demo=use_demo_for_year)

# ── Application header ────────────────────────────────────────────────────────
st.markdown(
    '<div class="maismap-header">'
    '<h1>MaïsMap</h1>'
    '<p>Climate &amp; Soil Intelligence for Smarter Agriculture in Northern Cameroon &nbsp;·&nbsp; '
    'NASA Space Apps Challenge 2026 &nbsp;·&nbsp; Team GeoWorks</p>'
    '</div>',
    unsafe_allow_html=True,
)

if is_demo:
    st.markdown(
        '<div class="banner-demo">⚠ <b>Demonstration data</b> — synthetic dataset for '
        'illustration only. Not official NASA measurements.</div>',
        unsafe_allow_html=True,
    )
else:
    st.markdown(
        f'<div class="banner-real">✓ <b>Real NASA POWER data</b> — '
        f'PRECTOTCORR · T2M_MAX · T2M_MIN &nbsp;|&nbsp; Year {selected_year} &nbsp;|&nbsp; '
        f'60-cell grid · 0.5° resolution · Northern Cameroon</div>',
        unsafe_allow_html=True,
    )

if not geojson:
    st.error(
        "No data available. Run `python src/acquisition/fetch_nasa_power.py` "
        "to fetch real NASA POWER data."
    )
    st.stop()

# Apply region filter
region_map = {"All": "All", "Nord": "Nord", "Extreme-Nord": "Extreme-Nord", "Adamaoua": "Adamaoua"}
region_filter_val = region_map.get(selected_region, "All")
all_features = geojson.get("features", [])
if selected_region != "All":
    all_features = [
        f for f in all_features
        if f["properties"].get("region") == region_filter_val
    ]

validation = validate_geojson({"type": "FeatureCollection", "features": all_features})

# ── Dashboard metrics ─────────────────────────────────────────────────────────
n_cells = len(all_features)
n_low   = sum(1 for f in all_features if f["properties"].get("risk_class") == "LOW")
n_med   = sum(1 for f in all_features if f["properties"].get("risk_class") == "MEDIUM")
n_high  = sum(1 for f in all_features if f["properties"].get("risk_class") == "HIGH")
n_fs    = sum(1 for f in all_features if f["properties"].get("false_start"))
rain_vals = [f["properties"].get("seasonal_rain_mm") for f in all_features
             if f["properties"].get("seasonal_rain_mm")]
mean_rain = round(sum(rain_vals) / len(rain_vals)) if rain_vals else None
heat_vals = [f["properties"].get("heat_days") for f in all_features
             if f["properties"].get("heat_days") is not None]
mean_heat = round(sum(heat_vals) / len(heat_vals), 1) if heat_vals else None

st.markdown(
    f"""<div class="metric-row">
      <div class="metric-card grey">
        <div class="metric-label">Grid cells</div>
        <div class="metric-value">{n_cells}</div>
        <div class="metric-sub">0.5° × 0.5° (~55 km)</div>
      </div>
      <div class="metric-card">
        <div class="metric-label">Low risk</div>
        <div class="metric-value">{n_low}</div>
        <div class="metric-sub">Favourable conditions</div>
      </div>
      <div class="metric-card orange">
        <div class="metric-label">Moderate risk</div>
        <div class="metric-value">{n_med}</div>
        <div class="metric-sub">Monitor closely</div>
      </div>
      <div class="metric-card red">
        <div class="metric-label">High risk</div>
        <div class="metric-value">{n_high}</div>
        <div class="metric-sub">Caution advised</div>
      </div>
      <div class="metric-card orange">
        <div class="metric-label">False starts</div>
        <div class="metric-value">{n_fs}</div>
        <div class="metric-sub">Cells with false onset</div>
      </div>
      <div class="metric-card blue">
        <div class="metric-label">Mean seasonal rain</div>
        <div class="metric-value">{mean_rain if mean_rain else 'N/A'}</div>
        <div class="metric-sub">mm (growing season)</div>
      </div>
      <div class="metric-card red">
        <div class="metric-label">Mean heat days</div>
        <div class="metric-value">{mean_heat if mean_heat is not None else 'N/A'}</div>
        <div class="metric-sub">Days Tmax &gt; 35 °C</div>
      </div>
    </div>""",
    unsafe_allow_html=True,
)

if validation["invalid"] > 0:
    st.markdown(
        f'<div class="banner-warn">{validation["invalid"]} cell(s) with data validation issues — '
        f'see Data tab for details.</div>',
        unsafe_allow_html=True,
    )

# ── Tabs ──────────────────────────────────────────────────────────────────────
tab_map, tab_climate, tab_rotation, tab_scenario, tab_data, tab_method = st.tabs([
    "Map", "Climate Analysis", "Crop Rotation Lab",
    "Scenario", "Data", "Methodology",
])

# ── MAP TAB ───────────────────────────────────────────────────────────────────
with tab_map:
    col_map, col_info = st.columns([3, 1])
    with col_map:
        st.markdown(
            f'<div class="section-hdr">Agricultural Risk Map — {selected_year}</div>',
            unsafe_allow_html=True,
        )
        filtered_gj = {**geojson, "features": all_features}
        folium_map = build_map(filtered_gj, selected_risk=risk_filter,
                               show_satellite=show_satellite)
        st_folium(folium_map, width="100%", height=560, returned_objects=[])

    with col_info:
        st.markdown(
            '<div class="section-hdr">How to read this map</div>',
            unsafe_allow_html=True,
        )
        st.markdown("""
**Grid cells** represent 0.5° × 0.5° areas (~55 km). Each cell is coloured by its
composite agricultural risk class for the selected year.

**Click any cell** to see detailed indicators: season onset date, false start,
dry-spell days, heat-stress days, risk score, and sowing advice.

**Risk classes:**
- 🟢 **Low** — favourable conditions, sowing possible
- 🟠 **Moderate** — acceptable but uncertain
- 🔴 **High** — significant stress indicators

**Risk score formula:**
- False start: 40%
- Dry spell: 35%
- Heat stress: 25%

*Source: Sivakumar (1988) / AGRHYMET method*
        """)
        st.markdown(
            '<div class="section-hdr">Study Area</div>',
            unsafe_allow_html=True,
        )
        st.markdown("""
**Regions:** Nord & Extreme-Nord Cameroon

**Extent:** 13°–16°E, 7.5°–12.5°N

**Cells:** 60 per year (6 lon × 10 lat)

**CRS:** EPSG:4326 (WGS84)

**Basemap:** © OpenStreetMap contributors
        """)
        if not is_demo:
            st.markdown(
                '<div class="section-hdr">Data Period</div>',
                unsafe_allow_html=True,
            )
            st.markdown(f"**Year:** {selected_year}\n\n**Source:** NASA POWER v9\n\n"
                        f"**Variables:** PRECTOTCORR, T2M_MAX, T2M_MIN")

# ── CLIMATE TAB ───────────────────────────────────────────────────────────────
with tab_climate:
    st.markdown(
        '<div class="section-hdr">Historical Climate Analysis — All Available Years</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="banner-info">Historical analysis based on real NASA POWER data '
        '(2020–2023) and synthetic demo data (2010–2023). '
        'These charts describe observed past conditions — not forecasts.</div>',
        unsafe_allow_html=True,
    )

    avail_years = sorted(set(real_years + (demo_years if use_demo_for_year else [])))
    trend_data = _load_all_years_cached(
        use_demo_for_year, region_filter_val, tuple(avail_years)
    )

    if trend_data:
        col_a, col_b = st.columns(2)
        with col_a:
            st.plotly_chart(chart_onset_by_year(trend_data), use_container_width=True)
            st.plotly_chart(chart_dry_spell(trend_data), use_container_width=True)
        with col_b:
            st.plotly_chart(chart_false_start_frequency(trend_data), use_container_width=True)
            st.plotly_chart(chart_heat_days(trend_data), use_container_width=True)
        st.plotly_chart(chart_risk_distribution(trend_data), use_container_width=True)

        st.markdown(
            '<div class="section-hdr">Summary Statistics</div>',
            unsafe_allow_html=True,
        )
        valid_onsets = [d["season_onset_date"] for d in trend_data if d.get("season_onset_date")]
        fs_yrs = sum(1 for d in trend_data if d.get("false_start"))
        rain_trend = [d["seasonal_rain_mm"] for d in trend_data if d.get("seasonal_rain_mm")]
        heat_trend = [d["heat_days"] for d in trend_data if d.get("heat_days") is not None]
        sc1, sc2, sc3, sc4 = st.columns(4)
        sc1.metric("Years analysed", len(trend_data))
        sc2.metric("Mean onset (DOY)", round(sum(valid_onsets)/len(valid_onsets)) if valid_onsets else "N/A")
        sc3.metric("Years with false start (>50% cells)", fs_yrs)
        sc4.metric("Mean seasonal rain (mm)", round(sum(rain_trend)/len(rain_trend)) if rain_trend else "N/A")
    else:
        st.info("No historical data available for this region and year selection.")

# ── CROP ROTATION TAB ─────────────────────────────────────────────────────────
with tab_rotation:
    st.markdown(
        '<div class="section-hdr">Crop Rotation Laboratory — Engine B</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="banner-info">'
        'Compare three rotation strategies for Northern Cameroon. '
        'Assessments are based on published agronomic literature (MINADER, IITA, FAO). '
        'Benefits labeled as hypotheses have not been measured at this specific location. '
        'This tool supports informed discussion — it does not prescribe optimal rotations.'
        '</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="section-hdr">Farmer Priorities</div>',
        unsafe_allow_html=True,
    )
    st.caption("Adjust the sliders to reflect local priorities. Strategy rankings update automatically.")
    p_col1, p_col2, p_col3 = st.columns(3)
    with p_col1:
        w_water  = st.slider("Water conservation", 0.0, 1.0, 0.5, 0.1)
        w_soil   = st.slider("Soil fertility", 0.0, 1.0, 0.5, 0.1)
    with p_col2:
        w_income = st.slider("Income diversification", 0.0, 1.0, 0.5, 0.1)
        w_drought = st.slider("Drought resilience", 0.0, 1.0, 0.5, 0.1)
    with p_col3:
        w_erosion = st.slider("Reduced erosion", 0.0, 1.0, 0.3, 0.1)
        w_inputs  = st.slider("Lower inputs", 0.0, 1.0, 0.3, 0.1)

    priorities = {
        "water_conservation": w_water,
        "soil_fertility": w_soil,
        "income_diversification": w_income,
        "drought_resilience": w_drought,
        "reduced_erosion": w_erosion,
        "lower_inputs": w_inputs,
    }
    scores = score_strategies(priorities)
    ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)

    st.markdown(
        '<div class="section-hdr">Strategy Ranking</div>',
        unsafe_allow_html=True,
    )
    rank_cols = st.columns(3)
    medals = ["1st", "2nd", "3rd"]
    for i, (sid, score) in enumerate(ranked):
        s = ROTATION_STRATEGIES[sid]
        with rank_cols[i]:
            st.metric(f"{medals[i]}: Strategy {sid}", f"{score}/100", s["name"])

    st.divider()
    st.markdown(
        '<div class="section-hdr">Detailed Strategy Comparison</div>',
        unsafe_allow_html=True,
    )

    rep_cell = all_features[len(all_features) // 2]["properties"] if all_features else {}
    risk_ctx = rep_cell.get("risk_class", "MEDIUM")
    fs_ctx   = rep_cell.get("false_start", False)
    dry_ctx  = rep_cell.get("dry_spell_days", 0)

    for sid in ["A", "B", "C"]:
        s = ROTATION_STRATEGIES[sid]
        clim = climate_suitability_score(risk_ctx, fs_ctx, dry_ctx, sid)
        score_val = scores[sid]
        is_top = sid == ranked[0][0]

        with st.expander(
            f"Strategy {sid}: {s['name']} — Priority score: {score_val}/100 | "
            f"Climate fit: {clim['label']} ({clim['score']}/100)",
            expanded=is_top,
        ):
            col_l, col_r = st.columns([2, 1])
            with col_l:
                st.markdown(f"**Crop sequence:** {' → '.join(s['sequence'])}")
                st.markdown(f"*{s['description']}*")
                st.markdown(f"**Climate suitability:** {s['climate_suitability']}")
                st.markdown(f"**Water demand:** {s['water_demand']}")
                st.markdown(f"**Nitrogen contribution:** {s['nitrogen_contribution']}")
                st.markdown(f"**Soil organic matter:** {s['soil_organic_matter']}")
                st.markdown(f"**Erosion protection:** {s['erosion_protection']}")
                st.markdown(f"**Market suitability:** {s['market_suitability']}")
                st.markdown("**Potential benefits (literature-based):**")
                for b in s["benefits"]:
                    st.markdown(f"- {b}")
                st.markdown("**Risks and limitations:**")
                for r in s["risks"]:
                    st.markdown(f"- {r}")
            with col_r:
                st.markdown(f"**Confidence:** {s['confidence']}")
                st.markdown(f"**Climate fit for {selected_year}:** {clim['label']}")
                for note in clim["notes"]:
                    st.caption(f"• {note}")
                st.markdown("**Data gaps:**")
                for gap in s["data_gaps"]:
                    st.caption(f"• {gap}")

    st.divider()
    st.markdown(
        '<div class="section-hdr">Crop Calendar Reference</div>',
        unsafe_allow_html=True,
    )
    st.caption("Source: MINADER agricultural calendar for Nord and Extreme-Nord regions")
    cal_df = pd.DataFrame([
        {"Crop": k.capitalize(), **{kk: vv for kk, vv in v.items()}}
        for k, v in CROP_CALENDARS.items()
    ])
    st.dataframe(cal_df, use_container_width=True, hide_index=True)

# ── SCENARIO TAB ──────────────────────────────────────────────────────────────
with tab_scenario:
    st.markdown(
        '<div class="section-hdr">Scenario Simulator — Sensitivity Analysis</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="banner-warn">⚠ Sensitivity scenario only — NOT a climate forecast. '
        'Shows how risk indicators would respond to hypothetical changes in rainfall '
        'and temperature. Enable the simulator in the sidebar.</div>',
        unsafe_allow_html=True,
    )
    if show_scenario:
        _render_scenario(all_features, rain_delta, temp_delta)
    else:
        st.info("Enable the scenario simulator in the sidebar to explore hypothetical climate changes.")

# ── DATA TAB ──────────────────────────────────────────────────────────────────
with tab_data:
    st.markdown(
        '<div class="section-hdr">Data — Filtered Cells</div>',
        unsafe_allow_html=True,
    )
    with st.expander("GeoJSON validation report", expanded=False):
        st.json(validation)

    rows = [f["properties"] for f in all_features]
    if rows:
        df = pd.DataFrame(rows)
        display_cols = [
            "cell_id", "region", "department", "year",
            "season_onset_date_str", "false_start", "dry_spell_days",
            "heat_days", "seasonal_rain_mm", "mean_tmax_c",
            "risk_score", "risk_class", "confidence", "data_source",
        ]
        display_cols = [c for c in display_cols if c in df.columns]
        st.dataframe(df[display_cols], use_container_width=True, height=420)
        csv = df[display_cols].to_csv(index=False).encode("utf-8")
        st.download_button(
            "Download CSV",
            csv,
            f"maismap_{selected_year}_{selected_region}.csv",
            "text/csv",
        )
    else:
        st.info("No data available for the current filter selection.")

# ── METHODOLOGY TAB ───────────────────────────────────────────────────────────
with tab_method:
    st.markdown(
        '<div class="section-hdr">Scientific Methodology & Data Sources</div>',
        unsafe_allow_html=True,
    )
    col_m1, col_m2 = st.columns(2)
    with col_m1:
        st.markdown("""
### Geographic Grid
- **Resolution:** 0.5° × 0.5° (~55 km) — matches NASA POWER native resolution
- **Study area:** 13°–16°E, 7.5°–12.5°N (Nord + Extreme-Nord Cameroon)
- **Cells:** 60 per year (6 lon × 10 lat) · CRS: EPSG:4326

### Rainy-Season Onset (Sivakumar 1988 / AGRHYMET)
- **Trigger:** ≥ 20 mm over 3 consecutive days after April 1 (DOY 91)
- **Validation:** no dry spell ≥ 7 days in the following 30 days
- **Reference:** Sivakumar (1988), *Agric. & Forest Meteorology* 42(4)

### False Start
- Trigger followed by ≥ 10 consecutive dry days within 30 days
- Dry day threshold: < 1 mm/day

### Risk Model
| Indicator | Weight |
|---|---|
| False start | 40% |
| Dry spell | 35% |
| Heat stress (Tmax > 35°C) | 25% |

Score 0–33 = LOW · 34–66 = MEDIUM · 67–100 = HIGH

> ⚠ Weights are provisional — not validated against yield data.
        """)
    with col_m2:
        st.markdown("""
### NASA Data Sources
| Source | Variable | Resolution | Period |
|---|---|---|---|
| NASA POWER v9 | PRECTOTCORR, T2M_MAX, T2M_MIN | 0.5° | 2020–2023 |
| NASA GIBS | MODIS True Color | Variable | Daily (overlay) |

### Partner Data
| Source | Data | Status |
|---|---|---|
| ISRIC SoilGrids v2.0 | pH, SOC, clay, sand, silt | Queried — null values for this region |
| MINADER | Agricultural calendars | Referenced |

### Limitations
- Real data covers 2020–2023 only (4 years)
- 0.5° resolution cannot capture field-level variation
- SoilGrids returned null values for Northern Cameroon
- Risk weights are provisional and not validated against yield data
- Crop rotation benefits are agronomic hypotheses, not measured outcomes
- No seasonal forecast capability — historical analysis only

### Basemap
- **Provider:** OpenStreetMap
- **Attribution:** © OpenStreetMap contributors
- **Licence:** ODbL — https://www.openstreetmap.org/copyright
        """)
