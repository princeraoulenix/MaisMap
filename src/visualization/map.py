"""
Folium interactive map builder for MaïsMap.
Uses OpenStreetMap tiles (no API key required, attribution included automatically).
Optional NASA GIBS MODIS overlay.
"""
import folium
from folium.plugins import MiniMap
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from config.settings import STUDY_BBOX

# Risk colour palette — earth tones, clear semantics
RISK_COLORS  = {"LOW": "#27ae60", "MEDIUM": "#e67e22", "HIGH": "#c0392b"}
RISK_LABELS  = {"LOW": "Low / Faible", "MEDIUM": "Moderate / Modéré", "HIGH": "High / Élevé"}
RISK_FILL_OPACITY = 0.60

# Study-area centre and tight zoom
_LAT_C = (STUDY_BBOX["lat_min"] + STUDY_BBOX["lat_max"]) / 2   # 10.0
_LON_C = (STUDY_BBOX["lon_min"] + STUDY_BBOX["lon_max"]) / 2   # 14.5
_ZOOM  = 7   # shows the full 5°×5° study area comfortably

# NASA GIBS WMTS — MODIS Terra True Color
_GIBS_URL = (
    "https://gibs.earthdata.nasa.gov/wmts/epsg3857/best/"
    "MODIS_Terra_CorrectedReflectance_TrueColor/default/2023-01-01/"
    "GoogleMapsCompatible_Level9/{z}/{y}/{x}.jpg"
)


