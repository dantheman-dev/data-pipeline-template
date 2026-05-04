"""Pytest test suite for the data-pipeline-template package."""

import os
import textwrap

import pandas as pd
import pytest

from data_pipeline.cleaner import handle_missing_values, normalize_column_names
from data_pipeline.loader import load_csv
from data_pipeline.pipeline import run_pipeline
from data_pipeline.validator import validate_columns, validate_types


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def sample_csv(tmp_path):
    """Write a small sample CSV to a temp file and return its path."""
    content = textwrap.dedent(
        """\
        First Name,Last Name,Age,Email,Score
        Alice,Smith,30,alice@example.com,95.5
        Bob,Jones,,bob@example.com,87.0
        Charlie,Brown,25,charlie@example.com,
        """
    )
    p = tmp_path / "sample.csv"
    p.write_text(content)
    return str(p)


@pytest.fixture
def messy_df():
    """A DataFrame with messy column names and missing values."""
    return pd.DataFrame(
        {
            "First Name": ["Alice", "Bob", None],
            "Last Name": ["Smith", None, "Brown"],
            "Age": [30, None, 25],
            "Score": [95.5, 87.0, None],
        }
    )


# ---------------------------------------------------------------------------
# loader
# ---------------------------------------------------------------------------


class TestLoadCsv:
    def test_loads_sample_file(self, sample_csv):
        df = load_csv(sample_csv)
        assert isinstance(df, pd.DataFrame)
        assert len(df) == 3

    def test_columns_preserved(self, sample_csv):
        df = load_csv(sample_csv)
        assert list(df.columns) == ["First Name", "Last Name", "Age", "Email", "Score"]

    def test_file_not_found(self):
        with pytest.raises(FileNotFoundError, match="not found"):
            load_csv("/nonexistent/path/file.csv")

    def test_empty_file_raises(self, tmp_path):
        p = tmp_path / "empty.csv"
        p.write_text("")
        with pytest.raises(ValueError, match="empty"):
            load_csv(str(p))

    def test_header_only_raises(self, tmp_path):
        """A file with only a header row and no data rows should raise ValueError."""
        p = tmp_path / "header_only.csv"
        p.write_text("col1,col2,col3\n")
        with pytest.raises(ValueError, match="no data rows"):
            load_csv(str(p))


# ---------------------------------------------------------------------------
# validator
# ---------------------------------------------------------------------------


class TestValidateColumns:
    def test_all_required_present(self, messy_df):
        # Should not raise.
        validate_columns(messy_df, ["First Name", "Age"])

    def test_case_insensitive(self, messy_df):
        validate_columns(messy_df, ["first name", "SCORE"])

    def test_missing_column_raises(self, messy_df):
        with pytest.raises(ValueError, match="Missing required column"):
            validate_columns(messy_df, ["First Name", "Salary"])

    def test_empty_required_list(self, messy_df):
        validate_columns(messy_df, [])  # Should not raise.

    def test_multiple_missing_columns(self, messy_df):
        with pytest.raises(ValueError) as exc_info:
            validate_columns(messy_df, ["Salary", "Department"])
        assert "Salary" in str(exc_info.value) or "Department" in str(exc_info.value)


class TestValidateTypes:
    def test_valid_numeric_column(self):
        df = pd.DataFrame({"age": [1, 2, 3], "score": [1.0, 2.0, 3.0]})
        warnings = validate_types(df, {"age": "int", "score": "float"})
        assert warnings == []

    def test_non_numeric_warns(self):
        df = pd.DataFrame({"age": ["thirty", "25", "40"]})
        warnings = validate_types(df, {"age": "int"})
        assert len(warnings) == 1
        assert "age" in warnings[0]

    def test_missing_column_skipped(self):
        df = pd.DataFrame({"name": ["Alice"]})
        warnings = validate_types(df, {"nonexistent": "int"})
        assert warnings == []

    def test_unknown_type_warns(self):
        df = pd.DataFrame({"col": [1, 2]})
        warnings = validate_types(df, {"col": "datetime"})
        assert any("Unknown type" in w for w in warnings)

    def test_bool_column_valid(self):
        df = pd.DataFrame({"active": ["true", "false", "1", "0"]})
        warnings = validate_types(df, {"active": "bool"})
        assert warnings == []

    def test_bool_column_invalid(self):
        df = pd.DataFrame({"active": ["yes_sir", "nope"]})
        warnings = validate_types(df, {"active": "bool"})
        assert any("active" in w for w in warnings)


# ---------------------------------------------------------------------------
# cleaner – normalize_column_names
# ---------------------------------------------------------------------------


