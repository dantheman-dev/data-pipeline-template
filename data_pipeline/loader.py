"""Load CSV data into a pandas DataFrame."""

import pandas as pd


def load_csv(path: str) -> pd.DataFrame:
    """Read a CSV file and return a DataFrame.

    Args:
        path: Path to the input CSV file.

    Returns:
        A pandas DataFrame containing the raw CSV data.

    Raises:
        FileNotFoundError: If the file does not exist.
        ValueError: If the file is empty or cannot be parsed.
    """
    try:
        df = pd.read_csv(path)
    except FileNotFoundError:
        raise FileNotFoundError(f"Input file not found: {path}")
    except pd.errors.EmptyDataError:
        raise ValueError(f"Input file is empty: {path}")
    except pd.errors.ParserError as exc:
        raise ValueError(f"Could not parse CSV file '{path}': {exc}") from exc

    if df.empty:
        raise ValueError(f"Input file contains no data rows: {path}")

    return df
