"""
Automated tests for MaïsMap analysis modules.
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
from src.data.data_loader import load_dataset, get_available_years


def _make_year(n=365, base=0.0):
    """Create a flat daily rainfall series."""
    return [base] * n


def _inject_rain(series, start, length, amount):
    """Inject rainfall into a series slice."""
    s = list(series)
    for i in range(start, min(start + length, len(s))):
        s[i] = amount
    return s


class TestOnset(unittest.TestCase):

    def test_clear_onset(self):
        """Three consecutive rainy days after April 1 with no following dry spell."""
        rain = _make_year(365, 0.0)
        # Inject 3 days of 8mm starting DOY 100 (index 99)
        rain = _inject_rain(rain, 99, 3, 8.0)
        # Keep it rainy for 30 days after
        rain = _inject_rain(rain, 102, 30, 3.0)
        onset = detect_onset(rain, 2020)
        self.assertIsNotNone(onset)
        self.assertEqual(onset, 100)

    def test_no_onset_dry_year(self):
        """No onset when the year is completely dry."""
        rain = _make_year(365, 0.0)
        self.assertIsNone(detect_onset(rain, 2020))

    def test_onset_invalidated_by_dry_spell(self):
        """Trigger followed by 10-day dry spell should not be detected as onset."""
        rain = _make_year(365, 0.0)
        rain = _inject_rain(rain, 99, 3, 8.0)
        # 10 dry days immediately after trigger — invalidates onset
        # (no rain injected after index 102)
        onset = detect_onset(rain, 2020)
        self.assertIsNone(onset)

    def test_onset_before_april_ignored(self):
        """Rain before April 1 (DOY 91) should not trigger onset."""
        rain = _make_year(365, 0.0)
        rain = _inject_rain(rain, 0, 10, 10.0)  # January rain
        rain = _inject_rain(rain, 10, 30, 3.0)
        self.assertIsNone(detect_onset(rain, 2020))


class TestFalseStart(unittest.TestCase):

    def test_false_start_detected(self):
        """Trigger followed by 12 dry days = false start."""
        rain = _make_year(365, 0.0)
        rain = _inject_rain(rain, 99, 3, 8.0)
        # 12 dry days after trigger (indices 102–113)
        onset = detect_false_start(rain)
        self.assertTrue(onset)

    def test_no_false_start_stable_rain(self):
        """Trigger followed by stable rain = no false start."""
        rain = _make_year(365, 0.0)
        rain = _inject_rain(rain, 99, 3, 8.0)
        rain = _inject_rain(rain, 102, 30, 3.0)
        self.assertFalse(detect_false_start(rain))

    def test_no_trigger_no_false_start(self):
        """No trigger = no false start."""
        rain = _make_year(365, 0.0)
        self.assertFalse(detect_false_start(rain))


class TestDrySpell(unittest.TestCase):

    def test_max_dry_spell_basic(self):
        rain = _make_year(365, 3.0)
        # Insert 14 dry days starting at onset+5
        onset = 100
        start = onset - 1 + 5
        for i in range(start, start + 14):
            rain[i] = 0.0
        result = max_dry_spell(rain, onset)
        self.assertEqual(result, 14)

    def test_no_dry_spell(self):
        rain = _make_year(365, 5.0)
        self.assertEqual(max_dry_spell(rain, 100), 0)

    def test_missing_onset(self):
        """With no onset, should still compute from default start."""
        rain = _make_year(365, 0.0)
        result = max_dry_spell(rain, None)
        self.assertGreater(result, 0)


class TestHeatStress(unittest.TestCase):

    def test_heat_days_counted(self):
        tmax = [30.0] * 365
        onset = 100
        # Set 15 days above threshold within season
        for i in range(onset - 1, onset - 1 + 15):
            tmax[i] = 36.0
        self.assertEqual(count_heat_days(tmax, onset), 15)

    def test_no_heat_days(self):
        tmax = [28.0] * 365
        self.assertEqual(count_heat_days(tmax, 100), 0)

    def test_none_values_skipped(self):
        tmax = [None] * 365
        self.assertEqual(count_heat_days(tmax, 100), 0)


class TestRiskModel(unittest.TestCase):

    def test_low_risk(self):
        result = compute_risk(False, 3, 2)
        self.assertEqual(result["class"], "LOW")
        self.assertLessEqual(result["score"], 33)

    def test_high_risk(self):
        result = compute_risk(True, 20, 25)
        self.assertEqual(result["class"], "HIGH")
        self.assertGreater(result["score"], 66)

    def test_medium_risk(self):
        result = compute_risk(False, 12, 12)
        self.assertIn(result["class"], ["MEDIUM", "HIGH"])

    def test_missing_data_handled(self):
        result = compute_risk(False, None, None)
        self.assertIn(result["class"], ["LOW", "MEDIUM", "HIGH"])
        self.assertIsNotNone(result["score"])

    def test_score_range(self):
        for fs in [True, False]:
            for ds in [0, 10, 20]:
                for ht in [0, 15, 30]:
                    r = compute_risk(fs, ds, ht)
                    self.assertGreaterEqual(r["score"], 0)
                    self.assertLessEqual(r["score"], 100)

    def test_sowing_advice_false_start(self):
        risk = compute_risk(True, 15, 10)
        advice = sowing_advice(risk, 105, True)
        self.assertIn("faux départ", advice.lower())

    def test_sowing_advice_no_onset(self):
        risk = compute_risk(False, 5, 3)
        advice = sowing_advice(risk, None, False)
        self.assertIn("aucun", advice.lower())


class TestDataLoader(unittest.TestCase):

    def test_available_years(self):
        years = get_available_years(use_demo=True)
        self.assertIsInstance(years, list)
        self.assertGreater(len(years), 0)
        self.assertTrue(all(isinstance(y, int) for y in years))

    def test_load_valid_year(self):
        years = get_available_years(use_demo=True)
        if years:
            data, is_demo = load_dataset(years[0], use_demo=True)
            self.assertIsNotNone(data)
            self.assertTrue(is_demo)
            self.assertIn("features", data)
            self.assertGreater(len(data["features"]), 0)

    def test_load_invalid_year(self):
        data, is_demo = load_dataset(1800, use_demo=True)
        # Should return None or empty features
        if data:
            self.assertEqual(len(data.get("features", [])), 0)

    def test_geojson_structure(self):
        years = get_available_years(use_demo=True)
        if years:
            data, _ = load_dataset(years[0], use_demo=True)
            self.assertEqual(data["type"], "FeatureCollection")
            for f in data["features"]:
                self.assertEqual(f["type"], "Feature")
                self.assertIn("geometry", f)
                self.assertIn("properties", f)
                props = f["properties"]
                self.assertIn("risk_class", props)
                self.assertIn(props["risk_class"], ["LOW", "MEDIUM", "HIGH"])

    def test_coordinate_order(self):
        """GeoJSON coordinates must be [longitude, latitude]."""
        years = get_available_years(use_demo=True)
        if years:
            data, _ = load_dataset(years[0], use_demo=True)
            for f in data["features"]:
                coords = f["geometry"]["coordinates"][0]
                for lon, lat in coords:
                    self.assertGreater(lon, 10.0, "Longitude should be > 10 for Cameroon")
                    self.assertLess(lat, 15.0, "Latitude should be < 15 for Cameroon")


if __name__ == "__main__":
    unittest.main(verbosity=2)
