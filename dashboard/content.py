"""
Explanatory text used across the dashboard.

Kept separate from layout code so the wording can be reviewed and edited without
touching any Streamlit logic.
"""

# --------------------------------------------------------------- framing (used everywhere)

FRAMING_IS = [
    "A cross-sectional classification of reported diabetes status",
    "Based on characteristics recorded in the same survey period",
    "A study of how feature choice affects classification",
    "A methodological study with stated limitations",
]

FRAMING_IS_NOT = [
    "Not a prediction of who will develop diabetes later",
    "Not a future-risk calculator or screening tool",
    "Not a diagnosis of any individual",
    "Not evidence that any variable causes diabetes",
]

FRAMING_WHY = (
    "The survey measures a person's characteristics and their diabetes status at the same "
    "moment. Nothing in the data records what came first, so no time order - and therefore "
    "no cause - can be established."
)

RESEARCH_QUESTION = (
    "How does the choice of information given to a machine-learning model affect how well "
    "it can classify which survey respondents report having diabetes?"
)

HEADLINE_FINDINGS = [
    ("Feature representation mattered substantially.",
     "Changing which variables the model could see moved F1 by 0.053 between feature "
     "conditions C and D2, and moved ROC-AUC from 0.774 to 0.827 across the completed "
     "conditions."),
    ("Reported hypertension and high cholesterol changed the trade-off.",
     "Adding CCC_80 and then CCC_90 improved several discrimination measures, but shifted "
     "the balance between precision and recall rather than improving everything at once."),
    ("The three model classes were broadly comparable.",
     "On the fixed D2 feature set the F1 spread across Logistic Regression, Random Forest "
     "and Gradient Boosting was 0.008 - far smaller than the effect of changing features."),
]

# ------------------------------------------------------------------------ metric glossary

METRIC_GLOSSARY = {
    "accuracy": (
        "How many predictions were correct overall.",
        "Useful as background only. Because about 91% of the modelling population does not "
        "report diabetes, a model that answers 'no' for everyone would already score 0.909 "
        "while finding nobody."),
    "precision": (
        "Of the people the model classified as having diabetes, how many actually belonged "
        "to the positive class?",
        "Precision can be pushed up simply by flagging fewer people, so it should always be "
        "read next to recall."),
    "recall": (
        "Of the people who actually belonged to the positive class, how many did the model "
        "find?",
        "Recall can be pushed to 1.0 by flagging everybody, which would make precision "
        "collapse."),
    "f1": (
        "A balance between precision and recall.",
        "F1 stays low if either side is poor, so it cannot be gamed by sacrificing one for "
        "the other. This project selects every classification threshold by maximising F1 on "
        "validation data."),
    "roc_auc": (
        "How well the model separates the two classes across possible thresholds.",
        "0.5 is no better than a coin flip and 1.0 is perfect ranking. Because it is computed "
        "across all thresholds, a good value does not guarantee good performance at the one "
        "threshold actually used."),
    "pr_auc": (
        "How well the model handles the positive class across possible thresholds.",
        "The most informative single metric here, because it ignores the large easy majority "
        "of true negatives. Random guessing at this project's 9.05% prevalence would score "
        "about 0.09."),
    "test_log_loss": (
        "How well the predicted probabilities themselves match the observed outcomes.",
        "Lower is better. It penalises confident wrong answers much more than hesitant ones, "
        "and comparing training with test values is a check for overfitting."),
    "log_loss": (
        "How well the predicted probabilities themselves match the observed outcomes.",
        "Lower is better. It penalises confident wrong answers much more than hesitant ones."),
}

# ------------------------------------------------------------------- "why did we do this?"

