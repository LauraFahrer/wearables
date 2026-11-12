
#!/usr/bin/env python3

"""
Feature Analysis

Checks:
    1. Feature-feature correlations
    2. Multicollinearity (Variance Inflation Factor)
    3. Feature-label dependencies
    4. Feature redundancy
    5. Class-wise feature distributions

Outputs:
    - feature_correlations.csv
    - multicollinearity.csv
    - feature_label_dependencies.csv
    - redundant_features.csv
    - classwise_numeric_distributions.csv
    - classwise_categorical_distributions.csv
    - feature_analysis_report.json
"""

import argparse
import json
import logging
from itertools import combinations
from pathlib import Path

import numpy as np
import pandas as pd

from scipy.stats import (
    chi2_contingency,
    f_oneway,
    pearsonr,
    spearmanr,
)

from sklearn.feature_selection import (
    mutual_info_classif,
    mutual_info_regression,
)

from sklearn.impute import SimpleImputer
from sklearn.preprocessing import OrdinalEncoder

from statsmodels.stats.outliers_influence import (
    variance_inflation_factor,
)


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
# Feature identification
# ---------------------------------------------------------

def identify_features(
    df: pd.DataFrame,
    class_column: str,
    excluded_columns: list,
):

    if class_column not in df.columns:
        raise ValueError(
            f"Label column '{class_column}' not found."
        )

    excluded = set(excluded_columns + [class_column])

    features = [
        col for col in df.columns
        if col not in excluded
        and not pd.api.types.is_datetime64_any_dtype(
            df[col]
        )
    ]

    numeric_features = [
        col for col in features
        if pd.api.types.is_numeric_dtype(df[col])
        and not pd.api.types.is_bool_dtype(df[col])
    ]

    categorical_features = [
        col for col in features
        if col not in numeric_features
    ]

    logger.info(
        "Identified %d numeric and %d categorical features.",
        len(numeric_features),
        len(categorical_features),
    )

    return features, numeric_features, categorical_features


# ---------------------------------------------------------
# Helper functions
# ---------------------------------------------------------

def encode_categorical(
    df: pd.DataFrame,
) -> pd.DataFrame:

    encoded = df.copy()

    for column in encoded.columns:

        values = encoded[column].astype("string")

        categories = sorted(
            values.dropna().unique().tolist()
        )

        mapping = {
            value: index
            for index, value in enumerate(categories)
        }

        encoded[column] = values.map(mapping)

    return encoded.astype(float)


def cramers_v(
    x: pd.Series,
    y: pd.Series,
) -> float:

    contingency = pd.crosstab(x, y)

    if contingency.empty:
        return np.nan

    if min(contingency.shape) < 2:
        return np.nan

    chi2 = chi2_contingency(
        contingency,
        correction=False,
    )[0]

    n = contingency.to_numpy().sum()

    if n == 0:
        return np.nan

    phi2 = chi2 / n

    rows, columns = contingency.shape

    # Bias-corrected Cramer's V
    phi2_corrected = max(
        0,
        phi2 - (
            (columns - 1) * (rows - 1)
            / (n - 1)
        ),
    ) if n > 1 else 0

    rows_corrected = (
        rows - (rows - 1) ** 2 / (n - 1)
    ) if n > 1 else rows

    columns_corrected = (
        columns - (columns - 1) ** 2 / (n - 1)
    ) if n > 1 else columns

    denominator = min(
        rows_corrected - 1,
        columns_corrected - 1,
    )

    if denominator <= 0:
        return np.nan

    return float(
        np.sqrt(phi2_corrected / denominator)
    )


def safe_float(value):

    if pd.isna(value) or not np.isfinite(value):
        return None

    return float(value)


# ---------------------------------------------------------
# 1. Feature-feature correlations
# ---------------------------------------------------------

def analyze_correlations(
    df: pd.DataFrame,
    numeric_features: list,
):

    logger.info("Analyzing feature-feature correlations...")

    if len(numeric_features) < 2:
        return {}

    numeric_df = df[numeric_features]

    pearson = numeric_df.corr(
        method="pearson"
    )

    spearman = numeric_df.corr(
        method="spearman"
    )

    pearson.to_csv(
        "feature_correlations.csv"
    )

    spearman.to_csv(
        "feature_correlations_spearman.csv"
    )

    return {
        "pearson": pearson.to_dict(),
        "spearman": spearman.to_dict(),
    }


