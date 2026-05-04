"""Clean a DataFrame: normalise column names and handle missing values."""

import re
from typing import Dict, Optional

import pandas as pd


def normalize_column_names(df: pd.DataFrame) -> pd.DataFrame:
    """Return a copy of *df* with column names converted to lowercase snake_case.

    Transformation steps:
    1. Strip surrounding whitespace.
    2. Replace spaces and hyphens with underscores.
    3. Insert an underscore before each uppercase letter that follows a
       lowercase letter (CamelCase → camel_case).
    4. Collapse consecutive underscores into one.
    5. Convert everything to lowercase.

    Args:
        df: Input DataFrame.

    Returns:
        A new DataFrame with normalised column names.
    """
    df = df.copy()

    def _to_snake(name: str) -> str:
        name = name.strip()
        # Replace spaces and hyphens with underscores.
        name = re.sub(r"[\s\-]+", "_", name)
        # CamelCase → snake_case
        name = re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", name)
        # Collapse multiple underscores.
        name = re.sub(r"_+", "_", name)
        return name.lower()

    df.columns = [_to_snake(c) for c in df.columns]
    return df


def handle_missing_values(
    df: pd.DataFrame,
    strategy: str = "drop",
    fill_values: Optional[Dict[str, object]] = None,
) -> pd.DataFrame:
    """Handle missing values in *df*.

    Args:
        df: Input DataFrame.
        strategy: One of:
            - ``"drop"``  — drop any row that contains at least one NaN.
            - ``"fill"``  — fill NaNs using *fill_values*; columns not present
              in *fill_values* are left unchanged.
            - ``"fill_default"`` — fill NaNs with sensible per-column defaults:
              numeric columns → ``0``, string/object columns → ``""``.
        fill_values: Explicit per-column fill values used when
            *strategy* is ``"fill"``.  Ignored for other strategies.

    Returns:
        A new DataFrame with missing values handled according to *strategy*.

    Raises:
        ValueError: If *strategy* is not one of the recognised values.
    """
    df = df.copy()

    if strategy == "drop":
        df = df.dropna()

    elif strategy == "fill":
        if fill_values:
            df = df.fillna(value=fill_values)

    elif strategy == "fill_default":
        defaults: Dict[str, object] = {}
        for col in df.columns:
            if pd.api.types.is_numeric_dtype(df[col]):
                defaults[col] = 0
            else:
                defaults[col] = ""
        df = df.fillna(value=defaults)

    else:
        raise ValueError(
            f"Unknown missing-value strategy '{strategy}'. "
            "Choose from: 'drop', 'fill', 'fill_default'."
        )

    return df
