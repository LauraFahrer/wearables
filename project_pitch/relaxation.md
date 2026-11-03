## Estimating relaxation during paced breathing from cardiac signals

**Problem**

Wearable devices could support breathing exercises by monitoring users’ relaxation responses. However, a lower heart rate or higher heart rate variability (HRV) does not necessarily mean that a person feels more relaxed. It remains important to assess whether cardiac measurements provide useful information about subjective relaxation beyond the instructed breathing rate.

**Research question**

Can cardiac features estimate self-reported relaxation during paced breathing in previously unseen participants? Does adding HRV improve prediction compared with using heart rate and breathing condition alone?

**Data**

- Dataset accompanying *Lower breathing frequencies in personalized slow-paced breathing enhance relaxation and reduce arousal*.
- 42 participants included in the original analysis.
- Randomized crossover design: each participant completed three five-minute breathing conditions at 40%, 60%, and 80% of their spontaneous breathing frequency.
- Physiological measurements and self-reported relaxation and perceived stress.
- Public OSF repository contains anonymized aggregated Excel tables, processed HRV data, raw physiological recordings, and R analysis scripts.
- Exact variables, scoring, missingness, reuse terms, and participant–condition linkage still need verification.

**Methods**

- Start with the processed tables; use raw recordings only if additional feature extraction is needed.
- Primary outcome: self-reported relaxation score for each breathing condition.
- Compare a training-set mean baseline, a breathing-condition-only model, a model adding heart rate, and a model additionally including HRV, initially RMSSD.
- Start with regularized linear regression to limit model complexity.
- Use leave-one-participant-out validation, keeping all conditions from each participant together. Perform preprocessing and any tuning using training participants only.

**Evaluation & explainability**

MAE as the primary metric and out-of-sample R² as a secondary metric. Compare errors between models and quantify uncertainty at the participant level. Explore cases where cardiac responses and reported relaxation disagree.

**Potential contribution & application**

Assess whether cardiac features add useful information about subjective relaxation beyond breathing condition. This could inform future wearable feedback systems for breathing exercises. Overlap with the original paper and analysis scripts will be checked before finalizing the contribution.

**Main limitations**

Small sample with repeated measurements from healthy university students. Breathing directly affects HRV, so increased HRV alone cannot establish relaxation or anxiety reduction. Transfer from laboratory measurements to wrist-worn devices remains untested. The project evaluates offline relaxation estimation; it does not test personalized breathing recommendations or clinical treatment effects.

**Links**

- Paper: https://pmc.ncbi.nlm.nih.gov/articles/PMC13241781/
- Project: https://osf.io/yqu9d/
- Data tables and analysis scripts: https://osf.io/h58xc/
