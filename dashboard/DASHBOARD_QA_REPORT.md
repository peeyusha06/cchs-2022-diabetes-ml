# Dashboard QA Report
## CCHS 2022 Diabetes Machine-Learning Project — Interactive Research Explorer

---

## 1. Build summary

| Item | Result |
|---|---|
| Pages | 9, all implemented and verified |
| Interactive controls | 16 states exercised, all pass |
| Console errors | none, on any page or state |
| Python errors on render | none, on any page or state |
| Screenshots captured and inspected | 26 |
| New data files created | **none** — the app reads the ten already-tracked result CSVs |
| Raw respondent data read | **none** |
| Experiment notebooks / result CSVs modified | **none** |
| `.gitignore` modified | **no** |
| Files staged or committed | **none** |

Environment: Python 3.12.0, Streamlit 1.63.0, pandas 3.0.5, Plotly 7.0.0.

---

## 2. Numerical verification

### 2.1 Data layer (automated assertions)

A test asserted every rendered figure against the result CSVs before any UI work:

* **72 assertions across the six feature conditions** — threshold, accuracy, precision,
  recall, F1, ROC-AUC, PR-AUC, the four confusion-matrix cells, and the feature count.
  **All pass.**
* **Confusion-matrix integrity**: all six conditions sum to exactly 13,249, the test-set size.
* **Metadata consistency**: every variable named in a condition's feature list has metadata,
  and every variable's `used_in` list agrees with the feature lists in both directions.
  **No mismatches.**

### 2.2 Rendered-content audit (automated)

Every page was loaded in a headless browser, every expander opened, and the resulting text
scraped. **40 required values all appear**, including 67,079 / 255 / 66,242 / 9.05% /
5,994 / 60,248 / 837 / 90.95%, the audit funnel (216, 223, 49, 56, 111), the 63,318
HWTDGWHO valid-skip figure, the 7.4% weighted contrast, D2's full metric set and confusion
matrix, the three log-loss values, the 5-fold means, the fresh-holdout values, seed 137,
and the split sizes 42,394 / 10,599 / 13,249.

### 2.3 Schema findings that required care

* `experiment_A_results.csv` and `experiment_B_results.csv` were saved with a 12-column
  schema and contain **no confusion-matrix columns**. Those eight numbers are taken from the
  executed notebooks and are labelled as such on screen.
* `experiment_F_results.csv` has **no `raw_feature_count` column** (it stores
  `original_candidate_count` instead). The loader therefore derives the feature count for
  every condition from the notebook feature lists. This was caught by a crash during
  testing, not by inspection.

---

## 3. Framing and claim audit

An automated check searched the full rendered text for phrases the project must not use.

| Forbidden phrase | Result |
|---|---|
| "predicts who will develop" | absent |
| "future diabetes risk model" | absent |
| "clinical risk calculator" | absent |
| "diagnoses diabetes" | absent |
| "the winning model" | absent |
| "L1 successfully" / "successfully eliminated" | absent |
| "proven leakage" | absent |
| "proof of generalization" | present **only** in the negated form ("not proof of generalisation") |
| "was the best model" | present **only** in the negated form (…retained because it is simpler — *not* "Logistic Regression was the best model") |

Confirmed present and correctly framed:

* D3, E1 and E2 appear only in a "What was planned but never completed" table, each marked
  **Not completed — cannot be cited as a result**.
* Experiment F is presented as **16 candidates → 16 retained → 0 dropped**, explicitly *not*
  successful sparse elimination, and flagged as not a like-for-like comparison with A/B.
* No model is declared the test-set winner; the page states test results were never used to
  select a model.
* RHC_05 is worded as a *methodological leakage / prediction-pathway concern*, with an
  explicit statement that leakage was not demonstrated.
* The 9.05% unweighted vs 7.4% weighted figures are presented as answers to different
  questions, with neither called "correct".
* A persistent IS / IS-NOT note appears in the sidebar on all nine pages.

---

## 4. Interaction testing

All 16 control states were driven in a real browser and the resulting widget value read back.

