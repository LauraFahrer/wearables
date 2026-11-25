include {CHECKSUM_CALCULATION}   from './modules/checksum_calculation'

include {INPUT_VALIDATION}       from './modules/input_validation'
include {EDA}                    from './modules/eda'
include {REPORT}              from './modules/report'

include {PROCESSING_DATA}        from './modules/processing_data'
include {SPLITTING_DATA}         from './modules/splitting_data'

include {MODEL_TUNING}           from './modules/model_tuning'

workflow {

    if (params.workflow == 'compute_checksum') {

        CHECKSUM_CALCULATION(
            file(params.dataset),
            params.dataset_id
        )

    } else if (params.workflow == 'eda') {

        INPUT_VALIDATION(
            file(params.dataset),
            file(params.metadata)
        )

        EDA(
            file(params.dataset),
            INPUT_VALIDATION.out.success
        )

        REPORT(
            EDA.out.success,
            EDA.out.workflow
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

    } else if (params.workflow == 'model_tuning') {

        MODEL_TUNING(
            file(params.train_data)
        )

    } else if (
        params.workflow != 'compute_checksum' &&
        params.workflow != 'eda' &&
        params.workflow != 'data_processing' &&
        params.workflow != 'model_tuning'
        ) {
        
        error"""
        Unknown workflow: ${params.workflow}.
        Available workflows: compute_checksum, eda, data_processing, model_tuning
        """
    }
}
