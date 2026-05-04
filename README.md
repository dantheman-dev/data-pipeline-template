# data-pipeline-template

Reusable Python template for loading, validating, and transforming structured data into clean, analysis-ready outputs.

## Features

- **Load** CSV input via pandas
- **Validate** required columns (case-insensitive) and expected types
- **Normalize** column names to `lowercase_snake_case`
- **Handle missing values** — drop rows, fill with explicit values, or fill with sensible defaults
- **Export** a cleaned CSV
- **Simple CLI** powered by `argparse`
- **Sample dataset** in `data/sample.csv`
- **pytest test suite** with 34 tests

## Project structure

```
data-pipeline-template/
├── data_pipeline/
│   ├── __init__.py
│   ├── loader.py      # load_csv()
│   ├── validator.py   # validate_columns(), validate_types()
│   ├── cleaner.py     # normalize_column_names(), handle_missing_values()
│   └── pipeline.py    # run_pipeline() — orchestrates all steps
├── tests/
│   └── test_pipeline.py
├── data/
│   └── sample.csv
├── cli.py
├── pyproject.toml
└── requirements.txt
```

## Installation

```bash
pip install -r requirements.txt
```

## Usage

### CLI

```bash
python cli.py --input data/sample.csv --output data/cleaned.csv
```

Full options:

```
usage: data-pipeline [-h] --input PATH --output PATH
                     [--required-columns [COL ...]]
                     [--missing-strategy {drop,fill,fill_default}]
                     [--fill-values [COL=VALUE ...]]

options:
  --input PATH                   Path to the input CSV file.
  --output PATH                  Path for the cleaned output CSV file.
  --required-columns [COL ...]   Column names that must be present.
  --missing-strategy             drop (default) | fill | fill_default
  --fill-values [COL=VALUE ...]  Per-column fill values for --missing-strategy=fill
```

**Examples**

```bash
# Drop rows with any missing value (default)
python cli.py --input data/sample.csv --output data/cleaned.csv

# Fill missing values with per-column defaults (0 / "")
python cli.py --input data/sample.csv --output data/cleaned.csv \
  --missing-strategy fill_default

# Fill specific columns with explicit values
python cli.py --input data/sample.csv --output data/cleaned.csv \
  --missing-strategy fill \
  --fill-values age=0 score=0.0 "last_name=Unknown"

# Require specific columns to be present
python cli.py --input data/sample.csv --output data/cleaned.csv \
  --required-columns "First Name" "Score"
```

### Python API

```python
from data_pipeline import run_pipeline

df = run_pipeline(
    input_path="data/sample.csv",
    output_path="data/cleaned.csv",
    required_columns=["First Name", "Score"],
    column_types={"age": "int", "score": "float"},
    missing_strategy="fill_default",
)
```

## Running tests

```bash
pytest
```

## Missing-value strategies

| Strategy       | Behaviour                                                         |
|----------------|-------------------------------------------------------------------|
| `drop`         | Remove any row that contains at least one `NaN` (default).        |
| `fill`         | Fill `NaN`s using explicit per-column values (`--fill-values`).   |
| `fill_default` | Fill numeric columns with `0`, string/object columns with `""`.   |
