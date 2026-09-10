# Interactive Research Explorer

A Streamlit dashboard that lets a first-time visitor understand the CCHS 2022 Diabetes
Machine-Learning Project without opening a notebook.

It is an **interactive research-project explorer**, not a clinical tool. It contains no
prediction form, trains nothing, and never reads raw respondent data.

---

## Run it locally

From the **repository root**:

```bash
pip install -r requirements.txt
streamlit run dashboard/app.py
```

The app opens at <http://localhost:8501>. No configuration, API keys or database are needed.

Tested with Python 3.12.0, Streamlit 1.63.0, pandas 3.0.5 and Plotly 7.0.0
(the exact versions pinned in the repository-root `requirements.txt`).

---

## Pages

| Page | What it answers |
|---|---|
| Overview | What is this project, and what does it claim? |
| Understand the Data | What is the CCHS, what is a PUMF, what is the target variable? |
| Feature Audit | Why can't all 255 columns be used, and how did they become 216 candidates? |
| Variable Explorer | What is each variable, and what did the project do with it? |
| Experiment Explorer | What did each of the six feature conditions test and find? |
| Model Comparison | How do Logistic Regression, Random Forest and Gradient Boosting compare? |
| Robustness & Interpretability | How stable is the result, and what did the models lean on? |
| Fresh Holdout | The test-set reuse problem, and the check run because of it. |
| Limitations & Conclusion | What the evidence supports, and what it cannot claim. |

Any page can be linked directly with a query parameter, for example
`?page=Feature+Audit` or `?page=Model+Comparison`.

---

## How the data layer works

The dashboard **creates no data files of its own**. It reads the ten result CSVs that are
already tracked in git under `notebooks/`:

```
notebooks/experiment_A_results.csv        notebooks/model_comparison_D2_results.csv
notebooks/experiment_B_results.csv        notebooks/d2_robustness_5fold_results.csv
notebooks/experiment_C_results.csv        notebooks/d2_interpretability_results.csv
notebooks/experiment_D1_results.csv       notebooks/d2_fresh_holdout_results.csv
notebooks/experiment_D2_results.csv
notebooks/experiment_F_results.csv
```

This matters for two reasons. First, there is a single source of truth — the numbers on
screen are read from the experiment artifacts rather than re-typed. Second, the repository
`.gitignore` excludes `*.csv`, so a new CSV placed inside `dashboard/` would be silently
left out of git and the deployed app would crash on a missing file. Reading the
already-tracked result files avoids that entirely, without modifying `.gitignore`.

A small number of facts genuinely do not exist in those CSVs:

* the Experiment A and B confusion matrices (their CSVs were saved with a smaller schema),
* the per-condition feature lists,
* the 255 → 223 → 216 feature-audit funnel,
* CCHS variable metadata (concepts, universes, code frequencies).

These live in `data_sources.py` as constants, each carrying a `source` string naming the
notebook or the CCHS document it came from.

### Data that is never touched

`Data_Données/pumf_cchs.csv` and `Data_Données/cchs_escc_bsw.csv` are never read. No
respondent-level record appears anywhere. The single example row on the "Understand the
Data" page is synthetic and labelled as such.

---

## File layout

```
dashboard/
├── app.py                # page routing, sidebar, persistent framing note
├── ui.py                 # palette, CSS, and reusable layout components
├── data_sources.py       # CSV loaders + documented constants (single source of truth)
├── content.py            # all explanatory prose, metric glossary, "why" answers
├── pages_impl/           # one small module per page
├── screenshots/          # QA evidence
├── DASHBOARD_BLUEPRINT.md
├── DASHBOARD_QA_REPORT.md
└── README.md
```

To change wording, edit `content.py`. To change styling, edit `ui.py`. To change a number,
you cannot — it comes from the result CSVs, which is the point.

---

## Deploying to Streamlit Community Cloud

1. Push the repository to GitHub.
2. On <https://share.streamlit.io>, create a new app pointing at this repository.
3. Set the main file path to `dashboard/app.py`.
4. Leave the Python dependencies as the repository-root `requirements.txt` (the default).

No secrets are required. The raw CCHS microdata is not in the repository and is not needed
by the dashboard — only the result CSVs, which are tracked.

---

## Scope and framing

Every page carries a persistent reminder in the sidebar:

> **What this study is** — a cross-sectional classification of *reported* diabetes status
> in CCHS 2022.
> **What it is not** — not future-risk prediction, not a diagnosis, not a screening tool,
> and not evidence of causation.

The dashboard deliberately does **not** draw ROC or PR curves, because the repository does
not contain the underlying saved curve data. Only values that exist in the project's own
result files are plotted.
