"""Model Comparison: three algorithms on the frozen D2 feature set."""

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

import content as C
import data_sources as D
import ui

# Metrics where a LOWER value is better.
LOWER_IS_BETTER = {"test_log_loss"}
COMPARE_METRICS = D.METRICS + ["test_log_loss"]


def _bar(df, metric):
    values = [float(df.loc[df["model"] == m, metric].iloc[0]) for m in df["model"]]
    fig = go.Figure(go.Bar(
        x=list(df["model"]), y=values,
        marker_color=[ui.MODEL_COLOURS[m] for m in df["model"]],
        text=[f"{v:.4f}" if metric == "test_log_loss" else f"{v:.3f}" for v in values],
        textposition="outside",
        hovertemplate="%{x}: %{y:.4f}<extra></extra>"))
    direction = "lower is better" if metric in LOWER_IS_BETTER else "higher is better"
    ui.base_layout(fig, height=340,
                   title=f"{D.METRIC_LABELS[metric]} on the D2 test set ({direction})",
                   ytitle=D.METRIC_LABELS[metric])
    fig.update_yaxes(range=[0, max(values) * 1.25])
    return fig


def render():
    mc = D.load_model_comparison()
    exp = D.load_experiments()

    ui.page_header("Part 4 · Models", "Model comparison",
                   "The D2 feature set is frozen. Only the algorithm changes.")

    st.markdown("## Why run this comparison?")
    st.write(
        "The experiments showed that changing the features changed the score. The natural "
        "follow-up question is whether changing the algorithm would change it more, less, or "
        "about the same. Holding the features, population, split and threshold procedure "
        "constant isolates the effect of the model itself.")
    ui.why_expander(C.WHY["models"])

    with st.expander("What settings were tried, and how were they chosen?"):
        st.write(
            "The searches were deliberately small. The goal was to compare model classes, not "
            "run an exhaustive tuning study. Every choice below was made on validation data "
            "only, then locked before the test set was scored.")
        ui.static_table(pd.DataFrame([
            {"Model": "Logistic Regression",
             "Settings tried on validation": "none — the project's existing configuration was reused",
             "Selected": "class_weight = balanced"},
            {"Model": "Random Forest",
             "Settings tried on validation": "3 combinations of tree count and depth",
             "Selected": "200 trees, max depth 10"},
            {"Model": "Gradient Boosting",
             "Settings tried on validation": "2 combinations of tree count and learning rate",
             "Selected": "200 trees, learning rate 0.05"},
        ]))
        st.caption("Selected configurations are the `config` column of "
                   "model_comparison_D2_results.csv.")

    # -------------------------------------------------------------- table
    st.markdown("## Results on the D2 test set")
    table = mc[["model", "threshold"] + COMPARE_METRICS].copy()
    table.columns = ["Model", "Threshold"] + [D.METRIC_LABELS[m] for m in COMPARE_METRICS]

    def _highlight(col):
        """Mark the best value in each column.

        Comparison happens at the precision actually displayed, so two models that
        both show 0.840 are both marked - highlighting only one would imply a
        difference the reader cannot see (RF and GB differ by 0.0004 on accuracy).
        """
        if col.name in ("Model", "Threshold"):
            return ["" for _ in col]
        dp = 4 if col.name == "Test log loss" else 3
        shown = col.round(dp)
        best = shown.min() if col.name == "Test log loss" else shown.max()
        return [f"color:{ui.GREEN};font-weight:700" if v == best else "" for v in shown]

    ui.static_table(
        table,
        formats={D.METRIC_LABELS[m]: ("{:.4f}" if m == "test_log_loss" else "{:.3f}")
                 for m in COMPARE_METRICS} | {"Threshold": "{:.2f}"},
        highlight=_highlight)
    st.caption("Green marks the best value in each column. For log loss, lower is better.")

    # -------------------------------------------------------------- chart
    metric = st.selectbox("Compare one metric", COMPARE_METRICS,
                          format_func=lambda m: D.METRIC_LABELS[m],
                          index=COMPARE_METRICS.index("roc_auc"), key="model_metric")
    st.plotly_chart(_bar(mc, metric), width="stretch", config={"displayModeBar": False})
    st.caption("Axis starts at zero, so bar heights are directly comparable.")
    ui.metric_explainer(metric, C.METRIC_GLOSSARY)

    # -------------------------------------------------------------- no winner
    st.markdown("## No model wins outright")
    leads = [
        ("Gradient Boosting", ui.ORANGE,
         "highest F1 (0.365), ROC-AUC (0.815) and precision (0.285)"),
        ("Logistic Regression", ui.BLUE,
         "highest recall (0.542) and highest PR-AUC (0.289)"),
        ("Random Forest", ui.GREEN,
         "lowest test log loss (0.5058); ties with Gradient Boosting for highest accuracy"),
    ]
    for model, colour, text in leads:
        st.markdown(
            f"<div class='card' style='border-left-color:{colour};margin-bottom:0.5rem'>"
            f"<span style='font-weight:700;color:{ui.INK}'>{model}</span>"
            f"<span style='color:{ui.BODY};margin-left:0.6rem'>{text}</span></div>",
            unsafe_allow_html=True)

    f1_spread = mc["f1"].max() - mc["f1"].min()
    feature_effect = float(exp.loc["D2", "f1"]) - float(exp.loc["C", "f1"])
    s1, s2 = st.columns(2)
    ui.metric_card(s1, f"{f1_spread:.3f}", "F1 spread across the three algorithms", ui.MUTED)
    ui.metric_card(s2, f"{feature_effect:.3f}",
                   "F1 change from feature condition C to D2", ui.ORANGE)
    ui.callout(
        "Changing the feature set moved F1 about six times as much as changing the algorithm "
        "did. That single comparison is the project's central result.")

    # -------------------------------------------------------------- reference model
    st.markdown("## Why Logistic Regression is the reference model")
    ui.callout(
        "<b>Test-set results were never used to select a model.</b> Using them to pick a winner "
        "would turn the final score into a best-of-three, which is exactly the circularity the "
        "three-way split exists to prevent.", kind="warn")
    r1, r2, r3 = st.columns(3)
    for col, (title, body, colour) in zip(
            (r1, r2, r3),
            [("Competitive",
              "Its F1 is within 0.005 of the best model, and it has the best PR-AUC and the "
              "best recall of the three.", ui.GREEN),
             ("Interpretable",
              "Its coefficients can be read directly, which is what makes the interpretability "
              "analysis possible.", ui.BLUE),
             ("Consistent",
              "It is the model used in every earlier feature experiment, so the whole A-to-F "
              "sequence stays comparable.", ui.BLUE)]):
        with col:
            st.markdown(
                f"<div class='card' style='border-left-color:{colour}'>"
                f"<div style='font-weight:700;color:{ui.INK};margin-bottom:0.25rem'>{title}</div>"
                f"<div style='font-size:0.9rem;color:{ui.BODY};line-height:1.5'>{body}</div>"
                f"</div>", unsafe_allow_html=True)
    ui.callout(
        "So the correct sentence is: “Logistic Regression was retained as the reference model "
        "because it is simpler and directly interpretable while performing comparably” — "
        "<b>not</b> “Logistic Regression was the best model”.", kind="good")
    ui.why_expander(C.WHY["logreg"])

    ui.source_note(
        "From model_comparison_D2_results.csv in notebooks/. The C-to-D2 F1 comparison also "
        "pulls from experiment_C_results.csv and experiment_D2_results.csv.")
