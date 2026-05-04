import pandas as pd
import re

REQUIRED_COLUMNS = ["item_id", "value", "cost"]

def load_data(path: str) -> pd.DataFrame:
    df = pd.read_csv(path)
    df.columns = normalize_columns(df.columns)
    validate_columns(df)
    return df

def normalize_columns(columns):
    def to_snake(s):
        s = s.strip().lower()
        s = re.sub(r"[^\w]+", "_", s)
        s = re.sub(r"_+", "_", s).strip("_")
        return s
    return [to_snake(c) for c in columns]

def validate_columns(df: pd.DataFrame):
    missing = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")

def handle_missing(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df = df.dropna(subset=REQUIRED_COLUMNS)
    return df

def process(input_path: str, output_path: str):
    df = load_data(input_path)
    df = handle_missing(df)
    df.to_csv(output_path, index=False)
    print(f"Clean data saved to {output_path}")

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Data Pipeline Template CLI")
    parser.add_argument("input", help="Input CSV path")
    parser.add_argument("output", help="Output CSV path")

    args = parser.parse_args()
    process(args.input, args.output)
