"""
Single source of truth for the dashboard.

Two kinds of data live here:

1. LOADERS that read the ten result CSVs that are already tracked in git under notebooks/.
   Nothing is copied or duplicated - the dashboard reads the real experiment artifacts.

2. CONSTANTS for the small number of facts that genuinely do not exist in those CSVs
   (Experiment A/B confusion matrices, A/B feature lists, the feature-audit funnel counts,
   and CCHS variable metadata). Every constant carries a `source` string saying where it
   came from, so any number on screen can be traced back.

No raw respondent data is read anywhere in this file.
"""

from pathlib import Path
import pandas as pd
import streamlit as st

# notebooks/ sits next to dashboard/ - resolve from __file__ so the app runs from any
# working directory and on Streamlit Community Cloud.
REPO_ROOT = Path(__file__).resolve().parent.parent
RESULTS_DIR = REPO_ROOT / "notebooks"

# --------------------------------------------------------------------------- loaders

_EXPERIMENT_FILES = {
    "A": "experiment_A_results.csv",
    "B": "experiment_B_results.csv",
    "C": "experiment_C_results.csv",
    "D1": "experiment_D1_results.csv",
    "D2": "experiment_D2_results.csv",
    "F": "experiment_F_results.csv",
}

METRICS = ["accuracy", "precision", "recall", "f1", "roc_auc", "pr_auc"]

# Canonical model order used everywhere in the dashboard.
MODEL_ORDER = ["Logistic Regression", "Random Forest", "Gradient Boosting"]

METRIC_LABELS = {
    "accuracy": "Accuracy",
    "precision": "Precision",
    "recall": "Recall",
    "f1": "F1",
    "roc_auc": "ROC-AUC",
    "pr_auc": "PR-AUC",
    "test_log_loss": "Test log loss",
    "log_loss": "Log loss",
}


@st.cache_data
def load_experiments() -> pd.DataFrame:
    """One row per feature condition (A, B, C, D1, D2, F), read from the six result CSVs.

    A and B were saved with a smaller schema than C/D1/D2/F, so the confusion-matrix and
    feature-count columns are missing for them; they are filled from NOTEBOOK_FACTS below.
    """
    rows = []
    for key, filename in _EXPERIMENT_FILES.items():
        row = pd.read_csv(RESULTS_DIR / filename).iloc[0].to_dict()
        row["condition"] = key
        rows.append(row)
    df = pd.DataFrame(rows).set_index("condition")

    # A and B were saved without confusion-matrix columns - fill them from the notebooks.
    for key in ("A", "B"):
        facts = NOTEBOOK_FACTS["confusion_matrix"][key]
        df.loc[key, "true_negatives"] = facts["tn"]
        df.loc[key, "false_positives"] = facts["fp"]
        df.loc[key, "false_negatives"] = facts["fn"]
        df.loc[key, "true_positives"] = facts["tp"]

    # raw_feature_count is absent from A and B (older schema) and from F (which stores
    # original_candidate_count instead), so derive it for every condition from the
    # notebook FEATURES lists - the authoritative definition of each condition.
    df["raw_feature_count"] = [len(NOTEBOOK_FACTS["feature_lists"][c]) for c in df.index]

    for col in ("true_negatives", "false_positives", "false_negatives",
                "true_positives", "raw_feature_count"):
        df[col] = df[col].astype(int)
    return df


@st.cache_data
def load_model_comparison() -> pd.DataFrame:
    """Logistic Regression vs Random Forest vs Gradient Boosting on the fixed D2 features."""
    return pd.read_csv(RESULTS_DIR / "model_comparison_D2_results.csv")


@st.cache_data
def load_fresh_holdout() -> pd.DataFrame:
    """The same three models re-evaluated on a freshly seeded split (random_state = 137)."""
    return pd.read_csv(RESULTS_DIR / "d2_fresh_holdout_results.csv")


@st.cache_data
def load_cv_folds() -> pd.DataFrame:
    """Per-fold 5-fold cross-validation scores (the numeric fold rows only)."""
    df = pd.read_csv(RESULTS_DIR / "d2_robustness_5fold_results.csv")
    return df[df["fold"].astype(str).str.isdigit()].copy()


