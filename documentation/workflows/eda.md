---
type: workflow
processes:
    - input_validation
    - quality_integrity
    - data_distribution
    - feature_analysis
    - pca
---

# EDA (Exploratory Data Analysis)

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