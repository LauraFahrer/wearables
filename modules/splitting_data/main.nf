process SPLITTING_DATA {

    publishDir "${projectDir}/results/data_processing/splitted_data", mode: 'copy'

    container 'python:3.12-slim'

    input:
    path processed_data
    val test_size
    val seed

    output:
    path "train_data.tsv", emit: train_data
    path "test_data.tsv", emit: test_data

    script:
    """

    python ${projectDir}/bin/splitting_data.py \
        ${processed_data} \
        --test-size ${test_size} \
        --seed ${seed}

    """

    stub:
    """
    echo -e "timestamp\\theart_rate\\tsteps\\n2026-01-01 10:00:00\\t75\\t120\\n2026-01-01 10:01:00\\t78\\t135" > train_data.tsv
    echo -e "timestamp\\theart_rate\\tsteps\\n2026-01-01 10:00:00\\t75\\t120\\n2026-01-01 10:01:00\\t78\\t135" > test_data.tsv
    """
}