"""Understand the Data: the CCHS, the PUMF, the target variable, and the class imbalance."""

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

import content as C
import data_sources as D
import ui


def _funnel_figure(facts):
    """Three-stage exclusion funnel, drawn as labelled blocks (values shown, not implied)."""
    stages = [
        (f"{facts['respondents']:,}", "All CCHS 2022 respondents", ui.BLUE, ui.PANEL),
        (f"−{facts['not_stated']:,}", "Removed: CCC_05 = 9 (not stated)", ui.RED, ui.WARN_BG),
        (f"{facts['modelling_population']:,}", "Modelling population", ui.GREEN, ui.GOOD_BG),
    ]
    fig = go.Figure()
    for i, (value, label, colour, bg) in enumerate(stages):
        fig.add_shape(type="rect", x0=i * 1.1, x1=i * 1.1 + 0.92, y0=0, y1=1,
                      fillcolor=bg, line=dict(color=ui.RULE, width=1), layer="below")
        fig.add_annotation(x=i * 1.1 + 0.46, y=0.66, text=f"<b>{value}</b>", showarrow=False,
                           font=dict(size=26, color=colour))
        fig.add_annotation(x=i * 1.1 + 0.46, y=0.26, text=label, showarrow=False,
                           font=dict(size=12, color=ui.BODY))
        if i < 2:
            fig.add_annotation(x=i * 1.1 + 1.01, y=0.5, text="→", showarrow=False,
                               font=dict(size=22, color=ui.MUTED))
    fig.update_xaxes(visible=False, range=[-0.05, 3.25])
    fig.update_yaxes(visible=False, range=[0, 1])
    fig.update_layout(template="simple_white", height=190,
                      margin=dict(l=0, r=0, t=6, b=0), plot_bgcolor="white")
    return fig


def _balance_figure(facts):
    neg, pos = facts["negatives"], facts["positives"]
    fig = go.Figure()
    fig.add_bar(x=[neg], y=["Modelling population"], orientation="h", marker_color=ui.BLUE,
                name=f"No diabetes — {neg:,} (90.95%)",
                hovertemplate="No diabetes: %{x:,}<extra></extra>")
    fig.add_bar(x=[pos], y=["Modelling population"], orientation="h", marker_color=ui.ORANGE,
                name=f"Reports diabetes — {pos:,} (9.05%)",
                hovertemplate="Reports diabetes: %{x:,}<extra></extra>")
    fig.update_layout(barmode="stack")
    ui.base_layout(fig, height=190, showlegend=True,
                   xtitle="Respondents in the modelling population")
    fig.update_yaxes(showticklabels=False)
    return fig


