# Dashboard Blueprint
## CCHS 2022 Diabetes Machine-Learning Project — Interactive Research Explorer

**Status:** blueprint only. No application code has been written. Awaiting approval.

---

## A. Purpose and positioning

An interactive **research project explorer**: a professor or researcher opens it and understands the
project in a few minutes without opening a notebook; a student with no Python or ML background can
explore it and understand what they are looking at.

It **complements** the 87-slide Master Understanding Deck rather than duplicating it. The deck is the
linear teaching resource; the dashboard is the non-linear explorer where the visitor chooses an
experiment, a metric, a variable or a model and sees the corresponding evidence.

It is **not** a clinical tool, not a risk calculator, and contains no user-prediction form.

---

## B. Architecture decision (important — resolves a repository conflict)

`.gitignore` line 2 is a blanket `*.csv`. Any new CSV written into `dashboard/data/` would be
**silently excluded from git**, and the app would then crash on Streamlit Community Cloud with a
missing-file error. The brief forbids changing `.gitignore`.

**Resolution:** the dashboard creates **no new CSV**. Instead:

1. It reads the **ten existing result CSVs directly from `notebooks/`**, which are already tracked in
   git (they were force-added). This also satisfies the "no duplicate truth" requirement — the app
   reads the real artifacts rather than re-typing numbers.
2. The handful of facts that exist **only inside notebooks or CCHS PDFs** (A and B confusion matrices,
   A/B feature lists, CCHS variable metadata, audit funnel counts) are encoded **once** in a tracked
   Python module, `dashboard/data_sources.py`, with a documented provenance string per item.
   `.py` files are not gitignored, so this deploys cleanly.
3. Paths resolve from `__file__`, so the app runs from any working directory and on Streamlit Cloud.

```
requirements.txt            # streamlit, pandas, plotly - at the REPOSITORY ROOT, because
                            # Streamlit Community Cloud reads it from there
dashboard/
    app.py                  # page routing, sidebar, persistent framing note
    ui.py                   # palette, CSS, and reusable layout components
    data_sources.py         # single source of truth: CSV loaders + documented constants
    content.py              # long-form explanatory text, "Why did we do this?" copy, metric glossary
    pages_impl/             # one module per page, kept small and readable
    README.md               # local run + deployment instructions
    DASHBOARD_BLUEPRINT.md
    DASHBOARD_QA_REPORT.md
    screenshots/            # QA evidence
```

*Built as specified above, with one change made during implementation:* the dependency file
lives at the repository root rather than inside `dashboard/`, because Streamlit Community
Cloud reads `requirements.txt` from the repository root by default. A second file inside
`dashboard/` would have been a duplicate source of truth. Styling was also split out of
`app.py` into `ui.py` so the nine page modules stay small.

No database, no API, no auth, no build step, no caching layer beyond `st.cache_data`.

---

## C. Data the dashboard WILL use

| Source | Used for | Tracked in git? |
|---|---|---|
| `notebooks/experiment_A_results.csv` … `experiment_F_results.csv` (6 files) | Per-condition thresholds and metrics; C/D1/D2/F confusion matrices and feature counts | yes |
| `notebooks/model_comparison_D2_results.csv` | LR/RF/GB comparison incl. log loss and configs | yes |
| `notebooks/d2_robustness_5fold_results.csv` | Per-fold values plus stored `mean` / `std` rows | yes |
| `notebooks/d2_interpretability_results.csv` | Variable importance values and per-model ranks | yes |
| `notebooks/d2_fresh_holdout_results.csv` | Fresh-split results, `split_random_state = 137` | yes |
| Executed notebooks (constants encoded once) | A and B confusion matrices; A/B feature lists; audit funnel 255→223→216 and 49/56/111; split sizes | source documented in code |
| CCHS 2022 PUMF Data Dictionary (constants encoded once) | Variable concepts, universes, question text, code frequencies | source documented in code |
| CCHS 2022 User Guide (one quotation) | Complex-design wording for the WTS_M explainer | source documented in code |
| `docs/CCHS_2022_Diabetes_Academic_Report.docx` | Narrative framing and limitation wording | prose only |

## D. Data the dashboard will explicitly NOT use

- `Data_Données/pumf_cchs.csv` — raw respondent microdata. Never read, never embedded.
- `Data_Données/cchs_escc_bsw.csv` — bootstrap weights. Never read, never embedded.
- No respondent-level records of any kind. The one example row shown is **synthetic and labelled as such**.
- No secrets, no credentials, no deployment tokens.

---

## E. Page structure

Nine pages in a sidebar selector. One main idea per section; no nested tabs.

### 1. Overview  (landing)

