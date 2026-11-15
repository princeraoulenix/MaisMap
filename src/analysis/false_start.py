"""
False-start detection.

A false start occurs when an apparent onset trigger is followed by a dry spell
of >= FALSE_START_DRY_DAYS consecutive days within FALSE_START_WINDOW days.
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from config.thresholds import (
    FALSE_START_DRY_DAYS, FALSE_START_WINDOW, DRY_DAY_THRESHOLD,
    ONSET_START_DOY, ONSET_RAIN_MM, ONSET_DAYS
)


def detect_false_start(daily_rain: list[float]) -> bool:
    """
    Return True if the first apparent onset trigger is a false start.

    A trigger is the first day after ONSET_START_DOY where cumulative rain
    over ONSET_DAYS >= ONSET_RAIN_MM, regardless of the subsequent dry-spell
    check used in onset.py.
    """
    n = len(daily_rain)
    for i in range(ONSET_START_DOY - 1, n - ONSET_DAYS):
        if sum(daily_rain[i:i + ONSET_DAYS]) >= ONSET_RAIN_MM:
            check_end = min(i + ONSET_DAYS + FALSE_START_WINDOW, n)
            post = daily_rain[i + ONSET_DAYS:check_end]
            if _max_dry_run(post) >= FALSE_START_DRY_DAYS:
                return True
            return False  # trigger found, no false start
    return False  # no trigger found — cannot be a false start


def _max_dry_run(rain_slice: list[float]) -> int:
    """Return the length of the longest consecutive dry-day run."""
    max_run = cur = 0
    for r in rain_slice:
        if r < DRY_DAY_THRESHOLD:
            cur += 1
            max_run = max(max_run, cur)
        else:
            cur = 0
    return max_run
