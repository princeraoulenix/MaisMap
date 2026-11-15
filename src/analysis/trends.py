"""
Historical trend analysis across multiple years.

Operates on a list of per-year result dicts (as produced by the pipeline).
Clearly distinguishes historical analysis from future prediction.
"""


def compute_trends(yearly_results: list[dict]) -> dict:
    """
    Compute multi-year statistics from a list of annual cell results.

    Parameters
    ----------
    yearly_results : list of dict
        Each dict must contain keys: year, season_onset_date (DOY or None),
        false_start (bool), dry_spell_days (int), heat_days (int), risk_score (float).

    Returns
    -------
    dict with keys: false_start_frequency, mean_onset_doy, mean_dry_spell,
                    mean_heat_days, risk_distribution, years_analyzed.
    """
    valid = [r for r in yearly_results if r.get("season_onset_date") is not None]
    n = len(yearly_results)

    false_starts = sum(1 for r in yearly_results if r.get("false_start"))
    onset_doys = [r["season_onset_date"] for r in valid if isinstance(r["season_onset_date"], int)]
    dry_spells = [r["dry_spell_days"] for r in yearly_results if r.get("dry_spell_days") is not None]
    heat_days = [r["heat_days"] for r in yearly_results if r.get("heat_days") is not None]
    risk_classes = [r.get("risk_class") for r in yearly_results if r.get("risk_class")]

    return {
        "years_analyzed": n,
        "false_start_frequency": round(false_starts / n, 3) if n else None,
        "mean_onset_doy": round(sum(onset_doys) / len(onset_doys)) if onset_doys else None,
        "mean_dry_spell": round(sum(dry_spells) / len(dry_spells), 1) if dry_spells else None,
        "mean_heat_days": round(sum(heat_days) / len(heat_days), 1) if heat_days else None,
        "risk_distribution": {
            "LOW": risk_classes.count("LOW"),
            "MEDIUM": risk_classes.count("MEDIUM"),
            "HIGH": risk_classes.count("HIGH"),
        },
    }
