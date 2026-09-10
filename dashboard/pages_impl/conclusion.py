"""Limitations & Conclusion: what the project concludes, and the boundary of those claims."""

import pandas as pd
import streamlit as st

import content as C
import data_sources as D
import ui


def render():
    ui.page_header("Part 6 · Conclusion", "Limitations and conclusion",
                   "What the evidence supports, and just as importantly what it does not.")

    # ------------------------------------------------------------- conclusion
    st.markdown("## The conclusion the evidence supports")
    ui.callout(
        "Within this study, changing <b>which information</b> the model was given mattered more "
        "than changing <b>which algorithm</b> was used.")

    for headline, detail in C.CONCLUSIONS:
        st.markdown(
            f"<div class='card' style='border-left-color:{ui.BLUE};margin-bottom:0.55rem'>"
            f"<div style='font-weight:700;color:{ui.INK};margin-bottom:0.2rem'>{headline}</div>"
            f"<div style='font-size:0.91rem;color:{ui.BODY};line-height:1.55'>{detail}</div>"
            f"</div>", unsafe_allow_html=True)

    # ------------------------------------------------------------- cannot claim
    st.markdown("## What this project cannot claim")
    st.write("Worth checking before writing about or presenting this work.")
    for headline, detail in C.CANNOT_CLAIM:
        st.markdown(
            f"<div class='card callout-warn' style='border-left-color:{ui.RED};"
            f"margin-bottom:0.5rem;background:{ui.WARN_BG}'>"
            f"<span style='font-weight:700;color:{ui.INK}'>{headline}</span>"
            f"<span style='color:{ui.BODY};margin-left:0.6rem;font-size:0.91rem'>{detail}"
            f"</span></div>", unsafe_allow_html=True)

    # ------------------------------------------------------------- not completed
    st.markdown("## What was planned but never completed")
    st.write("Stated explicitly so the project record is not overstated.")
    ui.static_table(
        pd.DataFrame(C.NOT_COMPLETED, columns=["Planned work", "Status", "What this means"]))
    ui.callout(
        "If anyone summarising this project cites D3, E1, E2 or a full 216-variable automatic "
        "selection as a finding, they are describing work that <b>does not exist in the "
        "repository</b>.", kind="warn")

    # ------------------------------------------------------------- limitations
    st.markdown("## Limitations")
    st.write("Twelve constraints on what any result from this dataset could mean. "
             "Expand any card for the fuller explanation.")

    for i in range(0, len(C.LIMITATIONS), 2):
        cols = st.columns(2)
        for col, (title, body) in zip(cols, C.LIMITATIONS[i:i + 2]):
            with col:
                with st.expander(title):
                    st.write(body)

    # ------------------------------------------------------------- where next
    st.markdown("## Where the full detail lives")
    w1, w2, w3 = st.columns(3)
    w1.markdown(
        "**The notebooks**  \nTwelve executed notebooks in `notebooks/`, from the dataset audit "
        "through to the fresh-holdout check.")
    w2.markdown(
        "**The result files**  \nTen CSV files in `notebooks/` hold every number this dashboard "
        "shows, so any figure here can be checked against the file it came from.")
    w3.markdown(
        "**This dashboard**  \n`dashboard/` in the same repository, if you want to see how a "
        "number on this page was put together.")

    ui.source_note(
        "The limitations and conclusions follow the academic report (Sections 8 and 10). "
        "The not-completed list comes from Notebook 02 and the repository itself. Every "
        "number on this page is from the ten experiment CSV files.")
