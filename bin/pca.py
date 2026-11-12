
#!/usr/bin/env python3

"""
Principal Component Analysis (PCA)

Checks:
    1. Numerical feature selection
    2. Missing value imputation
    3. Feature standardization
    4. PCA with 2 or 3 components
    5. Explained variance
    6. Sample scores
    7. Feature loadings
    8. PCA visualizations

Outputs:
    - pca_explained_variance.csv
    - pca_sample_scores.csv
    - pca_feature_loadings.csv
    - pca_scree_plot.png
    - pca_2d.png
    - pca_3d.png (if 3 components are selected)
    - pca_report.json
"""

import argparse
import json
import logging
from pathlib import Path

import matplotlib
matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from sklearn.decomposition import PCA
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler


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
# Feature selection
# ---------------------------------------------------------

def select_features(
    df: pd.DataFrame,
    excluded_columns: list,
):

    excluded = set(excluded_columns)

    numeric_features = [
        column
        for column in df.select_dtypes(
            include=np.number
        ).columns
        if column not in excluded
    ]

    if len(numeric_features) < 2:
        raise ValueError(
            "PCA requires at least two numerical features."
        )

    X = df[numeric_features].copy()

    # Replace infinite values with missing values
    X = X.replace(
        [np.inf, -np.inf],
        np.nan,
    )

    # Remove completely empty features
    X = X.dropna(
        axis=1,
        how="all",
    )

    # Remove constant features
    X = X.loc[
        :,
        X.nunique(dropna=True) > 1,
    ]

    if X.shape[1] < 2:
        raise ValueError(
            "Fewer than two valid numerical features remain."
        )

    logger.info(
        "Selected %d numerical features for PCA.",
        X.shape[1],
    )

    return X


# ---------------------------------------------------------
# Data preprocessing
# ---------------------------------------------------------

def preprocess_data(X: pd.DataFrame):

    logger.info("Preprocessing numerical features...")

    # Median imputation
    imputer = SimpleImputer(
        strategy="median"
    )

    X_imputed = imputer.fit_transform(X)

    # Standardization
    scaler = StandardScaler()

    X_scaled = scaler.fit_transform(
        X_imputed
    )

    return X_scaled


# ---------------------------------------------------------
# PCA
# ---------------------------------------------------------

def perform_pca(
    X_scaled: np.ndarray,
    n_components: int,
):

    max_components = min(
        X_scaled.shape[0],
        X_scaled.shape[1],
    )

    if n_components > max_components:
        raise ValueError(
            f"Requested {n_components} PCs, "
            f"but maximum possible is {max_components}."
        )

    logger.info(
        "Performing PCA with %d components...",
        n_components,
    )

    pca = PCA(
        n_components=n_components,
    )

    scores = pca.fit_transform(
        X_scaled
    )

    explained_variance = pca.explained_variance_ratio_

    cumulative_variance = np.cumsum(
        explained_variance
    )

    return (
        pca,
        scores,
        explained_variance,
        cumulative_variance,
    )


# ---------------------------------------------------------
# Explained variance
# ---------------------------------------------------------

def save_explained_variance(
    explained_variance: np.ndarray,
    cumulative_variance: np.ndarray,
):

    variance_df = pd.DataFrame({
        "principal_component": [
            f"PC{i + 1}"
            for i in range(len(explained_variance))
        ],
        "explained_variance": explained_variance,
        "cumulative_explained_variance": cumulative_variance,
    })

    variance_df.to_csv(
        "pca_explained_variance.csv",
        index=False,
    )

    return variance_df


# ---------------------------------------------------------
# Sample scores
# ---------------------------------------------------------

def save_sample_scores(
    scores: np.ndarray,
    index: pd.Index,
    labels: pd.Series = None,
):

    score_columns = [
        f"PC{i + 1}"
        for i in range(scores.shape[1])
    ]

    scores_df = pd.DataFrame(
        scores,
        columns=score_columns,
        index=index,
    )

    scores_df.index.name = "sample_index"

    if labels is not None:
        scores_df["class"] = labels.to_numpy()

    scores_df.to_csv(
        "pca_sample_scores.csv"
    )

    return scores_df


# ---------------------------------------------------------
# Feature loadings
# ---------------------------------------------------------

def save_feature_loadings(
    pca: PCA,
    features: list,
):

    loadings_df = pd.DataFrame(
        pca.components_.T,
        index=features,
        columns=[
            f"PC{i + 1}"
            for i in range(pca.n_components_)
        ],
    )

    loadings_df.index.name = "feature"

    loadings_df.to_csv(
        "pca_feature_loadings.csv"
    )

    return loadings_df


# ---------------------------------------------------------
# Scree plot
# ---------------------------------------------------------

def plot_scree(
    explained_variance: np.ndarray,
    cumulative_variance: np.ndarray,
):

    components = np.arange(
        1,
        len(explained_variance) + 1,
    )

    plt.figure(figsize=(8, 5))

    plt.bar(
        components,
        explained_variance,
        label="Individual explained variance",
    )

    plt.plot(
        components,
        cumulative_variance,
        marker="o",
        label="Cumulative explained variance",
    )

    plt.xlabel("Principal Component")
    plt.ylabel("Explained Variance Ratio")
    plt.title("PCA Scree Plot")

    plt.xticks(components)
    plt.ylim(0, 1.05)

    plt.legend()
    plt.tight_layout()

    plt.savefig(
        "pca_scree_plot.png",
        dpi=300,
    )

    plt.close()


# ---------------------------------------------------------
# 2D PCA visualization
# ---------------------------------------------------------

