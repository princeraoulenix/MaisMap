"""
Geospatial grid utilities for MaïsMap.
Validates grid consistency and generates cell geometries.
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from config.settings import STUDY_BBOX, GRID_CELL_DEG


def generate_grid_cells() -> list[dict]:
    """Return list of (lat, lon) lower-left corners for all study-area cells."""
    cells = []
    lat = STUDY_BBOX["lat_min"]
    while lat < STUDY_BBOX["lat_max"]:
        lon = STUDY_BBOX["lon_min"]
        while lon < STUDY_BBOX["lon_max"]:
            cells.append({"lat": round(lat, 1), "lon": round(lon, 1)})
            lon = round(lon + GRID_CELL_DEG, 1)
        lat = round(lat + GRID_CELL_DEG, 1)
    return cells


def validate_grid_coverage(geojson: dict) -> dict:
    """
    Check that a GeoJSON covers the expected grid cells.
    Returns {'expected': int, 'found': int, 'missing': list, 'extra': list}.
    """
    expected = {(c["lat"], c["lon"]) for c in generate_grid_cells()}
    found = set()
    for f in geojson.get("features", []):
        coords = f.get("geometry", {}).get("coordinates", [[]])[0]
        if coords:
            lon, lat = coords[0][0], coords[0][1]
            found.add((round(lat, 1), round(lon, 1)))

    return {
        "expected": len(expected),
        "found": len(found),
        "missing": sorted(expected - found),
        "extra": sorted(found - expected),
    }
