"""
Data loader — handles real NASA POWER GeoJSON and synthetic demo datasets.
Automatically uses real data when available, falls back to demo.
"""
import json, os, logging
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from config.settings import (
    DATA_DEMO_PATH, DATA_PROCESSED_PATH, SOIL_DATA_PATH,
    REAL_DATA_YEARS, USE_REAL_DATA_DEFAULT
)

logger = logging.getLogger(__name__)


def load_geojson(path: str) -> dict | None:
    if not os.path.exists(path):
        logger.warning("GeoJSON not found: %s", path)
        return None
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def load_soil_data() -> dict:
    """Load SoilGrids data. Returns empty dict if unavailable."""
    if not os.path.exists(SOIL_DATA_PATH):
        return {}
    with open(SOIL_DATA_PATH, encoding="utf-8") as f:
        return json.load(f)


def _soil_key(lat: float, lon: float) -> str:
    """Generate lookup key matching the soil data file format."""
    return f"{lat:.2f}_{lon:.2f}"


def _enrich_with_soil(features: list[dict], soil_data: dict) -> list[dict]:
    """Add soil properties to each feature if available."""
    if not soil_data:
        return features
    enriched = []
    for f in features:
        coords = f.get("geometry", {}).get("coordinates", [[]])[0]
        if coords:
            lon_ll, lat_ll = coords[0][0], coords[0][1]
            # Centroid
            clat = round(lat_ll + 0.25, 2)
            clon = round(lon_ll + 0.25, 2)
            key = _soil_key(clat, clon)
            soil = soil_data.get(key, {})
            soil_props = {k: v for k, v in soil.items()
                          if k not in ("lat", "lon", "source", "depth", "crs")}
            if soil_props:
                f = {**f, "properties": {**f["properties"], **soil_props,
                                          "soil_source": "ISRIC SoilGrids v2.0",
                                          "soil_depth": "0-5cm"}}
        enriched.append(f)
    return enriched


def load_dataset(year: int, use_demo: bool = False) -> tuple[dict | None, bool]:
    """
    Return (geojson_dict, is_demo).

    Priority: real processed data > demo data.
    """
    real_path = os.path.join(DATA_PROCESSED_PATH, f"grid_{year}.geojson")
    if not use_demo and os.path.exists(real_path):
        data = load_geojson(real_path)
        if data and data.get("features"):
            soil = load_soil_data()
            data["features"] = _enrich_with_soil(data["features"], soil)
            return data, False

    # Fall back to demo
    data = load_geojson(DATA_DEMO_PATH)
    if data:
        features = [
            f for f in data.get("features", [])
            if f.get("properties", {}).get("year") == year
        ]
        if features:
            return {**data, "features": features}, True
    return None, True


def get_available_years(use_demo: bool = False) -> list[int]:
    """Return sorted list of years with available data."""
    if not use_demo:
        years = []
        if os.path.exists(DATA_PROCESSED_PATH):
            for fn in os.listdir(DATA_PROCESSED_PATH):
                if fn.startswith("grid_") and fn.endswith(".geojson"):
                    try:
                        years.append(int(fn[5:9]))
                    except ValueError:
                        pass
        if years:
            return sorted(years)

    # Demo fallback
    if not os.path.exists(DATA_DEMO_PATH):
        return []
    with open(DATA_DEMO_PATH, encoding="utf-8") as f:
        data = json.load(f)
    return sorted({
        f["properties"]["year"]
        for f in data.get("features", [])
        if "year" in f.get("properties", {})
    })
