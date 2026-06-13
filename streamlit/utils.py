import json
import re

import duckdb
import pandas as pd
import streamlit as st

REGION_MAP = {
    "REGION I": "Ilocos Region (Region I)",
    "REGION II": "Cagayan Valley (Region II)",
    "REGION III": "Central Luzon (Region III)",
    "REGION IV-A": "CALABARZON (Region IV-A)",
    "REGION IV-B": "MIMAROPA (Region IV-B)",
    "REGION V": "Bicol Region (Region V)",
    "REGION VI": "Western Visayas (Region VI)",
    "REGION VII": "Central Visayas (Region VII)",
    "REGION VIII": "Eastern Visayas (Region VIII)",
    "REGION IX": "Zamboanga Peninsula (Region IX)",
    "REGION X": "Northern Mindanao (Region X)",
    "REGION XI": "Davao Region (Region XI)",
    "REGION XII": "SOCCSKSARGEN (Region XII)",
    "REGION XIII": "Caraga (Region XIII)",
    "NATIONAL CAPITAL REGION": "Metropolitan Manila",
    "CORDILLERA ADMINISTRATIVE REGION": "Cordillera Administrative Region (CAR)",
    "BARMM": "Autonomous Region of Muslim Mindanao (ARMM)",
}

SHORT_NAMES = {
    "REGION I": "Ilocos Region",
    "REGION II": "Cagayan Valley",
    "REGION III": "Central Luzon",
    "REGION IV-A": "CALABARZON",
    "REGION IV-B": "MIMAROPA",
    "REGION V": "Bicol Region",
    "REGION VI": "Western Visayas",
    "REGION VII": "Central Visayas",
    "REGION VIII": "Eastern Visayas",
    "REGION IX": "Zamboanga Peninsula",
    "REGION X": "Northern Mindanao",
    "REGION XI": "Davao Region",
    "REGION XII": "SOCCSKSARGEN",
    "REGION XIII": "Caraga",
    "NATIONAL CAPITAL REGION": "Metro Manila",
    "CORDILLERA ADMINISTRATIVE REGION": "CAR",
    "BARMM": "Bangsamoro",
}

PALETTE = {
    "bg":            "#1a1722",
    "panel":         "#221e2d",
    "panel2":        "#2b2638",
    "border":        "#322d42",
    "border_strong": "#473f59",
    "text":          "#ece1d0",
    "muted":         "#a59cae",
    "faint":         "#6f6878",
    "primary":       "#e0a85a",
    "green":         "#b3bd6a",
    "red":           "#e88b7a",
    "map_lo":        "#2a2438",
    "map_hi":        "#e8b265",
    "pill_bg":       "rgba(224,168,90,0.15)",
    "pill_border":   "rgba(224,168,90,0.28)",
    "green_pill_bg": "rgba(179,189,106,0.15)",
    "green_pill_bd": "rgba(179,189,106,0.28)",
    "grey_pill_bg":  "rgba(111,104,120,0.15)",
    "grey_pill_bd":  "rgba(111,104,120,0.22)",
}

LIGHT_PALETTE = {
    "bg":            "#f5eee0",
    "panel":         "#fffbf3",
    "panel2":        "#f0e6d0",
    "border":        "#e0ccaa",
    "border_strong": "#c8b085",
    "text":          "#1e1a12",
    "muted":         "#7a6a50",
    "faint":         "#a09070",
    "primary":       "#c2853a",
    "green":         "#6a7a2a",
    "red":           "#c05040",
    "map_lo":        "#efe4cf",
    "map_hi":        "#c2853a",
    "pill_bg":       "rgba(194,133,58,0.12)",
    "pill_border":   "rgba(194,133,58,0.30)",
    "green_pill_bg": "rgba(106,122,42,0.12)",
    "green_pill_bd": "rgba(106,122,42,0.28)",
    "grey_pill_bg":  "rgba(120,106,80,0.12)",
    "grey_pill_bd":  "rgba(120,106,80,0.22)",
}


def get_palette() -> dict:
    if st.session_state.get("theme", "dark") == "light":
        return LIGHT_PALETTE
    return PALETTE


@st.cache_resource
def get_connection() -> duckdb.DuckDBPyConnection:
    return duckdb.connect(
        "/Users/derrick/Projects/polis-ph/polis.duckdb", read_only=True
    )


@st.cache_data
def load_geojson() -> dict:
    with open(
        "/Users/derrick/Projects/polis-ph/streamlit/data/regions_simplified.json"
    ) as f:
        return json.load(f)


def clean_name(raw: str) -> str:
    s = raw.strip()
    parts = s.split(" ", 1)
    if parts[0].rstrip(".").isdigit() and len(parts) > 1:
        return " ".join(parts[1].split())
    return s


def parse_candidate(raw: str) -> tuple[str, str]:
    cleaned = clean_name(raw)
    m = re.match(r"^(.*?)\s*\(([^)]+)\)\s*$", cleaned)
    if m:
        return " ".join(m.group(1).split()), m.group(2).strip()
    return cleaned, ""