| | |
|---|---|
| **Purpose** | Communicate what the project is within about 20 seconds. |
| **Main content** | Title; subtitle "A cross-sectional classification study of diagnosed diabetes status"; four metric cards (67,079 respondents · 255 variables · 66,242 modelling population · 9.05% positive class); the plain-English research question; three headline findings; the IS / IS-NOT framing box; navigation hints. |
| **Controls** | None (deliberately — the landing page should not ask the visitor to do anything). |
| **Visuals** | Metric cards; a two-column IS / IS-NOT panel. |
| **Data source** | Counts from Notebook 02 / CCHS DD; findings from the result CSVs and academic report §10. |
| **Caveats shown** | The full IS / IS-NOT framing block appears here and is repeated as a persistent sidebar note on every page. |

### 2. Understand the data

| | |
|---|---|
| **Purpose** | What the CCHS is, what a PUMF is, what the target variable is, and why the class balance drives everything. |
| **Main content** | CCHS description (Statistics Canada, cross-sectional, 12+, health status / health-care use / determinants, 2022 redesign); PUMF explanation with real DHHGAGE codes as the example of grouped categories; one row = one respondent, one column = one variable; dimensions 67,079 × 255; target `CCC_05` with question text and the 1/2/9 code table; the exclusion funnel 67,079 → −837 → 66,242; class balance 5,994 / 60,248; the "always say no" trap at 90.95% accuracy. |
| **Controls** | Expanders: "Why is code 9 excluded?", "Why does 9.05% change how we judge the models?" |
| **Visuals** | Three-stage funnel (Plotly); horizontal stacked bar for class balance; code table. |
| **Data source** | CCHS 2022 PUMF Data Dictionary (CCC_05, DHHGAGE); Notebook 02 for the modelling population. |
| **Caveats shown** | 9.05% is unweighted — pointer forward to the WTS_M explainer. A synthetic example row is labelled synthetic. |

### 3. Feature audit

| | |
|---|---|
| **Purpose** | Why 255 columns cannot be fed to a model, and how they became 216 candidates. |
| **Main content** | Four problem cards (administrative/process columns, DO inclusion flags, special codes, restricted universes); the funnel 255 → −1 target − 31 DO flags → 223 → −7 admin/weight → 216; the 49 Core / 56 Review / 111 Restricted split; then four focused explainers as expandable sections: **special codes**, **BMI harmonisation**, **WTS_M**, **RHC_05**. |
| **Controls** | Special-code explainer: a variable selector (CCC_05, EDDVH3, HWTDGISW, HWTDGWHO, DHHGAGE) showing that variable's real codes and their real meanings. Expanders for each "Why did we do this?". |
| **Visuals** | Funnel chart; 49/56/111 bar; BMI decision flow (age → source variable → BMI_CLASS) rendered as a simple labelled diagram; a highlighted callout for the HWTDGWHO 63,318 valid-skip figure. |
| **Data source** | Notebook 01 Stage 13 (funnel and grouping); CCHS DD (all codes, universes, frequencies); CCHS User Guide §10.3 (complex-design quotation). |
| **Caveats shown** | "Never globally replace every 6 or 9 with missing." WTS_M section states 9.05% unweighted vs 7.4% weighted **as a contrast only**, explicitly not "7.4% is right and 9.05% is wrong". RHC_05 worded as a *methodological leakage / prediction-pathway concern*, never as demonstrated leakage. |

### 4. Variable explorer

| | |
|---|---|
| **Purpose** | Let a visitor look up any variable the project considered and see what it is and what the project did with it. |
| **Main content** | For the selected variable: name, human-readable concept, universe/applicability, coding (where verified), role in the project, which experiments used it, and the reason it was included / excluded / held out. |
| **Controls** | Variable selector (17 variables: DHHGAGE, DHH_SEX, EDDVH3, GEOGPRV, INCDGHH, SDCDGIMM, DHHDGHSZ, FSCDVHF2, ALCDVTTM, ECV_05, SMKDVSTY, LSM_01, WTP_50, BMI_CLASS, CCC_80, CCC_90, CCCDGCAR, WTS_M, RHC_05). Optional filter by role (core / contextual / clinical / held out / excluded). |
| **Visuals** | A definition card plus a small "used in" indicator across A, B, C, D1, D2, F. |
| **Data source** | Every concept, universe and question text verified in the CCHS 2022 PUMF Data Dictionary during this audit (see §G below). Experiment membership from the notebooks' `FEATURES` lists. |
| **Caveats shown** | Where a variable's universe is narrower than the 12+ modelling population (e.g. SMKDVSTY is 18+, LSM_01 and WTP_50 have module/proxy restrictions), that is stated factually. `BMI_CLASS` is labelled as **constructed by this project**, not a CCHS variable. |

