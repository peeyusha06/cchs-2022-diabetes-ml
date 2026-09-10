"""Robustness & Interpretability: 5-fold stability, and what the models leaned on."""

import plotly.graph_objects as go
import streamlit as st

import content as C
import data_sources as D
import ui

CV_METRICS = ["roc_auc", "pr_auc", "log_loss"]


def _cv_figure(summary, metric):
    mean_col, std_col = f"{metric}_mean", f"{metric}_std"
    models = list(summary["model"])
    means = [float(summary.loc[summary["model"] == m, mean_col].iloc[0]) for m in models]
    stds = [float(summary.loc[summary["model"] == m, std_col].iloc[0]) for m in models]

    fig = go.Figure(go.Scatter(
        x=models, y=means, mode="markers",
        marker=dict(size=13, color=[ui.MODEL_COLOURS[m] for m in models],
                    line=dict(width=1.4, color=ui.INK)),
        error_y=dict(type="data", array=stds, visible=True, thickness=1.6, width=9,
                     color=ui.INK),
        hovertemplate="%{x}<br>mean %{y:.4f}<extra></extra>"))
    for m, mu, sd in zip(models, means, stds):
        fig.add_annotation(x=m, y=mu + sd, yshift=16, showarrow=False,
                           text=f"{mu:.4f} ± {sd:.4f}",
                           font=dict(size=11.5, color=ui.INK))

    direction = "lower is better" if metric == "log_loss" else "higher is better"
    ui.base_layout(fig, height=360,
                   title=f"5-fold {D.METRIC_LABELS[metric]} — mean ± standard deviation "
                         f"({direction})",
                   ytitle=D.METRIC_LABELS[metric])
    lo = min(mu - sd for mu, sd in zip(means, stds))
    hi = max(mu + sd for mu, sd in zip(means, stds))
    pad = (hi - lo) * 0.55 + 1e-4
    fig.update_yaxes(range=[lo - pad, hi + pad])
    return fig


def _importance_figure(df, model_col, rank_col, title):
    d = df.sort_values(rank_col)
    fig = go.Figure(go.Bar(
        x=list(d[model_col]), y=list(d["variable"]), orientation="h",
        marker_color=ui.BLUE,
        text=[f"rank {int(r)}" for r in d[rank_col]], textposition="outside",
        hovertemplate="%{y}: %{x:.4f}<extra></extra>"))
    ui.base_layout(fig, height=400, title=title, xtitle="Aggregated importance value")
    fig.update_yaxes(autorange="reversed")
    fig.update_xaxes(range=[0, float(d[model_col].max()) * 1.3])
    return fig


