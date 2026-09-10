"""Fresh Holdout: disclose the test-set reuse problem, then show the check run because of it."""

import plotly.graph_objects as go
import streamlit as st

import content as C
import data_sources as D
import ui

METRICS = D.METRICS + ["test_log_loss"]


def _paired_figure(original, fresh, metric):
    models = list(original["model"])
    orig_vals = [float(original.loc[original["model"] == m, metric].iloc[0]) for m in models]
    fresh_vals = [float(fresh.loc[fresh["model"] == m, metric].iloc[0]) for m in models]

    fig = go.Figure()
    fig.add_bar(x=models, y=orig_vals, name="Original split (seed 42)",
                marker_color="#9BB4C9",
                text=[f"{v:.3f}" for v in orig_vals], textposition="outside",
                hovertemplate="Original: %{y:.4f}<extra></extra>")
    fig.add_bar(x=models, y=fresh_vals, name="Fresh split (seed 137)",
                marker_color=ui.ORANGE,
                text=[f"{v:.3f}" for v in fresh_vals], textposition="outside",
                hovertemplate="Fresh: %{y:.4f}<extra></extra>")
    direction = "lower is better" if metric == "test_log_loss" else "higher is better"
    ui.base_layout(fig, height=370, showlegend=True,
                   title=f"{D.METRIC_LABELS[metric]} — original vs fresh split ({direction})",
                   ytitle=D.METRIC_LABELS[metric])
    fig.update_layout(barmode="group")
    fig.update_yaxes(range=[0, max(orig_vals + fresh_vals) * 1.28])
    return fig


def render():
    original = D.load_model_comparison()
    fresh = D.load_fresh_holdout()
    facts = D.dataset_facts()

    ui.page_header("Part 5 · Trust", "Fresh holdout check",
                   "An honest problem, and the check that was run because of it.")

    # ------------------------------------------------------------- the problem
    st.markdown("## The problem: the same test set was scored repeatedly")
    st.write(
        f"Experiments A, B, C, D1 and D2 all used the same population and the same "
        f"random_state = {facts['random_state']} split, so all five were scored on the "
        f"identical {facts['test']:,}-row test partition.")

    chain = st.columns(5)
    for col, label in zip(chain, ["A", "B", "C", "D1", "D2"]):
        col.markdown(
            f"<div style='text-align:center;padding:0.5rem 0;border-radius:6px;"
            f"background:{ui.PANEL};border:1px solid {ui.RULE};font-weight:700;"
            f"color:{ui.INK}'>{label}</div>", unsafe_allow_html=True)
    st.caption(f"↓ every one of them scored against the identical test partition "
               f"(seed {facts['random_state']})")

    st.write(
        "What was still done correctly: within each experiment, the model and threshold "
        "were locked using training and validation data before the test set was touched. "
        "No threshold was ever tuned on test data.")
    ui.callout(
        "Across the project, those test results were visible while deciding what to try "
        "next. That makes the sequence an iterative development process, not five "
        "untouched final evaluations.", title="The limitation that remains", kind="warn")

    # ------------------------------------------------------------- the check
    st.markdown("## The check: deal the split again")
    seed = int(fresh["split_random_state"].iloc[0])
    steps = [
        ("Re-split", ui.BLUE,
         f"The same {facts['modelling_population']:,} people are divided again, using seed "
         f"{seed} instead of {facts['random_state']}. This produces a test set of "
         "different individuals."),
        ("Re-fit", ui.BLUE,
         "The three D2 models are retrained on the new training portion, using the exact "
         "configurations already chosen."),
        ("Re-use the locked thresholds", ui.ORANGE,
         "0.68 for Logistic Regression, 0.68 for Random Forest, 0.70 for Gradient Boosting. "
         "These carry over unchanged."),
        ("Score once", ui.GREEN,
         "The new test set is evaluated a single time. No tuning, no searching, no threshold "
         "re-selection."),
    ]
    for title, colour, body in steps:
        st.markdown(
            f"<div class='card' style='border-left-color:{colour};margin-bottom:0.5rem'>"
            f"<span style='font-weight:700;color:{ui.INK}'>{title}</span>"
            f"<span style='color:{ui.BODY};margin-left:0.6rem;font-size:0.92rem'>{body}</span>"
            f"</div>", unsafe_allow_html=True)
    ui.why_expander(C.WHY["fresh"])

    # ------------------------------------------------------------- results
    st.markdown("## Results")
    metric = st.selectbox("Compare one metric", METRICS,
                          format_func=lambda m: D.METRIC_LABELS[m],
                          index=METRICS.index("f1"), key="fresh_metric")
    st.plotly_chart(_paired_figure(original, fresh, metric), width="stretch",
                    config={"displayModeBar": False})
    st.caption("Axis starts at zero. The original-split values come from "
               "model_comparison_D2_results.csv; the fresh values from "
               "d2_fresh_holdout_results.csv.")
    ui.metric_explainer(metric, C.METRIC_GLOSSARY)

    view = st.radio("Show the full table for", ["Fresh split (seed 137)",
                                                "Original split (seed 42)"],
                    horizontal=True, key="fresh_table_view")
    src = fresh if view.startswith("Fresh") else original
    table = src[["model", "threshold"] + METRICS].copy()
    table.columns = ["Model", "Threshold"] + [D.METRIC_LABELS[m] for m in METRICS]
    ui.static_table(
        table,
        formats={D.METRIC_LABELS[m]: ("{:.4f}" if m == "test_log_loss" else "{:.3f}")
                 for m in METRICS} | {"Threshold": "{:.2f}"})

    # ------------------------------------------------------------- reading
    st.markdown("## How to read this")
    st.markdown(
        "**What it supports**\n"
        "- Every model scored slightly higher, so the original split was not flattering "
        "the results\n"
        "- The three models stayed close together, as before\n"
        "- Random Forest again had the lowest log loss; Logistic Regression again had the "
        "highest PR-AUC\n"
        "- The locked thresholds still produced sensible behaviour on unseen rows")
    st.markdown(
        "**What it does not support**\n"
        "- It is one additional split of the same survey, not external validation\n"
        "- It says nothing about another CCHS cycle, another country, or a clinical "
        "population\n"
        "- It does not remove the test-set reuse limitation from A-D2\n"
        "- Small re-orderings between Random Forest and Gradient Boosting on F1 remain "
        "noise, not evidence")

    ui.callout(
        "The honest one-line summary: on a second, previously unused split of the same "
        "survey, the D2 models behaved much as they did on the first, which is "
        "<b>supplementary confirmation, not proof of generalisation</b>.")

    ui.source_note(
        "From d2_fresh_holdout_results.csv (split random_state=137) and "
        "model_comparison_D2_results.csv, both in notebooks/.")