### 5. Experiments

| | |
|---|---|
| **Purpose** | The core exploration surface: what each feature condition tested and what it found. |
| **Main content** | Selector A / B / C / D1 / D2 / F. For the chosen condition: name and one-line research question; feature list as chips; what changed relative to its comparator; locked threshold; the six metrics as cards with deltas against the comparator where one exists (B vs A, D1 vs C, D2 vs D1); confusion matrix; plain-English interpretation; a condition-specific caveat. Below that, a cross-condition comparison. |
| **Controls** | (a) Experiment selector. (b) Metric selector for the cross-condition chart, **defaulting to ROC-AUC**. (c) Expanders: "What does this metric mean?" for all seven metrics. |
| **Visuals** | Metric cards with up/down deltas; 2×2 confusion matrix; one bar chart of the selected metric across A–F (single metric only — never mixed scales). |
| **Data source** | The six experiment CSVs; A/B confusion matrices and A/B feature lists from the executed notebooks (encoded once, provenance documented). |
| **Caveats shown** | B is not "better in every way" (recall fell). D1/D2 phrased as trade-offs, never causally. **F is shown as 16 candidates → 16 retained → 0 dropped**, described as *not* successful sparse elimination, and flagged as not a like-for-like comparison with A/B because its representation is broader (and it includes a scaled numeric variable). |

### 6. Model comparison

| | |
|---|---|
| **Purpose** | Show that on a fixed feature set, the algorithm mattered much less than the features did. |
| **Main content** | Why the comparison was run (D2 features held constant; only the algorithm changes); the small predefined search that was used; full 7-metric table for LR / RF / GB including test log loss; a "who leads on what" summary; the reference-model explanation. |
| **Controls** | Metric selector driving a three-bar chart; expander "Why compare multiple models?"; expander "Why keep Logistic Regression?" |
| **Visuals** | Table with the best value in each column marked; single-metric bar chart; a small panel contrasting the 0.008 F1 spread between algorithms with the 0.053 F1 change from feature condition C to D2. |
| **Data source** | `model_comparison_D2_results.csv`; C and D2 CSVs for the contrast. |
| **Caveats shown** | Explicit statement that **test results were not used to select a model**, that **no model is declared the winner**, and that Logistic Regression is retained for comparable performance + simplicity + interpretability — *not* because it scored best. |

### 7. Robustness and interpretability

| | |
|---|---|
| **Purpose** | How stable the comparison is, and what the fitted models actually leaned on. |
| **Main content** | **Section 1 — 5-fold CV:** plain-language explanation (training portion split five ways, validation and test untouched); mean ± sd for the three models on ROC-AUC, PR-AUC and log loss; what it does and does not show. **Section 2 — Interpretability:** ranked variables with age, hypertension, high cholesterol and BMI class in the top four for all three models; three cautions. |
| **Controls** | Metric selector for the CV chart (ROC-AUC / PR-AUC / log loss); model selector for the interpretability ranking; expanders "Why perform 5-fold CV?" and "What is impurity importance?". |
| **Visuals** | Error-bar chart of mean ± sd; horizontal ranked bar chart of importance. |
| **Data source** | `d2_robustness_5fold_results.csv` (uses the stored `mean` and `std` rows); `d2_interpretability_results.csv`. |
| **Caveats shown** | CV described as a **stability analysis of already-chosen settings**, not a new tuning run and not an unbiased estimate of external generalization. Interpretability: LR coefficient magnitudes and tree impurity importances are **different quantities on different scales**, only within-model rank order is comparable; importance is **not causation**; GEOGPRV's high LR rank is partly an aggregation artefact of 11 encoded province categories. Any zoomed axis is labelled. |

### 8. Fresh holdout

| | |
|---|---|
| **Purpose** | Disclose the test-set reuse problem honestly, then show the check that was run because of it. |
| **Main content** | The problem: A, B, C, D1 and D2 all scored the same 13,249-row partition, and those results were visible during development. What was still done correctly (each experiment locked its model and threshold on train+validation before touching test). The check: `random_state = 137`, same D2 feature set, same frozen configurations, same locked thresholds (0.68 / 0.68 / 0.70), no retuning, scored once. Results for all three models. |
| **Controls** | Toggle / radio: **original split (seed 42) vs fresh split (seed 137)**, driving the comparison chart; metric selector. |
| **Visuals** | Paired bar chart original vs fresh; results table. |
| **Data source** | `d2_fresh_holdout_results.csv`; `model_comparison_D2_results.csv` for the original-split side. |
| **Caveats shown** | Stated as **supplementary confirmation, not proof of generalization**. Explicitly: one additional split of the same survey; says nothing about another CCHS cycle, country or clinical cohort; does **not** remove the test-set reuse limitation. Small F1 re-orderings between RF and GB described as noise. |

