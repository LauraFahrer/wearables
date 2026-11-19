## dependencies: install pandas and duckdb in your ve
## start the script via command line using the path to the respective parquet-file you want to inspect as parameter:
## python preprocessing/inspect_parquet.py <PATH_TO_PARQUET_FILE>

#!/usr/bin/env python3

"""
Inspect a single Parquet file using DuckDB.

Usage:
    python bin/inspect_parquet.py path/to/session_01.parquet
"""

import argparse
from pathlib import Path

import duckdb


def inspect_parquet(file_path: Path):
    """Inspect the structure and contents of one Parquet file."""

    con = duckdb.connect()

    parquet_path = str(file_path.resolve()).replace("'", "''")

    con.execute(
        f"CREATE VIEW data AS "
        f"SELECT * FROM read_parquet('{parquet_path}')"
    )

    row_count = con.execute(
        "SELECT COUNT(*) FROM data"
    ).fetchone()[0]

    schema = con.execute(
        "DESCRIBE data"
    ).fetchdf()

    columns = schema["column_name"].tolist()
    types = schema["column_type"].tolist()

    print("\n" + "=" * 60)
    print(f"FILE: {file_path.name}")
    print("=" * 60)

    # 1. Basic information
    print("\n--- BASIC INFORMATION ---")
    print(f"Shape: ({row_count}, {len(columns)})")
    print(f"Size:  {file_path.stat().st_size / 1024**2:.2f} MB")

    # 2. Column names and data types
    print("\n--- COLUMNS AND DATA TYPES ---")
    for name, dtype in zip(columns, types):
        print(f"{name:<20} {dtype}")

    # 3. First rows
    print("\n--- FIRST 5 ROWS ---")
    print(
        con.execute(
            "SELECT * FROM data LIMIT 5"
        ).fetchdf().to_string(index=False)
    )

    # 4. Last rows
    print("\n--- LAST 5 ROWS ---")
    print(
        con.execute(
            "SELECT * FROM data ORDER BY time DESC LIMIT 5"
        ).df().sort_values("time").to_string(index=False)
        if "time" in columns
        else print(
                con.execute(
                    "SELECT * FROM data ORDER BY time DESC LIMIT 5"
                ).fetchdf().sort_values("time").to_string(index=False)
            )
    )

    # 5. Descriptive statistics
    print("\n--- DESCRIPTIVE STATISTICS ---")
    print(
        con.execute(
            "SUMMARIZE data"
        ).fetchdf().to_string(index=False)
    )

    # 6. Missing values (NULL and NaN)
    print("\n--- MISSING VALUES ---")

    missing_expressions = []

    for name, dtype in zip(columns, types):
        col = f'"{name}"'

        if any(t in str(dtype).upper() for t in
               ["FLOAT", "DOUBLE", "REAL"]):
            condition = f"{col} IS NULL OR isnan({col})"
        else:
            condition = f"{col} IS NULL"

        missing_expressions.append(
            f"COUNT(*) FILTER (WHERE {condition}) AS \"{name}\""
        )

    query = "SELECT " + ", ".join(missing_expressions) + " FROM data"

    missing = con.execute(query).df().iloc[0]

    for name, count in missing.items():
        percentage = count / row_count * 100 if row_count else 0
        print(f"{name:<20} {count:>10} ({percentage:.2f}%)")

    # 7. Number of unique values
    print("\n--- DISTINCT VALUES ---")

    for name in columns:
        col = f'"{name}"'
        count = con.execute(
            f"SELECT COUNT(DISTINCT {col}) FROM data"
        ).fetchone()[0]

        print(f"{name:<20} {count}")

    # 8. Event distribution
    if "event" in columns:
        print("\n--- EVENT DISTRIBUTION ---")

        events = con.execute("""
            SELECT
                event,
                COUNT(*) AS count
            FROM data
            GROUP BY event
            ORDER BY count DESC
        """).df()

        print(events.to_string(index=False))

    # 9. Time information and sampling frequency
    if "time" in columns:
        print("\n--- TIME INFORMATION ---")

        time_info = con.execute("""
            SELECT
                MIN(time) AS start_time,
                MAX(time) AS end_time,
                MAX(time) - MIN(time) AS duration
            FROM data
        """).df()

        print(time_info.to_string(index=False))

        sampling = con.execute("""
            WITH time_diffs AS (
                SELECT
                    time - LAG(time) OVER (ORDER BY time) AS dt
                FROM data
            )
            SELECT
                MEDIAN(dt) AS median_interval,
                AVG(dt) AS mean_interval
            FROM time_diffs
            WHERE dt > 0
        """).df()

        print("\nSampling intervals (milliseconds):")
        print(sampling.to_string(index=False))

        median_interval = sampling["median_interval"].iloc[0]

        if median_interval and median_interval > 0:
            frequency = 1000 / median_interval
            print(f"\nEstimated sampling frequency: "
                  f"{frequency:.2f} Hz")

    print("\n" + "=" * 60)
    print("Inspection finished.")
    print("=" * 60)

    con.close()


def main():
    parser = argparse.ArgumentParser(
        description="Inspect a single Parquet file."
    )

    parser.add_argument(
        "file",
        type=Path,
        help="Path to the Parquet file"
    )

    args = parser.parse_args()

    if not args.file.is_file():
        parser.error(f"File not found: {args.file}")

    if args.file.suffix.lower() != ".parquet":
        parser.error("Input file must have a .parquet extension")

    inspect_parquet(args.file)


if __name__ == "__main__":
    main()
