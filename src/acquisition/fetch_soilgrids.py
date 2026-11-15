"""
Fetch SoilGrids v2 soil properties for all MaïsMap grid cells.
Source: ISRIC World Soil Information — https://rest.isric.org/soilgrids/v2.0/
Properties: phh2o, soc, clay, sand, silt, bdod, cec, nitrogen
Depth: 0-5cm and 5-15cm
"""
import sys, os, json, time, logging, requests
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from config.settings import STUDY_BBOX, GRID_CELL_DEG, CACHE_DIR

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
logger = logging.getLogger(__name__)

SOILGRIDS_URL = "https://rest.isric.org/soilgrids/v2.0/properties/query"
PROPERTIES = ["phh2o", "soc", "clay", "sand", "silt", "bdod", "cec", "nitrogen"]
DEPTHS = ["0-5cm", "5-15cm"]
STEP = GRID_CELL_DEG
OUT_FILE = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'derived', 'soil_grid.json')


def _grid_centroids():
    pts = []
    lat = STUDY_BBOX["lat_min"]
    while lat < STUDY_BBOX["lat_max"]:
        lon = STUDY_BBOX["lon_min"]
        while lon < STUDY_BBOX["lon_max"]:
            pts.append((round(lat + STEP/2, 2), round(lon + STEP/2, 2)))
            lon = round(lon + STEP, 1)
        lat = round(lat + STEP, 1)
    return pts


def _fetch_soil(lat, lon):
    os.makedirs(CACHE_DIR, exist_ok=True)
    cache = os.path.join(CACHE_DIR, f"soil_{lat:.2f}_{lon:.2f}.json")
    if os.path.exists(cache):
        with open(cache, encoding="utf-8") as f:
            return json.load(f)
    params = {
        "lon": lon, "lat": lat,
        "property": PROPERTIES,
        "depth": DEPTHS,
        "value": "mean,uncertainty",
    }
    for attempt in range(3):
        try:
            r = requests.get(SOILGRIDS_URL, params=params, timeout=30)
            r.raise_for_status()
            data = r.json()
            with open(cache, "w", encoding="utf-8") as f:
                json.dump(data, f)
            return data
        except Exception as e:
            logger.warning("Attempt %d failed for soil (%.2f,%.2f): %s", attempt+1, lat, lon, e)
            time.sleep(2)
    return None


def _parse_soil(data):
    """Extract mean values for each property at 0-5cm depth."""
    result = {}
    if not data:
        return result
    for layer in data.get("properties", {}).get("layers", []):
        name = layer.get("name")
        d_factor = layer.get("unit_measure", {}).get("d_factor", 1)
        for depth_info in layer.get("depths", []):
            if depth_info.get("range", {}).get("top_depth") == 0:
                mean_val = depth_info.get("values", {}).get("mean")
                unc_val  = depth_info.get("values", {}).get("uncertainty")
                if mean_val is not None:
                    result[name] = round(mean_val / d_factor, 3)
                    if unc_val is not None:
                        result[f"{name}_uncertainty"] = round(unc_val / d_factor, 3)
    return result


def fetch_all():
    pts = _grid_centroids()
    results = {}
    for i, (lat, lon) in enumerate(pts):
        logger.info("[%d/%d] Soil at (%.2f, %.2f)", i+1, len(pts), lat, lon)
        raw = _fetch_soil(lat, lon)
        parsed = _parse_soil(raw)
        key = f"{lat:.2f}_{lon:.2f}"
        results[key] = {"lat": lat, "lon": lon, **parsed,
                        "source": "ISRIC SoilGrids v2.0",
                        "depth": "0-5cm", "crs": "EPSG:4326"}
        time.sleep(0.5)

    os.makedirs(os.path.dirname(OUT_FILE), exist_ok=True)
    with open(OUT_FILE, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    logger.info("Saved soil data for %d cells -> %s", len(results), OUT_FILE)
    return results


if __name__ == "__main__":
    fetch_all()
