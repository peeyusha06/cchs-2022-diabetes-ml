"""Feature Audit: why 255 columns cannot be used directly, and how they became 216."""

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

import content as C
import data_sources as D
import ui


def _funnel_figure(a):
    stages = [
        (f"{a['total_columns']}", "All PUMF columns", ui.INK, ui.PANEL),
        ("−1", "The target itself (CCC_05)", ui.MUTED, "#FFFFFF"),
        (f"−{a['do_flags_removed']}", "Module inclusion flags", ui.MUTED, "#FFFFFF"),
        (f"{a['after_target_and_flags']}", "Remaining", ui.BLUE, ui.INFO_BG),
        (f"−{a['admin_removed']}", "Administrative / weight columns", ui.MUTED, "#FFFFFF"),
        (f"{a['candidate_pool']}", "Candidate predictors", ui.GREEN, ui.GOOD_BG),
    ]
    fig = go.Figure()
    for i, (value, label, colour, bg) in enumerate(stages):
        fig.add_shape(type="rect", x0=i * 1.06, x1=i * 1.06 + 0.92, y0=0, y1=1,
                      fillcolor=bg, line=dict(color=ui.RULE, width=1), layer="below")
        fig.add_annotation(x=i * 1.06 + 0.46, y=0.68, text=f"<b>{value}</b>", showarrow=False,
                           font=dict(size=21, color=colour))
        fig.add_annotation(x=i * 1.06 + 0.46, y=0.24, text=label, showarrow=False,
                           font=dict(size=10.5, color=ui.BODY))
        if i < len(stages) - 1:
            fig.add_annotation(x=i * 1.06 + 0.985, y=0.5, text="→", showarrow=False,
                               font=dict(size=17, color=ui.MUTED))
    fig.update_xaxes(visible=False, range=[-0.05, 6.4])
    fig.update_yaxes(visible=False, range=[0, 1])
    fig.update_layout(template="simple_white", height=175,
                      margin=dict(l=0, r=0, t=6, b=0), plot_bgcolor="white")
    return fig


def _grouping_figure(a):
    labels = ["Core<br>broadly applicable", "Review<br>need extra scrutiny",
              "Restricted<br>age- or region-limited"]
    values = [a["core"], a["review"], a["restricted"]]
    fig = go.Figure(go.Bar(
        x=labels, y=values, marker_color=[ui.GREEN, ui.ORANGE, ui.RED],
        text=[str(v) for v in values], textposition="outside",
        hovertemplate="%{x}: %{y} variables<extra></extra>"))
    ui.base_layout(fig, height=290, ytitle="Variables",
                   title="How the 216 candidates were grouped")
    fig.update_yaxes(range=[0, max(values) * 1.2])
    return fig


def _bmi_flow():
    """Age-conditional BMI rule, drawn as a small labelled diagram."""
    fig = go.Figure()
    boxes = [
        (0.0, 0.5, "One respondent", ui.PANEL, ui.INK),
        (1.25, 0.86, "Aged 12–17", ui.WARN_BG, ui.ORANGE),
        (1.25, 0.14, "Aged 18 or older", ui.INFO_BG, ui.BLUE),
        (2.5, 0.86, "take HWTDGWHO<br>(youth BMI)", "#FFFFFF", ui.BODY),
        (2.5, 0.14, "take HWTDGISW<br>(adult BMI)", "#FFFFFF", ui.BODY),
        (3.75, 0.5, "<b>BMI_CLASS</b><br>one feature, all ages", ui.GOOD_BG, ui.GREEN),
    ]
    for x, y, text, bg, colour in boxes:
        fig.add_shape(type="rect", x0=x, x1=x + 1.0, y0=y - 0.19, y1=y + 0.19,
                      fillcolor=bg, line=dict(color=ui.RULE, width=1), layer="below")
        fig.add_annotation(x=x + 0.5, y=y, text=text, showarrow=False,
                           font=dict(size=11.5, color=colour))
    for x0, y0, x1, y1 in [(1.0, 0.5, 1.25, 0.86), (1.0, 0.5, 1.25, 0.14),
                           (2.25, 0.86, 2.5, 0.86), (2.25, 0.14, 2.5, 0.14),
                           (3.5, 0.86, 3.75, 0.5), (3.5, 0.14, 3.75, 0.5)]:
        fig.add_annotation(x=x1, y=y1, ax=x0, ay=y0, xref="x", yref="y", axref="x", ayref="y",
                           showarrow=True, arrowhead=2, arrowsize=1, arrowwidth=1.4,
                           arrowcolor=ui.MUTED, text="")
    fig.update_xaxes(visible=False, range=[-0.1, 4.9])
    fig.update_yaxes(visible=False, range=[-0.1, 1.15])
    fig.update_layout(template="simple_white", height=230,
                      margin=dict(l=0, r=0, t=6, b=0), plot_bgcolor="white")
    return fig


