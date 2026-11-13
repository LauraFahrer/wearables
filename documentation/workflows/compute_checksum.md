---
type: workflow
processes:
    - checksum_calculation
---

# Compute Checksum

## Description

The data accession workflow  calculates a SHA-256 checksum and saves it with relevant dataset metadata for subsequent verification during the exploratory data analysis and data processing workflow.

## Quick Start

    nextflow run main.nf --workflow compute_checksum -profile docker

## Parameters

| Parameter | Default | Purpose|
| --- | --- | --- | ---|
| `--workflow` | required | Workflow selection |
| `--dataset` | path to 'pupil_adhd_dataset.mat' | Path to dataset |
| `--dataset_id` | 'pupil_adhd' | `data_processing` | Dataset identifier in dataset.yml |