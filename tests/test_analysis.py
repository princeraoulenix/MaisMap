"""
MaïsMap automated test suite — 45 tests.
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
from src.crop_rotation.engine import (
    score_strategies, climate_suitability_score,
    ROTATION_STRATEGIES, PRIORITY_DIMENSIONS
)


def _flat(n=365, v=0.0): return [v] * n
def _inject(s, start, length, amount):
    s = list(s)
    for i in range(start, min(start+length, len(s))): s[i] = amount
    return s
def _make_feature(cell_id="C001", year=2022, risk_class="LOW", risk_score=20.0,
                  lat=8.0, lon=13.0, false_start=False, dry_days=5, heat_days=3,
                  data_source="SYNTHETIC"):
    return {
        "type": "Feature",
        "geometry": {"type": "Polygon", "coordinates": [
            [[lon,lat],[lon+.5,lat],[lon+.5,lat+.5],[lon,lat+.5],[lon,lat]]]},
        "properties": {
            "cell_id": cell_id, "region": "Nord", "year": year,
            "risk_class": risk_class, "risk_score": risk_score,
            "false_start": false_start, "dry_spell_days": dry_days,
            "heat_days": heat_days, "season_onset_date": 105,
            "data_source": data_source, "confidence": "demo",
        }
    }


class TestOnset(unittest.TestCase):
    def test_clear_onset(self):
        rain = _inject(_inject(_flat(), 99, 3, 8.0), 102, 30, 3.0)
        self.assertEqual(detect_onset(rain, 2020), 100)
    def test_no_onset_dry_year(self):
        self.assertIsNone(detect_onset(_flat(), 2020))
    def test_onset_invalidated_by_dry_spell(self):
        self.assertIsNone(detect_onset(_inject(_flat(), 99, 3, 8.0), 2020))
    def test_onset_before_april_ignored(self):
        rain = _inject(_inject(_flat(), 0, 10, 10.0), 10, 30, 3.0)
        self.assertIsNone(detect_onset(rain, 2020))
    def test_onset_returns_1based_doy(self):
        rain = _inject(_inject(_flat(), 99, 3, 8.0), 102, 30, 3.0)
        onset = detect_onset(rain, 2020)
        self.assertGreaterEqual(onset, 1)
        self.assertLessEqual(onset, 365)


class TestFalseStart(unittest.TestCase):
    def test_false_start_detected(self):
        self.assertTrue(detect_false_start(_inject(_flat(), 99, 3, 8.0)))
    def test_no_false_start_stable_rain(self):
        rain = _inject(_inject(_flat(), 99, 3, 8.0), 102, 30, 3.0)
        self.assertFalse(detect_false_start(rain))
    def test_no_trigger_no_false_start(self):
        self.assertFalse(detect_false_start(_flat()))


class TestDrySpell(unittest.TestCase):
    def test_max_dry_spell_basic(self):
        rain = _inject(_flat(365, 3.0), 104, 14, 0.0)
        self.assertEqual(max_dry_spell(rain, 100), 14)
    def test_no_dry_spell(self):
        self.assertEqual(max_dry_spell(_flat(365, 5.0), 100), 0)
    def test_missing_onset_uses_default(self):
        self.assertGreaterEqual(max_dry_spell(_flat(), None), 0)


class TestHeatStress(unittest.TestCase):
    def test_heat_days_counted(self):
        tmax = [30.0]*365
        for i in range(99, 114): tmax[i] = 36.0
        self.assertEqual(count_heat_days(tmax, 100), 15)
    def test_no_heat_days(self):
        self.assertEqual(count_heat_days([28.0]*365, 100), 0)
    def test_none_values_skipped(self):
        self.assertEqual(count_heat_days([None]*365, 100), 0)


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
        self.assertIn(r["class"], ["LOW","MEDIUM","HIGH"])
    def test_score_range(self):
        for fs in [True,False]:
            for ds in [0,10,20]:
                for ht in [0,15,30]:
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


class TestTrends(unittest.TestCase):
    def test_trends_basic(self):
        data = [
            {"year":2020,"season_onset_date":100,"false_start":True,
             "dry_spell_days":12,"heat_days":15,"risk_score":70,"risk_class":"HIGH"},
            {"year":2021,"season_onset_date":110,"false_start":False,
             "dry_spell_days":6,"heat_days":8,"risk_score":30,"risk_class":"LOW"},
        ]
        t = compute_trends(data)
        self.assertEqual(t["years_analyzed"], 2)
        self.assertEqual(t["false_start_frequency"], 0.5)
    def test_trends_empty(self):
        t = compute_trends([])
        self.assertEqual(t["years_analyzed"], 0)
        self.assertIsNone(t["false_start_frequency"])


class TestDataLoader(unittest.TestCase):
    def test_real_years_available(self):
        years = get_available_years(use_demo=False)
        self.assertIsInstance(years, list)
        self.assertGreater(len(years), 0)
        self.assertIn(2022, years)

    def test_load_real_year(self):
        data, is_demo = load_dataset(2022, use_demo=False)
        self.assertIsNotNone(data)
        self.assertFalse(is_demo)
        self.assertEqual(len(data["features"]), 60)

    def test_real_data_source_label(self):
        data, _ = load_dataset(2022, use_demo=False)
        src = data["features"][0]["properties"]["data_source"]
        self.assertIn("NASA POWER", src)

    def test_real_data_has_rain(self):
        data, _ = load_dataset(2022, use_demo=False)
        rain = data["features"][0]["properties"].get("seasonal_rain_mm")
        self.assertIsNotNone(rain)
        self.assertGreater(rain, 0)

    def test_load_demo_fallback(self):
        data, is_demo = load_dataset(2015, use_demo=True)
        self.assertIsNotNone(data)
        self.assertTrue(is_demo)

    def test_geojson_structure(self):
        data, _ = load_dataset(2022, use_demo=False)
        self.assertEqual(data["type"], "FeatureCollection")
        for f in data["features"]:
            self.assertEqual(f["type"], "Feature")
            self.assertIn(f["properties"]["risk_class"], ["LOW","MEDIUM","HIGH"])

    def test_coordinate_order(self):
        data, _ = load_dataset(2022, use_demo=False)
        for f in data["features"]:
            for lon, lat in f["geometry"]["coordinates"][0]:
                self.assertGreater(lon, 10.0)
                self.assertLess(lat, 15.0)


class TestValidator(unittest.TestCase):
    def test_valid_feature(self):
        r = validate_geojson({"type":"FeatureCollection","features":[_make_feature()]})
        self.assertEqual(r["valid"], 1)
    def test_missing_field_flagged(self):
        f = _make_feature()
        del f["properties"]["risk_class"]
        r = validate_geojson({"type":"FeatureCollection","features":[f]})
        self.assertEqual(r["invalid"], 1)
    def test_invalid_risk_class_flagged(self):
        r = validate_geojson({"type":"FeatureCollection","features":[_make_feature(risk_class="EXTREME")]})
        self.assertEqual(r["invalid"], 1)
    def test_duplicate_cell_id_flagged(self):
        r = validate_geojson({"type":"FeatureCollection","features":[_make_feature("C001"),_make_feature("C001")]})
        self.assertGreater(len(r["duplicate_ids"]), 0)
    def test_synthetic_counted(self):
        r = validate_geojson({"type":"FeatureCollection","features":[_make_feature(data_source="SYNTHETIC")]})
        self.assertEqual(r["synthetic_count"], 1)
    def test_empty_collection(self):
        r = validate_geojson({"type":"FeatureCollection","features":[]})
        self.assertEqual(r["total"], 0)


class TestGeospatialGrid(unittest.TestCase):
    def test_grid_cell_count(self):
        self.assertEqual(len(generate_grid_cells()), 60)
    def test_grid_cells_in_bbox(self):
        from config.settings import STUDY_BBOX
        for c in generate_grid_cells():
            self.assertGreaterEqual(c["lat"], STUDY_BBOX["lat_min"])
            self.assertLess(c["lat"], STUDY_BBOX["lat_max"])
    def test_coverage_validation(self):
        data, _ = load_dataset(2022, use_demo=False)
        report = validate_grid_coverage(data)
        self.assertEqual(report["expected"], 60)
        self.assertEqual(report["found"], 60)


class TestCropRotation(unittest.TestCase):
    def test_three_strategies_defined(self):
        self.assertIn("A", ROTATION_STRATEGIES)
        self.assertIn("B", ROTATION_STRATEGIES)
        self.assertIn("C", ROTATION_STRATEGIES)

    def test_score_strategies_returns_three(self):
        scores = score_strategies({"water_conservation": 0.8, "soil_fertility": 0.5})
        self.assertEqual(len(scores), 3)
        for sid in ["A","B","C"]:
            self.assertIn(sid, scores)
            self.assertGreaterEqual(scores[sid], 0)
            self.assertLessEqual(scores[sid], 100)

    def test_equal_priorities_b_c_beat_a(self):
        equal = {k: 1.0 for k in PRIORITY_DIMENSIONS}
        scores = score_strategies(equal)
        self.assertGreater(scores["B"], scores["A"])
        self.assertGreater(scores["C"], scores["A"])

    def test_zero_priorities(self):
        scores = score_strategies({})
        self.assertEqual(scores["A"], 0.0)

    def test_climate_suitability_high_risk_penalizes_a(self):
        score_a = climate_suitability_score("HIGH", True, 18, "A")
        score_c = climate_suitability_score("HIGH", True, 18, "C")
        self.assertGreater(score_c["score"], score_a["score"])

    def test_climate_suitability_returns_label(self):
        result = climate_suitability_score("LOW", False, 5, "B")
        self.assertIn(result["label"], ["Favorable","Moderate","Challenging"])

    def test_strategy_has_required_fields(self):
        required = ["name","sequence","benefits","risks","confidence","data_gaps"]
        for sid, s in ROTATION_STRATEGIES.items():
            for field in required:
                self.assertIn(field, s, f"Strategy {sid} missing field {field}")


if __name__ == "__main__":
    unittest.main(verbosity=2)