def build_map(
    geojson: dict,
    selected_risk: list | None = None,
    show_satellite: bool = False,
) -> folium.Map:
    """
    Build and return a Folium map with colour-coded risk grid cells.

    Basemap: OpenStreetMap (no API key, attribution automatic).
    Bounds: fitted to the study area so all 60 cells are visible on load.
    """
    m = folium.Map(
        location=[_LAT_C, _LON_C],
        zoom_start=_ZOOM,
        tiles="OpenStreetMap",   # free, no API key, OSM attribution included
        prefer_canvas=True,
        max_zoom=14,
        min_zoom=5,
    )

    # Fit map to study-area bounds on load
    m.fit_bounds([
        [STUDY_BBOX["lat_min"], STUDY_BBOX["lon_min"]],
        [STUDY_BBOX["lat_max"], STUDY_BBOX["lon_max"]],
    ])

    # Optional NASA GIBS satellite overlay
    if show_satellite:
        folium.TileLayer(
            tiles=_GIBS_URL,
            attr="Imagery © NASA GIBS / MODIS Terra",
            name="NASA MODIS True Color (GIBS)",
            overlay=True,
            opacity=0.55,
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
        color = RISK_COLORS.get(risk_class, "#7f8c8d")

        folium.GeoJson(
            {"type": "Feature", "geometry": feature["geometry"], "properties": props},
            style_function=lambda _, c=color: {
                "fillColor": c,
                "color": "#2c3e50",
                "weight": 0.8,
                "fillOpacity": RISK_FILL_OPACITY,
            },
            tooltip=folium.Tooltip(_build_tooltip(props), sticky=True),
            popup=folium.Popup(_build_popup(props), max_width=360),
        ).add_to(m)

    _add_legend(m)
    MiniMap(toggle_display=True, position="bottomright", zoom_level_offset=-6).add_to(m)

    if show_satellite:
        folium.LayerControl(collapsed=False).add_to(m)

    return m


def _build_tooltip(props: dict) -> str:
    rc = props.get("risk_class", "?")
    color = RISK_COLORS.get(rc, "#555")
    label = RISK_LABELS.get(rc, rc)
    score = props.get("risk_score", "?")
    region = props.get("region", "?")
    dept = props.get("department", "?")
    return (
        f"<div style='font-family:sans-serif;font-size:12px;padding:2px'>"
        f"<b>{region}</b> — {dept}<br>"
        f"Risk: <b style='color:{color}'>{label}</b> ({score}/100)"
        f"</div>"
    )


def _build_popup(props: dict) -> str:
    onset = props.get("season_onset_date_str") or (
        f"DOY {props['season_onset_date']}" if props.get("season_onset_date") else "Not detected"
    )
    fs_label = "Yes ⚠" if props.get("false_start") else "No ✓"
    rc = props.get("risk_class", "?")
    rc_color = RISK_COLORS.get(rc, "#555")
    rc_label = RISK_LABELS.get(rc, rc)
    src = props.get("data_source", "?")
    is_demo = "SYNTHETIC" in str(src).upper() or "DEMO" in str(src).upper()
    badge_bg = "#fff3cd" if is_demo else "#d4edda"
    badge_txt = "DEMO DATA" if is_demo else "NASA POWER"

    rain = props.get("seasonal_rain_mm")
    rain_str = f"{rain:.0f} mm" if rain is not None else "N/A"
    tmax = props.get("mean_tmax_c")
    tmax_str = f"{tmax:.1f} °C" if tmax is not None else "N/A"

    return f"""
    <div style="font-family:'Segoe UI',sans-serif;font-size:12px;line-height:1.6;
                min-width:280px;max-width:340px">
      <div style="background:#2c3e50;color:white;padding:8px 10px;margin:-1px -1px 8px -1px;
                  border-radius:3px 3px 0 0">
        <b style="font-size:13px">{props.get('region','?')} — {props.get('department','?')}</b>
        <span style="float:right;background:{badge_bg};color:#333;padding:1px 6px;
                     border-radius:3px;font-size:10px;font-weight:bold">{badge_txt}</span>
      </div>
      <table style="width:100%;border-collapse:collapse;font-size:12px">
        <tr style="background:#f8f9fa">
          <td style="padding:3px 6px;color:#666">Cell ID</td>
          <td style="padding:3px 6px"><b>{props.get('cell_id','?')}</b></td>
          <td style="padding:3px 6px;color:#666">Year</td>
          <td style="padding:3px 6px"><b>{props.get('year','?')}</b></td>
        </tr>
        <tr>
          <td style="padding:3px 6px;color:#666">Season onset</td>
          <td style="padding:3px 6px">{onset}</td>
          <td style="padding:3px 6px;color:#666">False start</td>
          <td style="padding:3px 6px">{fs_label}</td>
        </tr>
        <tr style="background:#f8f9fa">
          <td style="padding:3px 6px;color:#666">Max dry spell</td>
          <td style="padding:3px 6px">{props.get('dry_spell_days','?')} days</td>
          <td style="padding:3px 6px;color:#666">Heat days</td>
          <td style="padding:3px 6px">{props.get('heat_days','?')} (>35°C)</td>
        </tr>
        <tr>
          <td style="padding:3px 6px;color:#666">Seasonal rain</td>
          <td style="padding:3px 6px">{rain_str}</td>
          <td style="padding:3px 6px;color:#666">Mean Tmax</td>
          <td style="padding:3px 6px">{tmax_str}</td>
        </tr>
        <tr style="background:#f8f9fa">
          <td style="padding:3px 6px;color:#666">Risk score</td>
          <td style="padding:3px 6px"><b>{props.get('risk_score','?')}/100</b></td>
          <td style="padding:3px 6px;color:#666">Risk class</td>
          <td style="padding:3px 6px">
            <b style="color:{rc_color}">{rc_label}</b>
          </td>
        </tr>
      </table>
      <div style="background:#f0f4f0;border-left:3px solid {rc_color};
                  padding:6px 8px;margin-top:6px;font-size:11px;border-radius:0 3px 3px 0">
        <b>Sowing advice:</b> {props.get('sowing_advice','N/A')}
      </div>
      <div style="color:#999;font-size:10px;margin-top:5px;padding:0 2px">
        Source: {src} · Resolution: {props.get('spatial_resolution','0.5°')}
      </div>
    </div>
    """


def _add_legend(m: folium.Map):
    legend_html = """
    <div style="position:fixed;bottom:30px;left:10px;z-index:1000;
                background:white;padding:10px 14px;
                border:1px solid #ccc;border-radius:4px;
                box-shadow:0 1px 5px rgba(0,0,0,0.2);
                font-family:'Segoe UI',sans-serif;font-size:12px;line-height:2.0">
      <div style="font-weight:600;font-size:12px;color:#2c3e50;
                  border-bottom:1px solid #eee;margin-bottom:4px;padding-bottom:3px">
        Agricultural Risk
      </div>
      <div><span style="display:inline-block;width:14px;height:14px;
           background:#27ae60;border-radius:2px;vertical-align:middle;
           margin-right:6px"></span>Low risk</div>
      <div><span style="display:inline-block;width:14px;height:14px;
           background:#e67e22;border-radius:2px;vertical-align:middle;
           margin-right:6px"></span>Moderate risk</div>
      <div><span style="display:inline-block;width:14px;height:14px;
           background:#c0392b;border-radius:2px;vertical-align:middle;
           margin-right:6px"></span>High risk</div>
      <div style="color:#999;font-size:10px;margin-top:4px;
                  border-top:1px solid #eee;padding-top:3px">
        Grid: 0.5° × 0.5° (~55 km)
      </div>
    </div>
    """
    m.get_root().html.add_child(folium.Element(legend_html))
