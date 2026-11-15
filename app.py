"""
MaïsMap — Agricultural decision-support application
NASA Space Apps Challenge 2026 | GeoWorks Team
Northern Cameroon maize sowing risk analysis
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import streamlit as st
from streamlit_folium import st_folium

from config.settings import APP_TITLE, APP_SUBTITLE, DEMO_YEARS
from src.data.data_loader import load_dataset, get_available_years
from src.visualization.map import build_map
from src.visualization.charts import (
    chart_onset_by_year, chart_false_start_frequency,
    chart_dry_spell, chart_risk_distribution
)

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title=APP_TITLE,
    page_icon="🌽",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
  .demo-banner {
    background:#fff3cd;border:2px solid #ffc107;border-radius:8px;
    padding:10px 16px;font-weight:bold;color:#856404;margin-bottom:12px;
  }
  .metric-card {
    background:#f8f9fa;border-radius:8px;padding:12px;text-align:center;
  }
  .risk-low    { color:#2ecc71; font-weight:bold; }
  .risk-medium { color:#f39c12; font-weight:bold; }
  .risk-high   { color:#e74c3c; font-weight:bold; }
</style>
""", unsafe_allow_html=True)


# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/commons/e/e5/NASA_logo.svg", width=80)
    st.markdown(f"## 🌽 {APP_TITLE}")
    st.caption(APP_SUBTITLE)
    st.divider()

    use_demo = True  # Switch to False when real data is available
    available_years = get_available_years(use_demo=use_demo)
    if not available_years:
        available_years = DEMO_YEARS

    selected_year = st.selectbox("📅 Année", options=sorted(available_years, reverse=True))

    st.divider()
    st.markdown("**Filtres**")
    risk_filter = st.multiselect(
        "Classe de risque",
        options=["LOW", "MEDIUM", "HIGH"],
        default=["LOW", "MEDIUM", "HIGH"],
    )

    region_options = ["Toutes", "Nord", "Extrême-Nord", "Adamaoua"]
    selected_region = st.selectbox("Région", region_options)

    st.divider()
    show_scenario = st.checkbox("Simulateur de scénario", value=False)
    if show_scenario:
        rain_delta = st.slider("Variation pluie (%)", -30, 30, 0, step=5)
        temp_delta = st.slider("Variation température (°C)", -2, 4, 0, step=1)

    st.divider()
    st.caption("**Sources de données**")
    st.caption("NASA POWER · NASA GPM IMERG · NASA SMAP")
    st.caption("**Équipe :** GeoWorks")
    st.caption("**Challenge :** NASA Space Apps 2026")


# ── Load data ─────────────────────────────────────────────────────────────────
geojson, is_demo = load_dataset(selected_year, use_demo=use_demo)

# ── Demo banner ───────────────────────────────────────────────────────────────
if is_demo:
    st.markdown(
        '<div class="demo-banner">⚠️ DONNÉES DE DÉMONSTRATION — '
        'PAS DE MESURES NASA OFFICIELLES. '
        'Ces données sont synthétiques et servent uniquement à illustrer l\'application.</div>',
        unsafe_allow_html=True,
    )

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown(f"# 🌽 {APP_TITLE}")
st.markdown(f"*{APP_SUBTITLE}*")

