process INPUT_VALIDATION {

    container 'python:3.12-slim'

    input:
    val dataset

    output:
    path "*.tsv", emit: data
    path "*.json", emit: metadata

    script:
    """

    // python script here

    """

    stub:
    """

    touch data.tsv
    echo '{}' > metadata.json

    """
}