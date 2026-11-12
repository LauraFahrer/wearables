---
type: workflow
processes:
    - data_download
    - checksum_calculation
---

# Data Accession

## Description

The data accession workflow retrieves the selected dataset from its specified source based on the dataset configuration. It stores the downloaded raw data locally and calculates a SHA-256 checksum to ensure data integrity. The checksum and relevant dataset metadata are saved for subsequent verification during the data processing workflow.