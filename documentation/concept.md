# Concept

## Overview

1. Technical Setup
2. Clinical Problem Definition
3. Data Assessment & Preparation
4. Requirements & Success Criteria
5. Model Selection
6. Prototype Implementation
7. Testing & Evaluation
8. Clinical, Ethical & Regulatory Assessment

## 1. Technical Setup

- blocked main branch to keep it stable
- container (https://www.datacamp.com/blog/docker-container-images-for-machine-learning-and-ai)
- dataflow distribution with Nextflow
- nf-test
- Continuous Integration

## 2. Clinical Problem Definition

- identify suitable datasets (https://openesmdata.org/datasets/)
- passive sensors included
- difficult: migraine, stress detection, mild cognitive impairment

## 3. Data Assessment & Preparation

- document source, collection method, accessibility
- EDA: duplicates, outliers, missing values, class distribution, feature correlation, ...
- data processing (data integration if multiple sources (common data model), cleaning, transformation to ML features, documentation of data transformation)
- representativeness of intended population
- potential data bias
- data splitting
- prevent/ identify risks of data leakage?
- independent dataset for external evaluation if available


## 4. Requirements & Success Criteria

- define requirements and success criterias beforehand, document appropriately
- specify (and test) input/output formats
- specify/justify minimum performance thresholds


## 5. Model Selection

- simple baseline model
- justified model selection (are similar approaches available?)
- document design


## 6. Prototype Implementation

- input validation and basic error handling
- UI/ interaction mechanism
- workflow/dataflow
- model integration
- feature selection
- model training:
    - (nested) cross-validation for model selection (and hyperparameter tuning)
    - final model training on whole train set
    - freeze model parameters
- interpretablility: feature importance, dimensionality reduction, ...
- interpretable output


## 7. Testing & Evaluation

- define metrices
- internal evaluation on splitted test set
- external evaluation on independend dataset (generalization)
- comparison to baseline model
- analysis of failures, limitations
- asses robustness?
- evaluation report