def apply_theme() -> None:
    P = get_palette()
    st.markdown(
        f"""
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Source+Sans+3:wght@300;400;500;600&display=swap');

            * {{ font-family: 'Source Sans 3', sans-serif !important; }}

            .stApp {{ background-color: {P['bg']}; }}

            [data-testid="stSidebar"] {{
                background-color: {P['panel']} !important;
                border-right: 1px solid {P['border']} !important;
            }}
            [data-testid="stSidebar"] p {{
                color: {P['muted']} !important;
                font-size: 0.78rem !important;
            }}

            [data-testid="stVerticalBlockBorderWrapper"] {{
                background-color: {P['panel']} !important;
                border: 1px solid {P['border']} !important;
                border-radius: 8px !important;
                overflow: hidden;
            }}

            h1 {{
                color: {P['text']} !important;
                font-weight: 300 !important;
                font-size: 2.4rem !important;
                letter-spacing: -0.02em !important;
                line-height: 1.2 !important;
            }}
            h2 {{
                color: {P['text']} !important;
                font-weight: 300 !important;
                font-size: 1.6rem !important;
                letter-spacing: -0.01em !important;
                margin-top: 0.25rem !important;
            }}

            p {{ color: {P['muted']} !important; }}
            hr {{ border-color: {P['border']} !important; }}

            [data-testid="stCaptionContainer"] p {{
                color: {P['faint']} !important;
                font-size: 0.8rem !important;
            }}

            [data-testid="stSelectbox"] label {{
                color: {P['faint']} !important;
                font-size: 0.65rem !important;
                text-transform: uppercase !important;
                letter-spacing: 0.1em !important;
                font-weight: 500 !important;
            }}

            /* sidebar button */
            /* hide Streamlit top toolbar */
            header[data-testid="stHeader"] {{ display: none !important; }}

            /* hide auto-generated sidebar nav */
            [data-testid="stSidebarNav"] {{ display: none !important; }}

            /* hide sidebar collapse button */
            [data-testid="stSidebarCollapseButton"],
            [data-testid="stSidebarCollapsedControl"] {{ display: none !important; }}

            /* page link items */
            [data-testid="stPageLink"] a {{
                color: {P['muted']} !important;
                font-size: 0.88rem !important;
                text-decoration: none !important;
                padding: 0.3rem 0.5rem !important;
                border-radius: 4px !important;
                display: block !important;
                transition: background 0.15s, color 0.15s;
            }}
            [data-testid="stPageLink"] a:hover {{
                background: {P['panel2']} !important;
                color: {P['text']} !important;
            }}
            [data-testid="stPageLink-active"] a,
            [data-testid="stPageLink"][aria-current] a {{
                color: {P['primary']} !important;
                background: {P['panel2']} !important;
            }}

            /* theme toggle button */
            [data-testid="stSidebar"] button {{
                background: transparent !important;
                border: 1px solid {P['border_strong']} !important;
                color: {P['muted']} !important;
                font-size: 0.75rem !important;
                padding: 0.3rem 0.75rem !important;
                border-radius: 4px !important;
                width: 100% !important;
            }}
            [data-testid="stSidebar"] button:hover {{
                border-color: {P['primary']} !important;
                color: {P['primary']} !important;
            }}

            .section-label {{
                font-size: 0.65rem;
                color: {P['primary']};
                text-transform: uppercase;
                letter-spacing: 0.14em;
                font-weight: 600;
                margin: 0;
                padding: 0;
                line-height: 1;
            }}
            .tagline {{
                font-size: 0.68rem;
                color: {P['faint']};
                letter-spacing: 0.12em;
                text-transform: uppercase;
                margin-bottom: 0.2rem;
            }}

            .stat-card {{
                background: {P['panel']};
                border: 1px solid {P['border']};
                border-radius: 8px;
                padding: 1.75rem;
                min-height: 9rem;
                box-sizing: border-box;
            }}
            .stat-value {{
                font-size: 2.6rem;
                font-weight: 300;
                color: {P['primary']};
                letter-spacing: -0.03em;
                line-height: 1;
            }}
            .stat-label {{
                font-size: 0.65rem;
                color: {P['faint']};
                text-transform: uppercase;
                letter-spacing: 0.1em;
                margin-top: 0.5rem;
            }}
            .stat-sub {{
                font-size: 0.82rem;
                color: {P['muted']};
                margin-top: 0.2rem;
            }}

            .disclaimer {{
                background: {P['panel']};
                border: 1px solid {P['border']};
                border-left: 3px solid {P['primary']};
                border-radius: 4px;
                padding: 1rem 1.25rem;
                font-size: 0.85rem;
                color: {P['muted']};
                line-height: 1.7;
            }}

            .winner-pill {{
                display: inline-block;
                background: {P['pill_bg']};
                color: {P['primary']};
                border: 1px solid {P['pill_border']};
                border-radius: 4px;
                padding: 1px 8px;
                font-size: 0.72rem;
            }}
            .seats-3 {{
                display: inline-block;
                background: {P['pill_bg']};
                color: {P['primary']};
                border: 1px solid {P['pill_border']};
                border-radius: 4px;
                padding: 1px 8px;
                font-size: 0.72rem;
            }}
            .seats-2 {{
                display: inline-block;
                background: {P['green_pill_bg']};
                color: {P['green']};
                border: 1px solid {P['green_pill_bd']};
                border-radius: 4px;
                padding: 1px 8px;
                font-size: 0.72rem;
            }}
            .seats-1 {{
                display: inline-block;
                background: {P['grey_pill_bg']};
                color: {P['muted']};
                border: 1px solid {P['grey_pill_bd']};
                border-radius: 4px;
                padding: 1px 8px;
                font-size: 0.72rem;
            }}

            /* force table cells to be compact and vertically centered */
            table td, table th {{
                vertical-align: middle !important;
                line-height: 1.3 !important;
            }}

            #MainMenu {{ visibility: hidden; }}
            footer {{ visibility: hidden; }}
            .block-container {{ padding-top: 2rem !important; }}
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_sidebar() -> None:
    P = get_palette()

    # ── header ────────────────────────────────────────────────────────────────
    st.sidebar.markdown(
        f"<p style='font-size:1.1rem;font-weight:600;color:{P['text']};"
        f"letter-spacing:0.02em;margin-bottom:0.1rem;'>polis</p>"
        f"<p style='font-size:0.62rem;color:{P['faint']};letter-spacing:0.1em;"
        f"text-transform:uppercase;margin-top:0;'>2025 Midterm Elections</p>",
        unsafe_allow_html=True,
    )
    st.sidebar.divider()

    # ── navigation ────────────────────────────────────────────────────────────
    with st.sidebar:
        st.page_link("app.py", label="Overview")
        st.page_link("pages/1_senate.py", label="Senate")
        st.page_link("pages/2_party_list.py", label="Party List")
        st.page_link("pages/3_regional_breakdown.py", label="Regional Breakdown")

    st.sidebar.divider()

    # ── theme toggle ──────────────────────────────────────────────────────────
    is_dark = st.session_state.get("theme", "dark") == "dark"
    label = "☀  Light mode" if is_dark else "☾  Dark mode"
    if st.sidebar.button(label):
        st.session_state.theme = "light" if is_dark else "dark"
        st.rerun()

    st.sidebar.divider()

    # ── footer ────────────────────────────────────────────────────────────────
    st.sidebar.markdown(
        f"<p style='font-size:0.68rem;color:{P['faint']};line-height:2;'>"
        f"Data: COMELEC 2025<br>Spark · dbt · DuckDB</p>",
        unsafe_allow_html=True,
    )


def render_region_ranking(regional_df: pd.DataFrame) -> None:
    P = get_palette()
    max_votes = regional_df["TOTAL_VOTES"].max()
    rows = []
    for i, row in enumerate(regional_df.itertuples(index=False)):
        short = SHORT_NAMES.get(row.REGION, row.REGION)
        bar_pct = row.TOTAL_VOTES / max_votes * 100
        votes_m = f"{row.TOTAL_VOTES / 1e6:.1f}M"
        rows.append(
            f"<div style='display:flex;align-items:center;padding:0.4rem 0;"
            f"border-bottom:1px solid {P['border']};'>"
            f"<span style='color:{P['faint']};width:1.6rem;font-size:0.7rem;"
            f"text-align:right;margin-right:0.7rem;flex-shrink:0;'>{i + 1}</span>"
            f"<span style='color:{P['text']};flex:1;font-size:0.82rem;"
            f"white-space:nowrap;overflow:hidden;text-overflow:ellipsis;'>{short}</span>"
            f"<div style='width:72px;height:3px;background:{P['panel2']};"
            f"border-radius:2px;margin:0 0.7rem;flex-shrink:0;'>"
            f"<div style='width:{bar_pct:.1f}%;height:100%;background:{P['primary']};"
            f"border-radius:2px;'></div></div>"
            f"<span style='color:{P['muted']};font-size:0.75rem;"
            f"min-width:3.2rem;text-align:right;flex-shrink:0;'>{votes_m}</span>"
            f"</div>"
        )
    html = (
        f"<div style='background:{P['panel']};border:1px solid {P['border']};"
        f"border-radius:8px;padding:1rem 1.25rem;'>"
        f"<div style='display:flex;justify-content:space-between;"
        f"margin-bottom:0.6rem;padding-bottom:0.4rem;"
        f"border-bottom:1px solid {P['border_strong']};'>"
        f"<span style='font-size:0.6rem;color:{P['faint']};text-transform:uppercase;"
        f"letter-spacing:0.14em;font-weight:600;'>REGION RANKING</span>"
        f"<span style='font-size:0.6rem;color:{P['faint']};text-transform:uppercase;"
        f"letter-spacing:0.14em;'>total votes</span>"
        f"</div>"
        + "".join(rows)
        + "</div>"
    )
    st.markdown(html, unsafe_allow_html=True)
