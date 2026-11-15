"""
Lightweight Plotly charts for historical analysis.
"""
import plotly.graph_objects as go
import plotly.express as px


def chart_onset_by_year(yearly_data: list[dict]) -> go.Figure:
    """Bar chart of mean onset DOY per year."""
    years = [d["year"] for d in yearly_data if d.get("season_onset_date")]
    onsets = [d["season_onset_date"] for d in yearly_data if d.get("season_onset_date")]
    fig = go.Figure(go.Bar(x=years, y=onsets, marker_color="#3498db"))
    fig.update_layout(
        title="Jour de début de saison par année",
        xaxis_title="Année", yaxis_title="Jour de l'année (DOJ)",
        height=300, margin=dict(t=40, b=30)
    )
    return fig


def chart_false_start_frequency(yearly_data: list[dict]) -> go.Figure:
    """Bar chart showing false-start occurrence per year (0 or 1)."""
    years = [d["year"] for d in yearly_data]
    values = [1 if d.get("false_start") else 0 for d in yearly_data]
    colors = ["#e74c3c" if v else "#2ecc71" for v in values]
    fig = go.Figure(go.Bar(x=years, y=values, marker_color=colors))
    fig.update_layout(
        title="Faux départs par année",
        xaxis_title="Année", yaxis_title="Faux départ (1=Oui)",
        height=280, margin=dict(t=40, b=30), yaxis=dict(tickvals=[0, 1])
    )
    return fig


def chart_dry_spell(yearly_data: list[dict]) -> go.Figure:
    """Line chart of max dry-spell days per year."""
    years = [d["year"] for d in yearly_data if d.get("dry_spell_days") is not None]
    values = [d["dry_spell_days"] for d in yearly_data if d.get("dry_spell_days") is not None]
    fig = go.Figure(go.Scatter(x=years, y=values, mode="lines+markers",
                               line=dict(color="#e67e22", width=2)))
    fig.update_layout(
        title="Sécheresse maximale par année (jours consécutifs)",
        xaxis_title="Année", yaxis_title="Jours secs consécutifs",
        height=280, margin=dict(t=40, b=30)
    )
    return fig


def chart_risk_distribution(yearly_data: list[dict]) -> go.Figure:
    """Pie chart of risk class distribution across all years."""
    classes = [d.get("risk_class") for d in yearly_data if d.get("risk_class")]
    counts = {c: classes.count(c) for c in ["LOW", "MEDIUM", "HIGH"]}
    fig = go.Figure(go.Pie(
        labels=list(counts.keys()),
        values=list(counts.values()),
        marker_colors=["#2ecc71", "#f39c12", "#e74c3c"],
        hole=0.35
    ))
    fig.update_layout(title="Distribution des classes de risque", height=300,
                      margin=dict(t=40, b=10))
    return fig
