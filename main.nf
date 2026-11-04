include {DATA_DOWNLOAD}          from './modules/data_download'
include {CHECKSUM_CALCULATION}   from './modules/checksum_calculation'

include {INPUT_VALIDATION}       from './modules/input_validation'
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

    } else if (params.workflow == 'data_processing') {

        INPUT_VALIDATION(
            file(params.dataset_file)
            file(params.checksum_file)
        )

        EDA(
            INPUT_VALIDATION.out.validated_datadata,    // wird nicht ausgegeben
            INPUT_VALIDATION.out.metadata   // wird nicht ausgegeben
        )

        PROCESSING_DATA(
            INPUT_VALIDATION.out.validated_data,    // wird nicht ausgegeben
            INPUT_VALIDATION.out.metadata   // wird nicht ausgegeben
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
