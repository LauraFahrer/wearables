#!/usr/bin/env python3

"""
Model tuning: Logistic Regression

Steps:
    1. Load the training data (TSV)
    2. Separate target, sample id (and optional group) columns from features
    3. Build a pipeline: imputation -> scaling -> logistic regression
    4. Hyperparameter search (GridSearchCV) with cross-validation
       (StratifiedGroupKFold if a group column is given, to prevent leakage
       between measurements of the same participant; otherwise StratifiedKFold)
    5. Write the outputs required by the evaluation workflow

Outputs:
    - <model>_best_params.json   best hyperparameter values (without pipeline prefix)
    - <model>_config.yaml        model configuration (type, columns, preprocessing)
    - <model>_cv_results.csv     all tested parameter combinations and their CV scores
    - <model>_tuning_report.json summary of the tuning run (best score, CV setup, ...)
"""

import argparse
import json
import logging
import os
import warnings
from pathlib import Path

# scikit-learn >= 1.8 deprecates the 'penalty' argument in favour of 'l1_ratio'.
# We keep 'penalty' because the evaluation workflow expects it in the JSON file.
# Set via env var as well so parallel worker processes inherit the filter.
_PENALTY_FILTER = "ignore::FutureWarning,ignore:Inconsistent values:UserWarning"
os.environ["PYTHONWARNINGS"] = _PENALTY_FILTER
warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", message="Inconsistent values", category=UserWarning)

import pandas as pd
import yaml

from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import (
    GridSearchCV,
    StratifiedGroupKFold,
    StratifiedKFold,
)
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import MinMaxScaler, RobustScaler, StandardScaler


MODEL_TYPE = "logistic_regression"
STEP_NAME = "model"

SCALERS = {
    "standard": StandardScaler,
    "minmax": MinMaxScaler,
    "robust": RobustScaler,
    "none": None,
}

IMPUTATION_STRATEGIES = ["mean", "median", "most_frequent"]

# Only valid penalty/solver combinations are listed:
#   liblinear -> l1, l2
#   lbfgs     -> l2
#   saga      -> l1, l2 (elasticnet left out to keep the grid small)
PARAM_GRID = [
    {
        "C": [0.001, 0.01, 0.1, 1, 10, 100],
        "penalty": ["l1", "l2"],
        "solver": ["liblinear"],
        "class_weight": [None, "balanced"],
    },
    {
        "C": [0.001, 0.01, 0.1, 1, 10, 100],
        "penalty": ["l2"],
        "solver": ["lbfgs"],
        "class_weight": [None, "balanced"],
    },
]

# liblinear only supports binary targets -> for >= 3 classes use saga for l1/l2
PARAM_GRID_MULTICLASS = [
    {
        "C": [0.001, 0.01, 0.1, 1, 10, 100],
        "penalty": ["l1", "l2"],
        "solver": ["saga"],
        "class_weight": [None, "balanced"],
    },
    PARAM_GRID[1],
]


logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


def load_data(input_file, target_column, sample_id_column, group_column):

    data = pd.read_csv(input_file, sep="\t")

    if data.empty:
        raise ValueError("The training dataset is empty.")

    for column in [target_column, sample_id_column, group_column]:
        if column and column not in data.columns:
            raise ValueError(f"Column '{column}' not found in dataset.")

    data = data.dropna(subset=[target_column])

    y = data[target_column]
    groups = data[group_column] if group_column else None

    excluded = [c for c in [target_column, sample_id_column, group_column] if c]
    X = data.drop(columns=excluded)

    # Logistic regression needs numeric input -> keep numeric features only
    non_numeric = X.select_dtypes(exclude="number").columns.tolist()
    if non_numeric:
        logger.warning(f"Dropping non-numeric feature columns: {non_numeric}")
        X = X.drop(columns=non_numeric)

    if X.shape[1] == 0:
        raise ValueError("No numeric feature columns left after filtering.")

    if y.nunique() < 2:
        raise ValueError("The target column needs at least two classes.")

    return X, y, groups


def build_pipeline(scaling, imputation, seed):

    steps = [("imputer", SimpleImputer(strategy=imputation))]

    scaler = SCALERS[scaling]
    if scaler is not None:
        steps.append(("scaler", scaler()))

    steps.append(
        (STEP_NAME, LogisticRegression(max_iter=5000, random_state=seed))
    )

    return Pipeline(steps)


