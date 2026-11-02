include {DATA_DOWNLOAD}      from './modules/data_download'
include {INPUT_VALIDATION}   from './modules/input_validation'

workflow {

    DATA_DOWNLOAD(input.dataset)

    INPUT_VALIDATION(
        DATA_DOWNLOAD.out.
    )
}