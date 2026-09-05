# CCHS 2022 Diabetes Classification

A machine-learning research project using the 2022 Canadian Community Health Survey (CCHS) Public Use Microdata File (PUMF) to investigate the classification of diabetes status from demographic, anthropometric, socioeconomic, behavioural, contextual, and health-related information.

## Project Overview

This project examines how different groups of predictors contribute to diabetes classification in the 2022 CCHS.

The work is structured as a sequence of controlled experiments rather than a single model-building exercise. The feature-selection process combines:

- CCHS documentation and variable applicability
- domain-based reasoning
- literature-informed predictor verification
- controlled feature-block experiments
- data-driven feature selection

The goal is to understand not only how well different models perform, but also which information changes performance, where models fail, and what limitations arise from the survey structure and available variables.

## Dataset

The project uses the **2022 Canadian Community Health Survey (CCHS) Public Use Microdata File (PUMF)**.

The PUMF contains:

- **67,079 respondents**
- **255 variables**

The diabetes outcome is represented by `CCC_05`.

The CCHS data contain survey-specific response codes, valid skips, and population restrictions. These are interpreted using the official CCHS documentation rather than applying a single global missing-value rule.

The CCHS sampling weight (`WTS_M`) is not treated as an ordinary machine-learning predictor.

### Data availability

The raw CCHS microdata are **not included in this repository**.

The `data/` directory contains documentation only. Users who wish to reproduce the analysis should obtain the appropriate CCHS 2022 PUMF and follow the official Statistics Canada documentation and access conditions.

## Research Workflow

The project is organized into the following stages:

1. Full-dataset exploration and structural inspection
2. Data-quality and coding investigation
3. Survey-universe and module-applicability analysis
4. Candidate-pool construction
5. Documentation- and domain-guided feature selection
6. Literature-informed feature verification
7. Controlled feature-set experiments
8. Model training and evaluation
9. Failure analysis and interpretation

The feature-selection process distinguishes between broadly applicable predictors and variables that require separate population-specific experiments because of age, geography, questionnaire-path, or module restrictions.

## Planned Experimental Structure

The modelling experiments are organized around several feature conditions:

| Condition | Purpose |
|---|---|
| A | Historical baseline feature set |
| B | Preliminary documentation/domain-guided feature set |
| C | Literature-informed broadly applicable core |
| D1 | Core + hypertension |
| D2 | Core + hypertension + high cholesterol |
| D3 | 35+ clinical-history experiment |
| E1 | Adult smoking experiment |
| E2 | Restricted adult physical-activity experiment |
| F | Automatic feature-selection experiment |

These conditions are intended to isolate the contribution of different information blocks rather than simply maximize the number of predictors.

## Modelling Approach

The primary models are:

- Logistic Regression
- Random Forest
- Gradient Boosting

The general evaluation protocol uses a train/validation/test framework with training-only preprocessing and validation-based model and threshold decisions.

The final test set is reserved for locked evaluation.

Evaluation includes:

- Accuracy
- Precision
- Recall
- F1-score
- ROC-AUC
- PR-AUC
- Confusion matrix

Failure analysis is also used to examine false positives, false negatives, model disagreements, and difficult prediction cases.

## Repository Structure

```text
cchs-2022-diabetes-ml/
├── README.md
├── requirements.txt
├── notebooks/
│   └── 01_—_Full_Dataset_Exploration_&_Preliminary_Feature_Selection.ipynb
    └── 02_—_Controlled_Feature_Experiments_Setup.ipynb
├── docs/
├── results/
├── src/
└── data/
    └── README.md
