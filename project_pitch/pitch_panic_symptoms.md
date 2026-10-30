# Predicting panic attacks

## Objective
Investigate whether wearable-derived physiological and behavioral data can be used to identify patterns associated with panic symptoms. The project aims to develop an exploratory machine learning prototype that detects potential indicators of panic symptoms and could eventually support early interventions through wearable devices, for example by recommending relaxation exercises or other coping strategies.

## Dataset
https://openesmdata.org/datasets/0017_jang/

## Methods and Models
Since the dataset contains a relatively low number of features and participants, I would suggest to start with a classical statistical ML approach instead of a foundation model. A decision tree or logistic regression could be used as a baseline and compared to XGBoost, SVM or Random Forest model.