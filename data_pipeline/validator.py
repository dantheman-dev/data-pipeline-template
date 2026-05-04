"""Validate that a DataFrame has the required columns and compatible types."""

from typing import Dict, List

import pandas as pd

# Mapping of type-name strings (used in config / CLI) to pandas-friendly checks.
_TYPE_CHECKS: Dict[str, type] = {
    "str": str,
    "string": str,
    "int": int,
    "integer": int,
    "float": float,
    "number": float,
    "bool": bool,
    "boolean": bool,
}


def validate_columns(df: pd.DataFrame, required_columns: List[str]) -> None:
    """Assert that all required columns are present in *df*.

    Column comparison is case-insensitive and ignores surrounding whitespace so
    that it works correctly both before and after column-name normalization.

    Args:
        df: DataFrame to validate.
        required_columns: List of column names that must be present.

    Raises:
        ValueError: If one or more required columns are missing.
    """
    if not required_columns:
        return

    # Normalise for comparison only – do not mutate the DataFrame here.
    normalised_df_cols = {c.strip().lower() for c in df.columns}
    missing = [
        col
        for col in required_columns
        if col.strip().lower() not in normalised_df_cols
    ]

    if missing:
        raise ValueError(
            f"Missing required column(s): {missing}. "
            f"Available columns: {list(df.columns)}"
        )


def validate_types(
    df: pd.DataFrame, column_types: Dict[str, str]
) -> List[str]:
    """Check that columns contain values compatible with the expected types.

    Rows that cannot be cast to the expected type are flagged; the caller
    decides what to do with them (drop, fill, raise, etc.).

    Args:
        df: DataFrame (after column-name normalisation) to validate.
        column_types: Mapping of *normalised* column name → expected type
            string (``"int"``, ``"float"``, ``"str"``, ``"bool"``).

    Returns:
        A list of warning strings describing any type mismatches found.
    """
    warnings: List[str] = []

    for col, type_str in column_types.items():
        if col not in df.columns:
            continue

        expected = _TYPE_CHECKS.get(type_str.lower())
        if expected is None:
            warnings.append(
                f"Unknown type '{type_str}' for column '{col}'; skipping type check."
            )
            continue

        if expected in (int, float):
            non_numeric = pd.to_numeric(df[col], errors="coerce").isna() & df[col].notna()
            bad_count = int(non_numeric.sum())
            if bad_count:
                warnings.append(
                    f"Column '{col}': {bad_count} value(s) cannot be cast to {type_str}."
                )
        elif expected is bool:
            valid_bools = {"true", "false", "1", "0", "yes", "no"}
            non_bool = df[col].dropna().astype(str).str.lower().isin(valid_bools)
            bad_count = int((~non_bool).sum())
            if bad_count:
                warnings.append(
                    f"Column '{col}': {bad_count} value(s) are not recognised boolean literals."
                )

    return warnings
