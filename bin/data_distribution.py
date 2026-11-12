
#!/usr/bin/env python3

"""
Data Distribution Analysis

Checks:
    1. Class distributions
    2. Positive-to-negative (P/N) class ratio
    3. Number of participants
    4. Number of entries per participant
    5. Class distribution per participant

Outputs:
    - class_distribution.csv
    - participant_distribution.csv
    - participant_class_distribution.csv
    - distribution_report.json
"""

import argparse
import json
import logging
from pathlib import Path

import pandas as pd


# ---------------------------------------------------------
# Logging
# ---------------------------------------------------------

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

logger = logging.getLogger(__name__)


# ---------------------------------------------------------
# Data loading
# ---------------------------------------------------------

def load_dataset(file_path: Path) -> pd.DataFrame:

    logger.info("Loading dataset: %s", file_path)

    suffix = file_path.suffix.lower()

    if suffix == ".csv":
        df = pd.read_csv(file_path)
    elif suffix in [".tsv", ".txt"]:
        df = pd.read_csv(file_path, sep="\t")
    elif suffix == ".parquet":
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


# ---------------------------------------------------------
# 1. Class distributions
# ---------------------------------------------------------

def analyze_class_distribution(
    df: pd.DataFrame,
    class_column: str,
) -> dict:

    logger.info("Analyzing class distributions...")

    if class_column not in df.columns:
        raise ValueError(
            f"Class column '{class_column}' not found."
        )

    class_counts = df[class_column].value_counts(
        dropna=False
    )

    class_percentages = (
        df[class_column]
        .value_counts(normalize=True, dropna=False)
        * 100
    ).round(2)

    distribution = pd.DataFrame({
        "class": class_counts.index.astype(str),
        "count": class_counts.values,
        "percentage": class_percentages.values,
    })

    distribution.to_csv(
        "class_distribution.csv",
        index=False,
    )

    return {
        "class_column": class_column,
        "total_classes": int(
            df[class_column].nunique(dropna=False)
        ),
        "class_counts": {
            str(k): int(v)
            for k, v in class_counts.items()
        },
        "class_percentages": {
            str(k): float(v)
            for k, v in class_percentages.items()
        },
    }


# ---------------------------------------------------------
# 2. Positive-to-negative class ratio
# ---------------------------------------------------------

def analyze_class_ratio(
    df: pd.DataFrame,
    class_column: str,
    positive_label: str,
    negative_label: str,
) -> dict:

    logger.info("Calculating positive-to-negative ratio...")

    positive_count = int(
        (df[class_column].astype(str) == positive_label).sum()
    )

    negative_count = int(
        (df[class_column].astype(str) == negative_label).sum()
    )

    if negative_count == 0:
        ratio = None
    else:
        ratio = round(
            positive_count / negative_count,
            4,
        )

    return {
        "positive_label": positive_label,
        "negative_label": negative_label,
        "positive_count": positive_count,
        "negative_count": negative_count,
        "positive_negative_ratio": ratio,
        "ratio_interpretation": (
            f"{positive_count}:{negative_count}"
        ),
    }


# ---------------------------------------------------------
# 3. Participants and entries per participant
# ---------------------------------------------------------

def analyze_participants(
    df: pd.DataFrame,
    participant_column: str,
) -> dict:

    logger.info("Analyzing participant distribution...")

    if participant_column not in df.columns:
        raise ValueError(
            f"Participant column '{participant_column}' not found."
        )

    participant_counts = (
        df[participant_column]
        .value_counts(dropna=False)
        .rename_axis("participant")
        .reset_index(name="entries")
    )

    participant_counts.to_csv(
        "participant_distribution.csv",
        index=False,
    )

    valid_participants = df[
        participant_column
    ].dropna()

    entries_per_participant = (
        valid_participants.value_counts()
    )

    return {
        "participant_column": participant_column,
        "total_participants": int(
            valid_participants.nunique()
        ),
        "missing_participant_ids": int(
            df[participant_column].isna().sum()
        ),
        "total_entries": int(len(df)),
        "entries_per_participant": {
            str(k): int(v)
            for k, v in entries_per_participant.items()
        },
        "entries_summary": {
            "mean": float(
                entries_per_participant.mean()
            ),
            "median": float(
                entries_per_participant.median()
            ),
            "min": int(
                entries_per_participant.min()
            ),
            "max": int(
                entries_per_participant.max()
            ),
        } if not entries_per_participant.empty else {},
    }


# ---------------------------------------------------------
# 4. Class distribution per participant
# ---------------------------------------------------------

def analyze_participant_classes(
    df: pd.DataFrame,
    participant_column: str,
    class_column: str,
) -> dict:

    logger.info(
        "Analyzing class distributions per participant..."
    )

    grouped = (
        df.groupby(
            [participant_column, class_column],
            dropna=False,
        )
        .size()
        .reset_index(name="count")
    )

    # Convert counts to percentages within each participant
    grouped["percentage"] = (
        grouped["count"]
        / grouped.groupby(
            participant_column
        )["count"].transform("sum")
        * 100
    ).round(2)

    grouped.to_csv(
        "participant_class_distribution.csv",
        index=False,
    )

    return {
        "class_distribution_per_participant": [
            {
                "participant": str(row[participant_column]),
                "class": str(row[class_column]),
                "count": int(row["count"]),
                "percentage": float(row["percentage"]),
            }
            for _, row in grouped.iterrows()
        ],
    }


# ---------------------------------------------------------
# Main
# ---------------------------------------------------------

def main():

    parser = argparse.ArgumentParser(
        description="Data Distribution Analysis"
    )

    parser.add_argument(
        "dataset",
        type=Path,
        help="Path to input dataset",
    )

    parser.add_argument(
        "--class-column",
        required=True,
        help="Column containing class labels",
    )

    parser.add_argument(
        "--participant-column",
        required=True,
        help="Column containing participant IDs",
    )

    parser.add_argument(
        "--positive-label",
        default="positive",
        help="Label representing the positive class",
    )

    parser.add_argument(
        "--negative-label",
        default="negative",
        help="Label representing the negative class",
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

        logger.info("Starting distribution analysis...")

        class_distribution = analyze_class_distribution(
            df,
            args.class_column,
        )

        class_ratio = analyze_class_ratio(
            df,
            args.class_column,
            args.positive_label,
            args.negative_label,
        )

        participants = analyze_participants(
            df,
            args.participant_column,
        )

        participant_classes = analyze_participant_classes(
            df,
            args.participant_column,
            args.class_column,
        )

        report = {
            "dataset": args.dataset.name,
            "dataset_shape": {
                "rows": int(df.shape[0]),
                "columns": int(df.shape[1]),
            },
            "class_distribution": class_distribution,
            "class_ratio": class_ratio,
            "participants": participants,
            "participant_classes": participant_classes,
        }

        with open(
            "distribution_report.json",
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
            "Distribution analysis completed successfully."
        )

        logger.info(
            "Report saved to distribution_report.json"
        )

    except Exception:
        logger.exception(
            "Distribution analysis failed."
        )
        raise


if __name__ == "__main__":
    main()