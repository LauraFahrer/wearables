process CHECKSUM_CALCULATION {

    container 'python:3.12-slim'

    publishDir "${projectDir}/data/metadata", mode: 'copy'

    input:
    path raw_data
    val dataset_id

    output:
    path "*.json", emit: metadata

    script:
    """

    python ${projectDir}/bin/calculate_checksum.py \
        ${raw_data} \
        --dataset ${dataset_id}

    """

    stub:
    """
    echo '{"sha256": "stub"}' > ${dataset_id}_metadata.json
    """
}