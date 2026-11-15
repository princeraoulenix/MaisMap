"""
NASA POWER API connector.

Retrieves daily meteorological data for a point location.
API documentation: https://power.larc.nasa.gov/docs/services/api/

Data is cached locally to avoid repeated downloads.
"""
import os, json, time, logging
import requests

logger = logging.getLogger(__name__)

POWER_BASE = "https://power.larc.nasa.gov/api/temporal/daily/point"
CACHE_DIR = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'raw', 'cache')

PARAMETERS = {
    "PRECTOTCORR": "Precipitation (mm/day)",
    "T2M_MAX": "Maximum temperature at 2m (°C)",
    "T2M_MIN": "Minimum temperature at 2m (°C)",
}


def fetch_power_daily(lat: float, lon: float, start_year: int, end_year: int) -> dict | None:
    """
    Fetch daily POWER data for a point. Returns parsed JSON or None on failure.
    Results are cached as JSON files.
    """
    os.makedirs(CACHE_DIR, exist_ok=True)
    cache_file = os.path.join(
        CACHE_DIR, f"power_{lat:.2f}_{lon:.2f}_{start_year}_{end_year}.json"
    )
    if os.path.exists(cache_file):
        logger.info("Loading POWER data from cache: %s", cache_file)
        with open(cache_file) as f:
            return json.load(f)

    params = {
        "parameters": ",".join(PARAMETERS.keys()),
        "community": "AG",
        "longitude": lon,
        "latitude": lat,
        "start": f"{start_year}0101",
        "end": f"{end_year}1231",
        "format": "JSON",
    }
    try:
        logger.info("Fetching NASA POWER data for (%.2f, %.2f) %d–%d", lat, lon, start_year, end_year)
        resp = requests.get(POWER_BASE, params=params, timeout=60)
        resp.raise_for_status()
        data = resp.json()
        with open(cache_file, "w") as f:
            json.dump(data, f)
        return data
    except requests.RequestException as e:
        logger.error("NASA POWER request failed: %s", e)
        return None


def extract_daily_series(power_data: dict, variable: str, year: int) -> list[float] | None:
    """
    Extract a list of 365/366 daily values for a given variable and year.
    Returns None if data is unavailable.
    Missing values (-999) are replaced with None.
    """
    try:
        raw = power_data["properties"]["parameter"][variable]
        prefix = str(year)
        values = [
            (None if v == -999.0 else v)
            for k, v in raw.items()
            if k.startswith(prefix)
        ]
        return values if values else None
    except (KeyError, TypeError):
        return None
