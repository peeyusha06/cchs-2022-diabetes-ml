"""
Shared look-and-feel: colour palette, CSS, and small reusable layout components.

Keeping these in one place means every page looks the same and the styling can be
adjusted without editing nine page modules.
"""

import streamlit as st
import plotly.graph_objects as go

# ------------------------------------------------------------------------ palette
# Matches the Master Understanding Deck: navy ink, off-white ground, restrained
# orange accent, with blue / green / red used only where they carry meaning.
INK = "#1A2A3A"
BODY = "#3D4B5A"
MUTED = "#6B7A88"
ORANGE = "#C05621"   # positive (diabetes) class, accent
BLUE = "#2E6DA4"     # negative class, neutral data
GREEN = "#2F7A5A"    # improvement / correct
RED = "#A63A2E"      # caution / error
RULE = "#D8DEE5"
PANEL = "#F3F5F8"
INFO_BG = "#ECF2F8"
WARN_BG = "#FDF3EE"
GOOD_BG = "#EEF6F2"

MODEL_COLOURS = {
    "Logistic Regression": BLUE,
    "Random Forest": "#7FA6A0",
    "Gradient Boosting": ORANGE,
}

FONT = "-apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif"


def page_config():
    st.set_page_config(
        page_title="CCHS 2022 Diabetes ML - Research Explorer",
        page_icon="🔬",
        layout="wide",
        initial_sidebar_state="auto",
    )


def inject_css():
    st.markdown(
        f"""
        <style>
          .stApp {{ background: #FFFFFF; }}
          html, body, [class*="css"] {{ font-family: {FONT}; }}

          /* headings */
          h1 {{ color:{INK}; font-weight:700; letter-spacing:-0.01em; }}
          h2 {{ color:{INK}; font-weight:700; font-size:1.45rem;
                margin-top:1.9rem; margin-bottom:0.35rem; }}
          h3 {{ color:{INK}; font-weight:600; font-size:1.12rem; margin-top:1.2rem; }}
          p, li {{ color:{BODY}; font-size:0.97rem; line-height:1.6; }}

          /* page kicker above the title */
          .kicker {{ color:{BLUE}; font-size:0.76rem; font-weight:700;
                     letter-spacing:0.09em; text-transform:uppercase;
                     margin-bottom:0.15rem; }}
          .subtitle {{ color:{MUTED}; font-size:1.03rem; margin-top:-0.35rem;
                       margin-bottom:0.4rem; }}

          /* metric cards */
          .card {{ background:{PANEL}; border-radius:8px; padding:0.85rem 1rem;
                   border-left:4px solid {BLUE}; height:100%; }}
          .card-value {{ font-size:1.85rem; font-weight:700; color:{INK};
                         line-height:1.15; }}
          .card-label {{ font-size:0.8rem; color:{MUTED}; margin-top:0.15rem; }}
          .card-delta {{ font-size:0.78rem; font-weight:600; margin-top:0.2rem; }}

          /* callouts */
          .callout {{ border-radius:8px; padding:0.85rem 1.05rem; margin:0.5rem 0 0.9rem 0;
                      border-left:4px solid {BLUE}; background:{INFO_BG}; }}
          .callout-warn {{ border-left-color:{RED}; background:{WARN_BG}; }}
          .callout-good {{ border-left-color:{GREEN}; background:{GOOD_BG}; }}
          .callout-title {{ font-weight:700; color:{INK}; margin-bottom:0.2rem;
                            font-size:0.97rem; }}
          .callout p {{ margin:0; font-size:0.93rem; }}

          /* source footer */
          .source {{ color:{MUTED}; font-size:0.79rem; font-style:italic;
                     border-top:1px solid {RULE}; padding-top:0.6rem;
                     margin-top:2rem; }}

          /* feature chips */
          .chip {{ display:inline-block; background:#E8EDF2; color:{INK};
                   border-radius:12px; padding:0.2rem 0.62rem; margin:0.14rem 0.16rem 0.14rem 0;
                   font-size:0.79rem; font-weight:600; }}
          .chip-new {{ background:{ORANGE}; color:#FFFFFF; }}

          /* sidebar framing note */
          .frame-note {{ font-size:0.79rem; line-height:1.45; color:{BODY};
                         background:{PANEL}; border-radius:6px; padding:0.6rem 0.7rem; }}
          .frame-note b {{ color:{INK}; }}

          /* st.table: Streamlit wraps every cell in <p>, which would otherwise inherit
             the global paragraph colour and defeat the header and highlight colours. */
          [data-testid="stTableStyledTable"] th p {{ color:#FFFFFF !important;
                                                     font-weight:600; margin:0; }}
          [data-testid="stTableStyledTable"] td p {{ color:inherit !important; margin:0; }}
          [data-testid="stTableStyledTable"] td {{ font-variant-numeric:tabular-nums; }}

          /* tighten default streamlit spacing a little */
          .block-container {{ padding-top:3.4rem; padding-bottom:3rem; max-width:1180px; }}
          [data-testid="stMetricValue"] {{ font-size:1.6rem; }}
          div[data-testid="stExpander"] details {{ border-color:{RULE}; }}

          /* keep side-by-side cards/callouts the same height, so their bottom edges
             line up even when one has more text than the other.
             Verified against the real Streamlit 1.63 DOM: stColumn > (div) > stVerticalBlock
             > stElementContainer > stMarkdown > (div) > stMarkdownContainer > .card/.callout.
             The previous version of this rule used the wrong test id ("element-container"
             instead of "stElementContainer") and relied on :has(), so it never matched. */
          div[data-testid="stHorizontalBlock"] {{ align-items: stretch; }}
          div[data-testid="stColumn"] {{ display:flex; }}
          div[data-testid="stColumn"] > div {{ width:100%; height:100%; }}
          div[data-testid="stColumn"] div[data-testid="stVerticalBlock"],
          div[data-testid="stColumn"] div[data-testid="stElementContainer"],
          div[data-testid="stColumn"] div[data-testid="stElementContainer"] > div,
          div[data-testid="stColumn"] div[data-testid="stMarkdown"],
          div[data-testid="stColumn"] div[data-testid="stMarkdown"] > div,
          div[data-testid="stColumn"] div[data-testid="stMarkdownContainer"] {{
              height:100%; }}
          .card, .callout {{ height:100%; box-sizing:border-box; }}
        </style>
        """,
        unsafe_allow_html=True,
    )


