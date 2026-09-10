"""Experiment Explorer: the six completed feature conditions, and how they compare."""

import plotly.graph_objects as go
import streamlit as st

import content as C
import data_sources as D
import ui

ORDER = ["A", "B", "C", "D1", "D2", "F"]


def _new_variables(condition):
    """Variables this condition adds relative to its comparator (for chip highlighting)."""
    comparator = C.EXPERIMENTS[condition]["comparator"]
    if not comparator:
        return []
    return [f for f in D.feature_list(condition)
            if f not in D.feature_list(comparator)]


def _condition_chart(df, metric):
    values = [float(df.loc[c, metric]) for c in ORDER]
    colours = [ui.ORANGE if c == "F" else ui.BLUE for c in ORDER]
    fig = go.Figure(go.Bar(
        x=ORDER, y=values, marker_color=colours,
        text=[f"{v:.3f}" for v in values], textposition="outside",
        hovertemplate="Condition %{x}: %{y:.3f}<extra></extra>"))
    ui.base_layout(fig, height=350,
                   title=f"{D.METRIC_LABELS[metric]} across all six feature conditions",
                   ytitle=D.METRIC_LABELS[metric], xtitle="Feature condition")
    # zero-anchored axis so bar heights are honest
    fig.update_yaxes(range=[0, max(values) * 1.22])
    return fig


def render():
    df = D.load_experiments()
    ui.page_header("Part 3 · Experiments", "Experiment explorer",
                   "Six feature conditions run under one fixed framework. Only the information "
                   "given to the model changes.")

    ui.callout(
        "The population (66,242 respondents), the stratified split "
        "(42,394 / 10,599 / 13,249, random_state = 42), the model configuration and the "
        "validation-only threshold procedure are identical in every condition. That is what "
        "makes the differences attributable to the features.")

    # ------------------------------------------------------------- selector
    condition = st.selectbox(
        "Choose a feature condition", ORDER,
        format_func=lambda c: f"{c} — {C.EXPERIMENTS[c]['name'].split(' - ')[-1]}",
        index=4, key="experiment_choice")

    meta = C.EXPERIMENTS[condition]
    row = df.loc[condition]
    comparator = meta["comparator"]

    st.markdown(f"## {meta['name']}")
    st.markdown(f"**Research question.** {meta['question']}")
    st.markdown(f"**What changed.** {meta['changed']}")

    # ------------------------------------------------------------- features
    st.markdown("### Features used")
    feats = D.feature_list(condition)
    ui.chips(feats, highlight=_new_variables(condition))
    caption = f"{len(feats)} variables → {int(row['processed_feature_count'])} columns after one-hot encoding." \
        if "processed_feature_count" in row.index and not str(row.get("processed_feature_count")) == "nan" \
        else f"{len(feats)} variables."
    if comparator:
        caption += f"  Highlighted variables are new relative to condition {comparator}."
    st.caption(caption)

    # ------------------------------------------------------------- metrics
    st.markdown("### Test-set results")
    st.caption(f"Locked classification threshold: **{float(row['threshold']):.3f}** "
               "(chosen on validation data, then locked before the test set was scored).")

    cols = st.columns(6)
    for col, metric in zip(cols, D.METRICS):
        value = float(row[metric])
        delta = None
        good = None
        if comparator:
            base = float(df.loc[comparator, metric])
            delta = value - base
            if abs(delta) < 5e-4:
                delta, good = None, None
            else:
                good = delta > 0
        ui.metric_card(col, f"{value:.3f}", D.METRIC_LABELS[metric],
                       ui.ORANGE if metric in ("f1", "pr_auc") else ui.BLUE,
                       delta=delta, delta_good=good)
    if comparator:
        st.caption(f"Arrows compare against condition {comparator}.")

    with st.expander("What do these metrics mean?"):
        for metric in D.METRICS + ["test_log_loss"]:
            short, longer = C.METRIC_GLOSSARY[metric]
            st.markdown(f"**{D.METRIC_LABELS[metric]}** — {short}")
            st.caption(longer)

    # ------------------------------------------------------------- confusion + reading
    cm1, cm2 = st.columns([0.52, 0.48])
    with cm1:
        st.markdown("### Confusion matrix")
        st.plotly_chart(
            ui.confusion_matrix_figure(int(row["true_negatives"]), int(row["false_positives"]),
                                       int(row["false_negatives"]), int(row["true_positives"])),
            width="stretch", config={"displayModeBar": False})
        if condition in ("A", "B"):
            st.caption("Source: executed Experiment " + condition + " notebook. The A and B "
                       "result CSVs were saved without confusion-matrix columns.")
    with cm2:
        st.markdown("### What this tells us")
        st.write(meta["interpretation"])
        ui.callout(meta["caveat"], kind="warn")

    # ------------------------------------------------------------- F extra panel
    if condition == "F":
        st.markdown("### What the L1 screening step actually did")
        f1, f2, f3 = st.columns(3)
        ui.metric_card(f1, int(row["original_candidate_count"]),
                       "candidate variables went in", ui.INK)
        ui.metric_card(f2, int(row["selected_variable_count"]), "were retained", ui.GREEN)
        ui.metric_card(f3, int(row["original_candidate_count"] - row["selected_variable_count"]),
                       "were dropped", ui.RED)
        st.caption("Same 16 in, 16 out. The caveat above explains why that is not a "
                   "successful feature-selection result.")

    # ------------------------------------------------------------- comparison
    st.markdown("## What changed as the information changed?")
    st.write(
        "Choose one metric to compare all six conditions on the same scale. Only one metric is "
        "shown at a time, because accuracy, F1 and the AUC measures do not live on comparable "
        "scales.")
    metric = st.selectbox("Metric to compare", D.METRICS,
                          format_func=lambda m: D.METRIC_LABELS[m],
                          index=D.METRICS.index("roc_auc"), key="condition_metric")
    st.plotly_chart(_condition_chart(df, metric), width="stretch",
                    config={"displayModeBar": False})
    st.caption("Axis starts at zero, so bar heights are directly comparable. "
               "Condition F is highlighted because its feature representation is broader than "
               "the others, so it is not a like-for-like comparison.")

    ui.callout(
        "Read across the conditions rather than looking for a winner. A and B are two different "
        "hand-picked representations; C is a deliberately reduced reference; D1 and D2 add one "
        "reported condition each; F is a wider documented set on a slightly different "
        "preprocessing setup.")

    ui.source_note(
        "Numbers come straight from the six experiment CSV files in notebooks/. A and B's "
        "confusion matrices aren't in those files, so those two come from the executed "
        "notebooks instead.")