# ── Dashboard metrics ─────────────────────────────────────────────────────────
if geojson:
    features = geojson.get("features", [])

    # Apply region filter
    if selected_region != "Toutes":
        features = [f for f in features if f["properties"].get("region") == selected_region]

    n_cells = len(features)
    n_low = sum(1 for f in features if f["properties"].get("risk_class") == "LOW")
    n_med = sum(1 for f in features if f["properties"].get("risk_class") == "MEDIUM")
    n_high = sum(1 for f in features if f["properties"].get("risk_class") == "HIGH")
    n_fs = sum(1 for f in features if f["properties"].get("false_start"))

    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("Cellules analysées", n_cells)
    col2.metric("🟢 Risque faible", n_low)
    col3.metric("🟡 Risque modéré", n_med)
    col4.metric("🔴 Risque élevé", n_high)
    col5.metric("⚠️ Faux départs", n_fs)

    st.divider()

    # ── Tabs ──────────────────────────────────────────────────────────────────
    tab_map, tab_history, tab_scenario, tab_data = st.tabs(
        ["🗺️ Carte interactive", "📈 Analyse historique", "🔬 Scénario", "📋 Données"]
    )

    # ── Map tab ───────────────────────────────────────────────────────────────
    with tab_map:
        st.markdown(f"**Carte des risques agricoles — {selected_year}**")
        if selected_region != "Toutes":
            st.caption(f"Région filtrée : {selected_region}")

        filtered_geojson = {**geojson, "features": features}
        folium_map = build_map(filtered_geojson, selected_risk=risk_filter)
        st_folium(folium_map, width="100%", height=520, returned_objects=[])

        st.caption(
            "Cliquez sur une cellule pour afficher les détails. "
            "Les couleurs indiquent la classe de risque : "
            "🟢 Faible · 🟡 Modéré · 🔴 Élevé"
        )

    # ── Historical tab ────────────────────────────────────────────────────────
    with tab_history:
        st.markdown("**Analyse historique — toutes les années disponibles**")
        st.caption(
            "Cette section présente des statistiques historiques. "
            "Elle ne constitue pas une prévision climatique."
        )

        all_years_data, _ = load_dataset(selected_year, use_demo=use_demo)
        # Build per-year aggregates for the selected region
        all_geojson_raw, _ = _load_all_years(use_demo, selected_region, available_years)

        if all_geojson_raw:
            col_a, col_b = st.columns(2)
            with col_a:
                st.plotly_chart(chart_onset_by_year(all_geojson_raw), use_container_width=True)
                st.plotly_chart(chart_dry_spell(all_geojson_raw), use_container_width=True)
            with col_b:
                st.plotly_chart(chart_false_start_frequency(all_geojson_raw), use_container_width=True)
                st.plotly_chart(chart_risk_distribution(all_geojson_raw), use_container_width=True)

    # ── Scenario tab ──────────────────────────────────────────────────────────
    with tab_scenario:
        st.markdown("**Simulateur de scénario — sensibilité des indicateurs**")
        st.warning(
            "⚠️ Ceci est un scénario de sensibilité, PAS une prévision climatique. "
            "Les résultats illustrent comment les indicateurs réagiraient à des "
            "variations hypothétiques des conditions."
        )
        if show_scenario:
            _render_scenario(features, rain_delta, temp_delta)
        else:
            st.info("Activez le simulateur dans la barre latérale pour explorer des scénarios.")

    # ── Data tab ──────────────────────────────────────────────────────────────
    with tab_data:
        st.markdown("**Données brutes — cellules filtrées**")
        import pandas as pd
        rows = [f["properties"] for f in features]
        if rows:
            df = pd.DataFrame(rows)
            display_cols = [
                "cell_id", "region", "department", "year",
                "season_onset_date", "false_start", "dry_spell_days",
                "heat_days", "risk_score", "risk_class", "data_source"
            ]
            display_cols = [c for c in display_cols if c in df.columns]
            st.dataframe(df[display_cols], use_container_width=True, height=400)
            csv = df[display_cols].to_csv(index=False).encode("utf-8")
            st.download_button("Télécharger CSV", csv, f"maismap_{selected_year}.csv", "text/csv")
else:
    st.error("Aucune donnée disponible. Vérifiez que le fichier demo_grid.geojson existe.")


