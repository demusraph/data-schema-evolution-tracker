import numpy as np
import pandas as pd
from scipy import stats
from typing import Dict, List, Any
from .models import SchemaContract

class FingerprintEngine:
    """Computes statistical fingerprints for Pandas DataFrames."""
    
    @staticmethod
    def generate_fingerprint(df: pd.DataFrame) -> Dict[str, Any]:
        fingerprint = {}
        for col in df.columns:
            series = df[col]
            if pd.api.types.is_numeric_dtype(series):
                fingerprint[col] = {
                    "type": "numeric",
                    "mean": float(series.mean()),
                    "std": float(series.std()),
                    "null_count": int(series.isnull().sum())
                }
            else:
                fingerprint[col] = {
                    "type": "categorical",
                    "cardinality": int(series.nunique()),
                    "null_count": int(series.isnull().sum())
                }
        return fingerprint

class DriftAnalyzer:
    """Performs Kolmogorov-Smirnov tests for distribution drift."""
    
    @staticmethod
    def calculate_drift(old_data: pd.Series, new_data: pd.Series) -> float:
        """Returns the KS statistic for two distributions."""
        if not pd.api.types.is_numeric_dtype(old_data) or not pd.api.types.is_numeric_dtype(new_data):
            return 0.0
        
        # Drop NaNs for KS test
        stat, _ = stats.ks_2samp(old_data.dropna(), new_data.dropna())
        return float(stat)

    def validate_schema(self, contract: SchemaContract, df: pd.DataFrame) -> bool:
        """Strict validation of schema structure."""
        current_fields = set(df.columns)
        contract_fields = set(contract.fields.keys())
        return current_fields == contract_fields