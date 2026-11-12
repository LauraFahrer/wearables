process INPUT_VALIDATION {

    container 'python:3.12-slim'

    input:
    path dataset
    path metadata

    output:
    path "validation.success", emit: success

    script:
    """

    python ${projectDir}/bin/input_validation.py \
        --input ${dataset} \
        --checksum ${metadata} \

    touch validation.success

    """

    stub:
    """
    touch validation.success

    """
}