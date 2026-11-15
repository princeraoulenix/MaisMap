"""
Rainy-season onset detection — Sivakumar (1988) / AGRHYMET method.

Onset: first day after ONSET_START_DOY with cumulative rainfall >= ONSET_RAIN_MM
over ONSET_DAYS consecutive days, not followed by a dry spell >= ONSET_DRY_DAYS
within the next ONSET_WINDOW days.
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from config.thresholds import (
    ONSET_START_DOY, ONSET_RAIN_MM, ONSET_DAYS,
    ONSET_DRY_DAYS, ONSET_WINDOW, DRY_DAY_THRESHOLD
)


def detect_onset(daily_rain: list[float], year: int) -> int | None:
    """
    Return the day-of-year of rainy-season onset, or None if not detected.

    Parameters
    ----------
    daily_rain : list of float
        Daily precipitation (mm) for the full year, index 0 = Jan 1.
    year : int
        Calendar year (used to handle leap years).
    """
    n = len(daily_rain)
    for i in range(ONSET_START_DOY - 1, n - ONSET_DAYS):
        window_sum = sum(daily_rain[i:i + ONSET_DAYS])
        if window_sum >= ONSET_RAIN_MM:
            # Check for invalidating dry spell in the next ONSET_WINDOW days
            check_end = min(i + ONSET_DAYS + ONSET_WINDOW, n)
            if not _has_dry_spell(daily_rain[i + ONSET_DAYS:check_end], ONSET_DRY_DAYS):
                return i + 1  # 1-based DOY
    return None


def _has_dry_spell(rain_slice: list[float], min_length: int) -> bool:
    """Return True if rain_slice contains >= min_length consecutive dry days."""
    count = 0
    for r in rain_slice:
        if r < DRY_DAY_THRESHOLD:
            count += 1
            if count >= min_length:
                return True
        else:
            count = 0
    return False