# --------------------------------------------------------------------- components

def page_header(kicker: str, title: str, subtitle: str = ""):
    st.markdown(f"<div class='kicker'>{kicker}</div>", unsafe_allow_html=True)
    st.markdown(f"# {title}")
    if subtitle:
        st.markdown(f"<div class='subtitle'>{subtitle}</div>", unsafe_allow_html=True)
    st.write("")


def metric_card(col, value, label, colour=INK, delta=None, delta_good=None):
    """A single statistic. `delta_good` True renders green, False red, None grey."""
    delta_html = ""
    if delta is not None:
        if delta_good is True:
            c, arrow = GREEN, "▲"
        elif delta_good is False:
            c, arrow = RED, "▼"
        else:
            c, arrow = MUTED, "—"
        delta_html = (f"<div class='card-delta' style='color:{c}'>"
                      f"{arrow} {abs(delta):.3f}</div>")
    col.markdown(
        f"<div class='card' style='border-left-color:{colour}'>"
        f"<div class='card-value'>{value}</div>"
        f"<div class='card-label'>{label}</div>{delta_html}</div>",
        unsafe_allow_html=True,
    )


def callout(text, title=None, kind="info"):
    cls = {"info": "callout", "warn": "callout callout-warn",
           "good": "callout callout-good"}[kind]
    head = f"<div class='callout-title'>{title}</div>" if title else ""
    st.markdown(f"<div class='{cls}'>{head}<p>{text}</p></div>", unsafe_allow_html=True)


def chips(items, highlight=None):
    """Render feature names as pills; `highlight` marks newly added variables."""
    highlight = highlight or []
    html = "".join(
        f"<span class='chip {'chip-new' if i in highlight else ''}'>{i}</span>"
        for i in items
    )
    st.markdown(html, unsafe_allow_html=True)


def source_note(text):
    st.markdown(f"<div class='source'>{text}</div>", unsafe_allow_html=True)


def why_expander(entry):
    """Render a ('question', 'answer') tuple from content.WHY as an expander.

    The question itself already opens with "Why...", so it needs no extra prefix -
    repeating "Why did we do this?" on every expander site-wide read as boilerplate.
    """
    question, answer = entry
    with st.expander(question):
        st.write(answer)


def metric_explainer(metric_key, glossary):
    short, longer = glossary[metric_key]
    with st.expander("What does this metric mean?"):
        st.markdown(f"**{short}**")
        st.write(longer)


