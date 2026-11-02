## Amelie Pitch 3: Distinguishing Parkinson's from similar movement disorders with a smartwatch

**Problem**
Parkinson's disease is often misdiagnosed, especially early on and in patients with tremor. Conditions like essential tremor look similar but need different treatment. There is no approved blood test, and confirmatory tests (DaTscan, CSF alpha-synuclein) are expensive or invasive.

**Research question**
Can smartwatch movement data from a few minutes of standardised tasks distinguish Parkinson's disease from other movement disorders, not only from healthy controls? Which tasks and features carry the most diagnostic information?

**Data**
- Parkinson's Disease Smartwatch dataset (PADS), PhysioNet, open access
- Groups: Parkinson's, differential diagnoses (e.g. essential tremor), healthy controls
- Apple Watches on both wrists (accelerometer + gyroscope) during short standardised tasks (e.g. resting, arms extended, finger-to-nose), plus a non-motor symptom questionnaire
- Exact sample sizes, task list and licence to verify on PhysioNet

**Methods**
- Segment by task and wrist
- Features: tremor frequency and amplitude, rest vs. postural tremor, left-right asymmetry, movement smoothness
- Logistic regression and gradient boosting; optional 1D CNN for comparison
- Two tasks: Parkinson's vs. healthy (easy) and Parkinson's vs. differential diagnoses (the clinically relevant one)
- Person-wise cross-validation

**Evaluation & explainability**
Balanced accuracy, sensitivity, specificity, AUC. Rest vs. postural tremor and asymmetry are what neurologists check in the clinical exam, so feature importance (e.g. SHAP) can be compared directly with clinical reasoning.

**Innovation**
Low-cost screening with a widely available device, as triage before referral to a specialist and more expensive tests.

**Main limitations**
Differential diagnosis group may be small and mixed; data from one clinic; a false Parkinson's diagnosis has serious consequences, so the tool should support, not replace, specialists.

**Links**
- PADS dataset: https://physionet.org/content/parkinsons-disease-smartwatch/1.0.0/
