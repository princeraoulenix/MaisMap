"""
Folium interactive map builder for MaïsMap.
"""
import folium
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from config.settings import MAP_CENTER, MAP_ZOOM

RISK_COLORS = {"LOW": "#2ecc71", "MEDIUM": "#f39c12", "HIGH": "#e74c3c"}
RISK_FILL_OPACITY = 0.65


def build_map(geojson: dict, selected_risk: list[str] | None = None) -> folium.Map:
    """
    Build and return a Folium map with color-coded risk grid cells.

    Parameters
    ----------
    geojson : dict
        GeoJSON FeatureCollection filtered to a single year.
    selected_risk : list of str, optional
        If provided, only show cells with risk_class in this list.
    """
    m = folium.Map(location=MAP_CENTER, zoom_start=MAP_ZOOM, tiles="CartoDB positron")

    features = geojson.get("features", [])
    if selected_risk:
        features = [
            f for f in features
            if f["properties"].get("risk_class") in selected_risk
        ]

    for feature in features:
        props = feature["properties"]
        risk_class = props.get("risk_class", "MEDIUM")
        color = RISK_COLORS.get(risk_class, "#95a5a6")

        popup_html = _build_popup(props)
        tooltip = (
            f"{props.get('region', '?')} — {props.get('department', '?')}<br>"
            f"Risque : <b>{risk_class}</b> ({props.get('risk_score', '?')})"
        )

        folium.GeoJson(
            {"type": "Feature", "geometry": feature["geometry"], "properties": props},
            style_function=lambda _, c=color: {
                "fillColor": c,
                "color": "#555",
                "weight": 0.8,
                "fillOpacity": RISK_FILL_OPACITY,
            },
            tooltip=folium.Tooltip(tooltip),
            popup=folium.Popup(popup_html, max_width=320),
        ).add_to(m)

    _add_legend(m)
    return m


def _build_popup(props: dict) -> str:
    onset = props.get("season_onset_date_str") or props.get("season_onset_date", "N/A")
    fs = "Oui" if props.get("false_start") else "Non"
    return f"""
    <div style="font-family:sans-serif;font-size:13px;line-height:1.6">
      <b style="font-size:14px">{props.get('region','?')} — {props.get('department','?')}</b><br>
      <hr style="margin:4px 0">
      <b>Cellule :</b> {props.get('cell_id','?')}<br>
      <b>Année :</b> {props.get('year','?')}<br>
      <b>Début de saison :</b> {onset}<br>
      <b>Faux départ :</b> {fs}<br>
      <b>Sécheresse max :</b> {props.get('dry_spell_days','?')} jours<br>
      <b>Jours de chaleur :</b> {props.get('heat_days','?')}<br>
      <b>Score de risque :</b> {props.get('risk_score','?')}/100<br>
      <b>Classe de risque :</b> <span style="color:{_risk_color(props.get('risk_class',''))}">
        <b>{props.get('risk_class','?')}</b></span><br>
      <hr style="margin:4px 0">
      <i style="font-size:12px">{props.get('sowing_advice','')}</i><br>
      <hr style="margin:4px 0">
      <small>Source : {props.get('data_source','?')}<br>
      Résolution : {props.get('spatial_resolution','?')}</small>
    </div>
    """


def _risk_color(risk_class: str) -> str:
    return RISK_COLORS.get(risk_class, "#555")


def _add_legend(m: folium.Map):
    legend_html = """
    <div style="position:fixed;bottom:30px;left:30px;z-index:1000;background:white;
                padding:12px 16px;border-radius:8px;box-shadow:0 2px 8px rgba(0,0,0,0.3);
                font-family:sans-serif;font-size:13px">
      <b>Risque agricole</b><br>
      <span style="color:#2ecc71">&#9632;</span> Faible (LOW)<br>
      <span style="color:#f39c12">&#9632;</span> Modéré (MEDIUM)<br>
      <span style="color:#e74c3c">&#9632;</span> Élevé (HIGH)
    </div>
    """
    m.get_root().html.add_child(folium.Element(legend_html))
