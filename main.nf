include {INPUT_VALIDATION}   from './modules/input_validation'
include {EDA}                from './modules/eda'
include {PROCESSING_DATA}    from './modules/processing_data'
include {SPLITTING_DATA}     from './modules/splitting_data'

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

    } else if (params.workflow == 'data_processing') {

        INPUT_VALIDATION(
            params.dataset
        )

        EDA(
            INPUT_VALIDATION.out.data,
            INPUT_VALIDATION.out.metadata
        )

        PROCESSING_DATA(
            INPUT_VALIDATION.out.data,
            INPUT_VALIDATION.out.metadata
        )

        SPLITTING_DATA(
            PROCESSING_DATA.out.processed_data,
            params.test_size,
            params.seed
        )

    } else if (
        params.workflow != 'data_accession' &&
        params.workflow != 'data_processing'
        ) {
        
        error"""
        Unknown workflow: ${params.workflow}.
        Available workflows: data_accession, data_processing
        """
    }

}