def render():
    summary = D.load_cv_summary()
    folds = D.load_cv_folds()
    interp = D.load_interpretability()
    facts = D.dataset_facts()

    ui.page_header("Part 5 · Trust", "Robustness and interpretability",
                   "How stable the comparison is, and which variables the fitted models "
                   "actually used.")

    # ============================================================ 5-fold CV
    st.markdown("## Five-fold cross-validation")
    st.write(
        f"A single split could flatter or penalise a model by luck. This check divides the "
        f"{facts['train']:,} training rows into five equal parts and trains five times, holding "
        "back a different part for scoring each time. The spread across those five scores shows "
        "how sensitive the result is to how the data happened to be divided.")
    ui.callout(
        "Only the training portion was used. The validation and test sets were left "
        "untouched, so this check does not consume the held-out evaluation.")

    metric = st.selectbox("Metric", CV_METRICS, format_func=lambda m: D.METRIC_LABELS[m],
                          index=0, key="cv_metric")
    st.plotly_chart(_cv_figure(summary, metric), width="stretch",
                    config={"displayModeBar": False})
    st.caption(
        "Vertical axis is zoomed to make the standard-deviation bars visible — it does not "
        "start at zero. Overlapping bars mean the models are not clearly separated. "
        "Mean and standard deviation are the values the notebook itself saved.")

    with st.expander("See the individual fold scores"):
        pivot = folds.pivot(index="fold", columns="model", values=metric)
        pivot = pivot.reset_index().rename(columns={"fold": "Fold"})
        ui.static_table(pivot, formats={c: "{:.4f}" for c in pivot.columns if c != "Fold"})

    cc1, cc2 = st.columns(2)
    with cc1:
        st.markdown(
            "<div class='callout callout-good'><div class='callout-title'>What this does show"
            "</div><p>The models' error bars overlap on ROC-AUC and PR-AUC. The mean ROC-AUC "
            "spread is about 0.003 — smaller than the fold-to-fold variation within any single "
            "model.</p></div>", unsafe_allow_html=True)
    with cc2:
        st.markdown(
            "<div class='callout callout-warn'><div class='callout-title'>What this does NOT "
            "show</div><p>It is a stability check on already-chosen settings — not a new tuning "
            "run, not an unbiased estimate of final performance, and not a replacement for the "
            "held-out test set.</p></div>", unsafe_allow_html=True)
    ui.why_expander(C.WHY["cv"])

    # ============================================================ interpretability
    st.markdown("## What the models actually leaned on")
    st.write(
        "Each model was refit on the training data and its variable importances were "
        "aggregated back to the original CCHS variables. Age, reported high blood pressure, "
        "reported high cholesterol and BMI class occupy the top four positions for all three "
        "model classes.")

    model_choice = st.selectbox(
        "Show importance for", ["Logistic Regression", "Random Forest", "Gradient Boosting"],
        key="interp_model")
    col_map = {
        "Logistic Regression": ("Logistic Regression (abs coef sum)", "LR_rank"),
        "Random Forest": ("Random Forest (importance sum)", "RF_rank"),
        "Gradient Boosting": ("Gradient Boosting (importance sum)", "GB_rank"),
    }
    value_col, rank_col = col_map[model_choice]
    unit = ("summed absolute coefficient" if model_choice == "Logistic Regression"
            else "summed impurity importance")
    st.plotly_chart(
        _importance_figure(interp, value_col, rank_col,
                           f"{model_choice} — variables ranked by {unit}"),
        width="stretch", config={"displayModeBar": False})

    with st.expander("Compare the rank order across all three models"):
        ranks = interp[["variable", "LR_rank", "RF_rank", "GB_rank"]].sort_values("RF_rank")
        ranks.columns = ["Variable", "Logistic Regression", "Random Forest", "Gradient Boosting"]
        ui.static_table(ranks)
        st.caption("Lower numbers mean higher importance within that model.")

    st.markdown("### Three cautions about these rankings")
    cautions = [
        ("They are not on one common scale", ui.RED,
         "Logistic Regression is ranked by the summed size of its coefficients; the tree models "
         "are ranked by how much each variable reduced impurity when splitting. These are "
         "different quantities. Only the rank order within each model is comparable."),
        ("GEOGPRV's high Logistic Regression rank is partly an artefact", ui.ORANGE,
         "Province has 11 categories, so it becomes 11 encoded columns. Summing the size of 11 "
         "coefficients inflates its total relative to a variable with 2 categories. The tree "
         "models rank it 5th and 6th."),
        ("Importance is not causation", ui.RED,
         "A high rank means the fitted model used that variable to separate the two groups. It "
         "says nothing about mechanism, and nothing about what would happen if the variable "
         "changed."),
    ]
    for title, colour, body in cautions:
        st.markdown(
            f"<div class='card' style='border-left-color:{colour};margin-bottom:0.55rem'>"
            f"<div style='font-weight:700;color:{ui.INK};margin-bottom:0.2rem'>{title}</div>"
            f"<div style='font-size:0.9rem;color:{ui.BODY};line-height:1.55'>{body}</div>"
            f"</div>", unsafe_allow_html=True)

    with st.expander("What is impurity importance?"):
        st.write(
            "A decision tree splits the data into groups that are more uniform than the group "
            "it started with. Impurity importance measures how much each variable reduced that "
            "mixedness across all the splits in the model, averaged over all the trees. It says "
            "how useful a variable was for splitting — not the direction of the effect, and not "
            "whether the variable matters outside this model.")

    ui.source_note(
        "Sources: d2_robustness_5fold_results.csv (per-fold scores plus the mean and std rows "
        "saved by the notebook) and d2_interpretability_results.csv, both read directly from "
        "notebooks/. Cross-validation used StratifiedKFold with shuffle = True and "
        "random_state = 42 on the training portion only.")
