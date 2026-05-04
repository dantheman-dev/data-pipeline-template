"""Orchestrate the full data pipeline: load → validate → clean → export."""

from typing import Dict, List, Optional

import pandas as pd

from .cleaner import handle_missing_values, normalize_column_names
from .loader import load_csv
from .validator import validate_columns, validate_types


def run_pipeline(
    input_path: str,
    output_path: str,
    required_columns: Optional[List[str]] = None,
    column_types: Optional[Dict[str, str]] = None,
    missing_strategy: str = "drop",
    fill_values: Optional[Dict[str, object]] = None,
) -> pd.DataFrame:
    """Run the complete data pipeline.

    Steps:
    1. Load CSV from *input_path*.
    2. Validate that all *required_columns* are present (before normalisation).
    3. Normalise column names to lowercase snake_case.
    4. Validate *column_types* and emit warnings for mismatches.
    5. Handle missing values according to *missing_strategy*.
    6. Write the cleaned DataFrame to *output_path*.

    Args:
        input_path: Path to the raw input CSV.
        output_path: Path where the cleaned CSV will be written.
        required_columns: Column names that must exist in the raw file.
        column_types: Mapping of (normalised) column name → expected type.
        missing_strategy: ``"drop"``, ``"fill"``, or ``"fill_default"``.
        fill_values: Per-column fill values used when strategy is ``"fill"``.

    Returns:
        The cleaned DataFrame (also written to *output_path*).
    """
    # 1. Load
    df = load_csv(input_path)

    # 2. Validate required columns (against raw names)
    if required_columns:
        validate_columns(df, required_columns)

    # 3. Normalise column names
    df = normalize_column_names(df)

    # 4. Type validation (warnings only — we don't abort the pipeline)
    if column_types:
        warnings = validate_types(df, column_types)
        for warning in warnings:
            print(f"[WARNING] {warning}")

    # 5. Handle missing values
    df = handle_missing_values(df, strategy=missing_strategy, fill_values=fill_values)

    # 6. Write output
    df.to_csv(output_path, index=False)
    print(f"[INFO] Cleaned data written to '{output_path}' ({len(df)} rows).")

    return df