# ── Helper functions ──────────────────────────────────────────────────────────
@st.cache_data(ttl=300)
def _load_all_years(use_demo: bool, region: str, years: list[int]) -> tuple[list[dict], bool]:
    """Load and aggregate one representative cell per year for trend charts."""
    import json
    from config.settings import DATA_DEMO_PATH
    if not os.path.exists(DATA_DEMO_PATH):
        return [], True
    with open(DATA_DEMO_PATH, encoding="utf-8") as f:
        full = json.load(f)

    result = []
    for year in years:
        feats = [
            f["properties"] for f in full.get("features", [])
            if f["properties"].get("year") == year
            and (region == "Toutes" or f["properties"].get("region") == region)
        ]
        if not feats:
            continue
        # Aggregate: mean onset, false-start frequency, mean dry spell, mean heat
        onsets = [p["season_onset_date"] for p in feats if p.get("season_onset_date")]
        dry = [p["dry_spell_days"] for p in feats if p.get("dry_spell_days") is not None]
        heat = [p["heat_days"] for p in feats if p.get("heat_days") is not None]
        scores = [p["risk_score"] for p in feats if p.get("risk_score") is not None]
        fs_count = sum(1 for p in feats if p.get("false_start"))
        classes = [p.get("risk_class") for p in feats if p.get("risk_class")]
        dominant = max(set(classes), key=classes.count) if classes else "MEDIUM"

        result.append({
            "year": year,
            "season_onset_date": round(sum(onsets) / len(onsets)) if onsets else None,
            "false_start": fs_count > len(feats) * 0.5,
            "dry_spell_days": round(sum(dry) / len(dry), 1) if dry else None,
            "heat_days": round(sum(heat) / len(heat), 1) if heat else None,
            "risk_score": round(sum(scores) / len(scores), 1) if scores else None,
            "risk_class": dominant,
        })
    return result, True


def _render_scenario(features: list[dict], rain_delta: int, temp_delta: float):
    """Apply hypothetical scenario adjustments and show modified risk counts."""
    import copy
    from src.analysis.risk_model import compute_risk

    modified = []
    for f in features:
        p = copy.deepcopy(f["properties"])
        # Adjust dry spell: less rain → more dry days
        if p.get("dry_spell_days") is not None:
            factor = 1 - rain_delta / 100.0
            p["dry_spell_days"] = max(0, round(p["dry_spell_days"] * factor))
        # Adjust heat days: higher temp → more heat days
        if p.get("heat_days") is not None:
            p["heat_days"] = max(0, p["heat_days"] + round(temp_delta * 2))

        risk = compute_risk(
            p.get("false_start", False),
            p.get("dry_spell_days", 0),
            p.get("heat_days", 0)
        )
        p["risk_class"] = risk["class"]
        p["risk_score"] = risk["score"]
        modified.append(p)

    n_low = sum(1 for p in modified if p["risk_class"] == "LOW")
    n_med = sum(1 for p in modified if p["risk_class"] == "MEDIUM")
    n_high = sum(1 for p in modified if p["risk_class"] == "HIGH")

    st.markdown(f"**Scénario : pluie {rain_delta:+d}% · température {temp_delta:+.1f}°C**")
    c1, c2, c3 = st.columns(3)
    c1.metric("🟢 Risque faible", n_low)
    c2.metric("🟡 Risque modéré", n_med)
    c3.metric("🔴 Risque élevé", n_high)

    # Show modified map
    import json
    mod_geojson = {
        "type": "FeatureCollection",
        "features": [
            {"type": "Feature", "geometry": f["geometry"], "properties": p}
            for f, p in zip(features, modified)
        ]
    }
    # Rebuild features list from original geojson features
    orig_features = features  # already filtered
    mod_geojson2 = {
        "type": "FeatureCollection",
        "features": [
            {"type": "Feature",
             "geometry": orig_features[i]["geometry"] if isinstance(orig_features[i], dict) else orig_features[i],
             "properties": modified[i]}
            for i in range(len(modified))
        ]
    }
    scenario_map = build_map(mod_geojson2)
    st_folium(scenario_map, width="100%", height=450, returned_objects=[], key="scenario_map")
