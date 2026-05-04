"""Command-line interface for the data pipeline."""

import argparse
import sys

from data_pipeline.pipeline import run_pipeline


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="data-pipeline",
        description=(
            "Load, validate, clean, and export CSV data.\n\n"
            "Example:\n"
            "  python cli.py --input data/sample.csv --output data/cleaned.csv"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument(
        "--input",
        required=True,
        metavar="PATH",
        help="Path to the input CSV file.",
    )
    parser.add_argument(
        "--output",
        required=True,
        metavar="PATH",
        help="Path for the cleaned output CSV file.",
    )
    parser.add_argument(
        "--required-columns",
        nargs="*",
        metavar="COL",
        default=[],
        help="One or more column names that must be present in the input file.",
    )
    parser.add_argument(
        "--missing-strategy",
        choices=["drop", "fill", "fill_default"],
        default="drop",
        help=(
            "How to handle missing values: "
            "'drop' removes rows with any NaN (default); "
            "'fill' uses --fill-values; "
            "'fill_default' fills numerics with 0 and strings with ''."
        ),
    )
    parser.add_argument(
        "--fill-values",
        nargs="*",
        metavar="COL=VALUE",
        default=[],
        help=(
            "Per-column fill values used when --missing-strategy=fill. "
            "Format: column_name=value (e.g. age=0 score=0.0 name=Unknown)."
        ),
    )
    return parser


def parse_fill_values(pairs: list) -> dict:
    """Convert a list of ``col=value`` strings into a dict."""
    result = {}
    for pair in pairs:
        if "=" not in pair:
            print(f"[WARNING] Ignoring malformed fill-value entry: '{pair}'", file=sys.stderr)
            continue
        col, _, value = pair.partition("=")
        # Attempt numeric coercion so that '0' becomes 0, '3.14' becomes 3.14, etc.
        try:
            value = int(value)
        except ValueError:
            try:
                value = float(value)
            except ValueError:
                pass  # keep as string
        result[col.strip()] = value
    return result


def main(argv=None) -> None:
    parser = build_parser()
    args = parser.parse_args(argv)

    fill_values = parse_fill_values(args.fill_values) if args.fill_values else None

    try:
        run_pipeline(
            input_path=args.input,
            output_path=args.output,
            required_columns=args.required_columns or None,
            missing_strategy=args.missing_strategy,
            fill_values=fill_values,
        )
    except (FileNotFoundError, ValueError) as exc:
        print(f"[ERROR] {exc}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
