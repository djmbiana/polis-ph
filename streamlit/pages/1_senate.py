import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from utils import (
    REGION_MAP,
    apply_theme,
    get_connection,
    get_palette,
    load_geojson,
    parse_candidate,
    render_region_ranking,
    render_sidebar,
)

st.set_page_config(
    page_title="Senate - Polis",
    page_icon="🗳️",
    layout="wide",
    initial_sidebar_state="expanded",
)

apply_theme()

P = get_palette()


@st.cache_data
def fetch_regional_votes() -> pd.DataFrame:
    con = get_connection()
    df = con.execute(
        """
        SELECT dp.REGION, SUM(fv.VOTES) AS TOTAL_VOTES
        FROM fact_votes fv
        JOIN dim_candidate dc ON fv.CANDIDATE_ID = dc.CANDIDATE_ID
        JOIN dim_precinct dp ON fv.PRECINCT_ID = dp.PRECINCT_ID
        WHERE dc.POSITION = 'Senator'
          AND dp.REGION NOT IN ('OAV', 'LAV', 'NIR')
        GROUP BY dp.REGION
        ORDER BY TOTAL_VOTES DESC
        """
    ).fetchdf()
    df["GEO_REGION"] = df["REGION"].map(REGION_MAP.get)
    return df.dropna(subset=["GEO_REGION"])


@st.cache_data
def fetch_senate_rankings() -> pd.DataFrame:
    con = get_connection()
    return con.execute("SELECT * FROM mart_senate_rankings ORDER BY RANK").fetchdf()


def build_map(regional_df: pd.DataFrame, geojson: dict) -> go.Figure:
    fig = px.choropleth(
        regional_df,
        geojson=geojson,
        locations="GEO_REGION",
        featureidkey="properties.REGION",
        color="TOTAL_VOTES",
        color_continuous_scale=[
            [0.0, P["map_lo"]],
            [0.5, "#7a5828"],
            [1.0, P["map_hi"]],
        ],
        hover_name="GEO_REGION",
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
        height=620,
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


def build_winners_chart(rankings_df: pd.DataFrame) -> go.Figure:
    winners: pd.DataFrame = rankings_df[rankings_df["WINNER"].astype(bool)].copy()
    winners = winners.sort_values("TOTAL_VOTES", ascending=True)
    winners["DISPLAY"] = winners["CANDIDATE_NAME"].apply(
        lambda n: parse_candidate(n)[0]
    )

    fig = go.Figure(
        go.Bar(
            x=winners["TOTAL_VOTES"],
            y=winners["DISPLAY"],
            orientation="h",
            marker_color=P["primary"],
            marker_line_width=0,
            text=winners["TOTAL_VOTES"].apply(lambda v: f"{v / 1e6:.2f}M"),
            textposition="outside",
            textfont=dict(color=P["muted"], size=11),
            cliponaxis=False,
            hovertemplate="%{y}<br>%{x:,} votes<extra></extra>",
        )
    )
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin={"r": 90, "t": 20, "l": 10, "b": 40},
        height=480,
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


def render_results_table(rankings_df: pd.DataFrame) -> None:
    rows = []
    for _, row in rankings_df.iterrows():
        name, party = parse_candidate(str(row["CANDIDATE_NAME"]))
        is_winner = bool(row["WINNER"])
        rank_color = P["primary"] if is_winner else P["faint"]
        text_color = P["text"] if is_winner else P["muted"]
        name_weight = "600" if is_winner else "400"
        party_html = (
            f" <span style='font-size:0.7rem;color:{P['faint']};margin-left:0.3rem;"
            f"font-weight:400;'>{party}</span>"
            if party
            else ""
        )
        status_html = (
            "<span class='winner-pill'>Winner</span>"
            if is_winner
            else f"<span style='color:{P['faint']};'>—</span>"
        )
        rows.append(
            f"<tr style='border-bottom:1px solid {P['border']};'>"
            f"<td style='color:{rank_color};text-align:right;padding:0.55rem 1.5rem 0.55rem 0;"
            f"font-size:0.85rem;width:3rem;vertical-align:middle;'>{row['RANK']}</td>"
            f"<td style='padding:0.55rem 2rem 0.55rem 0;vertical-align:middle;'>"
            f"<span style='color:{text_color};font-weight:{name_weight};font-size:0.88rem;'>{name}</span>"
            f"{party_html}</td>"
            f"<td style='color:{text_color};text-align:right;padding:0.55rem 2rem 0.55rem 0;"
            f"font-size:0.88rem;vertical-align:middle;'>{int(row['TOTAL_VOTES']):,}</td>"
            f"<td style='color:{P['faint']};text-align:right;padding:0.55rem 2rem 0.55rem 0;"
            f"font-size:0.85rem;vertical-align:middle;'>{row['VOTE_PERCENTAGE']:.2f}%</td>"
            f"<td style='padding:0.55rem 0.5rem;text-align:center;vertical-align:middle;'>{status_html}</td>"
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
        f"<th style='{th}padding:0.55rem 1.5rem 0.55rem 0;text-align:right;width:3rem;'>Rank</th>"
        f"<th style='{th}padding:0.55rem 2rem 0.55rem 0;text-align:left;'>Candidate</th>"
        f"<th style='{th}padding:0.55rem 2rem 0.55rem 0;text-align:right;'>Votes</th>"
        f"<th style='{th}padding:0.55rem 2rem 0.55rem 0;text-align:right;'>Vote %</th>"
        f"<th style='{th}padding:0.55rem 0.5rem;text-align:center;'>Status</th>"
        f"</tr></thead>"
        f"<tbody>{''.join(rows)}</tbody>"
        f"</table>",
        unsafe_allow_html=True,
    )


# sidebar
render_sidebar()

# data
regional_df = fetch_regional_votes()
geojson = load_geojson()
rankings_df = fetch_senate_rankings()

# page
st.markdown(
    "<p class='tagline'>2025 Philippine Midterm Elections</p>", unsafe_allow_html=True
)
st.title("Senate Results")

st.markdown("<br>", unsafe_allow_html=True)

# votes per region
st.markdown("<p class='section-label'>VOTES BY REGION</p>", unsafe_allow_html=True)
st.markdown("## Where the votes came from")
st.caption("Total senate votes per region · OAV, LAV, and NIR excluded.")

st.markdown("<br style='line-height:0.5;'>", unsafe_allow_html=True)

col_map, col_rank = st.columns([3, 2])
with col_map:
    st.plotly_chart(build_map(regional_df, geojson), use_container_width=True)
with col_rank:
    render_region_ranking(regional_df)

st.markdown("<br>", unsafe_allow_html=True)

# election winners
st.markdown("<p class='section-label'>WINNERS</p>", unsafe_allow_html=True)
st.markdown("## Top 12 winners")
st.caption("Ranked by total votes received.")

st.markdown("<br style='line-height:0.5;'>", unsafe_allow_html=True)

with st.container(border=True):
    st.plotly_chart(build_winners_chart(rankings_df), use_container_width=True)

st.markdown("<br>", unsafe_allow_html=True)

# full results
st.markdown("<p class='section-label'>FULL RESULTS</p>", unsafe_allow_html=True)
st.markdown("## All candidates")
st.caption("66 candidates — 12 winners declared by COMELEC.")

st.markdown("<br style='line-height:0.5;'>", unsafe_allow_html=True)

with st.container(border=True):
    render_results_table(rankings_df)
