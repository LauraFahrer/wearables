process EDA {

    container 'python:3.12-slim'

    input:
    path dataset
    path success

    output:
    path "quality_report.json", emit: quality_report
    path "missing_values.csv", emit: missing_values
    path "duplicated_rows.csv", emit: duplicates
    path "outliers.csv", emit: outliers
    path "feature_summary.csv", emit: feature_summary

    path "distribution_report.json", emit: distribution_report
    path "class_distribution.csv", emit: class_distribution
    path "participant_distribution.csv", emit: participant_distribution
    path "participant_class_distribution.csv", emit: participant_class_distribution

    path "feature_analysis_report.json", emit: feature_report
    path "feature_correlations.csv", emit: correlations
    path "feature_correlations_spearman.csv", emit: correlations_spearman
    path "multicollinearity.csv", emit: multicollinearity
    path "feature_label_dependencies.csv", emit: label_dependencies
    path "redundant_features.csv", emit: redundant_features
    path "classwise_numeric_distributions.csv", emit: classwise_numeric
    path "classwise_categorical_distributions.csv", emit: classwise_categorical

    path "pca_report.json", emit: pca_report
    path "pca_explained_variance.csv", emit: pca_variance
    path "pca_sample_scores.csv", emit: pca_scores
    path "pca_feature_loadings.csv", emit: pca_loadings
    path "pca_scree_plot.png", emit: pca_scree
    path "pca_2d.png", emit: pca_2d
    path "pca_3d.png", optional: true, emit: pca_3d

    path "eda.success", emit: success
    val "eda", emit: workflow

    script:
    """

    pip install pandas numpy openpyxl scipy scikit-learn statsmodels matplotlib

    python ${projectDir}/bin/quality_integrity.py \
        ${dataset}

    python ${projectDir}/bin/data_distribution.py \
        ${dataset} \
        --class-column '${params.class_column}' \
        --participant-column '${params.participant_column}' \
        --positive-label '${params.positive_label}' \
        --negative-label '${params.negative_label}'

    python ${projectDir}/bin/feature_analysis.py \
        ${dataset} \
        --class-column '${params.class_column}' \
        --class-type '${params.class_type}' \
        --correlation-threshold ${params.correlation_threshold}

    python ${projectDir}/bin/pca.py \
        ${dataset} \
        --class-column '${params.class_column}' \
        --exclude-columns '${params.participant_column}' \
        --n-components ${params.pca_components}

    touch eda.success

    """

    stub:
    """
    touch quality_report.json
    touch missing_values.csv
    touch duplicated_rows.csv
    touch outliers.csv
    touch feature_summary.csv

    touch distribution_report.json
    touch class_distribution.csv
    touch participant_distribution.csv
    touch participant_class_distribution.csv

    touch feature_analysis_report.json
    touch feature_correlations.csv
    touch feature_correlations_spearman.csv
    touch multicollinearity.csv
    touch feature_label_dependencies.csv
    touch redundant_features.csv
    touch classwise_numeric_distributions.csv
    touch classwise_categorical_distributions.csv

    touch pca_report.json
    touch pca_explained_variance.csv
    touch pca_sample_scores.csv
    touch pca_feature_loadings.csv
    touch pca_scree_plot.png
    touch pca_2d.png
    touch pca_3d.png

    touch eda.success
    """
}