def render():
    a = D.audit_facts()
    ui.page_header("Part 2 · Preparation", "Feature audit",
                   "The largest part of this project was deciding which columns could "
                   "legitimately be used at all.")

    # ------------------------------------------------------- why not all 255
    st.markdown("## Why not just use all 255 columns?")
    problems = [
        ("Administrative columns", ui.RED,
         "A record number or file version says nothing about health. A record number is unique "
         "per person, so a model could effectively memorise it."),
        ("Module inclusion flags", ui.ORANGE,
         "31 columns record whether a survey section applied to that person. They describe the "
         "questionnaire's routing, not the respondent."),
        ("Special codes", ui.ORANGE,
         "The numbers 6 and 9 often mean “valid skip” or “not stated”. Treated as real values "
         "they become nonsense quantities."),
        ("Restricted universes", ui.BLUE,
         "Many variables exist only for certain ages or regions, so most rows are structurally "
         "blank rather than missing."),
    ]
    for row in (problems[:2], problems[2:]):
        cols = st.columns(2)
        for col, (title, colour, body) in zip(cols, row):
            with col:
                st.markdown(
                    f"<div class='card' style='border-left-color:{colour};margin-bottom:0.6rem'>"
                    f"<div style='font-weight:700;color:{ui.INK};margin-bottom:0.25rem'>{title}"
                    f"</div><div style='font-size:0.9rem;color:{ui.BODY};line-height:1.5'>"
                    f"{body}</div></div>", unsafe_allow_html=True)
    ui.why_expander(C.WHY["why_not_255"])

    # ------------------------------------------------------- funnel
    st.markdown("## From 255 columns to 216 candidates")
    st.plotly_chart(_funnel_figure(a), width="stretch", config={"displayModeBar": False})
    st.caption("Removed as administrative or weight columns: " +
               " · ".join(a["admin_variables"]))
    st.plotly_chart(_grouping_figure(a), width="stretch", config={"displayModeBar": False})
    ui.why_expander(C.WHY["do_flags"])

    # ------------------------------------------------------- special codes
    st.markdown("## Special codes: the same digit means different things")
    st.write(
        "This is the single most common way to corrupt a CCHS analysis. Pick a variable to see "
        "its real codes and what each one actually means.")
    choice = st.selectbox("Choose a variable", list(D.SPECIAL_CODE_EXAMPLES.keys()),
                          key="special_code_variable")
    rows = D.SPECIAL_CODE_EXAMPLES[choice]
    ui.static_table(
        pd.DataFrame(rows, columns=["Code", "Meaning", "Respondents", "How it is treated"]))

    if "HWTDGWHO" in choice:
        ui.callout(
            "94% of this column is a valid skip. If those 63,318 rows were treated as missing "
            "and filled with the most common value, the model would be handed an invented "
            "youth BMI for tens of thousands of adults. This is exactly the failure the BMI "
            "harmonisation step below was built to avoid.",
            title="Why this example matters most", kind="warn")

    ui.callout("<b>Never globally replace every 6 or 9 with missing.</b> The meaning is "
               "variable-specific, so the project defined the codes one variable at a time.",
               kind="warn")
    ui.why_expander(C.WHY["special_codes"])

    # ------------------------------------------------------- BMI
    st.markdown("## How BMI became a single feature")
    st.write(
        "CCHS stores BMI in two age-specific variables. Neither works on its own for a model "
        "covering everyone aged 12 and older, so the project combined them.")
    st.plotly_chart(_bmi_flow(), width="stretch", config={"displayModeBar": False})
    st.caption("Codes 6 and 9 are then converted to missing on BMI_CLASS itself, so a "
               "structural skip is never mistaken for a real BMI category. BMI_CLASS is used "
               "in conditions B, C, D1, D2 and F.")
    ui.why_expander(C.WHY["bmi"])

    # ------------------------------------------------------- WTS_M
    st.markdown("## Why the sampling weight WTS_M was excluded")
    st.markdown(
        f"<div class='callout'><div class='callout-title'>What the CCHS User Guide says</div>"
        f"<p><i>“{D.USER_GUIDE_QUOTE}”</i></p></div>", unsafe_allow_html=True)
    w1, w2 = st.columns(2)
    with w1:
        st.markdown(
            "**What WTS_M is for**  \nIt records how many people in Canada each respondent "
            "represents, so survey estimates can be scaled to the population.\n\n"
            "**Why it is not a predictor**  \nIt carries no health information. Including it "
            "would let the model use the sampling design as though it were a symptom.")
    with w2:
        p = D.PREVALENCE_CONTRAST
        st.markdown("**A concrete contrast**")
        cc1, cc2 = st.columns(2)
        ui.metric_card(cc1, f"{p['unweighted_pct']}%",
                       "unweighted share of the modelling population", ui.ORANGE)
        ui.metric_card(cc2, f"{p['weighted_pct']}%",
                       "survey-weighted share published for CCC_05 = Yes", ui.BLUE)
    ui.callout(
        "These two percentages answer <b>different questions</b>, and neither is “the wrong "
        "one”. The unweighted figure describes the modelling population this project actually "
        "trained on; the weighted figure is the survey's population estimate. Because the "
        "weights and bootstrap procedure were not applied here, these results are "
        "respondent-level machine learning, <b>not survey-weighted population estimates</b>.")
    ui.why_expander(C.WHY["wts_m"])

    # ------------------------------------------------------- RHC_05
    st.markdown("## Why RHC_05 was deliberately held out")
    r1, r2 = st.columns(2)
    with r1:
        st.markdown(
            "<div class='callout callout-warn'><div class='callout-title'>The concern</div>"
            "<p>Diabetes is diagnosed by a health professional. Someone with a regular provider "
            "is more likely to have been tested and told, so the variable may describe the "
            "route to diagnosis rather than the underlying condition.</p></div>",
            unsafe_allow_html=True)
    with r2:
        st.markdown(
            "<div class='callout'><div class='callout-title'>The decision</div>"
            "<p>Hold it outside the main feature sets, because including it would quietly shift "
            "the question from “who reports diabetes?” towards “who has contact with the health "
            "system?”.</p></div>", unsafe_allow_html=True)
    ui.callout(
        "<b>Wording matters.</b> This is a <b>methodological leakage / prediction-pathway "
        "concern</b>. The project did not demonstrate leakage, and does not claim to have.",
        kind="warn")
    ui.why_expander(C.WHY["rhc"])

    ui.source_note(
        "Sources: Notebook 01, Stage 13 (candidate-pool construction and grouping); "
        "Statistics Canada, CCHS 2022 PUMF Data Dictionary (all codes, universes and "
        f"frequencies); {D.USER_GUIDE_SOURCE} (complex-design quotation). "
        f"Prevalence contrast: {D.PREVALENCE_CONTRAST['source']}")
