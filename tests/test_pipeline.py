import pandas as pd
from src.pipeline import normalize_columns, handle_missing


def test_normalize_columns():
    cols = ["Item ID", "Value", "Cost"]
    result = normalize_columns(cols)
    assert result == ["item_id", "value", "cost"]


def test_handle_missing():
    df = pd.DataFrame({
        "item_id": ["A-1", "A-2"],
        "value": [100, None],
        "cost": [80, 90]
    })

    result = handle_missing(df)
    assert len(result) == 1
