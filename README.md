# CCHS 2022 Diabetes Classification

A machine learning project that looks at how well diabetes status can be classified from the 2022 Canadian Community Health Survey, and specifically at how much the choice of predictors matters compared to the choice of model.

Live dashboard: https://cchs-2022-diabetes-ml.streamlit.app/

The dashboard is the easiest way to look through the project. It walks through the data, the feature selection reasoning, all six completed experiments, the model comparison, and the limitations, all pulled directly from the result files in this repo rather than retyped.

## Research question

How does the choice of information given to a model affect how well it can classify which CCHS respondents report having diabetes, and how does that compare to the effect of changing the model itself?

It's a cross-sectional problem, not a forecasting one. The survey records a person's characteristics and their diabetes status at the same point in time, so there's no time order in the data and no way to establish causation from it. The project classifies reported diabetes status as it exists in CCHS 2022, not future risk, and it isn't meant to diagnose anyone.

## Data

The project uses the 2022 CCHS Public Use Microdata File (PUMF) from Statistics Canada, which has 67,079 respondents and 255 variables. The outcome is `CCC_05`, self-reported diabetes status.

The raw microdata is not included in this repository. To reproduce the analysis you would need to obtain the CCHS 2022 PUMF yourself and follow Statistics Canada's applicable documentation and access conditions. The `data/` folder only has notes on the expected raw file, not the file itself.

A good part of the early work went into handling the CCHS coding scheme properly instead of just dropping missing values. Variables use survey-specific response codes such as 6 (valid skip) and 9 (not stated), and what a code means depends on the variable, not a rule that can be applied globally. Several modules also only apply to certain ages or regions, so a lot of what looks like missing data is actually structural rather than random. The sampling weight `WTS_M` was kept out of the feature set entirely, since it describes the survey design rather than the respondent.

## What I did

- explored the full 255-variable PUMF and worked out which codes, skips, and universes applied to which variables
- narrowed 255 columns down to a candidate pool of 216 by removing target-adjacent columns, administrative fields, and questionnaire routing flags
- built a set of feature conditions (A through F) using a mix of CCHS documentation, domain reasoning, and literature-informed predictor checks, to see how different groups of predictors affected classification
- ran controlled experiments across those conditions with Logistic Regression as the reference model
- settled on D2 (a compact core plus reported hypertension and reported high cholesterol) as the fixed feature set, and used it to compare Logistic Regression, Random Forest, and Gradient Boosting
- checked how stable the model comparison was with 5-fold cross-validation on the training portion only
- looked at which variables the three fitted models actually leaned on
- ran a fresh holdout check on a previously unused split, since the same test partition had been scored repeatedly across experiments A through D2

Two parts of the original plan were never carried through: a 35+ clinical-history condition (D3) and adult-specific smoking and physical-activity conditions (E1, E2). They are not part of the results below and shouldn't be read as completed work.

Experiment F tried a wider set of 16 documented variables with an L1-penalized logistic regression as a screening step, to see if it would drop any of them. It kept all 16. So F is not evidence that automatic feature selection worked here, it's a wider representation that happened to score well, not a leaner one.

## Models and evaluation

Every condition used a stratified train/validation/test split (42,394 / 10,599 / 13,249 rows) with preprocessing fit on the training data only. The model and the classification threshold were both chosen on the validation set, by sweeping thresholds from 0.10 to 0.90 and keeping the one with the best F1. The test set was only scored once those settings were locked.

Diabetes cases are about 9% of the modelling population, so accuracy alone is a poor way to judge these models. A model that always predicts "no" would already score around 0.91 while finding nobody. Logistic Regression and Random Forest used `class_weight="balanced"`. Gradient Boosting doesn't have that option, so it was given balanced sample weights instead through `compute_sample_weight`.

For the model comparison on the fixed D2 features, hyperparameters came from small predefined sets checked on validation data, not an exhaustive search: Random Forest tried 3 combinations of tree count and depth, Gradient Boosting tried 2 combinations of tree count and learning rate, and Logistic Regression kept its existing configuration. No model was picked as a winner based on test-set performance.

## Results

Changing which features the model could see moved F1 by about 0.05 between the C and D2 conditions, and moved ROC-AUC from 0.774 to 0.827 across the completed conditions. That's a bigger swing than anything that came from changing the algorithm.

On the fixed D2 feature set, the three models ended up close together on the test set:

| Model | Threshold | F1 | ROC-AUC | PR-AUC |
|---|---|---|---|---|
| Logistic Regression | 0.68 | 0.360 | 0.814 | 0.289 |
| Random Forest | 0.68 | 0.357 | 0.811 | 0.276 |
| Gradient Boosting | 0.70 | 0.365 | 0.815 | 0.286 |

The F1 spread across all three is 0.008, small enough that no model class clearly wins. Gradient Boosting edges out on F1, ROC-AUC, and precision, Logistic Regression leads on recall and PR-AUC, and Random Forest has the lowest log loss. Logistic Regression was kept as the reference model afterward mostly because it's simpler and its coefficients can be read directly, not because it scored best on the test set.

5-fold cross-validation on the training portion (StratifiedKFold, random_state=42) showed the three models' error bars overlapping on ROC-AUC and PR-AUC, with a mean ROC-AUC spread of about 0.003 between models, smaller than the fold-to-fold variation within any single model. Age, reported hypertension, reported high cholesterol, and BMI class came out as the top variables for all three model classes once importances were aggregated back to the original CCHS variables, though Logistic Regression coefficients and tree-based impurity importance sit on different scales and can only be compared in rank order within each model, not across models.

One limitation surfaced partway through the project: experiments A through D2 were all scored against the exact same test partition, and those results were visible while deciding what to try next, which makes the sequence more of an iterative development process than five clean final evaluations. To check whether the conclusions depended on that one split, the D2 models were re-fit on a fresh train/validation/test split (a different random seed) using the exact same configurations and already-locked thresholds, then scored once. Every model scored slightly higher on the fresh split, the three models stayed close together, and the ranking pattern from before held up. It's supplementary confirmation on the same survey, not external validation.

## What this doesn't show

The classification here stays within a single CCHS cycle. Nobody's future diabetes risk is being predicted, nobody is being diagnosed, and since everything is measured at one point in time, none of the variables can be said to cause diabetes. The CCHS survey weights and bootstrap variance procedure aren't applied either, so nothing here is a population estimate, and none of it has been checked against another survey cycle or dataset.

## Repository

```
notebooks/   12 executed notebooks and their result CSVs, from the initial dataset audit through the fresh-holdout check
dashboard/   Streamlit app that walks through the data, experiments, and results
data/        notes on the expected raw data file (the file itself is not included)
```

Every number shown in the dashboard is read directly from the result CSVs in `notebooks/`, so any figure there can be traced back to the file it came from.

## Reproducibility

To run the dashboard locally:

```bash
pip install -r requirements.txt
streamlit run dashboard/app.py
```

To rerun the notebooks you'll need the CCHS 2022 PUMF yourself, since the raw file isn't in this repository. See `data/README.md` for what the notebooks expect it to look like.
