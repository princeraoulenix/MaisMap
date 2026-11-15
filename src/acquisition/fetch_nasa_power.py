"""
Fetch real NASA POWER data for all MaïsMap grid cells.
Saves per-cell JSON to data/raw/cache/ and builds processed GeoJSON.

Usage: python src/acquisition/fetch_nasa_power.py
"""
import sys, os, json, time, logging, requests
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from config.settings import STUDY_BBOX, GRID_CELL_DEG, DATA_PROCESSED_PATH, CACHE_DIR
from src.analysis.onset import detect_onset
from src.analysis.false_start import detect_false_start
from src.analysis.dry_spell import max_dry_spell
from src.analysis.heat_stress import count_heat_days
from src.analysis.risk_model import compute_risk, sowing_advice
from datetime import date

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
logger = logging.getLogger(__name__)

POWER_URL = "https://power.larc.nasa.gov/api/temporal/daily/point"
YEARS = [2020, 2021, 2022, 2023]
STEP = GRID_CELL_DEG


def _grid_cells():
    cells = []
    lat = STUDY_BBOX["lat_min"]
    while lat < STUDY_BBOX["lat_max"]:
        lon = STUDY_BBOX["lon_min"]
        while lon < STUDY_BBOX["lon_max"]:
            cells.append((round(lat, 1), round(lon, 1)))
            lon = round(lon + STEP, 1)
        lat = round(lat + STEP, 1)
    return cells


def _fetch_cell(lat, lon, year):
    os.makedirs(CACHE_DIR, exist_ok=True)
    cache = os.path.join(CACHE_DIR, f"power_{lat:.1f}_{lon:.1f}_{year}.json")
    if os.path.exists(cache):
        with open(cache, encoding="utf-8") as f:
            return json.load(f)
    params = {
        "parameters": "PRECTOTCORR,T2M_MAX,T2M_MIN",
        "community": "AG",
        "longitude": lon + STEP / 2,
        "latitude": lat + STEP / 2,
        "start": f"{year}0101",
        "end": f"{year}1231",
        "format": "JSON",
    }
    for attempt in range(3):
        try:
            r = requests.get(POWER_URL, params=params, timeout=60)
            r.raise_for_status()
            data = r.json()
            with open(cache, "w", encoding="utf-8") as f:
                json.dump(data, f)
            return data
        except Exception as e:
            logger.warning("Attempt %d failed for (%.1f,%.1f) %d: %s", attempt+1, lat, lon, year, e)
            time.sleep(2)
    return None


def _extract(data, var, year):
    try:
        raw = data["properties"]["parameter"][var]
        prefix = str(year)
        return [None if v == -999.0 else v for k, v in raw.items() if k.startswith(prefix)]
    except (KeyError, TypeError):
        return None


def _region(lat):
    if lat >= 10.5: return "Extreme-Nord"
    if lat >= 8.5:  return "Nord"
    return "Adamaoua"


def _dept(lat, lon):
    if lat >= 11.5: return "Logone-et-Chari" if lon >= 14.5 else "Mayo-Sava"
    if lat >= 10.5: return "Mayo-Kani" if lon >= 14.5 else "Diamare"
    if lat >= 9.5:  return "Benoue" if lon >= 14.0 else "Mayo-Rey"
    return "Faro"


def _polygon(lat, lon):
    return {"type": "Polygon", "coordinates": [[
        [lon, lat], [lon+STEP, lat], [lon+STEP, lat+STEP], [lon, lat+STEP], [lon, lat]
    ]]}


def process_year(year):
    cells = _grid_cells()
    features = []
    for i, (lat, lon) in enumerate(cells):
        logger.info("[%d/%d] lat=%.1f lon=%.1f year=%d", i+1, len(cells), lat, lon, year)
        data = _fetch_cell(lat, lon, year)
        if not data:
            logger.warning("Skipping (%.1f,%.1f) %d — no data", lat, lon, year)
            continue

        rain = _extract(data, "PRECTOTCORR", year)
        tmax = _extract(data, "T2M_MAX", year)
        tmin = _extract(data, "T2M_MIN", year)

        if not rain:
            continue

        rain_c = [r if r is not None else 0.0 for r in rain]
        onset   = detect_onset(rain_c, year)
        fs      = detect_false_start(rain_c)
        dry     = max_dry_spell(rain_c, onset)
        heat    = count_heat_days(tmax or [], onset) if tmax else None
        risk    = compute_risk(fs, dry, heat)
        advice  = sowing_advice(risk, onset, fs)

        onset_str = None
        if onset:
            try:
                onset_str = date.fromordinal(date(year,1,1).toordinal()+onset-1).isoformat()
            except Exception:
                pass

        # Mean Tmax and Tmin for season window
        season_start = (onset or 91) - 1
        season_end   = min(season_start + 120, len(tmax or []))
        tmax_season  = [t for t in (tmax or [])[season_start:season_end] if t is not None]
        tmin_season  = [t for t in (tmin or [])[season_start:season_end] if t is not None]
        mean_tmax    = round(sum(tmax_season)/len(tmax_season), 1) if tmax_season else None
        mean_tmin    = round(sum(tmin_season)/len(tmin_season), 1) if tmin_season else None
        total_rain   = round(sum(rain_c[season_start:season_end]), 1)

        features.append({
            "type": "Feature",
            "geometry": _polygon(lat, lon),
            "properties": {
                "cell_id": f"R{i+1:04d}",
                "region": _region(lat),
                "department": _dept(lat, lon),
                "year": year,
                "season_onset_date": onset,
                "season_onset_date_str": onset_str,
                "false_start": fs,
                "dry_spell_days": dry,
                "heat_days": heat,
                "risk_score": risk["score"],
                "risk_class": risk["class"],
                "sowing_advice": advice,
                "seasonal_rain_mm": total_rain,
                "mean_tmax_c": mean_tmax,
                "mean_tmin_c": mean_tmin,
                "data_source": "NASA POWER v9 (PRECTOTCORR, T2M_MAX, T2M_MIN)",
                "data_period": str(year),
                "spatial_resolution": "0.5 deg (~55 km)",
                "confidence": "real",
            }
        })
        time.sleep(0.25)

    return {"type": "FeatureCollection",
            "metadata": {"source": "NASA POWER v9", "year": year, "crs": "EPSG:4326"},
            "features": features}


if __name__ == "__main__":
    os.makedirs(DATA_PROCESSED_PATH, exist_ok=True)
    for yr in YEARS:
        logger.info("=== Year %d ===", yr)
        gj = process_year(yr)
        out = os.path.join(DATA_PROCESSED_PATH, f"grid_{yr}.geojson")
        with open(out, "w", encoding="utf-8") as f:
            json.dump(gj, f, ensure_ascii=False, indent=2)
        logger.info("Saved %d features -> %s", len(gj["features"]), out)
