"""
Data loader — handles demo GeoJSON and real processed datasets.
"""
import json, os, logging
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from config.settings import DATA_DEMO_PATH, DATA_PROCESSED_PATH

logger = logging.getLogger(__name__)


def load_geojson(path: str) -> dict | None:
    """Load and return a GeoJSON dict, or None on failure."""
    if not os.path.exists(path):
        logger.warning("GeoJSON not found: %s", path)
        return None
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def load_dataset(year: int, use_demo: bool = True) -> tuple[dict | None, bool]:
    """
    Return (geojson_dict, is_demo).

    Tries the real processed dataset first; falls back to demo.
    """
    real_path = os.path.join(DATA_PROCESSED_PATH, f"grid_{year}.geojson")
    if not use_demo and os.path.exists(real_path):
        data = load_geojson(real_path)
        if data:
            return data, False

    data = load_geojson(DATA_DEMO_PATH)
    if data:
        # Filter features to the requested year
        features = [
            f for f in data.get("features", [])
            if f.get("properties", {}).get("year") == year
        ]
        if features:
            return {**data, "features": features}, True
    return None, True


def get_available_years(use_demo: bool = True) -> list[int]:
    """Return sorted list of years available in the dataset."""
    if use_demo:
        path = DATA_DEMO_PATH
        if not os.path.exists(path):
            return []
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        years = sorted({
            f["properties"]["year"]
            for f in data.get("features", [])
            if "year" in f.get("properties", {})
        })
        return years

    years = []
    if os.path.exists(DATA_PROCESSED_PATH):
        for fn in os.listdir(DATA_PROCESSED_PATH):
            if fn.startswith("grid_") and fn.endswith(".geojson"):
                try:
                    years.append(int(fn[5:9]))
                except ValueError:
                    pass
    return sorted(years)