class TestNormalizeColumnNames:
    def test_lowercase(self):
        df = pd.DataFrame(columns=["Name", "AGE"])
        result = normalize_column_names(df)
        assert list(result.columns) == ["name", "age"]

    def test_spaces_to_underscores(self):
        df = pd.DataFrame(columns=["First Name", "Last Name"])
        result = normalize_column_names(df)
        assert list(result.columns) == ["first_name", "last_name"]

    def test_camel_case(self):
        df = pd.DataFrame(columns=["firstName", "lastName"])
        result = normalize_column_names(df)
        assert list(result.columns) == ["first_name", "last_name"]

    def test_hyphens_to_underscores(self):
        df = pd.DataFrame(columns=["first-name", "last-name"])
        result = normalize_column_names(df)
        assert list(result.columns) == ["first_name", "last_name"]

    def test_preserves_data(self, messy_df):
        result = normalize_column_names(messy_df)
        assert len(result) == len(messy_df)
        # Data values must be identical after column-name normalization.
        assert list(result["first_name"]) == list(messy_df["First Name"])

    def test_does_not_mutate_original(self):
        df = pd.DataFrame(columns=["First Name"])
        _ = normalize_column_names(df)
        assert list(df.columns) == ["First Name"]


# ---------------------------------------------------------------------------
# cleaner – handle_missing_values
# ---------------------------------------------------------------------------


class TestHandleMissingValues:
    def test_drop_removes_rows_with_nan(self, messy_df):
        result = handle_missing_values(messy_df, strategy="drop")
        assert result.isna().sum().sum() == 0
        assert len(result) < len(messy_df)

    def test_fill_default_numeric(self):
        df = pd.DataFrame({"age": [1.0, None, 3.0]})
        result = handle_missing_values(df, strategy="fill_default")
        assert result["age"].isna().sum() == 0
        assert result["age"].iloc[1] == 0

    def test_fill_default_string(self):
        df = pd.DataFrame({"name": ["Alice", None, "Charlie"]})
        result = handle_missing_values(df, strategy="fill_default")
        assert result["name"].iloc[1] == ""

    def test_fill_with_explicit_values(self):
        df = pd.DataFrame({"age": [1.0, None], "name": ["Alice", None]})
        result = handle_missing_values(
            df, strategy="fill", fill_values={"age": 99, "name": "Unknown"}
        )
        assert result["age"].iloc[1] == 99
        assert result["name"].iloc[1] == "Unknown"

    def test_invalid_strategy_raises(self, messy_df):
        with pytest.raises(ValueError, match="Unknown missing-value strategy"):
            handle_missing_values(messy_df, strategy="invalid")

    def test_does_not_mutate_original(self, messy_df):
        original_na_count = messy_df.isna().sum().sum()
        handle_missing_values(messy_df, strategy="drop")
        assert messy_df.isna().sum().sum() == original_na_count


# ---------------------------------------------------------------------------
# pipeline (integration)
# ---------------------------------------------------------------------------


class TestRunPipeline:
    def test_end_to_end_drop(self, sample_csv, tmp_path):
        output = str(tmp_path / "cleaned.csv")
        df = run_pipeline(sample_csv, output, missing_strategy="drop")
        assert os.path.exists(output)
        assert df.isna().sum().sum() == 0
        # Columns should be normalised
        assert "first_name" in df.columns

    def test_end_to_end_fill_default(self, sample_csv, tmp_path):
        output = str(tmp_path / "cleaned.csv")
        df = run_pipeline(sample_csv, output, missing_strategy="fill_default")
        assert os.path.exists(output)
        assert df.isna().sum().sum() == 0

    def test_required_columns_pass(self, sample_csv, tmp_path):
        output = str(tmp_path / "cleaned.csv")
        # Should not raise.
        run_pipeline(sample_csv, output, required_columns=["First Name", "Score"])

    def test_required_columns_missing_raises(self, sample_csv, tmp_path):
        output = str(tmp_path / "cleaned.csv")
        with pytest.raises(ValueError, match="Missing required column"):
            run_pipeline(sample_csv, output, required_columns=["Salary"])

    def test_output_is_valid_csv(self, sample_csv, tmp_path):
        output = str(tmp_path / "cleaned.csv")
        run_pipeline(sample_csv, output)
        loaded = pd.read_csv(output)
        assert isinstance(loaded, pd.DataFrame)
        assert len(loaded) > 0

    def test_type_warnings_emitted(self, tmp_path, capsys):
        csv_path = str(tmp_path / "bad_types.csv")
        pd.DataFrame({"Name": ["Alice"], "Age": ["not_a_number"]}).to_csv(csv_path, index=False)
        output = str(tmp_path / "out.csv")
        run_pipeline(csv_path, output, column_types={"age": "int"})
        captured = capsys.readouterr()
        assert "[WARNING]" in captured.out
