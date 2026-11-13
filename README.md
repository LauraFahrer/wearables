# Wearables

## Contents
This repository contains the code, documentation and research materials for the development of an AI prototype in healthcare and medical science based on wearable device data.

The specific research topic and clinical application are still being defined and will be established as part of the initial project phase. Further information, objectives and implementation details will be added as the project progresses.

## Contribution

The main branch of this repository is protected and should always contain a stable version of the project. To make changes, create a separate branch for each new feature, task or bug fix. Once the work is completed and tested, submit a Pull Request to merge the changes into main. After a successful merge, please delete your branch if GitHub indicates that it can be safely deleted.

## Project Card

https://www.overleaf.com/project/6ae46943efe3bea703a763b6/share#6fa714febdd700efa2c7b9681550de91833eead9a07d220b

## Datasets

https://openesmdata.org/datasets/

## Literature

https://link.springer.com/book/10.1007/978-3-031-39355-6

## Prerequisities

- Conda
- Nextflow
- Docker

## Quick Start

Whenever a new dataset is downloaded, the compute_checksum workflow must be executed first. This is necessary because the INPUT_VALIDATION process performs a checksum verification at the beginning of every other workflow to ensure data integrity.

To register a new dataset, add its dataset ID <DATASET_ID> and filename <DATASET> manually to datasets.yml configuration file as shown below. The compute_checksum workflow generates a metadata file <DATASET_ID.json> in <${projectDir}/data/metadata> containing the corresponding hash value <CHECKSUM>, which must also be added manually to datasets.yml.

    datasets:
        <DATASET_ID>:
            filename: <DATASET>
            checksum: <CHECKSUM>

The project supports several different workflows. The parameters required for each workflow are listed in Table XY of section 'Parameters'. For information on workflow-specific parameters, please refer to the corresponding workflow documentation in <${projectDir}/documentation/workflows>.

A workflow can be started using the default parameters and Docker with the following command:

    nextflow run main.nf --workflow <WORKFLOW> --dataset <DATASET> -profile docker

!!CHECK PARAMETER AGAIN!!

To run the stub-tests with Docker use the following command:

    nextflow run main.nf --workflow <WORKFLOW> -profile docker -stub-run

## Parameters

| Parameter | Default | Purpose|
| --- | --- | ---|
| `--workflow` | required | Workflow selection |
| `--dataset` | path to 'pupil_adhd_dataset.mat' | Path to dataset |
| `--dataset_id` | 'pupil_adhd' | Dataset identifier in dataset.yml |
