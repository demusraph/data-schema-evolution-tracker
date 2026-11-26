import unittest
import pandas as pd
import numpy as np
from datetime import datetime
from data_schema_evolution_tracker.models import SchemaContract, ValidationResult
from data_schema_evolution_tracker.core import FingerprintEngine, DriftAnalyzer

class TestCoreComponents(unittest.TestCase):
    def setUp(self):
        self.engine = FingerprintEngine()
        self.analyzer = DriftAnalyzer()
        self.sample_df = pd.DataFrame({
            "id": [1, 2, 3, 4],
            "value": [10.5, 20.0, 15.2, 12.8],
            "category": ["A", "B", "A", "C"]
        })

    def test_fingerprint_generation_keys(self):
        """Ensure fingerprint contains all expected columns."""
        fp = self.engine.generate_fingerprint(self.sample_df)
        self.assertIn("id", fp)
        self.assertIn("value", fp)
        self.assertIn("category", fp)

    def test_fingerprint_numeric_logic(self):
        """Verify numeric column statistics calculation."""
        fp = self.engine.generate_fingerprint(self.sample_df)
        self.assertEqual(fp["value"]["type"], "numeric")
        self.assertAlmostEqual(fp["value"]["mean"], 14.625)
        self.assertEqual(fp["value"]["null_count"], 0)

    def test_fingerprint_categorical_logic(self):
        """Verify categorical column cardinality calculation."""
        fp = self.engine.generate_fingerprint(self.sample_df)
        self.assertEqual(fp["category"]["type"], "categorical")
        self.assertEqual(fp["category"]["cardinality"], 3)

    def test_drift_analyzer_identical_distributions(self):
        """KS statistic for identical distributions should be near 0."""
        s1 = pd.Series([1, 2, 3, 4, 5])
        s2 = pd.Series([1, 2, 3, 4, 5])
        drift = self.analyzer.calculate_drift(s1, s2)
        self.assertEqual(drift, 0.0)

    def test_drift_analyzer_different_distributions(self):
        """KS statistic for distinct distributions should be > 0."""
        s1 = pd.Series([1, 1, 1, 1])
        s2 = pd.Series([10, 10, 10, 10])
        drift = self.analyzer.calculate_drift(s1, s2)
        self.assertGreater(drift, 0.0)

    def test_schema_validation_success(self):
        """Validate schema matching logic."""
        contract = SchemaContract(
            schema_id="test_schema",
            version=1,
            fields={"id": "int", "value": "float", "category": "str"}
        )
        is_valid = self.analyzer.validate_schema(contract, self.sample_df)
        self.assertTrue(is_valid)

    def test_schema_validation_failure(self):
        """Validate schema mismatch detection."""
        contract = SchemaContract(
            schema_id="test_schema",
            version=1,
            fields={"id": "int", "missing_col": "str"}
        )
        is_valid = self.analyzer.validate_schema(contract, self.sample_df)
        self.assertFalse(is_valid)

    def test_validation_result_model(self):
        """Ensure ValidationResult initializes correctly."""
        res = ValidationResult(is_valid=True, drift_score=0.05, message="OK")
        self.assertTrue(res.is_valid)
        self.assertEqual(res.drift_score, 0.05)
        self.assertIsInstance(res.timestamp, datetime)

    def test_fingerprint_null_handling(self):
        """Verify null counts are tracked correctly."""
        df_null = pd.DataFrame({"a": [1, None, 3]})
        fp = self.engine.generate_fingerprint(df_null)
        self.assertEqual(fp["a"]["null_count"], 1)

    def test_drift_non_numeric_input(self):
        """Ensure non-numeric drift returns 0.0."""
        s1 = pd.Series(["a", "b"])
        s2 = pd.Series(["c", "d"])
        drift = self.analyzer.calculate_drift(s1, s2)
        self.assertEqual(drift, 0.0)

if __name__ == "__main__":
    unittest.main()