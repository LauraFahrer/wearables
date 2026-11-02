include {INPUT_VALIDATION}   from './data_processing/input_validation'
include {EDA}                from './data_processing/eda'
include {DATA_PROCESSING}    from './data_processing/data_processing'
include {SPLITTING_DATA}     from './data_processing/splitting_data'

workflow {
    INPUT_VALIDATION(params.input)

    EDA(
        INPUT_VALIDATION.out.
    )

    DATA_PROCESSING(
        EDA.out
    )

    SPLITTING_DATA(
        DATA_PROCESSING.out
    )
}