WHY = {
    "wts_m": (
        "Why was the sampling weight WTS_M excluded?",
        "WTS_M records how many people in Canada each respondent represents, so that survey "
        "estimates can be scaled to the population. It carries no health information about "
        "the person. Including it would let the model use the survey design as though it were "
        "a symptom. The cost of leaving it out is that these results are respondent-level "
        "machine learning, not survey-weighted population estimates."),
    "special_codes": (
        "Why not simply replace every 6 and 9 with missing?",
        "Because the same digit means different things on different variables. On some "
        "variables 9 is a legitimate 'not stated'; on others 6 means the question did not "
        "apply at all. Replacing them globally would delete real answers on some variables "
        "and, worse, would hide the fact that a 6 usually marks a structural skip. The "
        "project therefore defined the codes variable by variable."),
    "bmi": (
        "Why was BMI harmonised into a single variable?",
        "CCHS stores BMI in two age-specific variables. Using only the adult variable leaves "
        "every 12-17-year-old as a skip; using only the youth variable leaves 63,318 adults "
        "as skips. Putting both in as separate columns means each is mostly structural blanks. "
        "Combining them by age produces one feature that is defined for everyone."),
    "do_flags": (
        "Why were the DO... flags removed?",
        "The 31 'DO' columns are inclusion flags that record whether a survey section applied "
        "to a respondent. They describe the questionnaire's routing, not the person's health, "
        "and they can quietly encode who was eligible for a question, which correlates with "
        "age or region."),
    "balanced": (
        "Why use class_weight = 'balanced'?",
        "About 91% of the training data is negative, so the cheapest way for a model to be "
        "'right' most of the time is to lean heavily towards 'no' and ignore the rare positive "
        "cases. Balanced weighting makes mistakes on the rare class count for more during "
        "training. A side effect is that predicted probabilities shift upward, which is why "
        "the selected thresholds sit between 0.57 and 0.71 rather than near 0.50. Gradient "
        "Boosting has no class_weight setting, so balanced sample weights were used instead."),
    "threshold": (
        "Why is the threshold chosen on validation data?",
        "The model outputs a probability, and a threshold turns that into a yes/no decision. "
        "If the threshold were tuned on the test set, the reported score would be the best of "
        "many attempts on the very data meant to represent unseen people. Instead each "
        "experiment sweeps thresholds from 0.10 to 0.90 on validation data, keeps the value "
        "with the highest F1, locks it, and only then evaluates the test set once."),
    "models": (
        "Why compare several model classes?",
        "Part of the project showed that changing the features changed the score. Comparing "
        "algorithms on a frozen feature set answers the natural follow-up question: would "
        "changing the algorithm change it more, less, or about the same? Holding the features, "
        "population, split and threshold procedure constant isolates the effect of the model."),
    "cv": (
        "Why perform 5-fold cross-validation?",
        "A single train/validation split could flatter or penalise a model by luck. Five-fold "
        "cross-validation splits the training portion five ways and scores each part in turn, "
        "so the spread across folds shows how sensitive the result is to how the data happened "
        "to be divided. Only the training portion was used, leaving validation and test alone."),
    "fresh": (
        "Why run a fresh holdout?",
        "Experiments A through D2 all scored the same 13,249-row test partition, and those "
        "results were visible while deciding what to try next. Re-dealing the split with an "
        "unused seed and re-applying the already-frozen settings checks whether the original "
        "conclusions depended on that one particular partition."),
    "logreg": (
        "Why keep Logistic Regression as the reference model?",
        "Not because it won. Test results were never used to select a model, since that would "
        "turn the final score into a best-of-three. Logistic Regression is retained because its "
        "performance is broadly comparable to the tree-based alternatives, it is simpler, and "
        "its coefficients can be read directly - which is what makes the interpretability "
        "analysis possible."),
    "rhc": (
        "Why was RHC_05 held out?",
        "Diabetes is diagnosed by a health professional, so someone with a regular provider is "
        "more likely to have been tested and told. Including that variable would quietly shift "
        "the question from 'who reports diabetes?' towards 'who has contact with the health "
        "system?'. This is a methodological leakage and prediction-pathway concern - the "
        "project did not demonstrate leakage and does not claim to have."),
    "why_not_255": (
        "Why can't all 255 columns just be fed to a model?",
        "Four separate reasons. Administrative columns such as a record number say nothing "
        "about health and could be memorised. Inclusion flags describe the questionnaire. "
        "Special codes like 6 and 9 become nonsense quantities if treated as real values. And "
        "many variables only apply to certain ages or regions, so most rows are structurally "
        "blank rather than missing."),
}

# ------------------------------------------------------------------ experiment narratives

