## Amelie Pitch 2 : Predicting attention lapses from eye signals, towards attention-aware glasses for ADHD

**Problem**
Attention in children with ADHD fluctuates strongly. Current support can't react to the moment attention drops. Glasses with eye tracking could detect such moments and give a cue to refocus, but it is unclear whether eye signals predict lapses early enough.

**Research question**
Do eye-tracking features that glasses could also measure (pupil size, blinks, gaze stability) predict attention lapses (errors, slow responses) before they happen, in children with and without ADHD?

**Data**
- Pupil size and eye-tracking dataset from ADHD children (Scientific Data, 2019): 28 children with ADHD (17 also on and off methylphenidate), 22 controls
- Working memory task with distractors, 160 trials per session; correct/incorrect and reaction time per trial
- Screen-based eye tracker (1000 Hz), public on Figshare

**Methods**
- Lapse = error or slowest 10–15% of each child's responses
- Features only from the pre-trial fixation period: pupil baseline, blinks, gaze stability
- Simulate glasses by downsampling; logistic regression and gradient boosting
- Leave-one-child-out validation

**Evaluation & explainability**
AUC, precision at a fixed alert rate; pupil size reflects arousal (noradrenaline system), so feature importance can be compared with established neuroscience.

**Innovation & transfer**
Non-drug, in-the-moment support for ADHD; same approach could later apply to daytime sleepiness or fatigue (e.g. MS, long COVID).

**Main limitations**
Small sample, errors are a noisy lapse proxy, transfer to real glasses only simulated.

**Links**
- Dataset: https://doi.org/10.6084/m9.figshare.7218725.v3
- Paper: https://doi.org/10.1038/s41597-019-0037-2
