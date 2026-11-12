process REPORT {

    container 'python:3.12-slim'

    input:
    path success
    val workflow

    script:
    """

    python ${projectDir}/bin/report.py ${workflow}

    """

    stub:
    """
    echo "Workflow completed successfully."
    """
}