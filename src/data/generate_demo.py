"""
Generate synthetic demonstration GeoJSON for MaïsMap.

This script creates a realistic but SYNTHETIC dataset for Northern Cameroon.
It is NOT based on real NASA measurements.
Run once: python generate_demo.py
"""
import json, os, random, math
from datetime import date

random.seed(42)

# Grid: 0.5° cells covering Northern + Far North Cameroon
LON_MIN, LON_MAX = 13.0, 16.0
LAT_MIN, LAT_MAX = 7.5, 12.5
STEP = 0.5
YEARS = list(range(2010, 2024))  # 14 demo years

def _region(lat):
    if lat >= 10.5:
        return "Extrême-Nord"
    if lat >= 8.5:
        return "Nord"
    return "Adamaoua"



def _department(lat, lon):
    if lat >= 11.5:
        return "Logone-et-Chari" if lon >= 14.5 else "Mayo-Sava"
    if lat >= 10.5:
        return "Mayo-Kani" if lon >= 14.5 else "Diamaré"
    if lat >= 9.5:
        return "Bénoué" if lon >= 14.0 else "Mayo-Rey"
    return "Faro"


def _cell_polygon(lat, lon):
    """Return a GeoJSON Polygon for a 0.5° cell."""
    return {
        "type": "Polygon",
        "coordinates": [[
            [lon, lat], [lon + STEP, lat],
            [lon + STEP, lat + STEP], [lon, lat + STEP],
            [lon, lat]
        ]]
    }


def _simulate_year(lat, lon, year):
    """Simulate plausible agronomic indicators for one cell-year."""
    # Latitude gradient: drier further north
    lat_factor = (lat - LAT_MIN) / (LAT_MAX - LAT_MIN)  # 0 (south) → 1 (north)

    # Onset: earlier in south (~day 100), later in north (~day 145), ±15 days noise
    base_onset = 100 + int(lat_factor * 45)
    onset_doy = base_onset + random.randint(-15, 15)

    # False start: more frequent in north (30–60% probability)
    false_start_prob = 0.20 + lat_factor * 0.35
    # Occasional bad years
    if year in (2011, 2017, 2021):
        false_start_prob = min(false_start_prob + 0.20, 0.85)
    false_start = random.random() < false_start_prob

    # Dry spell: longer in north and in false-start years
    base_dry = 6 + int(lat_factor * 10)
    if false_start:
        base_dry += random.randint(5, 12)
    dry_spell_days = max(0, base_dry + random.randint(-3, 5))

    # Heat days: more in north
    base_heat = 5 + int(lat_factor * 20)
    heat_days = max(0, base_heat + random.randint(-5, 8))

    # Risk score
    fs_score = 100.0 if false_start else 0.0
    ds_score = min(dry_spell_days / 15.0 * 100.0, 100.0)
    ht_score = min(heat_days / 20.0 * 100.0, 100.0)
    score = round(0.40 * fs_score + 0.35 * ds_score + 0.25 * ht_score, 1)

    if score <= 33:
        risk_class = "LOW"
    elif score <= 66:
        risk_class = "MEDIUM"
    else:
        risk_class = "HIGH"

    # Onset date string
    try:
        onset_date = date(year, 1, 1).replace()
        onset_date = date.fromordinal(date(year, 1, 1).toordinal() + onset_doy - 1).isoformat()
    except Exception:
        onset_date = None

    # Sowing advice
    if false_start:
        advice = ("Faux départ détecté. Conditions suggèrent d'attendre des pluies "
                  "plus stables avant de semer.")
    elif risk_class == "HIGH":
        advice = "Risque élevé. Semis déconseillé sans suivi pluviométrique local."
    elif risk_class == "MEDIUM":
        advice = "Risque modéré. Surveiller les prévisions locales avant de semer."
    else:
        advice = (f"Conditions favorables. Semis possible autour du {onset_date}. "
                  "Confirmer avec les prévisions locales.")

    return {
        "onset_doy": onset_doy,
        "season_onset_date": onset_doy,
        "season_onset_date_str": onset_date,
        "false_start": false_start,
        "dry_spell_days": dry_spell_days,
        "heat_days": heat_days,
        "risk_score": score,
        "risk_class": risk_class,
        "sowing_advice": advice,
    }


def generate():
    features = []
    cell_id = 0
    lats = [round(LAT_MIN + i * STEP, 1) for i in range(int((LAT_MAX - LAT_MIN) / STEP))]
    lons = [round(LON_MIN + j * STEP, 1) for j in range(int((LON_MAX - LON_MIN) / STEP))]

    for year in YEARS:
        for lat in lats:
            for lon in lons:
                cell_id += 1
                sim = _simulate_year(lat, lon, year)
                features.append({
                    "type": "Feature",
                    "geometry": _cell_polygon(lat, lon),
                    "properties": {
                        "cell_id": f"C{cell_id:04d}",
                        "region": _region(lat),
                        "department": _department(lat, lon),
                        "year": year,
                        "season_onset_date": sim["season_onset_date"],
                        "season_onset_date_str": sim["season_onset_date_str"],
                        "false_start": sim["false_start"],
                        "dry_spell_days": sim["dry_spell_days"],
                        "heat_days": sim["heat_days"],
                        "risk_score": sim["risk_score"],
                        "risk_class": sim["risk_class"],
                        "sowing_advice": sim["sowing_advice"],
                        "data_source": "SYNTHETIC — DEMONSTRATION ONLY",
                        "data_period": f"{year}",
                        "spatial_resolution": "0.5 deg (~55 km)",
                        "confidence": "demo",
                    }
                })

    geojson = {
        "type": "FeatureCollection",
        "metadata": {
            "title": "MaïsMap Demo Dataset",
            "description": "SYNTHETIC DATA — NOT OFFICIAL NASA MEASUREMENTS",
            "years": YEARS,
            "cells_per_year": len(lats) * len(lons),
            "crs": "EPSG:4326",
        },
        "features": features,
    }

    out_path = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'demo', 'demo_grid.geojson')
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(geojson, f, ensure_ascii=False, indent=2)
    print(f"Generated {len(features)} features -> {out_path}")


if __name__ == "__main__":
    generate()