def render():
    facts = D.dataset_facts()
    ui.page_header("Part 1 · The data", "Understand the data",
                   "Where the numbers come from, and what the project is trying to classify.")

    # ------------------------------------------------------------------ CCHS
    st.markdown("## What is the CCHS?")
    st.write(
        "The Canadian Community Health Survey is a large national survey run by Statistics "
        "Canada. It covers people aged 12 and older, and it measures health status, health-care "
        "use and the determinants of health. The 2022 cycle was a major redesign, so "
        "comparisons with earlier cycles need caution.")
    ui.callout(
        "The CCHS is <b>cross-sectional</b>: each person is observed once. That single word "
        "limits every conclusion on this dashboard, because nothing in the data records what "
        "happened before or after.", kind="warn")

    # ------------------------------------------------------------------ PUMF
    st.markdown("## What is a PUMF?")
    left, right = st.columns([0.5, 0.5])
    with left:
        st.write(
            "A **Public Use Microdata File** is the publicly released version of the survey. "
            "It contains row-level records — one row per respondent — but to protect "
            "confidentiality the answers are grouped into broad categories and stored as "
            "numeric codes rather than exact values.")
        st.write(
            f"The file used here is **{facts['respondents']:,} rows × "
            f"{facts['variables']} columns**. One row is one respondent's full set of answers; "
            "one column is one survey variable.")
    with right:
        st.markdown("**Exact age is not in the file. Instead:**")
        ui.static_table(pd.DataFrame({
            "Code": ["1", "2", "3", "4", "5"],
            "Meaning": ["12 to 17 years", "18 to 34 years", "35 to 49 years",
                        "50 to 64 years", "65 and older"],
            "Respondents": ["3,761", "10,123", "12,829", "16,399", "23,967"],
        }))
        st.caption("Actual DHHGAGE codes and frequencies from the CCHS 2022 PUMF Data Dictionary.")

    with st.expander("What does one row actually look like?"):
        st.write(
            "The row below is **synthetic** — it was constructed to show the structure. "
            "No real respondent record appears anywhere in this dashboard.")
        ui.static_table(pd.DataFrame([{
            "DHHGAGE": "4", "DHH_SEX": "2", "GEOGPRV": "35", "BMI_CLASS": "2",
            "CCC_80": "1", "CCC_05 (target)": "1",
        }, {
            "DHHGAGE": "50-64 yrs", "DHH_SEX": "female", "GEOGPRV": "Ontario",
            "BMI_CLASS": "overweight/obese", "CCC_80": "reports high BP",
            "CCC_05 (target)": "reports diabetes",
        }]))

    # ------------------------------------------------------------------ target
    st.markdown("## The target variable: CCC_05")
    ui.callout("Survey question: <b>“Do you have diabetes?”</b> &nbsp;&nbsp; "
               "<span style='color:#6B7A88'>Universe: respondents with DOCCC = 1</span>")
    ui.static_table(pd.DataFrame({
        "Code": ["1", "2", "9"],
        "Meaning": ["Yes — reports diabetes", "No", "Not stated"],
        "Respondents": [f"{facts['positives']:,}", f"{facts['negatives']:,}",
                        f"{facts['not_stated']:,}"],
        "Used in modelling?": ["Yes — the positive class", "Yes — the negative class",
                               "No — excluded"],
    }))

    with st.expander("Why is code 9 excluded?"):
        st.write(
            "“Not stated” gives the model no answer to learn from and no answer to score "
            f"against. Keeping those {facts['not_stated']} respondents would mean inventing a "
            "label for them, so they are removed before any modelling begins.")

    st.markdown("### Who ends up in the model")
    st.plotly_chart(_funnel_figure(facts), width="stretch",
                    config={"displayModeBar": False})

    # ------------------------------------------------------------------ imbalance
    st.markdown("## The positive class is rare")
    st.plotly_chart(_balance_figure(facts), width="stretch",
                    config={"displayModeBar": False})

    c1, c2 = st.columns([0.42, 0.58])
    with c1:
        ui.metric_card(c1, "9.05%", "of the modelling population reports diabetes "
                                    f"({facts['positives']:,} of "
                                    f"{facts['modelling_population']:,})", ui.ORANGE)
    with c2:
        ui.callout(
            "A model that simply answered “no diabetes” for every single person would score "
            "<b>90.95% accuracy</b> and find <b>zero</b> of the 5,994 people who report "
            "diabetes. That is why this project judges models mainly on precision, recall, "
            "F1 and PR-AUC rather than on accuracy.", title="The accuracy trap", kind="warn")

    with st.expander("Why does 9.05% change how we judge the models?"):
        st.write(
            "When one class is rare, a metric that counts all correct answers equally is "
            "dominated by the easy majority. Precision and recall look only at the positive "
            "class, F1 balances them, and PR-AUC summarises positive-class ranking quality "
            "across thresholds. All four are explained on the Experiment Explorer page.")

    ui.callout(
        "This 9.05% is an <b>unweighted</b> share of the modelling population. The survey's "
        "own weighted percentage differs — see the sampling-weight explainer on the Feature "
        "Audit page.", kind="info")

    ui.source_note(
        "Sources: Statistics Canada, CCHS 2022 PUMF Data Dictionary (September 2025) for "
        "CCC_05 and DHHGAGE codes and frequencies; Notebook 02 for the modelling population "
        "and class counts.")
