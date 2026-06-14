from pathlib import Path

import duckdb
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from utils import (
    REGION_MAP,
    SHORT_NAMES,
    apply_theme,
    clean_name,
    get_palette,
    load_geojson,
    parse_candidate,
    render_sidebar,
)

st.set_page_config(
    page_title="Regional Breakdown - Polis",
    page_icon="🗳️",
    layout="wide",
    initial_sidebar_state="expanded",
)

apply_theme()

P = get_palette()


@st.cache_data
def fetch_candidates(position: str) -> pd.DataFrame:
    db_path = Path(__file__).parent.parent.parent / "polis.duckdb"
    con = duckdb.connect(str(db_path), read_only=True)
    return con.execute(
        "SELECT DISTINCT CANDIDATE_NAME FROM dim_candidate "
        "WHERE POSITION = ? ORDER BY CANDIDATE_NAME",
        [position],
    ).fetchdf()


@st.cache_data
def fetch_regional_breakdown(candidate_name: str, position: str) -> pd.DataFrame:
    db_path = Path(__file__).parent.parent.parent / "polis.duckdb"
    con = duckdb.connect(str(db_path), read_only=True)
    df = con.execute(
        """
        SELECT dp.REGION, SUM(fv.VOTES) AS TOTAL_VOTES
        FROM fact_votes fv
        JOIN dim_candidate dc ON fv.CANDIDATE_ID = dc.CANDIDATE_ID
        JOIN dim_precinct dp ON fv.PRECINCT_ID = dp.PRECINCT_ID
        WHERE dc.CANDIDATE_NAME = ?
          AND dc.POSITION = ?
          AND dp.REGION NOT IN ('OAV', 'LAV', 'NIR')
        GROUP BY dp.REGION
        ORDER BY TOTAL_VOTES DESC
        """,
        [candidate_name, position],
    ).fetchdf()
    total = df["TOTAL_VOTES"].sum()
    df["PCT"] = (df["TOTAL_VOTES"] / total * 100).round(2) if total > 0 else 0.0
    df["GEO_REGION"] = df["REGION"].map(REGION_MAP.get)
    df["SHORT"] = df["REGION"].map(SHORT_NAMES.get).fillna(df["REGION"])
    return df


def build_map(breakdown_df: pd.DataFrame, geojson: dict) -> go.Figure:
    plot_df = breakdown_df.dropna(subset=["GEO_REGION"])
    fig = px.choropleth(
        plot_df,
        geojson=geojson,
        locations="GEO_REGION",
        featureidkey="properties.REGION",
        color="TOTAL_VOTES",
        color_continuous_scale=[
            [0.0, P["map_lo"]],
            [0.5, "#7a5828"],
            [1.0, P["map_hi"]],
        ],
        hover_name="SHORT",
        hover_data={"TOTAL_VOTES": ":,", "GEO_REGION": False},
    )
    fig.update_geos(
        visible=False,
        bgcolor=P["bg"],
        lataxis_range=[4.5, 21.5],
        lonaxis_range=[115.5, 127.5],
    )
    fig.update_layout(
        paper_bgcolor=P["bg"],
        plot_bgcolor=P["bg"],
        margin={"r": 0, "t": 0, "l": 0, "b": 0},
        height=500,
        coloraxis_colorbar=dict(
            title="Votes",
            tickfont=dict(color=P["faint"], size=10),
            title_font=dict(color=P["faint"], size=10),
            bgcolor=P["panel"],
            bordercolor=P["border"],
            borderwidth=1,
            thickness=10,
        ),
    )
    fig.update_traces(marker_line_color=P["border_strong"], marker_line_width=0.6)
    return fig


def build_bar_chart(breakdown_df: pd.DataFrame) -> go.Figure:
    df = breakdown_df.sort_values("TOTAL_VOTES", ascending=True)

    fig = go.Figure(
        go.Bar(
            x=df["TOTAL_VOTES"],
            y=df["SHORT"],
            orientation="h",
            marker_color=P["primary"],
            marker_line_width=0,
            text=df["TOTAL_VOTES"].apply(lambda v: f"{int(v):,}"),
            textposition="outside",
            textfont=dict(color=P["muted"], size=11),
            cliponaxis=False,
            hovertemplate="%{y}<br>%{x:,} votes<extra></extra>",
        )
    )
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin={"r": 160, "t": 20, "l": 10, "b": 40},
        height=max(420, len(df) * 26),
        xaxis=dict(
            tickfont=dict(color=P["faint"], size=11),
            gridcolor=P["border"],
            zeroline=False,
            showline=False,
            tickformat=",",
        ),
        yaxis=dict(
            tickfont=dict(color=P["text"], size=12),
            gridcolor="rgba(0,0,0,0)",
        ),
        showlegend=False,
    )
    return fig


