"""
Plotly charts for MaïsMap historical analysis.
All charts include reference lines for agronomic thresholds.
"""
import plotly.graph_objects as go
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from config.thresholds import DRY_SPELL_CRITICAL, DRY_SPELL_SEVERE, HEAT_DAYS_MODERATE, HEAT_DAYS_HIGH

_LAYOUT = dict(height=300, margin=dict(t=44, b=30, l=40, r=20),
               plot_bgcolor="#fafafa", paper_bgcolor="white",
               font=dict(family="sans-serif", size=12))


def chart_onset_by_year(yearly_data: list[dict]) -> go.Figure:
    """Bar chart of mean onset DOY per year with April 1 reference line."""
    pairs = [(d["year"], d["season_onset_date"])
             for d in yearly_data if d.get("season_onset_date")]
    if not pairs:
        return _empty_fig("Début de saison par année")
    years, onsets = zip(*pairs)
    fig = go.Figure(go.Bar(
        x=list(years), y=list(onsets),
        marker_color="#3498db", name="Début de saison (DOJ)",
    ))
    fig.add_hline(y=91, line_dash="dot", line_color="#e74c3c",
                  annotation_text="1er avril (DOJ 91)", annotation_position="top right")
    fig.update_layout(
        title="Jour de début de saison par année",
        xaxis_title="Année", yaxis_title="Jour de l'année (DOJ)",
        **_LAYOUT,
    )
    return fig


def chart_false_start_frequency(yearly_data: list[dict]) -> go.Figure:
    """Bar chart of false-start percentage per year."""
    years  = [d["year"] for d in yearly_data]
    values = [d.get("false_start_pct", (1 if d.get("false_start") else 0) * 100)
              for d in yearly_data]
    colors = ["#e74c3c" if v > 50 else "#f39c12" if v > 0 else "#2ecc71" for v in values]
    fig = go.Figure(go.Bar(x=years, y=values, marker_color=colors, name="% cellules faux départ"))
    fig.update_layout(
        title="Fréquence des faux départs par année (%)",
        xaxis_title="Année", yaxis_title="% cellules avec faux départ",
        yaxis=dict(range=[0, 105]),
        **_LAYOUT,
    )
    return fig


def chart_dry_spell(yearly_data: list[dict]) -> go.Figure:
    """Line chart of mean max dry-spell days per year with threshold lines."""
    pairs = [(d["year"], d["dry_spell_days"])
             for d in yearly_data if d.get("dry_spell_days") is not None]
    if not pairs:
        return _empty_fig("Sécheresse par année")
    years, values = zip(*pairs)
    fig = go.Figure(go.Scatter(
        x=list(years), y=list(values),
        mode="lines+markers",
        line=dict(color="#e67e22", width=2),
        marker=dict(size=6),
        name="Sécheresse max moy. (jours)",
    ))
    fig.add_hline(y=DRY_SPELL_CRITICAL, line_dash="dot", line_color="#f39c12",
                  annotation_text=f"Critique ({DRY_SPELL_CRITICAL}j)", annotation_position="top right")
    fig.add_hline(y=DRY_SPELL_SEVERE, line_dash="dot", line_color="#e74c3c",
                  annotation_text=f"Sévère ({DRY_SPELL_SEVERE}j)", annotation_position="top right")
    fig.update_layout(
        title="Sécheresse maximale moyenne par année",
        xaxis_title="Année", yaxis_title="Jours secs consécutifs",
        **_LAYOUT,
    )
    return fig


def chart_heat_days(yearly_data: list[dict]) -> go.Figure:
    """Line chart of mean heat-stress days per year."""
    pairs = [(d["year"], d["heat_days"])
             for d in yearly_data if d.get("heat_days") is not None]
    if not pairs:
        return _empty_fig("Jours de chaleur par année")
    years, values = zip(*pairs)
    fig = go.Figure(go.Scatter(
        x=list(years), y=list(values),
        mode="lines+markers",
        line=dict(color="#c0392b", width=2),
        marker=dict(size=6),
        name="Jours Tmax>35°C",
    ))
    fig.add_hline(y=HEAT_DAYS_MODERATE, line_dash="dot", line_color="#f39c12",
                  annotation_text=f"Modéré ({HEAT_DAYS_MODERATE}j)", annotation_position="top right")
    fig.add_hline(y=HEAT_DAYS_HIGH, line_dash="dot", line_color="#e74c3c",
                  annotation_text=f"Élevé ({HEAT_DAYS_HIGH}j)", annotation_position="top right")
    fig.update_layout(
        title="Jours de stress thermique moyen par année (Tmax > 35°C)",
        xaxis_title="Année", yaxis_title="Jours (Tmax > 35°C)",
        **_LAYOUT,
    )
    return fig


def chart_risk_distribution(yearly_data: list[dict]) -> go.Figure:
    """Donut chart of risk class distribution across all years."""
    classes = [d.get("risk_class") for d in yearly_data if d.get("risk_class")]
    counts = {c: classes.count(c) for c in ["LOW", "MEDIUM", "HIGH"]}
    fig = go.Figure(go.Pie(
        labels=["Faible (LOW)", "Modéré (MEDIUM)", "Élevé (HIGH)"],
        values=[counts["LOW"], counts["MEDIUM"], counts["HIGH"]],
        marker_colors=["#2ecc71", "#f39c12", "#e74c3c"],
        hole=0.40,
        textinfo="label+percent",
    ))
    fig.update_layout(
        title="Distribution des classes de risque (toutes années)",
        showlegend=False,
        **_LAYOUT,
    )
    return fig


def _empty_fig(title: str) -> go.Figure:
    fig = go.Figure()
    fig.update_layout(title=f"{title} — données insuffisantes", **_LAYOUT)
    return fig