| Page | Control | States tested | Result |
|---|---|---|---|
| Feature Audit | special-code variable selector | HWTDGWHO, DHHGAGE | pass |
| Variable Explorer | variable selector | CCC_90, WTS_M, RHC_05 | pass |
| Variable Explorer | role filter | "Held out or excluded" | pass |
| Experiment Explorer | condition selector | A, B, F | pass |
| Experiment Explorer | metric selector | PR-AUC | pass |
| Model Comparison | metric selector | Recall, Test log loss | pass |
| Robustness | CV metric selector | Log loss | pass |
| Robustness | interpretability model selector | Gradient Boosting | pass |
| Fresh Holdout | metric selector | Recall | pass |
| Fresh Holdout | original/fresh table radio | Original split | pass |

Deep links (`?page=…`) were used for all nine pages and resolve correctly.

---

## 5. Visual issues found and fixed

Every issue below was found by inspecting rendered screenshots, not by assumption.

| # | Issue | Fix |
|---|---|---|
| 1 | Page kicker clipped at the top of **every** page | Increased `.block-container` top padding from 2.3rem to 3.4rem |
| 2 | Landing page H1 was "An interactive research explorer"; the brief specifies the project name as the title | Swapped kicker and title so H1 is "CCHS 2022 Diabetes Machine-Learning Project" |
| 3 | 5-fold chart listed models alphabetically (GB, LR, RF), inconsistent with every other page | Added a canonical model order (LR, RF, GB) applied in the loader |
| 4 | Feature-audit funnel label "Module inclusion flags (DO…)" read as truncated text | Shortened to "Module inclusion flags" |
| 5 | Accuracy showed 0.840 for both RF and GB but bolded only GB, implying a difference the reader cannot see (they differ by 0.0004) | Best-value comparison now happens at displayed precision, so genuine ties are both marked |
| 6 | Chart legend overlapped the chart title | Legends moved below the plot, with matching height and margin adjustments |
| 7 | `st.dataframe` renders to a `<canvas>` — table contents were unselectable, uncopyable and invisible to screen readers and to the content audit | All nine static tables converted to DOM-rendered `st.table` via a new `ui.static_table()` helper |
| 8 | After that conversion, the green best-value highlight rendered as plain bold | Reordered the Styler so base properties are applied before the highlight |
| 9 | Table header text rendered grey on navy (poor contrast) and cell highlight colour was lost | Root cause was the global `p { color }` rule: Streamlit wraps each cell in `<p>`. Scoped CSS added for `[data-testid="stTableStyledTable"] th p` and `td p` |

Issue 9 is worth noting: the *computed* style on the `<td>` was correct, so the bug was only
visible in a zoomed screenshot. It was found by capturing the table element at 3× scale
rather than trusting the full-page view.

---

## 6. Chart honesty

* No ROC or PR curves are drawn anywhere. The repository contains no saved curve data, and
  fabricating one would be misleading.
* All comparison bar charts are **zero-anchored**, so bar heights are directly comparable,
  and each carries a caption saying so.
* The one chart with a deliberately zoomed axis — the 5-fold mean ± standard deviation
  chart, where zooming is necessary to see the error bars at all — carries an explicit
  caption stating that the axis does not start at zero, and noting that overlapping bars
  mean the models are not clearly separated.
