process EDA {

    container 'python:3.12-slim'

    input:
    path data
    path metadata

    output:
    path "*.tsv", emit: eda_file

    script:
    """

    // python script here

    """

    stub:
    """
    echo -e "feature\\tvalue\\nmean\\t0.5\\nstd\\t0.2" > eda_results.tsv
    """
}