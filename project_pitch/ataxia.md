## Amelie Pitch 1: Sensitive gait monitoring in degenerative ataxia

**Problem**
Degenerative ataxias progress slowly. The clinical score (SARA) is coarse and only measured at clinic visits, so small changes over time or therapy effects are hard to detect.

**Research question (draft)**
Can IMU-based gait features, especially turning, estimate ataxia severity and detect changes over time more sensitively than SARA? Optionally: does a model trained on lab gait still work on everyday-life gait?

**Data**
- IMU recordings from the ataxia outpatient clinic (Hertie Institute), approval from Dr. Ilg pending
- Clinical labels: SARA scores, ideally with longitudinal follow-ups and healthy controls etc.
- Not public; access depends on approval without a new ethics procedure

**Methods**
- Segment walking bouts and turns from raw IMU signals
- Extract interpretable gait features (stride length, step width, variability, lateral deviation, turning speed)
- Regression (SARA) or classification (patient vs. control) with simple models (e.g. random forest, gradient boosting)
- Person-wise validation (leave-one-subject-out)

**Evaluation**
MAE and correlation with SARA, AUC for classification; for the lab-vs-everyday question, the performance drop between the two settings.

**Explainability**
Features are gait parameters that clinicians already use, so feature importance can be checked against clinical reasoning.

**Clinical use & innovation**
Objective monitoring between clinic visits and a more sensitive digital endpoint for clinical trials in rare diseases.

**Fallback if the ataxia data is not available**
- Adjusted question: Can foot sensor gait data distinguish different motor-neurodegenerative diseases from each other and from healthy controls?
- Data: Gait in Neurodegenerative Disease Database (PhysioNet), force-sensitive foot sensors, Parkinson's, Huntington's, ALS and healthy controls, public
  https://physionet.org/content/gaitndd/1.0.0/
- Same pipeline: stride-based features (stride time, swing/stance time, variability) → multiclass classification with person-wise validation
- Limitation: small sample and no ataxia patients
