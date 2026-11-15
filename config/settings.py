# MaïsMap — Application settings
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DATA_DEMO_PATH      = os.path.join(BASE_DIR, "data", "demo", "demo_grid.geojson")
DATA_PROCESSED_PATH = os.path.join(BASE_DIR, "data", "processed")
DATA_RAW_PATH       = os.path.join(BASE_DIR, "data", "raw")
CACHE_DIR           = os.path.join(BASE_DIR, "data", "raw", "cache")
DATA_DERIVED_PATH   = os.path.join(BASE_DIR, "data", "derived")
SOIL_DATA_PATH      = os.path.join(BASE_DIR, "data", "derived", "soil_grid.json")

# Study area bounding box: Northern + Far North Cameroon
STUDY_BBOX = {"lon_min": 13.0, "lon_max": 16.0, "lat_min": 7.5, "lat_max": 12.5}

# Grid cell size in degrees (~50 km at this latitude)
GRID_CELL_DEG = 0.5

# Map defaults — centered on Garoua
MAP_CENTER = [9.5, 14.5]
MAP_ZOOM = 6

# Real data available for these years (NASA POWER fetched)
REAL_DATA_YEARS = [2020, 2021, 2022, 2023]

# Demo years (synthetic fallback)
DEMO_YEARS = list(range(2010, 2024))

# Use real data by default when available
USE_REAL_DATA_DEFAULT = True

APP_TITLE    = "MaïsMap"
APP_SUBTITLE = "Aide à la décision agricole — Nord Cameroun"
