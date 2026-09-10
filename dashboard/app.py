"""
CCHS 2022 Diabetes Machine-Learning Project - interactive research explorer.

Run locally from the repository root:

    streamlit run dashboard/app.py

This dashboard is a presentation layer over completed research. It trains nothing,
reruns nothing, and never reads raw respondent-level survey data. Every number shown
comes from the result CSV files already tracked in notebooks/, or from a small set of
documented constants in data_sources.py.
"""

import sys
from pathlib import Path

import streamlit as st

# Make the sibling modules importable whether Streamlit is launched from the repo root
# or from inside dashboard/.
sys.path.insert(0, str(Path(__file__).resolve().parent))

import content as C          # noqa: E402
import ui                     # noqa: E402
from pages_impl import (      # noqa: E402
    overview, data_page, feature_audit, variable_explorer,
    experiments, model_comparison, robustness, fresh_holdout, conclusion,
)

PAGES = {
    "Overview": overview.render,
    "Understand the Data": data_page.render,
    "Feature Audit": feature_audit.render,
    "Variable Explorer": variable_explorer.render,
    "Experiment Explorer": experiments.render,
    "Model Comparison": model_comparison.render,
    "Robustness & Interpretability": robustness.render,
    "Fresh Holdout": fresh_holdout.render,
    "Limitations & Conclusion": conclusion.render,
}


def sidebar():
    with st.sidebar:
        st.markdown(
            f"<div style='font-weight:700;color:{ui.INK};font-size:1.02rem;"
            f"line-height:1.3'>CCHS 2022 Diabetes<br>Machine-Learning Project</div>"
            f"<div style='color:{ui.MUTED};font-size:0.78rem;margin-top:0.25rem'>"
            f"Interactive research explorer</div>", unsafe_allow_html=True)
        st.write("")

        # Deep linking: ?page=Feature+Audit opens that page directly, so a specific
        # view can be shared or bookmarked.
        names = list(PAGES.keys())
        requested = st.query_params.get("page")
        default_index = names.index(requested) if requested in names else 0

        choice = st.radio("Go to", names, index=default_index, key="nav",
                          label_visibility="collapsed")

        if st.query_params.get("page") != choice:
            st.query_params["page"] = choice

        st.divider()
        # Framing note pinned on every page, so the scope cannot be missed
        # regardless of which page the visitor lands on.
        st.markdown(
            "<div class='frame-note'>"
            "<b>What this study is</b><br>"
            "A cross-sectional classification of <i>reported</i> diabetes status in "
            "CCHS 2022.<br><br>"
            "<b>What it is not</b><br>"
            "Not future-risk prediction, not a diagnosis, not a screening tool, and not "
            "evidence of causation."
            "</div>", unsafe_allow_html=True)

        st.divider()
        st.caption(
            "Built from the project's own result files. No raw respondent data is read or "
            "displayed anywhere in this dashboard.")
        return choice


def main():
    ui.page_config()
    ui.inject_css()
    page = sidebar()
    PAGES[page]()


if __name__ == "__main__":
    main()