def build_cv(y, groups, cv_folds, seed):

    # Folds cannot exceed the size of the smallest class
    n_splits = min(cv_folds, y.value_counts().min())

    if groups is not None:
        n_splits = min(n_splits, groups.nunique())

    if n_splits < 2:
        raise ValueError("Not enough samples per class/group for cross-validation.")

    if n_splits < cv_folds:
        logger.warning(f"Reducing number of CV folds from {cv_folds} to {n_splits}.")

    if groups is not None:
        return StratifiedGroupKFold(n_splits=n_splits, shuffle=True, random_state=seed), n_splits

    return StratifiedKFold(n_splits=n_splits, shuffle=True, random_state=seed), n_splits


def prefix_grid(grid):
    # GridSearchCV on a pipeline needs the step name as prefix: "model__C"
    return [
        {f"{STEP_NAME}__{key}": values for key, values in block.items()}
        for block in grid
    ]


def strip_prefix(params):
    prefix = f"{STEP_NAME}__"
    return {key.removeprefix(prefix): value for key, value in params.items()}


def write_outputs(search, args, n_splits, n_features):

    model = MODEL_TYPE

    # 1. Best parameters (JSON) -> read by the evaluation workflow
    best_params = strip_prefix(search.best_params_)
    with open(f"{model}_best_params.json", "w", encoding="utf-8") as file:
        json.dump(best_params, file, indent=4)

    # 2. Model configuration (YAML) -> read by the evaluation workflow
    config = {
        "model": {
            "type": model,
            "target_column": args.target_column,
            "sample_id_column": args.sample_id_column,
            "features": {
                "selection": "all",
            },
            "preprocessing": {
                "scaling": args.scaling,
                "imputation": args.imputation,
            },
        }
    }
    with open(f"{model}_config.yaml", "w", encoding="utf-8") as file:
        yaml.safe_dump(config, file, sort_keys=False)

    # 3. All CV results (CSV)
    cv_results = pd.DataFrame(search.cv_results_)
    cv_results.columns = [c.replace(f"param_{STEP_NAME}__", "param_") for c in cv_results.columns]
    cv_results = cv_results.sort_values("rank_test_score")
    cv_results.to_csv(f"{model}_cv_results.csv", index=False)

    # 4. Summary report (JSON)
    report = {
        "model": model,
        "scoring": args.scoring,
        "best_cv_score": float(search.best_score_),
        "best_params": best_params,
        "cv_folds": int(n_splits),
        "cv_strategy": "StratifiedGroupKFold" if args.group_column else "StratifiedKFold",
        "group_column": args.group_column,
        "n_features": int(n_features),
        "n_candidates": int(len(cv_results)),
        "seed": args.seed,
    }
    with open(f"{model}_tuning_report.json", "w", encoding="utf-8") as file:
        json.dump(report, file, indent=4)

    return best_params


def main():

    parser = argparse.ArgumentParser(
        description="Tune a logistic regression model with cross-validated grid search."
    )

    parser.add_argument("input_file", type=Path)
    parser.add_argument("--target-column", default="class")
    parser.add_argument("--sample-id-column", default="sample_id")
    parser.add_argument("--group-column", default=None)
    parser.add_argument("--scaling", choices=list(SCALERS.keys()), default="standard")
    parser.add_argument("--imputation", choices=IMPUTATION_STRATEGIES, default="median")
    parser.add_argument("--cv-folds", type=int, default=5)
    parser.add_argument("--scoring", default="balanced_accuracy")
    parser.add_argument("--seed", type=int, default=42)

    args = parser.parse_args()

    # Nextflow passes empty strings for unset params
    args.group_column = args.group_column or None
    args.sample_id_column = args.sample_id_column or None

    X, y, groups = load_data(
        args.input_file,
        args.target_column,
        args.sample_id_column,
        args.group_column,
    )
    logger.info(f"Samples: {len(X)}, features: {X.shape[1]}, classes: {y.nunique()}")

    pipeline = build_pipeline(args.scaling, args.imputation, args.seed)
    cv, n_splits = build_cv(y, groups, args.cv_folds, args.seed)

    param_grid = PARAM_GRID if y.nunique() == 2 else PARAM_GRID_MULTICLASS

    search = GridSearchCV(
        estimator=pipeline,
        param_grid=prefix_grid(param_grid),
        scoring=args.scoring,
        cv=cv,
        n_jobs=-1,
        refit=True,
        error_score="raise",
    )
    search.fit(X, y, groups=groups)

    best_params = write_outputs(search, args, n_splits, X.shape[1])

    logger.info(f"Best {args.scoring}: {search.best_score_:.4f}")
    logger.info(f"Best parameters: {best_params}")


if __name__ == "__main__":
    main()
