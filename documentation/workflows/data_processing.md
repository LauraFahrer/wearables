---
type: workflow
processes:
    - input_validation
    - processing_data
    - splitting_data
---

# Data Processing

## Description

The data processing workflow prepares the dataset for subsequent model development. Input validation verifies the integrity of the input dataset using its stored SHA-256 checksum and checks its basic file structure and format. Data processing applies the necessary processing steps to generate ML features for analysis and model training. Depending on the dataset and its requirements, this step may be further divided into separate processes. Finally, data splitting divides the processed dataset into appropriate subsets for model development and evaluation, ensuring that the splitting strategy accounts for the characteristics of the data (e.g. participant-based splitting for wearable data).