@st.cache_data
def load_cv_summary() -> pd.DataFrame:
    """Mean and standard deviation per model, taken from the rows the notebook itself saved.

    The notebook wrote 'mean' and 'std' rows into the CSV, so the dashboard reports the
    project's own stored summary rather than recomputing it.
    """
    df = pd.read_csv(RESULTS_DIR / "d2_robustness_5fold_results.csv")
    means = df[df["fold"].astype(str) == "mean"].set_index("model")
    stds = df[df["fold"].astype(str) == "std"].set_index("model")
    out = pd.DataFrame(index=means.index)
    for col in ("roc_auc", "pr_auc", "log_loss"):
        out[f"{col}_mean"] = means[col]
        out[f"{col}_std"] = stds[col]
    # Present models in the project's canonical order rather than alphabetically,
    # so this page matches the model-comparison table.
    return out.reindex(MODEL_ORDER).reset_index()


@st.cache_data
def load_interpretability() -> pd.DataFrame:
    """Aggregated per-variable importance and within-model ranks from the D2 training fit."""
    return pd.read_csv(RESULTS_DIR / "d2_interpretability_results.csv")


# ------------------------------------------------------- constants not present in CSVs

NOTEBOOK_FACTS = {
    # Experiment A and B result CSVs were saved with a 12-column schema that has no
    # confusion-matrix columns. These four numbers per experiment come from the printed
    # output of the executed notebooks and were re-verified against them.
    "confusion_matrix": {
        "A": {"tn": 8726, "fp": 3324, "fn": 372, "tp": 827,
              "source": "Experiment_A_Baseline_Logistic_Regression.ipynb, final test output"},
        "B": {"tn": 9692, "fp": 2358, "fn": 482, "tp": 717,
              "source": "Experiment_B_Preliminary_Feature_Set.ipynb, final test output"},
    },
    # Feature lists as defined in each experiment notebook's FEATURES list.
    "feature_lists": {
        "A": ["DHHGAGE", "DHH_SEX", "GEOGPRV", "DHHDGHSZ", "EDDVH3", "LSM_01",
              "HWTDGISW", "WTP_50", "SMKDVSTY", "FSCDVHF2", "INCDGHH"],
        "B": ["ALCDVTTM", "DHHDGHSZ", "DHHGAGE", "DHH_SEX", "EDDVH3", "FSCDVHF2",
              "GEOGPRV", "BMI_CLASS", "INCDGHH", "ECV_05", "SDCDGIMM"],
        "C": ["DHHGAGE", "DHH_SEX", "EDDVH3", "BMI_CLASS", "INCDGHH", "SDCDGIMM", "GEOGPRV"],
        "D1": ["DHHGAGE", "DHH_SEX", "EDDVH3", "BMI_CLASS", "INCDGHH", "SDCDGIMM",
               "GEOGPRV", "CCC_80"],
        "D2": ["DHHGAGE", "DHH_SEX", "EDDVH3", "BMI_CLASS", "INCDGHH", "SDCDGIMM",
               "GEOGPRV", "CCC_80", "CCC_90"],
        "F": ["DHHGAGE", "DHH_SEX", "DHHDGHSZ", "EDDVH3", "GEOGPRV", "INCDGHH",
              "FSCDVHF2", "ALCDVTTM", "ECV_05", "SDCDGIMM", "LSM_01", "WTP_50",
              "SMKDVSTY", "CCC_80", "CCC_90", "BMI_CLASS"],
        "source": "FEATURES / CANDIDATE_FEATURES lists in the six experiment notebooks",
    },
    # Dataset and split figures, identical across every main experiment.
    "dataset": {
        "respondents": 67079,
        "variables": 255,
        "modelling_population": 66242,
        "positives": 5994,
        "negatives": 60248,
        "not_stated": 837,
        "train": 42394,
        "validation": 10599,
        "test": 13249,
        "random_state": 42,
        "source": "Notebook 02 and every experiment notebook (stratified split, random_state = 42)",
    },
    # Feature-audit funnel, Notebook 01 Stage 13.
    "feature_audit": {
        "total_columns": 255,
        "after_target_and_flags": 223,
        "candidate_pool": 216,
        "do_flags_removed": 31,
        "admin_removed": 7,
        "admin_variables": ["VERDATE", "REFPER", "ADM_RNO", "COLMODE",
                            "COLMODEY", "COLMODEP", "WTS_M"],
        "core": 49,
        "review": 56,
        "restricted": 111,
        "source": "Notebook 01, Stage 13 candidate-pool construction",
    },
}


