process MODEL_TUNING {

    publishDir "${projectDir}/results/model_tuning", mode: 'copy'

    container 'python:3.12-slim'

    input:
    path train_data

    output:
    path "logistic_regression_best_params.json", emit: best_params
    path "logistic_regression_config.yaml", emit: model_config
    path "logistic_regression_cv_results.csv", emit: cv_results
    path "logistic_regression_tuning_report.json", emit: tuning_report

    script:
    """

    pip install pandas scikit-learn pyyaml

    python ${projectDir}/bin/model_tuning.py \
        ${train_data} \
        --target-column '${params.target_column}' \
        --sample-id-column '${params.sample_id_column}' \
        --group-column '${params.group_column}' \
        --scaling ${params.scaling} \
        --imputation ${params.imputation} \
        --cv-folds ${params.cv_folds} \
        --scoring ${params.scoring} \
        --seed ${params.seed}

    """

    stub:
    """
    echo '{"C": 0.1, "penalty": "l2", "solver": "liblinear", "class_weight": "balanced"}' > logistic_regression_best_params.json
    printf 'model:\\n  type: logistic_regression\\n  target_column: class\\n  sample_id_column: sample_id\\n  features:\\n    selection: all\\n  preprocessing:\\n    scaling: standard\\n    imputation: median\\n' > logistic_regression_config.yaml
    touch logistic_regression_cv_results.csv
    touch logistic_regression_tuning_report.json
    """
}
