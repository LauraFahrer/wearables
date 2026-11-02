# Predicting panic attacks

## Objective
Investigate whether wearable-derived physiological and behavioral data can be used to identify patterns associated with panic symptoms. The project aims to develop an exploratory machine learning prototype that detects potential indicators of panic symptoms and could eventually support early interventions through wearable devices, for example by recommending relaxation exercises or other coping strategies.

## Phase 1: Supervised Learning and Hypothesis Generation

Analyze a publicly available dataset containing wearable-derived features and panic-related labels to investigate potential associations between physiological and behavioral patterns and impending panic symptoms. Develop and evaluate classical machine learning models to identify relevant features and assess their predictive potential.

### Dataset

https://openesmdata.org/datasets/0017_jang/

The dataset contains longitudinal data from 43 participants, including panic-related measures and passive sensor data. Its relatively small sample size and daily sampling frequency will be considered when defining the research scope and evaluation strategy.

### Methods and Models

Since the dataset contains a relatively low number of features and participants, I would suggest to start with a classical statistical ML approach instead of a foundation model. A decision tree or logistic regression could be used as a baseline and compared to XGBoost, SVM or Random Forest model.

## Phase 2: Unsupervised Pattern Discovery

Explore whether patterns identified in Phase 1 can also be observed in larger, independent wearable dataset without panic-related labels. Apply unsupervised learning techniques, such as clustering or anomaly detection to identify recurring physiological and behavioral patterns. Investigate whether these patterns are consistent with the findings from Phase 1, while acknowledging that their association with panic symptoms cannot be confirmed without appropriate labels or external validation.

### Dataset

Not defined yet.

### Methods and Models

K-Means or Hierarchical Clustering.