include {INPUT_VALIDATION}   from './modules/input_validation'
include {EDA}                from './modules/eda'
include {DATA_PROCESSING}    from './modules/data_processing'
include {SPLITTING_DATA}     from './modules/splitting_data'

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