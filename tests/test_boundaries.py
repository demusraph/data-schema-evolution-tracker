import unittest
import pandas as pd
import numpy as np
from data_schema_evolution_tracker.core import FingerprintEngine, DriftAnalyzer
from data_schema_evolution_tracker.models import SchemaContract

class TestBoundaries(unittest.TestCase):
    """Exhaustive boundary testing for schema evolution and drift detection."""

    def setUp(self):
        self.engine = FingerprintEngine()
        self.analyzer = DriftAnalyzer()

    def test_empty_dataframe_fingerprint(self):
        """Test fingerprinting an empty DataFrame."""
        df = pd.DataFrame({'a': []})
        fingerprint = self.engine.generate_fingerprint(df)
        self.assertEqual(fingerprint['a']['null_count'], 0)
        self.assertEqual(fingerprint['a']['type'], 'numeric')

    def test_single_element_drift(self):
        """Test drift calculation with single-element series."""
        s1 = pd.Series([1.0])
        s2 = pd.Series([1.0])
        drift = self.analyzer.calculate_drift(s1, s2)
        self.assertEqual(drift, 0.0)

    def test_identical_distribution_drift(self):
        """Test drift between identical distributions."""
        s1 = pd.Series([1, 2, 3, 4, 5])
        s2 = pd.Series([1, 2, 3, 4, 5])
        drift = self.analyzer.calculate_drift(s1, s2)
        self.assertEqual(drift, 0.0)

    def test_max_divergence_drift(self):
        """Test drift between completely disjoint distributions."""
        s1 = pd.Series([1, 2, 3])
        s2 = pd.Series([100, 200, 300])
        drift = self.analyzer.calculate_drift(s1, s2)
        self.assertEqual(drift, 1.0)

    def test_schema_validation_exact_match(self):
        """Test schema validation with exact field match."""
        contract = SchemaContract(schema_id="test", version=1, fields={"a": "int", "b": "str"})
        df = pd.DataFrame(columns=["a", "b"])
        self.assertTrue(self.analyzer.validate_schema(contract, df))

    def test_schema_validation_missing_fields(self):
        """Test schema validation failure when fields are missing."""
        contract = SchemaContract(schema_id="test", version=1, fields={"a": "int", "b": "str"})
        df = pd.DataFrame(columns=["a"])
        self.assertFalse(self.analyzer.validate_schema(contract, df))

    def test_schema_validation_extra_fields(self):
        """Test schema validation failure when extra fields are present."""
        contract = SchemaContract(schema_id="test", version=1, fields={"a": "int"})
        df = pd.DataFrame(columns=["a", "b"])
        self.assertFalse(self.analyzer.validate_schema(contract, df))

    def test_negative_value_drift(self):
        """Test drift calculation with negative values."""
        s1 = pd.Series([-10.0, -5.0, 0.0])
        s2 = pd.Series([-10.0, -5.0, 0.0])
        drift = self.analyzer.calculate_drift(s1, s2)
        self.assertEqual(drift, 0.0)

    def test_nan_handling_in_drift(self):
        """Test that NaNs are dropped during drift calculation."""
        s1 = pd.Series([1.0, 2.0, np.nan])
        s2 = pd.Series([1.0, 2.0])
        drift = self.analyzer.calculate_drift(s1, s2)
        self.assertEqual(drift, 0.0)

    def test_non_numeric_drift_boundary(self):
        """Test that non-numeric drift returns 0.0 as per implementation."""
        s1 = pd.Series(['a', 'b'])
        s2 = pd.Series(['a', 'c'])
        drift = self.analyzer.calculate_drift(s1, s2)
        self.assertEqual(drift, 0.0)

if __name__ == '__main__':
    unittest.main()