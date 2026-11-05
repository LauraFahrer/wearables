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

To run the stub-tests with Docker:

    nextflow run main.nf --workflow <WORKFLOW> -profile docker -stub-run

(not working currently):

Run a workflow with the included test-profile dataset with Docker:

    nextflow run main.nf --workflow <WORKFLOW> -profile test, docker

To download or analyze a specific dataset with Docker:

    nextflow run main.nf --workflow <WORKFLOW> --dataset <DATASET> -profile docker

## Parameters

| Parameter | Default | Workflow | Purpose|
| --- | --- | --- | ---|
| `--workflow` | required | `data_accession` `data_processing` `...` | Workflow selection |
| `--dataset` | `test` | `data_processing` `...` | Dataset identifier |
| `--test-size` | 0.2 | `data_processing` | Size of test set |
| `--seed` | 42 | `data_processing` | Seed value |