def plot_pca_2d(
    scores_df: pd.DataFrame,
    explained_variance: np.ndarray,
):

    plt.figure(figsize=(8, 6))

    if "class" in scores_df.columns:

        for label, group in scores_df.groupby(
            "class",
            dropna=False,
        ):

            plt.scatter(
                group["PC1"],
                group["PC2"],
                label=str(label),
                alpha=0.7,
            )

        plt.legend(
            title="Class",
            bbox_to_anchor=(1.05, 1),
            loc="upper left",
        )

    else:

        plt.scatter(
            scores_df["PC1"],
            scores_df["PC2"],
            alpha=0.7,
        )

    plt.xlabel(
        f"PC1 ({explained_variance[0] * 100:.2f}%)"
    )

    plt.ylabel(
        f"PC2 ({explained_variance[1] * 100:.2f}%)"
    )

    plt.title("PCA: PC1 vs PC2")

    plt.axhline(0, linestyle="--", linewidth=0.5)
    plt.axvline(0, linestyle="--", linewidth=0.5)

    plt.tight_layout()

    plt.savefig(
        "pca_2d.png",
        dpi=300,
        bbox_inches="tight",
    )

    plt.close()


# ---------------------------------------------------------
# 3D PCA visualization
# ---------------------------------------------------------

def plot_pca_3d(
    scores_df: pd.DataFrame,
    explained_variance: np.ndarray,
):

    if scores_df.shape[1] < 3:
        return

    from mpl_toolkits.mplot3d import Axes3D

    fig = plt.figure(figsize=(9, 7))

    ax = fig.add_subplot(
        111,
        projection="3d",
    )

    if "class" in scores_df.columns:

        for label, group in scores_df.groupby(
            "class",
            dropna=False,
        ):

            ax.scatter(
                group["PC1"],
                group["PC2"],
                group["PC3"],
                label=str(label),
                alpha=0.7,
            )

        ax.legend(
            title="Class",
            bbox_to_anchor=(1.15, 1),
        )

    else:

        ax.scatter(
            scores_df["PC1"],
            scores_df["PC2"],
            scores_df["PC3"],
            alpha=0.7,
        )

    ax.set_xlabel(
        f"PC1 ({explained_variance[0] * 100:.2f}%)"
    )

    ax.set_ylabel(
        f"PC2 ({explained_variance[1] * 100:.2f}%)"
    )

    ax.set_zlabel(
        f"PC3 ({explained_variance[2] * 100:.2f}%)"
    )

    ax.set_title("PCA: PC1, PC2 and PC3")

    plt.tight_layout()

    plt.savefig(
        "pca_3d.png",
        dpi=300,
        bbox_inches="tight",
    )

    plt.close()


# ---------------------------------------------------------
# Main
# ---------------------------------------------------------

def main():

    parser = argparse.ArgumentParser(
        description="Principal Component Analysis"
    )

    parser.add_argument(
        "dataset",
        type=Path,
        help="Path to input dataset",
    )

    parser.add_argument(
        "--class-column",
        default=None,
        help="Optional class label column",
    )

    parser.add_argument(
        "--exclude-columns",
        nargs="*",
        default=[],
        help="Columns to exclude from PCA",
    )

    parser.add_argument(
        "--n-components",
        type=int,
        choices=[2, 3],
        default=3,
        help="Number of principal components (default: 3)",
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

        # Exclude class label and user-defined columns
        excluded = list(
            args.exclude_columns
        )

        if args.class_column:
            excluded.append(
                args.class_column
            )

        # Select features
        X = select_features(
            df,
            excluded,
        )

        # Extract optional class labels
        labels = None

        if args.class_column:

            if args.class_column not in df.columns:
                raise ValueError(
                    f"Class column '{args.class_column}' not found."
                )

            labels = df.loc[
                X.index,
                args.class_column,
            ]

        # Preprocessing
        X_scaled = preprocess_data(X)

        # PCA
        (
            pca,
            scores,
            explained_variance,
            cumulative_variance,
        ) = perform_pca(
            X_scaled,
            args.n_components,
        )

        # Save results
        variance_df = save_explained_variance(
            explained_variance,
            cumulative_variance,
        )

        scores_df = save_sample_scores(
            scores,
            X.index,
            labels,
        )

        loadings_df = save_feature_loadings(
            pca,
            X.columns.tolist(),
        )

        # Visualizations
        plot_scree(
            explained_variance,
            cumulative_variance,
        )

        plot_pca_2d(
            scores_df,
            explained_variance,
        )

        if args.n_components == 3:

            plot_pca_3d(
                scores_df,
                explained_variance,
            )

        # JSON report
        report = {
            "dataset": args.dataset.name,
            "n_samples": int(X.shape[0]),
            "n_features": int(X.shape[1]),
            "n_components": args.n_components,
            "features": X.columns.tolist(),
            "explained_variance": {
                f"PC{i + 1}": float(value)
                for i, value in enumerate(
                    explained_variance
                )
            },
            "cumulative_explained_variance": float(
                cumulative_variance[-1]
            ),
            "preprocessing": {
                "missing_value_imputation": "Median",
                "scaling": "StandardScaler (Z-score)",
                "infinite_values": "Replaced with NaN",
            },
        }

        with open(
            "pca_report.json",
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
            "PCA completed successfully."
        )

        logger.info(
            "Cumulative explained variance: %.2f%%",
            cumulative_variance[-1] * 100,
        )

    except Exception:

        logger.exception(
            "PCA analysis failed."
        )

        raise


if __name__ == "__main__":
    main()