def dataset_facts() -> dict:
    return NOTEBOOK_FACTS["dataset"]


def audit_facts() -> dict:
    return NOTEBOOK_FACTS["feature_audit"]


def feature_list(condition: str) -> list:
    return NOTEBOOK_FACTS["feature_lists"][condition]


# ------------------------------------------------------------------ CCHS variable metadata
# Every concept, universe and question text below was read directly from the
# CCHS 2022 PUMF Data Dictionary (September 2025). Nothing here is inferred.

DD = "Statistics Canada, CCHS 2022 PUMF Data Dictionary (September 2025)"

VARIABLES = {
    "DHHGAGE": dict(
        concept="Age - (G)", universe="All respondents", role="Core predictor",
        coding="1 = 12 to 17 · 2 = 18 to 34 · 3 = 35 to 49 · 4 = 50 to 64 · 5 = 65 and older",
        special_codes="None",
        note="Used in every feature condition. Ranked first or second in importance for all "
             "three model classes.",
        used_in=["A", "B", "C", "D1", "D2", "F"], source=DD),
    "DHH_SEX": dict(
        concept="Sex at birth", universe="All respondents", role="Core predictor",
        coding="1 = Male · 2 = Female", special_codes="None",
        note="Broadly applicable demographic variable, present in every condition.",
        used_in=["A", "B", "C", "D1", "D2", "F"], source=DD),
    "EDDVH3": dict(
        concept="Highest level of education - household, 3 levels - (D)",
        universe="All respondents", role="Core predictor",
        coding="1 = Less than secondary · 2 = Secondary, no post-secondary · 3 = Post-secondary",
        special_codes="9 = Not stated",
        note="Household-level education, so it describes the household rather than the individual.",
        used_in=["A", "B", "C", "D1", "D2", "F"], source=DD),
    "GEOGPRV": dict(
        concept="Province or territory of residence of respondent - (G)",
        universe="All respondents", role="Contextual predictor",
        coding="Province/territory codes, 11 categories (10 = N.L. … 59 = B.C., 60 = territories)",
        special_codes="None",
        note="Its high Logistic Regression importance rank is partly an artefact of aggregating "
             "11 one-hot encoded categories; the tree models rank it 5th and 6th.",
        used_in=["A", "B", "C", "D1", "D2", "F"], source=DD),
    "INCDGHH": dict(
        concept="Total Household Income - All Sources - (D, G)",
        universe="All respondents", role="Core predictor",
        coding="Grouped income bands, from 'No income or less than $20,000' upward",
        special_codes="9 = Not stated",
        note="Socioeconomic information; grouped for confidentiality in the PUMF.",
        used_in=["A", "B", "C", "D1", "D2", "F"], source=DD),
    "SDCDGIMM": dict(
        concept="Immigrant flag - (D, G)", universe="All respondents",
        role="Contextual predictor",
        coding="1 = Non-immigrant · 2 = Immigrant or non-permanent resident",
        special_codes="9 = Not stated",
        note="Included as a broad contextual representation. Other socio-demographic variables "
             "were reserved for experiments that were never run.",
        used_in=["B", "C", "D1", "D2", "F"], source=DD),
    "DHHDGHSZ": dict(
        concept="Household size - Grouped", universe="All respondents",
        role="Predictor in A, B and F", coding="Grouped household size",
        special_codes="9 = Not stated",
        note="Dropped from the compact C core, which kept only the literature-informed variables.",
        used_in=["A", "B", "F"], source=DD),
    "FSCDVHF2": dict(
        concept="Household food security status (including marginally) - (D)",
        universe="Respondents with DOFSC = 1", role="Predictor in A, B and F",
        coding="Food-security status categories", special_codes="9 = Not stated",
        note="Module-gated variable: it is only defined for respondents routed into the food "
             "security module.",
        used_in=["A", "B", "F"], source=DD),
    "ALCDVTTM": dict(
        concept="Type of drinker - 12 months - (D)", universe="All respondents",
        role="Predictor in B and F", coding="Drinker-type categories",
        special_codes="9 = Not stated",
        note="Behavioural variable added in the B representation and retained in F.",
        used_in=["B", "F"], source=DD),
    "ECV_05": dict(
        concept="Tried e-cigarette / vaping device - life",
        universe="Respondents with DOECV = 1", role="Predictor in B and F",
        coding="1 = Yes · 2 = No", special_codes="9 = Not stated",
        note="Question text: 'Have you ever tried an e-cigarette or vaping device?'",
        used_in=["B", "F"], source=DD),
    "SMKDVSTY": dict(
        concept="Smoking status (type 2) - traditional definition - (D)",
        universe="Respondents aged 18 and older", role="Predictor in A and F",
        coding="Smoking-status categories", special_codes="96 and 99 handled as special codes",
        note="Its universe is narrower than the 12+ modelling population, so respondents aged "
             "12-17 fall outside it. The project handled this through variable-specific "
             "special-code rules rather than by treating the skip as a real category.",
        used_in=["A", "F"], source=DD),
    "LSM_01": dict(
        concept="Satisfaction with life in general",
        universe="Respondents with DOLSM = 1 and PROXYSEX = (1, 2)",
        role="The only numeric predictor used (in A and F)",
        coding="0 to 10 scale", special_codes="99 handled as a special code",
        note="Treated as numeric: median-imputed and standardised, unlike every other variable "
             "in the project, which is treated as categorical.",
        used_in=["A", "F"], source=DD),
    "WTP_50": dict(
        concept="Self-perceived weight - overweight / underweight / just about right",
        universe="Respondents with DOWTP = 1 and PROXYSEX = (1, 2) and who answered PRS_05",
        role="Predictor in A and F", coding="Perceived-weight categories",
        special_codes="9 = Not stated",
        note="Subjective weight perception. Held out of the compact C core because it overlaps "
             "with the BMI representation.",
        used_in=["A", "F"], source=DD),
    "BMI_CLASS": dict(
        concept="Harmonised BMI classification - CONSTRUCTED BY THIS PROJECT",
        universe="All respondents aged 12 and older (by construction)",
        role="Core predictor",
        coding="1 = Underweight/Normal (adults) or Thinness/Normal (youth) · "
               "2 = Overweight/Obese",
        special_codes="6 and 9 converted to missing before modelling",
        note="Not a CCHS variable. Built by taking HWTDGWHO for ages 12-17 and HWTDGISW for "
             "ages 18+, so that a structural age skip is never mistaken for a real BMI category.",
        used_in=["B", "C", "D1", "D2", "F"],
        source="Constructed in Experiments B, C, D1, D2 and F from the two CCHS BMI variables"),
    "HWTDGISW": dict(
        concept="BMI classification for adults (self-reported) - intl standard - (D, G)",
        universe="Respondents aged 18 and older",
        role="Source variable for BMI_CLASS; used directly in Experiment A",
        coding="1 = Underweight/Normal weight · 2 = Overweight/Obese Class I, II, III",
        special_codes="6 = Valid skip (3,793 records) · 9 = Not stated (2,836 records)",
        note="Experiment A used this adult variable directly, which means respondents aged "
             "12-17 had no usable BMI value in A.",
        used_in=["A"], source=DD),
    "HWTDGWHO": dict(
        concept="BMI age 12 to 17 (self-reported) - WHO classification - (D, G)",
        universe="Respondents aged 12 to 17",
        role="Source variable for BMI_CLASS",
        coding="1 = Thinness/Normal (2,453) · 2 = Overweight/Obese (972)",
        special_codes="6 = Valid skip (63,318 records) · 9 = Not stated (336 records)",
        note="The clearest example in the whole dataset of why code 6 is not missing data: "
             "63,318 of 67,079 records are a valid skip simply because those respondents are "
             "adults, not because anything is missing.",
        used_in=[], source=DD),
    "CCC_80": dict(
        concept="Has high blood pressure", universe="Respondents with DOCCC = 1",
        role="Clinical expansion variable added in D1",
        coding="1 = Yes (16,967) · 2 = No (49,600)", special_codes="9 = Not stated (512)",
        note="Question text: 'Do you have high blood pressure?' This is a reported condition, "
             "not a laboratory measurement. Ranked first in importance for both tree models.",
        used_in=["D1", "D2", "F"], source=DD),
    "CCC_90": dict(
        concept="Has had high blood cholesterol - lifetime",
        universe="Respondents with DOCCC = 1",
        role="Clinical expansion variable added in D2",
        coding="1 = Yes (16,869) · 2 = No (50,042)", special_codes="9 = Not stated (168)",
        note="Question text: 'Have you ever been told by a health professional that your blood "
             "cholesterol was high?' A reported history, not a laboratory measurement.",
        used_in=["D2", "F"], source=DD),
    "CCCDGCAR": dict(
        concept="Cardiovascular condition (Heart disease or stroke) - (G)",
        universe="Respondents aged 35 and older with DOCCC = 1",
        role="Held out of the general model",
        coding="1 = Yes (5,618) · 2 = No (46,032)",
        special_codes="6 = Valid skip (13,884) · 9 = Not stated (1,545)",
        note="Its universe starts at age 35, so for everyone younger it is structurally blank "
             "rather than unknown. It was reserved for a 35+ experiment (D3) that was never "
             "completed.",
        used_in=[], source=DD),
    "RHC_05": dict(
        concept="Regular health care provider", universe="Respondents with DORHC = 1",
        role="Deliberately held out",
        coding="Health-care provider categories", special_codes="Not stated code applies",
        note="Held out because having a regular provider may reflect health-care access and "
             "diagnosis pathways rather than the underlying condition. This is a methodological "
             "leakage / prediction-pathway concern; the project did not demonstrate leakage and "
             "does not claim to have.",
        used_in=[], source=DD),
    "WTS_M": dict(
        concept="Weights - Master", universe="All respondents",
        role="Excluded from the predictor set",
        coding="Survey sampling weight (continuous)", special_codes="Not applicable",
        note="A sampling weight describes the survey design, not the respondent's health. "
             "Because the weights and bootstrap procedure were not applied, the project's "
             "results are respondent-level machine learning, not survey-weighted population "
             "estimates.",
        used_in=[], source=DD),
}

