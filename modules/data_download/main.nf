process DATA_DOWNLOAD {

    container 'python:3.12-slim'

    publishDir "${projectDir}/data/raw_data", mode: 'copy'

    input:
    val dataset_id
    path datasets_config

    output:
    path "*.tsv", emit: raw_data

    script:
    """

    python ${projectDir}/bin/data_accession.py \
        --dataset ${dataset_id} \
        --config ${datasets_config}

    """

    stub:
    """
    echo -e "timestamp\\theart_rate\\tsteps\\n2026-01-01 10:00:00\\t75\\t120" > ${dataset_id}_dataset.tsv
    """
}