# ---------------------------------------------------------
# 2. Multicollinearity (VIF)
# ---------------------------------------------------------

def analyze_multicollinearity(
    df: pd.DataFrame,
    numeric_features: list,
):

    logger.info("Analyzing multicollinearity using VIF...")

    if len(numeric_features) < 2:
        return []

    numeric_df = df[numeric_features].replace(
        [np.inf, -np.inf],
        np.nan,
    )

    # Remove features without any valid values
    numeric_df = numeric_df.dropna(
        axis=1,
        how="all",
    )

    # Remove constant features
    numeric_df = numeric_df.loc[
        :,
        numeric_df.nunique(dropna=True) > 1,
    ]

    if numeric_df.shape[1] < 2:
        return []

    # Median imputation
    imputer = SimpleImputer(
        strategy="median"
    )

    X = imputer.fit_transform(numeric_df)

    if X.shape[0] <= X.shape[1]:
        logger.warning(
            "Too few observations for reliable VIF estimation."
        )
        return []

    vif_results = []

    for index, column in enumerate(numeric_df.columns):

        try:

            vif = variance_inflation_factor(
                X,
                index,
            )

            vif_results.append({
                "feature": column,
                "VIF": safe_float(vif),
            })

        except Exception as error:

            logger.warning(
                "Could not calculate VIF for %s: %s",
                column,
                error,
            )

    vif_df = pd.DataFrame(vif_results)

    if not vif_df.empty:
        vif_df.to_csv(
            "multicollinearity.csv",
            index=False,
        )

    return vif_results


# ---------------------------------------------------------
# 3. Feature-label dependencies
# ---------------------------------------------------------

def analyze_feature_label_dependencies(
    df: pd.DataFrame,
    numeric_features: list,
    categorical_features: list,
    label_column: str,
    label_type: str,
):

    logger.info("Analyzing feature-label dependencies...")

    results = []

    data = df.dropna(
        subset=[label_column]
    ).copy()

    y = data[label_column]

    for feature in numeric_features:

        valid = data[
            [feature, label_column]
        ].replace(
            [np.inf, -np.inf],
            np.nan,
        ).dropna()

        if len(valid) < 3:
            continue

        x = valid[feature]
        target = valid[label_column]

        if x.nunique() < 2:
            continue

        if label_type == "classification":

            if target.nunique() < 2:
                continue

            groups = [
                group[feature].to_numpy()
                for _, group in valid.groupby(label_column)
            ]

            try:
                f_stat, p_value = f_oneway(*groups)

            except Exception:
                f_stat, p_value = np.nan, np.nan

            try:
                mi = mutual_info_classif(
                    x.to_numpy().reshape(-1, 1),
                    target.to_numpy(),
                    random_state=42,
                )[0]

            except Exception:
                mi = np.nan

            results.append({
                "feature": feature,
                "feature_type": "numeric",
                "test": "ANOVA F-test",
                "statistic": safe_float(f_stat),
                "p_value": safe_float(p_value),
                "mutual_information": safe_float(mi),
                "n_observations": len(valid),
            })

        else:

            if target.nunique() < 2:
                continue

            try:
                pearson_r, pearson_p = pearsonr(
                    x,
                    target,
                )

                spearman_r, spearman_p = spearmanr(
                    x,
                    target,
                )

                mi = mutual_info_regression(
                    x.to_numpy().reshape(-1, 1),
                    target.to_numpy(),
                    random_state=42,
                )[0]

            except Exception:
                pearson_r = pearson_p = np.nan
                spearman_r = spearman_p = np.nan
                mi = np.nan

            results.append({
                "feature": feature,
                "feature_type": "numeric",
                "test": "Pearson/Spearman",
                "pearson_r": safe_float(pearson_r),
                "pearson_p": safe_float(pearson_p),
                "spearman_r": safe_float(spearman_r),
                "spearman_p": safe_float(spearman_p),
                "mutual_information": safe_float(mi),
                "n_observations": len(valid),
            })

    # Categorical features
    for feature in categorical_features:

        valid = data[
            [feature, label_column]
        ].dropna()

        if len(valid) < 3:
            continue

        if valid[feature].nunique() < 2:
            continue

        if label_type == "classification":

            contingency = pd.crosstab(
                valid[feature],
                valid[label_column],
            )

            if min(contingency.shape) < 2:
                continue

            chi2, p_value, _, _ = chi2_contingency(
                contingency
            )

            results.append({
                "feature": feature,
                "feature_type": "categorical",
                "test": "Chi-square",
                "statistic": safe_float(chi2),
                "p_value": safe_float(p_value),
                "cramers_v": safe_float(
                    cramers_v(
                        valid[feature],
                        valid[label_column],
                    )
                ),
                "n_observations": len(valid),
            })

        else:

            # Encode categorical feature for mutual information
            encoded = encode_categorical(
                valid[[feature]]
            )

            try:
                mi = mutual_info_regression(
                    encoded.to_numpy(),
                    valid[label_column].to_numpy(),
                    discrete_features=True,
                    random_state=42,
                )[0]

            except Exception:
                mi = np.nan

            results.append({
                "feature": feature,
                "feature_type": "categorical",
                "test": "Mutual Information",
                "mutual_information": safe_float(mi),
                "n_observations": len(valid),
            })

    results_df = pd.DataFrame(results)

    results_df.to_csv(
        "feature_label_dependencies.csv",
        index=False,
    )

    return results


