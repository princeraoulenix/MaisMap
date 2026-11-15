"""
Folium interactive map builder for MaïsMap.
Supports optional NASA GIBS satellite imagery overlays.
"""
import folium
from folium.plugins import MiniMap
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from config.settings import MAP_CENTER, MAP_ZOOM

RISK_COLORS = {"LOW": "#2ecc71", "MEDIUM": "#f39c12", "HIGH": "#e74c3c"}
RISK_LABELS = {"LOW": "Faible", "MEDIUM": "Modéré", "HIGH": "Élevé"}
RISK_FILL_OPACITY = 0.65

# NASA GIBS WMS — verified tile URL (MODIS Terra True Color, daily)
GIBS_MODIS_URL = (
    "https://gibs.earthdata.nasa.gov/wmts/epsg3857/best/"
    "MODIS_Terra_CorrectedReflectance_TrueColor/default/2023-01-01/"
    "GoogleMapsCompatible_Level9/{z}/{y}/{x}.jpg"
)


def build_map(
    geojson: dict,
    selected_risk: list[str] | None = None,
    show_satellite: bool = False,
) -> folium.Map:
    """
    Build and return a Folium map with color-coded risk grid cells.

    Parameters
    ----------
    geojson : GeoJSON FeatureCollection filtered to a single year.
    selected_risk : if provided, only show cells with risk_class in this list.
    show_satellite : if True, add NASA GIBS MODIS overlay.
    """
    m = folium.Map(
        location=MAP_CENTER,
        zoom_start=MAP_ZOOM,
        tiles="CartoDB positron",
        prefer_canvas=True,
    )

    # Optional NASA GIBS satellite overlay
    if show_satellite:
        folium.TileLayer(
            tiles=GIBS_MODIS_URL,
            attr="NASA GIBS / MODIS Terra",
            name="NASA MODIS (GIBS)",
            overlay=True,
            opacity=0.6,
        ).add_to(m)

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

        folium.GeoJson(
            {"type": "Feature", "geometry": feature["geometry"], "properties": props},
            style_function=lambda _, c=color: {
                "fillColor": c,
                "color": "#444",
                "weight": 0.9,
                "fillOpacity": RISK_FILL_OPACITY,
            },
            tooltip=folium.Tooltip(_build_tooltip(props)),
            popup=folium.Popup(_build_popup(props), max_width=340),
        ).add_to(m)

    _add_legend(m)
    MiniMap(toggle_display=True, position="bottomright").add_to(m)

    if show_satellite:
        folium.LayerControl().add_to(m)

    return m


def _build_tooltip(props: dict) -> str:
    rc = props.get("risk_class", "?")
    label = RISK_LABELS.get(rc, rc)
    return (
        f"<b>{props.get('region','?')}</b> — {props.get('department','?')}<br>"
        f"Risque : <b style='color:{RISK_COLORS.get(rc,'#555')}'>{label}</b> "
        f"({props.get('risk_score','?')}/100)"
    )


def _build_popup(props: dict) -> str:
    onset = props.get("season_onset_date_str") or props.get("season_onset_date", "N/A")
    fs_label = "⚠️ Oui" if props.get("false_start") else "✅ Non"
    rc = props.get("risk_class", "?")
    rc_color = RISK_COLORS.get(rc, "#555")
    rc_label = RISK_LABELS.get(rc, rc)
    src = props.get("data_source", "?")
    is_demo = "SYNTHETIC" in str(src).upper() or "DEMO" in str(src).upper()
    src_badge = (
        '<span style="background:#fff3cd;padding:1px 5px;border-radius:3px;font-size:11px">'
        '⚠️ DÉMO</span>'
        if is_demo else
        '<span style="background:#d4edda;padding:1px 5px;border-radius:3px;font-size:11px">'
        '✅ NASA</span>'
    )

    return f"""
    <div style="font-family:sans-serif;font-size:13px;line-height:1.7;min-width:260px">
      <b style="font-size:14px">{props.get('region','?')} — {props.get('department','?')}</b>
      &nbsp;{src_badge}<br>
      <hr style="margin:4px 0;border-color:#ddd">
      <table style="width:100%;border-collapse:collapse">
        <tr><td><b>Cellule</b></td><td>{props.get('cell_id','?')}</td></tr>
        <tr><td><b>Année</b></td><td>{props.get('year','?')}</td></tr>
        <tr><td><b>Début de saison</b></td><td>{onset}</td></tr>
        <tr><td><b>Faux départ</b></td><td>{fs_label}</td></tr>
        <tr><td><b>Sécheresse max</b></td><td>{props.get('dry_spell_days','?')} jours</td></tr>
        <tr><td><b>Jours de chaleur</b></td><td>{props.get('heat_days','?')} (Tmax&gt;35°C)</td></tr>
        <tr><td><b>Score de risque</b></td><td>{props.get('risk_score','?')}/100</td></tr>
        <tr><td><b>Classe de risque</b></td>
            <td><b style="color:{rc_color}">{rc_label} ({rc})</b></td></tr>
      </table>
      <hr style="margin:4px 0;border-color:#ddd">
      <div style="background:#f8f9fa;padding:6px 8px;border-radius:4px;font-size:12px;
                  border-left:3px solid {rc_color}">
        <b>Conseil :</b> {props.get('sowing_advice','N/A')}
      </div>
      <hr style="margin:4px 0;border-color:#ddd">
      <small style="color:#888">
        Source : {src}<br>
        Résolution : {props.get('spatial_resolution','?')}
      </small>
    </div>
    """


def _add_legend(m: folium.Map):
    legend_html = """
    <div style="position:fixed;bottom:50px;left:12px;z-index:1000;background:white;
                padding:10px 14px;border-radius:8px;
                box-shadow:0 2px 8px rgba(0,0,0,0.25);
                font-family:sans-serif;font-size:12px;line-height:1.8">
      <b style="font-size:13px">Risque agricole</b><br>
      <span style="color:#2ecc71;font-size:16px">&#9632;</span> Faible (LOW)<br>
      <span style="color:#f39c12;font-size:16px">&#9632;</span> Modéré (MEDIUM)<br>
      <span style="color:#e74c3c;font-size:16px">&#9632;</span> Élevé (HIGH)<br>
      <hr style="margin:4px 0;border-color:#eee">
      <small style="color:#888">Résolution : 0,5° (~55 km)</small>
    </div>
    """
    m.get_root().html.add_child(folium.Element(legend_html))