### 9. Limitations and conclusion

| | |
|---|---|
| **Purpose** | What the project concludes, and the boundary of those conclusions. |
| **Main content** | Twelve limitation cards (cross-sectional design; class imbalance; complex survey design / no survey-weighted estimates; self-reported information; variable-specific universes; manual feature selection; fixed rather than exhaustive search; generalization; F scoped to 16 documented variables; comorbidity timing and shared health-care contact; repeated test-set use across A–D2). A "what was planned but never completed" panel (D3, E1, E2, the full 216-variable automatic selection, exhaustive tuning, external validation). Then the evidence-based conclusion statements. A "what this project cannot claim" guardrail list. |
| **Controls** | Expanders on each limitation for the longer explanation. |
| **Visuals** | Limitation cards in a grid; a compact conclusion statement panel. |
| **Data source** | Academic report §8 and §10; Notebook 02 and the repository for the not-completed list. |
| **Caveats shown** | This page **is** the caveat page. It states plainly that D3/E1/E2 and the 216-variable selection were never completed and must not be cited as findings. |

---

## F. Cross-cutting behaviours

- **Persistent framing.** A compact IS / IS-NOT note is pinned in the sidebar on every page, so the cross-sectional framing cannot be missed regardless of entry point.
- **Metric glossary.** One shared `st.expander` component, "What does this mean?", reused wherever a metric appears, with the plain-language definitions specified in the brief.
- **"Why did we do this?"** expanders on: excluding WTS_M; not globally replacing 6/9; harmonising BMI; removing DO flags; `class_weight="balanced"`; validation-only threshold selection; comparing multiple models; 5-fold CV; the fresh holdout; keeping Logistic Regression; holding out RHC_05.
- **Source lines.** Every page ends with a compact source caption naming the specific artifact(s) used.
- **Chart honesty.** Only real saved project numbers are plotted. **No ROC or PR curves will be drawn** — the repository contains no saved curve data, and the brief forbids fabricating them. Any truncated axis is labelled in the chart title or caption; where a metric range is small, the default will be a zero-anchored axis with values labelled on the bars.
- **Colour.** Restrained academic palette matching the deck: dark navy `#1A2A3A` ink, off-white ground, orange `#C05621` accent, blue `#2E6DA4` neutral/negative-class, green `#2F7A5A` for improvement, red `#A63A2E` for caution. Colour never carries meaning alone — every encoded value is also labelled.

---

## G. Verification performed during this audit

- All **10 result CSVs** re-read; md5 recorded; **every metric figure in the brief matches the CSVs exactly — zero discrepancies**.
- **A and B CSVs contain no confusion-matrix columns.** The A (8,726 / 3,324 / 372 / 827) and B (9,692 / 2,358 / 482 / 717) matrices were re-extracted from the executed notebook outputs and match the brief.
- A and B feature lists (11 variables each) re-extracted from the notebooks.
- CCHS Data Dictionary re-queried and **verified** for: CCC_05, CCC_80, CCC_90, DHHGAGE, DHH_SEX, EDDVH3, INCDGHH, SDCDGIMM, GEOGPRV, HWTDGISW, HWTDGWHO, CCCDGCAR, DHHDGHSZ, FSCDVHF2, ALCDVTTM, ECV_05, SMKDVSTY, LSM_01, WTP_50, RHC_05, WTS_M — concept, universe and question text captured for each.
- Confirmed **no existing dashboard or application code** anywhere in the repository.

---

## H. Blueprint self-review

**Duplication removed.** An early draft had separate pages for "target variable" and "class imbalance";
they are one page because the imbalance only means anything next to the target counts. A separate
"special codes" page was folded into Feature audit for the same reason. Model comparison and the
reference-model choice are one page, because splitting them invites the reader to treat the metric
table as a leaderboard.

**Unsupported claims removed.** No page states that F selected variables, that any model won, that the
fresh holdout validates the model, or that any variable causes diabetes.

**Text reduced.** Long explanations moved into expanders so each page's default view is short. No page
opens with more than roughly 80 words of continuous prose.

**Charts over prose.** The funnels, the class balance, the cross-condition comparison, the CV error
bars, the importance ranking and the original-vs-fresh comparison are all charts rather than tables of
numbers embedded in sentences.

**Interactions audited.** Every control changes something a reader would actually want to compare:
experiment, metric, variable, model, split. No sliders, no animation, no 3-D, no prediction form.

**Pages that were considered and rejected.** A "try the model" page (forbidden and scientifically
inappropriate); a notebook viewer (duplicates GitHub); a live re-training page (violates the
performance and scope constraints); a raw-data browser (privacy).
