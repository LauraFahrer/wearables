process PROCESSING_DATA {
    container 'python:3.12-slim'

    input:
    path data
    path metadata

    output:
    path "*_processed.tsv", emit: processed_data
    

    script:
    """

    // python script here

    """

    stub:
    """
    echo -e "timestamp\\theart_rate\\tsteps\\n2026-01-01 10:00:00\\t75\\t120\\n2026-01-01 10:01:00\\t78\\t135" > processed_data.tsv
    """
}