def render_summary_table(breakdown_df: pd.DataFrame) -> None:
    rows = []
    for _, row in breakdown_df.iterrows():
        rows.append(
            f"<tr style='border-bottom:1px solid {P['border']};'>"
            f"<td style='color:{P['text']};padding:0.55rem 2rem 0.55rem 0;"
            f"font-size:0.88rem;vertical-align:middle;'>{row['SHORT']}</td>"
            f"<td style='color:{P['text']};text-align:center;padding:0.55rem 1rem;"
            f"font-size:0.88rem;vertical-align:middle;'>{int(row['TOTAL_VOTES']):,}</td>"
            f"<td style='color:{P['primary']};text-align:center;padding:0.55rem 1rem;"
            f"font-size:0.85rem;vertical-align:middle;'>{row['PCT']:.2f}%</td>"
            f"</tr>"
        )
    th = (
        f"font-size:0.62rem;color:{P['faint']};text-transform:uppercase;"
        f"letter-spacing:0.1em;font-weight:400;vertical-align:middle;"
    )
    st.markdown(
        f"<table style='width:100%;border-collapse:collapse;"
        f'font-family:"Source Sans 3",sans-serif;\'>'
        f"<thead><tr style='border-bottom:1px solid {P['border_strong']};'>"
        f"<th style='{th}padding:0.55rem 2rem 0.55rem 0;text-align:left;'>Region</th>"
        f"<th style='{th}padding:0.55rem 1rem;text-align:center;'>Votes</th>"
        f"<th style='{th}padding:0.55rem 1rem;text-align:center;'>% of Total</th>"
        f"</tr></thead>"
        f"<tbody>{''.join(rows)}</tbody>"
        f"</table>",
        unsafe_allow_html=True,
    )


# sidebar
render_sidebar()

# page
st.markdown(
    "<p class='tagline'>2025 Philippine Midterm Elections</p>", unsafe_allow_html=True
)
st.title("Regional Breakdown")
st.markdown(
    f"<p style='color:{P['muted']};font-size:1rem;font-weight:300;line-height:1.8;"
    f"max-width:560px;margin-top:0.25rem;'>"
    "See how a single candidate or party performed across all 17 regions. "
    "Pick a position and a name to redraw the map."
    "</p>",
    unsafe_allow_html=True,
)
st.caption("Source: precinct-level scrape · for geographic analysis only")

st.markdown("<br>", unsafe_allow_html=True)


# dropdown menus
def _senator_display(n: str) -> str:
    return parse_candidate(n)[0]


col_pos, col_cand = st.columns([1, 3])
with col_pos:
    position = st.selectbox("Position", options=["Senator", "Party List"], index=0)

if position is None:
    st.stop()

candidates_df = fetch_candidates(position)

display_fn = _senator_display if position == "Senator" else clean_name

with col_cand:
    selected_raw = st.selectbox(
        "Candidate",
        options=candidates_df["CANDIDATE_NAME"].tolist(),
        format_func=display_fn,
        index=0,
    )

if selected_raw is None:
    st.stop()

candidate_display = display_fn(selected_raw)

if position == "Senator":
    _, party = parse_candidate(selected_raw)
    subtitle = f"{candidate_display} · {party}" if party else candidate_display
else:
    subtitle = candidate_display

st.markdown("<br>", unsafe_allow_html=True)

# data
breakdown_df = fetch_regional_breakdown(selected_raw, position)
geojson = load_geojson()

if breakdown_df.empty:
    st.caption("No regional data available for this candidate.")
    st.stop()

total_votes = int(breakdown_df["TOTAL_VOTES"].sum())
top_row = breakdown_df.iloc[0]
top_region = top_row["SHORT"]
top_votes = int(top_row["TOTAL_VOTES"])
top_pct = float(top_row["PCT"])

# stat cards
c1, c2 = st.columns(2)
with c1:
    st.markdown(
        f"<div class='stat-card'>"
        f"<div class='stat-value'>{total_votes:,}</div>"
        f"<div class='stat-label'>Total votes (domestic regions)</div>"
        f"</div>",
        unsafe_allow_html=True,
    )
with c2:
    st.markdown(
        f"<div class='stat-card'>"
        f"<div class='stat-value' style='font-size:1.8rem;color:{P['primary']};'>{top_region}</div>"
        f"<div class='stat-label'>Strongest region</div>"
        f"<div class='stat-sub'>{top_votes:,} votes · {top_pct:.1f}% of total</div>"
        f"</div>",
        unsafe_allow_html=True,
    )

st.markdown(
    f"<div class='disclaimer' style='margin-top:1rem;'>"
    f"<strong style='color:{P['text']};'>Note:</strong> "
    "Vote totals here will differ from the Senate page. "
    "The Senate page uses final COMELEC certified results. "
    "This page uses precinct-level scrape data for geographic analysis only."
    "</div>",
    unsafe_allow_html=True,
)

st.markdown("<br>", unsafe_allow_html=True)

# map + bar chart
st.markdown("<p class='section-label'>VOTE DISTRIBUTION</p>", unsafe_allow_html=True)
st.markdown(f"## {subtitle}")

st.markdown("<br style='line-height:0.5;'>", unsafe_allow_html=True)

col_map, col_bar = st.columns([1, 1])
with col_map:
    st.plotly_chart(build_map(breakdown_df, geojson), use_container_width=True)
with col_bar:
    with st.container(border=True):
        st.markdown(
            f"<p style='font-size:0.6rem;color:{P['faint']};text-transform:uppercase;"
            f"letter-spacing:0.14em;font-weight:600;margin:0 0 0.5rem 0;'>"
            f"VOTES BY REGION</p>",
            unsafe_allow_html=True,
        )
        st.plotly_chart(build_bar_chart(breakdown_df), use_container_width=True)

st.markdown("<br>", unsafe_allow_html=True)

# summary table
st.markdown("<p class='section-label'>BREAKDOWN</p>", unsafe_allow_html=True)
st.markdown("## By region")

st.markdown("<br style='line-height:0.5;'>", unsafe_allow_html=True)

with st.container(border=True):
    render_summary_table(breakdown_df)
