# EDA (Exploratory Data Analysis)

## Type

Workflow

## Processes

- input_validation
- quality_integrity
- data_distribution
- feature_analysis
- pca

## Description

The EDA workflow aims to provide a comprehensive overview of the dataset, assess its quality and statistical properties, and identify potential issues or patterns that may influence subsequent data processing and model development. It supports an informed understanding of the data, helps identify relevant feature relationships, and highlights potential limitations or biases.

The workflow includes the following analyses:

### 1. Data Quality and Integrity

- Missing values
- NaN values
- Duplicated entries
- Outliers
- Data types
- Unique values and constant features

### 2. Data Distributions

- Class distributions
- Positive-to-negative (P/N) class ratio
- Number of participants and entries per participant
- Class distribution per participant

### 3. Feature Analysis

- Feature-feature correlations and multicollinearity
- Feature-label dependencies
- Feature redundancy (highly correlated features)
- Class-wise feature distributions

### 4. Principal Component Analysis (PCA)

- Investigation of class separation using the first two or three principal components

### 5. Model Assumptions and Statistical Properties

- Linearity
- Normality
- Homoscedasticity

## Quick Start

Korrekter Datensatz noch nicht hinterlegt; erfolgreicher Durchlauf mit eigenem Testdatensatz

	nextflow run main.nf --workflow eda -profile docker

## Parameters

| Parameter | Default | Process | Purpose |
| --- | --- | --- | --- |
| `--class_column` | | data_distribution, pca | Column with class label |
| `--participiant_column` | | data_distribution, pca | Column with participant ID |
| `--positive_label` | | data_distribution | Label of positive class |
| `--negative_label` | | data_distribution | Label of negative class |
| `--class_type` | | feature_analysis | Defining regression or classification problem |
| `--correlation_threshold` | 0.9 | feature_analysis | Correlation threshold for redundant features |
| `--pca_components` | 3 | pca | Number of computed principle components |