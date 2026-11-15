"""
MaïsMap automated test suite — 35 tests.
Run: .venv/Scripts/python.exe -m pytest tests/ -v
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import unittest
from src.analysis.onset import detect_onset
from src.analysis.false_start import detect_false_start
from src.analysis.dry_spell import max_dry_spell
from src.analysis.heat_stress import count_heat_days
from src.analysis.risk_model import compute_risk, sowing_advice
from src.analysis.trends import compute_trends
from src.data.data_loader import load_dataset, get_available_years
from src.data.validator import validate_geojson
from src.geospatial.grid import generate_grid_cells, validate_grid_coverage


# ── Helpers ───────────────────────────────────────────────────────────────────
def _flat(n=365, v=0.0):
    return [v] * n

def _inject(series, start, length, amount):
    s = list(series)
    for i in range(start, min(start + length, len(s))):
        s[i] = amount
    return s

def _make_feature(cell_id="C001", year=2022, risk_class="LOW", risk_score=20.0,
                  lat=8.0, lon=13.0, false_start=False, dry_days=5, heat_days=3,
                  data_source="SYNTHETIC"):
    return {
        "type": "Feature",
        "geometry": {
            "type": "Polygon",
            "coordinates": [[[lon, lat], [lon+0.5, lat], [lon+0.5, lat+0.5],
                              [lon, lat+0.5], [lon, lat]]]
        },
        "properties": {
            "cell_id": cell_id, "region": "Nord", "year": year,
            "risk_class": risk_class, "risk_score": risk_score,
            "false_start": false_start, "dry_spell_days": dry_days,
            "heat_days": heat_days, "season_onset_date": 105,
            "data_source": data_source, "confidence": "demo",
        }
    }


# ── Onset ─────────────────────────────────────────────────────────────────────
class TestOnset(unittest.TestCase):

    def test_clear_onset(self):
        rain = _inject(_flat(), 99, 3, 8.0)
        rain = _inject(rain, 102, 30, 3.0)
        self.assertEqual(detect_onset(rain, 2020), 100)

    def test_no_onset_dry_year(self):
        self.assertIsNone(detect_onset(_flat(), 2020))

    def test_onset_invalidated_by_dry_spell(self):
        rain = _inject(_flat(), 99, 3, 8.0)
        self.assertIsNone(detect_onset(rain, 2020))

    def test_onset_before_april_ignored(self):
        rain = _inject(_flat(), 0, 10, 10.0)
        rain = _inject(rain, 10, 30, 3.0)
        self.assertIsNone(detect_onset(rain, 2020))

    def test_onset_returns_1based_doy(self):
        rain = _inject(_flat(), 99, 3, 8.0)
        rain = _inject(rain, 102, 30, 3.0)
        onset = detect_onset(rain, 2020)
        self.assertGreaterEqual(onset, 1)
        self.assertLessEqual(onset, 365)


# ── False start ───────────────────────────────────────────────────────────────
class TestFalseStart(unittest.TestCase):

    def test_false_start_detected(self):
        rain = _inject(_flat(), 99, 3, 8.0)
        self.assertTrue(detect_false_start(rain))

    def test_no_false_start_stable_rain(self):
        rain = _inject(_flat(), 99, 3, 8.0)
        rain = _inject(rain, 102, 30, 3.0)
        self.assertFalse(detect_false_start(rain))

    def test_no_trigger_no_false_start(self):
        self.assertFalse(detect_false_start(_flat()))


# ── Dry spell ─────────────────────────────────────────────────────────────────
class TestDrySpell(unittest.TestCase):

    def test_max_dry_spell_basic(self):
        rain = _inject(_flat(365, 3.0), 104, 14, 0.0)
        self.assertEqual(max_dry_spell(rain, 100), 14)

    def test_no_dry_spell(self):
        self.assertEqual(max_dry_spell(_flat(365, 5.0), 100), 0)

    def test_missing_onset_uses_default(self):
        result = max_dry_spell(_flat(), None)
        self.assertGreaterEqual(result, 0)


# ── Heat stress ───────────────────────────────────────────────────────────────
class TestHeatStress(unittest.TestCase):

    def test_heat_days_counted(self):
        tmax = [30.0] * 365
        for i in range(99, 114):
            tmax[i] = 36.0
        self.assertEqual(count_heat_days(tmax, 100), 15)

    def test_no_heat_days(self):
        self.assertEqual(count_heat_days([28.0] * 365, 100), 0)

    def test_none_values_skipped(self):
        self.assertEqual(count_heat_days([None] * 365, 100), 0)


# ── Risk model ────────────────────────────────────────────────────────────────
class TestRiskModel(unittest.TestCase):

    def test_low_risk(self):
        r = compute_risk(False, 3, 2)
        self.assertEqual(r["class"], "LOW")
        self.assertLessEqual(r["score"], 33)

    def test_high_risk(self):
        r = compute_risk(True, 20, 25)
        self.assertEqual(r["class"], "HIGH")
        self.assertGreater(r["score"], 66)

    def test_missing_data_handled(self):
        r = compute_risk(False, None, None)
        self.assertIn(r["class"], ["LOW", "MEDIUM", "HIGH"])

    def test_score_range(self):
        for fs in [True, False]:
            for ds in [0, 10, 20]:
                for ht in [0, 15, 30]:
                    r = compute_risk(fs, ds, ht)
                    self.assertGreaterEqual(r["score"], 0)
                    self.assertLessEqual(r["score"], 100)

    def test_sowing_advice_false_start(self):
        r = compute_risk(True, 15, 10)
        self.assertIn("faux", sowing_advice(r, 105, True).lower())

    def test_sowing_advice_no_onset(self):
        r = compute_risk(False, 5, 3)
        self.assertIn("aucun", sowing_advice(r, None, False).lower())

    def test_components_present(self):
        r = compute_risk(True, 12, 8)
        self.assertIn("false_start_score", r["components"])
        self.assertIn("dry_spell_score", r["components"])
        self.assertIn("heat_score", r["components"])


# ── Trends ────────────────────────────────────────────────────────────────────
class TestTrends(unittest.TestCase):

    def test_trends_basic(self):
        data = [
            {"year": 2020, "season_onset_date": 100, "false_start": True,
             "dry_spell_days": 12, "heat_days": 15, "risk_score": 70, "risk_class": "HIGH"},
            {"year": 2021, "season_onset_date": 110, "false_start": False,
             "dry_spell_days": 6, "heat_days": 8, "risk_score": 30, "risk_class": "LOW"},
        ]
        t = compute_trends(data)
        self.assertEqual(t["years_analyzed"], 2)
        self.assertEqual(t["false_start_frequency"], 0.5)
        self.assertEqual(t["mean_onset_doy"], 105)

    def test_trends_empty(self):
        t = compute_trends([])
        self.assertEqual(t["years_analyzed"], 0)
        self.assertIsNone(t["false_start_frequency"])


# ── Data loader ───────────────────────────────────────────────────────────────
class TestDataLoader(unittest.TestCase):

    def test_available_years(self):
        years = get_available_years(use_demo=True)
        self.assertIsInstance(years, list)
        self.assertGreater(len(years), 0)

    def test_load_valid_year(self):
        years = get_available_years(use_demo=True)
        data, is_demo = load_dataset(years[0], use_demo=True)
        self.assertIsNotNone(data)
        self.assertTrue(is_demo)
        self.assertGreater(len(data["features"]), 0)

    def test_load_invalid_year(self):
        data, _ = load_dataset(1800, use_demo=True)
        if data:
            self.assertEqual(len(data.get("features", [])), 0)

    def test_geojson_structure(self):
        years = get_available_years(use_demo=True)
        data, _ = load_dataset(years[0], use_demo=True)
        self.assertEqual(data["type"], "FeatureCollection")
        for f in data["features"]:
            self.assertEqual(f["type"], "Feature")
            self.assertIn("geometry", f)
            self.assertIn("properties", f)
            self.assertIn(f["properties"]["risk_class"], ["LOW", "MEDIUM", "HIGH"])

    def test_coordinate_order(self):
        years = get_available_years(use_demo=True)
        data, _ = load_dataset(years[0], use_demo=True)
        for f in data["features"]:
            for lon, lat in f["geometry"]["coordinates"][0]:
                self.assertGreater(lon, 10.0)
                self.assertLess(lat, 15.0)


# ── Validator ─────────────────────────────────────────────────────────────────
class TestValidator(unittest.TestCase):

    def test_valid_feature(self):
        gj = {"type": "FeatureCollection", "features": [_make_feature()]}
        r = validate_geojson(gj)
        self.assertEqual(r["valid"], 1)
        self.assertEqual(r["invalid"], 0)

    def test_missing_field_flagged(self):
        f = _make_feature()
        del f["properties"]["risk_class"]
        r = validate_geojson({"type": "FeatureCollection", "features": [f]})
        self.assertEqual(r["invalid"], 1)
        self.assertIn("risk_class", r["missing_fields"])

    def test_invalid_risk_class_flagged(self):
        f = _make_feature(risk_class="EXTREME")
        r = validate_geojson({"type": "FeatureCollection", "features": [f]})
        self.assertEqual(r["invalid"], 1)

    def test_duplicate_cell_id_flagged(self):
        f1 = _make_feature(cell_id="C001")
        f2 = _make_feature(cell_id="C001")
        r = validate_geojson({"type": "FeatureCollection", "features": [f1, f2]})
        self.assertGreater(len(r["duplicate_ids"]), 0)

    def test_synthetic_counted(self):
        gj = {"type": "FeatureCollection",
              "features": [_make_feature(data_source="SYNTHETIC — DEMO")]}
        r = validate_geojson(gj)
        self.assertEqual(r["synthetic_count"], 1)
        self.assertEqual(r["real_count"], 0)

    def test_empty_collection(self):
        r = validate_geojson({"type": "FeatureCollection", "features": []})
        self.assertEqual(r["total"], 0)
        self.assertEqual(r["valid"], 0)


# ── Geospatial grid ───────────────────────────────────────────────────────────
class TestGeospatialGrid(unittest.TestCase):

    def test_grid_cell_count(self):
        cells = generate_grid_cells()
        # 6 lon steps × 10 lat steps = 60
        self.assertEqual(len(cells), 60)

    def test_grid_cells_in_bbox(self):
        from config.settings import STUDY_BBOX, GRID_CELL_DEG
        cells = generate_grid_cells()
        for c in cells:
            self.assertGreaterEqual(c["lat"], STUDY_BBOX["lat_min"])
            self.assertLess(c["lat"], STUDY_BBOX["lat_max"])
            self.assertGreaterEqual(c["lon"], STUDY_BBOX["lon_min"])
            self.assertLess(c["lon"], STUDY_BBOX["lon_max"])

    def test_coverage_validation(self):
        years = get_available_years(use_demo=True)
        data, _ = load_dataset(years[0], use_demo=True)
        report = validate_grid_coverage(data)
        self.assertEqual(report["expected"], 60)
        self.assertEqual(report["found"], 60)
        self.assertEqual(len(report["missing"]), 0)


if __name__ == "__main__":
    unittest.main(verbosity=2)
