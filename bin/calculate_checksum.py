import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

from checksum_function import calculate_sha256


'''
- opens the downloaded raw data file
- accepts the corresponding dataset ID
- computes SHA-256 hash value
- documents data accession and checksum as metadata
'''


def main():

    parser = argparse.ArgumentParser(
        description="Calculate SHA-256 checksum and save dataset metadata."
    )

    parser.add_argument(
        "input_file",
        type=Path,
        help="Path to the downloaded dataset."
    )

    parser.add_argument(
        "--dataset",
        required=True,
        help="Dataset identifier."
    )

    args = parser.parse_args()

    input_file = args.input_file

    if not input_file.is_file():
        raise FileNotFoundError(
            f"Dataset not found: {input_file}"
        )

    # Calculate checksum
    checksum = calculate_sha256(input_file)

    # Collect metadata
    metadata = {
        "dataset_id": args.dataset,
        "filename": input_file.name,
        "file_size_bytes": input_file.stat().st_size,
        "checksum": {
            "algorithm": "sha256",
            "value": checksum
        },
        "accession": {
            "download_date": datetime.now(
                timezone.utc
            ).isoformat(),
        }
    }

    # Save metadata
    output_file = Path(f"{args.dataset}_metadata.json")

    with open(output_file, "w", encoding="utf-8") as file:
        json.dump(metadata, file, indent=4)

    print(f"Checksum successfully calculated: {checksum}")
    print(f"Metadata saved to: {output_file}")


if __name__ == "__main__":
    main()
