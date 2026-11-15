"""
Dry-spell analysis within the agricultural season.

Season window: onset DOY to onset + 120 days (approximate maize growing period).
If onset is None, the full April–October window is used.
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from config.thresholds import DRY_DAY_THRESHOLD, ONSET_START_DOY

SEASON_LENGTH = 120  # days after onset


def max_dry_spell(daily_rain: list[float], onset_doy: int | None) -> int:
    """Return the maximum consecutive dry-day run within the season window."""
    start = (onset_doy - 1) if onset_doy else (ONSET_START_DOY - 1)
    end = min(start + SEASON_LENGTH, len(daily_rain))
    return _max_run(daily_rain[start:end])


def _max_run(rain_slice: list[float]) -> int:
    max_r = cur = 0
    for r in rain_slice:
        if r < DRY_DAY_THRESHOLD:
            cur += 1
            max_r = max(max_r, cur)
        else:
            cur = 0
    return max_r
