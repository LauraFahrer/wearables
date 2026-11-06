include {DATA_DOWNLOAD}          from './modules/data_download'
include {CHECKSUM_CALCULATION}   from './modules/checksum_calculation'

include {INPUT_VALIDATION}       from './modules/input_validation'
include {QUALITY_INTEGRITY}      from './modules/quality_integrity'
include {DATA_DISTRIBUTION}      from './modules/data_distribution'
include {FEATURE_ANALYSIS}       from './modules/feature_analysis'
include {PCA}                    from './modules/pca'

include {EDA}                    from './modules/eda'
include {PROCESSING_DATA}        from './modules/processing_data'
include {SPLITTING_DATA}         from './modules/splitting_data'

workflow {

    if (params.workflow == 'data_accession') {

        DATA_DOWNLOAD(
            params.dataset,
            file(params.dataset_config)     // path to datasets.yml -> does this work?
        )

        CHECKSUM_CALCULATION(
            DATA_DOWNLOAD.out.raw_data,
            params.dataset
        )

    } else if (params.workflow == 'eda') {

        INPUT_VALIDATION(
            file(params.dataset_file),
            file(params.checksum_file)
        )

        QUALITY_INTEGRITY(
            file(params.dataset_file),
            INPUT_VALIDATION.out.success
        )

        DATA_DISTRIBUTION(
            file(params.dataset_file),
            INPUT_VALIDATION.out.success
        )

        FEATURE_ANALYSIS(
            file(params.dataset_file),
            INPUT_VALIDATION.out.success
        )

        PCA(
            file(params.dataset_file),
            INPUT_VALIDATION.out.success
        )

    } else if (params.workflow == 'data_processing') {

        INPUT_VALIDATION(
            file(params.dataset_file),
            file(params.checksum_file)
        )

        PROCESSING_DATA(
            file(params.dataset_file),
            INPUT_VALIDATION.out.success
        )

        SPLITTING_DATA(
            PROCESSING_DATA.out.processed_data,
            params.test_size,
            params.seed
        )

    } else if (
        params.workflow != 'data_accession' &&
        params.workflow != 'eda' &&
        params.workflow != 'data_processing'
        ) {
        
        error"""
        Unknown workflow: ${params.workflow}.
        Available workflows: data_accession, eda, data_processing
        """
    }

}
