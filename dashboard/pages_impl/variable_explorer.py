"""Variable Explorer: look up any variable the project considered."""

import pandas as pd
import streamlit as st

import data_sources as D
import ui

CONDITIONS = ["A", "B", "C", "D1", "D2", "F"]

ROLE_FILTERS = {
    "All variables": lambda v: True,
    "Used in the final D2 model": lambda v: "D2" in v["used_in"],
    "Used in at least one experiment": lambda v: len(v["used_in"]) > 0,
    "Held out or excluded": lambda v: len(v["used_in"]) == 0,
}


def render():
    ui.page_header("Part 2 · Preparation", "Variable explorer",
                   "Every variable the project considered, what it means, and what was done "
                   "with it.")

    left, right = st.columns([0.42, 0.58])
    with left:
        role = st.selectbox("Filter by role", list(ROLE_FILTERS.keys()),
                            key="var_role_filter")
    options = [k for k, v in D.VARIABLES.items() if ROLE_FILTERS[role](v)]
    if not options:
        st.info("No variables match this filter.")
        return
    with right:
        name = st.selectbox("Choose a variable", options, key="var_name")

    v = D.VARIABLES[name]

    # ------------------------------------------------------------- header card
    st.markdown(
        f"<div class='callout'><div class='callout-title' style='font-size:1.15rem'>{name}</div>"
        f"<p style='font-size:1.0rem'>{v['concept']}</p></div>", unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    with c1:
        st.markdown("**Universe (who it applies to)**")
        st.write(v["universe"])
        st.markdown("**Coding**")
        st.write(v["coding"])
    with c2:
        st.markdown("**Special codes**")
        st.write(v["special_codes"])
        st.markdown("**Role in this project**")
        st.write(v["role"])

    # ------------------------------------------------------------- usage strip
    st.markdown("### Used in which feature conditions?")
    cols = st.columns(len(CONDITIONS))
    for col, cond in zip(cols, CONDITIONS):
        used = cond in v["used_in"]
        col.markdown(
            f"<div style='text-align:center;padding:0.55rem 0;border-radius:6px;"
            f"background:{ui.GOOD_BG if used else '#F5F6F8'};"
            f"border:1px solid {ui.RULE}'>"
            f"<div style='font-weight:700;color:{ui.GREEN if used else ui.MUTED};"
            f"font-size:1.05rem'>{cond}</div>"
            f"<div style='font-size:0.72rem;color:{ui.MUTED}'>"
            f"{'used' if used else 'not used'}</div></div>",
            unsafe_allow_html=True)

    if not v["used_in"]:
        ui.callout("This variable was <b>not used as a predictor</b> in any completed "
                   "experiment. The note below explains why.", kind="warn")

    # ------------------------------------------------------------- note
    st.markdown("### Note")
    st.write(v["note"])

    # ------------------------------------------------------------- context table
    with st.expander("Show every variable at a glance"):
        rows = []
        for key, val in D.VARIABLES.items():
            rows.append({
                "Variable": key,
                "Concept": val["concept"],
                "Universe": val["universe"],
                "Used in": ", ".join(val["used_in"]) if val["used_in"] else "— held out —",
            })
        ui.static_table(pd.DataFrame(rows))

    ui.source_note(
        f"Source for concept, universe, coding and frequencies: {v['source']}. "
        "Experiment membership is taken from the FEATURES lists in the executed experiment "
        "notebooks. BMI_CLASS is constructed by this project and is not a CCHS variable.")