EXPERIMENTS = {
    "A": dict(
        name="Experiment A - the baseline",
        question="Does a hand-picked set of 11 broadly available variables classify reported "
                 "diabetes status usefully?",
        changed="The first controlled baseline. Everything after this is measured against it.",
        interpretation=(
            "A finds most of the true cases - recall 0.690 - but pays for it with 3,324 false "
            "alarms, so precision is only 0.199. Its accuracy of 0.721 is actually lower than "
            "the 0.909 a do-nothing model would score, because balanced weighting pushes it to "
            "flag many people. That made it obvious early that accuracy could not be the "
            "headline metric."),
        caveat=(
            "A uses the adult BMI variable HWTDGISW directly rather than a harmonised BMI, so "
            "respondents aged 12-17 have no usable BMI value in this condition."),
        comparator=None),
    "B": dict(
        name="Experiment B - a different representation",
        question="Does a different hand-picked representation of the same size change "
                 "performance?",
        changed="Same framework and same number of variables as A, but a different selection. "
                "This is the first condition to use the harmonised BMI_CLASS.",
        interpretation=(
            "Five of the six metrics improved relative to A, but recall fell from 0.690 to "
            "0.598. B finds 110 fewer true cases than A while raising 966 fewer false alarms. "
            "It sits at a different point on the precision/recall trade-off, helped by its "
            "higher locked threshold of 0.635."),
        caveat=(
            "B is not 'better than A in every way'. Describing it that way hides the recall "
            "loss, which is the metric most people would care about if the tool were ever used "
            "to find cases."),
        comparator="A"),
    "C": dict(
        name="Experiment C - the compact reference",
        question="What does a deliberately small, literature-informed core achieve on its own?",
        changed="Reduced to seven broadly applicable variables so that later additions can be "
                "attributed cleanly.",
        interpretation=(
            "C scores slightly worse than B on most measures, which is expected and acceptable. "
            "Its job is not to win: it is to be a small, stable baseline that D1 and D2 can be "
            "compared against one variable at a time."),
        caveat=(
            "C is a reference condition, not an attempt at the best possible model. Reading its "
            "lower scores as a failure would misread its purpose."),
        comparator=None),
    "D1": dict(
        name="D1 - adding reported high blood pressure",
        question="What happens when one reported health condition is added to the compact core?",
        changed="C plus CCC_80, reported high blood pressure.",
        interpretation=(
            "Accuracy, precision, F1, ROC-AUC and PR-AUC all rose relative to C, but recall "
            "fell sharply from 0.519 to 0.457. D1 misses 74 more true cases than C while "
            "cutting false alarms by 656."),
        caveat=(
            "This is a descriptive change in the precision/recall trade-off under one tested "
            "setup. It is not evidence that high blood pressure causes diabetes, nor that it "
            "would improve prediction in any other setting."),
        comparator="C"),
    "D2": dict(
        name="D2 - adding reported high cholesterol",
        question="Does a second reported condition recover the recall that D1 gave up?",
        changed="D1 plus CCC_90, a reported history of high cholesterol.",
        interpretation=(
            "Recall recovers strongly, from 0.457 to 0.542, and precision, F1, ROC-AUC and "
            "PR-AUC all rise as well. Only accuracy dips slightly. D2 became the fixed feature "
            "set used for every later analysis in the project."),
        caveat=(
            "Still a trade-off rather than a universal improvement, and still an association "
            "measured within a single survey period. CCC_80 and CCC_90 are recorded at the same "
            "time as the diabetes answer, so no temporal ordering can be established."),
        comparator="D1"),
    "F": dict(
        name="Experiment F - a broader representation with L1 screening",
        question="What happens with all 16 variables whose special codes and applicability had "
                 "been documented, using L1 regularisation as a screening step?",
        changed="A wider documented feature set, plus an L1-penalised screening step fitted on "
                "the training rows only.",
        interpretation=(
            "F achieved the strongest ROC-AUC (0.827) and PR-AUC (0.317) of all the completed "
            "Logistic Regression conditions. The headline result, though, is what the screening "
            "step did not do: all 16 candidate variables were retained and none were dropped."),
        caveat=(
            "This is not evidence that automatic sparse feature elimination worked - L1 removed "
            "nothing at the chosen penalty strength. F also uses a broader preprocessing setup "
            "including one scaled numeric variable, so it is not a like-for-like swap with A, "
            "B, C or D2. It is a wider representation, not a cleaner one."),
        comparator=None),
}

# ------------------------------------------------------------------------ limitations