* Every chart title states the metric and its direction ("higher is better" / "lower is
  better"), so it is readable without the surrounding prose.
* Colour never carries meaning alone: every encoded value is also labelled in text.

---

## 7. Accessibility and readability

* All tabular content is real DOM text (selectable, copyable, screen-reader accessible)
  after fix 7 above.
* Body text is 0.97rem with 1.6 line height; the smallest text is the 0.79rem source
  footer. Nothing requires zooming.
* Chart titles and axis labels are descriptive enough to stand alone.
* Hover tooltips on every chart give exact values at 4 decimal places.

---

## 8. Privacy and reproducibility

* `Data_Données/pumf_cchs.csv` and `Data_Données/cchs_escc_bsw.csv` are never opened. Verified
  by inspection of the whole `dashboard/` package — the only file paths constructed are
  `notebooks/*.csv`.
* The single example respondent row is synthetic and labelled synthetic on screen.
* No secrets, tokens or credentials exist in the dashboard.
* All paths resolve from `__file__`, so the app runs from any working directory and on
  Streamlit Community Cloud.
* `requirements.txt` at the repository root now pins the three tested versions.

---

## 9. Remaining issues and things for you to decide

1. **`requirements.txt` was previously empty and tracked.** Filling it modifies a tracked
   file. This was authorised, but it is the only tracked file this task changes.
2. **Version pins are exact** (`streamlit==1.63.0`, `pandas==3.0.5`, `plotly==7.0.0`).
   pandas 3.0.5 is very new; if Streamlit Cloud has trouble resolving it, relaxing to
   `pandas>=2.2` is the first thing to try.
3. **The repository README is still a planning-era document.** It lists D3, E1 and E2 under
   "Planned Experimental Structure" and shows an outdated file tree. Per your instruction I
   did not touch it. It should be updated in the separate README pass, along with adding the
   dashboard link.
4. **No deployment URL exists yet.** The dashboard README documents the deployment steps but
   invents no URL.
5. **Playwright was installed for QA only.** It is a test dependency and is deliberately
   absent from `requirements.txt`.
6. **The "See the individual fold scores" table** shows folds for the currently selected CV
   metric only. That is intentional, but if you would rather show all three metrics at once,
   say so.

---

## 10. Screenshot index

Nine full-page captures (`01_…` to `09_…`), sixteen control-state captures (`ctrl_…`), and
one zoomed table detail (`detail_model_table.png`) are in `dashboard/screenshots/`.
All 26 were visually inspected; the nine issues in section 5 were found that way.

---

# Appendix — Pre-deployment review

Performed after implementation sign-off, on a clean virtual environment and a fresh clone.

## A. Clean-environment install

A new venv was created and **only** `requirements.txt` was installed. All three pins resolved
with no conflicts and no dependency backtracking:

```
python 3.12.0 · streamlit 1.63.0 · pandas 3.0.5 · plotly 7.0.0
```

`playwright` was confirmed **absent** from that venv, proving the QA tooling is not a runtime
dependency. No version was changed: nothing failed, so nothing needed changing.

## B. Fresh-clone deployment simulation

The repository was cloned to a new path, the pending (still uncommitted) `dashboard/` and
`requirements.txt` were copied in, and the app was launched there with the clean venv:

* All **10 result CSVs are present in a fresh clone**, confirming the data the app needs is
  already tracked in git.
* `Data_Données/` is **absent from the clone entirely** — and the app runs anyway. The clone
  is 12 MB against a ~1.1 GB raw PUMF, which is direct proof that neither the raw CCHS CSV
  nor the bootstrap-weight CSV is required.
* All 9 pages and all 16 controls pass against the clone. No console errors, no startup errors.

## C. Launch-location independence

The app was started successfully three ways, all serving identical content:

| Launch | Command | Result |
|---|---|---|
| Repository root (documented) | `streamlit run dashboard/app.py` | pass |
| Unrelated working directory | `streamlit run /abs/path/dashboard/app.py` from `/tmp` | pass |
| Inside `dashboard/` (likely user error) | `streamlit run app.py` | pass |

Paths resolve from `__file__`, so the working directory is irrelevant. A scan confirmed **no
absolute paths** anywhere in the dashboard package, and the only third-party imports are
`streamlit`, `pandas` and `plotly`.

## D. Re-verification

| Check | Result |
|---|---|
| 72 data assertions (run inside the clean venv) | all pass |
| Confusion matrices sum to 13,249 | all six pass |
| Variable metadata coverage and `used_in` consistency | no gaps, no mismatches |
| F schema handling (`original_candidate_count`, no `raw_feature_count`) | correct |
| 9 pages load | all pass, no errors |
| 16 interactive controls | all pass |
| Deep links `?page=…` for all 9 pages | all pass, sidebar radio state matches |
| Invalid `?page=` value | falls back to Overview |
| Static tables DOM-rendered | 11 DOM tables, **0 canvas grids** |
| Scientific guardrails | 24 of 24 pass |
| Forbidden-phrase scan | none present |

The guardrail sweep was re-run with the required selections made (Experiment F selected, and
WTS_M / CCC_80 / CCC_90 / RHC_05 chosen in the Variable Explorer), because several guardrail
statements live in content that only renders once the relevant item is selected. An earlier
sweep that used only default selections produced false failures for exactly that reason.

## E. Issue found and fixed in this pass

One documentation inaccuracy: `DASHBOARD_BLUEPRINT.md` listed `requirements.txt` inside
`dashboard/` and omitted `ui.py`. The file layout section was corrected to show the
dependency file at the repository root — which is where Streamlit Community Cloud reads it
from, and which avoids a duplicate source of truth — with a short note recording the change
from the original plan.

No application code was changed in this pass.

## F. Pre-deployment status: **PASS**
