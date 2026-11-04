process INPUT_VALIDATION {

    container 'python:3.12-slim'

    input:
    path dataset
    path checksum

    output:
    path "validation.success", emit: success

    script:
    """

    python ${projectDir}/bin/input_validation.py \
        --input ${dataset} \
        --checksum ${checksum} \

    touch validation.success

    """

    stub:
    """
    echo "Input validation successful."

    """
}