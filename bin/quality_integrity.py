
#!/usr/bin/env python3

"""
Data Quality and Integrity Analysis

Checks:
    1. Missing values
    2. NaN / infinite values
    3. Duplicated entries
    4. Outliers
    5. Data types
    6. Unique values and constant features

Outputs:
    - quality_report.json
    - missing_values.csv
    - duplicated_rows.csv
    - outliers.csv
    - feature_summary.csv
"""

import argparse
import json
import logging
from pathlib import Path

import numpy as np
import pandas as pd


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

logger = logging.getLogger(__name__)


def load_dataset(file_path: Path) -> pd.DataFrame:

    logger.info("Loading dataset: %s", file_path)

    suffix = file_path.suffix.lower()

    if suffix == ".csv":
        df = pd.read_csv(file_path)
    elif suffix in [".tsv", ".txt"]:
        df = pd.read_csv(file_path, sep="\t")
    elif suffix in [".parquet"]:
        df = pd.read_parquet(file_path)
    elif suffix in [".xlsx", ".xls"]:
        df = pd.read_excel(file_path)
    else:
        raise ValueError(
            f"Unsupported file format: {suffix}"
        )

    logger.info(
        "Dataset loaded: %d rows, %d columns",
        df.shape[0],
        df.shape[1],
    )

    return df


def analyze_missing_values(df: pd.DataFrame) -> dict:

    logger.info("Analyzing missing values...")

    missing = df.isna().sum()

    missing_summary = pd.DataFrame({
        "missing_count": missing,
        "missing_percentage": (
            missing / len(df) * 100
        ).round(2),
    })

    missing_summary = missing_summary[
        missing_summary["missing_count"] > 0
    ].sort_values(
        "missing_count",
        ascending=False,
    )

    missing_summary.to_csv(
        "missing_values.csv"
    )

    # Detect infinite values in numerical columns
    numeric_df = df.select_dtypes(
        include=np.number
    )

    infinite = pd.DataFrame(
        np.isinf(numeric_df),
        columns=numeric_df.columns,
        index=numeric_df.index,
    ).sum()

    infinite_summary = infinite[
        infinite > 0
    ].to_dict()

    return {
        "total_missing_values": int(
            missing.sum()
        ),
        "columns_with_missing_values": int(
            (missing > 0).sum()
        ),
        "missing_values_per_column": {
            str(k): int(v)
            for k, v in missing.items()
        },
        "infinite_values_per_column": {
            str(k): int(v)
            for k, v in infinite_summary.items()
        },
    }


def analyze_duplicates(df: pd.DataFrame) -> dict:

    logger.info("Analyzing duplicated entries...")

    duplicate_mask = df.duplicated(
        keep="first"
    )

    duplicates = df[duplicate_mask]

    duplicates.to_csv(
        "duplicated_rows.csv",
        index=False,
    )

    return {
        "total_duplicated_rows": int(
            duplicate_mask.sum()
        ),
        "duplicate_percentage": round(
            duplicate_mask.sum() / len(df) * 100,
            2,
        ) if len(df) > 0 else 0,
    }


def analyze_outliers(df: pd.DataFrame) -> dict:

    logger.info("Detecting numerical outliers...")

    numeric_df = df.select_dtypes(
        include=np.number
    )

    outlier_records = []

    for column in numeric_df.columns:

        values = numeric_df[column].dropna()

        if len(values) < 4:
            continue

        q1 = values.quantile(0.25)
        q3 = values.quantile(0.75)

        iqr = q3 - q1

        if iqr == 0:
            continue

        lower_bound = q1 - 1.5 * iqr
        upper_bound = q3 + 1.5 * iqr

        outlier_mask = (
            (numeric_df[column] < lower_bound)
            | (numeric_df[column] > upper_bound)
        )

        outlier_indices = numeric_df.index[
            outlier_mask.fillna(False)
        ]

        for index in outlier_indices:

            outlier_records.append({
                "row_index": int(index),
                "feature": column,
                "value": float(
                    numeric_df.loc[index, column]
                ),
                "lower_bound": float(lower_bound),
                "upper_bound": float(upper_bound),
            })

    outliers = pd.DataFrame(
        outlier_records,
        columns=[
            "row_index",
            "feature",
            "value",
            "lower_bound",
            "upper_bound",
        ],
    )

    outliers.to_csv(
        "outliers.csv",
        index=False,
    )

    outlier_summary = (
        outliers.groupby("feature")
        .size()
        .to_dict()
        if not outliers.empty
        else {}
    )

    return {
        "total_outliers": len(outliers),
        "outliers_per_feature": {
            str(k): int(v)
            for k, v in outlier_summary.items()
        },
        "detection_method": "IQR (1.5 * IQR)",
    }


def analyze_data_types(df: pd.DataFrame) -> dict:

    logger.info("Analyzing data types...")

    dtype_summary = {
        str(column): str(dtype)
        for column, dtype in df.dtypes.items()
    }

    return {
        "data_types": dtype_summary,
        "numeric_columns": int(
            len(df.select_dtypes(include=np.number).columns)
        ),
        "categorical_columns": int(
            len(df.select_dtypes(include=["object", "category"]).columns)
        ),
        "datetime_columns": int(
            len(df.select_dtypes(include=["datetime"]).columns)
        ),
    }


def analyze_unique_values(df: pd.DataFrame) -> dict:

    logger.info("Analyzing unique values and constant features...")

    unique_counts = df.nunique(
        dropna=False
    )

    constant_features = unique_counts[
        unique_counts <= 1
    ].index.tolist()

    feature_summary = pd.DataFrame({
        "data_type": df.dtypes.astype(str),
        "unique_values": unique_counts,
        "is_constant": unique_counts <= 1,
    })

    feature_summary.to_csv(
        "feature_summary.csv"
    )

    return {
        "unique_values_per_feature": {
            str(k): int(v)
            for k, v in unique_counts.items()
        },
        "constant_features": [
            str(feature)
            for feature in constant_features
        ],
        "total_constant_features": len(
            constant_features
        ),
    }


def main():

    parser = argparse.ArgumentParser(
        description="Data Quality and Integrity Analysis"
    )

    parser.add_argument(
        "dataset",
        type=Path,
        help="Path to input dataset",
    )

    args = parser.parse_args()

    if not args.dataset.exists():
        parser.error(
            f"Dataset not found: {args.dataset}"
        )

    try:

        df = load_dataset(args.dataset)

        if df.empty:
            raise ValueError(
                "Dataset contains no rows."
            )

        logger.info("Starting quality analysis...")

        report = {
            "dataset": args.dataset.name,
            "dataset_shape": {
                "rows": int(df.shape[0]),
                "columns": int(df.shape[1]),
            },
            "missing_values": analyze_missing_values(df),
            "duplicates": analyze_duplicates(df),
            "outliers": analyze_outliers(df),
            "data_types": analyze_data_types(df),
            "unique_values": analyze_unique_values(df),
        }

        with open(
            "quality_report.json",
            "w",
            encoding="utf-8",
        ) as file:

            json.dump(
                report,
                file,
                indent=4,
                ensure_ascii=False,
            )

        logger.info(
            "Quality analysis completed successfully."
        )

        logger.info(
            "Report saved to quality_report.json"
        )

    except Exception:
        logger.exception(
            "Quality analysis failed."
        )
        raise


if __name__ == "__main__":
    main()
