import unittest
import pandas as pd
import numpy as np
from datetime import datetime
from pydantic import ValidationError
from data_schema_evolution_tracker.models import SchemaContract, ValidationResult
from data_schema_evolution_tracker.core import FingerprintEngine, DriftAnalyzer

class TestValidation(unittest.TestCase):
    def setUp(self):
        self.contract = SchemaContract(
            schema_id="test_schema",
            version=1,
            fields={"id": "int", "value": "float"}
        )
        self.engine = FingerprintEngine()
        self.analyzer = DriftAnalyzer()

    def test_schema_contract_creation(self):
        """Test valid SchemaContract instantiation."""
        contract = SchemaContract(schema_id="v1", version=1, fields={"a": "int"})
        self.assertEqual(contract.schema_id, "v1")
        self.assertEqual(contract.version, 1)

    def test_schema_contract_invalid_types(self):
        """Test Pydantic validation for missing required fields."""
        with self.assertRaises(ValidationError):
            SchemaContract(schema_id="v1")  # Missing version and fields

    def test_schema_contract_frozen(self):
        """Test that SchemaContract is immutable."""
        with self.assertRaises(Exception):
            self.contract.version = 2

    def test_fingerprint_engine_numeric(self):
        """Test fingerprint generation for numeric data."""
        df = pd.DataFrame({"val": [1.0, 2.0, 3.0]})
        fp = self.engine.generate_fingerprint(df)
        self.assertEqual(fp["val"]["type"], "numeric")
        self.assertEqual(fp["val"]["mean"], 2.0)

    def test_fingerprint_engine_categorical(self):
        """Test fingerprint generation for categorical data."""
        df = pd.DataFrame({"cat": ["a", "b", "a"]})
        fp = self.engine.generate_fingerprint(df)
        self.assertEqual(fp["cat"]["type"], "categorical")
        self.assertEqual(fp["cat"]["cardinality"], 2)

    def test_drift_analyzer_identical_distributions(self):
        """Test that identical distributions yield zero drift."""
        s1 = pd.Series([1.0, 2.0, 3.0])
        s2 = pd.Series([1.0, 2.0, 3.0])
        drift = self.analyzer.calculate_drift(s1, s2)
        self.assertEqual(drift, 0.0)

    def test_drift_analyzer_non_numeric_handling(self):
        """Test that non-numeric data returns 0.0 drift."""
        s1 = pd.Series(["a", "b"])
        s2 = pd.Series(["c", "d"])
        drift = self.analyzer.calculate_drift(s1, s2)
        self.assertEqual(drift, 0.0)

    def test_schema_validation_success(self):
        """Test schema validation with matching columns."""
        df = pd.DataFrame({"id": [1], "value": [1.1]})
        is_valid = self.analyzer.validate_schema(self.contract, df)
        self.assertTrue(is_valid)

    def test_schema_validation_failure(self):
        """Test schema validation with missing columns."""
        df = pd.DataFrame({"id": [1]})  # Missing 'value'
        is_valid = self.analyzer.validate_schema(self.contract, df)
        self.assertFalse(is_valid)

    def test_validation_result_model(self):
        """Test ValidationResult serialization and defaults."""
        res = ValidationResult(is_valid=True, drift_score=0.05, message="OK")
        self.assertTrue(res.is_valid)
        self.assertEqual(res.drift_score, 0.05)
        self.assertIsInstance(res.timestamp, datetime)
        self.assertIsNotNone(res.request_id)

if __name__ == "__main__":
    unittest.main()