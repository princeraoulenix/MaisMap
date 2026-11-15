"""
Agricultural risk model.

Combines false-start probability, dry-spell severity and heat-stress days
into a 0–100 risk score with LOW / MEDIUM / HIGH classification.

Weights are documented in config/thresholds.py.
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from config.thresholds import (
    RISK_WEIGHT_FALSE_START, RISK_WEIGHT_DRY_SPELL, RISK_WEIGHT_HEAT,
    RISK_LOW_MAX, RISK_MEDIUM_MAX,
    DRY_SPELL_CRITICAL, DRY_SPELL_SEVERE,
    HEAT_DAYS_MODERATE, HEAT_DAYS_HIGH
)


def compute_risk(false_start: bool, max_dry_days: int, heat_days: int) -> dict:
    """
    Return {'score': float, 'class': str, 'components': dict}.

    Score components are normalised to 0–100 before weighting.
    Missing data (None) is treated conservatively as moderate risk.
    """
    fs_score = 100.0 if false_start else 0.0

    if max_dry_days is None:
        ds_score = 50.0
    elif max_dry_days >= DRY_SPELL_SEVERE:
        ds_score = 100.0
    elif max_dry_days >= DRY_SPELL_CRITICAL:
        ds_score = 60.0
    else:
        ds_score = min(max_dry_days / DRY_SPELL_CRITICAL * 60.0, 60.0)

    if heat_days is None:
        ht_score = 50.0
    elif heat_days >= HEAT_DAYS_HIGH:
        ht_score = 100.0
    elif heat_days >= HEAT_DAYS_MODERATE:
        ht_score = 60.0
    else:
        ht_score = min(heat_days / HEAT_DAYS_MODERATE * 60.0, 60.0)

    score = (
        RISK_WEIGHT_FALSE_START * fs_score
        + RISK_WEIGHT_DRY_SPELL * ds_score
        + RISK_WEIGHT_HEAT * ht_score
    )

    if score <= RISK_LOW_MAX:
        risk_class = "LOW"
    elif score <= RISK_MEDIUM_MAX:
        risk_class = "MEDIUM"
    else:
        risk_class = "HIGH"

    return {
        "score": round(score, 1),
        "class": risk_class,
        "components": {
            "false_start_score": round(fs_score, 1),
            "dry_spell_score": round(ds_score, 1),
            "heat_score": round(ht_score, 1),
        },
    }


def sowing_advice(risk: dict, onset_doy: int | None, false_start: bool) -> str:
    """Generate a cautious, human-readable sowing recommendation."""
    if onset_doy is None:
        return ("Aucun début de saison détecté pour cette année. "
                "Attendre des pluies régulières avant tout semis.")
    if false_start:
        return ("Faux départ détecté : les premières pluies ont été suivies d'une "
                "longue période sèche. Conditions suggèrent d'attendre des pluies "
                "plus stables avant de semer.")
    if risk["class"] == "HIGH":
        return ("Risque élevé : sécheresses prolongées et/ou stress thermique "
                "importants. Semis déconseillé sans suivi pluviométrique local.")
    if risk["class"] == "MEDIUM":
        return ("Risque modéré : conditions acceptables mais incertaines. "
                "Surveiller les prévisions locales avant de semer.")
    return ("Conditions favorables détectées. Semis possible autour du jour "
            f"{onset_doy} (DOJ). Confirmer avec les prévisions locales.")
