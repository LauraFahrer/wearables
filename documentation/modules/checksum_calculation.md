---
type: module
input:
    - raw_data
    - dataset_id
output:
    - metadata
image:
    - python:3.12-slim
parent:
    - DATA_DOWNLOAD
child:
tools:
---

# CHECKSUM_CALCULATION

## Description

The CHECKSUM_CALCULATION module runs the python script calculate_checksum.py and calculates the SHA-256 checksum of the downloaded dataset and saves it together with relevant dataset metadata in a JSON file. This checksum is later used to verify data integrity during input validation.