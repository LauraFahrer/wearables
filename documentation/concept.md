# Concept

## Overview

	1. Clinical Problem Definition
	2. Data Assessment & Preparation
	3. Requirements & Success Criteria
	4. Model Selection
	5. Prototype Implementation
	6. Testing & Evaluation
	7. Clinical, Ethical & Regulatory Assessment

## 1. Clinical Problem Definition

- identify suitable datasets (https://openesmdata.org/datasets/)
- passive sensors included
- difficult: migraine, stress detection, mild cognitive impairment

## 2. Data Assessment & Preparation

- document source, collection method, accessibility
- EDA: duplicates, outliers, missing values, class distribution, feature correlation, ...
- data processing (data integration if multiple sources (common data model), cleaning, transformation to ML features, documentation of data transformation)
- representativeness of intended population
- potential data bias
- data splitting
- prevent/ identify risks of data leakage?
- independent dataset for external evaluation if available


## 3. Requirements & Success Criteria

- define requirements and success criterias beforehand, document appropriately
- specify (and test) input/output formats
- specify/justify minimum performance thresholds


## 4. Model Selection

- simple baseline model
- justified model selection (are similar approaches available?)
- document design


## 5. Prototype Implementation

- input validation and basic error handling
- UI/ interaction mechanism
- workflow/dataflow
- model integration
- feature selection
- model training:
    - (nested) cross-validation for model selection (and hyperparameter tuning)
    - final model training on whole train set
    - froze model parameters
- interpretablility: feature importance, dimensionality reduction, ...
- interpretable output


## 6. Testing & Evaluation

- define metrices
- internal evaluation on splitted test set
- external evaluation on independend dataset (generalization)
- comparison to baseline model
- analysis of failures, limitations
- asses robustness?
- evaluation report