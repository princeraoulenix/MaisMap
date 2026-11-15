"""
NASA POWER data pipeline for MaïsMap.

Fetches daily PRECTOTCORR and T2M_MAX for each 0.5-degree grid cell
over Northern Cameroon, runs the agronomic analysis, and exports
a GeoJSON file to data/processed/grid_{year}.geojson.

Usage:
    python src/data/nasa_pipeline.py --year 2022
    python src/data/nasa_pipeline.py --year 2022 --year 2021

Requires internet access. Results are cached in data/raw/cache/.
"""
import argparse, json, os, sys, time, logging
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from src.data.nasa_power import fetch_power_daily, extract_daily_series
from src.analysis.onset import detect_onset
from src.analysis.false_start import detect_false_start
from src.analysis.dry_spell import max_dry_spell
from src.analysis.heat_stress import count_heat_days
from src.analysis.risk_model import compute_risk, sowing_advice
from config.settings import STUDY_BBOX, GRID_CELL_DEG, DATA_PROCESSED_PATH
from datetime import date

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
logger = logging.getLogger(__name__)

STEP = GRID_CELL_DEG


def _cell_polygon(lat: float, lon: float) -> dict:
    return {
        "type": "Polygon",
        "coordinates": [[
            [lon, lat], [lon + STEP, lat],
            [lon + STEP, lat + STEP], [lon, lat + STEP],
            [lon, lat],
        ]],
    }


def _region(lat: float) -> str:
    if lat >= 10.5:
        return "Extreme-Nord"
    if lat >= 8.5:
        return "Nord"
    return "Adamaoua"


def _department(lat: float, lon: float) -> str:
    if lat >= 11.5:
        return "Logone-et-Chari" if lon >= 14.5 else "Mayo-Sava"
    if lat >= 10.5:
        return "Mayo-Kani" if lon >= 14.5 else "Diamare"
    if lat >= 9.5:
        return "Benoue" if lon >= 14.0 else "Mayo-Rey"
    return "Faro"


def process_year(year: int) -> dict:
    """
    Fetch NASA POWER data for all grid cells and compute agronomic indicators.
    Returns a GeoJSON FeatureCollection.
    """
    bbox = STUDY_BBOX
    lats = []
    lat = bbox["lat_min"]
    while lat < bbox["lat_max"]:
        lats.append(round(lat, 1))
        lat = round(lat + STEP, 1)
    lons = []
    lon = bbox["lon_min"]
    while lon < bbox["lon_max"]:
        lons.append(round(lon, 1))
        lon = round(lon + STEP, 1)

    features = []
    cell_id = 0

    for lat in lats:
        for lon in lons:
            cell_id += 1
            cell_lat = lat + STEP / 2  # centroid
            cell_lon = lon + STEP / 2

            logger.info("Processing cell %d: lat=%.1f lon=%.1f year=%d",
                        cell_id, lat, lon, year)

            power_data = fetch_power_daily(cell_lat, cell_lon, year, year)

            if power_data is None:
                logger.warning("No POWER data for (%.1f, %.1f) %d — skipping", lat, lon, year)
                continue

            rain = extract_daily_series(power_data, "PRECTOTCORR", year)
            tmax = extract_daily_series(power_data, "T2M_MAX", year)

            if not rain:
                logger.warning("Empty rain series for (%.1f, %.1f) %d", lat, lon, year)
                continue

            # Replace None with 0 only for rain (missing = no rain recorded);
            # keep None for tmax to avoid false heat-day counts.
            rain_clean = [r if r is not None else 0.0 for r in rain]

            onset_doy = detect_onset(rain_clean, year)
            false_start = detect_false_start(rain_clean)
            dry_days = max_dry_spell(rain_clean, onset_doy)
            heat_days = count_heat_days(tmax or [], onset_doy) if tmax else None

            risk = compute_risk(false_start, dry_days, heat_days)
            advice = sowing_advice(risk, onset_doy, false_start)

            onset_date_str = None
            if onset_doy:
                try:
                    onset_date_str = date.fromordinal(
                        date(year, 1, 1).toordinal() + onset_doy - 1
                    ).isoformat()
                except Exception:
                    pass

            features.append({
                "type": "Feature",
                "geometry": _cell_polygon(lat, lon),
                "properties": {
                    "cell_id": f"R{cell_id:04d}",
                    "region": _region(lat),
                    "department": _department(lat, lon),
                    "year": year,
                    "season_onset_date": onset_doy,
                    "season_onset_date_str": onset_date_str,
                    "false_start": false_start,
                    "dry_spell_days": dry_days,
                    "heat_days": heat_days,
                    "risk_score": risk["score"],
                    "risk_class": risk["class"],
                    "sowing_advice": advice,
                    "data_source": "NASA POWER v9 (PRECTOTCORR, T2M_MAX)",
                    "data_period": str(year),
                    "spatial_resolution": "0.5 deg (~55 km)",
                    "confidence": "real",
                },
            })

            # Respect NASA POWER rate limits
            time.sleep(0.3)

    return {
        "type": "FeatureCollection",
        "metadata": {
            "title": f"MaisMap Real Dataset {year}",
            "description": "NASA POWER historical data — real measurements",
            "year": year,
            "source": "NASA POWER v9",
            "crs": "EPSG:4326",
        },
        "features": features,
    }


def main():
    parser = argparse.ArgumentParser(description="MaisMap NASA POWER pipeline")
    parser.add_argument("--year", type=int, action="append", required=True,
                        help="Year(s) to process (repeat for multiple)")
    args = parser.parse_args()

    os.makedirs(DATA_PROCESSED_PATH, exist_ok=True)

    for year in args.year:
        logger.info("=== Processing year %d ===", year)
        geojson = process_year(year)
        out_path = os.path.join(DATA_PROCESSED_PATH, f"grid_{year}.geojson")
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(geojson, f, ensure_ascii=False, indent=2)
        logger.info("Saved %d features -> %s", len(geojson["features"]), out_path)


if __name__ == "__main__":
    main()