# Special-code examples used by the interactive explainer on the Feature Audit page.
SPECIAL_CODE_EXAMPLES = {
    "CCC_05 (diabetes - the target)": [
        ("1", "Yes", "5,994 respondents", "Positive class"),
        ("2", "No", "60,248 respondents", "Negative class"),
        ("9", "Not stated", "837 respondents", "Excluded from modelling"),
    ],
    "EDDVH3 (education)": [
        ("1", "Less than secondary school graduation", "-", "Real category"),
        ("2", "Secondary graduation, no post-secondary", "-", "Real category"),
        ("3", "Post-secondary certificate / diploma / degree", "-", "Real category"),
        ("9", "Not stated", "-", "Treated as missing"),
    ],
    "HWTDGISW (adult BMI, 18+)": [
        ("1", "Underweight / Normal weight", "23,799 respondents", "Real measurement"),
        ("2", "Overweight / Obese (Class I, II, III)", "36,651 respondents", "Real measurement"),
        ("6", "Valid skip", "3,793 respondents", "Question did not apply - not missing"),
        ("9", "Not stated", "2,836 respondents", "Genuinely unknown"),
    ],
    "HWTDGWHO (youth BMI, 12-17)": [
        ("1", "Thinness / Normal", "2,453 respondents", "Real measurement"),
        ("2", "Overweight / Obese", "972 respondents", "Real measurement"),
        ("6", "Valid skip", "63,318 respondents", "These respondents are adults - not missing"),
        ("9", "Not stated", "336 respondents", "Genuinely unknown"),
    ],
    "DHHGAGE (age group)": [
        ("1", "12 to 17 years", "3,761 respondents", "Real category"),
        ("2", "18 to 34 years", "10,123 respondents", "Real category"),
        ("3", "35 to 49 years", "12,829 respondents", "Real category"),
        ("4", "50 to 64 years", "16,399 respondents", "Real category"),
        ("5", "65 and older", "23,967 respondents", "Real category"),
    ],
}

# Weighted vs unweighted contrast used on the WTS_M explainer.
PREVALENCE_CONTRAST = {
    "unweighted_pct": 9.05,
    "weighted_pct": 7.4,
    "source": "Unweighted share is 5,994 / 66,242 from Notebook 02. The 7.4% weighted "
              "percentage for CCC_05 = Yes is the published weighted frequency in the "
              "CCHS 2022 PUMF Data Dictionary.",
}

USER_GUIDE_QUOTE = (
    "The CCHS is based upon a complex design, with stratification and multiple stages of "
    "selection, and unequal probabilities of selection of respondents."
)
USER_GUIDE_SOURCE = "Statistics Canada, CCHS 2022 User Guide, Section 10.3"
