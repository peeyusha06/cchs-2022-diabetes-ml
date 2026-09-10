"""Landing page: what the project is, in about twenty seconds."""

import streamlit as st
import content as C
import data_sources as D
import ui


def render():
    facts = D.dataset_facts()

    ui.page_header(
        "Interactive research explorer",
        "CCHS 2022 Diabetes Machine-Learning Project",
        "A cross-sectional classification study of diagnosed diabetes status",
    )

    # --- headline numbers ---------------------------------------------------
    c1, c2, c3, c4 = st.columns(4)
    ui.metric_card(c1, f"{facts['respondents']:,}", "respondents in the CCHS 2022 PUMF", ui.BLUE)
    ui.metric_card(c2, f"{facts['variables']}", "survey variables", ui.BLUE)
    ui.metric_card(c3, f"{facts['modelling_population']:,}", "modelling population", ui.BLUE)
    ui.metric_card(c4, "9.05%", "report diabetes (positive class)", ui.ORANGE)

    # --- research question --------------------------------------------------
    st.markdown("## The research question")
    ui.callout(C.RESEARCH_QUESTION)

    # --- three findings -----------------------------------------------------
    st.markdown("## Three findings")
    for i, (headline, detail) in enumerate(C.HEADLINE_FINDINGS, start=1):
        col_n, col_t = st.columns([0.055, 0.945])
        col_n.markdown(
            f"<div style='font-size:1.5rem;font-weight:700;color:{ui.BLUE};"
            f"line-height:1.1'>{i}</div>", unsafe_allow_html=True)
        col_t.markdown(f"**{headline}**  \n{detail}")

    # --- framing ------------------------------------------------------------
    st.markdown("## What this study is, and is not")
    left, right = st.columns(2)
    with left:
        st.markdown(
            "<div class='callout callout-good'><div class='callout-title'>"
            "This study IS</div><p>" +
            "<br>".join("• " + x for x in C.FRAMING_IS) + "</p></div>",
            unsafe_allow_html=True)
    with right:
        st.markdown(
            "<div class='callout callout-warn'><div class='callout-title'>"
            "This study is NOT</div><p>" +
            "<br>".join("• " + x for x in C.FRAMING_IS_NOT) + "</p></div>",
            unsafe_allow_html=True)
    ui.callout(C.FRAMING_WHY, title="Why the distinction matters")

    # --- where to go next ---------------------------------------------------
    st.markdown("## Where to go next")
    n1, n2, n3 = st.columns(3)
    n1.markdown(
        "**Understand the Data**  \nWhat the CCHS is, what the target variable is, and why "
        "only 9% of rows are positive.\n\n"
        "**Feature Audit**  \nHow 255 columns became 216 candidates, and the coding traps "
        "along the way.\n\n"
        "**Variable Explorer**  \nLook up any variable and see what the project did with it.")
    n2.markdown(
        "**Experiment Explorer**  \nSix feature conditions, what each changed and what each "
        "found.\n\n"
        "**Model Comparison**  \nLogistic Regression, Random Forest and Gradient Boosting on "
        "one fixed feature set.\n\n"
        "**Robustness & Interpretability**  \nHow stable the result is, and what the models "
        "leaned on.")
    n3.markdown(
        "**Fresh Holdout**  \nAn honest look at test-set reuse, and the check that was run "
        "because of it.\n\n"
        "**Limitations & Conclusion**  \nWhat the project concludes and, just as importantly, "
        "what it cannot claim.")

    ui.source_note(
        "Sources: counts from Notebook 02 and the CCHS 2022 PUMF Data Dictionary; findings from "
        "the ten experiment result CSV files in <code>notebooks/</code>. "
        "This dashboard reads those files directly - no numbers are re-typed.")
