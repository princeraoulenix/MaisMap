"""
MaïsMap — Agricultural decision-support application
NASA Space Apps Challenge 2026 | GeoWorks Team
Northern Cameroon maize sowing risk analysis
"""
import sys, os, json, copy
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import streamlit as st
from streamlit_folium import st_folium
import pandas as pd

from config.settings import APP_TITLE, APP_SUBTITLE, DEMO_YEARS, DATA_DEMO_PATH
from src.data.data_loader import load_dataset, get_available_years
from src.data.validator import validate_geojson
from src.visualization.map import build_map
from src.visualization.charts import (
    chart_onset_by_year, chart_false_start_frequency,
    chart_dry_spell, chart_heat_days, chart_risk_distribution,
)
from src.analysis.risk_model import compute_risk

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title=APP_TITLE,
    page_icon="🌽",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
  .demo-banner{background:#fff3cd;border:2px solid #ffc107;border-radius:8px;
    padding:10px 16px;font-weight:bold;color:#856404;margin-bottom:8px;}
  .real-banner{background:#d4edda;border:2px solid #28a745;border-radius:8px;
    padding:10px 16px;font-weight:bold;color:#155724;margin-bottom:8px;}
  .warn-box{background:#f8d7da;border:1px solid #f5c6cb;border-radius:6px;
    padding:8px 12px;color:#721c24;font-size:13px;margin:6px 0;}
  .info-box{background:#d1ecf1;border:1px solid #bee5eb;border-radius:6px;
    padding:8px 12px;color:#0c5460;font-size:13px;margin:6px 0;}
  .section-title{font-size:16px;font-weight:600;margin:8px 0 4px 0;}
</style>
""", unsafe_allow_html=True)


# ── Cached helpers (defined BEFORE use) ──────────────────────────────────────
@st.cache_data(ttl=600, show_spinner=False)
def _load_all_years_cached(use_demo: bool, region: str, years: tuple) -> list[dict]:
    """Aggregate per-year statistics across all available years for trend charts."""
    if not os.path.exists(DATA_DEMO_PATH):
        return []
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
        onsets = [p["season_onset_date"] for p in feats if p.get("season_onset_date")]
        dry    = [p["dry_spell_days"] for p in feats if p.get("dry_spell_days") is not None]
        heat   = [p["heat_days"] for p in feats if p.get("heat_days") is not None]
        scores = [p["risk_score"] for p in feats if p.get("risk_score") is not None]
        fs_count = sum(1 for p in feats if p.get("false_start"))
        classes  = [p.get("risk_class") for p in feats if p.get("risk_class")]
        dominant = max(set(classes), key=classes.count) if classes else "MEDIUM"

        result.append({
            "year": year,
            "season_onset_date": round(sum(onsets) / len(onsets)) if onsets else None,
            "false_start": fs_count > len(feats) * 0.5,
            "dry_spell_days": round(sum(dry) / len(dry), 1) if dry else None,
            "heat_days": round(sum(heat) / len(heat), 1) if heat else None,
            "risk_score": round(sum(scores) / len(scores), 1) if scores else None,
            "risk_class": dominant,
            "false_start_pct": round(fs_count / len(feats) * 100),
        })
    return result


def _render_scenario(features: list[dict], rain_delta: int, temp_delta: float):
    """Apply sensitivity adjustments and display modified risk distribution + map."""
    modified_props = []
    for f in features:
        p = copy.deepcopy(f["properties"])
        if p.get("dry_spell_days") is not None:
            factor = 1.0 - rain_delta / 100.0
            p["dry_spell_days"] = max(0, round(p["dry_spell_days"] * factor))
        if p.get("heat_days") is not None:
            p["heat_days"] = max(0, p["heat_days"] + round(temp_delta * 2))
        risk = compute_risk(
            p.get("false_start", False),
            p.get("dry_spell_days", 0),
            p.get("heat_days", 0),
        )
        p["risk_class"] = risk["class"]
        p["risk_score"] = risk["score"]
        modified_props.append(p)

    n_low  = sum(1 for p in modified_props if p["risk_class"] == "LOW")
    n_med  = sum(1 for p in modified_props if p["risk_class"] == "MEDIUM")
    n_high = sum(1 for p in modified_props if p["risk_class"] == "HIGH")

    st.markdown(f"**Résultat du scénario : pluie {rain_delta:+d}% · température {temp_delta:+.1f}°C**")
    c1, c2, c3 = st.columns(3)
    c1.metric("🟢 Risque faible", n_low)
    c2.metric("🟡 Risque modéré", n_med)
    c3.metric("🔴 Risque élevé", n_high)

    mod_geojson = {
        "type": "FeatureCollection",
        "features": [
            {"type": "Feature", "geometry": features[i]["geometry"], "properties": modified_props[i]}
            for i in range(len(features))
        ],
    }
    scenario_map = build_map(mod_geojson)
    st_folium(scenario_map, width="100%", height=420, returned_objects=[], key="scenario_map")


# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/commons/e/e5/NASA_logo.svg", width=72)
    st.markdown(f"## 🌽 {APP_TITLE}")
    st.caption(APP_SUBTITLE)
    st.divider()

    use_demo = True  # Set False when real processed data is placed in data/processed/
    available_years = get_available_years(use_demo=use_demo) or DEMO_YEARS
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
    show_satellite = st.checkbox("Superposition satellite NASA GIBS", value=False)
    st.divider()
    st.markdown("**Simulateur de scénario**")
    show_scenario = st.checkbox("Activer le simulateur", value=False)
    rain_delta = st.slider("Variation pluie (%)", -30, 30, 0, step=5,
                           disabled=not show_scenario)
    temp_delta = st.slider("Variation température (°C)", -2, 4, 0, step=1,
                           disabled=not show_scenario)

    st.divider()
    st.caption("**Sources NASA**")
    st.caption("POWER · GPM IMERG · SMAP")
    st.caption("**Équipe :** GeoWorks")
    st.caption("**Challenge :** Space Apps 2026")


# ── Load & validate data ──────────────────────────────────────────────────────
geojson, is_demo = load_dataset(selected_year, use_demo=use_demo)

# ── Data-source banner ────────────────────────────────────────────────────────
if is_demo:
    st.markdown(
        '<div class="demo-banner">⚠️ DONNÉES DE DÉMONSTRATION — '
        'PAS DE MESURES NASA OFFICIELLES. '
        'Données synthétiques à titre illustratif uniquement.</div>',
        unsafe_allow_html=True,
    )
else:
    st.markdown(
        '<div class="real-banner">✅ Données NASA POWER — Mesures historiques réelles.</div>',
        unsafe_allow_html=True,
    )

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown(f"# 🌽 {APP_TITLE}")
st.markdown(
    f"*{APP_SUBTITLE}* &nbsp;|&nbsp; "
    f"Année sélectionnée : **{selected_year}** &nbsp;|&nbsp; "
    f"{'Données démo' if is_demo else 'Données NASA POWER'}"
)

# ── Main content ──────────────────────────────────────────────────────────────
if not geojson:
    st.error(
        "Aucune donnée disponible pour cette année. "
        "Vérifiez que `data/demo/demo_grid.geojson` existe "
        "ou lancez `python src/data/generate_demo.py`."
    )
    st.stop()

# Apply region filter
all_features = geojson.get("features", [])
if selected_region != "Toutes":
    all_features = [
        f for f in all_features
        if f["properties"].get("region") == selected_region
    ]

# Validate
validation = validate_geojson({"type": "FeatureCollection", "features": all_features})

# ── Dashboard metrics ─────────────────────────────────────────────────────────
n_cells = len(all_features)
n_valid = validation["valid"]
n_low   = sum(1 for f in all_features if f["properties"].get("risk_class") == "LOW")
n_med   = sum(1 for f in all_features if f["properties"].get("risk_class") == "MEDIUM")
n_high  = sum(1 for f in all_features if f["properties"].get("risk_class") == "HIGH")
n_fs    = sum(1 for f in all_features if f["properties"].get("false_start"))

col1, col2, col3, col4, col5, col6 = st.columns(6)
col1.metric("Cellules", n_cells)
col2.metric("Valides", n_valid)
col3.metric("🟢 Faible", n_low)
col4.metric("🟡 Modéré", n_med)
col5.metric("🔴 Élevé", n_high)
col6.metric("⚠️ Faux départs", n_fs)

if validation["invalid"] > 0:
    st.markdown(
        f'<div class="warn-box">⚠️ {validation["invalid"]} cellule(s) avec données invalides '
        f'— voir onglet Données pour le détail.</div>',
        unsafe_allow_html=True,
    )

st.divider()

# ── Tabs ──────────────────────────────────────────────────────────────────────
tab_map, tab_history, tab_scenario, tab_data, tab_method = st.tabs([
    "🗺️ Carte interactive",
    "📈 Analyse historique",
    "🔬 Scénario",
    "📋 Données",
    "📖 Méthodologie",
])

# ── MAP TAB ───────────────────────────────────────────────────────────────────
with tab_map:
    st.markdown(f'<div class="section-title">Carte des risques agricoles — {selected_year}</div>',
                unsafe_allow_html=True)
    if selected_region != "Toutes":
        st.caption(f"Région : {selected_region}")

    filtered_geojson = {**geojson, "features": all_features}
    folium_map = build_map(filtered_geojson, selected_risk=risk_filter,
                           show_satellite=show_satellite)
    st_folium(folium_map, width="100%", height=540, returned_objects=[])

    st.caption(
        "Cliquez sur une cellule pour afficher les indicateurs détaillés. "
        "🟢 Risque faible · 🟡 Risque modéré · 🔴 Risque élevé. "
        "Résolution spatiale : 0,5° (~55 km). "
        "Cette carte ne représente pas des conditions à l'échelle parcellaire."
    )

# ── HISTORY TAB ───────────────────────────────────────────────────────────────
with tab_history:
    st.markdown('<div class="section-title">Analyse historique — toutes les années disponibles</div>',
                unsafe_allow_html=True)
    st.markdown(
        '<div class="info-box">📊 Statistiques historiques basées sur les données disponibles. '
        'Ces graphiques décrivent le passé observé — ils ne constituent pas une prévision.</div>',
        unsafe_allow_html=True,
    )

    trend_data = _load_all_years_cached(use_demo, selected_region, tuple(available_years))

    if trend_data:
        col_a, col_b = st.columns(2)
        with col_a:
            st.plotly_chart(chart_onset_by_year(trend_data), use_container_width=True)
            st.plotly_chart(chart_dry_spell(trend_data), use_container_width=True)
        with col_b:
            st.plotly_chart(chart_false_start_frequency(trend_data), use_container_width=True)
            st.plotly_chart(chart_heat_days(trend_data), use_container_width=True)
        st.plotly_chart(chart_risk_distribution(trend_data), use_container_width=True)

        # Summary statistics
        st.divider()
        st.markdown("**Résumé statistique**")
        valid_onsets = [d["season_onset_date"] for d in trend_data if d.get("season_onset_date")]
        fs_years = sum(1 for d in trend_data if d.get("false_start"))
        sc1, sc2, sc3, sc4 = st.columns(4)
        sc1.metric("Années analysées", len(trend_data))
        sc2.metric("Début de saison moyen (DOJ)",
                   round(sum(valid_onsets) / len(valid_onsets)) if valid_onsets else "N/A")
        sc3.metric("Années avec faux départ", fs_years)
        sc4.metric("Fréquence faux départs",
                   f"{round(fs_years / len(trend_data) * 100)}%" if trend_data else "N/A")
    else:
        st.info("Aucune donnée historique disponible pour cette région.")

# ── SCENARIO TAB ──────────────────────────────────────────────────────────────
with tab_scenario:
    st.markdown('<div class="section-title">Simulateur de scénario — sensibilité des indicateurs</div>',
                unsafe_allow_html=True)
    st.markdown(
        '<div class="warn-box">⚠️ Scénario de sensibilité uniquement — PAS une prévision climatique. '
        'Les résultats montrent comment les indicateurs de risque réagiraient à des variations '
        'hypothétiques de pluie et de température.</div>',
        unsafe_allow_html=True,
    )
    if show_scenario:
        _render_scenario(all_features, rain_delta, temp_delta)
    else:
        st.info("Activez le simulateur dans la barre latérale (case à cocher) pour explorer des scénarios.")

# ── DATA TAB ──────────────────────────────────────────────────────────────────
with tab_data:
    st.markdown('<div class="section-title">Données — cellules filtrées</div>',
                unsafe_allow_html=True)

    # Validation report
    with st.expander("Rapport de validation des données", expanded=False):
        st.json(validation)

    rows = [f["properties"] for f in all_features]
    if rows:
        df = pd.DataFrame(rows)
        display_cols = [
            "cell_id", "region", "department", "year",
            "season_onset_date_str", "false_start", "dry_spell_days",
            "heat_days", "risk_score", "risk_class", "confidence",
            "data_source", "spatial_resolution",
        ]
        display_cols = [c for c in display_cols if c in df.columns]
        st.dataframe(df[display_cols], use_container_width=True, height=420)

        csv = df[display_cols].to_csv(index=False).encode("utf-8")
        st.download_button(
            "⬇️ Télécharger CSV",
            csv,
            f"maismap_{selected_year}_{selected_region}.csv",
            "text/csv",
        )
    else:
        st.info("Aucune cellule à afficher avec les filtres actuels.")

# ── METHODOLOGY TAB ───────────────────────────────────────────────────────────
with tab_method:
    st.markdown('<div class="section-title">Méthodologie scientifique</div>',
                unsafe_allow_html=True)
    st.markdown("""
**MaïsMap** utilise des données climatiques historiques NASA pour calculer des indicateurs
agronomiques pertinents pour la culture du maïs au Nord Cameroun.

---

### Grille géographique
- Résolution : 0,5° (~55 km) — cohérente avec la résolution de NASA POWER
- Zone d'étude : Nord et Extrême-Nord Cameroun (13°–16°E, 7,5°–12,5°N)
- ⚠️ Cette résolution ne capture pas les variations microclimatiques locales

### Début de saison (méthode Sivakumar 1988 / AGRHYMET)
- **Déclencheur** : cumul ≥ 20 mm sur 3 jours consécutifs après le 1er avril
- **Validation** : absence de sécheresse ≥ 7 jours dans les 30 jours suivants
- Source : Sivakumar (1988), AGRHYMET Regional Centre methodology

### Faux départ
- Déclencheur suivi d'une sécheresse ≥ 10 jours consécutifs dans les 30 jours
- Seuil de jour sec : < 1 mm/jour

### Sécheresses
- Durée maximale de jours secs consécutifs dans la saison (début + 120 jours)
- Seuil critique : 10 jours · Seuil sévère : 15 jours

### Stress thermique
- Seuil : Tmax > 35°C (viabilité du pollen du maïs, CIMMYT)
- Comptage sur la fenêtre saisonnière

### Modèle de risque
| Indicateur | Poids |
|---|---|
| Faux départ | 40% |
| Sécheresse | 35% |
| Stress thermique | 25% |

- Score 0–33 → **Faible** · 34–66 → **Modéré** · 67–100 → **Élevé**
- Les poids sont provisoires et documentés dans `config/thresholds.py`

### Sources de données NASA
| Source | Variable | Résolution | Période |
|---|---|---|---|
| NASA POWER | Précipitations, Tmax | 0,5° | 1984–présent |
| NASA GPM IMERG | Précipitations | 0,1° | 2000–présent |
| NASA SMAP | Humidité sol surface | 36 km | 2015–présent |

### Limites
- Les données de démonstration sont **synthétiques** — elles n'ont aucune valeur opérationnelle
- La résolution 0,5° ne permet pas d'analyse parcellaire
- Les recommandations de semis doivent être confirmées par les services d'encadrement locaux
- Ce prototype ne remplace pas les conseils agronomiques professionnels
""")
