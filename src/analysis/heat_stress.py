"""
Heat-stress analysis.

Counts days exceeding HEAT_STRESS_TMAX within the season window.
Threshold: 35 °C Tmax — above this, maize pollen viability is significantly reduced
(Schlenker & Roberts 2009; CIMMYT heat-stress guidelines).
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from config.thresholds import HEAT_STRESS_TMAX, ONSET_START_DOY

SEASON_LENGTH = 120


def count_heat_days(daily_tmax: list[float], onset_doy: int | None) -> int:
    """Return the number of days with Tmax > HEAT_STRESS_TMAX within the season."""
    start = (onset_doy - 1) if onset_doy else (ONSET_START_DOY - 1)
    end = min(start + SEASON_LENGTH, len(daily_tmax))
    return sum(1 for t in daily_tmax[start:end] if t is not None and t > HEAT_STRESS_TMAX)