# ---------------------------------------------------------
# 4. Feature redundancy
# ---------------------------------------------------------

def analyze_redundancy(
    df: pd.DataFrame,
    numeric_features: list,
    categorical_features: list,
    threshold: float,
):

    logger.info(
        "Identifying redundant features (threshold: %.2f)...",
        threshold,
    )

    redundant_pairs = []

    # Numeric features: absolute Pearson correlation
    if len(numeric_features) >= 2:

        corr = df[numeric_features].corr(
            method="pearson"
        )

        for feature_a, feature_b in combinations(
            numeric_features,
            2,
        ):

            value = corr.loc[
                feature_a,
                feature_b,
            ]

            if pd.notna(value) and abs(value) >= threshold:

                redundant_pairs.append({
                    "feature_1": feature_a,
                    "feature_2": feature_b,
                    "association": safe_float(value),
                    "association_type": "Pearson correlation",
                    "absolute_association": abs(value),
                })

    # Categorical features: Cramer's V
    if len(categorical_features) >= 2:

        for feature_a, feature_b in combinations(
            categorical_features,
            2,
        ):

            valid = df[
                [feature_a, feature_b]
            ].dropna()

            if len(valid) < 2:
                continue

            value = cramers_v(
                valid[feature_a],
                valid[feature_b],
            )

            if pd.notna(value) and value >= threshold:

                redundant_pairs.append({
                    "feature_1": feature_a,
                    "feature_2": feature_b,
                    "association": value,
                    "association_type": "Cramer's V",
                    "absolute_association": value,
                })

    redundant_df = pd.DataFrame(
        redundant_pairs,
        columns=[
            "feature_1",
            "feature_2",
            "association",
            "association_type",
            "absolute_association",
        ],
    )

    redundant_df.to_csv(
        "redundant_features.csv",
        index=False,
    )

    return {
        "threshold": threshold,
        "total_redundant_pairs": len(
            redundant_pairs
        ),
        "redundant_pairs": redundant_pairs,
    }


# ---------------------------------------------------------
# 5. Class-wise feature distributions
# ---------------------------------------------------------

def analyze_classwise_distributions(
    df: pd.DataFrame,
    numeric_features: list,
    categorical_features: list,
    label_column: str,
    label_type: str,
):

    logger.info(
        "Analyzing class-wise feature distributions..."
    )

    if label_type != "classification":
        logger.info(
            "Skipping class-wise analysis for regression target."
        )
        return {}

    data = df.dropna(
        subset=[label_column]
    ).copy()

    # Numeric feature distributions
    numeric_results = []

    for feature in numeric_features:

        for label, group in data.groupby(label_column):

            values = group[feature].replace(
                [np.inf, -np.inf],
                np.nan,
            ).dropna()

            if values.empty:
                continue

            numeric_results.append({
                "feature": feature,
                "class": str(label),
                "count": len(values),
                "mean": safe_float(values.mean()),
                "std": safe_float(values.std()),
                "median": safe_float(values.median()),
                "q25": safe_float(values.quantile(0.25)),
                "q75": safe_float(values.quantile(0.75)),
                "min": safe_float(values.min()),
                "max": safe_float(values.max()),
            })

    numeric_df = pd.DataFrame(
        numeric_results
    )

    numeric_df.to_csv(
        "classwise_numeric_distributions.csv",
        index=False,
    )

    # Categorical feature distributions
    categorical_results = []

    for feature in categorical_features:

        grouped = (
            data.groupby(
                [label_column, feature],
                dropna=False,
            )
            .size()
            .reset_index(name="count")
        )

        grouped["percentage"] = (
            grouped["count"]
            / grouped.groupby(label_column)[
                "count"
            ].transform("sum")
            * 100
        ).round(2)

        for _, row in grouped.iterrows():

            categorical_results.append({
                "feature": feature,
                "class": str(row[label_column]),
                "category": str(row[feature]),
                "count": int(row["count"]),
                "percentage": float(row["percentage"]),
            })

    categorical_df = pd.DataFrame(
        categorical_results
    )

    categorical_df.to_csv(
        "classwise_categorical_distributions.csv",
        index=False,
    )

    return {
        "numeric_features_analyzed": len(
            numeric_features
        ),
        "categorical_features_analyzed": len(
            categorical_features
        ),
        "number_of_classes": int(
            data[label_column].nunique()
        ),
    }