def base_layout(fig, height=380, title=None, ytitle=None, xtitle=None, showlegend=False):
    """Common Plotly styling so every chart in the dashboard looks the same."""
    # The legend sits BELOW the plot: placing it above collides with the chart title.
    # The `title` key is only added when there is one — passing title=None through to
    # Plotly still renders an (empty) title trace, which showed up as a literal
    # "undefined" in the deployed app.
    # When a chart has BOTH an x-axis title and a legend, the bottom margin needs a
    # third stacked row (tick labels, then axis title, then legend) or the legend
    # draws on top of the axis title.
    extra = 44 if (xtitle and showlegend) else 0
    legend_y = -0.42 if (xtitle and showlegend) else -0.16
    layout = dict(
        template="simple_white",
        height=height + (34 if showlegend else 0) + extra,
        margin=dict(l=10, r=10, t=52 if title else 18, b=(54 if showlegend else 10) + extra),
        font=dict(family=FONT, size=13, color=BODY),
        showlegend=showlegend,
        legend=dict(orientation="h", yanchor="top", y=legend_y, x=0),
        hoverlabel=dict(font_size=12),
    )
    if title:
        layout["title"] = dict(text=title, font=dict(size=15, color=INK))
    fig.update_layout(**layout)
    if ytitle:
        fig.update_yaxes(title_text=ytitle)
    if xtitle:
        fig.update_xaxes(title_text=xtitle)
    fig.update_xaxes(showgrid=False, linecolor=RULE)
    fig.update_yaxes(gridcolor=RULE, linecolor=RULE, zerolinecolor=RULE)
    return fig


def confusion_matrix_figure(tn, fp, fn, tp, height=300):
    """2x2 confusion matrix drawn as an annotated grid (counts, not a colour scale)."""
    cells = [
        # (row, col, value, label, colour, background)
        (1, 0, tn, "True Negative", GREEN, GOOD_BG),
        (1, 1, fp, "False Positive", RED, WARN_BG),
        (0, 0, fn, "False Negative", RED, WARN_BG),
        (0, 1, tp, "True Positive", GREEN, GOOD_BG),
    ]
    fig = go.Figure()
    for r, c, value, label, colour, bg in cells:
        fig.add_shape(type="rect", x0=c - 0.46, x1=c + 0.46, y0=r - 0.42, y1=r + 0.42,
                      fillcolor=bg, line=dict(color=RULE, width=1), layer="below")
        fig.add_annotation(x=c, y=r + 0.12, text=f"<b>{value:,}</b>", showarrow=False,
                           font=dict(size=24, color=colour))
        fig.add_annotation(x=c, y=r - 0.20, text=label, showarrow=False,
                           font=dict(size=12, color=MUTED))
    fig.update_xaxes(range=[-0.62, 1.62], tickvals=[0, 1],
                     ticktext=["Model said: NO", "Model said: YES"],
                     showgrid=False, zeroline=False, side="top")
    fig.update_yaxes(range=[-0.62, 1.62], tickvals=[0, 1],
                     ticktext=["Actually YES", "Actually NO"],
                     showgrid=False, zeroline=False)
    fig.update_layout(template="simple_white", height=height,
                      margin=dict(l=10, r=10, t=40, b=10),
                      font=dict(family=FONT, size=12, color=BODY),
                      plot_bgcolor="white")
    fig.update_xaxes(linecolor="white"); fig.update_yaxes(linecolor="white")
    return fig

def static_table(df, formats=None, highlight=None):
    """Render a small static table as real HTML (st.table), not a canvas grid.

    st.dataframe draws to a <canvas>, so its contents cannot be selected, copied or
    read by a screen reader. Every table in this dashboard is small and static, so
    st.table is both more accessible and easier to read.

    `highlight` is an optional function(column) -> list of CSS strings, matching the
    pandas Styler.apply signature.
    """
    styler = df.style.hide(axis="index")
    # Base cell styling FIRST, so a per-cell highlight applied afterwards wins.
    styler = styler.set_properties(**{"font-size": "0.9rem", "color": BODY})
    if highlight is not None:
        styler = styler.apply(highlight, axis=0)
    if formats:
        styler = styler.format(formats)
    styler = styler.set_table_styles([
        {"selector": "th",
         "props": [("background-color", INK), ("color", "#FFFFFF !important"),
                   ("font-size", "0.85rem"), ("font-weight", "600"),
                   ("text-align", "left"), ("padding", "0.5rem 0.6rem")]},
        {"selector": "thead th",
         "props": [("background-color", INK), ("color", "#FFFFFF !important")]},
        {"selector": "td", "props": [("padding", "0.42rem 0.6rem"),
                                     ("border-bottom", f"1px solid {RULE}")]},
    ])
    st.table(styler)
