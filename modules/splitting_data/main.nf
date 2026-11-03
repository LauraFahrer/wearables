process SPLITTING_DATA {

    container 'python:3.12-slim'

    input:
    path processed_data

    output:
    path "*.tsv", emit: train_data
    path "*.tsv", emit: test_data

    script:
    """

    // python script here

    """

    stub:
    """
    echo -e "timestamp\\theart_rate\\tsteps\\n2026-01-01 10:00:00\\t75\\t120\\n2026-01-01 10:01:00\\t78\\t135" > train_data.tsv
    echo -e "timestamp\\theart_rate\\tsteps\\n2026-01-01 10:00:00\\t75\\t120\\n2026-01-01 10:01:00\\t78\\t135" > test_data.tsv
    """
}