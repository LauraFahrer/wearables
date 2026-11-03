include {INPUT_VALIDATION}   from './modules/input_validation'
include {EDA}                from './modules/eda'
include {PROCESSING_DATA}    from './modules/processing_data'
include {SPLITTING_DATA}     from './modules/splitting_data'

workflow {

    if (params.workflow == 'data_accession') {

        // to be defined

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
            PROCESSING_DATA.out.processed_data
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
