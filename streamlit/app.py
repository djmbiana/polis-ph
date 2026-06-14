from pathlib import Path

import duckdb
import streamlit as st

from utils import apply_theme, get_palette, render_sidebar

st.set_page_config(
    page_title="Polis",
    page_icon="🗳️",
    layout="wide",
    initial_sidebar_state="expanded",
)

apply_theme()

P = get_palette()


@st.cache_data
def fetch_stats() -> tuple[int, int, int]:
    db_path = Path(__file__).parent.parent / "polis.duckdb"
    con = duckdb.connect(str(db_path), read_only=True)
    row_v = con.execute("SELECT SUM(VOTES) FROM fact_votes").fetchone()
    row_p = con.execute("SELECT COUNT(*) FROM dim_precinct").fetchone()
    row_c = con.execute("SELECT COUNT(*) FROM dim_candidate").fetchone()
    total_votes = int(row_v[0] or 0) if row_v else 0
    total_precincts = int(row_p[0] or 0) if row_p else 0
    total_candidates = int(row_c[0] or 0) if row_c else 0
    return total_votes, total_precincts, total_candidates


render_sidebar()

total_votes, total_precincts, total_candidates = fetch_stats()

st.markdown(
    "<p class='tagline'>2025 Philippine Midterm Elections · By the Numbers</p>",
    unsafe_allow_html=True,
)
st.title("Polis")
st.markdown(
    f"<p style='color:{P['muted']};font-size:1rem;font-weight:300;line-height:1.8;"
    f"max-width:560px;margin-top:0.5rem;'>"
    "An end-to-end look at how the Philippines voted in the 2025 midterm elections. "
    "Explore senatorial results, party list standings, and precinct-level vote "
    "distribution across every region — built for anyone who wants to understand "
    "the data behind the headlines."
    "</p>",
    unsafe_allow_html=True,
)

st.markdown("<br>", unsafe_allow_html=True)

c1, c2, c3 = st.columns(3)
with c1:
    st.markdown(
        f"<div class='stat-card'>"
        f"<div class='stat-value'>{total_votes:,}</div>"
        f"<div class='stat-label'>Total votes cast</div>"
        f"<div class='stat-sub'>across all races</div>"
        f"</div>",
        unsafe_allow_html=True,
    )
with c2:
    st.markdown(
        f"<div class='stat-card'>"
        f"<div class='stat-value'>{total_precincts:,}</div>"
        f"<div class='stat-label'>Precincts reporting</div>"
        f"<div class='stat-sub'>partial COMELEC scrape</div>"
        f"</div>",
        unsafe_allow_html=True,
    )
with c3:
    st.markdown(
        f"<div class='stat-card'>"
        f"<div class='stat-value'>{total_candidates:,}</div>"
        f"<div class='stat-label'>Candidates on ballot</div>"
        f"<div class='stat-sub'>senate + party-list</div>"
        f"</div>",
        unsafe_allow_html=True,
    )

st.markdown("<br>", unsafe_allow_html=True)
st.divider()

st.markdown(
    f"<div class='disclaimer'>"
    f"<strong style='color:{P['text']};'>Note:</strong> "
    f"This dashboard is an exploratory overview and is <em>not</em> intended as authoritative "
    f"or 100% accurate reporting. Senate and Party List totals are sourced from official COMELEC "
    f"data, but regional vote breakdowns come from a partial scrape of raw precinct results — "
    f"coverage gaps mean regional totals will not match national figures. "
    f"For official certified results, refer directly to "
    f"<a href='https://comelec.gov.ph' target='_blank' "
    f"style='color:{P['primary']};text-decoration:none;'>COMELEC</a>."
    f"</div>",
    unsafe_allow_html=True,
)

st.markdown("<br style='line-height:0.5;'>", unsafe_allow_html=True)
st.caption("Navigate using the sidebar.")
