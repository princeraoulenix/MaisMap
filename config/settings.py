# MaïsMap — Application settings
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DATA_DEMO_PATH = os.path.join(BASE_DIR, "data", "demo", "demo_grid.geojson")
DATA_PROCESSED_PATH = os.path.join(BASE_DIR, "data", "processed")
DATA_RAW_PATH = os.path.join(BASE_DIR, "data", "raw")
CACHE_DIR = os.path.join(BASE_DIR, "data", "raw", "cache")

# Study area bounding box: Northern + Far North Cameroon
STUDY_BBOX = {"lon_min": 13.0, "lon_max": 16.0, "lat_min": 7.5, "lat_max": 12.5}

# Grid cell size in degrees (~50 km at this latitude)
GRID_CELL_DEG = 0.5

# Map defaults
MAP_CENTER = [9.5, 14.5]
MAP_ZOOM = 6

# Demo years available
DEMO_YEARS = list(range(1984, 2024))

APP_TITLE = "MaïsMap"
APP_SUBTITLE = "Aide à la décision agricole — Nord Cameroun"