# ---------------------------------------------------------
# Main
# ---------------------------------------------------------

def main():

    parser = argparse.ArgumentParser(
        description="Feature Analysis"
    )

    parser.add_argument(
        "dataset",
        type=Path,
        help="Path to input dataset",
    )

    parser.add_argument(
        "--class-column",
        required=True,
        help="Target label column",
    )

    parser.add_argument(
        "--class-type",
        choices=["auto", "classification", "regression"],
        default="auto",
        help="Target type (default: auto)",
    )

    parser.add_argument(
        "--exclude-columns",
        nargs="*",
        default=[],
        help="Columns to exclude from feature analysis",
    )

    parser.add_argument(
        "--correlation-threshold",
        type=float,
        default=0.90,
        help="Threshold for feature redundancy (default: 0.90)",
    )

    args = parser.parse_args()

    if not args.dataset.exists():
        parser.error(
            f"Dataset not found: {args.dataset}"
        )

    if not 0 < args.correlation_threshold <= 1:
        parser.error(
            "Correlation threshold must be between 0 and 1."
        )

    try:

        df = load_dataset(args.dataset)

        if df.empty:
            raise ValueError(
                "Dataset contains no rows."
            )

        (
            features,
            numeric_features,
            categorical_features,
        ) = identify_features(
            df,
            args.class_column,
            args.exclude_columns,
        )

        # Determine target type
        if args.class_type == "auto":

            is_numeric = pd.api.types.is_numeric_dtype(
                df[args.class_column]
            )

            unique_count = df[
                args.class_column
            ].nunique()

            class_type = (
                "classification"
                if not is_numeric or unique_count <= 10
                else "regression"
            )

        else:
            class_type = args.class_type

        logger.info(
            "Detected target type: %s",
            class_type,
        )

        logger.info("Starting feature analysis...")

        correlations = analyze_correlations(
            df,
            numeric_features,
        )

        multicollinearity = analyze_multicollinearity(
            df,
            numeric_features,
        )

        dependencies = analyze_feature_label_dependencies(
            df,
            numeric_features,
            categorical_features,
            args.class_column,
            class_type,
        )

        redundancy = analyze_redundancy(
            df,
            numeric_features,
            categorical_features,
            args.correlation_threshold,
        )

        classwise = analyze_classwise_distributions(
            df,
            numeric_features,
            categorical_features,
            args.class_column,
            class_type,
        )

        report = {
            "dataset": args.dataset.name,
            "dataset_shape": {
                "rows": int(df.shape[0]),
                "columns": int(df.shape[1]),
            },
            "target": {
                "column": args.class_column,
                "type": class_type,
            },
            "features": {
                "total": len(features),
                "numeric": numeric_features,
                "categorical": categorical_features,
            },
            "correlations": correlations,
            "multicollinearity": multicollinearity,
            "feature_label_dependencies": dependencies,
            "redundancy": redundancy,
            "classwise_distributions": classwise,
        }

        with open(
            "feature_analysis_report.json",
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
            "Feature analysis completed successfully."
        )

        logger.info(
            "Report saved to feature_analysis_report.json"
        )

    except Exception:
        logger.exception(
            "Feature analysis failed."
        )
        raise


if __name__ == "__main__":
    main()