LIMITATIONS = [
    ("Cross-sectional design",
     "Characteristics and diabetes status are recorded at the same moment, so there is no time "
     "order, no future risk and no causation available from this data."),
    ("Class imbalance",
     "Positive cases are about 9% of the modelling population, so accuracy is misleading and "
     "positive-class metrics stay low even for a reasonable model."),
    ("Complex survey design not applied",
     "The survey's weights and bootstrap variance procedure were not used, so nothing here is a "
     "population estimate."),
    ("Self-reported information",
     "Both the predictors and the outcome come from what respondents reported. Recall error, "
     "misunderstanding and non-disclosure all remain possible."),
    ("Variable-specific universes",
     "CCHS modules have different age, geography and inclusion universes. Selected restrictions "
     "were handled explicitly, but the full 216-variable candidate space was never modelled."),
    ("Manual feature selection",
     "Which variables entered each condition was a human judgement, informed by documentation "
     "and literature but still a judgement."),
    ("Fixed rather than exhaustive hyperparameter search",
     "Small predefined configurations were compared rather than an exhaustive optimisation, so "
     "no model is shown at its best possible settings."),
    ("Generalization not established",
     "Everything was measured inside CCHS 2022. No other survey cycle, country or clinical "
     "cohort was tested."),
    ("Experiment F scope",
     "F was limited to the 16 variables whose codes had been documented, not the full 216-"
     "variable pool, and the L1 step removed none of them."),
    ("Comorbidity timing unknown",
     "CCC_80 and CCC_90 are recorded in the same period as the outcome. Their predictive value "
     "may partly reflect shared health-care contact rather than a specific relationship."),
    ("Repeated test-set use across A-D2",
     "One test partition was scored five times during development and those results were "
     "visible while deciding what to try next. The fresh-holdout check reduces the concern but "
     "does not remove it."),
    ("Undiagnosed diabetes is invisible",
     "Someone who has diabetes but has never been told would appear in this data as a negative "
     "case, because the outcome is a reported diagnosis."),
]

NOT_COMPLETED = [
    ("Experiment D3 - 35+ clinical variables", "Not completed", "Cannot be cited as a result"),
    ("Experiment E1 - adult smoking condition", "Not completed", "Cannot be cited as a result"),
    ("Experiment E2 - adult physical activity", "Not completed", "Cannot be cited as a result"),
    ("Automatic selection over all 216 variables", "Not completed",
     "Experiment F covered 16 documented variables only"),
    ("Exhaustive hyperparameter search", "Not attempted",
     "Small predefined searches were used instead"),
    ("External validation on other data", "Not attempted",
     "All results are internal to CCHS 2022"),
]

CONCLUSIONS = [
    ("Feature representation appears to matter substantially.",
     "Moving from feature condition C to D2 changed F1 by 0.053, while moving between three "
     "different algorithms on the fixed D2 features changed it by only 0.008."),
    ("The two reported conditions changed performance meaningfully.",
     "Adding reported high blood pressure and then a reported history of high cholesterol "
     "shifted the precision/recall balance and improved several discrimination measures "
     "relative to the compact C reference."),
    ("The broader F representation gave the strongest discrimination.",
     "F reached ROC-AUC 0.827 and PR-AUC 0.317, the highest of the completed Logistic "
     "Regression conditions - but the L1 screen retained all 16 candidates and dropped none, "
     "so this is not evidence that sparse selection succeeded."),
    ("No model class clearly dominates on the fixed D2 representation.",
     "Gradient Boosting leads on F1, ROC-AUC and precision; Logistic Regression on recall and "
     "PR-AUC; Random Forest ties for accuracy and has the lowest log loss."),
    ("Logistic Regression is retained as the reference model.",
     "Because it remains competitive while being simpler and directly interpretable - not "
     "because it scored best on the test set."),
    ("The scope of the claim is narrow and deliberate.",
     "These results are about classifying reported diabetes status within CCHS 2022. The "
     "project does not establish future diabetes risk, causation, or external generalization."),
]

CANNOT_CLAIM = [
    ("It cannot say who will develop diabetes",
     "The data is a single snapshot; there is no follow-up period in it at all."),
    ("It cannot diagnose anyone",
     "The outcome is a survey answer, not a clinical assessment, and precision is far too low "
     "for individual use."),
    ("It cannot establish a cause",
     "High-ranking variables are statistical associations measured at one moment."),
    ("It cannot give national prevalence figures",
     "That would require the survey weights and bootstrap procedure, which were not used."),
    ("It cannot claim to generalise",
     "No other cycle, country or clinical cohort was tested."),
    ("It cannot claim automatic feature selection worked",
     "The L1 screen retained all 16 candidate variables and dropped none."),
]
