from checksum_function import calculate_sha256

import json
import argparse
import csv
import sys
from pathlib import Path


def validate_checksum(data_file, checksum_file):
    """Compare the current file hash with the stored hash."""

    actual_hash = calculate_sha256(data_file)

    with open(checksum_file, "r", encoding="utf-8") as file:
        metadata = json.load(file)

    expected_hash = metadata["checksum"]["value"].lower()

    if actual_hash != expected_hash:
        raise ValueError(
            "Checksum validation failed! "
            f"Expected: {expected_hash}, "
            f"Actual: {actual_hash}"
        )

    return actual_hash


def validate_tsv(data_file):
    """Validate basic TSV structure."""

    with open(
        data_file,
        "r",
        newline="",
        encoding="utf-8-sig"
    ) as file:

        reader = csv.reader(file, delimiter="\t")
        headers = next(reader, None)

        if not headers:
            raise ValueError("TSV file is empty.")

        if any(not header.strip() for header in headers):
            raise ValueError("TSV contains empty column names.")

        if len(headers) != len(set(headers)):
            raise ValueError("TSV contains duplicate column names.")

        row_count = 0

        for line_number, row in enumerate(reader, start=2):

            if len(row) != len(headers):
                raise ValueError(
                    f"Invalid number of columns in line {line_number}: "
                    f"expected {len(headers)}, got {len(row)}."
                )

            row_count += 1

        if row_count == 0:
            raise ValueError("TSV contains no data rows.")

    return row_count


def main():

    parser = argparse.ArgumentParser(
        description="Validate dataset integrity and TSV format."
    )

    parser.add_argument("--input", required=True)
    parser.add_argument("--checksum", required=True)

    args = parser.parse_args()

    data_file = Path(args.input)
    checksum_file = Path(args.checksum)

    if not data_file.is_file():
        raise FileNotFoundError(
            f"Dataset not found: {data_file}"
        )

    if not checksum_file.is_file():
        raise FileNotFoundError(
            f"Checksum file not found: {checksum_file}"
        )

    print("Starting input validation...")

    # 1. Check file integrity
    validate_checksum(data_file, checksum_file)
    print("Checksum validation successful.")

    # 2. Validate TSV structure
    row_count = validate_tsv(data_file)
    print("TSV validation successful.")

    print("Input validation completed successfully.")
    print(f"Rows: {row_count}")


if __name__ == "__main__":

    try:
        main()

    except Exception as error:
        print(f"ERROR: {error}", file=sys.stderr)
        sys.exit(1)